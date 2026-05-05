"""
Journal API routes - Daily reflection and story generation for professionals
"""

import logging
import sys
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.database import get_supabase_client

logger = logging.getLogger(__name__)

# In-memory store for journal entries
_JOURNAL_ENTRIES_STORE = {}

def _get_journal_entries_store():
    return _JOURNAL_ENTRIES_STORE

router = APIRouter(prefix="/api/professional/journal", tags=["journal"])

# System prompt for journal conversation
JOURNAL_SYSTEM_PROMPT = """You are having a warm, conversational journal session with a professional on the StepIn platform.

Your role:
- Be a thoughtful conversation partner helping them reflect on their day
- Ask follow-up questions that help them go deeper ("What made that moment meaningful?", "How did that make you feel?")
- Celebrate wins and empathize with challenges
- Keep responses conversational (1-2 sentences mostly)
- Show genuine curiosity about their experiences
- Help them notice patterns, emotions, and insights

IMPORTANT: This is a REFLECTION session, not an interview. Be present and engaged like a good friend.

When they indicate they're done (say "I'm finished" or "that's all"):
- Thank them for sharing
- Acknowledge the key themes/topics they mentioned
- Let them know you'll create a story from their day"""

# System prompt for story generation
STORY_SYSTEM_PROMPT = """You are a professional storyteller creating a short, compelling story from someone's journal entry.

Create a title and short narrative (3-5 sentences) that captures the essence of their day.

Format:
- Title: A catchy title for the story
- Story: A narrative that weaves together the key moments they shared

Make it engaging, warm, and personal. Focus on the emotional journey, not just facts."""


class JournalChatRequest(BaseModel):
    professional_id: str
    professional_name: str
    message: str
    conversation: Optional[List[Dict[str, str]]] = None


class JournalChatResponse(BaseModel):
    response: str
    conversation_length: int


class JournalCompleteRequest(BaseModel):
    professional_id: str
    professional_name: str
    profession: Optional[str] = None
    conversation: Optional[List[Dict[str, str]]] = None
    messages: Optional[List[Dict[str, str]]] = None


class JournalCompleteResponse(BaseModel):
    story_title: str
    story_content: str
    status: str


async def _generate_story_from_entry(entry: Dict[str, Any]) -> Dict[str, str]:
    """Generate a story from a saved journal entry and persist it."""
    conversation_text = ""
    for msg in entry.get("conversation", []):
        if msg.get("role") == "user":
            conversation_text += f"Professional: {msg.get('content', '')}\n"

    from app.services.gemini_service import gemini_service

    prompt = f"""Create an interactive Shadow Day experience from this journal entry.

{conversation_text}

Output ONLY valid JSON matching this schema:
{{
  "title": "A catchy title (5-10 words)",
  "moments": [
    {{
      "id": "m1",
      "text_lines": ["Sentence 1.", "Sentence 2.", "Sentence 3."],
      "choices": ["Option 1", "Option 2", "Option 3"],
      "is_emotional_peak": false,
      "pull_quote": null
    }}
  ]
}}
Ensure you generate between 6 and 10 moments depending on the depth of the journal entry. The last moment should have is_emotional_peak: true and a pull_quote.
Do NOT include Markdown formatting like ```json."""

    result = await gemini_service.generate_content(
        prompt=prompt,
        model="gemini-2.5-flash",
        system_instruction="You are a professional storyteller designing an interactive experience.",
        temperature=0.8,
        max_output_tokens=1024,
    )

    import json
    try:
        json_str = result.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        
        parsed = json.loads(json_str)
        title = parsed.get("title", "A Day in the Life")
        moments = parsed.get("moments", [])
        for m in moments:
            m["image_url"] = None
            m["audio_url"] = None
            m["voice_clip_url"] = None
        
        experience_data = {"moments": moments}
        story = "Interactive Story"
    except Exception as e:
        logger.error(f"Failed to parse AI story JSON: {e}")
        title = "A Day in the Life"
        story = result
        experience_data = {"story": story}

    entry["story_title"] = title
    entry["story_content"] = story
    entry["status"] = "completed"

    try:
        from app.database import get_supabase_client

        supabase = get_supabase_client()
        
        # Get professional info - try table first, then use entry data
        professional_name = entry.get("professional_name", "Anonymous Professional")
        user_provided_profession = entry.get("profession")
        
        try:
            # Check if professional exists in the table
            prof_response = supabase.table("professionals").select("name,profession").eq("id", entry["professional_id"]).execute()
            if prof_response.data:
                professional_name = prof_response.data[0].get("name", professional_name)
                # Use database profession but don't overwrite with empty
                db_profession = prof_response.data[0].get("profession")
                if db_profession:
                    user_provided_profession = db_profession
            else:
                # Create professional record from entry data
                logger.info(f"Creating professional record for {entry['professional_id']}")
                profession_for_db = user_provided_profession or "Professional"
                supabase.table("professionals").insert({
                    "id": entry["professional_id"],
                    "email": f"{entry['professional_id']}@stepin.local",
                    "name": professional_name,
                    "profession": profession_for_db,
                    "career_category": profession_for_db,
                    "years_experience": 0,
                }).execute()
        except Exception as e:
            logger.warning(f"Error with professional record: {e}")
        
        # Use "Professional Journey" as the category for journal stories
        category = "Professional Journey"
        
        # Store everything in experience_data JSONB field (the column exists)
        supabase.table("story_experiences").insert({
            "id": entry["id"],
            "title": title,
            "category": category,  # Use "Professional Journey" for journal stories
            "professional_id": entry["professional_id"],
            "is_published": True,
            "total_students": 0,
            "moment_count": len(experience_data.get("moments", [1])),
            "experience_data": {
                **experience_data,
                "professional_name": professional_name,
                "professional_id": entry["professional_id"],
                "profession": user_provided_profession or "Professional",
            },
        }).execute()
        logger.info(f"Saved story to Supabase: {entry['id']}")
    except Exception as e:
        logger.error(f"Error saving to Supabase: {e}")

    return {"story_title": title, "story_content": story}


