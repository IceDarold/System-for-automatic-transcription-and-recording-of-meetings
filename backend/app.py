from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from schemas import LoginFormModel, RegistrationFormModel
from sqlalchemy.orm import Session
from models import User, Base
from database import engine, SessionLocal
from schemas import UserCreate
from database import database


app = FastAPI()

# Настройка CORS
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Можно заменить на конкретные домены, например ["http://localhost:3000"]
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = FastAPI(middleware=middleware)


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.post("/loadvideo")
async def load_video(video: UploadFile = File(...)):
    # Проверяем, есть ли файл в запросе
    if not video:
        raise HTTPException(status_code=400, detail="No file part in the request")

    # Если пользователь не выбрал файл
    if video.filename == "":
        raise HTTPException(status_code=400, detail="No selected file")

    # Здесь можно добавить сохранение файла или его обработку
    print(f"Файл {video.filename} загружен")
    
    return {
        "filename": video.filename,
        "content_type": video.content_type,
        "status": "Файл успешно получен"
    }

@app.get("/loadvideo")
async def load_video_get():
    return {"message": "GET-запрос на /loadvideo работает"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/sendRegistration")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.login == user.login).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    hashed_password = user.password

    new_user = User(
        name=user.name,
        department=user.department,
        login=user.login,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Регистрация успешна", "user": new_user.login}

@app.post("/sendLogin")
async def login_user(form_data: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.login == form_data.login).first()
    if not db_user or form_data.password != db_user.password_hash:
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")

    return {"message": "Вход выполнен успешно"}
    