"""
Model Training Module
=====================
Trains and evaluates multiple classifiers for manufacturing efficiency
classification. Compares Logistic Regression, Random Forest, and XGBoost.
"""

import numpy as np
import pandas as pd
import logging
import os
import joblib
import json
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold, learning_curve
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from xgboost import XGBClassifier
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

# Class label mapping
CLASS_NAMES = ["Low", "Medium", "High"]


def build_models(config):
    """Initialize all models with configuration parameters."""
    models = {}

    # Logistic Regression
    lr_config = config["models"]["logistic_regression"]
    models["Logistic Regression"] = LogisticRegression(
        max_iter=lr_config["max_iter"],
        class_weight=lr_config["class_weight"],
        solver=lr_config["solver"],
        random_state=config["data"]["random_state"],
        n_jobs=-1,
    )

    # Random Forest
    rf_config = config["models"]["random_forest"]
    models["Random Forest"] = RandomForestClassifier(
        n_estimators=rf_config["n_estimators"],
        max_depth=rf_config["max_depth"],
        min_samples_split=rf_config["min_samples_split"],
        min_samples_leaf=rf_config["min_samples_leaf"],
        class_weight=rf_config["class_weight"],
        random_state=config["data"]["random_state"],
        n_jobs=rf_config["n_jobs"],
    )

    # XGBoost
    xgb_config = config["models"]["xgboost"]
    models["XGBoost"] = XGBClassifier(
        n_estimators=xgb_config["n_estimators"],
        max_depth=xgb_config["max_depth"],
        learning_rate=xgb_config["learning_rate"],
        subsample=xgb_config["subsample"],
        colsample_bytree=xgb_config["colsample_bytree"],
        objective=xgb_config["objective"],
        num_class=xgb_config["num_class"],
        eval_metric=xgb_config["eval_metric"],
        use_label_encoder=False,
        random_state=config["data"]["random_state"],
        n_jobs=-1,
        verbosity=0,
    )

    return models


def train_and_evaluate(models, X_train, X_test, y_train, y_test, config):
    """
    Train all models and evaluate on test set.
    Returns results dict and the best model.
    """
    results = {}
    trained_models = {}

    for name, model in models.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Training: {name}")
        logger.info(f"{'='*60}")

        # Train
        model.fit(X_train, y_train)
        trained_models[name] = model

        # Predict
        y_pred = model.predict(X_test)
        y_pred_proba = None
        if hasattr(model, "predict_proba"):
            y_pred_proba = model.predict_proba(X_test)

        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1_macro = f1_score(y_test, y_pred, average="macro")
        f1_weighted = f1_score(y_test, y_pred, average="weighted")
        precision_macro = precision_score(y_test, y_pred, average="macro", zero_division=0)
        recall_macro = recall_score(y_test, y_pred, average="macro", zero_division=0)

        # Cross-validation on training set
        cv = StratifiedKFold(
            n_splits=config["evaluation"]["cv_folds"],
            shuffle=True,
            random_state=config["data"]["random_state"],
        )
        cv_scores = cross_val_score(
            model, X_train, y_train, cv=cv, scoring="f1_macro", n_jobs=-1
        )

        # Classification report
        report = classification_report(
            y_test, y_pred, target_names=CLASS_NAMES, zero_division=0
        )

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)

        results[name] = {
            "accuracy": accuracy,
            "f1_macro": f1_macro,
            "f1_weighted": f1_weighted,
            "precision_macro": precision_macro,
            "recall_macro": recall_macro,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "classification_report": report,
            "confusion_matrix": cm,
            "y_pred": y_pred,
            "y_pred_proba": y_pred_proba,
        }

        logger.info(f"Accuracy:       {accuracy:.4f}")
        logger.info(f"Macro F1:       {f1_macro:.4f}")
        logger.info(f"Weighted F1:    {f1_weighted:.4f}")
        logger.info(f"Precision:      {precision_macro:.4f}")
        logger.info(f"Recall:         {recall_macro:.4f}")
        logger.info(f"CV F1 (mean):   {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        logger.info(f"\nClassification Report:\n{report}")
        logger.info(f"Confusion Matrix:\n{cm}")

    return results, trained_models


def select_best_model(results, trained_models, metric="f1_macro"):
    """Select the best model based on the specified metric."""
    best_name = max(results, key=lambda k: results[k][metric])
    best_model = trained_models[best_name]
    best_score = results[best_name][metric]

    logger.info(f"\n{'='*60}")
    logger.info(f"BEST MODEL: {best_name} ({metric}: {best_score:.4f})")
    logger.info(f"{'='*60}")

    return best_name, best_model, best_score


def save_model(model, model_name, save_dir="models"):
    """Save the best model to disk."""
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, "best_model.pkl")
    joblib.dump(model, model_path)

    # Also save model name
    meta_path = os.path.join(save_dir, "model_meta.json")
    with open(meta_path, "w") as f:
        json.dump({"best_model_name": model_name}, f)

    logger.info(f"Best model ({model_name}) saved to {model_path}")
    return model_path


