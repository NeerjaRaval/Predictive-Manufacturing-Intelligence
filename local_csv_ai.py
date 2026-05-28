import pandas as pd
import numpy as np
import re
import requests
import json
import os
from datetime import datetime

class LocalCSVAI:
    def __init__(self, csv_path="Thales_Group_Manufacturing.csv"):
        self.csv_path = csv_path
        self.df = None
        self.load_data()
        
    def load_data(self):
        try:
            if os.path.exists(self.csv_path):
                self.df = pd.read_csv(self.csv_path)
                # Clean column names just in case
                self.df.columns = [c.strip() for c in self.df.columns]
                # Ensure Machine_ID is numeric
                self.df['Machine_ID'] = pd.to_numeric(self.df['Machine_ID'], errors='coerce')
                print(f"LocalCSVAI: Successfully loaded dataset with {len(self.df)} rows.")
            else:
                print(f"LocalCSVAI WARNING: {self.csv_path} not found.")
        except Exception as e:
            print(f"LocalCSVAI ERROR loading CSV: {e}")

    def check_ollama(self):
        """Check if local Ollama service is running."""
        try:
            r = requests.get("http://localhost:11434", timeout=0.5)
            return r.status_code == 200
        except Exception:
            return False

    def query_ollama(self, prompt, model="llama3"):
        """Query local Ollama LLM."""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=10)
            if r.status_code == 200:
                return r.json().get("response", "")
        except Exception as e:
            print(f"Ollama query failed: {e}")
        return None

    def analyze(self, user_query):
        """
        Processes natural language queries and performs operations on the CSV.
        Returns a dictionary containing:
        - 'text': Markdown text response
        - 'chart': Optional chart data and config for rendering
        - 'table': Optional structured summary data
        """
        if self.df is None:
            return {
                "text": "Sorry, I couldn't access the local manufacturing CSV dataset.",
                "chart": None,
                "table": None
            }

        q = user_query.lower().strip()
        
        # 1. MATCH MACHINE NUMBERS (e.g. Machine 12, Machine-05, M-04, MCH-39, ID 22)
        machine_match = re.search(r'(?:machine|mch|m|id)[-\s]*([0-9]+)', q)
        machine_id = int(machine_match.group(1)) if machine_match else None
        
        # If two machines are specified
        machines_found = [int(m) for m in re.findall(r'(?:machine|mch|m|id)[-\s]*([0-9]+)', q)]
        
        # 2. DEFINE METRIC DICTIONARY & EXTRACTION
        metrics = {
            "temperature": "Temperature_C",
            "vibration": "Vibration_Hz",
            "power": "Power_Consumption_kW",
            "consumption": "Power_Consumption_kW",
            "latency": "Network_Latency_ms",
            "network": "Network_Latency_ms",
            "packet": "Packet_Loss_%",
            "loss": "Packet_Loss_%",
            "defect": "Quality_Control_Defect_Rate_%",
            "quality": "Quality_Control_Defect_Rate_%",
            "speed": "Production_Speed_units_per_hr",
            "production": "Production_Speed_units_per_hr",
            "maintenance": "Predictive_Maintenance_Score",
            "score": "Predictive_Maintenance_Score",
            "error": "Error_Rate_%",
            "efficiency": "Efficiency_Status"
        }
        
        found_metrics = [v for k, v in metrics.items() if k in q]
        # Remove duplicates
        found_metrics = list(set(found_metrics))
        
        # --- ANALYTICAL INTENTS ---
        
        # INTENT A: COMPARE TWO MACHINES
        if len(machines_found) >= 2:
            m1, m2 = machines_found[0], machines_found[1]
            df_m1 = self.df[self.df['Machine_ID'] == m1]
            df_m2 = self.df[self.df['Machine_ID'] == m2]
            
            if len(df_m1) > 0 and len(df_m2) > 0:
                m1_stats = df_m1.mean(numeric_only=True).to_dict()
                m2_stats = df_m2.mean(numeric_only=True).to_dict()
                
                text = f"### 📊 Machine Comparison: Machine {m1} vs Machine {m2}\n\n"
                text += f"Here is a side-by-side historical performance comparison based on the CSV telemetry logs:\n\n"
                
                comparison_rows = []
                comparison_keys = [
                    ("Temperature (°C)", "Temperature_C", ".1f"),
                    ("Vibration (Hz)", "Vibration_Hz", ".1f"),
                    ("Power Consumption (kW)", "Power_Consumption_kW", ".2f"),
                    ("Network Latency (ms)", "Network_Latency_ms", ".1f"),
                    ("Packet Loss (%)", "Packet_Loss_%", ".2f"),
                    ("QC Defect Rate (%)", "Quality_Control_Defect_Rate_%", ".2f"),
                    ("Production Speed (units/hr)", "Production_Speed_units_per_hr", ".1f"),
                    ("Predictive Maint. Score", "Predictive_Maintenance_Score", ".2f"),
                    ("Error Rate (%)", "Error_Rate_%", ".2f")
                ]
                
                text += "| Metric | Machine " + str(m1) + " | Machine " + str(m2) + " | Difference |\n"
                text += "| :--- | :---: | :---: | :---: |\n"
                
                chart_data = []
                
                for label, col, fmt in comparison_keys:
                    val1 = m1_stats.get(col, 0)
                    val2 = m2_stats.get(col, 0)
                    diff = val1 - val2
                    sign = "+" if diff > 0 else ""
                    
                    text += f"| **{label}** | {val1:{fmt}} | {val2:{fmt}} | {sign}{diff:{fmt}} |\n"
                    
                    # Normalise values for chart comparison
                    chart_data.append({
                        "metric": label.split(" (")[0],
                        f"Machine {m1}": round(val1, 2),
                        f"Machine {m2}": round(val2, 2)
                    })
                
                # Check efficiency profiles
                m1_eff = df_m1['Efficiency_Status'].value_counts(normalize=True).to_dict()
                m2_eff = df_m2['Efficiency_Status'].value_counts(normalize=True).to_dict()
                
                text += f"\n#### ⚡ Efficiency Profiles:\n"
                text += f"- **Machine {m1}**: High: {m1_eff.get('High', 0)*100:.1f}%, Medium: {m1_eff.get('Medium', 0)*100:.1f}%, Low: {m1_eff.get('Low', 0)*100:.1f}%\n"
                text += f"- **Machine {m2}**: High: {m2_eff.get('High', 0)*100:.1f}%, Medium: {m2_eff.get('Medium', 0)*100:.1f}%, Low: {m2_eff.get('Low', 0)*100:.1f}%\n"
                
                # Dynamic Recharts Config
                recharts_config = {
                    "type": "bar",
                    "data": chart_data[:4], # Show first 4 indicators for clean rendering
                    "xKey": "metric",
                    "bars": [
                        {"dataKey": f"Machine {m1}", "fill": "var(--primary-neon)"},
                        {"dataKey": f"Machine {m2}", "fill": "var(--status-critical)"}
                    ]
                }
                
                return {
                    "text": text,
                    "chart": recharts_config,
                    "table": chart_data
                }
                
        # INTENT B: INDIVIDUAL MACHINE DETAILED PROFILE
        if machine_id is not None:
            df_m = self.df[self.df['Machine_ID'] == machine_id]
            if len(df_m) == 0:
                return {
                    "text": f"Machine {machine_id} was not found in the local telemetry logs. Available IDs are 1 to 50.",
                    "chart": None,
                    "table": None
                }
            
            # Calculate metrics
            avg_temp = df_m['Temperature_C'].mean()
            avg_vib = df_m['Vibration_Hz'].mean()
            avg_power = df_m['Power_Consumption_kW'].mean()
            avg_latency = df_m['Network_Latency_ms'].mean()
            avg_loss = df_m['Packet_Loss_%'].mean()
            avg_defect = df_m['Quality_Control_Defect_Rate_%'].mean()
            avg_speed = df_m['Production_Speed_units_per_hr'].mean()
            avg_maint = df_m['Predictive_Maintenance_Score'].mean()
            avg_error = df_m['Error_Rate_%'].mean()
            
            eff_counts = df_m['Efficiency_Status'].value_counts()
            dominant_eff = eff_counts.index[0] if len(eff_counts) > 0 else "Unknown"
            
            # Anomaly checks
            is_overheating = avg_temp > 80
            is_vibrating = avg_vib > 6
            is_high_error = avg_error > 5
            is_low_maint = avg_maint < 0.5
            
            anomalies = []
            if is_overheating: anomalies.append("High Operating Temperatures (>80°C)")
            if is_vibrating: anomalies.append("Elevated Vibration Frequencies (>6Hz)")
            if is_high_error: anomalies.append("High Error Rates (>5%)")
            if is_low_maint: anomalies.append("Low Maintenance Score (<0.50)")
            
            anomaly_sec = ""
            if anomalies:
                anomaly_sec = "\n#### 🚨 Warnings & Concerns:\n" + "\n".join([f"- **{a}**" for a in anomalies]) + "\n"
            else:
                anomaly_sec = "\n#### ✅ Status: Stable / Nominal Operations\nNo immediate telemetry deviations detected.\n"
                
            text = f"### 🏭 Machine {machine_id} Telemetry Profile\n\n"
            text += f"Here is the historical performance summary computed from {len(df_m)} records:\n\n"
            text += f"| Telemetry Parameter | Average Level | Benchmark |\n"
            text += f"| :--- | :---: | :---: |\n"
            text += f"| **Temperature** | {avg_temp:.1f} °C | Nominal (< 75°C) |\n"
            text += f"| **Vibration** | {avg_vib:.2f} Hz | Nominal (< 5 Hz) |\n"
            text += f"| **Power Consumption** | {avg_power:.2f} kW | Nominal (< 15 kW) |\n"
            text += f"| **Network Latency** | {avg_latency:.1f} ms | Nominal (< 10 ms) |\n"
            text += f"| **Packet Loss** | {avg_loss:.2f}% | Nominal (< 0.5%) |\n"
            text += f"| **QC Defect Rate** | {avg_defect:.2f}% | Nominal (< 2.0%) |\n"
            text += f"| **Production Speed** | {avg_speed:.1f} u/h | Target (> 500 u/h) |\n"
            text += f"| **Error Rate** | {avg_error:.2f}% | Nominal (< 2.0%) |\n"
            text += f"| **Predictive Maint. Score** | {avg_maint:.2f} | Warning (< 0.50) |\n\n"
            
            text += f"**Dominant Efficiency Status**: <span style='color:{'var(--status-good)' if dominant_eff == 'High' else 'var(--status-warning)' if dominant_eff == 'Medium' else 'var(--status-critical)'}; font-weight: bold;'>{dominant_eff}</span>\n"
            text += anomaly_sec
            
            # Render a neat timeline chart of recent temperatures for this machine
            recent_telemetry = df_m.tail(15)
            chart_data = []
            for idx, r in recent_telemetry.iterrows():
                chart_data.append({
                    "time": r.get("Timestamp", "N/A")[:5] if isinstance(r.get("Timestamp"), str) else f"pt-{len(chart_data)}",
                    "Temperature": round(r["Temperature_C"], 1),
                    "Vibration": round(r["Vibration_Hz"], 2),
                    "Power": round(r["Power_Consumption_kW"], 2)
                })
                
            recharts_config = {
                "type": "area",
                "data": chart_data,
                "xKey": "time",
                "areas": [
                    {"dataKey": "Temperature", "stroke": "var(--status-critical)", "fill": "rgba(248, 81, 73, 0.1)"},
                    {"dataKey": "Vibration", "stroke": "var(--primary-neon)", "fill": "rgba(88, 166, 255, 0.1)"}
                ]
            }
            
            return {
                "text": text,
                "chart": recharts_config,
                "table": chart_data
            }

        # INTENT C: GENERAL DATA SUMMARY / OVERVIEW
        if any(w in q for w in ["summary", "overview", "what is this", "tell me about"]):
            total_records = len(self.df)
            num_machines = self.df['Machine_ID'].nunique()
            op_modes = self.df['Operation_Mode'].value_counts()
            eff_status = self.df['Efficiency_Status'].value_counts()
            
            text = f"### 📊 Local CSV Dataset Overview\n\n"
            text += f"This smart manufacturing dataset contains historical IoT telemetry, quality control metrics, and 6G network latency stats:\n\n"
            text += f"- **Total Records**: {total_records:,}\n"
            text += f"- **Unique Industrial Machines**: {num_machines} (IDs 1 through 50)\n"
            text += f"- **Operational Modes recorded**:\n"
            for mode, count in op_modes.items():
                text += f"  - `{mode}`: {count:,} records ({count/total_records*100:.1f}%)\n"
            
            text += f"- **Efficiency Status Breakdown**:\n"
            chart_data = []
            for status, count in eff_status.items():
                pct = count/total_records*100
                color = "var(--status-good)" if status == "High" else "var(--status-warning)" if status == "Medium" else "var(--status-critical)"
                text += f"  - <span style='color:{color}; font-weight:600;'>{status}</span>: {count:,} ({pct:.1f}%)\n"
                chart_data.append({
                    "name": status,
                    "value": count,
                    "percentage": round(pct, 1),
                    "color": color
                })
                
            text += f"\nWould you like me to identify anomalies, perform correlations, or analyze a specific machine (e.g. ask 'Show machine 12 telemetry')?"
            
            recharts_config = {
                "type": "pie",
                "data": chart_data,
                "xKey": "name",
                "yKey": "value"
            }
            
            return {
                "text": text,
                "chart": recharts_config,
                "table": chart_data
            }

        # INTENT D: ANOMALIES & OUTLIERS DETECTION
        if any(w in q for w in ["anomaly", "anomalies", "outlier", "outliers", "spike", "spikes", "deviation"]):
            # Filter rows with critical limits
            temp_anom = self.df[self.df['Temperature_C'] > 85]
            vib_anom = self.df[self.df['Vibration_Hz'] > 8.0]
            loss_anom = self.df[self.df['Packet_Loss_%'] > 2.0]
            maint_critical = self.df[self.df['Predictive_Maintenance_Score'] < 0.25]
            
            text = f"### 🚨 Local Telemetry Anomalies Report\n\n"
            text += f"A statistical scan of the dataset has flagged operational metrics exceeding safety benchmarks:\n\n"
            text += f"1. **Temperature Overheating (>85°C)**: {len(temp_anom)} occurrences.\n"
            text += f"2. **Critical Vibrations (>8.0Hz)**: {len(vib_anom)} occurrences.\n"
            text += f"3. **High Network Packet Loss (>2.0%)**: {len(loss_anom)} occurrences.\n"
            text += f"4. **Imminent Failure Risks (Maintenance Score < 0.25)**: {len(maint_critical)} occurrences.\n\n"
            
            # Group by Machine ID to find worst offenders
            worst_temps = temp_anom['Machine_ID'].value_counts().head(3)
            worst_vibs = vib_anom['Machine_ID'].value_counts().head(3)
            worst_loss = loss_anom['Machine_ID'].value_counts().head(3)
            
            text += "#### 🛠️ Top Anomaly Offenders by Machine ID:\n"
            if len(worst_temps) > 0:
                text += f"- **Temperature**: Machines {', '.join([f'M-{int(m)} ({c} times)' for m, c in worst_temps.items()])}\n"
            if len(worst_vibs) > 0:
                text += f"- **Vibrations**: Machines {', '.join([f'M-{int(m)} ({c} times)' for m, c in worst_vibs.items()])}\n"
            if len(worst_loss) > 0:
                text += f"- **6G Packet Loss**: Machines {', '.join([f'M-{int(m)} ({c} times)' for m, c in worst_loss.items()])}\n"
            
            text += f"\n*Action Item*: We recommend scheduling preventative maintenance on these machines immediately to prevent efficiency drops."
            
            # Build bar data for chart
            chart_data = []
            all_offenders = set(list(worst_temps.index) + list(worst_vibs.index) + list(worst_loss.index))
            for m in list(all_offenders)[:6]:
                chart_data.append({
                    "machine": f"M-{int(m)}",
                    "Temperature Overheats": len(temp_anom[temp_anom['Machine_ID'] == m]),
                    "Vibration Spikes": len(vib_anom[vib_anom['Machine_ID'] == m]),
                    "Packet Loss Drops": len(loss_anom[loss_anom['Machine_ID'] == m])
                })
                
            recharts_config = {
                "type": "bar",
                "data": chart_data,
                "xKey": "machine",
                "bars": [
                    {"dataKey": "Temperature Overheats", "fill": "var(--status-critical)"},
                    {"dataKey": "Vibration Spikes", "fill": "var(--status-warning)"},
                    {"dataKey": "Packet Loss Drops", "fill": "var(--primary-neon)"}
                ]
            }
            
            return {
                "text": text,
                "chart": recharts_config,
                "table": chart_data
            }

        # INTENT E: EXTREME VALUES (Highest / Lowest)
        if any(w in q for w in ["highest", "worst", "maximum", "lowest", "best", "minimum", "most", "least"]):
            # Find the machine with highest temp, highest vibration, lowest maintenance score, highest defect rate
            max_temp_row = self.df.loc[self.df['Temperature_C'].idxmax()]
            max_vib_row = self.df.loc[self.df['Vibration_Hz'].idxmax()]
            min_maint_row = self.df.loc[self.df['Predictive_Maintenance_Score'].idxmin()]
            max_defect_row = self.df.loc[self.df['Quality_Control_Defect_Rate_%'].idxmax()]
            max_error_row = self.df.loc[self.df['Error_Rate_%'].idxmax()]
            
            text = f"### 🔝 Local Factory Extremes & Critical Records\n\n"
            text += f"Here are the absolute peak and bottom records from the local CSV records:\n\n"
            text += f"- **Highest Temperature**: **{max_temp_row['Temperature_C']:.1f}°C** on Machine **M-{int(max_temp_row['Machine_ID'])}** (Mode: `{max_temp_row['Operation_Mode']}`, status: `{max_temp_row['Efficiency_Status']}`)\n"
            text += f"- **Highest Vibration**: **{max_vib_row['Vibration_Hz']:.2f} Hz** on Machine **M-{int(max_vib_row['Machine_ID'])}** (Mode: `{max_vib_row['Operation_Mode']}`, status: `{max_vib_row['Efficiency_Status']}`)\n"
            text += f"- **Lowest Maintenance Score**: **{min_maint_row['Predictive_Maintenance_Score']:.3f}** on Machine **M-{int(min_maint_row['Machine_ID'])}** (Vibration: `{min_maint_row['Vibration_Hz']:.1f}Hz`, status: `{min_maint_row['Efficiency_Status']}`)\n"
            text += f"- **Highest QC Defect Rate**: **{max_defect_row['Quality_Control_Defect_Rate_%']:.1f}%** on Machine **M-{int(max_defect_row['Machine_ID'])}** (Speed: `{max_defect_row['Production_Speed_units_per_hr']:.0f} u/h`)\n"
            text += f"- **Highest Operational Error**: **{max_error_row['Error_Rate_%']:.1f}%** on Machine **M-{int(max_error_row['Machine_ID'])}**\n\n"
            
            # Chart the values
            chart_data = [
                {"parameter": "Max Temp (°C)", "value": round(max_temp_row['Temperature_C'], 1), "Machine": f"M-{int(max_temp_row['Machine_ID'])}"},
                {"parameter": "Max Vibration (Hz)", "value": round(max_vib_row['Vibration_Hz'], 1), "Machine": f"M-{int(max_vib_row['Machine_ID'])}"},
                {"parameter": "Max Defect Rate (%)", "value": round(max_defect_row['Quality_Control_Defect_Rate_%'], 1), "Machine": f"M-{int(max_defect_row['Machine_ID'])}"},
                {"parameter": "Max Error Rate (%)", "value": round(max_error_row['Error_Rate_%'], 1), "Machine": f"M-{int(max_error_row['Machine_ID'])}"}
            ]
            
            recharts_config = {
                "type": "bar",
                "data": chart_data,
                "xKey": "parameter",
                "bars": [
                    {"dataKey": "value", "fill": "var(--status-critical)"}
                ]
            }
            
            return {
                "text": text,
                "chart": recharts_config,
                "table": chart_data
            }

        # INTENT F: CORRELATIONS & RELATIONSHIPS
        if any(w in q for w in ["correlation", "relationship", "affect", "affects", "influence", "vs", "versus"]):
            text = f"### 🔗 Statistical Telemetry Correlations\n\n"
            text += f"We computed Pearson correlation coefficients ($r$) across the entire dataset:\n\n"
            
            # Compute some logical correlations
            c_temp_vib = self.df['Temperature_C'].corr(self.df['Vibration_Hz'])
            c_temp_power = self.df['Temperature_C'].corr(self.df['Power_Consumption_kW'])
            c_lat_loss = self.df['Network_Latency_ms'].corr(self.df['Packet_Loss_%'])
            c_vib_maint = self.df['Vibration_Hz'].corr(self.df['Predictive_Maintenance_Score'])
            c_speed_defect = self.df['Production_Speed_units_per_hr'].corr(self.df['Quality_Control_Defect_Rate_%'])
            
            text += f"- **Temperature vs. Vibration**: $r$ = **{c_temp_vib:.3f}** ("
            text += "Strong positive" if c_temp_vib > 0.6 else "Moderate positive" if c_temp_vib > 0.3 else "Weak positive" if c_temp_vib > 0 else "Weak negative" if c_temp_vib > -0.3 else "Moderate negative" if c_temp_vib > -0.6 else "Strong negative"
            text += " correlation)\n"
            
            text += f"- **Temperature vs. Power Consumption**: $r$ = **{c_temp_power:.3f}** ("
            text += "Strong positive" if c_temp_power > 0.6 else "Moderate positive" if c_temp_power > 0.3 else "Weak positive" if c_temp_power > 0 else "Weak negative"
            text += " correlation)\n"
            
            text += f"- **Network Latency vs. Packet Loss**: $r$ = **{c_lat_loss:.3f}** ("
            text += "Strong positive" if c_lat_loss > 0.6 else "Moderate positive" if c_lat_loss > 0.3 else "Weak positive"
            text += " correlation)\n"
            
            text += f"- **Vibration vs. Maintenance Score**: $r$ = **{c_vib_maint:.3f}** ("
            text += "Strong positive" if c_vib_maint > 0.6 else "Moderate positive" if c_vib_maint > 0.3 else "Weak negative" if c_vib_maint > -0.3 else "Moderate negative" if c_vib_maint > -0.6 else "Strong negative"
            text += " correlation)\n"
            
            text += f"- **Production Speed vs. QC Defect Rate**: $r$ = **{c_speed_defect:.3f}**\n\n"
            
            text += f"**Key AI Insight**: Vibration and Temperature are key drivers of machinery fatigue. Highly elevated vibrations wear bearings rapidly, causing an inverse drop in your **Predictive Maintenance Score**."
            
            chart_data = [
                {"pair": "Temp & Vibration", "correlation": round(c_temp_vib, 3)},
                {"pair": "Temp & Power", "correlation": round(c_temp_power, 3)},
                {"pair": "Latency & Packet Loss", "correlation": round(c_lat_loss, 3)},
                {"pair": "Vibration & Maintenance", "correlation": round(c_vib_maint, 3)},
                {"pair": "Speed & Defect Rate", "correlation": round(c_speed_defect, 3)}
            ]
            
            recharts_config = {
                "type": "bar",
                "data": chart_data,
                "xKey": "pair",
                "bars": [
                    {"dataKey": "correlation", "fill": "var(--primary-neon)"}
                ]
            }
            
            return {
                "text": text,
                "chart": recharts_config,
                "table": chart_data
            }

        # DEFAULT RESPONSE: If Ollama is available, query it to provide an intelligent fallback. Otherwise, do general query matches.
        if self.check_ollama():
            # Construct dataset summary prompt
            avg_row = self.df.mean(numeric_only=True).to_dict()
            prompt = f"""
You are an expert AI data analyst at an industrial manufacturing smart factory.
The factory has 50 machines monitoring Temperature, Vibration, Power Consumption, network stats (latency, packet loss) over a 6G network.
Here is the average status of the factory:
- Average temperature: {avg_row.get('Temperature_C', 0):.1f}°C
- Average vibration: {avg_row.get('Vibration_Hz', 0):.2f} Hz
- Average network latency: {avg_row.get('Network_Latency_ms', 0):.1f} ms
- Average packet loss: {avg_row.get('Packet_Loss_%', 0):.2f}%
- Average quality control defect rate: {avg_row.get('Quality_Control_Defect_Rate_%', 0):.2f}%
- Average production speed: {avg_row.get('Production_Speed_units_per_hr', 0):.1f} units/hr
- Average predictive maintenance score: {avg_row.get('Predictive_Maintenance_Score', 0):.2f}
- Average error rate: {avg_row.get('Error_Rate_%', 0):.2f}%

The user is asking: "{user_query}"
Give a professional, brief, insightful answer about this smart manufacturing factory data. Keep it highly relevant, concise, and structured in Markdown.
"""
            ollama_response = self.query_ollama(prompt)
            if ollama_response:
                return {
                    "text": ollama_response,
                    "chart": None,
                    "table": None
                }

        # Traditional fallback
        avg_row = self.df.mean(numeric_only=True).to_dict()
        text = f"### 🤖 AI Agent Local CSV Analysis\n\n"
        text += f"I analyzed your query relative to the manufacturing telemetry logs:\n\n"
        text += f"Based on our active CSV records of 50 machines:\n"
        text += f"- **Average Power Consumption**: {avg_row.get('Power_Consumption_kW', 0):.2f} kW\n"
        text += f"- **Average Network Latency**: {avg_row.get('Network_Latency_ms', 0):.1f} ms\n"
        text += f"- **Average defect rate**: {avg_row.get('Quality_Control_Defect_Rate_%', 0):.2f}%\n"
        text += f"- **Overall Predictive Maintenance score**: {avg_row.get('Predictive_Maintenance_Score', 0):.2f}/1.00\n\n"
        text += f"You can ask me to perform deep aggregations or find outliers, e.g.:\n"
        text += f"- *'Show Machine 12 telemetry details'*\n"
        text += f"- *'Compare Machine 5 and Machine 10'*\n"
        text += f"- *'Find temperature anomalies'* or *'Check correlations'*\n"
        
        return {
            "text": text,
            "chart": None,
            "table": None
        }
