from fastapi import APIRouter
from backend.core.rate_limiter import gemini_rate_limiter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Simple endpoint to check that the ClauseGuard API server is online."""
    return {"status": "ClauseGuard API is running"}


@router.get("/health/rate-limiter")
def rate_limiter_status():
    """Returns current Gemini API quota usage (useful for monitoring)."""
    return gemini_rate_limiter.status()
