"""Recommender Agent - LangGraph implementation for recommending careers to students"""
import json
import logging
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END

from app.agents.state import RecommenderState, get_default_state
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Recommender Agent for StepIn platform.

Your role is to match students with career worlds based on their Career DNA profile.
This drives the landing page recommendations and DNA card suggestions.

Guidelines:
- Match based on what energizes the student, not what drains them
- Ensure at least 80% relevance score threshold
- Consider the data flywheel: track careers that frequently get "Not For Me" 
  from similar profiles and deprioritize those
- Provide clear reasoning for each recommendation
- Recommend careers that align with the student's strength map
- NEVER be prescriptive - suggest, don't tell"""


async def load_student_profile(agent, state: RecommenderState) -> RecommenderState:
    """Load the student's profile data"""
    # In production, this would fetch from database
    # For now, use data from state
    return state


async def get_available_careers(agent, state: RecommenderState) -> RecommenderState:
    """Get available career worlds to recommend from"""
    # In production, this would query the database
    # For now, we assume this is passed in or would be fetched
    available_careers = state.get("available_stories", [])
    
    if not available_careers:
        # Default careers if none provided
        state["available_stories"] = [
            {"id": "medicine", "title": "Medicine", "category": "Healthcare"},
            {"id": "technology", "title": "Technology", "category": "Tech"},
            {"id": "law", "title": "Law", "category": "Legal"},
            {"id": "engineering", "title": "Engineering", "category": "Engineering"},
            {"id": "education", "title": "Education", "category": "Education"},
            {"id": "arts", "title": "Arts & Design", "category": "Creative"},
            {"id": "finance", "title": "Finance", "category": "Business"},
            {"id": "science", "title": "Science", "category": "Research"},
        ]
    
    return state


async def calculate_relevance_scores(agent, state: RecommenderState) -> RecommenderState:
    """Calculate relevance scores for each career based on student profile"""
    strength_map = state.get("strength_map", {})
    energized_by = state.get("result", {}).get("energized_by", [])
    available_careers = state.get("available_stories", [])
    not_motivated_by = state.get("not_motivated_by", [])
    
    # Career-to-strength mappings
    career_strengths = {
        "medicine": ["empathy", "analytical", "leadership", "communication"],
        "technology": ["technical", "analytical", "autonomy", "creative"],
        "law": ["analytical", "communication", "leadership"],
        "engineering": ["technical", "analytical", "problem_solving"],
        "education": ["empathy", "communication", "leadership"],
        "arts": ["creative", "empathy", "communication"],
        "finance": ["analytical", "autonomy", "leadership"],
        "science": ["analytical", "technical", "autonomy"],
    }
    
    relevance_scores = {}
    
    for career in available_careers:
        career_id = career.get("id", "")
        career_key = career_id.lower().replace(" ", "_")
        
        # Skip if student said "Not For Me" previously
        if career_id in not_motivated_by:
            relevance_scores[career_id] = 0.1  # Very low score
            continue
        
        # Calculate relevance based on strength alignment
        required_strengths = career_strengths.get(career_key, [])
        score = 0.0
        
        for strength in required_strengths:
            strength_value = strength_map.get(strength, 0.5)
            score += strength_value
        
        # Normalize and add energized bonus
        if required_strengths:
            score = score / len(required_strengths)
        
        # Bonus for energized match
        for energized in energized_by:
            if any(s in energized.lower() for s in required_strengths):
                score = min(1.0, score + 0.15)
        
        relevance_scores[career_id] = score
    
    state["relevance_scores"] = relevance_scores
    return state


