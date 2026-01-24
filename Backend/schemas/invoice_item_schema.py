from pydantic import BaseModel, Field
from datetime import datetime

class InvoiceItemBase(BaseModel):
    invoice_id: int = Field(..., description="The ID of the invoice this item belongs to.")
    userId: int = Field(..., description="The ID of the user who owns this invoice item.")
    description: str = Field(..., max_length=255, description="Description of the invoice item.")

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItem(InvoiceItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
