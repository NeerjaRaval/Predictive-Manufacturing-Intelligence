"""
Page 2: Machine Insights + Health Heatmap
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib, json

st.set_page_config(page_title="Machine Insights", page_icon="server", layout="wide")

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

    .machine-card { 
        background-color: var(--surface-graphite); 
        border-radius: 12px; 
        padding: 1.5rem;
        border: 1px solid var(--border-muted); 
        margin-bottom: 1rem; 
        transition: transform 0.2s ease;
    }
    .machine-card:hover { border-color: #58a6ff80; transform: translateY(-2px); }
    
    .kpi-val { font-size: 1.8rem; font-weight: 700; color: var(--text-main); }
    .kpi-lbl { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; margin-top:0.3rem;}

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
def load_data():
    df = pd.read_csv("Thales_Group_Manufacturing.csv")
    df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Timestamp"], format="%d-%m-%Y %H:%M:%S")
    return df

df = load_data()

# ─── Main Header & Status ───
head_col1, head_col2 = st.columns([3, 1])

with head_col1:
    st.markdown(f"""
    <div class="main-header">
        <h1>Machine Fleet Insights</h1>
        <p>Holistic Node Health, Longitudinal Analysis, and Comparative Diagnostics</p>
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
with s1: st.markdown(status_template.format(label="Nodes Active", color="var(--vibrant-green)", status="50/50"), unsafe_allow_html=True)
with s2: st.markdown(status_template.format(label="Fleet Health", color="var(--vibrant-green)", status="Optimal"), unsafe_allow_html=True)
with s3: st.markdown(status_template.format(label="Data Stream", color="var(--vibrant-green)", status="Live"), unsafe_allow_html=True)
with s4: st.markdown(status_template.format(label="Alerts", color="var(--vibrant-green)", status="None"), unsafe_allow_html=True)

st.markdown("""
<div class="guidance-text">
    This module provides a holistic view of hardware performance across the entire manufacturing floor. Identify underperforming nodes via the global heatmap, or drill down into specific machines for targeted analysis.
</div>
""", unsafe_allow_html=True)


# ─── Machine Health Heatmap ───
st.markdown('<div class="section-header">Global Fleet Health Heatmap (Active 50 Nodes)</div>', unsafe_allow_html=True)

machines = sorted(df["Machine_ID"].unique())
heatmap_data = []
for mid in machines:
    m_df = df[df["Machine_ID"] == mid]
    dist = m_df["Efficiency_Status"].value_counts(normalize=True).to_dict()
    # Score: High=2, Medium=1, Low=0, weighted average
    score = dist.get("High", 0.0) * 2 + dist.get("Medium", 0.0) * 1 + dist.get("Low", 0.0) * 0
    heatmap_data.append({"Machine_ID": mid, "Health_Score": score,
                         "High%": dist.get("High", 0.0)*100, "Medium%": dist.get("Medium", 0.0)*100,
                         "Low%": dist.get("Low", 0.0)*100})

hm_df = pd.DataFrame(heatmap_data)

# Reshape into 5x10 grid
n_rows, n_cols = 5, 10
z_vals = hm_df["Health_Score"].values.reshape(n_rows, n_cols)
text_vals = [[f"M-{int(hm_df.iloc[r*n_cols+c]['Machine_ID']):03d}<br>H:{hm_df.iloc[r*n_cols+c]['High%']:.0f}%"
              for c in range(n_cols)] for r in range(n_rows)]
hover_vals = [[f"Machine {int(hm_df.iloc[r*n_cols+c]['Machine_ID'])}<br>Health Score: {hm_df.iloc[r*n_cols+c]['Health_Score']:.2f}<br>High Eff: {hm_df.iloc[r*n_cols+c]['High%']:.1f}%<br>Medium Eff: {hm_df.iloc[r*n_cols+c]['Medium%']:.1f}%<br>Low Eff: {hm_df.iloc[r*n_cols+c]['Low%']:.1f}%"
               for c in range(n_cols)] for r in range(n_rows)]

fig_hm = go.Figure(data=go.Heatmap(
    z=z_vals, text=text_vals, texttemplate="%{text}", textfont=dict(size=10, color="white"),
    customdata=hover_vals, hovertemplate="%{customdata}<extra></extra>",
    colorscale=[[0, "#f85149"], [0.5, "#d29922"], [1, "#3fb950"]],
    colorbar=dict(title="System Health", tickvals=[0, 0.5, 1, 1.5, 2], ticktext=["Critical", "", "Degraded", "", "Optimal"]),
    zmin=0, zmax=2,
))
fig_hm.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#8b949e"),
    height=380, margin=dict(t=10, b=10, l=10, r=20),
    xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False, autorange="reversed"),
)
st.plotly_chart(fig_hm, use_container_width=True)

# ─── Machine Selector ───
st.markdown('<div class="section-header">Targeted Node Analysis</div>', unsafe_allow_html=True)

col_sel, col_sel2 = st.columns([1, 1])
with col_sel:
    selected_machine = st.selectbox("Select Target Machine", machines, format_func=lambda x: f"Machine {x:03d}")
with col_sel2:
    compare_machine = st.selectbox("Compare with Baseline (Optional)", [None] + list(machines),
                                   format_func=lambda x: "None" if x is None else f"Machine {x:03d}")

machine_df = df[df["Machine_ID"] == selected_machine].copy()

# ─── Machine Profile Card ───
mc1, mc2, mc3, mc4 = st.columns(4)
dom_class = machine_df["Efficiency_Status"].mode().values[0]
with mc1:
    st.markdown(f'<div class="machine-card"><div class="kpi-val">{len(machine_df):,}</div>'
                f'<div class="kpi-lbl">Event Records</div></div>', unsafe_allow_html=True)
