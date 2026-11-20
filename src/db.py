"""Database Initialization and SQL Analytical Query Execution Engine for RetainIQ.

Creates an embedded SQLite analytical database, loads cleaned customer records,
and executes all 16 production-grade analytical queries.
"""

from pathlib import Path
from typing import Dict, Any, List
import sqlite3
import re
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path("data/processed/telco.db")
SCHEMA_PATH = Path("sql/schema.sql")
QUERIES_PATH = Path("sql/queries.sql")
CLEAN_CSV_PATH = Path("data/processed/telco_churn_clean.csv")


def initialize_database(
    db_path: Path = DB_PATH,
    schema_path: Path = SCHEMA_PATH,
    data_path: Path = CLEAN_CSV_PATH
) -> sqlite3.Connection:
    """Initialize SQLite database, apply schema DDL, and insert customer records."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Apply schema
    schema_sql = schema_path.read_text(encoding="utf-8")
    cursor.executescript(schema_sql)
    logger.info("Applied schema from %s to %s", schema_path, db_path)

    # Load cleaned data
    df = pd.read_csv(data_path)
    
    # Map pandas columns to database column names
    col_mapping = {
        "customerID": "customer_id",
        "gender": "gender",
        "SeniorCitizen": "senior_citizen",
        "Partner": "partner",
        "Dependents": "dependents",
        "tenure": "tenure",
        "PhoneService": "phone_service",
        "MultipleLines": "multiple_lines",
        "InternetService": "internet_service",
        "OnlineSecurity": "online_security",
        "OnlineBackup": "online_backup",
        "DeviceProtection": "device_protection",
        "TechSupport": "tech_support",
        "StreamingTV": "streaming_tv",
        "StreamingMovies": "streaming_movies",
        "Contract": "contract",
        "PaperlessBilling": "paperless_billing",
        "PaymentMethod": "payment_method",
        "MonthlyCharges": "monthly_charges",
        "TotalCharges": "total_charges",
        "Churn": "churn",
        "ChurnBinary": "churn_binary"
    }

    db_df = df[list(col_mapping.keys())].rename(columns=col_mapping)
    db_df.to_sql("customers", conn, if_exists="append", index=False)
    conn.commit()

    # Verify count
    cursor.execute("SELECT COUNT(*) FROM customers;")
    loaded_count = cursor.fetchone()[0]
    logger.info("Successfully loaded %d records into SQLite 'customers' table", loaded_count)
    return conn


def parse_queries(queries_path: Path = QUERIES_PATH) -> List[Dict[str, str]]:
    """Parse distinct SQL queries from queries.sql using -- NAME: tags."""
    content = queries_path.read_text(encoding="utf-8")
    raw_blocks = content.split("-- NAME: ")
    queries = []

    for block in raw_blocks[1:]:  # Skip header preamble
        lines = block.strip().split("\n")
        name = lines[0].strip()
        sql = "\n".join(lines[1:]).strip()
        # Clean trailing semicolons if present
        if sql.endswith(";"):
            sql = sql[:-1].strip()
        queries.append({"name": name, "sql": sql})

    return queries


def execute_all_queries(
    conn: sqlite3.Connection,
    queries: List[Dict[str, str]]
) -> Dict[str, pd.DataFrame]:
    """Execute all parsed queries and return results as DataFrames."""
    results = {}
    for q in queries:
        name = q["name"]
        sql = q["sql"]
        try:
            df = pd.read_sql_query(sql, conn)
            results[name] = df
            logger.info("Executed %-35s -> Returned %2d rows, %d cols", name, len(df), len(df.columns))
        except Exception as e:
            logger.error("Error executing query '%s': %s", name, e)
            raise e
    return results


def run_sql_mart() -> Dict[str, pd.DataFrame]:
    """Runner to initialize DB and verify all queries."""
    conn = initialize_database()
    queries = parse_queries()
    logger.info("Parsed %d distinct SQL queries from %s", len(queries), QUERIES_PATH)
    results = execute_all_queries(conn, queries)
    conn.close()
    return results


if __name__ == "__main__":
    run_sql_mart()
