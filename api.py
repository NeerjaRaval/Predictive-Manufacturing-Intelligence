"""
Predictive Manufacturing Intelligence - Backend API
====================================================
Project Structure:
  /api/kpis               -> Dashboard KPI summary (OEE, Alerts, Predicted Failures, AI Health Score)
  /api/charts/production  -> Daily production trends, OEE, downtime breakdown
  /api/machines           -> All machine telemetry averages and status
  /api/machines/{id}      -> Individual machine detailed telemetry
  /api/alerts             -> Threshold-based anomaly alerts
  /api/maintenance        -> Predictive maintenance queue
  /api/energy             -> Energy & power consumption analytics
  /api/copilot            -> Local Free AI analyst for CSV Q&A
  /api/settings           -> Active model & alert threshold config
  /health                 -> Health check
  /predict                -> Single ML prediction (existing)
  /predict_batch          -> Batch ML prediction (existing)
"""

import joblib
import json
import numpy as np
import os
import csv
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# ─────────────────────────────────────────────
# App Initialization
# ─────────────────────────────────────────────
app = FastAPI(
    title="Predictive Manufacturing Intelligence API",
    description="REST API for real-time manufacturing efficiency predictions, analytics, and local AI copilot",
    version="2.0.0"
)

# Allow Vite dev server and production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:80", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Global Config (Alert Thresholds & Model)
# ─────────────────────────────────────────────
SETTINGS = {
    "active_model": "random_forest",        # random_forest | xgboost | logistic_regression
    "thresholds": {
        "temperature_warning": 78.0,         # °C
        "temperature_critical": 85.0,        # °C
        "vibration_warning": 5.5,            # Hz
        "vibration_critical": 7.5,           # Hz
        "latency_warning": 12.0,             # ms
        "latency_critical": 18.0,            # ms
        "packet_loss_warning": 1.0,          # %
        "packet_loss_critical": 2.5,         # %
        "defect_rate_warning": 5.0,          # %
        "defect_rate_critical": 10.0,        # %
        "maintenance_score_critical": 0.30   # score (lower = worse)
    }
}

# ─────────────────────────────────────────────
# Load CSV Dataset on Startup
# ─────────────────────────────────────────────
CSV_PATH = "Thales_Group_Manufacturing.csv"
df_global: Optional[pd.DataFrame] = None

def load_csv():
    global df_global
    try:
        df = pd.read_csv(CSV_PATH)
        df.columns = [c.strip() for c in df.columns]
        df["Machine_ID"] = pd.to_numeric(df["Machine_ID"], errors="coerce")
        # Parse date
        df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
        df_global = df
        print(f"[API] CSV loaded: {len(df)} rows, {df['Machine_ID'].nunique()} machines.")
    except Exception as e:
        print(f"[API] WARNING: Could not load CSV: {e}")
        df_global = None

load_csv()

# ─────────────────────────────────────────────
# Load ML Models on Startup
# ─────────────────────────────────────────────
MODELS = {}
try:
    MODELS["random_forest"] = joblib.load("models/random_forest.pkl")
    MODELS["xgboost"]       = joblib.load("models/xgboost.pkl")
    MODELS["logistic_regression"] = joblib.load("models/logistic_regression.pkl")
    scaler        = joblib.load("models/scaler.pkl")
    feature_names = joblib.load("models/feature_names.pkl")
    label_mapping = joblib.load("models/label_encoder.pkl")
    label_reverse = {v: k for k, v in label_mapping.items()}
    print("[API] All ML models loaded successfully.")
except Exception as e:
    print(f"[API] WARNING: Could not load some models: {e}")
    scaler = None
    feature_names = []
    label_reverse = {}

# ─────────────────────────────────────────────
# Pydantic Request Models
# ─────────────────────────────────────────────
class FeatureVector(BaseModel):
    features: Dict[str, float]
    model_name: Optional[str] = "random_forest"

class BatchFeatureVector(BaseModel):
    records: List[Dict[str, float]]
    model_name: Optional[str] = "random_forest"

class CopilotQuery(BaseModel):
    query: str

class SettingsUpdate(BaseModel):
    active_model: Optional[str] = None
    thresholds: Optional[Dict[str, float]] = None

# ─────────────────────────────────────────────
# Prediction Logging
# ─────────────────────────────────────────────
LOG_FILE = "logs/prediction_audit.csv"
os.makedirs("logs", exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "predicted_class", "confidence", "machine_id", "model", "input_features"])

def log_prediction(predicted_class: str, confidence: float, features: dict, model_name: str = "random_forest"):
    try:
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                predicted_class,
                round(confidence, 4),
                features.get("Machine_ID", "Unknown"),
                model_name,
                json.dumps(features)
            ])
    except Exception as e:
        print(f"[API] Logging failed: {e}")

