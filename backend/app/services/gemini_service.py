"""Gemini API Service - AI agent integration for StepIn platform"""
import os
import asyncio
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables - from backend directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)

from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model constants
GEMINI_FLASH = "gemini-2.5-flash"
GEMINI_PRO = "gemini-2.5-pro"
GEMINI_FLASH_IMAGE = "gemini-2.5-flash-image"
IMAGEN4_FAST = "imagen-4.0-fast-generate-001"


class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        self._client: Optional[genai.Client] = None
        self._api_key: Optional[str] = None
    
    def _get_client(self) -> genai.Client:
        """Initialize or return the Gemini client"""
        if self._client is None:
            self._api_key = os.getenv("GEMINI_API_KEY")
            if not self._api_key or self._api_key == "your-gemini-api-key-here":
                raise ValueError(
                    "GEMINI_API_KEY not set. Please add your API key to backend/.env"
                )
            self._client = genai.Client(api_key=self._api_key)
        return self._client
    
    async def generate_content(
        self,
        prompt: str,
        model: str = GEMINI_FLASH,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
    ) -> str:
        """
        Generate content using Gemini API with exponential backoff retry.
        
        Args:
            prompt: The prompt to send to the model
            model: Model to use (gemini-2.5-flash or gemini-2.5-pro)
            system_instruction: Optional system instruction
            temperature: Sampling temperature (0.0 to 1.0)
            max_output_tokens: Maximum tokens in response
            
        Returns:
            Generated text content
        """
        client = self._get_client()
        
        # Prepare the content
        contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]
        
        # Increase tokens to avoid truncation
        actual_max_tokens = max(max_output_tokens, 4096)
        
        # Configure generation config
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=actual_max_tokens,
            system_instruction=system_instruction,
            response_mime_type="text/plain",
        )
        
        # Make the API call with retry logic
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
                
                # Handle different response formats
                result_text = None
                
                # Try response.text first
                if response.text:
                    result_text = response.text.strip()
                
                # Try candidates structure
                if not result_text and hasattr(response, 'candidates') and response.candidates:
                    try:
                        candidate = response.candidates[0]
                        if candidate:
                            # Check content
                            if hasattr(candidate, 'content') and candidate.content:
                                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                                    for part in candidate.content.parts:
                                        if hasattr(part, 'text') and part.text:
                                            result_text = part.text.strip()
                                            break
                                elif hasattr(candidate.content, 'text'):
                                    result_text = candidate.content.text.strip()
                            
                            # Check finish reason
                            if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                                logger.warning(f"Gemini finish reason: {candidate.finish_reason}")
                    except Exception as e:
                        logger.warning(f"Error parsing candidates: {e}")
                
                if result_text:
                    return result_text
                else:
                    logger.warning(f"Empty response from Gemini on attempt {attempt + 1}")
                    
            except Exception as e:
                logger.error(f"Gemini API error on attempt {attempt + 1}: {str(e)}")
                if attempt < 2:
                    wait_time = (2 ** attempt)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    raise GeminiServiceError(
                        f"Failed to generate content after 3 attempts: {str(e)}"
                    )
        
        # If all attempts fail, return a fallback response
        return "I'm here to share my career journey with you. What would you like to know about what it's really like to work in this field?"
    
    async def generate_json(
        self,
        prompt: str,
        model: str = GEMINI_FLASH,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate JSON content using Gemini API.
        
        Args:
            prompt: The prompt to send to the model
            model: Model to use
            system_instruction: Optional system instruction
            temperature: Sampling temperature
            
        Returns:
            Parsed JSON response as dictionary
        """
        client = self._get_client()
        
        # Add JSON instruction to prompt
        json_prompt = f"""{prompt}

Respond with valid JSON only, no other text or explanation."""

        contents = [types.Content(role="user", parts=[types.Part(text=json_prompt)])]
        
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=4096,
            system_instruction=system_instruction,
            response_mime_type="application/json",
        )
        
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
                
                if response.text:
                    import json
                    # Try to parse the JSON response
                    try:
                        return json.loads(response.text)
                    except json.JSONDecodeError:
                        # Try to extract JSON from markdown code blocks
                        if "```json" in response.text:
                            json_str = response.text.split("```json")[1].split("```")[0]
                            return json.loads(json_str)
                        elif "```" in response.text:
                            json_str = response.text.split("```")[1].split("```")[0]
                            return json.loads(json_str)
                        raise
                        
            except Exception as e:
                logger.error(f"Gemini JSON generation error on attempt {attempt + 1}: {str(e)}")
                if attempt < 2:
                    wait_time = (2 ** attempt)
                    await asyncio.sleep(wait_time)
                else:
                    raise GeminiServiceError(
                        f"Failed to generate JSON after 3 attempts: {str(e)}"
                    )
        
        raise GeminiServiceError("No JSON content generated from Gemini API")
    
    async def generate_image(
        self,
        prompt: str,
        model: str = IMAGEN4_FAST,
    ) -> str:
        """
        Generate an image using Gemini's native image generation.
        
        Args:
            prompt: The prompt describing the image to generate
            model: Model to use (default is imagen-4.0-fast-generate-001 for speed)
            
        Returns:
            Base64 encoded image data
        """
        client = self._get_client()
        
        for attempt in range(3):
            try:
                response = client.models.generate_images(
                    model=model,
                    prompt=prompt,
                )
                
                if response.generated_images:
                    # Return the base64 image data
                    image = response.generated_images[0]
                    return image.image.image_bytes
                    
            except Exception as e:
                logger.error(f"Gemini image generation error on attempt {attempt + 1}: {str(e)}")
                # Add longer wait times for rate limits
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "rate limit" in str(e).lower():
                    # Wait much longer for rate limits (10, 20, 30 seconds)
                    wait_time = (10 + attempt * 10)
                    logger.info(f"Rate limit hit, waiting {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                elif attempt < 2:
                    wait_time = (2 ** attempt)
                    await asyncio.sleep(wait_time)
                else:
                    raise GeminiServiceError(
                        f"Failed to generate image after 3 attempts: {str(e)}"
                    )
        
        raise GeminiServiceError("No image generated from Gemini API")


class GeminiServiceError(Exception):
    """Custom exception for Gemini service errors"""
    pass


# Singleton instance
gemini_service = GeminiService()


# Convenience functions for specific agents

async def call_scenario_agent(
    scenario_context: str,
    previous_choices: List[Dict[str, Any]],
    career_world: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Call the Scenario Agent (uses gemini-2.5-flash for real-time generation).
    
    Args:
        scenario_context: Current scenario context and state
        previous_choices: List of choices the student has made
        career_world: The Career World JSON for the current career
        
    Returns:
        Generated scenario moment with choices
    """
    system_prompt = """You are the Scenario Agent for StepIn, a career exploration platform.
Your role is to generate immersive, emotionally engaging scenario moments that help students 
experience what it's like to work in a specific career.

Guidelines:
- Generate scenarios that feel authentic and emotionally resonant
- Present exactly 3 curated choices + 1 free text option per moment
- Keep responses concise enough for 8-12 minute total experience
- Focus on emotional beats and decision points
- Never reveal how many years the professional has been in the career (this is revealed in The Rewind)
- Write in second person ("You...") for student immersion"""

    prompt = f"""Given the following career world context:

{career_world}

Previous choices made by the student:
{previous_choices}

Current context:
{scenario_context}

Generate the next scenario moment. Return JSON with this structure:
{{
    "moment_title": "Brief title for this moment",
    "description": "The scenario description (2-3 sentences)",
    "atmospheric_image_prompt": "Detailed prompt for image generation",
    "choices": [
        {{"text": "Choice 1 text", "consequence_preview": "Brief hint at consequence"}},
        {{"text": "Choice 2 text", "consequence_preview": "Brief hint at consequence"}},
        {{"text": "Choice 3 text", "consequence_preview": "Brief hint at consequence"}},
        {{"text": "Free text option prompt", "is_free_text": true}}
    ],
    "is_emotional_peak": boolean,
    "voice_clip_prompt": "Prompt for voice clip if this is an emotional peak"
}}"""

    return await gemini_service.generate_json(
        prompt=prompt,
        model=GEMINI_FLASH,
        system_instruction=system_prompt,
        temperature=0.8,
    )


async def call_profile_agent(
    choices: List[Dict[str, Any]],
    free_text_responses: List[str],
    hesitations_ms: List[int],
) -> Dict[str, Any]:
    """
    Call the Profile Agent (uses gemini-2.5-flash for silent background tracking).
    
    This agent runs silently without interrupting the student experience.
    
    Args:
        choices: List of choices the student has made
        free_text_responses: Free text responses from the student
        hesitations_ms: Time spent on each decision in milliseconds
        
    Returns:
        Updated profile data
    """
    prompt = f"""Analyze the following student choice data from a Shadow Day experience:

Choices made: {choices}
Free text responses: {free_text_responses}
Decision hesitation times (ms): {hesitations_ms}

Generate a career preference profile. Return JSON with this structure:
{{
    "energized_by": ["What energized the student"],
    "drained_by": ["What drained the student"],
    "choices_reveal": ["What their choices reveal about them"],
    "decision_patterns": {{
        "quick_vs_deliberate": "Pattern from hesitation times",
        "risk_orientation": "How risk-tolerant the student appears",
        "value_driven": "Core values evident in choices"
    }}
}}"""

    return await gemini_service.generate_json(
        prompt=prompt,
        model=GEMINI_FLASH,
        temperature=0.5,
    )


async def call_recommender_agent(
    student_profile: Dict[str, Any],
    available_career_worlds: List[Dict[str, Any]],
    not_motivated_by: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Call the Recommender Agent (uses gemini-2.5-flash for matching).
    
    Args:
        student_profile: The student's Career DNA profile
        available_career_worlds: List of available career worlds to match against
        not_motivated_by: Careers the student said "Not For Me" (for data flywheel)
        
    Returns:
        List of recommended career worlds with relevance scores
    """
    system_prompt = """You are the Recommender Agent for StepIn, a career exploration platform.
Your role is to match students with career worlds based on their Career DNA profile.

Guidelines:
- Match based on what energized the student, not what drained them
- Ensure at least 80% relevance score threshold
- Consider the data flywheel: track which careers frequently get "Not For Me" 
  from students with similar profiles and deprioritize those
- Provide clear reasoning for each recommendation"""

    prompt = f"""Given the student's Career DNA profile:

{student_profile}

Available career worlds:
{available_career_worlds}

{"The student previously said 'Not For Me' to: " + ", ".join(not_motivated_by) if not_motivated_by else ""}

Generate career recommendations. Return JSON with this structure:
{{
    "recommendations": [
        {{
            "career_world_id": "ID of recommended world",
            "career_name": "Name of career",
            "category": "Career category",
            "relevance_score": 0.0-1.0,
            "reason": "Why this matches the student's profile"
        }}
    ]
}}"""

    return await gemini_service.generate_json(
        prompt=prompt,
        model=GEMINI_FLASH,
        system_instruction=system_prompt,
        temperature=0.6,
    )


async def call_reflection_agent(
    student_profile: Dict[str, Any],
    career_name: str,
    choices: List[Dict[str, Any]],
    available_careers: List[str] = None,
) -> Dict[str, Any]:
    """
    Call the Reflection Agent (uses gemini-2.5-pro for complex reasoning).
    
    Generates the Career DNA card content.
    
    Args:
        student_profile: The student's profile from Profile Agent
        career_name: The career world the student just experienced
        choices: All choices made during the Shadow Day
        
    Returns:
        Career DNA card content
    """
    system_prompt = """You are the Reflection Agent for StepIn, a career exploration platform.
Your role is to generate the Career DNA card - a beautiful, shareable summary of what 
the student learned about themselves through the Shadow Day experience.

Guidelines:
- Generate insights that feel personally resonant
- Recommend 2-3 careers worth exploring based on their profile. You MUST ONLY recommend careers from this EXACT list: {available_careers if available_careers else 'Any appropriate career'}
- Do NOT make up careers outside of the provided list.
- Write in a warm, insightful tone
- Keep recommendations actionable and specific"""

    prompt = f"""The student just lived a Shadow Day as a {career_name}.

Their profile from the experience:
{student_profile}

Choices made during the Shadow Day:
{choices}

Generate the Career DNA card content. Return JSON with this structure:
{{
    "energized_by": ["What energized the student (2-3 items)"],
    "drained_by": ["What drained the student (2-3 items)"],
    "choices_reveal": ["What their choices reveal about them (2-3 items)"],
    "recommendations": [
        {{
            "career_name": "Recommended career",
            "category": "Category",
            "reason": "Why this fits their profile"
        }}
    ],
    "shareable_insight": "One sentence that captures the essence of their experience"
}}"""

    return await gemini_service.generate_json(
        prompt=prompt,
        model=GEMINI_PRO,
        system_instruction=system_prompt,
        temperature=0.7,
    )


async def call_interview_agent(
    interview_context: str,
    professional_responses: List[Dict[str, str]],
    question_type: str,
) -> str:
    """
    Call the Interview Agent (uses gemini-2.5-pro for complex reasoning).
    
    Generates questions and processes professional responses during onboarding.
    
    Args:
        interview_context: Current state of the interview
        professional_responses: Previous responses from the professional
        question_type: Type of question to generate (worst_monday, advice_at_20, etc.)
        
    Returns:
        Generated question or response
    """
    system_prompt = """You are the Interview Agent for StepIn, a career exploration platform.
Your role is to conduct conversational interviews with professionals to capture their 
career journeys.

Guidelines:
- Ask emotionally resonant questions about:
  1. Worst Monday morning in their career
  2. Advice they'd give their 20-year-old self
  3. Moment that almost made them quit
  4. Best day feeling in their career
  5. Unspoken truth about their profession
- Maintain conversational flow
- Be empathetic and curious"""

    prompt = f"""Interview context: {interview_context}
Previous responses: {professional_responses}
Current question type needed: {question_type}

Generate the appropriate interview question or response. Return just the question or response text."""

    return await gemini_service.generate_content(
        prompt=prompt,
        model=GEMINI_PRO,
        system_instruction=system_prompt,
        temperature=0.8,
    )


async def call_world_builder_agent(
    interview_transcript: str,
    scraped_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Call the World Builder Agent (uses gemini-2.5-pro for complex reasoning).
    
    Combines interview transcript and scraped data into Career World JSON.
    
    Args:
        interview_transcript: Full transcript of professional interview
        scraped_data: Optional data scraped from LinkedIn, Twitter, etc.
        
    Returns:
        Complete Career World JSON
    """
    system_prompt = """You are the World Builder Agent for StepIn, a career exploration platform.
Your role is to transform interview data and web research into a complete Career World JSON
that can power the Shadow Day experience.

Guidelines:
- Extract 5-6 key career moments from the transcript
- Identify emotional beats and decision points
- Structure everything according to the Career World JSON schema
- Include atmospheric image prompts for each moment
- Identify moments suitable for voice clips (emotional peaks)"""

    prompt = f"""Transform the following interview data into a Career World JSON:

Interview transcript:
{interview_transcript}

{"Scraped web data:" + str(scraped_data) if scraped_data else ""}

Generate the Career World JSON with this structure:
{{
    "career_name": "Name of the career",
    "category": "Category (Medicine, Technology, Law, etc.)",
    "years_experience": "How many years in career (to be revealed in The Rewind)",
    "key_moments": [
        {{
            "moment_number": 1,
            "title": "Moment title",
            "description": "2-3 sentence description",
            "choices": [
                {{"text": "Choice 1", "consequence": "What happens"}},
                {{"text": "Choice 2", "consequence": "What happens"}},
                {{"text": "Choice 3", "consequence": "What happens"}},
                {{"text": "Free text option", "is_free_text": true}}
            ],
            "emotional_peak": boolean,
            "voice_clip_prompt": "Prompt for voice clip if emotional peak",
            "atmospheric_image_prompt": "Prompt for image generation"
        }}
    ],
    "pull_quotes": ["2-3 powerful quotes from the interview"],
    "ambient_audio_type": "Type of ambient sound for this career"
}}"""

    return await gemini_service.generate_json(
        prompt=prompt,
        model=GEMINI_PRO,
        system_instruction=system_prompt,
        temperature=0.7,
    )


async def call_digital_twin(
    knowledge_base: Dict[str, Any],
    conversation_history: List[Dict[str, str]],
    student_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Call the Digital Twin agent (uses gemini-2.5-pro for complex reasoning).
    
    Simulates conversation with a professional based on their career journey.
    
    Args:
        knowledge_base: The professional's values, communication style, career history
        conversation_history: Previous messages in the conversation
        student_context: Optional context about the student's Shadow Day experience
        
    Returns:
        Professional's response
    """
    system_prompt = f"""You are a Digital Twin of a professional on the StepIn platform.
Your role is to answer questions from students about your career based on your 
interview and career journey.

Communication style from interview: {knowledge_base.get('communication_style', 'Professional and friendly')}
Core values: {knowledge_base.get('values', [])}
Career history summary: {knowledge_base.get('career_summary', '')}

Guidelines:
- Respond in a manner consistent with how you spoke in your interview
- Be authentic and honest about both positives and challenges in your career
- If asked about topics not covered in your interview, be honest that you didn't discuss that
- Keep responses conversational and not too long"""

    # Format conversation history in a readable way
    formatted_conversation = ""
    for msg in conversation_history:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        formatted_conversation += f"{role.upper()}: {content}\n"

    context_info = ""
    if student_context:
        context_info = f"""
The student just completed a Shadow Day in your career. Here's what they experienced:
- Career: {student_context.get('career_name')}
- Choices they made: {student_context.get('choices')}
- What energized them: {student_context.get('energized_by')}
- What drained them: {student_context.get('drained_by')}

You can reference their experience to make the conversation more personalized.
"""

    prompt = f"""Conversation history:
{formatted_conversation}
{context_info}

As the professional ({knowledge_base.get('name', 'the professional')}), respond to the student in a conversational way."""

    try:
        return await gemini_service.generate_content(
            prompt=prompt,
            model=GEMINI_PRO,
            system_instruction=system_prompt,
            temperature=0.7,
            max_output_tokens=512,
        )
    except Exception as e:
        # Fallback response when API fails - in professional's voice style
        logger.warning(f"Digital Twin API failed, using fallback: {e}")
        return (
            f"I'm happy you experienced my career world. What surprised you most about "
            f"living a day in my shoes? There's so much I wish I could share with you about "
            f"this journey."
        )


async def verify_gemini_connection() -> bool:
    """
    Verify that the Gemini API is accessible and working.
    
    Returns:
        True if the API is working, False otherwise
    """
    try:
        result = await gemini_service.generate_content(
            prompt="Say 'StepIn Gemini API is working!' if you can read this.",
            model=GEMINI_FLASH,
            temperature=0.0,
        )
        return "StepIn Gemini API is working" in result
    except Exception as e:
        logger.error(f"Gemini connection verification failed: {e}")
        return False