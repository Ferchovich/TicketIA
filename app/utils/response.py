"""Standard response helpers for TicketIA API."""
from typing import Any, Optional
from quart import jsonify


def success_response(
    data: Any = None,
    message: str = "OK",
    status_code: int = 200,
):
    """Return a standardized success response."""
    payload = {
        "success": True,
        "message": message,
        "data": data,
        "errors": None,
    }
    return jsonify(payload), status_code


def error_response(
    message: str,
    errors: Optional[Any] = None,
    status_code: int = 400,
):
    """Return a standardized error response."""
    payload = {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors,
    }
    return jsonify(payload), status_code


def paginated_response(
    data: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "OK",
):
    """Return a standardized paginated response."""
    payload = {
        "success": True,
        "message": message,
        "data": data,
        "errors": None,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
        },
    }
    return jsonify(payload), 200
