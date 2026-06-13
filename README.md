# 🤖 hAI.FIN

![Version](https://img.shields.io/badge/Version-0.1.0-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Status](https://img.shields.io/badge/Status-Alpha-yellow.svg)
![DRY RUN](https://img.shields.io/badge/Default-DRY__RUN-orange.svg)
[![GitHub Pages](https://img.shields.io/badge/Docs-GitHub%20Pages-brightgreen.svg)](https://jbkunama1.github.io/hAI.FIN)
[![GitHub last commit](https://img.shields.io/github/last-commit/jbkunama1/hAI.FIN)](https://github.com/jbkunama1/hAI.FIN/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/jbkunama1/hAI.FIN)](https://github.com/jbkunama1/hAI.FIN/issues)

> **Autonomer, konservativer ETF-Trading-Agent für eToro Agent Portfolios.**  
> Self-hosted · Docker/Portainer · Regelbasiert · Telegram-Alerts · Streamlit-Dashboard

🔗 **[Live-Doku & Demo → jbkunama1.github.io/hAI.FIN](https://jbkunama1.github.io/hAI.FIN)**

---

## ✨ Features

| Feature | Beschreibung |
|---|---|
| 🧠 **Composite Signal Score** | MA200, MA50, RSI, Fear&Greed, VIX, Zinskurve, Event-Kalender |
| 📊 **Live-Marktdaten** | CNN Fear&Greed, yfinance, FRED – größtenteils ohne API-Key |
| 🛡️ **Harte Guardrails** | Max. Trades/Tag, Positionslimit, Cash-Reserve, Asset-Whitelist |
| 📱 **Telegram-Notifier** | Morgen-Briefing, Trade-Alerts, Fehler, VIX-Notbremse |
| 📈 **Streamlit-Dashboard** | Live-Signale, Portfolio-Simulation, Trade-Log |
| 🧪 **Unit-Tests** | 8 Tests für Signal-Logik (pytest) |
| ⏰ **GitHub Actions** | Täglicher Cron Mo–Fr 09:45 ET, Logs als Artefakte |
| 🐳 **Docker-Ready** | Agent + Dashboard als eigene Services |

---

## 🚀 Schnellstart

### Voraussetzungen
- Docker & Docker Compose (oder Portainer)
- eToro Account mit **Agent Portfolio**
- Optional: Finnhub-Key (kostenlos), Telegram-Bot

### 1. Klonen & konfigurieren

```bash
git clone https://github.com/jbkunama1/hAI.FIN.git
cd hAI.FIN
cp .env.example .env
joe .env   # oder nano/vim
```

### 2. Lokal testen (ohne Docker)

```bash
pip install -r requirements.txt

# Unit-Tests
python -m pytest tests/ -v

# Agent einmalig (DRY_RUN)
DRY_RUN=true python -m src.agent

# Dashboard starten
bash dashboard/run.sh
# → http://localhost:8501
```

### 3. Docker Compose (empfohlen)

```bash
docker compose up -d
# Agent läuft im Hintergrund
# Dashboard → http://<server>:8501
```

### 4. Portainer-Stack
1. Stack Editor öffnen
2. `docker-compose.yml` einfügen
3. `.env`-Variablen eintragen
4. **Deploy Stack**

---

## 📂 Projektstruktur

```
hAI.FIN/
├── 📄 docker-compose.yml       # Agent + Dashboard Services
├── 📄 Dockerfile               # Container-Definition
├── 📄 requirements.txt         # Python-Abhängigkeiten
├── 📄 .env.example             # Konfigurationsvorlage (alle Keys erklärt)
├── 📁 src/
│   ├── agent.py                 # Hauptschleife
│   ├── data_fetcher.py          # CNN F&G, yfinance, FRED, Finnhub
│   ├── signals.py               # Composite Score Berechnung
│   ├── portfolio.py             # Portfolio-Simulation & Guardrails
│   ├── logger.py                # JSON-Logging
│   └── notifier.py              # Telegram-Alerts
├── 📁 dashboard/
│   └── app.py                   # Streamlit-UI
├── 📁 config/
│   ├── system-prompt.md         # Agent-Wissensbasis v2.0
│   ├── trading-policy.json      # Regeln & Guardrails
│   ├── market-signals.md        # Signalreferenz & Schwellenwerte
│   ├── data-sources.md          # Freie Datenquellen & Scoring
│   └── agent-knowledge.md       # ETF-Profile, Marktphasen
├── 📁 tests/
│   └── test_signals.py          # 8 Unit-Tests
├── 📁 docs/
│   └── index.html               # GitHub Pages Landing Page
└── 📁 .github/workflows/
    └── daily-run.yml            # Mo–Fr 09:45 ET Cron
```

---

## 🧠 Entscheidungslogik

Der Agent berechnet vor jedem Trade einen **Composite Signal Score**:

```
+2  Kurs > MA200          → Langfristiger Aufwärtstrend
+1  MA50 > MA200          → Golden Cross aktiv
+1  RSI 35–60             → Weder überkauft noch überverkauft
+1  Fear&Greed < 45       → Markt hat Angst (konträrer Kaufindikator)
−1  Fear&Greed > 75       → Extreme Gier (Vorsicht)
−2  Kurs < MA200          → Abwärtstrend
−1  VIX > 30              → Hohe Marktangst
−1  T10Y2Y < 0            → Invertierte Zinskurve (Rezessionssignal)
−1  Earnings/FOMC/CPI     → Event-Risiko

Score ≥ 3  →  BUY
Score 1–2  →  HOLD
Score ≤ 0  →  SKIP
Score ≤ −2 →  REDUCE
```

---

## 📡 Freie Datenquellen (kein Key nötig)

| Quelle | Daten | Key |
|---|---|---|
| CNN Fear & Greed | Sentiment 0–100 | ❌ |
| yfinance | Kurse, MA200/50, RSI | ❌ |
| FRED (Fed) | VIX, Zinskurve, Leitzins | ❌ |
| Finnhub | Earnings-Kalender, News | ✅ kostenlos |
| Alpha Vantage | RSI, MACD, Fundamentals | ✅ kostenlos |

---

## 🔧 Konfiguration `.env`

| Variable | Beschreibung | Standard |
|---|---|---|
| `DRY_RUN` | Testmodus (keine echten Orders) | `true` |
| `ALLOWED_ASSETS` | Handelbare Assets | `SPY,QQQ,VTI` |
| `MAX_TRADES_PER_DAY` | Limit pro Tag | `3` |
| `MAX_POSITION_PCT` | Max. Positionsgröße | `0.10` |
| `MIN_CASH_RESERVE_PCT` | Mindest-Cash-Reserve | `0.20` |
| `ORDER_SIZE_PCT` | Ordergröße | `0.05` |
| `VIX_EMERGENCY` | Notbremse VIX-Schwelle | `40` |
| `FINNHUB_KEY` | Finnhub API Key | optional |
| `TELEGRAM_BOT_TOKEN` | Telegram-Bot-Token | optional |
| `TELEGRAM_CHAT_ID` | Telegram-Chat-ID | optional |

Alle Variablen mit Erklärung in [`.env.example`](.env.example).

---

## 📱 Telegram einrichten

```bash
# 1. Bot erstellen
# Telegram → @BotFather → /newbot → Token kopieren

# 2. Chat-ID ermitteln
curl https://api.telegram.org/bot<TOKEN>/getUpdates
# → "chat":{"id": 12345678}

# 3. In .env eintragen
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=12345678
```

---

## 🛡️ Guardrails & Sicherheit

- ✅ Nur `ALLOWED_ASSETS` handelbar
- ✅ `MAX_TRADES_PER_DAY` absolut
- ✅ `MIN_CASH_RESERVE_PCT` immer einhalten
- ✅ Kein Short, kein Hebel per Default
- ✅ VIX ≥ 40 → automatischer Cash-Modus
- ✅ Keine Orders außerhalb 09:30–16:00 ET
- ✅ `DRY_RUN=true` als sicherer Standard

---

## 📋 Changelog

### v0.1.0 – 2026-06-13
- 🎉 Initiales Release
- Composite Signal Score (8 Indikatoren)
- Streamlit-Dashboard
- Docker/Portainer-Setup
- Telegram-Notifier
- GitHub Actions Cron
- 8 Unit-Tests
- GitHub Pages Landing Page

---

## ⚠️ Disclaimer

> **Trading birgt erhebliche Risiken. Du kannst dein eingesetztes Kapital vollständig verlieren.**
>
> Dieses Projekt ist ein experimentelles Open-Source-Tool für Bildungs- und Forschungszwecke.
> Der Autor übernimmt keinerlei Haftung für Verluste oder Schäden jeglicher Art.
> Nutze ausschließlich Kapital, dessen Verlust du dir leisten kannst.
>
> **Never trade more than you can afford to lose.**

---

## 🤝 Mitmachen

1. Fork erstellen
2. Branch: `git checkout -b feature/MeinFeature`
3. Commit: `git commit -m 'feat: Beschreibung'`
4. Push: `git push origin feature/MeinFeature`
5. Pull Request öffnen

---

## 📜 Lizenz

[MIT](LICENSE) – Open Source, frei nutzbar.

---

<p align="center">
  🤖 Built with passion for self-hosted AI &amp; finance automation<br>
  <a href="https://jbkunama1.github.io/hAI.FIN">jbkunama1.github.io/hAI.FIN</a>
</p>
