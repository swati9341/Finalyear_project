"""
Database operation helpers with automatic Supabase fallback.
Use these functions in your routers instead of direct database operations.
"""

import logging
from typing import Optional, List, Callable, Any, TypeVar
from sqlalchemy.orm import Session
from database_fallback import db_fallback
from supabase_client import supabase_fallback

logger = logging.getLogger(__name__)

T = TypeVar('T')


def query_primary(db: Session, query_func: Callable[[], Any]) -> Optional[Any]:
    """
    Execute a query on the primary database.
    
    Usage:
        user = query_primary(db, lambda: db.query(User).filter(User.email == email).first())
    """
    return query_func()


def create_record(
    db: Session,
    model_instance: T,
    table_name: str,
    supabase_data: dict
) -> Optional[T]:
    """
    Create a record with automatic Supabase fallback.
    
    Args:
        db: SQLAlchemy session
        model_instance: The model instance to create
        table_name: Table name in Supabase (should match SQLAlchemy table)
        supabase_data: Dictionary of data to insert in Supabase
    
    Returns:
        The created instance or None if creation fails
    
    Usage:
        user_data = {"name": "John", "email": "john@example.com", "password_hash": "..."}
        new_user = create_record(
            db,
            User(name="John", email="john@example.com", password_hash="..."),
            "users",
            user_data
        )
    """
    return db_fallback.create_with_fallback(db, model_instance, table_name, supabase_data)


def read_record(
    db: Session,
    fallback_table: str,
    fallback_id: int,
    primary_query: Callable[[], Optional[Any]],
    fallback_id_column: str = "id"
) -> Optional[Any]:
    """
    Read a record with Supabase as primary and fallback to primary database.
    
    Args:
        db: SQLAlchemy session
        fallback_table: Supabase table name
        fallback_id: ID of the record to fetch
        primary_query: Lambda function for primary database query
        fallback_id_column: Column name for ID (defaults to 'id')
    
    Returns:
        The record or None if not found
    
    Usage:
        user = read_record(
            db,
            "users",
            user_id,
            lambda: db.query(User).filter(User.id == user_id).first()
        )
    """
    def supabase_func():
        return supabase_fallback.get_by_id(
            fallback_table, fallback_id, fallback_id_column
        )
    
    return db_fallback.read_with_fallback(supabase_func, primary_query, fallback_table)


def read_record_by_email(
    db: Session,
    fallback_table: str,
    email: str,
    primary_query: Callable[[], Optional[Any]]
) -> Optional[Any]:
    """
    Read a user record by email with Supabase as primary and fallback to primary database.
    
    Args:
        db: SQLAlchemy session
        fallback_table: Supabase table name (usually 'users')
        email: Email address to search for
        primary_query: Lambda function for primary database query by email
    
    Returns:
        The record or None if not found
    
    Usage:
        user = read_record_by_email(
            db,
            "users",
            "user@example.com",
            lambda: db.query(User).filter(User.email == "user@example.com").first()
        )
    """
    def supabase_func():
        return supabase_fallback.get_by_email(
            fallback_table, email
        )
    
    return db_fallback.read_with_fallback(supabase_func, primary_query, fallback_table)


def update_record(
    db: Session,
    db_instance: T,
    updates: dict,
    table_name: str,
    id_value: int
) -> Optional[T]:
    """
    Update a record with automatic Supabase fallback.
    
    Args:
        db: SQLAlchemy session
        db_instance: The model instance to update (should be from primary DB)
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
    return db_fallback.update_with_fallback(db, db_instance, updates, table_name, id_value)


def delete_record(
    db: Session,
    db_instance: T,
    table_name: str,
    id_value: int
) -> bool:
    """
    Delete a record with automatic Supabase fallback.
    
    Args:
        db: SQLAlchemy session
        db_instance: The model instance to delete
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
    return db_fallback.delete_with_fallback(db, db_instance, table_name, id_value)


def list_records(
    db: Session,
    fallback_table: str,
    primary_query: Callable[[], List[Any]]
) -> Optional[List[Any]]:
    """
    List records with Supabase as primary and fallback to primary database.
    
    Args:
        db: SQLAlchemy session
        fallback_table: Supabase table name
        primary_query: Lambda function for primary database query to get all records
    
    Returns:
        List of records or None if query fails
    
    Usage:
        users = list_records(
            db,
            "users",
            lambda: db.query(User).all()
        )
    """
    def supabase_func():
        return supabase_fallback.select(fallback_table)
    
    return db_fallback.query_with_fallback(supabase_func, primary_query, fallback_table)
