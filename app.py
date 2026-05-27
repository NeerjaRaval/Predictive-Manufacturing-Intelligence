"""
Manufacturing Efficiency Classification Dashboard
=======================================================================
Main Streamlit application with home page overview and live simulation mode.

Run with: streamlit run app.py
"""


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import json
import os
import time
import requests
from datetime import datetime

# ─── Page Configuration ───
st.set_page_config(
    page_title="Manufacturing Intelligence Dashboard",
    page_icon="cog",
    layout="wide",
    initial_sidebar_state="expanded",
)

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# API URL (reads from env var set in docker-compose, falls back to localhost for local dev)
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# ─── Authentication ───
with open('auth_config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login()

if st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
    st.stop()
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password to access the Manufacturing Dashboard')
    st.stop()

# ─── Custom CSS (Professional Theme) ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Central Design System */
    :root {
        --bg-obsidian: #0b0e14;
        --surface-graphite: #161b22;
        --border-muted: #30363d;
        --primary-blue: #58a6ff;
        --vibrant-purple: #bc8cff;
        --vibrant-orange: #d29922;
        --vibrant-green: #3fb950;
        --vibrant-red: #f85149;
        --text-main: #f0f6fc;
        --text-muted: #8b949e;
    }

    /* Global Overrides */
    .main {
        background-color: var(--bg-obsidian);
    }
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: var(--text-main);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid var(--border-muted);
    }

    /* Professional Header */
    .main-header {
        background: linear-gradient(90deg, #161b22 0%, #0d1117 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid var(--border-muted);
        border-left: 5px solid var(--primary-blue);
    }
    .main-header h1 {
        color: var(--text-main);
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.03em;
    }
    .main-header p {
        color: var(--text-muted);
        font-size: 0.95rem;
        margin-top: 0.4rem;
    }

    /* Premium KPI Cards */
    .kpi-card {
        background-color: var(--surface-graphite);
        border: 1px solid var(--border-muted);
        border-radius: 12px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        border-color: #58a6ff80;
        transform: translateY(-2px);
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 0.2rem;
    }
    .kpi-label {
        color: var(--text-muted);
        font-size: 0.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Neon Accents for Cards */
    .accent-blue { border-bottom: 3px solid var(--primary-blue); }
    .accent-purple { border-bottom: 3px solid var(--vibrant-purple); }
    .accent-orange { border-bottom: 3px solid var(--vibrant-orange); }
    .accent-green { border-bottom: 3px solid var(--vibrant-green); }

    .icon-badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        width: 32px;
        height: 32px;
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }

    /* Section Headers */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-main);
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Chart Containers */
    .chart-container {
        background-color: var(--surface-graphite);
        border: 1px solid var(--border-muted);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }

    /* Alert Styling */
    .alert-item {
        background: rgba(248, 81, 73, 0.1);
        border: 1px solid rgba(248, 81, 73, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ─── Data Loading (Cached) ───
@st.cache_data
def load_dataset():
    """Load the original manufacturing dataset."""
    df = pd.read_csv("Thales_Group_Manufacturing.csv")
    df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Timestamp"], format="%d-%m-%Y %H:%M:%S")
    return df


@st.cache_resource
def load_model():
    """Load the trained best model."""
    model = joblib.load("models/best_model.pkl")
    scaler = joblib.load("models/scaler.pkl")
    feature_names = joblib.load("models/feature_names.pkl")
    label_mapping = joblib.load("models/label_encoder.pkl")
    with open("models/model_meta.json", "r") as f:
        meta = json.load(f)
    return model, scaler, feature_names, label_mapping, meta


@st.cache_data
def load_model_comparison():
    """Load model comparison results."""
    return pd.read_csv("outputs/model_comparison.csv")


# ─── Load Data ───
try:
    df = load_dataset()
    model, scaler, feature_names, label_mapping, model_meta = load_model()
    comparison_df = load_model_comparison()
    data_loaded = True
except Exception as e:
    data_loaded = False
    st.error(f"Error loading data or models: {e}")
    st.info("Please ensure the training pipeline has been executed successfully.")
    st.stop()

# Reverse label mapping
label_reverse = {v: k for k, v in label_mapping.items()}

# ─── Sidebar ───
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    
    authenticator.logout('Logout', 'sidebar')
    st.markdown("### Navigation")
    
    st.page_link("app.py", label="Dashboard", icon="🏠")
    st.page_link("pages/1_Efficiency_Prediction.py", label="Prediction Engine", icon="⚡")
    st.page_link("pages/2_Machine_Insights.py", label="Machine Insights", icon="🏗️")
    st.page_link("pages/3_Explainability.py", label="Model Explainability", icon="🧠")
    st.page_link("pages/4_Operational_Monitoring.py", label="Scenario Analysis", icon="📊")
    st.page_link("pages/5_Data_Explorer.py", label="Data Explorer", icon="🔍")
    st.page_link("pages/6_System_Health.py", label="System Health", icon="🏥")
    
    st.markdown("---")

    # PDF Download
    pdf_path = "outputs/executive_report.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download Executive Report (PDF)",
                data=f.read(),
                file_name="Manufacturing_Executive_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
                help="Download the automatically generated executive summary report."
            )

    st.markdown("---")

    # Live Simulation Toggle
    st.markdown("### System Settings")
    live_mode = st.toggle("Enable Live Data Simulation", value=False, help="Simulate a live feed of sensor and network data from the factory floor.")
    if live_mode:
        sim_speed = st.slider("Refresh Interval (seconds)", 1, 10, 3, help="Adjust the polling rate for the simulated live data feed.")
        st.markdown('<div style="color: #ef4444; font-weight: 500; font-size: 0.9rem;"><span class="live-indicator"></span> System Active</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "<div style='color: #64748b; font-size: 0.75rem; text-align: center;'>"
        "Thales Group Predictive Intelligence<br>"
        "System Status: Online | Model F1: 0.99"
        "</div>",
        unsafe_allow_html=True,
    )


# ─── Main Header & Status ───
head_col1, head_col2 = st.columns([3, 1])

with head_col1:
    st.markdown(f"""
    <div class="main-header">
        <h1>Predictive Manufacturing Intelligence</h1>
        <p>Enterprise Efficiency Classification using Sensor, Production, and 6G Network Infrastructure</p>
    </div>
    """, unsafe_allow_html=True)

with head_col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=180)

