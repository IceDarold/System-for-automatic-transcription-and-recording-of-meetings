from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Set-Cookie"],
)

access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
apiLink = "/api/v1"

@app.post(apiLink + "/auth/login")
def login():
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
        }


@app.get(apiLink + "/meetings")
def meetings():
    fakeDataLogin = {
  "items": [
    {
      "id": 1,
      "title": "Финансы: Оптимизация",
      "date": "2025-05-05T21:16:18.527Z",
      "tags": [
        { "id": 1, "label": "Финансы" },
        { "id": 2, "label": "Аналитика" }
      ],
      "participants": [
        { "id": 101, "name": "Иван Петров", "role": "Спикер" },
        { "id": 102, "name": "Мария Смирнова", "role": "Организатор" }
      ],
      "created_by": {
        "id": 201,
        "name": "Администратор",
        "role": "admin"
      },
      "description": "Обсуждение новых методов оптимизации финансовых процессов.",
      "access_level": "public",
      "status": "pending",
      "processing_progress": 45,
      "is_ready": False,
      "created_at": "2025-05-01T10:00:00.000Z",
      "updated_at": "2025-05-04T15:30:00.000Z"
    },
    {
      "id": 2,
      "title": "AI: Анализ данных",
      "date": "2025-05-06T14:00:00.000Z",
      "tags": [
        { "id": 3, "label": "AI" },
        { "id": 4, "label": "Данные" }
      ],
      "participants": [
        { "id": 103, "name": "Дмитрий Васильев", "role": "Аналитик" },
        { "id": 104, "name": "Екатерина Николаева", "role": "Спикер" }
      ],
      "created_by": {
        "id": 202,
        "name": "Moderator",
        "role": "moderator"
      },
      "description": "Анализ эффективности алгоритмов машинного обучения.",
      "access_level": "private",
      "status": "in progress",
      "processing_progress": 75,
      "is_ready": True,
      "created_at": "2025-04-28T09:00:00.000Z",
      "updated_at": "2025-05-04T12:00:00.000Z"
    },
    {
      "id": 3,
      "title": "Проекты: Управление",
      "date": "2025-05-07T10:00:00.000Z",
      "tags": [
        { "id": 5, "label": "Проекты" },
        { "id": 6, "label": "Управление" }
      ],
      "participants": [
        { "id": 105, "name": "Алексей Кузнецов", "role": "Модератор" },
        { "id": 106, "name": "Татьяна Иванова", "role": "Участник" }
      ],
      "created_by": {
        "id": 203,
        "name": "Project Manager",
        "role": "user"
      },
      "description": "Обмен полезным опытом между менеджерами проектов.",
      "access_level": "protected",
      "status": "completed",
      "processing_progress": 100,
      "is_ready": True,
      "created_at": "2025-04-20T10:00:00.000Z",
      "updated_at": "2025-05-05T14:21:34.761Z"
    },
    {
      "id": 4,
      "title": "Экология: Стандарты",
      "date": "2025-05-08T09:00:00.000Z",
      "tags": [
        { "id": 7, "label": "Экология" },
        { "id": 8, "label": "Стандарты" }
      ],
      "participants": [
        { "id": 107, "name": "Николай Андреев", "role": "Спикер" },
        { "id": 108, "name": "Ольга Петрова", "role": "Участник" }
      ],
      "created_by": {
        "id": 204,
        "name": "Eco Admin",
        "role": "admin"
      },
      "description": "Новые экологические нормы для сельскохозяйственных проектов.",
      "access_level": "public",
      "status": "planned",
      "processing_progress": 0,
      "is_ready": False,
      "created_at": "2025-04-15T11:00:00.000Z",
      "updated_at": "2025-04-15T11:00:00.000Z"
    },
    {
      "id": 5,
      "title": "Роботы в сельском хозяйстве",
      "date": "2025-05-09T11:00:00.000Z",
      "tags": [
        { "id": 9, "label": "Роботы" },
        { "id": 10, "label": "Технологии" }
      ],
      "participants": [
        { "id": 109, "name": "Антон Григорьев", "role": "Спикер" },
        { "id": 110, "name": "Людмила Соколова", "role": "Ассистент" }
      ],
      "created_by": {
        "id": 205,
        "name": "Tech Lead",
        "role": "admin"
      },
      "description": "Применение роботизированных систем в аграрном секторе.",
      "access_level": "private",
      "status": "in progress",
      "processing_progress": 30,
      "is_ready": False,
      "created_at": "2025-04-10T14:00:00.000Z",
      "updated_at": "2025-05-02T10:00:00.000Z"
    },
    {
      "id": 6,
      "title": "Кибербезопасность",
      "date": "2025-05-10T15:00:00.000Z",
      "tags": [
        { "id": 11, "label": "Безопасность" },
        { "id": 12, "label": "IT" }
      ],
      "participants": [
        { "id": 111, "name": "Артем Михайлов", "role": "Спикер" },
        { "id": 112, "name": "Алина Карпова", "role": "Участник" }
      ],
      "created_by": {
        "id": 206,
        "name": "Security Master",
        "role": "admin"
      },
      "description": "Обсуждение защиты данных в финансовых системах.",
      "access_level": "protected",
      "status": "in progress",
      "processing_progress": 50,
      "is_ready": False,
      "created_at": "2025-04-12T09:00:00.000Z",
      "updated_at": "2025-05-03T16:00:00.000Z"
    },
    {
      "id": 7,
      "title": "Цифровая трансформация",
      "date": "2025-05-11T12:00:00.000Z",
      "tags": [
        { "id": 13, "label": "Digital" },
        { "id": 14, "label": "Трансформация" }
      ],
      "participants": [
        { "id": 113, "name": "Владислав Семёнов", "role": "Спикер" },
        { "id": 114, "name": "Юлия Лебедева", "role": "Участник" }
      ],
      "created_by": {
        "id": 207,
        "name": "CTO",
        "role": "admin"
      },
      "description": "Как внедрить цифровые технологии в малом бизнесе.",
      "access_level": "public",
      "status": "completed",
      "processing_progress": 100,
      "is_ready": True,
      "created_at": "2025-04-14T08:00:00.000Z",
      "updated_at": "2025-05-04T18:00:00.000Z"
    },
    {
      "id": 8,
      "title": "Облачные решения",
      "date": "2025-05-12T10:30:00.000Z",
      "tags": [
        { "id": 15, "label": "Облако" },
        { "id": 16, "label": "Хранение" }
      ],
      "participants": [
        { "id": 115, "name": "Игорь Тихонов", "role": "Спикер" },
        { "id": 116, "name": "Светлана Яковлева", "role": "Аналитик" }
      ],
      "created_by": {
        "id": 208,
        "name": "Cloud Admin",
        "role": "admin"
      },
      "description": "Обзор облачных платформ и их применение в бизнесе.",
      "access_level": "private",
      "status": "pending",
      "processing_progress": 10,
      "is_ready": False,
      "created_at": "2025-04-18T12:00:00.000Z",
      "updated_at": "2025-05-05T10:00:00.000Z"
    }
  ],
  "has_more": True,
  "total": 20,
  "filters": {
    "search": "meetings",
    "status": ["pending", "in progress"]
  }
}
    return fakeDataLogin
  
