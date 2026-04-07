import json
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

#with this function we create a dictionary that contains all the json data
async def json_creator(url: str, domain: str, title: str, gold_text: str): #crawler is only used to retrieve the html text

    json_dict = {}
    browser_cfg = BrowserConfig(headless=False) #if true the page opened does not show
    crawler_cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:

        result = await crawler.arun(
            url=url, config=crawler_cfg
            )

        json_dict["url"] = url
        json_dict["domain"] = domain
        json_dict["title"] = title
        json_dict["html_text"] = result.html
        json_dict["gold_text"] = gold_text

        return json_dict

urls_to_process = [
    {"url" : "https://it.wikipedia.org/wiki/Roma", 
     "domain" : "it.wikipedia.org", 
     "title" : "Roma", 
     "golden_text" : "wikipedia_gs_txt/Roma_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Sistema_solare", 
     "domain" : "it.wikipedia.org", 
     "title" : "Sistema Solare", 
     "golden_text" : "wikipedia_gs_txt/Sistema_Solare_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Permesso_di_soggiorno_UE_per_soggiornanti_di_lungo_periodo", 
     "domain" : "it.wikipedia.org", 
     "title" : "Permesso di soggiorno UE per soggiornanti di lungo periodo", 
     "golden_text" : "wikipedia_gs_txt/GS_PermessoSoggiorno.txt"},

    {"url" : "https://it.wikipedia.org/wiki/Mercurio_(elemento_chimico)", 
     "domain" : "it.wikipedia.org", 
     "title" : "Mercurio (elemento chimico)", 
     "golden_text" : "wikipedia_gs_txt/Mercurio(elemento_chimico)_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Seconda_guerra_mondiale", 
     "domain" : "it.wikipedia.org", 
     "title" : "Seconda guerra mondiale", 
     "golden_text" : "wikipedia_gs_txt/Seconda_Guerra_Mondiale_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Leonardo_da_Vinci", 
     "domain" : "it.wikipedia.org", 
     "title" : "Leonardo da Vinci", 
     "golden_text" : "wikipedia_gs_txt/Leonardo_da_Vinci_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Equazione_di_Schr%C3%B6dinger", 
     "domain" : "it.wikipedia.org", 
     "title" : "Equazione di Schrödinger", 
     "golden_text" : "wikipedia_gs_txt/Equazione_di_Schrodinger_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Massa_(fisica)", 
     "domain" : "it.wikipedia.org", 
     "title" : "Massa (fisica)", 
     "golden_text" : "wikipedia_gs_txt/Massa_(fisica)_gs.txt"}

    ]

for current_page in urls_to_process:

    curr_url = current_page["url"]
    curr_domain = current_page["domain"]
    curr_title = current_page["title"]
    with open(current_page["golden_text"], "r", encoding="utf-8") as f: #gs.txt is a general txt file that contains the text manually pasted from the selected url
        curr_gold_text = f.read()

    json_data = asyncio.run(json_creator(curr_url,curr_domain,curr_title,curr_gold_text))

    #json returns a python list
    try:
        with open(f"dominio_{curr_domain}_gs.json", "r", encoding="utf-8") as r_file:
            data = json.load(r_file)
    except FileNotFoundError:
        data = []

    data.append(json_data)

    #write whole list to json file
    with open(f"dominio_{curr_domain}_gs.json", "w", encoding="utf-8") as a_file:
        json.dump(data, a_file, indent=2)







