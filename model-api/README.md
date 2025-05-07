# Model API

API сервис для обработки аудио и текстовых данных встреч, включая транскрибацию, определение спикеров, генерацию сводок и протоколов, а также чат-бот для ответов на вопросы о встречах.

## Требования

- Python 3.8+
- pip (менеджер пакетов Python)

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
```

2. Активируйте виртуальное окружение:
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск API

1. Убедитесь, что виртуальное окружение активировано (в начале строки командной строки должен быть префикс `(venv)`)

2. Запустите сервер:
```bash
uvicorn main:app --reload
```

Сервер будет доступен по адресу: http://localhost:8000

## API Endpoints

- `POST /transcribe` - транскрибация аудио
- `POST /summary` - генерация сводки
- `POST /speakers` - определение спикеров
- `POST /speaker-transcript` - транскрипция с определением спикеров
- `POST /protocol` - генерация протокола
- `POST /chat/answer` - ответы на вопросы о встрече
- `GET /chat/meeting/{meeting_id}` - получение информации о встрече

## Запуск тестов

1. Убедитесь, что виртуальное окружение активировано

2. Запустите тесты:
```bash
pytest tests/test_endpoints.py -v
```

## Переменные окружения

Создайте файл `.env` в корневой директории проекта со следующими параметрами:

```
BACKEND_API_URL=http://localhost:8000/api  # URL основного бэкенда
```

## Структура проекта

```
model-api/
├── main.py              # Основной файл FastAPI приложения
├── requirements.txt     # Зависимости проекта
├── tests/              # Тесты
│   ├── __init__.py
│   └── test_endpoints.py
├── services/           # Сервисы обработки
│   ├── transcriber.py
│   ├── summarizer.py
│   ├── diarizer.py
│   ├── speaker_text.py
│   ├── protocol_generator_local.py
│   └── meeting_chatbot.py
├── models/            # Модели данных
│   ├── Meeting.py
│   └── ChatInput.py
└── utils/            # Вспомогательные функции
    ├── io.py
    └── data_formater.py
```

## Документация API

После запуска сервера, документация API доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 