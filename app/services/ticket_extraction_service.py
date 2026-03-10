"""
Ticket extraction service.

Contains the mock extractor and the interface that real OCR providers will implement.
Replace `extract_ticket_data_mock` with a call to Google Document AI, AWS Textract, etc.
"""
import logging
import random
import uuid
from datetime import date, timedelta
from typing import Optional

from app.schemas.ticket_schema import TicketExtractedData
from app.utils.date_parser import parse_date
from app.utils.currency_parser import parse_amount
from app.utils.cuit_parser import normalize_cuit
from app.utils.exceptions import ExtractionError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------


async def extract_from_image(
    file_bytes: bytes,
    content_type: str,
    provider: str = "mock",
) -> TicketExtractedData:
    """
    Entry point for ticket data extraction.
    Routes to the appropriate OCR provider.
    """
    logger.info("Extracting ticket data using provider=%s", provider)

    if provider == "mock":
        return await extract_ticket_data_mock(file_bytes, content_type)

    # Future providers:
    # if provider == "google_document_ai":
    #     return await extract_with_google_document_ai(file_bytes, content_type)
    # if provider == "aws_textract":
    #     return await extract_with_aws_textract(file_bytes, content_type)

    raise ExtractionError(f"Unknown OCR provider: {provider}")


# ---------------------------------------------------------------------------
# Mock extractor – replace with real implementation later
# ---------------------------------------------------------------------------


async def extract_ticket_data_mock(
    file_bytes: bytes,
    content_type: str,
) -> TicketExtractedData:
    """
    Mock extractor that returns realistic, consistent Argentine ticket data.
    This function must be replaced with a real OCR call in production.
    """
    logger.debug("Running mock ticket extraction (file size=%d bytes)", len(file_bytes))

    # Simulate variable confidence based on image size (larger = more "confident")
    confidence = min(0.95, 0.60 + (len(file_bytes) / (1024 * 1024)) * 0.15)

    # Build a realistic Argentine invoice
    sample_companies = [
        ("30-71234567-8", "SUPERMERCADO LA ESQUINA S.A."),
        ("20-23456789-4", "FARMACIA DEL PUEBLO SRL"),
        ("30-68901234-1", "FERRETERÍA SAN MARTÍN SA"),
        ("27-12345678-3", "LIBRERÍA Y PAPELERÍA CENTRAL"),
        ("30-70000001-2", "RESTAURANTE EL BUEN SABOR SRL"),
    ]
    company = random.choice(sample_companies)

    subtotal = round(random.uniform(500, 15000), 2)
    iva_rate = 0.21
    iva = round(subtotal * iva_rate, 2)
    importe_total = round(subtotal + iva, 2)

    # A date in the last 90 days
    days_ago = random.randint(0, 90)
    fecha = (date.today() - timedelta(days=days_ago)).isoformat()

    tipos = ["FACTURA A", "FACTURA B", "TICKET", "REMITO", "NOTA DE CREDITO"]
    tipo = random.choice(tipos)
    punto_venta = str(random.randint(1, 9)).zfill(4)
    numero = str(random.randint(1, 99999)).zfill(8)

    raw_text = (
        f"{company[1]}\n"
        f"CUIT: {company[0]}\n"
        f"Av. Corrientes 1234, Buenos Aires\n"
        f"{tipo} Nro. {punto_venta}-{numero}\n"
        f"Fecha: {fecha}\n"
        f"Subtotal: ${subtotal:,.2f}\n"
        f"IVA 21%: ${iva:,.2f}\n"
        f"TOTAL: ${importe_total:,.2f}\n"
    )

    return TicketExtractedData(
        cuit=normalize_cuit(company[0]),
        razon_social=company[1],
        importe_total=importe_total,
        subtotal=subtotal,
        iva=iva,
        moneda="ARS",
        fecha_emision=fecha,
        tipo_comprobante=tipo,
        numero_comprobante=f"{punto_venta}-{numero}",
        punto_venta=punto_venta,
        domicilio_comercial="Av. Corrientes 1234, Buenos Aires",
        categoria_sugerida=None,  # Never invent categories
        texto_crudo_ocr=raw_text,
        confianza_extraccion=round(confidence, 4),
    )
