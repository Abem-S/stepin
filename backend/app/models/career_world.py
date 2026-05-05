from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class CareerWorldBase(BaseModel):
    """Base Career World model"""
    category: str
    title: str
    career_category: str
    key_moments: List[dict]
    emotional_beats: List[dict]
    decision_points: List[dict]
    voice_clip_refs: List[str]


class CareerWorldCreate(CareerWorldBase):
    """Career World creation request"""
    professional_id: UUID


class CareerWorldResponse(CareerWorldBase):
    """Career World response"""
    id: UUID
    professional_id: UUID
    is_seed: bool = False
    total_students: int = 0

    class Config:
        from_attributes = True