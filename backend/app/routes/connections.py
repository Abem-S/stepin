"""
Connection Request API routes - Student to Professional connections
"""

import logging
from typing import Optional
from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/connections", tags=["connections"])


class RequestConnectionRequest(BaseModel):
    student_id: str
    student_name: str
    professional_id: str
    message: Optional[str] = None
    shadow_day_data: Optional[dict] = None  # What they learned in Shadow Day


class RequestConnectionResponse(BaseModel):
    request_id: str
    status: str


@router.post("/request", response_model=RequestConnectionResponse)
async def request_connection(request: RequestConnectionRequest):
    """
    Student requests a connection with a professional
    
    Includes Shadow Day experience data to help professional decide
    """
    request_id = f"conn-{uuid4().hex[:8]}"
    
    # In production, save to database
    logger.info(f"Connection request: {request_id} from {request.student_id} to {request.professional_id}")
    
    return RequestConnectionResponse(
        request_id=request_id,
        status="pending",
    )


@router.get("/student/{student_id}")
async def get_student_connections(student_id: str):
    """Get all connection requests from a student"""
    # In production, fetch from database
    return {
        "student_id": student_id,
        "connections": [
            {
                "id": "conn-1",
                "professional_name": "Dr. Sarah Chen",
                "status": "pending",
                "requested_at": "2024-01-15T10:00:00Z",
            }
        ],
    }


@router.get("/professional/{professional_id}")
async def get_professional_connections(professional_id: str):
    """Get all connection requests for a professional"""
    # In production, fetch from database
    return {
        "professional_id": professional_id,
        "requests": [
            {
                "id": "conn-1",
                "student_id": "student-1",
                "student_name": "Alex M.",
                "message": "I'd love to chat about your path!",
                "shadow_day": {
                    "career": "Medicine",
                    "energized_by": ["Direct patient care", "Fast-paced"],
                    "drained_by": ["Bureaucracy"],
                },
                "status": "pending",
                "requested_at": "2024-01-15T10:00:00Z",
            }
        ],
    }