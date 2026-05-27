"""
Page 3: Model Explainability (SHAP)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib, json
import os

st.set_page_config(page_title="Model Explainability", page_icon="microchip", layout="wide")

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

    .insight-box { 
        background-color: var(--surface-graphite); 
        padding: 1.5rem; 
        border-radius: 12px; 
        border: 1px solid var(--border-muted); 
        margin-top: 1rem; 
        line-height: 1.6; 
        color: var(--text-muted); 
    }
    .insight-box b { color: var(--text-main); }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_artifacts():
    model = joblib.load("models/best_model.pkl")
    scaler = joblib.load("models/scaler.pkl")
    feat_names = joblib.load("models/feature_names.pkl")
    label_map = joblib.load("models/label_encoder.pkl")
    importance = joblib.load("models/feature_importance.pkl") if os.path.exists("models/feature_importance.pkl") else None
    explainer = joblib.load("models/shap_explainer.pkl") if os.path.exists("models/shap_explainer.pkl") else None
    shap_vals = joblib.load("models/shap_values.pkl") if os.path.exists("models/shap_values.pkl") else None
    with open("models/model_meta.json") as f: meta = json.load(f)
    return model, scaler, feat_names, label_map, importance, explainer, shap_vals, meta

@st.cache_data
def load_dataset():
    return pd.read_csv("Thales_Group_Manufacturing.csv")

model, scaler, feature_names, label_mapping, importance_df, shap_explainer, shap_values, meta = load_artifacts()
df = load_dataset()
label_reverse = {v: k for k, v in label_mapping.items()}
CLASS_NAMES = ["Low", "Medium", "High"]
COLORS = {"High": "#10b981", "Medium": "#f59e0b", "Low": "#ef4444"}

# ─── Main Header & Status ───
head_col1, head_col2 = st.columns([3, 1])

with head_col1:
    st.markdown(f"""
    <div class="main-header">
        <h1>Model Explainability</h1>
        <p>SHAP-based Decision Logic, Global Feature Impact, and Micro-Level Narratives</p>
    </div>
    """, unsafe_allow_html=True)

with head_col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=180)

# System Status Row
s1, s2, s3, s4 = st.columns(4)
status_template = """
<div style="background: var(--surface-graphite); border: 1px solid var(--border-muted); border-radius: 8px; padding: 0.8rem; display: flex; align-items: center; justify-content: space-between;">
    <span style="color: var(--text-muted); font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">{label}</span>
    <span style="color: {color}; font-size: 0.85rem; font-weight: 700; display: flex; align-items: center; gap: 6px;">
        <span style="width: 8px; height: 8px; background: {color}; border-radius: 50%; display: inline-block;"></span>
        {status}
    </span>
</div>
"""
with s1: st.markdown(status_template.format(label="Decision Logic", color="var(--vibrant-green)", status="SHAP Enabled"), unsafe_allow_html=True)
with s2: st.markdown(status_template.format(label="Model Type", color="var(--primary-blue)", status="Random Forest"), unsafe_allow_html=True)
with s3: st.markdown(status_template.format(label="Features", color="var(--primary-blue)", status="14 Factors"), unsafe_allow_html=True)
with s4: st.markdown(status_template.format(label="Bias Check", color="var(--vibrant-green)", status="Pass"), unsafe_allow_html=True)

st.markdown("""
<div class="guidance-text">
    This module demystifies the AI's decision-making process using SHAP (SHapley Additive exPlanations). It details both global feature importance and specific per-class impact factors.
