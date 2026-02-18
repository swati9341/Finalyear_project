from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from models.invoice_item import InvoiceItem as InvoiceItemModel
from models.user import User as UserModel
from models.invoice_template import InvoiceTemplate as InvoiceTemplateModel
from schemas.demo_invoice_schema import DemoInvoice

router = APIRouter(prefix="/demo", tags=["Demo Data"])

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/invoice/{user_id}",
    response_model=List[DemoInvoice], # Return a list of demo invoices
    summary="Get demo invoice data for a specific user from the database"
)
def get_demo_invoices_from_db(user_id: int, db: Session = Depends(get_db)):
    # Query InvoiceItem, join with User and InvoiceTemplate
    # We'll fetch a few items to demonstrate a list
    invoice_items_data = (
        db.query(InvoiceItemModel, UserModel, InvoiceTemplateModel)
        .join(UserModel, InvoiceItemModel.userId == UserModel.id)
        .join(InvoiceTemplateModel, InvoiceItemModel.invoice_id == InvoiceTemplateModel.id)
        .filter(UserModel.id == user_id) # Filter by user_id
        .limit(5) # Limit to a few for demo purposes
        .all()
    )

    if not invoice_items_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No demo invoice data found for user ID {user_id} in the database. Please create some invoice items and templates for this user.")

    demo_invoices = []
    for item, user, template in invoice_items_data:
        demo_invoices.append(DemoInvoice(
            invoice_no=f"INV-{item.invoice_id}", # Using invoice_id from InvoiceItem (which links to template)
            customer=user.name,
            date=item.created_at.strftime('%Y-%m-%d'),
            type=template.type
        ))
    return demo_invoices