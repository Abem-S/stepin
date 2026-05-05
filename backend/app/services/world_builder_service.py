"""
World Builder Service - Converts interview transcripts to Career World JSON

This service takes the professional's interview responses and transforms them
into a complete Career World that powers the Shadow Day experience.
"""

import json
import logging
from typing import Dict, Any, List, Optional

from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class WorldBuilderService:
    """
    Builds Career World JSON from interview transcript and optional web data
    """
    
    def __init__(self):
        self.system_prompt = """You are the World Builder Agent for StepIn, a career exploration platform.
Your role is to transform interview data into a complete Career World JSON that powers the Shadow Day experience.

You must output valid JSON with this exact structure:
{
    "id": "unique-career-world-id",
    "title": "Descriptive title for the career world",
    "category": "Medicine|Technology|Law|Design|Education|Finance|Engineering|Creative Arts|Science",
    "professional_name": "Professional's name",
    "years_experience": "X years",
    "moments": [
        {
            "id": "m1",
            "text_lines": ["Line 1 of the scenario", "Line 2", "Line 3"],
            "choices": ["Choice 1", "Choice 2", "Choice 3", "Or write your own..."],
            "is_emotional_peak": true|false,
            "pull_quote": "Powerful quote if emotional_peak, otherwise null"
        }
    ],
    "ambient_audio_type": "Description of ambient sound for this career",
    "voice_clip_keys": ["key1", "key2"]
}

Guidelines:
- Create exactly 5 scenario moments (m1-m5)
- m2 and m5 should be emotional peaks
- Each moment has 3 choices + 1 free text option
- Write in second person ("You...") for student immersion
- Extract authentic details from the interview
- Include a pull quote for emotional moments"""
    
    async def build_world_from_interview(
        self,
        professional_name: str,
        career_title: str,
        interview_responses: Dict[str, str],
        years_experience: Optional[int] = None,
        category: str = "Technology",
    ) -> Dict[str, Any]:
        """
        Build a complete Career World from interview responses
        
        Args:
            professional_name: Name of the professional
            career_title: Their job title
            interview_responses: Dict of question_key -> response
            years_experience: Years in career
            category: Career category
            
        Returns:
            Complete Career World JSON
        """
        # Format responses for the prompt
        responses_text = "\n".join([
            f"{key}: {response}"
            for key, response in interview_responses.items()
        ])
        
        prompt = f"""Create a Career World JSON for {professional_name}, a {career_title} with {years_experience or 'several'} years experience.

Their interview responses:
{responses_text}

Generate the complete Career World JSON following the schema provided."""

        try:
            result = await gemini_service.generate_json(
                prompt=prompt,
                model="gemini-2.5-pro",
                system_instruction=self.system_prompt,
                temperature=0.7,
            )
            
            # Add metadata
            result["professional_name"] = professional_name
            result["career_title"] = career_title
            result["years_experience"] = f"{years_experience or 'several'} years"
            result["category"] = category
            
            logger.info(f"Built Career World for {professional_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error building Career World: {e}")
            raise
    
    async def build_world_with_scraped_data(
        self,
        professional_name: str,
        career_title: str,
        interview_responses: Dict[str, str],
        scraped_data: Optional[Dict[str, Any]] = None,
        years_experience: Optional[int] = None,
        category: str = "Technology",
    ) -> Dict[str, Any]:
        """
        Build Career World with additional web-scraped data
        """
        responses_text = "\n".join([
            f"{key}: {response}"
            for key, response in interview_responses.items()
        ])
        
        prompt = f"""Create a Career World JSON for {professional_name}, a {career_title}.

Interview responses:
{responses_text}
"""
        if scraped_data:
            prompt += f"""
Additional information from web:
- LinkedIn headline: {scraped_data.get('linkedin_headline', 'N/A')}
- Recent posts: {scraped_data.get('recent_posts', 'N/A')}
"""
        
        prompt += """
Generate the complete Career World JSON following the schema provided."""

        try:
            result = await gemini_service.generate_json(
                prompt=prompt,
                model="gemini-2.5-pro",
                system_instruction=self.system_prompt,
                temperature=0.7,
            )
            
            result["professional_name"] = professional_name
            result["career_title"] = career_title
            result["years_experience"] = f"{years_experience or 'several'} years"
            result["category"] = category
            
            return result
            
        except Exception as e:
            logger.error(f"Error building Career World with scraped data: {e}")
            raise


# Singleton
world_builder_service = WorldBuilderService()


async def build_career_world(
    professional_name: str,
    career_title: str,
    interview_responses: Dict[str, str],
    years_experience: Optional[int] = None,
    category: str = "Technology",
    scraped_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Convenience function to build a Career World"""
    if scraped_data:
        return await world_builder_service.build_world_with_scraped_data(
            professional_name=professional_name,
            career_title=career_title,
            interview_responses=interview_responses,
            scraped_data=scraped_data,
            years_experience=years_experience,
            category=category,
        )
    else:
        return await world_builder_service.build_world_from_interview(
            professional_name=professional_name,
            career_title=career_title,
            interview_responses=interview_responses,
            years_experience=years_experience,
            category=category,
        )