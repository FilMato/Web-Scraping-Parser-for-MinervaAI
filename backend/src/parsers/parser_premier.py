from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import re
from bs4 import BeautifulSoup
from parsers.parser_base import Parser


def _clean_output(testo_grezzo: str) -> str:
    sezioni_da_eliminare = ["Related Content", "Also in this series", "Club reports"]
    testo_pulito = testo_grezzo
    testo_pulito = re.sub(r'###### Watch:.*\n?', '', testo_pulito)
    for titoli in sezioni_da_eliminare:
        if titoli in testo_pulito:
            testo_pulito = testo_pulito.split(titoli)[0]
    testo_pulito = re.sub(r'Share News\n?', '', testo_pulito)
    testo_pulito = re.sub(r'\[Read more about.*?\]\(.*?\)', '', testo_pulito)
    return testo_pulito


def _postprocess_markdown(text: str) -> str:
    """
    Pulisce l'output markdown di Crawl4AI:
    1. Rimuove immagini markdown  ![alt](url) che diventano token rumore
    2. Converte tabelle markdown  | col1 | col2 |  in formato tab-separated
    """
    # Rimuovi immagini markdown: ![alt](url) o ![](url)
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text)

    # Converti tabelle markdown in righe tab-separated
    lines = text.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|') and '|' in stripped[1:-1]:
            inner = stripped[1:-1]
            cells = [c.strip() for c in inner.split('|')]
            # Salta le righe separatore  | --- | --- | --- |
            if all(re.match(r'^[-: ]+$', c) or c == '' for c in cells):
                continue
            row_text = '\t'.join(cells)
            if row_text.strip():
                result.append(row_text)
        else:
            result.append(line)
    return '\n'.join(result)


class PremierLeagueParser(Parser):
    def __init__(self):
        super().__init__()
        self.use_magic: bool = False
        self.wait_until_type: str = "domcontentloaded"
        self.delay_time: float = 5.0

    @property
    def domain(self) -> str:
        return "www.premierleague.com"

    async def parser_url2(self, url: str, html_text: str) -> dict[str, str]:
        soup = BeautifulSoup(html_text, "html.parser")
        titolo_estratto = (
            soup.select_one(".article__header-title")
            or soup.select_one("h1")
            or soup.select_one("title")
        )
        titolo_estratto = titolo_estratto.text.strip() if titolo_estratto else "Titolo non trovato"

        browser_cfg = BrowserConfig(headless=True)
        crawler_cfg = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            css_selector=".main-content",
            excluded_selector=(
                "#onetrust-consent-sdk, picture, .article__tags, .video-player, "
                ".video-embedded, .article__author, .article__publish-date, "
                ".sg-wrapper, .sg-skipnav-container, .js-live-audio, noscript, "
                ".embeddable-article, .content-grid, .filters-chips, .club-badge, "
                ".filters, .u-show-tablet, .standings-row__team-name-short, "
                ".tab-navigation, .standings-row__form, "
                "th[scope='col']:last-child, .standings__segmented-controls, "
                ".transfer-centre__tabs, .page-header__wrapper, .standings-footer, "
                ".article__header-title, .embeddable-photo__description, "
                ".content-rail, .generic-promo, .global-ad-slot, "
                ".injury-news__table-row > *:nth-child(3), "
                ".transfer-centre__table-row > *:nth-child(3), "
                ".scoreboard__content, .motm--winner, .match-report--club, "
                ".scoreboard-bottom__cta-all-matches, .base-TabsList-horizontal"
            ),
            wait_until="domcontentloaded",
        )

        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(url=f"raw:{html_text}", config=crawler_cfg)
            if result.success and result.markdown:
                # Postprocessing: rimuovi immagini e converti tabelle in tsv
                cleaned = _postprocess_markdown(result.markdown)
                result_markdown = _clean_output(cleaned)
                if result_markdown:
                    return {
                        "url": url,
                        "domain": self.domain,
                        "title": titolo_estratto,
                        "parsed_text": result_markdown,
                        "html_text": html_text,
                    }

        return {
            "url": url,
            "domain": self.domain,
            "title": titolo_estratto,
            "parsed_text": "",
            "html_text": html_text,
        }