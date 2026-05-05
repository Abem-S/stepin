"""Diary Extraction Agent - LangGraph implementation"""
import json
import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.agents.state import DiaryExtractionState, get_default_state
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Diary Extraction Agent for StepIn platform.

Your role is to transform raw voice conversation transcripts into structured diary entries.
You analyze the conversation to extract:
1. Key moments from the day (specific events, decisions, interactions)
2. Emotional beats (how the professional felt throughout)
3. Decisions faced (dilemmas, trade-offs, choices made)
4. Lessons learned (insights, wisdom gained)

Guidelines:
- Extract 3-5 key moments that define the day's narrative
- Identify the emotional journey (fear, joy, frustration, pride, doubt, etc.)
- Note any decision points where the professional had to choose
- Capture authentic lessons in the professional's voice
- Be specific - use real dialogue, times, and details from the transcript"""


async def extract_key_moments(agent, state: DiaryExtractionState) -> DiaryExtractionState:
    """Extract key moments from the transcript"""
    transcript = state.get("raw_transcript", "")
    
    prompt = f"""Extract the key moments from this voice transcript:

{transcript}

Return a JSON array of key moments, each with:
- "time": approximate time of day (e.g., "9:00 AM")
- "event": what happened (brief description)
- "emotional_context": how the professional felt

Example:
[
  {{"time": "7:00 AM", "event": "Team standup meeting", "emotional_context": "anxious"}},
  {{"time": "2:00 PM", "event": "Client presentation", "emotional_context": "confident"}}
]"""

    try:
        result = await gemini_service.generate_json(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.5,
        )
        state["extracted_content"] = state.get("extracted_content", {})
        state["extracted_content"]["key_moments"] = result if isinstance(result, list) else []
    except Exception as e:
        logger.error(f"Error extracting key moments: {e}")
        state["error"] = str(e)
    
    return state


async def extract_emotional_beats(agent, state: DiaryExtractionState) -> DiaryExtractionState:
    """Extract emotional journey from the transcript"""
    transcript = state.get("raw_transcript", "")
    
    prompt = f"""Analyze the emotional journey from this voice transcript:

{transcript}

Identify the emotional beats - how the professional's mood changed throughout the conversation.
Return a JSON array of emotional states:

[
  {{"emotion": "fear", "when": "early in the conversation", "cause": "uncertainty about a decision"}},
  {{"emotion": "pride", "when": "later in the conversation", "cause": "successfully completing a task"}}
]"""

    try:
        result = await gemini_service.generate_json(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.5,
        )
        state["extracted_content"] = state.get("extracted_content", {})
        state["extracted_content"]["emotional_beats"] = result if isinstance(result, list) else []
    except Exception as e:
        logger.error(f"Error extracting emotional beats: {e}")
    
    return state


async def extract_decisions(agent, state: DiaryExtractionState) -> DiaryExtractionState:
    """Extract decision points from the transcript"""
    transcript = state.get("raw_transcript", "")
    
    prompt = f"""Identify the key decisions and dilemmas from this voice transcript:

{transcript}

Return JSON array of decisions faced:
[
  {{"decision": "Whether to speak up in the meeting", "options": ["speak up", "stay quiet"], "what_they_chose": "speak up"}},
  {{"decision": "How to handle the difficult client", "options": ["empathize", "be direct"], "what_they_chose": "empathize"}}
]"""

    try:
        result = await gemini_service.generate_json(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.5,
        )
        state["extracted_content"] = state.get("extracted_content", {})
        state["extracted_content"]["decisions"] = result if isinstance(result, list) else []
    except Exception as e:
        logger.error(f"Error extracting decisions: {e}")
    
    return state


async def extract_lessons(agent, state: DiaryExtractionState) -> DiaryExtractionState:
    """Extract lessons learned from the transcript"""
    transcript = state.get("raw_transcript", "")
    
    prompt = f"""Extract the lessons and insights from this voice transcript:

{transcript}

Return JSON array of lessons:
[
  {{"lesson": "Medicine is about showing up when it matters most", "context": "after a challenging surgery"}},
  {{"lesson": "Feedback is a gift, even when it hurts", "context": "after a difficult code review"}}
]"""

    try:
        result = await gemini_service.generate_json(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.5,
        )
        state["extracted_content"] = state.get("extracted_content", {})
        state["extracted_content"]["lessons"] = result if isinstance(result, list) else []
    except Exception as e:
        logger.error(f"Error extracting lessons: {e}")
    
    return state


async def compile_diary_entry(agent, state: DiaryExtractionState) -> DiaryExtractionState:
    """Compile all extracted content into the final diary entry"""
    extracted = state.get("extracted_content", {})
    
    diary_entry = {
        "key_moments": extracted.get("key_moments", []),
        "emotional_beats": extracted.get("emotional_beats", []),
        "decisions": extracted.get("decisions", []),
        "lessons": extracted.get("lessons", []),
    }
    
    # Generate a summary
    prompt = f"""Create a one-sentence summary of this diary entry:

Key moments: {diary_entry['key_moments']}
Emotional journey: {diary_entry['emotional_beats']}
Lessons: {diary_entry['lessons']}

Just return the summary sentence."""

    try:
        summary = await gemini_service.generate_content(
            prompt=prompt,
            model="gemini-2.5-flash",
            temperature=0.5,
        )
        diary_entry["summary"] = summary
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        diary_entry["summary"] = "A day of growth and reflection in the professional's journey."
    
    state["diary_entry"] = diary_entry
    return state


class DiaryExtractionAgent:
    """LangGraph agent for extracting structured diary entries from voice transcripts"""
    
    def __init__(self):
        self.name = "Diary Extraction Agent"
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph = StateGraph(DiaryExtractionState)
        
        # Add nodes
        graph.add_node("extract_moments", extract_key_moments)
        graph.add_node("extract_emotions", extract_emotional_beats)
        graph.add_node("extract_decisions", extract_decisions)
        graph.add_node("extract_lessons", extract_lessons)
        graph.add_node("compile_entry", compile_diary_entry)
        
        # Define edges
        graph.set_entry_point("extract_moments")
        graph.add_edge("extract_moments", "extract_emotions")
        graph.add_edge("extract_emotions", "extract_decisions")
        graph.add_edge("extract_decisions", "extract_lessons")
        graph.add_edge("extract_lessons", "compile_entry")
        graph.add_edge("compile_entry", END)
        
        self.graph = graph.compile()
    
    async def run(self, transcript: str, professional_id: str) -> Dict[str, Any]:
        """
        Extract structured diary entry from transcript.
        
        Args:
            transcript: Raw voice conversation transcript
            professional_id: ID of the professional whose diary this is
            
        Returns:
            Structured diary entry dictionary
        """
        initial_state: DiaryExtractionState = {
            **get_default_state(),
            "raw_transcript": transcript,
            "professional_id": professional_id,
        }
        
        result = await self.graph.ainvoke(initial_state)
        return result.get("diary_entry", {})


# Singleton instance
diary_extraction_agent = DiaryExtractionAgent()


async def extract_diary_entry(transcript: str, professional_id: str) -> Dict[str, Any]:
    """Convenience function to extract diary entry"""
    return await diary_extraction_agent.run(transcript, professional_id)