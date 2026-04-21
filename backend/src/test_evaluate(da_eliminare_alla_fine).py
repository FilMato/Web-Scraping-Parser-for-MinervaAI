import json
import os

def clean(text):
    text = text.replace('"', '')
    text = text.replace("'", '')
    return text

# 1. Trova la cartella in cui si trova questo script (backend/src)
base_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Percorsi Assoluti dinamici (a prova di errore del terminale)
# Dal tuo screenshot, il parser salva in: backend/src/parsers/risultati/
percorso_parsed = os.path.join(base_dir, "parsers", "risultati", "Risultato_parser.txt")

# gs_data si trova 2 livelli sopra src (nella root del progetto)
percorso_gold = os.path.join(base_dir, "..", "..", "gs_data", "mypersonaltrainer_gs", "torta_ricotta.txt")

# 3. Leggiamo i file con un blocco di sicurezza (try/except)
try:
    with open(percorso_parsed, "r", encoding="utf-8") as f:
        parsed_text = clean(f.read())
        
    with open(percorso_gold, "r", encoding="utf-8") as f:
        gold_text = clean(f.read())
except FileNotFoundError as e:
    print(f"\n ERRORE: File non trovato!\nControlla il percorso: {e}")
    exit()

# 4. Creiamo il dizionario Python
payload = {
    "parsed_text": parsed_text,
    "gold_text": gold_text
}

# 5. Salviamo tutto in un file JSON (invece di stamparlo tagliato nel terminale)
percorso_output = os.path.join(base_dir, "payload_generato.json")

with open(percorso_output, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=4)

print(f"\n Successo! Il file JSON completo è stato salvato qui:")
print(percorso_output)
print("-> Aprilo su VS Code, seleziona tutto (Ctrl+A), copia e incolla su Swagger!")