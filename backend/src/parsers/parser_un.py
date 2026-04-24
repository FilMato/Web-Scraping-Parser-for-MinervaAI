from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CacheMode, BrowserConfig, CrawlerRunConfig, DefaultMarkdownGenerator
import re
from parsers.parser_base import Parser



_CSS_SELECTORS = [
                ".body-article",          
                ".radix-layouts-content", 
                ".post-content",          
                ".field-name-body",  
                ".main-container container",     
                "#main-content",
                "#content",              
                "#main"                     
            ]

_EXCLUDED_TAGS = ['title', 
                  'nav', 
                  'header', 
                  'footer',
                  'button', 
                  'video']

_EXCLUDED_SELECTOR = ".views-field-field-news-tags, .block-content-footer, .type-entermedia_image, #player-gui, #addtoany, #sharing_widget, #skip-link, .image-caption, #sharing-widget, #breadcrumbs, #more_button, .photo-credit, .page-header, .fusion-video, #player-controls, .wp-caption-text"

def _clean_output(text: str) -> str:
        text = re.sub(r'\[\]\([^)]+\)', '', text) #clear empty markdown links
        return text


class Parser_UN(Parser):

    def __init__(self):
        super().__init__()
        self.use_magic: bool = False
        self.wait_until_type: str = "domcontentloaded" 
        self.delay_time: float = 0.0
        self.remove_overlays: bool = False
        self._domain = "un.org"

    @property
    def domain(self):
         return self._domain
        
    async def parser_url2(self, url: str, html_text: str) -> dict[str, str]: #input url, output json obj
    
        browser_cfg = BrowserConfig(headless = True)
        soup = BeautifulSoup(html_text, "html.parser")
        title = soup.select_one("title")
        title = title.text.strip() if title else "Errore nel trovare il titolo"
        md_generator = DefaultMarkdownGenerator(
            options={
                "ignore_images": True
            },
            content_source= "cleaned_html"
        )
        no_selector_cfg = CrawlerRunConfig(cache_mode = CacheMode.BYPASS,
                                            exclude_all_images = True,
                                            exclude_social_media_links =True,
                                            excluded_tags = _EXCLUDED_TAGS,
                                            excluded_selector = _EXCLUDED_SELECTOR,
                                            markdown_generator=md_generator)
        
        async with AsyncWebCrawler(config=browser_cfg) as crawler:

            for selector in _CSS_SELECTORS:
                selector_cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS,
                                        css_selector = selector,
                                        exclude_all_images = True,
                                        exclude_social_media_links = True,
                                        excluded_tags = _EXCLUDED_TAGS,
                                        excluded_selector = _EXCLUDED_SELECTOR,
                                        markdown_generator=md_generator)
                result = await crawler.arun(
                    url = f'raw:{html_text}', 
                    config = selector_cfg
                )
                result_markdown = _clean_output(result.markdown)
                if result.success and result_markdown and len(result_markdown.strip()) > 50:
                    return {
                        "url": url,
                        "domain": self._domain,
                        "title": title,
                        "parsed_text": result_markdown,
                        "html_text": result.html or ""   
                    }
                
            result = await crawler.arun( #se non dovesse esistere alcun selector faccio il parsing un'ultima volta senza alcun selector
                url = f'raw:{html_text}', 
                config = no_selector_cfg 
            )
            result_markdown = _clean_output(result.markdown)
            if result.success and result_markdown and len(result_markdown.strip()) > 50:
                    return {
                        "url": url,
                        "domain": self._domain,
                        "title": title,
                        "parsed_text": result_markdown,
                        "html_text": result.html or ""   
                    }
            return {
                "url": url,
                "domain": self._domain,
                "title": "Errore di parsing",
                "parsed_text": "",
                "html_text": ""
            }  