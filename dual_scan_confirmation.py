"""
dual_scan_confirmation.py
---------------------------------
Purpose: Scanner ka 9:20 AM signal aur 9:45 AM signal compare karke
sirf wahi stocks confirm karna jinka signal same raha (dual-scan confirmation rule).

Kaise use karein:
1. Is file ko apne Streamlit project folder mein rakho (app.py ke saath).
2. app.py mein top pe import karo:
       from dual_scan_confirmation import save_scan_snapshot, show_confirmation_table
3. Apne scan function ke turant baad (jahan scan_results_df ban chuka hai) ye 2 lines add karo:
       save_scan_snapshot(scan_results_df)
       show_confirmation_table()

Requirement: scan_results_df mein kam se kam ye 2 columns hone chahiye:
   - "STOCK"  -> stock ka naam
   - "SIGNAL" -> current signal (e.g. BUY, SELL, STRONG SELL, WAIT)

Agar tumhare column names alag hain (e.g. "Symbol", "Signal_Type"), to neeche
COLUMN NAMES section mein bas naam badal dena.
"""

import streamlit as st
from datetime import datetime
import json
import os

# ============================================================
# COLUMN NAMES — apne dataframe ke hisaab se yahan change karo
# ============================================================
STOCK_COL = "STOCK"
SIGNAL_COL = "SIGNAL"

# ============================================================
# PERSISTENT STORAGE (optional but recommended)
# Streamlit Cloud pe session_state refresh/restart pe reset ho jata hai.
# Isliye hum ek chhoti si JSON file mein bhi save kar rahe hain taaki
# 9:20 ka snapshot 9:45 tak zinda rahe, chahe app refresh ho jaye.
# ============================================================
STORAGE_FILE = "dual_scan_snapshots.json"


def _load_storage():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_storage(data):
    try:
        with open(STORAGE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        st.warning(f"Snapshot file save nahi ho payi: {e}")


# ============================================================
# SESSION STATE INIT
# ============================================================
def _init_state():
    if "signal_920" not in st.session_state:
        stored = _load_storage()
        st.session_state.signal_920 = stored.get("signal_920", {})
        st.session_state.signal_920_date = stored.get("signal_920_date", "")

    if "signal_945" not in st.session_state:
        st.session_state.signal_945 = {}

    if "confirmed_signals" not in st.session_state:
        st.session_state.confirmed_signals = {}


# ============================================================
# STEP 1: Scan snapshot save karo (time-window based)
# ============================================================
def save_scan_snapshot(scan_results_df):
    """
    Har baar scan chalne ke baad ye function call karo.
    Ye automatically detect karega ki abhi 9:20 ka window hai ya 9:45 ka,
    aur us hisaab se signal store kar lega.
    """
    _init_state()

    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")

    if STOCK_COL not in scan_results_df.columns or SIGNAL_COL not in scan_results_df.columns:
        st.error(
            f"Column '{STOCK_COL}' ya '{SIGNAL_COL}' scan_results_df mein nahi mila. "
            f"Available columns: {list(scan_results_df.columns)}"
        )
        return

    # ---- 9:20 window (9:15 - 9:30) ----
    if "09:15" <= current_time <= "09:30":
        snapshot = dict(zip(scan_results_df[STOCK_COL], scan_results_df[SIGNAL_COL]))
        st.session_state.signal_920 = snapshot
        st.session_state.signal_920_date = today
        _save_storage({
            "signal_920": snapshot,
            "signal_920_date": today
        })
        st.info(f"📌 9:20 snapshot saved — {len(snapshot)} stocks captured.")

    # ---- 9:45 window (9:40 - 9:55) ----
    elif "09:40" <= current_time <= "09:55":
        # Agar aaj ka 9:20 snapshot nahi mila to warn karo
        if st.session_state.signal_920_date != today or not st.session_state.signal_920:
            st.warning(
                "⚠️ Aaj ka 9:20 snapshot nahi mila. Pehle 9:20-9:30 ke beech scan chalao, "
                "tabhi 9:45 comparison sahi hoga."
            )
            return

        snapshot = dict(zip(scan_results_df[STOCK_COL], scan_results_df[SIGNAL_COL]))
        st.session_state.signal_945 = snapshot
        st.info(f"📌 9:45 snapshot saved — {len(snapshot)} stocks captured.")

        _compare_signals()

    else:
        # Baaki time pe kuch save nahi karna, sirf info dikhado (optional, remove if not needed)
        pass


# ============================================================
# STEP 2: Compare karo — sirf same signal wale stocks nikaalo
# ============================================================
def _compare_signals():
    confirmed = {}
    for stock, sig_920 in st.session_state.signal_920.items():
        sig_945 = st.session_state.signal_945.get(stock)
        if sig_945 is not None and sig_945 == sig_920:
            confirmed[stock] = sig_945

    st.session_state.confirmed_signals = confirmed
    return confirmed


# ============================================================
# STEP 3: UI mein confirmed list dikhana
# ============================================================
def show_confirmation_table():
    _init_state()

    st.markdown("### ✅ Dual-Scan Confirmed Signals (9:20 == 9:45)")

    if not st.session_state.signal_920:
        st.warning("Abhi tak 9:20 ka snapshot nahi liya gaya.")
        return

    if not st.session_state.signal_945:
        st.info("9:45 ka scan abhi hona baaki hai. 9:40-9:55 ke beech scan chalao.")
        return

    if not st.session_state.confirmed_signals:
        st.warning("Koi bhi stock ka signal 9:20 se 9:45 tak same nahi raha. Sab skip.")
        return

    rows = []
    for stock, sig in st.session_state.confirmed_signals.items():
        rows.append({
            "STOCK": stock,
            "SIGNAL @9:20": st.session_state.signal_920.get(stock),
            "SIGNAL @9:45": sig,
            "STATUS": "✅ CONFIRMED — chart analysis ke liye aage badho"
        })

    st.dataframe(rows, use_container_width=True)
    st.caption(
        f"Total confirmed: {len(rows)} / {len(st.session_state.signal_920)} stocks "
        f"jo 9:20 pe scan hue the."
    )


# ============================================================
# STEP 4 (optional): Manual reset button — naye din ke liye
# ============================================================
def reset_snapshots():
    """Ye function ek button ke saath call karo agar tum manually
    naya din start karna chahte ho (test karte waqt useful)."""
    st.session_state.signal_920 = {}
    st.session_state.signal_945 = {}
    st.session_state.confirmed_signals = {}
    st.session_state.signal_920_date = ""
    if os.path.exists(STORAGE_FILE):
        os.remove(STORAGE_FILE)
    st.success("Snapshots reset ho gaye.")
