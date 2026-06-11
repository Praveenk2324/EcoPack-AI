"""
Model definitions for EcoPack-AI.

Both CO2 and Cost predictors use XGBoost — single model type,
consistent hyperparameters, easy to tune via params.yaml.
"""

import xgboost as xgb


def build_co2_model() -> xgb.XGBRegressor:
    """Build XGBoost regressor for CO2 emission prediction."""
    return xgb.XGBRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
    )


def build_cost_model() -> xgb.XGBRegressor:
    """Build XGBoost regressor for packaging cost prediction."""
    return xgb.XGBRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
    )
