"""Agent API routes (Internal)"""
import logging
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

from app.models.agent import (
    NextQuestionRequest,
    NextQuestionResponse,
    WorldBuilderRequest,
    WorldBuilderResponse,
    ScenarioRequest,
    ScenarioResponse,
    ProfileUpdateRequest,
    ProfileUpdateResponse,
    ReflectionRequest,
    ReflectionResponse,
    RecommenderRequest,
    RecommenderResponse,
    ImageGenerationRequest,
    ImageGenerationResponse,
)
from app.services.gemini_service import gemini_service, GeminiServiceError, call_profile_agent, call_reflection_agent, call_scenario_agent, call_recommender_agent

router = APIRouter(prefix="/api/agents", tags=["agents"])

# Interview questions for agents
INTERVIEW_QUESTIONS = [
    {"key": "worst_monday", "question": "What's the worst Monday morning you've had in this career?"},
    {"key": "advice_at_20", "question": "What advice would you give yourself at 20?"},
    {"key": "almost_quit", "question": "What's a moment that almost made you quit?"},
    {"key": "best_day", "question": "Describe the best day feeling in this career."},
    {"key": "unspoken_truth", "question": "What's an unspoken truth about this career?"},
]


@router.post("/interview/next-question", response_model=NextQuestionResponse)
async def get_next_interview_question(data: NextQuestionRequest):
    """Get next interview question"""
    if data.question_index >= len(INTERVIEW_QUESTIONS):
        return NextQuestionResponse(
            question="",
            question_key="",
            is_final=True,
        )
    
    q = INTERVIEW_QUESTIONS[data.question_index]
    return NextQuestionResponse(
        question=q["question"],
        question_key=q["key"],
        is_final=data.question_index == len(INTERVIEW_QUESTIONS) - 1,
    )


@router.post("/world-builder", response_model=WorldBuilderResponse)
async def build_career_world(data: WorldBuilderRequest):
    """Generate Career World JSON (stub - would use AI agent)"""
    # Mock response - in production uses World Builder Agent
    return WorldBuilderResponse(
        career_world_json={
            "category": "technology",
            "title": "Startup Engineer's Launch Day",
            "key_moments": [
                {"index": 0, "title": "Critical Bug Discovery", "situation": "2 hours before launch"},
                {"index": 1, "title": "Team Conflict", "situation": "Different opinions on the fix"},
                {"index": 2, "title": "Ship vs Delay Decision", "situation": "Must choose now"},
                {"index": 3, "title": "Post-Launch Crisis", "situation": "Production issues"},
                {"index": 4, "title": "Late Night Retrospective", "situation": "Learning moment"},
            ],
            "emotional_beats": [
                {"moment": 0, "emotion": "panic"},
                {"moment": 1, "emotion": "frustration"},
                {"moment": 2, "emotion": "pressure"},
                {"moment": 3, "emotion": "adrenaline"},
                {"moment": 4, "emotion": "reflection"},
            ],
            "decision_points": [
                {"moment": 2, "choice_a": "Ship anyway", "choice_b": "Delay launch"},
            ],
            "voice_clip_refs": ["worst_monday", "best_day"],
        },
        digital_twin_kb={
            "professional_name": "Alex Rivera",
            "communication_style": "direct and practical",
            "values": ["teamwork", "transparency", "continuous_learning"],
            "key_stories": [],
        },
        is_complete=True,
    )


@router.post("/scenario", response_model=ScenarioResponse)
async def generate_next_scenario(data: ScenarioRequest):
    """Generate next scenario moment using Scenario Agent (AI-powered)"""
    try:
        # Create career world context for the AI
        career_world = {
            "career_name": "Medical Professional",
            "category": "medicine",
            "title": "A Day in the Life of a Doctor"
        }
        
        # Call the real Scenario Agent
        result = await call_scenario_agent(
            scenario_context=f"Moment {data.current_moment_index + 1} of the Shadow Day experience",
            previous_choices=[{"choice": data.student_choice, "free_text": data.student_free_text}] if data.student_choice is not None else [],
            career_world=career_world,
        )
        
        return ScenarioResponse(
            next_moment_index=data.current_moment_index + 1,
            text_lines=result.get("text_lines", ["The moment unfolds..."]),
            image_url=None,
            audio_url=None,
            choices=[c.get("text", "") for c in result.get("choices", [])][:4],
            is_emotional_peak=result.get("is_emotional_peak", False),
            voice_clip_url=result.get("voice_clip_url"),
            pull_quote=result.get("pull_quote"),
        )
    except Exception as e:
        # Fallback to mock response if AI fails
        next_index = data.current_moment_index + 1
        is_peak = next_index in [2, 4]
        
        return ScenarioResponse(
            next_moment_index=next_index,
            text_lines=[
                f"Moment {next_index + 1} begins...",
                "The situation unfolds in front of you.",
                "What will you do?",
            ],
            image_url=None,
            audio_url=None,
            choices=[
                "Take charge and act",
                "Seek advice from others",
                "Take a step back",
                "Something different...",
            ],
            is_emotional_peak=is_peak,
            voice_clip_url=None,
            pull_quote="This is a defining moment..." if is_peak else None,
        )


