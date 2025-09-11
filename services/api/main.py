from fastapi import FastAPI
from services.api.admin import router as admin_router

app = FastAPI(
    title="Worksie Admin API",
    description="API for managing ML models and other administrative tasks.",
    version="1.0.0",
)

import time
from fastapi import Request

app.include_router(admin_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Worksie Admin API"}

@app.get("/healthz", tags=["health"])
def healthz():
    return {"ok": True}

@app.get("/synthetic", tags=["health"])
def synthetic(request: Request):
    t0 = time.time()
    # In a real scenario, you might add a quick check to a dependency like a DB.
    elapsed_ms = int((time.time() - t0) * 1000)
    print(f"SYNTHETIC api elapsed_ms={elapsed_ms}")
    return {"ok": True, "elapsed_ms": elapsed_ms}
