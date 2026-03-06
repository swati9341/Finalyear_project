from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
from schemas.demo_invoice_schema import DemoInvoice
from utils.db_helpers import read_record
from supabase_client import supabase_fallback # Import supabase_fallback directly for complex queries

router = APIRouter(prefix="/demo", tags=["Demo Data"])

@router.get(
    "/invoice/{user_id}",
    response_model=List[DemoInvoice], # Return a list of demo invoices
    summary="Get demo invoice data for a specific user from the database"
)
def get_demo_invoices_from_db(user_id: int):
    # Fetch invoice items for the given user_id
    invoice_items_data: Optional[List[Dict[str, Any]]] = supabase_fallback.filter_by("invoice_items", userId=user_id)

    if not invoice_items_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No demo invoice data found for user ID {user_id} in the database. Please create some invoice items and templates for this user.")

    demo_invoices = []
    # To get user name and template type, we need to fetch them for each item
    # This is less efficient than a SQL join but necessary with direct Supabase client
    for item in invoice_items_data:
        user_data = read_record("users", item.get("userId"))
        template_data = read_record("invoice_templates", item.get("invoice_id"))

        if user_data and template_data:
            demo_invoices.append(DemoInvoice(
                invoice_no=f"INV-{item.get('invoice_id')}",
                customer=user_data.get("name"),
                date=item.get("created_at").split('T')[0] if item.get("created_at") else "N/A", # Supabase returns ISO format
                type=template_data.get("type")
            ))
    
    if not demo_invoices:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No complete demo invoice data found for user ID {user_id}.")

    return demo_invoices