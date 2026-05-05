"""Shadow Day Service - Scenario flow orchestration"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID


class ShadowDayService:
    """Service for managing Shadow Day sessions and scenario flow"""
    
    def __init__(self):
        # In-memory mock storage
        self._sessions: dict = {}
    
    async def create_session(
        self,
        student_id: UUID,
        career_world_id: UUID,
    ) -> dict:
        """Start a new Shadow Day session"""
        session_id = UUID()
        session = {
            "id": session_id,
            "student_id": student_id,
            "career_world_id": career_world_id,
            "choices": {},
            "timing_data": {},
            "hesitations_ms": {},
            "rewind_answer": None,
            "completed_at": None,
            "created_at": datetime.utcnow(),
        }
        self._sessions[str(session_id)] = session
        return session
    
    async def get_session(self, session_id: UUID) -> Optional[dict]:
        """Get a session by ID"""
        return self._sessions.get(str(session_id))
    
    async def submit_choice(
        self,
        session_id: UUID,
        moment_index: int,
        choice_index: Optional[int],
        free_text: Optional[str],
        hesitation_ms: int,
    ) -> dict:
        """Submit a choice for a scenario moment"""
        session = self._sessions.get(str(session_id))
        if not session:
            return None
        
        choice_data = {
            "moment_index": moment_index,
            "choice_index": choice_index,
            "free_text": free_text,
            "hesitation_ms": hesitation_ms,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        session["choices"][str(moment_index)] = choice_data
        session["hesitations_ms"][str(moment_index)] = hesitation_ms
        session["timing_data"][str(moment_index)] = {
            "hesitation_ms": hesitation_ms,
            "made_at": datetime.utcnow().isoformat(),
        }
        
        return session
    
    async def get_moment(
        self,
        session_id: UUID,
        moment_index: int,
    ) -> Optional[dict]:
        """Get a specific scenario moment from the session's career world"""
        session = self._sessions.get(str(session_id))
        if not session:
            return None
        
        # In production, this would load from career_world_service
        # For now, return mock moment data
        return {
            "moment_index": moment_index,
            "text_lines": [
                f"Moment {moment_index + 1} - Opening line...",
                "The situation unfolds before you.",
                "What will you do?",
            ],
            "image_url": None,
            "audio_url": None,
            "choices": [
                "Choice A",
                "Choice B", 
                "Choice C",
                "Something else...",
            ],
            "is_emotional_peak": moment_index in [2, 4],
            "voice_clip_url": None,
            "pull_quote": "A powerful quote from the professional..." if moment_index in [2, 4] else None,
        }
    
    async def submit_rewind_answer(
        self,
        session_id: UUID,
        answer: str,
    ) -> Optional[dict]:
        """Submit the rewind answer (yes or not_for_me)"""
        session = self._sessions.get(str(session_id))
        if not session:
            return None
        
        session["rewind_answer"] = answer
        if answer:
            session["completed_at"] = datetime.utcnow()
        
        return session
    
    async def get_session_count(self) -> int:
        """Get total number of sessions"""
        return len(self._sessions)


# Singleton instance
shadow_day_service = ShadowDayService()