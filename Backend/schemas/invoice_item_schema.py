from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional # Added import for Optional

class InvoiceItemBase(BaseModel):
    invoice_id: int = Field(..., description="The ID of the invoice this item belongs to.")
    userId: int = Field(..., description="The ID of the user who owns this invoice item.")
    description: str = Field(..., max_length=255, description="Description of the invoice item.")
    data: Optional[str] = Field(None, max_length=255, description="Additional data for the invoice item, stored as a string (e.g., JSON string).")

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItem(InvoiceItemBase):
    id: int
    created_at: datetime
    template_name: Optional[str] = None

    class Config:
        from_attributes = True