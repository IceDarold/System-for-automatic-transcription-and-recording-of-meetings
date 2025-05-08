import os
import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session
from models.file import File as FileModel, FileType
from core.config import settings

# Configure storage settings
# STORAGE_DIR = os.getenv("STORAGE_DIR", "storage")
# ALLOWED_MIME_TYPES = {
#     "audio/": ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4"],
#     "video/": ["video/mp4", "video/quicktime", "video/x-msvideo"]
# }

async def save_file(
    db: Session,
    file: UploadFile,
    meeting_id: int,
    file_type: FileType
) -> FileModel:
    """Save an uploaded file and create a database record"""
    
    # Validate MIME type
    if not any(file.content_type.startswith(prefix) for prefix in settings.ALLOWED_UPLOAD_PREFIXES):
        raise ValueError(f"Unsupported file type: {file.content_type}")
    
    # Generate unique filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    
    # Create storage directory if it doesn't exist
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    
    # Save file
    file_path = os.path.join(settings.STORAGE_DIR, filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create database record
    file_model = FileModel(
        filename=file.filename,
        file_type=file_type,
        mime_type=file.content_type,
        size=len(content),
        url=f"/files/{filename}",  # URL for accessing the file
        storage_path=file_path,
        meeting_id=meeting_id
    )
    
    db.add(file_model)
    db.commit()
    db.refresh(file_model)
    
    return file_model

async def save_text_content_as_file(
    db: Session,
    content: str,
    original_filename_base: str, # e.g., "summary" or "protocol"
    meeting_id: int,
    file_type: FileType, # e.g., FileType.summary or FileType.protocol
    mime_type: str = "text/plain"
) -> FileModel:
    """Save text content to a file and create a database record."""
    # Generate unique filename
    filename = f"{uuid.uuid4()}_{original_filename_base}.txt"

    # Ensure storage directory exists
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)

    file_path = os.path.join(settings.STORAGE_DIR, filename)
    content_bytes = content.encode('utf-8')

    with open(file_path, "wb") as f: # write in binary mode as we have bytes
        f.write(content_bytes)

    file_size = len(content_bytes)

    # Create database record
    file_model = FileModel(
        filename=original_filename_base + ".txt", # User-friendly original name
        file_type=file_type,
        mime_type=mime_type,
        size=file_size,
        url=f"/files/{filename}",  # URL for accessing the file
        storage_path=file_path,
        meeting_id=meeting_id
    )

    db.add(file_model)
    db.commit() # Committing here, ensure this is fine with the transactionality of the calling task
    db.refresh(file_model)

    return file_model 