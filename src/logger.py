"""hAI.FIN – Strukturiertes JSON-Logging."""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """Gibt jeden Log-Eintrag als JSON-Zeile aus."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts":      datetime.now(timezone.utc).isoformat(),
            "level":   record.levelname,
            "logger":  record.name,
            "msg":     record.getMessage(),
        }
        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


def setup_logging(log_dir: str = "logs", level: str = "INFO") -> None:
    """Logging einrichten: JSON-Datei + lesbarer Console-Output."""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = log_path / f"haifin_{today}.log"

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # JSON-Datei
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(JsonFormatter())
    root.addHandler(fh)

    # Konsole (human-readable)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s – %(message)s",
        datefmt="%H:%M:%S"
    ))
    root.addHandler(ch)


def write_trade_log(action: str, symbol: str, amount_usd: float,
                   score: dict, portfolio_state: dict,
                   dry_run: bool = True) -> None:
    """Pflicht-Log-Eintrag nach jeder Entscheidung (auch HOLD/SKIP)."""
    trade_logger = logging.getLogger("haifin.trade")
    entry = {
        "action":     action,          # BUY | SELL | HOLD | SKIP | REDUCE
        "symbol":     symbol,
        "amount_usd": amount_usd,
        "dry_run":    dry_run,
        "score":      score,
        "portfolio":  portfolio_state,
        "ts":         datetime.now(timezone.utc).isoformat(),
    }
    trade_logger.info(json.dumps(entry, ensure_ascii=False))
