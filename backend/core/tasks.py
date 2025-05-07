from sqlalchemy.orm import Session
from models.meeting import Meeting, MeetingStatus
from models.file import FileType, File as FileModel
from models.transcript import TranscriptBlock
from core.storage import save_text_content_as_file
from core.model_api import model_api, ModelAPIError
from database import SessionLocal
import os
import json
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

async def process_meeting(meeting_id: int):
    """
    Process a meeting's audio file using model-api service to generate
    transcript, summary, and protocol.
    """
    # Get meeting from database
    db: Session = SessionLocal()
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting or not meeting.audio_file:
        if meeting:
            db.close()
        return
    
    try:
        # Step 1: Transcribe audio
        meeting.processing_progress = 10
        db.commit()
        
        transcript_data = await model_api.transcribe_audio(
            audio_url=meeting.audio_file.url,
            language="ru"
        )
        
        # Create transcript blocks
        blocks = []
        for item in transcript_data:
            block = TranscriptBlock(
                meeting_id=meeting_id,
                start_time=item["start_time"],
                end_time=item["end_time"],
                text=item["text"],
                confidence=item["confidence"],
                language=item["language"],
                transcript_metadata=item.get("metadata")
            )
            blocks.append(block)
        
        db.add_all(blocks)
        meeting.processing_progress = 40
        db.commit()
        
        # Step 2: Detect speakers
        speaker_data = await model_api.detect_speakers(
            transcript=transcript_data,
            audio_url=meeting.audio_file.url
        )
        
        # Update speaker information in transcript blocks
        for block, speaker in zip(blocks, speaker_data):
            if speaker.get("speaker_id"):
                block.speaker_id = speaker["speaker_id"]
        
        meeting.processing_progress = 60
        db.commit()
        
        # Step 3: Generate summary
        summary_text = await model_api.generate_summary(
            transcript=transcript_data,
            language="ru"
        )
        summary_file_model = await save_text_content_as_file(
            db=db, 
            content=summary_text, 
            original_filename_base=f"meeting_{meeting_id}_summary",
            meeting_id=meeting_id, 
            file_type=FileType.summary
        )
        meeting.summary_file_id = summary_file_model.id
        meeting.processing_progress = 80
        db.commit()
        
        # Step 4: Generate protocol
        protocol_text = await model_api.generate_protocol(
            transcript=transcript_data,
            summary=summary_text,
            language="ru"
        )
        protocol_file_model = await save_text_content_as_file(
            db=db, 
            content=protocol_text, 
            original_filename_base=f"meeting_{meeting_id}_protocol",
            meeting_id=meeting_id, 
            file_type=FileType.protocol
        )
        meeting.protocol_file_id = protocol_file_model.id
        
        # Update final status
        meeting.status = MeetingStatus.done
        meeting.processing_progress = 100
        db.commit()
        
    except ModelAPIError as e:
        logger.error(f"Model API error for meeting {meeting_id}: {str(e)}")
        meeting.status = MeetingStatus.failed
        meeting.error_message = f"AI processing failed: {str(e)}"
        db.commit()
        
    except Exception as e:
        logger.error(f"Unexpected error processing meeting {meeting_id}: {str(e)}")
        meeting.status = MeetingStatus.failed
        meeting.error_message = f"Processing failed: {str(e)}"
        db.commit()
        
    finally:
        db.close()

async def update_processing_status(meeting_id: int, status: str, progress: int):
    """Update meeting processing status"""
    db: Session = SessionLocal()
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.processing_progress = progress
            if status == "failed":
                meeting.status = MeetingStatus.failed
            elif progress == 100:
                meeting.status = MeetingStatus.done
            db.commit()
    finally:
        db.close() 