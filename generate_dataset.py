"""
PulseMetrics-AI: Synthetic B2B SaaS Enterprise Dataset Generator
Generates realistic customer, subscription, telemetry, support, and qualitative feedback data
with realistic noise and overlapping distributions for real-world modeling.
"""

import os
import random
import datetime
import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. Dimension: Customers & Companies
# -------------------------------------------------------------
INDUSTRIES = ["Fintech", "Healthcare", "E-commerce", "Cybersecurity", "EdTech", "DevOps", "Logistics", "Marketing SaaS"]
REGIONS = ["North America", "EMEA", "APAC", "LATAM"]
COMPANY_SIZES = ["1-50 employees", "51-200 employees", "201-1000 employees", "1000+ employees"]
TIERS = ["Starter", "Growth", "Enterprise"]

COMPANY_NAMES = [
    "ApexFlow", "CloudScale", "Stripewave", "VortexData", "OmniLogic", "DataPulse", "Nexora", "Synthetix",
    "QuantIQ", "IronShield", "KubeSphere", "LogiChain", "BioSync", "PayMatrix", "RetailSphere", "NeuroTech",
    "MetricWorks", "AuraCloud", "CoreStack", "Hyperion", "InfraOps", "TrustWave", "PrismGuard", "EchoLink",
    "FinSecure", "HealthVault", "ClearSignal", "VeloceData", "ScaleBridge", "ZennithAnalytics"
]

N_CUSTOMERS = 1500
customer_list = []
start_date = datetime.date(2023, 1, 1)
end_date = datetime.date(2024, 12, 31)

for cid in range(1001, 1001 + N_CUSTOMERS):
    name_base = random.choice(COMPANY_NAMES)
    company_name = f"{name_base} {random.randint(10, 999)} Inc."
    industry = random.choice(INDUSTRIES)
    region = random.choices(REGIONS, weights=[0.45, 0.30, 0.18, 0.07])[0]
    size = random.choices(COMPANY_SIZES, weights=[0.35, 0.35, 0.20, 0.10])[0]
    
    if size == "1000+ employees":
        tier = random.choices(TIERS, weights=[0.05, 0.25, 0.70])[0]
    elif size == "201-1000 employees":
        tier = random.choices(TIERS, weights=[0.15, 0.55, 0.30])[0]
    else:
        tier = random.choices(TIERS, weights=[0.55, 0.38, 0.07])[0]
        
    created_days = random.randint(0, (end_date - start_date).days)
    signup_date = start_date + datetime.timedelta(days=created_days)
    
    customer_list.append({
        "customer_id": f"CUST-{cid}",
        "company_name": company_name,
        "industry": industry,
        "region": region,
        "company_size": size,
        "tier": tier,
        "signup_date": signup_date.isoformat(),
        "primary_contact_role": random.choice(["VP Engineering", "Head of Product", "Director of IT", "Lead Analyst", "CTO", "COO"])
    })

df_customers = pd.DataFrame(customer_list)
df_customers.to_csv(os.path.join(OUTPUT_DIR, "dim_customers.csv"), index=False)

# -------------------------------------------------------------
# 2. Fact: Subscriptions & MRR Dynamics
# -------------------------------------------------------------
TIER_BASE_PRICING = {"Starter": 199.0, "Growth": 799.0, "Enterprise": 2499.0}

subscriptions = []
churn_dates = {}

for _, cust in df_customers.iterrows():
    c_id = cust["customer_id"]
    tier = cust["tier"]
    signup = datetime.date.fromisoformat(cust["signup_date"])
    
    base_churn_p = 0.26 if tier == "Starter" else (0.15 if tier == "Growth" else 0.08)
    is_churned = random.random() < base_churn_p
    
    tenure_months = (end_date.year - signup.year) * 12 + (end_date.month - signup.month)
    if tenure_months <= 0:
        tenure_months = 1
        
    mrr = TIER_BASE_PRICING[tier] * random.uniform(0.9, 1.4)
    seats = 5 if tier == "Starter" else (25 if tier == "Growth" else 100)
    seats = int(seats * random.uniform(0.8, 2.2))
    
    status = "Active"
    churn_date = None
    if is_churned and tenure_months > 2:
        churn_month_offset = random.randint(1, tenure_months - 1)
        churn_dt = signup + datetime.timedelta(days=churn_month_offset * 30)
        if churn_dt < end_date:
            status = "Churned"
            churn_date = churn_dt.isoformat()
            churn_dates[c_id] = churn_date

    billing_cycle = random.choice(["Monthly", "Annual", "Annual"]) if tier == "Enterprise" else random.choice(["Monthly", "Monthly", "Annual"])
    discount_pct = 0.15 if billing_cycle == "Annual" else 0.0

    subscriptions.append({
        "subscription_id": f"SUB-{c_id.split('-')[1]}",
        "customer_id": c_id,
        "plan_tier": tier,
        "mrr": round(mrr, 2),
        "arr": round(mrr * 12, 2),
        "licensed_seats": seats,
        "billing_cycle": billing_cycle,
        "discount_percent": discount_pct,
        "status": status,
        "start_date": signup.isoformat(),
        "churn_date": churn_date if churn_date else ""
    })

