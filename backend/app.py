from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import settings
from api.v1.endpoints import auth
from api.meetings import router as meetings_router
from api.studio import router as studio_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount storage directory for file access
app.mount("/files", StaticFiles(directory="storage"), name="files")

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(meetings_router, prefix=settings.API_V1_STR, tags=["meetings"])
app.include_router(studio_router, prefix=settings.API_V1_STR, tags=["studio"])


@app.get("/")
def root():
    return {"message": "Welcome to Meeting Transcription System API"}