# ─────────────────────────────────────────────
# Helper: Get Active Model
# ─────────────────────────────────────────────
def get_active_model():
    model_name = SETTINGS["active_model"]
    if model_name in MODELS:
        return MODELS[model_name], model_name
    if MODELS:
        name = list(MODELS.keys())[0]
        return MODELS[name], name
    return None, None


# ═══════════════════════════════════════════════════════════════
#  API ROUTES
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────
@app.get("/health")
def health_check():
    """Verify that the API, ML models, and CSV dataset are loaded and ready."""
    return {
        "status": "healthy",
        "models_loaded": list(MODELS.keys()),
        "active_model": SETTINGS["active_model"],
        "csv_loaded": df_global is not None,
        "csv_records": len(df_global) if df_global is not None else 0,
        "version": "2.0.0"
    }


# ─────────────────────────────────────────────
# /api/kpis - Dashboard KPI Summary
# ─────────────────────────────────────────────
@app.get("/api/kpis")
def get_kpis():
    """
    Returns the 4 main KPI cards for the Dashboard:
    - OEE (Overall Equipment Effectiveness)
    - Active Alerts (threshold violations)
    - Predicted Failures (low maintenance score machines)
    - AI Health Score
    """
    if df_global is None:
        raise HTTPException(status_code=503, detail="CSV dataset not loaded")

    df = df_global
    T = SETTINGS["thresholds"]

    # --- OEE Calculation ---
    # OEE = Availability × Performance × Quality
    # Proxy from CSV:
    #   Availability  = 1 - (Error_Rate_% / 100)
    #   Performance   = Production_Speed / max_possible (capped at 1)
    #   Quality       = 1 - (Quality_Control_Defect_Rate_% / 100)
    max_speed = df["Production_Speed_units_per_hr"].quantile(0.95)
    availability  = (1 - df["Error_Rate_%"].mean() / 100)
    performance   = min(df["Production_Speed_units_per_hr"].mean() / max_speed, 1.0) if max_speed > 0 else 0
    quality       = (1 - df["Quality_Control_Defect_Rate_%"].mean() / 100)
    oee = round(availability * performance * quality * 100, 1)

    # Week-ago subset for delta
    latest_date = df["Date"].max()
    week_ago = latest_date - pd.Timedelta(days=7)
    df_recent  = df[df["Date"] >= week_ago]
    df_old     = df[df["Date"] < week_ago]

    if len(df_old) > 10:
        avail_old  = (1 - df_old["Error_Rate_%"].mean() / 100)
        perf_old   = min(df_old["Production_Speed_units_per_hr"].mean() / max_speed, 1.0)
        qual_old   = (1 - df_old["Quality_Control_Defect_Rate_%"].mean() / 100)
        oee_old    = avail_old * perf_old * qual_old * 100
        oee_delta  = round(oee - oee_old, 1)
    else:
        oee_delta = 0.0

    # --- Active Alerts ---
    alert_mask = (
        (df["Temperature_C"]              > T["temperature_warning"])  |
        (df["Vibration_Hz"]               > T["vibration_warning"])    |
        (df["Network_Latency_ms"]         > T["latency_warning"])      |
        (df["Packet_Loss_%"]              > T["packet_loss_warning"])   |
        (df["Quality_Control_Defect_Rate_%"] > T["defect_rate_warning"])
    )
    # Count unique machines that have any alert currently (based on their last record)
    last_per_machine = df.sort_values("Date").groupby("Machine_ID").last().reset_index()
    alert_mask_last = (
        (last_per_machine["Temperature_C"]              > T["temperature_warning"])  |
        (last_per_machine["Vibration_Hz"]               > T["vibration_warning"])    |
        (last_per_machine["Network_Latency_ms"]         > T["latency_warning"])      |
        (last_per_machine["Packet_Loss_%"]              > T["packet_loss_warning"])
    )
    active_alerts = int(alert_mask_last.sum())

    # --- Predicted Failures (next 7 days proxy) ---
    # Machines with Predictive_Maintenance_Score < critical threshold
    low_maint = last_per_machine[
        last_per_machine["Predictive_Maintenance_Score"] < T["maintenance_score_critical"]
    ]
    predicted_failures = len(low_maint)

    # --- AI Health Score (composite) ---
    # Weighted average of inverted bad metrics, normalised 0-100
    score_temp   = max(0, 1 - max(0, df["Temperature_C"].mean() - 60) / 40)
    score_vib    = max(0, 1 - df["Vibration_Hz"].mean() / 10)
    score_maint  = df["Predictive_Maintenance_Score"].mean()
    score_err    = max(0, 1 - df["Error_Rate_%"].mean() / 20)
    ai_health    = round((score_temp * 0.25 + score_vib * 0.25 + score_maint * 0.3 + score_err * 0.2) * 100, 0)

    # --- Efficiency Distribution ---
    eff_counts = df["Efficiency_Status"].value_counts(normalize=True).to_dict()

    return {
        "oee": oee,
        "oee_delta": oee_delta,
        "active_alerts": active_alerts,
        "predicted_failures": predicted_failures,
        "ai_health_score": int(ai_health),
        "efficiency_distribution": {
            "high":   round(eff_counts.get("High",   0) * 100, 1),
            "medium": round(eff_counts.get("Medium", 0) * 100, 1),
            "low":    round(eff_counts.get("Low",    0) * 100, 1)
        }
    }


