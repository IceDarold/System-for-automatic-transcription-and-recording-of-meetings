#!/bin/bash

# Запуск FastAPI бэкенда
echo "🚀 Запуск FastAPI бэкенда..."
cd backend || { echo "Не найдена папка 'backend'"; exit 1; }

# Активация виртуального окружения (если используется)
source venv/Scripts/activate || echo "Виртуальное окружение не найдено"

# Запуск сервера FastAPI
uvicorn app:app --port 8000 &
BACKEND_PID=$!

# Ждём немного, чтобы FastAPI успел запуститься
sleep 3

# Запуск фронтенда
echo "🧭 Запуск React фронтенда..."
cd ../frontend || { echo "Не найдена папка 'frontend'"; kill $BACKEND_PID; exit 1; }


npm run build &

# Лог для завершения
trap "kill $BACKEND_PID; exit" INT TERM

echo "✅ Бэкенд и фронтенд запущены"
wait