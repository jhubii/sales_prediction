import json
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "random_forest_sales_model.pkl"
FEATURE_INFO_PATH = ROOT / "models" / "feature_info.json"

_model = None
_features = None
_cat_cols = None
_num_cols = None
_cat_vals = None


def load_artifacts():
    global _model, _features, _cat_cols, _num_cols, _cat_vals

    if _model is None:
        _model = joblib.load(MODEL_PATH)

    if _features is None:
        info = json.loads(FEATURE_INFO_PATH.read_text(encoding="utf-8"))

        _features = (
            info.get("all_features")
            or info.get("feature_order")
            or info.get("features")
        )
        if not _features:
            raise ValueError(
                "feature_info.json must contain 'all_features' (or 'feature_order'/'features')."
            )

        _cat_cols = info.get("categorical_features", [])
        _num_cols = info.get("numeric_features", [])
        _cat_vals = info.get("categorical_values", {})


def coerce_types(row: dict) -> dict:
    """Ensure numeric columns are numeric (MVC often sends numbers as strings)."""
    out = dict(row)

    for c in _num_cols:
        v = out.get(c)
        if v is None:
            continue
        try:
            out[c] = float(v)
        except Exception:
            raise ValueError(f"Invalid numeric value for '{c}': {v}")

    for c in _cat_cols:
        v = out.get(c)
        if v is None:
            continue
        allowed = _cat_vals.get(c)
        if allowed and v not in allowed:
            raise ValueError(f"Invalid value for '{c}': {v}")

    return out


def predict_from_dict(payload: dict) -> float:
    load_artifacts()

    missing = [f for f in _features if f not in payload]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    row = {f: payload[f] for f in _features}
    row = coerce_types(row)

    X = pd.DataFrame([row], columns=_features)

    log_pred = float(_model.predict(X)[0])
    pred = float(np.expm1(log_pred))
    return pred


def get_feature_order():
    load_artifacts()
    return _features
