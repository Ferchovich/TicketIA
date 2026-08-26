"""Raw document repository - handles ticket_documents and ticket_raw_texts tables."""
import logging
from typing import Optional
from app.utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class RawDocumentRepository:
    def __init__(self, client):
        self._client = client

    async def create_document(self, data: dict) -> dict:
        try:
            result = (
                self._client.table("ticket_documents").insert(data).execute()
            )
            return result.data[0]
        except Exception as exc:
            logger.error("Error creating ticket_document: %s", exc)
            raise DatabaseError(f"Failed to save document metadata: {exc}") from exc

    async def create_raw_text(self, data: dict) -> dict:
        try:
            result = (
                self._client.table("ticket_raw_texts").insert(data).execute()
            )
            return result.data[0]
        except Exception as exc:
            logger.error("Error saving raw text: %s", exc)
            raise DatabaseError(f"Failed to save raw text: {exc}") from exc

    async def find_raw_text_by_ticket(self, ticket_id: str) -> Optional[dict]:
        try:
            result = (
                self._client.table("ticket_raw_texts")
                .select("*")
                .eq("ticket_id", ticket_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            rows = result.data or []
            return rows[0] if rows else None
        except Exception as exc:
            logger.error("Error fetching raw text for ticket %s: %s", ticket_id, exc)
            raise DatabaseError(f"Failed to fetch raw text: {exc}") from exc
