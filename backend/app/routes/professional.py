"""
Professional onboarding and World Builder API routes
"""

import logging
from typing import Optional, List
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.world_builder_service import build_career_world

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/professional", tags=["professional"])


class InterviewCompleteRequest(BaseModel):
    professional_id: str
    professional_name: str
    career_title: str
    years_experience: int
    category: str
    interview_responses: dict  # question_key -> response text


class InterviewCompleteResponse(BaseModel):
    career_world_id: str
    status: str
    title: str
    moments_count: int


class UpdateProfessionalRequest(BaseModel):
    name: Optional[str] = None
    career_title: Optional[str] = None
    bio: Optional[str] = None


class VoiceClipUploadRequest(BaseModel):
    professional_id: str
    question_key: str
    # In production, this would include a file upload URL


@router.post("/interview/complete", response_model=InterviewCompleteResponse)
async def complete_interview(request: InterviewCompleteRequest):
    """
    Complete the onboarding interview and generate Career World
    
    This is called after the professional finishes all interview questions.
    It uses the World Builder Agent to transform responses into a Career World JSON.
    """
    try:
        logger.info(f"Building Career World for professional {request.professional_id}")
        
        # Build the career world from interview responses
        career_world = await build_career_world(
            professional_name=request.professional_name,
            career_title=request.career_title,
            interview_responses=request.interview_responses,
            years_experience=request.years_experience,
            category=request.category,
        )
        
        # Generate a unique ID for the career world
        career_world_id = f"{request.category.lower()}-{uuid4().hex[:8]}"
        career_world["id"] = career_world_id
        
        # In production, save to database
        # For now, return the generated world
        
        return InterviewCompleteResponse(
            career_world_id=career_world_id,
            status="complete",
            title=career_world.get("title", "New Career World"),
            moments_count=len(career_world.get("moments", [])),
        )
        
    except Exception as e:
        logger.error(f"Error completing interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{professional_id}/career-world")
async def get_professional_career_world(professional_id: str):
    """Get the Career World created by a professional"""
    # In production, fetch from database
    # For now, return placeholder
    return {
        "id": f"career-world-{professional_id}",
        "status": "not_found",
        "message": "No career world found. Complete onboarding first.",
    }


@router.post("/{professional_id}/voice-clips")
async def upload_voice_clip(
    professional_id: str,
    request: VoiceClipUploadRequest,
):
    """
    Upload a voice clip for a specific interview question
    
    In production, this would handle actual file upload to storage
    """
    # In production, save to storage and database
    return {
        "status": "uploaded",
        "professional_id": professional_id,
        "question_key": request.question_key,
    }


@router.get("/{professional_id}/dashboard")
async def get_professional_dashboard(professional_id: str):
    """Get professional dashboard data"""
    # In production, fetch from database
    return {
        "id": professional_id,
        "name": "Dr. Sarah Chen",
        "career_title": "Chief Medical Officer",
        "years_experience": 12,
        "students_count": 247,
        "connection_requests": 5,
        "voice_clips_recorded": 5,
        "career_worlds": [
            {"id": "medicine-1", "title": "Surgical Resident's Tuesday", "students": 247}
        ],
    }


@router.get("/{professional_id}/students")
async def get_professional_students(professional_id: str):
    """Get list of students who lived professional's career"""
    # In production, fetch from database
    return {
        "students": [
            {
                "id": "1",
                "name": "Alex M.",
                "date": "2024-01-15",
                "energized_by": ["Direct patient care", "Fast-paced environment"],
                "drained_by": ["Bureaucracy", "Admin work"],
            },
            {
                "id": "2", 
                "name": "Jordan K.",
                "date": "2024-01-14",
                "energized_by": ["Making an impact", "Team collaboration"],
                "drained_by": ["Lack of resources"],
            },
        ]
    }


@router.get("/{professional_id}/connections")
async def get_connection_requests(professional_id: str):
    """Get pending connection requests from students"""
    # In production, fetch from database
    return {
        "requests": [
            {
                "id": "1",
                "student_id": "student-1",
                "student_name": "Alex M.",
                "message": "I'd love to chat about your path to becoming a CMO!",
                "shadow_day_date": "2024-01-15",
                "status": "pending",
            },
            {
                "id": "2",
                "student_id": "student-2",
                "student_name": "Jordan K.",
                "message": "Would you have 15 minutes for a quick call?",
                "shadow_day_date": "2024-01-14",
                "status": "pending",
            },
        ]
    }


@router.post("/{professional_id}/connections/{request_id}/accept")
async def accept_connection(professional_id: str, request_id: str):
    """Accept a student connection request"""
    # In production, update database
    return {"status": "accepted", "request_id": request_id}


@router.post("/{professional_id}/connections/{request_id}/decline")
async def decline_connection(professional_id: str, request_id: str):
    """Decline a student connection request"""
    # In production, update database
    return {"status": "declined", "request_id": request_id}