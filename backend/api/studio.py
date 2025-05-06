from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Body
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.meeting import Meeting, MeetingStatus, AccessLevel, Tag
from models.user import User, UserRole
from models.file import File as FileModel, FileType
from schemas.meeting import MeetingResponse, MeetingDetailResponse, TranscriptBlockResponse, MeetingCreate, TagResponse, UserResponse
from core.auth import get_current_user
from core.audit import log_action
from core.storage import save_file
from core.tasks import process_meeting
from models.transcript import TranscriptBlock
from core.media import convert_to_wav

router = APIRouter()

def check_ffmpeg():
    """Check if ffmpeg is available in the system"""
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (FileNotFoundError, subprocess.SubprocessError):
        return False

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

@router.post("/meetings", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting_draft(
    meeting_data: MeetingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_editor_access(current_user)
    meeting = Meeting(
        title=meeting_data.title,
        date=meeting_data.date,
        start_time=meeting_data.start_time,
        end_time=meeting_data.end_time,
        duration=meeting_data.duration,
        location=meeting_data.location,
        is_online=meeting_data.is_online,
        description=meeting_data.description,
        status=MeetingStatus.pending,
        created_by_id=current_user.id,
        access_level=meeting_data.access_level
    )
    db.add(meeting)
    db.flush()
    meeting.access_users.append(current_user)
    db.commit()
    db.refresh(meeting)
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
        created_by_id=current_user.id,
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

@router.post("/meetings/{meeting_id}/upload-file", status_code=status.HTTP_201_CREATED)
async def upload_meeting_file(
    meeting_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload an audio or video file for a meeting. All files are converted to WAV if possible."""
    check_editor_access(current_user)
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    check_meeting_owner(meeting, current_user)
    if not (file.content_type.startswith('audio/') or file.content_type.startswith('video/')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only audio and video files are allowed"
        )
    
    # Save the file using FileType.audio for both audio and video files
    # (we'll convert video to audio anyway)
    file_model = await save_file(
        db=db,
        file=file,
        meeting_id=meeting_id,
        file_type=FileType.audio
    )
    
    # Set default values
    wav_url = file_model.url
    converted = False
    
    # Only attempt conversion if file is not already WAV
    if not file.content_type.endswith('wav'):
        import os
        
        # Use storage_path for file system operations
        input_path = file_model.storage_path
        file_dir = os.path.dirname(input_path)
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(file_dir, f"{file_name}.wav")
        
        # Try to convert to WAV
        try:
            # Check if ffmpeg is available
            if not check_ffmpeg():
                print("Warning: ffmpeg is not installed or not found in PATH.")
                print("Please install ffmpeg to enable audio/video conversion.")
                print("Visit https://ffmpeg.org/download.html for installation instructions.")
            else:
                # Attempt conversion
                conversion_success = convert_to_wav(input_path, output_path)
                if conversion_success and os.path.exists(output_path):
                    # Update file model with new WAV file
                    wav_file = FileModel(
                        filename=f"{os.path.splitext(file_model.filename)[0]}.wav",
                        file_type=FileType.audio,
                        mime_type="audio/wav",
                        size=os.path.getsize(output_path),
                        url=f"/files/{os.path.basename(output_path)}",
                        storage_path=output_path,
                        meeting_id=meeting_id
                    )
                    db.add(wav_file)
                    db.commit()
                    db.refresh(wav_file)
                    
                    # Set the WAV file as the meeting's audio file
                    meeting.audio_file_id = wav_file.id
                    db.commit()
                    
                    # Update return values
                    wav_url = wav_file.url
                    converted = True
                    # Return both original and converted file info
                    return {
                        "id": wav_file.id,
                        "url": wav_url,
                        "converted_to_wav": converted,
                        "original_file_id": file_model.id
                    }
        except Exception as e:
            print(f"Error during conversion: {str(e)}")
    
    # If we get here, either the file was already WAV or conversion failed
    # Set the original file as the meeting's audio file
        meeting.audio_file_id = file_model.id
        db.commit()
    
    return {
        "id": file_model.id, 
        "url": wav_url, 
        "converted_to_wav": converted
    }

@router.post("/meetings/{meeting_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def process_meeting_endpoint(
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
    update_data: dict = Body(...),
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
    if "transcript" in update_data:
        # Delete existing blocks
        db.query(TranscriptBlock).filter(TranscriptBlock.meeting_id == meeting_id).delete()
        
        # Handle both string and list formats
        transcript = update_data["transcript"]
        if isinstance(transcript, list):
            # Create new blocks from list of transcript blocks
            for block in transcript:
                db_block = TranscriptBlock(
                    meeting_id=meeting_id,
                    speaker_id=block.get("speaker", {}).get("id") if block.get("speaker") else None,
                    start_time=block.get("start"),
                    end_time=block.get("end"),
                    text=block.get("text"),
                    confidence=block.get("confidence", 1.0),
                    language=block.get("language", "en"),
                    transcript_metadata=block.get("metadata")
                )
                db.add(db_block)
        else:
            # Handle simple string transcript
            meeting.transcript = transcript
    
    # Update summary if provided
    if "summary" in update_data:
        meeting.summary = update_data["summary"]
    
    # Update protocol if provided
    if "protocol" in update_data:
        meeting.protocol = update_data["protocol"]
    
    # Update title if provided
    if "title" in update_data:
        meeting.title = update_data["title"]
    
    # Update tags if provided
    if "tags" in update_data:
        # Remove existing tags
        meeting.tags = []
        
        # Add new tags
        for tag_data in update_data["tags"]:
            # Check if tag exists
            tag = db.query(Tag).filter(Tag.label == tag_data["name"]).first()
            if not tag:
                # Create new tag
                tag = Tag(label=tag_data["name"])
                db.add(tag)
                db.flush()
            
            meeting.tags.append(tag)
    
    # Update participants if provided
    if "participants" in update_data:
        # Remove existing participants
        meeting.participants = []
        
        # Add new participants
        for participant_data in update_data["participants"]:
            # Check if participant exists by name
            first_name = participant_data["first_name"]
            last_name = participant_data["last_name"]
            
            participant = db.query(User).filter(
                User.first_name == first_name,
                User.last_name == last_name
            ).first()
            
            if not participant:
                # Create new participant
                participant = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=participant_data.get("email", f"{first_name}.{last_name}@example.com"),
                    password_hash="temporary_hash"  # Need to set required field
                )
                db.add(participant)
                db.flush()
            
            meeting.participants.append(participant)
    
    # Update meeting date if provided
    if "date" in update_data:
        meeting.date = update_data["date"]
    
    # Update meeting duration if provided
    if "duration" in update_data:
        meeting.duration = update_data["duration"]
    
    db.commit()
    
    return {
        "transcript": update_data.get("transcript", meeting.transcript),
        "summary": update_data.get("summary", meeting.summary),
        "protocol": update_data.get("protocol", meeting.protocol),
        "status": "updated"
    }

@router.post("/meetings/{meeting_id}/publish")
async def publish_meeting(
    meeting_id: int,
    access_level: AccessLevel = Form(default=AccessLevel.public),
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
    
    # Update meeting
    meeting.status = MeetingStatus.done
    meeting.access_level = access_level
    meeting.is_published = True
    db.commit()
    
    return {
        "status": "published",
        "is_published": True,
        "is_ready": True
    } 