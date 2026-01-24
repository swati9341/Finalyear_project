from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer)
    userId = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow())
