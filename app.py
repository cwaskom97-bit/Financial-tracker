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
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "ai", "text": 'Ask me anything — e.g. "Predict next quarter\'s revenue" or "What if we hire 50 people?"'}
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

# Seeded pseudo-random history builder matching JS logic
def build_history():
    # Fixed seed values to mirror JS rnd()
    state = 7
    def deterministic_rnd():
        nonlocal state
        state = (state * 9301 + 49297) % 233280
        return state / 233280

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    rows = []
    revenue = 480000
    expenses = 430000
    
    for m in months:
        revenue *= 1 + (0.015 + (deterministic_rnd() - 0.45) * 0.03)
        expenses *= 1 + (0.012 + (deterministic_rnd() - 0.5) * 0.025)
        rows.append({
            "Month": m,
            "Revenue": round(revenue),
            "Expenses": round(expenses),
            "Profit": round(revenue - expenses)
        })
    return pd.DataFrame(rows)

HISTORY = build_history()

def build_forecast(history_df, headcount_delta=0, marketing_delta=0, price_delta=0):
    n = len(history_df)
    xs = np.arange(n)
    rev_ys = history_df["Revenue"].values * (1 + price_delta / 100)
    exp_ys = history_df["Expenses"].values + (headcount_delta * 9500) + marketing_delta

    def fit_linear(ys):
        xm = np.mean(xs)
        ym = np.mean(ys)
        num = np.sum((xs - xm) * (ys - ym))
        den = np.sum((xs - xm) ** 2)
        slope = num / (den if den != 0 else 1)
        intercept = ym - slope * xm
        residuals = ys - (slope * xs + intercept)
        vol = np.sqrt(np.sum(residuals ** 2) / n)
        return slope, intercept, vol

    r_slope, r_intercept, r_vol = fit_linear(rev_ys)
    e_slope, e_intercept, e_vol = fit_linear(exp_ys)

    forecast_rows = []
    for step in range(1, 5):
        x = n - 1 + step
        rev_exp = r_slope * x + r_intercept
        exp_exp = e_slope * x + e_intercept
        band = (r_vol + e_vol) * (1 + 0.3 * step)
        
        forecast_rows.append({
            "Quarter": f"Q+{step}",
            "Expected Profit": round(rev_exp - exp_exp),
            "Optimistic Profit": round(rev_exp - exp_exp + band),
            "Worst-case Profit": round(rev_exp - exp_exp - band),
            "Revenue Forecast": round(rev_exp),
            "Expenses Forecast": round(exp_exp)
        })
    return pd.DataFrame(forecast_rows)

DEPARTMENTS = pd.DataFrame([
    {"Department": "Engineering", "Budget": 180000, "Actual": 196500},
    {"Department": "Marketing", "Budget": 90000, "Actual": 131000},
    {"Department": "Sales", "Budget": 70000, "Actual": 66200},
    {"Department": "Operations", "Budget": 50000, "Actual": 52800},
    {"Department": "People & HR", "Budget": 30000, "Actual": 28100},
])

VENDORS = [
    {"Vendor": "AWS", "Category": "Cloud Infra", "Monthly": 22000, "Renews In": "62d", "Status": "Active"},
    {"Vendor": "Google Cloud", "Category": "Cloud Infra", "Monthly": 4500, "Renews In": "62d", "Status": "Overlap (Med Risk)"},
    {"Vendor": "Datadog", "Category": "Observability", "Monthly": 3200, "Renews In": "14d", "Status": "Overlap (Med Risk)"},
    {"Vendor": "New Relic", "Category": "Observability", "Monthly": 2900, "Renews In": "201d", "Status": "Overlap (Med Risk)"},
    {"Vendor": "HubSpot", "Category": "Marketing", "Monthly": 6500, "Renews In": "9d", "Status": "Active"},
    {"Vendor": "WeWork", "Category": "Facilities", "Monthly": 15000, "Renews In": "45d", "Status": "Active"},
    {"Vendor": "Sable Logistics LLC", "Category": "Consulting", "Monthly": 18500, "Renews In": "3d", "Status": "Flagged (High Risk)"},
]

ALERTS = [
    {"severity": "🚨 CRITICAL", "title": "Suspicious vendor payment", "detail": "$18,500 paid to 'Sable Logistics LLC' — no prior invoice history, no PO match.", "impact": 18500},
    {"severity": "⚠️ HIGH", "title": "Duplicate observability spend", "detail": "Datadog and New Relic both bill for APM/monitoring — redundant coverage.", "impact": 2900},
    {"severity": "⚠️ HIGH", "title": "Marketing overspend, 46% over budget", "detail": "Meta Ads spend spiked to $41,000 this month vs a planned $28,000.", "impact": 13000},
    {"severity": "ℹ️ MEDIUM", "title": "Duplicate charge detected", "detail": "WeWork billed twice within the same 7-day window for the same $15,000 amount.", "impact": 15000},
]

