from fastapi import FastAPI
from core.config import settings
from api.endpoints import goals, health

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="MLOps + AI System for Brian Tracy 12-Step Goal Planning",
    version="1.0.0"
)

app.include_router(health.router, tags=["Health"])
app.include_router(goals.router, prefix=settings.API_V1_STR, tags=["Goals"])
