"""Unit and Integration tests for Business Metrics and SQL Analytical Mart."""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from src.metrics import calculate_reconciled_kpis, calculate_breakdowns
from src.db import initialize_database, parse_queries, execute_all_queries, DB_PATH, SCHEMA_PATH, QUERIES_PATH

CLEAN_CSV = Path("data/processed/telco_churn_clean.csv")


@pytest.fixture(scope="module")
def clean_data():
    """Load pre-cleaned telco data."""
    return pd.read_csv(CLEAN_CSV)


def test_business_metrics_kpis(clean_data):
    """Test exact mathematical reconciliation of core business KPIs."""
    kpis = calculate_reconciled_kpis(clean_data)

    # 1. Volume verification
    assert kpis["customer_count"] == 7043
    assert kpis["retained_customer_count"] == 5174
    assert kpis["churn_customer_count"] == 1869
    assert kpis["churn_rate_pct"] == 26.54
    assert kpis["customer_count"] == kpis["retained_customer_count"] + kpis["churn_customer_count"]

    # 2. Tenure verification
    assert round(kpis["tenure"]["avg_overall_months"], 1) == 32.4
    assert kpis["tenure"]["median_churned_months"] == 10.0
    assert kpis["tenure"]["median_retained_months"] == 38.0

    # 3. Financial balance-sheet verification
    fin = kpis["financials"]
    assert fin["total_monthly_contracted_charges"] == 456116.60
    assert fin["retained_monthly_recurring_charges"] == 316985.75
    assert fin["historical_monthly_charges_churned_base"] == 139130.85
    assert np.isclose(
        fin["total_monthly_contracted_charges"],
        fin["retained_monthly_recurring_charges"] + fin["historical_monthly_charges_churned_base"],
        atol=1e-2
    )
    assert fin["churned_monthly_charges_share_pct"] == 30.50


def test_breakdown_metrics(clean_data):
    """Test multi-dimensional metric aggregations."""
    breakdowns = calculate_breakdowns(clean_data)
    assert "by_contract" in breakdowns
    assert "by_tenure_cohort" in breakdowns
    
    contract_df = breakdowns["by_contract"]
    assert len(contract_df) == 3
    assert set(contract_df["Contract"]) == {"Month-to-month", "One year", "Two year"}
    assert contract_df["total_customers"].sum() == 7043
    assert contract_df["churned_customers"].sum() == 1869


def test_sql_mart_schema_and_queries():
    """Test SQLite database initialization and execution of all 16 queries."""
    conn = initialize_database(DB_PATH, SCHEMA_PATH, CLEAN_CSV)
    queries = parse_queries(QUERIES_PATH)
    
    # Verify at least 15 queries exist
    assert len(queries) >= 15
    assert len(queries) == 16

    results = execute_all_queries(conn, queries)
    assert len(results) == 16

    # Verify Query 1 matches Python KPI calculations
    q1 = results["query_01_executive_kpis"]
    assert len(q1) == 1
    assert q1["total_customers"].iloc[0] == 7043
    assert q1["churned_customers"].iloc[0] == 1869
    assert q1["churn_rate_pct"].iloc[0] == 26.54
    assert q1["total_monthly_contracted_charges"].iloc[0] == 456116.60
    assert q1["historical_mrc_churned_base"].iloc[0] == 139130.85

    # Verify Query 2 (by contract) has 3 rows
    q2 = results["query_02_churn_by_contract"]
    assert len(q2) == 3

    # Verify all queries return non-empty DataFrames
    for name, df in results.items():
        assert len(df) > 0, f"Query {name} returned empty DataFrame!"

    conn.close()
