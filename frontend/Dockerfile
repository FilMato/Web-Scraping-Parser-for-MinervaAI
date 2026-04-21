FROM python:3.13-slim

WORKDIR /app

# Installazione dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia del codice sorgente
COPY src/ ./src/

# IMPORTANTE: Copia la cartella templates necessaria per Jinja2
COPY templates/ ./src/templates/

# Configurazione del path per far trovare i moduli a Python
ENV PYTHONPATH=/app/src

# Il frontend deve stare sulla porta 8004
EXPOSE 8004

# Nota la correzione del nome: frontend invece di fronted
CMD ["uvicorn", "src.frontend:app", "--host", "0.0.0.0", "--port", "8004"]