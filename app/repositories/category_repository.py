"""Category repository - handles all DB operations for categories."""
import logging
from typing import Optional
from app.utils.exceptions import DatabaseError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)


class CategoryRepository:
    def __init__(self, client):
        self._client = client

    async def find_all(self) -> list[dict]:
        try:
            result = self._client.table("categories").select("*").order("name").execute()
            return result.data or []
        except Exception as exc:
            logger.error("Error fetching categories: %s", exc)
            raise DatabaseError(f"Failed to fetch categories: {exc}") from exc

    async def find_by_id(self, category_id: str) -> dict:
        try:
            result = (
                self._client.table("categories")
                .select("*")
                .eq("id", category_id)
                .single()
                .execute()
            )
            if not result.data:
                raise NotFoundError(f"Category {category_id} not found")
            return result.data
        except NotFoundError:
            raise
        except Exception as exc:
            logger.error("Error fetching category %s: %s", category_id, exc)
            raise DatabaseError(f"Failed to fetch category: {exc}") from exc

    async def create(self, data: dict) -> dict:
        try:
            result = self._client.table("categories").insert(data).execute()
            return result.data[0]
        except Exception as exc:
            err_str = str(exc).lower()
            if "unique" in err_str or "duplicate" in err_str:
                raise ConflictError(f"Category name already exists") from exc
            logger.error("Error creating category: %s", exc)
            raise DatabaseError(f"Failed to create category: {exc}") from exc

    async def update(self, category_id: str, data: dict) -> dict:
        try:
            result = (
                self._client.table("categories")
                .update(data)
                .eq("id", category_id)
                .execute()
            )
            if not result.data:
                raise NotFoundError(f"Category {category_id} not found")
            return result.data[0]
        except NotFoundError:
            raise
        except Exception as exc:
            logger.error("Error updating category %s: %s", category_id, exc)
            raise DatabaseError(f"Failed to update category: {exc}") from exc

    async def delete(self, category_id: str) -> bool:
        """Delete category only if not in use."""
        try:
            # Check if any tickets reference this category
            tickets = (
                self._client.table("tickets")
                .select("id")
                .eq("category_id", category_id)
                .limit(1)
                .execute()
            )
            if tickets.data:
                raise ConflictError(
                    "Cannot delete category: it is referenced by existing tickets"
                )
            result = (
                self._client.table("categories")
                .delete()
                .eq("id", category_id)
                .execute()
            )
            return True
        except (ConflictError, NotFoundError):
            raise
        except Exception as exc:
            logger.error("Error deleting category %s: %s", category_id, exc)
            raise DatabaseError(f"Failed to delete category: {exc}") from exc
