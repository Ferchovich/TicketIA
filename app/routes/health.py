"""Health check routes."""
import logging
from quart import Blueprint
from app.utils.response import success_response

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
async def health_check():
    """Return service health status."""
    return success_response(
        data={"status": "ok", "service": "TicketIA API"},
        message="Service is healthy",
    )
