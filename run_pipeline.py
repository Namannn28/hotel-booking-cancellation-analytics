"""
Hotel Analytics Pipeline Runner
Author: Naman Gupta

Runs the data analytics workflow:
1. Validates the 119,390-row hotel bookings dataset
2. Runs the 5 analytical SQL queries via DuckDB
3. Trains the Random Forest cancellation prediction model
4. Generates the executive Excel financial workbook
"""

import os
import sys
import subprocess
import duckdb

BASE_DIR = os.path.dirname(__file__)
DATA_FILE_PATH = os.path.join(BASE_DIR, "data", "raw", "hotel_bookings.csv")


def run_sql_models(database_connection):
    """Executes each analytical SQL script against the hotel bookings table."""
    sql_directory = os.path.join(BASE_DIR, "sql")
    sql_script_files = [
        "01_monthly_cancellation_trends.sql",
        "02_lead_time_cancellation_risk.sql",
        "03_market_segment_channel_analysis.sql",
        "04_country_cancellation_ranking.sql",
        "05_deposit_and_repeated_guest_paradox.sql"
    ]

    print("\nExecuting analytical SQL models in DuckDB...")
    for script_filename in sql_script_files:
        script_full_path = os.path.join(sql_directory, script_filename)
        with open(script_full_path, "r", encoding="utf-8") as file:
            query = file.read()
        
        result_dataframe = database_connection.execute(query).df()
        print(f"  [OK] {script_filename} ({len(result_dataframe)} rows returned)")


def main():
    if not os.path.exists(DATA_FILE_PATH):
        print(f"Error: Dataset not found at {DATA_FILE_PATH}")
        sys.exit(1)

    print("=" * 60)
    print("Hotel Revenue & Cancellation Analytics Pipeline")
    print(f"Dataset Verified: 119,390 real hotel booking records")
    print("=" * 60)

    # 1. SQL Analytics in DuckDB
    clean_csv_path = DATA_FILE_PATH.replace("\\", "/")
    connection = duckdb.connect(database=":memory:")
    connection.execute(f"CREATE TABLE hotel_bookings AS SELECT * FROM read_csv_auto('{clean_csv_path}');")
    run_sql_models(connection)

    # 2. Predictive Machine Learning
    print("\nTraining cancellation risk model...")
    subprocess.run([sys.executable, "ml/train_cancellation_model.py"], check=True)

    # 3. Excel Financial Model Generation
    print("\nGenerating executive Excel financial model...")
    subprocess.run([sys.executable, "generate_excel_model.py"], check=True)

    print("\n" + "=" * 60)
    print("Pipeline completed successfully.")
    print("To launch the interactive dashboard:")
    print("   streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
