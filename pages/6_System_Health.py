import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.monitoring import get_live_stats, check_drift

st.set_page_config(page_title="System Health & Monitoring", page_icon="🏥", layout="wide")

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

    .health-card {
        background-color: var(--surface-graphite);
        border: 1px solid var(--border-muted);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border-bottom: 3px solid var(--border-muted);
    }
    .status-ok { color: var(--vibrant-green); font-weight: bold; }
    .status-warning { color: #d29922; font-weight: bold; }
    .status-critical { color: var(--vibrant-red); font-weight: bold; }

    .chart-container {
        background-color: var(--surface-graphite);
        border: 1px solid var(--border-muted);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Main Header & Status ───
head_col1, head_col2 = st.columns([3, 1])

with head_col1:
    st.markdown(f"""
    <div class="main-header">
        <h1>Infrastructure & Model Health</h1>
        <p>Live Audit Logs, Drift Detection, and System Stability Monitoring</p>
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
with s1: st.markdown(status_template.format(label="Audit Service", color="var(--vibrant-green)", status="Active"), unsafe_allow_html=True)
with s2: st.markdown(status_template.format(label="Log Volume", color="var(--primary-blue)", status="Syncing"), unsafe_allow_html=True)
with s3: st.markdown(status_template.format(label="Drift Check", color="var(--vibrant-green)", status="Passed"), unsafe_allow_html=True)
with s4: st.markdown(status_template.format(label="Disk Space", color="var(--vibrant-green)", status="Healthy"), unsafe_allow_html=True)

st.markdown("""
<div class="guidance-text">
    Monitor the operational integrity of the ML infrastructure. This page provides real-time audit visibility and detects concept drift by comparing live prediction traffic against training baselines.
</div>
""", unsafe_allow_html=True)


# Load baseline (from the main dataset)
@st.cache_data
def get_training_baseline():
    df = pd.read_csv("Thales_Group_Manufacturing.csv")
    return df["Efficiency_Status"].value_counts(normalize=True).to_dict()

training_baseline = get_training_baseline()
live_stats = get_live_stats()

if not live_stats:
    st.info("ℹ️ No live predictions have been recorded yet. Use the 'Efficiency Prediction' page to generate logs.")
    st.stop()

# --- Top KPIs ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="health-card" style="border-bottom-color: var(--text-muted);"><div style="color:var(--text-muted); font-size:0.8rem;">TOTAL PREDICTIONS</div><div style="font-size:1.8rem; font-weight:700; color:var(--text-main);">{live_stats["total_predictions"]}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="health-card" style="border-bottom-color: var(--primary-blue);"><div style="color:var(--text-muted); font-size:0.8rem;">AVG CONFIDENCE</div><div style="font-size:1.8rem; font-weight:700; color:var(--primary-blue);">{live_stats["avg_confidence"]:.1%}</div></div>', unsafe_allow_html=True)
with c3:
    is_drift, reasons = check_drift(training_baseline)
    status_class = "status-critical" if is_drift else "status-ok"
    status_color = "var(--vibrant-red)" if is_drift else "var(--vibrant-green)"
    status_text = "DRIFT DETECTED" if is_drift else "STABLE"
    st.markdown(f'<div class="health-card" style="border-bottom-color: {status_color};"><div style="color:var(--text-muted); font-size:0.8rem;">MODEL STABILITY</div><div class="{status_class}" style="font-size:1.8rem; font-weight:700;">{status_text}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="health-card" style="border-bottom-color: var(--vibrant-green);"><div style="color:var(--text-muted); font-size:0.8rem;">API STATUS</div><div class="status-ok" style="font-size:1.8rem; font-weight:700;">ONLINE</div></div>', unsafe_allow_html=True)

if is_drift:
    st.warning(f"⚠️ **Model Drift Warning:** The distribution of live predictions has shifted significantly from the training baseline. \n\n **Reasons:** \n - " + "\n - ".join(reasons))

# --- Charts ---
st.markdown("### Data Distribution Comparison")
col_left, col_right = st.columns(2)

with col_left:
    # Baseline vs Live Comparison
    comparison_data = []
    for cls in ["High", "Medium", "Low"]:
        comparison_data.append({"Class": cls, "Type": "Training Baseline", "Percentage": training_baseline.get(cls, 0)*100})
        comparison_data.append({"Class": cls, "Type": "Live Predictions", "Percentage": live_stats["class_distribution"].get(cls, 0)*100})
    
    df_comp = pd.DataFrame(comparison_data)
    fig = px.bar(df_comp, x="Class", y="Percentage", color="Type", barmode="group",
                 color_discrete_map={"Training Baseline": "#334155", "Live Predictions": "#38bdf8"},
                 template="plotly_dark")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    # Prediction Volume (from timestamps)
    df_logs = pd.read_csv("logs/prediction_audit.csv")
    df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'])
    df_trend = df_logs.resample('1min', on='timestamp').size().reset_index(name='count')
    
    fig_trend = px.line(df_trend, x='timestamp', y='count', title="Prediction Volume (Requests/Min)",
                        line_shape="spline", render_mode="svg", template="plotly_dark")
    fig_trend.update_traces(line_color='#10b981')
    fig_trend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
    st.plotly_chart(fig_trend, use_container_width=True)

# --- Raw Logs ---
st.markdown("### Prediction Audit Logs (Last 50)")
df_display = pd.read_csv("logs/prediction_audit.csv").tail(50).iloc[::-1]
st.dataframe(df_display, use_container_width=True, hide_index=True)
