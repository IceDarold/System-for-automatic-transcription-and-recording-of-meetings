from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

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