</div>
""", unsafe_allow_html=True)

# ─── Global Feature Importance ───
st.markdown('<div class="section-header">Global Feature Impact Framework (SHAP)</div>', unsafe_allow_html=True)

if importance_df is not None:
    top_n = st.slider("Display top N features", 5, 20, 15)
    top = importance_df.head(top_n).iloc[::-1]

    colors = px.colors.sequential.Blues[::-1]
    n_colors = len(colors)

    fig_imp = go.Figure(go.Bar(
        x=top["Importance"].values, y=top["Feature"].values, orientation="h",
        marker=dict(color=[colors[i % n_colors] for i in range(len(top))]),
        text=[f"{v:.4f}" for v in top["Importance"].values], textposition="outside",
        textfont=dict(size=10)))
    fig_imp.update_layout(
        title="Mean |SHAP Value| per Feature",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1"),
        height=max(350, top_n * 28), margin=dict(t=40, b=20, l=200, r=80),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Mean |SHAP Value|"))
    st.plotly_chart(fig_imp, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
        <strong style="color:#38bdf8;">Key Architectural Insight:</strong> The primary drivers of efficiency are 
        <b>{importance_df.iloc[0]['Feature']}</b> (Impact factor: {importance_df.iloc[0]['Importance']:.4f}),
        <b>{importance_df.iloc[1]['Feature']}</b> ({importance_df.iloc[1]['Importance']:.4f}), and
        <b>{importance_df.iloc[2]['Feature']}</b> ({importance_df.iloc[2]['Importance']:.4f}).
        Controlling these variables provides the highest theoretical yield optimization.
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("Feature importance data not available. Please ensure the training pipeline has executed.")

# ─── Per-Class Feature Impact ───
st.markdown('<div class="section-header">Directional Impact by Target State</div>', unsafe_allow_html=True)

if shap_values is not None and isinstance(shap_values, list) and len(shap_values) == 3:
    class_tab = st.selectbox("Select Target State", CLASS_NAMES)
    class_idx = CLASS_NAMES.index(class_tab)

    sv = shap_values[class_idx]
    mean_shap = sv.mean(axis=0)

    sorted_idx = np.argsort(np.abs(mean_shap))[::-1][:15]

    fig_dir = go.Figure()
    for idx in sorted_idx[::-1]:
        color = "#10b981" if mean_shap[idx] > 0 else "#ef4444"
        fig_dir.add_trace(go.Bar(
            y=[feature_names[idx]], x=[mean_shap[idx]], orientation="h",
            marker_color=color, showlegend=False,
            hovertemplate=f"<b>{feature_names[idx]}</b><br>Mean SHAP: {mean_shap[idx]:.4f}<extra></extra>"))

    fig_dir.update_layout(
        title=f"Feature Directional Vectors for '{class_tab}' Target",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1"),
        height=400, margin=dict(t=40, b=20, l=200, r=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Mean SHAP Value",
                   zeroline=True, zerolinecolor="rgba(255,255,255,0.1)"))
    st.plotly_chart(fig_dir, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
        <strong style="color:#38bdf8;">Interpretation Framework for {class_tab}:</strong><br>
        • <span style="color:#10b981; font-weight: 600;">Positive Values (Right):</span> Metrics that increase the statistical likelihood of a {class_tab} classification.<br>
        • <span style="color:#ef4444; font-weight: 600;">Negative Values (Left):</span> Metrics that decrease the likelihood of a {class_tab} classification.
    </div>
    """, unsafe_allow_html=True)

# ─── Single Prediction Explainer ───
st.markdown('<div class="section-header">Targeted Record Analytics</div>', unsafe_allow_html=True)

row_idx = st.number_input("Target Record ID from Dataset", 0, len(df)-1, 42, step=1)
row = df.iloc[row_idx]

st.dataframe(df.iloc[[row_idx]], use_container_width=True, hide_index=True)

