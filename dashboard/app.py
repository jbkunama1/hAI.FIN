"""hAI.FIN – Streamlit Dashboard"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st
import pandas as pd

# Projekt-Root ins sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_fetcher import fetch_all
from src.signals import calculate_score
from src.portfolio import Portfolio

# ── Seitenkonfiguration ────────────────────────────────────────────────
st.set_page_config(
    page_title="hAI.FIN Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
.signal-buy    { background:#d4edda; border-left:4px solid #28a745; padding:12px; border-radius:6px; }
.signal-hold   { background:#fff3cd; border-left:4px solid #ffc107; padding:12px; border-radius:6px; }
.signal-skip   { background:#f8d7da; border-left:4px solid #dc3545; padding:12px; border-radius:6px; }
.signal-reduce { background:#f8d7da; border-left:4px solid #dc3545; padding:12px; border-radius:6px; }
.signal-emergency { background:#dc3545; color:white; padding:12px; border-radius:6px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://raw.githubusercontent.com/jbkunama1/hAI.FIN/main/docs/logo.svg",
             use_container_width=True, caption="hAI.FIN")
    st.title("hAI.FIN")
    st.caption("Autonomer ETF-Handelsagent")
    st.divider()

    assets = st.multiselect(
        "Assets analysieren",
        ["SPY", "QQQ", "VTI", "VWCE", "VUSA"],
        default=["SPY", "QQQ", "VTI"],
    )
    initial_cash = st.number_input("Portfolio-Wert (USD)", value=10_000, step=500)
    auto_refresh = st.toggle("Auto-Refresh (60s)", value=False)
    st.divider()
    st.caption(f"Stand: {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    if st.button("🔄 Jetzt aktualisieren", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Daten laden (gecacht, 60s TTL) ────────────────────────────────────
@st.cache_data(ttl=60)
def load_market_data(symbol: str) -> dict:
    return fetch_all(symbol=symbol, finnhub_key=os.getenv("FINNHUB_KEY"))

@st.cache_data(ttl=60)
def load_signal(symbol: str) -> dict:
    md = load_market_data(symbol)
    s  = calculate_score(md)
    return {"signal": s, "market": md}

# ── Hilfsfunktionen ───────────────────────────────────────────────────
def score_color(score: int) -> str:
    if score >= 3:  return "normal"
    if score >= 1:  return "off"
    return "inverse"

def action_badge(action: str) -> str:
    icons = {"BUY": "🟢", "HOLD": "🟡", "SKIP": "🔴", "REDUCE": "🔴", "EMERGENCY": "🚨"}
    return f"{icons.get(action, '⚪')} {action}"

def fg_label(score: float) -> str:
    if score < 25:   return "😱 Extreme Angst"
    if score < 45:   return "😟 Angst"
    if score < 56:   return "😐 Neutral"
    if score < 75:   return "😏 Gier"
    return "🤑 Extreme Gier"

def fg_color(score: float) -> str:
    if score < 25:   return "inverse"
    if score < 45:   return "off"
    if score < 56:   return "normal"
    return "inverse"

# ── Haupttitel ────────────────────────────────────────────────────────
st.title("📈 hAI.FIN – Live Dashboard")
st.caption("Composite Signal Score · Portfolio-Simulation · Trade-Log")
st.divider()

# ── Globale Markt-Indikatoren (erste Zeile) ───────────────────────────
st.subheader("🌍 Markt-Überblick")
spy_data = load_market_data("SPY")

col1, col2, col3, col4 = st.columns(4)
with col1:
    fg = spy_data.get("fear_greed")
    st.metric("Fear & Greed",
              f"{fg:.0f}" if fg else "n/a",
              fg_label(fg) if fg else "",
              delta_color=fg_color(fg) if fg else "normal")
with col2:
    vix = spy_data.get("vix")
    st.metric("VIX", f"{vix:.1f}" if vix else "n/a",
              "⚠️ Hoch" if (vix and vix > 30) else "Normal",
              delta_color="inverse" if (vix and vix > 30) else "normal")
with col3:
    spread = spy_data.get("yield_spread")
    st.metric("10Y-2Y Spread",
              f"{spread:+.2f}%" if spread is not None else "n/a",
              "🔴 Invertiert" if (spread is not None and spread < 0) else "Normal",
              delta_color="inverse" if (spread is not None and spread < 0) else "normal")
with col4:
    t = spy_data.get("ticker", {})
    spy_price = t.get("price")
    spy_ma200 = t.get("ma200")
    trend = "📈 Bullish" if (spy_price and spy_ma200 and spy_price > spy_ma200) else "📉 Bearish"
    st.metric("SPY Trend", trend,
              f"MA200: {spy_ma200:.0f}" if spy_ma200 else "")

st.divider()

# ── Asset-Signale (eine Karte pro Asset) ──────────────────────────────
st.subheader("🎯 Signal-Analyse")

for asset in assets:
    with st.spinner(f"Lade {asset}…"):
        data = load_signal(asset)
    signal  = data["signal"]
    market  = data["market"]
    ticker  = market.get("ticker", {})
    action  = signal.action
    css_cls = f"signal-{action.lower()}"

    with st.expander(f"{action_badge(action)}  **{asset}**  |  Score: {signal.total}  |  {signal.reason}",
                     expanded=(action == "BUY")):
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Kurs",   f"${ticker.get('price', 'n/a'):.2f}" if ticker.get('price') else "n/a")
        c2.metric("MA200",  f"${ticker.get('ma200', 'n/a'):.2f}" if ticker.get('ma200') else "n/a")
        c3.metric("MA50",   f"${ticker.get('ma50',  'n/a'):.2f}" if ticker.get('ma50')  else "n/a")
        c4.metric("RSI(14)", f"{ticker.get('rsi', 'n/a'):.1f}"  if ticker.get('rsi')   else "n/a")
        c5.metric("Score",  signal.total,
                  delta_color=score_color(signal.total))

        # Score-Komponenten als Tabelle
        rows = []
        for name, comp in signal.components.items():
            val = comp["value"]
            rows.append({
                "Indikator": name,
                "Punkte":    f"{'+' if val > 0 else ''}{val}",
                "Detail":    comp["detail"],
            })
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

# ── Portfolio-Simulation ───────────────────────────────────────────────
st.subheader("💼 Portfolio-Simulation")

if "portfolio" not in st.session_state:
    st.session_state.portfolio = Portfolio(
        initial_cash=initial_cash,
        max_position_pct=0.10,
        min_cash_reserve_pct=0.20,
        max_trades_per_day=3,
    )
    st.session_state.trade_history = []

portfolio = st.session_state.portfolio
state     = portfolio.state()

p1, p2, p3, p4 = st.columns(4)
p1.metric("Gesamt-Wert",   f"${state['total_usd']:,.0f}")
p2.metric("Cash",          f"${state['cash_usd']:,.0f}",  f"{state['cash_pct']:.1f}%")
p3.metric("Positionen",    len(state["positions"]))
p4.metric("Trades heute",  state["trades_today"],
          delta_color="inverse" if state["trades_today"] >= 3 else "normal")

if state["positions"]:
    pos_df = pd.DataFrame([
        {"Asset": k, "Wert (USD)": f"${v:,.2f}",
         "Anteil": f"{v/state['total_usd']*100:.1f}%"}
        for k, v in state["positions"].items()
    ])
    st.dataframe(pos_df, use_container_width=True, hide_index=True)
else:
    st.info("Noch keine offenen Positionen.")

# Manuelle Trade-Ausführung (DRY_RUN)
st.caption("Manueller Trade (DRY_RUN)")
tcol1, tcol2, tcol3 = st.columns([2, 2, 1])
with tcol1:
    trade_asset  = st.selectbox("Asset", assets, key="trade_asset")
with tcol2:
    trade_amount = st.number_input("Betrag (USD)", min_value=10.0,
                                   max_value=float(state["cash_usd"]),
                                   value=min(500.0, float(state["cash_usd"])),
                                   step=50.0, key="trade_amount")
with tcol3:
    st.write("")
    if st.button("📥 Kaufen (DRY)", use_container_width=True):
        ok, reason = portfolio.check_guardrails(trade_asset, trade_amount, assets)
        if ok:
            res = portfolio.execute_buy(trade_asset, trade_amount, dry_run=True)
            st.session_state.trade_history.append({
                "Zeit": datetime.now(timezone.utc).strftime("%H:%M"),
                "Aktion": "BUY", "Asset": trade_asset,
                "Betrag": f"${trade_amount:.0f}",
            })
            st.success(f"✅ DRY_RUN BUY {trade_asset} {trade_amount:.0f} USD simuliert")
            st.rerun()
        else:
            st.error(f"❌ Guardrail: {reason}")

st.divider()

# ── Trade-Log ─────────────────────────────────────────────────────────
st.subheader("📋 Trade-Log (Session)")

log_path = Path("logs")
if log_path.exists():
    log_files = sorted(log_path.glob("haifin_*.log"), reverse=True)
    if log_files:
        log_entries = []
        with open(log_files[0], encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("logger") == "haifin.trade":
                        inner = json.loads(entry["msg"])
                        log_entries.append({
                            "Zeit":    inner.get("ts", "")[:19].replace("T", " "),
                            "Aktion":  inner.get("action", ""),
                            "Asset":   inner.get("symbol", ""),
                            "Betrag":  f"${inner.get('amount_usd', 0):.0f}",
                            "Score":   inner.get("score", {}).get("total", ""),
                            "DRY_RUN": "✓" if inner.get("dry_run") else "LIVE",
                        })
                except Exception:
                    pass
        if log_entries:
            df_log = pd.DataFrame(log_entries)
            st.dataframe(df_log, use_container_width=True, hide_index=True)
        else:
            st.info("Noch keine Trade-Logs in den Dateien.")
    else:
        st.info("Keine Log-Dateien gefunden.")
elif st.session_state.trade_history:
    st.dataframe(pd.DataFrame(st.session_state.trade_history),
                 use_container_width=True, hide_index=True)
else:
    st.info("Noch keine Trades in dieser Session.")

# ── Auto-Refresh ──────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(60)
    st.cache_data.clear()
    st.rerun()
