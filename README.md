# TicketIA API

REST API for analyzing, extracting, and managing ticket/invoice data using AI-powered OCR. Built with Python + Quart (async) + Supabase.

## Features

- Upload ticket/invoice images and extract structured data
- Store tickets with full audit trail (raw OCR text, extraction logs)
- Manage categories for ticket classification
- Full CRUD for tickets and categories
- Async architecture ready for production
- Mock OCR extractor (swap in Google Document AI, AWS Textract, etc.)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | [Quart](https://quart.palletsprojects.com/) (async Flask-like) |
| ASGI Server | [Hypercorn](https://hypercorn.readthedocs.io/) |
| Database | [Supabase](https://supabase.com/) (PostgreSQL) |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) |
| Image processing | [Pillow](https://pillow.readthedocs.io/) |

## Project Structure

```
app/
├── __init__.py            # App factory
├── main.py                # Entry point
├── config.py              # Settings (pydantic-settings)
├── extensions.py          # Supabase client helpers
├── routes/                # HTTP route handlers
│   ├── health.py
│   ├── tickets.py
│   ├── categories.py
│   └── providers.py
├── services/              # Business logic
│   ├── ticket_extraction_service.py
│   ├── ticket_storage_service.py
│   └── image_preprocessing_service.py
├── repositories/          # Database access layer
│   ├── ticket_repository.py
│   ├── category_repository.py
│   └── raw_document_repository.py
├── schemas/               # Pydantic models
│   ├── ticket_schema.py
│   ├── category_schema.py
│   └── common_schema.py
└── utils/
    ├── exceptions.py      # Custom exceptions
    ├── response.py        # Standard response helpers
    ├── date_parser.py
    ├── currency_parser.py
    └── cuit_parser.py
tests/
sql/
└── schema.sql             # Supabase table definitions
```

## Installation

### Prerequisites

- Python 3.12+
- A [Supabase](https://supabase.com/) project

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Ferchovich/TicketIA.git
cd TicketIA

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials and settings

# 5. Create database tables
# Copy the contents of sql/schema.sql and run in your Supabase SQL editor

# 6. Start the server
python -m app.main
# or
hypercorn app.main:app --bind 0.0.0.0:8000
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Environment (development/production) | `development` |
| `APP_PORT` | Server port | `8000` |
| `APP_HOST` | Server host | `0.0.0.0` |
| `APP_SECRET_KEY` | Secret key for sessions | `change-me-in-production` |
| `SUPABASE_URL` | Your Supabase project URL | required |
| `SUPABASE_KEY` | Supabase anon key | required |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | required |
| `MAX_UPLOAD_MB` | Maximum upload file size in MB | `10` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000` |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | `INFO` |

## API Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Service health check |

### Tickets
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/tickets/analyze` | Upload image and extract data (no DB save) |
| POST | `/api/tickets` | Save an analyzed ticket |
| GET | `/api/tickets` | List tickets (with filters & pagination) |
| GET | `/api/tickets/<id>` | Get ticket detail |
| PATCH | `/api/tickets/<id>` | Update ticket (category, status, corrections) |

### Categories
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/categories` | List all categories |
| POST | `/api/categories` | Create category |
| PATCH | `/api/categories/<id>` | Update category |
| DELETE | `/api/categories/<id>` | Delete category (if not in use) |

### Providers
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/providers` | List available OCR providers |

## Example Payloads

### POST /api/tickets/analyze (multipart/form-data)
```
image: <file>
provider: mock   (optional, default: mock)
```

### POST /api/tickets
```json
{
  "cuit": "30-71234567-8",
  "razon_social": "SUPERMERCADO LA ESQUINA S.A.",
  "importe_total": 1452.30,
  "subtotal": 1200.00,
  "iva": 252.30,
  "moneda": "ARS",
  "fecha_emision": "2024-03-15",
  "tipo_comprobante": "FACTURA B",
  "numero_comprobante": "0001-00012345",
  "punto_venta": "0001",
  "domicilio_comercial": "Av. Corrientes 1234, Buenos Aires",
  "category_id": "uuid-here",
  "raw_text": "Raw OCR text...",
  "extraction_confidence": 0.92
}
```

### GET /api/tickets (query params)
```
?page=1&page_size=20
&fecha_desde=2024-01-01&fecha_hasta=2024-12-31
&cuit=30712345678
&razon_social=supermercado
&status=saved
```

### PATCH /api/tickets/<id>
```json
{
  "category_id": "uuid-here",
  "status": "reviewed"
}
```

## Running Tests

```bash
pytest tests/ -v
```

## Standard Response Format

All endpoints return a consistent JSON structure:

```json
{
  "success": true,
  "message": "Description of result",
  "data": { ... },
  "errors": null
}
```

Paginated responses include an extra `pagination` key:
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

## Ticket States

| Status | Description |
|--------|-------------|
| `uploaded` | File received, not yet analyzed |
| `analyzed` | OCR extraction completed |
| `pending_category` | Awaiting category assignment |
| `saved` | Fully saved with category |
| `reviewed` | Manually reviewed and confirmed |
| `error` | Extraction or saving failed |

## Replacing the Mock OCR

In `app/services/ticket_extraction_service.py`, the `extract_from_image()` function routes to providers. To add a real provider:

1. Add a new `extract_with_<provider>()` async function
2. Add a new `elif provider == "<id>":` branch in `extract_from_image()`
3. Update `AVAILABLE_PROVIDERS` in `app/routes/providers.py`

## Security Notes

- File type and size are validated before processing
- Stack traces are never exposed to clients
- Inputs are sanitized via Pydantic validators
- CORS is restricted to configured origins
- Secrets are loaded from environment variables only
- Bearer token authentication can be added as a Quart middleware

## License

MIT
