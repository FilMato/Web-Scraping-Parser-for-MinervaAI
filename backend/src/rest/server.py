import os
import re
import sys
import time
import mariadb # Ricordatevi di metterlo nel requirements.txt
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from urllib.parse import urlparse
from typing import Optional
from clients import ollama_client

#importo per evaluation
from src.evaluator.evaluator import Evaluator
#importo factory per parser
from src.factory.parserfactory import ParserFactory
#importo seeder per popolamento iniziale del database
from src.db.seeder import populate_database

# --- BLOCCO DI CODICE DA CANCELLARE DOPO AVER MODIFICATO CORRETTAMENTE LE FUNZIONI DELL'API PER USARE IL DATABASE INVECE DEI FILE JSON ---
import json
base_dir = os.path.dirname(os.path.abspath(__file__))
percorso_domains = os.path.join(base_dir, "..", "..", "domains.json")
try:
    with open(percorso_domains, "r", encoding="utf-8") as f:
        dati_json = json.load(f)
        SUPPORTED_DOMAINS = dati_json.get("domains", [])
except FileNotFoundError:   # Fallback in caso di problemi di percorso prendo i domini manualmente
    SUPPORTED_DOMAINS = [
        "www.my-personaltrainer.it",
        "it.wikipedia.org",
        "www.premierleague.com",
        "www.un.org"
    ]
GS_DOMAINS = {}
cartella_gs = os.path.join(base_dir, "..", "..", "gs_data")
for dominio in SUPPORTED_DOMAINS:
    nome_file = f"dominio_{dominio}_gs.json"    
    percorso_file = os.path.join(cartella_gs, nome_file)
    try:
        with open(percorso_file, "r", encoding="utf-8") as f:
            GS_DOMAINS[dominio] = json.load(f)
    except FileNotFoundError:
        print(f"File Gold Standard non trovato per {dominio} ({nome_file})")
GS_INDEX = {} # dizionario indicizzato per URL...
for dominio, articoli in GS_DOMAINS.items():
    GS_INDEX[dominio] = {a["url"]: a for a in articoli}
# --- FINE BLOCCO DA CANCELLARE -----------------------------------------------------------------------------------------------------------------

