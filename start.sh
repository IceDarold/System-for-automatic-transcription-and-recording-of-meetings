#!/bin/bash

# Перейти в корневую папку проекта
cd "$(dirname "$0")"

# Запуск бэкенда (FastAPI)
echo "🚀 Запускаем FastAPI backend..."
cd backend

# Создать виртуальное окружение, если его нет
if [ ! -d "venv" ]; then
  echo "🔧 Создаём виртуальное окружение..."
  python -m venv venv
fi

# Активация виртуального окружения
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
  source venv/bin/activate
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
  source venv/Scripts/activate
else
  echo "⚠️ Неизвестная ОС. Попробуем использовать bin для Unix..."
  source venv/bin/activate
fi

# Установить зависимости, если их нет
if [ ! -f "venv/.requirements_installed" ]; then
  echo "📦 Устанавливаем зависимости для FastAPI..."
  pip install -r requirements.txt --quiet
  touch venv/.requirements_installed
fi

# Запуск бэкенда
echo "🔌 Бэкенд запущен на http://127.0.0.1:8000"
uvicorn app:app --reload &
BACKEND_PID=$!

# Запуск фронтенда (React)
echo "🌐 Запускаем React-фронтенд..."
cd ../frontend

# Установить зависимости, если их нет
if [ ! -d "node_modules" ]; then
  echo "📦 Устанавливаем зависимости для React..."
  npm install
fi

echo "📱 Фронтенд будет доступен по адресу: http://localhost:3000"
npm start &
FRONTEND_PID=$!

# Ловим сигналы завершения, чтобы остановить оба процесса
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM

# Ждём бесконечно, пока пользователь не нажмёт Ctrl+C
wait