import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from urllib.parse import urlparse

# Importiamo i nostri parser
from parsers.parser_mypersonaltrainer import MyPersonalTrainerParser
from parsers.parser_wikipedia import WikipediaParser
from parsers.parser_premier import PremierLeagueParser
from parsers.parser_un import Parser_UN

#importo per evaluation
from evaluator import Evaluator

app = FastAPI()

PARSERS_DOMAINS = {
    "www.my-personaltrainer.it": MyPersonalTrainerParser(),
    "it.wikipedia.org": WikipediaParser(),
    "www.premierleague.com": PremierLeagueParser(),
    "www.un.org": Parser_UN()
}


GS_DOMAINS = {}
base_dir = os.path.dirname(os.path.abspath(__file__))
cartella_gs = os.path.join(base_dir, "..", "gs_data")
mappa_file = {
    "it.wikipedia.org": "dominio_it.wikipedia.org_gs.json",
    "www.premierleague.com": "dominio_premierleague.com_gs.json",
    "www.un.org": "dominio_un.org_gs.json",
    "www.my-personaltrainer.it": "dominio_www.my-personaltrainer.it_gs.json"
}
for dominio, nome_file in mappa_file.items():
    percorso_file = os.path.join(cartella_gs, nome_file)
    with open(percorso_file, "r", encoding="utf-8") as f:
        GS_DOMAINS[dominio] = json.load(f)


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
    
# Classe per il corpo della richiesta
class PostRequest(BaseModel):
    url: str
    html_text: str

@app.post("/parse")
async def parse(request: PostRequest):
    domain = urlparse(request.url).netloc
    if domain not in PARSERS_DOMAINS:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    parser = PARSERS_DOMAINS[domain]
    try:
        risultato = await parser.parser_url2(request.url, request.html_text)
        return risultato
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/domains")
async def domains():
    return {"domains": list(PARSERS_DOMAINS.keys())}

@app.get("/gold_standard")
async def gold_standard(url: str):
    domain = urlparse(url).netloc
    if domain not in PARSERS_DOMAINS:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    gs=GS_DOMAINS[domain]
    for j in gs:
        if j["url"] == url:
            return  j

@app.get("/full_gold_standard")
async def full_gold_standard(domain: str):
    if domain not in GS_DOMAINS:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    gs=GS_DOMAINS[domain]
    return {"gold_standard": gs}

@app.get("/full_gs_eval")
async def full_gs_eval(domain: str):
    if domain not in GS_DOMAINS:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    count = 0
    valutatore = Evaluator()
    articoli = GS_DOMAINS[domain]
    parser = PARSERS_DOMAINS[domain]
    somme = {
        "token_level_eval": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
        "rouge_2_eval": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
        "information_density_evaluation": {"Score gold standard": 0.0, "Score parsed text": 0.0, "Difference": 0.0},
        "TF-IDF_cosine_similarity": 0.0
    }
    for articolo in articoli:
        print(articolo["url"])
        parser_json=await parser.parser_url(articolo["url"])
        gold_text = articolo["gold_text"]
        
        #parsed_text = parser_json["parsed_text"]
        # Inizializziamo parsed_text a una stringa vuota, e solo se parser_json è valido e contiene "parsed_text", lo aggiorniamo
        parsed_text = ""
        parser_json = await parser.parser_url(articolo["url"])
        if parser_json and "parsed_text" in parser_json:
            parsed_text = parser_json["parsed_text"]

        try:
            result = valutatore.eval_server(parsed_text, gold_text)
        except Exception:
            # Se la matematica esplode, mettiamo tutto a zero
            result = {
                "token_level_eval": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
                "rouge_2_eval": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
                "information_density_evaluation": {"Score gold standard": 0.0, "Score parsed text": 0.0, "Difference": 0.0},
                "TF-IDF_cosine_similarity": 0.0
            }
        
        print(result)
        somme["token_level_eval"]["precision"] += result["token_level_eval"]["precision"]
        somme["token_level_eval"]["recall"] += result["token_level_eval"]["recall"]
        somme["token_level_eval"]["f1"] += result["token_level_eval"]["f1"]
        somme["rouge_2_eval"]["precision"] += result["rouge_2_eval"]["precision"]
        somme["rouge_2_eval"]["recall"] += result["rouge_2_eval"]["recall"]
        somme["rouge_2_eval"]["f1"] += result["rouge_2_eval"]["f1"]
        somme["information_density_evaluation"]["Score gold standard"] += result["information_density_evaluation"]["Score gold standard"]
        somme["information_density_evaluation"]["Score parsed text"] += result["information_density_evaluation"]["Score parsed text"]
        somme["information_density_evaluation"]["Difference"] += result["information_density_evaluation"]["Difference"]
        somme["TF-IDF_cosine_similarity"] += result["TF-IDF_cosine_similarity"]
        count += 1
    return {
        "token_level_eval": {
            "precision": somme["token_level_eval"]["precision"] / count,
            "recall": somme["token_level_eval"]["recall"] / count,
            "f1": somme["token_level_eval"]["f1"] / count 
        },
        "rouge_2_eval": {
            "precision": somme["rouge_2_eval"]["precision"] / count,
            "recall": somme["rouge_2_eval"]["recall"] / count,
            "f1": somme["rouge_2_eval"]["f1"] / count
        },
        "information_density_evaluation": {
            "Score gold standard": somme["information_density_evaluation"]["Score gold standard"] / count,
            "Score parsed text": somme["information_density_evaluation"]["Score parsed text"] / count,
            "Difference": somme["information_density_evaluation"]["Difference"] / count
        },
        "TF-IDF_cosine_similarity": somme["TF-IDF_cosine_similarity"] / count  
    }        


# Classe per il corpo della richiesta
class EvaluationRequest(BaseModel):
    parsed_text: str
    gold_text: str

@app.post("/evaluate")
async def evaluate(request: EvaluationRequest):
    try:
        return Evaluator().eval_server(request.parsed_text, request.gold_text)
    except Exception:
        # Se c'è un errore restituiamo gli zeri in modo pulito
        return {
            "token_level_eval": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
            "rouge_2_eval": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
            "information_density_evaluation": {"Score gold standard": 0.0, "Score parsed text": 0.0, "Difference": 0.0},
            "TF-IDF_cosine_similarity": 0.0
        }


