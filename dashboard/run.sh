#!/bin/bash
# hAI.FIN Dashboard starten
cd "$(dirname "$0")/.."
pip install -q streamlit yfinance requests pandas python-dotenv
streamlit run dashboard/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --browser.gatherUsageStats false
