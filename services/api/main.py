from fastapi import FastAPI
from services.api.admin import router as admin_router

app = FastAPI(
    title="Worksie Admin API",
    description="API for managing ML models and other administrative tasks.",
    version="1.0.0",
)

app.include_router(admin_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Worksie Admin API"}
