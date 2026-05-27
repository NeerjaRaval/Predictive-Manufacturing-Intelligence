"""
Page 1: Efficiency Prediction Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import os

st.set_page_config(page_title="Efficiency Prediction", page_icon="zap", layout="wide")

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("🔒 Please log in from the main Dashboard page to access this module.")
    st.stop()

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.markdown("---")
    st.page_link("app.py", label="Dashboard", icon="🏠")
    st.page_link("pages/1_Efficiency_Prediction.py", label="Prediction Engine", icon="⚡")
    st.page_link("pages/2_Machine_Insights.py", label="Machine Insights", icon="🏗️")
    st.page_link("pages/3_Explainability.py", label="Model Explainability", icon="🧠")
    st.page_link("pages/4_Operational_Monitoring.py", label="Scenario Analysis", icon="📊")
    st.page_link("pages/5_Data_Explorer.py", label="Data Explorer", icon="🔍")
    st.page_link("pages/6_System_Health.py", label="System Health", icon="🏥")

# Resolve API URL from environment or default to localhost for local dev
API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-obsidian: #0b0e14;
        --surface-graphite: #161b22;
        --border-muted: #30363d;
        --primary-blue: #58a6ff;
        --vibrant-green: #3fb950;
        --vibrant-red: #f85149;
        --text-main: #f0f6fc;
        --text-muted: #8b949e;
    }

    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: var(--text-main); }

    .main-header { 
        background-color: var(--surface-graphite); 
        padding: 2rem; 
        border-radius: 12px; 
        border: 1px solid var(--border-muted);
        border-left: 5px solid var(--primary-blue);
        margin-bottom: 2rem;
    }
    .main-header h1 { margin: 0; font-size: 2.2rem; font-weight: 700; letter-spacing: -0.02em; }
    .main-header p { margin: 0.5rem 0 0 0; color: var(--text-muted); font-size: 1.1rem; }

    .pred-card { 
        background-color: var(--surface-graphite); 
        border-radius: 12px; 
        padding: 2rem;
        text-align: center; 
        border: 1px solid var(--border-muted);
        border-bottom: 4px solid var(--primary-blue);
    }
    .pred-badge { font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0; letter-spacing: -0.02em; }
    
    .section-header { 
        color: var(--text-main); 
        font-size: 1.1rem; 
        font-weight: 600; 
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem; 
        border-bottom: 1px solid var(--border-muted); 
    }

    .factor-card { 
        background: rgba(88, 166, 255, 0.05); 
        border-radius: 8px; 
        padding: 1rem; 
        margin: 0.5rem 0;
        border-left: 4px solid var(--primary-blue); 
        color: var(--text-muted); 
        font-size: 0.9rem; 
    }
    
    .guidance-text { 
        background-color: rgba(88, 166, 255, 0.1); 
        border-left: 4px solid var(--primary-blue);
        padding: 1.2rem; 
        border-radius: 0 8px 8px 0; 
        color: var(--text-main); 
        font-size: 0.9rem; 
        margin-bottom: 2rem; 
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_dataset():
    return pd.read_csv("Thales_Group_Manufacturing.csv")

df = load_dataset()

# ─── Main Header & Status ───
head_col1, head_col2 = st.columns([3, 1])

with head_col1:
    st.markdown(f"""
    <div class="main-header">
        <h1>Efficiency Prediction Engine</h1>
        <p>Manual Parameter Input, Historical Record Validation, and Batch Processing</p>
    </div>
    """, unsafe_allow_html=True)

with head_col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=180)

# System Status Row
s1, s2, s3, s4 = st.columns(4)

# Status indicators
api_status_val = "Offline"; api_color = "var(--vibrant-red)"
try:
    if requests.get(f"{API_URL}/health", timeout=1).status_code == 200:
        api_status_val = "Online"; api_color = "var(--vibrant-green)"
except: pass

db_status_val = "Connected" if os.path.exists("Thales_Group_Manufacturing.csv") else "Missing"
db_color = "var(--vibrant-green)" if db_status_val == "Connected" else "var(--vibrant-red)"

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
with s3: st.markdown(status_template.format(label="ML Engine", color="var(--vibrant-green)", status="Ready"), unsafe_allow_html=True)
with s4: st.markdown(status_template.format(label="Connectivity", color="var(--vibrant-green)", status="Stable"), unsafe_allow_html=True)

st.markdown("""
<div class="guidance-text">
    Use this module to manually evaluate infrastructure telemetry or process bulk data files. The underlying engine utilizes the trained Random Forest model.
