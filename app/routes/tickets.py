"""Ticket routes."""
import json as _json
import logging
from datetime import datetime, timezone
from quart import Blueprint, request
from pydantic import ValidationError as PydanticValidationError

from app.extensions import get_supabase_client
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket_schema import TicketCreate, TicketUpdate, TicketListFilters
from app.services.image_preprocessing_service import validate_file, preprocess_image
from app.services.ticket_extraction_service import extract_from_image
from app.services.ticket_storage_service import TicketStorageService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.exceptions import (
    NotFoundError,
    DatabaseError,
    FileTooLargeError,
    UnsupportedFileTypeError,
    ExtractionError,
    ValidationError,
)

logger = logging.getLogger(__name__)

tickets_bp = Blueprint("tickets", __name__)


def _get_ticket_repo():
    client = get_supabase_client()
    if client is None:
        raise DatabaseError("Database connection is not available")
    return TicketRepository(client)


def _get_storage_service():
    client = get_supabase_client()
    if client is None:
        raise DatabaseError("Database connection is not available")
    return TicketStorageService(client)


@tickets_bp.post("/tickets/analyze")
async def analyze_ticket():
    """
    Receive an image upload, run extraction, and return extracted fields.
    Does NOT save to database - use POST /tickets for that.
    """
    try:
        files = await request.files
        if "image" not in files:
            return error_response("No image file provided (field name: 'image')", status_code=400)

        file = files["image"]
        file_bytes = file.read()
        filename = file.filename or "upload"
        content_type = file.content_type or "application/octet-stream"

        # Validate
        validate_file(filename, content_type, len(file_bytes))

        # Preprocess
        processed_bytes, _ = await preprocess_image(file_bytes, content_type)

        # Extract
        form_data = await request.form
        provider = form_data.get("provider", "mock")
        extracted = await extract_from_image(processed_bytes, content_type, provider=provider)

        return success_response(
            data=extracted.model_dump(),
            message="Ticket analyzed successfully",
        )

    except (FileTooLargeError, UnsupportedFileTypeError) as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except ExtractionError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Unexpected error analyzing ticket")
        return error_response("Internal server error", status_code=500)


@tickets_bp.post("/tickets")
async def create_ticket():
    """Save an analyzed ticket to the database."""
    try:
        body = await request.get_json(force=True, silent=True) or {}
        schema = TicketCreate(**body)
    except PydanticValidationError as exc:
        return error_response("Validation error", errors=_json.loads(exc.json()), status_code=422)

    try:
        service = _get_storage_service()
        ticket = await service.save_ticket(schema)
        return success_response(data=ticket, message="Ticket saved", status_code=201)
    except DatabaseError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Unexpected error saving ticket")
        return error_response("Internal server error", status_code=500)


@tickets_bp.get("/tickets")
async def list_tickets():
    """List tickets with filtering and pagination."""
    try:
        args = request.args
        filters = TicketListFilters(
            page=int(args.get("page", 1)),
            page_size=int(args.get("page_size", 20)),
            fecha_desde=args.get("fecha_desde"),
            fecha_hasta=args.get("fecha_hasta"),
            cuit=args.get("cuit"),
            razon_social=args.get("razon_social"),
            categoria_id=args.get("categoria_id"),
            status=args.get("status"),
        )
    except (ValueError, PydanticValidationError) as exc:
        return error_response("Invalid query parameters", status_code=400)

    try:
        repo = _get_ticket_repo()
        tickets, total = await repo.find_all(
            page=filters.page,
            page_size=filters.page_size,
            fecha_desde=filters.fecha_desde,
            fecha_hasta=filters.fecha_hasta,
            cuit=filters.cuit,
            razon_social=filters.razon_social,
            categoria_id=filters.categoria_id,
            status=filters.status,
        )
        return paginated_response(
            data=tickets,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )
    except DatabaseError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Unexpected error listing tickets")
        return error_response("Internal server error", status_code=500)


@tickets_bp.get("/tickets/<ticket_id>")
async def get_ticket(ticket_id: str):
    """Get full ticket detail."""
    try:
        repo = _get_ticket_repo()
        ticket = await repo.find_by_id(ticket_id)
        return success_response(data=ticket, message="Ticket found")
    except NotFoundError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except DatabaseError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Unexpected error fetching ticket %s", ticket_id)
        return error_response("Internal server error", status_code=500)


@tickets_bp.patch("/tickets/<ticket_id>")
async def update_ticket(ticket_id: str):
    """Patch a ticket (category, status, manual corrections)."""
    try:
        body = await request.get_json(force=True, silent=True) or {}
        schema = TicketUpdate(**body)
    except PydanticValidationError as exc:
        return error_response("Validation error", errors=_json.loads(exc.json()), status_code=422)

    update_data = schema.model_dump(exclude_none=True)
    if not update_data:
        return error_response("No fields to update", status_code=400)

    try:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        repo = _get_ticket_repo()
        ticket = await repo.update(ticket_id, update_data)
        return success_response(data=ticket, message="Ticket updated")
    except NotFoundError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except DatabaseError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Unexpected error updating ticket %s", ticket_id)
        return error_response("Internal server error", status_code=500)
