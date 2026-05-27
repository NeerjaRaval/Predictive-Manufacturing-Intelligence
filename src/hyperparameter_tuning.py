"""
Hyperparameter Tuning Module
=============================
Uses Optuna for automated Bayesian hyperparameter optimization
of Random Forest and XGBoost classifiers.
"""

import numpy as np
import logging
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from xgboost import XGBClassifier
import optuna
from optuna.samplers import TPESampler

# Suppress Optuna's verbose logging
optuna.logging.set_verbosity(optuna.logging.WARNING)

logger = logging.getLogger(__name__)


def create_rf_objective(X_train, y_train, cv_folds=3, random_state=42):
    """Create Optuna objective function for Random Forest."""

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
            "max_depth": trial.suggest_int("max_depth", 5, 30),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
            "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
            "class_weight": trial.suggest_categorical(
                "class_weight", ["balanced", "balanced_subsample"]
            ),
        }

        model = RandomForestClassifier(
            **params, random_state=random_state, n_jobs=-1
        )

        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
        scores = cross_val_score(
            model, X_train, y_train, cv=cv, scoring="f1_macro", n_jobs=-1
        )

        return scores.mean()

    return objective


def create_xgb_objective(X_train, y_train, cv_folds=3, random_state=42):
    """Create Optuna objective function for XGBoost."""

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
            "max_depth": trial.suggest_int("max_depth", 3, 15),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "gamma": trial.suggest_float("gamma", 0, 5),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10, log=True),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        }

        model = XGBClassifier(
            **params,
            objective="multi:softprob",
            num_class=3,
            eval_metric="mlogloss",
            use_label_encoder=False,
            random_state=random_state,
            n_jobs=-1,
            verbosity=0,
        )

        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
        scores = cross_val_score(
            model, X_train, y_train, cv=cv, scoring="f1_macro", n_jobs=-1
        )

        return scores.mean()

    return objective


def tune_models(X_train, y_train, config):
    """
    Run Optuna hyperparameter tuning for Random Forest and XGBoost.
    Returns best parameters for each model.
    """
    tuning_config = config["tuning"]
    n_trials = tuning_config["n_trials"]
    timeout = tuning_config["timeout"]
    cv_folds = tuning_config["cv_folds"]
    random_state = config["data"]["random_state"]

    results = {}

    # Tune Random Forest
    logger.info(f"\n{'='*60}")
    logger.info(f"Tuning Random Forest ({n_trials} trials, {timeout}s timeout)")
    logger.info(f"{'='*60}")

    rf_study = optuna.create_study(
        direction="maximize",
        sampler=TPESampler(seed=random_state),
        study_name="random_forest_tuning",
    )
    rf_objective = create_rf_objective(X_train, y_train, cv_folds, random_state)
    rf_study.optimize(rf_objective, n_trials=n_trials, timeout=timeout, show_progress_bar=True)

    logger.info(f"RF Best F1 (macro): {rf_study.best_value:.4f}")
    logger.info(f"RF Best Params: {rf_study.best_params}")

    results["Random Forest"] = {
        "best_params": rf_study.best_params,
        "best_score": rf_study.best_value,
        "study": rf_study,
    }

    # Tune XGBoost
    logger.info(f"\n{'='*60}")
    logger.info(f"Tuning XGBoost ({n_trials} trials, {timeout}s timeout)")
    logger.info(f"{'='*60}")

    xgb_study = optuna.create_study(
        direction="maximize",
        sampler=TPESampler(seed=random_state),
        study_name="xgboost_tuning",
    )
    xgb_objective = create_xgb_objective(X_train, y_train, cv_folds, random_state)
    xgb_study.optimize(xgb_objective, n_trials=n_trials, timeout=timeout, show_progress_bar=True)

    logger.info(f"XGB Best F1 (macro): {xgb_study.best_value:.4f}")
    logger.info(f"XGB Best Params: {xgb_study.best_params}")

    results["XGBoost"] = {
        "best_params": xgb_study.best_params,
        "best_score": xgb_study.best_value,
        "study": xgb_study,
    }

    # Save tuning results
    save_dir = config["paths"]["models_dir"]
    os.makedirs(save_dir, exist_ok=True)
    tuning_path = os.path.join(save_dir, "tuning_results.pkl")
    joblib.dump(results, tuning_path)
    logger.info(f"Tuning results saved to {tuning_path}")

    return results


def build_tuned_models(tuning_results, config):
    """Build models with the best hyperparameters from tuning."""
    random_state = config["data"]["random_state"]
    tuned_models = {}

    # Tuned Random Forest
    rf_params = tuning_results["Random Forest"]["best_params"]
    tuned_models["Random Forest (Tuned)"] = RandomForestClassifier(
        **rf_params, random_state=random_state, n_jobs=-1
    )

    # Tuned XGBoost
    xgb_params = tuning_results["XGBoost"]["best_params"]
    tuned_models["XGBoost (Tuned)"] = XGBClassifier(
        **xgb_params,
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        use_label_encoder=False,
        random_state=random_state,
        n_jobs=-1,
        verbosity=0,
    )

    return tuned_models
