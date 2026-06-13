# hAI.FIN – Marktsignal-Referenz

Konkrete Signale, Schwellenwerte und Interpretationsregeln für den Agenten.

---

## 📈 Trend-Indikatoren

### Moving Averages

| Signal | Bedingung | Bedeutung | Aktion |
|--------|-----------|-----------|--------|
| **Golden Cross** | MA50 kreuzt MA200 von unten | Starkes Kaufsignal | Position aufbauen |
| **Death Cross** | MA50 kreuzt MA200 von oben | Starkes Verkaufssignal | Position reduzieren |
| **Bullish** | Kurs > MA200 | Langfristiger Aufwärtstrend | Käufe erlaubt |
| **Bearish** | Kurs < MA200 | Langfristiger Abwärtstrend | Keine neuen Käufe |
| **Konsolidierung** | Kurs ±2% um MA200 | Unklarer Trend | Abwarten |

### RSI (14-Tage, daily)

| Wert | Zone | Interpretation | Aktion |
|------|------|----------------|--------|
| > 80 | Extrem überkauft | Kurzfristige Korrektur wahrscheinlich | Kein Kauf, evtl. Teilverkauf |
| 70–80 | Überkauft | Vorsicht | Kein Positionsaufbau |
| 60–70 | Leicht erhitzt | Normal im Bullenmarkt | Halten |
| **35–60** | **Neutral** | **Optimaler Kaufbereich** | **Kauf erlaubt** |
| 25–35 | Leicht überverkauft | Mögliche Stabilisierung | Kleiner Kauf möglich |
| < 25 | Extrem überverkauft | Panikverkauf, Überreaktion | Schrittweise akkumulieren |

---

## 😱 Sentiment-Indikatoren

### CNN Fear & Greed Index
Konträrer Indikator: **Extreme Angst = Kaufgelegenheit, Extreme Gier = Vorsicht**

```
0–24   Extreme Fear   ⬆️ Historisch gute Einstiegschance
25–44  Fear           ⬆️ Vorsichtiger Aufbau möglich  
45–55  Neutral        ➡️ Standard-Regeln anwenden
56–74  Greed          ⬇️ Keine neuen Positionen
75–100 Extreme Greed  ⬇️ Bestehende Positionen prüfen
```

### VIX (Volatility Index)
| Wert | Marktstimmung | Aktion |
|------|---------------|--------|
| < 15 | Ruhig, geringe Angst | Normal handeln |
| 15–20 | Leicht erhöht | Normal handeln |
| 20–30 | Erhöhte Unsicherheit | Positionsgrößen halbieren |
| > 30 | Hohe Angst / Krise | Keine neuen Käufe |
| > 40 | Panik | Cash halten, auf Stabilisierung warten |

---

## 🏛️ Makro-Indikatoren

### Zinskurve (T10Y2Y Spread via FRED)
```
10Y-Rendite minus 2Y-Rendite:
  > 0%    Normale Kurve    → Kein Rezessionssignal
  0–0%   Flache Kurve     → Vorsicht, Wachstumssorgen
  < 0%    Invertiert       → Rezessionssignal (historisch zuverlässig)
```

**Wichtig:** Invertierung zeigt Rezession 6–18 Monate im Voraus an.
Beim Eintritt in die Invertierung: Max-Position auf 5% reduzieren.

### Fed Funds Rate (Zinsniveau)
| Phase | Auswirkung auf QQQ/SPY | Strategie |
|-------|------------------------|----------|
| Zinssenkungszyklus | Positiv (billigeres Geld) | Positionen aufbauen |
| Zinserhöhungszyklus | Negativ für Wachstum (QQQ!) | QQQ-Anteil reduzieren |
| Zinspause | Neutral | Standard-Regeln |

---

## 📅 Wirtschaftskalender – No-Trade-Tage

An diesen Tagen keine neuen Positionen eröffnen:

| Event | Warum gefährlich |
|-------|------------------|
| **FOMC-Entscheid** | Sofortige, unvorhersehbare Marktreaktion |
| **US CPI-Veröffentlichung** | Inflationsdaten bewegen Fed-Erwartungen massiv |
| **NFP (Non-Farm Payrolls)** | Jobs-Daten steuern Fed-Zinspfad |
| **Quadruple Witching** | Derivatives-Ablauf, extreme Volatilität |
| **Jackson Hole Symposium** | Fed-Vorsitzender signalisiert Zinspolitik |

**Regel:** Finnhub Earnings-Kalender täglich abrufen. Wenn Top-10-S&P500-Unternehmen (Apple, MSFT, NVIDIA etc.) reporten → keine Orders.

---

## 🧭 Entscheidungsbeispiele

### Beispiel 1: Klares Kaufsignal
```
Datum: normaler Handelstag, 10:00 ET
SPY Kurs: 520 USD, MA200: 490 USD  → bullish (+2)
MA50 > MA200                       → Golden Cross (+1)
RSI: 48                            → neutral (+1)
Fear&Greed: 38                     → Fear (+1)
VIX: 16                            → normal (0)
T10Y2Y: +0.3%                      → normal (0)
Kein Event heute                   → (0)

SCORE = 5 → KAUF erlaubt
Ordre: SPY, 10% des Portfolio-Werts
```

### Beispiel 2: Klares Halte-Signal
```
SPY Kurs: 500 USD, MA200: 495 USD  → bullish, aber knapp (+1)
RSI: 72                            → überkauft (-0, kein Kaufsignal)
Fear&Greed: 78                     → Extreme Greed (-1)
VIX: 14                            → normal (0)
FOMC heute                         → (-1)

SCORE = -1 → NICHT handeln, bestehende Position halten
```

### Beispiel 3: Verkaufssignal
```
SPY Kurs: 440 USD, MA200: 490 USD  → bearish (-2)
RSI: 35                            → überverkauft (0)
Fear&Greed: 18                     → Extreme Fear (+1)
VIX: 38                            → Krise (-1)
T10Y2Y: -0.5%                      → Invertiert (-1)

SCORE = -3 → Position um 50% reduzieren
```
