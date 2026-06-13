# 🤖 hAI.FIN

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![Portainer](https://img.shields.io/badge/Portainer-Stack-orange.svg)
![9Router](https://img.shields.io/badge/9Router-Compatible-purple.svg)
![eToro](https://img.shields.io/badge/eToro-Agent--Portfolio-red.svg)
![Status](https://img.shields.io/badge/Status-Alpha-yellow.svg)

> **Ein minimalistischer, autonomer Trading-Agent für eToro Agent Portfolios.**  
> Self-hosted, Docker-tauglich, mit 9Router als LLM-Backend.

---

## 🎯 Features

- 🐳 **Docker-Ready** – Einfacher Portainer-Stack
- 🧠 **9Router-Integration** – Nutzt deinen eigenen LLM-Router
- 📈 **eToro Skill** – Offizieller API-Zugang via Agent Portfolio
- 🛡️ **Harte Guardrails** – Max. Trades, Positionslimits, erlaubte Assets
- 📝 **MIT-Lizenz** – Open Source, frei nutzbar
- ⚡ **Schnellstart** – API-Keys eintragen, Container starten

---

## 🚀 Schnellstart

### 1. Voraussetzungen

- Docker & Docker Compose (oder Portainer)
- eToro Account mit **Agent Portfolio**
- eToro API Keys (Public Key + User Key)
- 9Router Instanz (oder OpenAI-kompatibler Endpoint)

### 2. Repository klonen

```bash
git clone https://github.com/jbkunama1/hAI.FIN.git
cd hAI.FIN
```

### 3. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
nano .env
```

### 4. Starten

**Mit Docker Compose:**
```bash
docker-compose up -d
```

**Mit Portainer:**
1. Stack Editor öffnen
2. Inhalt von `docker-compose.yml` einfügen
3. Environment Variablen eintragen
4. Deploy Stack

---

## 🔧 Konfiguration

| Variable | Beschreibung | Beispiel |
|----------|-------------|----------|
| `OPENAI_API_BASE` | 9Router Endpoint | `https://9router.dein-server.de/v1` |
| `OPENAI_API_KEY` | API Key für Router | `your-9router-api-key-here` |
| `MODEL_NAME` | LLM Modell | `gpt-4o-mini` |
| `ETORO_PUBLIC_KEY` | eToro Public Key | `pk_live_...` |
| `ETORO_USER_KEY` | eToro User Key | `uk_live_...` |
| `ETORO_AGENT_PORTFOLIO_ID` | Agent Portfolio ID | `portfolio-123` |
| `MAX_TRADES_PER_DAY` | Max. Trades/Tag | `3` |
| `MAX_POSITION_PERCENT` | Max. Position/Trade | `10` |
| `ALLOWED_ASSETS` | Erlaubte Assets | `QQQ,SPY,VTI` |
| `DRY_RUN` | Testmodus ohne echte Orders | `true`/`false` |

---

## 🛡️ Sicherheit & Guardrails

**WICHTIG:** Dieser Agent kann mit echtem Geld handeln!

- ✅ Nur innerhalb eines **eToro Agent Portfolios** betreiben
- ✅ Portfolio-Kapital begrenzen (z.B. 200–500 $)
- ✅ Zuerst `DRY_RUN=true` zum Testen aktivieren
- ✅ Erlaubte Assets und Limits definieren
- ✅ Keine Hebelprodukte, keine Shorts per Default
- ✅ IP-Whitelisting für API Keys nutzen

---

## 🏗️ Architektur

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   hAI.FIN   │────▶│   9Router   │────▶│    LLM      │
│   Agent     │     │  (Dein Host)│     │ (GPT/Claude)│
└─────────────┘     └─────────────┘     └─────────────┘
       │
       ▼
┌────────────────┐
│   eToro API    │
│ Agent Portfolio│
└────────────────┘
```

---

## 📂 Projektstruktur

```
hAI.FIN/
├── 📄 docker-compose.yml      # Portainer-Stack
├── 📄 Dockerfile              # Container-Definition
├── 📄 .env.example            # Konfigurationsvorlage
├── 📄 README.md               # Diese Datei
├── 📄 LICENSE                 # MIT-Lizenz
├── 📁 config/
│   ├── system-prompt.md       # Agent-Verhalten
│   └── trading-policy.json    # Harte Trading-Regeln
└── 📁 scripts/
    └── start.sh               # Container-Start
```

---

## ⚠️ Disclaimer

> ⚠️ **Trading birgt erhebliche Risiken. Du kannst dein eingesetztes Kapital verlieren.**
>
> Dieses Projekt ist ein experimentelles Tool für Bildungs- und Forschungszwecke.
> Der Autor übernimmt keine Haftung für Verluste oder Schäden.
> Nutze ausschließlich Geld, das du bereit bist zu verlieren.
>
> **Never trade more than you can afford to lose.**

---

## 🤝 Mitmachen

1. Fork erstellen
2. Feature-Branch: `git checkout -b feature/NeuesFeature`
3. Committen: `git commit -m 'feat: Neues Feature'`
4. Pushen: `git push origin feature/NeuesFeature`
5. Pull Request öffnen

---

## 📜 Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**. Siehe [LICENSE](LICENSE) für Details.

---

<p align="center">
  🤖 Built with passion for self-hosted AI & finance automation
</p>
