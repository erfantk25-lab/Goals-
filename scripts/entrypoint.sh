#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."
# Note: In docker-compose we rely on service_healthy, but this is a fallback
sleep 3

echo "Running Database Migrations..."
alembic upgrade head

echo "Starting FastAPI server..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000
