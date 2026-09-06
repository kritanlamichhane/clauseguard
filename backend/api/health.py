from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Simple endpoint to check that the ClauseGuard API server is online."""
    return {"status": "ClauseGuard API is running"}
