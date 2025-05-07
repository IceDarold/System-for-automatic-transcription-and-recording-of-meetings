from fastapi import APIRouter, Depends, Query, HTTPException, status, Body, File, UploadFile
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_, and_, func
from typing import List, Optional
from datetime import datetime
import shutil # For disk space and file operations
import os
from pathlib import Path
import logging

from database import get_db
from models.meeting import Meeting, AccessLevel, MeetingStatus, Tag
from models.user import User, UserRole
from models.transcript import TranscriptBlock
from models.file import File as DBFile # Renamed to avoid conflict with UploadFile
from schemas.meeting import MeetingResponse, MeetingListResponse, MeetingDetailResponse, MeetingSearchParams, TranscriptBlockResponse, UserResponse, MeetingCreate, TagResponse
from core.auth import get_current_user
from core.audit import log_action
from core.config import settings # For file settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Helper function to check disk space
def has_sufficient_disk_space(file_size_bytes: int) -> bool:
    # Check space in the storage directory's partition
    total, used, free = shutil.disk_usage(Path(settings.STORAGE_DIR).resolve().parent)
    # Add a small buffer, e.g., 10% of file size or a fixed amount
    buffer_bytes = max(file_size_bytes * 0.1, 10 * 1024 * 1024) # 10MB buffer or 10% of file
    return free >= file_size_bytes + buffer_bytes

