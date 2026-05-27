"""
Page 5: Automated EDA (Data Explorer)
"""
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Explorer", page_icon="table", layout="wide")

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
</style>
""", unsafe_allow_html=True)

import os

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
        <h1>Automated Data Explorer</h1>
        <p>Univariate Distributions, Bivariate Relationships, and Raw Telemetry Analysis</p>
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
with s1: st.markdown(status_template.format(label="Total Records", color="var(--primary-blue)", status=f"{len(df):,}"), unsafe_allow_html=True)
with s2: st.markdown(status_template.format(label="Dimensions", color="var(--primary-blue)", status="14 Vars"), unsafe_allow_html=True)
with s3: st.markdown(status_template.format(label="Data Type", color="var(--vibrant-green)", status="Structured"), unsafe_allow_html=True)
with s4: st.markdown(status_template.format(label="Update Mode", color="var(--vibrant-green)", status="Static CSV"), unsafe_allow_html=True)

st.markdown("""
<div class="guidance-text">
    Perform raw Exploratory Data Analysis (EDA) on the underlying telemetry dataset. Use this module to visualize raw correlations, distributions, and univariate trends without AI augmentation.
</div>
""", unsafe_allow_html=True)


# ─── Raw Data Viewer ───
st.markdown('<div class="section-header">Raw Telemetry Viewer</div>', unsafe_allow_html=True)
st.dataframe(df.head(100), use_container_width=True)

# ─── Variable Distributions ───
st.markdown('<div class="section-header">Univariate Distributions</div>', unsafe_allow_html=True)
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
if "Machine_ID" in numeric_cols: numeric_cols.remove("Machine_ID")

c1, c2 = st.columns([1, 3])
with c1:
    dist_col = st.selectbox("Select Target Metric", numeric_cols)
    color_by = st.selectbox("Color Distribution By", ["None", "Efficiency_Status", "Operation_Mode"])
with c2:
    fig_dist = px.histogram(df, x=dist_col, color=None if color_by == "None" else color_by,
                            marginal="box", nbins=50, 
                            color_discrete_map={"High": "#3fb950", "Medium": "#d29922", "Low": "#f85149"} if color_by == "Efficiency_Status" else None)
    fig_dist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#8b949e"),
                           height=400, margin=dict(t=20, b=20, l=20, r=20), xaxis=dict(gridcolor="#30363d"), yaxis=dict(gridcolor="#30363d"))
    st.plotly_chart(fig_dist, use_container_width=True)

# ─── Bivariate Relationships ───
st.markdown('<div class="section-header">Bivariate Relationships (Scatter)</div>', unsafe_allow_html=True)
sc1, sc2, sc3 = st.columns(3)
with sc1: x_col = st.selectbox("X-Axis Metric", numeric_cols, index=0)
with sc2: y_col = st.selectbox("Y-Axis Metric", numeric_cols, index=1)
with sc3: c_col = st.selectbox("Color By", ["Efficiency_Status", "Operation_Mode"])

# Sample for performance
sample_df = df.sample(min(5000, len(df)))
fig_scat = px.scatter(sample_df, x=x_col, y=y_col, color=c_col, opacity=0.6,
                      color_discrete_map={"High": "#3fb950", "Medium": "#d29922", "Low": "#f85149"} if c_col == "Efficiency_Status" else None)
fig_scat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#8b949e"),
                       height=500, margin=dict(t=20, b=20, l=20, r=20), xaxis=dict(gridcolor="#30363d"), yaxis=dict(gridcolor="#30363d"))
st.plotly_chart(fig_scat, use_container_width=True)

# ─── Correlation Matrix ───
st.markdown('<div class="section-header">Global Correlation Matrix (Pearson)</div>', unsafe_allow_html=True)
corr = df[numeric_cols].corr()
fig_corr = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r")
fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#8b949e"),
                       height=600, margin=dict(t=20, b=40, l=20, r=20))
st.plotly_chart(fig_corr, use_container_width=True)
