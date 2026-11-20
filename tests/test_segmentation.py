"""Unit tests for Customer Segmentation and Mart Enrichment in RetainIQ."""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from src.segmentation import (
    assign_tenure_cohort,
    compute_service_breadth,
    assign_value_risk_quadrant,
    enrich_customer_mart,
    profile_segments,
    run_segmentation_pipeline,
    ENRICHED_CSV_PATH,
    FIGURES_DIR
)

CLEAN_CSV = Path("data/processed/telco_churn_clean.csv")


@pytest.fixture(scope="module")
def clean_data():
    return pd.read_csv(CLEAN_CSV)


def test_tenure_cohort_mapping():
    assert assign_tenure_cohort(0) == "01. Onboarding (0-6m)"
    assert assign_tenure_cohort(6) == "01. Onboarding (0-6m)"
    assert assign_tenure_cohort(12) == "02. Nurture (7-12m)"
    assert assign_tenure_cohort(24) == "03. Established (13-24m)"
    assert assign_tenure_cohort(48) == "04. Mature (25-48m)"
    assert assign_tenure_cohort(72) == "05. Loyalist (49-72m)"


def test_service_breadth_calculation():
    row_all_yes = pd.Series({
        "OnlineSecurity": "Yes",
        "OnlineBackup": "Yes",
        "DeviceProtection": "Yes",
        "TechSupport": "Yes",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes"
    })
    assert compute_service_breadth(row_all_yes) == 6

    row_none = pd.Series({
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No"
    })
    assert compute_service_breadth(row_none) == 0


def test_value_risk_quadrant_logic():
    assert "VIP Flight Risk" in assign_value_risk_quadrant(85.0, "Month-to-month")
    assert "Core Champions" in assign_value_risk_quadrant(85.0, "Two year")
    assert "Transactional Vulnerable" in assign_value_risk_quadrant(45.0, "Month-to-month")
    assert "Stable Base" in assign_value_risk_quadrant(45.0, "One year")


def test_enrich_customer_mart(clean_data):
    mart = enrich_customer_mart(clean_data)
    assert len(mart) == 7043
    assert "ValueRiskQuadrant" in mart.columns
    assert "TenureCohort" in mart.columns
    assert "ServiceBreadth" in mart.columns

    # Verify all 4 quadrants present
    quadrants = mart["ValueRiskQuadrant"].unique()
    assert len(quadrants) == 4

    # Verify ServiceBreadth ranges from 0 to 6
    assert mart["ServiceBreadth"].min() == 0
    assert mart["ServiceBreadth"].max() == 6


def test_profile_segments_financial_reconciliation(clean_data):
    mart = enrich_customer_mart(clean_data)
    profiles = profile_segments(mart)

    # Reconcile customer volume
    assert profiles["customer_count"].sum() == 7043
    assert profiles["churn_count"].sum() == 1869

    # Reconcile MRR
    assert np.isclose(profiles["total_monthly_charges"].sum(), 456116.60, atol=1e-2)
    assert np.isclose(profiles["churned_monthly_charges"].sum(), 139130.85, atol=1e-2)

    # Verify Q1 concentrates majority of churned charges
    q1 = profiles[profiles["ValueRiskQuadrant"].str.contains("VIP Flight Risk")].iloc[0]
    assert q1["customer_count"] == 2104
    assert q1["churn_count"] == 1111
    assert q1["churn_rate_pct"] == 52.80
    assert q1["churned_monthly_charges"] == 96996.80
    assert q1["share_of_churned_mrc_pct"] > 69.0


def test_run_segmentation_pipeline_execution():
    mart, profiles = run_segmentation_pipeline()
    assert ENRICHED_CSV_PATH.exists()
    assert (FIGURES_DIR / "segmentation_value_risk_quadrant.png").exists()
    assert (FIGURES_DIR / "tenure_cohort_waterfall.png").exists()
    assert (FIGURES_DIR / "service_breadth_churn_rate.png").exists()
