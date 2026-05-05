"""Recommendation Service - Matching students to professionals"""
from typing import List
from uuid import UUID


class RecommendationService:
    """Service for recommending careers to students"""
    
    # Mock career categories with metadata
    CAREER_CATEGORIES = [
        {"id": "medicine", "name": "Medicine", "world_count": 1},
        {"id": "technology", "name": "Technology", "world_count": 1},
        {"id": "law", "name": "Law", "world_count": 0},
        {"id": "design", "name": "Design", "world_count": 0},
        {"id": "education", "name": "Education", "world_count": 0},
        {"id": "finance", "name": "Finance", "world_count": 0},
        {"id": "engineering", "name": "Engineering", "world_count": 0},
        {"id": "creative_arts", "name": "Creative Arts", "world_count": 0},
        {"id": "science", "name": "Science", "world_count": 0},
    ]
    
    async def get_categories(self) -> List[dict]:
        """Get all career categories"""
        return self.CAREER_CATEGORIES
    
    async def get_recommendations(
        self,
        student_id: UUID,
        profile_data: dict,
    ) -> List[dict]:
        """Get career recommendations for a student"""
        # Mock implementation - in production uses Recommender Agent
        # with 80%+ relevance threshold
        
        # Return mock recommendations based on profile
        recommendations = [
            {
                "career_name": "Product Design",
                "category": "Technology",
                "reason": "Your creative problem-solving skills align well with this path",
                "relevance": 0.87,
            },
            {
                "career_name": "UX Research",
                "category": "Technology", 
                "reason": "Your analytical approach makes you a great fit",
                "relevance": 0.82,
            },
            {
                "career_name": "Healthcare Innovation",
                "category": "Medicine",
                "reason": "Your empathy combined with technical aptitude is valuable",
                "relevance": 0.79,
            },
        ]
        
        return recommendations
    
    async def get_alternative_world(
        self,
        student_id: UUID,
        rejected_world_id: UUID,
        profile_data: dict,
    ) -> dict:
        """Get an alternative career world for a student who said 'Not For Me'"""
        # Mock - in production this would use the Recommender Agent
        # to find the next best matching world
        
        return {
            "alternative_world_id": "alt-world-001",
            "reason": "Based on your profile, this world might be a better fit",
            "category": "Technology",
        }


# Singleton instance
recommendation_service = RecommendationService()