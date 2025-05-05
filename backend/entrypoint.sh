#!/bin/bash
set -e

# Run database initialization script (which includes waiting for PostgreSQL)
echo "Initializing database..."
/app/scripts/init_db.sh

# Start the application
echo "Starting backend application..."
uvicorn app:app --host 0.0.0.0 --port 8000 