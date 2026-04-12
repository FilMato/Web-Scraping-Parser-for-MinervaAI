import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import re
import os

def clean_output(testo_grezzo:str)->str:
    sezioni_da_elimnare=["## Note","## Voci correlate"]
    testo_pulito=testo_grezzo
    for titoli in sezioni_da_elimnare:
        if titoli in testo_pulito:
            testo_pulito=testo_pulito.split(titoli)[0]
    testo_pulito = re.sub(r'\[+\d{1,3}\]+\(https?://[^\)]+\)', '', testo_pulito)
    testo_pulito = re.sub(r'\*+([^*]+)\*+', r'\1', testo_pulito)
    testo_pulito = re.sub(r'\_+([^_]+)\_+', r'\1', testo_pulito)
    testo_pulito = re.sub(r'\#+\s?([^#]+)', r'\1', testo_pulito)
    testo_pulito = re.sub(r'\[([^\]]+)\]\((?:[^)\\]|\\.)*\)', r'\1', testo_pulito)
    return testo_pulito


async def main():
    browser_cfg=BrowserConfig(headless=True)

    crawler_cfg=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, excluded_tags=['nav','footer','header','aside','figure'], css_selector=".mw-parser-output", excluded_selector=".torna-a, .hatnote, .mw-editsection, .infobox, .sinottico, a[href*='Voci_di_qualità'], a[href*='Politica_di_protezione'], .thumb, .gallery, #coordinates, .navbox, .noviewer, .timeline-wrapper, p[typeof*='mw:Transclusion'], .ambox, table.noprint[style*='float']" )

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        
        result= await crawler.arun(
            url="https://it.wikipedia.org/wiki/Mercurio_(elemento_chimico)",
            config=crawler_cfg
        )
        
        # Ottieni il percorso assoluto della cartella in cui si trova QUESTO script (es. backend/src/)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Definisci il percorso della nuova cartella "risultati"
        risultati_dir = os.path.join(base_dir, "risultati")
        
        file_txt_path = os.path.join(risultati_dir, "Risultato_parser_wikipedia.txt")
        file_html_path = os.path.join(risultati_dir, "Risultato_html_parser_wikipedia.html")

        # Salva i file
        with open(file_txt_path, "w", encoding="utf-8") as f:
            f.write(clean_output(result.markdown))
            
        with open(file_html_path, "w", encoding="utf-8") as f1:
            f1.write(result.html)

if __name__ == "__main__":
    asyncio.run(main())