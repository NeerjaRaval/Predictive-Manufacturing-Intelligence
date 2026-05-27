import pandas as pd
import numpy as np
import os
import json

LOG_FILE = "logs/prediction_audit.csv"

def get_live_stats():
    """Read the prediction logs and return summary statistics."""
    if not os.path.exists(LOG_FILE):
        return None
    
    try:
        df_logs = pd.read_csv(LOG_FILE)
        if df_logs.empty:
            return None
            
        stats = {
            "total_predictions": len(df_logs),
            "avg_confidence": df_logs["confidence"].mean(),
            "class_distribution": df_logs["predicted_class"].value_counts(normalize=True).to_dict(),
            "recent_logs": df_logs.tail(10).to_dict('records')
        }
        return stats
    except Exception as e:
        print(f"Monitoring stats failed: {e}")
        return None

def check_drift(training_distribution):
    """
    Compare live prediction distribution vs training distribution.
    If 'Low' or 'Medium' increases significantly, it indicates potential drift.
    """
    live_stats = get_live_stats()
    if not live_stats:
        return None, "No data"
        
    live_dist = live_stats["class_distribution"]
    
    drift_detected = False
    reasons = []
    
    for cls, train_pct in training_distribution.items():
        live_pct = live_dist.get(cls, 0)
        # If any class changes by more than 15 percentage points, flag it
        if abs(live_pct - train_pct) > 0.15:
            drift_detected = True
            reasons.append(f"{cls} efficiency shifted from {train_pct:.1%} to {live_pct:.1%}")
            
    return drift_detected, reasons
