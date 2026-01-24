from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from models.invoice_item import InvoiceItem as InvoiceItemModel
from schemas.invoice_item_schema import (
    InvoiceItemCreate,
    InvoiceItem as InvoiceItemSchema
)

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
    db_invoice_item = InvoiceItemModel(
        invoice_id=data.invoice_id,
        userId=data.userId,
        description=data.description
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
