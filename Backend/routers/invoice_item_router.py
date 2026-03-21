from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from typing import List
import logging
import json
from io import BytesIO

from xhtml2pdf import pisa
from jinja2 import Template

from schemas.invoice_item_schema import (
    InvoiceItemCreate,
    InvoiceItem as InvoiceItemSchema
)

from utils.db_helpers import create_record, read_record, list_records
from supabase_client import supabase_fallback


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/invoice_items", tags=["Invoice Items"])


# -----------------------------------------
# CREATE INVOICE ITEM
# -----------------------------------------
@router.post(
    "/",
    response_model=InvoiceItemSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_item(data: InvoiceItemCreate):

    invoice_template = read_record("invoice_templates", data.invoice_id)

    if not invoice_template:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice Template with ID {data.invoice_id} not found."
        )

    created_item = create_record(
        table_name="invoice_items",
        supabase_data={
            "invoice_id": data.invoice_id,
            "userId": data.userId,
            "description": data.description,
            "data": data.data
        }
    )

    if not created_item:
        raise HTTPException(status_code=500, detail="Failed to create invoice item")

    return InvoiceItemSchema(**created_item)


# -----------------------------------------
# LIST INVOICE ITEMS
# -----------------------------------------
@router.get("/", response_model=List[InvoiceItemSchema])
def list_invoice_items(user_id: int = Query(...)):

    invoice_items = list_records("invoice_items") or []

    invoice_items = [
        item for item in invoice_items if item.get("userId") == user_id
    ]

    for item in invoice_items:

        template = read_record("invoice_templates", item.get("invoice_id"))

        item["template_name"] = (
            template.get("template_name") if template else None
        )

    return [InvoiceItemSchema(**item) for item in invoice_items]


# -----------------------------------------
# GET SINGLE INVOICE ITEM
# -----------------------------------------
@router.get("/{item_id}", response_model=InvoiceItemSchema)
def get_invoice_item(item_id: int):

    invoice_item = read_record("invoice_items", item_id)

    if not invoice_item:
        raise HTTPException(status_code=404, detail="Invoice item not found")

    return InvoiceItemSchema(**invoice_item)


# -----------------------------------------
# GENERATE PDF
# -----------------------------------------
@router.get("/{item_id}/pdf")
def generate_invoice_pdf(item_id: int):

    invoice_item = read_record("invoice_items", item_id)

    if not invoice_item:
        raise HTTPException(status_code=404, detail="Invoice item not found")

    template = read_record("invoice_templates", invoice_item.get("invoice_id"))

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    try:

        data_str = invoice_item.get("data")

        if isinstance(data_str, str):
            data = json.loads(data_str)
        else:
            data = data_str

        html_template = template.get("html_content")

        rendered_html = Template(html_template).render(**data)

        buffer = BytesIO()

        pisa_status = pisa.CreatePDF(
            rendered_html,
            dest=buffer
        )

        if pisa_status.err:
            raise HTTPException(status_code=500, detail="Error generating PDF")

        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=invoice_{item_id}.pdf"
            }
        )

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF: {str(e)}"
        )