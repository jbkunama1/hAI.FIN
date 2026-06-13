# hAI.FIN – Minimal OpenClaw eToro Trading Agent
FROM python:3.11-slim

WORKDIR /app

# System-Abhaengigkeiten
RUN apt-get update && apt-get install -y \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# OpenClaw installieren
RUN pip install --no-cache-dir openclaw

# Projekt-Dateien kopieren
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY .env.example ./.env.example

# Rechte setzen
RUN chmod +x scripts/*.sh

# Start-Skript
ENTRYPOINT ["./scripts/start.sh"]
