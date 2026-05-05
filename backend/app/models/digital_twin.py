from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class TwinMessage(BaseModel):
    """Twin message"""
    message: str
    timestamp: datetime


class TwinConversationCreate(BaseModel):
    """Start new Digital Twin conversation"""
    student_id: UUID
    professional_id: UUID


class TwinConversationResponse(BaseModel):
    """Digital Twin conversation response"""
    id: UUID
    student_id: UUID
    professional_id: UUID
    messages: List[TwinMessage]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TwinMessageSend(BaseModel):
    """Send message to Digital Twin"""
    conversation_id: UUID
    message: str


class TwinMessageResponse(BaseModel):
    """Twin message response"""
    id: UUID
    conversation_id: UUID
    message: str
    is_from_twin: bool
    timestamp: datetime

    class Config:
        from_attributes = True