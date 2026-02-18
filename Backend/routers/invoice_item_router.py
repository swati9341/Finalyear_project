from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import logging
import json
import re
from io import BytesIO
from pyhtml2pdf.converter import convert

from database import SessionLocal
from models.invoice_template import InvoiceTemplate as InvoiceTemplateModel # Import InvoiceTemplateModel
from models.invoice_item import InvoiceItem as InvoiceItemModel
from schemas.invoice_item_schema import (
    InvoiceItemCreate,
    InvoiceItem as InvoiceItemSchema
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/invoice_items", tags=["Invoice Items"])

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create Invoice Item
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

    # If template exists, proceed to create the invoice item
    db_invoice_item = InvoiceItemModel(
        invoice_id=data.invoice_id,
        userId=data.userId,
        description=data.description,
        data=data.data # Added data field
    )
    db.add(db_invoice_item)
    db.commit()
    db.refresh(db_invoice_item)
    return db_invoice_item

# List All Invoice Items
@router.get(
    "/",
    response_model=List[InvoiceItemSchema],
    summary="List all invoice items"
)
def list_invoice_items(db: Session = Depends(get_db)):
    invoice_items = db.query(InvoiceItemModel).all()
    # Enrich each item with template information
    for item in invoice_items:
        template = db.query(InvoiceTemplateModel).filter(InvoiceTemplateModel.id == item.invoice_id).first()
        item.template_name = template.template_name if template else None
    return invoice_items

# Get Invoice Item by ID
@router.get(
    "/{item_id}",
    response_model=InvoiceItemSchema,
    summary="Get invoice item by ID"
)
def get_invoice_item(item_id: int, db: Session = Depends(get_db)):
    invoice_item = db.query(InvoiceItemModel).filter(InvoiceItemModel.id == item_id).first()
    if not invoice_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice item not found")
    return invoice_item


# Generate PDF from Invoice Item
@router.get(
    "/{item_id}/pdf",
    summary="Generate PDF from invoice item"
)
def generate_invoice_pdf(item_id: int, db: Session = Depends(get_db)):
    """Generate PDF by replacing placeholders in template HTML with invoice item data"""
    logger.info(f"Generating PDF for invoice item: {item_id}")
    
    # Fetch the invoice item
    invoice_item = db.query(InvoiceItemModel).filter(InvoiceItemModel.id == item_id).first()
    if not invoice_item:
        logger.error(f"Invoice item not found: {item_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice item not found")
    
    # Fetch the template
    template = db.query(InvoiceTemplateModel).filter(
        InvoiceTemplateModel.id == invoice_item.invoice_id
    ).first()
    if not template:
        logger.error(f"Template not found for invoice_id: {invoice_item.invoice_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    
    logger.debug(f"Template found: {template.template_name}")
    
    try:
        # Parse the invoice item data
        if isinstance(invoice_item.data, str):
            data = json.loads(invoice_item.data)
        else:
            data = invoice_item.data
        
        logger.debug(f"Invoice data: {data}")
        
        # Get the HTML content from template
        html_content = template.html_content
        
        # Replace placeholders in HTML with actual data
        # Placeholders are expected to be in format: {{key}} or {key}
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