from pydantic import BaseModel, Field
from typing import List


class InvoiceItemCreate(BaseModel):
    description: str = Field(..., example="Widget A")
    quantity: int = Field(..., example=2)
    price: float = Field(..., example=9.99)


class InvoiceCreate(BaseModel):
    customer_id: int = Field(..., example=123)
    tax: float = Field(..., example=2.5)
    items: List[InvoiceItemCreate]

    class Config:
        schema_extra = {
            "example": {
                "customer_id": 123,
                "tax": 2.5,
                "items": [
                    {"description": "Widget A", "quantity": 2, "price": 9.99},
                    {"description": "Service B", "quantity": 1, "price": 49.5},
                ],
            }
        }
