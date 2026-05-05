"""Reflection Agent - LangGraph implementation for generating Career DNA cards"""
import json
import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END

from app.agents.state import ProfileState, get_default_state
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Reflection Agent for StepIn platform.

Your role is to generate the Career DNA card - a beautiful, shareable summary of what 
the student learned about themselves through the Shadow Day experience.

Guidelines:
- Generate insights that feel personally resonant and authentic
- NEVER tell the student what career to choose - only show what energizes/drains them
- Recommend 2-3 careers worth exploring based on their profile (not prescribe)
- Write in a warm, insightful tone
- Create a "shareable insight" - one sentence that captures the essence
- Make it visually appealing for the DNA card format"""


async def load_profile_data(agent, state: ProfileState) -> ProfileState:
    """Load all profile data for reflection"""
    # This node aggregates data from the Profile Agent
    # In production, this would fetch from the database
    
    return state


async def generate_dna_content(agent, state: ProfileState) -> ProfileState:
    """Generate the Career DNA card content"""
    energized_by = state.get("energized_by", [])
    drained_by = state.get("drained_by", [])
    choices_reveal = state.get("choices_reveal", [])
    career_name = state.get("student_profile", {}).get("career_name", "the career")
    
    prompt = f"""Generate the Career DNA card content for a student who experienced: {career_name}

What energized them: {json.dumps(energized_by)}
What drained them: {json.dumps(drained_by)}
What their choices reveal: {json.dumps(choices_reveal)}

Generate:
1. "energized_by": 2-3 items that energized the student
2. "drained_by": 2-3 items that drained the student  
3. "choices_reveal": 2-3 insights about who they are
4. "recommendations": 2-3 careers worth exploring (NOT "you should be X")
   - Each with: career_name, category, reason (how it connects to their profile)
5. "shareable_insight": One powerful sentence capturing their experience

Return JSON:
{{
  "energized_by": ["What energized them"],
  "drained_by": ["What drained them"],
  "choices_reveal": ["What choices reveal"],
  "recommendations": [
    {{"career_name": "Career", "category": "Category", "reason": "Why it fits"}}
  ],
  "shareable_insight": "One sentence summary"
}}"""

    try:
        result = await gemini_service.generate_json(
            prompt=prompt,
            model="gemini-2.5-pro",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
        )
        state["recommendations"] = result.get("recommendations", [])
        state["result"] = state.get("result", {})
        state["result"]["dna_content"] = result
    except Exception as e:
        logger.error(f"Error generating DNA content: {e}")
        state["error"] = str(e)
    
    return state


async def generate_shareable_insight(agent, state: ProfileState) -> ProfileState:
    """Generate the main shareable insight if not already generated"""
    dna_content = state.get("result", {}).get("dna_content", {})
    
    if dna_content.get("shareable_insight"):
        return state  # Already generated
    
    energized_by = state.get("energized_by", [])
    
    prompt = f"""Create one powerful, shareable sentence that captures this student's experience:

Energized by: {energized_by}

Make it:
- Personal and resonant
- Not prescriptive (don't say "you should be...")
- Something they'd want to share
- 1-2 sentences max

Just return the sentence."""

    try:
        insight = await gemini_service.generate_content(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.8,
        )
        state["result"] = state.get("result", {})
        state["result"]["dna_content"] = state.get("result", {}).get("dna_content", {})
        state["result"]["dna_content"]["shareable_insight"] = insight
    except Exception as e:
        logger.warning(f"Error generating insight: {e}")
    
    return state


async def finalize_dna_card(agent, state: ProfileState) -> ProfileState:
    """Finalize the Career DNA card"""
    dna_content = state.get("result", {}).get("dna_content", {})
    
    # Ensure we have all required fields
    dna_content.setdefault("energized_by", state.get("energized_by", []))
    dna_content.setdefault("drained_by", state.get("drained_by", []))
    dna_content.setdefault("choices_reveal", state.get("choices_reveal", []))
    
    state["result"] = state.get("result", {})
    state["result"]["career_dna_card"] = dna_content
    
    return state


class ReflectionAgent:
    """LangGraph agent for generating Career DNA cards"""
    
    def __init__(self):
        self.name = "Reflection Agent"
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph = StateGraph(ProfileState)
        
        # Add nodes
        graph.add_node("load_profile", load_profile_data)
        graph.add_node("generate_content", generate_dna_content)
        graph.add_node("generate_insight", generate_shareable_insight)
        graph.add_node("finalize", finalize_dna_card)
        
        # Define edges
        graph.set_entry_point("load_profile")
        graph.add_edge("load_profile", "generate_content")
        graph.add_edge("generate_content", "generate_insight")
        graph.add_edge("generate_insight", "finalize")
        graph.add_edge("finalize", END)
        
        self.graph = graph.compile()
    
    async def run(
        self,
        energized_by: List[str],
        drained_by: List[str],
        choices_reveal: List[str],
        career_name: str = None,
        existing_recommendations: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate Career DNA card content.
        
        Args:
            energized_by: What energizes the student
            drained_by: What drains the student
            choices_reveal: What choices reveal about them
            career_name: The career they experienced
            existing_recommendations: Existing recommendations to consider
            
        Returns:
            Complete Career DNA card content
        """
        initial_state: ProfileState = {
            **get_default_state(),
            "energized_by": energized_by,
            "drained_by": drained_by,
            "choices_reveal": choices_reveal,
            "student_profile": {"career_name": career_name} if career_name else {},
            "recommendations": existing_recommendations or [],
        }
        
        result = await self.graph.ainvoke(initial_state)
        
        return result.get("result", {}).get("career_dna_card", {
            "energized_by": energized_by,
            "drained_by": drained_by,
            "choices_reveal": choices_reveal,
            "recommendations": [],
            "shareable_insight": "Every experience teaches us something new about ourselves.",
        })


# Singleton instance
reflection_agent = ReflectionAgent()


async def generate_career_dna_card(
    energized_by: List[str],
    drained_by: List[str],
    choices_reveal: List[str],
    career_name: str = None,
    existing_recommendations: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Convenience function to generate Career DNA card"""
    return await reflection_agent.run(
        energized_by=energized_by,
        drained_by=drained_by,
        choices_reveal=choices_reveal,
        career_name=career_name,
        existing_recommendations=existing_recommendations,
    )