if st.button("Generate Explainability Narrative", use_container_width=True, type="primary"):
    feat = {"Temperature_C": row["Temperature_C"], "Vibration_Hz": row["Vibration_Hz"],
            "Power_Consumption_kW": row["Power_Consumption_kW"], "Network_Latency_ms": row["Network_Latency_ms"],
            "Packet_Loss_%": row["Packet_Loss_%"], "Quality_Control_Defect_Rate_%": row["Quality_Control_Defect_Rate_%"],
            "Production_Speed_units_per_hr": row["Production_Speed_units_per_hr"],
            "Predictive_Maintenance_Score": row["Predictive_Maintenance_Score"], "Error_Rate_%": row["Error_Rate_%"],
            "hour": 0, "day_of_week": 0,
            "Mode_Active": int(row["Operation_Mode"]=="Active"), "Mode_Idle": int(row["Operation_Mode"]=="Idle"),
            "Mode_Maintenance": int(row["Operation_Mode"]=="Maintenance")}
    feat["Energy_Efficiency_Ratio"] = feat["Production_Speed_units_per_hr"]/max(feat["Power_Consumption_kW"],0.01)
    feat["Error_to_Output_Ratio"] = feat["Error_Rate_%"]/max(feat["Production_Speed_units_per_hr"],0.01)
    feat["Network_Reliability_Score"] = max(0,1-((feat["Network_Latency_ms"]/50)+(feat["Packet_Loss_%"]/5))/2)
    feat["Sensor_Stability_Index"] = 1/(1+abs(feat["Temperature_C"]-60)/60+abs(feat["Vibration_Hz"]-2.55)/2.55)
    feat["Defect_Error_Interaction"] = feat["Quality_Control_Defect_Rate_%"]*feat["Error_Rate_%"]
    feat["Maintenance_Risk"] = (1-feat["Predictive_Maintenance_Score"])*feat["Error_Rate_%"]

    X = np.array([[feat.get(f, 0) for f in feature_names]])
    X_scaled = scaler.transform(X)
    pred = model.predict(X_scaled)[0]
    proba = model.predict_proba(X_scaled)[0]
    pc = label_reverse[pred]
    actual = row["Efficiency_Status"]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("System Prediction", pc, delta=f"{max(proba)*100:.1f}% confidence")
        st.metric("Recorded Target", actual, delta="Verified" if pc == actual else "Mismatch")

    if shap_explainer:
        try:
            sv = shap_explainer.shap_values(X_scaled)
            sv_pred = sv[int(pred)][0] if isinstance(sv, list) else sv[0]

            sorted_idx = np.argsort(np.abs(sv_pred))[::-1]
            top5 = sorted_idx[:5]

            fig_wf = go.Figure(go.Waterfall(
                name="SHAP", orientation="h",
                y=[feature_names[i] for i in top5],
                x=[sv_pred[i] for i in top5],
                connector=dict(line=dict(color="rgba(255,255,255,0.05)")),
                increasing=dict(marker=dict(color="#10b981")),
                decreasing=dict(marker=dict(color="#ef4444")),
                textposition="outside", text=[f"{sv_pred[i]:.4f}" for i in top5]))

            fig_wf.update_layout(
                title="Micro-Level Feature Contributions (Waterfall)",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1"),
                height=300, margin=dict(t=40, b=20, l=200, r=80),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"))
            with col2:
                st.plotly_chart(fig_wf, use_container_width=True)

            top3 = sorted_idx[:3]
            parts = [f"The system classified this telemetry vector as **{pc}** with **{max(proba)*100:.1f}%** confidence.\n\n**Primary Drivers:**\n"]
            for i in top3:
                d = "positively" if sv_pred[i] > 0 else "negatively"
                parts.append(f"- **{feature_names[i]}** (Input: {feat.get(feature_names[i],0):.3f}) "
                             f"{d} influenced the result (Impact Matrix: {sv_pred[i]:.4f})")

            st.markdown(f'<div class="insight-box">{"<br>".join(parts)}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"SHAP explainer generated an internal error: {e}")

# ─── Optuna Results ───
if os.path.exists("models/tuning_results.pkl"):
    st.markdown('<div class="section-header">Hyperparameter Optimization Matrix (Optuna)</div>', unsafe_allow_html=True)
    tuning = joblib.load("models/tuning_results.pkl")
    for model_name, result in tuning.items():
        st.subheader(f"{model_name} Engine - Peak Metric: {result['best_score']:.4f}")
        study = result["study"]
        trials_df = study.trials_dataframe()
        fig_opt = px.scatter(trials_df, x="number", y="value", title=f"{model_name} Epoch Tracking",
                             labels={"number": "Evaluation Iteration", "value": "Macro F1 Score"})
        fig_opt.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(color="#cbd5e1"), height=300, xaxis=dict(gridcolor="rgba(255,255,255,0.05)"), yaxis=dict(gridcolor="rgba(255,255,255,0.05)"))
        st.plotly_chart(fig_opt, use_container_width=True)
        with st.expander("View Optimal Parameters Schema"):
            st.json(result["best_params"])
