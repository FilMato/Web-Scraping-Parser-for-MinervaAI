import asyncio #QUESTO IMPORT SERVE A GESTIRE I LOOP ASINCRONI(ALTRIMENTI QUANDO CERCO LE COSE SUL WEB TUTTO IL RESTO SI BLOCCA)
from crawl4ai import AsyncWebCrawler,BrowserConfig,CrawlerRunConfig,CacheMode
import re

from backend.src.evaluator import Evaluator

def clean_output(testo_grezzo:str)->str:
    
    sezioni_da_elimnare=["## Note","## Voci correlate"]
    testo_pulito=testo_grezzo
    for titoli in sezioni_da_elimnare:
        if titoli in testo_pulito:
            testo_pulito=testo_pulito.split(titoli)[0]
    testo_pulito = re.sub(r'\[+\d{1,3}\]+\(https?://[^\)]+\)', '', testo_pulito) #[1] etc
 
    return testo_pulito



async def main():
    browser_cfg=BrowserConfig(headless=True) #IMPOSTATO =FALSE MI APRE LA FINESTRA DEL URL OGNI VOLTA CHE RUNNO, PER RISPARMIARE LO METTEREMO =TRUE

    crawler_cfg=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, excluded_tags=['nav','footer','header','aside','figure'], css_selector=".mw-parser-output", excluded_selector=".torna-a, .hatnote, .mw-editsection, .infobox, .sinottico, a[href*='Voci_di_qualità'], a[href*='Politica_di_protezione'], .thumb, .gallery, #coordinates, .navbox, .noviewer, .timeline-wrapper, p[typeof*='mw:Transclusion'], .ambox, table.noprint[style*='float']" ) #QUESTO SERVE AD IGNORARARE EVENTUALI PAGINE GIA PRESENTI IN CACHE E A FORZARE A CERCARLE OGNI VOLTA DAL WEB(IMPORTANTE 
                                                              #PER AVERE SEMPRE DATI AGGIORNATI)



    async with AsyncWebCrawler(config=browser_cfg) as crawler: #
        
        result= await crawler.arun( #SCARICA LA PAGINA INDICATA NEL URL E APPLICA LA CONFIGURAZIONE INDICATA, GRAZIE AD AWAIT IL RPOGRAMMA SI FERMA A QUESTA RIGA FINCHE 
                                    #IL DOWNLOAD NON FINISCE, PERMETTENDO AL PROCESSORE DI GESTIRE ALTRE ATTIVITA

            url="https://it.wikipedia.org/wiki/Leonardo_da_Vinci",
            config=crawler_cfg
        )

        #print(clean_output(result.html))
        with open("Risultato_parser.html","w",encoding="utf-8") as f:
            f.write(result.html)

        """with open("Risultato_parser.txt", "r", encoding= "utf-8") as ps:
            p_s = ps.read()
        
        with open("gs_data/wikipedia_gs_txt/Leonardo_da_Vinci_gs.txt", "r", encoding= "utf-8") as gs:
            g_s = gs.read()

        ev = Evaluator(g_s, p_s)
        print(len(g_s), len(p_s))
        print("token level eval:" + ev.token_level_eval())
        print("rouge l eval:" + ev.rouge_l_evaluation())"""
        #CI SONO VARI RISULTATI CHE SARANNO CONTENUTI IN RESULT: - MARKDOWN: 
        #                                                        - HTML: MI RESTITUISCE L'HTML ORIGINALE DELLA PAGINA
        #                                                        - CLEANED_HTML: UNA VERSIONE HTML GIA "PULITA"
        #                                                        - SUCCESS: VALORE BOOLEANO, MI DICE SE IL CRAWLING VA A BUON FINE
        #                                                        - ERROR_MESSAGE: NEL CASO SUCCES=FALSE CONTIENE L'ERRORE                                                     
asyncio.run(main()) #SERVE A RUNNARE UNA FUNZIONA DEFINITA CON ASYNC DEF


#NEL CONTESTO DEL NOSTRO PROGETTO QUESTA è LA BASE DA CUI PARTIRE, PER MODIFICARE AL MEGLIO LA CONFIGURAZIOEN IN MODO DA OTTENERE IL RISULTATO MIGLIORE
#DOVREMO: -MODIFICARE LA CONFIGURAZIOEN DEL CRAWLERRUNCONFIG, PER ESEMPIO SI POSSONO IGNORARE DEI TAG HTML, OPPURE RIMUOVERE EVENTUALI POP-UP, MENU,TABELLE ECC..(BISOGNA 
#          CONFRONTARE IL RISULTATO COL GS IN MODO DA CAPIRE COME SI STA ANDANDO) 
#         -SELEZIONARE LE PAGINE E GLI URL DA USARE COME BASE(CON UN LAYOUT + DIVERSO POSSIBILE ED EVITANDO DI PRENDERE LA PAGINA PRINCIPALE)
#         -LAVORARE SUL RISULTATO OTTENUTO DOPO IL PARSING, PER RIMUOVERE PAROLE O PATTERN DI TESTO RIPETITIVI COME STRINGHE DEL TIPO [MODIFICA TESTO,ISCRIVI ALLA NEWSLATTER ECC...]
#IN SOSTAZNA IL PROCESSO è COMPOSTO DA 3 PARTI: 1) LAVORARE SULLA CONFIGURAZIONE DI CRAWLERCONFIG
#                                               2) PULIZIA DEL TESTO DOPO IL PARSING
#                                               3) VERIFICARE IL RISULTATO OTTENUTO RISPETTO AL GS