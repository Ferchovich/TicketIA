-- TicketIA Database Schema for Supabase (PostgreSQL)
-- Run this in your Supabase SQL editor to create all required tables.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. categories
-- ============================================================
CREATE TABLE IF NOT EXISTS categories (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 2. ticket_documents
-- ============================================================
CREATE TABLE IF NOT EXISTS ticket_documents (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_filename TEXT,
    mime_type         TEXT,
    storage_path      TEXT,
    public_url        TEXT,
    uploaded_by       TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 3. tickets
-- ============================================================
CREATE TABLE IF NOT EXISTS tickets (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id           UUID REFERENCES ticket_documents(id) ON DELETE SET NULL,
    category_id           UUID REFERENCES categories(id) ON DELETE SET NULL,
    cuit                  TEXT,
    razon_social          TEXT,
    importe_total         NUMERIC(12, 2),
    subtotal              NUMERIC(12, 2),
    iva                   NUMERIC(12, 2),
    moneda                TEXT DEFAULT 'ARS',
    fecha_emision         DATE,
    tipo_comprobante      TEXT,
    numero_comprobante    TEXT,
    punto_venta           TEXT,
    domicilio_comercial   TEXT,
    extraction_confidence NUMERIC(5, 4),
    status                TEXT NOT NULL DEFAULT 'uploaded'
                            CHECK (status IN ('uploaded','analyzed','pending_category','saved','reviewed','error')),
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tickets_cuit       ON tickets(cuit);
CREATE INDEX IF NOT EXISTS idx_tickets_status     ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_fecha      ON tickets(fecha_emision);
CREATE INDEX IF NOT EXISTS idx_tickets_category   ON tickets(category_id);

-- ============================================================
-- 4. ticket_raw_texts
-- ============================================================
CREATE TABLE IF NOT EXISTS ticket_raw_texts (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id     UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    raw_text      TEXT,
    provider_name TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 5. ticket_extraction_logs
-- ============================================================
CREATE TABLE IF NOT EXISTS ticket_extraction_logs (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id    UUID REFERENCES tickets(id) ON DELETE SET NULL,
    stage        TEXT,
    success      BOOLEAN NOT NULL DEFAULT TRUE,
    message      TEXT,
    payload_json JSONB,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Trigger to auto-update updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_tickets_updated_at
    BEFORE UPDATE ON tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default categories
INSERT INTO categories (name, description) VALUES
    ('Alimentación',    'Supermercados, restaurantes, delivery'),
    ('Transporte',      'Combustible, peajes, transporte público'),
    ('Salud',           'Farmacia, médicos, clínicas'),
    ('Hogar',           'Ferretería, muebles, electrodomésticos'),
    ('Entretenimiento', 'Cine, teatro, streaming'),
    ('Educación',       'Libros, cursos, papelería'),
    ('Servicios',       'Electricidad, gas, internet'),
    ('Otros',           'Gastos no categorizados')
ON CONFLICT (name) DO NOTHING;
