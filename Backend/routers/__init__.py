"""Routers package initializer - expose named router modules for convenience."""
from . import auth as auth
from . import template_router as template_router
from . import invoice_item_router as invoice_item_router
from . import demo_router as demo_router # Added demo_router

__all__ = [ "auth", "template_router", "invoice_item_router", "demo_router"]