</div>
""", unsafe_allow_html=True)


tab1, tab2, tab3 = st.tabs(["Manual Parameter Input", "Historical Record Selection", "Batch Processing"])

with tab1:
    st.markdown('<div class="section-header">Configure Telemetry Parameters</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        temp = st.slider("Temperature (C)", 30.0, 90.0, 60.0, 0.5, help="Machine core operating temperature.")
        vib = st.slider("Vibration (Hz)", 0.1, 5.0, 2.5, 0.1, help="Structural vibration frequency.")
        pwr = st.slider("Power (kW)", 1.5, 10.0, 5.5, 0.1, help="Current electrical draw.")
    with c2:
        lat = st.slider("Latency (ms)", 1.0, 50.0, 25.0, 0.5, help="Network latency to central controller.")
        pkt = st.slider("Packet Loss (%)", 0.0, 5.0, 2.5, 0.1, help="Data packet loss rate over 6G network.")
        dfr = st.slider("Defect Rate (%)", 0.0, 10.0, 5.0, 0.1, help="Measured quality control defect rate.")
    with c3:
        spd = st.slider("Production Speed", 50.0, 500.0, 275.0, 5.0, help="Units produced per hour.")
        mnt = st.slider("Maintenance Score", 0.0, 1.0, 0.5, 0.01, help="AI-derived predictive maintenance health score (1.0 is healthy).")
        err = st.slider("Error Rate (%)", 0.0, 15.0, 7.5, 0.1, help="Operational error rate.")
    mode = st.selectbox("Operation Mode", ["Active", "Idle", "Maintenance"], help="Current factory state of the machine.")
    if st.button("Evaluate Efficiency Status", use_container_width=True, type="primary"):
        from datetime import datetime; now = datetime.now()
        feat = {"Temperature_C": temp, "Vibration_Hz": vib, "Power_Consumption_kW": pwr,
                "Network_Latency_ms": lat, "Packet_Loss_%": pkt, "Quality_Control_Defect_Rate_%": dfr,
                "Production_Speed_units_per_hr": spd, "Predictive_Maintenance_Score": mnt, "Error_Rate_%": err,
                "hour": now.hour, "day_of_week": now.weekday(),
                "Mode_Active": int(mode=="Active"), "Mode_Idle": int(mode=="Idle"), "Mode_Maintenance": int(mode=="Maintenance")}
        feat = compute_engineered(feat)
        st.markdown("---")
        predict_and_display(feat)

with tab2:
    st.markdown('<div class="section-header">Historical Record Validation</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; font-size:0.9rem;'>Select a row index from the dataset to test the model's prediction against the recorded ground truth.</p>", unsafe_allow_html=True)
    row_idx = st.number_input("Record Index ID", 0, len(df)-1, 0, step=1)
    st.dataframe(df.iloc[[row_idx]], use_container_width=True, hide_index=True)
    if st.button("Evaluate Selected Record", use_container_width=True, type="primary"):
        row = df.iloc[row_idx]
        feat = {"Temperature_C": row["Temperature_C"], "Vibration_Hz": row["Vibration_Hz"],
                "Power_Consumption_kW": row["Power_Consumption_kW"], "Network_Latency_ms": row["Network_Latency_ms"],
                "Packet_Loss_%": row["Packet_Loss_%"], "Quality_Control_Defect_Rate_%": row["Quality_Control_Defect_Rate_%"],
                "Production_Speed_units_per_hr": row["Production_Speed_units_per_hr"],
                "Predictive_Maintenance_Score": row["Predictive_Maintenance_Score"], "Error_Rate_%": row["Error_Rate_%"],
                "hour": 0, "day_of_week": 0,
                "Mode_Active": int(row["Operation_Mode"]=="Active"), "Mode_Idle": int(row["Operation_Mode"]=="Idle"),
                "Mode_Maintenance": int(row["Operation_Mode"]=="Maintenance")}
        feat = compute_engineered(feat)
        st.markdown("---")
        pc, _ = predict_and_display(feat)
        actual = row["Efficiency_Status"]
        match_color = "#10b981" if pc == actual else "#ef4444"
        st.markdown(f"**Recorded Ground Truth:** {actual} | **System Match:** <span style='color:{match_color}; font-weight:bold;'>{'Verified' if pc==actual else 'Mismatch'}</span>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section-header">Batch Processing</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; font-size:0.9rem;'>Upload a CSV containing raw telemetry data. The system will process all rows and append prediction columns.</p>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload CSV Telemetry File", type="csv")
    if uploaded:
        batch = pd.read_csv(uploaded)
        st.dataframe(batch.head(), use_container_width=True)
        if st.button("Execute Batch Processing", use_container_width=True, type="primary"):
            records = []
            for _, row in batch.iterrows():
                feat = {f: float(row.get(f, 0)) for f in ["Temperature_C","Vibration_Hz","Power_Consumption_kW",
                        "Network_Latency_ms","Packet_Loss_%","Quality_Control_Defect_Rate_%",
                        "Production_Speed_units_per_hr","Predictive_Maintenance_Score","Error_Rate_%"]}
                feat["hour"] = 0.0; feat["day_of_week"] = 0.0
                feat["Mode_Active"] = float(row.get("Operation_Mode","")=="Active")
                feat["Mode_Idle"] = float(row.get("Operation_Mode","")=="Idle")
                feat["Mode_Maintenance"] = float(row.get("Operation_Mode","")=="Maintenance")
                feat = compute_engineered(feat)
                records.append(feat)
            with st.spinner("Sending batch to Prediction API..."):
                try:
                    response = requests.post(f"{API_URL}/predict_batch", json={"records": records}, timeout=30)
                    response.raise_for_status()
                    api_results = response.json()["results"]
                    res = [{"Predicted_Class": r["prediction"], "Confidence_%": round(r["confidence"]*100, 1)} for r in api_results]
                    rdf = pd.concat([batch, pd.DataFrame(res)], axis=1)
                    st.success(f"Processing complete: {len(rdf)} records evaluated via API.")
                    st.dataframe(rdf, use_container_width=True)
                    st.download_button("Download Processed Results", rdf.to_csv(index=False), "processed_predictions.csv", "text/csv", use_container_width=True)
                except Exception as e:
                    st.error(f"Batch API Error: {e}")
