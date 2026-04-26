import os
import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# URL del backend (sovrascrivibile via variabile d'ambiente per Docker)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8003")

templates = Jinja2Templates(directory="/LABORATORIO-PER-IL-110/frontend/templates")


async def get_domains() -> list[str]: #funzione asincrona, non blocca l'intero sistema quando chiamata(in modo da poter gestire + richieste)
    """Recupera la lista dei domini supportati dal backend."""
    try:
        async with httpx.AsyncClient() as client: #apre una sessione di rete come client(si chiude in automatico poichè aperto nella with)
            resp = await client.get(f"{BACKEND_URL}/domains", timeout=10) #fa una chiamata get al end point /domains
            resp.raise_for_status() #se il backend ha risposto con un errore (di tipo 4xx o 5xx), lancia un eccezzione
            return resp.json().get("domains", []) #converte la risposta in un jaison e legge la chiave domains
    except Exception:
        return []


async def get_full_gold_standard(domain: str) -> list[dict]:  #mi restituisce una lista di dizionari, cioè una lista di json 
    """Recupera tutto il gold standard di un dominio dal backend."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BACKEND_URL}/full_gold_standard",
                params={"domain": domain},
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("gold_standard", [])
    except Exception:
        pass
    return []


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Pagina principale: carica domini e URL del GS per il menu a tendina."""
    domains = await get_domains()

    # Costruisce mappa domain -> lista URL del GS
    gs_urls: dict[str, list[str]] = {}
    for domain in domains:
        entries = await get_full_gold_standard(domain)
        gs_urls[domain] = [e["url"] for e in entries if "url" in e]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "domains": domains,
            "gs_urls": gs_urls,
            "result": None,
            "error": None,
        },
    )
@app.post("/parse_url",response_class=HTMLResponse)
async def parse_url(request:Request,url:str=Form(...)): #prende in input request(obligatorio per jinja2, serve la sessione corrente) e form cioè indica di cercare l'url nel corpo della richiesta http
    domains= await get_domains()
    gs_urls:dict[str,list[str]]={} #creiamo il dizionario degli url dei gs, per ogni dominio avremo tutti gli url presenti nel gs
    for domini in domains:
        gold=await get_full_gold_standard(domini)
        lista_url=[]
        for e in gold:
            if "url" in e:
                lista_url.append(e["url"])
        gs_urls[domini]=lista_url
    error=None #inizializziamo per contenere l'eventuale messaggio di errore da restituire
    result=None #per contenere la risposta json
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            parse_response=await client.get(f"{BACKEND_URL}/parse",params={"url":url})
            if parse_response.status_code !=200:
                error=f"Errore dal backend ({parse_response.status_code}):{parse_response.text}"
            else:
                parsed=parse_response.json() #trasformiamo la risposta in un json (avrà la froma dei json restituiti dai parser)
                result={
                    "url":parsed.get("url",url),
                    "domain":parsed.get("domain",""),
                    "title":parsed.get("title",""),
                    "parsed_text":parsed.get("parsed_text",""),
                    "html_text":parsed.get("html_text",""),
                    "gold_text":None, #non lo popoliamo, va messo solo se l'url è nel gs
                    "evaluation":None, #stessa cosa di gold_text
                }

                gs_response=await client.get(f"{BACKEND_URL}/gold_standard",params={"url":url}) #andiamo ora a cercare il gs del nostro url per il confronto
                if gs_response.status_code !=200:
                     error=f"Errore dal backend ({gs_response.status_code}):{gs_response.text}"
                else:
                    gs_data=gs_response.json()
                    if gs_data: #se l'url non è nei gs gs_data sarà null
                        result["gold_text"]=gs_data.get("gold_text")
                        if result["gold_text"]: #verifichiamo l'esistena del gs
                            evaluation_response=await client.post(f"{BACKEND_URL}/evaluate",json={"parsed_text":result["parsed_text"],"gold_text":result["gold_text"]}) #mandiamo la richiesta di evaluate(prende in input il parsed text e il gs)
                            if evaluation_response.status_code !=200:
                                 error=f"Errore dal backend ({evaluation_response.status_code}):{evaluation_response.text}"
                            else:
                                result["evaluation"]=evaluation_response.json()
    except httpx.ConnectError:
        error = f"Impossibile connettersi al backend ({BACKEND_URL}). Assicurati che sia in esecuzione."
    except Exception as e:
        error = f"Errore inatteso: {e}"

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "domains":       domains,
            "gs_urls":       gs_urls,
            "result":        result,
            "error":         error,
            "submitted_url": url,
            "backend_url":   BACKEND_URL,
        }
    )
                                



                

