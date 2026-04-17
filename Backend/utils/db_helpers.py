"""
Database operation helpers for Supabase.
Use these functions in your routers instead of direct database operations.
"""

import logging
from typing import Optional, List, Any, TypeVar, Dict
from supabase_client import supabase_fallback

logger = logging.getLogger(__name__)

T = TypeVar('T')

def create_record(
    table_name: str,
    supabase_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Create a record directly in Supabase.
    
    Args:
        table_name: Table name in Supabase (should match SQLAlchemy table)
        supabase_data: Dictionary of data to insert in Supabase
    
    Returns:
        The created record as a dictionary or None if creation fails
    
    Usage:
        user_data = {"name": "John", "email": "john@example.com", "password_hash": "..."}
        new_user = create_record(
            db,
            User(name="John", email="john@example.com", password_hash="..."),
            "users",
            user_data
        )
    """
    logger.debug(f"Attempting Supabase insert into {table_name} with data: {supabase_data}")
    created_data = supabase_fallback.insert(table_name, supabase_data)
    if created_data:
        logger.info(f"Successfully created record in Supabase table '{table_name}'")
        return created_data
    else:
        logger.error(f"Failed to create record in Supabase table '{table_name}'")
        return None


def read_record(
    table_name: str,
    record_id: int,
    id_column: str = "id"
) -> Optional[Dict[str, Any]]:
    """
    Read a record directly from Supabase.
    
    Args:
        table_name: Supabase table name
        record_id: ID of the record to fetch
        id_column: Column name for ID (defaults to 'id')
    
    Returns:
        The record as a dictionary or None if not found
    
    Usage:
        user = read_record(
            db,
            "users",
            user_id,
            lambda: db.query(User).filter(User.id == user_id).first()
        )
    """
    logger.debug(f"Attempting Supabase read from {table_name} for {id_column}={record_id}")
    record = supabase_fallback.get_by_id(table_name, record_id, id_column)
    if record:
        logger.info(f"Successfully read record from Supabase table '{table_name}' for {id_column}={record_id}")
        return record
    else:
        logger.warning(f"Record not found in Supabase table '{table_name}' for {id_column}={record_id}")
        return None


def read_record_by_email(
    table_name: str,
    email: str,
) -> Optional[Dict[str, Any]]:
    """
    Read a user record by email directly from Supabase.
    
    Args:
        table_name: Supabase table name (e.g., 'users')
        email: Email address to search for
    
    Returns:
        The record as a dictionary or None if not found
    
    Usage:
        user = read_record_by_email(
            db,
            "users",
            "user@example.com",
            lambda: db.query(User).filter(User.email == "user@example.com").first()
        )
    """
    logger.debug(f"Attempting Supabase read from {table_name} for email={email}")
    record = supabase_fallback.get_by_email(table_name, email)
    if record:
        logger.info(f"Successfully read record from Supabase table '{table_name}' for email={email}")
        return record
    else:
        logger.warning(f"Record not found in Supabase table '{table_name}' for email={email}")
        return None


def update_record(
    updates: Dict[str, Any],
    table_name: str,
    id_value: int,
    id_column: str = "id"
) -> Optional[Dict[str, Any]]:
    """
    Update a record directly in Supabase.
    
    Args:
        updates: Dictionary of fields to update
        table_name: Table name in Supabase
        id_value: ID of the record being updated
    
    Returns:
        The updated instance or None if update fails
    
    Usage:
        updated_user = update_record(
            db,
            user,
            {"email": "newemail@example.com"},
            "users",
            user.id
        )
    """    
    logger.debug(f"Attempting Supabase update in {table_name} for {id_column}={id_value} with data: {updates}")
    updated_data = supabase_fallback.update(table_name, id_value, updates, id_column)
    if updated_data:
        logger.info(f"Successfully updated record in Supabase table '{table_name}' for {id_column}={id_value}")
        return updated_data
    else:
        logger.error(f"Failed to update record in Supabase table '{table_name}' for {id_column}={id_value}")
        return None


def delete_record(
    table_name: str,
    id_value: int,
    id_column: str = "id"
) -> bool:
    """
    Delete a record directly from Supabase.
    
    Args:
        table_name: Table name in Supabase
        id_value: ID of the record being deleted
    
    Returns:
        True if deletion succeeded, False otherwise
    
    Usage:
        success = delete_record(
            db,
            user,
            "users",
            user.id
        )
    """
    logger.debug(f"Attempting Supabase delete from {table_name} for {id_column}={id_value}")
    success = supabase_fallback.delete(table_name, id_value, id_column)
    if success:
        logger.info(f"Successfully deleted record from Supabase table '{table_name}' for {id_column}={id_value}")
    else:
        logger.error(f"Failed to delete record from Supabase table '{table_name}' for {id_column}={id_value}")
    return success


def list_records(
    table_name: str,
) -> Optional[List[Dict[str, Any]]]:
    """
    List records directly from Supabase.
    
    Args:
        table_name: Supabase table name
    
    Returns:
        List of records as dictionaries or None if query fails
    
    Usage:
        users = list_records(
            db,
            "users",
            lambda: db.query(User).all()
        )
    """
    logger.debug(f"Attempting Supabase list from {table_name}")
    records = supabase_fallback.select(table_name)
    if records is not None:
        logger.info(f"Successfully listed records from Supabase table '{table_name}'")
        return records
    else:
        logger.error(f"Failed to list records from Supabase table '{table_name}'")
        return None
