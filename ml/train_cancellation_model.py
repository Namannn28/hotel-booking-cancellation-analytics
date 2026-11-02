"""
Hotel Booking Cancellation & Revenue Recovery: Predictive ML Engine
Trains an interpretable, production-ready classifier to predict reservation cancellation risk.
Computes evaluation metrics (ROC-AUC, Precision, Recall, Confusion Matrix) and feature importances.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, precision_score, recall_score, accuracy_score
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "hotel_bookings.csv")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# 1. Load Data
df = pd.read_csv(DATA_PATH)
print(f"Loaded {len(df):,} real hotel booking records.")

# Clean missing values
df["children"] = df["children"].fillna(0)
df["country"] = df["country"].fillna("Unknown")
df["adr"] = df["adr"].clip(lower=0, upper=1000) # Remove negative outliers

# 2. Select Relevant Business Features
numeric_features = [
    "lead_time", "stays_in_weekend_nights", "stays_in_week_nights",
    "adults", "children", "is_repeated_guest", "previous_cancellations",
    "previous_bookings_not_canceled", "booking_changes", "days_in_waiting_list",
    "adr", "required_car_parking_spaces", "total_of_special_requests"
]

categorical_features = ["hotel", "market_segment", "deposit_type", "customer_type"]

# One-hot encode categoricals
df_encoded = pd.get_dummies(df[numeric_features + categorical_features], drop_first=True)
feature_cols = df_encoded.columns.tolist()

X = df_encoded
y = df["is_canceled"]

# 3. Train-Test Split (80% Train, 20% Test, Stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

# 4. Model Training: Random Forest Classifier
print("Training Random Forest Classifier (100 estimators, max_depth=12)...")
rf_model = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

# 5. Model Evaluation
y_pred = rf_model.predict(X_test)
y_prob = rf_model.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print("\n" + "="*50)
print("=== Hotel Cancellation Model Performance ===")
print(f"Accuracy Score   : {acc:.4f} ({acc*100:.1f}%)")
print(f"ROC-AUC Score    : {roc_auc:.4f}")
print(f"Precision (Class 1): {precision:.4f}")
print(f"Recall (Class 1)   : {recall:.4f}")
print("Confusion Matrix :")
print(f"  [TN: {cm[0,0]:,}  FP: {cm[0,1]:,}]")
print(f"  [FN: {cm[1,0]:,}  TP: {cm[1,1]:,}]")
print("="*50)

# 6. Feature Importance Extraction
feat_imp = pd.DataFrame({
    "Feature": feature_cols,
    "Importance": rf_model.feature_importances_
}).sort_values(by="Importance", ascending=False)

feat_imp.to_csv(os.path.join(MODELS_DIR, "feature_importance.csv"), index=False)
print("\nTop 7 Predictors of Booking Cancellation:")
print(feat_imp.head(7).to_string(index=False))

# 7. Save Model Artifacts
joblib.dump(rf_model, os.path.join(MODELS_DIR, "hotel_cancellation_rf.joblib"))
joblib.dump(feature_cols, os.path.join(MODELS_DIR, "feature_columns.joblib"))

# 8. Compute Monthly Overbooking Threshold Recommendations
# Calculates empirical cancellation probability by month & hotel to optimize overbooking %
overbooking_strategy = df.groupby(["hotel", "arrival_date_month"]).agg(
    total_bookings=("is_canceled", "count"),
    cancellations=("is_canceled", "sum"),
    cancellation_rate=("is_canceled", "mean")
).reset_index()

# Recommended Overbooking = Cancellation Rate * 0.40 (conservative hedge to avoid walk-away penalties)
overbooking_strategy["recommended_overbooking_pct"] = (overbooking_strategy["cancellation_rate"] * 40.0).round(1)
overbooking_strategy.to_csv(os.path.join(PROCESSED_DIR, "overbooking_recommendations.csv"), index=False)

print(f"\nSaved model and overbooking strategy to: {PROCESSED_DIR}")
