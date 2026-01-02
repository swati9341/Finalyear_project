from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from database import SessionLocal
from models.invoice import Invoice
from models.invoice_item import InvoiceItem
from schemas.invoice_schema import InvoiceCreate
from services.pdf_service import generate_invoice_pdf
import uuid

router = APIRouter(prefix="/invoices", tags=["Invoices"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", summary="Create an invoice", response_description="Invoice creation result")
def create_invoice(
    data: InvoiceCreate = Body(
        ...,
        description="Invoice payload",
        examples={
            "default": {
                "summary": "Sample invoice",
                "value": InvoiceCreate.Config.schema_extra["example"],
            }
        },
    ),
    db: Session = Depends(get_db),
):
    invoice_no = str(uuid.uuid4())[:8]

    subtotal = sum(item.quantity * item.price for item in data.items)
    total = subtotal + data.tax

    invoice = Invoice(
        invoice_number=invoice_no,
        customer_id=data.customer_id,
        subtotal=subtotal,
        tax=data.tax,
        total=total
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    for item in data.items:
        db.add(InvoiceItem(
            invoice_id=invoice.id,
            description=item.description,
            quantity=item.quantity,
            price=item.price
        ))

    db.commit()

    file_path = f"pdfs/{invoice_no}.pdf"
    generate_invoice_pdf(file_path, invoice, data.items)

    invoice.pdf_path = file_path
    db.commit()

    return {"message": "Invoice created", "invoice_number": invoice_no}