async def rank_recommendations(agent, state: RecommenderState) -> RecommenderState:
    """Rank careers by relevance and filter by threshold"""
    relevance_scores = state.get("relevance_scores", {})
    available_careers = state.get("available_stories", [])
    
    # Filter by threshold (80%)
    threshold = 0.80
    
    ranked = []
    for career in available_careers:
        career_id = career.get("id", "")
        score = relevance_scores.get(career_id, 0.0)
        
        if score >= threshold:
            # Generate reasoning
            reasoning = _generate_reasoning(career, score, state)
            ranked.append({
                **career,
                "relevance_score": round(score, 2),
                "reason": reasoning,
            })
    
    # Sort by score descending
    ranked.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    state["result"] = state.get("result", {})
    state["result"]["recommendations"] = ranked[:6]  # Top 6
    
    return state


def _generate_reasoning(career: Dict[str, Any], score: float, state: RecommenderState) -> str:
    """Generate human-readable reasoning for recommendation"""
    strength_map = state.get("strength_map", {})
    energized_by = state.get("result", {}).get("energized_by", [])
    
    career_id = career.get("id", "").lower()
    
    # Match strengths to career
    reasoning_parts = []
    
    for strength, value in strength_map.items():
        if value >= 0.6:
            if strength in ["empathy", "communication"] and career_id in ["medicine", "education", "arts"]:
                reasoning_parts.append(f"strong {strength}")
            elif strength in ["analytical", "technical"] and career_id in ["technology", "engineering", "science", "finance"]:
                reasoning_parts.append(f"strong {strength}")
    
    if reasoning_parts:
        return f"Matches your {reasoning_parts[0]} and more"
    
    return "Aligned with your profile"


async def apply_data_flywheel(agent, state: RecommenderState) -> RecommenderState:
    """Apply data flywheel logic to adjust recommendations"""
    not_motivated_by = state.get("not_motivated_by", [])
    
    # In production, this would query historical data:
    # "For students with similar strength maps, which careers got 'Not For Me'?"
    # Then reduce their scores
    
    # For now, just log the data flywheel consideration
    if not_motivated_by:
        logger.info(f"Data flywheel: Student not motivated by {not_motivated_by}")
    
    return state


class RecommenderAgent:
    """LangGraph agent for recommending careers based on student profile"""
    
    def __init__(self):
        self.name = "Recommender Agent"
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph = StateGraph(RecommenderState)
        
        # Add nodes
        graph.add_node("load_profile", load_student_profile)
        graph.add_node("get_careers", get_available_careers)
        graph.add_node("calculate_scores", calculate_relevance_scores)
        graph.add_node("rank_recommendations", rank_recommendations)
        graph.add_node("apply_flywheel", apply_data_flywheel)
        
        # Define edges
        graph.set_entry_point("load_profile")
        graph.add_edge("load_profile", "get_careers")
        graph.add_edge("get_careers", "calculate_scores")
        graph.add_edge("calculate_scores", "apply_flywheel")
        graph.add_edge("apply_flywheel", "rank_recommendations")
        graph.add_edge("rank_recommendations", END)
        
        self.graph = graph.compile()
    
    async def run(
        self,
        strength_map: Dict[str, float],
        energized_by: List[str] = None,
        not_motivated_by: List[str] = None,
        available_stories: List[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate career recommendations for a student.
        
        Args:
            strength_map: Student's strength map
            energized_by: What energizes the student
            not_motivated_by: Careers student said "Not For Me" to
            available_stories: Available career worlds to recommend
            
        Returns:
            Ranked list of career recommendations
        """
        initial_state: RecommenderState = {
            **get_default_state(),
            "strength_map": strength_map,
            "result": {"energized_by": energized_by or []},
            "not_motivated_by": not_motivated_by or [],
            "available_stories": available_stories or [],
        }
        
        result = await self.graph.ainvoke(initial_state)
        
        return result.get("result", {}).get("recommendations", [])


# Singleton instance
recommender_agent = RecommenderAgent()


async def recommend_careers(
    strength_map: Dict[str, float],
    energized_by: List[str] = None,
    not_motivated_by: List[str] = None,
    available_stories: List[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Convenience function to get career recommendations"""
    return await recommender_agent.run(
        strength_map=strength_map,
        energized_by=energized_by,
        not_motivated_by=not_motivated_by,
        available_stories=available_stories,
    )