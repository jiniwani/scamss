FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests, sys; import os; import time; import socket; import urllib.request; \
from urllib.error import URLError; \
import json; \
req=urllib.request.Request('http://127.0.0.1:8080/healthz'); \
urllib.request.urlopen(req); print('ok')" || exit 1

EXPOSE 8080

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]