@app.get(apiLink + "/teams") 
def teams():
  fakeDataTeams = {
  "items": [
    {
      "id": 1,
      "title": "Финансовая аналитика",
      "date": "2025-05-05T21:16:18.527Z",
      "tags": [
        { "id": 1, "label": "Финансы" },
        { "id": 2, "label": "Аналитика" }
      ],
      "participants": [
        { "id": 101, "name": "Иван Петров", "role": "Менеджер" },
        { "id": 102, "name": "Мария Смирнова", "role": "Аналитик" }
      ],
      "created_by": {
        "id": 201,
        "name": "Администратор",
        "role": "admin"
      },
      "description": "Команда по анализу финансовых потоков и бюджетированию.",
      "access_level": "public",
      "status": "active",
      "processing_progress": 100,
      "is_ready": True,
      "created_at": "2025-05-01T10:00:00.000Z",
      "updated_at": "2025-05-04T15:30:00.000Z"
    },
    {
      "id": 2,
      "title": "AI Исследования",
      "date": "2025-05-06T14:00:00.000Z",
      "tags": [
        { "id": 3, "label": "AI" },
        { "id": 4, "label": "ML" }
      ],
      "participants": [
        { "id": 103, "name": "Дмитрий Васильев", "role": "Разработчик" },
        { "id": 104, "name": "Екатерина Николаева", "role": "Тестировщик" }
      ],
      "created_by": {
        "id": 202,
        "name": "Moderator",
        "role": "moderator"
      },
      "description": "Команда, занимающаяся исследованием ИИ-алгоритмов и их применением.",
      "access_level": "private",
      "status": "active",
      "processing_progress": 100,
      "is_ready": True,
      "created_at": "2025-04-28T09:00:00.000Z",
      "updated_at": "2025-05-04T12:00:00.000Z"
    },
    {
      "id": 3,
      "title": "Проектный офис",
      "date": "2025-05-07T10:00:00.000Z",
      "tags": [
        { "id": 5, "label": "Управление проектами" },
        { "id": 6, "label": "PM" }
      ],
      "participants": [
        { "id": 105, "name": "Алексей Кузнецов", "role": "Менеджер" },
        { "id": 106, "name": "Татьяна Иванова", "role": "Ассистент" }
      ],
      "created_by": {
        "id": 203,
        "name": "Project Manager",
        "role": "user"
      },
      "description": "Команда по управлению внутренними и внешними проектами компании.",
      "access_level": "protected",
      "status": "active",
      "processing_progress": 100,
      "is_ready": True,
      "created_at": "2025-04-20T10:00:00.000Z",
      "updated_at": "2025-05-05T14:21:34.761Z"
    },
    {
      "id": 4,
      "title": "Экологический контроль",
      "date": "2025-05-08T09:00:00.000Z",
      "tags": [
        { "id": 7, "label": "Экология" },
        { "id": 8, "label": "Контроль" }
      ],
      "participants": [
        { "id": 107, "name": "Николай Андреев", "role": "Специалист" },
        { "id": 108, "name": "Ольга Петрова", "role": "Аналитик" }
      ],
      "created_by": {
        "id": 204,
        "name": "Eco Admin",
        "role": "admin"
      },
      "description": "Команда по контролю за экологическими стандартами и нормами.",
      "access_level": "public",
      "status": "active",
      "processing_progress": 100,
      "is_ready": True,
      "created_at": "2025-04-15T11:00:00.000Z",
      "updated_at": "2025-04-15T11:00:00.000Z"
    },
    {
      "id": 5,
      "title": "IT Безопасность",
      "date": "2025-05-09T11:00:00.000Z",
      "tags": [
        { "id": 9, "label": "Безопасность" },
        { "id": 10, "label": "Инфраструктура" }
      ],
      "participants": [
        { "id": 109, "name": "Антон Григорьев", "role": "Спец по безопасности" },
        { "id": 110, "name": "Людмила Соколова", "role": "Админ" }
      ],
      "created_by": {
        "id": 205,
        "name": "Tech Lead",
        "role": "admin"
      },
      "description": "Обеспечение кибербезопасности всей IT-инфраструктуры.",
      "access_level": "private",
      "status": "active",
      "processing_progress": 100,
      "is_ready": True,
      "created_at": "2025-04-10T14:00:00.000Z",
      "updated_at": "2025-05-02T10:00:00.000Z"
    },
    {
      "id": 6,
      "title": "Продуктовая команда",
      "date": "2025-05-10T15:00:00.000Z",
      "tags": [
        { "id": 11, "label": "Продукт" },
        { "id": 12, "label": "UX/UI" }
      ],
      "participants": [
        { "id": 111, "name": "Артем Михайлов", "role": "Продакт-менеджер" },
        { "id": 112, "name": "Алина Карпова", "role": "Дизайнер" }
      ],
      "created_by": {
        "id": 206,
        "name": "Security Master",
        "role": "admin"
      },
      "description": "Команда по разработке продуктов и улучшению пользовательского опыта.",
      "access_level": "protected",
      "status": "in progress",
      "processing_progress": 85,
      "is_ready": True,
      "created_at": "2025-04-12T09:00:00.000Z",
      "updated_at": "2025-05-03T16:00:00.000Z"
    },
    {
      "id": 7,
      "title": "HR Отдел",
      "date": "2025-05-11T12:00:00.000Z",
      "tags": [
        { "id": 13, "label": "HR" },
        { "id": 14, "label": "Кадры" }
      ],
      "participants": [
        { "id": 113, "name": "Владислав Семёнов", "role": "HR-менеджер" },
        { "id": 114, "name": "Юлия Лебедева", "role": "Рекрутер" }
      ],
      "created_by": {
        "id": 207,
        "name": "CTO",
        "role": "admin"
      },
      "description": "Команда по найму, обучению и развитию сотрудников.",
      "access_level": "public",
      "status": "completed",
      "processing_progress": 100,
      "is_ready": True,
      "created_at": "2025-04-14T08:00:00.000Z",
      "updated_at": "2025-05-04T18:00:00.000Z"
    },
    {
      "id": 8,
      "title": "DevOps Инженеры",
      "date": "2025-05-12T10:30:00.000Z",
      "tags": [
        { "id": 15, "label": "Инфраструктура" },
        { "id": 16, "label": "CI/CD" }
      ],
      "participants": [
        { "id": 115, "name": "Игорь Тихонов", "role": "DevOps" },
        { "id": 116, "name": "Светлана Яковлева", "role": "Инженер" }
      ],
      "created_by": {
        "id": 208,
        "name": "Cloud Admin",
        "role": "admin"
      },
      "description": "Команда DevOps, отвечающая за CI/CD и инфраструктуру.",
      "access_level": "private",
      "status": "pending",
      "processing_progress": 10,
      "is_ready": False,
      "created_at": "2025-04-18T12:00:00.000Z",
      "updated_at": "2025-05-05T10:00:00.000Z"
    }
  ],
  "has_more": True,
  "total": 15,
  "filters": {
    "search": "teams",
    "status": ["active", "in progress"]
  }
}
  return fakeDataTeams


