"""
Hotel Booking Cancellation Analysis & Prediction Model
Author: Naman Gupta

Trains a Random Forest classifier to predict booking cancellations,
evaluates precision/recall/ROC-AUC, and calculates feature importance
to help hotel revenue managers identify high-risk reservations in advance.
"""

import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "hotel_bookings.csv")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


def load_and_preprocess_data():
    """Loads 119k real booking records and prepares business features."""
    df = pd.read_csv(DATA_PATH)
    
    # Fill missing values with business defaults
    df["children"] = df["children"].fillna(0).astype(int)
    df["country"] = df["country"].fillna("Unknown")
    df["adr"] = df["adr"].clip(lower=0, upper=1000)
    
    # Core operational metrics
    numerical_features = [
        "lead_time",
        "stays_in_weekend_nights",
        "stays_in_week_nights",
        "adults",
        "children",
        "is_repeated_guest",
        "previous_cancellations",
        "previous_bookings_not_canceled",
        "booking_changes",
        "days_in_waiting_list",
        "adr",
        "required_car_parking_spaces",
        "total_of_special_requests"
    ]
    
    # Key categorical dimensions
    categorical_features = ["hotel", "market_segment", "deposit_type", "customer_type"]
    
    # Convert categorical columns to binary indicators
    df_encoded = pd.get_dummies(df[numerical_features + categorical_features], drop_first=True)
    
    target = df["is_canceled"]
    return df, df_encoded, target


def train_cancellation_model(features, target):
    """Trains a Random Forest classifier to predict cancellation risk."""
    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.20, random_state=42, stratify=target
    )
    
    classifier = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    )
    classifier.fit(X_train, y_train)
    
    # Evaluate model performance
    predictions = classifier.predict(X_test)
    prediction_probabilities = classifier.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, predictions)
    roc_auc = roc_auc_score(y_test, prediction_probabilities)
    precision = precision_score(y_test, predictions)
    recall = recall_score(y_test, predictions)
    conf_matrix = confusion_matrix(y_test, predictions)
    
    print("-" * 50)
    print("Hotel Cancellation Risk Model - Performance Summary")
    print(f"Accuracy  : {accuracy * 100:.2f}%")
    print(f"ROC-AUC   : {roc_auc:.4f}")
    print(f"Precision : {precision * 100:.2f}%  (Low false-positive rate protects guest trust)")
    print(f"Recall    : {recall * 100:.2f}%")
    print("Confusion Matrix (23,878 reservations evaluated):")
    print(f"  Confirmed Correctly (TN): {conf_matrix[0, 0]:,}")
    print(f"  False Alarms (FP)       : {conf_matrix[0, 1]:,}")
    print(f"  Missed Cancellations (FN): {conf_matrix[1, 0]:,}")
    print(f"  Cancellations Caught (TP): {conf_matrix[1, 1]:,}")
    print("-" * 50)
    
    # Save feature importances
    feature_importance_df = pd.DataFrame({
        "Feature": features.columns,
        "Importance": classifier.feature_importances_
    }).sort_values(by="Importance", ascending=False)
    
    feature_importance_df.to_csv(os.path.join(MODELS_DIR, "feature_importance.csv"), index=False)
    
    # Save trained model and column list
    joblib.dump(classifier, os.path.join(MODELS_DIR, "hotel_cancellation_rf.joblib"))
    joblib.dump(features.columns.tolist(), os.path.join(MODELS_DIR, "feature_columns.joblib"))
    
    return classifier, feature_importance_df


def generate_overbooking_policy(raw_df):
    """Calculates empirical monthly cancellation rates to guide safe overbooking buffers."""
    overbooking_schedule = raw_df.groupby(["hotel", "arrival_date_month"]).agg(
        total_reservations=("is_canceled", "count"),
        total_cancellations=("is_canceled", "sum"),
        cancellation_rate=("is_canceled", "mean")
    ).reset_index()
    
    # Conservative overbooking recommendation: 40% of historical cancellation rate
    overbooking_schedule["recommended_overbooking_buffer_pct"] = (
        overbooking_schedule["cancellation_rate"] * 40.0
    ).round(1)
    
    overbooking_schedule.to_csv(os.path.join(PROCESSED_DIR, "overbooking_recommendations.csv"), index=False)
    print("Generated monthly overbooking recommendations table.")


def main():
    print("Loading hotel booking dataset...")
    raw_df, features, target = load_and_preprocess_data()
    
    print("Training predictive model...")
    model, feature_importance = train_cancellation_model(features, target)
    
    print("\nTop 5 Drivers of Reservation Cancellation:")
    print(feature_importance.head(5).to_string(index=False))
    
    generate_overbooking_policy(raw_df)


if __name__ == "__main__":
    main()
