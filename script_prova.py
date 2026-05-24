import requests
import json

# Definiamo i test: ogni dizionario è un caso distinto
test_cases = [
    {
        "nome": "Test 1 - Identico",
        "parsed": "my favourite color is yellow but i also like green, blue and pink.",
        "gold": "my favourite color is yellow but i also like green, blue and pink."
    },
    {
        "nome": "Test 2 - Rumore minimo",
        "parsed": "my favourite color is yellow but i also like green, blue and pink. <div></div>",
        "gold": "my favourite color is yellow but i also like green, blue and pink."
    },
    {
        "nome": "Test 3 - Il tuo caso complesso",
        "parsed": "my favourite color [color](https://color.it)is [yellow (https://yellow.com)but i also like green, nk.\n I like yellow and pink better when they !!!!!!!!!!!!!!!!!!!! are soft toned and kind of WOWWWWW SHSHHSHAH pastel, but I love deep blues img<blue> and greens",
        "gold": "my favourite color is yellow but i also like green, blue and pink.\n I like yellow and pink better when they are soft toned and kind of pastel, but I love deep blues and greens"
    }
]

model = "gemma4:e2b"

for caso in test_cases:
    print(f"--- Inizio: {caso['nome']} ---")
    
    prompt = f"""Act like a text analyst. Your goal is to compare two different texts: 
Parsed Text: {caso['parsed']}
Gold Text: {caso['gold']}

Evaluate their overall score on a scale from 1 to 5. The maximum score (5) means that the Parsed Text is perfectly equal to the Gold Text and contains no extra noise.
The Parsed Text must be: equal in length with the Gold Text; equal in phrasing, content, word sequence, capitalization, punctuation.
If one of these criteria is not met the score has to be lowered:
    - html noise is -0.1 per noise found from the total score
    - capitalization, punctuation and spacing  is -0.01 from the total score
    - length difference is -0.1 per extra word from the total score

Your answer must be ONLY a valid JSON formatted exactly like this:
{{
    "judge_score": 0,
    "judge_feedback": "write your detailed explanation here"
}}"""

    payload = {
        "model": model,
        "prompt": prompt,
        "format": "json",
        "stream": False
    }

    resp = requests.post("http://0.0.0.0:11434/api/generate", json=payload)
    # 1. Verifica che la richiesta sia arrivata al server (stato 200 OK)
    #resp.raise_for_status() 

    # 2. Stampa il contenuto grezzo per vedere se il server ha risposto qualcosa di valido
   # print(f"Stato risposta: {resp.status_code}, Contenuto grezzo: {resp.text[:100]}...")
    
    # Corretto: .json() è il metodo della risposta di requests
    json_resp = resp.json()

    try:
        # Estraiamo il dizionario dalla risposta dell'LLM
        giudizio = json.loads(json_resp["response"])
        print("LLM ha risposto:", giudizio, "\n")
    except Exception as e:
        print("Errore formato JSON. Risposta grezza:", json_resp.get("response"), "\n")