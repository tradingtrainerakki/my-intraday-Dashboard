%%writefile app.py
import streamlit as st
import pandas as pd
from nsepython import *
import yfinance as yf
import pandas_ta as ta

st.set_page_config(page_title="F&O Pro Scanner", layout="wide")

def calculate_levels(cp, signal):
    if "BUY" in signal:
        sl, t1 = round(cp * 0.995, 2), round(cp * 1.01, 2)
    elif "SELL" in signal:
        sl, t1 = round(cp * 1.005, 2), round(cp * 0.99, 2)
    else: sl, t1 = "-", "-"
    return sl, t1

def get_pro_data(ticker):
    try:
        df = yf.download(ticker + ".NS", period="2d", interval="5m", progress=False)
        if len(df) < 20: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        prev_close, today_open = df['Close'].shift(1).iloc[0], df['Open'].iloc[0]
        gap_pct = ((today_open - prev_close) / prev_close) * 100
        if abs(gap_pct) > 2.0: return None
        v, p = df['Volume'], (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (p * v).cumsum() / v.cumsum()
        df['EMA9'], df['EMA21'] = ta.ema(df['Close'], 9), ta.ema(df['Close'], 21)
        last = df.iloc[-1]
        cp, vwap, ema9, ema21 = last['Close'], last['VWAP'], last['EMA9'], last['EMA21']
        vol_ratio = round(last['Volume'] / df['Volume'].mean(), 1)
        score = 0
        if cp > vwap: score += 30
        if ema9 > ema21: score += 30
        if vol_ratio > 1.2: score += 20
        score += 20
        signal = "🚀 STRONG BUY" if score >= 80 else "🔴 SELL" if score <= 30 else "🟡 WAIT"
        sl, tgt = calculate_levels(cp, signal)
        return {"STOCK": ticker, "LTP": round(cp, 2), "GAP %": f"{round(gap_pct, 2)}%",
                "SIGNAL": signal, "VWAP": "ABOVE" if cp > vwap else "BELOW",
                "STRENGTH": f"{score}%", "STOP LOSS": sl, "TARGET": tgt}
    except: return None

st.title("🔥 F&O Live Scanner")
if st.button('Scan Market'):
    try:
        watchlist = nse_oi_gainers()['symbol'].head(30).tolist()
    except:
        watchlist = ["RELIANCE", "TCS", "HDFCBANK", "SBIN", "INFY"]
    results = [get_pro_data(t) for t in watchlist if get_pro_data(t) is not None]
    if results: st.table(pd.DataFrame(results).head(10))
    else: st.warning("No Stocks Found!")
