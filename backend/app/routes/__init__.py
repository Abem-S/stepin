# API Routes
from .professionals import router as professionals_router
from .student_journey import router as student_journey_router
from .digital_twin import router as digital_twin_router
from .connections import router as connections_router
from .agents import router as agents_router
from .careers import router as careers_router

__all__ = [
    "professionals_router",
    "student_journey_router",
    "digital_twin_router",
    "connections_router",
    "agents_router",
    "careers_router",
]