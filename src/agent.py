"""hAI.FIN – Hauptschleife des Agenten."""

import os
import logging
import time
from datetime import datetime, timezone

from src.logger import setup_logging, write_trade_log
from src.data_fetcher import fetch_all
from src.signals import calculate_score
from src.portfolio import Portfolio

logger = logging.getLogger("haifin.agent")

# Umgebungsvariablen
DRY_RUN          = os.getenv("DRY_RUN", "true").lower() == "true"
LOG_LEVEL        = os.getenv("LOG_LEVEL", "INFO")
FINNHUB_KEY      = os.getenv("FINNHUB_KEY", "")
ALLOWED_ASSETS   = os.getenv("ALLOWED_ASSETS", "SPY,QQQ,VTI").split(",")
INITIAL_CASH     = float(os.getenv("INITIAL_CASH", "10000"))
ORDER_SIZE_PCT   = float(os.getenv("ORDER_SIZE_PCT", "0.05"))   # 5% pro Trade
MAX_TRADES       = int(os.getenv("MAX_TRADES_PER_DAY", "3"))
MIN_CASH_PCT     = float(os.getenv("MIN_CASH_RESERVE_PCT", "0.20"))
MAX_POS_PCT      = float(os.getenv("MAX_POSITION_PCT", "0.10"))

# VIX-Notbremse: ab diesem Wert geht der Agent in Cash-Modus
VIX_EMERGENCY    = float(os.getenv("VIX_EMERGENCY", "40"))


def run_cycle(portfolio: Portfolio, symbol: str = "SPY") -> str:
    """
    Einen vollstaendigen Entscheidungszyklus ausfuehren.
    Gibt die ausgefuehrte Aktion zurueck (BUY/HOLD/SKIP/REDUCE/EMERGENCY).
    """
    logger.info(f"=== Zyklus-Start | {symbol} | DRY_RUN={DRY_RUN} ===")

    # Schritt 1: Marktdaten abrufen
    market_data = fetch_all(symbol=symbol, finnhub_key=FINNHUB_KEY or None)

    # Schritt 2: VIX-Notbremse
    vix = market_data.get("vix")
    if vix is not None and vix > VIX_EMERGENCY:
        logger.warning(f"VIX NOTBREMSE: {vix:.1f} > {VIX_EMERGENCY} – Cash-Modus")
        write_trade_log(
            action="EMERGENCY", symbol=symbol, amount_usd=0,
            score={"total": -99, "reason": f"VIX {vix:.1f} > {VIX_EMERGENCY}"},
            portfolio_state=portfolio.state(), dry_run=DRY_RUN
        )
        return "EMERGENCY"

    # Schritt 3: Composite Score berechnen
    signal = calculate_score(market_data)

    # Schritt 4: Aktion ausfuehren
    order_amount = round(portfolio.total_value * ORDER_SIZE_PCT, 2)
    result = {"status": "none"}

    if signal.action == "BUY":
        ok, reason = portfolio.check_guardrails(symbol, order_amount, ALLOWED_ASSETS)
        if ok:
            result = portfolio.execute_buy(symbol, order_amount, dry_run=DRY_RUN)
        else:
            signal.action = "SKIP"
            signal.reason  = f"Guardrail blockiert: {reason}"
            logger.info(f"BUY blockiert: {reason}")

    elif signal.action == "REDUCE":
        result = portfolio.execute_reduce(symbol, fraction=0.5, dry_run=DRY_RUN)

    # Schritt 5: Pflicht-Log
    write_trade_log(
        action=signal.action,
        symbol=symbol,
        amount_usd=order_amount if signal.action == "BUY" else 0,
        score=signal.as_dict(),
        portfolio_state=portfolio.state(),
        dry_run=DRY_RUN,
    )

    logger.info(f"=== Zyklus-Ende | {signal.action} | Score={signal.total} ===")
    return signal.action


def main():
    """Einstiegspunkt – laeuft als Daemon oder einmalig (per Cron)."""
    setup_logging(log_dir="logs", level=LOG_LEVEL)
    logger.info("hAI.FIN Agent gestartet")
    logger.info(f"DRY_RUN={DRY_RUN} | Assets={ALLOWED_ASSETS} | Cash={INITIAL_CASH}")

    portfolio = Portfolio(
        initial_cash=INITIAL_CASH,
        max_position_pct=MAX_POS_PCT,
        min_cash_reserve_pct=MIN_CASH_PCT,
        max_trades_per_day=MAX_TRADES,
    )

    # Pro Asset einen Zyklus ausfuehren
    for asset in ALLOWED_ASSETS:
        try:
            run_cycle(portfolio, symbol=asset.strip())
            time.sleep(2)  # Rate-Limit-Schutz
        except Exception as e:
            logger.error(f"Unbehandelter Fehler bei {asset}: {e}", exc_info=True)

    logger.info(f"Portfolio-Status: {portfolio.state()}")
    logger.info("hAI.FIN Agent beendet")


if __name__ == "__main__":
    main()
