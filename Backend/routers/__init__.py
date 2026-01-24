"""Routers package initializer - expose named router modules for convenience."""
from . import invoice_router as invoices
from . import auth as auth
from . import template_router as template_router

__all__ = ["invoices", "auth", "template_router"]
