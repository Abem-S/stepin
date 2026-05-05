from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel


# Interview Agent
class NextQuestionRequest(BaseModel):
    """Request next interview question"""
    professional_id: UUID
    conversation_history: List[dict]
    question_index: int


class NextQuestionResponse(BaseModel):
    """Next interview question response"""
    question: str
    question_key: str
    is_final: bool = False


# World Builder Agent
class WorldBuilderRequest(BaseModel):
    """World Builder Agent request"""
    professional_id: UUID
    transcript: List[dict]
    scraped_data: Optional[dict] = None


class WorldBuilderResponse(BaseModel):
    """World Builder Agent response"""
    career_world_json: dict
    digital_twin_kb: dict
    is_complete: bool


# Scenario Agent
class ScenarioRequest(BaseModel):
    """Scenario Agent request"""
    career_world_id: str
    current_moment_index: int
    student_choice: Optional[int] = None
    student_free_text: Optional[str] = None
    student_hesitation_ms: int = 0


class ScenarioResponse(BaseModel):
    """Scenario Agent response"""
    next_moment_index: int
    text_lines: List[str]
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    choices: List[str]
    is_emotional_peak: bool = False
    voice_clip_url: Optional[str] = None
    pull_quote: Optional[str] = None


# Profile Agent
class ProfileUpdateRequest(BaseModel):
    """Profile update request"""
    student_id: str  # Using string instead of UUID for flexibility
    session_id: str
    choices: List[dict]
    free_text_responses: List[str]
    hesitations_ms: List[int]


class ProfileUpdateResponse(BaseModel):
    """Profile update response"""
    student_id: str
    profile_updated: bool
    energized_by: List[str]
    drained_by: List[str]


# Reflection Agent
class ReflectionRequest(BaseModel):
    """Reflection Agent request"""
    student_id: str
    session_id: str
    profile_data: dict


class ReflectionResponse(BaseModel):
    """Reflection Agent response"""
    energized_by: List[str]
    drained_by: List[str]
    choices_reveal: List[str]
    recommendations: List[dict]
    career_dna_card_data: dict


# Recommender Agent
class RecommenderRequest(BaseModel):
    """Recommender Agent request"""
    student_id: str
    profile_data: dict
    available_career_worlds: Optional[List[dict]] = None
    not_motivated_by: Optional[List[str]] = None


class RecommenderResponse(BaseModel):
    """Recommender Agent response"""
    recommendations: List[dict]
    relevance_scores: List[float]
    not_motivated_by: Optional[List[str]] = None
# Image Generation
class ImageGenerationRequest(BaseModel):
    """Request to generate an atmospheric image"""
    prompt: str
    career_world_id: Optional[str] = None
    moment_index: Optional[int] = None


class ImageGenerationResponse(BaseModel):
    """Image generation response"""
    image_data: Optional[str]  # Base64 encoded
    success: bool
    prompt: str
    error: Optional[str] = None