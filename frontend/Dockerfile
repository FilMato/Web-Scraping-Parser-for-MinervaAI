FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN crawl4ai-setup

COPY src/ ./src/
COPY templates/ ./templates/

EXPOSE 8004
CMD ["uvicorn", "src.frontend:app", "--host", "0.0.0.0", "--port", "8004"]