# ─────────────────────────────────────────────
# /api/charts/production - Production Trend Charts
# ─────────────────────────────────────────────
@app.get("/api/charts/production")
def get_production_charts(days: int = 14):
    """
    Returns daily aggregated charts data for production trend,
    OEE trend, failure risk bar, and downtime breakdown (pie).
    Query param: ?days=14
    """
    if df_global is None:
        raise HTTPException(status_code=503, detail="CSV dataset not loaded")

    df = df_global.copy()
    df = df[df["Date"].notna()].sort_values("Date")

    latest = df["Date"].max()
    start  = latest - pd.Timedelta(days=days - 1)
    df_range = df[df["Date"] >= start]

    # --- Daily Production Trend ---
    max_speed   = df["Production_Speed_units_per_hr"].quantile(0.95)
    target_speed = round(max_speed * 0.92, 0)

    daily = df_range.groupby("Date").agg(
        actual_speed=("Production_Speed_units_per_hr", "mean"),
        avg_error=("Error_Rate_%", "mean"),
        avg_defect=("Quality_Control_Defect_Rate_%", "mean"),
    ).reset_index()

    production_trend = []
    for _, row in daily.iterrows():
        production_trend.append({
            "name": row["Date"].strftime("%b %d"),
            "actual": round(row["actual_speed"], 1),
            "target": round(target_speed, 1),
        })

    # --- OEE Trend ---
    oee_trend = []
    for _, row in daily.iterrows():
        avail = max(0, 1 - row["avg_error"] / 100)
        perf  = min(row["actual_speed"] / max_speed, 1.0) if max_speed > 0 else 0
        qual  = max(0, 1 - row["avg_defect"] / 100)
        oee_val = round(avail * perf * qual * 100, 1)
        oee_trend.append({"name": row["Date"].strftime("%b %d"), "value": oee_val})

    # --- Failure Risk Bar (last 7 days per machine) ---
    T = SETTINGS["thresholds"]
    last_per_machine = df.sort_values("Date").groupby("Machine_ID").last().reset_index()
    last_per_machine["risk_score"] = (
        (last_per_machine["Temperature_C"]      / T["temperature_critical"]).clip(0, 1) * 30 +
        (last_per_machine["Vibration_Hz"]        / T["vibration_critical"]).clip(0, 1) * 30 +
        ((1 - last_per_machine["Predictive_Maintenance_Score"])) * 40
    )
    top5 = last_per_machine.nlargest(5, "risk_score")
    failure_risk = []
    for _, row in top5.iterrows():
        risk = int(row["risk_score"])
        color = "var(--status-critical)" if risk > 70 else "var(--status-warning)" if risk > 45 else "var(--primary-neon)"
        failure_risk.append({
            "name": f"M-{int(row['Machine_ID'])}",
            "risk": risk,
            "color": color
        })

    # --- Downtime Reasons Pie (based on Operation Mode + threshold violations) ---
    idle_count    = len(df_range[df_range["Operation_Mode"] == "Idle"])
    temp_fault    = len(df_range[df_range["Temperature_C"] > T["temperature_critical"]])
    vib_fault     = len(df_range[df_range["Vibration_Hz"]  > T["vibration_critical"]])
    net_fault     = len(df_range[df_range["Packet_Loss_%"] > T["packet_loss_critical"]])
    other         = max(0, len(df_range) - idle_count - temp_fault - vib_fault - net_fault)
    total_dt      = idle_count + temp_fault + vib_fault + net_fault + other

    downtime_pie = []
    if total_dt > 0:
        downtime_pie = [
            {"name": "Equipment Failure",  "value": round(temp_fault / total_dt * 100, 1), "color": "var(--status-critical)"},
            {"name": "Idle / Setup",        "value": round(idle_count / total_dt * 100, 1), "color": "var(--primary-neon)"},
            {"name": "Vibration Events",    "value": round(vib_fault  / total_dt * 100, 1), "color": "var(--status-warning)"},
            {"name": "Network Disruption",  "value": round(net_fault  / total_dt * 100, 1), "color": "#bc8cff"},
            {"name": "Other",               "value": round(other      / total_dt * 100, 1), "color": "var(--text-muted)"},
        ]

    return {
        "production_trend": production_trend,
        "oee_trend":         oee_trend,
        "failure_risk":      failure_risk,
        "downtime_pie":      downtime_pie,
        "days_shown":        days
    }


