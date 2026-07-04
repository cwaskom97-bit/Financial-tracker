import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# Ensure layout is wide and consistent
st.set_page_config(
    page_title="AI Financial Intelligence Hub", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State Variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "ai", "text": 'System ready. Once a live business integration is established, I can predict quarters, analyze runway, and audit vendor anomalies.'}
    ]
if "scenario_headcount" not in st.session_state:
    st.session_state.scenario_headcount = 0
if "scenario_marketing" not in st.session_state:
    st.session_state.scenario_marketing = 0
if "scenario_price" not in st.session_state:
    st.session_state.scenario_price = 0

# Static Formatter Utilities
def fmt(n):
    return f"${int(round(n)):,}"

# --- INITIAL EMPTY STATE DATA STRUCTURES (READY FOR LIVE CONNECTION) ---
# Set to 0 and empty placeholders until an external corporate API/ERP is linked.
def build_empty_history():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    rows = [{"Month": m, "Revenue": 0, "Expenses": 0, "Profit": 0} for m in months]
    return pd.DataFrame(rows)

HISTORY = build_empty_history()

def build_forecast(history_df, headcount_delta=0, marketing_delta=0, price_delta=0):
    # Generates zeroed baselines when no historical data exists
    forecast_rows = []
    for step in range(1, 5):
        forecast_rows.append({
            "Quarter": f"Q+{step}",
            "Expected Profit": 0,
            "Optimistic Profit": 0,
            "Worst-case Profit": 0,
            "Revenue Forecast": 0,
            "Expenses Forecast": 0
        })
    return pd.DataFrame(forecast_rows)

DEPARTMENTS = pd.DataFrame([
    {"Department": "Engineering", "Budget": 0, "Actual": 0},
    {"Department": "Marketing", "Budget": 0, "Actual": 0},
    {"Department": "Sales", "Budget": 0, "Actual": 0},
    {"Department": "Operations", "Budget": 0, "Actual": 0},
    {"Department": "People & HR", "Budget": 0, "Actual": 0},
])

VENDORS = []  # No active contracts mapped yet
ALERTS = []   # No transaction risks identified on empty books
RECOMMENDATIONS = []

# Config Theme Values
bg_color = "#0b0e14" if st.session_state.dark_mode else "#f6f3ec"
text_color = "#e7e3d8" if st.session_state.dark_mode else "#1c1a14"
card_color = "#12161f" if st.session_state.dark_mode else "#ffffff"
border_color = "#232a38" if st.session_state.dark_mode else "#ddd6c4"

# Safe Global Styles injection via string formatting instead of raw f-strings
styles = """
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    div[data-testid="stMetricValue"] {{ font-family: monospace; font-weight: 700; }}
    .kpi-card {{
        background-color: {card}; border: 1px solid {border};
        padding: 15px; border-radius: 8px; margin-bottom: 10px;
    }}
    </style>
""".format(bg=bg_color, txt=text_color, card=card_color, border=border_color)

st.markdown(styles, unsafe_allow_html=True)


