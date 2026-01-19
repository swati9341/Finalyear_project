# College-project-

Short README for the repository.

This repository contains a Backend implementation for an Automated Invoice System (FastAPI).

Quick links
- Backend README: `Backend/README.md` — how to run the server, Swagger UI, and notes about the DB and hashing.
- Swagger UI: http://127.0.0.1:8000/docs (when server is running)
- ER diagram: `docs/er_diagram.puml` (PlantUML source) and `docs/er_diagram.svg` (rendered SVG).

## Running the Backend

To run the backend server:

```powershell
cd Backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

ER diagram
- The ER diagram describes these main entities: `user`, `customer`, `invoice`, `invoice_item`.

