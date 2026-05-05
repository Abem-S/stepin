"""Interview Service - WebSocket-based conversational interview flow"""
from typing import List
from uuid import UUID


class InterviewService:
    """Service for handling professional interview sessions"""
    
    # Standard interview questions
    INTERVIEW_QUESTIONS = [
        {
            "key": "worst_monday",
            "question": "What's the worst Monday morning you've had in this career?",
        },
        {
            "key": "advice_at_20",
            "question": "What advice would you give yourself at 20?",
        },
        {
            "key": "almost_quit",
            "question": "What's a moment that almost made you quit?",
        },
        {
            "key": "best_day",
            "question": "Describe the best day feeling in this career.",
        },
        {
            "key": "unspoken_truth",
            "question": "What's an unspoken truth about this career?",
        },
    ]
    
    async def get_next_question(self, question_index: int) -> dict:
        """Get the next interview question"""
        if question_index >= len(self.INTERVIEW_QUESTIONS):
            return None
        
        return self.INTERVIEW_QUESTIONS[question_index]
    
    async def process_answer(self, question_key: str, answer: str) -> dict:
        """Process a professional's answer (placeholder for agent processing)"""
        # Mock processing - in production this would trigger the World Builder Agent
        return {
            "processed": True,
            "key": question_key,
            "answer_length": len(answer),
        }
    
    async def complete_interview(
        self, 
        professional_id: UUID, 
        transcript: List[dict]
    ) -> dict:
        """Complete the interview and trigger World Builder"""
        # Mock - in production this would call the World Builder Agent
        return {
            "professional_id": str(professional_id),
            "transcript_length": len(transcript),
            "world_building_started": True,
        }


# Singleton instance
interview_service = InterviewService()