"""Profile Agent - LangGraph implementation for analyzing student choices and building strength maps"""
import json
import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END

from app.agents.state import ProfileState, get_default_state
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Profile Agent for StepIn platform.

Your role is to analyze a student's choices during a Shadow Day experience and build their strength map.
This runs silently in the background - the student doesn't see this happening.

Guidelines:
- Analyze patterns in choices to identify strengths
- Track what energizes the student (choices that align with their values)
- Track what drains the student (choices that conflict with their values)
- Identify decision patterns (quick vs deliberative, risk orientation, values)
- Update the student's strength map based on the experience
- NEVER tell the student what career to choose - only show what energizes/drains them"""


async def analyze_choices(agent, state: ProfileState) -> ProfileState:
    """Analyze the student's choices to identify patterns"""
    choices = state.get("choices", [])
    hesitations = state.get("hesitations_ms", [])
    free_text = state.get("free_text_responses", [])
    
    prompt = f"""Analyze these student choices from a Shadow Day experience:

Choices made: {json.dumps(choices)}
Hesitation times (ms): {hesitations}
Free text responses: {json.dumps(free_text)}

Analyze for:
1. Decision patterns (quick vs deliberative)
2. Risk orientation (cautious vs bold)
3. Value-driven choices (what matters to them)
4. Emotional responses

Return JSON:
{{
  "decision_patterns": {{
    "quick_vs_deliberate": "Pattern description",
    "risk_orientation": "conservative|moderate|adventurous",
    "core_values": ["value1", "value2"]
  }},
  "choice_themes": ["theme1", "theme2"]
}}"""

    try:
        result = await gemini_service.generate_json(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.5,
        )
        state["result"] = state.get("result", {})
        state["result"]["patterns"] = result.get("decision_patterns", {})
    except Exception as e:
        logger.error(f"Error analyzing choices: {e}")
        state["error"] = str(e)
    
    return state


async def identify_energized_drained(agent, state: ProfileState) -> ProfileState:
    """Identify what energizes and drains the student"""
    choices = state.get("choices", [])
    story_experience = state.get("story_experience", {})
    
    prompt = f"""From these student choices, identify what energizes and drains them:

Choices: {json.dumps(choices)}
Story: {story_experience.get('title')}

For each choice made, determine:
- What the choice energized (if choice was A)
- What the choice drained (if choice was B)

Aggregate into lists of what energizes/drains the student overall.

Return JSON:
{{
  "energized_by": ["list of what energizes them"],
  "drained_by": ["list of what drains them"]
}}"""

    try:
        result = await gemini_service.generate_json(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.5,
        )
        state["energized_by"] = result.get("energized_by", [])
        state["drained_by"] = result.get("drained_by", [])
    except Exception as e:
        logger.error(f"Error identifying energized/drained: {e}")
    
    return state


async def generate_strength_map(agent, state: ProfileState) -> ProfileState:
    """Generate or update the student's strength map"""
    energized_by = state.get("energized_by", [])
    drained_by = state.get("drained_by", [])
    existing_map = state.get("strength_map", {})
    
    # Map energized/drained to strength dimensions
    strength_mapping = {
        "leadership": ["lead", "guide", "mentor", "decide", "take charge"],
        "empathy": ["help", "understand", "connect", "support", "listen"],
        "analytical": ["analyze", "solve", "think", "understand", "figure out"],
        "creative": ["create", "design", "imagine", "innovate", "new"],
        "technical": ["build", "code", "technical", "system", "engineer"],
        "communication": ["speak", "present", "write", "share", "explain"],
        "collaboration": ["team", "together", "collaborate", "group", "partner"],
        "autonomy": ["independent", "own", "self", "personal", "freedom"],
    }
    
    # Start with existing map
    strength_map = dict(existing_map) if existing_map else {}
    
    # Add energized strengths
    for strength, keywords in strength_mapping.items():
        for energized_item in energized_by:
            if any(kw in energized_item.lower() for kw in keywords):
                current = strength_map.get(strength, 0.0)
                strength_map[strength] = min(1.0, current + 0.15)
    
    # Subtract drained (inverse)
    for strength, keywords in strength_mapping.items():
        for drained_item in drained_by:
            if any(kw in drained_item.lower() for kw in keywords):
                current = strength_map.get(strength, 0.0)
                strength_map[strength] = max(0.0, current - 0.1)
    
    state["strength_map"] = strength_map
    return state


async def extract_revealed_traits(agent, state: ProfileState) -> ProfileState:
    """Extract what the student's choices reveal about them"""
    choices = state.get("choices", [])
    
    prompt = f"""Analyze what this student's choices reveal about them:

{json.dumps(choices, indent=2)}

Generate 3-5 insights about who they are based on their decisions.

Return JSON:
{{
  "choices_reveal": [
    "They value authentic connection over surface-level interaction",
    "They prefer thoughtful deliberation over quick decisions",
    "They find meaning in helping others grow"
  ]
}}"""

    try:
        result = await gemini_service.generate_json(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.6,
        )
        state["choices_reveal"] = result.get("choices_reveal", [])
    except Exception as e:
        logger.error(f"Error extracting revealed traits: {e}")
    
    return state


class ProfileAgent:
    """LangGraph agent for analyzing student choices and building strength maps"""
    
    def __init__(self):
        self.name = "Profile Agent"
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph = StateGraph(ProfileState)
        
        # Add nodes
        graph.add_node("analyze_choices", analyze_choices)
        graph.add_node("identify_energized_drained", identify_energized_drained)
        graph.add_node("generate_strength_map", generate_strength_map)
        graph.add_node("extract_traits", extract_revealed_traits)
        
        # Define edges
        graph.set_entry_point("analyze_choices")
        graph.add_edge("analyze_choices", "identify_energized_drained")
        graph.add_edge("identify_energized_drained", "generate_strength_map")
        graph.add_edge("generate_strength_map", "extract_traits")
        graph.add_edge("extract_traits", END)
        
        self.graph = graph.compile()
    
    async def run(
        self,
        choices: List[Dict[str, Any]],
        hesitations_ms: List[int] = None,
        free_text_responses: List[str] = None,
        existing_strength_map: Dict[str, float] = None,
        story_experience: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Analyze choices and generate student profile.
        
        Args:
            choices: List of choices made during Shadow Day
            hesitations_ms: Time spent on each decision (ms)
            free_text_responses: Free text responses
            existing_strength_map: Current strength map to update
            story_experience: The story experience for context
            
        Returns:
            Updated profile data
        """
        initial_state: ProfileState = {
            **get_default_state(),
            "choices": choices,
            "hesitations_ms": hesitations_ms or [],
            "free_text_responses": free_text_responses or [],
            "strength_map": existing_strength_map or {},
            "story_experience": story_experience or {},
        }
        
        result = await self.graph.ainvoke(initial_state)
        
        return {
            "strength_map": result.get("strength_map", {}),
            "energized_by": result.get("energized_by", []),
            "drained_by": result.get("drained_by", []),
            "choices_reveal": result.get("choices_reveal", []),
            "decision_patterns": result.get("result", {}).get("patterns", {}),
        }


# Singleton instance
profile_agent = ProfileAgent()


async def analyze_student_profile(
    choices: List[Dict[str, Any]],
    hesitations_ms: List[int] = None,
    free_text_responses: List[str] = None,
    existing_strength_map: Dict[str, float] = None,
    story_experience: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Convenience function to analyze student profile"""
    return await profile_agent.run(
        choices=choices,
        hesitations_ms=hesitations_ms,
        free_text_responses=free_text_responses,
        existing_strength_map=existing_strength_map,
        story_experience=story_experience,
    )