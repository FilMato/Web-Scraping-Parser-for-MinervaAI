import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode, BrowserConfig, CrawlerRunConfig, LLMConfig, DefaultMarkdownGenerator, PruningContentFilter
from crawl4ai.content_filter_strategy import LLMContentFilter

import re
import os
from urllib.parse import urlparse
import json

from  parser_base import Parser

class Parser_UN(Parser):

    def __init__(self):
        super().__init__()
        self.css_selectors = [
                ".body-article",          
                ".radix-layouts-content", 
                ".post-content",          
                ".field-name-body",  
                ".main-container container"     
                "#main-content",
                "#content",              
                "#main",
                ""                       
            ]
        

    @staticmethod
    def clean_output(text: str):
        text = re.sub(r'\[\]\([^)]+\)', '', text) #clear empty markdown links
        return text
    
    async def parser_url(self, url: str) -> dict: #input url, output json obj

        path = urlparse(url).path
        urlname = os.path.basename(path)
        titolo = os.path.splitext(urlname)[0].replace("-", " ").capitalize()

        browser_cfg = BrowserConfig(headless=False)
       
        md_generator = DefaultMarkdownGenerator(
            options={
                "ignore_images": True
            },
            content_source= "cleaned_html"
        )
        
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
        
            for selector in self.css_selectors:
                crawler_cfg_ok = CrawlerRunConfig(cache_mode=CacheMode.BYPASS,
                                                css_selector=selector,
                                                exclude_all_images= True,
                                                exclude_social_media_links=True,
                                                excluded_tags=['img', 'nav', 'header', 'footer','button', 'video'],
                                                excluded_selector=".views-field-field-news-tags, .block-content-footer, .type-entermedia_image, #player-gui, #addtoany, #sharing_widget, #skip-link, .image-caption, #sharing-widget, #breadcrumbs, #more_button, .photo-credit, .page-header, .fusion-video, #player-controls, .wp-caption-text",
                                                markdown_generator=md_generator
                                            )
                result = await crawler.arun(
                    url = url, config=crawler_cfg_ok
                )
                result_markdown = self.clean_output(result.markdown)
                if result.success and result_markdown and len(result_markdown.strip()) > 50:
                    return {
                        "url": url,
                        "domain": "it.wikipedia.org",
                        "title": titolo,
                        "parsed_text": result_markdown,
                        "html_text": result.html or ""   
                    }
                
            return {
                "url": url,
                "domain": "it.wikipedia.org",
                "title": "Errore di parsing",
                "parsed_text": "",
                "html_text": ""
            }  