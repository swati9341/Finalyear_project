# College-project-

Short README for the repository.

This repository contains a Backend (FastAPI) and Frontend (Streamlit) implementation for an Automated Invoice System.

## Features

- **Backend**: User registration and login, invoice creation from templates, invoice item management, invoice template management.
- **Frontend**: Streamlit UI for login/signup, template selection, invoice generation, integrated with backend APIs.
- **Database**: SQLite (default) or MySQL support. Tables: `users`, `invoices`, `invoice_items`, `invoice_templates`.

Quick links
- Backend README: `Backend/README.md` — detailed setup, API docs, and notes.
- Swagger UI: http://127.0.0.1:8000/docs (when backend is running)
- ER diagram: `docs/er_diagram.puml` (PlantUML source) and `docs/er_diagram.svg` (rendered SVG).

## API Endpoints

### Invoice Items
- `POST /invoice_items/` - Create a new invoice item
- `POST /invoice_items/create-from-template` - Create invoice from a template
- `GET /invoice_items/` - List all invoice items
- `GET /invoice_items/{item_id}` - Get invoice item by ID

### Templates
- `POST /templates/create` - Create a new invoice template
- `GET /templates/` - List all templates
- `GET /templates/{template_id}` - Get template by ID

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user

## Running Both Frontend and Backend

To run both frontend and backend simultaneously, use the provided batch script:

```powershell
.\run.bat
```

This will start:
- Backend: http://127.0.0.1:8000 (with Swagger UI at http://127.0.0.1:8000/docs)
- Frontend: http://localhost:8501

## Running Backend Only

To run the backend server:

```powershell
cd Backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Running Frontend Only

To run the Streamlit frontend:

```powershell
cd Frontend
streamlit run frontend.py
```

Access the frontend at `http://localhost:8501`.

## Latest Changes

- Added `POST /invoice_items/create-from-template` endpoint to create invoices from templates
- Implemented invoice template selection and management in frontend
- Added comprehensive logging to auth and JWT modules for debugging
- Created `run.bat` script to easily start both frontend and backend
- Fixed template fetching - removed unnecessary user_id parameter
- Added demo invoices endpoint for retrieving user invoices

ER diagram
- The ER diagram describes these main entities: `user`, `invoice`, `invoice_item`, `invoice_template`.

