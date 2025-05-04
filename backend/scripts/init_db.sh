#!/bin/bash

# Ждем, пока PostgreSQL будет готов
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h db -p 5432 -U postgres; do
    sleep 1
done

# Применяем миграции
echo "Applying database migrations..."
cd /app && PYTHONPATH=/app alembic upgrade head

echo "Database initialization completed!" 