import sys, os

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
    pass

@app.get("/full_gold_standard:")
def full_gold_standard(dominio: str):
    pass

@app.get("/full_gs_eval:")
def full_gs_eval(dominio: str):
    pass
    

# Classe per il corpo della richiesta
class EvaluationRequest(BaseModel):
    parsed_text: str
    gold_text: str

@app.post("/evaluate")
def evaluate(request: EvaluationRequest):
    return Evaluator().eval_server(request.parsed_text, request.gold_text)


