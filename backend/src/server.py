import sys, os, json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from urllib.parse import urlparse
# Importiamo i nostri parser
from parsers.parser_mypersonaltrainer import MyPersonalTrainerParser
from parsers.parser_wikipedia import WikipediaParser
from parsers.parser_premier import PremierLeagueParser

#importo per evaluation
from evaluator import Evaluator

app = FastAPI()

PARSERS_DOMAINS = {
    "www.my-personaltrainer.it": MyPersonalTrainerParser(),
    "it.wikipedia.org": WikipediaParser(),
    "www.premierleague.com": PremierLeagueParser()
}
@app.get("/parse")
async def parse(url: str):
    domain = urlparse(url).netloc
    if domain not in PARSERS_DOMAINS:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    
    parser = PARSERS_DOMAINS[domain]
    try:
        risultato = await parser.parser_url(url)
        parser.salva_risultati(risultato["parsed_text"], risultato["html_text"]) #salva i risultati in file, da eliminare alla fine
        return risultato
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/domains")
async def domains():
    return {"domains": list(PARSERS_DOMAINS.keys())}

@app.get("/gold_standard")
def gold_standard(URL: str):
    domain = urlparse(URL).netloc
    if domain not in PARSERS_DOMAINS:
        return "Error: unsupported domain"
    with open(f"gs_data/dominio_{domain}_gs.json") as json_data:
        j = json.load(json_data)
    
    for obj in j:
        if obj["url"] == URL:
            return obj
    return "Error: url not in gs"

@app.get("/full_gold_standard:")
def full_gold_standard(dominio: str):
    with open(f"gs_data/dominio_{dominio}_gs.json") as json_data:
        j = json.load(json_data)
    return j

@app.get("/full_gs_eval:")
def full_gs_eval(domain: str):
    if domain not in PARSERS_DOMAINS:
        return "Error: unsupported domain"
    
    output_dict = {
        "token_level_eval" : {
            "precision": 0, 
            "recall": 0,
            "f1": 0
        },
        "rouge_2_eval": {
            "precision": 0, 
            "recall": 0,
            "f1": 0
        },
        "information_density_evaluation" : {
            "Score gold standard" : 0,
            "Score parsed text" : 0,
            "Difference" : 0
        },
        "TF-IDF_cosine_similarity" : {
            "Score" : 0
        } 
    }

    gs = full_gold_standard(domain)
    parser = PARSERS_DOMAINS[domain]
    tot_urls = 0
    for obj in gs: #itera sui membri del gs
       json_parsed = parser.parser_url(obj["url"])
       evaluation = evaluate(json_parsed["parsed_text"], obj["gold_text"])
       tot_urls += 1
       for method in evaluation: #itera sui metodi
            for score in method: #itera sui campi di ogni metodo
                output_dict[method][score] += evaluation[method][score]
    
    for method in output_dict:
        for score in method:
            output_dict[method][score] /= tot_urls
    
    return output_dict

# Classe per il corpo della richiesta
class EvaluationRequest(BaseModel):
    parsed_text: str
    gold_text: str

@app.post("/evaluate")
def evaluate(request: EvaluationRequest):
    return Evaluator().eval_server(request.parsed_text, request.gold_text)


