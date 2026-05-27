"""
Training Pipeline Orchestrator
===============================
End-to-end script that runs the full ML pipeline:
Load Data → Preprocess → Feature Engineering → Hyperparameter Tuning →
Model Training → Evaluation → Explainability → Report Generation

Usage:
    python train.py
    python train.py --no-tune        (skip hyperparameter tuning)
    python train.py --config custom.yaml
"""

import os
import sys
import argparse
import logging
import time
import yaml
import joblib
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("training.log", mode="w"),
    ],
)
logger = logging.getLogger("train")

# Import pipeline modules
from src.preprocessing import load_config, load_data, parse_datetime, encode_features, get_feature_columns, temporal_train_test_split, random_train_test_split, scale_features, apply_smote
from src.feature_engineering import engineer_all_features
from src.model_training import (
    build_models,
    train_and_evaluate,
    select_best_model,
    save_model,
    save_all_models,
    plot_confusion_matrices,
    plot_learning_curves,
    save_comparison_table,
    save_classification_reports,
)
from src.hyperparameter_tuning import tune_models, build_tuned_models
from src.explainability import run_explainability_pipeline
from src.report_generator import generate_report


def main(config_path="config.yaml", skip_tuning=False):
    """Run the complete training pipeline."""
    start_time = time.time()

    logger.info("=" * 70)
    logger.info("  AI-Based Manufacturing Efficiency Classification")
    logger.info("  Training Pipeline Started")
    logger.info("=" * 70)

    # ──────────────────────────────────────────────────────
    # Step 1: Load Configuration
    # ──────────────────────────────────────────────────────
    logger.info("\n[STEP 1] Loading Configuration")
    config = load_config(config_path)
    logger.info(f"Config loaded from {config_path}")

    # Create output directories
    os.makedirs(config["paths"]["models_dir"], exist_ok=True)
    os.makedirs(config["paths"]["outputs_dir"], exist_ok=True)

    # ──────────────────────────────────────────────────────
    # Step 2: Load & Parse Data
    # ──────────────────────────────────────────────────────
    logger.info("\n[STEP 2] Loading and Parsing Data")
    df = load_data(config["data"]["path"])
    df = parse_datetime(df)
    logger.info(f"Dataset: {len(df)} rows, {len(df.columns)} columns")

    # ──────────────────────────────────────────────────────
    # Step 3: Feature Engineering
    # ──────────────────────────────────────────────────────
    logger.info("\n[STEP 3] Feature Engineering")
    df = engineer_all_features(df, config)

    # ──────────────────────────────────────────────────────
    # Step 4: Encode & Prepare Features
    # ──────────────────────────────────────────────────────
    logger.info("\n[STEP 4] Encoding Features")
    df, label_encoder = encode_features(df)
    feature_cols = get_feature_columns(df)
    logger.info(f"Feature columns ({len(feature_cols)}): {feature_cols}")

    # ──────────────────────────────────────────────────────
    # Step 5: Train/Test Split
    # ──────────────────────────────────────────────────────
    logger.info("\n[STEP 5] Train/Test Split")
    if config["data"].get("temporal_split", True):
        X_train, X_test, y_train, y_test, split_date = temporal_train_test_split(
            df, feature_cols, "Efficiency_Label",
            test_size=config["data"]["test_size"],
        )
        logger.info(f"Temporal split at {split_date}")
    else:
        X_train, X_test, y_train, y_test, split_date = random_train_test_split(
            df, feature_cols, "Efficiency_Label",
            test_size=config["data"]["test_size"],
            random_state=config["data"]["random_state"],
        )

    # ──────────────────────────────────────────────────────
    # Step 6: Scale Features
    # ──────────────────────────────────────────────────────
    logger.info("\n[STEP 6] Scaling Features")
    X_train_scaled, X_test_scaled, scaler = scale_features(
        X_train, X_test, feature_cols,
        save_dir=config["paths"]["models_dir"],
    )

    # ──────────────────────────────────────────────────────
    # Step 7: SMOTE Oversampling
    # ──────────────────────────────────────────────────────
    logger.info("\n[STEP 7] SMOTE Oversampling")
    if config["preprocessing"]["smote"]["enabled"]:
        X_train_final, y_train_final = apply_smote(
            X_train_scaled, y_train,
            sampling_strategy=config["preprocessing"]["smote"]["sampling_strategy"],
            k_neighbors=config["preprocessing"]["smote"]["k_neighbors"],
        )
    else:
        X_train_final, y_train_final = X_train_scaled, y_train
        logger.info("SMOTE disabled, using original training data")

    # Save label mapping
    label_mapping = {"Low": 0, "Medium": 1, "High": 2}
    joblib.dump(label_mapping, os.path.join(config["paths"]["models_dir"], "label_encoder.pkl"))

    # ──────────────────────────────────────────────────────
    # Step 8: Hyperparameter Tuning (Optional)
    # ──────────────────────────────────────────────────────
    tuned_models = {}
    if not skip_tuning and config["tuning"]["enabled"]:
        logger.info("\n[STEP 8] Hyperparameter Tuning with Optuna")
        tuning_results = tune_models(X_train_final, y_train_final, config)

        # Build tuned models
        tuned_models = build_tuned_models(tuning_results, config)
        logger.info(f"Tuned models built: {list(tuned_models.keys())}")
    else:
        logger.info("\n[STEP 8] Skipping Hyperparameter Tuning")

    # ──────────────────────────────────────────────────────
    # Step 9: Model Training & Evaluation
    # ──────────────────────────────────────────────────────
    logger.info("\n[STEP 9] Model Training & Evaluation")

    # Build baseline models
    baseline_models = build_models(config)

    # Combine baseline + tuned models
    all_models = {**baseline_models, **tuned_models}
    logger.info(f"Training {len(all_models)} models: {list(all_models.keys())}")

    # Train and evaluate
    results, trained_models = train_and_evaluate(
        all_models, X_train_final, X_test_scaled, y_train_final, y_test, config
    )

    # ──────────────────────────────────────────────────────
    # Step 10: Select Best Model
    # ──────────────────────────────────────────────────────
    logger.info("\n[STEP 10] Selecting Best Model")
    best_name, best_model, best_score = select_best_model(
        results, trained_models, metric=config["evaluation"]["primary_metric"]
    )

    # Save models
    save_model(best_model, best_name, save_dir=config["paths"]["models_dir"])
    save_all_models(trained_models, save_dir=config["paths"]["models_dir"])

    # ──────────────────────────────────────────────────────
    # Step 11: Visualization & Reports
    # ──────────────────────────────────────────────────────
    logger.info("\n[STEP 11] Generating Visualizations")
    plot_confusion_matrices(results, save_dir=config["paths"]["outputs_dir"])

    # Learning curves for best model
    plot_learning_curves(
        best_model, best_name, X_train_final, y_train_final,
        save_dir=config["paths"]["outputs_dir"],
    )

    # Save comparison table
    comparison_df = save_comparison_table(results, save_dir=config["paths"]["outputs_dir"])
    save_classification_reports(results, save_dir=config["paths"]["outputs_dir"])

    # ──────────────────────────────────────────────────────
    # Step 12: SHAP Explainability
    # ──────────────────────────────────────────────────────
    logger.info("\n[STEP 12] SHAP Explainability Analysis")
    explainer, importance_df, shap_values = run_explainability_pipeline(
        best_model, best_name,
        X_train_final, X_test_scaled, feature_cols,
        save_dir=config["paths"]["outputs_dir"],
    )

    # ──────────────────────────────────────────────────────
    # Step 13: PDF Executive Report
    # ──────────────────────────────────────────────────────
    logger.info("\n[STEP 13] Generating PDF Executive Report")
    try:
        report_path = generate_report(
            df, comparison_df, best_name, importance_df,
            save_dir=config["paths"]["outputs_dir"],
        )
        logger.info(f"PDF report saved to {report_path}")
    except Exception as e:
        logger.warning(f"PDF report generation failed: {e}")

    # ──────────────────────────────────────────────────────
    # Summary
    # ──────────────────────────────────────────────────────
    elapsed = time.time() - start_time
    logger.info("\n" + "=" * 70)
    logger.info("  TRAINING PIPELINE COMPLETE")
    logger.info("=" * 70)
    logger.info(f"  Total time:       {elapsed:.1f}s ({elapsed/60:.1f} min)")
    logger.info(f"  Best model:       {best_name}")
    logger.info(f"  Best F1 (macro):  {best_score:.4f}")
    logger.info(f"  Models saved to:  {config['paths']['models_dir']}/")
    logger.info(f"  Outputs saved to: {config['paths']['outputs_dir']}/")
    logger.info(f"  Top 3 features:   {', '.join(importance_df.head(3)['Feature'].tolist())}")
    logger.info("=" * 70)

    return results, best_name, best_model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train Manufacturing Efficiency Classification Models"
    )
    parser.add_argument(
        "--config", type=str, default="config.yaml",
        help="Path to configuration YAML file",
    )
    parser.add_argument(
        "--no-tune", action="store_true",
        help="Skip hyperparameter tuning (faster)",
    )
    args = parser.parse_args()

    main(config_path=args.config, skip_tuning=args.no_tune)
