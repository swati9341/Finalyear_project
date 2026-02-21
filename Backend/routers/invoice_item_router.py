from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import logging
import json
from io import BytesIO
from pyhtml2pdf.converter import convert

from database import SessionLocal
from models.invoice_template import InvoiceTemplate as InvoiceTemplateModel
from models.invoice_item import InvoiceItem as InvoiceItemModel
from schemas.invoice_item_schema import (
    InvoiceItemCreate,
    InvoiceItem as InvoiceItemSchema
)
from utils.db_helpers import create_record, read_record, list_records

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/invoice_items", tags=["Invoice Items"])

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------------------
# CREATE INVOICE ITEM
# -----------------------------------------
@router.post(
    "/",
    response_model=InvoiceItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create an invoice item"
)
def create_invoice_item(data: InvoiceItemCreate, db: Session = Depends(get_db)):
    # Check if the invoice_id corresponds to an existing InvoiceTemplate
    invoice_template = db.query(InvoiceTemplateModel).filter(InvoiceTemplateModel.id == data.invoice_id).first()
    if not invoice_template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice Template with ID {data.invoice_id} not found.")

    # If template exists, proceed to create the invoice item with Supabase-first fallback
    db_invoice_item = InvoiceItemModel(
        invoice_id=data.invoice_id,
        userId=data.userId,
        description=data.description,
        data=data.data
    )
    
    created_item = create_record(
        db,
        db_invoice_item,
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
    
    return created_item


# -----------------------------------------
# LIST ALL INVOICE ITEMS
# -----------------------------------------
@router.get(
    "/",
    response_model=List[InvoiceItemSchema],
    summary="List all invoice items"
)
def list_invoice_items(db: Session = Depends(get_db)):
    # List with Supabase-first fallback
    invoice_items = list_records(
        db,
        "invoice_items",
        lambda: db.query(InvoiceItemModel).all()
    )
    
    if invoice_items is None:
        raise HTTPException(status_code=500, detail="Failed to fetch invoice items")
    
    # Enrich each item with template information
    for item in invoice_items:
        # Extract invoice_id based on response type
        if isinstance(item, dict):
            invoice_id = item.get("invoice_id")
        else:
            invoice_id = item.invoice_id
        
        # Query template with the extracted invoice_id
        template = db.query(InvoiceTemplateModel).filter(InvoiceTemplateModel.id == invoice_id).first()
        
        if isinstance(item, dict):
            item['template_name'] = template.template_name if template else None
        else:
            item.template_name = template.template_name if template else None
    
    return invoice_items


# -----------------------------------------
# GET SINGLE INVOICE ITEM
# -----------------------------------------
@router.get(
    "/{item_id}",
    response_model=InvoiceItemSchema,
    summary="Get invoice item by ID"
)
def get_invoice_item(item_id: int, db: Session = Depends(get_db)):
    # Get with Supabase-first fallback
    invoice_item = read_record(
        db,
        "invoice_items",
        item_id,
        lambda: db.query(InvoiceItemModel).filter(InvoiceItemModel.id == item_id).first()
    )
    
    if not invoice_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice item not found")
    
    return invoice_item


# -----------------------------------------
# GENERATE PDF
# -----------------------------------------
@router.get("/{item_id}/pdf", summary="Generate PDF from invoice item")
def generate_invoice_pdf(item_id: int, db: Session = Depends(get_db)):
    """Generate PDF by replacing placeholders in template HTML with invoice item data"""
    logger.info(f"Generating PDF for invoice item: {item_id}")
    
    # Fetch the invoice item with Supabase-first fallback
    invoice_item = read_record(
        db,
        "invoice_items",
        item_id,
        lambda: db.query(InvoiceItemModel).filter(InvoiceItemModel.id == item_id).first()
    )
    
    if not invoice_item:
        logger.error(f"Invoice item not found: {item_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice item not found")
    
    # Extract invoice_id based on response type
    if isinstance(invoice_item, dict):
        invoice_id = invoice_item.get("invoice_id")
    else:
        invoice_id = invoice_item.invoice_id
    
    # Fetch the template
    template = db.query(InvoiceTemplateModel).filter(
        InvoiceTemplateModel.id == invoice_id
    ).first()
    if not template:
        logger.error(f"Template not found for invoice_id: {invoice_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    
    logger.debug(f"Template found: {template.template_name}")
    
    try:
        # Parse the invoice item data
        if isinstance(invoice_item, dict):
            data_str = invoice_item.get("data")
        else:
            data_str = invoice_item.data
            
        if isinstance(data_str, str):
            data = json.loads(data_str)
        else:
            data = data_str
        
        logger.debug(f"Invoice data: {data}")
        
        # Get the HTML content from template
        html_content = template.html_content
        
        # Replace placeholders in HTML with actual data
        for key, value in data.items():
            # Replace {{key}} format
            html_content = html_content.replace(f"{{{{{key}}}}}", str(value))
            # Replace {key} format
            html_content = html_content.replace(f"{{{key}}}", str(value))
        
        logger.debug("Placeholders replaced successfully")
        
        # Generate PDF from HTML using pyhtml2pdf
        output_pdf = BytesIO()
        convert(source=html_content, target=output_pdf)
        pdf_bytes = output_pdf.getvalue()
        
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