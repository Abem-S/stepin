from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class CareerRecommendation(BaseModel):
    """Career recommendation"""
    career_name: str
    category: str
    reason: str


class CareerDNACard(BaseModel):
    """Career DNA Card"""
    student_id: UUID
    energized_by: List[str]
    drained_by: List[str]
    choices_reveal: List[str]
    recommendations: List[CareerRecommendation]
    card_image_url: Optional[str] = None


class ProfileResponse(BaseModel):
    """Student profile response"""
    id: UUID
    student_id: UUID
    career_world_id: Optional[UUID] = None
    energized_by: Optional[List[str]] = None
    drained_by: Optional[List[str]] = None
    choices_reveal: Optional[List[str]] = None
    recommendations: Optional[List[CareerRecommendation]] = None
    career_dna_card_url: Optional[str] = None

    class Config:
        from_attributes = True