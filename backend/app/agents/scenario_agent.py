"""Scenario Agent - LangGraph implementation for real-time scenario generation"""
import json
import logging
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END

from app.agents.state import ScenarioState, get_default_state
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Scenario Agent for StepIn, a career exploration platform.

Your role is to generate real-time scenario moments during a student's Shadow Day experience.
This happens after the student makes a choice - you generate the next moment based on their decision.

Guidelines:
- Generate scenarios in under 2 seconds (use gemini-2.5-flash)
- Write in second person ("You...") for immersion
- Make scenes vivid with sensory details
- Present choices that feel meaningful
- Track the emotional journey (energized_by, drained_by)
- Keep scenarios concise for the real-time experience"""


async def load_current_moment(agent, state: ScenarioState) -> ScenarioState:
    """Load the current moment data from the story experience"""
    story_experience = state.get("story_experience", {})
    current_moment = state.get("current_moment", 1)
    
    moments = story_experience.get("experience_data", {}).get("moments", [])
    
    # Find the current moment
    for moment in moments:
        if moment.get("id") == current_moment:
            state["current_moment_data"] = moment
            break
    
    return state


async def process_student_choice(agent, state: ScenarioState) -> ScenarioState:
    """Process the student's choice and determine the result"""
    student_choice = state.get("student_choice", {})
    current_moment = state.get("current_moment_data", {})
    
    choice_type = student_choice.get("type", "a")  # "a" or "b"
    
    # Update energized_by and drained_by based on choice
    choices = state.get("choices", [])
    choices.append({
        "moment_id": current_moment.get("id"),
        "choice": choice_type,
        "moment_text": current_moment.get("scene", ""),
    })
    state["choices"] = choices
    
    # Track energized/drained
    energized_by = current_moment.get("energized_by", [])
    drained_by = current_moment.get("drained_by", [])
    
    # If choice is 'a', add energized_by; if 'b', add drained_by
    if choice_type == "a" and energized_by:
        existing_energized = state.get("result", {}).get("energized_by", [])
        state["result"] = state.get("result", {})
        state["result"]["energized_by"] = existing_energized + energized_by
    elif choice_type == "b" and drained_by:
        existing_drained = state.get("result", {}).get("drained_by", [])
        state["result"] = state.get("result", {})
        state["result"]["drained_by"] = existing_drained + drained_by
    
    return state


async def generate_next_moment(agent, state: ScenarioState) -> ScenarioState:
    """Generate the next moment based on student's choice"""
    current_moment = state.get("current_moment_data", {})
    student_choice = state.get("student_choice", {})
    total_moments = state.get("total_moments", 10)
    
    choice_type = student_choice.get("type", "a")
    
    # Get next moment ID
    next_moment_id = (
        current_moment.get("next_moment_a") if choice_type == "a" 
        else current_moment.get("next_moment_b")
    )
    
    # Check if story is complete
    if next_moment_id is None or next_moment_id > total_moments:
        state["next_moment_data"] = None  # End of story
        return state
    
    # Find the next moment in story experience
    story_experience = state.get("story_experience", {})
    moments = story_experience.get("experience_data", {}).get("moments", [])
    
    for moment in moments:
        if moment.get("id") == next_moment_id:
            state["next_moment_data"] = moment
            state["current_moment"] = next_moment_id
            break
    
    return state


