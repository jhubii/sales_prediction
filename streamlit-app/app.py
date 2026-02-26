import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import gdown
import os

from db import init_db, insert_prediction, fetch_latest

FILE_ID = "12wWayMKI5I15hoyrqBP0HH32Fh4Cx43h"

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "random_forest_sales_model.pkl"
INFO_PATH = ROOT / "models" / "feature_info.json"


def download_model():
    os.makedirs(MODEL_PATH.parent, exist_ok=True)

    if not MODEL_PATH.exists():
        url = f"https://drive.google.com/uc?id={FILE_ID}"
        gdown.download(url, str(MODEL_PATH), quiet=False)


@st.cache_resource
def load_artifacts():
    download_model()

    model = joblib.load(MODEL_PATH)
    info = json.loads(INFO_PATH.read_text(encoding="utf-8"))

    features = info.get("all_features")
    cat_cols = info.get("categorical_features", [])
    cat_vals = info.get("categorical_values", {})

    return model, features, cat_cols, cat_vals


def main():
    st.title("Sales Predictor")
    init_db()

    model, features, cat_cols, cat_vals = load_artifacts()

    mode = st.radio("Mode", ["Manual Input", "CSV Upload", "History"], horizontal=True)

    # ------------------ MANUAL INPUT ------------------
    if mode == "Manual Input":
        st.subheader("Input Features")

        inputs = {}
        for col in features:
            if col in cat_cols:
                inputs[col] = st.selectbox(col, cat_vals.get(col, []))
            else:
                inputs[col] = st.number_input(col, value=0.0)

        if st.button("Predict"):
            X = pd.DataFrame([inputs], columns=features)
            log_pred = float(model.predict(X)[0])
            pred = float(np.expm1(log_pred))

            insert_prediction(
                datetime.now().isoformat(timespec="seconds"), json.dumps(inputs), pred
            )

            st.success(f"Predicted Sales: ${pred:,.2f}")

    # ------------------ CSV UPLOAD ------------------
    elif mode == "CSV Upload":
        st.subheader("Upload CSV for Batch Prediction")
        st.caption("Required columns:")
        st.code(", ".join(features))

        file = st.file_uploader("Upload CSV", type=["csv"])
        if file:
            df = pd.read_csv(file)
            st.dataframe(df.head(20), use_container_width=True)

            if st.button("Predict CSV"):
                missing = [c for c in features if c not in df.columns]
                if missing:
                    st.error(f"Missing columns: {missing}")
                    return

                X = df[features].copy()
                log_preds = model.predict(X)
                preds = np.expm1(log_preds)

                out = df.copy()
                out["prediction"] = preds
                out["prediction_formatted"] = out["prediction"].map(
                    lambda x: f"${x:,.2f}"
                )

                st.success(f"Predicted {len(out)} rows.")
                st.dataframe(out.head(50), use_container_width=True)

                # download
                st.download_button(
                    "Download predictions.csv",
                    out.to_csv(index=False).encode("utf-8"),
                    "predictions.csv",
                    "text/csv",
                )

    # ------------------ HISTORY ------------------
    else:
        st.subheader("Recent Predictions (DB)")
        rows = fetch_latest(30)
        if rows:
            df_hist = pd.DataFrame(
                rows, columns=["id", "created_at", "features_json", "prediction"]
            )
            df_hist["prediction"] = df_hist["prediction"].map(lambda x: f"${x:,.2f}")
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.info("No predictions yet.")


if __name__ == "__main__":
    main()
