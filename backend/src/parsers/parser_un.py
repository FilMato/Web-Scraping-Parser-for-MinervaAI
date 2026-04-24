from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CacheMode, BrowserConfig, CrawlerRunConfig, DefaultMarkdownGenerator

import re

from parsers.parser_base import Parser

class Parser_UN(Parser):

    def __init__(self):
        super().__init__()
        self.domain = "un.org"
        self.css_selectors = [
                ".body-article",          
                ".radix-layouts-content", 
                ".post-content",          
                ".field-name-body",  
                ".main-container container",     
                "#main-content",
                "#content",              
                "#main"                     
            ]

    @staticmethod
    def _clean_output(text: str):
        text = re.sub(r'\[\]\([^)]+\)', '', text) #clear empty markdown links
        return text

    async def parser_url(self, url: str) -> dict: #input url, output json obj
        browser_cfg = BrowserConfig(headless=True)
       # domain = urlparse(url).netloc
        cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        result = ""
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(url=url, config=cfg)
        if result.success and result.html:
            return self.parser_url2(url, result.html)
        else:
             return {
                "url": url,
                "domain": self.domain,
                "title": "Errore di parsing",
                "parsed_text": "",
                "html_text": ""
            }  
        
    async def parser_url2(self, url: str, html_text: str) -> dict: #input url, output json obj
       # domain = urlparse(url).netloc
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
        no_selector_cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS,
                                            exclude_all_images= True,
                                            exclude_social_media_links=True,
                                            excluded_tags=['title', 'nav', 'header', 'footer','button', 'video'],
                                            excluded_selector=".views-field-field-news-tags, .block-content-footer, .type-entermedia_image, #player-gui, #addtoany, #sharing_widget, #skip-link, .image-caption, #sharing-widget, #breadcrumbs, #more_button, .photo-credit, .page-header, .fusion-video, #player-controls, .wp-caption-text",
                                            markdown_generator=md_generator)
        
        async with AsyncWebCrawler(config=browser_cfg) as crawler:

            for selector in self.css_selectors:
                selector_cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS,
                                        css_selector=selector,
                                        exclude_all_images= True,
                                        exclude_social_media_links=True,
                                        excluded_tags=['nav', 'header', 'footer','button', 'video'],
                                        excluded_selector=".views-field-field-news-tags, .block-content-footer, .type-entermedia_image, #player-gui, #addtoany, #sharing_widget, #skip-link, .image-caption, #sharing-widget, #breadcrumbs, #more_button, .photo-credit, .page-header, .fusion-video, #player-controls, .wp-caption-text",
                                        markdown_generator=md_generator)
                result = await crawler.arun(
                    url = f'raw:{html_text}', 
                    config = selector_cfg
                )
                result_markdown = self._clean_output(result.markdown)
                if result.success and result_markdown and len(result_markdown.strip()) > 50:
                    return {
                        "url": url,
                        "domain": self.domain,
                        "title": title,
                        "parsed_text": result_markdown,
                        "html_text": result.html or ""   
                    }
                
            result = await crawler.arun( #se non dovesse esistere alcun selector faccio il parsing un'ultima volta senza alcun selector
                url = f'raw:{html_text}', 
                config = no_selector_cfg 
            )
            result_markdown = self._clean_output(result.markdown)
            if result.success and result_markdown and len(result_markdown.strip()) > 50:
                    return {
                        "url": url,
                        "domain": self.domain,
                        "title": title,
                        "parsed_text": result_markdown,
                        "html_text": result.html or ""   
                    }
            return {
                "url": url,
                "domain": self.domain,
                "title": "Errore di parsing",
                "parsed_text": "",
                "html_text": ""
            }  