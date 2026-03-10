"""Common Pydantic schemas shared across the application."""
from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[Any] = None


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedAPIResponse(APIResponse):
    pagination: Optional[PaginationMeta] = None
