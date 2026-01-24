from fastapi import FastAPI
from routers import auth
from database import Base, engine
from routers import template_router
from models import user, invoice_item, invoice_template
from routers import invoice_item_router # Added invoice_item_router
from models import user, invoice_item, invoice_template 

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Automated Invoice System",
    description=(
        "Simple backend to create invoices from JSON and generate PDF files. "
        "Endpoints: POST /invoices/create, GET /invoices/{id}, GET /invoices/{id}/pdf. "
        "Endpoints: POST /invoices/create, GET /invoices/{id}, GET /invoices/{id}/pdf, POST /invoice_items/, GET /invoice_items/, GET /invoice_items/{item_id}. " # Updated description
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
        {"name": "Invoice Items", "description": "Manage individual items within invoices."}, # Added Invoice Items tag
        {"name": "Invoice Templates", "description": "Manage invoice templates."},
    ],
)

app.include_router(auth.router)
app.include_router(template_router.router)
app.include_router(invoice_item_router.router) # Included new router


@app.get("/")
def root():
    return {"message": "Backend running"}