# ─────────────────────────────────────────────
# /api/machines - All Machines List
# ─────────────────────────────────────────────
@app.get("/api/machines")
def get_machines(search: str = "", status: str = "", limit: int = 100, offset: int = 0):
    """
    Returns aggregated telemetry per machine from the CSV dataset.
    Query params: ?search=&status=Healthy|Warning|Critical&limit=100&offset=0
    """
    if df_global is None:
        raise HTTPException(status_code=503, detail="CSV dataset not loaded")

    T = SETTINGS["thresholds"]
    df = df_global
    last_per_machine = df.sort_values("Date").groupby("Machine_ID").last().reset_index()
    avg_per_machine  = df.groupby("Machine_ID").agg(
        avg_temp=("Temperature_C", "mean"),
        avg_vib=("Vibration_Hz", "mean"),
        avg_power=("Power_Consumption_kW", "mean"),
        avg_latency=("Network_Latency_ms", "mean"),
        avg_loss=("Packet_Loss_%", "mean"),
        avg_defect=("Quality_Control_Defect_Rate_%", "mean"),
        avg_speed=("Production_Speed_units_per_hr", "mean"),
        avg_maint=("Predictive_Maintenance_Score", "mean"),
        avg_error=("Error_Rate_%", "mean"),
        total_records=("Machine_ID", "count")
    ).reset_index()

    # Get dominant efficiency status
    eff_per_machine = df.groupby("Machine_ID")["Efficiency_Status"].agg(
        lambda x: x.value_counts().index[0]
    ).reset_index().rename(columns={"Efficiency_Status": "dominant_efficiency"})

    merged = avg_per_machine.merge(eff_per_machine, on="Machine_ID", how="left")
    merged = merged.merge(
        last_per_machine[["Machine_ID", "Operation_Mode", "Temperature_C", "Vibration_Hz", "Predictive_Maintenance_Score"]],
        on="Machine_ID", suffixes=("", "_last")
    )

    machines = []
    for _, row in merged.iterrows():
        machine_id = int(row["Machine_ID"])

        # Health Score 0-100
        h_temp  = max(0, 1 - max(0, row["avg_temp"] - 60) / 40)
        h_vib   = max(0, 1 - row["avg_vib"] / 10)
        h_maint = row["avg_maint"]
        h_err   = max(0, 1 - row["avg_error"] / 20)
        health  = round((h_temp * 0.25 + h_vib * 0.25 + h_maint * 0.3 + h_err * 0.2) * 100)

        # Status
        is_critical = (
            row["Temperature_C"] > T["temperature_critical"] or
            row["Vibration_Hz"]  > T["vibration_critical"] or
            row["avg_maint"]     < T["maintenance_score_critical"]
        )
        is_warning = (
            row["Temperature_C"] > T["temperature_warning"] or
            row["Vibration_Hz"]  > T["vibration_warning"]
        )
        machine_status = "Critical" if is_critical else ("Warning" if is_warning else "Healthy")

        # Apply filters
        if search and search.lower() not in f"machine {machine_id} m-{machine_id}".lower():
            continue
        if status and machine_status.lower() != status.lower():
            continue

        machines.append({
            "id": f"M-{machine_id:02d}",
            "machine_id": machine_id,
            "health": health,
            "status": machine_status,
            "dominant_efficiency": row.get("dominant_efficiency", "Unknown"),
            "operation_mode": row.get("Operation_Mode", "Unknown"),
            "avg_temperature": round(row["avg_temp"], 1),
            "avg_vibration":   round(row["avg_vib"], 2),
            "avg_power":       round(row["avg_power"], 2),
            "avg_latency":     round(row["avg_latency"], 1),
            "avg_packet_loss": round(row["avg_loss"], 2),
            "avg_defect_rate": round(row["avg_defect"], 2),
            "avg_speed":       round(row["avg_speed"], 1),
            "avg_maint_score": round(row["avg_maint"], 3),
            "avg_error_rate":  round(row["avg_error"], 2),
            "total_records":   int(row["total_records"]),
        })

    # Sort: Critical first, Warning second, Healthy last
    status_order = {"Critical": 0, "Warning": 1, "Healthy": 2}
    machines.sort(key=lambda m: status_order.get(m["status"], 3))

    total = len(machines)
    paginated = machines[offset: offset + limit]

    return {
        "machines": paginated,
        "total": total,
        "offset": offset,
        "limit": limit,
        "healthy_count":  sum(1 for m in machines if m["status"] == "Healthy"),
        "warning_count":  sum(1 for m in machines if m["status"] == "Warning"),
        "critical_count": sum(1 for m in machines if m["status"] == "Critical")
    }


