import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="F&O Pro Scanner", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stButton>button {
        background: linear-gradient(90deg, #f7971e, #ffd200);
        color: black; font-weight: bold; font-size: 16px;
        border-radius: 12px; padding: 10px 30px; border: none;
        box-shadow: 0 4px 15px rgba(247,151,30,0.4);
    }
    .stButton>button:hover { transform: scale(1.05); }
    .title-text {
        font-size: 2.5rem; font-weight: 800;
        background: linear-gradient(90deg, #f7971e, #ffd200, #ff6b6b);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .journal-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px; padding: 20px;
        border: 1px solid #f7971e55; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/", "Connection": "keep-alive",
}

FALLBACK_WATCHLIST = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "SBIN", "AXISBANK", "KOTAKBANK", "LT", "WIPRO",
    "BAJFINANCE", "HINDUNILVR", "MARUTI", "TITAN", "SUNPHARMA",
    "ULTRACEMCO", "ONGC", "NTPC", "POWERGRID", "ADANIENT",
    "TATAMOTORS", "TATASTEEL", "JSWSTEEL", "HINDALCO", "COALINDIA",
    "BPCL", "IOC", "GAIL", "TECHM", "HCLTECH"
]

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:
        return False, "Weekend — Market Band Hai 🏖️"
    if now.hour < 9 or (now.hour == 9 and now.minute < 15):
        return False, "Market abhi khula nahi (9:15 AM se)"
    if now.hour > 15 or (now.hour == 15 and now.minute > 30):
        return False, "Market band ho gaya (3:30 PM ke baad)"
    return True, "Market Open Hai ✅"

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
    except:
        pass
    return FALLBACK_WATCHLIST

def calculate_levels(cp, signal):
    if "BUY" in signal:
        return round(cp * 0.995, 2), round(cp * 1.01, 2)
    elif "SELL" in signal:
        return round(cp * 1.005, 2), round(cp * 0.99, 2)
    return "-", "-"

def get_pro_data(ticker):
    try:
        df = yf.download(ticker + ".NS", period="5d", interval="5m", progress=False)
        if len(df) < 20:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()

        today = pd.Timestamp.now().date()
        today_data = df[df.index.date == today]
        prev_data = df[df.index.date < today]

        if len(today_data) < 2:
            all_dates = sorted(df.index.date.unique())
            if len(all_dates) < 2:
                return None
            today_data = df[df.index.date == all_dates[-1]]
            prev_data = df[df.index.date == all_dates[-2]]

        if len(prev_data) == 0 or len(today_data) == 0:
            return None

        prev_close = float(prev_data['Close'].iloc[-1])
        today_open = float(today_data['Open'].iloc[0])
        gap_pct = round(((today_open - prev_close) / prev_close) * 100, 2)

        if abs(gap_pct) > 2.0:
            return None

        v = today_data['Volume']
        p = (today_data['High'] + today_data['Low'] + today_data['Close']) / 3
        vwap = float((p * v).cumsum().iloc[-1] / v.cumsum().iloc[-1])

        ema9 = float(ema(df['Close'], 9).iloc[-1])
        ema21 = float(ema(df['Close'], 21).iloc[-1])
        cp = float(today_data['Close'].iloc[-1])
        vol_ratio = round(float(today_data['Volume'].iloc[-1]) / float(today_data['Volume'].mean()), 1)

        score = 20
        if cp > vwap: score += 30
        if ema9 > ema21: score += 30
        if vol_ratio > 1.2: score += 20

        signal = "🚀 STRONG BUY" if score >= 80 else "🔴 SELL" if score <= 30 else "🟡 WAIT"
        sl, tgt = calculate_levels(cp, signal)

        return {
            "STOCK": ticker,
            "LTP": round(cp, 2),
            "GAP %": f"{gap_pct}%",
            "SIGNAL": signal,
            "VWAP": "⬆️ ABOVE" if cp > vwap else "⬇️ BELOW",
            "EMA9": round(ema9, 2),
            "EMA21": round(ema21, 2),
            "EMA TREND": "📈 BULLISH" if ema9 > ema21 else "📉 BEARISH",
            "VOL RATIO": vol_ratio,
            "STRENGTH": f"{score}%",
            "STOP LOSS": sl,
            "TARGET": tgt
        }
    except:
        return None

# ---- Candlestick Chart ----
def get_candle_data(ticker, interval, period):
    try:
        df = yf.download(ticker + ".NS", period=period, interval=interval, progress=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        df['EMA9'] = ema(df['Close'], 9)
        df['EMA21'] = ema(df['Close'], 21)
        v = df['Volume']
        p = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (p * v).cumsum() / v.cumsum()
        return df
    except:
        return None

def plot_candles(df, ticker, interval_label):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03,
                        row_heights=[0.75, 0.25])

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name="Price",
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4444'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['EMA9'],
        line=dict(color='#ffd200', width=1.5), name='EMA9'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA21'],
        line=dict(color='#ff6b6b', width=1.5), name='EMA21'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'],
        line=dict(color='#00bfff', width=1.5, dash='dash'), name='VWAP'), row=1, col=1)

    colors = ['#00ff88' if float(df['Close'].iloc[i]) >= float(df['Open'].iloc[i])
              else '#ff4444' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'],
        marker_color=colors, name='Volume', opacity=0.7), row=2, col=1)

    fig.update_layout(
        title=f"📊 {ticker} — {interval_label}",
        template="plotly_dark",
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        xaxis_rangeslider_visible=False,
        height=550,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    fig.update_xaxes(showgrid=True, gridcolor='#1e1e2e')
    fig.update_yaxes(showgrid=True, gridcolor='#1e1e2e')
    return fig

def color_signal(val):
    if "STRONG BUY" in str(val): return 'background-color: #004d00; color: #00ff00; font-weight: bold'
    if "SELL" in str(val): return 'background-color: #4d0000; color: #ff4444; font-weight: bold'
    if "WAIT" in str(val): return 'background-color: #4d4d00; color: #ffff00; font-weight: bold'
    return ''

def color_strength(val):
    try:
        v = int(str(val).replace('%',''))
        if v >= 80: return 'color: #00ff00; font-weight: bold'
        if v <= 40: return 'color: #ff4444'
        return 'color: #ffff00'
    except: return ''

def color_ema_trend(val):
    if "BULLISH" in str(val): return 'color: #00ff00; font-weight: bold'
    if "BEARISH" in str(val): return 'color: #ff4444; font-weight: bold'
    return ''

# ======== JOURNAL FUNCTIONS ========
JOURNAL_FILE = "journal.json"

def load_journal():
    try:
        with open(JOURNAL_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_journal(entries):
    with open(JOURNAL_FILE, "w") as f:
        json.dump(entries, f, indent=2)

# ======== MAIN UI ========
st.markdown('<p class="title-text">🔥 F&O Pro Live Scanner</p>', unsafe_allow_html=True)

open_status, msg = is_market_open()
col1, col2, col3 = st.columns(3)
col1.metric("Market Status", msg)
col2.metric("Data Source", "NSE Live OI Gainers")
col3.metric("Indicators", "VWAP + EMA9/21 + Volume")
st.markdown("---")

if not open_status:
    st.warning(f"⚠️ {msg} — Last trading day ka data dikhayega scanner")

# ======== TABS ========
tab1, tab2, tab3 = st.tabs(["📡 Live Scanner", "📊 Candlestick Chart", "📓 Entry Journal"])

# -------- TAB 1: SCANNER --------
with tab1:
    if st.button('🔍 Scan Market'):
        with st.spinner("NSE se OI Gainers fetch ho rahe hain..."):
            watchlist = get_oi_gainers()
        st.info(f"📋 {len(watchlist)} stocks scan ho rahe hain...")

        results = []
        progress = st.progress(0)
        status_txt = st.empty()

        for i, ticker in enumerate(watchlist):
            status_txt.text(f"⏳ Scanning: {ticker} ({i+1}/{len(watchlist)})")
            data = get_pro_data(ticker)
            if data:
                results.append(data)
            progress.progress((i + 1) / len(watchlist))

        status_txt.empty()

        if results:
            df_result = pd.DataFrame(results)
            st.session_state['scan_results'] = results

            buy_count = len(df_result[df_result['SIGNAL'].str.contains('BUY')])
            sell_count = len(df_result[df_result['SIGNAL'].str.contains('SELL')])
            wait_count = len(df_result[df_result['SIGNAL'].str.contains('WAIT')])

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("✅ Total Found", len(df_result))
            c2.metric("🚀 Strong Buy", buy_count)
            c3.metric("🔴 Sell", sell_count)
            c4.metric("🟡 Wait", wait_count)

            styled = df_result.style\
                .applymap(color_signal, subset=['SIGNAL'])\
                .applymap(color_strength, subset=['STRENGTH'])\
                .applymap(color_ema_trend, subset=['EMA TREND'])

            st.dataframe(styled, use_container_width=True, height=500)
        else:
            st.warning("⚠️ No Stocks Found!")

# -------- TAB 2: CANDLESTICK --------
with tab2:
    st.subheader("📊 Candlestick Chart with EMA & VWAP")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        chart_ticker = st.text_input("Stock Symbol daalo (e.g. RELIANCE, SBIN)", value="RELIANCE").upper()
    with col_b:
        timeframe = st.selectbox("Timeframe", ["5 Min", "15 Min", "1 Hour"])

    interval_map = {
        "5 Min":  ("5m",  "5d"),
        "15 Min": ("15m", "5d"),
        "1 Hour": ("1h",  "30d"),
    }

    if st.button("📈 Load Chart"):
        interval, period = interval_map[timeframe]
        with st.spinner(f"Loading {chart_ticker} {timeframe} chart..."):
            df_chart = get_candle_data(chart_ticker, interval, period)

        if df_chart is not None and len(df_chart) > 5:
            fig = plot_candles(df_chart, chart_ticker, timeframe)
            st.plotly_chart(fig, use_container_width=True)

            last = df_chart.iloc[-1]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("LTP", round(float(last['Close']), 2))
            m2.metric("VWAP", round(float(last['VWAP']), 2))
            m3.metric("EMA9", round(float(last['EMA9']), 2))
            m4.metric("EMA21", round(float(last['EMA21']), 2))
        else:
            st.error("Data nahi mila — symbol check karo ya market band hai")

# -------- TAB 3: JOURNAL --------
with tab3:
    st.subheader("📓 Entry Journal — Apni Trades Track Karo")

    with st.expander("➕ Nayi Entry Add Karo", expanded=True):
        j1, j2, j3 = st.columns(3)
        j_date = j1.date_input("Date", datetime.now())
        j_stock = j2.text_input("Stock", placeholder="e.g. RELIANCE")
        j_type = j3.selectbox("Trade Type", ["BUY", "SELL"])

        j4, j5, j6 = st.columns(3)
        j_entry = j4.number_input("Entry Price", min_value=0.0, format="%.2f")
        j_sl = j5.number_input("Stop Loss", min_value=0.0, format="%.2f")
        j_target = j6.number_input("Target", min_value=0.0, format="%.2f")

        j7, j8 = st.columns(2)
        j_qty = j7.number_input("Quantity", min_value=1, value=1)
        j_status = j8.selectbox("Status", ["OPEN", "HIT TARGET", "HIT SL", "EXITED"])

        j_notes = st.text_area("Notes / Reason", placeholder="Trade lene ka reason kya tha?")

        if st.button("💾 Entry Save Karo"):
            if j_stock:
                entries = load_journal()
                pnl = 0
                if j_status != "OPEN":
                    if j_type == "BUY":
                        exit_price = j_target if j_status == "HIT TARGET" else j_sl if j_status == "HIT SL" else j_entry
                    else:
                        exit_price = j_sl if j_status == "HIT TARGET" else j_target if j_status == "HIT SL" else j_entry
                    pnl = round((exit_price - j_entry) * j_qty if j_type == "BUY" else (j_entry - exit_price) * j_qty, 2)

                new_entry = {
                    "date": str(j_date),
                    "stock": j_stock.upper(),
                    "type": j_type,
                    "entry": j_entry,
                    "sl": j_sl,
                    "target": j_target,
                    "qty": j_qty,
                    "status": j_status,
                    "pnl": pnl,
                    "notes": j_notes
                }
                entries.append(new_entry)
                save_journal(entries)
                st.success(f"✅ {j_stock.upper()} entry save ho gayi!")
            else:
                st.error("Stock ka naam daalo!")

    st.markdown("---")
    st.subheader("📋 Meri Trades")

    entries = load_journal()
    if entries:
        df_journal = pd.DataFrame(entries)

        total_pnl = df_journal['pnl'].sum()
        wins = len(df_journal[df_journal['pnl'] > 0])
        losses = len(df_journal[df_journal['pnl'] < 0])
        open_trades = len(df_journal[df_journal['status'] == 'OPEN'])

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("💰 Total P&L", f"₹{round(total_pnl, 2)}", delta=f"₹{round(total_pnl,2)}")
        p2.metric("✅ Winning Trades", wins)
        p3.metric("❌ Losing Trades", losses)
        p4.metric("🔓 Open Trades", open_trades)

        def color_pnl(val):
            try:
                if float(val) > 0: return 'color: #00ff00; font-weight: bold'
                if float(val) < 0: return 'color: #ff4444; font-weight: bold'
            except: pass
            return ''

        def color_status(val):
            if val == "HIT TARGET": return 'color: #00ff00; font-weight: bold'
            if val == "HIT SL": return 'color: #ff4444; font-weight: bold'
            if val == "OPEN": return 'color: #ffd200; font-weight: bold'
            return ''

        styled_j = df_journal.style\
            .applymap(color_pnl, subset=['pnl'])\
            .applymap(color_status, subset=['status'])

        st.dataframe(styled_j, use_container_width=True, height=400)

        if st.button("🗑️ Saari Entries Delete Karo"):
            save_journal([])
            st.success("Journal clear ho gaya!")
            st.rerun()
    else:
        st.info("Abhi koi entry nahi hai — upar se add karo!")
