"""
Digital Twin Service - AI-powered conversation with professionals

This service uses Gemini to simulate conversation with a professional,
using their interview and career world as knowledge base.
"""

import json
import logging
from typing import List, Dict, Any, Optional

from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class DigitalTwinService:
    """
    Manages conversations with AI Digital Twins of professionals
    
    Uses the professional's interview responses and Career World as knowledge base.
    """
    
    def __init__(self):
        # Store knowledge bases for each professional
        self.knowledge_bases: Dict[str, Dict[str, Any]] = {}
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
    
    def set_knowledge_base(self, professional_id: str, knowledge_base: Dict[str, Any]):
        """Set the knowledge base for a professional"""
        self.knowledge_bases[professional_id] = knowledge_base
        logger.info(f"Knowledge base set for professional {professional_id}")
    
    def get_knowledge_base(self, professional_id: str) -> Optional[Dict[str, Any]]:
        """Get the knowledge base for a professional"""
        return self.knowledge_bases.get(professional_id)
    
    def generate_system_prompt(self, professional_id: str) -> str:
        """Generate system prompt from knowledge base"""
        kb = self.get_knowledge_base(professional_id)
        
        if not kb:
            return """You are a professional on the StepIn platform. Answer questions about your career journey."""
        
        name = kb.get("professional_name", "the professional")
        career = kb.get("career_title", "their career")
        years = kb.get("years_experience", "several")
        
        # Build context from interview
        moments = kb.get("moments", [])
        moments_text = ""
        if moments:
            moments_text = "KEY CAREER MOMENTS FROM MY JOURNEY:\n"
            for m in moments[:3]:  # Include top 3 moments
                lines = m.get("text_lines", [])
                if lines:
                    moments_text += f"- {lines[0]}\n"
        
        # Build from voice clips/answers
        voice_clips = kb.get("voice_clip_responses", {})
        answers_text = ""
        if voice_clips:
            answers_text = "ANSWERS TO KEY QUESTIONS:\n"
            for key, answer in voice_clips.items():
                answers_text += f"- {key}: {answer[:200]}...\n"
        
        prompt = f"""You are a Digital Twin of {name}, a {career} with {years} of experience.

ABOUT YOUR JOURNEY:
{answers_text}

KEY MOMENTS:
{moments_text}

HOW TO RESPOND:
- Answer as {name} would, based on their actual career journey
- Be warm, authentic, and honest - share both positives and challenges
- Reference specific moments from your journey when relevant
- Keep responses conversational (50-150 words)
- If asked about topics not covered, say so honestly
- End with a follow-up question to keep conversation engaging

You have real knowledge from your interview - use it to provide authentic, specific answers."""
        
        return prompt
    
    async def start_conversation(
        self,
        professional_id: str,
        student_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Start a new Digital Twin conversation"""
        self.conversations[professional_id] = []
        
        # Get knowledge base
        kb = self.get_knowledge_base(professional_id)
        
        # Generate contextual opening
        if student_context and kb:
            opening = await self._generate_contextual_opening(kb, student_context)
        elif kb:
            opening = await self._generate_standard_opening(kb)
        else:
            opening = "Hi! I'm the Digital Twin of this professional. I'd love to share my career journey with you. What would you like to know?"
        
        self.conversations[professional_id].append({
            "role": "assistant",
            "content": opening,
        })
        
        return opening
    
    async def _generate_contextual_opening(
        self,
        kb: Dict[str, Any],
        student_context: Dict[str, Any],
    ) -> str:
        """Generate opening based on student's Shadow Day experience"""
        name = kb.get("professional_name", "I")
        career = kb.get("career_title", "")
        
        energized = student_context.get("energized_by", [])
        drained = student_context.get("drained_by", [])
        
        prompt = f"""Generate a warm, personalized opening message from {name}'s Digital Twin.

CONTEXT: The student just completed a Shadow Day in {career} and experienced:
- What energized them: {', '.join(energized[:2]) if energized else 'various aspects'}
- What drained them: {', '.join(drained[:2]) if drained else 'certain challenges'}

Write 2-3 sentences that:
1. Acknowledge their experience in my career world
2. Offer to answer their real questions about what it's actually like
3. Invite them to ask anything

Keep it conversational and genuine. Don't be too long."""
        
        try:
            return await gemini_service.generate_content(
                prompt=prompt,
                model="gemini-2.5-pro",
                temperature=0.7,
                max_output_tokens=150,
            )
        except Exception as e:
            logger.error(f"Error generating opening: {e}")
            return f"Hi! I heard you explored my career world. I'm curious - what surprised you most? I'd love to share what it's really like to work in {career}."
    
    async def _generate_standard_opening(self, kb: Dict[str, Any]) -> str:
        """Generate standard opening"""
        name = kb.get("professional_name", "I")
        career = kb.get("career_title", "this field")
        
        return f"Hi! I'm the Digital Twin of {name}. I shared my career journey through the Shadow Day experience, and now I'd love to answer any questions you have about what it's really like to work in {career}. What would you like to know?"
    
    async def send_message(
        self,
        professional_id: str,
        message: str,
    ) -> str:
        """Send a message and get response from Digital Twin"""
        conversation = self.conversations.get(professional_id, [])
        kb = self.get_knowledge_base(professional_id)
        
        # Add user message
        conversation.append({"role": "user", "content": message})
        
        # Build context for response
        system_prompt = self.generate_system_prompt(professional_id)
        
        # Format conversation history
        history_text = ""
        for msg in conversation[:-1]:
            history_text += f"{msg['role'].upper()}: {msg['content']}\n"
        
        prompt = f"""CONVERSATION HISTORY:
{history_text}

LATEST MESSAGE FROM STUDENT:
{message}

Respond as the professional would, using knowledge from their interview. Keep it conversational and authentic."""

        try:
            response = await gemini_service.generate_content(
                prompt=prompt,
                model="gemini-2.5-pro",
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=200,
            )
            
            conversation.append({"role": "assistant", "content": response})
            self.conversations[professional_id] = conversation
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'd love to share more about my journey. What would you like to know?"
    
    def get_conversation_history(self, professional_id: str) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversations.get(professional_id, [])
    
    def clear_conversation(self, professional_id: str):
        """Clear conversation history"""
        if professional_id in self.conversations:
            del self.conversations[professional_id]


# Singleton
digital_twin_service = DigitalTwinService()


# Convenience functions

def set_professional_knowledge_base(
    professional_id: str,
    career_world: Dict[str, Any],
    interview_responses: Dict[str, str],
):
    """Set knowledge base from Career World and interview"""
    digital_twin_service.set_knowledge_base(professional_id, {
        "professional_name": career_world.get("professional_name", "Professional"),
        "career_title": career_world.get("career_title", "Professional"),
        "years_experience": career_world.get("years_experience", ""),
        "category": career_world.get("category", ""),
        "moments": career_world.get("moments", []),
        "voice_clip_responses": interview_responses,
    })


async def start_digital_twin(
    professional_id: str,
    student_context: Optional[Dict[str, Any]] = None,
) -> str:
    """Start a Digital Twin conversation"""
    return await digital_twin_service.start_conversation(
        professional_id=professional_id,
        student_context=student_context,
    )


async def chat_with_digital_twin(
    professional_id: str,
    message: str,
) -> str:
    """Chat with a Digital Twin"""
    return await digital_twin_service.send_message(
        professional_id=professional_id,
        message=message,
    )


def get_digital_twin_history(professional_id: str) -> List[Dict[str, str]]:
    """Get conversation history"""
    return digital_twin_service.get_conversation_history(professional_id)
# Wrapper functions for route compatibility
def start_digital_twin_conversation(
    professional_id: str,
    professional_data: Dict[str, Any],
    student_context: Optional[Dict[str, Any]] = None,
) -> str:
    """Start a Digital Twin conversation (sync wrapper for routes)"""
    import asyncio
    
    # Set knowledge base if provided
    if professional_data:
        digital_twin_service.set_knowledge_base(professional_id, {
            "professional_name": professional_data.get("name", "Professional"),
            "career_title": professional_data.get("career_title", "Professional"),
            "years_experience": professional_data.get("years_experience", ""),
            "category": "",
            "moments": [],
            "voice_clip_responses": {},
        })
    
    try:
        # Try to get existing loop or create new one
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we need to schedule the coroutine
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, start_digital_twin(
                    professional_id=professional_id,
                    student_context=student_context,
                ))
                return future.result()
        except RuntimeError:
            # No running loop, can use asyncio.run directly
            return asyncio.run(start_digital_twin(
                professional_id=professional_id,
                student_context=student_context,
            ))
    except Exception as e:
        logger.error(f"Error starting digital twin: {e}")
        return f"Hi! I'm the Digital Twin. I'd love to share my career journey with you. What would you like to know?"


def chat_with_digital_twin(
    professional_id: str,
    message: str,
    professional_data: Optional[Dict[str, Any]] = None,
) -> str:
    """Chat with a Digital Twin (sync wrapper for routes)"""
    import asyncio
    
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, digital_twin_service.send_message(
                    professional_id=professional_id,
                    message=message,
                ))
                return future.result()
        except RuntimeError:
            return asyncio.run(digital_twin_service.send_message(
                professional_id=professional_id,
                message=message,
            ))
    except Exception as e:
        logger.error(f"Error in digital twin chat: {e}")
        return "I'd love to share more about my journey. What would you like to know?"


def clear_digital_twin_conversation(professional_id: str):
    """Clear conversation history"""
    digital_twin_service.clear_conversation(professional_id)