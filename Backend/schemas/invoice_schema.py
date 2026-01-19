from pydantic import BaseModel, Field
from typing import List


class InvoiceItemCreate(BaseModel):
    description: str = Field(..., example="Widget A")
    quantity: int = Field(..., example=2)
    price: float = Field(..., example=9.99)


class InvoiceCreate(BaseModel):
    user_id: int = Field(..., example=1)
    customer_name: str = Field(..., example="John Doe")
    customer_email: str = Field(..., example="john@example.com")
    customer_phone: str = Field(..., example="+1234567890")
    tax: float = Field(..., example=2.5)
    items: List[InvoiceItemCreate]

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "customer_name": "John Doe",
                "customer_email": "john@example.com",
                "customer_phone": "+1234567890",
                "tax": 2.5,
                "items": [
                    {"description": "Widget A", "quantity": 2, "price": 9.99},
                    {"description": "Service B", "quantity": 1, "price": 49.5},
                ],
            }
        }
