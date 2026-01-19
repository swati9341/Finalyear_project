from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    customer_name = Column(String(255))
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    subtotal = Column(Numeric(10,2))
    tax = Column(Numeric(10,2))
    total = Column(Numeric(10,2))
    pdf_path = Column(String(255))

    items = relationship("InvoiceItem", back_populates="invoice")