@router.post("/profile", response_model=ProfileUpdateResponse)
async def update_student_profile(data: ProfileUpdateRequest):
    """Update student profile using Profile Agent (AI-powered)"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[PROFILE AGENT] Called with {len(data.choices)} choices")
    
    try:
        # Call the real Profile Agent
        logger.info("[PROFILE AGENT] Calling AI...")
        result = await call_profile_agent(
            choices=data.choices,
            free_text_responses=data.free_text_responses,
            hesitations_ms=data.hesitations_ms,
        )
        logger.info(f"[PROFILE AGENT] AI returned: {result}")
        
        profile_data = {
            "energized_by": result.get("energized_by", []),
            "drained_by": result.get("drained_by", []),
            "choices_reveal": result.get("choices_reveal", []),
            "decision_patterns": result.get("decision_patterns", {}),
        }

        # Persist to Supabase (upsert so it updates on repeat sessions)
        try:
            from app.database import get_supabase_client
            supabase = get_supabase_client()
            supabase.table("student_strengths").upsert({
                "student_id": data.student_id,
                "strength_map": profile_data,
            }, on_conflict="student_id").execute()
            logger.info(f"[PROFILE AGENT] Saved profile for student {data.student_id}")
        except Exception as db_err:
            logger.warning(f"[PROFILE AGENT] DB save failed (non-fatal): {db_err}")
        
        return ProfileUpdateResponse(
            student_id=data.student_id,
            profile_updated=True,
            energized_by=profile_data["energized_by"],
            drained_by=profile_data["drained_by"],
        )
    except Exception as e:
        logger.error(f"[PROFILE AGENT] Error: {e}")
        avg_hesitation = sum(data.hesitations_ms) / len(data.hesitations_ms) if data.hesitations_ms else 0
        energized = ["Thoughtful and deliberate"] if avg_hesitation > 5000 else ["Decisive and action-oriented"]
        drained = ["Uncertainty and ambiguity"]
        return ProfileUpdateResponse(
            student_id=data.student_id,
            profile_updated=True,
            energized_by=energized,
            drained_by=drained,
        )


@router.post("/reflection", response_model=ReflectionResponse)
async def generate_career_dna(data: ReflectionRequest):
    """Generate Career DNA using Reflection Agent (AI-powered)"""
    try:
        from app.database import get_supabase_client
        supabase = get_supabase_client()
        stories = supabase.table("story_experiences").select("title,category").eq("is_published", True).execute()
        available_careers = [f"{row['title']} ({row['category']})" for row in stories.data] if stories.data else []
        
        # Call the real Reflection Agent
        result = await call_reflection_agent(
            student_profile=data.profile_data,
            career_name=data.profile_data.get("career_name", "Professional"),
            choices=data.profile_data.get("choices", []),
            available_careers=available_careers,
        )
        
        # Save DNA to in-memory store so dashboard can fetch it
        from app.routes.student import save_student_dna
        save_student_dna(data.student_id, result)

        return ReflectionResponse(
            energized_by=result.get("energized_by", []),
            drained_by=result.get("drained_by", []),
            choices_reveal=result.get("choices_reveal", []),
            recommendations=result.get("recommendations", []),
            career_dna_card_data=result,
        )
    except Exception as e:
        # Fallback to mock response
        return ReflectionResponse(
            energized_by=[
                "Creative problem-solving",
                "Making an impact on others",
                "Learning and growing",
            ],
            drained_by=[
                "Micromanagement",
                "Bureaucratic obstacles",
                "Lack of purpose",
            ],
            choices_reveal=[
                "You prioritize outcomes over process",
                "You value meaningful work",
                "You take calculated risks",
            ],
            recommendations=[
                {
                    "career_name": "Product Design",
                    "category": "Technology",
                    "reason": "Your creative and impact-driven nature fits well",
                },
                {
                    "career_name": "UX Research",
                    "category": "Technology",
                    "reason": "Your analytical skills are strong",
                },
            ],
            career_dna_card_data={
                "energized_by": ["Creative problem-solving", "Making an impact on others"],
                "drained_by": ["Micromanagement", "Bureaucracy"],
                "choices_reveal": ["You prioritize outcomes over process"],
            },
        )


@router.post("/recommender", response_model=RecommenderResponse)
async def get_recommendations(data: RecommenderRequest):
    """Get career recommendations using Recommender Agent (AI-powered)"""
    try:
        from app.database import get_supabase_client
        supabase = get_supabase_client()

        profile_data = data.profile_data or {}
        if data.student_id and not profile_data:
            try:
                profile_resp = supabase.table("student_strengths").select("strength_map").eq("student_id", data.student_id).execute()
                if profile_resp.data:
                    profile_data = profile_resp.data[0].get("strength_map", {})
            except Exception:
                pass

        available_worlds = []
        try:
            stories_resp = supabase.table("story_experiences").select("id,title,category").eq("is_published", True).execute()
            available_worlds = [{"id": row["id"], "career_name": row["title"], "category": row["category"]} for row in stories_resp.data]
        except Exception:
            pass

        result = await call_recommender_agent(
            student_profile=profile_data,
            available_career_worlds=available_worlds,
            not_motivated_by=data.not_motivated_by,
        )
        recommendations = result.get("recommendations", [])
        return RecommenderResponse(
            recommendations=recommendations,
            relevance_scores=[r.get("relevance_score", 0) for r in recommendations],
            not_motivated_by=data.not_motivated_by,
        )
    except Exception as e:
        logger.error(f"[RECOMMENDER] Error: {e}")
        return RecommenderResponse(recommendations=[], relevance_scores=[])
@router.post("/image/generate", response_model=ImageGenerationResponse)
async def generate_image(data: ImageGenerationRequest):
    """
    Generate an atmospheric image for a scenario moment.
    This endpoint is used for pre-generating images in the background.
    """
    try:
        # Call Gemini image generation
        image_data = await gemini_service.generate_image(
            prompt=data.prompt,
        )
        
        # Return base64 encoded image
        import base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        return ImageGenerationResponse(
            image_data=image_b64,
            success=True,
            prompt=data.prompt,
        )
    except Exception as e:
        # Return fallback on error
        return ImageGenerationResponse(
            image_data=None,
            success=False,
            prompt=data.prompt,
            error=str(e),
        )