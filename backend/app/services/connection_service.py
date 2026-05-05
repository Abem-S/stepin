"""Connection Request Service - Real connection workflow"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID


class ConnectionRequestService:
    """Service for managing real connection requests between students and professionals"""
    
    def __init__(self):
        # In-memory mock storage
        self._requests: dict = {}
    
    async def create_request(
        self,
        student_id: UUID,
        professional_id: UUID,
        session_id: UUID,
        message: Optional[str] = None,
    ) -> dict:
        """Create a new connection request"""
        request_id = UUID()
        
        request = {
            "id": request_id,
            "student_id": student_id,
            "professional_id": professional_id,
            "session_id": session_id,
            "status": "pending",
            "student_message": message,
            "professional_response": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        self._requests[str(request_id)] = request
        return request
    
    async def get_request(self, request_id: UUID) -> Optional[dict]:
        """Get a connection request by ID"""
        return self._requests.get(str(request_id))
    
    async def get_requests_by_student(
        self,
        student_id: UUID,
    ) -> List[dict]:
        """Get all connection requests for a student"""
        return [
            r for r in self._requests.values()
            if str(r["student_id"]) == str(student_id)
        ]
    
    async def get_requests_by_professional(
        self,
        professional_id: UUID,
    ) -> List[dict]:
        """Get all connection requests for a professional"""
        return [
            r for r in self._requests.values()
            if str(r["professional_id"]) == str(professional_id)
        ]
    
    async def get_pending_requests(
        self,
        professional_id: UUID,
    ) -> List[dict]:
        """Get pending connection requests for a professional"""
        return [
            r for r in self._requests.values()
            if str(r["professional_id"]) == str(professional_id)
            and r["status"] == "pending"
        ]
    
    async def update_request_status(
        self,
        request_id: UUID,
        status: str,  # "accepted" or "declined"
        response_message: Optional[str] = None,
    ) -> Optional[dict]:
        """Update a connection request status"""
        request = self._requests.get(str(request_id))
        if not request:
            return None
        
        request["status"] = status
        request["professional_response"] = response_message
        request["updated_at"] = datetime.utcnow()
        
        self._requests[str(request_id)] = request
        return request
    
    async def get_stats_by_professional(
        self,
        professional_id: UUID,
    ) -> dict:
        """Get connection request statistics for a professional"""
        requests = await self.get_requests_by_professional(professional_id)
        
        pending = [r for r in requests if r["status"] == "pending"]
        accepted = [r for r in requests if r["status"] == "accepted"]
        declined = [r for r in requests if r["status"] == "declined"]
        
        return {
            "total": len(requests),
            "pending": len(pending),
            "accepted": len(accepted),
            "declined": len(declined),
        }


# Singleton instance
connection_request_service = ConnectionRequestService()