import pandas as pd
import numpy as np

df = pd.read_csv('WA_Fn-UseC_-Telco-Customer-Churn.csv')

print("=== 1. SHAPE ===")
print(f"Total Rows: {df.shape[0]}")
print(f"Total Columns: {df.shape[1]}")

print("\n=== 2. FIELD NAMES & RAW DTYPES ===")
for i, col in enumerate(df.columns, 1):
    print(f"{i:2d}. {col:20s} | dtype: {str(df[col].dtype):10s} | Sample: {repr(df[col].iloc[0])}")

print("\n=== 3. TARGET COLUMN (Churn) ===")
counts = df['Churn'].value_counts(dropna=False)
pcts = df['Churn'].value_counts(normalize=True, dropna=False) * 100
for val in counts.index:
    print(f"  Label '{val}': {counts[val]:,d} records ({pcts[val]:.2f}%)")

print("\n=== 4. CUSTOMER ID INTEGRITY ===")
total_rows = len(df)
unique_ids = df['customerID'].nunique()
duplicates = df['customerID'].duplicated().sum()
print(f"  Total records: {total_rows}")
print(f"  Unique customerIDs: {unique_ids}")
print(f"  Duplicate customerIDs: {duplicates}")

print("\n=== 5. DATA QUALITY: WHITESPACE & MISSING VALUES ===")
null_summary = df.isnull().sum()
explicit_nulls = null_summary[null_summary > 0]
print(f"  Explicit nulls across all columns:\n{explicit_nulls if len(explicit_nulls) > 0 else '  None'}")

blank_counts = {}
for col in df.select_dtypes(include='object').columns:
    blanks = (df[col].astype(str).str.strip() == '').sum()
    if blanks > 0:
        blank_counts[col] = blanks
print(f"  Whitespace-only cells detected: {blank_counts}")

if 'TotalCharges' in blank_counts:
    tc_blanks = df[df['TotalCharges'].astype(str).str.strip() == '']
    print(f"\n  Detail of {len(tc_blanks)} records with blank TotalCharges:")
    print(tc_blanks[['customerID', 'tenure', 'MonthlyCharges', 'TotalCharges', 'Churn', 'Contract']])
    print(f"  Tenure values for blank TotalCharges: {tc_blanks['tenure'].unique().tolist()}")
    print(f"  Churn values for blank TotalCharges: {tc_blanks['Churn'].value_counts().to_dict()}")

print("\n=== 6. CARDINALITY OF CATEGORICAL FEATURES ===")
for col in df.select_dtypes(include='object').columns:
    if col != 'customerID':
        vals = df[col].unique().tolist()
        if len(vals) <= 5:
            print(f"  {col:18s}: {vals}")
        else:
            print(f"  {col:18s}: {len(vals)} distinct values -> {vals[:3]}...")

print("\n=== 7. NUMERICAL DISTRIBUTIONS ===")
clean_tc = pd.to_numeric(df['TotalCharges'].replace(r'^\s*$', np.nan, regex=True), errors='coerce')
num_df = pd.DataFrame({
    'tenure': df['tenure'],
    'MonthlyCharges': df['MonthlyCharges'],
    'TotalCharges_numeric': clean_tc
})
print(num_df.describe().round(2))
