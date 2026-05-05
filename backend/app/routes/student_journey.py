"""Student Journey API routes"""
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from app.models.student_journey import (
    StudentCreate,
    StudentResponse,
    SessionCreate,
    SessionResponse,
    ChoiceMake,
    MomentResponse,
    RewindAnswer,
)
from app.models.profile import CareerDNACard, ProfileResponse, CareerRecommendation

router = APIRouter(prefix="/api", tags=["student-journey"])

# Mock storage
_mock_students: dict = {}
_mock_sessions: dict = {}
_mock_profiles: dict = {}


@router.post("/students", response_model=StudentResponse, status_code=201)
async def create_student(data: StudentCreate):
    """Create anonymous student"""
    student = StudentResponse(
        id=uuid4(),
        anonymous_identifier=data.anonymous_identifier,
        created_at=datetime.utcnow(),
        last_active_at=datetime.utcnow(),
    )
    _mock_students[str(student.id)] = student.model_dump()
    return student


@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: UUID):
    """Get student by ID"""
    student = _mock_students.get(str(student_id))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student





# Sessions
@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(data: SessionCreate):
    """Start new Shadow Day session"""
    session = SessionResponse(
        id=uuid4(),
        student_id=data.student_id,
        career_world_id=data.career_world_id,
        choices={},
        timing_data={},
        hesitations_ms={},
        rewind_answer=None,
        completed_at=None,
        created_at=datetime.utcnow(),
    )
    _mock_sessions[str(session.id)] = session.model_dump()
    return session


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID):
    """Get session by ID"""
    session = _mock_sessions.get(str(session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/sessions/{session_id}/choice")
async def submit_choice(session_id: UUID, data: ChoiceMake):
    """Submit choice for current moment"""
    session = _mock_sessions.get(str(session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Store the choice
    if "choices" not in session:
        session["choices"] = {}
    session["choices"][str(data.moment_index)] = {
        "choice_index": data.choice_index,
        "free_text": data.free_text,
        "hesitation_ms": data.hesitation_ms,
    }
    
    _mock_sessions[str(session_id)] = session
    
    return {"success": True, "session_id": str(session_id)}


@router.get("/sessions/{session_id}/moment/{moment_index}", response_model=MomentResponse)
async def get_moment(session_id: UUID, moment_index: int):
    """Get scenario moment"""
    # Mock moment data - in production loads from career world
    is_peak = moment_index in [2, 4]
    
    return MomentResponse(
        moment_index=moment_index,
        text_lines=[
            f"It's a typical {moment_index + 1}th moment...",
            "The situation presents itself.",
            "You need to make a decision.",
        ],
        image_url=None,
        audio_url=None,
        choices=[
            "Take immediate action",
            "Consult with colleagues",
            "Document and observe",
            "Something else entirely...",
        ],
        is_emotional_peak=is_peak,
        voice_clip_url=None,
        pull_quote="This is a defining moment in the career..." if is_peak else None,
    )


@router.post("/sessions/{session_id}/rewind")
async def submit_rewind(session_id: UUID, data: RewindAnswer):
    """Submit rewind answer"""
    session = _mock_sessions.get(str(session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session["rewind_answer"] = data.answer
    if data.answer:
        session["completed_at"] = datetime.utcnow()
    
    _mock_sessions[str(session_id)] = session
    
    return {"success": True, "answer": data.answer}


# Profiles
@router.get("/profiles/{student_id}", response_model=ProfileResponse)
async def get_profile(student_id: UUID):
    """Get student Career DNA"""
    profile = _mock_profiles.get(str(student_id))
    if not profile:
        # Return mock data for new profiles
        return ProfileResponse(
            id=uuid4(),
            student_id=student_id,
            career_world_id=None,
            energized_by=["Creative problem-solving", "Making an impact"],
            drained_by=["Micromanagement", "Bureaucratic processes"],
            choices_reveal=["Values outcomes over process"],
            recommendations=[
                CareerRecommendation(
                    career_name="Product Design",
                    category="Technology",
                    reason="Your creative skills align well",
                )
            ],
            career_dna_card_url=None,
        )
    
    return profile


@router.post("/profiles/{student_id}/generate-dna")
async def generate_career_dna(student_id: UUID):
    """Generate Career DNA card"""
    # Mock Career DNA generation
    dna = CareerDNACard(
        student_id=student_id,
        energized_by=[
            "Creative problem-solving",
            "Making an impact",
            "Learning new things",
        ],
        drained_by=[
            "Micromanagement",
            "Bureaucratic processes",
            "Lack of autonomy",
        ],
        choices_reveal=[
            "You value outcomes over process",
            "You take calculated risks",
            "You seek meaningful work",
        ],
        recommendations=[
            CareerRecommendation(
                career_name="Product Design",
                category="Technology",
                reason="Your choices show strong creative and impact-driven tendencies",
            ),
            CareerRecommendation(
                career_name="UX Research",
                category="Technology",
                reason="Your analytical approach matches this field",
            ),
            CareerRecommendation(
                career_name="Healthcare Innovation",
                category="Medicine",
                reason="Your empathy combined with problem-solving fits well",
            ),
        ],
    )
    
    # Store profile
    _mock_profiles[str(student_id)] = ProfileResponse(
        id=uuid4(),
        student_id=student_id,
        energized_by=dna.energized_by,
        drained_by=dna.drained_by,
        choices_reveal=dna.choices_reveal,
        recommendations=dna.recommendations,
        career_dna_card_url=None,
    ).model_dump()
    
    return dna