"""Ticket repository - handles all DB operations for tickets."""
import logging
from typing import Optional
from app.utils.exceptions import DatabaseError, NotFoundError

logger = logging.getLogger(__name__)


class TicketRepository:
    def __init__(self, client):
        self._client = client

    async def create(self, data: dict) -> dict:
        try:
            result = self._client.table("tickets").insert(data).execute()
            return result.data[0]
        except Exception as exc:
            logger.error("Error creating ticket: %s", exc)
            raise DatabaseError(f"Failed to create ticket: {exc}") from exc

    async def find_by_id(self, ticket_id: str) -> dict:
        try:
            result = (
                self._client.table("tickets")
                .select("*")
                .eq("id", ticket_id)
                .single()
                .execute()
            )
            if not result.data:
                raise NotFoundError(f"Ticket {ticket_id} not found")
            return result.data
        except NotFoundError:
            raise
        except Exception as exc:
            logger.error("Error fetching ticket %s: %s", ticket_id, exc)
            raise DatabaseError(f"Failed to fetch ticket: {exc}") from exc

    async def find_all(
        self,
        page: int = 1,
        page_size: int = 20,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        cuit: Optional[str] = None,
        razon_social: Optional[str] = None,
        categoria_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[dict], int]:
        try:
            query = self._client.table("tickets").select("*", count="exact")
            if fecha_desde:
                query = query.gte("fecha_emision", fecha_desde)
            if fecha_hasta:
                query = query.lte("fecha_emision", fecha_hasta)
            if cuit:
                query = query.eq("cuit", cuit)
            if razon_social:
                query = query.ilike("razon_social", f"%{razon_social}%")
            if categoria_id:
                query = query.eq("category_id", categoria_id)
            if status:
                query = query.eq("status", status)

            offset = (page - 1) * page_size
            query = query.order("created_at", desc=True).range(offset, offset + page_size - 1)
            result = query.execute()
            total = result.count if result.count is not None else len(result.data or [])
            return result.data or [], total
        except Exception as exc:
            logger.error("Error listing tickets: %s", exc)
            raise DatabaseError(f"Failed to list tickets: {exc}") from exc

    async def update(self, ticket_id: str, data: dict) -> dict:
        try:
            result = (
                self._client.table("tickets")
                .update(data)
                .eq("id", ticket_id)
                .execute()
            )
            if not result.data:
                raise NotFoundError(f"Ticket {ticket_id} not found")
            return result.data[0]
        except NotFoundError:
            raise
        except Exception as exc:
            logger.error("Error updating ticket %s: %s", ticket_id, exc)
            raise DatabaseError(f"Failed to update ticket: {exc}") from exc

    async def log_extraction(self, data: dict) -> dict:
        try:
            result = (
                self._client.table("ticket_extraction_logs").insert(data).execute()
            )
            return result.data[0]
        except Exception as exc:
            logger.warning("Failed to log extraction event: %s", exc)
            return {}
