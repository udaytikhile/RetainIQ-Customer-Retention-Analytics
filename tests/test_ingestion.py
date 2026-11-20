"""Unit tests for data ingestion, validation, and cleaning in RetainIQ."""

import pytest
import pandas as pd
import numpy as np

from src.ingestion import (
    load_raw_data,
    validate_raw_schema,
    validate_customer_id_uniqueness,
    validate_target_labels,
    clean_total_charges,
    validate_numeric_ranges,
    clean_and_prepare_data,
    DataValidationError,
    REQUIRED_COLUMNS
)

RAW_CSV_PATH = "data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv"


def test_load_raw_data_shape():
    """Verify raw dataset has exactly 7,043 rows and 21 columns."""
    df = load_raw_data(RAW_CSV_PATH)
    assert df.shape[0] == 7043
    assert df.shape[1] == 21
    assert "customerID" in df.columns
    assert "Churn" in df.columns


def test_validate_raw_schema_missing_column():
    """Ensure missing columns trigger DataValidationError."""
    df = pd.DataFrame({"customerID": ["C1"], "Churn": ["No"]})
    with pytest.raises(DataValidationError, match="Missing required columns"):
        validate_raw_schema(df)


def test_validate_customer_id_uniqueness():
    """Ensure duplicate customer IDs trigger DataValidationError."""
    df = pd.DataFrame({"customerID": ["C1", "C1", "C2"]})
    with pytest.raises(DataValidationError, match="duplicate customerIDs"):
        validate_customer_id_uniqueness(df)


def test_validate_target_labels():
    """Ensure invalid target labels trigger DataValidationError."""
    df_valid = pd.DataFrame({"Churn": ["Yes", "No", "No", "Yes"]})
    validate_target_labels(df_valid)  # Should not raise

    df_invalid = pd.DataFrame({"Churn": ["Yes", "Unknown", "No"]})
    with pytest.raises(DataValidationError, match="Invalid labels detected"):
        validate_target_labels(df_invalid)


def test_clean_total_charges_whitespace():
    """Verify whitespace TotalCharges is imputed as 0.0 for tenure 0."""
    sample = pd.DataFrame({
        "customerID": ["C1", "C2"],
        "tenure": [0, 5],
        "MonthlyCharges": [25.0, 50.0],
        "TotalCharges": [" ", "250.0"]
    })
    cleaned, meta = clean_total_charges(sample)
    assert meta["blank_total_charges_count"] == 1
    assert cleaned.loc[0, "TotalCharges"] == 0.0
    assert cleaned.loc[1, "TotalCharges"] == 250.0
    assert cleaned["TotalCharges"].dtype == float


def test_validate_numeric_ranges():
    """Ensure negative values in numeric columns are rejected."""
    df_negative = pd.DataFrame({
        "tenure": [-1],
        "MonthlyCharges": [50.0],
        "TotalCharges": [100.0]
    })
    with pytest.raises(DataValidationError, match="Found negative values in 'tenure'"):
        validate_numeric_ranges(df_negative)


def test_full_clean_and_prepare_data_on_actual_dataset():
    """End-to-end verification of clean_and_prepare_data on the real dataset."""
    raw_df = load_raw_data(RAW_CSV_PATH)
    clean_df, audit = clean_and_prepare_data(raw_df)

    # Check dimensions
    assert len(clean_df) == 7043
    assert "ChurnBinary" in clean_df.columns
    assert clean_df["ChurnBinary"].sum() == 1869

    # Check zero NaNs
    assert clean_df.isna().sum().sum() == 0

    # Check types
    assert np.issubdtype(clean_df["TotalCharges"].dtype, np.floating)
    assert np.issubdtype(clean_df["MonthlyCharges"].dtype, np.floating)
    assert np.issubdtype(clean_df["tenure"].dtype, np.integer)
    assert np.issubdtype(clean_df["ChurnBinary"].dtype, np.integer)

    # Check audit metrics
    assert audit["total_records"] == 7043
    assert audit["blank_total_charges_count"] == 11
    assert audit["churn_yes_count"] == 1869
    assert audit["churn_no_count"] == 5174
    assert round(audit["baseline_churn_rate"], 4) == 0.2654
