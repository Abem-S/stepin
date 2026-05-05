"""LangGraph Agent State Definitions"""
from typing import TypedDict, List, Optional, Dict, Any
from datetime import date


class AgentState(TypedDict, total=False):
    """
    Base state for all LangGraph agents in StepIn.
    
    This state is passed between nodes in the agent graph
    and maintains context throughout the agent execution.
    """
    # Identity
    professional_id: Optional[str]
    student_id: Optional[str]
    session_id: Optional[str]
    
    # Diary & Story
    diary_entry: Optional[Dict[str, Any]]
    diary_entries: Optional[List[Dict[str, Any]]]
    story_experience: Optional[Dict[str, Any]]
    
    # Student Profile
    student_profile: Optional[Dict[str, Any]]
    strength_map: Optional[Dict[str, float]]
    career_rankings: Optional[List[Dict[str, Any]]]
    
    # Shadow Day Session
    choices: List[Dict[str, Any]]
    current_moment: int
    total_moments: int
    hesitations_ms: List[int]
    free_text_responses: List[str]
    
    # Conversational
    conversation_history: List[Dict[str, str]]
    messages: List[Dict[str, str]]
    rag_context: List[str]
    
    # Output
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    
    # Metadata
    model: str
    temperature: float


class DiaryExtractionState(AgentState):
    """State specific to Diary Extraction Agent"""
    raw_transcript: Optional[str]
    extracted_content: Optional[Dict[str, Any]]


class StoryGenerationState(AgentState):
    """State specific to Story Generation Agent"""
    moment_count: int  # 6-30 dynamically determined
    experience_data: Optional[Dict[str, Any]]


class ScenarioState(AgentState):
    """State specific to Scenario Agent"""
    current_moment_data: Optional[Dict[str, Any]]
    student_choice: Optional[Dict[str, Any]]
    next_moment_data: Optional[Dict[str, Any]]


class ProfileState(AgentState):
    """State specific to Profile/Reflection Agent"""
    energized_by: List[str]
    drained_by: List[str]
    choices_reveal: List[str]
    recommendations: List[Dict[str, Any]]


class RecommenderState(AgentState):
    """State specific to Recommender Agent"""
    available_stories: List[Dict[str, Any]]
    relevance_scores: Dict[str, float]
    not_motivated_by: List[str]


class DigitalTwinState(AgentState):
    """State specific to Digital Twin Agent"""
    user_message: str
    professional_context: Dict[str, Any]
    retrieved_diary_entries: List[Dict[str, Any]]


# Default values for state initialization
def get_default_state() -> AgentState:
    """Get default state values"""
    return {
        "professional_id": None,
        "student_id": None,
        "session_id": None,
        "diary_entry": None,
        "diary_entries": [],
        "story_experience": None,
        "student_profile": None,
        "strength_map": {},
        "career_rankings": [],
        "choices": [],
        "current_moment": 0,
        "total_moments": 6,
        "hesitations_ms": [],
        "free_text_responses": [],
        "conversation_history": [],
        "messages": [],
        "rag_context": [],
        "result": None,
        "error": None,
        "model": "gemini-2.5-flash",
        "temperature": 0.7,
    }