async def generate_moment_for_choice(agent, state: ScenarioState) -> ScenarioState:
    """
    Generate a new moment dynamically (fallback when not pre-generated).
    Used for adaptive experiences where moments are generated on-the-fly.
    """
    story_experience = state.get("story_experience", {})
    current_moment = state.get("current_moment", 1)
    student_choice = state.get("student_choice", {})
    choices = state.get("choices", [])
    
    prompt = f"""Generate moment {current_moment} for this Shadow Day story.

Story context:
- Professional: {story_experience.get('title')}
- Category: {story_experience.get('category')}

Previous choices:
{json.dumps(choices[-3:] if len(choices) >= 3 else choices)}

Student just chose: {student_choice.get('type')} - {student_choice.get('text', '')}

Generate the next moment. Return JSON:
{{
  "scene": "Second-person description",
  "choice_a": "First choice text",
  "choice_b": "Second choice text",
  "result_a": "What happens with choice A",
  "result_b": "What happens with choice B", 
  "next_moment_a": {current_moment + 1},
  "next_moment_b": {current_moment + 1},
  "energized_by": [],
  "drained_by": []
}}"""

    try:
        result = await gemini_service.generate_json(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.8,
        )
        state["next_moment_data"] = result
        state["current_moment"] = current_moment + 1
    except Exception as e:
        logger.error(f"Error generating moment: {e}")
        # Use fallback
        state["next_moment_data"] = {
            "id": current_moment + 1,
            "scene": "The story continues...",
            "choice_a": "Continue forward",
            "choice_b": "Take a moment to reflect",
            "result_a": "You move forward with confidence.",
            "result_b": "You pause to consider what you've learned.",
            "next_moment_a": current_moment + 2,
            "next_moment_b": current_moment + 2,
            "energized_by": [],
            "drained_by": [],
        }
    
    return state


class ScenarioAgent:
    """LangGraph agent for real-time scenario generation during Shadow Day"""
    
    def __init__(self):
        self.name = "Scenario Agent"
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph = StateGraph(ScenarioState)
        
        # Add nodes
        graph.add_node("load_moment", load_current_moment)
        graph.add_node("process_choice", process_student_choice)
        graph.add_node("generate_next", generate_next_moment)
        graph.add_node("generate_dynamic", generate_moment_for_choice)
        
        # Define edges
        graph.set_entry_point("load_moment")
        graph.add_edge("load_moment", "process_choice")
        
        # Conditional: pre-generated or dynamic
        graph.add_conditional_edges(
            "process_choice",
            lambda state: "has_pregenerated" if state.get("story_experience", {}).get("experience_data", {}).get("moments") else "needs_generation",
            {
                "has_pregenerated": "generate_next",
                "needs_generation": "generate_dynamic",
            }
        )
        
        graph.add_edge("generate_next", END)
        graph.add_edge("generate_dynamic", END)
        
        self.graph = graph.compile()
    
    async def run(
        self,
        story_experience: Dict[str, Any],
        current_moment: int,
        student_choice: Dict[str, Any],
        total_moments: int = 10,
    ) -> Dict[str, Any]:
        """
        Get the next scenario moment based on student's choice.
        
        Args:
            story_experience: The story experience data
            current_moment: Current moment number
            student_choice: Student's choice (type: "a" or "b", text: str)
            total_moments: Total moments in the story
            
        Returns:
            Next moment data
        """
        initial_state: ScenarioState = {
            **get_default_state(),
            "story_experience": story_experience,
            "current_moment": current_moment,
            "student_choice": student_choice,
            "total_moments": total_moments,
        }
        
        result = await self.graph.ainvoke(initial_state)
        
        # Return the next moment or indicate end of story
        if result.get("next_moment_data") is None:
            return {
                "is_complete": True,
                "energized_by": result.get("result", {}).get("energized_by", []),
                "drained_by": result.get("result", {}).get("drained_by", []),
                "choices": result.get("choices", []),
            }
        
        return {
            "is_complete": False,
            "moment": result.get("next_moment_data"),
            "current_moment": result.get("current_moment", current_moment + 1),
        }


# Singleton instance
scenario_agent = ScenarioAgent()


async def get_next_moment(
    story_experience: Dict[str, Any],
    current_moment: int,
    student_choice: Dict[str, Any],
    total_moments: int = 10,
) -> Dict[str, Any]:
    """Convenience function to get next moment"""
    return await scenario_agent.run(story_experience, current_moment, student_choice, total_moments)