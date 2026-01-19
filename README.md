# College-project-

Short README for the repository.

This repository contains a Backend (FastAPI) and Frontend (Streamlit) implementation for an Automated Invoice System.

## Features

- **Backend**: User registration and login, invoice creation with PDF generation.
- **Frontend**: Streamlit UI for login/signup, integrated with backend APIs.
- **Database**: SQLite (default) or MySQL support. Tables: `users`, `invoices`, `invoice_items`.

Quick links
- Backend README: `Backend/README.md` — detailed setup, API docs, and notes.
- Swagger UI: http://127.0.0.1:8000/docs (when backend is running)
- ER diagram: `docs/er_diagram.puml` (PlantUML source) and `docs/er_diagram.svg` (rendered SVG).

## Running the Backend

To run the backend server:

```powershell
cd Backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Running the Frontend

To run the Streamlit frontend:

```powershell
cd Frontend
streamlit run frontend.py
```

Access the frontend at `http://localhost:8501`.

## Latest Changes

- Removed `customers` table; customer details now stored directly in `invoices`.
- Added `name` and `phone` fields to `users` table.
- Updated invoice creation to include customer info inline.
- Frontend integrated with backend auth APIs.
- Enhanced PDF generation with customer details.

ER diagram
- The ER diagram describes these main entities: `user`, `invoice`, `invoice_item`.

