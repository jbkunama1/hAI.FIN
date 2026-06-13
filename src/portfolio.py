"""hAI.FIN – Portfolio-Verwaltung und Guardrail-Checks."""

import logging
from typing import Optional

logger = logging.getLogger("haifin.portfolio")

# Zielallokation
TARGET_ALLOCATION = {"SPY": 0.40, "QQQ": 0.30, "VTI": 0.20, "CASH": 0.10}


class Portfolio:
    """
    Vereinfachtes Portfolio-Modell fuer DRY_RUN und spaetere eToro-API-Anbindung.
    Im DRY_RUN-Modus werden alle Werte in-memory gehalten.
    """

    def __init__(self,
                 initial_cash: float = 10_000.0,
                 max_position_pct: float = 0.10,
                 min_cash_reserve_pct: float = 0.20,
                 max_trades_per_day: int = 3):
        self.cash               = initial_cash
        self.positions: dict    = {}      # symbol -> USD-Wert
        self.trades_today: int  = 0
        self.max_position_pct   = max_position_pct
        self.min_cash_reserve_pct = min_cash_reserve_pct
        self.max_trades_per_day = max_trades_per_day

    @property
    def total_value(self) -> float:
        return self.cash + sum(self.positions.values())

    @property
    def cash_pct(self) -> float:
        return self.cash / self.total_value if self.total_value > 0 else 1.0

    def state(self) -> dict:
        total = self.total_value
        return {
            "total_usd":    round(total, 2),
            "cash_usd":     round(self.cash, 2),
            "cash_pct":     round(self.cash_pct * 100, 1),
            "positions":    {k: round(v, 2) for k, v in self.positions.items()},
            "trades_today": self.trades_today,
        }

    # ------------------------------------------------------------------
    # Guardrails
    # ------------------------------------------------------------------

    def check_guardrails(self, symbol: str, amount_usd: float,
                         allowed_assets: list) -> tuple[bool, str]:
        """Gibt (ok: bool, reason: str) zurueck."""
        if symbol not in allowed_assets:
            return False, f"{symbol} nicht in ALLOWED_ASSETS"

        if self.trades_today >= self.max_trades_per_day:
            return False, f"MAX_TRADES_PER_DAY ({self.max_trades_per_day}) erreicht"

        cash_after = self.cash - amount_usd
        min_cash   = self.total_value * self.min_cash_reserve_pct
        if cash_after < min_cash:
            return False, (
                f"Cash nach Trade ({cash_after:.0f} USD) < Mindestcash "
                f"({min_cash:.0f} USD = {self.min_cash_reserve_pct*100:.0f}%)"
            )

        pos_after  = self.positions.get(symbol, 0) + amount_usd
        max_pos    = self.total_value * self.max_position_pct
        if pos_after > max_pos:
            return False, (
                f"Position nach Trade ({pos_after:.0f} USD) > MAX "
                f"({max_pos:.0f} USD = {self.max_position_pct*100:.0f}%)"
            )

        return True, "Alle Guardrails OK"

    # ------------------------------------------------------------------
    # Trade-Ausfuehrung (DRY_RUN)
    # ------------------------------------------------------------------

    def execute_buy(self, symbol: str, amount_usd: float, dry_run: bool = True) -> dict:
        """Kauf simulieren oder (spaeter) echten Order senden."""
        if amount_usd <= 0 or amount_usd > self.cash:
            return {"status": "error", "reason": "Ungueltige Order-Groesse"}

        if dry_run:
            self.cash -= amount_usd
            self.positions[symbol] = self.positions.get(symbol, 0) + amount_usd
            self.trades_today += 1
            logger.info(f"[DRY_RUN] BUY {symbol} {amount_usd:.2f} USD")
            return {"status": "simulated", "symbol": symbol, "amount_usd": amount_usd}
        else:
            # Hier kommt spaeter die echte eToro-API-Integration
            logger.warning("LIVE-Trading noch nicht implementiert – Fallback auf DRY_RUN")
            return self.execute_buy(symbol, amount_usd, dry_run=True)

    def execute_reduce(self, symbol: str, fraction: float = 0.5,
                       dry_run: bool = True) -> dict:
        """Position um 'fraction' reduzieren."""
        pos = self.positions.get(symbol, 0)
        if pos <= 0:
            return {"status": "skip", "reason": f"Keine Position in {symbol}"}
        sell_amount = round(pos * fraction, 2)
        if dry_run:
            self.positions[symbol] = round(pos - sell_amount, 2)
            self.cash += sell_amount
            self.trades_today += 1
            logger.info(f"[DRY_RUN] REDUCE {symbol} -{sell_amount:.2f} USD ({fraction*100:.0f}%)")
            return {"status": "simulated", "symbol": symbol, "sold_usd": sell_amount}
        else:
            logger.warning("LIVE-Trading noch nicht implementiert – Fallback auf DRY_RUN")
            return self.execute_reduce(symbol, fraction, dry_run=True)
