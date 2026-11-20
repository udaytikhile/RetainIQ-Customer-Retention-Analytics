"""Business Metrics Calculation and Financial Reconciliation Engine for RetainIQ.

Implements strict mathematical accounting of customer volume, churn rates, tenure distributions,
and contracted recurring charges, adhering to non-forecasting terminology standards.
"""

from pathlib import Path
from typing import Dict, Any
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def calculate_reconciled_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate executive business metrics with strict balance-sheet reconciliation."""
    total_customers = len(df)
    churn_mask = df["Churn"] == "Yes"
    retained_mask = df["Churn"] == "No"

    churn_count = int(churn_mask.sum())
    retained_count = int(retained_mask.sum())
    churn_rate = churn_count / total_customers if total_customers > 0 else 0.0

    # Tenure metrics
    avg_tenure_overall = float(df["tenure"].mean())
    median_tenure_overall = float(df["tenure"].median())
    avg_tenure_retained = float(df.loc[retained_mask, "tenure"].mean())
    median_tenure_retained = float(df.loc[retained_mask, "tenure"].median())
    avg_tenure_churned = float(df.loc[churn_mask, "tenure"].mean())
    median_tenure_churned = float(df.loc[churn_mask, "tenure"].median())

    # Revenue & Charge metrics
    total_mrr = float(df["MonthlyCharges"].sum())
    retained_mrr = float(df.loc[retained_mask, "MonthlyCharges"].sum())
    churned_monthly_charges = float(df.loc[churn_mask, "MonthlyCharges"].sum())
    
    avg_monthly_charge_overall = float(df["MonthlyCharges"].mean())
    avg_monthly_charge_retained = float(df.loc[retained_mask, "MonthlyCharges"].mean())
    avg_monthly_charge_churned = float(df.loc[churn_mask, "MonthlyCharges"].mean())

    total_historical_billed = float(df["TotalCharges"].sum())
    retained_historical_billed = float(df.loc[retained_mask, "TotalCharges"].sum())
    churned_historical_billed = float(df.loc[churn_mask, "TotalCharges"].sum())

    # Strict reconciliation assertions
    assert total_customers == churn_count + retained_count, "Customer count reconciliation error!"
    assert np.isclose(total_mrr, retained_mrr + churned_monthly_charges, atol=1e-2), "MRR reconciliation error!"
    assert np.isclose(total_historical_billed, retained_historical_billed + churned_historical_billed, atol=1e-2), (
        "Total billed charges reconciliation error!"
    )

    metrics = {
        "customer_count": total_customers,
        "retained_customer_count": retained_count,
        "churn_customer_count": churn_count,
        "churn_rate_pct": round(churn_rate * 100, 2),
        "tenure": {
            "avg_overall_months": round(avg_tenure_overall, 2),
            "median_overall_months": median_tenure_overall,
            "avg_retained_months": round(avg_tenure_retained, 2),
            "median_retained_months": median_tenure_retained,
            "avg_churned_months": round(avg_tenure_churned, 2),
            "median_churned_months": median_tenure_churned,
        },
        "financials": {
            "total_monthly_contracted_charges": round(total_mrr, 2),
            "retained_monthly_recurring_charges": round(retained_mrr, 2),
            "historical_monthly_charges_churned_base": round(churned_monthly_charges, 2),
            "churned_monthly_charges_share_pct": round((churned_monthly_charges / total_mrr) * 100, 2),
            "avg_monthly_charge_overall": round(avg_monthly_charge_overall, 2),
            "avg_monthly_charge_retained": round(avg_monthly_charge_retained, 2),
            "avg_monthly_charge_churned": round(avg_monthly_charge_churned, 2),
            "total_historical_cumulative_billed": round(total_historical_billed, 2),
        }
    }

    logger.info(
        "Reconciled KPIs: Customers=%d, Churned=%d (%.2f%%), Total MRR=$%.2f, Churned MRR=$%.2f",
        metrics["customer_count"],
        metrics["churn_customer_count"],
        metrics["churn_rate_pct"],
        metrics["financials"]["total_monthly_contracted_charges"],
        metrics["financials"]["historical_monthly_charges_churned_base"]
    )
    return metrics


def calculate_breakdowns(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Generate multi-dimensional aggregation tables for BI and SQL validation."""
    breakdowns = {}

    # 1. By Contract
    breakdowns["by_contract"] = df.groupby("Contract").agg(
        total_customers=("customerID", "count"),
        churned_customers=("ChurnBinary", "sum"),
        churn_rate_pct=("ChurnBinary", lambda s: round(s.mean() * 100, 2)),
        total_monthly_charges=("MonthlyCharges", "sum"),
        churned_monthly_charges=("MonthlyCharges", lambda s: round(s[df.loc[s.index, "ChurnBinary"] == 1].sum(), 2)),
        avg_tenure_months=("tenure", "mean")
    ).reset_index()

    # 2. By Tenure Cohort
    df_copy = df.copy()
    bins = [-1, 6, 12, 24, 48, 72]
    labels = ["0-6m", "7-12m", "13-24m", "25-48m", "49-72m"]
    df_copy["TenureCohort"] = pd.cut(df_copy["tenure"], bins=bins, labels=labels)
    
    breakdowns["by_tenure_cohort"] = df_copy.groupby("TenureCohort", observed=False).agg(
        total_customers=("customerID", "count"),
        churned_customers=("ChurnBinary", "sum"),
        churn_rate_pct=("ChurnBinary", lambda s: round(s.mean() * 100, 2)),
        total_monthly_charges=("MonthlyCharges", "sum"),
        churned_monthly_charges=("MonthlyCharges", lambda s: round(s[df_copy.loc[s.index, "ChurnBinary"] == 1].sum(), 2))
    ).reset_index()

    return breakdowns


if __name__ == "__main__":
    from src.ingestion import run_pipeline
    clean_df, _ = run_pipeline()
    kpis = calculate_reconciled_kpis(clean_df)
    import pprint
    pprint.pprint(kpis)
