import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="F&O Pro Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# USERS
# ============================================================
USERS = {
    "akki":  "Ca@1809",
    "user1": "pass123",
    "user2": "pass456",
    "user3": "pass789",
}

# ============================================================
# GLOBAL CSS — Dark Premium Theme
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: #080c12 !important;
    color: #c8d8e8 !important;
}
.main { background-color: #080c12 !important; }
section[data-testid="stSidebar"] { background-color: #0d1219 !important; }

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Top Header Bar ── */
.top-header {
    background: linear-gradient(135deg, #0d1a26, #091520);
    border-bottom: 1px solid #1e2d3d;
    padding: 18px 28px;
    border-radius: 0 0 12px 12px;
    margin-bottom: 20px;
}
.logo-text {
    font-family: 'Syne', sans-serif !important;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00d4ff, #00ff88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 3px;
}
.logo-sub {
    font-size: 10px;
    color: #3a5a7a;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-top: -4px;
}

/* ── Metric Cards ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1a26, #111820) !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 10px !important;
    padding: 16px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
}
[data-testid="metric-container"]:hover {
    border-color: #00d4ff55 !important;
    transform: translateY(-2px);
    transition: all 0.2s;
}
[data-testid="stMetricLabel"] {
    font-size: 10px !important;
    letter-spacing: 2px !important;
    color: #6a8aaa !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #00d4ff !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(90deg, #00d4ff22, #00ff8822) !important;
    color: #00d4ff !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    border-radius: 8px !important;
    padding: 10px 28px !important;
    border: 1px solid #00d4ff44 !important;
    letter-spacing: 1px !important;
    transition: all 0.2s !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #00d4ff, #00ff88) !important;
    color: #000 !important;
    border-color: transparent !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0,212,255,0.3) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1219 !important;
    border-bottom: 1px solid #1e2d3d !important;
    gap: 4px !important;
    padding: 0 8px !important;
    border-radius: 8px 8px 0 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6a8aaa !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 10px 20px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00d4ff15, #00ff8815) !important;
    color: #00d4ff !important;
    border-bottom: 2px solid #00d4ff !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background-color: #0d1219 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 8px !important;
    color: #c8d8e8 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 0 1px #00d4ff44 !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border: 1px solid #1e2d3d !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrameResizable"] {
    background: #0d1219 !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #00d4ff, #00ff88) !important;
    border-radius: 4px !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #00d4ff !important; }

/* ── Alerts ── */
.stSuccess {
    background: #00ff8815 !important;
    border: 1px solid #00ff8840 !important;
    border-radius: 8px !important;
    color: #00ff88 !important;
}
.stWarning {
    background: #ffc70015 !important;
    border: 1px solid #ffc70040 !important;
    border-radius: 8px !important;
}
.stError {
    background: #ff406015 !important;
    border: 1px solid #ff406040 !important;
    border-radius: 8px !important;
}
.stInfo {
    background: #00d4ff15 !important;
    border: 1px solid #00d4ff40 !important;
    border-radius: 8px !important;
}

/* ── Divider ── */
hr { border-color: #1e2d3d !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #0d1219 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 8px !important;
    color: #c8d8e8 !important;
    font-size: 12px !important;
}

/* ── Stat badge ── */
.stat-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}
.badge-buy   { background:#00ff8820; border:1px solid #00ff8840; color:#00ff88; }
.badge-sell  { background:#ff406020; border:1px solid #ff406040; color:#ff4060; }
.badge-wait  { background:#ffc70020; border:1px solid #ffc70040; color:#ffc700; }
.badge-open  { background:#00d4ff20; border:1px solid #00d4ff40; color:#00d4ff; }

/* ── Section header ── */
.section-header {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.1rem;
    font-weight: 700;
    color: #00d4ff;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-left: 3px solid #00d4ff;
    padding-left: 10px;
    margin: 16px 0 12px 0;
}

/* ── Login box ── */
.login-container {
    max-width: 400px;
    margin: 80px auto;
    background: linear-gradient(135deg, #0d1a26, #111820);
    border: 1px solid #1e2d3d;
    border-radius: 16px;
    padding: 40px;
    text-align: center;
}
.login-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00d4ff, #00ff88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

/* ── Journal card ── */
.journal-card {
    background: linear-gradient(135deg, #0d1a26, #111820);
    border: 1px solid #1e2d3d;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 8px;
}
.journal-card:hover { border-color: #00d4ff44; }

/* ── Selectbox label ── */
label {
    color: #6a8aaa !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# LOGIN
# ============================================================
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("""
        <div class="login-container">
            <div class="login-title">📈 F&O PRO SCANNER</div>
            <div style="color:#3a5a7a; font-size:10px; letter-spacing:3px; margin-bottom:24px;">NSE · INTRADAY · LIVE</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div style="background:#0d1219;border:1px solid #1e2d3d;border-radius:12px;padding:28px;">', unsafe_allow_html=True)
            username = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")
            if st.button("🚀 Login", use_container_width=True):
                if username in USERS and USERS[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Wrong Username or Password!")
            st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

check_password()


# ============================================================
# HELPERS
# ============================================================
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/", "Connection": "keep-alive",
}

FALLBACK_WATCHLIST = [
    "RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","SBIN","AXISBANK","KOTAKBANK",
    "LT","WIPRO","BAJFINANCE","HINDUNILVR","MARUTI","TITAN","SUNPHARMA",
    "ULTRACEMCO","ONGC","NTPC","POWERGRID","ADANIENT","TATAMOTORS","TATASTEEL",
    "JSWSTEEL","HINDALCO","COALINDIA","BPCL","IOC","GAIL","TECHM","HCLTECH"
]

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:
        return False, "Weekend — Market Band Hai 🏖️"
    if now.hour < 9 or (now.hour == 9 and now.minute < 15):
        return False, f"Market Opens at 9:15 AM"
    if now.hour > 15 or (now.hour == 15 and now.minute > 30):
        return False, "Market Closed (3:30 PM)"
    return True, "Market Open ✅"

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
            if isinstance(data, list):
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
        prev_data  = df[df.index.date < today]

        if len(today_data) < 2:
            all_dates = sorted(df.index.date.unique())
            if len(all_dates) < 2:
                return None
            today_data = df[df.index.date == all_dates[-1]]
            prev_data  = df[df.index.date == all_dates[-2]]

        if len(prev_data) == 0 or len(today_data) == 0:
            return None

        prev_close = float(prev_data['Close'].iloc[-1])
        today_open = float(today_data['Open'].iloc[0])
        gap_pct    = round(((today_open - prev_close) / prev_close) * 100, 2)

        if abs(gap_pct) > 2.0:
            return None

        v    = today_data['Volume']
        p    = (today_data['High'] + today_data['Low'] + today_data['Close']) / 3
        vwap = float((p * v).cumsum().iloc[-1] / v.cumsum().iloc[-1])

        ema9  = float(ema(df['Close'], 9).iloc[-1])
        ema21 = float(ema(df['Close'], 21).iloc[-1])
        cp    = float(today_data['Close'].iloc[-1])
        chg   = round(((cp - prev_close) / prev_close) * 100, 2)

        vol_ratio = round(
            float(today_data['Volume'].iloc[-1]) / float(today_data['Volume'].mean()), 1
        )

        score = 20
        if cp > vwap:   score += 30
        if ema9 > ema21: score += 30
        if vol_ratio > 1.2: score += 20

        if score >= 80:
            signal = "🚀 STRONG BUY"
        elif score <= 30:
            signal = "🔴 SELL"
        else:
            signal = "🟡 WAIT"

        sl, tgt = calculate_levels(cp, signal)

        return {
            "STOCK":     ticker,
            "LTP":       round(cp, 2),
            "CHG %":     f"{'+' if chg >= 0 else ''}{chg}%",
            "SIGNAL":    signal,
            "VWAP":      "⬆ ABOVE" if cp > vwap else "⬇ BELOW",
            "EMA TREND": "📈 BULLISH" if ema9 > ema21 else "📉 BEARISH",
            "VOL RATIO": f"{vol_ratio}x",
            "STRENGTH":  f"{score}%",
            "STOP LOSS": sl,
            "TARGET":    tgt,
        }
    except:
        return None


# ============================================================
# CHART
# ============================================================
def get_candle_data(ticker, interval, period):
    try:
        df = yf.download(ticker + ".NS", period=period, interval=interval, progress=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        df['EMA9']  = ema(df['Close'], 9)
        df['EMA21'] = ema(df['Close'], 21)
        v = df['Volume']
        p = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (p * v).cumsum() / v.cumsum()
        return df
    except:
        return None

def plot_candles(df, ticker, interval_label):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.02, row_heights=[0.75, 0.25])

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name="Price",
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4060',
        increasing_fillcolor='#00ff8855',
        decreasing_fillcolor='#ff406055',
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['EMA9'],
        line=dict(color='#ffc700', width=1.5), name='EMA 9'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA21'],
        line=dict(color='#ff6b6b', width=1.5), name='EMA 21'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'],
        line=dict(color='#00d4ff', width=1.5, dash='dot'), name='VWAP'), row=1, col=1)

    colors = ['#00ff88' if float(df['Close'].iloc[i]) >= float(df['Open'].iloc[i])
              else '#ff4060' for i in range(len(df))]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'],
        marker_color=colors, name='Volume', opacity=0.6
    ), row=2, col=1)

    fig.update_layout(
        title=dict(
            text=f"<b>{ticker}</b> — {interval_label}",
            font=dict(size=16, color='#c8d8e8')
        ),
        template="plotly_dark",
        paper_bgcolor='#080c12',
        plot_bgcolor='#0d1219',
        xaxis_rangeslider_visible=False,
        height=580,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            font=dict(size=11), bgcolor='rgba(0,0,0,0)'
        ),
        margin=dict(l=10, r=10, t=60, b=10),
        font=dict(family='JetBrains Mono')
    )
    fig.update_xaxes(showgrid=True, gridcolor='#1e2d3d', zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='#1e2d3d', zeroline=False)
    return fig


# ============================================================
# STYLE FUNCTIONS
# ============================================================
def color_signal(val):
    v = str(val)
    if "STRONG BUY" in v: return 'background:#00ff8820;color:#00ff88;font-weight:700;border-radius:4px;'
    if "SELL"       in v: return 'background:#ff406020;color:#ff4060;font-weight:700;border-radius:4px;'
    if "WAIT"       in v: return 'background:#ffc70020;color:#ffc700;font-weight:700;border-radius:4px;'
    return ''

def color_strength(val):
    try:
        v = int(str(val).replace('%',''))
        if v >= 80: return 'color:#00ff88;font-weight:700'
        if v <= 40: return 'color:#ff4060'
        return 'color:#ffc700'
    except: return ''

def color_ema(val):
    if "BULLISH" in str(val): return 'color:#00ff88;font-weight:700'
    if "BEARISH" in str(val): return 'color:#ff4060;font-weight:700'
    return ''

def color_vwap(val):
    if "ABOVE" in str(val): return 'color:#00ff88'
    if "BELOW" in str(val): return 'color:#ff4060'
    return ''

def color_chg(val):
    try:
        v = float(str(val).replace('%','').replace('+',''))
        if v > 0: return 'color:#00ff88;font-weight:700'
        if v < 0: return 'color:#ff4060;font-weight:700'
    except: pass
    return ''

def color_pnl(val):
    try:
        if float(val) > 0: return 'color:#00ff88;font-weight:700'
        if float(val) < 0: return 'color:#ff4060;font-weight:700'
    except: pass
    return ''

def color_status(val):
    if val == "HIT TARGET": return 'color:#00ff88;font-weight:700'
    if val == "HIT SL":     return 'color:#ff4060;font-weight:700'
    if val == "OPEN":       return 'color:#ffc700;font-weight:700'
    return ''


# ============================================================
# JOURNAL
# ============================================================
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


# ============================================================
# HEADER
# ============================================================
open_status, market_msg = is_market_open()
now_str = datetime.now().strftime("%d %b %Y · %H:%M:%S")

st.markdown(f"""
<div class="top-header">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
    <div>
      <div class="logo-text">📈 F&O PRO SCANNER</div>
      <div class="logo-sub">NSE · Intraday · Live OI + EMA + VWAP</div>
    </div>
    <div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap;">
      <div style="background:{'#00ff8820' if open_status else '#ff406020'};
                  border:1px solid {'#00ff8840' if open_status else '#ff406040'};
                  border-radius:6px;padding:6px 14px;
                  color:{'#00ff88' if open_status else '#ff4060'};
                  font-size:12px;font-weight:700;letter-spacing:1px;">
        {'🟢' if open_status else '🔴'} {market_msg}
      </div>
      <div style="color:#3a5a7a;font-size:11px;">⏰ {now_str}</div>
      <div style="color:#6a8aaa;font-size:11px;">👤 {st.session_state.get('username','').upper()}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3 = st.tabs(["  📡  LIVE SCANNER  ", "  📊  CHART VIEW  ", "  📓  TRADE JOURNAL  "])


# ─────────────────────────────────────────
# TAB 1 — SCANNER
# ─────────────────────────────────────────
with tab1:
    if not open_status:
        st.warning(f"⚠️ {market_msg} — Last trading day ka data dikhayega")

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        scan_btn = st.button("🔍  SCAN MARKET", use_container_width=True)

    if scan_btn:
        with st.spinner("NSE se OI Gainers fetch ho rahe hain..."):
            watchlist = get_oi_gainers()

        st.markdown(f'<div class="section-header">📋 {len(watchlist)} Stocks Scan Ho Rahe Hain</div>', unsafe_allow_html=True)

        results  = []
        progress = st.progress(0)
        status   = st.empty()

        for i, ticker in enumerate(watchlist):
            status.markdown(f'<div style="color:#6a8aaa;font-size:11px;letter-spacing:1px;">⏳ SCANNING: <span style="color:#00d4ff;font-weight:700;">{ticker}</span> ({i+1}/{len(watchlist)})</div>', unsafe_allow_html=True)
            data = get_pro_data(ticker)
            if data:
                results.append(data)
            progress.progress((i + 1) / len(watchlist))

        status.empty()
        progress.empty()

        if results:
            df_result = pd.DataFrame(results)
            st.session_state['scan_results'] = results

            buy_c  = len(df_result[df_result['SIGNAL'].str.contains('BUY')])
            sell_c = len(df_result[df_result['SIGNAL'].str.contains('SELL')])
            wait_c = len(df_result[df_result['SIGNAL'].str.contains('WAIT')])

            # Stat cards
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("📊 Total Found",   len(df_result))
            c2.metric("🚀 Strong Buy",    buy_c)
            c3.metric("🔴 Sell",          sell_c)
            c4.metric("🟡 Wait",          wait_c)
            c5.metric("⏰ Scanned At",    datetime.now().strftime("%H:%M:%S"))

            st.markdown('<div class="section-header">📈 Scan Results</div>', unsafe_allow_html=True)

            # Filter buttons
            f1, f2, f3, f4 = st.columns(4)
            show_filter = f1.selectbox("Filter by Signal", ["All", "Strong Buy", "Sell", "Wait"], label_visibility="collapsed")

            df_show = df_result.copy()
            if show_filter == "Strong Buy":
                df_show = df_show[df_show['SIGNAL'].str.contains('BUY')]
            elif show_filter == "Sell":
                df_show = df_show[df_show['SIGNAL'].str.contains('SELL')]
            elif show_filter == "Wait":
                df_show = df_show[df_show['SIGNAL'].str.contains('WAIT')]

            styled = (
                df_show.style
                .map(color_signal,   subset=['SIGNAL'])
                .map(color_strength, subset=['STRENGTH'])
                .map(color_ema,      subset=['EMA TREND'])
                .map(color_vwap,     subset=['VWAP'])
                .map(color_chg,      subset=['CHG %'])
                .set_properties(**{
                    'background-color': '#0d1219',
                    'color':            '#c8d8e8',
                    'border-color':     '#1e2d3d',
                    'font-size':        '12px',
                })
                .set_table_styles([
                    {'selector': 'thead th', 'props': [
                        ('background-color', '#111820'),
                        ('color', '#6a8aaa'),
                        ('font-size', '10px'),
                        ('letter-spacing', '2px'),
                        ('text-transform', 'uppercase'),
                        ('border-bottom', '2px solid #1e2d3d'),
                        ('padding', '10px 12px'),
                    ]},
                    {'selector': 'tbody tr:hover', 'props': [
                        ('background-color', '#111820 !important'),
                    ]},
                    {'selector': 'tbody td', 'props': [
                        ('padding', '10px 12px'),
                        ('border-bottom', '1px solid #1e2d3d'),
                    ]},
                ])
            )

            st.dataframe(styled, use_container_width=True, height=520)

            # Download button
            csv = df_result.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 CSV Download Karo",
                data=csv,
                file_name=f"scan_{datetime.now().strftime('%d%m%Y_%H%M')}.csv",
                mime='text/csv',
            )
        else:
            st.warning("⚠️ Koi stock nahi mila — market band hai ya data nahi mila")

    elif 'scan_results' in st.session_state:
        st.info("💡 Pichli scan ke results dikh rahe hain — nayi scan ke liye button dabao")
        df_result = pd.DataFrame(st.session_state['scan_results'])
        styled = (
            df_result.style
            .map(color_signal,   subset=['SIGNAL'])
            .map(color_strength, subset=['STRENGTH'])
            .map(color_ema,      subset=['EMA TREND'])
            .map(color_vwap,     subset=['VWAP'])
        )
        st.dataframe(styled, use_container_width=True, height=520)


# ─────────────────────────────────────────
# TAB 2 — CHART
# ─────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">📊 Candlestick Chart — EMA + VWAP</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        chart_ticker = st.text_input("Stock Symbol", value="RELIANCE", placeholder="e.g. SBIN, TCS, RELIANCE").upper()
    with col_b:
        timeframe = st.selectbox("Timeframe", ["5 Min", "15 Min", "1 Hour"])
    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)
        load_btn = st.button("📈  Load Chart", use_container_width=True)

    interval_map = {
        "5 Min":  ("5m",  "5d"),
        "15 Min": ("15m", "5d"),
        "1 Hour": ("1h",  "30d"),
    }

    if load_btn:
        interval, period = interval_map[timeframe]
        with st.spinner(f"Loading {chart_ticker} {timeframe} chart..."):
            df_chart = get_candle_data(chart_ticker, interval, period)

        if df_chart is not None and len(df_chart) > 5:
            fig = plot_candles(df_chart, chart_ticker, timeframe)
            st.plotly_chart(fig, use_container_width=True)

            last = df_chart.iloc[-1]
            prev = df_chart.iloc[-2]
            chg_val = round(float(last['Close']) - float(prev['Close']), 2)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("💰 LTP",   round(float(last['Close']), 2), delta=chg_val)
            m2.metric("〰 VWAP",  round(float(last['VWAP']), 2))
            m3.metric("📊 EMA 9",  round(float(last['EMA9']), 2))
            m4.metric("📊 EMA 21", round(float(last['EMA21']), 2))

            # Signal summary
            cp    = float(last['Close'])
            vwap  = float(last['VWAP'])
            e9    = float(last['EMA9'])
            e21   = float(last['EMA21'])
            above_vwap = cp > vwap
            bull_ema   = e9 > e21

            if above_vwap and bull_ema:
                sig_color = "#00ff88"; sig_text = "🚀 BULLISH SETUP — Entry ke liye tayar"
            elif not above_vwap and not bull_ema:
                sig_color = "#ff4060"; sig_text = "🔴 BEARISH SETUP — Short side dekho"
            else:
                sig_color = "#ffc700"; sig_text = "🟡 MIXED SIGNALS — Wait karo"

            st.markdown(f"""
            <div style="background:{sig_color}15;border:1px solid {sig_color}40;
                        border-radius:8px;padding:12px 20px;margin-top:8px;
                        color:{sig_color};font-weight:700;font-size:13px;letter-spacing:1px;">
                {sig_text}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Data nahi mila — symbol check karo ya market band hai")


# ─────────────────────────────────────────
# TAB 3 — JOURNAL
# ─────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">📓 Trade Journal — Apni Trades Track Karo</div>', unsafe_allow_html=True)

    with st.expander("➕  Nayi Trade Entry Add Karo", expanded=False):
        j1, j2, j3 = st.columns(3)
        j_date  = j1.date_input("📅 Date", datetime.now())
        j_stock = j2.text_input("📌 Stock", placeholder="e.g. RELIANCE")
        j_type  = j3.selectbox("📊 Trade Type", ["BUY", "SELL"])

        j4, j5, j6 = st.columns(3)
        j_entry  = j4.number_input("💰 Entry Price", min_value=0.0, format="%.2f")
        j_sl     = j5.number_input("🛑 Stop Loss",   min_value=0.0, format="%.2f")
        j_target = j6.number_input("🎯 Target",      min_value=0.0, format="%.2f")

        j7, j8 = st.columns(2)
        j_qty    = j7.number_input("📦 Quantity", min_value=1, value=1)
        j_status = j8.selectbox("🔖 Status", ["OPEN", "HIT TARGET", "HIT SL", "EXITED"])

        j_notes = st.text_area("📝 Notes / Reason", placeholder="Trade lene ka reason kya tha? ICT setup, OI data, etc.")

        if st.button("💾  Entry Save Karo", use_container_width=True):
            if j_stock:
                entries = load_journal()
                pnl = 0
                if j_status != "OPEN":
                    if j_type == "BUY":
                        exit_price = j_target if j_status == "HIT TARGET" else j_sl if j_status == "HIT SL" else j_entry
                    else:
                        exit_price = j_sl if j_status == "HIT TARGET" else j_target if j_status == "HIT SL" else j_entry
                    pnl = round((exit_price - j_entry) * j_qty if j_type == "BUY" else (j_entry - exit_price) * j_qty, 2)

                entries.append({
                    "date": str(j_date), "stock": j_stock.upper(),
                    "type": j_type, "entry": j_entry, "sl": j_sl,
                    "target": j_target, "qty": j_qty,
                    "status": j_status, "pnl": pnl, "notes": j_notes
                })
                save_journal(entries)
                st.success(f"✅ {j_stock.upper()} entry save ho gayi!")
            else:
                st.error("❌ Stock ka naam daalo!")

    st.markdown("---")

    entries = load_journal()
    if entries:
        df_journal = pd.DataFrame(entries)

        total_pnl = df_journal['pnl'].sum()
        wins      = len(df_journal[df_journal['pnl'] > 0])
        losses    = len(df_journal[df_journal['pnl'] < 0])
        open_t    = len(df_journal[df_journal['status'] == 'OPEN'])
        win_rate  = round((wins / max(wins + losses, 1)) * 100, 1)

        p1, p2, p3, p4, p5 = st.columns(5)
        p1.metric("💰 Total P&L",    f"₹{round(total_pnl, 2)}", delta=f"₹{round(total_pnl,2)}")
        p2.metric("✅ Winning",       wins)
        p3.metric("❌ Losing",        losses)
        p4.metric("🎯 Win Rate",      f"{win_rate}%")
        p5.metric("🔓 Open Trades",   open_t)

        styled_j = (
            df_journal.style
            .map(color_pnl,    subset=['pnl'])
            .map(color_status, subset=['status'])
            .set_properties(**{
                'background-color': '#0d1219',
                'color':            '#c8d8e8',
                'border-color':     '#1e2d3d',
                'font-size':        '12px',
            })
            .set_table_styles([
                {'selector': 'thead th', 'props': [
                    ('background-color', '#111820'),
                    ('color', '#6a8aaa'),
                    ('font-size', '10px'),
                    ('letter-spacing', '2px'),
                    ('text-transform', 'uppercase'),
                    ('border-bottom', '2px solid #1e2d3d'),
                    ('padding', '10px 12px'),
                ]},
                {'selector': 'tbody td', 'props': [
                    ('padding', '10px 12px'),
                    ('border-bottom', '1px solid #1e2d3d'),
                ]},
            ])
        )
        st.dataframe(styled_j, use_container_width=True, height=420)

        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button("🗑️  Journal Clear Karo"):
                save_journal([])
                st.success("Journal clear ho gaya!")
                st.rerun()
    else:
        st.markdown("""
        <div style="background:#0d1219;border:1px solid #1e2d3d;border-radius:10px;
                    padding:40px;text-align:center;color:#3a5a7a;">
            <div style="font-size:2rem;margin-bottom:8px;">📓</div>
            <div style="font-size:12px;letter-spacing:2px;">Abhi koi entry nahi — upar se add karo!</div>
        </div>
        """, unsafe_allow_html=True)