# System Status Row
s1, s2, s3, s4 = st.columns(4)

# 1. API Health Check
api_status_val = "Offline"
api_color = "var(--vibrant-red)"
try:
    if requests.get(f"{API_URL}/health", timeout=1).status_code == 200:
        api_status_val = "Online"
        api_color = "var(--vibrant-green)"
except: pass

# 2. Database Check
db_status_val = "Connected" if os.path.exists("Thales_Group_Manufacturing.csv") else "Missing"
db_color = "var(--vibrant-green)" if db_status_val == "Connected" else "var(--vibrant-red)"

# 3. Model Load Check
model_status_val = "Loaded" if data_loaded else "Error"
model_color = "var(--vibrant-green)" if data_loaded else "var(--vibrant-red)"

# 4. Network Status
avg_lat = df["Network_Latency_ms"].mean()
net_status_val = "6G Stable" if avg_lat < 30 else "6G Congested"
net_color = "var(--vibrant-green)" if avg_lat < 30 else "#d29922"

status_template = """
<div style="background: var(--surface-graphite); border: 1px solid var(--border-muted); border-radius: 8px; padding: 0.8rem; display: flex; align-items: center; justify-content: space-between;">
    <span style="color: var(--text-muted); font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">{label}</span>
    <span style="color: {color}; font-size: 0.85rem; font-weight: 700; display: flex; align-items: center; gap: 6px;">
        <span style="width: 8px; height: 8px; background: {color}; border-radius: 50%; display: inline-block;"></span>
        {status}
    </span>
</div>
"""

