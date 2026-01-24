from fastapi import FastAPI
from routers import auth
from database import Base, engine
from routers import invoices
from routers import template_router
from models import user, invoice, invoice_item, invoice_template

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Automated Invoice System",
    description=(
        "Simple backend to create invoices from JSON and generate PDF files. "
        "Endpoints: POST /invoices/create, GET /invoices/{id}, GET /invoices/{id}/pdf. "
        "Also includes invoice template management."
    ),
    version="0.1.0",
    contact={"name": "Project Owner", "email": "owner@example.com"},
    license_info={"name": "MIT"},
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "docExpansion": "none",
    },
    # nicer grouping and descriptions for the OpenAPI docs
    openapi_tags=[
        {"name": "Auth", "description": "Endpoints to register and authenticate users."},
        {"name": "Invoices", "description": "Create invoices and generate PDF representations."},
        {"name": "Invoice Templates", "description": "Manage invoice templates."},
    ],
)

app.include_router(auth.router)
app.include_router(invoices.router)
app.include_router(template_router.router)


@app.get("/")
def root():
    return {"message": "Backend running"}
