import asyncio
import requests
from bs4 import BeautifulSoup
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
    def _clean_output(text: str):
        text = re.sub(r'\[\]\([^)]+\)', '', text) #clear empty markdown links
        return text

    async def parser_url(self, url: str) -> dict: #input url, output json obj
        domain = urlparse(url).netloc

        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        title = soup.title.get_text()
        title = soup.select_one("title")
        title = title.text.strip() if title else "Errore nel trovare il titolo"

        browser_cfg = BrowserConfig(headless = True)
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
                                            excluded_selector=".context-un_news_large_credi, #block-views-block-content-fields-block-tags, .minimal-share-wrapper, #block-content-footer, .views-field-field-news-tags, .block-content-footer, .type-entermedia_image, #player-gui, #addtoany, #sharing_widget, #skip-link, .image-caption, #sharing-widget, #breadcrumbs, #more_button, .photo-credit, .page-header, .fusion-video, #player-controls, .wp-caption-text",
                                            markdown_generator=md_generator)
        
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            for selector in self.css_selectors:
                selector_cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS,
                                        css_selector=selector,
                                        exclude_all_images= True,
                                        exclude_social_media_links=True,
                                        excluded_tags=['nav', 'header', 'footer','button', 'video'],
                                        excluded_selector=".context-un_news_large_credi, #block-views-block-content-fields-block-tags, .minimal-share-wrapper, #block-content-footer, #sidebar_second, .views-field-field-news-tags, .block-content-footer, .type-entermedia_image, #player-gui, #addtoany, #sharing_widget, #skip-link, .image-caption, #sharing-widget, #breadcrumbs, #more_button, .photo-credit, .page-header, .fusion-video, #player-controls, .wp-caption-text",
                                        markdown_generator=md_generator)
                result = await crawler.arun(
                    url = url, 
                    config = selector_cfg
                )
                result_markdown = self._clean_output(result.markdown)
                if result.success and result_markdown and len(result_markdown.strip()) > 50:
                    print(title)
                    return {
                        "url": url,
                        "domain": domain,
                        "title": title,
                        "parsed_text": result_markdown,
                        "html_text": result.html or ""   
                    }
            #se non dovesse esistere alcun selector faccio il parsing un'ultima volta senza specificare il selector
            result = await crawler.arun(
                url = url, 
                config = no_selector_cfg 
            )
            result_markdown = self._clean_output(result.markdown)
            if result.success and result_markdown and len(result_markdown.strip()) > 50:
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
            result_markdown = self._clean_output(result.markdown)
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