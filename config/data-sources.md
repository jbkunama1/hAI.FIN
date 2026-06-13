# hAI.FIN – Freie Marktdatenquellen

Alle Quellen sind kostenlos nutzbar. Quellen ohne API-Key werden bevorzugt.
Der Agent nutzt diese Daten zur Entscheidungsfindung – niemals als alleinige Grundlage.

---

## 🟢 Kein API-Key erforderlich

### 1. CNN Fear & Greed Index
- **URL:** `https://production.dataviz.cnn.io/index/fearandgreed/graphdata`
- **Format:** JSON
- **Inhalt:** Aktueller Score (0–100), historische Werte, 7 Teilindikatoren
- **Aufruf:**
  ```bash
  curl -s -H "User-Agent: Mozilla/5.0" \
    https://production.dataviz.cnn.io/index/fearandgreed/graphdata
  ```
- **Interpretation:**
  | Score | Bedeutung | Aktion |
  |-------|-----------|--------|
  | 0–24 | Extreme Fear | Potenzielle Kaufgelegenheit (konträr) |
  | 25–44 | Fear | Vorsichtig kaufen |
  | 45–55 | Neutral | Standard-Regeln anwenden |
  | 56–74 | Greed | Positionen nicht erhöhen |
  | 75–100 | Extreme Greed | Keine neuen Käufe, ggf. reduzieren |

### 2. Yahoo Finance (inoffiziell via yfinance)
- **Python:** `pip install yfinance`
- **Liefert:** Kursdaten, MA200, MA50, RSI (berechnet), Volumen, Dividenden
- **Beispiel:**
  ```python
  import yfinance as yf
  spy = yf.Ticker("SPY")
  hist = spy.history(period="1y")
  ma200 = hist["Close"].rolling(200).mean().iloc[-1]
  current = hist["Close"].iloc[-1]
  trend = "bullish" if current > ma200 else "bearish"
  ```
- **Limit:** Kein offizielles Rate-Limit, aber max. 2000 Calls/Stunde empfohlen

### 3. FRED (Federal Reserve Economic Data)
- **URL:** `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>`
- **Key erforderlich:** Nein für CSV-Download
- **Nützliche Serien:**
  | Serie | Beschreibung |
  |-------|--------------|
  | `DFF` | Fed Funds Rate (aktueller Leitzins) |
  | `T10Y2Y` | 10Y-2Y Treasury Spread (Rezessionsindikator) |
  | `VIXCLS` | VIX Closing Price |
  | `UNRATE` | US Arbeitslosenquote |
  | `CPIAUCSL` | US Inflationsrate (CPI) |
- **Beispiel:**
  ```bash
  curl -s "https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10Y2Y" | tail -5
  ```

### 4. US Treasury Yield Curve (direkt vom Staat)
- **URL:** `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml`
- **Format:** XML
- **Inhalt:** Tägliche Treasury-Renditen (1M bis 30Y)
- **Wichtig:** Invertierte Zinskurve (10Y < 2Y) = Rezessionssignal

---

## 🟡 Kostenlos mit kostenlosem API-Key

### 5. Alpha Vantage
- **Key:** Kostenlos unter https://www.alphavantage.co/support/#api-key
- **Free Tier:** 25 Calls/Tag, 5 Calls/Minute
- **Liefert:** Echtzeitkurse, technische Indikatoren (RSI, MACD, BB), Fundamentaldaten
- **Env-Variable:** `ALPHA_VANTAGE_KEY`
- **Beispiel RSI:**
  ```bash
  curl "https://www.alphavantage.co/query?function=RSI&symbol=SPY\
  &interval=daily&time_period=14&series_type=close\
  &apikey=${ALPHA_VANTAGE_KEY}"
  ```

### 6. Finnhub
- **Key:** Kostenlos unter https://finnhub.io/register
- **Free Tier:** 60 Calls/Minute
- **Liefert:** Echtzeitkurse, News mit Sentiment-Score, Insider-Transaktionen, Earnings-Kalender
- **Env-Variable:** `FINNHUB_KEY`
- **Besonderheit:** Liefert direkten News-Sentiment-Score (-1 bis +1) für ETFs
- **Beispiel:**
  ```bash
  # Markt-News mit Sentiment
  curl "https://finnhub.io/api/v1/news?category=general&token=${FINNHUB_KEY}"
  # Earnings-Kalender (wichtig für No-Trade-Tage)
  curl "https://finnhub.io/api/v1/calendar/earnings?from=2025-01-01&to=2025-01-07&token=${FINNHUB_KEY}"
  ```

---

## 📊 Abgeleitete Signale (kombiniert)

Der Agent kombiniert diese Quellen zu einem **Composite Signal** vor jedem Trade:

```
SIGNAL_SCORE = 0

(+2) Preis > MA200          → Aufwaertstrend bestätigt
(+1) MA50 > MA200           → Golden Cross aktiv
(+1) RSI zwischen 35-60     → Weder überkauft noch überverkauft
(+1) Fear&Greed < 45        → Markt hat Angst (konträrer Kaufindikator)
(-1) Fear&Greed > 75        → Extreme Gier (Vorsicht)
(-2) Preis < MA200          → Abwaertstrend
(-1) VIX > 30               → Hohe Marktangst / Volatilität
(-1) T10Y2Y invertiert      → Rezessionssignal
(-1) Earnings/FOMC/CPI heute → Event-Risiko

Entscheidung:
  Score >= 3  → KAUF erlaubt
  Score 1-2   → HALTEN, kein Aufbau
  Score <= 0  → NICHT handeln / reduzieren
```

---

## ⚠️ Wichtige Hinweise

- **Niemals** auf Basis einer einzelnen Quelle handeln
- Alle Signale sind **nachlaufend** (Lagging Indicators) – sie bestätigen Trends, sagen sie nicht vorher
- Bei Datenfehler oder Timeout: konservativster Fall annehmen (Score = 0)
- Free-Tier-Limits immer prüfen, bevor Calls gemacht werden
- `yfinance` ist inoffiziell – bei Änderungen der Yahoo-API könnte es ausfallen
