"""Professionals API routes"""
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from pydantic import EmailStr

from app.models.professional import (
    ProfessionalCreate,
    ProfessionalResponse,
    ProfessionalInterviewComplete,
    VoiceClipCreate,
    VoiceClipResponse,
    DashboardStats,
    ConnectionRequestUpdate,
    ConnectionRequestResponse,
)

router = APIRouter(prefix="/api/professionals", tags=["professionals"])

# Mock storage for professionals
_mock_professionals: dict = {}

# Pre-populate with sample professionals for testing
_sample_professionals = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "sarah.chen@hospital.org",
        "name": "Dr. Sarah Chen",
        "career_category": "Medicine",
        "years_experience": 8,
        "profession": "Surgical Resident",
        "linkedin_url": "https://linkedin.com/in/sarahchen",
        "twitter_url": None,
        "website_url": None,
        "connection_preference": "email",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "email": "marcus.tech@startup.io",
        "name": "Marcus Johnson",
        "career_category": "Technology",
        "years_experience": 5,
        "profession": "Senior Software Engineer",
        "linkedin_url": "https://linkedin.com/in/marcusjohnson",
        "twitter_url": None,
        "website_url": None,
        "connection_preference": "linkedin",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "email": "elena.law@firm.com",
        "name": "Elena Rodriguez",
        "career_category": "Law",
        "years_experience": 12,
        "profession": "Corporate Law Partner",
        "linkedin_url": "https://linkedin.com/in/elenarodriguez",
        "twitter_url": None,
        "website_url": None,
        "connection_preference": "email",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    },
]

# Initialize mock storage with sample data
for p in _sample_professionals:
    _mock_professionals[p["id"]] = p


@router.post("", response_model=ProfessionalResponse, status_code=201)
async def create_professional(data: ProfessionalCreate):
    """Start professional onboarding"""
    now = datetime.utcnow()
    professional = ProfessionalResponse(
        id=uuid4(),
        email=data.email,
        name=data.name,
        career_category=None,
        years_experience=None,
        linkedin_url=None,
        twitter_url=None,
        website_url=None,
        connection_preference="email",
        created_at=now,
        updated_at=now,
    )
    _mock_professionals[str(professional.id)] = professional.model_dump()
    return professional


@router.get("/{professional_id}", response_model=ProfessionalResponse)
async def get_professional(professional_id: UUID):
    """Get professional profile"""
    professional = _mock_professionals.get(str(professional_id))
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")
    return professional


@router.put("/{professional_id}", response_model=ProfessionalResponse)
async def update_professional(professional_id: UUID, data: ProfessionalCreate):
    """Update professional"""
    professional = _mock_professionals.get(str(professional_id))
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")
    
    professional["email"] = data.email
    professional["name"] = data.name
    professional["updated_at"] = datetime.utcnow()
    _mock_professionals[str(professional_id)] = professional
    return professional


@router.post("/{professional_id}/interview/start")
async def start_interview(professional_id: UUID):
    """Start interview session (WebSocket) - returns WebSocket endpoint"""
    # In production, this would establish a WebSocket connection
    # For now, return the WebSocket URL
    return {
        "websocket_url": f"/ws/interview/{professional_id}",
        "message": "Connect to this WebSocket for real-time interview"
    }


@router.post("/{professional_id}/voice-clips", response_model=VoiceClipResponse)
async def upload_voice_clip(professional_id: UUID, data: VoiceClipCreate):
    """Upload voice clip"""
    voice_clip = VoiceClipResponse(
        id=uuid4(),
        professional_id=professional_id,
        question_key=data.question_key,
        audio_url=data.audio_url,
        duration_seconds=data.duration_seconds,
        created_at=datetime.utcnow(),
    )
    return voice_clip


@router.get("/{professional_id}/dashboard", response_model=DashboardStats)
async def get_dashboard(professional_id: UUID):
    """Get professional dashboard"""
    # Mock data
    return DashboardStats(
        total_students=42,
        anonymized_outcomes=[
            {"energized": "Creative problem-solving", "count": 15},
            {"energized": "Making an impact", "count": 12},
            {"energized": "Learning new things", "count": 15},
        ],
        pending_requests=3,
        accepted_requests=5,
    )


@router.put("/{professional_id}/connection-requests/{request_id}", response_model=ConnectionRequestResponse)
async def update_connection_request(
    professional_id: UUID,
    request_id: UUID,
    data: ConnectionRequestUpdate,
):
    """Accept or decline connection request"""
    # Mock - in production would update in database
    return ConnectionRequestResponse(
        id=request_id,
        student_id=uuid4(),
        professional_id=professional_id,
        session_id=None,
        status=data.status,
        student_message=None,
        professional_response=data.response_message,
    )


@router.post("/interview/complete", status_code=201)
async def complete_interview(data: ProfessionalInterviewComplete):
    """Complete professional interview"""
    # In production, this would trigger the World Builder Agent
    return {
        "professional_id": str(data.professional_id),
        "transcript_length": len(data.transcript),
        "consent_given": data.consent_given,
        "world_building_started": True,
    }