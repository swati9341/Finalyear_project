from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class InvoiceTemplateCreate(BaseModel):
    template_name: str = Field(..., example="Default Template")
    html_content: str = Field(..., example="<html><body>Invoice Template</body></html>")
    type: str = Field(..., example="invoice")
    mandatory_params: List[str] = Field(default_factory=list, example=["customer_name", "total"])

    class Config:
        json_schema_extra = {
            "example": {
                "template_name": "Default Template",
                "html_content": "<html><body>Invoice Template</body></html>",
                "type": "invoice",
                "mandatory_params": ["customer_name", "total"]
            }
        }


class InvoiceTemplate(BaseModel):
    id: int = Field(..., example=1)
    template_name: str = Field(..., example="Default Template")
    html_content: str = Field(..., example="<html><body>Invoice Template</body></html>")
    type: str = Field(..., example="invoice")
    mandatory_params: List[str] = Field(default_factory=list, example=["customer_name", "total"])
    created_at: datetime = Field(..., example="2023-01-01T00:00:00")

    class Config:
        from_attributes = True  # ✅ REQUIRED for ORM objects
        json_schema_extra = {
            "example": {
                "id": 1,
                "template_name": "Default Template",
                "html_content": "<html><body>Invoice Template</body></html>",
                "type": "invoice",
                "mandatory_params": ["customer_name", "total"],
                "created_at": "2023-01-01T00:00:00"
            }
        }
