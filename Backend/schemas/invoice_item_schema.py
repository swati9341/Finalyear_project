from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional # Added import for Optional

class InvoiceItemBase(BaseModel):
    invoice_id: int = Field(..., description="The ID of the invoice this item belongs to.")
    userId: int = Field(..., description="The ID of the user who owns this invoice item.")
    description: str = Field(..., description="Description of the invoice item.")
    data: Optional[dict] = Field(None, description="Additional data for the invoice item, stored as a JSON object.")

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItem(InvoiceItemBase):
    id: int
    created_at: datetime
    template_name: Optional[str] = None

    class Config:
        from_attributes = True