df_subscriptions = pd.DataFrame(subscriptions)
df_subscriptions.to_csv(os.path.join(OUTPUT_DIR, "fact_subscriptions.csv"), index=False)

# -------------------------------------------------------------
# 3. Fact: Product Telemetry & Usage Logs (Realistic Overlapping Distributions)
# -------------------------------------------------------------
usage_logs = []
for _, sub in df_subscriptions.iterrows():
    c_id = sub["customer_id"]
    status = sub["status"]
    tier = sub["plan_tier"]
    
    # Introduce real-world noise: ~15% of active customers are unengaged (at risk!),
    # and ~10% of churned customers had decent engagement before sudden executive shift
    is_at_risk_active = (status == "Active" and random.random() < 0.15)
    is_healthy_churned = (status == "Churned" and random.random() < 0.10)
    
    if (status == "Churned" and not is_healthy_churned) or is_at_risk_active:
        login_freq_weekly = np.clip(np.random.normal(2.1, 1.2), 0.2, 7.0)
        active_seat_ratio = np.clip(np.random.normal(0.42, 0.18), 0.05, 0.95)
        api_calls_monthly = int(np.clip(np.random.normal(3500, 2000), 100, 25000))
        features_used_count = int(np.clip(np.random.normal(3.5, 1.5), 1, 10))
        nps_score = int(np.clip(np.random.normal(5.2, 2.0), 1, 10))
        last_active_days = int(np.clip(np.random.normal(28, 15), 2, 90))
    else:
        login_freq_weekly = np.clip(np.random.normal(4.8, 1.3), 1.0, 7.0)
        active_seat_ratio = np.clip(np.random.normal(0.78, 0.14), 0.20, 1.0)
        api_calls_monthly = int(np.clip(np.random.normal(18000, 9000), 1000, 80000))
        features_used_count = int(np.clip(np.random.normal(7.2, 1.8), 2, 10))
        nps_score = int(np.clip(np.random.normal(8.1, 1.5), 3, 10))
        last_active_days = int(np.clip(np.random.normal(6, 4), 1, 25))
        
    usage_logs.append({
        "customer_id": c_id,
        "avg_weekly_logins": round(float(login_freq_weekly), 1),
        "active_seat_utilization": round(float(active_seat_ratio), 2),
        "monthly_api_calls": api_calls_monthly,
        "active_features_count": features_used_count,
        "nps_score": nps_score,
        "storage_used_gb": round(random.uniform(10.0, 500.0), 1),
        "last_active_days_ago": last_active_days
    })

df_usage = pd.DataFrame(usage_logs)
df_usage.to_csv(os.path.join(OUTPUT_DIR, "fact_product_usage.csv"), index=False)

# -------------------------------------------------------------
# 4. Fact: Customer Support Tickets
# -------------------------------------------------------------
ticket_categories = ["Billing & Invoicing", "API & Webhook Failure", "Performance Latency", "Feature Request", "SSO & Authentication", "Data Sync Delay"]
ticket_priorities = ["Low", "Medium", "High", "Critical"]

