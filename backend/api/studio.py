from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.meeting import Meeting, MeetingStatus, AccessLevel
from models.user import User, UserRole
from models.file import File as FileModel, FileType
from schemas.meeting import MeetingResponse, MeetingDetailResponse, TranscriptBlockResponse
from core.auth import get_current_user
from core.audit import log_action
from core.storage import save_file
from core.tasks import process_meeting

router = APIRouter()

def check_editor_access(user: User):
    """Check if user has editor access"""
    if user.role not in [UserRole.editor, UserRole.superadmin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only editors and superadmins can access the studio"
        )

def check_meeting_owner(meeting: Meeting, user: User):
    """Check if user is the meeting owner or superadmin"""
    if meeting.created_by_id != user.id and user.role != UserRole.superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only meeting owner or superadmin can perform this action"
        )

@router.post("/meetings", response_model=MeetingResponse)
async def create_meeting_draft(
    title: str = Form(...),
    date: datetime = Form(...),
    short_description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new meeting draft"""
    check_editor_access(current_user)
    
    # Create meeting
    meeting = Meeting(
        title=title,
        date=date,
        short_description=short_description,
        status=MeetingStatus.pending,
        created_by_id=current_user.id,
        access_level=AccessLevel.private
    )
    db.add(meeting)
    db.flush()  # Get meeting ID
    
    # Add owner access
    meeting.access_users.append(current_user)
    
    db.commit()
    db.refresh(meeting)
    
    # Log action
    await log_action(
        db=db,
        user_id=current_user.id,
        action="create_meeting",
        resource_id=meeting.id,
        resource_type="meeting"
    )
    
    return meeting

@router.post("/meetings/{meeting_id}/files")
async def upload_meeting_file(
    meeting_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file for a meeting"""
    check_editor_access(current_user)
    
    # Get meeting
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    check_meeting_owner(meeting, current_user)
    
    # Validate file type
    if not file.content_type.startswith(('audio/', 'video/')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only audio and video files are allowed"
        )
    
    # Save file
    file_type = FileType.audio if file.content_type.startswith('audio/') else FileType.video
    file_model = await save_file(
        db=db,
        file=file,
        meeting_id=meeting_id,
        file_type=file_type
    )
    
    # Update meeting if it's an audio file
    if file_type == FileType.audio:
        meeting.audio_file_id = file_model.id
        db.commit()
    
    return {"id": file_model.id, "url": file_model.url}

@router.post("/meetings/{meeting_id}/start")
async def start_meeting_processing(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start AI processing for a meeting"""
    check_editor_access(current_user)
    
    # Get meeting
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    check_meeting_owner(meeting, current_user)
    
    # Validate meeting state
    if meeting.status != MeetingStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meeting must be in pending state"
        )
    
    # Check for audio file
    if not meeting.audio_file_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is required for processing"
        )
    
    # Update status
    meeting.status = MeetingStatus.processing
    meeting.processing_progress = 0
    db.commit()
    
    # Start processing tasks
    await process_meeting(meeting_id)
    
    return {"status": "processing_started"}

@router.get("/meetings/{meeting_id}/editor", response_model=MeetingDetailResponse)
async def get_editor_data(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get meeting data for editor"""
    check_editor_access(current_user)
    
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
    
    check_meeting_owner(meeting, current_user)
    
    return meeting

@router.put("/meetings/{meeting_id}/editor")
async def update_editor_data(
    meeting_id: int,
    transcript: Optional[List[TranscriptBlockResponse]] = None,
    summary: Optional[str] = None,
    protocol: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update meeting content in editor"""
    check_editor_access(current_user)
    
    # Get meeting
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    check_meeting_owner(meeting, current_user)
    
    # Update transcript blocks if provided
    if transcript is not None:
        # Delete existing blocks
        db.query(TranscriptBlock).filter(TranscriptBlock.meeting_id == meeting_id).delete()
        
        # Create new blocks
        for block in transcript:
            db_block = TranscriptBlock(
                meeting_id=meeting_id,
                speaker_id=block.speaker.id if block.speaker else None,
                start_time=block.start,
                end_time=block.end,
                text=block.text,
                confidence=block.confidence,
                language=block.language,
                transcript_metadata=block.metadata
            )
            db.add(db_block)
    
    # Update summary if provided
    if summary is not None:
        meeting.summary = summary
    
    # Update protocol if provided
    if protocol is not None:
        meeting.protocol = protocol
    
    db.commit()
    
    return {"status": "updated"}

@router.post("/meetings/{meeting_id}/publish")
async def publish_meeting(
    meeting_id: int,
    access_level: AccessLevel = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish a meeting"""
    check_editor_access(current_user)
    
    # Get meeting
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    check_meeting_owner(meeting, current_user)
    
    # Validate meeting state
    if meeting.status not in [MeetingStatus.processing, MeetingStatus.done]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meeting must be in processing or done state"
        )
    
    # Check required content
    if not meeting.transcript_blocks or not meeting.summary or not meeting.protocol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meeting must have transcript, summary, and protocol"
        )
    
    # Update meeting
    meeting.status = MeetingStatus.done
    meeting.access_level = access_level
    db.commit()
    
    return {"status": "published"} 