from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import os, json, subprocess
from google.cloud import pubsub_v1

# Placeholder for the actual auth guard dependency
def auth_guard():
    # In a real application, this would validate a token
    # and return user info. For this implementation, we'll
    # return a mock user with admin privileges.
    return {"uid": "mock-admin-user", "isAdmin": True}

router = APIRouter(prefix="/v1/admin", tags=["admin"])
publisher = pubsub_v1.PublisherClient()
PROMOTE_TOPIC = os.getenv("PROMOTE_TOPIC", "projects/your-gcp-project-id/topics/promote-model")

def require_admin(user=Depends(auth_guard)):
    if not user or not user.get("isAdmin"):
        raise HTTPException(status_code=403, detail="Forbidden")
    return user

class PromoteReq(BaseModel):
    modelId: str
    rolloutRatio: float = 0.10
    notes: str | None = None
    trigger: str = "pubsub"

@router.post("/models/promote")
def promote(req: PromoteReq, user=Depends(require_admin)):
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
