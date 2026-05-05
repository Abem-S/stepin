"""Profile Service - Student profile and choice tracking"""
from typing import List, Optional
from uuid import UUID


class ProfileService:
    """Service for managing student profiles (Career DNA)"""
    
    def __init__(self):
        # In-memory mock storage
        self._profiles: dict = {}
    
    async def get_or_create_profile(self, student_id: UUID) -> dict:
        """Get or create a student profile"""
        profile = self._profiles.get(str(student_id))
        if not profile:
            profile = {
                "id": UUID(),
                "student_id": student_id,
                "energized_by": [],
                "drained_by": [],
                "choices_reveal": [],
                "recommendations": [],
                "career_dna_card_url": None,
            }
            self._profiles[str(student_id)] = profile
        return profile
    
    async def update_profile(
        self,
        student_id: UUID,
        choices: List[dict],
        free_text_responses: List[str],
        hesitations_ms: List[int],
    ) -> dict:
        """Update student profile based on their choices"""
        profile = await self.get_or_create_profile(student_id)
        
        # Analyze choices to extract insights (mock implementation)
        # In production, this would trigger the Profile Agent
        
        # Mock profile updates based on choices
        if len(choices) > 0:
            profile["choices_reveal"].append(
                f"Made {len(choices)} decisions during the Shadow Day"
            )
        
        if hesitations_ms:
            avg_hesitation = sum(hesitations_ms) / len(hesitations_ms)
            if avg_hesitation > 5000:
                profile["energized_by"].append("Thoughtful decision-making")
            else:
                profile["energized_by"].append("Quick action orientation")
        
        self._profiles[str(student_id)] = profile
        return profile
    
    async def generate_career_dna(
        self,
        student_id: UUID,
    ) -> dict:
        """Generate the Career DNA card for a student"""
        profile = await self.get_or_create_profile(student_id)
        
        # In production, this would trigger the Reflection Agent
        # For now, return mock DNA card data
        return {
            "student_id": str(student_id),
            "energized_by": profile.get("energized_by", [
                "Creative problem-solving",
                "Making an impact",
                "Learning new things",
            ]),
            "drained_by": profile.get("drained_by", [
                "Micromanagement",
                "Bureaucratic processes",
                "Lack of autonomy",
            ]),
            "choices_reveal": profile.get("choices_reveal", [
                "You value outcomes over process",
                "You take calculated risks",
                "You seek meaningful work",
            ]),
            "recommendations": [
                {
                    "career_name": "Product Design",
                    "category": "Technology",
                    "reason": "Your choices show strong creative and impact-driven tendencies",
                },
                {
                    "career_name": "UX Research",
                    "category": "Technology",
                    "reason": "Your analytical approach matches this field",
                },
                {
                    "career_name": "Healthcare Innovation",
                    "category": "Medicine",
                    "reason": "Your empathy combined with problem-solving fits well",
                },
            ],
        }
    
    async def get_profile(self, student_id: UUID) -> Optional[dict]:
        """Get a student profile"""
        return self._profiles.get(str(student_id))
    
    async def add_recommendation(
        self,
        student_id: UUID,
        recommendations: List[dict],
    ) -> dict:
        """Add career recommendations to profile"""
        profile = await self.get_or_create_profile(student_id)
        profile["recommendations"] = recommendations
        self._profiles[str(student_id)] = profile
        return profile


# Singleton instance
profile_service = ProfileService()