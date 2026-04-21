import asyncio #QUESTO IMPORT SERVE A GESTIRE I LOOP ASINCRONI(ALTRIMENTI QUANDO CERCO LE COSE SUL WEB TUTTO IL RESTO SI BLOCCA)
from crawl4ai import AsyncWebCrawler,BrowserConfig,CrawlerRunConfig,CacheMode
import re
from bs4 import BeautifulSoup
from parsers.parser_base import Parser

def clean_output(testo_grezzo:str)->str:
    sezioni_da_elimnare=["Related Content","Also in this series"]
    testo_pulito=testo_grezzo
    testo_pulito = re.sub(r'###### Watch:.*\n?', '', testo_pulito)
    testo_pulito = re.sub(r'\#+\s?([^#]+)', r'\1', testo_pulito)
    for titoli in sezioni_da_elimnare:
        if titoli in testo_pulito:
            testo_pulito=testo_pulito.split(titoli)[0]
    testo_pulito=re.sub(r'Share News\n?', '', testo_pulito)
    testo_pulito = re.sub(r'\_+([^_]+)\_+', r'\1', testo_pulito)
    testo_pulito = re.sub(r'\*+([^*]+)\*+', r'\1', testo_pulito)
    testo_pulito = re.sub(r'\[Read more about.*?\]\(.*?\)', '', testo_pulito)
    return testo_pulito

class PremierLeagueParser(Parser):
    def __init__(self):
        super().__init__()

    async def parser_url(self,url:str)->dict:
        browser_cfg=BrowserConfig(headless=True) #IMPOSTATO =FALSE MI APRE LA FINESTRA DEL URL OGNI VOLTA CHE RUNNO, PER RISPARMIARE LO METTEREMO =TRUE

        crawler_cfg=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS, #PER AVERE SEMPRE DATI AGGIORNATI)
            css_selector=".main-content",
            excluded_selector="picture, .article__tags, .video-player, .video-embedded, .article__author, .article__publish-date, .sg-wrapper, .sg-skipnav-container, .js-live-audio, noscript, .embeddable-article, .content-grid, .filters-chips, .club-badge, .filters, .u-show-tablet, .standings-row__team-name-short, .tab-navigation, .standings-row__form, th[scope='col']:last-child, .standings__segmented-controls, .transfer-centre__tabs, .page-header__wrapper, .standings-footer, .article__header-title, .embeddable-photo__description, .content-rail, .generic-promo, .global-ad-slot",
            wait_until="networkidle",)
        async with AsyncWebCrawler(config=browser_cfg) as crawler: #
            
            result= await crawler.arun(url=url, config=crawler_cfg)
            soup = BeautifulSoup(result.html, "html.parser")
            titolo_estratto = (
            # Prova i selettori più comuni di Premier League
            soup.select_one(".article__header-title") or
            soup.select_one("h1") or
            soup.select_one("title")
            )
            titolo_estratto = titolo_estratto.text.strip() if titolo_estratto else "Titolo non trovato"
            result_markdown=clean_output(result.markdown)
            if result.success and result_markdown:
                return{
                    "url":url,
                    "domain":"www.premierleague.com",
                    "title":titolo_estratto,
                    "parsed_text":result_markdown,
                    "html_text":result.html or ""
                }
        return {
            "url":url,
            "domain":"www.premierleague.com",
            "title":"Errore di parsing",
            "parsed_text":"",
            "html_text":"" 
        }
    
    async def parser_url2(self, url: str, html_text: str) -> dict:
        soup = BeautifulSoup(html_text, "html.parser")
        titolo_estratto = (
            soup.select_one(".article__header-title") or
            soup.select_one("h1") or
            soup.select_one("title")
        )
        titolo_estratto = titolo_estratto.text.strip() if titolo_estratto else "Titolo non trovato"
        browser_cfg = BrowserConfig(headless=True)
        crawler_cfg = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            css_selector=".main-content",
            excluded_selector="picture, .article__tags, .video-player, .video-embedded, .article__author, .article__publish-date, .sg-wrapper, .sg-skipnav-container, .js-live-audio, noscript, .embeddable-article, .content-grid, .filters-chips, .club-badge, .filters, .u-show-tablet, .standings-row__team-name-short, .tab-navigation, .standings-row__form, th[scope='col']:last-child, .standings__segmented-controls, .transfer-centre__tabs, .page-header__wrapper, .standings-footer, .article__header-title, .embeddable-photo__description, .content-rail, .generic-promo, .global-ad-slot",
            wait_until="networkidle",
        )
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(url=f"raw:{html_text}", config=crawler_cfg)
            if result.success and result.markdown:
                result_markdown = clean_output(result.markdown)
                if result_markdown:
                    return {
                        "url": url,
                        "domain": "www.premierleague.com",
                        "title": titolo_estratto,
                        "parsed_text": result_markdown,
                        "html_text": html_text
                    }
        return {
            "url": url,
            "domain": "www.premierleague.com",
            "title": titolo_estratto,
            "parsed_text": "",
            "html_text": html_text
        }
    
                

