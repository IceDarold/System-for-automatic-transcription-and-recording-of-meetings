# Используем минимальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Указываем команду запуска FastAPI с автообновлением
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "info", "--reload"]

