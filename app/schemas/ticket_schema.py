"""Pydantic schemas for tickets."""
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, field_validator
from decimal import Decimal

ALLOWED_TICKET_STATUSES = {
    "uploaded",
    "analyzed",
    "pending_category",
    "saved",
    "reviewed",
    "error",
}


class TicketExtractedData(BaseModel):
    """Data extracted from a ticket image."""
    cuit: Optional[str] = None
    razon_social: Optional[str] = None
    importe_total: Optional[float] = None
    subtotal: Optional[float] = None
    iva: Optional[float] = None
    moneda: Optional[str] = "ARS"
    fecha_emision: Optional[str] = None
    tipo_comprobante: Optional[str] = None
    numero_comprobante: Optional[str] = None
    punto_venta: Optional[str] = None
    domicilio_comercial: Optional[str] = None
    categoria_sugerida: Optional[str] = None
    texto_crudo_ocr: Optional[str] = None
    confianza_extraccion: Optional[float] = None


class TicketCreate(BaseModel):
    """Request body for saving a ticket."""
    document_id: Optional[str] = None
    category_id: Optional[str] = None
    cuit: Optional[str] = None
    razon_social: Optional[str] = None
    importe_total: Optional[float] = None
    subtotal: Optional[float] = None
    iva: Optional[float] = None
    moneda: Optional[str] = "ARS"
    fecha_emision: Optional[str] = None
    tipo_comprobante: Optional[str] = None
    numero_comprobante: Optional[str] = None
    punto_venta: Optional[str] = None
    domicilio_comercial: Optional[str] = None
    extraction_confidence: Optional[float] = None
    raw_text: Optional[str] = None
    ocr_provider: Optional[str] = "mock"
    status: str = "saved"

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        if v not in ALLOWED_TICKET_STATUSES:
            raise ValueError(f"status must be one of {ALLOWED_TICKET_STATUSES}")
        return v


class TicketUpdate(BaseModel):
    """Request body for updating a ticket."""
    category_id: Optional[str] = None
    status: Optional[str] = None
    cuit: Optional[str] = None
    razon_social: Optional[str] = None
    importe_total: Optional[float] = None
    subtotal: Optional[float] = None
    iva: Optional[float] = None
    moneda: Optional[str] = None
    fecha_emision: Optional[str] = None
    tipo_comprobante: Optional[str] = None
    numero_comprobante: Optional[str] = None
    punto_venta: Optional[str] = None
    domicilio_comercial: Optional[str] = None

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_TICKET_STATUSES:
            raise ValueError(f"status must be one of {ALLOWED_TICKET_STATUSES}")
        return v


class TicketOut(BaseModel):
    id: str
    document_id: Optional[str] = None
    category_id: Optional[str] = None
    cuit: Optional[str] = None
    razon_social: Optional[str] = None
    importe_total: Optional[float] = None
    subtotal: Optional[float] = None
    iva: Optional[float] = None
    moneda: Optional[str] = None
    fecha_emision: Optional[str] = None
    tipo_comprobante: Optional[str] = None
    numero_comprobante: Optional[str] = None
    punto_venta: Optional[str] = None
    domicilio_comercial: Optional[str] = None
    extraction_confidence: Optional[float] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TicketListFilters(BaseModel):
    """Query parameters for listing tickets."""
    page: int = 1
    page_size: int = 20
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    cuit: Optional[str] = None
    razon_social: Optional[str] = None
    categoria_id: Optional[str] = None
    status: Optional[str] = None
