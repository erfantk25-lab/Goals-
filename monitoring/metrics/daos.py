import logging
from sqlalchemy.orm import Session
from db.models import ModelMetric, LLMMetric, SystemLog, DriftMetric, Alert

logger = logging.getLogger(__name__)

def save_system_log(db: Session, request_id: str, endpoint: str, latency_ms: float, status_code: int, error_message: str = None, request_payload: dict = None):
    try:
        log = SystemLog(
            request_id=request_id,
            endpoint=endpoint,
            latency_ms=latency_ms,
            status_code=status_code,
            error_message=error_message,
            request_payload=request_payload
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save system log: {e}")
        db.rollback()

def save_llm_metric(db: Session, prompt_version_id: str, input_tokens: int, output_tokens: int, latency_ms: float, validation_success: bool, category: str = None):
    try:
        metric = LLMMetric(
            prompt_version_id=prompt_version_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            validation_success=validation_success,
            category=category
        )
        db.add(metric)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save llm metric: {e}")
        db.rollback()

def save_model_metric(db: Session, metric_name: str, metric_value: float, model_version: str):
    try:
        metric = ModelMetric(
            metric_name=metric_name,
            metric_value=metric_value,
            model_version=model_version
        )
        db.add(metric)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save model metric: {e}")
        db.rollback()

def save_drift_metric(db: Session, drift_score: float, drift_detected: bool, method: str, feature_name: str = None):
    try:
        metric = DriftMetric(
            drift_score=drift_score,
            drift_detected=drift_detected,
            method=method,
            feature_name=feature_name
        )
        db.add(metric)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save drift metric: {e}")
        db.rollback()

def save_alert(db: Session, alert_type: str, severity: str, message: str):
    try:
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            message=message
        )
        db.add(alert)
        db.commit()
        print(f"🚨 [ALERT] {severity}: {alert_type} - {message}")
    except Exception as e:
        logger.error(f"Failed to save alert: {e}")
        db.rollback()
