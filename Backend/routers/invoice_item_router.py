from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from typing import List
import logging
import json
from io import BytesIO
import requests
import base64
import re
from urllib.parse import urljoin

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
# Convert External Images to Base64
# -----------------------------------------
def convert_images_to_base64(html_content):
    """
    Convert external image URLs to base64 data URIs.
    This ensures images are embedded in the HTML and render properly in PDFs.
    """
    
    def replace_image_url(match):
        img_tag = match.group(0)
        logger.info(f"Found image tag: {img_tag[:100]}...")
        
        # Extract src attribute (more flexible regex)
        src_match = re.search(r'src\s*=\s*["\']([^"\']*)["\']', img_tag, re.IGNORECASE)
        
        if not src_match:
            logger.warning(f"No src attribute found in img tag: {img_tag[:100]}")
            return img_tag
        
        src_url = src_match.group(1).strip()
        logger.info(f"Found src URL: {src_url}")
        
        # Skip if already a data URI
        if src_url.startswith('data:'):
            logger.info(f"Skipping data URI: {src_url[:50]}...")
            return img_tag
        
        try:
            image_data = None
            
            # Fetch the image
            if src_url.startswith(('http://', 'https://')):
                logger.info(f"Fetching image from URL: {src_url}")
                response = requests.get(src_url, timeout=10)
                response.raise_for_status()
                image_data = response.content
                logger.info(f"Successfully fetched image from {src_url}, size: {len(image_data)} bytes")
            elif src_url.startswith(('/', './')):
                # Try to read from file system
                logger.info(f"Trying to read image from file: {src_url}")
                with open(src_url, 'rb') as f:
                    image_data = f.read()
                logger.info(f"Successfully read image from {src_url}, size: {len(image_data)} bytes")
            else:
                logger.warning(f"Unsupported URL format: {src_url}")
                return img_tag
            
            if not image_data:
                logger.warning(f"No image data retrieved for: {src_url}")
                return img_tag
            
            # Determine MIME type
            mime_type = 'image/png'  # default
            if src_url.lower().endswith('.png'):
                mime_type = 'image/png'
            elif src_url.lower().endswith(('.jpg', '.jpeg')):
                mime_type = 'image/jpeg'
            elif src_url.lower().endswith('.gif'):
                mime_type = 'image/gif'
            elif src_url.lower().endswith('.svg'):
                mime_type = 'image/svg+xml'
            elif src_url.lower().endswith('.webp'):
                mime_type = 'image/webp'
            
            # Convert to base64
            b64_data = base64.b64encode(image_data).decode('utf-8')
            data_uri = f'data:{mime_type};base64,{b64_data}'
            logger.info(f"Created data URI of length: {len(data_uri)}")
            
            # Replace src in the img tag - use more precise replacement
            new_img_tag = re.sub(
                r'src\s*=\s*["\']([^"\']*)["\']',
                f'src="{data_uri}"',
                img_tag,
                flags=re.IGNORECASE
            )
            logger.info(f"Successfully converted image: {src_url}")
            return new_img_tag
        
        except Exception as e:
            logger.error(f"Failed to convert image {src_url} to base64: {str(e)}", exc_info=True)
            return img_tag
    
    # Find all img tags and replace their src with base64 (more flexible regex to handle newlines)
    found_images = re.findall(r'<img[^>]*>', html_content, flags=re.IGNORECASE | re.DOTALL)
    logger.info(f"Found {len(found_images)} image tags in HTML")
    
    html_content = re.sub(r'<img[^>]*>', replace_image_url, html_content, flags=re.IGNORECASE | re.DOTALL)
    return html_content


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

    mandatory_params = invoice_template.get("mandatory_params", [])
    if mandatory_params:
        if isinstance(data.data, str):
            try:
                input_data = json.loads(data.data)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in data field.")
        else:
            input_data = data.data or {}

        missing_or_empty = []
        for param in mandatory_params:
            val = input_data.get(param)
            if val is None or str(val).strip() == "":
                missing_or_empty.append(param)
        
        if missing_or_empty:
            raise HTTPException(
                status_code=400,
                detail=f"Missing or empty mandatory parameters: {', '.join(missing_or_empty)}"
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
        
        # Convert external images to base64 before PDF generation
        rendered_html = convert_images_to_base64(rendered_html)

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