@app.get(apiLink + "/teams/{team_id}")
def team(team_id: str):
  fakeDataTeam = {
  "id": 3,
  "title": "Проектный офис",
  "date": "2025-05-07T10:00:00.000Z",
  "tags": [
    {
      "id": 5,
      "label": "Управление проектами"
    },
    {
      "id": 6,
      "label": "PM"
    }
  ],
  "participants": [
    {
      "id": 105,
      "name": "Алексей Кузнецов",
      "role": "Менеджер"
    },
    {
      "id": 106,
      "name": "Татьяна Иванова",
      "role": "Ассистент"
    }
  ],
  "created_by": {
    "id": 203,
    "name": "Project Manager",
    "role": "user"
  },
  "description": "Команда по управлению внутренними и внешними проектами компании.",
  "access_level": "protected",
  "status": "active",
  "processing_progress": 100,
  "is_ready": True,
  "created_at": "2025-04-20T10:00:00.000Z",
  "updated_at": "2025-05-05T14:21:34.761Z"
}
  return fakeDataTeam

@app.get(apiLink + "/meetings/{meeting_id}/audio")
def audio(meeting_id):
  file_path = os.path.join("./audio", "1.mp3")
  return FileResponse(path=file_path, media_type="audio/mpeg", filename="1.mp3")


@app.get(apiLink + "/meetings/{id}")
def getDataMeetings(id: int):
  return {
    "title": f"Новый проект {id}",
"tags": [
  "стратегия",
  "продукт",
  "команда",
  "проекты",
  "эффективность",
  "бюджет",
  "клиенты",
  "маркетинг",
  "отчеты",
  "инновации"
], "description": "Еженедельный созвон команды для обсуждения текущих задач, прогресса по проектам, выявления блокеров и планов на ближайшую неделю.\n\
    Цель: синхронизация участников, повышение прозрачности процессов и оперативное решение возникающих вопросов. "
  }