RECOMMENDATIONS = [
    {"title": "Freeze payment to Sable Logistics LLC pending vendor verification", "impact": 18500, "effort": "Medium"},
    {"title": "Cap Meta Ads emergency-boost approvals at $5,000 without VP sign-off", "impact": 13000, "effort": "Low"},
    {"title": "Consolidate observability tooling onto Datadog", "impact": 2900, "effort": "Low"},
    {"title": "Renegotiate WeWork contract ahead of 45-day renewal window", "impact": 4200, "effort": "Medium"},
]

# Theme Injection Styling
bg_color = "#0b0e14" if st.session_state.dark_mode else "#f6f3ec"
text_color = "#e7e3d8" if st.session_state.dark_mode else "#1c1a14"
card_color = "#12161f" if st.session_state.dark_mode else "#ffffff"
border_color = "#232a38" if st.session_state.dark_mode else "#ddd6c4"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    div[data-testid="stMetricValue"] {{ font-family: monospace; font-weight: 700; }}
    .kpi-card {{
        background-color: {card_color}; border: 1px solid {border_color};
        padding: 15px; border-radius: 8px; margin-bottom: 10px;
    }}
    </style>
""", unsafe_allowed_html=True)

# Top Navbar Area
col_title, col_theme = st.columns([9, 1])
with col_title:
    st.title("🎛️ AI-POWERED FINANCIAL INTELLIGENCE ENGINE")
with col_theme:
    if st.button("☀️ Light" if st.session_state.dark_mode else "🌙 Dark"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.sidebar.empty() # Force reload dynamic colors

# Navigation Tabs
tabs = st.tabs(["📊 Executive Dashboard", "🧠 AI Insights & Forecasting", "🧾 Invoices & Scenario Studio"])

# ---------------------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# ---------------------------------------------------------------------
with tabs[0]:
    latest = HISTORY.iloc[-1]
    prev = HISTORY.iloc[-2]
    
    rev_delta = float(((latest['Revenue'] - prev['Revenue']) / prev['Revenue']) * 100)
    exp_delta = float(((latest['Expenses'] - prev['Expenses']) / prev['Expenses']) * 100)
    burn_rate = abs(latest['Profit']) if latest['Profit'] < 0 else 0
    cash_on_hand = 2100000

    # KPI Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Revenue", value=fmt(latest['Revenue']), delta=f"{rev_delta:.1%}")
    with c2:
        st.metric(label="Operating Expenses", value=fmt(latest['Expenses']), delta=f"{exp_delta:.1%}", delta_color="inverse")
    with c3:
        st.metric(label="Net Income", value=fmt(latest['Profit']), delta=fmt(latest['Profit'] - prev['Profit']))
    with c4:
        st.metric(label="Burn Rate", value=fmt(burn_rate) + "/mo" if burn_rate else "None", delta="0.0%")

    st.markdown("---")
    
    col_main_chart, col_gauge = st.columns([2, 1])
    with col_main_chart:
        st.subheader("Revenue vs Expenses — Trailing 12 Months")
        chart_data = HISTORY.set_index("Month")[["Revenue", "Expenses"]]
        st.area_chart(chart_data, color=["#4fae7c", "#c0604f"])

    with col_gauge:
        st.subheader("System Health Metrics")
        st.markdown(f"""
        <div class='kpi-card' style='text-align: center;'>
            <h1 style='color: #d4a94f; font-size: 48px; margin: 0;'>64</h1>
            <p style='letter-spacing: 2px; text-transform: uppercase; font-size: 12px;'>AI Health Score / 100</p>
            <hr style='border-color: {border_color};'/>
            <p style='font-size: 13px;'>Positive net income, but margin compressed by marketing overspend.</p>
            <p style='font-size: 13px; font-weight: bold;'>Cash Runway: {f"{cash_on_hand / (burn_rate if burn_rate else 1):.0f} mos" if burn_rate else 'Infinite'}</p>
        </div>
        """, unsafe_allowed_html=True)

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
        for alert in ALERTS:
            st.markdown(f"""
            <div class='kpi-card'>
                <div style='display: flex; justify-content: space-between;'>
                    <b>{alert['title']}</b>
                    <span style='color:#c0604f; font-size:11px;'>{alert['severity']}</span>
                </div>
                <p style='font-size: 12px; opacity: 0.8;'>{alert['detail']}</p>
                <span style='font-family: monospace; color:#d4a94f;'>Est Impact: {fmt(alert['impact'])}/mo</span>
            </div>
            """, unsafe_allowed_html=True)

    with col_recomms:
        st.subheader("✨ Autonomous AI Optimizations")
        for rec in RECOMMENDATIONS:
            st.markdown(f"""
            <div class='kpi-card'>
                <div style='display: flex; justify-content: space-between;'>
                    <b>{rec['title']}</b>
                    <span style='color:#4fae7c; font-weight: bold;'>+{fmt(rec['impact'])}/mo</span>
                </div>
                <p style='font-size: 11px; opacity: 0.7; margin-top: 5px;'>Effort Complexity: {rec['effort']}</p>
            </div>
            """, unsafe_allowed_html=True)


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
                mock_vendors = ["AWS", "HubSpot", "WeWork", "Doyle & Marsh LLP", "Figma"]
                v_choice = random.choice(mock_vendors)
                amt_choice = random.randint(500, 24500)
                po_match = random.choice([True, False])
                
                st.markdown(f"""
                <div class='kpi-card' style='font-family: monospace; font-size:13px;'>
                    <span style='color:#4fae7c;'>✔ Extraction Process Completed Successfully</span><br/><br/>
                    <b>File Name:</b> {uploaded_file.name}<br/>
                    <b>Identified Vendor:</b> {v_choice}<br/>
                    <b>Calculated Total:</b> {fmt(amt_choice)}<br/>
                    <b>PO Registry Status:</b> {'Matched' if po_match else 'No matching PO Found'}
                </div>
                """, unsafe_allowed_html=True)

        st.subheader("📋 Active Contract & Renewal Schedules")
        st.table(pd.DataFrame(VENDORS))

    with col_input_right:
        st.subheader("🛠️ Scenario Simulation Engine")
        
        hc = st.slider("Headcount adjustments", min_value=-100, max_value=150, value=st.session_state.scenario_headcount)
        mkt = st.slider("Marketing budget shifts ($/mo)", min_value=-30000, max_value=80000, step=1000, value=st.session_state.scenario_marketing)
        prc = st.slider("Pricing matrix variance (%)", min_value=-20, max_value=20, value=st.session_state.scenario_price)
        
        # Save updates to session variables
        st.session_state.scenario_headcount = hc
        st.session_state.scenario_marketing = mkt
        st.session_state.scenario_price = prc

        if st.button("Reset Matrix Sandbox"):
            st.session_state.scenario_headcount = 0
            st.session_state.scenario_marketing = 0
            st.session_state.scenario_price = 0
            st.rerun()

        # Generate dynamically affected charts on the fly!
        simulated_forecast = build_forecast(HISTORY, hc, mkt, prc)
        st.line_chart(simulated_forecast.set_index("Quarter")[["Expected Profit"]], color=["#d4a94f"])

    st.markdown("---")
    
    # AI Conversational Chat System
    st.subheader("💬 AI Conversational Co-Pilot")
    
    # Custom Suggestion Buttons
    suggestion_cols = st.columns(4)
    s_queries = [
        "Predict next quarter's revenue", 
        "What if we hire 50 people?", 
        "Which subscriptions are wasted?", 
        "Show marketing ROI"
    ]
    
    # Process queries using the logic map
    def get_ai_reply(query):
        q = query.lower()
        if "hire" in q or "headcount" in q:
            return f"Modeling new hires at a blended $9,500/mo fully-loaded cost each. Forecast matrices dynamically shifted inside your Sandbox panel."
        elif "marketing" in q:
            return "Marketing ROI this quarter: for every $1 spent on Meta + Google Ads, we're seeing roughly $2.40 in pipeline value down from $3.10 last quarter."
        elif "waste" in q or "unused" in q or "subscription" in q:
            return "Top wasted spend found: Datadog/New Relic overlap ($2,900/mo), Sable Logistics anomaly payment ($18,500), and a double WeWork capture ($15,000)."
        elif "predict" in q or "forecast" in q:
            return "Next quarter's expected profit parameters are trending positively with a 95% baseline accuracy model calculation."
        return "I looked across revenue, spend, and charts. Give me a more specific timeframe or criteria to look up!"

    # Render suggestion chips
    for idx, prompt_text in enumerate(s_queries):
        with suggestion_cols[idx]:
            if st.button(prompt_text, key=f"sug_{idx}"):
                st.session_state.chat_history.append({"role": "user", "text": prompt_text})
                st.session_state.chat_history.append({"role": "ai", "text": get_ai_reply(prompt_text)})

    # Message logs
    for msg in st.session_state.chat_history:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.write(msg["text"])

    # Input handling
    if chat_input := st.chat_input("Ask a financial question..."):
        st.session_state.chat_history.append({"role": "user", "text": chat_input})
        st.session_state.chat_history.append({"role": "ai", "text": get_ai_reply(chat_input)})
        st.rerun()
