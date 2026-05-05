"""
Interview Agent - Uses Gemini Live Audio for real-time voice conversation

This agent conducts the professional onboarding interview via voice.
It uses Gemini's native audio capabilities for audio-in, audio-out conversation.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any, List
from enum import Enum

from google import genai
from google.genai import types
import asyncio

logger = logging.getLogger(__name__)

# Gemini Live Audio model
GEMINI_LIVE_MODEL = "gemini-2.5-flash-preview-native-audio-12-2025"


class InterviewStage(str, Enum):
    """Stages of the interview conversation"""
    GREETING = "greeting"
    QUESTION = "question"
    LISTENING = "listening"
    FOLLOW_UP = "follow_up"
    CLOSING = "closing"


# Interview questions that the AI will ask
INTERVIEW_QUESTIONS = [
    {
        "key": "worst_monday",
        "question": "Tell me about the worst Monday morning you've had in your career. What happened, and how did you get through it?",
        "follow_up": "That's such a relatable experience. What did you learn from that situation?",
    },
    {
        "key": "advice_at_20",
        "question": "If you could go back and give advice to your 20-year-old self just starting out, what would you say?",
        "follow_up": "That's beautiful advice. Do you think younger people entering the field today appreciate that wisdom?",
    },
    {
        "key": "almost_quit",
        "question": "What's a moment in your career that almost made you quit? What kept you going?",
        "follow_up": "That's a pivotal moment. What specifically helped you push through?",
    },
    {
        "key": "best_day",
        "question": "Describe the best day you've ever had in this career. What made it so special?",
        "follow_up": "What a wonderful memory! What made that day stand out so much?",
    },
    {
        "key": "unspoken_truth",
        "question": "What's an unspoken truth about your career that you wish more people knew?",
        "follow_up": "That's an important insight. Why do you think it's not talked about more?",
    },
]


class InterviewAgent:
    """
    AI Interview Agent using Gemini Live Audio
    
    Conducts professional onboarding through natural voice conversation.
    The AI asks questions, listens to responses, and follows up naturally.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        self.current_question_index = 0
        self.conversation_history: List[Dict[str, str]] = []
        self.is_active = False
        self.system_instruction = """You are conducting a professional interview for StepIn, a career exploration platform.

Your role:
- Have a natural, conversational voice interview with the professional
- Ask one question at a time from the provided list
- Listen actively to their response (they'll speak directly to you)
- Ask follow-up questions that dig deeper into emotionally interesting moments
- Keep responses conversational - you're having a chat, not filling a form
- Never read questions verbatim - make them feel natural
- When they finish answering, acknowledge what they said briefly, then ask the next question
- After 5 questions, thank them warmly and explain next steps

Tone: Warm, curious, empathetic, professional but friendly.
Voice: Natural speaking pace, not rushed.""" 
    
    async def start_interview(self, professional_name: str) -> Dict[str, Any]:
        """Start a new interview session"""
        self.is_active = True
        self.current_question_index = 0
        self.conversation_history = []
        
        # In production, this would set up a LiveKit room for audio transport
        # and connect to Gemini Live API
        
        return {
            "status": "started",
            "professional_name": professional_name,
            "current_question": INTERVIEW_QUESTIONS[0]["question"],
            "question_number": 1,
            "total_questions": len(INTERVIEW_QUESTIONS),
            "instructions": "Speak naturally. The AI will ask you questions and listen to your responses.",
        }
    
    async def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get the current question to ask"""
        if self.current_question_index >= len(INTERVIEW_QUESTIONS):
            return None
        
        return INTERVIEW_QUESTIONS[self.current_question_index]
    
    async def process_response(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Process audio from professional and generate response
        
        In production, this would:
        1. Send audio to Gemini Live API
        2. Get transcribed text
        3. Generate AI response
        4. Convert response to audio
        5. Return audio for playback
        """
        # This is a placeholder - in production, use Live API
        # For now, return mock response
        
        current_q = INTERVIEW_QUESTIONS[self.current_question_index] if self.current_question_index < len(INTERVIEW_QUESTIONS) else None
        
        # Move to next question
        self.current_question_index += 1
        
        return {
            "transcribed": "Professional's response (transcribed from audio)",
            "ai_response": current_q["follow_up"] if current_q else "Thank you for sharing your journey!",
            "next_question": INTERVIEW_QUESTIONS[self.current_question_index]["question"] if self.current_question_index < len(INTERVIEW_QUESTIONS) else None,
            "is_complete": self.current_question_index >= len(INTERVIEW_QUESTIONS),
        }
    
    async def end_interview(self) -> Dict[str, Any]:
        """End the interview and return summary"""
        self.is_active = False
        
        # In production, this would trigger the World Builder Agent
        # to convert all responses to Career World JSON
        
        return {
            "status": "complete",
            "questions_answered": len(INTERVIEW_QUESTIONS),
            "conversation_history": self.conversation_history,
            "next_step": "Building your Career World...",
        }
    
    def get_knowledge_base(self) -> Dict[str, Any]:
        """Get the knowledge base built from the interview"""
        return {
            "professional_name": self.conversation_history[0].get("name", "Professional") if self.conversation_history else "Professional",
            "key_moments": [],
            "values": [],
            "voice_clip_prompts": [],
            "conversation_summary": "\n".join([
                f"Q: {msg.get('question', '')}\nA: {msg.get('answer', '')}"
                for msg in self.conversation_history
            ]),
        }


async def create_interview_session(professional_id: str, professional_name: str) -> InterviewAgent:
    """Create a new interview agent session"""
    # In production, get API key from environment
    import os
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    agent = InterviewAgent(api_key=api_key)
    await agent.start_interview(professional_name)
    
    return agent


# For text-based fallback (testing without audio)
async def generate_question_as_text(professional_id: str, question_key: str) -> str:
    """Generate a question in text form (for testing)"""
    for q in INTERVIEW_QUESTIONS:
        if q["key"] == question_key:
            return q["question"]
    return "Tell me about your career journey."