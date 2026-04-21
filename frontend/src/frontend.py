import os
import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# URL del backend (sovrascrivibile via variabile d'ambiente per Docker)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8003")

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


async def get_domains() -> list[str]: #funzione asincrona, non blocca l'intero sistema quando chiamata(in modo da poter gestire + richieste)
    """Recupera la lista dei domini supportati dal backend."""
    try:
        async with httpx.AsyncClient() as client: #apre una sessione di rete come client(si chiude in automatico poichè aperto nella with)
            resp = await client.get(f"{BACKEND_URL}/domains", timeout=10) #fa una chiamata get al end point /domains
            resp.raise_for_status() #se il backend ha risposto con un errore (di tipo 4xx o 5xx), lancia un eccezzione
            return resp.json().get("domains", []) #converte la risposta in un jaison e legge la chiave domains
    except Exception:
        return []


async def get_full_gold_standard(domain: str) -> list[dict]:
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
