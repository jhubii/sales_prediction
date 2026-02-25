from fastapi import FastAPI, HTTPException
from .schemas import PredictRequest, PredictResponse
from .model_loader import predict_from_dict, get_feature_order

app = FastAPI(title="Sales Model API", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/features")
def features():
    try:
        return {"feature_order": get_feature_order()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        pred = predict_from_dict(req.features)
        return PredictResponse(prediction=pred)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # IMPORTANT: show real error instead of "Prediction failed."
        raise HTTPException(status_code=500, detail=str(e))
