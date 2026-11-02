"""
PulseMetrics-AI: Natural Language to SQL Analytics Engine
Uses DuckDB in-memory execution to translate and execute analytical queries over raw parquet/CSVs.
"""

import os
import duckdb
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

class TextToSQLEngine:
    def __init__(self):
        self.con = duckdb.connect(database=":memory:")
        self._load_tables()
        
    def _load_tables(self):
        # Register views directly from generated CSVs
        for tbl in ["dim_customers", "fact_subscriptions", "fact_product_usage", "fact_support_tickets"]:
            csv_path = os.path.join(RAW_DIR, f"{tbl}.csv").replace("\\", "/")
            self.con.execute(f"CREATE TABLE {tbl} AS SELECT * FROM read_csv_auto('{csv_path}');")

    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """Executes a sanitized SQL query and returns a pandas DataFrame."""
        return self.con.execute(sql_query).df()

    def translate_and_query(self, question: str):
        """
        Translates common analytical questions into optimized SQL queries.
        Includes built-in template intelligence and fallback execution.
        """
        q = question.lower()
        
        # 1. Total ARR / MRR by Tier
        if "tier" in q and ("arr" in q or "revenue" in q or "mrr" in q):
            sql = """
            SELECT 
                c.tier,
                COUNT(s.customer_id) AS total_customers,
                COUNT(CASE WHEN s.status = 'Active' THEN 1 END) AS active_customers,
                ROUND(SUM(CASE WHEN s.status = 'Active' THEN s.arr ELSE 0 END), 2) AS total_active_arr,
                ROUND(AVG(CASE WHEN s.status = 'Active' THEN s.arr ELSE NULL END), 2) AS avg_arr_per_account,
                ROUND(COUNT(CASE WHEN s.status = 'Churned' THEN 1 END) * 100.0 / COUNT(s.customer_id), 1) AS churn_rate_pct
            FROM dim_customers c
            JOIN fact_subscriptions s ON c.customer_id = s.customer_id
            GROUP BY c.tier
            ORDER BY total_active_arr DESC;
            """
            explanation = "Aggregated active ARR, account count, and churn percentage grouped by plan tier."
            
        # 2. Churn rate by industry
        elif "industry" in q or "sector" in q:
            sql = """
            SELECT 
                c.industry,
                COUNT(s.customer_id) AS total_accounts,
                COUNT(CASE WHEN s.status = 'Churned' THEN 1 END) AS churned_accounts,
                ROUND(COUNT(CASE WHEN s.status = 'Churned' THEN 1 END) * 100.0 / COUNT(s.customer_id), 1) AS churn_rate_pct,
                ROUND(SUM(CASE WHEN s.status = 'Active' THEN s.arr ELSE 0 END), 2) AS active_arr
            FROM dim_customers c
            JOIN fact_subscriptions s ON c.customer_id = s.customer_id
            GROUP BY c.industry
            ORDER BY churn_rate_pct DESC;
            """
            explanation = "Benchmarked customer attrition rate and active ARR across all vertical industries."

        # 3. Top churn risk or lowest NPS accounts
        elif "nps" in q or "dissatisfied" in q or "unhappy" in q:
            sql = """
            SELECT 
                c.customer_id,
                c.company_name,
                c.tier,
                s.status,
                s.arr,
                u.nps_score,
                u.avg_weekly_logins,
                u.last_active_days_ago
            FROM dim_customers c
            JOIN fact_subscriptions s ON c.customer_id = s.customer_id
            JOIN fact_product_usage u ON c.customer_id = u.customer_id
            WHERE s.status = 'Active'
            ORDER BY u.nps_score ASC, s.arr DESC
            LIMIT 10;
            """
            explanation = "Filtered top 10 at-risk active customers with lowest NPS scores ranked by revenue exposure."

        # 4. Support tickets and SLA latency
        elif "ticket" in q or "support" in q or "sla" in q:
            sql = """
            SELECT 
                category,
                priority,
                COUNT(ticket_id) AS ticket_volume,
                ROUND(AVG(resolution_time_hours), 1) AS avg_resolution_hours,
                ROUND(AVG(csat_rating), 2) AS avg_csat,
                SUM(escalated_to_tier2) AS tier2_escalations
            FROM fact_support_tickets
            GROUP BY category, priority
            ORDER BY priority DESC, ticket_volume DESC;
            """
            explanation = "Support ticket volume, resolution latency, CSAT ratings, and escalations by issue category."

        # Default: Executive high-level KPI scorecard
        else:
            sql = """
            SELECT 
                COUNT(customer_id) AS total_accounts,
                COUNT(CASE WHEN status = 'Active' THEN 1 END) AS active_accounts,
                ROUND(SUM(CASE WHEN status = 'Active' THEN arr ELSE 0 END), 2) AS total_active_arr,
                ROUND(AVG(CASE WHEN status = 'Active' THEN arr ELSE NULL END), 2) AS blended_arpu,
                ROUND(COUNT(CASE WHEN status = 'Churned' THEN 1 END) * 100.0 / COUNT(customer_id), 2) AS overall_churn_rate_pct
            FROM fact_subscriptions;
            """
            explanation = "Executive enterprise baseline: Total accounts, active ARR, blended ARPU, and churn rate."

        df_res = self.execute_query(sql)
        return {
            "sql": sql.strip(),
            "explanation": explanation,
            "data": df_res
        }

if __name__ == "__main__":
    engine = TextToSQLEngine()
    res = engine.translate_and_query("What is our ARR and churn rate by tier?")
    print("Executed SQL:\n", res["sql"])
    print("\nResult Preview:\n", res["data"])
