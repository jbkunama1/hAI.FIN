# hAI.FIN – Agent Knowledge Base

Diese Datei enthält strukturiertes Hintergrundwissen für den Agenten.
Sie wird bei Bedarf als zusätzlicher Kontext mitgegeben.

---

## 📊 ETF-Profile (Erlaubte Assets)

### SPY – SPDR S&P 500 ETF Trust
- **Index:** S&P 500 (500 größte US-Unternehmen)
- **TER:** 0.0945%
- **AUM:** ~500 Mrd. USD (größter ETF weltweit)
- **Ausschüttung:** Quartalsweise Dividenden
- **Volatilität:** Mittel (~15% annualisiert im Durchschnitt)
- **Typischer Drawdown Rezession:** -30 bis -50%
- **Geeignet für:** Kern-Position, langfristiger Aufbau

### QQQ – Invesco NASDAQ-100 ETF
- **Index:** NASDAQ-100 (100 größte Nicht-Finanz-Unternehmen an NASDAQ)
- **TER:** 0.20%
- **Top-Holdings:** Apple, Microsoft, NVIDIA, Amazon, Meta, Alphabet
- **Volatilität:** Hoch (~20% annualisiert)
- **Typischer Drawdown Rezession:** -40 bis -80%
- **Besonderheit:** Sehr tech-lastig, korreliert stark mit Zinsentscheiden
- **Geeignet für:** Wachstums-Beimischung, NICHT als Hauptposition

### VTI – Vanguard Total Stock Market ETF
- **Index:** CRSP US Total Market (~4000 US-Aktien)
- **TER:** 0.03% (einer der günstigsten ETFs)
- **Besonderheit:** Enthält auch Mid- und Small-Caps zusätzlich zu S&P 500
- **Volatilität:** Ähnlich SPY, leicht höher durch Small-Cap-Anteil
- **Geeignet für:** Breite US-Markt-Exposition

### VWCE – Vanguard FTSE All-World UCITS ETF (Acc)
- **Index:** FTSE All-World (~3700 Aktien, global)
- **TER:** 0.22%
- **Währung:** EUR (XETRA-notiert)
- **Besonderheit:** Thesaurierend (keine Ausschüttung), ideal für europäische Anleger
- **Geeignet für:** Globale Diversifikation, EUR-Anleger

### VUSA – Vanguard S&P 500 UCITS ETF
- **Index:** S&P 500
- **TER:** 0.07%
- **Währung:** USD / GBP / EUR (je nach Börse)
- **Besonderheit:** Europäische UCITS-Version des S&P 500, geringer TER als SPY
- **Geeignet für:** Europäische Anleger, die S&P 500 abbilden wollen

---

## 📅 Marktkalender & Wichtige Termine

### US-Handelszeiten
- Normale Handelszeiten: Mo–Fr, 09:30–16:00 ET (15:30–22:00 MEZ)
- US-Feiertage: Kein Handel (NYSE geschlossen)

### Regelmäßige Markt-Events (Vorsicht)
| Event | Häufigkeit | Auswirkung |
|-------|------------|------------|
| Fed FOMC Meeting | 8x jährlich | Hoch (Zinserwartungen) |
| US CPI (Inflation) | Monatlich | Hoch (Fed-Erwartungen) |
| US Jobs Report (NFP) | 1. Freitag/Monat | Mittel-Hoch |
| Earnings Season | Quartalsweise (Jan/Apr/Jul/Okt) | Mittel |
| Quadruple Witching | 3. Freitag März/Jun/Sep/Dez | Erhöhte Volatilität |

**Regel:** An Tagen mit Fed-Entscheiden oder CPI-Veröffentlichung: keine neuen Positionen eröffnen.

---

## 📉 Risiko-Referenzwerte

| Metrik | Konservativ | Moderat | Aggressiv |
|--------|------------|---------|----------|
| Max. Drawdown (Ziel) | -15% | -25% | -40% |
| Sharpe Ratio (Ziel) | > 0.8 | > 1.0 | > 1.2 |
| Cash-Reserve | 20-30% | 10-20% | 0-10% |
| Max. Position | 10% | 20% | 30% |
| Trades/Tag | 1-3 | 3-5 | 5-10 |

hAI.FIN operiert standardmäßig im **konservativen** Modus.

---

## 🔍 Checkliste vor jedem Trade

```
[ ] Asset in ALLOWED_ASSETS?
[ ] Handelszeit gültig (09:30-16:00 ET)?
[ ] Trades heute < MAX_TRADES_PER_DAY?
[ ] Cash nach Trade >= MIN_CASH_RESERVE_PERCENT?
[ ] Position nach Trade <= MAX_POSITION_PERCENT?
[ ] Kein Fed/CPI-Event heute?
[ ] Preis > MA200 (für Käufe)?
[ ] RSI zwischen 35-65?
[ ] DRY_RUN=false (für echte Ausführung)?
```

Alle 9 Häkchen = Trade erlaubt.
Ein fehlendes Häkchen = Trade nicht ausführen.
