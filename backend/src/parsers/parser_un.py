import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import re

from parsers.parser_base import Parser

class Parser_UN(Parser):

    def __init__(self):
        super().__init__()
    
    