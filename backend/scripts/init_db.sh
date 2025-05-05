#!/bin/bash

# Выводим информацию о переменных окружения для отладки
echo "Database connection parameters:"
echo "Host: $POSTGRES_SERVER"
echo "Port: $POSTGRES_PORT"
echo "User: $POSTGRES_USER"
echo "Database: $POSTGRES_DB"

# Ждем, пока база данных будет готова
echo "Waiting for database..."
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if PGPASSWORD=$POSTGRES_PASSWORD pg_isready -h "$POSTGRES_SERVER" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "postgres" > /dev/null 2>&1; then
        echo "Database is ready!"
        break
    fi
    
    retry_count=$((retry_count + 1))
    echo "Attempt $retry_count of $max_retries: Database is not ready yet..."
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo "Could not connect to database after $max_retries attempts"
    exit 1
fi

# Проверка, нужно ли сбросить базу данных
if [ "$RESET_DB" = "true" ]; then
    echo "Resetting database..."
    python scripts/reset_db.py
else
    # Применяем миграции
    echo "Running database migrations..."
    alembic upgrade head || true
fi

# Заполняем базу тестовыми данными
echo "Seeding database with test data..."
python scripts/seed_all.py

# Запускаем приложение
echo "Starting application..."
exec uvicorn app:app --host 0.0.0.0 --port 8000 