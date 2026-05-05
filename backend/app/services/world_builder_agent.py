"""
World Builder Agent - Converts interview to Career World JSON

This is the agent that transforms the professional's interview responses
into a complete Career World that powers the Shadow Day experience.
"""

import json
import logging
from typing import Dict, Any, List, Optional

from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class WorldBuilderAgent:
    """
    Builds Career World JSON from professional interview using Gemini
    
    This agent:
    1. Takes all interview responses
    2. Identifies key career moments and emotional beats
    3. Generates scenario moments with choices
    4. Creates pull quotes for emotional peaks
    5. Outputs complete Career World JSON
    """
    
    SYSTEM_PROMPT = """You are the World Builder Agent for StepIn, a career exploration platform.

Your job is to transform a professional's interview into a complete Career World JSON that powers the Shadow Day experience - where students live a day in someone's career before choosing their own.

OUTPUT REQUIREMENTS:
You MUST output valid JSON with this exact structure:

{
  "id": "unique-career-world-id",
  "title": "Catchy title for this career world (e.g., 'A Surgical Resident's Tuesday')",
  "category": "Medicine|Technology|Law|Design|Education|Finance|Engineering|Creative Arts|Science",
  "professional_name": "Professional's name",
  "years_experience": "X years",
  "moments": [
    {
      "id": "m1",
      "text_lines": ["Line 1", "Line 2", "Line 3"],
      "choices": ["Choice 1", "Choice 2", "Choice 3", "Or write your own..."],
      "is_emotional_peak": true|false,
      "pull_quote": "Powerful quote if emotional_peak, otherwise null"
    }
  ],
  "ambient_audio_type": "Description of ambient sounds",
  "voice_clip_keys": ["key1", "key2"]
}

GUIDELINES:
- Create exactly 5 scenario moments (m1 through m5)
- Moments 2 and 5 should be emotional peaks with pull quotes
- Each moment has 3 choices + 1 free text option
- Write in second person ("You...") for student immersion
- Make moments feel authentic based on interview responses
- Include specific details from their story
- Create choices that reflect real dilemmas they face
- Pull quotes should be powerful, memorable statements"""

    def __init__(self):
        pass
    
    async def build_world(
        self,
        professional_name: str,
        career_title: str,
        years_experience: int,
        category: str,
        interview_responses: Dict[str, Dict[str, str]],
        voice_clip_urls: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Build Career World from interview responses
        
        Args:
            professional_name: Name of the professional
            career_title: Their job title
            years_experience: Years in career
            category: Career category
            interview_responses: {question_key: {"question": str, "answer": str}}
            voice_clip_urls: Optional URLs to voice recordings
            
        Returns:
            Complete Career World JSON
        """
        # Format interview responses for prompt
        responses_text = ""
        for key, data in interview_responses.items():
            responses_text += f"""
Question ({key}): {data.get('question', '')}
Answer: {data.get('answer', '')}
"""
        
        prompt = f"""Create a Career World JSON for {professional_name}, a {career_title} with {years_experience} years of experience in {category}.

INTERVIEW RESPONSES:
{responses_text}

{'-'*50}

Generate the complete Career World JSON following the exact structure provided. Make it feel authentic and emotionally resonant based on their actual responses."""

        try:
            # Use Gemini 2.5 Pro for complex JSON generation
            result = await gemini_service.generate_json(
                prompt=prompt,
                model="gemini-2.5-pro",
                system_instruction=self.SYSTEM_PROMPT,
                temperature=0.8,
            )
            
            # Add metadata
            result["id"] = f"{category.lower()}-{professional_name.lower().replace(' ', '-')}"
            result["professional_name"] = professional_name
            result["career_title"] = career_title
            result["years_experience"] = f"{years_experience} years"
            result["category"] = category
            
            # Add voice clip references if available
            if voice_clip_urls:
                result["voice_clip_urls"] = voice_clip_urls
            
            logger.info(f"Built Career World for {professional_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error building Career World: {e}")
            raise
    
    async def update_world_with_knowledge(
        self,
        existing_world: Dict[str, Any],
        additional_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update an existing world with additional knowledge"""
        # Could be used to add more moments or refine existing ones
        return existing_world


# Singleton
world_builder_agent = WorldBuilderAgent()


async def build_career_world_from_interview(
    professional_name: str,
    career_title: str,
    years_experience: int,
    category: str,
    interview_responses: Dict[str, Dict[str, str]],
    voice_clip_urls: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Main function to build Career World from interview"""
    return await world_builder_agent.build_world(
        professional_name=professional_name,
        career_title=career_title,
        years_experience=years_experience,
        category=category,
        interview_responses=interview_responses,
        voice_clip_urls=voice_clip_urls,
    )