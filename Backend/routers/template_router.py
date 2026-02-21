from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.invoice_template import InvoiceTemplate as InvoiceTemplateModel
from schemas.template_schema import (
    InvoiceTemplateCreate,
    InvoiceTemplate as InvoiceTemplateSchema
)
from utils.db_helpers import create_record, read_record, list_records

router = APIRouter(prefix="/templates", tags=["Invoice Templates"])


# ✅ DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Create Invoice Template
@router.post(
    "/create",
    response_model=InvoiceTemplateSchema,
    summary="Create an invoice template"
)
def create_template(data: InvoiceTemplateCreate, db: Session = Depends(get_db)):

    template = InvoiceTemplateModel(
        template_name=data.template_name,
        html_content=data.html_content,
        type=data.type,
        mandatory_params=data.mandatory_params
    )

    # Create with Supabase-first fallback
    created_template = create_record(
        db,
        template,
        table_name="invoice_templates",
        supabase_data={
            "template_name": data.template_name,
            "html_content": data.html_content,
            "type": data.type,
            "mandatory_params": data.mandatory_params
        }
    )
    
    if not created_template:
        raise HTTPException(status_code=500, detail="Failed to create template")

    return created_template


# ✅ List All Templates
@router.get(
    "/",
    response_model=list[InvoiceTemplateSchema],
    summary="List all invoice templates"
)
def list_templates(db: Session = Depends(get_db)):

    templates = list_records(
        db,
        "invoice_templates",
        lambda: db.query(InvoiceTemplateModel).all()
    )
    
    if templates is None:
        raise HTTPException(status_code=500, detail="Failed to fetch templates")
    
    return templates


# ✅ Get Template by ID
@router.get(
    "/{template_id}",
    response_model=InvoiceTemplateSchema,
    summary="Get invoice template by ID"
)
def get_template(template_id: int, db: Session = Depends(get_db)):

    template = read_record(
        db,
        "invoice_templates",
        template_id,
        lambda: db.query(InvoiceTemplateModel).filter(InvoiceTemplateModel.id == template_id).first()
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template
