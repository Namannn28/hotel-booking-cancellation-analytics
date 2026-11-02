"""
PulseMetrics-AI: Master Pipeline Runner
Executes the end-to-end data analytics and AI pipeline in a single command:
1. Synthetic Data Generation
2. SQL Analytical Modeling (DuckDB)
3. Predictive Churn Modeling (Random Forest)
4. Unsupervised Customer RFM Clustering (K-Means)
5. Executive Financial Model Workbook Generation (OpenPyXL)
6. Copilot Self-Verification Test
"""

import os
import sys
import subprocess
import duckdb
import pandas as pd

def log(msg):
    print(f"\n[PulseMetrics-AI] >>> {msg}")

def main():
    log("Step 1: Generating B2B SaaS Enterprise Datasets...")
    import generate_dataset

    log("Step 2: Executing Production SQL Analytical Models via DuckDB...")
    con = duckdb.connect(database=":memory:")
    raw_dir = os.path.join(os.path.dirname(__file__), "data", "raw").replace("\\", "/")
    
    # Load raw tables
    for tbl in ["dim_customers", "fact_subscriptions", "fact_product_usage", "fact_support_tickets"]:
        con.execute(f"CREATE TABLE {tbl} AS SELECT * FROM read_csv_auto('{raw_dir}/{tbl}.csv');")

    sql_files = [
        "01_kpi_arr_waterfall.sql",
        "02_cohort_retention.sql",
        "03_rfm_segmentation.sql",
        "04_product_engagement.sql",
        "05_churn_driver_analysis.sql"
    ]
    
    for sql_file in sql_files:
        sql_path = os.path.join(os.path.dirname(__file__), "sql", sql_file)
        with open(sql_path, "r", encoding="utf-8") as f:
            query = f.read()
        res = con.execute(query).df()
        print(f"  [OK] Successfully executed {sql_file} ({len(res)} rows)")

    log("Step 3: Training Predictive Churn Model & Generating Risk Alert Feed...")
    subprocess.run([sys.executable, "ml/train_churn_model.py"], check=True)

    log("Step 4: Executing Unsupervised K-Means Customer Clustering...")
    subprocess.run([sys.executable, "ml/rfm_clustering.py"], check=True)

    log("Step 5: Generating Multi-Tab Formatted Executive Excel Model...")
    subprocess.run([sys.executable, "generate_excel_model.py"], check=True)

    log("Step 6: Testing Autonomous GenAI Analytics Copilot (Text-to-SQL + RAG)...")
    from ai_agent.copilot import AnalyticsCopilot
    copilot = AnalyticsCopilot()
    test_brief = copilot.generate_executive_brief("What is our active ARR and churn rate by plan tier?")
    print("  [OK] Copilot test verification successful!")

    print("\n" + "="*70)
    print("  PulseMetrics-AI: Full Pipeline Completed Successfully!")
    print("  To launch the interactive executive dashboard, run:")
    print("     streamlit run app.py")
    print("="*70)

if __name__ == "__main__":
    main()
