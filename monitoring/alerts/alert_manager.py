from sqlalchemy.orm import Session
from monitoring.metrics.daos import save_alert

class AlertManager:
    def __init__(self, db: Session):
        self.db = db

    def check_drift_alert(self, drift_score: float, method: str):
        if drift_score > 0.2:
            save_alert(
                db=self.db,
                alert_type="DATA_DRIFT",
                severity="HIGH",
                message=f"Significant data drift detected. Score: {drift_score} ({method})"
            )

    def check_latency_alert(self, endpoint: str, latency_ms: float):
        if latency_ms > 2000:
            save_alert(
                db=self.db,
                alert_type="HIGH_LATENCY",
                severity="MEDIUM",
                message=f"High latency on {endpoint}: {latency_ms}ms"
            )

    def check_error_rate_alert(self, total_requests: int, error_requests: int):
        if total_requests > 10:
            error_rate = error_requests / total_requests
            if error_rate > 0.05:
                save_alert(
                    db=self.db,
                    alert_type="HIGH_ERROR_RATE",
                    severity="HIGH",
                    message=f"Error rate exceeded 5%: {error_rate*100:.1f}%"
                )

    def check_llm_validation_alert(self, total_llm_calls: int, failed_calls: int):
        if total_llm_calls > 10:
            fail_rate = failed_calls / total_llm_calls
            if fail_rate > 0.10:
                save_alert(
                    db=self.db,
                    alert_type="LLM_VALIDATION_FAILURE",
                    severity="HIGH",
                    message=f"LLM Invalid output rate exceeded 10%: {fail_rate*100:.1f}%"
                )
