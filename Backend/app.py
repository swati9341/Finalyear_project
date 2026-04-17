import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables FIRST, before importing anything else
dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    print("WARNING: .env file not found. Environment variables might not be loaded.")

from fastapi import FastAPI
from routers import auth
from routers import template_router
from routers import invoice_item_router,  home_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Automated Invoice System",
    description=(
        "Simple backend to create invoices from JSON and generate PDF files. "
        "Endpoints: POST /invoices/create, GET /invoices/{id}, GET /invoices/{id}/pdf, POST /invoice_items/ (with invoice_id, userId, description, data), GET /invoice_items/, GET /invoice_items/{item_id}, GET /demo/invoice. " # Updated description
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
        {"name": "Demo Data", "description": "Endpoints for retrieving demo data from the database."}, # Added Demo Data tag
        {"name": "Invoice Templates", "description": "Manage invoice templates."},
    ],
)

app.include_router(auth.router)
app.include_router(template_router.router)
app.include_router(invoice_item_router.router) # Included new router
app.include_router(home_router.router) # Included new home router
