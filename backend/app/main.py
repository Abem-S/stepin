"""
StepIn Platform - FastAPI Backend
Career exploration platform with LangGraph agents and voice AI
"""
import os
import re
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.routes import (
    professionals_router,
    student_journey_router,
    digital_twin_router,
    connections_router,
    agents_router,
    careers_router,
)
from app.routes.interview import router as interview_router
from app.routes import professional as professional_router
from app.routes.journal import router as journal_router
from app.routes.student import router as student_router

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Starting StepIn Platform API...")
    yield
    # Shutdown
    logger.info("Shutting down StepIn Platform API...")


# Create FastAPI app
app = FastAPI(
    title="StepIn Platform API",
    description="Career exploration platform - Professionals share daily stories via voice AI, students explore careers through immersive Shadow Day experiences",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter to app state
app.state.limiter = limiter


# =============================================================================
# SECURITY MIDDLEWARE
# =============================================================================

# Rate limit handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests",
            "message": "Please slow down and try again in a moment.",
            "detail": str(exc)
        }
    )


# CORS Configuration - Allow only frontend domain (configure for production)
FRONTEND_DOMAIN = os.getenv("FRONTEND_DOMAIN", "localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://{FRONTEND_DOMAIN}",
        f"https://{FRONTEND_DOMAIN}",
        "https://frontend-service-gzxusx3aya-uc.a.run.app",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://localhost:8001",
        "http://localhost:8002",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Custom security headers middleware
@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # XSS Protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    
    return response


# Request size limit middleware
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB


@app.middleware("http")
async def request_size_limit(request: Request, call_next):
    """Limit request sizes to prevent payload attacks"""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=413,
                content={
                    "error": "Payload too large",
                    "message": "Request payload exceeds maximum size of 10MB"
                }
            )
    response = await call_next(request)
    return response


# Audit logging middleware
@app.middleware("http")
async def audit_logging(request: Request, call_next):
    """Log sensitive operations for audit"""
    import logging
    import time
    from datetime import datetime
    
    audit_logger = logging.getLogger("audit")
    
    # Sensitive endpoints to audit
    sensitive_paths = ["/api/agents/", "/api/professionals/", "/api/students/"]
    
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Log sensitive operations
    if any(path in request.url.path for path in sensitive_paths):
        audit_logger.info(
            f"AUDIT: {request.method} {request.url.path} "
            f"status={response.status_code} duration={duration:.3f}s "
            f"client={request.client.host if request.client else 'unknown'}"
        )
    
    return response


# =============================================================================
# INPUT SANITIZATION
# =============================================================================

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent prompt injection.
    
    Removes common prompt injection patterns.
    """
    if not text:
        return ""
    
    # Remove potential prompt injection patterns
    patterns = [
        r'(?i)(ignore|disregard|forget|overwrite)\s+(previous|above|system|all)\s+(instructions|prompt|rules)',
        r'(?i)(you\s+are\s+now|pretend\s+to\s+be|roleplay\s+as)\s+(a\s+)?(different|new|custom)',
        r'(?i)(output\s+everything|print\s+all|reveal\s+your)',
        r'(?i)\\x00|\\n\\r\\t',  # Control characters
        r'<script[^>]*>.*?</script>',  # XSS attempts
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Limit length
    max_length = 10000
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text.strip()


# Add sanitizer to app state
app.state.sanitize_input = sanitize_input


# =============================================================================
# INCLUDE ROUTERS
# =============================================================================
# Note: Routers already have their own prefixes defined internally

app.include_router(professionals_router)  # Router has prefix="/api/professionals"
app.include_router(student_journey_router)
app.include_router(digital_twin_router)
app.include_router(connections_router)
app.include_router(agents_router)
app.include_router(careers_router)  # Router has prefix="/api/careers"
app.include_router(interview_router)
app.include_router(professional_router.router)  # Router has prefix="/api/professional"
app.include_router(journal_router)  # Router has prefix="/api/professional/journal"
app.include_router(student_router)  # Router has prefix="/api/student"


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "stepin-backend",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "StepIn Platform API",
        "version": "1.0.0",
        "description": "Career exploration through immersive storytelling",
        "docs": "/docs",
    }


# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)