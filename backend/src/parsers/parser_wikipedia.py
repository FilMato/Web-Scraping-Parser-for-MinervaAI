from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import re
import os
from urllib.parse import urlparse, unquote

from parsers.parser_base import Parser

def clean_output(testo_grezzo:str)->str:
    sezioni_da_elimnare=["## Note","## Voci correlate"]
    testo_pulito=testo_grezzo
    for titoli in sezioni_da_elimnare:
        if titoli in testo_pulito:
            testo_pulito=testo_pulito.split(titoli)[0]
    testo_pulito = re.sub(r'\[+\d{1,3}\]+\(https?://[^\)]+\)', '', testo_pulito)
    return testo_pulito


class WikipediaParser(Parser):

    def __init__(self):
        super().__init__()
        self.use_magic: bool = False
        self.wait_until_type: str = "domcontentloaded" 
        self.delay_time: float = 0.0
        self.remove_overlays: bool = False
        self._domain = "it.wikipedia.org"

    @property
    def domain(self):
        return self._domain  
    
    async def parser_url2(self, url: str, html_text: str) -> dict:
        browser_cfg = BrowserConfig(headless=True)

        path = unquote(urlparse(url).path)
        urlname = os.path.basename(path)
        titolo = os.path.splitext(urlname)[0].replace("-", " ").capitalize()
        
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            crawler_cfg = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS, 
                excluded_tags=['nav','footer','header','aside','figure'], 
                css_selector=".mw-parser-output", 
                excluded_selector=".torna-a, .hatnote, .mw-editsection, .infobox, .sinottico, a[href*='Voci_di_qualità'], a[href*='Politica_di_protezione'], .thumb, .gallery, #coordinates, .navbox, .noviewer, .timeline-wrapper, p[typeof*='mw:Transclusion'], .ambox, table.noprint[style*='float'], .vector-body-before-content, .mw-file-element" 
            )
            
            result = await crawler.arun(url=f"raw:{html_text}", config=crawler_cfg)
            
            if result.success and result.markdown:
                result_markdown = clean_output(result.markdown)
                
                if result_markdown and len(result_markdown.strip()) > 50:
                    return {
                        "url": url,
                        "domain": self.domain,
                        "title": titolo,
                        "parsed_text": result_markdown,
                        "html_text": html_text
                    }
                
            return {
                "url": url,
                "domain": self.domain,
                "title": titolo,
                "parsed_text": "",
                "html_text": html_text
            }
        

