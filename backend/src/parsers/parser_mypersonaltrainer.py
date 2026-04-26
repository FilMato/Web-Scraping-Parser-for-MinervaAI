from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import os
from urllib.parse import urlparse

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
        self.use_magic: bool = True
        self.wait_until_type: str = "domcontentloaded" 
        self.delay_time: float = 1.0
        self.remove_overlays: bool = False
        self._domain = "www.my-personaltrainer.it"

    @property
    def domain(self):
        return self._domain
      
        
    async def parser_url2(self, url: str, html_text: str) -> dict:
        browser_cfg = BrowserConfig(headless=True)
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
                        "domain": self._domain,
                        "title": titolo,
                        "parsed_text": result.markdown,
                        "html_text": html_text 
                    }
            return {
                "url": url,
                "domain": self._domain,
                "title": titolo,
                "parsed_text": "", 
                "html_text": html_text
            }