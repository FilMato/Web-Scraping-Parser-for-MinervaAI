import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode, BrowserConfig, CrawlerRunConfig, LLMConfig, DefaultMarkdownGenerator, PruningContentFilter
from crawl4ai.content_filter_strategy import LLMContentFilter

import re
import os
from urllib.parse import urlparse
import json

from parsers.parser_base import Parser

class Parser_UN(Parser):

    def __init__(self):
        super().__init__()
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
    def clean_output(text: str):

        text = re.sub(r'\[\]\([^)]+\)', '', text) #clear empty markdown links
        return text
    
    @staticmethod
    def _get_title(text: str) -> str:

        match_str = re.search(r'\<title>(.+)<\/title>', text)
        return match_str.group(1) if match_str else "no matches!"

    async def parser_url(self, url: str) -> dict: #input url, output json obj

        domain = urlparse(url).netloc
        browser_cfg = BrowserConfig(headless = True)
        title = "title"
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
                    url = url, 
                    config = selector_cfg
                )
                result_markdown = self.clean_output(result.markdown)
                if result.success and result_markdown and len(result_markdown.strip()) > 50:
                    print(title)
                    return {
                        "url": url,
                        "domain": domain,
                        "title": title,
                        "parsed_text": result_markdown,
                        "html_text": result.html or ""   
                    }
                
            result = await crawler.arun( #se non dovesse esistere alcun selector faccio il parsing un'ultima volta senza alcun selector
                url = url, 
                config = no_selector_cfg 
            )
            result_markdown = self.clean_output(result.markdown)
            if result.success and result_markdown and len(result_markdown.strip()) > 50:
                    print(title)
                    return {
                        "url": url,
                        "domain": domain,
                        "title": title,
                        "parsed_text": result_markdown,
                        "html_text": result.html or ""   
                    }
            return {
                "url": url,
                "domain": domain,
                "title": "Errore di parsing",
                "parsed_text": "",
                "html_text": ""
            }
        
    async def parser_url2(self, url: str, html_text: str) -> dict: #input url, output json obj

        domain = urlparse(url).netloc
        browser_cfg = BrowserConfig(headless = True)
        title = self._get_title(html_text)
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
                result_markdown = self.clean_output(result.markdown)
                if result.success and result_markdown and len(result_markdown.strip()) > 50:
                    print(title)
                    return {
                        "url": url,
                        "domain": domain,
                        "title": title,
                        "parsed_text": result_markdown,
                        "html_text": result.html or ""   
                    }
                
            result = await crawler.arun( #se non dovesse esistere alcun selector faccio il parsing un'ultima volta senza alcun selector
                url = f'raw:{html_text}', 
                config = no_selector_cfg 
            )
            result_markdown = self.clean_output(result.markdown)
            if result.success and result_markdown and len(result_markdown.strip()) > 50:
                    print(title)
                    return {
                        "url": url,
                        "domain": domain,
                        "title": title,
                        "parsed_text": result_markdown,
                        "html_text": result.html or ""   
                    }
            return {
                "url": url,
                "domain": domain,
                "title": "Errore di parsing",
                "parsed_text": "",
                "html_text": ""
            }  