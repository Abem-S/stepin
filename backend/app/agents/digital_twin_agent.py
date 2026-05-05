"""Digital Twin Agent - LangGraph implementation with RAG for voice conversations"""
import json
import logging
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END

from app.agents.state import DigitalTwinState, get_default_state
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Digital Twin of a professional on the StepIn platform.

Your role is to answer questions from students about careers based on the professional's 
diary entries and story experiences. You embody their communication style and values.

Guidelines:
- Respond in a manner consistent with the professional's voice
- Be authentic about both positives and challenges in the career
- Use knowledge from diary entries to provide specific examples
- If asked about topics not covered, be honest
- Keep responses conversational (2-4 sentences)
- Reference your own experiences when relevant"""


async def retrieve_rag_context(agent, state: DigitalTwinState) -> DigitalTwinState:
    """Retrieve relevant context from diary entries using RAG"""
    # In production, this would query the RAG system (pgvector)
    # For now, we'll simulate with stored context
    
    professional_context = state.get("professional_context", {})
    user_message = state.get("user_message", "")
    
    # Simulate RAG retrieval - in production, this would be a vector search
    retrieved_entries = []
    
    # Get diary entries from the professional
    diary_entries = professional_context.get("diary_entries", [])
    
    # Simple keyword-based retrieval (production would use embeddings)
    user_keywords = user_message.lower().split()
    
    for entry in diary_entries:
        entry_text = json.dumps(entry).lower()
        # Check for keyword matches
        if any(kw in entry_text for kw in user_keywords if len(kw) > 3):
            retrieved_entries.append(entry)
    
    # If no keyword matches, return recent entries
    if not retrieved_entries:
        retrieved_entries = diary_entries[:2]  # Get 2 most recent
    
    state["retrieved_diary_entries"] = retrieved_entries
    
    # Build RAG context string
    context_parts = []
    for entry in retrieved_entries:
        summary = entry.get("summary", "")
        content = entry.get("content", {})
        key_moments = content.get("key_moments", [])
        
        context_parts.append(f"- {summary}")
        for moment in key_moments[:2]:  # Top 2 moments per entry
            context_parts.append(f"  • {moment.get('event', '')}")
    
    state["rag_context"] = context_parts
    
    return state


async def generate_response(agent, state: DigitalTwinState) -> DigitalTwinState:
    """Generate the Digital Twin's response"""
    user_message = state.get("user_message", "")
    professional_context = state.get("professional_context", {})
    rag_context = state.get("rag_context", [])
    conversation_history = state.get("conversation_history", [])
    
    # Build the prompt with RAG context
    context_str = "\n".join(rag_context) if rag_context else "No specific diary entries match this question."
    
    professional_name = professional_context.get("name", "the professional")
    profession = professional_context.get("profession", "")
    
    prompt = f"""You are {professional_name}, a {profession}.

STUDENT QUESTION: {user_message}

RELEVANT EXPERIENCES FROM YOUR JOURNEY:
{context_str}

CONVERSATION HISTORY:
{json.dumps(conversation_history[-4:] if len(conversation_history) > 4 else conversation_history)}

Respond as {professional_name} would. Be personal, authentic, and reference your own experiences when relevant. Keep it conversational - 2-4 sentences."""

    try:
        response = await gemini_service.generate_content(
            prompt=prompt,
            model="gemini-2.5-pro",
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
            max_output_tokens=256,
        )
        
        state["result"] = state.get("result", {})
        state["result"]["response"] = response
        
    except Exception as e:
        logger.error(f"Error generating Digital Twin response: {e}")
        # Fallback response
        state["result"] = state.get("result", {})
        state["result"]["response"] = (
            f"I'm glad you're curious about what it's like to work as a {profession}. "
            f"My journey has been challenging but incredibly rewarding. "
            f"What specific aspect would you like to know more about?"
        )
    
    return state


async def update_conversation_history(agent, state: DigitalTwinState) -> DigitalTwinState:
    """Update conversation history with the new exchange"""
    user_message = state.get("user_message", "")
    response = state.get("result", {}).get("response", "")
    
    conversation_history = state.get("conversation_history", [])
    conversation_history.append({"role": "student", "content": user_message})
    conversation_history.append({"role": "professional", "content": response})
    
    # Keep only last 10 messages for context window
    state["conversation_history"] = conversation_history[-10:]
    
    return state


async def check_conversation_end(agent, state: DigitalTwinState) -> DigitalTwinState:
    """Check if the conversation should end or continue"""
    # In production, this might check for goodbye keywords or session timeout
    
    # For now, always allow continuation
    state["result"] = state.get("result", {})
    state["result"]["should_continue"] = True
    
    return state


class DigitalTwinAgent:
    """LangGraph agent for Digital Twin conversations with RAG"""
    
    def __init__(self):
        self.name = "Digital Twin Agent"
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph = StateGraph(DigitalTwinState)
        
        # Add nodes
        graph.add_node("retrieve_context", retrieve_rag_context)
        graph.add_node("generate_response", generate_response)
        graph.add_node("update_history", update_conversation_history)
        graph.add_node("check_end", check_conversation_end)
        
        # Define edges
        graph.set_entry_point("retrieve_context")
        graph.add_edge("retrieve_context", "generate_response")
        graph.add_edge("generate_response", "update_history")
        graph.add_edge("update_history", "check_end")
        graph.add_edge("check_end", END)
        
        self.graph = graph.compile()
    
    async def run(
        self,
        user_message: str,
        professional_context: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a Digital Twin response.
        
        Args:
            user_message: The student's question/message
            professional_context: Professional's profile and diary entries
            conversation_history: Previous messages in the conversation
            
        Returns:
            Response from the Digital Twin
        """
        initial_state: DigitalTwinState = {
            **get_default_state(),
            "user_message": user_message,
            "professional_context": professional_context,
            "conversation_history": conversation_history or [],
        }
        
        result = await self.graph.ainvoke(initial_state)
        
        return {
            "response": result.get("result", {}).get("response", ""),
            "should_continue": result.get("result", {}).get("should_continue", True),
            "conversation_history": result.get("conversation_history", []),
        }


# Singleton instance
digital_twin_agent = DigitalTwinAgent()


async def get_digital_twin_response(
    user_message: str,
    professional_context: Dict[str, Any],
    conversation_history: List[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Convenience function to get Digital Twin response"""
    return await digital_twin_agent.run(
        user_message=user_message,
        professional_context=professional_context,
        conversation_history=conversation_history,
    )