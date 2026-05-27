"""
Data Preprocessing Module
=========================
Handles data cleaning, encoding, scaling, temporal splitting, and SMOTE oversampling
for the Manufacturing Efficiency Classification pipeline.
"""

import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import joblib
import os
import yaml

logger = logging.getLogger(__name__)


def load_config(config_path="config.yaml"):
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_data(data_path):
    """Load the manufacturing dataset from CSV."""
    logger.info(f"Loading data from {data_path}")
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def parse_datetime(df):
    """
    Parse Date and Timestamp columns into a combined datetime column.
    Sort chronologically and add time-based features.
    """
    logger.info("Parsing datetime columns...")
    df = df.copy()

    # Combine Date + Timestamp into datetime
    df["datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Timestamp"], format="%d-%m-%Y %H:%M:%S"
    )

    # Sort chronologically
    df = df.sort_values("datetime").reset_index(drop=True)

    # Extract time-based features for analysis
    df["hour"] = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.dayofweek
    df["day_of_month"] = df["datetime"].dt.day

    logger.info(
        f"Date range: {df['datetime'].min()} to {df['datetime'].max()}"
    )
    return df


def encode_features(df):
    """
    Encode categorical features:
    - One-hot encode Operation_Mode
    - Label encode Efficiency_Status (target)
    """
    logger.info("Encoding categorical features...")
    df = df.copy()

    # One-hot encode Operation_Mode
    operation_dummies = pd.get_dummies(
        df["Operation_Mode"], prefix="Mode", dtype=int
    )
    df = pd.concat([df, operation_dummies], axis=1)

    # Label encode target
    label_encoder = LabelEncoder()
    # Ensure consistent ordering: High=0, Low=1, Medium=2 -> remap to Low=0, Medium=1, High=2
    df["Efficiency_Label"] = df["Efficiency_Status"].map(
        {"Low": 0, "Medium": 1, "High": 2}
    )

    logger.info(
        f"Operation modes encoded: {operation_dummies.columns.tolist()}"
    )
    logger.info(
        f"Target distribution:\n{df['Efficiency_Label'].value_counts().sort_index()}"
    )

    return df, label_encoder


def get_feature_columns(df):
    """Get the list of feature columns for model training."""
    # Numerical features from original dataset
    numerical_features = [
        "Temperature_C",
        "Vibration_Hz",
        "Power_Consumption_kW",
        "Network_Latency_ms",
        "Packet_Loss_%",
        "Quality_Control_Defect_Rate_%",
        "Production_Speed_units_per_hr",
        "Predictive_Maintenance_Score",
        "Error_Rate_%",
    ]

    # Time features
    time_features = ["hour", "day_of_week"]

    # One-hot encoded features
    mode_features = [col for col in df.columns if col.startswith("Mode_")]

    # Engineered features (if they exist)
    engineered_features = [
        col
        for col in df.columns
        if col
        in [
            "Energy_Efficiency_Ratio",
            "Error_to_Output_Ratio",
            "Network_Reliability_Score",
            "Sensor_Stability_Index",
            "Defect_Error_Interaction",
            "Maintenance_Risk",
        ]
    ]

    all_features = (
        numerical_features + time_features + mode_features + engineered_features
    )

    # Only return features that exist in the dataframe
    available_features = [f for f in all_features if f in df.columns]
    logger.info(f"Using {len(available_features)} features for training")

    return available_features


def temporal_train_test_split(df, feature_cols, target_col, test_size=0.2):
    """
    Time-series aware split: train on older data, test on newer data.
    This simulates real deployment where the model is trained on past data
    and predicts future efficiency.
    """
    logger.info("Performing temporal train/test split...")

    # Sort by datetime (should already be sorted)
    df = df.sort_values("datetime").reset_index(drop=True)

    # Calculate split point
    split_idx = int(len(df) * (1 - test_size))
    split_date = df.iloc[split_idx]["datetime"]

    logger.info(f"Split point: index {split_idx}, date {split_date}")

    # Split
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    X_train = train_df[feature_cols].values
    X_test = test_df[feature_cols].values
    y_train = train_df[target_col].values
    y_test = test_df[target_col].values

    logger.info(
        f"Train: {len(X_train)} samples ({train_df['datetime'].min()} to {train_df['datetime'].max()})"
    )
    logger.info(
        f"Test:  {len(X_test)} samples ({test_df['datetime'].min()} to {test_df['datetime'].max()})"
    )
    logger.info(
        f"Train target distribution: {np.bincount(y_train.astype(int))}"
    )
    logger.info(
        f"Test target distribution:  {np.bincount(y_test.astype(int))}"
    )

    return X_train, X_test, y_train, y_test, split_date


