"""Power BI Star-Schema Export and Operational Action Queue Generator for RetainIQ.

Combines ML risk scores, behavioral segmentation, and statistical driver rankings
into production-ready star-schema CSV tables for direct ingestion into Power BI.
"""

from pathlib import Path
from typing import Dict, Any
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SCORED_CSV = Path("data/processed/telco_churn_scored.csv")
MART_CSV = Path("data/processed/telco_analytics_mart.csv")
EXPORTS_DIR = Path("exports")


def assign_retention_action(row: pd.Series) -> str:
    """Generate prescriptive, non-causal retention action based on risk score and product tier."""
    prob = row.get("PredictedChurnProbability", 0.0)
    contract = row.get("Contract", "")
    spend = row.get("MonthlyCharges", 0.0)
    tech_support = row.get("TechSupport", "")
    payment = row.get("PaymentMethod", "")

    if prob >= 0.60 and spend >= 75.0:
        return "Priority 1: Executive Concierge Outreach & Customized Plan Review"
    elif prob >= 0.45 and contract == "Month-to-month":
        return "Priority 2: 12-Month Term Commitment Incentive ($10/mo credit)"
    elif prob >= 0.35 and tech_support == "No":
        return "Priority 3: 60-Day TechSupport & Cybersecurity Trial Bundle"
    elif prob >= 0.30 and payment == "Electronic check":
        return "Priority 4: Automated Auto-Pay Switch Incentive ($5 one-time credit)"
    else:
        return "Priority 5: Standard Digital Engagement & Usage Nurture"


def build_power_bi_tables() -> Dict[str, pd.DataFrame]:
    """Build and export all 4 dedicated Power BI tables and the central fact table."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load data sources
    if not SCORED_CSV.exists():
        from src.modeling import run_modeling_pipeline
        run_modeling_pipeline()
    scored_df = pd.read_csv(SCORED_CSV)

    if not MART_CSV.exists():
        from src.segmentation import run_segmentation_pipeline
        run_segmentation_pipeline()
    mart_df = pd.read_csv(MART_CSV)

    # Merge mart enrichment (TenureCohort, ValueRiskQuadrant, ServiceBreadth) into scored df
    cols_to_add = ["TenureCohort", "ValueRiskQuadrant", "ServiceBreadth"]
    for c in cols_to_add:
        if c not in scored_df.columns and c in mart_df.columns:
            scored_df[c] = mart_df[c]

    # Assign operational action
    scored_df["RecommendedRetentionPlay"] = scored_df.apply(assign_retention_action, axis=1)

    # Table 1: Central Fact Table (7,043 rows)
    fact_table = scored_df.copy()
    p1 = EXPORTS_DIR / "fact_customer_retention.csv"
    fact_table.to_csv(p1, index=False)
    logger.info("Exported central fact table (%d rows) to %s", len(fact_table), p1)

    # Table 2: Executive Overview Summary Table
    exec_overview = scored_df.groupby(["Contract", "InternetService"], observed=False).agg(
        total_customers=("customerID", "count"),
        churned_customers=("ChurnBinary", "sum"),
        churn_rate_pct=("ChurnBinary", lambda s: round(s.mean() * 100, 2)),
        total_monthly_charges=("MonthlyCharges", "sum"),
        churned_monthly_charges=("MonthlyCharges", lambda s: round(s[scored_df.loc[s.index, "ChurnBinary"] == 1].sum(), 2)),
        avg_tenure=("tenure", "mean"),
        avg_predicted_risk=("PredictedChurnProbability", "mean")
    ).reset_index()
    exec_overview["total_monthly_charges"] = exec_overview["total_monthly_charges"].round(2)
    exec_overview["churned_monthly_charges"] = exec_overview["churned_monthly_charges"].round(2)
    exec_overview["avg_tenure"] = exec_overview["avg_tenure"].round(1)
    exec_overview["avg_predicted_risk"] = exec_overview["avg_predicted_risk"].round(4)
    p2 = EXPORTS_DIR / "power_bi_executive_overview.csv"
    exec_overview.to_csv(p2, index=False)
    logger.info("Exported executive overview table to %s", p2)

    # Table 3: Churn Drivers Statistical Summary Table (Intrinsic 16 Categorical Drivers)
    from src.eda import analyze_categoricals
    clean_base = pd.read_csv("data/processed/telco_churn_clean.csv")
    cat_drivers = analyze_categoricals(clean_base)
    p3 = EXPORTS_DIR / "power_bi_churn_drivers.csv"
    cat_drivers.to_csv(p3, index=False)
    logger.info("Exported churn drivers table to %s", p3)

    # Table 4: Segments & Lifecycle Cohorts Table
    from src.segmentation import profile_segments
    segments_summary = profile_segments(scored_df)
    p4 = EXPORTS_DIR / "power_bi_segments_cohorts.csv"
    segments_summary.to_csv(p4, index=False)
    logger.info("Exported segments & cohorts table to %s", p4)

    # Table 5: Actionable Operational Retention Prioritization Queue (Full Scored Base)
    queue_cols = [
        "customerID", "PredictedRiskTier", "PredictedChurnProbability",
        "MonthlyCharges", "tenure", "Contract", "InternetService",
        "TechSupport", "PaymentMethod", "ValueRiskQuadrant",
        "TenureCohort", "RecommendedRetentionPlay", "Churn"
    ]
    retention_queue = scored_df[queue_cols].sort_values(
        by=["PredictedChurnProbability", "MonthlyCharges"], ascending=[False, False]
    ).reset_index(drop=True)
    p5 = EXPORTS_DIR / "power_bi_retention_prioritization.csv"
    retention_queue.to_csv(p5, index=False)
    logger.info("Exported retention prioritization queue (%d rows) to %s", len(retention_queue), p5)

    return {
        "fact_table": fact_table,
        "exec_overview": exec_overview,
        "cat_drivers": cat_drivers,
        "segments_summary": segments_summary,
        "retention_queue": retention_queue
    }


if __name__ == "__main__":
    build_power_bi_tables()
