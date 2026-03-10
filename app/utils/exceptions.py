"""Custom exception hierarchy for TicketIA API."""
from typing import Optional, Any


class TicketIABaseError(Exception):
    """Base exception for all TicketIA errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details


class ValidationError(TicketIABaseError):
    """Raised when input validation fails."""
    status_code = 422
    error_code = "VALIDATION_ERROR"


class NotFoundError(TicketIABaseError):
    """Raised when a requested resource is not found."""
    status_code = 404
    error_code = "NOT_FOUND"


class StorageError(TicketIABaseError):
    """Raised when a storage operation fails."""
    status_code = 500
    error_code = "STORAGE_ERROR"


class ExtractionError(TicketIABaseError):
    """Raised when ticket data extraction fails."""
    status_code = 422
    error_code = "EXTRACTION_ERROR"


class DatabaseError(TicketIABaseError):
    """Raised when a database operation fails."""
    status_code = 500
    error_code = "DATABASE_ERROR"


class FileTooLargeError(TicketIABaseError):
    """Raised when uploaded file exceeds size limit."""
    status_code = 413
    error_code = "FILE_TOO_LARGE"


class UnsupportedFileTypeError(TicketIABaseError):
    """Raised when uploaded file type is not supported."""
    status_code = 415
    error_code = "UNSUPPORTED_FILE_TYPE"


class ConflictError(TicketIABaseError):
    """Raised when a resource conflict occurs (e.g. duplicate)."""
    status_code = 409
    error_code = "CONFLICT"
