#!/bin/bash
set -e

# hAI.FIN Start-Skript
echo "🤖 hAI.FIN wird gestartet..."

# eToro Skill installieren
openclaw skill install https://skills.bullaware.com/etoro-api/SKILL.md

# System-Prompt laden
export SYSTEM_PROMPT=$(cat /app/config/system-prompt.md)

# Agent starten
echo "🚀 Starte Trading-Agent (DRY_RUN=${DRY_RUN})..."
openclaw run \
  --model "${MODEL_NAME}" \
  --api-base "${OPENAI_API_BASE}" \
  --api-key "${OPENAI_API_KEY}" \
  --system-prompt "${SYSTEM_PROMPT}" \
  --config /app/config/trading-policy.json \
  --mode autonomous
