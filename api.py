import joblib
import json
import numpy as np
import os
import csv
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(
    title="Predictive Manufacturing Intelligence API", 
    description="REST API for real-time manufacturing efficiency predictions",
    version="1.0.0"
)

# --- Load Models on Startup ---
try:
    model = joblib.load("models/best_model.pkl")
    scaler = joblib.load("models/scaler.pkl")
    feature_names = joblib.load("models/feature_names.pkl")
    label_mapping = joblib.load("models/label_encoder.pkl")
    label_reverse = {v: k for k, v in label_mapping.items()}
except Exception as e:
    raise RuntimeError(f"Failed to load models. Ensure models exist in the /models directory. Error: {e}")

# --- Pydantic Data Models ---
class FeatureVector(BaseModel):
    features: Dict[str, float]

class BatchFeatureVector(BaseModel):
    records: List[Dict[str, float]]

# --- Logging Setup ---
LOG_FILE = "logs/prediction_audit.csv"
os.makedirs("logs", exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "predicted_class", "confidence", "machine_id", "input_features"])

def log_prediction(predicted_class: str, confidence: float, features: dict):
    """Save prediction metadata to CSV for drift monitoring."""
    try:
        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            # Store features as a JSON string to keep the CSV clean
            machine_id = features.get("Machine_ID", "Unknown")
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                predicted_class,
                round(confidence, 4),
                machine_id,
                json.dumps(features)
            ])
    except Exception as e:
        print(f"Logging failed: {e}")

# --- API Endpoints ---
@app.get("/health")
def health_check():
    """Verify that the API and ML models are loaded and ready."""
    return {"status": "healthy", "model_status": "loaded"}

@app.post("/predict")
def predict_single(payload: FeatureVector):
    """
    Predict efficiency status for a single machine telemetry record.
    """
    try:
        # Construct feature array exactly in the order the model expects
        X_raw = np.array([[payload.features.get(f, 0.0) for f in feature_names]])
        X_scaled = scaler.transform(X_raw)
        
        pred_idx = model.predict(X_scaled)[0]
        probabilities = model.predict_proba(X_scaled)[0]
        
        predicted_class = label_reverse[pred_idx]
        confidence = float(max(probabilities))
        
        # Log the prediction
        log_prediction(predicted_class, confidence, payload.features)
        
        return {
            "prediction": predicted_class,
            "confidence": confidence,
            "probabilities": {label_reverse[i]: float(p) for i, p in enumerate(probabilities)}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_batch")
def predict_batch(payload: BatchFeatureVector):
    """
    Predict efficiency status for multiple telemetry records simultaneously.
    """
    try:
        X_raw = np.array([[record.get(f, 0.0) for f in feature_names] for record in payload.records])
        X_scaled = scaler.transform(X_raw)
        
        predictions = model.predict(X_scaled)
        probabilities = model.predict_proba(X_scaled)
        
        results = []
        for i in range(len(predictions)):
            results.append({
                "prediction": label_reverse[predictions[i]],
                "confidence": float(max(probabilities[i]))
            })
            # Log each prediction in the batch
            log_prediction(label_reverse[predictions[i]], float(max(probabilities[i])), payload.records[i])
            
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
