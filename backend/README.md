# Meeting Transcription System - Backend

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл .env в корневой директории backend со следующим содержимым:
```env
PROJECT_NAME=Meeting Transcription System
VERSION=1.0.0
API_V1_STR=/api/v1

# JWT Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=meeting_system
```

4. Создайте базу данных PostgreSQL:
```bash
createdb meeting_system
```

5. Примените миграции:
```bash
alembic upgrade head
```

## Запуск

```bash
uvicorn app:app --reload
```

## API Endpoints

### Аутентификация

- `POST /api/v1/auth/register` - Регистрация нового пользователя
- `POST /api/v1/auth/login` - Вход в систему
- `POST /api/v1/auth/refresh` - Обновление токена
- `POST /api/v1/auth/logout` - Выход из системы

## Тестирование

Для тестирования API вы можете использовать Swagger UI, доступный по адресу:
```
http://localhost:8000/docs
```

## Безопасность

- Все пароли хешируются с использованием bcrypt
- JWT токены имеют ограниченное время жизни
- Реализована система ролей (user, superadmin)
- Ведется аудит действий пользователей 