def save_all_models(trained_models, save_dir="models"):
    """Save all trained models for comparison in dashboard."""
    os.makedirs(save_dir, exist_ok=True)
    for name, model in trained_models.items():
        safe_name = name.lower().replace(" ", "_")
        path = os.path.join(save_dir, f"{safe_name}.pkl")
        joblib.dump(model, path)
        logger.info(f"Saved {name} to {path}")


def plot_confusion_matrices(results, save_dir="outputs"):
    """Plot confusion matrices for all models side by side."""
    os.makedirs(save_dir, exist_ok=True)

    n_models = len(results)
    fig, axes = plt.subplots(1, n_models, figsize=(7 * n_models, 6))
    if n_models == 1:
        axes = [axes]

    for ax, (name, res) in zip(axes, results.items()):
        cm = res["confusion_matrix"]
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=CLASS_NAMES,
            yticklabels=CLASS_NAMES,
            ax=ax,
            cbar_kws={"shrink": 0.8},
        )
        ax.set_title(f"{name}\nAccuracy: {res['accuracy']:.4f} | F1: {res['f1_macro']:.4f}", fontsize=12)
        ax.set_ylabel("Actual")
        ax.set_xlabel("Predicted")

    plt.tight_layout()
    path = os.path.join(save_dir, "confusion_matrices.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Confusion matrices saved to {path}")


def plot_learning_curves(model, model_name, X_train, y_train, save_dir="outputs"):
    """Plot learning curves to check for overfitting."""
    os.makedirs(save_dir, exist_ok=True)

    train_sizes, train_scores, val_scores = learning_curve(
        model,
        X_train,
        y_train,
        cv=3,
        scoring="f1_macro",
        train_sizes=np.linspace(0.1, 1.0, 10),
        n_jobs=-1,
        random_state=42,
    )

    train_mean = train_scores.mean(axis=1)
    train_std = train_scores.std(axis=1)
    val_mean = val_scores.mean(axis=1)
    val_std = val_scores.std(axis=1)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color="blue")
    ax.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.1, color="orange")
    ax.plot(train_sizes, train_mean, "o-", color="blue", label="Training Score")
    ax.plot(train_sizes, val_mean, "o-", color="orange", label="Validation Score")
    ax.set_xlabel("Training Set Size")
    ax.set_ylabel("Macro F1 Score")
    ax.set_title(f"Learning Curve - {model_name}")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)

    path = os.path.join(save_dir, "learning_curves.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Learning curves saved to {path}")


def save_comparison_table(results, save_dir="outputs"):
    """Save model comparison as CSV."""
    os.makedirs(save_dir, exist_ok=True)

    rows = []
    for name, res in results.items():
        rows.append(
            {
                "Model": name,
                "Accuracy": round(res["accuracy"], 4),
                "Macro F1": round(res["f1_macro"], 4),
                "Weighted F1": round(res["f1_weighted"], 4),
                "Precision": round(res["precision_macro"], 4),
                "Recall": round(res["recall_macro"], 4),
                "CV F1 Mean": round(res["cv_mean"], 4),
                "CV F1 Std": round(res["cv_std"], 4),
            }
        )

    df = pd.DataFrame(rows)
    path = os.path.join(save_dir, "model_comparison.csv")
    df.to_csv(path, index=False)
    logger.info(f"Model comparison saved to {path}")
    logger.info(f"\n{df.to_string(index=False)}")

    return df


def save_classification_reports(results, save_dir="outputs"):
    """Save detailed classification reports to text file."""
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, "classification_reports.txt")

    with open(path, "w") as f:
        for name, res in results.items():
            f.write(f"{'='*60}\n")
            f.write(f"Model: {name}\n")
            f.write(f"{'='*60}\n")
            f.write(f"Accuracy: {res['accuracy']:.4f}\n")
            f.write(f"Macro F1: {res['f1_macro']:.4f}\n")
            f.write(f"\n{res['classification_report']}\n\n")

    logger.info(f"Classification reports saved to {path}")
