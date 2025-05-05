import os
import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session
from models.file import File as FileModel, FileType

# Configure storage settings
STORAGE_DIR = os.getenv("STORAGE_DIR", "storage")
ALLOWED_MIME_TYPES = {
    "audio/": ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4"],
    "video/": ["video/mp4", "video/quicktime", "video/x-msvideo"]
}

async def save_file(
    db: Session,
    file: UploadFile,
    meeting_id: int,
    file_type: FileType
) -> FileModel:
    """Save an uploaded file and create a database record"""
    
    # Validate MIME type
    if not any(file.content_type.startswith(prefix) for prefix in ALLOWED_MIME_TYPES.keys()):
        raise ValueError(f"Unsupported file type: {file.content_type}")
    
    # Generate unique filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    
    # Create storage directory if it doesn't exist
    os.makedirs(STORAGE_DIR, exist_ok=True)
    
    # Save file
    file_path = os.path.join(STORAGE_DIR, filename)
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