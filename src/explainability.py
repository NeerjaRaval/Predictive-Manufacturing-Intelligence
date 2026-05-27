"""
Explainability Module
=====================
Provides SHAP-based model explanations for manufacturing efficiency predictions.
Includes global feature importance, per-prediction explanations, and narrative generation.
"""

import numpy as np
import pandas as pd
import logging
import os
import joblib
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

CLASS_NAMES = ["Low", "Medium", "High"]


def create_explainer(model, X_train, model_name=""):
    """
    Create a SHAP explainer appropriate for the model type.
    Uses TreeExplainer for tree-based models, KernelExplainer otherwise.
    """
    logger.info(f"Creating SHAP explainer for {model_name}...")

    try:
        # TreeExplainer for Random Forest / XGBoost
        explainer = shap.TreeExplainer(model)
        logger.info("Using TreeExplainer")
    except Exception:
        # Fallback to KernelExplainer (slower)
        logger.info("TreeExplainer failed, falling back to KernelExplainer")
        background = shap.sample(X_train, min(100, len(X_train)))
        explainer = shap.KernelExplainer(model.predict_proba, background)

    return explainer


def compute_shap_values(explainer, X, max_samples=1000):
    """
    Compute SHAP values for the given data.
    Limits samples for performance on large datasets.
    """
    if len(X) > max_samples:
        logger.info(f"Sampling {max_samples} from {len(X)} for SHAP computation")
        indices = np.random.RandomState(42).choice(len(X), max_samples, replace=False)
        X_sample = X[indices]
    else:
        X_sample = X
        indices = np.arange(len(X))

    logger.info(f"Computing SHAP values for {len(X_sample)} samples...")
    shap_values = explainer.shap_values(X_sample)

    return shap_values, X_sample, indices


def get_global_feature_importance(shap_values, feature_names):
    """
    Calculate global feature importance as mean |SHAP| across all classes.
    Returns a DataFrame sorted by importance.
    """
    # shap_values is a list of arrays (one per class) or a 3D array
    if isinstance(shap_values, list):
        # Average across classes
        mean_abs_shap = np.mean(
            [np.abs(sv).mean(axis=0) for sv in shap_values], axis=0
        )
    else:
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        if mean_abs_shap.ndim > 1:
            mean_abs_shap = mean_abs_shap.mean(axis=-1)

    importance_df = pd.DataFrame(
        {"Feature": feature_names, "Importance": mean_abs_shap}
    ).sort_values("Importance", ascending=False)

    return importance_df


def plot_global_importance(importance_df, save_dir="outputs", top_n=15):
    """Plot global feature importance bar chart."""
    os.makedirs(save_dir, exist_ok=True)

    top = importance_df.head(top_n)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top)))
    bars = ax.barh(
        range(len(top)),
        top["Importance"].values[::-1],
        color=colors,
    )
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["Feature"].values[::-1])
    ax.set_xlabel("Mean |SHAP Value|")
    ax.set_title("Global Feature Importance (SHAP)")
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    path = os.path.join(save_dir, "feature_importance.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Feature importance plot saved to {path}")
    return path


def explain_single_prediction(
    model, explainer, X_single, feature_names, class_names=CLASS_NAMES
):
    """
    Explain a single prediction with SHAP values and natural language.
    
    Returns:
        dict with prediction, confidence, top features, and narrative text
    """
    # Get prediction
    prediction = model.predict(X_single.reshape(1, -1))[0]
    probabilities = model.predict_proba(X_single.reshape(1, -1))[0]
    predicted_class = class_names[int(prediction)]

    # Get SHAP values for this instance
    shap_vals = explainer.shap_values(X_single.reshape(1, -1))

    # Get SHAP values for predicted class
    if isinstance(shap_vals, list):
        sv = shap_vals[int(prediction)][0]
    else:
        sv = shap_vals[0]
        if sv.ndim > 1:
            sv = sv[:, int(prediction)]

    # Top contributing features
    feature_contributions = pd.DataFrame(
        {
            "Feature": feature_names,
            "SHAP_Value": sv,
            "Feature_Value": X_single,
            "Abs_SHAP": np.abs(sv),
        }
    ).sort_values("Abs_SHAP", ascending=False)

    top_3 = feature_contributions.head(3)

    # Generate narrative
    narrative = generate_narrative(predicted_class, top_3, probabilities)

    return {
        "predicted_class": predicted_class,
        "prediction_idx": int(prediction),
        "probabilities": {cn: round(float(p), 4) for cn, p in zip(class_names, probabilities)},
        "confidence": round(float(probabilities[int(prediction)]) * 100, 1),
        "top_features": top_3.to_dict("records"),
        "all_contributions": feature_contributions,
        "narrative": narrative,
    }


def generate_narrative(predicted_class, top_features, probabilities):
    """
    Auto-generate a human-readable explanation of the prediction.
    Example: "Efficiency is Low because Error_Rate is 14.9% (high)
             and Production_Speed is 89 units/hr (low)"
    """
    confidence = max(probabilities) * 100

    parts = [
        f"The manufacturing efficiency is classified as **{predicted_class}** "
        f"with {confidence:.1f}% confidence."
    ]

    parts.append("\n\n**Key factors driving this classification:**\n")

    for i, row in top_features.iterrows():
        feature = row["Feature"]
        shap_val = row["SHAP_Value"]
        feat_val = row["Feature_Value"]
        direction = "increasing" if shap_val > 0 else "decreasing"
        impact = "positively" if shap_val > 0 else "negatively"

        # Clean feature name for display
        display_name = feature.replace("_", " ").replace("%", "pct")

        parts.append(
            f"- **{display_name}** (value: {feat_val:.3f}) is {impact} "
            f"influencing the prediction, {direction} the likelihood of "
            f"{predicted_class} efficiency."
        )

    return "\n".join(parts)


def run_explainability_pipeline(model, model_name, X_train, X_test, feature_names, save_dir="outputs"):
    """
    Run the full explainability pipeline.
    Returns explainer and importance dataframe for use in dashboard.
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Running SHAP Explainability for {model_name}")
    logger.info(f"{'='*60}")

    # Create explainer
    explainer = create_explainer(model, X_train, model_name)

    # Compute SHAP values on test set
    shap_values, X_sample, indices = compute_shap_values(explainer, X_test)

    # Global importance
    importance_df = get_global_feature_importance(shap_values, feature_names)
    logger.info(f"\nTop 10 Most Important Features:")
    logger.info(importance_df.head(10).to_string(index=False))

    # Plot
    plot_global_importance(importance_df, save_dir)

    # Save explainer and SHAP values
    models_dir = save_dir.replace("outputs", "models")
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(explainer, os.path.join(models_dir, "shap_explainer.pkl"))
    joblib.dump(shap_values, os.path.join(models_dir, "shap_values.pkl"))
    joblib.dump(importance_df, os.path.join(models_dir, "feature_importance.pkl"))

    logger.info("Explainability pipeline complete!")

    return explainer, importance_df, shap_values
