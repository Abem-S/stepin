"""
Interview API routes
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from app.services.interview_agent import (
    InterviewAgent,
    create_interview_session,
    INTERVIEW_QUESTIONS,
)

from app.services.world_builder_agent import build_career_world_from_interview

# Store active interview sessions
interview_sessions: dict[str, InterviewAgent] = {}

router = APIRouter(prefix="/api/interview", tags=["interview"])


class StartInterviewRequest(BaseModel):
    professional_id: str
    professional_name: str
    career_title: str
    years_experience: int
    category: str


class StartInterviewResponse(BaseModel):
    status: str
    message: str
    current_question: str
    question_number: int
    total_questions: int


class SubmitAnswerRequest(BaseModel):
    professional_id: str
    answer_text: str


class SubmitAnswerResponse(BaseModel):
    next_question: Optional[str]
    follow_up: Optional[str]
    is_complete: bool
    progress: int


class BuildInterviewRequest(BaseModel):
    professional_id: str
    professional_name: str
    career_title: str
    years_experience: int
    category: str
    interview_responses: dict = {}


class BuildWorldResponse(BaseModel):
    career_world_id: str
    status: str
    title: str
    moments_count: int


@router.post("/start", response_model=StartInterviewResponse)
async def start_interview(request: StartInterviewRequest):
    """Start an interview with AI"""
    try:
        agent = await create_interview_session(
            professional_id=request.professional_id,
            professional_name=request.professional_name,
        )
        
        interview_sessions[request.professional_id] = agent
        result = await agent.start_interview(request.professional_name)
        
        return StartInterviewResponse(
            status="started",
            message="Interview started.",
            current_question=result["current_question"],
            question_number=1,
            total_questions=result["total_questions"],
        )
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    """Submit an answer to the current question"""
    try:
        agent = interview_sessions.get(request.professional_id)
        if not agent:
            raise HTTPException(status_code=404, detail="No active interview session")
        
        current_q = await agent.get_current_question()
        if current_q:
            agent.conversation_history.append({
                "question": current_q["question"],
                "answer": request.answer_text,
                "key": current_q["key"],
            })
        
        is_complete = agent.current_question_index >= len(INTERVIEW_QUESTIONS)
        next_q = await agent.get_current_question()
        
        return SubmitAnswerResponse(
            next_question=next_q["question"] if next_q else None,
            follow_up=next_q["follow_up"] if next_q else None,
            is_complete=is_complete,
            progress=agent.current_question_index,
        )
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/build-world", response_model=BuildWorldResponse)
async def build_world(request: BuildInterviewRequest):
    """Build Career World from completed interview"""
    try:
        agent = interview_sessions.get(request.professional_id)
        
        interview_responses = {}
        if agent:
            for item in agent.conversation_history:
                interview_responses[item["key"]] = {
                    "question": item["question"],
                    "answer": item["answer"],
                }
        
        for key, answer in request.interview_responses.items():
            if key not in interview_responses:
                interview_responses[key] = {"question": "", "answer": answer}
        
        career_world = await build_career_world_from_interview(
            professional_name=request.professional_name,
            career_title=request.career_title,
            years_experience=request.years_experience,
            category=request.category,
            interview_responses=interview_responses,
        )
        
        return BuildWorldResponse(
            career_world_id=career_world.get("id", f"world-{request.professional_id}"),
            status="complete",
            title=career_world.get("title", "New Career World"),
            moments_count=len(career_world.get("moments", [])),
        )
    except Exception as e:
        logger.error(f"Error building world: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/questions")
async def get_questions():
    """Get list of interview questions"""
    return {"questions": INTERVIEW_QUESTIONS}