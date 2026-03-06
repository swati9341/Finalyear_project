from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import logging
import json
from io import BytesIO
from fpdf import FPDF

from schemas.invoice_item_schema import (
    InvoiceItemCreate,
    InvoiceItem as InvoiceItemSchema
)
from utils.db_helpers import create_record, read_record, list_records
from supabase_client import supabase_fallback # Import supabase_fallback directly for template check

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/invoice_items", tags=["Invoice Items"])


# -----------------------------------------
# CREATE INVOICE ITEM
# -----------------------------------------
@router.post(
    "/",
    response_model=InvoiceItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create an invoice item"
)
def create_invoice_item(data: InvoiceItemCreate):
    # Check if the invoice_id corresponds to an existing InvoiceTemplate
    invoice_template = read_record("invoice_templates", data.invoice_id)
    if not invoice_template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice Template with ID {data.invoice_id} not found.")

    # If template exists, proceed to create the invoice item
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
# LIST ALL INVOICE ITEMS
# -----------------------------------------
from fastapi import Query

@router.get(
    "/",
    response_model=List[InvoiceItemSchema],
    summary="List all invoice items"
)
def list_invoice_items(user_id: int= Query(...)):
    # List records directly from Supabase
    invoice_items: Optional[List[Dict[str, Any]]] = list_records("invoice_items")

    # Fix: if DB returns None
    if invoice_items is None:
        invoice_items = []
    
    print(f"Fetched {len(invoice_items)} invoice items from Supabase")
    print(f"Filtering for user_id: {user_id}")

    # Filter by userId (match DB column)
    invoice_items = [
        item for item in invoice_items if item.get("userId") == user_id
    ]

    # Enrich each item with template information
    for item in invoice_items:
        invoice_id = item.get("invoice_id")

        template = read_record("invoice_templates", invoice_id)

        item["template_name"] = (
            template.get("template_name") if template else None
        )

    return [InvoiceItemSchema(**item) for item in invoice_items]


# -----------------------------------------
# GET SINGLE INVOICE ITEM
# -----------------------------------------
@router.get(
    "/{item_id}",
    response_model=InvoiceItemSchema,
    summary="Get invoice item by ID"
)
def get_invoice_item(item_id: int):
    # Get record directly from Supabase
    invoice_item: Optional[Dict[str, Any]] = read_record(
        "invoice_items",
        item_id,
    )
    if not invoice_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice item not found")
    
    return InvoiceItemSchema(**invoice_item)


# -----------------------------------------
# GENERATE PDF
# -----------------------------------------
@router.get("/{item_id}/pdf", summary="Generate PDF from invoice item")
def generate_invoice_pdf(item_id: int):
    """Generate PDF by replacing placeholders in template HTML with invoice item data"""
    logger.info(f"Generating PDF for invoice item: {item_id}")
    
    # Fetch the invoice item directly from Supabase
    invoice_item: Optional[Dict[str, Any]] = read_record(
        "invoice_items",
        item_id,
    )
    if not invoice_item:
        logger.error(f"Invoice item not found: {item_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice item not found")
    
    invoice_id = invoice_item.get("invoice_id")
    # Fetch the template
    template: Optional[Dict[str, Any]] = read_record("invoice_templates", invoice_id)
    if not template:
        logger.error(f"Template not found for invoice_id: {invoice_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    
    logger.debug(f"Template found: {template.get('template_name')}")
    
    try:
        data_str = invoice_item.get("data")
            
        if isinstance(data_str, str):
            data = json.loads(data_str)
        else:
            data = data_str
        
        logger.debug(f"Invoice data: {data}")
        
        # Get the HTML content from template
        html_content = template.get("html_content")
        
        # Replace placeholders in HTML with actual data
        for key, value in data.items():
            # Replace {{key}} format
            html_content = html_content.replace(f"{{{{{key}}}}}", str(value))
            # Replace {key} format
            html_content = html_content.replace(f"{{{key}}}", str(value))
        
        logger.debug("Placeholders replaced successfully")
        
        # Generate PDF using fpdf2's write_html() directly
        pdf = FPDF(format='A4')
        pdf.set_auto_page_break(False)
        pdf.set_margins(15, 15, 15)
        pdf.add_page()

        pdf.set_font("Arial", size=11)

        for line in html_content:
            pdf.cell(0, 8, line, ln=True)

        pdf_bytes = pdf.output(dest="S")
        output_pdf = BytesIO(pdf_bytes)
        
        logger.info(f"PDF generated successfully for invoice item: {item_id}")
        
        # Return PDF as streaming response
        output_pdf.seek(0)
        return StreamingResponse(
            output_pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=invoice_{item_id}.pdf"}
        )
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse invoice data JSON: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid invoice data format")
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")