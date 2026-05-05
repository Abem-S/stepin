from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ConnectionRequestCreate(BaseModel):
    """Create connection request"""
    student_id: UUID
    professional_id: UUID
    session_id: UUID
    message: Optional[str] = None


class ConnectionRequestResponse(BaseModel):
    """Connection request response"""
    id: UUID
    student_id: UUID
    professional_id: UUID
    session_id: Optional[UUID] = None
    status: str
    student_message: Optional[str] = None
    professional_response: Optional[str] = None

    class Config:
        from_attributes = True