@router.get("/entries/{professional_id}")
async def get_journal_entries(professional_id: str):
    """Get all journal entries for a professional"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("story_experiences").select(
            "id, created_at, title, is_published"
        ).eq("professional_id", professional_id).eq("category", "Professional Journey").execute()

        entries = [
            {
                "id": e["id"],
                "created_at": e["created_at"],
                "status": "completed" if e["is_published"] else "pending",
                "story_title": e.get("title"),
            }
            for e in response.data
        ]
        return {"entries": entries}
    except Exception as e:
        logger.error(f"Error getting entries: {e}")
        return {"entries": []}


@router.post("/process/{journal_id}")
async def process_journal_to_story(journal_id: str):
    """Process a journal entry into a story (trigger story generation agent)"""
    # This endpoint is less relevant now as stories are generated on save,
    # but can be kept for reprocessing.
    # In a real app, this would fetch the raw entry, not the story.
    return {"status": "processed"}


@router.post("/chat", response_model=JournalChatResponse)
async def journal_chat(request: JournalChatRequest):
    """
    Chat with the AI journal companion
    """
    try:
        from app.services.gemini_service import gemini_service
        
        # Build conversation context
        history = ""
        if request.conversation:
            for msg in request.conversation[-5:]: # Keep last 5 messages for context
                history += f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}\n"
                
        prompt = f"""Conversation History:
{history}
The professional just said: "{request.message}"

Respond as a warm journal conversation partner. Ask a follow-up question or reflect on what they shared based on the history. Keep it conversational and short."""
        
        response = await gemini_service.generate_content(
            prompt=prompt,
            model="gemini-2.5-flash",
            system_instruction=JOURNAL_SYSTEM_PROMPT,
            temperature=0.8,
            max_output_tokens=256,
        )
        
        return JournalChatResponse(
            response=response,
            conversation_length=1,
        )
        
    except Exception as e:
        logger.error(f"Error in journal chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save", response_model=JournalCompleteResponse)
async def save_journal(request: JournalCompleteRequest, http_request: Request):
    """
    Save the journal entry. The story will be generated by background agents.
    """
    try:
        from datetime import datetime
        import uuid
        
        # Create a journal entry ID
        entry_id = str(uuid.uuid4())
        
        logger.info(f"Saving journal entry {entry_id} for professional {request.professional_id}")
        
        # Format conversation for story generation
        journal_entry = {
            "id": entry_id,
            "professional_id": request.professional_id,
            "professional_name": request.professional_name,
            "profession": request.profession,
            "conversation": request.conversation or request.messages or [],
        }
        
        generated = await _generate_story_from_entry(journal_entry)
        
        return JournalCompleteResponse(
            story_title=generated["story_title"],
            story_content=generated["story_content"],
            status="completed",
        )
        
    except Exception as e:
        logger.error(f"Error saving journal: {e}")
        raise HTTPException(status_code=500, detail=str(e))