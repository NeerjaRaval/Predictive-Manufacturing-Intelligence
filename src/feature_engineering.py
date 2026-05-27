"""
Feature Engineering Module
==========================
Creates derived features from raw sensor, production, and network data
to improve model predictive power.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def create_energy_efficiency_ratio(df):
    """
    Energy Efficiency Ratio = Production_Speed / Power_Consumption
    Measures output per unit of energy consumed.
    Higher is better — more production with less power.
    """
    df = df.copy()
    df["Energy_Efficiency_Ratio"] = (
        df["Production_Speed_units_per_hr"] / df["Power_Consumption_kW"].replace(0, np.nan)
    ).fillna(0)
    logger.info("Created: Energy_Efficiency_Ratio")
    return df


def create_error_to_output_ratio(df):
    """
    Error-to-Output Ratio = Error_Rate / Production_Speed
    Measures error density relative to production throughput.
    Lower is better — fewer errors per unit produced.
    """
    df = df.copy()
    df["Error_to_Output_Ratio"] = (
        df["Error_Rate_%"] / df["Production_Speed_units_per_hr"].replace(0, np.nan)
    ).fillna(0)
    logger.info("Created: Error_to_Output_Ratio")
    return df


def create_network_reliability_score(df):
    """
    Network Reliability Score = 1 - (Latency/50 + Packet_Loss/5) / 2
    Composite metric for 6G network health.
    Range: 0 (poor) to 1 (excellent).
    Latency normalized by max (50ms), Packet Loss by max (5%).
    """
    df = df.copy()
    latency_normalized = df["Network_Latency_ms"] / 50.0
    packet_loss_normalized = df["Packet_Loss_%"] / 5.0

    df["Network_Reliability_Score"] = 1 - (
        (latency_normalized + packet_loss_normalized) / 2
    )
    # Clip to [0, 1] range
    df["Network_Reliability_Score"] = df["Network_Reliability_Score"].clip(0, 1)
    logger.info("Created: Network_Reliability_Score")
    return df


def create_sensor_stability_index(df):
    """
    Sensor Stability Index = 1 / (1 + Temp_deviation + Vibration_deviation)
    Measures how stable sensor readings are relative to the median.
    Range: 0 (highly unstable) to 1 (perfectly stable).
    """
    df = df.copy()

    # Calculate deviations from median
    temp_median = df["Temperature_C"].median()
    vib_median = df["Vibration_Hz"].median()

    temp_deviation = np.abs(df["Temperature_C"] - temp_median) / temp_median
    vib_deviation = np.abs(df["Vibration_Hz"] - vib_median) / vib_median

    df["Sensor_Stability_Index"] = 1 / (1 + temp_deviation + vib_deviation)
    logger.info("Created: Sensor_Stability_Index")
    return df


def create_defect_error_interaction(df):
    """
    Defect-Error Interaction = Defect_Rate × Error_Rate
    Captures the joint effect of quality defects and operational errors.
    High values indicate simultaneous quality and operational issues.
    """
    df = df.copy()
    df["Defect_Error_Interaction"] = (
        df["Quality_Control_Defect_Rate_%"] * df["Error_Rate_%"]
    )
    logger.info("Created: Defect_Error_Interaction")
    return df


def create_maintenance_risk(df):
    """
    Maintenance Risk = (1 - Maintenance_Score) × Error_Rate
    High risk when maintenance readiness is low AND errors are high.
    Captures machines that are error-prone due to poor maintenance.
    """
    df = df.copy()
    df["Maintenance_Risk"] = (
        (1 - df["Predictive_Maintenance_Score"]) * df["Error_Rate_%"]
    )
    logger.info("Created: Maintenance_Risk")
    return df


def engineer_all_features(df, config=None):
    """
    Apply all feature engineering transformations.
    
    Parameters:
        df: DataFrame with raw features
        config: Optional config dict to control which features to create
    
    Returns:
        DataFrame with all engineered features added
    """
    logger.info("=" * 50)
    logger.info("Starting feature engineering...")
    logger.info("=" * 50)

    initial_cols = len(df.columns)

    # Apply each feature engineering function
    feature_functions = [
        ("create_energy_efficiency_ratio", create_energy_efficiency_ratio),
        ("create_error_to_output_ratio", create_error_to_output_ratio),
        ("create_network_reliability_score", create_network_reliability_score),
        ("create_sensor_stability_index", create_sensor_stability_index),
        ("create_defect_error_interaction", create_defect_error_interaction),
        ("create_maintenance_risk", create_maintenance_risk),
    ]

    for name, func in feature_functions:
        if config is None or config.get("feature_engineering", {}).get(name, True):
            df = func(df)

    new_cols = len(df.columns) - initial_cols
    logger.info(f"Feature engineering complete! Added {new_cols} new features.")

    # Log summary statistics of new features
    engineered_cols = [
        "Energy_Efficiency_Ratio",
        "Error_to_Output_Ratio",
        "Network_Reliability_Score",
        "Sensor_Stability_Index",
        "Defect_Error_Interaction",
        "Maintenance_Risk",
    ]
    existing_eng_cols = [c for c in engineered_cols if c in df.columns]
    if existing_eng_cols:
        logger.info("\nEngineered Feature Statistics:")
        logger.info(df[existing_eng_cols].describe().to_string())

    return df
