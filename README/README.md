# AI-Based Manufacturing Efficiency Intelligence

A production-grade Machine Learning pipeline and interactive analytical dashboard designed to monitor, predict, and explain manufacturing efficiency using sensor telemetry, production metrics, and 6G network data.

## 🚀 Project Overview

In modern smart factories enabled by Industrial IoT and 6G connectivity, efficiency can fluctuate rapidly due to sensor deviations, network instability, and quality variations. Traditional dashboards only show historical data, but this system answers the critical question: **What is the current efficiency state of the manufacturing process right now, and why?**

This project features a fully automated Machine Learning pipeline (handling extreme class imbalances) and a professional 5-page Streamlit dashboard tailored for corporate environments.

## ✨ Key Features

### 1. Robust Machine Learning Pipeline (`src/`)
* **Data Preprocessing**: Handles temporal sorting, scales numerical features, and encodes categorical states.
* **Feature Engineering**: Centralized generation of complex interaction metrics (e.g., *Energy Efficiency Ratio*, *Network Reliability Score*, *Sensor Stability Index*).
* **Class Imbalance Handling**: Utilizes SMOTE (Synthetic Minority Over-sampling Technique) to accurately predict the rare "High Efficiency" class (which constitutes only 3% of the raw data).
* **Model Optimization**: Automated hyperparameter tuning using Optuna. The production model is a **Random Forest Classifier** achieving an exceptional **Macro F1 Score of 0.9965**.
* **Explainability Engine**: Integrated SHAP (SHapley Additive exPlanations) values generation for deep model interpretability.

### 2. Professional Streamlit Dashboard (`pages/`)
The application features a sleek, slate-blue corporate UI with 5 interactive modules:
* **Executive Summary (`app.py`)**: High-level KPIs, production yield, defect rates, and a 1-click Executive PDF Report Generator.
* **Efficiency Prediction**: Single-record live inference with interactive parameter sliders. Predicts whether a machine will operate at High, Medium, or Low efficiency.
* **Machine Fleet Insights**: Global heatmap showing the health distribution of all active manufacturing nodes (50 machines). Allows for deep-dive analysis into specific hardware.
* **AI Explainability (SHAP)**: Demystifies the AI decision-making process. Shows global feature impact (e.g., which sensors drive efficiency) and micro-level waterfall charts for individual predictions.
* **Operational Monitoring**: Segment efficiency by operation modes and compare IT (network) vs OT (sensor) metrics. Features a powerful **What-If Stress Test Simulator** to project fleet-wide impacts of latency or power fluctuations.
* **Automated Data Explorer**: Raw telemetry viewer with auto-generated univariate distributions, bivariate scatter plots, and Pearson correlation matrices.

## 🛠️ Technology Stack
* **Core**: Python 3.9+
* **Machine Learning**: Scikit-Learn, Optuna, Imbalanced-Learn (SMOTE)
* **Model Explainability**: SHAP
* **Data Manipulation**: Pandas, NumPy
* **Interactive UI**: Streamlit
* **Data Visualization**: Plotly Express & Plotly Graph Objects
* **Reporting**: FPDF2

## 📦 Project Structure

```text
Predictive Manufacturing Intelligence/
│
├── app.py                            # Dashboard Home / Executive Summary
├── pages/                            # Dashboard Modules
│   ├── 1_Efficiency_Prediction.py
│   ├── 2_Machine_Insights.py
│   ├── 3_Explainability.py
│   ├── 4_Operational_Monitoring.py
│   └── 5_Data_Explorer.py
│
├── src/                              # ML Pipeline Modules
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   └── report_generator.py
│
├── train.py                          # Master ML training script
├── models/                           # Saved models, scalers, & encoders (generated after train.py)
├── outputs/                          # Generated SHAP data and PDF reports
├── README/                           # Project documentation
└── Thales_Group_Manufacturing.csv    # Raw telemetry dataset
```

## ⚙️ How to Run Locally

1. **Install Dependencies:**
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure you have `streamlit`, `pandas`, `scikit-learn`, `plotly`, `shap`, `imbalanced-learn`, `optuna`, and `fpdf2` installed).*

2. **Train the ML Pipeline:**
   Before running the dashboard, generate the models and SHAP explainer by running the training script:
   ```bash
   python train.py
   ```
   *Note: This will take a few moments as it runs SMOTE, Optuna hyperparameter tuning, and SHAP value generation. Outputs will be saved in the `models/` directory.*

3. **Launch the Dashboard:**
   Start the interactive Streamlit server:
   ```bash
   streamlit run app.py
   ```
   The dashboard will automatically open in your default web browser at `http://localhost:8501`.

## 📈 Future Scalability
* **Deployment**: The system is fully containerizable via Docker for deployment to cloud platforms (AWS/Azure/GCP).
* **API Integration**: The prediction logic in `model_training.py` can be exposed as a REST endpoint using FastAPI to integrate seamlessly with existing factory execution systems (MES). 





