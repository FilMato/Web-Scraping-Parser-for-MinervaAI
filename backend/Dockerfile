FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN crawl4ai-setup

COPY src/ ./src/
ENV PYTHONPATH=/app/src

EXPOSE 8003
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8003"]