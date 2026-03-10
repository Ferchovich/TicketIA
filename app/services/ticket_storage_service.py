"""Ticket storage service - orchestrates saving ticket data to Supabase tables."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.schemas.ticket_schema import TicketCreate
from app.repositories.ticket_repository import TicketRepository
from app.repositories.raw_document_repository import RawDocumentRepository
from app.utils.exceptions import DatabaseError, StorageError

logger = logging.getLogger(__name__)


class TicketStorageService:
    def __init__(self, client):
        self._ticket_repo = TicketRepository(client)
        self._doc_repo = RawDocumentRepository(client)
        self._client = client

    async def save_ticket(
        self,
        ticket_data: TicketCreate,
        original_filename: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> dict:
        """
        Save a ticket and its associated data to the database.
        Creates entries in: tickets, ticket_raw_texts, ticket_extraction_logs.
        """
        now = datetime.now(timezone.utc).isoformat()

        # 1. Save document metadata if we have file info
        document_id = ticket_data.document_id
        if not document_id and original_filename:
            try:
                doc = await self._doc_repo.create_document({
                    "id": str(uuid.uuid4()),
                    "original_filename": original_filename,
                    "mime_type": mime_type or "application/octet-stream",
                    "storage_path": None,
                    "public_url": None,
                    "uploaded_by": None,
                    "created_at": now,
                })
                document_id = doc.get("id")
            except Exception as exc:
                logger.warning("Could not save document metadata: %s", exc)

        # 2. Determine status
        status = ticket_data.status
        if not ticket_data.category_id and status == "saved":
            status = "pending_category"

        # 3. Save ticket record
        ticket_record = {
            "id": str(uuid.uuid4()),
            "document_id": document_id,
            "category_id": ticket_data.category_id,
            "cuit": ticket_data.cuit,
            "razon_social": ticket_data.razon_social,
            "importe_total": ticket_data.importe_total,
            "subtotal": ticket_data.subtotal,
            "iva": ticket_data.iva,
            "moneda": ticket_data.moneda or "ARS",
            "fecha_emision": ticket_data.fecha_emision,
            "tipo_comprobante": ticket_data.tipo_comprobante,
            "numero_comprobante": ticket_data.numero_comprobante,
            "punto_venta": ticket_data.punto_venta,
            "domicilio_comercial": ticket_data.domicilio_comercial,
            "extraction_confidence": ticket_data.extraction_confidence,
            "status": status,
            "created_at": now,
            "updated_at": now,
        }

        ticket = await self._ticket_repo.create(ticket_record)
        ticket_id = ticket["id"]

        # 4. Save raw OCR text
        if ticket_data.raw_text:
            try:
                await self._doc_repo.create_raw_text({
                    "id": str(uuid.uuid4()),
                    "ticket_id": ticket_id,
                    "raw_text": ticket_data.raw_text,
                    "provider_name": ticket_data.ocr_provider or "mock",
                    "created_at": now,
                })
            except Exception as exc:
                logger.warning("Could not save raw text: %s", exc)

        # 5. Log successful extraction
        try:
            await self._ticket_repo.log_extraction({
                "id": str(uuid.uuid4()),
                "ticket_id": ticket_id,
                "stage": "save",
                "success": True,
                "message": "Ticket saved successfully",
                "payload_json": None,
                "created_at": now,
            })
        except Exception as exc:
            logger.warning("Could not write extraction log: %s", exc)

        return ticket
