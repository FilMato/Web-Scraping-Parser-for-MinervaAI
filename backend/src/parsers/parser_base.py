from abc import ABC, abstractmethod
from crawl4ai import AsyncWebCrawler, CacheMode, BrowserConfig, CrawlerRunConfig, DefaultMarkdownGenerator
from urllib.parse import urlparse

class Parser(ABC):
    
    def __init__(self):
        self.use_magic: bool = False
        self.wait_until_type: str = "domcontentloaded" 
        
        #dal sito di domcontentloaded :
        """The DOMContentLoaded event fires when the HTML document has been completely parsed, 
        and all deferred scripts (<script defer src="…"> and <script type="module">) have downloaded and executed. 
        It doesn't wait for other things like images, subframes, and async scripts to finish loading.""" # --> per ovviare a questo pericolo si utilizza un delay raginevolmente grande
        
        self.delay_time: float = 0.0
        self.remove_overlays: bool = False

    @property
    @abstractmethod
    def domain(self): #obbliga ogni sottoclasse a definire la propria proprietà (in questo caso il dominio)
        pass 

    async def parser_url(self, url: str) -> dict[str, str]:
        browser_cfg = BrowserConfig(headless=True)
        cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, 
                                magic=self.use_magic,
                                wait_until=self.wait_until_type,
                                delay_before_return_html=self.delay_time,
                                remove_overlay_elements=self.remove_overlays
                               )
        result = ""
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(url=url, config=cfg)
        if result.success and result.html:
            return await self.parser_url2(url, result.html)
        else:
             return {
                "url": url,
                "domain": self.domain(),
                "title": "Errore di parsing",
                "parsed_text": "",
                "html_text": ""
            }  

    @abstractmethod
    async def parser_url2(self, url: str, html_text: str) -> dict[str, str]:
        #Ogni sottoclasse deve implementrlo in un modo diverso
        pass