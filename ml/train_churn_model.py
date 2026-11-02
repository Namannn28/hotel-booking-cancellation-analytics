"""
PulseMetrics-AI: Customer Churn Prediction Engine
Trains an interpretable Ensemble Classifier to predict B2B SaaS account churn,
computes feature importance, and outputs actionable high-risk customer scores.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# 1. Load Data
df_cust = pd.read_csv(os.path.join(RAW_DIR, "dim_customers.csv"))
df_sub = pd.read_csv(os.path.join(RAW_DIR, "fact_subscriptions.csv"))
df_usage = pd.read_csv(os.path.join(RAW_DIR, "fact_product_usage.csv"))
df_tickets = pd.read_csv(os.path.join(RAW_DIR, "fact_support_tickets.csv"))

# 2. Aggregate Support Tickets per Customer
ticket_agg = df_tickets.groupby("customer_id").agg(
    total_tickets=("ticket_id", "count"),
    avg_ticket_sla_hours=("resolution_time_hours", "mean"),
    avg_csat=("csat_rating", "mean"),
    tier2_escalations=("escalated_to_tier2", "sum")
).reset_index()

# 3. Master Feature Matrix Join
df = df_cust.merge(df_sub, on="customer_id")
df = df.merge(df_usage, on="customer_id")
df = df.merge(ticket_agg, on="customer_id", how="left").fillna({
    "total_tickets": 0, "avg_ticket_sla_hours": 0, "avg_csat": 3.0, "tier2_escalations": 0
})

# 4. Feature Engineering & Target
df["target_churn"] = (df["status"] == "Churned").astype(int)

# One-hot encode categorical features
cat_cols = ["industry", "region", "tier", "billing_cycle"]
df_encoded = pd.get_dummies(df, columns=cat_cols, drop_first=True)

feature_cols = [
    "mrr", "licensed_seats", "avg_weekly_logins", "active_seat_utilization",
    "monthly_api_calls", "active_features_count", "nps_score", "storage_used_gb",
    "last_active_days_ago", "total_tickets", "avg_ticket_sla_hours", "avg_csat",
    "tier2_escalations"
] + [c for c in df_encoded.columns if c.startswith(tuple([x + "_" for x in cat_cols]))]

X = df_encoded[feature_cols]
y = df_encoded["target_churn"]

# 5. Train / Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# 6. Train Random Forest Model
model = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)
model.fit(X_train, y_train)

# 7. Model Evaluation
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

roc_auc = roc_auc_score(y_test, y_prob)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"=== Customer Churn Model Performance ===")
print(f"ROC-AUC Score : {roc_auc:.4f}")
print(f"Precision     : {precision:.4f}")
print(f"Recall        : {recall:.4f}")
print(f"F1-Score      : {f1:.4f}")
print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred))

# 8. Feature Importance
importances = pd.DataFrame({
    "Feature": feature_cols,
    "Importance": model.feature_importances_
}).sort_values(by="Importance", ascending=False)

importances.to_csv(os.path.join(MODELS_DIR, "feature_importance.csv"), index=False)
print("Top 5 Churn Predictors:")
print(importances.head(5).to_string(index=False))

# 9. Save Model
joblib.dump(model, os.path.join(MODELS_DIR, "churn_rf_model.joblib"))
joblib.dump(feature_cols, os.path.join(MODELS_DIR, "feature_columns.joblib"))

# 10. Generate High-Risk Customer Alert Table for Active Customers
active_mask = df["status"] == "Active"
active_customers = df[active_mask].copy()
active_X = df_encoded[active_mask][feature_cols]

active_customers["churn_risk_probability"] = model.predict_proba(active_X)[:, 1]
high_risk = active_customers[active_customers["churn_risk_probability"] >= 0.50].sort_values(
    by="churn_risk_probability", ascending=False
)

high_risk[[
    "customer_id", "company_name", "tier", "arr", "active_seat_utilization",
    "last_active_days_ago", "nps_score", "churn_risk_probability"
]].to_csv(os.path.join(PROCESSED_DIR, "active_high_risk_customers.csv"), index=False)

print(f"\nGenerated {len(high_risk)} high-risk active customer alerts in: active_high_risk_customers.csv")