#definizione classi pydantic per i corpi delle richieste e definizione endpoints
class ParseOutput(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    parsed_text: str

class PostParseRequest(BaseModel):  #input di post/parse
    url: str
    local:Optional[bool]=False

class DomainsOutput(BaseModel):
    domains: list[str]

class GoldStandardUrlsOutput(BaseModel):
    urls: list[str]

class GSOutput(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str

class FullGSOutput(BaseModel):
    gold_standard: list[GSOutput]

class EvaluationRequest(BaseModel): #input di post/evaluate
    parsed_text: str
    gold_text: str

# definizione dei modelli per le metriche del'evaluation
class Metrics(BaseModel):
    precision: float
    recall: float
    f1: float
class DensityMetrics(BaseModel):
    score_gold_standard: float = Field(alias="Score gold standard")
    score_parsed_text: float = Field(alias="Score parsed text")
    Difference: float

class EvaluationOutput(BaseModel):
    token_level_eval: Metrics
    rouge_2_eval: Metrics
    information_density_evaluation: DensityMetrics
    tf_idf_cosine_similarity: float = Field(alias="TF-IDF_cosine_similarity")

class JudgeOutput(BaseModel):
    model_name: str
    judge_score: float #da vedere forse deve essere int
    judge_feedback: str

def Zero_Inizializer(model_class: type[BaseModel]) -> dict:   #Legge un modello Pydantic e crea un dizionario con la stessa struttura inizializzato a 0.0
    zero_dict = {}
    for field_name, field_info in model_class.model_fields.items():
        key = field_info.alias if field_info.alias else field_name  # Se abbiamo usato un alias (es. "TF-IDF_cosine_similarity") usiamo quello, altrimenti il nome normale
        field_type = field_info.annotation
        if isinstance(field_type, type) and issubclass(field_type, BaseModel):  # Se il campo è un'altra classe Pydantic (es. Metrics o DensityMetrics) facciamo ricorsione
            zero_dict[key] = Zero_Inizializer(field_type)
        else:   # Altrimenti assumiamo che sia un valore singolo e lo mettiamo a 0.0
            zero_dict[key] = 0.0 
    return zero_dict


# Questa funzione serve come doppio controllo per assicurarsi che il backend non si avvii finché MariaDB non è pronto. Anche se abbiamo messo un healthcheck nel docker-compose.
@asynccontextmanager
async def lifespan(app: FastAPI):
    max_retries = 5
    delay_seconds = 5
    conn = None
    
    print("Tentativo di connessione a MariaDB in corso...")
    while max_retries > 0:
        try:
            conn = mariadb.connect(
                host=os.getenv("DB_HOST", "mariadb"),
                user=os.getenv("DB_USER", "minerva_user"),
                password=os.getenv("DB_PASSWORD", "minerva_pass"),
                database=os.getenv("DB_NAME", "minerva_db"),
                port=3306
            )
            print("Connessione a MariaDB stabilita con successo!")
            break
        except mariadb.Error as e:
            print(f"MariaDB non è ancora pronto. Errore: {e}")
            max_retries -= 1
            if max_retries == 0:
                print("Impossibile connettersi al database. Spegnimento del backend.")
                sys.exit(1)
            time.sleep(delay_seconds)
            
    app.state.db = conn
    
    # Popolamento iniziale del database con i dati del Gold Standard
    if conn:
        populate_database(conn)

    yield # Il server è ora attivo e pronto a ricevere richieste

    # Fase di spegnimento
    if app.state.db:
        app.state.db.close()
        print("Connessione a MariaDB chiusa correttamente.")
#----------------------------------------------------------------


app = FastAPI(lifespan=lifespan)


@app.post("/parse")
async def post_parse(request: PostParseRequest)-> ParseOutput:
    domain = urlparse(request.url).netloc
    if domain not in SUPPORTED_DOMAINS:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    parser = ParserFactory.create(domain)   #seleziona il parser corretto in base al dominio, se il dominio non è supportato solleva un'eccezione
    if request.local:
        articolo=GS_INDEX.get(domain,{}).get(request.url) #Quando pippo mi da il DB va modificata con la chiamata alla repository
        if not articolo:
            raise HTTPException(status_code=404,detail="URL no trovato nelo DB")
        try:
            risultato = await parser.parser_url2(request.url, articolo["html_text"])
            return risultato
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        try:
            risultato=await parser.parser_url(request.url)
            return risultato
        except Exception as e:
            raise HTTPException(status_code=502,detail=f"URL irragiungibile: {str(e)}")


@app.get("/domains")
async def domains() -> DomainsOutput:
    return {"domains": SUPPORTED_DOMAINS}


@app.get("/gold_standard")
async def gold_standard(url: str) -> GSOutput:
    domain = urlparse(url).netloc
    if domain not in SUPPORTED_DOMAINS:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    articolo = GS_INDEX.get(domain, {}).get(url) #da modificare con la chiamata al databse quando ci sta
    if not articolo:
        raise HTTPException(status_code=404, detail="URL non nel gold standard")
    return articolo

@app.get("/gold_standard_urls")
async def gold_standard_urls(domain:str) ->GoldStandardUrlsOutput:
    if domain not in SUPPORTED_DOMAINS:
        raise HTTPException(status_code=400,detail="Dominio non supportato")
    urls=list(GS_INDEX.get(domain,{}).keys()) #da sostituire GS_INDEX con il database
    return {"urls":urls}

@app.get("/full_gold_standard")
async def full_gold_standard(domain: str) -> FullGSOutput:
    if domain not in GS_DOMAINS:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    gs=GS_DOMAINS[domain]   #prendo in base al dominio il corrispettivo file dominio_gs.json che contiene il gold standard per quel dominio
    return {"gold_standard": gs}


@app.get("/full_gs_eval")
async def full_gs_eval(domain: str) -> EvaluationOutput:
    if domain not in GS_DOMAINS:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    count = 0
    valutatore = Evaluator()
    articoli = GS_DOMAINS[domain]   #prendo in base al dominio il corrispettivo file dominio_gs.json che contiene il gold standard per quel dominio
    parser = ParserFactory.create(domain)   #seleziona il parser corretto in base al dominio, se il dominio non è supportato solleva un'eccezione
    somme = Zero_Inizializer(EvaluationOutput)    #inizializzo a zero tutte le somme che mi serviranno per fare la media alla fine
    for articolo in articoli:
        gold_text = articolo["gold_text"]
        parsed_text = ""    # inizializziamo parsed_text a una stringa vuota, e solo se parser_json è valido e contiene "parsed_text", lo aggiorniamo
        try:
            parser_json = await parser.parser_url2(articolo["url"], articolo["html_text"])
            parsed_text = parser_json.parsed_text if parser_json else ""
        except Exception:
            parsed_text=""
        try:
            result = valutatore.eval_server(parsed_text, gold_text)
        except Exception:
            result = Zero_Inizializer(EvaluationOutput)   # se la valutazione fallisce, mettiamo tutto a zero

        for key, value in result.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    somme[key][sub_key] += sub_value
            else:
                somme[key] += value
        count += 1 
    if count == 0:  # se non ci sono articoli, restituisco gli zeri per evitare la divisione per zero
        return EvaluationOutput(**somme)
    medie = {}
    for key, value in somme.items():
        if isinstance(value, dict):
            medie[key] = {sub_key: sub_val / count for sub_key, sub_val in value.items()}    # comprehension per calcolare la media di ogni sotto-elemento del dizionario
        else:
            medie[key] = value / count   # media per i valori singoli    
    return EvaluationOutput(**medie)

#funzione per pulire il markdown
def strip_txt(text: str) -> str: 
            
    text = text.lower()
    text = re.sub(r'\*+([^*]+)\*+', r'\1', text) #grassetto
    text = re.sub(r'\_+([^_]+)\_+', r'\1', text) #corsivo
    text = re.sub(r'\#+\s?([^#]+)', r'\1', text) #titoli
    text = re.sub(r'\[([^\]]+)\]\((?:[^)\\]|\\.)*\)', r'\1', text) #link
            
    return text


@app.post("/evaluate")
async def evaluate(request: EvaluationRequest) -> EvaluationOutput:
    parsed_text = strip_txt(request.parsed_text)
    try:
        return Evaluator().eval_server(parsed_text, request.gold_text)
    except Exception as e:
        print(f"Errore durante la valutazione: {e}") 
        return EvaluationOutput(**Zero_Inizializer(EvaluationOutput))

@app.post("/evaluate_judge")
async def evaluate_judge(request: EvaluationRequest) -> JudgeOutput: #perché questo funzioni judge deve ritornare un dizionario che abbia le stesse identiche chiavi di JudgeOutput
    parsed_text = strip_txt(request.parsed_text)
    return await ollama_client.judge(parsed_text=parsed_text, gold_text=request.gold_text)



