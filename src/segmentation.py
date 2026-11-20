"""Customer Value-at-Risk and Behavioral Segmentation Engine for RetainIQ.

Implements multi-dimensional customer segmentation combining financial exposure (MonthlyCharges, TotalCharges)
with contractual and lifecycle risk (Contract, Tenure Cohorts, Service Breadth).
Outputs strictly non-causal observational profiles and high-res visualizations.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CLEAN_CSV_PATH = Path("data/processed/telco_churn_clean.csv")
ENRICHED_CSV_PATH = Path("data/processed/telco_analytics_mart.csv")
FIGURES_DIR = Path("reports/figures")


def assign_tenure_cohort(tenure: int) -> str:
    """Map continuous tenure in months to standard customer lifecycle cohorts."""
    if tenure <= 6:
        return "01. Onboarding (0-6m)"
    elif tenure <= 12:
        return "02. Nurture (7-12m)"
    elif tenure <= 24:
        return "03. Established (13-24m)"
    elif tenure <= 48:
        return "04. Mature (25-48m)"
    else:
        return "05. Loyalist (49-72m)"


def compute_service_breadth(row: pd.Series) -> int:
    """Calculate total active cybersecurity, support, and streaming add-on services."""
    services = [
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies"
    ]
    return sum(1 for s in services if row.get(s) == "Yes")


def assign_value_risk_quadrant(monthly_charges: float, contract: str) -> str:
    """Classify customer into actionable 4-quadrant Value-at-Risk matrix.
    
    Threshold:
      - High Value: MonthlyCharges >= $70.00 (Upper half / premium bundle threshold)
      - Standard/Lower Value: MonthlyCharges < $70.00
      - High Risk: Month-to-month contract (no renewal barrier)
      - Low Risk: One-year or Two-year contract (contractual commitment)
    """
    is_high_value = monthly_charges >= 70.00
    is_high_risk = contract == "Month-to-month"

    if is_high_value and is_high_risk:
        return "Quadrant 1: VIP Flight Risk (High Spend, Month-to-Month)"
    elif is_high_value and not is_high_risk:
        return "Quadrant 2: Core Champions (High Spend, Long Contract)"
    elif not is_high_value and is_high_risk:
        return "Quadrant 3: Transactional Vulnerable (Lower Spend, Month-to-Month)"
    else:
        return "Quadrant 4: Stable Base (Lower Spend, Long Contract)"


def enrich_customer_mart(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich cleaned dataset with analytical segments, lifecycle cohorts, and service metrics."""
    mart = df.copy()

    # 1. Lifecycle Tenure Cohort
    mart["TenureCohort"] = mart["tenure"].apply(assign_tenure_cohort)

    # 2. Service Breadth Index (0 - 6)
    mart["ServiceBreadth"] = mart.apply(compute_service_breadth, axis=1)

    # 3. Value-at-Risk Quadrant
    mart["ValueRiskQuadrant"] = mart.apply(
        lambda r: assign_value_risk_quadrant(r["MonthlyCharges"], r["Contract"]),
        axis=1
    )

    # 4. Charge Ratios (proxy for price sensitivity and tenure-adjusted spend)
    mart["AverageMonthlyHistoricalSpend"] = np.where(
        mart["tenure"] == 0,
        mart["MonthlyCharges"],
        mart["TotalCharges"] / np.maximum(mart["tenure"], 1)
    )

    return mart


def profile_segments(mart: pd.DataFrame) -> pd.DataFrame:
    """Generate executive statistical profile across the 4 Value-at-Risk quadrants."""
    total_customers = len(mart)
    total_mrr = mart["MonthlyCharges"].sum()
    total_churned_mrc = mart.loc[mart["ChurnBinary"] == 1, "MonthlyCharges"].sum()

    grouped = mart.groupby("ValueRiskQuadrant").agg(
        customer_count=("customerID", "count"),
        churn_count=("ChurnBinary", "sum"),
        churn_rate_pct=("ChurnBinary", lambda s: round(s.mean() * 100, 2)),
        total_monthly_charges=("MonthlyCharges", "sum"),
        churned_monthly_charges=("MonthlyCharges", lambda s: round(s[mart.loc[s.index, "ChurnBinary"] == 1].sum(), 2)),
        avg_monthly_charges=("MonthlyCharges", "mean"),
        avg_tenure_months=("tenure", "mean"),
        avg_service_breadth=("ServiceBreadth", "mean")
    ).reset_index()

    grouped["customer_share_pct"] = round((grouped["customer_count"] / total_customers) * 100, 2)
    grouped["mrr_share_pct"] = round((grouped["total_monthly_charges"] / total_mrr) * 100, 2)
    grouped["share_of_churned_mrc_pct"] = round(
        (grouped["churned_monthly_charges"] / total_churned_mrc) * 100, 2
    )

    # Format numeric columns
    grouped["total_monthly_charges"] = grouped["total_monthly_charges"].round(2)
    grouped["avg_monthly_charges"] = grouped["avg_monthly_charges"].round(2)
    grouped["avg_tenure_months"] = grouped["avg_tenure_months"].round(1)
    grouped["avg_service_breadth"] = grouped["avg_service_breadth"].round(2)

    return grouped


