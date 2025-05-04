#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! pg_isready -h db -p 5432 -U postgres; do
    sleep 1
done
echo "PostgreSQL is ready"

echo "Running migrations..."
cd /app && PYTHONPATH=/app alembic upgrade head

echo "Starting application..."
uvicorn app:app --host 0.0.0.0 --port 8000 