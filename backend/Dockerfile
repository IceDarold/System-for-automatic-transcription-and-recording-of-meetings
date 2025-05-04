FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание непривилегированного пользователя
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Сделаем скрипт исполняемым
RUN chmod +x /app/scripts/init_db.sh

# Запуск приложения
CMD ["sh", "-c", "/app/scripts/init_db.sh && uvicorn app:app --host 0.0.0.0 --port 8000"] 