from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from database import Base
from datetime import datetime

class InvoiceTemplate(Base):
    __tablename__ = "invoice_templates"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    template_name = Column(String(255), nullable=False)
    html_content = Column(Text, nullable=False)

    type = Column(String(50), nullable=False)  # invoice / receipt

    mandatory_params = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
