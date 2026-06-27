# MLOps Monitoring & Observability

## Overview
The monitoring system uses a custom-built, database-backed observability layer tracking system metrics, LLM usages, and mathematical data drift without requiring expensive third-party SaaS tools.

## System Observability
We capture API traces using the `SystemLogMiddleware` (`api/middleware.py`).
Every incoming request generates a `SystemLog` record in PostgreSQL containing:
- Endpoint path (`/api/v1/generate-goal-plan`)
- Processing Latency (ms)
- Status code (e.g. 200, 500)
- Error details (if any)
- Request ID mapping

## Data Drift (PSI)
We monitor "Data Drift" using the Population Stability Index (PSI) in `monitoring/drift/data_drift.py`.
- **Phase 1**: Training data defines our "Baseline" distribution (e.g. goal_length and complexity_score).
- **Phase 2**: Real-time inferences form the "Current" distribution.
If the input data statistically diverges from the baseline (PSI > 0.2), the system saves a `DriftMetric` and fires a `HIGH` priority `Alert` to the database.

## Concept Drift
The `ConceptDriftTracker` (`monitoring/drift/concept_drift.py`) monitors rolling accuracies. If the model's accuracy drops below a configurable threshold (e.g., < 75% over the last 100 predictions), it raises a Concept Drift alert indicating that the model's relationships have degraded and retraining is required.

## Alerting Engine
`AlertManager` evaluates thresholds across System Logs, LLM Metrics, and Drift Metrics. It generates alerts directly into the `Alerts` table, which can be visualized via standard BI dashboards or queried directly via the `/api/v1/metrics` endpoint.