# ---------------------------------------------------------------------
# SCREEN 1: LOGIN PORTAL
# ---------------------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    
    with col_l2:
        st.markdown(f"""
        <div class='kpi-card' style='padding: 30px;'>
            <h2 style='text-align: center; margin-top: 0;'>💼 Corporate Intelligence Login</h2>
            <p style='text-align: center; font-size: 13px; opacity: 0.7;'>
                Enter administrative credentials to unlock data synchronizations.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username/Email", placeholder="admin@company.com")
        password = st.text_input("Security Access Password", type="password", placeholder="••••••••")
        
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("Authenticate System Access", use_container_width=True):
            # Simple demonstration authentication logic
            if username == "admin" and password == "password":
                st.session_state.logged_in = True
                st.success("Access Verified. Initializing platform workspace...")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Invalid credentials. Please verify administrative portal permissions.")
                
    st.stop()  # Prevents code below from executing unless logged_in is true


# ---------------------------------------------------------------------
# SCREEN 2: MAIN DASHBOARD APPLICATION (ACCESS GRANTED)
# ---------------------------------------------------------------------
# Top Navbar Area
col_title, col_theme, col_logout = st.columns([8, 1, 1])
with col_title:
    st.title("🎛️ AI-POWERED FINANCIAL INTELLIGENCE ENGINE")
with col_theme:
    if st.button("☀️ Light" if st.session_state.dark_mode else "🌙 Dark", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
with col_logout:
    if st.button("🔒 Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# Integration Management Notice Area
st.info("🔌 System running on zeroed parameters. Connect your company's ERP (QuickBooks, NetSuite, SAP) or banking APIs to stream verified metrics.")

# Navigation Tabs
tabs = st.tabs(["📊 Executive Dashboard", "🧠 AI Insights & Forecasting", "🧾 Invoices & Scenario Studio"])

# ---------------------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# ---------------------------------------------------------------------
with tabs[0]:
    rev_delta = 0.0
    exp_delta = 0.0
    burn_rate = 0
    cash_on_hand = 0

    # KPI Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Revenue", value=fmt(0), delta=f"{rev_delta:.1%}")
    with c2:
        st.metric(label="Operating Expenses", value=fmt(0), delta=f"{exp_delta:.1%}", delta_color="inverse")
    with c3:
        st.metric(label="Net Income", value=fmt(0), delta=fmt(0))
    with c4:
        st.metric(label="Burn Rate", value="None", delta="0.0%")

    st.markdown("---")
    
    col_main_chart, col_gauge = st.columns([2, 1])
    with col_main_chart:
        st.subheader("Revenue vs Expenses — Trailing 12 Months")
        chart_data = HISTORY.set_index("Month")[["Revenue", "Expenses"]]
        st.area_chart(chart_data, color=["#4fae7c", "#c0604f"])

    with col_gauge:
        st.subheader("System Health Metrics")
        
        gauge_html = """
        <div class='kpi-card' style='text-align: center;'>
            <h1 style='color: #7c8494; font-size: 48px; margin: 0;'>--</h1>
            <p style='letter-spacing: 2px; text-transform: uppercase; font-size: 12px;'>AI Health Score / 100</p>
            <hr style='border-color: {border};'/>
            <p style='font-size: 13px; opacity:0.6;'>Awaiting live enterprise pipeline ledger connections.</p>
            <p style='font-size: 13px; font-weight: bold;'>Cash Runway: Uncalculated</p>
        </div>
        """.format(border=border_color)
        
        st.markdown(gauge_html, unsafe_allow_html=True)

    st.subheader("Budget vs Actual Expenditures by Department")
    dept_chart = DEPARTMENTS.set_index("Department")[["Budget", "Actual"]]
    st.bar_chart(dept_chart, color=["#7c8494", "#d4a94f"])


# ---------------------------------------------------------------------
# TAB 2: AI INSIGHTS & FORECASTING
# ---------------------------------------------------------------------
with tabs[1]:
    st.subheader("Profit Forecast Models — Optimistic / Expected / Worst-case")
    base_forecast = build_forecast(HISTORY, 0, 0, 0)
    forecast_chart = base_forecast.set_index("Quarter")[["Expected Profit", "Optimistic Profit", "Worst-case Profit"]]
    st.line_chart(forecast_chart, color=["#d4a94f", "#4fae7c", "#c0604f"])

    st.markdown("---")
    
    col_alerts, col_recomms = st.columns(2)
    with col_alerts:
        st.subheader("🚨 Waste, Fraud & Anomaly Flags")
        if not ALERTS:
            st.markdown("<p style='font-size:13px; opacity:0.5;'>No transaction history analyzed yet.</p>", unsafe_allow_html=True)

    with col_recomms:
        st.subheader("✨ Autonomous AI Optimizations")
        if not RECOMMENDATIONS:
            st.markdown("<p style='font-size:13px; opacity:0.5;'>No strategic cost reductions calculated yet.</p>", unsafe_allow_html=True)


# ---------------------------------------------------------------------
# TAB 3: INVOICES & SCENARIO STUDIO
# ---------------------------------------------------------------------
with tabs[2]:
    col_input_left, col_input_right = st.columns([1, 1])
    
    with col_input_left:
        st.subheader("🧾 Invoice Dropzone & OCR Extractor")
        uploaded_file = st.file_uploader("Upload incoming transaction files (PDF, PNG, JPG)", type=["pdf", "png", "jpg"])
        
        if uploaded_file is not None:
            with st.spinner("Executing Intelligent Line-Item Parsing..."):
                time.sleep(1.1)
                invoice_html = """
                <div class='kpi-card' style='font-family: monospace; font-size:13px;'>
                    <span style='color:#4fae7c;'>✔ Extraction Process Completed</span><br/><br/>
                    <b>File Name:</b> {file}<br/>
                    <b>Identified Vendor:</b> Unregistered New Vendor<br/>
                    <b>Calculated Total:</b> {amount}<br/>
                    <b>PO Registry Status:</b> Pending Connection Sync
                </div>
                """.format(file=uploaded_file.name, amount=fmt(0))
                st.markdown(invoice_html, unsafe_allow_html=True)

        st.subheader("📋 Active Contract & Renewal Schedules")
        if VENDORS:
            st.table(pd.DataFrame(VENDORS))
        else:
            st.markdown("<p style='font-size:13px; opacity:0.5;'>No operational software vendors indexed.</p>", unsafe_allow_html=True)

    with col_input_right:
        st.subheader("🛠️ Scenario Simulation Engine")
        
        hc = st.slider("Headcount adjustments", min_value=-100, max_value=150, value=st.session_state.scenario_headcount)
        mkt = st.slider("Marketing budget shifts ($/mo)", min_value=-30000, max_value=80000, step=1000, value=st.session_state.scenario_marketing)
        prc = st.slider("Pricing matrix variance (%)", min_value=-20, max_value=20, value=st.session_state.scenario_price)
        
        st.session_state.scenario_headcount = hc
        st.session_state.scenario_marketing = mkt
        st.session_state.scenario_price = prc

        if st.button("Reset Matrix Sandbox"):
            st.session_state.scenario_headcount = 0
            st.session_state.scenario_marketing = 0
            st.session_state.scenario_price = 0
            st.rerun()

        simulated_forecast = build_forecast(HISTORY, hc, mkt, prc)
        st.line_chart(simulated_forecast.set_index("Quarter")[["Expected Profit"]], color=["#d4a94f"])

    st.markdown("---")
    
    st.subheader("💬 AI Conversational Co-Pilot")
    
    suggestion_cols = st.columns(4)
    s_queries = [
        "Predict next quarter's revenue", 
        "What if we hire 50 people?", 
        "Which subscriptions are wasted?", 
        "Show marketing ROI"
    ]
    
    def get_ai_reply(query):
        return "I am ready to compute this query, but I require an authentic historical financial dataset to generate accurate predictions or pinpoint optimization metrics."

    for idx, prompt_text in enumerate(s_queries):
        with suggestion_cols[idx]:
            if st.button(prompt_text, key=f"sug_{idx}"):
                st.session_state.chat_history.append({"role": "user", "text": prompt_text})
                st.session_state.chat_history.append({"role": "ai", "text": get_ai_reply(prompt_text)})

    for msg in st.session_state.chat_history:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.write(msg["text"])

    if chat_input := st.chat_input("Ask a financial question..."):
        st.session_state.chat_history.append({"role": "user", "text": chat_input})
        st.session_state.chat_history.append({"role": "ai", "text": get_ai_reply(chat_input)})
        st.rerun()