# ─────────────────────────────────────────────
# /api/machines/{machine_id} - Individual Machine Detail
# ─────────────────────────────────────────────
@app.get("/api/machines/{machine_id}")
def get_machine_detail(machine_id: int, days: int = 30):
    """
    Returns detailed telemetry, recent trend (line chart), and efficiency breakdown
    for a single machine.
    """
    if df_global is None:
        raise HTTPException(status_code=503, detail="CSV dataset not loaded")

    df_m = df_global[df_global["Machine_ID"] == machine_id].sort_values("Date")
    if len(df_m) == 0:
        raise HTTPException(status_code=404, detail=f"Machine {machine_id} not found in dataset")

    # Averages
    avg = df_m.mean(numeric_only=True).to_dict()

    # Efficiency breakdown
    eff = df_m["Efficiency_Status"].value_counts(normalize=True).to_dict()

    # Recent trend (last N days)
    latest = df_m["Date"].max()
    start  = latest - pd.Timedelta(days=days - 1)
    df_recent = df_m[df_m["Date"] >= start]

    daily_trend = df_recent.groupby("Date").agg(
        temperature=("Temperature_C", "mean"),
        vibration=("Vibration_Hz", "mean"),
        power=("Power_Consumption_kW", "mean"),
        latency=("Network_Latency_ms", "mean"),
        speed=("Production_Speed_units_per_hr", "mean"),
    ).reset_index()

    trend_data = [
        {
            "date": row["Date"].strftime("%b %d"),
            "temperature": round(row["temperature"], 1),
            "vibration":   round(row["vibration"], 2),
            "power":       round(row["power"], 2),
            "latency":     round(row["latency"], 1),
            "speed":       round(row["speed"], 1),
        }
        for _, row in daily_trend.iterrows()
    ]

    return {
        "machine_id": machine_id,
        "label": f"M-{machine_id:02d}",
        "averages": {k: round(v, 3) if isinstance(v, float) else v for k, v in avg.items() if k != "Machine_ID"},
        "efficiency_breakdown": {
            "high":   round(eff.get("High",   0) * 100, 1),
            "medium": round(eff.get("Medium", 0) * 100, 1),
            "low":    round(eff.get("Low",    0) * 100, 1),
        },
        "total_records":  len(df_m),
        "date_range": {
            "from": df_m["Date"].min().strftime("%Y-%m-%d"),
            "to":   df_m["Date"].max().strftime("%Y-%m-%d"),
        },
        "trend": trend_data
    }


# ─────────────────────────────────────────────
# /api/alerts - Threshold-Based Active Alerts
# ─────────────────────────────────────────────
@app.get("/api/alerts")
def get_alerts():
    """
    Returns the list of active threshold-based anomaly alerts
    across all machines based on their latest telemetry records.
    """
    if df_global is None:
        raise HTTPException(status_code=503, detail="CSV dataset not loaded")

    T = SETTINGS["thresholds"]
    df = df_global

    # Get most recent record per machine
    last = df.sort_values("Date").groupby("Machine_ID").last().reset_index()

    alerts = []
    alert_id = 1

    for _, row in last.iterrows():
        machine = f"M-{int(row['Machine_ID']):02d}"
        ts = row["Date"].strftime("%b %d, %Y") if pd.notna(row["Date"]) else "N/A"

        def make_alert(param, value, unit, warning_t, critical_t, category):
            nonlocal alert_id
            if value > critical_t:
                severity, tag = "Critical", "critical"
            elif value > warning_t:
                severity, tag = "Warning", "warning"
            else:
                return None
            a = {
                "id":       f"ALT-{alert_id:03d}",
                "machine":  machine,
                "category": category,
                "message":  f"{param} is {value:.2f}{unit} (threshold: {warning_t}{unit})",
                "severity": severity,
                "tag":      tag,
                "value":    round(value, 2),
                "threshold": warning_t,
                "date":     ts,
                "status":   "Active"
            }
            alert_id += 1
            return a

        a = make_alert("Temperature", row["Temperature_C"], "°C",
                       T["temperature_warning"], T["temperature_critical"], "Thermal")
        if a: alerts.append(a)

        a = make_alert("Vibration", row["Vibration_Hz"], " Hz",
                       T["vibration_warning"], T["vibration_critical"], "Mechanical")
        if a: alerts.append(a)

        a = make_alert("Network Latency", row["Network_Latency_ms"], " ms",
                       T["latency_warning"], T["latency_critical"], "Network")
        if a: alerts.append(a)

        a = make_alert("Packet Loss", row["Packet_Loss_%"], "%",
                       T["packet_loss_warning"], T["packet_loss_critical"], "Network")
        if a: alerts.append(a)

        a = make_alert("QC Defect Rate", row["Quality_Control_Defect_Rate_%"], "%",
                       T["defect_rate_warning"], T["defect_rate_critical"], "Quality")
        if a: alerts.append(a)

    # Sort: Critical first
    alerts.sort(key=lambda a: (0 if a["severity"] == "Critical" else 1))

    return {
        "alerts": alerts,
        "total": len(alerts),
        "critical_count": sum(1 for a in alerts if a["severity"] == "Critical"),
        "warning_count":  sum(1 for a in alerts if a["severity"] == "Warning"),
        "thresholds": T
    }


