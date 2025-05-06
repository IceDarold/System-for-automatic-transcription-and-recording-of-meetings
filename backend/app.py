from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import settings
from api.v1 import api_router
from api.meetings import router as meetings_router
from api.studio import router as studio_router
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost", "http://127.0.0.1:3000", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create storage directory if it doesn't exist
if not os.path.exists("storage"):
    os.makedirs("storage")

# Mount storage directory for file access
app.mount("/files", StaticFiles(directory="storage"), name="files")

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(meetings_router, prefix=settings.API_V1_STR, tags=["meetings"])
app.include_router(studio_router, prefix=f"{settings.API_V1_STR}/studio", tags=["studio"])


@app.get("/")
def root():
    return {"message": "Welcome to Meeting Transcription System API"}
