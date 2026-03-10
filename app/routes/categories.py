"""Category routes."""
import json as _json
import logging
import uuid
from datetime import datetime, timezone
from quart import Blueprint, request
from pydantic import ValidationError as PydanticValidationError

from app.extensions import get_supabase_client
from app.repositories.category_repository import CategoryRepository
from app.schemas.category_schema import CategoryCreate, CategoryUpdate
from app.utils.response import success_response, error_response
from app.utils.exceptions import (
    NotFoundError,
    DatabaseError,
    ConflictError,
)

logger = logging.getLogger(__name__)

categories_bp = Blueprint("categories", __name__)


def _get_repo():
    client = get_supabase_client()
    if client is None:
        raise DatabaseError("Database connection is not available")
    return CategoryRepository(client)


@categories_bp.get("/categories")
async def list_categories():
    """List all categories."""
    try:
        repo = _get_repo()
        categories = await repo.find_all()
        return success_response(data=categories, message=f"Found {len(categories)} categories")
    except DatabaseError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Unexpected error listing categories")
        return error_response("Internal server error", status_code=500)


@categories_bp.post("/categories")
async def create_category():
    """Create a new category."""
    try:
        body = await request.get_json(force=True, silent=True) or {}
        schema = CategoryCreate(**body)
    except PydanticValidationError as exc:
        return error_response("Validation error", errors=_json.loads(exc.json()), status_code=422)

    try:
        now = datetime.now(timezone.utc).isoformat()
        repo = _get_repo()
        category = await repo.create({
            "id": str(uuid.uuid4()),
            "name": schema.name,
            "description": schema.description,
            "created_at": now,
            "updated_at": now,
        })
        return success_response(data=category, message="Category created", status_code=201)
    except ConflictError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except DatabaseError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Unexpected error creating category")
        return error_response("Internal server error", status_code=500)


@categories_bp.patch("/categories/<category_id>")
async def update_category(category_id: str):
    """Update a category."""
    try:
        body = await request.get_json(force=True, silent=True) or {}
        schema = CategoryUpdate(**body)
    except PydanticValidationError as exc:
        return error_response("Validation error", errors=_json.loads(exc.json()), status_code=422)

    update_data = schema.model_dump(exclude_none=True)
    if not update_data:
        return error_response("No fields to update", status_code=400)

    try:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        repo = _get_repo()
        category = await repo.update(category_id, update_data)
        return success_response(data=category, message="Category updated")
    except NotFoundError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except DatabaseError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Unexpected error updating category %s", category_id)
        return error_response("Internal server error", status_code=500)


@categories_bp.delete("/categories/<category_id>")
async def delete_category(category_id: str):
    """Delete a category (only if not in use)."""
    try:
        repo = _get_repo()
        await repo.delete(category_id)
        return success_response(data=None, message="Category deleted")
    except ConflictError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except NotFoundError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except DatabaseError as exc:
        return error_response(exc.message, status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Unexpected error deleting category %s", category_id)
        return error_response("Internal server error", status_code=500)