# ─────────────────────────────────────────────
# /api/maintenance - Predictive Maintenance Queue
# ─────────────────────────────────────────────
@app.get("/api/maintenance")
def get_maintenance():
    """
    Returns a list of machines needing maintenance based on low
    Predictive_Maintenance_Score, high error rates, and high vibration.
    """
    if df_global is None:
        raise HTTPException(status_code=503, detail="CSV dataset not loaded")

    T = SETTINGS["thresholds"]
    df = df_global
    last = df.sort_values("Date").groupby("Machine_ID").last().reset_index()
    avg  = df.groupby("Machine_ID").agg(
        avg_maint=("Predictive_Maintenance_Score", "mean"),
        avg_error=("Error_Rate_%", "mean"),
        avg_vib=("Vibration_Hz", "mean"),
    ).reset_index()
    merged = last.merge(avg, on="Machine_ID")

    tasks = []
    task_types = {
        "low_maint":  ("Replace/Lubricate Components",  "Critical", 1),
        "high_vib":   ("Inspect & Balance Bearings",     "High",     2),
        "high_error": ("Inspect Operational Systems",    "Medium",   3),
    }

    for _, row in merged.iterrows():
        machine = f"M-{int(row['Machine_ID']):02d}"
        score   = row["avg_maint"]
        vib     = row["avg_vib"]
        err     = row["avg_error"]

        if score < T["maintenance_score_critical"]:
            days_until = max(1, int(score * 10))
            tasks.append({
                "id":       f"MNT-{int(row['Machine_ID']):03d}A",
                "machine":  machine,
                "task":     task_types["low_maint"][0],
                "priority": task_types["low_maint"][1],
                "due_days": days_until,
                "score":    round(score, 3),
                "status":   "Pending"
            })
        elif vib > T["vibration_warning"]:
            days_until = max(2, int((T["vibration_critical"] - vib) * 3))
            tasks.append({
                "id":       f"MNT-{int(row['Machine_ID']):03d}B",
                "machine":  machine,
                "task":     task_types["high_vib"][0],
                "priority": task_types["high_vib"][1],
                "due_days": days_until,
                "score":    round(vib, 2),
                "status":   "Pending"
            })
        elif err > 5:
            days_until = max(5, int((20 - err) / 2))
            tasks.append({
                "id":       f"MNT-{int(row['Machine_ID']):03d}C",
                "machine":  machine,
                "task":     task_types["high_error"][0],
                "priority": task_types["high_error"][1],
                "due_days": days_until,
                "score":    round(err, 2),
                "status":   "Pending"
            })

    # Sort by priority then due_days
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    tasks.sort(key=lambda t: (priority_order.get(t["priority"], 9), t["due_days"]))

    return {
        "tasks": tasks,
        "total": len(tasks),
        "critical_count": sum(1 for t in tasks if t["priority"] == "Critical"),
        "high_count":     sum(1 for t in tasks if t["priority"] == "High"),
        "medium_count":   sum(1 for t in tasks if t["priority"] == "Medium"),
    }


# ─────────────────────────────────────────────
# /api/energy - Energy & Power Analytics
# ─────────────────────────────────────────────
@app.get("/api/energy")
def get_energy(days: int = 14):
    """
    Returns power consumption trends, energy efficiency by operation mode,
    and top power-consuming machines.
    """
    if df_global is None:
        raise HTTPException(status_code=503, detail="CSV dataset not loaded")

    df = df_global.copy()
    df = df[df["Date"].notna()].sort_values("Date")
    latest = df["Date"].max()
    start  = latest - pd.Timedelta(days=days - 1)
    df_range = df[df["Date"] >= start]

    # --- Daily Power Trend ---
    daily_power = df_range.groupby("Date").agg(
        avg_power=("Power_Consumption_kW", "mean"),
        max_power=("Power_Consumption_kW", "max"),
    ).reset_index()

    power_trend = [
        {
            "name":      row["Date"].strftime("%b %d"),
            "avg_power": round(row["avg_power"], 2),
            "max_power": round(row["max_power"], 2),
        }
        for _, row in daily_power.iterrows()
    ]

    # --- Energy Efficiency by Operation Mode ---
    mode_energy = df_range.groupby("Operation_Mode").agg(
        avg_power=("Power_Consumption_kW", "mean"),
        avg_speed=("Production_Speed_units_per_hr", "mean"),
    ).reset_index()
    mode_energy["efficiency_ratio"] = mode_energy["avg_speed"] / mode_energy["avg_power"].replace(0, 1)

    energy_by_mode = [
        {
            "mode":             row["Operation_Mode"],
            "avg_power":        round(row["avg_power"], 2),
            "avg_speed":        round(row["avg_speed"], 1),
            "efficiency_ratio": round(row["efficiency_ratio"], 2),
        }
        for _, row in mode_energy.iterrows()
    ]

    # --- Top Power Consuming Machines ---
    top_power = df.groupby("Machine_ID")["Power_Consumption_kW"].mean().nlargest(8).reset_index()
    top_machines_power = [
        {"machine": f"M-{int(r['Machine_ID'])}", "avg_power": round(r["Power_Consumption_kW"], 2)}
        for _, r in top_power.iterrows()
    ]

    # --- Network Latency vs Power Correlation ---
    corr_lat_power = round(df["Network_Latency_ms"].corr(df["Power_Consumption_kW"]), 3)

    # --- Summary KPIs ---
    total_kw = round(df_range["Power_Consumption_kW"].sum(), 1)
    avg_kw   = round(df_range["Power_Consumption_kW"].mean(), 2)
    peak_kw  = round(df_range["Power_Consumption_kW"].max(), 2)

    return {
        "summary": {
            "total_kwh_period":       total_kw,
            "avg_kw":                 avg_kw,
            "peak_kw":                peak_kw,
            "latency_power_corr":     corr_lat_power,
        },
        "power_trend":         power_trend,
        "energy_by_mode":      energy_by_mode,
        "top_machines_power":  top_machines_power,
        "days_shown":          days
    }


