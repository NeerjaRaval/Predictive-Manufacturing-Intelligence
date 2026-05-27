"""
Page 4: Operational Monitoring & What-If Scenario Analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib

st.set_page_config(page_title="Operational Monitoring", page_icon="activity", layout="wide")

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

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-obsidian: #0b0e14;
        --surface-graphite: #161b22;
        --border-muted: #30363d;
        --primary-blue: #58a6ff;
        --vibrant-green: #3fb950;
        --vibrant-orange: #d29922;
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

    .section-header { 
        color: var(--text-main); 
        font-size: 1.1rem; 
        font-weight: 600; 
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem; 
        border-bottom: 1px solid var(--border-muted); 
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

    .kpi-card { 
        background-color: var(--surface-graphite); 
        border-radius: 12px; 
        padding: 1.5rem;
        border: 1px solid var(--border-muted); 
        text-align: center; 
        border-bottom: 3px solid var(--primary-blue);
    }
    .kpi-val { font-size: 2rem; font-weight: 700; color: var(--text-main); }
    .kpi-lbl { color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("Thales_Group_Manufacturing.csv")

@st.cache_resource
def load_model():
    model = joblib.load("models/best_model.pkl")
    scaler = joblib.load("models/scaler.pkl")
    feature_names = joblib.load("models/feature_names.pkl")
    label_mapping = joblib.load("models/label_encoder.pkl")
    return model, scaler, feature_names, label_mapping

df = load_data()
model, scaler, feature_names, label_mapping = load_model()
label_reverse = {v: k for k, v in label_mapping.items()}
COLORS = {"High": "#3fb950", "Medium": "#d29922", "Low": "#f85149"}

st.markdown("# Operational Condition Analytics")
st.markdown("""
<div class="guidance-text">
    Analyze system performance segmented by operational modes and network conditions. Use the What-If Simulator to stress-test specific scenarios.
</div>
""", unsafe_allow_html=True)

# ─── Operational Mode Breakdown ───
st.markdown('<div class="section-header">Efficiency Segmentation by Operational Mode</div>', unsafe_allow_html=True)

mode_eff = pd.crosstab(df["Operation_Mode"], df["Efficiency_Status"], normalize="index") * 100
fig_mode = go.Figure()
for status in ["High", "Medium", "Low"]:
    if status in mode_eff.columns:
        fig_mode.add_trace(go.Bar(
            name=status, x=mode_eff.index, y=mode_eff[status],
            marker_color=COLORS[status], text=mode_eff[status].apply(lambda x: f"{x:.1f}%"),
            textposition="auto", textfont=dict(size=11, color="white")))

fig_mode.update_layout(
    barmode="stack", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#8b949e"), height=350, margin=dict(t=20, b=20, l=20, r=20),
    yaxis=dict(title="Percentage (%)", gridcolor="#30363d"),
    xaxis=dict(gridcolor="#30363d"), legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig_mode, use_container_width=True)

# ─── Network vs Sensor Radar ───
st.markdown('<div class="section-header">IT/OT Impact Framework</div>', unsafe_allow_html=True)
c1, c2 = st.columns([1, 2])

with c1:
    st.markdown("<p style='color:#94a3b8; font-size:0.9rem;'>Compare the relative instability of IT network metrics versus OT sensor metrics across efficiency classes. Values are normalized.</p>", unsafe_allow_html=True)
    sel_class = st.selectbox("Select Target Class for Overlay", ["High", "Medium", "Low"])

with c2:
    metrics_it = ["Network_Latency_ms", "Packet_Loss_%"]
    metrics_ot = ["Temperature_C", "Vibration_Hz", "Error_Rate_%", "Quality_Control_Defect_Rate_%"]
    all_m = metrics_it + metrics_ot
    
    df_norm = df.copy()
    for m in all_m: df_norm[m] = df_norm[m] / df_norm[m].max()

    avg_all = df_norm[all_m].mean()
    avg_sel = df_norm[df_norm["Efficiency_Status"] == sel_class][all_m].mean()

    fig_net = go.Figure()
    fig_net.add_trace(go.Scatterpolar(r=avg_all.tolist()+[avg_all.iloc[0]], theta=all_m+[all_m[0]],
                                      fill="toself", name="Fleet Baseline", line=dict(color="#94a3b8")))
    fig_net.add_trace(go.Scatterpolar(r=avg_sel.tolist()+[avg_sel.iloc[0]], theta=all_m+[all_m[0]],
                                      fill="toself", name=f"{sel_class} Average", line=dict(color=COLORS[sel_class])))
    fig_net.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=False, gridcolor="#30363d")),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#8b949e"), height=350, margin=dict(t=30, b=30, l=60, r=60))
    st.plotly_chart(fig_net, use_container_width=True)

# ─── What-If Scenario Analysis ───
st.markdown('<div class="section-header">What-If Stress Test Simulator</div>', unsafe_allow_html=True)
st.markdown("<p style='color:#94a3b8; font-size:0.9rem;'>Adjust fleet-wide parameters by a percentage to simulate the macro impact on efficiency distributions.</p>", unsafe_allow_html=True)

wc1, wc2, wc3 = st.columns(3)
with wc1: lat_shift = st.slider("Network Latency Modifier (%)", -50, 100, 0, 5)
with wc2: err_shift = st.slider("Error Rate Modifier (%)", -50, 100, 0, 5)
with wc3: pwr_shift = st.slider("Power Consumption Modifier (%)", -50, 100, 0, 5)

if st.button("Run Global Simulation", use_container_width=True, type="primary"):
    with st.spinner("Processing scenario parameters across 10,000 synthetic instances..."):
        sim_df = df.sample(min(10000, len(df))).copy()
        
        sim_df["Network_Latency_ms"] *= (1 + lat_shift/100.0)
        sim_df["Error_Rate_%"] *= (1 + err_shift/100.0)
        sim_df["Power_Consumption_kW"] *= (1 + pwr_shift/100.0)

        from src.feature_engineering import engineer_all_features
        from src.preprocessing import encode_features
        sim_df = engineer_all_features(sim_df)
        sim_df, _ = encode_features(sim_df)
        for f in feature_names:
            if f not in sim_df.columns: sim_df[f] = 0

        X_sim = scaler.transform(sim_df[feature_names].values)
        preds = model.predict(X_sim)
        pred_labels = [label_reverse[p] for p in preds]

        orig_dist = df["Efficiency_Status"].value_counts(normalize=True) * 100
        sim_dist = pd.Series(pred_labels).value_counts(normalize=True) * 100

        rc1, rc2, rc3 = st.columns(3)
        for state in ["High", "Medium", "Low"]:
            o_val = orig_dist.get(state, 0)
            s_val = sim_dist.get(state, 0)
            delta = s_val - o_val
            color = "#3fb950" if (state=="High" and delta>0) or (state=="Low" and delta<0) else "#f85149"
            with (rc1 if state=="High" else rc2 if state=="Medium" else rc3):
                st.markdown(f"""
                <div class="kpi-card" style="border-bottom-color: {color};">
                    <div class="kpi-val">{s_val:.1f}%</div>
                    <div class="kpi-lbl">Projected {state}</div>
                    <div style="color:{color}; font-size:0.9rem; font-weight:600;">{'+' if delta>0 else ''}{delta:.1f}% vs Baseline</div>
                </div>
                """, unsafe_allow_html=True)
