from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class StudentCreate(BaseModel):
    """Create anonymous student"""
    anonymous_identifier: Optional[str] = None


class StudentResponse(BaseModel):
    """Student response"""
    id: UUID
    anonymous_identifier: Optional[str] = None
    created_at: datetime
    last_active_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    """Start new Shadow Day session"""
    student_id: UUID
    career_world_id: UUID


class SessionResponse(BaseModel):
    """Session response"""
    id: UUID
    student_id: UUID
    career_world_id: UUID
    choices: Optional[dict] = None
    timing_data: Optional[dict] = None
    hesitations_ms: Optional[dict] = None
    rewind_answer: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChoiceMake(BaseModel):
    """Submit choice for current moment"""
    session_id: UUID
    moment_index: int
    choice_index: Optional[int] = None
    free_text: Optional[str] = None
    hesitation_ms: int


class MomentResponse(BaseModel):
    """Scenario moment response"""
    moment_index: int
    text_lines: List[str]
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    choices: List[str]
    is_emotional_peak: bool = False
    voice_clip_url: Optional[str] = None
    pull_quote: Optional[str] = None


class RewindAnswer(BaseModel):
    """Rewind answer submission"""
    session_id: UUID
    answer: str  # "yes" or "not_for_me"