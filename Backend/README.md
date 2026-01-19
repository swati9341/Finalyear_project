# Automated Invoice System — Backend

This is a small FastAPI backend for creating invoices from a JSON payload and generating PDF invoices.

Quick overview
- Endpoints:
  - POST /auth/register — register user (requires name, email, phone, password)
  - POST /auth/login — login and receive access token
  - POST /invoices/create — create an invoice (JSON request body with user_id, customer details, tax, items)
  - GET /invoices/{id} — get invoice JSON
  - GET /invoices/{id}/pdf — download invoice PDF

Database Schema:
- `users`: id, name, email, phone, password_hash
- `invoices`: id, invoice_number, user_id, customer_name, customer_email, customer_phone, subtotal, tax, total, pdf_path
- `invoice_items`: id, invoice_id, description, quantity, price

Requirements
- Python 3.11+ (project was developed with 3.12)
- Virtual environment (recommended)
- See `requirements.txt` for Python packages.

Local setup (PowerShell)

1. Create and activate venv (if not already created):

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Optional: set DB env vars (for MySQL) or omit to use local SQLite fallback:

```powershell
$env:DB_USER = 'user'
$env:DB_PASS = 'pass'
$env:DB_NAME = 'invoicedb'
$env:DB_HOST = 'localhost'
```

Run the server

```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open the API docs (Swagger UI)

- http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

Notes
- The password hashing uses `bcrypt_sha256` by default (with `bcrypt` as a fallback) so very long passwords are supported without truncation.
- By default the app will fall back to SQLite (file `invoices.db`) if DB env vars are not provided.
- Example request bodies are included in the Pydantic schemas and will show up in Swagger UI.

Next steps you might want
- Add response models with examples for better Swagger responses.
- Add authorization dependencies for protected endpoints and include a security scheme in OpenAPI.
- Replace the local SQLite fallback with a configured MySQL/Postgres DB in production.
