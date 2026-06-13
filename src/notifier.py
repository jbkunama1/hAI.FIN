"""hAI.FIN – Telegram-Benachrichtigungen bei Trades und Fehlern."""

import os
import logging
import requests
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("haifin.notifier")

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
TIMEOUT = 8


class TelegramNotifier:
    """
    Sendet formatierte Nachrichten an einen Telegram-Chat.
    Initialisierung erfolgt automatisch aus Umgebungsvariablen.
    Wenn kein Token/Chat-ID vorhanden → stilles No-Op (kein Absturz).
    """

    def __init__(self,
                 token: Optional[str] = None,
                 chat_id: Optional[str] = None):
        self.token   = token   or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.enabled = bool(self.token and self.chat_id)
        if not self.enabled:
            logger.info("Telegram-Notifier deaktiviert (kein Token/Chat-ID).")

    # ------------------------------------------------------------------
    # Basis-Send
    # ------------------------------------------------------------------

    def send(self, text: str, silent: bool = False) -> bool:
        """Nachricht senden. Gibt True bei Erfolg zurueck."""
        if not self.enabled:
            return False
        try:
            url  = TELEGRAM_API.format(token=self.token)
            resp = requests.post(url, json={
                "chat_id":              self.chat_id,
                "text":                 text,
                "parse_mode":           "HTML",
                "disable_notification": silent,
            }, timeout=TIMEOUT)
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.warning(f"Telegram-Fehler: {e}")
            return False

    # ------------------------------------------------------------------
    # Trade-Nachrichten
    # ------------------------------------------------------------------

    def notify_trade(self, action: str, symbol: str, amount_usd: float,
                     score: int, reason: str, dry_run: bool = True) -> bool:
        """Nachricht nach Kauf, Verkauf oder Reduktion."""
        icons = {"BUY": "✅", "SELL": "🔴", "REDUCE": "⚠️", "HOLD": "🟡", "SKIP": "⏭️", "EMERGENCY": "🚨"}
        icon  = icons.get(action.upper(), "⚪")
        label = "[DRY RUN]" if dry_run else "[LIVE]"
        ts    = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        text = (
            f"{icon} <b>hAI.FIN {label}</b>\n"
            f"\n"
            f"<b>Aktion:</b>  {action.upper()}\n"
            f"<b>Asset:</b>   {symbol}\n"
            f"<b>Betrag:</b>  ${amount_usd:,.2f}\n"
            f"<b>Score:</b>   {score:+d}\n"
            f"<b>Grund:</b>   {reason}\n"
            f"\n"
            f"<i>{ts}</i>"
        )
        return self.send(text, silent=(action in ("HOLD", "SKIP")))

    def notify_buy(self, symbol: str, amount_usd: float,
                   score: int, reason: str, dry_run: bool = True) -> bool:
        return self.notify_trade("BUY", symbol, amount_usd, score, reason, dry_run)

    def notify_reduce(self, symbol: str, amount_usd: float,
                      score: int, reason: str, dry_run: bool = True) -> bool:
        return self.notify_trade("REDUCE", symbol, amount_usd, score, reason, dry_run)

    # ------------------------------------------------------------------
    # Status-Nachrichten
    # ------------------------------------------------------------------

    def notify_portfolio(self, state: dict, dry_run: bool = True) -> bool:
        """Tägliche Portfolio-Zusammenfassung."""
        label = "[DRY RUN]" if dry_run else "[LIVE]"
        ts    = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        pos_lines = ""
        for sym, val in state.get("positions", {}).items():
            pct = val / state["total_usd"] * 100 if state["total_usd"] else 0
            pos_lines += f"  • {sym}: ${val:,.0f} ({pct:.1f}%)\n"
        if not pos_lines:
            pos_lines = "  • Keine offenen Positionen\n"

        text = (
            f"💼 <b>hAI.FIN Portfolio {label}</b>\n"
            f"\n"
            f"<b>Gesamt:</b>      ${state['total_usd']:,.0f}\n"
            f"<b>Cash:</b>        ${state['cash_usd']:,.0f} ({state['cash_pct']:.1f}%)\n"
            f"<b>Trades heute:</b> {state['trades_today']}\n"
            f"\n"
            f"<b>Positionen:</b>\n{pos_lines}"
            f"<i>{ts}</i>"
        )
        return self.send(text, silent=True)

    def notify_market_summary(self, fear_greed: Optional[float],
                              vix: Optional[float],
                              spread: Optional[float],
                              top_signal: str) -> bool:
        """Morgen-Briefing mit Marktlage."""
        fg_label  = _fg_text(fear_greed)
        vix_label = f"⚠️ {vix:.1f} (hoch!)" if (vix and vix > 30) else f"✅ {vix:.1f}" if vix else "n/a"
        sp_label  = f"🔴 {spread:+.2f}% (invertiert)" if (spread is not None and spread < 0) \
                    else f"✅ {spread:+.2f}%" if spread is not None else "n/a"
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        text = (
            f"🌅 <b>hAI.FIN Morgen-Briefing</b>\n"
            f"\n"
            f"😱 <b>Fear &amp; Greed:</b> {fg_label}\n"
            f"📈 <b>VIX:</b>           {vix_label}\n"
            f"🏦 <b>10Y-2Y Spread:</b> {sp_label}\n"
            f"🎯 <b>Top-Signal:</b>    {top_signal}\n"
            f"\n"
            f"<i>{ts}</i>"
        )
        return self.send(text)

    def notify_error(self, context: str, error: str) -> bool:
        """Kritischer Fehler – immer mit Ton."""
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        text = (
            f"🚨 <b>hAI.FIN FEHLER</b>\n"
            f"\n"
            f"<b>Kontext:</b> {context}\n"
            f"<b>Fehler:</b>  <code>{error[:300]}</code>\n"
            f"\n"
            f"<i>{ts}</i>"
        )
        return self.send(text, silent=False)

    def notify_emergency(self, vix: float) -> bool:
        """VIX-Notbremse ausgelöst."""
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        text = (
            f"🚨 <b>hAI.FIN NOTBREMSE</b>\n"
            f"\n"
            f"VIX = <b>{vix:.1f}</b> überschreitet Grenzwert!\n"
            f"Agent wechselt in <b>Cash-Modus</b>.\n"
            f"Keine neuen Käufe bis Normalisierung.\n"
            f"\n"
            f"<i>{ts}</i>"
        )
        return self.send(text, silent=False)


# ------------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------------

def _fg_text(score: Optional[float]) -> str:
    if score is None:  return "n/a"
    if score < 25:     return f"😱 {score:.0f} – Extreme Angst"
    if score < 45:     return f"😟 {score:.0f} – Angst"
    if score < 56:     return f"😐 {score:.0f} – Neutral"
    if score < 75:     return f"😏 {score:.0f} – Gier"
    return f"🤑 {score:.0f} – Extreme Gier"
