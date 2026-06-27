import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from db.session import SessionLocal
from monitoring.metrics.daos import save_system_log
from monitoring.alerts.alert_manager import AlertManager

class SystemLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Read request body if needed (requires some tricks in Starlette to not consume the stream, skipping for simplicity)
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            status_code = response.status_code
            error_message = None
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            status_code = 500
            error_message = str(e)
            raise e
        finally:
            # We don't want to log every single /health call to avoid spamming the DB,
            # but for this assignment we will log most endpoints.
            if "/health" not in request.url.path:
                # Save to DB
                db = SessionLocal()
                try:
                    save_system_log(
                        db=db,
                        request_id=request_id,
                        endpoint=request.url.path,
                        latency_ms=process_time,
                        status_code=status_code,
                        error_message=error_message,
                        request_payload=None
                    )
                    # Check Alerts
                    alert_mgr = AlertManager(db)
                    alert_mgr.check_latency_alert(request.url.path, process_time)
                finally:
                    db.close()
                    
        return response
