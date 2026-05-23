import asyncio
import httpx
import random

# Assicurati che il tuo backend FastAPI stia girando su questa porta
BACKEND_URL = "http://0.0.0.0:8003"

async def test_real_data_pipeline():
    async with httpx.AsyncClient(timeout=120.0) as client:  # Timeout alzato a 2 minuti per testi molto lunghi
        print("=== 1. RECUPERO DOMINI DISPONIBILI ===")
        try:
            resp_domains = await client.get(f"{BACKEND_URL}/domains")
            resp_domains.raise_for_status()
        except httpx.ConnectError:
            print(f"❌ ERRORE: Impossibile connettersi a {BACKEND_URL}. Il backend è acceso?")
            return

        domains = resp_domains.json().get("domains", [])
        if not domains:
            print("❌ Nessun dominio supportato trovato.")
            return
            
        # Modifica 1: Sceglie un dominio a caso dalla lista
        test_domain = random.choice(domains) 
        print(f"✓ Dominio casuale selezionato: {test_domain}")

        print("\n=== 2. RECUPERO ARTICOLI DAL GOLD STANDARD LOCALE ===")
        resp_gs = await client.get(f"{BACKEND_URL}/full_gold_standard", params={"domain": test_domain})
        if resp_gs.status_code != 200:
            print(f"❌ Errore nel recupero del gold standard: {resp_gs.text}")
            return
            
        articoli = resp_gs.json().get("gold_standard", [])
        if not articoli:
            print(f"❌ Nessun articolo trovato per il dominio {test_domain} nei JSON locali.")
            return
            
        # Modifica 2: Sceglie un articolo a caso dal dominio estratto
        test_article = random.choice(articoli)
        target_url = test_article["url"]
        real_gold_text = test_article["gold_text"]
        print(f"✓ URL casuale selezionato: {target_url}")
        print(f"✓ Lunghezza Gold Text autentico: {len(real_gold_text)} caratteri")

        print("\n=== 3. PARSING DELL'URL TRAMITE IL TUO PARSER ===")
        # Invia la richiesta POST a /parse usando local=True per leggere l'HTML già salvato
        parse_payload = {"url": target_url, "local": True}
        resp_parse = await client.post(f"{BACKEND_URL}/parse", json=parse_payload)
        
        if resp_parse.status_code != 200:
            print(f"❌ Errore durante il parsing (Status {resp_parse.status_code}):\n{resp_parse.text}")
            return
            
        real_parsed_text = resp_parse.json().get("parsed_text", "")
        print(f"✓ Lunghezza Parsed Text estratto: {len(real_parsed_text)} caratteri")

        print("\n=== 4. ESECUZIONE LLM AS A JUDGE SU DATI REALI ===")
        print("Attendere, Ollama sta leggendo i testi completi e formulando il giudizio... ⏳")
        judge_payload = {
            "parsed_text": real_parsed_text,
            "gold_text": real_gold_text
        }
        
        resp_judge = await client.post(f"{BACKEND_URL}/evaluate_judge", json=judge_payload)
        
        if resp_judge.status_code == 200:
            final_output = resp_judge.json()
            print("\n✨ GIUDIZIO COMPLETATO CON SUCCESSO ✨")
            print("=" * 70)
            print(f"Modello Utilizzato: {final_output.get('model_name')}")
            print(f"Score Assegnato   : {final_output.get('judge_score')}/5")
            print(f"Feedback LLM      :\n{final_output.get('judge_feedback')}")
            print("=" * 70)
        else:
            print(f"\n❌ ERRORE DA EVALUATE_JUDGE (Status {resp_judge.status_code}):\n{resp_judge.text}")

if __name__ == "__main__":
    asyncio.run(test_real_data_pipeline())