@router.get("/meetings", response_model=MeetingListResponse)
async def get_meetings(
    search_params: MeetingSearchParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a list of meetings with advanced search and filtering capabilities.
    
    Parameters:
    - search: Text search in title and description (supports Russian language)
    - start_date: Filter meetings after this date
    - end_date: Filter meetings before this date
    - participant_ids: Filter by meeting participants
    - tag_ids: Filter by meeting tags
    - team_ids: Filter by team (when implemented)
    - access_level: Filter by access level (public/restricted/private)
    - status: Filter by meeting status
    - created_by_id: Filter by meeting creator
    - sort: Sort order (created_at_desc/created_at_asc/date_desc/date_asc)
    - limit: Number of items per page (1-50)
    - offset: Pagination offset
    
    Returns:
    - items: List of meetings
    - has_more: Whether there are more items
    - total: Total number of items matching the filters
    - filters: Active filters applied to the search
    """
    # Base query with eager loading
    query = db.query(Meeting).options(
        selectinload(Meeting.created_by),
        selectinload(Meeting.tags),
        selectinload(Meeting.participants),
        selectinload(Meeting.access_users)
    )

    # Apply access control
    access_conditions = [
        Meeting.access_level == AccessLevel.public,
        and_(
            Meeting.access_level == AccessLevel.restricted,
            Meeting.access_users.contains(current_user)
        ),
        and_(
            Meeting.access_level == AccessLevel.private,
            or_(
                Meeting.created_by_id == current_user.id,
                current_user.role == UserRole.superadmin
            )
        )
    ]
    query = query.filter(or_(*access_conditions))

    # Apply search filters
    if search_params.search:
        search_term = search_params.search
        # Use full-text search with Russian language support
        query = query.filter(
            func.to_tsvector('russian', Meeting.title + ' ' + func.coalesce(Meeting.description, '')).op('@@')(
                func.to_tsquery('russian', func.plainto_tsquery('russian', search_term))
            )
        )

    # Apply date range filter
    if search_params.start_date:
        query = query.filter(Meeting.date >= search_params.start_date)
    if search_params.end_date:
        query = query.filter(Meeting.date <= search_params.end_date)

    # Apply participant filter
    if search_params.participant_ids:
        query = query.filter(Meeting.participants.any(User.id.in_(search_params.participant_ids)))

    # Apply tag filter
    if search_params.tag_ids:
        query = query.filter(Meeting.tags.any(Tag.id.in_(search_params.tag_ids)))

    # Apply team filter (if implemented)
    if search_params.team_ids:
        # TODO: Implement team filtering when team functionality is added
        pass

    # Apply access level filter
    if search_params.access_level:
        query = query.filter(Meeting.access_level == search_params.access_level)

    # Apply status filter
    if search_params.status:
        query = query.filter(Meeting.status == search_params.status)

    # Apply created by filter
    if search_params.created_by_id:
        query = query.filter(Meeting.created_by_id == search_params.created_by_id)

    # Apply sorting
    if search_params.sort == "created_at_desc":
        query = query.order_by(Meeting.created_at.desc())
    elif search_params.sort == "created_at_asc":
        query = query.order_by(Meeting.created_at.asc())
    elif search_params.sort == "date_desc":
        query = query.order_by(Meeting.date.desc())
    elif search_params.sort == "date_asc":
        query = query.order_by(Meeting.date.asc())

    # Get total count for pagination
    total_count = query.count()

    # Apply pagination
    meetings = query.offset(search_params.offset).limit(search_params.limit + 1).all()

    # Check if there are more items
    has_more = len(meetings) > search_params.limit
    if has_more:
        meetings = meetings[:-1]

    # Convert to response model
    items = [
        MeetingResponse(
            id=meeting.id,
            title=meeting.title,
            date=meeting.date,
            description=meeting.description,
            access_level=meeting.access_level,
            status=meeting.status,
            created_by_id=meeting.created_by_id,
            processing_progress=meeting.processing_progress,
            created_at=meeting.created_at,
            updated_at=meeting.updated_at,
            location=meeting.location,
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            duration=meeting.duration,
            is_online=meeting.is_online,
            is_published=meeting.is_published if hasattr(meeting, 'is_published') else False,
            tags=[TagResponse(id=tag.id, label=tag.label) for tag in meeting.tags],
            participants=[{"id": p.id, "name": f"{p.first_name} {p.last_name}"} for p in meeting.participants]
        )
        for meeting in meetings
    ]

    # Prepare active filters for response
    active_filters = {}
    if search_params.search:
        active_filters["search"] = search_params.search
    if search_params.start_date:
        active_filters["start_date"] = search_params.start_date
    if search_params.end_date:
        active_filters["end_date"] = search_params.end_date
    if search_params.participant_ids:
        active_filters["participant_ids"] = search_params.participant_ids
    if search_params.tag_ids:
        active_filters["tag_ids"] = search_params.tag_ids
    if search_params.team_ids:
        active_filters["team_ids"] = search_params.team_ids
    if search_params.access_level:
        active_filters["access_level"] = search_params.access_level
    if search_params.status:
        active_filters["status"] = search_params.status
    if search_params.created_by_id:
        active_filters["created_by_id"] = search_params.created_by_id

    return MeetingListResponse(
        items=items,
        has_more=has_more,
        total=total_count,
        filters=active_filters
    )

@router.get("/meetings/{meeting_id}", response_model=MeetingDetailResponse)
async def get_meeting_detail(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get meeting with all related data
    meeting = db.query(Meeting).options(
        selectinload(Meeting.created_by),
        selectinload(Meeting.tags),
        selectinload(Meeting.participants),
        selectinload(Meeting.access_users),
        selectinload(Meeting.transcript_blocks).selectinload(TranscriptBlock.speaker),
        selectinload(Meeting.audio_file),
        selectinload(Meeting.transcript_file),
        selectinload(Meeting.summary_file),
        selectinload(Meeting.protocol_file)
    ).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    # Check access rights
    has_access = (
        meeting.access_level == AccessLevel.public or
        (meeting.access_level == AccessLevel.restricted and current_user in meeting.access_users) or
        (meeting.access_level == AccessLevel.private and (
            meeting.created_by_id == current_user.id or
            current_user.role == UserRole.superadmin
        ))
    )

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this meeting"
        )

    # Log the view action
    await log_action(
        db=db,
        user_id=current_user.id,
        action="view_meeting",
        resource_id=meeting_id,
        resource_type="meeting"
    )

    # Prepare transcript blocks
    transcript_blocks = None
    if meeting.transcript_blocks:
        transcript_blocks = [
            TranscriptBlockResponse(
                speaker=UserResponse(
                    id=block.speaker.id,
                    name=f"{block.speaker.first_name} {block.speaker.last_name}"
                ) if block.speaker else None,
                start=block.start_time,
                end=block.end_time,
                text=block.text,
                confidence=block.confidence,
                language=block.language,
                metadata=block.transcript_metadata
            )
            for block in meeting.transcript_blocks
        ]

    # Get file URLs
    audio_url = meeting.audio_file.url if meeting.audio_file else None
    summary = meeting.summary_file.url if meeting.summary_file else None
    protocol = meeting.protocol_file.url if meeting.protocol_file else None

    return MeetingDetailResponse(
        id=meeting.id,
        title=meeting.title,
        date=meeting.date,
        description=meeting.description,
        access_level=meeting.access_level,
        status=meeting.status,
        created_by_id=meeting.created_by_id,
        processing_progress=meeting.processing_progress,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
        location=meeting.location,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        duration=meeting.duration,
        is_online=meeting.is_online,
        is_published=meeting.is_published if hasattr(meeting, 'is_published') else False,
        audio_url=audio_url,
        transcript=transcript_blocks,
        summary=summary,
        protocol=protocol,
        error_message=meeting.error_message,
        tags=[TagResponse(id=tag.id, label=tag.label) for tag in meeting.tags],
        participants=[{"id": p.id, "name": f"{p.first_name} {p.last_name}"} for p in meeting.participants],
        transcript_blocks=transcript_blocks if transcript_blocks else [],
        files=[FileResponse(**file.__dict__) for file in meeting.files] if hasattr(meeting, 'files') and meeting.files else []
    )

@router.put("/meetings/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int,
    update_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a meeting"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    # Check if user has permission to update
    if meeting.created_by_id != current_user.id and current_user.role != UserRole.superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this meeting"
        )

    # Update meeting fields
    for field, value in update_data.items():
        if hasattr(meeting, field):
            setattr(meeting, field, value)

    db.commit()
    db.refresh(meeting)

    # Log the update action
    await log_action(
        db=db,
        user_id=current_user.id,
        action="update_meeting",
        resource_id=meeting_id,
        resource_type="meeting"
    )

    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        date=meeting.date,
        description=meeting.description,
        access_level=meeting.access_level,
        status=meeting.status,
        created_by_id=meeting.created_by_id,
        processing_progress=meeting.processing_progress,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
        location=meeting.location,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        duration=meeting.duration,
        is_online=meeting.is_online,
        is_published=meeting.is_published if hasattr(meeting, 'is_published') else False,
        tags=[TagResponse(id=tag.id, label=tag.label) for tag in meeting.tags],
        participants=[{"id": p.id, "name": f"{p.first_name} {p.last_name}"} for p in meeting.participants]
    )

@router.delete("/meetings/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a meeting"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    # Check if user has permission to delete
    if meeting.created_by_id != current_user.id and current_user.role != UserRole.superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this meeting"
        )

    # Delete meeting
    db.delete(meeting)
    db.commit()

    # Log the delete action
    await log_action(
        db=db,
        user_id=current_user.id,
        action="delete_meeting",
        resource_id=meeting_id,
        resource_type="meeting"
    )

    return None

@router.post("/meetings", response_model=MeetingResponse)
async def create_meeting(
    meeting_data: MeetingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new meeting"""
    # Create meeting
    meeting = Meeting(
        title=meeting_data.title,
        date=meeting_data.date,
        start_time=meeting_data.start_time,
        end_time=meeting_data.end_time,
        duration=meeting_data.duration,
        location=meeting_data.location,
        is_online=meeting_data.is_online,
        description=meeting_data.description,
        access_level=meeting_data.access_level,
        status=MeetingStatus.pending,
        created_by_id=current_user.id
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    # Log the create action
    await log_action(
        db=db,
        user_id=current_user.id,
        action="create_meeting",
        resource_id=meeting.id,
        resource_type="meeting"
    )

    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        date=meeting.date,
        description=meeting.description,
        access_level=meeting.access_level,
        status=meeting.status,
        created_by_id=meeting.created_by_id,
        processing_progress=meeting.processing_progress,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
        location=meeting.location,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        duration=meeting.duration,
        is_online=meeting.is_online,
        is_published=meeting.is_published if hasattr(meeting, 'is_published') else False,
        tags=[TagResponse(id=tag.id, label=tag.label) for tag in meeting.tags],
        participants=[{"id": p.id, "name": f"{p.first_name} {p.last_name}"} for p in meeting.participants]
    )

@router.post("/meetings/{meeting_id}/audio", status_code=status.HTTP_201_CREATED)
async def upload_audio(
    meeting_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"User {current_user.id} attempting to upload audio for meeting {meeting_id}")
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        logger.warning(f"Meeting {meeting_id} not found for audio upload by user {current_user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    # Check if user has rights to modify the meeting (e.g., creator or admin)
    # This logic might need adjustment based on your exact access control rules
    if meeting.created_by_id != current_user.id and current_user.role != UserRole.admin and current_user.role != UserRole.superadmin:
        logger.warning(f"User {current_user.id} forbidden to upload audio for meeting {meeting_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to upload audio to this meeting")

    # Validate file type (MIME type)
    if file.content_type not in settings.ALLOWED_AUDIO_MIME_TYPES:
        logger.warning(f"Invalid audio file type '{file.content_type}' for meeting {meeting_id} by user {current_user.id}. Allowed: {settings.ALLOWED_AUDIO_MIME_TYPES}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file.content_type}. Allowed types: {', '.join(settings.ALLOWED_AUDIO_MIME_TYPES)}"
        )
    
    # Validate file size
    # We need to read the file to get its actual size, as file.size might not be reliable for streams.
    # To avoid reading the whole file into memory if it's too large, we can do it in chunks or seek.
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()  # Get file size in bytes
    file.file.seek(0) # Reset cursor to the beginning

    max_size_bytes = settings.MAX_AUDIO_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        logger.warning(f"Audio file for meeting {meeting_id} by user {current_user.id} too large ({file_size} bytes). Max: {max_size_bytes} bytes.")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_AUDIO_FILE_SIZE_MB}MB."
        )
    
    # Check for sufficient disk space
    if not has_sufficient_disk_space(file_size):
        logger.error(f"Insufficient disk space to store audio file for meeting {meeting_id} (size: {file_size} bytes).")
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            detail="Insufficient disk space to store the file. Please contact support."
        )

    storage_path = Path(settings.STORAGE_DIR)
    meeting_audio_dir = storage_path / "meetings" / str(meeting_id) / "audio"
    try:
        meeting_audio_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory {meeting_audio_dir} for meeting {meeting_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create storage directory")
    
    # Sanitize filename to prevent directory traversal and other attacks
    # Using file.filename directly can be risky
    original_filename = Path(file.filename)
    safe_filename = f"{original_filename.stem}_{int(datetime.utcnow().timestamp())}{original_filename.suffix}"
    file_path = meeting_audio_dir / safe_filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Audio file '{safe_filename}' (size: {file_size} bytes) saved to {file_path} for meeting {meeting_id}")
    except Exception as e:
        logger.error(f"Could not save audio file '{safe_filename}' for meeting {meeting_id}: {str(e)}", exc_info=True)
        # Attempt to clean up partially written file if error occurs
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception as remove_exc:
                logger.error(f"Failed to remove partially written file {file_path} after error: {remove_exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save file")
    finally:
        await file.close()

    # Create a record in the File table
    db_file = DBFile(
        filename=safe_filename,
        filepath=str(file_path.relative_to(storage_path)), # Store relative path
        filesize=file_size,
        mimetype=file.content_type,
        uploaded_by_id=current_user.id,
        meeting_id=meeting.id  # Link to the meeting
    )
    db.add(db_file)
    
    # Update meeting with the new audio file ID
    meeting.audio_file_id = db_file.id # This assumes audio_file_id exists on Meeting model
    meeting.status = MeetingStatus.pending # Reset status for reprocessing if needed
    meeting.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(db_file)
        db.refresh(meeting)
        logger.info(f"Audio file record created (ID: {db_file.id}) and meeting {meeting_id} updated for user {current_user.id}")
        await log_action(db, current_user.id, "upload_audio", resource_id=meeting.id, resource_type="meeting", details={"file_id": db_file.id, "filename": safe_filename})
    except Exception as e:
        db.rollback()
        logger.error(f"Database error after saving audio file for meeting {meeting_id}: {str(e)}", exc_info=True)
        # If DB fails, try to delete the orphaned file
        if file_path.exists():
            try:
                os.remove(file_path)
                logger.info(f"Orphaned audio file {file_path} deleted after DB error.")
            except Exception as remove_exc:
                logger.error(f"Failed to remove orphaned file {file_path} after DB error: {remove_exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving file metadata")

    return {"filename": safe_filename, "filepath": str(db_file.filepath), "file_id": db_file.id, "meeting_id": meeting.id, "message": "Audio uploaded successfully"}

@router.post("/meetings/{meeting_id}/chat")
async def chat_with_meeting(
    meeting_id: int,
    question: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question about a meeting"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    # Check access
    has_access = (
        meeting.access_level == AccessLevel.public or
        (meeting.access_level == AccessLevel.restricted and current_user in meeting.access_users) or
        (meeting.access_level == AccessLevel.private and (
            meeting.created_by_id == current_user.id or
            current_user.role == UserRole.superadmin
        ))
    )
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this meeting"
        )
    
    # Validate question
    if not question.get("question") or len(question.get("question").strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )
    
    # For now, just return a placeholder response
    # In a real implementation, this would call an LLM API
    return {
        "answer": "This is a placeholder answer. In a real implementation, this would provide an answer based on the meeting content."
    } 