# ─────────────────────────────────────────────
# /api/analytics - Deep Analytics Charts
# ─────────────────────────────────────────────
@app.get("/api/analytics")
def get_analytics(days: int = 30):
    """
    Returns production vs target, OEE trend, top bottleneck machines,
    and downtime reasons for the Analytics page.
    """
    if df_global is None:
        raise HTTPException(status_code=503, detail="CSV dataset not loaded")

    df = df_global.copy()
    df = df[df["Date"].notna()].sort_values("Date")
    latest = df["Date"].max()
    start  = latest - pd.Timedelta(days=days - 1)
    df_range = df[df["Date"] >= start]

    max_speed = df["Production_Speed_units_per_hr"].quantile(0.95)
    target    = round(max_speed * 0.92, 0)

    daily = df_range.groupby("Date").agg(
        actual_speed=("Production_Speed_units_per_hr", "mean"),
        avg_error=("Error_Rate_%", "mean"),
        avg_defect=("Quality_Control_Defect_Rate_%", "mean"),
    ).reset_index()

    production_vs_target = [
        {
            "name":   row["Date"].strftime("%b %d"),
            "actual": round(row["actual_speed"], 1),
            "target": round(target, 1),
        }
        for _, row in daily.iterrows()
    ]

    oee_trend = []
    for _, row in daily.iterrows():
        avail = max(0, 1 - row["avg_error"] / 100)
        perf  = min(row["actual_speed"] / max_speed, 1.0) if max_speed > 0 else 0
        qual  = max(0, 1 - row["avg_defect"] / 100)
        oee_trend.append({"name": row["Date"].strftime("%b %d"), "value": round(avail * perf * qual * 100, 1)})

    # Summary KPIs
    overall_avail = max(0, 1 - df["Error_Rate_%"].mean() / 100)
    overall_perf  = min(df["Production_Speed_units_per_hr"].mean() / max_speed, 1.0)
    overall_qual  = max(0, 1 - df["Quality_Control_Defect_Rate_%"].mean() / 100)

    kpis = {
        "oee":          round(overall_avail * overall_perf * overall_qual * 100, 1),
        "availability": round(overall_avail * 100, 1),
        "performance":  round(overall_perf  * 100, 1),
        "quality":      round(overall_qual  * 100, 1),
    }

    # Top bottleneck machines (most low efficiency + highest defect)
    worst = df.groupby("Machine_ID").agg(
        defect=("Quality_Control_Defect_Rate_%", "mean"),
        error=("Error_Rate_%", "mean"),
        low_pct=("Efficiency_Status", lambda x: (x == "Low").mean()),
    ).reset_index().nlargest(5, "low_pct")

    bottlenecks = [
        {
            "machine":   f"M-{int(r['Machine_ID'])}",
            "impact":    f"{round(r['low_pct'] * 100, 1)}%",
            "defect":    round(r["defect"], 1),
            "error":     round(r["error"], 1),
        }
        for _, r in worst.iterrows()
    ]

    T = SETTINGS["thresholds"]
    idle_count = len(df_range[df_range["Operation_Mode"] == "Idle"])
    temp_fault = len(df_range[df_range["Temperature_C"] > T["temperature_critical"]])
    vib_fault  = len(df_range[df_range["Vibration_Hz"]  > T["vibration_critical"]])
    net_fault  = len(df_range[df_range["Packet_Loss_%"] > T["packet_loss_critical"]])
    other      = max(0, len(df_range) - idle_count - temp_fault - vib_fault - net_fault)
    total_dt   = max(1, idle_count + temp_fault + vib_fault + net_fault + other)

    downtime_reasons = [
        {"name": "Equipment Failure",  "value": round(temp_fault / total_dt * 100, 1), "color": "var(--status-critical)"},
        {"name": "Idle / Setup",        "value": round(idle_count / total_dt * 100, 1), "color": "var(--primary-neon)"},
        {"name": "Vibration Events",    "value": round(vib_fault  / total_dt * 100, 1), "color": "var(--status-warning)"},
        {"name": "Network Disruption",  "value": round(net_fault  / total_dt * 100, 1), "color": "#bc8cff"},
        {"name": "Other",               "value": round(other      / total_dt * 100, 1), "color": "var(--text-muted)"},
    ]

    return {
        "kpis":                  kpis,
        "production_vs_target":  production_vs_target,
        "oee_trend":             oee_trend,
        "bottlenecks":           bottlenecks,
        "downtime_reasons":      downtime_reasons,
        "days_shown":            days
    }


