from fastapi import FastAPI
from core.config import settings
from api.endpoints import goals, health, metrics, feedback

from fastapi.responses import JSONResponse
from fastapi import Request
from api.middleware import SystemLogMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="MLOps + AI System for Brian Tracy 12-Step Goal Planning",
    version="1.0.0"
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "details": str(exc)},
    )

app.add_middleware(SystemLogMiddleware)

app.include_router(health.router, tags=["Health"])
app.include_router(metrics.router, prefix=settings.API_V1_STR, tags=["Metrics"])
app.include_router(goals.router, prefix=settings.API_V1_STR, tags=["Goals"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_STR}/feedback", tags=["Feedback"])
