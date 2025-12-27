"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Status information indicating the service is healthy.
    """
    return {"status": "healthy"}


