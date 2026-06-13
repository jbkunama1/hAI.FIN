"""hAI.FIN – Marktdaten-Abruf (CNN F&G, yfinance, FRED)"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import requests
import yfinance as yf
import pandas as pd

logger = logging.getLogger("haifin.fetcher")

FRED_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv"
FEAR_GREED_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
HEADERS = {"User-Agent": "Mozilla/5.0 (hAI.FIN trading agent)"}
TIMEOUT = 10  # Sekunden


def fetch_fear_greed() -> Optional[float]:
    """CNN Fear & Greed Index – aktueller Score (0-100). None bei Fehler."""
    try:
        r = requests.get(FEAR_GREED_URL, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        score = float(data["fear_and_greed"]["score"])
        logger.info(f"Fear&Greed Score: {score:.1f}")
        return score
    except Exception as e:
        logger.warning(f"Fear&Greed Abruf fehlgeschlagen: {e}")
        return None


def fetch_ticker_signals(symbol: str) -> dict:
    """Kursdaten, MA200, MA50, RSI(14) via yfinance."""
    result = {"symbol": symbol, "price": None, "ma200": None, "ma50": None, "rsi": None, "error": None}
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y", auto_adjust=True)
        if hist.empty or len(hist) < 200:
            raise ValueError(f"Zu wenige Datenpunkte fuer {symbol}: {len(hist)}")
        close = hist["Close"]
        result["price"]  = round(float(close.iloc[-1]), 4)
        result["ma200"]  = round(float(close.rolling(200).mean().iloc[-1]), 4)
        result["ma50"]   = round(float(close.rolling(50).mean().iloc[-1]), 4)
        result["rsi"]    = round(_calc_rsi(close), 2)
        logger.info(f"{symbol} | Kurs={result['price']} MA200={result['ma200']} RSI={result['rsi']}")
    except Exception as e:
        result["error"] = str(e)
        logger.warning(f"{symbol} Datenabruf fehlgeschlagen: {e}")
    return result


def _calc_rsi(series: pd.Series, period: int = 14) -> float:
    """Wilder RSI berechnen."""
    delta = series.diff().dropna()
    gain  = delta.clip(lower=0).ewm(com=period - 1, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(com=period - 1, adjust=False).mean()
    rs    = gain / loss.replace(0, float("inf"))
    return float(100 - (100 / (1 + rs.iloc[-1])))


def fetch_fred_series(series_id: str) -> Optional[float]:
    """Letzten Wert einer FRED-Zeitserie abrufen (kein Key noetig)."""
    try:
        url = f"{FRED_BASE}?id={series_id}"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        lines = [l for l in r.text.strip().splitlines() if not l.startswith("DATE")]
        # letzten gueltigen (nicht '.') Wert suchen
        for line in reversed(lines):
            _, val = line.split(",")
            if val.strip() != ".":
                result = float(val.strip())
                logger.info(f"FRED {series_id}: {result}")
                return result
        return None
    except Exception as e:
        logger.warning(f"FRED {series_id} fehlgeschlagen: {e}")
        return None


def fetch_vix() -> Optional[float]:
    """VIX via FRED (VIXCLS)."""
    return fetch_fred_series("VIXCLS")


def fetch_yield_spread() -> Optional[float]:
    """10Y-2Y Treasury Spread via FRED (T10Y2Y). Negativ = invertiert."""
    return fetch_fred_series("T10Y2Y")


def fetch_earnings_events(finnhub_key: Optional[str] = None) -> bool:
    """True wenn heute Earnings-Events grosser Unternehmen. Graceful fallback."""
    if not finnhub_key:
        logger.info("Kein Finnhub-Key – Earnings-Check uebersprungen")
        return False
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        url = (
            f"https://finnhub.io/api/v1/calendar/earnings"
            f"?from={today}&to={today}&token={finnhub_key}"
        )
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json().get("earningsCalendar", [])
        big = [e for e in data if e.get("symbol") in {
            "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","BRK.B","JPM","V"
        }]
        if big:
            logger.info(f"Earnings-Event heute: {[e['symbol'] for e in big]}")
        return bool(big)
    except Exception as e:
        logger.warning(f"Finnhub Earnings-Check fehlgeschlagen: {e}")
        return False


def fetch_all(symbol: str = "SPY", finnhub_key: Optional[str] = None) -> dict:
    """Alle Marktdaten in einem Dict sammeln."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "ticker": fetch_ticker_signals(symbol),
        "fear_greed": fetch_fear_greed(),
        "vix": fetch_vix(),
        "yield_spread": fetch_yield_spread(),
        "earnings_event_today": fetch_earnings_events(finnhub_key),
    }
