"""
EcoPack-AI — FastAPI Application.

Provides packaging recommendation endpoints.
Test via Swagger UI at http://localhost:8000/docs
"""

import json
import os
from contextlib import asynccontextmanager
from enum import Enum
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# ── Model loading ────────────────────────────────────────────────────────────
MODELS_DIR = "models"


class ModelStore:
    """Holds all loaded model artifacts."""

    co2_model = None
    cost_model = None
    scaler = None
    feature_config: dict = {}
    materials_df: Optional[pd.DataFrame] = None
    metadata: dict = {}
    loaded: bool = False


store = ModelStore()


def load_models() -> None:
    """Load all trained models and artifacts from models/."""
    try:
        store.co2_model = joblib.load(os.path.join(MODELS_DIR, "co2_model.joblib"))
        store.cost_model = joblib.load(os.path.join(MODELS_DIR, "cost_model.joblib"))
        store.scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.joblib"))
        store.feature_config = joblib.load(
            os.path.join(MODELS_DIR, "feature_config.joblib")
        )
        store.materials_df = pd.read_csv(
            os.path.join(MODELS_DIR, "materials_db.csv")
        )

        meta_path = os.path.join(MODELS_DIR, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                store.metadata = json.load(f)

        store.loaded = True
        print("✅ All models loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        store.loaded = False


# ── FastAPI app ──────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models on startup."""
    load_models()
    yield


app = FastAPI(
    title="EcoPack-AI",
    description=(
        "AI-powered eco-friendly packaging recommendation system. "
        "Predicts CO₂ emissions and cost for 600+ materials, then recommends "
        "the top 5 options based on your optimization preference."
    ),
    version="2.0.0",
    lifespan=lifespan,
)


# ── Schemas ──────────────────────────────────────────────────────────────────


class ShippingMode(str, Enum):
    air = "Air"
    road = "Road"
    sea = "Sea"
    rail = "Rail"


class Optimization(str, Enum):
    balanced = "balanced"
    eco = "eco"
    cost = "cost"


class RecommendRequest(BaseModel):
    weight_kg: float = Field(..., gt=0, description="Product weight in kilograms", examples=[2.5])
    volume_m3: float = Field(..., gt=0, description="Product volume in cubic metres", examples=[0.005])
    distance_km: float = Field(..., gt=0, description="Shipping distance in kilometres", examples=[1500])
    shipping_mode: ShippingMode = Field(..., description="Mode of transport", examples=["Road"])
    optimization: Optimization = Field(
        default=Optimization.balanced,
        description="Optimization preference: eco, cost, or balanced",
        examples=["balanced"],
    )


class MaterialRecommendation(BaseModel):
    rank: int
    material_name: str
    category: str
    predicted_co2_kg: float
    predicted_cost_usd: float
    biodegradable: bool
    combined_score: float


class RecommendResponse(BaseModel):
    product_weight_kg: float
    shipping_distance_km: float
    shipping_mode: str
    optimization: str
    recommendations: list[MaterialRecommendation]


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    model_version: str


class ModelInfoResponse(BaseModel):
    model_version: str
    training_date: str
    model_type: str
    co2_metrics: dict
    cost_metrics: dict
    total_materials: int
    categories: list[str]
    training_samples: int


# ── Recommendation logic ────────────────────────────────────────────────────


def get_recommendations(
    weight_kg: float,
    volume_m3: float,
    distance_km: float,
    shipping_mode: str,
    optimization: str,
) -> list[dict]:
    """Generate top-5 packaging recommendations using the trained models."""
    if not store.loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")

    # Set optimization weights
    weights = {"eco": (0.8, 0.2), "cost": (0.2, 0.8), "balanced": (0.6, 0.4)}
    w_co2, w_cost = weights.get(optimization, (0.6, 0.4))

    shipping_road = 1.0 if shipping_mode == "Road" else 0.0

    numeric_features = store.feature_config["numeric_features"]
    co2_features = store.feature_config["co2_features"]
    cost_features = store.feature_config["cost_features"]

    results = []

    for _, mat in store.materials_df.iterrows():
        # Build raw feature row
        raw = {
            "Weight_kg": weight_kg,
            "Distance_km": distance_km,
            "Material_CO2_Factor": mat["CO2_Emission_kg"],
            "Material_Density": mat["Density_kg_m3"],
            "Cost_per_kg": mat["Cost_per_kg"],
            "Product_Volume_m3": volume_m3,
        }

        # Scale numeric features
        raw_df = pd.DataFrame([raw])
        scaled = store.scaler.transform(raw_df[numeric_features])
        scaled_dict = dict(zip(numeric_features, scaled[0]))
        scaled_dict["Shipping_Mode_Road"] = shipping_road

        # Predict CO2
        co2_input = pd.DataFrame([[scaled_dict[f] for f in co2_features]], columns=co2_features)
        co2_pred = float(store.co2_model.predict(co2_input)[0])

        # Predict Cost
        cost_input = pd.DataFrame([[scaled_dict[f] for f in cost_features]], columns=cost_features)
        cost_pred = float(store.cost_model.predict(cost_input)[0])

        # Clamp to non-negative
        co2_pred = max(co2_pred, 0.0)
        cost_pred = max(cost_pred, 0.0)

        results.append(
            {
                "material_name": mat["Material_Name"],
                "category": mat["Category"],
                "predicted_co2_kg": co2_pred,
                "predicted_cost_usd": cost_pred,
                "biodegradable": str(mat["Biodegradable"]).strip().lower() == "yes",
            }
        )

    df = pd.DataFrame(results)

    if df.empty:
        return []

    # Normalize scores (lower is better)
    for col, score_col in [("predicted_co2_kg", "co2_score"), ("predicted_cost_usd", "cost_score")]:
        col_min, col_max = df[col].min(), df[col].max()
        if col_max == col_min:
            df[score_col] = 0.0
        else:
            df[score_col] = (df[col] - col_min) / (col_max - col_min)

    df["combined_score"] = w_co2 * df["co2_score"] + w_cost * df["cost_score"]

    # Round for readability
    df["predicted_co2_kg"] = df["predicted_co2_kg"].round(3)
    df["predicted_cost_usd"] = df["predicted_cost_usd"].round(2)
    df["combined_score"] = df["combined_score"].round(3)

    top5 = df.nsmallest(5, "combined_score").reset_index(drop=True)
    top5["rank"] = range(1, len(top5) + 1)

    return top5[
        ["rank", "material_name", "category", "predicted_co2_kg", "predicted_cost_usd", "biodegradable", "combined_score"]
    ].to_dict("records")


# ── Endpoints ────────────────────────────────────────────────────────────────


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if store.loaded else "degraded",
        models_loaded=store.loaded,
        model_version=store.metadata.get("model_version", "unknown"),
    )


@app.get("/model-info", response_model=ModelInfoResponse, tags=["System"])
def model_info():
    """Get model training metadata and performance metrics."""
    if not store.loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")
    return ModelInfoResponse(**store.metadata)


@app.post("/recommend", response_model=RecommendResponse, tags=["Recommendations"])
def recommend(req: RecommendRequest):
    """
    Get top-5 eco-friendly packaging recommendations.

    Provide product weight, volume, shipping distance & mode,
    and your optimization preference (eco / cost / balanced).
    """
    recs = get_recommendations(
        weight_kg=req.weight_kg,
        volume_m3=req.volume_m3,
        distance_km=req.distance_km,
        shipping_mode=req.shipping_mode.value,
        optimization=req.optimization.value,
    )

    if not recs:
        raise HTTPException(status_code=500, detail="No recommendations generated")

    return RecommendResponse(
        product_weight_kg=req.weight_kg,
        shipping_distance_km=req.distance_km,
        shipping_mode=req.shipping_mode.value,
        optimization=req.optimization.value,
        recommendations=[MaterialRecommendation(**r) for r in recs],
    )