# ─────────────────────────────────────────────
# /api/copilot - Local CSV AI Q&A Chat Endpoint
# ─────────────────────────────────────────────
@app.post("/api/copilot")
def copilot_query(payload: CopilotQuery):
    """
    Submit a natural language question about the local CSV dataset.
    Returns Markdown text + optional Recharts config for inline chart rendering.
    """
    try:
        from local_csv_ai import LocalCSVAI
        ai = LocalCSVAI(CSV_PATH)
        result = ai.analyze(payload.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Copilot error: {str(e)}")


# ─────────────────────────────────────────────
# /api/settings - Get / Update Config
# ─────────────────────────────────────────────
@app.get("/api/settings")
def get_settings():
    """Return current active model and alert threshold configuration."""
    return {
        "active_model": SETTINGS["active_model"],
        "available_models": list(MODELS.keys()),
        "thresholds": SETTINGS["thresholds"],
    }

@app.post("/api/settings")
def update_settings(payload: SettingsUpdate):
    """Update active model and/or alert thresholds."""
    if payload.active_model:
        if payload.active_model not in MODELS:
            raise HTTPException(status_code=400, detail=f"Model '{payload.active_model}' not available. Choose from: {list(MODELS.keys())}")
        SETTINGS["active_model"] = payload.active_model

    if payload.thresholds:
        for key, value in payload.thresholds.items():
            if key in SETTINGS["thresholds"]:
                SETTINGS["thresholds"][key] = value

    return {"message": "Settings updated successfully", "settings": SETTINGS}


# ═══════════════════════════════════════════════════════════════
#  EXISTING ML PREDICTION ENDPOINTS (unchanged + multi-model)
# ═══════════════════════════════════════════════════════════════

@app.post("/predict")
def predict_single(payload: FeatureVector):
    """
    Predict efficiency status for a single machine telemetry record.
    Optionally specify model_name (random_forest | xgboost | logistic_regression).
    """
    try:
        model_obj, model_name = get_active_model()
        if payload.model_name and payload.model_name in MODELS:
            model_obj  = MODELS[payload.model_name]
            model_name = payload.model_name

        if model_obj is None or scaler is None:
            raise HTTPException(status_code=503, detail="ML models not loaded")

        X_raw    = np.array([[payload.features.get(f, 0.0) for f in feature_names]])
        X_scaled = scaler.transform(X_raw)

        pred_idx      = model_obj.predict(X_scaled)[0]
        probabilities = model_obj.predict_proba(X_scaled)[0]
        predicted_class = label_reverse[pred_idx]
        confidence    = float(max(probabilities))

        log_prediction(predicted_class, confidence, payload.features, model_name)

        return {
            "prediction":    predicted_class,
            "confidence":    confidence,
            "model_used":    model_name,
            "probabilities": {label_reverse[i]: float(p) for i, p in enumerate(probabilities)}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict_batch")
def predict_batch(payload: BatchFeatureVector):
    """
    Predict efficiency status for multiple telemetry records simultaneously.
    Optionally specify model_name in the payload.
    """
    try:
        model_obj, model_name = get_active_model()
        if payload.model_name and payload.model_name in MODELS:
            model_obj  = MODELS[payload.model_name]
            model_name = payload.model_name

        if model_obj is None or scaler is None:
            raise HTTPException(status_code=503, detail="ML models not loaded")

        X_raw    = np.array([[record.get(f, 0.0) for f in feature_names] for record in payload.records])
        X_scaled = scaler.transform(X_raw)

        predictions   = model_obj.predict(X_scaled)
        probabilities = model_obj.predict_proba(X_scaled)

        results = []
        for i in range(len(predictions)):
            pred_class = label_reverse[predictions[i]]
            conf       = float(max(probabilities[i]))
            results.append({
                "prediction": pred_class,
                "confidence": conf,
                "probabilities": {label_reverse[j]: float(p) for j, p in enumerate(probabilities[i])}
            })
            log_prediction(pred_class, conf, payload.records[i], model_name)

        return {"results": results, "model_used": model_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
