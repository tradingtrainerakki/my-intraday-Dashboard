import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import requests

st.set_page_config(page_title="F&O Pro Scanner", layout="wide")

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
}

FALLBACK_WATCHLIST = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "SBIN", "AXISBANK", "KOTAKBANK", "LT", "WIPRO",
    "BAJFINANCE", "HINDUNILVR", "MARUTI", "TITAN", "SUNPHARMA",
    "ULTRACEMCO", "ONGC", "NTPC", "POWERGRID", "ADANIENT",
    "TATAMOTORS", "TATASTEEL", "JSWSTEEL", "HINDALCO", "COALINDIA",
    "BPCL", "IOC", "GAIL", "TECHM", "HCLTECH"
]

def get_nse_session():
    session = requests.Session()
    session.headers.update(NSE_HEADERS)
    try:
        session.get("https://www.nseindia.com", timeout=10)
    except:
        pass
    return session

def get_oi_gainers():
    try:
        session = get_nse_session()
        url = "https://www.nseindia.com/api/live-analysis-oi-spurts-underlyings"
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return [item['symbol'] for item in data[:30] if 'symbol' in item]
            elif isinstance(data, dict) and 'data' in data:
                return [item['symbol'] for item in data['data'][:30] if 'symbol' in item]
    except Exception as e:
        st.warning(f"NSE API se data nahi mila — Fallback list use ho rahi hai")
    return FALLBACK_WATCHLIST

def calculate_levels(cp, signal):
    if "BUY" in signal:
        return round(cp * 0.995, 2), round(cp * 1.01, 2)
    elif "SELL" in signal:
        return round(cp * 1.005, 2), round(cp * 0.99, 2)
    return "-", "-"

def get_pro_data(ticker):
    try:
        df = yf.download(ticker + ".NS", period="2d", interval="5m", progress=False)
        if len(df) < 20: return None
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        prev_close = df['Close'].shift(1).iloc[0]
        today_open = df['Open'].iloc[0]
        gap_pct = ((today_open - prev_close) / prev_close) * 100
        if abs(gap_pct) > 2.0: return None
        v, p = df['Volume'], (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (p * v).cumsum() / v.cumsum()
        df['EMA9'] = ta.ema(df['Close'], 9)
        df['EMA21'] = ta.ema(df['Close'], 21)
        last = df.iloc[-1]
        cp, vwap, ema9, ema21 = last['Close'], last['VWAP'], last['EMA9'], last['EMA21']
        vol_ratio = round(last['Volume'] / df['Volume'].mean(), 1)
        score = 20
        if cp > vwap: score += 30
        if ema9 > ema21: score += 30
        if vol_ratio > 1.2: score += 20
        signal = "🚀 STRONG BUY" if score >= 80 else "🔴 SELL" if score <= 30 else "🟡 WAIT"
        sl, tgt = calculate_levels(float(cp), signal)
        return {
            "STOCK": ticker,
            "LTP": round(float(cp), 2),
            "GAP %": f"{round(float(gap_pct), 2)}%",
            "SIGNAL": signal,
            "VWAP": "ABOVE" if cp > vwap else "BELOW",
            "STRENGTH": f"{score}%",
            "STOP LOSS": sl,
            "TARGET": tgt
        }
    except:
        return None

st.title("🔥 F&O Live Scanner")
st.caption("NSE Live OI Gainers | VWAP + EMA + Volume Analysis")

if st.button('🔍 Scan Market'):
    with st.spinner("NSE se OI Gainers fetch ho rahe hain..."):
        watchlist = get_oi_gainers()
    st.info(f"📋 {len(watchlist)} stocks scan ho rahe hain...")

    results = []
    progress = st.progress(0)
    status = st.empty()
    for i, ticker in enumerate(watchlist):
        status.text(f"Scanning: {ticker}")
        data = get_pro_data(ticker)
        if data:
            results.append(data)
        progress.progress((i + 1) / len(watchlist))
    status.empty()

    if results:
        df_result = pd.DataFrame(results)
        st.success(f"✅ {len(df_result)} stocks found!")
        st.dataframe(df_result, use_container_width=True)
    else:
        st.warning("⚠️ No Stocks Found! Market may be closed.")
