from crawl4ai import AsyncWebCrawler,BrowserConfig,CrawlerRunConfig,CacheMode
import re
from bs4 import BeautifulSoup
from parsers.parser_base import Parser


def _clean_output(testo_grezzo:str)->str:
        sezioni_da_elimnare=["Related Content","Also in this series","Club reports"]
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
        self.use_magic: bool = False
        self.wait_until_type: str = "domcontentloaded" 
        self.delay_time: float = 5.0
        self.remove_overlays: bool = False
        self._domain = "premierleague.com"

    @property
    def domain(self) -> str:
        return self._domain

    async def parser_url2(self, url: str, html_text: str) -> dict[str, str]:
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
            excluded_selector="#onetrust-consent-sdk,picture, .article__tags, .video-player, .video-embedded, .article__author, .article__publish-date, .sg-wrapper, .sg-skipnav-container, .js-live-audio, noscript, .embeddable-article, .content-grid, .filters-chips, .club-badge, .filters, .u-show-tablet, .standings-row__team-name-short, .tab-navigation, .standings-row__form, th[scope='col']:last-child, .standings__segmented-controls, .transfer-centre__tabs, .page-header__wrapper, .standings-footer, .article__header-title, .embeddable-photo__description, .content-rail, .generic-promo, .global-ad-slot, .injury-news__table-row > *:nth-child(3), .transfer-centre__table-row > *:nth-child(3), .scoreboard__content, .motm--winner, .match-report--club, .scoreboard-bottom__cta-all-matches, .base-TabsList-horizontal",
            wait_until="domcontentloaded",
        )
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(url=f"raw:{html_text}", config=crawler_cfg)
            if result.success and result.markdown:
                result_markdown = _clean_output(result.markdown)
                if result_markdown:
                    return {
                        "url": url,
                        "domain": self.domain,
                        "title": titolo_estratto,
                        "parsed_text": result_markdown,
                        "html_text": html_text
                    }
        return {
            "url": url,
            "domain": self.domain,
            "title": titolo_estratto,
            "parsed_text": "",
            "html_text": html_text,
        }
    
                

