"""Story Generation Agent - LangGraph implementation for dynamic story experiences"""
import json
import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END

from app.agents.state import StoryGenerationState, get_default_state
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Story Generation Agent for StepIn platform.

Your role is to transform diary entries into immersive Shadow Day story experiences.
Each story consists of "moments" - interactive scenes where students make choices.

Guidelines:
- Create 6-30 moments based on the richness of the diary entry
- Each moment has: scene description, 2 choices, results, next_moment navigation
- Track energized_by and drained_by for each choice
- Include emotional peaks at key decision points
- Write in second person ("You...") for student immersion
- Make scenes vivid with specific times, places, and sensory details"""


async def analyze_diary_richness(agent, state: StoryGenerationState) -> StoryGenerationState:
    """Analyze how many moments to generate based on diary content"""
    diary_entry = state.get("diary_entry", {})
    
    # Count key elements to determine moment count
    key_moments = diary_entry.get("key_moments", [])
    emotional_beats = diary_entry.get("emotional_beats", [])
    decisions = diary_entry.get("decisions", [])
    
    content_richness = len(key_moments) + len(emotional_beats) + len(decisions)
    
    # Map richness to moment count (6-30)
    if content_richness >= 8:
        moment_count = 15  # Very rich - lots of content
    elif content_richness >= 5:
        moment_count = 10  # Moderately rich
    elif content_richness >= 3:
        moment_count = 8   # Some content
    else:
        moment_count = 6   # Minimal content
    
    state["moment_count"] = moment_count
    return state


async def determine_story_arc(agent, state: StoryGenerationState) -> StoryGenerationState:
    """Determine the narrative arc of the story"""
    diary_entry = state.get("diary_entry", {})
    key_moments = diary_entry.get("key_moments", [])
    
    prompt = f"""Analyze this diary entry and suggest a story structure:

Key moments: {key_moments}

Suggest the story arc with:
- Opening: How to start the Shadow Day (setting the scene)
- Rising action: Key events to include
- Climax: The most impactful moment
- Resolution: How to end the story

Return JSON:
{{
  "arc_type": "challenge_overcome|growth_journey|day_in_life|turning_point",
  "opening_hook": "How to start the story",
  "key_events": ["event1", "event2", ...],
  "climax_moment": "The pivotal moment",
  "ending": "How to conclude"
}}"""

    try:
        result = await gemini_service.generate_json(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.6,
        )
        state["experience_data"] = state.get("experience_data", {})
        state["experience_data"]["arc"] = result
    except Exception as e:
        logger.error(f"Error determining story arc: {e}")
        state["error"] = str(e)
    
    return state


async def generate_moments(agent, state: StoryGenerationState) -> StoryGenerationState:
    """Generate all story moments based on diary content"""
    diary_entry = state.get("diary_entry", {})
    moment_count = state.get("moment_count", 8)
    student_profile = state.get("student_profile", {})
    
    key_moments = diary_entry.get("key_moments", [])
    emotional_beats = diary_entry.get("emotional_beats", [])
    
    prompt = f"""Generate a Shadow Day story experience with {moment_count} moments.

DIARY ENTRY CONTENT:
- Key moments: {json.dumps(key_moments)}
- Emotional journey: {json.dumps(emotional_beats)}

STUDENT PROFILE (to personalize):
{json.dumps(student_profile) if student_profile else "New student - no profile yet"}

Generate {moment_count} moments. Each moment needs:
- id: moment number (1-{moment_count})
- scene: Second-person description of the moment (time, place, situation)
- choice_a: First choice text
- choice_b: Second choice text  
- result_a: What happens if they choose A
- result_b: What happens if they choose B
- next_moment_a: ID of next moment after A (or null if ending)
- next_moment_b: ID of next moment after B (or null if ending)
- energized_by: Array of what energizes them if they choose A (empty if B)
- drained_by: Array of what drains them if they choose B (empty if A)

Return as JSON:
{{
  "moments": [
    {{
      "id": 1,
      "scene": "...",
      "choice_a": "...",
      "choice_b": "...",
      "result_a": "...",
      "result_b": "...",
      "next_moment_a": 2,
      "next_moment_b": 3,
      "energized_by": [],
      "drained_by": []
    }}
  ]
}}