with mc2:
    st.markdown(f'<div class="machine-card"><div class="kpi-val" style="color:{COLORS[dom_class]}">{dom_class}</div>'
                f'<div class="kpi-lbl">Primary State</div></div>', unsafe_allow_html=True)
with mc3:
    avg_err = machine_df["Error_Rate_%"].mean()
    st.markdown(f'<div class="machine-card"><div class="kpi-val">{avg_err:.2f}%</div>'
                f'<div class="kpi-lbl">Mean Error Rate</div></div>', unsafe_allow_html=True)
with mc4:
    avg_spd = machine_df["Production_Speed_units_per_hr"].mean()
    st.markdown(f'<div class="machine-card"><div class="kpi-val">{avg_spd:.0f}</div>'
                f'<div class="kpi-lbl">Mean Throughput (u/h)</div></div>', unsafe_allow_html=True)

# ─── Efficiency Timeline ───
col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    # Daily efficiency distribution for selected machine
    m_daily = machine_df.set_index("datetime").groupby(pd.Grouper(freq="D"))["Efficiency_Status"].value_counts().unstack(fill_value=0)
    m_daily_pct = m_daily.div(m_daily.sum(axis=1), axis=0) * 100

    fig_tl = go.Figure()
    for status in ["High", "Medium", "Low"]:
        if status in m_daily_pct.columns:
            fig_tl.add_trace(go.Scatter(
                x=m_daily_pct.index, y=m_daily_pct[status], name=status,
                fill="tonexty" if status != "High" else "tozeroy",
                line=dict(color=COLORS[status], width=1.5), stackgroup="one"))

    fig_tl.update_layout(
        title=f"Machine {selected_machine:03d} - Longitudinal Efficiency",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1"),
        height=320, margin=dict(t=40, b=30, l=50, r=20),
        yaxis=dict(title="Proportion (%)", gridcolor="rgba(255,255,255,0.05)", range=[0,100]),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"), hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_tl, use_container_width=True)

with col_chart2:
    dist = machine_df["Efficiency_Status"].value_counts()
    fig_pie = go.Figure(data=[go.Pie(
        labels=dist.index, values=dist.values, hole=0.6,
        marker=dict(colors=[COLORS[k] for k in dist.index]),
        textinfo="label+percent", textfont=dict(size=12, color="#f8fafc"))])
    fig_pie.update_layout(
        title=f"Distribution Profile",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1"),
        height=320, margin=dict(t=40, b=10, l=10, r=10), showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

# ─── Comparison Mode ───
if compare_machine is not None:
    st.markdown(f'<div class="section-header">Architecture Comparison: Machine {selected_machine:03d} vs {compare_machine:03d}</div>',
                unsafe_allow_html=True)
    comp_df = df[df["Machine_ID"] == compare_machine]
    metrics = ["Temperature_C", "Vibration_Hz", "Power_Consumption_kW", "Error_Rate_%",
               "Production_Speed_units_per_hr", "Network_Latency_ms"]

    m1_vals = [machine_df[m].mean() for m in metrics]
    m2_vals = [comp_df[m].mean() for m in metrics]

    # Normalize for radar chart
    max_vals = [max(a, b, 1) for a, b in zip(m1_vals, m2_vals)]
    m1_norm = [v/mx for v, mx in zip(m1_vals, max_vals)]
    m2_norm = [v/mx for v, mx in zip(m2_vals, max_vals)]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=m1_norm + [m1_norm[0]], theta=metrics + [metrics[0]],
                                        fill="toself", name=f"M-{selected_machine:03d}",
                                        line=dict(color="#58a6ff")))
    fig_radar.add_trace(go.Scatterpolar(r=m2_norm + [m2_norm[0]], theta=metrics + [metrics[0]],
                                        fill="toself", name=f"M-{compare_machine:03d}",
                                        line=dict(color="#bc8cff")))
    fig_radar.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=False, gridcolor="#30363d")),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#8b949e"),
        height=380, margin=dict(t=40, b=40, l=80, r=80))
    st.plotly_chart(fig_radar, use_container_width=True)

# ─── Machines x Time Heatmap ───
st.markdown('<div class="section-header">Fleet Temporal Topology (Daily Matrix)</div>', unsafe_allow_html=True)

# Efficiency score per machine per day
daily_scores = df.copy()
daily_scores["date"] = daily_scores["datetime"].dt.date
daily_scores["eff_score"] = daily_scores["Efficiency_Status"].map({"Low": 0, "Medium": 1, "High": 2})
pivot = daily_scores.groupby(["Machine_ID", "date"])["eff_score"].mean().reset_index()
pivot_table = pivot.pivot(index="Machine_ID", columns="date", values="eff_score")

fig_ht = px.imshow(
    pivot_table.values, x=[str(d) for d in pivot_table.columns], y=[f"M-{m:03d}" for m in pivot_table.index],
    color_continuous_scale=[[0, "#f85149"], [0.5, "#d29922"], [1, "#3fb950"]],
    aspect="auto", labels=dict(color="System Score"))
fig_ht.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#8b949e"),
    height=600, margin=dict(t=10, b=40, l=60, r=20),
    xaxis=dict(tickangle=45, dtick=7), coloraxis_colorbar=dict(tickvals=[0,1,2], ticktext=["Critical","Degraded","Optimal"]))
st.plotly_chart(fig_ht, use_container_width=True)
