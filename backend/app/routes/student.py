"""
Student profile API - stores and retrieves student DNA in-memory
(Use this until Supabase student_dna table is created without FK constraint)
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/student", tags=["student"])

# In-memory DNA store: { student_id -> dna_dict }
_DNA_STORE: Dict[str, Dict[str, Any]] = {}


def save_student_dna(student_id: str, dna: Dict[str, Any]):
    """Save/merge student DNA into in-memory store + try Supabase."""
    existing = _DNA_STORE.get(student_id, {})
    # Merge arrays (accumulate insights over multiple sessions)
    for key in ["energized_by", "drained_by", "choices_reveal"]:
        old = existing.get(key, [])
        new = dna.get(key, [])
        merged = list(dict.fromkeys(old + new))  # deduplicate while preserving order
        existing[key] = merged
    existing["recommendations"] = dna.get("recommendations", existing.get("recommendations", []))
    existing["career_dna_card_data"] = dna.get("career_dna_card_data", {})
    _DNA_STORE[student_id] = existing
    logger.info(f"[STUDENT DNA] Saved for {student_id}: {list(existing.keys())}")

    # Also try persisting to Supabase (best-effort)
    try:
        from app.database import get_supabase_client
        supabase = get_supabase_client()
        # Try student_dna table first (no FK), then student_strengths as fallback
        for table in ["student_dna", "student_strengths"]:
            try:
                field = "dna" if table == "student_dna" else "strength_map"
                supabase.table(table).upsert(
                    {"student_id": student_id, field: existing},
                    on_conflict="student_id"
                ).execute()
                logger.info(f"[STUDENT DNA] Persisted to {table}")
                break
            except Exception as e:
                logger.warning(f"[STUDENT DNA] {table} upsert failed: {e}")
    except Exception as e:
        logger.warning(f"[STUDENT DNA] DB persist failed (non-fatal): {e}")


@router.get("/dna/{student_id}")
async def get_student_dna(student_id: str):
    """Get student Career DNA — checks in-memory store first, then Supabase."""
    # 1. In-memory first (fastest, works always)
    if student_id in _DNA_STORE:
        return {"found": True, "dna": _DNA_STORE[student_id]}

    # 2. Try Supabase
    try:
        from app.database import get_supabase_client
        supabase = get_supabase_client()
        for table, field in [("student_dna", "dna"), ("student_strengths", "strength_map")]:
            try:
                resp = supabase.table(table).select(field).eq("student_id", student_id).execute()
                if resp.data:
                    dna = resp.data[0].get(field, {})
                    _DNA_STORE[student_id] = dna  # cache it
                    return {"found": True, "dna": dna}
            except Exception:
                continue
    except Exception:
        pass

    return {"found": False, "dna": {}}


@router.post("/dna/{student_id}")
async def upsert_student_dna(student_id: str, body: Dict[str, Any]):
    """Manually save student DNA (called after reflection agent)."""
    save_student_dna(student_id, body)
    return {"saved": True}
