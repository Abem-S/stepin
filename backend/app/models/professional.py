from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class ProfessionalCreate(BaseModel):
    """Professional onboarding request"""
    email: EmailStr
    name: str


class ProfessionalResponse(BaseModel):
    """Professional profile response"""
    id: UUID
    email: EmailStr
    name: str
    career_category: Optional[str] = None
    years_experience: Optional[int] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    website_url: Optional[str] = None
    connection_preference: str = "email"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterviewTurn(BaseModel):
    """Single interview Q&A turn"""
    question: str
    answer: str
    timestamp: datetime


class ProfessionalInterviewComplete(BaseModel):
    """Professional interview completion payload"""
    professional_id: UUID
    transcript: List[InterviewTurn]
    consent_given: bool


class VoiceClipCreate(BaseModel):
    """Voice clip upload request"""
    question_key: str
    audio_url: str
    duration_seconds: Optional[int] = None


class VoiceClipResponse(BaseModel):
    """Voice clip response"""
    id: UUID
    professional_id: UUID
    question_key: str
    audio_url: str
    duration_seconds: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Professional dashboard statistics"""
    total_students: int
    anonymized_outcomes: List[dict]
    pending_requests: int
    accepted_requests: int


class ConnectionRequestUpdate(BaseModel):
    """Update connection request status"""
    status: str  # "accepted" or "declined"
    response_message: Optional[str] = None


class ConnectionRequestResponse(BaseModel):
    """Connection request response"""
    id: UUID
    student_id: UUID
    professional_id: UUID
    session_id: Optional[UUID] = None
    status: str
    student_message: Optional[str] = None
    professional_response: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True