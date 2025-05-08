# Тесты для системы автоматической транскрипции и записи встреч

## Настройка окружения

### Настройка тестовой базы данных PostgreSQL

Для запуска полных интеграционных тестов необходима PostgreSQL база данных. Тесты автоматически обнаруживают доступность PostgreSQL и в случае ее отсутствия будут использовать SQLite.

#### Вариант 1: Docker

```bash
# Запуск PostgreSQL контейнера для тестов
docker run --name test-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=test_meetings_db -p 5432:5432 -d postgres:13

# Проверка работоспособности
docker exec -it test-postgres psql -U postgres -c "SELECT version();"
```

#### Вариант 2: Локальная установка PostgreSQL

1. Установите PostgreSQL
2. Создайте базу данных для тестов:
```sql
CREATE DATABASE test_meetings_db;
```

### Настройка переменных окружения

Вы можете настроить параметры подключения к PostgreSQL с помощью следующих переменных окружения:

```bash
# Для Windows (PowerShell)
$env:PG_TEST_USER = "ваш_пользователь"         # По умолчанию: postgres
$env:PG_TEST_PASSWORD = "ваш_пароль"           # По умолчанию: postgres
$env:PG_TEST_HOST = "хост_базы_данных"         # По умолчанию: localhost
$env:PG_TEST_PORT = "порт_базы_данных"         # По умолчанию: 5432
$env:PG_TEST_DB = "имя_тестовой_базы_данных"   # По умолчанию: test_meetings_db

# ИЛИ задать полный URL подключения
$env:POSTGRES_TEST_DATABASE_URL = "postgresql://пользователь:пароль@хост:порт/база_данных"

# Для Linux/Mac
export PG_TEST_USER="ваш_пользователь"
export PG_TEST_PASSWORD="ваш_пароль"
export PG_TEST_HOST="хост_базы_данных"
export PG_TEST_PORT="порт_базы_данных"
export PG_TEST_DB="имя_тестовой_базы_данных"

# ИЛИ задать полный URL подключения
export POSTGRES_TEST_DATABASE_URL="postgresql://пользователь:пароль@хост:порт/база_данных"
```

## Запуск тестов

### Запуск всех тестов

```bash
cd backend
python -m pytest
```

### Запуск конкретной группы тестов

```bash
# Тесты авторизации
python -m pytest tests/integration/test_auth.py

# Тесты для встреч
python -m pytest tests/integration/test_meetings.py
```

### Запуск конкретного теста

```bash
python -m pytest tests/integration/test_meetings.py::test_meeting_search_integration -v
```

## Особенности запуска тестов

- Тесты полнотекстового поиска (`test_meeting_search_integration`) требуют PostgreSQL и будут пропущены при использовании SQLite
- Если тесты не могут подключиться к PostgreSQL, они автоматически используют SQLite в памяти
- При использовании PostgreSQL, после каждого теста данные очищаются с помощью `TRUNCATE TABLE CASCADE`

## Test Structure

- `conftest.py` - Common test fixtures and configuration
- `test_models.py`