def generate_segmentation_visuals(mart: pd.DataFrame, output_dir: Path = FIGURES_DIR) -> None:
    """Generate executive segmentation charts."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Value-at-Risk Quadrant Scatter / Bubble Distribution
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    quadrant_summary = mart.groupby("ValueRiskQuadrant").agg(
        customers=("customerID", "count"),
        mrr=("MonthlyCharges", "sum"),
        churn_rate=("ChurnBinary", lambda s: s.mean() * 100),
        churned_mrc=("MonthlyCharges", lambda s: s[mart.loc[s.index, "ChurnBinary"] == 1].sum())
    ).reset_index()

    colors = ["#d9534f", "#2b5c8f", "#f0ad4e", "#5cb85c"]
    bars = ax.barh(
        quadrant_summary["ValueRiskQuadrant"],
        quadrant_summary["churned_mrc"],
        color=colors,
        edgecolor="black",
        alpha=0.85
    )
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 1000, bar.get_y() + bar.get_height() / 2, f"${w:,.2f}", va="center", fontweight="bold")

    ax.set_title(
        "Historical Monthly Recurring Charges of Churned Base by Customer Quadrant ($)",
        fontsize=12, fontweight="bold", pad=12
    )
    ax.set_xlabel("Historical Monthly Charges of Churned Customers ($)")
    ax.set_xlim(0, 110000)
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_dir / "segmentation_value_risk_quadrant.png")
    plt.close()

    # 2. Tenure Lifecycle Waterfall & Churn Rate
    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=300)
    tenure_summary = mart.groupby("TenureCohort").agg(
        customers=("customerID", "count"),
        churn_rate=("ChurnBinary", lambda s: s.mean() * 100)
    ).reset_index()

    ax2 = ax1.twinx()
    ax1.bar(tenure_summary["TenureCohort"], tenure_summary["customers"], color="#2b5c8f", alpha=0.6, width=0.45)
    ax2.plot(tenure_summary["TenureCohort"], tenure_summary["churn_rate"], color="#d9534f", marker="o", linewidth=2.5)

    for i, txt in enumerate(tenure_summary["churn_rate"]):
        ax2.annotate(f"{txt:.1f}%", (i, txt + 1.5), ha="center", fontweight="bold", color="#d9534f")

    ax1.set_title("Customer Lifecycle Cohorts: Customer Base Volume vs. Empirical Churn Rate", fontsize=12, fontweight="bold", pad=12)
    ax1.set_ylabel("Total Customers", color="#2b5c8f")
    ax2.set_ylabel("Empirical Churn Rate (%)", color="#d9534f")
    ax2.set_ylim(0, 60)
    ax1.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "tenure_cohort_waterfall.png")
    plt.close()

    # 3. Service Breadth vs Churn Rate
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    sb_summary = mart.groupby("ServiceBreadth")["ChurnBinary"].agg(["count", "mean"]).reset_index()
    sb_summary["mean"] = sb_summary["mean"] * 100
    bars = ax.bar(sb_summary["ServiceBreadth"], sb_summary["mean"], color="#5bc0de", edgecolor="#2b5c8f", width=0.5)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1.0, f"{h:.1f}%", ha="center", fontweight="bold")

    ax.set_title("Empirical Churn Rate (%) by Active Ancillary Services Count (0 to 6)", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Number of Subscribed Ancillary Services")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_ylim(0, 50)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_dir / "service_breadth_churn_rate.png")
    plt.close()

    logger.info("Generated 3 segmentation figures in %s", output_dir)


def run_segmentation_pipeline() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Execute end-to-end segmentation and export enriched analytics mart."""
    if not CLEAN_CSV_PATH.exists():
        from src.ingestion import run_pipeline
        run_pipeline()
    clean_df = pd.read_csv(CLEAN_CSV_PATH)
    mart = enrich_customer_mart(clean_df)
    
    # Save enriched mart
    ENRICHED_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    mart.to_csv(ENRICHED_CSV_PATH, index=False)
    logger.info("Saved enriched customer analytics mart to %s", ENRICHED_CSV_PATH)

    profiles = profile_segments(mart)
    generate_segmentation_visuals(mart)

    logger.info("\n=== CUSTOMER VALUE-AT-RISK QUADRANT PROFILES ===\n%s", profiles.to_string())
    return mart, profiles


if __name__ == "__main__":
    run_segmentation_pipeline()
