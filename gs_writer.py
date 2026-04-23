import json
import os
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

#with this function we create a dictionary that contains all the json data
async def json_creator(url: str, domain: str, title: str, gold_text: str): #crawler is only used to retrieve the html text

    json_dict = {}
    browser_cfg = BrowserConfig(headless=True) #if true the page opened does not show
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
     "golden_text" : "gs_data/wikipedia_gs_txt/Roma_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Sistema_solare", 
     "domain" : "it.wikipedia.org", 
     "title" : "Sistema Solare", 
     "golden_text" : "gs_data/wikipedia_gs_txt/Sistema_Solare_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Permesso_di_soggiorno_UE_per_soggiornanti_di_lungo_periodo", 
     "domain" : "it.wikipedia.org", 
     "title" : "Permesso di soggiorno UE per soggiornanti di lungo periodo", 
     "golden_text" : "gs_data/wikipedia_gs_txt/GS_PermessoSoggiorno.txt"},

    {"url" : "https://it.wikipedia.org/wiki/Mercurio_(elemento_chimico)", 
     "domain" : "it.wikipedia.org", 
     "title" : "Mercurio (elemento chimico)", 
     "golden_text" : "gs_data/wikipedia_gs_txt/Mercurio(elemento_chimico)_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Seconda_guerra_mondiale", 
     "domain" : "it.wikipedia.org", 
     "title" : "Seconda guerra mondiale", 
     "golden_text" : "gs_data/wikipedia_gs_txt/Seconda_Guerra_Mondiale_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Leonardo_da_Vinci", 
     "domain" : "it.wikipedia.org", 
     "title" : "Leonardo da Vinci", 
     "golden_text" : "gs_data/wikipedia_gs_txt/Leonardo_da_Vinci_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Equazione_di_Schr%C3%B6dinger", 
     "domain" : "it.wikipedia.org", 
     "title" : "Equazione di Schrödinger", 
     "golden_text" : "gs_data/wikipedia_gs_txt/Equazione_di_Schrodinger_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Massa_(fisica)", 
     "domain" : "it.wikipedia.org", 
     "title" : "Massa (fisica)", 
     "golden_text" : "gs_data/wikipedia_gs_txt/Massa_(fisica)_gs.txt"},

     {"url" : "https://it.wikipedia.org/wiki/Antico_Egitto", 
     "domain" : "it.wikipedia.org", 
     "title" : "Antico Egitto", 
     "golden_text" : "gs_data/wikipedia_gs_txt/Antico_Egitto_gs.txt"},

     {"url" : "https://www.un.org/fr/about-us/history-of-the-un/san-francisco-conference", 
     "domain" : "un.org", 
     "title" : "La Conférence de San Francisco", 
     "golden_text" : "gs_data/un_gs_txt/La_Conference_de_San_Francisco_gs.txt"},

     {"url" : "https://www.un.org/es/common-agenda/implementation", 
     "domain" : "un.org", 
     "title" : "Implementacion", 
     "golden_text" : "gs_data/un_gs_txt/Implementacion_gs.txt"},

     {"url" : "https://www.un.org/unispal/history/", 
     "domain" : "un.org", 
     "title" : "History of the Question of Palestine", 
     "golden_text" : "gs_data/un_gs_txt/History_of_the_question_of_palestine_gs.txt"},

     {"url" : "https://www.un.org/en/observances/asteroid-day", 
     "domain" : "un.org", 
     "title" : "International Asteroid Day 30 June", 
     "golden_text" : "gs_data/un_gs_txt/International_Asteroid_day_30_June_gs.txt"},

     {"url" : "https://www.un.org/peacebuilding/gender-strategy", 
     "domain" : "un.org", 
     "title" : "The Peacebuilding Commission's Gender Strategy", 
     "golden_text" : "gs_data/un_gs_txt/The_Peacebuilding_Commissions_Gender_Strategy_gs.txt"},

     {"url" : "https://www.un.org/en/about-us/universal-declaration-of-human-rights", 
     "domain" : "un.org", 
     "title" : "Universal Declaration of Human Rights", 
     "golden_text" : "gs_data/un_gs_txt/Universal_Declaration_of_Human_Rights_gs_txt"},

     {"url" : "https://www.un.org/en/climatechange/science/mythbusters", 
     "domain" : "un.org", 
     "title" : "Myth Busters", 
     "golden_text" : "gs_data/un_gs_txt/Myth_Busters_gs.txt"},

     {"url" : "https://www.un.org/en/climatechange/cop26", 
     "domain" : "un.org", 
     "title" : "COP26: Together for our planet", 
     "golden_text" : "gs_data\un_gs_txt\Cop26_together_for_our_planet.txt"},

     {   "url": "https://www.my-personaltrainer.it/salute-benessere/cervello.html",
    "domain": "www.my-personaltrainer.it",
    "title": "Cervello", 
    "golden_text" : "gs_data/mypersonaltrainer_gs/cervello.txt"
},
{   "url": "https://www.my-personaltrainer.it/ETICHETTE-NUTRIZIONALI.htm",
    "domain": "www.my-personaltrainer.it",
    "title": "Etichette nutrizionali",
    "golden_text" : "gs_data/mypersonaltrainer_gs/etichette_nutrizionali.txt"
},
{   "url": "https://www.my-personaltrainer.it/nutrizione/malnutrizione.html",
    "domain": "www.my-personaltrainer.it",
    "title": "Malnutrizione", 
    "golden_text" : "gs_data/mypersonaltrainer_gs/malnutrizione.txt"
},
{   "url": "https://www.my-personaltrainer.it/Tv/Ricette/Dolci_Dessert/torta-alla-ricotta-senza-farina.html",
    "domain": "www.my-personaltrainer.it",
    "title": "Torta alla ricotta senza farina",
    "golden_text" : "gs_data/mypersonaltrainer_gs/torta_ricotta.txt"
},
{   "url": "https://www.my-personaltrainer.it/nutrizione/vitamine-minerali.html",
    "domain": "www.my-personaltrainer.it",
    "title": "Vitamine minerali", 
    "golden_text" : "gs_data/mypersonaltrainer_gs/vitamine.txt"
},
{   "url" : "https://www.my-personaltrainer.it/nutrizione/dieta-mediterranea.html", 
     "domain" : "www.my-personaltrainer.it", 
     "title" : "Dieta mediterranea", 
     "golden_text" : "gs_data/mypersonaltrainer_gs/dieta_mediterranea.txt"
},
{   "url" : "https://www.my-personaltrainer.it/alimentazione/alimentazione-prima-allenamento.html", 
     "domain" : "www.my-personaltrainer.it", 
     "title" : "Alimentazione prima allenamento", 
     "golden_text" : "gs_data/mypersonaltrainer_gs/alimentazione_allenamento.txt"
},
{   "url" : "https://www.my-personaltrainer.it/salute/influenza.html", 
     "domain" : "www.my-personaltrainer.it", 
     "title" : "Influenza", 
     "golden_text" : "gs_data/mypersonaltrainer_gs/influenza.txt"
},
{   "url" : "https://www.my-personaltrainer.it/integratori/sport-e-integratori-quando-e-come-assumerli.html", 
     "domain" : "www.my-personaltrainer.it", 
     "title" : "Sport e integratori quando e come assumerli", 
     "golden_text" : "gs_data/mypersonaltrainer_gs/integratori.txt"
},
{   "url" : "https://www.my-personaltrainer.it/allenamento/squat.html", 
     "domain" : "www.my-personaltrainer.it", 
     "title" : "Squat", 
     "golden_text" : "gs_data/mypersonaltrainer_gs/squat.txt"
},

    {"url" : "https://www.premierleague.com/en/tables/premier-league/2024-25/all-matchweeks", 
     "domain" : "premierleague.com", 
     "title" : "Table", 
     "golden_text" : "gs_data/premierleague_gs/classifica_gs.txt" 
    },

    {"url" : "https://www.premierleague.com/en/transfers/2025-26/january", 
        "domain" : "premierleague.com", 
        "title" : "Transfer Watch", 
        "golden_text" : "gs_data/premierleague_gs/transfer_gs.txt" 
    },

    {"url" : "https://www.premierleague.com/en/news/4324979", 
        "domain" : "premierleague.com", 
        "title" : "Strong, fearless - Is midfield role next for Lewis-Skelly after new deal?", 
        "golden_text" : "gs_data/premierleague_gs/role_Lewis-Kelly_gs.txt"
    },

    {"url" : "https://www.premierleague.com/en/news/3533373", 
        "domain" : "premierleague.com", 
        "title" : "Season trends: Record low number of red cards", 
        "golden_text" : "gs_data/premierleague_gs/red_cards_gs.txt"
    },

    {"url" : "https://www.premierleague.com/en/stats/records", 
     "domain" : "premierleague.com", 
     "title" : "Stats Centre", 
     "golden_text" : "gs_data/premierleague_gs/Stats_gs.txt"
     },

     {"url" : "https://www.premierleague.com/en/transfers/2025-26/january", 
     "domain" : "premierleague.com", 
     "title" : "Latest Injury News", 
     "golden_text" : "gs_data/premierleague_gs/injuries_gs.txt"
     },

    {"url" : "https://www.premierleague.com/en/news/4637711/premier-league-news-stories-including-man-city-stats-without-rodri-arsene-wenger-arsenal-title-prediction", 
        "domain" : "premierleague.com", 
        "title" : "The Briefing: Rodri ruled out, Arsene Wenger’s title prediction and more", 
        "golden_text" : "gs_data/premierleague_gs/Rodri_news_gs.txt"
    },

    {"url" : "https://www.premierleague.com/en/news/4604681/202526-premier-league-golden-glove-which-goalkeeper-has-kept-the-most-clean-sheets", 
        "domain" : "premierleague.com", 
        "title" : "2025/26 Premier League Golden Glove race:Who has the most clean sheets?", 
        "golden_text" : "gs_data/premierleague_gs/clean_sheets_gs.txt"
    }
]

output_folder = "gs_data"
os.makedirs(output_folder, exist_ok=True) 

for current_page in urls_to_process:

    curr_url = current_page["url"]
    curr_domain = current_page["domain"]
    curr_title = current_page["title"]
    with open(current_page["golden_text"], "r", encoding="utf-8") as f: #gs.txt is a general txt file that contains the text manually pasted from the selected url
        curr_gold_text = f.read()

    json_data = asyncio.run(json_creator(curr_url,curr_domain,curr_title,curr_gold_text))
    file_path = os.path.join(output_folder, f"dominio_{curr_domain}_gs.json")

    #json returns a python list
    try:
        with open(file_path, "r", encoding="utf-8") as r_file:
            data = json.load(r_file)
    except FileNotFoundError:
        data = []

    data.append(json_data)

    #write whole list to json file
    with open(file_path, "w", encoding="utf-8") as a_file:
        json.dump(data, a_file, indent=2)







