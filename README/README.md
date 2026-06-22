# AI-Based Smart Manufacturing Predictive Intelligence

A production-grade Machine Learning classification system and interactive analytical dashboard designed to monitor, predict, and explain manufacturing efficiency using sensor telemetry, production metrics, and 6G network data.

---

## 🚀 Project Overview

In modern smart factories enabled by Industrial IoT and 6G connectivity, operational efficiency can fluctuate rapidly due to sensor deviations, network instability, and quality variations. This project moves away from static, historical reports to provide a real-time answer to the critical operational questions: **What is the current efficiency state of the manufacturing process right now, why is it in that state, and when is maintenance required?**

This repository features:
1. **FastAPI REST Service (`api.py`)** exposing full dashboard metrics, dynamic threshold configurations, ML model selection, and an on-the-fly PDF Executive Report compiler.
2. **Machine Learning Engine (`src/`)** performing robust feature engineering, handling extreme class imbalance (using SMOTE), hyperparameter tuning (using Optuna), and explaining predictions via SHAP.
3. **React Frontend Dashboard (`frontend/`)** providing a premium, interactive dark-themed corporate UI with glassmorphism styling and real-time visualization of fleet telemetry.

---

## ✨ Key Features

### 1. Robust Machine Learning Engine (`src/`)
* **Data Preprocessing & Encoding**: Handles temporal sorting, scales numerical features via standard scaler, and encodes operational modes.
* **Feature Engineering**: Computes derived interaction metrics:
  - *Energy Efficiency Ratio* (Power Consumption vs. Speed)
  - *Network Reliability Score* (Latency vs. Packet Loss)
  - *Sensor Stability Index* (Temperature vs. Vibration)
* **Class Imbalance Handling**: Employs SMOTE (Synthetic Minority Over-sampling Technique) to address the extreme class imbalance of the rare "High Efficiency" state (approx. 3% of logs).
* **Model Optimization**: Automated hyperparameter tuning via Optuna. Evaluates Random Forest, XGBoost, and Logistic Regression models.
* **Explainability Panel**: Computes SHAP (SHapley Additive exPlanations) values to determine features that drive efficiency predictions.

### 2. High-Performance REST API (`api.py`)
* Fully documented FastAPI application supporting endpoints for:
  - Summary KPIs (OEE, Active Alerts count, Predicted Failures).
  - Telemetry logs & averages for the fleet of 50 machines (`/api/machines`).
  - Single and batch machine prediction overrides (`/predict` & `/predict_batch`).
  - AI Copilot natural-language CSV analysis (`/api/copilot`) supporting structured Recharts responses.
  - On-the-fly PDF Executive Summary compiler (`/api/reports/download`).

### 3. Sleek React Dashboard UI (`frontend/`)
Designed as a dark-mode dashboard with custom micro-animations and Recharts visualization:
* **Dashboard Home**: High-impact operational summaries: overall OEE index, active anomaly warnings, and AI health scoring.
* **Machine Fleet Explorer**: A responsive grid to inspect and filter all 50 machines, including search by Machine ID and sorting by telemetry thresholds.
* **Playground Predictor**: Run manual telemetry tests for single or batch rows using different models (Random Forest, XGBoost, Logistic Regression).
* **Energy Analytics**: Correlation matrices, power profiles, and energy-to-speed ratios.
* **Interactive Settings Panel**: Allows operators to switch the active backend ML model on-the-fly and customize warning/critical safety thresholds.

---

## 🛠️ Technology Stack

* **Backend REST API**: FastAPI, Uvicorn, Python 3.9+
* **Machine Learning**: Scikit-Learn, XGBoost, Optuna, Imbalanced-Learn (SMOTE), Joblib
* **Data Manipulation**: Pandas, NumPy
* **Explainability**: SHAP
* **Reporting**: FPDF2, Matplotlib, Seaborn
* **Frontend Web App**: React, Vite, React Router, Recharts, Lucide Icons, Vanilla CSS

---

## 📦 Project Structure

```text
Predictive Manufacturing Intelligence/
│
├── api.py                         # FastAPI REST API (OEE calculations, telemetry endpoints, settings)
├── local_csv_ai.py                # Local Copilot engine (matches intents, parses CSV, Ollama query fallback)
├── train.py                       # Master ML training pipeline (SMOTE, Optuna tuning, saves models)
├── requirements.txt               # Backend Python dependencies
├── package.json                   # Root package.json (cross-project runner scripts)
│
├── src/                           # Backend Python Modules
│   ├── preprocessing.py           # Ingestion, cleaning, temporal splitting
│   ├── feature_engineering.py     # Energy ratios, network scores, sensor index
│   ├── model_training.py          # Baseline and advanced model fitting
│   ├── hyperparameter_tuning.py   # Optuna tuning wrapper
│   ├── explainability.py          # SHAP explainer generator
│   ├── monitoring.py              # Audit logs & prediction drift checking
│   └── report_generator.py        # Executive PDF compilation using FPDF
│
├── frontend/                      # React Frontend Application
│   ├── index.html                 # HTML shell
│   ├── package.json               # NPM packages & build steps
│   └── src/                       # React components & pages
│       ├── App.jsx / main.jsx     # App entry & Routing configuration
│       ├── Layout.jsx             # Neon-themed sidebar layout and wrapper
│       └── pages/                 # UI pages (Dashboard, Machines, Predictions, Energy, Settings, etc.)
│
├── models/                        # Serialized ML assets (*.pkl files, scaler, features list)
├── outputs/                       # Saved Matplotlib charts & generated PDF files
└── Thales_Group_Manufacturing.csv # Telemetry dataset (100,000 logs for 50 machines)
```

---

## ⚙️ How to Setup and Run Locally

### 1. Root Scripts & Dependencies Installation
From the project root directory, run:
```bash
# Install backend Python dependencies
pip install -r requirements.txt

# Install frontend Node dependencies (Vite, React, Recharts, etc.)
npm run install-all
```

### 2. Train the Machine Learning Models
Generate the model files (`.pkl`) and explanation vectors by running:
```bash
python train.py
```
*Note: This script will run SMOTE oversampling, evaluate Random Forest/XGBoost models, perform hyperparameter tuning with Optuna, and serialize outputs to the `models/` directory.*

### 3. Launch the Application
Start both the FastAPI backend server and the React frontend development server simultaneously:
```bash
# Starts FastAPI on http://localhost:8000 and the React dev server on http://localhost:5173
npm run dev
```

Alternatively, you can start them separately:
```bash
# To start the Backend API:
npm run start-api

# To start the React Frontend (from the frontend directory):
cd frontend && npm run dev
```

---

## 📈 Future Scalability
* **Real-time Streaming**: Connect the API to an Apache Kafka or MQTT broker to consume live sensor telemetry streams directly.
* **Model Retraining Trigger**: Schedule cron-jobs to automatically retrain the pipeline when prediction drift (monitored in `src/monitoring.py`) exceeds 15%.