IMPORTANT: 
- Write in second person (You...) for student immersion
- Make scenes emotionally vivid and specific
- Include real dialogue where appropriate
- Ensure each moment has a clear decision point"""

    try:
        result = await gemini_service.generate_json(
            prompt=prompt,
            model="gemini-2.5-pro",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.8,
        )
        state["experience_data"] = state.get("experience_data", {})
        state["experience_data"]["moments"] = result.get("moments", [])
    except Exception as e:
        logger.error(f"Error generating moments: {e}")
        # Create fallback moments
        state["experience_data"] = state.get("experience_data", {})
        state["experience_data"]["moments"] = _create_fallback_moments(moment_count)
    
    return state


def _create_fallback_moments(count: int) -> List[Dict[str, Any]]:
    """Create fallback moments if generation fails"""
    moments = []
    for i in range(1, count + 1):
        moment = {
            "id": i,
            "scene": f"Moment {i} of your Shadow Day experience. A pivotal decision awaits.",
            "choice_a": "Embrace the challenge",
            "choice_b": "Take a cautious approach",
            "result_a": f"You choose to embrace the challenge. This leads to {i + 1}.",
            "result_b": "You choose caution. This leads to a different path.",
            "next_moment_a": i + 1 if i < count else None,
            "next_moment_b": i + 1 if i < count else None,
            "energized_by": ["challenge"],
            "drained_by": ["caution"],
        }
        moments.append(moment)
    return moments


async def add_voice_clip_prompts(agent, state: StoryGenerationState) -> StoryGenerationState:
    """Add voice clip prompts for emotional peak moments"""
    experience_data = state.get("experience_data", {})
    moments = experience_data.get("moments", [])
    
    if not moments:
        return state
    
    # Identify emotional peaks (usually 2-3 moments)
    peak_indices = [len(moments) // 3, 2 * len(moments) // 3]
    
    prompt = f"""For these story moments, suggest when the professional would record a voice clip:

Moments: {json.dumps([{{"id": m["id"], "scene": m["scene"]}} for m in moments])}

A voice clip is a moment where the professional shares a personal thought or feeling.
Suggest 2-3 moments that would have voice clips by listing their IDs:
{json.dumps(peak_indices)}

Return JSON:
{{
  "voice_clip_moments": [list of moment IDs that should have voice clips],
  "prompts": {{"moment_id": "prompt for recording"}}
}}"""

    try:
        result = await gemini_service.generate_json(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.5,
        )
        state["experience_data"]["voice_clips"] = result.get("voice_clip_moments", peak_indices)
    except Exception as e:
        logger.warning(f"Error generating voice clip prompts: {e}")
        state["experience_data"]["voice_clips"] = peak_indices
    
    return state


async def compile_story_experience(agent, state: StoryGenerationState) -> StoryGenerationState:
    """Compile the final story experience"""
    diary_entry = state.get("diary_entry", {})
    moment_count = state.get("moment_count", 8)
    experience_data = state.get("experience_data", {})
    
    # Determine category from professional's career
    student_profile = state.get("student_profile", {})
    category = student_profile.get("profession", "General")
    
    story_experience = {
        "title": f"Shadow Day: {diary_entry.get('summary', 'A Day in the Life')[:50]}",
        "category": category,
        "moment_count": moment_count,
        "min_moments": 6,
        "max_moments": 30,
        "experience_data": experience_data,
    }
    
    state["story_experience"] = story_experience
    return state


class StoryGenerationAgent:
    """LangGraph agent for generating dynamic Shadow Day story experiences"""
    
    def __init__(self):
        self.name = "Story Generation Agent"
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph = StateGraph(StoryGenerationState)
        
        # Add nodes
        graph.add_node("analyze_richness", analyze_diary_richness)
        graph.add_node("determine_arc", determine_story_arc)
        graph.add_node("generate_moments", generate_moments)
        graph.add_node("add_voice_clips", add_voice_clip_prompts)
        graph.add_node("compile_story", compile_story_experience)
        
        # Define edges
        graph.set_entry_point("analyze_richness")
        graph.add_edge("analyze_richness", "determine_arc")
        graph.add_edge("determine_arc", "generate_moments")
        graph.add_edge("generate_moments", "add_voice_clips")
        graph.add_edge("add_voice_clips", "compile_story")
        graph.add_edge("compile_story", END)
        
        self.graph = graph.compile()
    
    async def run(
        self,
        diary_entry: Dict[str, Any],
        professional_id: str,
        student_profile: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate story experience from diary entry.
        
        Args:
            diary_entry: Structured diary entry from Diary Extraction Agent
            professional_id: ID of the professional
            student_profile: Optional student profile for personalization
            
        Returns:
            Complete story experience dictionary
        """
        initial_state: StoryGenerationState = {
            **get_default_state(),
            "diary_entry": diary_entry,
            "professional_id": professional_id,
            "student_profile": student_profile or {},
        }
        
        result = await self.graph.ainvoke(initial_state)
        return result.get("story_experience", {})


# Singleton instance
story_generation_agent = StoryGenerationAgent()


async def generate_story_experience(
    diary_entry: Dict[str, Any],
    professional_id: str,
    student_profile: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Convenience function to generate story experience"""
    return await story_generation_agent.run(diary_entry, professional_id, student_profile)