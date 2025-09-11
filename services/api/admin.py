from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import os, json, subprocess
from google.cloud import pubsub_v1, firestore

# --- Constants for Promotion Guard ---
# Define metric budgets. In a real system, these might come from config.
METRIC_BUDGETS = {
    "val_mae": 50.0,  # Maximum acceptable validation Mean Absolute Error
    "p95_ms": 2000,   # Maximum acceptable p95 latency in milliseconds
}

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets

# --- Security ---
# This uses a simple bearer token for authentication. In a production system,
# this should be replaced with a more robust OIDC or JWT validation flow.
bearer_scheme = HTTPBearer()
ADMIN_API_BEARER_TOKEN = os.getenv("API_BEARER")

def require_admin(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """Dependency to ensure the user is an admin."""
    if not ADMIN_API_BEARER_TOKEN:
        raise HTTPException(status_code=500, detail="Admin bearer token not configured on server.")

    is_authorized = secrets.compare_digest(creds.credentials, ADMIN_API_BEARER_TOKEN)
    if not is_authorized:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid or missing bearer token.")

    # Return a mock user object. In a real system, this would come from the token claims.
    return {"uid": "api-admin-user", "isAdmin": True}


router = APIRouter(prefix="/v1/admin", tags=["admin"], dependencies=[Depends(require_admin)])
publisher = pubsub_v1.PublisherClient()
db = firestore.Client()
PROMOTE_TOPIC = os.getenv("PROMOTE_TOPIC")

class PromoteReq(BaseModel):
    modelId: str
    rolloutRatio: float = 0.10
    notes: str | None = None
    trigger: str = "pubsub"

@router.post("/models/promote")
def promote(req: PromoteReq, user=Depends(require_admin)):
    # --- Promotion Guard Logic ---
    model_ref = db.collection("model_registry").document(req.modelId)
    model_doc = model_ref.get()

    if not model_doc.exists:
        raise HTTPException(status_code=404, detail=f"Model {req.modelId} not found.")

    model_data = model_doc.to_dict()
    metrics = model_data.get("metrics", {})

    if not metrics:
        # Allow promotion if no metrics are present, but maybe log a warning.
        print(f"Warning: Promoting model {req.modelId} without any metrics.")
    else:
        val_mae = metrics.get("val_mae")
        p95_ms = metrics.get("p95_ms")

        if val_mae and val_mae > METRIC_BUDGETS["val_mae"]:
            raise HTTPException(status_code=400, detail=f"Promotion failed: val_mae ({val_mae}) exceeds budget ({METRIC_BUDGETS['val_mae']}).")

        if p95_ms and p95_ms > METRIC_BUDGETS["p95_ms"]:
            raise HTTPException(status_code=400, detail=f"Promotion failed: p95_ms ({p95_ms}) exceeds budget ({METRIC_BUDGETS['p95_ms']}).")
    # --- End Promotion Guard ---

    payload = {
        "modelId": req.modelId,
        "rolloutRatio": max(0.0, min(1.0, req.rolloutRatio)),
        "requestedBy": user["uid"],
        "notes": req.notes or ""
    }
    if req.trigger == "job":
        job = os.getenv("PROMOTER_JOB_NAME", "model-promoter")
        region = os.getenv("REGION", "us-central1")
        # NOTE: Using gcloud CLI is not ideal in a container.
        # It's better to use the Cloud Run Jobs API client library.
        subprocess.run([
            "gcloud","run","jobs","execute",job,
            "--region",region,"--args",json.dumps(payload)
        ], check=True)
    else:
        publisher.publish(PROMOTE_TOPIC, json.dumps(payload).encode("utf-8"))
    return {"ok": True, "enqueued": True, "payload": payload}

class RollbackReq(BaseModel):
    toModelId: str | None = None

@router.post("/models/rollback")
def rollback(req: RollbackReq, user=Depends(require_admin)):
    payload = { "rollbackTo": req.toModelId, "requestedBy": user["uid"] }
    # The user's spec sends a message with an "action" key.
    message_payload = {"action": "rollback", **payload}
    publisher.publish(PROMOTE_TOPIC, json.dumps(message_payload).encode("utf-8"))
    return {"ok": True}