tickets = []
tid = 50001
for _, sub in df_subscriptions.iterrows():
    c_id = sub["customer_id"]
    status = sub["status"]
    
    num_tickets = random.randint(3, 10) if status == "Churned" else random.randint(1, 5)
    
    for _ in range(num_tickets):
        tid += 1
        prio = random.choices(ticket_priorities, weights=[0.2, 0.4, 0.25, 0.15] if status == "Churned" else [0.4, 0.4, 0.15, 0.05])[0]
        cat = random.choice(ticket_categories)
        res_time_hours = random.uniform(18, 72) if prio in ["High", "Critical"] and status == "Churned" else random.uniform(2, 30)
        csat = random.randint(1, 3) if status == "Churned" and random.random() < 0.55 else random.randint(3, 5)
        
        tickets.append({
            "ticket_id": f"TICK-{tid}",
            "customer_id": c_id,
            "category": cat,
            "priority": prio,
            "resolution_time_hours": round(res_time_hours, 1),
            "csat_rating": csat,
            "escalated_to_tier2": 1 if prio in ["High", "Critical"] and random.random() < 0.65 else 0
        })

df_tickets = pd.DataFrame(tickets)
df_tickets.to_csv(os.path.join(OUTPUT_DIR, "fact_support_tickets.csv"), index=False)

# -------------------------------------------------------------
# 5. Qualitative Transcripts for RAG Engine
# -------------------------------------------------------------
EXIT_INTERVIEW_TEMPLATES = [
    "Customer cited competitor Datadog offering a 30% cheaper annual contract with native Kubernetes integration. Primary complaint was API latency during peak hours.",
    "The VP of Engineering left the organization. New leadership mandated vendor consolidation into Microsoft Azure stack. Product usage plummeted over past 90 days.",
    "Customer experienced multiple billing inaccuracies following expansion to 150 seats. Lack of custom reporting dashboards caused friction with CFO.",
    "Severe data sync delay on webhook pipelines caused downstream ingestion failures. Opened 4 critical support tickets with slow SLA response time.",
    "Budget cuts across engineering division forced downgrading/cancelling non-essential SaaS licenses. Stated the tool was useful but too expensive for current runway.",
    "SSO and Okta authentication broke twice during company migration. Compliance team flagged security integration bottlenecks.",
    "Churned due to lack of advanced role-based access control (RBAC). Migrated to Snowflake + PowerBI in-house architecture."
]

QBR_EXPANSION_TEMPLATES = [
    "Quarterly review with CTO: Extremely pleased with automated anomaly detection. Planning to expand from Growth to Enterprise tier next quarter (+50 seats).",
    "Account health is stellar. Team increased monthly API usage by 180%. Requested automated weekly Slack digests for executive team.",
    "QBR positive. Customer achieved 4.2x ROI on data processing pipelines. Discussed multi-year contract renewal with 12% discount.",
    "High adoption across data analyst team. Requested dedicated customer success manager and custom data connector for BigQuery."
]

qualitative_records = []
doc_id = 1

churned_custs = df_subscriptions[df_subscriptions["status"] == "Churned"]["customer_id"].values
for c_id in churned_custs[:150]:
    doc_id += 1
    qualitative_records.append({
        "doc_id": f"DOC-{doc_id}",
        "customer_id": c_id,
        "doc_type": "Churn Exit Interview",
        "date": churn_dates.get(c_id, "2024-06-15"),
        "author": "Customer Success Director",
        "notes": f"Account {c_id}: {random.choice(EXIT_INTERVIEW_TEMPLATES)}"
    })

active_custs = df_subscriptions[df_subscriptions["status"] == "Active"]["customer_id"].values
for c_id in active_custs[:200]:
    doc_id += 1
    qualitative_records.append({
        "doc_id": f"DOC-{doc_id}",
        "customer_id": c_id,
        "doc_type": "QBR Executive Review",
        "date": "2024-11-20",
        "author": "Strategic Account Executive",
        "notes": f"Account {c_id}: {random.choice(QBR_EXPANSION_TEMPLATES)}"
    })

df_qualitative = pd.DataFrame(qualitative_records)
df_qualitative.to_csv(os.path.join(OUTPUT_DIR, "qualitative_customer_transcripts.csv"), index=False)

print(f"Realistic dataset refreshed in {OUTPUT_DIR}:")
print(f" - dim_customers: {len(df_customers)}")
print(f" - fact_subscriptions: {len(df_subscriptions)}")
print(f" - fact_product_usage: {len(df_usage)}")
print(f" - fact_support_tickets: {len(df_tickets)}")
print(f" - qualitative_transcripts: {len(df_qualitative)}")
