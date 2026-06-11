"""
Data Preprocessing Pipeline for EcoPack-AI.

Loads raw CSVs, cleans data, engineers features, maps materials,
and saves processed output + scaler artifact.

Usage:
    python -m src.preprocess
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import warnings

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")
MODELS_DIR = "models"

HISTORY_PATH = os.path.join(RAW_DIR, "packaging_history.csv")
MATERIALS_PATH = os.path.join(RAW_DIR, "materials_database.csv")
OUTPUT_PATH = os.path.join(PROCESSED_DIR, "cleaned_data.csv")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.joblib")

# ── Deterministic material mapping ───────────────────────────────────────────
# Maps the 10 packaging types in the history data to specific materials
# in the 600-row materials database.
PACKAGING_TO_MATERIAL = {
    "Kraft Paper Mailer": "Single-Ply Kraft Paper",
    "Mushroom Pkg (Mycelium)": "Food-Grade Mushroom Mycelium",
    "Wood Crate": "Lightweight Plywood",
    "PLA Bioplastic": "Insulated PLA Bioplastic",
    "Honeycomb Paper": "Standard Kraft Paper",
    "Recycled PET Box": "Recycled PET Plastic",
    "Bubble Wrap (LDPE)": "Standard Bubble Wrap (LDPE)",
    "Corrugated Cardboard": "Standard Corrugated Cardboard",
    "Styrofoam (EPS)": "Standard Styrofoam (EPS)",
    "Cornstarch Foam": "Double-Wall Cornstarch Foam",
}

# Numeric columns to scale during training
NUMERIC_FEATURES = [
    "Weight_kg",
    "Distance_km",
    "Material_CO2_Factor",
    "Material_Density",
    "Cost_per_kg",
    "Product_Volume_m3",
]


def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load raw CSVs from data/raw/."""
    print("📂 Loading raw data...")
    history_df = pd.read_csv(HISTORY_PATH)
    materials_df = pd.read_csv(MATERIALS_PATH)
    print(f"   History:   {history_df.shape[0]:,} rows × {history_df.shape[1]} cols")
    print(f"   Materials: {materials_df.shape[0]:,} rows × {materials_df.shape[1]} cols")
    return history_df, materials_df


def clean_data(history_df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing values and fix invalid dimensions."""
    df = history_df.copy()

    # Impute missing Cost_USD and CO2_Emission_kg with category medians
    for col in ["Cost_USD", "CO2_Emission_kg"]:
        n_missing = df[col].isnull().sum()
        if n_missing > 0:
            medians = df.groupby("Category")[col].median()
            df[col] = df.apply(
                lambda r: medians[r["Category"]] if pd.isnull(r[col]) else r[col],
                axis=1,
            )
            print(f"   Imputed {n_missing} missing values in {col}")

    # Fix zero/null dimensions with category means
    for dim in ["L_cm", "W_cm", "H_cm"]:
        invalid = (df[dim] == 0) | df[dim].isnull()
        n_invalid = invalid.sum()
        if n_invalid > 0:
            means = df.groupby("Category")[dim].mean()
            df[dim] = df.apply(
                lambda r: means[r["Category"]]
                if (r[dim] == 0 or pd.isnull(r[dim]))
                else r[dim],
                axis=1,
            )
            print(f"   Fixed {n_invalid} invalid values in {dim}")

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add computed columns."""
    df = df.copy()
    df["Product_Volume_m3"] = (df["L_cm"] * df["W_cm"] * df["H_cm"]) / 1_000_000
    print(f"   Product_Volume_m3 range: [{df['Product_Volume_m3'].min():.6f}, {df['Product_Volume_m3'].max():.6f}]")
    return df


def map_materials(
    history_df: pd.DataFrame, materials_df: pd.DataFrame
) -> pd.DataFrame:
    """Map packaging names to materials and merge properties."""
    df = history_df.copy()

    # Map packaging → material name
    df["Material_Name"] = df["Packaging_Used"].map(PACKAGING_TO_MATERIAL)
    mapped = df["Material_Name"].notna().sum()
    print(f"   Mapped {mapped}/{len(df)} packaging entries to materials")

    # Merge material properties
    mat_cols = materials_df[
        ["Material_Name", "Density_kg_m3", "CO2_Emission_kg", "Cost_per_kg", "Biodegradable"]
    ].copy()
    mat_cols = mat_cols.rename(
        columns={
            "Density_kg_m3": "Material_Density",
            "CO2_Emission_kg": "Material_CO2_Factor",
        }
    )

    df = df.merge(mat_cols, on="Material_Name", how="left", suffixes=("", "_mat"))

    # Drop rows that couldn't be mapped (should be 0)
    before = len(df)
    df = df.dropna(subset=["Material_Density"])
    dropped = before - len(df)
    if dropped:
        print(f"   ⚠️  Dropped {dropped} rows without material match")

    return df


def fit_scaler(df: pd.DataFrame) -> StandardScaler:
    """Fit a StandardScaler on numeric features and save it."""
    scaler = StandardScaler()
    scaler.fit(df[NUMERIC_FEATURES])
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)
    print(f"   Scaler saved → {SCALER_PATH}")
    return scaler


def run() -> None:
    """Execute the full preprocessing pipeline."""
    print("=" * 60)
    print("🔧 EcoPack-AI — Preprocessing Pipeline")
    print("=" * 60)

    history_df, materials_df = load_raw_data()

    print("\n🧹 Cleaning data...")
    history_df = clean_data(history_df)

    print("\n⚙️  Engineering features...")
    history_df = engineer_features(history_df)

    print("\n🔗 Mapping materials...")
    history_df = map_materials(history_df, materials_df)

    print("\n📏 Fitting scaler...")
    fit_scaler(history_df)

    print("\n💾 Saving processed data...")
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    history_df.to_csv(OUTPUT_PATH, index=False)
    print(f"   {OUTPUT_PATH}  ({history_df.shape[0]:,} rows × {history_df.shape[1]} cols)")

    print("\n✅ Preprocessing complete!")


if __name__ == "__main__":
    run()
