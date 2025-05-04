from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.meeting import Meeting, AccessLevel
from models.user import User, UserRole
from core.auth import get_current_user
from schemas.meeting import MeetingResponse, MeetingListResponse

router = APIRouter()

@router.get("/meetings", response_model=MeetingListResponse)
async def get_meetings(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    sort: str = Query("created_at_desc", regex="^(created_at_desc|created_at_asc|date_desc|date_asc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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

    # Apply sorting
    if sort == "created_at_desc":
        query = query.order_by(Meeting.created_at.desc())
    elif sort == "created_at_asc":
        query = query.order_by(Meeting.created_at.asc())
    elif sort == "date_desc":
        query = query.order_by(Meeting.date.desc())
    elif sort == "date_asc":
        query = query.order_by(Meeting.date.asc())

    # Get total count for has_more
    total_count = query.count()

    # Apply pagination
    meetings = query.offset(offset).limit(limit + 1).all()

    # Check if there are more items
    has_more = len(meetings) > limit
    if has_more:
        meetings = meetings[:-1]

    # Convert to response model
    items = [
        MeetingResponse(
            id=meeting.id,
            title=meeting.title,
            date=meeting.date.isoformat(),
            tags=[{"id": tag.id, "label": tag.label} for tag in meeting.tags],
            participants=[{"id": p.id, "name": f"{p.first_name} {p.last_name}"} for p in meeting.participants],
            created_by={"id": meeting.created_by.id, "name": f"{meeting.created_by.first_name} {meeting.created_by.last_name}"},
            short_description=meeting.short_description,
            thumbnail_url=meeting.thumbnail_url
        )
        for meeting in meetings
    ]

    return MeetingListResponse(items=items, has_more=has_more) 