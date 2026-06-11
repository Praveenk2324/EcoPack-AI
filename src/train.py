"""
Training Pipeline for EcoPack-AI.

Loads processed data, trains CO2 and Cost XGBoost models,
evaluates them, and saves all artifacts to models/.

Usage:
    python -m src.train
"""

import json
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from src.model import build_co2_model, build_cost_model

# ── Paths ────────────────────────────────────────────────────────────────────
PROCESSED_DIR = os.path.join("data", "processed")
MODELS_DIR = "models"

DATA_PATH = os.path.join(PROCESSED_DIR, "cleaned_data.csv")
MATERIALS_RAW = os.path.join("data", "raw", "materials_database.csv")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.joblib")

# ── Feature configuration ───────────────────────────────────────────────────
# Features shared by both models
COMMON_FEATURES = ["Weight_kg", "Distance_km", "Material_Density"]

# CO2 model specific features
CO2_FEATURES = COMMON_FEATURES + ["Material_CO2_Factor", "Shipping_Mode_Road"]

# Cost model specific features
COST_FEATURES = COMMON_FEATURES + ["Cost_per_kg", "Product_Volume_m3", "Shipping_Mode_Road"]

# Numeric features to scale (must match preprocess.py)
NUMERIC_FEATURES = [
    "Weight_kg",
    "Distance_km",
    "Material_CO2_Factor",
    "Material_Density",
    "Cost_per_kg",
    "Product_Volume_m3",
]

CO2_TARGET = "CO2_Emission_kg"
COST_TARGET = "Cost_USD"

TEST_SIZE = 0.2
RANDOM_STATE = 42


def load_data() -> pd.DataFrame:
    """Load processed data."""
    print("📂 Loading processed data...")
    df = pd.read_csv(DATA_PATH)
    print(f"   {df.shape[0]:,} rows × {df.shape[1]} cols")
    return df


def prepare_features(df: pd.DataFrame, scaler) -> pd.DataFrame:
    """Encode categoricals and scale numerics."""
    out = df.copy()

    # Binary encode Shipping_Mode (Road=1, else=0)
    out["Shipping_Mode_Road"] = (out["Shipping_Mode"] == "Road").astype(float)

    # Scale numeric features
    out[NUMERIC_FEATURES] = scaler.transform(out[NUMERIC_FEATURES])

    return out


def evaluate(y_true, y_pred, label: str) -> dict:
    """Compute and print evaluation metrics."""
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    mean_val = float(y_true.mean())

    print(f"   RMSE : {rmse:.4f}  ({rmse / mean_val * 100:.2f}% of mean)")
    print(f"   MAE  : {mae:.4f}  ({mae / mean_val * 100:.2f}% of mean)")
    print(f"   R²   : {r2:.4f}")

    return {"rmse": rmse, "mae": mae, "r2": r2, "mean": mean_val}


def run() -> None:
    """Execute the full training pipeline."""
    print("=" * 60)
    print("🚀 EcoPack-AI — Training Pipeline")
    print("=" * 60)

    # Load data & scaler
    df = load_data()
    scaler = joblib.load(SCALER_PATH)
    print(f"   Scaler loaded from {SCALER_PATH}")

    # Prepare features
    print("\n⚙️  Preparing features...")
    df_prepared = prepare_features(df, scaler)

    # ── Train CO2 model ──────────────────────────────────────────────────────
    print("\n🌿 Training CO2 Prediction Model (XGBoost)...")
    X_co2 = df_prepared[CO2_FEATURES]
    y_co2 = df_prepared[CO2_TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X_co2, y_co2, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print(f"   Train: {len(X_train):,}  |  Test: {len(X_test):,}")

    co2_model = build_co2_model()
    co2_model.fit(X_train, y_train)
    y_pred = co2_model.predict(X_test)
    co2_metrics = evaluate(y_test, y_pred, "CO2")

    # ── Train Cost model ─────────────────────────────────────────────────────
    print("\n💰 Training Cost Prediction Model (XGBoost)...")
    X_cost = df_prepared[COST_FEATURES]
    y_cost = df_prepared[COST_TARGET]

    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
        X_cost, y_cost, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print(f"   Train: {len(X_train_c):,}  |  Test: {len(X_test_c):,}")

    cost_model = build_cost_model()
    cost_model.fit(X_train_c, y_train_c)
    y_pred_c = cost_model.predict(X_test_c)
    cost_metrics = evaluate(y_test_c, y_pred_c, "Cost")

    # ── Save artifacts ───────────────────────────────────────────────────────
    print("\n💾 Saving model artifacts...")
    os.makedirs(MODELS_DIR, exist_ok=True)

    joblib.dump(co2_model, os.path.join(MODELS_DIR, "co2_model.joblib"))
    joblib.dump(cost_model, os.path.join(MODELS_DIR, "cost_model.joblib"))
    print("   ✅ co2_model.joblib")
    print("   ✅ cost_model.joblib")

    # Save feature config
    feature_config = {
        "co2_features": CO2_FEATURES,
        "cost_features": COST_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
    }
    joblib.dump(feature_config, os.path.join(MODELS_DIR, "feature_config.joblib"))
    print("   ✅ feature_config.joblib")

    # Save materials database for inference
    materials_df = pd.read_csv(MATERIALS_RAW)
    joblib.dump(materials_df, os.path.join(MODELS_DIR, "materials_db.joblib"))
    print("   ✅ materials_db.joblib")

    # Save metadata
    metadata = {
        "model_version": "2.0",
        "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model_type": "XGBoost Regressor",
        "co2_metrics": co2_metrics,
        "cost_metrics": cost_metrics,
        "total_materials": int(len(materials_df)),
        "categories": materials_df["Category"].unique().tolist(),
        "training_samples": int(len(df)),
        "test_size": TEST_SIZE,
    }
    with open(os.path.join(MODELS_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    print("   ✅ metadata.json")

    print("\n" + "=" * 60)
    print("✅ Training complete! All artifacts saved to models/")
    print("=" * 60)


if __name__ == "__main__":
    run()
