"""
PulseMetrics-AI: Unsupervised RFM Customer Segmentation (K-Means)
Performs K-Means clustering across Recency, Frequency, Monetary & Product Engagement features.
Evaluates cluster quality with Silhouette Score and generates executive segment archetypes.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

df_cust = pd.read_csv(os.path.join(RAW_DIR, "dim_customers.csv"))
df_sub = pd.read_csv(os.path.join(RAW_DIR, "fact_subscriptions.csv"))
df_usage = pd.read_csv(os.path.join(RAW_DIR, "fact_product_usage.csv"))

df = df_cust.merge(df_sub, on="customer_id").merge(df_usage, on="customer_id")
# Filter to active accounts for forward-looking marketing & customer success segmentation
active_df = df[df["status"] == "Active"].copy()

features = [
    "last_active_days_ago",       # Recency proxy
    "avg_weekly_logins",          # Frequency proxy
    "arr",                        # Monetary proxy
    "active_seat_utilization",    # Adoption proxy
    "active_features_count"       # Breadth proxy
]

X = active_df[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K-Means with k=4 clusters
k = 4
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
active_df["cluster_id"] = kmeans.fit_predict(X_scaled)

sil_score = silhouette_score(X_scaled, active_df["cluster_id"])
print(f"=== K-Means Customer Clustering Results ===")
print(f"Silhouette Score (k={k}): {sil_score:.4f}")

# Profile clusters
cluster_profile = active_df.groupby("cluster_id").agg(
    customer_count=("customer_id", "count"),
    avg_arr=("arr", "mean"),
    avg_recency=("last_active_days_ago", "mean"),
    avg_weekly_logins=("avg_weekly_logins", "mean"),
    avg_seat_utilization=("active_seat_utilization", "mean"),
    avg_features=("active_features_count", "mean")
).reset_index()

# Map to business archetypes based on profile metrics
# Rank by ARR and Engagement
cluster_profile = cluster_profile.sort_values(by="avg_arr", ascending=False)
archetype_names = [
    "Enterprise Champions",
    "High-Growth Core Accounts",
    "Moderate Engagement Mid-Market",
    "At-Risk / Dormant Accounts"
]
mapping = dict(zip(cluster_profile["cluster_id"], archetype_names))
active_df["segment_name"] = active_df["cluster_id"].map(mapping)

print("\nCluster Segment Profile:")
print(cluster_profile.to_string(index=False))

# Export segmented customer base
export_cols = [
    "customer_id", "company_name", "industry", "tier", "arr", "segment_name",
    "last_active_days_ago", "avg_weekly_logins", "active_seat_utilization", "nps_score"
]
active_df[export_cols].to_csv(os.path.join(PROCESSED_DIR, "customer_rfm_segments.csv"), index=False)
joblib.dump(kmeans, os.path.join(MODELS_DIR, "kmeans_rfm_model.joblib"))
joblib.dump(scaler, os.path.join(MODELS_DIR, "rfm_scaler.joblib"))

print(f"\nSaved segmented accounts to: {os.path.join(PROCESSED_DIR, 'customer_rfm_segments.csv')}")
