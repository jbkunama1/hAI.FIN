#!/bin/bash
# Security: fail on unset variables and pipe errors
set -euo pipefail

# hAI.FIN Start-Skript
echo "🤖 hAI.FIN wird gestartet..."

# -------------------------------------------------------
# Pflichtprüfung: Alle erforderlichen Variablen vorhanden?
# -------------------------------------------------------
REQUIRED_VARS=(
  OPENAI_API_BASE
  OPENAI_API_KEY
  MODEL_NAME
  ETORO_PUBLIC_KEY
  ETORO_USER_KEY
  ETORO_AGENT_PORTFOLIO_ID
)

for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "❌ FEHLER: Pflicht-Variable '$var' ist nicht gesetzt. Abbruch."
    exit 1
  fi
done

echo "✅ Alle Pflicht-Variablen gesetzt."

# -------------------------------------------------------
# eToro Skill: Lokale Kopie verwenden statt Remote-Download
# Security: Kein unkontrollierter Remote-Code-Download zur Laufzeit
# -------------------------------------------------------
if [[ -f "/app/config/etoro-skill.md" ]]; then
  echo "📦 Installiere eToro Skill aus lokaler Kopie..."
  openclaw skill install /app/config/etoro-skill.md
else
  echo "⚠️  WARNUNG: Lokale Skill-Datei nicht gefunden."
  echo "   Erstelle: config/etoro-skill.md (Kopie von https://skills.bullaware.com/etoro-api/SKILL.md)"
  echo "   Der Agent startet NICHT ohne verifizierten Skill."
  exit 1
fi

# System-Prompt laden
export SYSTEM_PROMPT
SYSTEM_PROMPT=$(cat /app/config/system-prompt.md)

# Agent starten
echo "🚀 Starte Trading-Agent (DRY_RUN=${DRY_RUN})..."
openclaw run \
  --model "${MODEL_NAME}" \
  --api-base "${OPENAI_API_BASE}" \
  --api-key "${OPENAI_API_KEY}" \
  --system-prompt "${SYSTEM_PROMPT}" \
  --config /app/config/trading-policy.json \
  --mode autonomous
