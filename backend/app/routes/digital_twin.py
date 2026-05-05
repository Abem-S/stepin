"""
Digital Twin API routes - AI conversation with professionals
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.digital_twin_service import (
    start_digital_twin_conversation,
    chat_with_digital_twin,
    get_digital_twin_history,
    clear_digital_twin_conversation,
    digital_twin_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/digital-twin", tags=["digital-twin"])


class StudentContext(BaseModel):
    """Context about student's Shadow Day experience"""
    career_name: str
    energized_by: list[str] = []
    drained_by: list[str] = []
    choices: list[str] = []


class StartConversationRequest(BaseModel):
    professional_id: str
    professional_name: str
    career_title: str
    years_experience: int
    values: list[str] = []
    student_context: Optional[StudentContext] = None


class StartConversationResponse(BaseModel):
    professional_id: str
    opening_message: str


class ChatRequest(BaseModel):
    professional_id: str
    message: str
    professional_name: str = ""
    professional_data: Optional[dict] = None


class ChatResponse(BaseModel):
    professional_id: str
    response: str
    conversation_length: int


@router.post("/start", response_model=StartConversationResponse)
async def start_conversation(request: StartConversationRequest):
    """
    Start a new conversation with a professional's Digital Twin
    
    Args:
        request: Professional's basic info including optional student_context
        
    Returns:
        Opening message from the Digital Twin
    """
    try:
        professional_data = {
            "name": request.professional_name,
            "career_title": request.career_title,
            "years_experience": request.years_experience,
            "values": request.values,
        }
        
        # Set knowledge base if provided
        if professional_data:
            digital_twin_service.set_knowledge_base(request.professional_id, {
                "professional_name": professional_data.get("name", "Professional"),
                "career_title": professional_data.get("career_title", "Professional"),
                "years_experience": f"{professional_data.get('years_experience', 0)} years",
                "category": "",
                "moments": [],
                "voice_clip_responses": {},
            })
        
        ctx = request.student_context.dict() if request.student_context else None
        
        opening_message = await digital_twin_service.start_conversation(
            professional_id=request.professional_id,
            student_context=ctx,
        )
        
        return StartConversationResponse(
            professional_id=request.professional_id,
            opening_message=opening_message,
        )
        
    except Exception as e:
        logger.error(f"Error starting Digital Twin conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to a Digital Twin and get response
    """
    try:
        response = await digital_twin_service.send_message(
            professional_id=request.professional_id,
            message=request.message,
        )
        
        history = digital_twin_service.get_conversation_history(request.professional_id)
        
        return ChatResponse(
            professional_id=request.professional_id,
            response=response,
            conversation_length=len(history),
        )
        
    except Exception as e:
        logger.error(f"Error in Digital Twin chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{professional_id}")
async def get_history(professional_id: str):
    """Get conversation history with a Digital Twin"""
    history = get_digital_twin_history(professional_id)
    return {
        "professional_id": professional_id,
        "messages": history,
    }


@router.delete("/history/{professional_id}")
async def clear_history(professional_id: str):
    """Clear conversation history"""
    clear_digital_twin_conversation(professional_id)
    return {"status": "cleared", "professional_id": professional_id}