from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from api.dependencies import get_db
from sqlalchemy.sql import func
from api.schemas import DashboardMetricsResponse
from db.models import SystemLog, ModelMetric, LLMMetric, Alert, DriftMetric, Feedback

router = APIRouter()

@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """Expose system metrics for observability tools."""
    total_requests = db.query(SystemLog).count()
    error_requests = db.query(SystemLog).filter(SystemLog.status_code >= 400).count()
    total_alerts = db.query(Alert).count()
    
    return {
        "system": {
            "total_requests": total_requests,
            "error_rate": (error_requests / total_requests) if total_requests > 0 else 0,
            "total_alerts": total_alerts
        },
        "status": "healthy"
    }

@router.get("/dashboard-metrics", response_model=DashboardMetricsResponse)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Provides aggregated metrics for the Streamlit MLOps Dashboard."""
    total_requests = db.query(SystemLog).count()
    error_requests = db.query(SystemLog).filter(SystemLog.status_code >= 400).count()
    total_alerts = db.query(Alert).count()
    error_rate = (error_requests / total_requests) if total_requests > 0 else 0.0

    latest_drift = db.query(DriftMetric).order_by(DriftMetric.timestamp.desc()).first()
    latest_drift_score = latest_drift.drift_score if latest_drift else 0.0

    avg_latency = db.query(func.avg(LLMMetric.latency_ms)).scalar() or 0.0
    total_input = db.query(func.sum(LLMMetric.input_tokens)).scalar() or 0
    total_output = db.query(func.sum(LLMMetric.output_tokens)).scalar() or 0

    latest_acc = db.query(ModelMetric).filter(ModelMetric.metric_name == "rolling_accuracy").order_by(ModelMetric.timestamp.desc()).first()
    latest_model_accuracy = latest_acc.metric_value if latest_acc else 0.0

    return DashboardMetricsResponse(
        total_requests=total_requests,
        error_rate=error_rate,
        total_alerts=total_alerts,
        latest_drift_score=latest_drift_score,
        avg_llm_latency_ms=avg_latency,
        total_tokens_used=total_input + total_output,
        latest_model_accuracy=latest_model_accuracy
    )

def _run_retraining():
    """Background task: retrains the ML model."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info("🔄 Background retraining job started...")
        from ml.training.train import GoalDifficultyPredictor
        predictor = GoalDifficultyPredictor()
        predictor.train()
        logger.info("✅ Background retraining job completed successfully!")
    except Exception as e:
        logger.error(f"❌ Retraining failed: {e}")

@router.post("/mlops/retrain")
def trigger_retraining(background_tasks: BackgroundTasks):
    """Triggers a live ML model retraining job in the background."""
    background_tasks.add_task(_run_retraining)
    return {
        "status": "accepted",
        "message": "Model retraining job dispatched in the background. Check server logs for progress."
    }

@router.get("/metrics-history")
def get_metrics_history(db: Session = Depends(get_db), limit: int = 20):
    """Returns time-series data for dashboard charts."""
    llm_rows = db.query(LLMMetric).order_by(LLMMetric.timestamp.desc()).limit(limit).all()
    drift_rows = db.query(DriftMetric).order_by(DriftMetric.timestamp.desc()).limit(limit).all()

    llm_history = [
        {
            "timestamp": str(r.timestamp)[:16],
            "latency_ms": round(r.latency_ms, 1),
            "tokens": r.input_tokens + r.output_tokens,
            "prompt_version": r.prompt_version_id
        }
        for r in reversed(llm_rows)
    ]

    drift_history = [
        {
            "timestamp": str(r.timestamp)[:16],
            "drift_score": round(r.drift_score, 4)
        }
        for r in reversed(drift_rows)
    ]

    return {
        "llm_history": llm_history,
        "drift_history": drift_history
    }

@router.get("/feedback-summary")
def get_feedback_summary(db: Session = Depends(get_db)):
    """Returns aggregated feedback ratings."""
    feedback_rows = db.query(Feedback).all()
    if not feedback_rows:
        return {"average_rating": 0, "total_ratings": 0, "distribution": {}}
    
    ratings = [f.rating for f in feedback_rows]
    distribution = {i: ratings.count(i) for i in range(1, 6)}
    
    return {
        "average_rating": sum(ratings) / len(ratings),
        "total_ratings": len(ratings),
        "distribution": distribution
    }
