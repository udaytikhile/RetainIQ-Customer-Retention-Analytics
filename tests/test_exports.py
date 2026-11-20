"""Unit tests for Power BI Export Tables and Operational Queue in RetainIQ."""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from src.export_power_bi import build_power_bi_tables, EXPORTS_DIR


def test_build_power_bi_tables():
    """Verify all export CSVs are created with proper schemas and row counts."""
    tables = build_power_bi_tables()

    assert EXPORTS_DIR.exists()
    assert (EXPORTS_DIR / "fact_customer_retention.csv").exists()
    assert (EXPORTS_DIR / "power_bi_executive_overview.csv").exists()
    assert (EXPORTS_DIR / "power_bi_churn_drivers.csv").exists()
    assert (EXPORTS_DIR / "power_bi_segments_cohorts.csv").exists()
    assert (EXPORTS_DIR / "power_bi_retention_prioritization.csv").exists()

    fact = tables["fact_table"]
    queue = tables["retention_queue"]
    overview = tables["exec_overview"]
    drivers = tables["cat_drivers"]
    segments = tables["segments_summary"]

    # 1. Row counts & integrity
    assert len(fact) == 7043
    assert len(queue) == 7043
    assert fact.isna().sum().sum() == 0
    assert queue.isna().sum().sum() == 0

    # 2. Executive Overview has 9 combinations (3 Contracts x 3 InternetServices)
    assert len(overview) == 9
    assert overview["total_customers"].sum() == 7043
    assert overview["churned_customers"].sum() == 1869

    # 3. Churn Drivers has 16 categorical dimensions
    assert len(drivers) == 16
    assert "Cramers_V" in drivers.columns
    assert drivers.iloc[0]["Feature"] == "Contract"

    # 4. Segments Summary has 4 quadrants
    assert len(segments) == 4
    assert segments["customer_count"].sum() == 7043

    # 5. Queue contains essential operational prioritization fields
    required_queue_cols = [
        "customerID", "PredictedRiskTier", "PredictedChurnProbability",
        "MonthlyCharges", "tenure", "Contract", "RecommendedRetentionPlay"
    ]
    for col in required_queue_cols:
        assert col in queue.columns

    # Verify probabilities are valid
    assert queue["PredictedChurnProbability"].min() >= 0.0
    assert queue["PredictedChurnProbability"].max() <= 1.0

    # Verify recommended retention plays are assigned to all rows
    assert queue["RecommendedRetentionPlay"].notna().all()
    assert len(queue["RecommendedRetentionPlay"].unique()) >= 4
