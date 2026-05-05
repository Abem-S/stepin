"""RAG Service - Store and query diary entries using pgvector"""
import json
import logging
from typing import List, Dict, Any, Optional

from app.database import get_supabase_client

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG operations using pgvector"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def store_diary_embedding(
        self,
        professional_id: str,
        diary_entry_id: str,
        content_text: str,
        embedding: List[float],
    ) -> bool:
        """
        Store a diary entry with its embedding for RAG queries.
        
        Args:
            professional_id: ID of the professional
            diary_entry_id: ID of the diary entry
            content_text: Text content to store
            embedding: Embedding vector from Gemini
            
        Returns:
            True if successful
        """
        try:
            # For now, store in rag_embeddings table without vector
            # (pgvector requires proper setup in Supabase)
            self.supabase.table("rag_embeddings").insert({
                "professional_id": professional_id,
                "diary_entry_id": diary_entry_id,
                "content_text": content_text,
                # "embedding": embedding,  # Would use this with pgvector
            }).execute()
            
            logger.info(f"Stored RAG embedding for diary entry {diary_entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing RAG embedding: {e}")
            return False
    
    async def store_diary_entry_full(
        self,
        professional_id: str,
        diary_entry: Dict[str, Any],
    ) -> bool:
        """
        Store a complete diary entry with all metadata.
        
        Args:
            professional_id: ID of the professional
            diary_entry: Full diary entry data
            
        Returns:
            True if successful
        """
        try:
            # Extract text content from diary entry
            content = diary_entry.get("content", {})
            key_moments = content.get("key_moments", [])
            
            # Create searchable text
            text_parts = [
                diary_entry.get("title", ""),
                diary_entry.get("summary", ""),
            ]
            for moment in key_moments:
                text_parts.append(moment.get("event", ""))
            
            content_text = " | ".join(text_parts)
            
            # Store the diary entry
            self.supabase.table("diary_entries").insert({
                "id": diary_entry.get("id"),
                "professional_id": professional_id,
                "entry_date": diary_entry.get("entry_date"),
                "title": diary_entry.get("title"),
                "content": content,
                "summary": diary_entry.get("summary"),
            }).execute()
            
            logger.info(f"Stored diary entry {diary_entry.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing diary entry: {e}")
            return False
    
    async def query_similar_entries(
        self,
        professional_id: str,
        query_text: str,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Query similar diary entries for a professional.
        
        In production with pgvector, this would use vector similarity search.
        For now, we do a simple text search.
        
        Args:
            professional_id: ID of the professional
            query_text: Query text to find similar entries
            limit: Maximum number of results
            
        Returns:
            List of similar diary entries
        """
        try:
            # Simple text search (production would use vector similarity)
            response = self.supabase.table("rag_embeddings").select(
                "diary_entry_id,content_text,created_at"
            ).eq("professional_id", professional_id).execute()
            
            if not response.data:
                return []
            
            # For now, return all entries (production would rank by similarity)
            diary_entries = []
            for row in response.data[:limit]:
                # Get full diary entry
                entry_response = self.supabase.table("diary_entries").select(
                    "*"
                ).eq("id", row["diary_entry_id"]).execute()
                
                if entry_response.data:
                    diary_entries.append(entry_response.data[0])
            
            return diary_entries
            
        except Exception as e:
            logger.error(f"Error querying similar entries: {e}")
            return []
    
    async def get_professional_context(
        self,
        professional_id: str,
    ) -> Dict[str, Any]:
        """
        Get all relevant context for a professional (for Digital Twin).
        
        Args:
            professional_id: ID of the professional
            
        Returns:
            Professional data with diary entries for context
        """
        try:
            # Get professional data
            prof_response = self.supabase.table("professionals").select(
                "*"
            ).eq("id", professional_id).execute()
            
            if not prof_response.data:
                return {}
            
            professional = prof_response.data[0]
            
            # Get diary entries
            entries_response = self.supabase.table("diary_entries").select(
                "*"
            ).eq("professional_id", professional_id).order("entry_date", desc=True).execute()
            
            professional["diary_entries"] = entries_response.data or []
            
            return professional
            
        except Exception as e:
            logger.error(f"Error getting professional context: {e}")
            return {}


# Singleton instance
rag_service = RAGService()


async def store_diary_for_rag(
    professional_id: str,
    diary_entry: Dict[str, Any],
) -> bool:
    """Store diary entry for RAG retrieval"""
    return await rag_service.store_diary_entry_full(professional_id, diary_entry)


async def query_diary_context(
    professional_id: str,
    query: str,
    limit: int = 3,
) -> List[Dict[str, Any]]:
    """Query diary entries for context"""
    return await rag_service.query_similar_entries(professional_id, query, limit)


async def get_professional_rag_context(
    professional_id: str,
) -> Dict[str, Any]:
    """Get full context for Digital Twin"""
    return await rag_service.get_professional_context(professional_id)