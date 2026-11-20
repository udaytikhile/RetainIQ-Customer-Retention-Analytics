"""Data Ingestion, Validation, and Cleaning Module for RetainIQ.

Handles IBM Telco Customer Churn data loading, strict integrity validations,
careful handling of TotalCharges whitespace anomalies, and typing harmonization.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import logging
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "customerID", "gender", "SeniorCitizen", "Partner", "Dependents",
    "tenure", "PhoneService", "MultipleLines", "InternetService",
    "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
    "StreamingTV", "StreamingMovies", "Contract", "PaperlessBilling",
    "PaymentMethod", "MonthlyCharges", "TotalCharges", "Churn"
]


class DataValidationError(Exception):
    """Raised when data integrity checks fail."""
    pass


def load_raw_data(filepath: str | Path) -> pd.DataFrame:
    """Load raw Telco Customer Churn CSV into a pandas DataFrame."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found at: {path}")
    df = pd.read_csv(path)
    logger.info("Loaded %d rows and %d columns from %s", df.shape[0], df.shape[1], path)
    return df


def validate_raw_schema(df: pd.DataFrame) -> None:
    """Validate that all required columns exist in the DataFrame."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DataValidationError(f"Missing required columns in dataset: {missing}")


def validate_customer_id_uniqueness(df: pd.DataFrame) -> None:
    """Ensure customerID is strictly unique with zero duplicate rows."""
    duplicate_count = df["customerID"].duplicated().sum()
    if duplicate_count > 0:
        raise DataValidationError(
            f"Integrity failure: Found {duplicate_count} duplicate customerIDs!"
        )


def validate_target_labels(df: pd.DataFrame) -> None:
    """Ensure Churn target column only contains valid binary classes ('Yes', 'No')."""
    unique_labels = set(df["Churn"].dropna().unique())
    valid_labels = {"Yes", "No"}
    if not unique_labels.issubset(valid_labels):
        invalid = unique_labels - valid_labels
        raise DataValidationError(f"Invalid labels detected in target column 'Churn': {invalid}")


def clean_total_charges(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean TotalCharges by handling whitespace values.

    Empirical finding: 11 rows have whitespace-only TotalCharges with tenure == 0.
    These represent newly joined customers who have completed 0 billing cycles.
    They are imputed as 0.00.
    """
    df = df.copy()
    raw_tc = df["TotalCharges"].astype(str)
    blank_mask = raw_tc.str.strip() == ""
    blank_count = int(blank_mask.sum())

    if blank_count > 0:
        # Verify tenure is 0 for these records
        non_zero_tenure = (df.loc[blank_mask, "tenure"] != 0).sum()
        if non_zero_tenure > 0:
            logger.warning(
                "%d records with blank TotalCharges have non-zero tenure!", non_zero_tenure
            )
        logger.info(
            "Found %d records with whitespace TotalCharges. Imputing with 0.0 (all tenure=0).",
            blank_count
        )
        df.loc[blank_mask, "TotalCharges"] = "0.0"

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    
    # Assert zero NaNs remaining
    remaining_nan = df["TotalCharges"].isna().sum()
    if remaining_nan > 0:
        raise DataValidationError(f"Failed to parse all TotalCharges values: {remaining_nan} NaNs remain")

    return df, {"blank_total_charges_count": blank_count}


def validate_numeric_ranges(df: pd.DataFrame) -> None:
    """Validate that numeric columns are non-negative and within reasonable bounds."""
    if (df["tenure"] < 0).any():
        raise DataValidationError("Found negative values in 'tenure'")
    if (df["MonthlyCharges"] < 0).any():
        raise DataValidationError("Found negative values in 'MonthlyCharges'")
    if (df["TotalCharges"] < 0).any():
        raise DataValidationError("Found negative values in 'TotalCharges'")


def clean_and_prepare_data(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Execute complete ingestion, validation, and cleaning pipeline."""
    # 1. Schema check
    validate_raw_schema(raw_df)
    
    # 2. Uniqueness check
    validate_customer_id_uniqueness(raw_df)
    
    # 3. Target label check
    validate_target_labels(raw_df)

    # 4. Clean TotalCharges
    df, tc_meta = clean_total_charges(raw_df)

    # 5. Type harmonizations
    df["tenure"] = df["tenure"].astype(int)
    df["MonthlyCharges"] = df["MonthlyCharges"].astype(float)
    df["TotalCharges"] = df["TotalCharges"].astype(float)
    df["SeniorCitizen"] = df["SeniorCitizen"].astype(int)
    
    # 6. Numeric ranges check
    validate_numeric_ranges(df)

    # 7. Add analytics binary target
    df["ChurnBinary"] = (df["Churn"] == "Yes").astype(int)

    # 8. Compile audit summary
    audit_summary = {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "churn_yes_count": int((df["Churn"] == "Yes").sum()),
        "churn_no_count": int((df["Churn"] == "No").sum()),
        "baseline_churn_rate": float((df["Churn"] == "Yes").mean()),
        "total_monthly_charges": float(df["MonthlyCharges"].sum()),
        "total_cumulative_charges": float(df["TotalCharges"].sum()),
        **tc_meta
    }

    logger.info(
        "Data validation successful. Processed %d records. Baseline churn: %.2f%%",
        audit_summary["total_records"],
        audit_summary["baseline_churn_rate"] * 100
    )
    return df, audit_summary


def run_pipeline(
    input_path: str | Path = "data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv",
    output_path: str | Path = "data/processed/telco_churn_clean.csv"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """End-to-end ingestion runner that writes cleaned data to disk."""
    raw_df = load_raw_data(input_path)
    clean_df, audit = clean_and_prepare_data(raw_df)
    
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(out_p, index=False)
    logger.info("Saved cleaned dataset to %s", out_p)
    return clean_df, audit


if __name__ == "__main__":
    run_pipeline()
