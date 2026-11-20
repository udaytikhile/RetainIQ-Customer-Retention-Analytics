"""Unit and validation tests for Machine Learning Pipeline in RetainIQ."""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.modeling import (
    get_feature_target_split,
    build_preprocessor,
    evaluate_model_at_threshold,
    compute_threshold_curve,
    run_modeling_pipeline,
    REPORT_PATH,
    FIGURES_DIR
)

DATA_PATH = Path("data/processed/telco_churn_clean.csv")


@pytest.fixture(scope="module")
def dataset():
    return pd.read_csv(DATA_PATH)


def test_feature_target_split(dataset):
    X, y, num_cols, cat_cols = get_feature_target_split(dataset)
    assert len(X) == 7043
    assert len(y) == 7043
    assert "customerID" not in X.columns
    assert "Churn" not in X.columns
    assert "ChurnBinary" not in X.columns
    assert set(num_cols) == {"tenure", "MonthlyCharges", "TotalCharges"}
    assert len(cat_cols) == 16


def test_stratified_train_test_split(dataset):
    X, y, _, _ = get_feature_target_split(dataset)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    assert len(X_train) == 5634
    assert len(X_test) == 1409
    
    # Verify exact class preservation (stratified)
    train_churn_rate = y_train.mean()
    test_churn_rate = y_test.mean()
    assert abs(train_churn_rate - 0.2654) < 0.005
    assert abs(test_churn_rate - 0.2654) < 0.005
    assert y_test.sum() == 374


def test_preprocessor_leakage_safety(dataset):
    X, y, num_cols, cat_cols = get_feature_target_split(dataset)
    X_train, X_test, _, _ = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    
    preprocessor = build_preprocessor(num_cols, cat_cols)
    
    # Fit only on train
    X_train_trans = preprocessor.fit_transform(X_train)
    # Transform test without re-fitting
    X_test_trans = preprocessor.transform(X_test)

    assert X_train_trans.shape[0] == 5634
    assert X_test_trans.shape[0] == 1409
    assert X_train_trans.shape[1] == X_test_trans.shape[1]


def test_evaluate_model_at_threshold():
    y_true = np.array([1, 1, 0, 0])
    y_proba = np.array([0.9, 0.4, 0.2, 0.8])
    metrics = evaluate_model_at_threshold(y_true, y_proba, threshold=0.5)

    assert metrics["accuracy"] == 0.5
    assert metrics["threshold"] == 0.5
    assert "confusion_matrix" in metrics
    assert metrics["confusion_matrix"]["TP"] == 1
    assert metrics["confusion_matrix"]["FP"] == 1


def test_compute_threshold_curve():
    y_true = np.array([1, 1, 0, 0, 1, 0, 1, 0])
    y_proba = np.array([0.85, 0.75, 0.1, 0.3, 0.65, 0.4, 0.9, 0.15])
    curve = compute_threshold_curve(y_true, y_proba)
    assert len(curve) > 5
    assert "Threshold" in curve.columns
    assert "Recall" in curve.columns
    assert "Precision" in curve.columns


def test_run_modeling_pipeline():
    results = run_modeling_pipeline()

    # Verify both models exceed 0.80 ROC-AUC
    lr = results["lr_eval_def"]
    gb = results["gb_eval_def"]
    assert lr["roc_auc"] >= 0.80
    assert gb["roc_auc"] >= 0.80

    # Verify PR-AUC is well above naive random baseline (0.2654)
    assert lr["pr_auc"] > 0.55
    assert gb["pr_auc"] > 0.55

    # Verify artifacts were generated
    assert REPORT_PATH.exists()
    assert (FIGURES_DIR / "roc_curve_comparison.png").exists()
    assert (FIGURES_DIR / "pr_curve_comparison.png").exists()
    assert (FIGURES_DIR / "threshold_tradeoffs.png").exists()
    assert (FIGURES_DIR / "confusion_matrices.png").exists()
    assert Path("data/processed/telco_churn_scored.csv").exists()
