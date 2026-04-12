import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import re
import os
from urllib.parse import urlparse

# parte dell'evaluetor
import sys
# 1. Trova la cartella corrente ('parsers')
current_dir = os.path.dirname(os.path.abspath(__file__))
# 2. Risali di un livello per trovare la cartella genitore ('src')
parent_dir = os.path.dirname(current_dir)
# 3. Aggiungi la cartella 'src' ai percorsi in cui Python cerca i moduli
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
# 4. Ora Python "vede" i file dentro 'src', quindi puoi importare l'Evaluator!
from evaluator import Evaluator


CSS_SELECTORS = [
    "#toc-hook",          # id che contiene i contenuti che ci servono nella stramaggioranza degli URL
    ".sal-article-body",  # corpo articolo alternativo
    "article",            # se questi due non esistono, prendo tutta la sezione article 
    "main"                # fallback generico
]

def clean_output(testo_grezzo: str) -> str:
    testo_pulito = testo_grezzo
    testo_pulito = re.sub(r'\*+([^*]+)\*+', r'\1', testo_pulito)
    testo_pulito = re.sub(r'\_+([^_]+)\_+', r'\1', testo_pulito)
    testo_pulito = re.sub(r'\#+\s?([^#]+)', r'\1', testo_pulito)
    testo_pulito = re.sub(r'\[([^\]]+)\]\((?:[^)\\]|\\.)*\)', r'\1', testo_pulito)
    return testo_pulito

async def parser_url(url: str) -> dict: # prende in input un URL specifico e restituisce un dizionario con i risultati del parsing (url, dominio, titolo, testo in markdown e testo in html)
    browser_cfg = BrowserConfig(headless=True)

    path = urlparse(url).path
    urlname = os.path.basename(path)
    title_slug = os.path.splitext(urlname)[0] # ottengo il nome del URL senza estensione, che userò come titolo

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        for selector in CSS_SELECTORS:
            crawler_cfg = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                css_selector=selector,
                excluded_tags=["nav", "footer", "header", "aside", "figure", "img", "script", "style"],
                excluded_selector=".sal-content-whatsapp-channel, .sal-adv-slot, #relatedSearchesLeaf, .sal-widget-image,.sal-breadcrumb, .sal-social-share, .sal-tags" )
    
            result = await crawler.arun(url=url, config=crawler_cfg)
            if result.success and result.markdown and len(result.markdown.strip()) > 50:
                return {
                    "url": url,
                    "domain": "www.my-personaltrainer.it",
                    "title": title_slug,
                    "parsed_text": result.markdown,
                    "html_text": result.html or ""   
                }
            
        return {
            "url": url,
            "domain": "www.my-personaltrainer.it",
            "title": "Errore di parsing",
            "parsed_text": "",
            "html_text": ""
        }

def salva_risultati(parsed_text: str, html_text: str) -> None: # prende in input html_text e parsed_text della funzione precente e salva i file

    base_dir = os.path.dirname(os.path.abspath(__file__))
    risultati_dir = os.path.join(base_dir, "risultati")
    
    file_txt_path = os.path.join(risultati_dir, "Risultato_parser_mypersonaltrainer.txt")
    file_html_path = os.path.join(risultati_dir, "Risultato_html_parser_mypersonaltrainer.html")

    with open(file_txt_path, "w", encoding="utf-8") as f:
        f.write(clean_output(parsed_text))

    with open(file_html_path, "w", encoding="utf-8") as f:
        f.write(html_text)


# per ora questo main è solo un test, in futuro andrà modificato per processare più URL e per fare l'evaluation con il GS
async def main():

    url = "https://www.my-personaltrainer.it/salute-benessere/cervello.html"

    risultato = await parser_url(url)
    if risultato["parsed_text"]:
        salva_risultati(risultato["parsed_text"], risultato["html_text"])

        # EVALUATION
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        cervello_path = os.path.join(project_root, "gs_data", "mypersonaltrainer_gs", "cervello.txt")
        gs = open(cervello_path, "r", encoding="utf-8").read()
        evaluator=Evaluator(parsed_txt=risultato["parsed_text"], gs_txt=gs)
        print(evaluator.token_level_eval())
        print(evaluator.rouge_l_evaluation())
    else:
        print("Parsing fallito per tutti i selettori.")


if __name__ == "__main__":
    asyncio.run(main())