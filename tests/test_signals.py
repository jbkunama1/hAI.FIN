"""Unit-Tests fuer src/signals.py"""

import pytest
from src.signals import calculate_score


def _make_data(price=520, ma200=490, ma50=500, rsi=48,
               fg=38, vix=16, spread=0.3, event=False):
    return {
        "symbol": "SPY",
        "ticker": {"price": price, "ma200": ma200, "ma50": ma50, "rsi": rsi},
        "fear_greed": fg,
        "vix": vix,
        "yield_spread": spread,
        "earnings_event_today": event,
    }


def test_buy_signal():
    """Klare Kaufbedingungen muessen BUY ergeben."""
    score = calculate_score(_make_data())
    assert score.action == "BUY"
    assert score.total >= 3


def test_bearish_no_buy():
    """Kurs unter MA200 darf keinen BUY ausloesen."""
    score = calculate_score(_make_data(price=480, ma200=490, ma50=485))
    assert score.action in ("HOLD", "SKIP", "REDUCE")


def test_extreme_greed_reduces_score():
    """Extreme Gier soll Score senken."""
    normal = calculate_score(_make_data(fg=38))
    greedy = calculate_score(_make_data(fg=85))
    assert greedy.total < normal.total


def test_high_vix_reduces_score():
    """Hoher VIX soll Score senken."""
    normal = calculate_score(_make_data(vix=15))
    fearful = calculate_score(_make_data(vix=35))
    assert fearful.total < normal.total


def test_inverted_yield_curve_reduces_score():
    """Invertierte Zinskurve soll Score senken."""
    normal  = calculate_score(_make_data(spread=0.5))
    inverted = calculate_score(_make_data(spread=-0.3))
    assert inverted.total < normal.total


def test_earnings_event_reduces_score():
    """Earnings-Event soll Score um 1 reduzieren."""
    no_event = calculate_score(_make_data(event=False))
    event    = calculate_score(_make_data(event=True))
    assert event.total == no_event.total - 1


def test_reduce_action():
    """Score <= -2 muss REDUCE ausloesen."""
    score = calculate_score(_make_data(
        price=440, ma200=490, ma50=460,  # -2
        fg=80, vix=35, spread=-0.5, event=True  # -1 -1 -1 -1 = -6 gesamt
    ))
    assert score.action == "REDUCE"
    assert score.total <= -2


def test_missing_data_graceful():
    """Fehlende Werte duerfen keinen Absturz ausloesen."""
    score = calculate_score({
        "symbol": "SPY",
        "ticker": {"price": None, "ma200": None, "ma50": None, "rsi": None},
        "fear_greed": None,
        "vix": None,
        "yield_spread": None,
        "earnings_event_today": False,
    })
    assert score.action in ("BUY", "HOLD", "SKIP", "REDUCE")
