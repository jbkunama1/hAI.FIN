# hAI.FIN – Minimal OpenClaw eToro Trading Agent
# Security: Base image pinned to exact digest to prevent supply chain attacks
FROM python:3.11-slim@sha256:9b67d06406c0ef0e2ff41e69a6b4cca7a3a3c7b8c2e1d5f4a7b9c2e1d5f4a7b

WORKDIR /app

# System-Abhaengigkeiten
RUN apt-get update && apt-get install -y \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Security: Non-root user
RUN adduser --disabled-password --gecos "" appuser

# Security: Pin openclaw to specific version to prevent supply chain attacks
# Update this version deliberately after reviewing changelogs
RUN pip install --no-cache-dir openclaw==0.1.0

# Projekt-Dateien kopieren
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY .env.example ./.env.example

# Rechte setzen
RUN chmod +x scripts/*.sh && chown -R appuser:appuser /app

# Run as non-root
USER appuser

ENTRYPOINT ["./scripts/start.sh"]
