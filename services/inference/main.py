import time
from fastapi import FastAPI, Request
from pydantic import BaseModel
from .inference import predict as run_prediction

app = FastAPI(
    title="Worksie Inference Service",
    description="Service for running ML model inference with canary support.",
    version="1.0.0",
)

@app.get("/healthz", tags=["health"])
def healthz():
    return {"ok": True}

@app.get("/synthetic", tags=["health"])
def synthetic():
    t0 = time.time()
    # In a real scenario, you might run a no-op model call or a cached path.
    elapsed_ms = int((time.time() - t0) * 1000)
    print(f"SYNTHETIC inference elapsed_ms={elapsed_ms}")
    return {"ok": True, "elapsed_ms": elapsed_ms}

class PredictionRequest(BaseModel):
    image_path: str
    org_id: str

@app.post("/predict", tags=["inference"])
async def predict(request: PredictionRequest):
    """Endpoint to run a prediction."""
    try:
        result = run_prediction(request.image_path, request.org_id)
        return {"success": True, "prediction": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
