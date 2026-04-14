import sys, os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from urllib.parse import urlparse
# Importiamo i nostri parser
from parsers.parser_mypersonaltrainer import MyPersonalTrainerParser
from parsers.parser_wikipedia import WikipediaParser

app = FastAPI()

PARSERS_DOMAINS = {
    "www.my-personaltrainer.it": MyPersonalTrainerParser(),
    "it.wikipedia.org": WikipediaParser(),
}
@app.get("/parse", URL=str)
async def get_parse(url: str):
    domain = urlparse(url).netloc
    if domain not in PARSERS_DOMAINS:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    
    parser = PARSERS_DOMAINS[domain]
    try:
        risultato = await parser.parser_url(url)
        parser.salva_risultati(risultato["parsed_text"], risultato["html_text"])
        return risultato
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/domains")
async def get_domains():
    return {"domains": list(PARSERS_DOMAINS.keys())}

@app.get("/gold_standard",  URL=str)
def gold_standard(URL: str):
    ciao

@app.get("/full_gold_standard:", dominio=str)
def full_gold_standard(dominio: str):
    ciao

@app.get("/full_gs_eval:", dominio=str)
def full_gs_eval(dominio: str):
    ciao
    
@app.post("/evaluate", parsed_text=str, gold_text=str)
def evaluate(parsed_text: str, gold_text: str):
    ciao
    


