import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import os
from urllib.parse import urlparse
import random

from parsers.parser_base import Parser

CSS_SELECTORS = [
    "#toc-hook",          # id che contiene i contenuti che ci servono nella stramaggioranza degli URL
    ".sal-article-body",  # corpo articolo alternativo
    "article",            # se i due precedenti non esistono, prendo tutta la sezione article 
    "main"                # fallback generico
]

class MyPersonalTrainerParser(Parser):

    def __init__(self):
        super().__init__()

    async def parser_url(self, url: str) -> dict: # prende in input un URL specifico e restituisce un dizionario con i risultati del parsing (url, dominio, titolo, testo in markdown e testo in html)
        browser_cfg = BrowserConfig(
            headless=True,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )

        path = urlparse(url).path
        urlname = os.path.basename(path)
        titolo = os.path.splitext(urlname)[0].replace("-", " ").capitalize()

        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            for selector in CSS_SELECTORS:
                crawler_cfg = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    magic=True,
                    css_selector=selector,
                    excluded_tags=["nav", "footer", "header", "aside", "figure", "img", "script", "style"],
                    excluded_selector=".sal-content-whatsapp-channel, .sal-adv-slot, #relatedSearchesLeaf, .sal-widget-image,.sal-breadcrumb, .sal-social-share, .sal-tags",
                    wait_until="domcontentloaded",
                    delay_before_return_html=5.0
                )
        
                result = await crawler.arun(url=url, config=crawler_cfg)
                if result.success and result.markdown and len(result.markdown.strip()) > 50:
                    return {
                        "url": url,
                        "domain": "www.my-personaltrainer.it",
                        "title": titolo,
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
        
    async def parser_url2(self, url: str, html_text: str) -> dict:
        session_id = f"session_{random.randint(1000, 9999)}"
        
        browser_cfg = BrowserConfig(
            headless=True,
            # Cycle through a few common User-Agents
            headers={
                "User-Agent": random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
                ])
            }
        )
        path = urlparse(url).path
        urlname = os.path.basename(path)
        titolo = os.path.splitext(urlname)[0].replace("-", " ").capitalize()

        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            for selector in CSS_SELECTORS:
                crawler_cfg = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    css_selector=selector,
                    excluded_tags=["nav", "footer", "header", "aside", "figure", "img", "script", "style"],
                    excluded_selector=".sal-content-whatsapp-channel, .sal-adv-slot, #relatedSearchesLeaf, .sal-widget-image,.sal-breadcrumb, .sal-social-share, .sal-tags",
                    wait_until="domcontentloaded"
                )
                result = await crawler.arun(url=f"raw:{html_text}", config=crawler_cfg)
                if result.success and result.markdown and len(result.markdown.strip()) > 50:
                    return {
                        "url": url,
                        "domain": "www.my-personaltrainer.it",
                        "title": titolo,
                        "parsed_text": result.markdown,
                        "html_text": html_text 
                    }
            return {
                "url": url,
                "domain": "www.my-personaltrainer.it",
                "title": titolo,
                "parsed_text": "", 
                "html_text": html_text
            }