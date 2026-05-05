"""LangGraph Agents for StepIn Platform"""

from app.agents.base import BaseAgent, StructuredOutputAgent
from app.agents.state import (
    AgentState,
    DiaryExtractionState,
    StoryGenerationState,
    ScenarioState,
    ProfileState,
    RecommenderState,
    DigitalTwinState,
    get_default_state,
)

# Import all agent implementations
from app.agents.diary_extraction_agent import (
    DiaryExtractionAgent,
    diary_extraction_agent,
    extract_diary_entry,
)

from app.agents.story_generation_agent import (
    StoryGenerationAgent,
    story_generation_agent,
    generate_story_experience,
)

from app.agents.scenario_agent import (
    ScenarioAgent,
    scenario_agent,
    get_next_moment,
)

from app.agents.profile_agent import (
    ProfileAgent,
    profile_agent,
    analyze_student_profile,
)

from app.agents.reflection_agent import (
    ReflectionAgent,
    reflection_agent,
    generate_career_dna_card,
)

from app.agents.recommender_agent import (
    RecommenderAgent,
    recommender_agent,
    recommend_careers,
)

from app.agents.digital_twin_agent import (
    DigitalTwinAgent,
    digital_twin_agent,
    get_digital_twin_response,
)

__all__ = [
    # Base classes
    "BaseAgent",
    "StructuredOutputAgent",
    # State types
    "AgentState",
    "DiaryExtractionState",
    "StoryGenerationState",
    "ScenarioState",
    "ProfileState",
    "RecommenderState",
    "DigitalTwinState",
    "get_default_state",
    # Agent implementations
    "DiaryExtractionAgent",
    "diary_extraction_agent",
    "extract_diary_entry",
    "StoryGenerationAgent",
    "story_generation_agent",
    "generate_story_experience",
    "ScenarioAgent",
    "scenario_agent",
    "get_next_moment",
    "ProfileAgent",
    "profile_agent",
    "analyze_student_profile",
    "ReflectionAgent",
    "reflection_agent",
    "generate_career_dna_card",
    "RecommenderAgent",
    "recommender_agent",
    "recommend_careers",
    "DigitalTwinAgent",
    "digital_twin_agent",
    "get_digital_twin_response",
]