"""hAI.FIN – Hauptschleife des Agenten (mit Telegram-Notifier)."""

import os
import logging
import time
from datetime import datetime, timezone

from src.logger import setup_logging, write_trade_log
from src.data_fetcher import fetch_all
from src.signals import calculate_score
from src.portfolio import Portfolio
from src.notifier import TelegramNotifier

logger = logging.getLogger("haifin.agent")

# Umgebungsvariablen
DRY_RUN           = os.getenv("DRY_RUN", "true").lower() == "true"
LOG_LEVEL         = os.getenv("LOG_LEVEL", "INFO")
FINNHUB_KEY       = os.getenv("FINNHUB_KEY", "")
ALLOWED_ASSETS    = os.getenv("ALLOWED_ASSETS", "SPY,QQQ,VTI").split(",")
INITIAL_CASH      = float(os.getenv("INITIAL_CASH", "10000"))
ORDER_SIZE_PCT    = float(os.getenv("ORDER_SIZE_PCT", "0.05"))
MAX_TRADES        = int(os.getenv("MAX_TRADES_PER_DAY", "3"))
MIN_CASH_PCT      = float(os.getenv("MIN_CASH_RESERVE_PCT", "0.20"))
MAX_POS_PCT       = float(os.getenv("MAX_POSITION_PCT", "0.10"))
VIX_EMERGENCY     = float(os.getenv("VIX_EMERGENCY", "40"))
MORNING_BRIEFING  = os.getenv("TELEGRAM_MORNING_BRIEFING", "true").lower() == "true"


def run_cycle(portfolio: Portfolio, notifier: TelegramNotifier,
              symbol: str = "SPY") -> str:
    logger.info(f"=== Zyklus-Start | {symbol} | DRY_RUN={DRY_RUN} ===")

    # Schritt 1: Marktdaten
    market_data = fetch_all(symbol=symbol, finnhub_key=FINNHUB_KEY or None)

    # Schritt 2: VIX-Notbremse
    vix = market_data.get("vix")
    if vix is not None and vix > VIX_EMERGENCY:
        logger.warning(f"VIX NOTBREMSE: {vix:.1f}")
        notifier.notify_emergency(vix)
        write_trade_log(
            action="EMERGENCY", symbol=symbol, amount_usd=0,
            score={"total": -99, "reason": f"VIX {vix:.1f} > {VIX_EMERGENCY}"},
            portfolio_state=portfolio.state(), dry_run=DRY_RUN
        )
        return "EMERGENCY"

    # Schritt 3: Signal berechnen
    signal = calculate_score(market_data)

    # Schritt 4: Aktion
    order_amount = round(portfolio.total_value * ORDER_SIZE_PCT, 2)

    if signal.action == "BUY":
        ok, reason = portfolio.check_guardrails(symbol, order_amount, ALLOWED_ASSETS)
        if ok:
            portfolio.execute_buy(symbol, order_amount, dry_run=DRY_RUN)
            notifier.notify_buy(symbol, order_amount, signal.total,
                                signal.reason, dry_run=DRY_RUN)
        else:
            signal.action = "SKIP"
            signal.reason  = f"Guardrail: {reason}"
            logger.info(f"BUY blockiert: {reason}")

    elif signal.action == "REDUCE":
        res = portfolio.execute_reduce(symbol, fraction=0.5, dry_run=DRY_RUN)
        sold = res.get("sold_usd", 0)
        notifier.notify_reduce(symbol, sold, signal.total,
                               signal.reason, dry_run=DRY_RUN)

    # Schritt 5: Pflicht-Log
    write_trade_log(
        action=signal.action, symbol=symbol,
        amount_usd=order_amount if signal.action == "BUY" else 0,
        score=signal.as_dict(), portfolio_state=portfolio.state(),
        dry_run=DRY_RUN,
    )

    logger.info(f"=== Zyklus-Ende | {signal.action} | Score={signal.total} ===")
    return signal.action


def main():
    setup_logging(log_dir="logs", level=LOG_LEVEL)
    logger.info("hAI.FIN Agent gestartet")

    notifier  = TelegramNotifier()
    portfolio = Portfolio(
        initial_cash=INITIAL_CASH,
        max_position_pct=MAX_POS_PCT,
        min_cash_reserve_pct=MIN_CASH_PCT,
        max_trades_per_day=MAX_TRADES,
    )

    # Morgen-Briefing (erstes Asset als Marktproxy)
    if MORNING_BRIEFING:
        try:
            first = fetch_all(symbol="SPY", finnhub_key=FINNHUB_KEY or None)
            sig   = calculate_score(first)
            notifier.notify_market_summary(
                fear_greed=first.get("fear_greed"),
                vix=first.get("vix"),
                spread=first.get("yield_spread"),
                top_signal=f"SPY → {sig.action} (Score {sig.total})",
            )
        except Exception as e:
            logger.warning(f"Morgen-Briefing fehlgeschlagen: {e}")

    # Pro Asset einen Zyklus
    for asset in ALLOWED_ASSETS:
        try:
            run_cycle(portfolio, notifier, symbol=asset.strip())
            time.sleep(2)
        except Exception as e:
            logger.error(f"Fehler bei {asset}: {e}", exc_info=True)
            notifier.notify_error(context=f"Zyklus {asset}", error=str(e))

    # Tagesabschluss: Portfolio-Status senden
    notifier.notify_portfolio(portfolio.state(), dry_run=DRY_RUN)
    logger.info(f"Portfolio: {portfolio.state()}")
    logger.info("hAI.FIN Agent beendet")


if __name__ == "__main__":
    main()
