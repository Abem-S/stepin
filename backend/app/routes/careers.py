"""Careers API routes for StepIn"""
import logging
from typing import List, Optional
from uuid import UUID
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query, Request

from app.database import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/careers", tags=["careers"])


def _category_slug(value: str) -> str:
    """Create a stable URL-safe category slug."""
    return "-".join((value or "").strip().lower().replace("_", " ").split())


def _category_key(value: str) -> str:
    """Normalize category labels/slugs for matching across API inputs and DB values."""
    return " ".join((value or "").strip().lower().replace("-", " ").replace("_", " ").split())


@router.get("")
@router.get("/")
async def get_career_categories():
    """Get all career categories with world counts"""
    supabase = get_supabase_client()
    
    categories_map = {}
    
    try:
        # Get all published story experiences directly from Supabase
        response = supabase.table("story_experiences").select("*").eq("is_published", True).execute()
        
        # Group by category and normalize slugs for all stories (including Professional Journey)
        for row in response.data:
            cat = row.get("category", "General")
            if cat not in categories_map:
                categories_map[cat] = {
                    "id": _category_slug(cat),
                    "name": cat,
                    "world_count": 0,
                    "total_students": 0
                }
            categories_map[cat]["world_count"] += 1
            categories_map[cat]["total_students"] += row.get("total_students", 0)
    except Exception as e:
        logger.error(f"Error fetching categories from Supabase: {e}")
    
    # Convert to list
    categories = list(categories_map.values())
    
    # Ensure fallback categories exist for UI consistency
    seed_ids = ["medicine", "technology"]
    for sid in seed_ids:
        if not any(c["id"] == sid for c in categories):
            name = sid.capitalize()
            categories.append({"id": sid, "name": name, "world_count": 0, "total_students": 0})
    
    return {"categories": categories}


@router.get("/recommendations")
async def get_recommendations(
    student_id: Optional[str] = Query(None, description="Student ID for personalized recommendations"),
    strength_map: Optional[str] = Query(None, description="JSON string of strength map"),
):
    """Get career recommendations based on student profile"""
    from app.agents import recommend_careers
    import json
    
    supabase = get_supabase_client()
    
    try:
        # Get strength map from student if not provided
        if not strength_map and student_id:
            student_response = supabase.table("student_strengths").select(
                "strength_map"
            ).eq("student_id", student_id).execute()
            
            if student_response.data:
                strength_map_json = student_response.data[0].get("strength_map", {})
                strength_map = json.dumps(strength_map_json)
        
        # Parse strength map
        strength_map_dict = {}
        if strength_map:
            try:
                strength_map_dict = json.loads(strength_map)
            except:
                pass
        
        # Get available stories
        stories_response = supabase.table("story_experiences").select(
            "id,title,category,professional_id,total_students"
        ).eq("is_published", True).execute()
        
        available_stories = [
            {
                "id": row["id"],
                "title": row["title"],
                "category": row["category"],
                "professional_id": row["professional_id"],
                "total_students": row.get("total_students", 0),
            }
            for row in stories_response.data
        ]
        
        # Get recommendations from agent
        recommendations = await recommend_careers(
            strength_map=strength_map_dict,
            energized_by=strength_map_dict.get("energized_by", []),
            available_stories=available_stories,
        )
        
        return {"recommendations": recommendations}
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        # Return default recommendations
        return {
            "recommendations": [
                {"id": "medicine-1", "title": "Surgical Resident's Tuesday", "category": "Medicine", "relevance_score": 0.9},
                {"id": "technology-1", "title": "Startup Engineer's Launch Day", "category": "Technology", "relevance_score": 0.85},
            ]
        }


@router.get("/{category}/worlds")
async def get_category_worlds(category: str, request: Request, search: Optional[str] = Query(None)):
    """Get all worlds for a specific category, sorted latest first, with optional search"""
    category_value = unquote(category)
    target_category_key = _category_key(category_value)

    supabase = get_supabase_client()
    worlds = []

    try:
        response = (
            supabase.table("story_experiences")
            .select("id,title,category,professional_id,total_students,moment_count,created_at,experience_data")
            .eq("is_published", True)
            .order("created_at", desc=True)
            .execute()
        )

        for row in response.data:
            if _category_key(row.get("category", "")) != target_category_key:
                continue

            # Get professional name from experience_data JSON (safer than column)
            exp_data = row.get("experience_data") or {}
            prof_name = (
                exp_data.get("professional_name")
                or row.get("professional_name")
                or "Anonymous Professional"
            )

            # Client-side search filter (name or title)
            if search:
                q = search.lower()
                if q not in row.get("title", "").lower() and q not in prof_name.lower():
                    continue

            worlds.append({
                "id": row["id"],
                "title": row["title"],
                "category": row["category"],
                "professional_name": prof_name,
                "professional_id": row.get("professional_id"),
                "total_students": row.get("total_students", 0),
                "moment_count": row.get("moment_count", 6),
                "created_at": row.get("created_at"),
            })
    except Exception as e:
        logger.error("Error loading worlds for category '%s': %s", category_value, e)

    return {"category": category_value, "worlds": worlds}



@router.get("/world/{world_id}")
async def get_world_details(world_id: str):
    """Get full world details for Shadow Day experience"""
    supabase = get_supabase_client()
    
    try:
        # Get story experience
        story_response = supabase.table("story_experiences").select(
            "*"
        ).eq("id", world_id).execute()
        
        if not story_response.data:
            raise HTTPException(status_code=404, detail="World not found")
        
        story = story_response.data[0]
        
        # Get professional info
        prof_response = supabase.table("professionals").select(
            "name,profession,years_experience"
        ).eq("id", story.get("professional_id")).execute()
        
        professional = prof_response.data[0] if prof_response.data else {}
        
        return {
            "id": story["id"],
            "title": story["title"],
            "category": story["category"],
            "professional_name": professional.get("name", "Unknown"),
            "profession": professional.get("profession", ""),
            "years_experience": professional.get("years_experience", 0),
            "moment_count": story.get("moment_count", 6),
            "experience_data": story.get("experience_data", {}),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching world details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch world details")