from fastapi import APIRouter, HTTPException
from schemas.template_schema import (
    InvoiceTemplateCreate,
    InvoiceTemplate as InvoiceTemplateSchema
)
from utils.db_helpers import create_record, read_record, list_records
from supabase_client import supabase_fallback # Ensure this is imported if not already
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/templates", tags=["Invoice Templates"])




# ✅ Create Invoice Template
@router.post(
    "/create",
    response_model=InvoiceTemplateSchema,
    summary="Create an invoice template"
)
def create_template(data: InvoiceTemplateCreate):
    # Check if a template with the same name already exists
    # Using the custom filter_by method in SupabaseClient
    existing_template = supabase_fallback.filter_by("invoice_templates", template_name=data.template_name)
    if existing_template:
        raise HTTPException(status_code=409, detail=f"Template with name '{data.template_name}' already exists.")

    created_template: Optional[Dict[str, Any]] = create_record(
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

    return InvoiceTemplateSchema(**created_template)


# ✅ List All Templates
@router.get(
    "/",
    response_model=list[InvoiceTemplateSchema],
    summary="List all invoice templates"
)
def list_templates():
    templates: Optional[List[Dict[str, Any]]] = list_records(
        "invoice_templates",
    )
    
    if templates is None:
        raise HTTPException(status_code=500, detail="Failed to fetch templates")
    
    return [InvoiceTemplateSchema(**template) for template in templates]


# ✅ Get Template by ID
@router.get(
    "/{template_id}",
    response_model=InvoiceTemplateSchema,
    summary="Get invoice template by ID"
)
def get_template(template_id: int):
    template: Optional[Dict[str, Any]] = read_record(
        "invoice_templates",
        template_id,
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return InvoiceTemplateSchema(**template)
