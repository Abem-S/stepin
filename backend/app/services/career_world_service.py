"""Career World Service - CRUD for Career World JSON with Redis Caching"""
from typing import List, Optional
from uuid import UUID
import json
import logging

from app.database import get_supabase, get_redis

logger = logging.getLogger(__name__)

# Redis cache TTL in seconds (15 minutes)
CAREER_WORLD_CACHE_TTL = 900
CACHE_KEY_PREFIX = "career_world:"
CACHE_KEY_ALL = "career_worlds:all"
CACHE_KEY_CATEGORY = "career_worlds:category:"


class CareerWorldService:
    """Service for managing Career Worlds with Redis caching"""
    
    def __init__(self):
        pass  # Database and Redis clients are retrieved lazily
    
    def _get_db(self):
        return get_supabase()
    
    def _get_redis(self):
        return get_redis()
    
    def _cache_world(self, world: dict) -> None:
        """Cache a career world in Redis"""
        try:
            redis_client = self._get_redis()
            cache_key = f"{CACHE_KEY_PREFIX}{world['id']}"
            redis_client.setex(
                cache_key,
                CAREER_WORLD_CACHE_TTL,
                json.dumps(world)
            )
        except Exception as e:
            logger.warning(f"Failed to cache career world: {e}")
    
    def _invalidate_cache(self, world_id: str = None, category: str = None) -> None:
        """Invalidate relevant cache entries"""
        try:
            redis_client = self._get_redis()
            if world_id:
                redis_client.delete(f"{CACHE_KEY_PREFIX}{world_id}")
            if category:
                redis_client.delete(f"{CACHE_KEY_CATEGORY}{category}")
            # Always invalidate the "all" cache
            redis_client.delete(CACHE_KEY_ALL)
        except Exception as e:
            logger.warning(f"Failed to invalidate cache: {e}")
    
    async def create_world(
        self,
        category: str,
        title: str,
        career_category: str,
        professional_id: UUID,
        key_moments: List[dict],
        emotional_beats: List[dict],
        decision_points: List[dict],
        voice_clip_refs: List[str],
        is_seed: bool = False,
    ) -> dict:
        """Create a new Career World"""
        db = self._get_db()
        world_data = {
            "category": category,
            "title": title,
            "career_category": career_category,
            "professional_id": str(professional_id),
            "world_data": json.dumps({
                "key_moments": key_moments,
                "emotional_beats": emotional_beats,
                "decision_points": decision_points,
                "voice_clip_refs": voice_clip_refs,
            }),
            "is_seed": is_seed,
            "total_students": 0,
        }
        
        response = db.table("career_worlds").insert(world_data).execute()
        world = response.data[0] if response.data else {}
        
        # Cache the new world
        if world:
            self._cache_world(world)
        
        return world
    
    async def get_world(self, world_id: UUID) -> Optional[dict]:
        """Get a Career World by ID - checks cache first"""
        cache_key = f"{CACHE_KEY_PREFIX}{world_id}"
        
        try:
            redis_client = self._get_redis()
            cached = redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for career world {world_id}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis cache read error: {e}")
        
        # Cache miss - fetch from database
        db = self._get_db()
        response = db.table("career_worlds").select("*").eq("id", str(world_id)).execute()
        
        if response.data:
            world = response.data[0]
            self._cache_world(world)
            return world
        
        return None
    
    async def get_worlds_by_category(self, category: str) -> List[dict]:
        """Get all Career Worlds for a category - checks cache first"""
        cache_key = f"{CACHE_KEY_CATEGORY}{category}"
        
        try:
            redis_client = self._get_redis()
            cached = redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for category {category}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis cache read error: {e}")
        
        # Cache miss - fetch from database
        db = self._get_db()
        response = (
            db.table("career_worlds")
            .select("*")
            .eq("category", category)
            .execute()
        )
        
        worlds = response.data if response.data else []
        
        # Cache the results
        if worlds:
            try:
                redis_client = self._get_redis()
                redis_client.setex(cache_key, CAREER_WORLD_CACHE_TTL, json.dumps(worlds))
            except Exception as e:
                logger.warning(f"Redis cache write error: {e}")
        
        return worlds
    
    async def list_all_worlds(self) -> List[dict]:
        """List all Career Worlds - checks cache first"""
        try:
            redis_client = self._get_redis()
            cached = redis_client.get(CACHE_KEY_ALL)
            if cached:
                logger.debug("Cache hit for all career worlds")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis cache read error: {e}")
        
        # Cache miss - fetch from database
        db = self._get_db()
        response = db.table("career_worlds").select("*").execute()
        
        worlds = response.data if response.data else []
        
        # Cache the results
        if worlds:
            try:
                redis_client = self._get_redis()
                redis_client.setex(CACHE_KEY_ALL, CAREER_WORLD_CACHE_TTL, json.dumps(worlds))
            except Exception as e:
                logger.warning(f"Redis cache write error: {e}")
        
        return worlds
    
    async def update_world(self, world_id: UUID, **updates) -> Optional[dict]:
        """Update a Career World"""
        db = self._get_db()
        
        # Handle world_data specially (convert to JSON string)
        if "world_data" in updates and isinstance(updates["world_data"], dict):
            updates["world_data"] = json.dumps(updates["world_data"])
        
        response = (
            db.table("career_worlds")
            .update(updates)
            .eq("id", str(world_id))
            .execute()
        )
        
        if response.data:
            world = response.data[0]
            self._cache_world(world)
            self._invalidate_cache(str(world_id))
            return world
        
        return None
    
    async def increment_student_count(self, world_id: UUID) -> None:
        """Increment the student count for a world"""
        db = self._get_db()
        
        # Get current count
        response = db.table("career_worlds").select("total_students").eq("id", str(world_id)).execute()
        
        if response.data:
            current_count = response.data[0].get("total_students", 0)
            new_count = current_count + 1
            
            db.table("career_worlds").update({"total_students": new_count}).eq("id", str(world_id)).execute()
            
            # Invalidate cache
            self._invalidate_cache(str(world_id))


# Singleton instance
career_world_service = CareerWorldService()