from abc import ABC, abstractmethod
from urllib.parse import urlparse
import os

class Parser(ABC):
    
    def __init__(self):
        pass

    @abstractmethod
    async def parser_url(self, url: str) -> dict:
        #Ogni sottoclasse deve implementrlo in un modo diverso
        pass

    def format_response(self, url: str, domain: str, title: str, html_text: str, parsed_text: str) -> dict:
        return {
            "url": url,
            "domain": domain,
            "title": title,
            "html_text": html_text,
            "parsed_text": parsed_text
        }

    #solo per noi, da eliminare alla fine 
    def salva_risultati(parsed_text: str, html_text: str) -> None: # prende in input html_text e parsed_text della funzione precente e salva i file

        base_dir = os.path.dirname(os.path.abspath(__file__))
        risultati_dir = os.path.join(base_dir, "risultati")
        
        file_txt_path = os.path.join(risultati_dir, "Risultato_parser.txt")
        file_html_path = os.path.join(risultati_dir, "Risultato_html_parser.html")

        with open(file_txt_path, "w", encoding="utf-8") as f:
            f.write(parsed_text)

        with open(file_html_path, "w", encoding="utf-8") as f:
            f.write(html_text)