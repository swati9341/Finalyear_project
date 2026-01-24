from pydantic import BaseModel, Field
from datetime import datetime

class DemoInvoice(BaseModel):
    # Map to InvoiceItem.invoice_id (which is validated against InvoiceTemplate.id)
    invoice_no: str = Field(..., alias="Invoice No", example="INV-1001")
    # Map to User.name via InvoiceItem.userId
    customer: str = Field(..., alias="Customer", example="Ravi Kumar")
    # Map to InvoiceItem.created_at
    date: str = Field(..., alias="Date", example="2026-01-24")
    # Map to InvoiceTemplate.type via InvoiceItem.invoice_id
    type: str = Field(..., alias="Type", example="Test")

    class Config:
        populate_by_name = True # Allow field names to be populated from aliases