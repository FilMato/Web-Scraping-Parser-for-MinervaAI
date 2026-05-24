FROM python:3.13-slim

WORKDIR /app

# Installiamo le dipendenze di sistema necessarie per compilare il connettore MariaDB
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN crawl4ai-setup
RUN python -m nltk.downloader stopwords punkt

COPY src/ ./src/
ENV PYTHONPATH=/app/src

EXPOSE 8003
CMD ["uvicorn", "src.rest.server:app", "--host", "0.0.0.0", "--port", "8003"]