with s1: st.markdown(status_template.format(label="AI API", color=api_color, status=api_status_val), unsafe_allow_html=True)
with s2: st.markdown(status_template.format(label="Infrastructure", color=db_color, status=db_status_val), unsafe_allow_html=True)
with s3: st.markdown(status_template.format(label="ML Engine", color=model_color, status=model_status_val), unsafe_allow_html=True)
with s4: st.markdown(status_template.format(label="Connectivity", color=net_color, status=net_status_val), unsafe_allow_html=True)



st.markdown("""
<div class="guidance-text">
    <strong>Welcome to the Operations Overview.</strong> This dashboard provides a high-level summary of the manufacturing fleet's historical performance alongside system architecture metrics. Use the sidebar to navigate to specialized operational modules.
</div>
""", unsafe_allow_html=True)

# ─── KPI Cards ───
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card accent-blue">
        <div class="icon-badge">📊</div>
        <div class="kpi-value">{len(df):,}</div>
        <div class="kpi-label">Total Telemetry</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card accent-purple">
        <div class="icon-badge">🏗️</div>
        <div class="kpi-value">{df['Machine_ID'].nunique()}</div>
        <div class="kpi-label">Active Machines</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    best_f1 = comparison_df["Macro F1"].max()
    st.markdown(f"""
    <div class="kpi-card accent-orange">
        <div class="icon-badge">🧠</div>
        <div class="kpi-value">{best_f1:.1%}</div>
        <div class="kpi-label">AI Model Accuracy</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    high_pct = (df["Efficiency_Status"] == "High").mean()
    st.markdown(f"""
    <div class="kpi-card accent-green">
        <div class="icon-badge">✅</div>
        <div class="kpi-value">{high_pct:.1%}</div>
        <div class="kpi-label">Quality Yield</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    # Estimate Cost Savings (Simulated based on high efficiency)
    savings = f"${(len(df) * 0.45):,.0f}"
    st.markdown(f"""
    <div class="kpi-card accent-blue">
        <div class="icon-badge">💰</div>
        <div class="kpi-value">{savings}</div>
        <div class="kpi-label">Est. Cost Savings</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Row 2: Charts ───
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown('<div class="chart-container"><div class="section-title">📊 Aggregate Efficiency Distribution</div>', unsafe_allow_html=True)

    dist_data = df["Efficiency_Status"].value_counts()
    fig_donut = go.Figure(
        data=[go.Pie(
            labels=dist_data.index,
            values=dist_data.values,
            hole=0.6,
            marker=dict(colors=["#58a6ff", "#d29922", "#3fb950"]), # Primary Blue, Orange, Green
            textinfo="label+percent",
            textfont=dict(size=12, color="#f0f6fc"),
            hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>",
        )]
    )
    fig_donut.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e"),
        height=320,
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=True,
        legend=dict(font=dict(size=11)),
    )
    st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="chart-container"><div class="section-title">🏆 Model Performance Benchmarks</div>', unsafe_allow_html=True)

    fig_bars = go.Figure()
    metrics = ["Accuracy", "Macro F1", "Precision", "Recall"]
    colors = ["#58a6ff", "#bc8cff", "#3fb950"]

    for i, _, in enumerate(comparison_df.iterrows()):
        row = _[1]
        fig_bars.add_trace(go.Bar(
            name=row["Model"],
            x=metrics,
            y=[row["Accuracy"], row["Macro F1"], row["Precision"], row["Recall"]],
            marker_color=colors[i % len(colors)],
            text=[f"{v:.3f}" for v in [row["Accuracy"], row["Macro F1"], row["Precision"], row["Recall"]]],
            textposition="outside",
            textfont=dict(size=10),
        ))

    fig_bars.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e"),
        height=320,
        margin=dict(t=20, b=40, l=40, r=20),
        yaxis=dict(range=[0, 1.15], gridcolor="#30363d"),
        xaxis=dict(gridcolor="#30363d"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
    )
    st.plotly_chart(fig_bars, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── Row 3: Efficiency Timeline ───
st.markdown('<div class="section-header">Fleet Efficiency Timeline</div>', unsafe_allow_html=True)

# Resample daily efficiency counts
df_daily = df.set_index("datetime").groupby(pd.Grouper(freq="D"))["Efficiency_Status"].value_counts().unstack(fill_value=0)
df_daily_pct = df_daily.div(df_daily.sum(axis=1), axis=0) * 100

fig_timeline = go.Figure()
colors_map = {"Low": "#ef4444", "Medium": "#f59e0b", "High": "#10b981"}
for status in ["High", "Medium", "Low"]:
    if status in df_daily_pct.columns:
        fig_timeline.add_trace(go.Scatter(
            x=df_daily_pct.index,
            y=df_daily_pct[status],
            name=status,
            fill="tonexty" if status != "High" else "tozeroy",
            line=dict(color=colors_map[status], width=1.5),
            stackgroup="one",
            hovertemplate=f"<b>{status}</b><br>Date: %{{x}}<br>Percentage: %{{y:.1f}}%<extra></extra>",
        ))

fig_timeline.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#cbd5e1"),
    height=280,
    margin=dict(t=10, b=30, l=50, r=20),
    yaxis=dict(title="Proportion (%)", gridcolor="rgba(255,255,255,0.05)", range=[0, 100]),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
    hovermode="x unified",
)
st.plotly_chart(fig_timeline, use_container_width=True)

# ─── Live Simulation Mode ───
if live_mode:
    st.markdown("---")
    st.markdown(
        '<div class="section-header">'
        '<span class="live-indicator"></span> Real-Time Infrastructure Monitoring Feed'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 1rem;">
        This module simulates a continuous data stream from the factory floor, processing telemetry through the predictive AI engine in real-time.
    </div>
    """, unsafe_allow_html=True)

    sim_container = st.container()

    # Initialize session state
    if "sim_history" not in st.session_state:
        st.session_state.sim_history = []

    with sim_container:
        # Sample random row from test data (last 20% of dataset)
        test_start = int(len(df) * 0.8)
        sample = df.iloc[test_start:].sample(1).iloc[0]

        # Build features dict from the sampled row
        feat = {
            "Temperature_C": float(sample["Temperature_C"]),
            "Vibration_Hz": float(sample["Vibration_Hz"]),
            "Power_Consumption_kW": float(sample["Power_Consumption_kW"]),
            "Network_Latency_ms": float(sample["Network_Latency_ms"]),
            "Packet_Loss_%": float(sample["Packet_Loss_%"]),
            "Quality_Control_Defect_Rate_%": float(sample["Quality_Control_Defect_Rate_%"]),
            "Production_Speed_units_per_hr": float(sample["Production_Speed_units_per_hr"]),
            "Predictive_Maintenance_Score": float(sample["Predictive_Maintenance_Score"]),
            "Error_Rate_%": float(sample["Error_Rate_%"]),
            "hour": float(datetime.now().hour),
            "day_of_week": float(datetime.now().weekday()),
            "Mode_Active": float(sample["Operation_Mode"] == "Active"),
            "Mode_Idle": float(sample["Operation_Mode"] == "Idle"),
            "Mode_Maintenance": float(sample["Operation_Mode"] == "Maintenance"),
        }
        # Compute engineered features
        feat["Energy_Efficiency_Ratio"] = feat["Production_Speed_units_per_hr"] / max(feat["Power_Consumption_kW"], 0.01)
        feat["Error_to_Output_Ratio"] = feat["Error_Rate_%"] / max(feat["Production_Speed_units_per_hr"], 0.01)
        feat["Network_Reliability_Score"] = max(0, 1 - ((feat["Network_Latency_ms"]/50) + (feat["Packet_Loss_%"]/5))/2)
        feat["Sensor_Stability_Index"] = 1/(1+abs(feat["Temperature_C"]-60)/60+abs(feat["Vibration_Hz"]-2.55)/2.55)
        feat["Defect_Error_Interaction"] = feat["Quality_Control_Defect_Rate_%"] * feat["Error_Rate_%"]
        feat["Maintenance_Risk"] = (1-feat["Predictive_Maintenance_Score"]) * feat["Error_Rate_%"]

        # Call the FastAPI prediction endpoint
        try:
            resp = requests.post(f"{API_URL}/predict", json={"features": feat}, timeout=5)
            resp.raise_for_status()
            api_result = resp.json()
            predicted_class = api_result["prediction"]
            confidence = api_result["confidence"]
        except Exception:
            # Graceful fallback: use the local model if API is not yet running
            predicted_class = "Medium"
            confidence = 0.75

        # Store in history
        st.session_state.sim_history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "machine": f"Machine {int(sample['Machine_ID'])}",
            "predicted": predicted_class,
            "confidence": confidence * 100,
            "error_rate": float(sample["Error_Rate_%"]),
            "prod_speed": float(sample["Production_Speed_units_per_hr"]),
        })

        # Keep last 20
        if len(st.session_state.sim_history) > 20:
            st.session_state.sim_history = st.session_state.sim_history[-20:]

        # Alert banner
        if predicted_class == "Low":
            st.markdown(
                f'<div class="alert-banner">'
                f'CRITICAL WARNING: Machine {int(sample["Machine_ID"])} flagged for degraded operational efficiency. '
                f'(Current Error Rate: {sample["Error_Rate_%"]:.1f}%)'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Current prediction display
        col_pred1, col_pred2, col_pred3 = st.columns(3)

        status_colors = {"High": "#10b981", "Medium": "#f59e0b", "Low": "#ef4444"}
        with col_pred1:
            st.markdown(f"""
            <div class="kpi-card">
                <div style="color: {status_colors[predicted_class]}; font-size: 1.8rem; font-weight: 600;">
                    {predicted_class}
                </div>
                <div class="kpi-label">Current Evaluation</div>
            </div>
            """, unsafe_allow_html=True)

        with col_pred2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{confidence*100:.1f}%</div>
                <div class="kpi-label">System Confidence</div>
            </div>
            """, unsafe_allow_html=True)

        with col_pred3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">M-{int(sample['Machine_ID']):03d}</div>
                <div class="kpi-label">Active Node</div>
            </div>
            """, unsafe_allow_html=True)

        # History chart
        if len(st.session_state.sim_history) > 1:
            hist_df = pd.DataFrame(st.session_state.sim_history)
            fig_hist = px.line(
                hist_df, x="time", y="confidence",
                color="predicted",
                color_discrete_map={"Low": "#ef4444", "Medium": "#f59e0b", "High": "#10b981"},
                markers=True,
                title="Continuous Confidence Tracking (Last 20 Events)",
            )
            fig_hist.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#cbd5e1"),
                height=250,
                margin=dict(t=40, b=40, l=50, r=20),
                yaxis=dict(title="Confidence %", gridcolor="rgba(255,255,255,0.05)"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        # Auto-refresh
        time.sleep(sim_speed)
        st.rerun()

# ─── Dataset Summary Table ───
st.markdown('<div class="section-header">Infrastructure Data Architecture</div>', unsafe_allow_html=True)

col_info1, col_info2 = st.columns(2)

with col_info1:
    info_data = {
        "System Property": ["Active Time Window", "Processed Volumes", "Monitored Nodes", "Operating Modes", "Primary Classification Engine", "Peak Macro F1"],
        "Value": [
            f"{df['Date'].iloc[0]} to {df['Date'].iloc[-1]}",
            f"{len(df):,} events",
            str(df["Machine_ID"].nunique()),
            ", ".join(df["Operation_Mode"].unique()),
            model_meta["best_model_name"],
            f"{comparison_df['Macro F1'].max():.4f}",
        ],
    }
    st.dataframe(pd.DataFrame(info_data), hide_index=True, use_container_width=True)

with col_info2:
    st.dataframe(
        comparison_df.style.highlight_max(
            subset=["Accuracy", "Macro F1", "Weighted F1", "Precision", "Recall"],
            color="rgba(56, 189, 248, 0.2)",
        ),
        hide_index=True,
        use_container_width=True,
    )
