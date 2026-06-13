"""hAI.FIN – Composite Signal Score Berechnung."""

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("haifin.signals")


@dataclass
class SignalScore:
    total: int = 0
    components: dict = field(default_factory=dict)
    action: str = "SKIP"       # BUY | HOLD | SKIP | REDUCE
    reason: str = ""

    def add(self, name: str, value: int, detail: str = ""):
        self.components[name] = {"value": value, "detail": detail}
        self.total += value

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "action": self.action,
            "reason": self.reason,
            "components": self.components,
        }


def calculate_score(market_data: dict) -> SignalScore:
    """
    Composite Signal Score gemaess system-prompt.md.

    Scoring:
      +2  Kurs > MA200
      +1  MA50 > MA200 (Golden Cross)
      +1  RSI 35-60 (neutral zone)
      +1  Fear&Greed < 45
      -1  Fear&Greed > 75
      -2  Kurs < MA200
      -1  VIX > 30
      -1  Zinskurve invertiert (T10Y2Y < 0)
      -1  Earnings-Event / No-Trade-Tag
    """
    score = SignalScore()
    t = market_data.get("ticker", {})

    price  = t.get("price")
    ma200  = t.get("ma200")
    ma50   = t.get("ma50")
    rsi    = t.get("rsi")
    fg     = market_data.get("fear_greed")
    vix    = market_data.get("vix")
    spread = market_data.get("yield_spread")
    event  = market_data.get("earnings_event_today", False)

    # --- Trend ---
    if price is not None and ma200 is not None:
        if price > ma200:
            score.add("ma200_trend", +2, f"Kurs {price:.2f} > MA200 {ma200:.2f} (bullish)")
        else:
            score.add("ma200_trend", -2, f"Kurs {price:.2f} < MA200 {ma200:.2f} (bearish)")
    else:
        score.add("ma200_trend", 0, "Kein Datenpunkt (neutral)")

    if ma50 is not None and ma200 is not None:
        if ma50 > ma200:
            score.add("golden_cross", +1, f"MA50 {ma50:.2f} > MA200 {ma200:.2f}")
        else:
            score.add("golden_cross", 0, f"MA50 {ma50:.2f} <= MA200 {ma200:.2f} (kein Golden Cross)")

    # --- Momentum ---
    if rsi is not None:
        if 35 <= rsi <= 60:
            score.add("rsi", +1, f"RSI {rsi:.1f} in neutraler Zone (35-60)")
        elif rsi > 70:
            score.add("rsi", 0, f"RSI {rsi:.1f} ueberkauft (>70) – kein Bonus")
        else:
            score.add("rsi", 0, f"RSI {rsi:.1f} ausserhalb neutraler Zone")
    else:
        score.add("rsi", 0, "RSI nicht verfuegbar")

    # --- Sentiment ---
    if fg is not None:
        if fg < 45:
            score.add("fear_greed", +1, f"Fear&Greed {fg:.0f} – Markt hat Angst (kontraer positiv)")
        elif fg > 75:
            score.add("fear_greed", -1, f"Fear&Greed {fg:.0f} – Extreme Gier (Vorsicht)")
        else:
            score.add("fear_greed", 0, f"Fear&Greed {fg:.0f} – neutral")
    else:
        score.add("fear_greed", 0, "Fear&Greed nicht verfuegbar")

    # --- Makro ---
    if vix is not None and vix > 30:
        score.add("vix", -1, f"VIX {vix:.1f} > 30 – erhoehte Volatilitaet")
    else:
        score.add("vix", 0, f"VIX {vix:.1f if vix else 'n/a'} – normal")

    if spread is not None and spread < 0:
        score.add("yield_curve", -1, f"T10Y2Y {spread:.2f}% – Zinskurve invertiert (Rezessionssignal)")
    else:
        score.add("yield_curve", 0, f"T10Y2Y {spread:.2f}% – normal" if spread is not None else "T10Y2Y nicht verfuegbar")

    # --- Event-Risiko ---
    if event:
        score.add("event_risk", -1, "Earnings-Event grosser S&P500-Komponente heute")
    else:
        score.add("event_risk", 0, "Kein bekanntes Event heute")

    # --- Aktion bestimmen ---
    if score.total >= 3:
        score.action = "BUY"
        score.reason  = f"Score {score.total} >= 3: Kaufbedingungen erfuellt"
    elif score.total >= 1:
        score.action = "HOLD"
        score.reason  = f"Score {score.total}: Positionen halten, kein Aufbau"
    elif score.total <= -2:
        score.action = "REDUCE"
        score.reason  = f"Score {score.total} <= -2: Position reduzieren"
    else:
        score.action = "SKIP"
        score.reason  = f"Score {score.total}: Nicht handeln"

    logger.info(f"Composite Score={score.total} → {score.action} | {score.reason}")
    return score
