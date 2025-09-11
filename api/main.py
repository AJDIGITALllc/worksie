from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI()

class CreateEstimate(BaseModel):
    imagePath: str
    domain: str
    orgId: str
    projectId: str

@app.post("/v1/estimates")
def create_estimate(req: CreateEstimate):
    est_id = str(uuid.uuid4())
    fast = {"total": 325.00, "confidence": 0.62, "items": [{"part":"Front Bumper","regionId":"R1","labor":120,"parts":205,"total":325}]}
    # In a real app, this would trigger a background job to refine the estimate.
    return {"estimateId": est_id, "fastEstimate": fast}
