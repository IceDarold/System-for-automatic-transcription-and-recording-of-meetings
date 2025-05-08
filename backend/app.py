from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status, Request
from pydantic import ValidationError
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from core.config import settings
from core.logging_config import setup_logging
from api.v1 import api_router
from api.meetings import router as meetings_router
from api.studio import router as studio_router
from database import check_db_connection, init_db

# Setup logging AS THE FIRST THING
setup_logging()

# Get a logger instance (after setup_logging is called)
logger = logging.getLogger(settings.PROJECT_NAME)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    # Startup logic
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database on startup: {str(e)}", exc_info=True)
        raise Exception(f"Database initialization failed: {str(e)}")
    
    try:
        storage_dir = Path(settings.STORAGE_DIR)
        if not storage_dir.exists():
            storage_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created storage directory: {settings.STORAGE_DIR}")
    except Exception as e:
        logger.error(f"Failed to create storage directory: {str(e)}", exc_info=True)
        raise
    yield
    logger.info("Application shutdown...")
    # Shutdown logic (if any) can go here

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = exc.body
    if hasattr(body, "multi_items"):
        body = dict(body.multi_items())
    logger.warning("Request validation error", extra={"detail": exc.errors(), "body": body})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": body
        },
    )

@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    logger.warning(f"Value error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Value Error", "detail": str(exc)},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred."},
    )

# Mount storage directory for file access
try:
    app.mount("/files", StaticFiles(directory=settings.STORAGE_DIR), name="files")
except Exception as e:
    logger.error(f"Failed to mount storage directory: {str(e)}", exc_info=True)
    raise

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(meetings_router, prefix=settings.API_V1_STR, tags=["meetings"])
app.include_router(studio_router, prefix=f"{settings.API_V1_STR}/studio", tags=["studio"])

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to Meeting Transcription System API"}
