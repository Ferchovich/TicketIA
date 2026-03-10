"""OCR provider info routes (placeholder for future expansion)."""
import logging
from quart import Blueprint
from app.utils.response import success_response

logger = logging.getLogger(__name__)

providers_bp = Blueprint("providers", __name__)

AVAILABLE_PROVIDERS = [
    {
        "id": "mock",
        "name": "Mock Extractor",
        "description": "Simulated extraction for development and testing",
        "available": True,
    },
    {
        "id": "google_document_ai",
        "name": "Google Document AI",
        "description": "Google Cloud Document AI OCR provider",
        "available": False,
    },
    {
        "id": "aws_textract",
        "name": "AWS Textract",
        "description": "Amazon Web Services Textract OCR provider",
        "available": False,
    },
]


@providers_bp.get("/providers")
async def list_providers():
    """List available OCR providers."""
    return success_response(data=AVAILABLE_PROVIDERS, message="Available OCR providers")