def random_train_test_split(df, feature_cols, target_col, test_size=0.2, random_state=42):
    """Fallback: stratified random split."""
    logger.info("Performing stratified random train/test split...")

    X = df[feature_cols].values
    y = df[target_col].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    logger.info(f"Train: {len(X_train)} samples, Test: {len(X_test)} samples")
    return X_train, X_test, y_train, y_test, None


def scale_features(X_train, X_test, feature_names, save_dir="models"):
    """Apply StandardScaler to numerical features."""
    logger.info("Scaling features with StandardScaler...")

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save scaler
    os.makedirs(save_dir, exist_ok=True)
    scaler_path = os.path.join(save_dir, "scaler.pkl")
    joblib.dump(scaler, scaler_path)
    logger.info(f"Scaler saved to {scaler_path}")

    # Save feature names
    feature_names_path = os.path.join(save_dir, "feature_names.pkl")
    joblib.dump(feature_names, feature_names_path)
    logger.info(f"Feature names saved to {feature_names_path}")

    return X_train_scaled, X_test_scaled, scaler


def apply_smote(X_train, y_train, sampling_strategy="auto", k_neighbors=5):
    """Apply SMOTE oversampling to address class imbalance."""
    logger.info("Applying SMOTE oversampling...")
    logger.info(f"Before SMOTE - class distribution: {np.bincount(y_train.astype(int))}")

    smote = SMOTE(
        sampling_strategy=sampling_strategy,
        k_neighbors=k_neighbors,
        random_state=42,
    )
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

    logger.info(
        f"After SMOTE  - class distribution: {np.bincount(y_resampled.astype(int))}"
    )
    logger.info(
        f"Samples increased from {len(X_train)} to {len(X_resampled)}"
    )

    return X_resampled, y_resampled


def preprocess_pipeline(config_path="config.yaml"):
    """
    Run the full preprocessing pipeline.
    Returns processed data ready for model training.
    """
    config = load_config(config_path)

    # Load data
    df = load_data(config["data"]["path"])

    # Parse datetime
    df = parse_datetime(df)

    # Encode features
    df, label_encoder = encode_features(df)

    # Get feature columns
    feature_cols = get_feature_columns(df)

    # Train/test split
    if config["data"].get("temporal_split", True):
        X_train, X_test, y_train, y_test, split_date = temporal_train_test_split(
            df,
            feature_cols,
            "Efficiency_Label",
            test_size=config["data"]["test_size"],
        )
    else:
        X_train, X_test, y_train, y_test, split_date = random_train_test_split(
            df,
            feature_cols,
            "Efficiency_Label",
            test_size=config["data"]["test_size"],
            random_state=config["data"]["random_state"],
        )

    # Scale features
    X_train_scaled, X_test_scaled, scaler = scale_features(
        X_train, X_test, feature_cols, save_dir=config["paths"]["models_dir"]
    )

    # Apply SMOTE on training set only
    if config["preprocessing"]["smote"]["enabled"]:
        X_train_final, y_train_final = apply_smote(
            X_train_scaled,
            y_train,
            sampling_strategy=config["preprocessing"]["smote"]["sampling_strategy"],
            k_neighbors=config["preprocessing"]["smote"]["k_neighbors"],
        )
    else:
        X_train_final, y_train_final = X_train_scaled, y_train

    # Save label encoder mapping
    label_mapping = {"Low": 0, "Medium": 1, "High": 2}
    os.makedirs(config["paths"]["models_dir"], exist_ok=True)
    joblib.dump(
        label_mapping,
        os.path.join(config["paths"]["models_dir"], "label_encoder.pkl"),
    )

    result = {
        "X_train": X_train_final,
        "X_test": X_test_scaled,
        "y_train": y_train_final,
        "y_test": y_test,
        "feature_names": feature_cols,
        "scaler": scaler,
        "label_mapping": label_mapping,
        "split_date": split_date,
        "df": df,
    }

    logger.info("Preprocessing pipeline complete!")
    return result
