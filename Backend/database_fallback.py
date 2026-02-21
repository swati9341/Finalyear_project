"""
Database fallback wrapper that attempts primary database first, then Supabase.
Provides a unified interface for database operations with automatic fallback.
"""

import logging
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import SessionLocal, engine
from supabase_client import supabase_fallback

logger = logging.getLogger(__name__)


class DatabaseFallback:
    """
    Database operations wrapper with primary Supabase and fallback to MySQL/SQLite.
    Uses Supabase exclusively if available at startup, otherwise uses local database.
    Does not attempt fallback during operation - uses one or the other based on initial check.
    """
    
    def __init__(self):
        self.primary_available = self._check_primary_database()
        self.supabase_available = supabase_fallback.is_connected
        
        # Determine which database to use for the entire lifecycle
        if self.supabase_available:
            logger.info("Using Supabase as primary database for entire lifecycle")
            self.use_supabase = True
        else:
            logger.info("Supabase not available. Using local database (MySQL/SQLite) for entire lifecycle")
            self.use_supabase = False
    
    def _check_primary_database(self) -> bool:
        """Check if primary database is available."""
        try:
            with engine.connect() as conn:
                logger.info("Primary database is available")
                return True
        except Exception as e:
            logger.warning(f"Primary database not available: {e}")
            return False
    
    @contextmanager
    def get_db(self):
        """Get a database session with fallback support."""
        db = SessionLocal()
        try:
            yield db
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error: {e}. Consider configuring Supabase fallback.")
            raise
        finally:
            db.close()
    
    def query_with_fallback(
        self,
        supabase_query_func,
        primary_query_func,
        table_name: str
    ) -> Optional[Any]:
        """
        Execute a query using the database determined at initialization.
        No fallback attempts during operation - uses Supabase if available at startup, otherwise local DB.
        
        Args:
            supabase_query_func: Function that performs the Supabase query
            primary_query_func: Function that performs the local database (MySQL/SQLite) query
            table_name: Name of the table being queried (for logging)
        
        Returns:
            Query result or None if query fails
        """
        try:
            if self.use_supabase:
                logger.debug(f"Querying Supabase for {table_name}")
                result = supabase_query_func()
                return result
            else:
                logger.debug(f"Querying primary database for {table_name}")
                result = primary_query_func()
                return result
        except Exception as e:
            logger.error(f"Query failed for {table_name}: {e}")
            return None
    
    def create_with_fallback(
        self,
        db: Session,
        model_instance,
        table_name: str,
        supabase_data: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Create a record using the database determined at initialization.
        No fallback attempts during operation - uses Supabase if available at startup, otherwise local DB.
        
        Args:
            db: SQLAlchemy session
            model_instance: SQLAlchemy model instance to create
            table_name: Name of the table
            supabase_data: Data to insert in Supabase format
        
        Returns:
            The created instance or None if creation fails
        """
        try:
            if self.use_supabase:
                logger.debug(f"Creating record in Supabase {table_name}")
                result = supabase_fallback.insert(table_name, supabase_data)
                if result:
                    logger.info(f"Created record in Supabase {table_name}")
                    return result
                return None
            else:
                logger.debug(f"Creating record in primary database {table_name}")
                db.add(model_instance)
                db.commit()
                db.refresh(model_instance)
                logger.info(f"Created record in primary database {table_name}")
                return model_instance
        except Exception as e:
            logger.error(f"Create failed for {table_name}: {e}")
            if not self.use_supabase:
                db.rollback()
            return None
    
    def read_with_fallback(
        self,
        supabase_read_func,
        primary_read_func,
        table_name: str
    ) -> Optional[Any]:
        """
        Read a record using the database determined at initialization.
        No fallback attempts during operation - uses Supabase if available at startup, otherwise local DB.
        
        Args:
            supabase_read_func: Function that performs the Supabase read
            primary_read_func: Function that performs the primary database read
            table_name: Name of the table being read
        
        Returns:
            The read record or None if read fails
        """
        return self.query_with_fallback(supabase_read_func, primary_read_func, table_name)
    
    def update_with_fallback(
        self,
        db: Session,
        db_instance,
        updates: Dict[str, Any],
        table_name: str,
        id_value: int
    ) -> Optional[Any]:
        """
        Update a record using the database determined at initialization.
        No fallback attempts during operation - uses Supabase if available at startup, otherwise local DB.
        
        Args:
            db: SQLAlchemy session
            db_instance: SQLAlchemy model instance to update
            updates: Dictionary of updates to apply
            table_name: Name of the table
            id_value: ID of the record being updated
        
        Returns:
            The updated instance or None if update fails
        """
        try:
            if self.use_supabase:
                logger.debug(f"Updating record in Supabase {table_name}")
                result = supabase_fallback.update(table_name, id_value, updates)
                if result:
                    logger.info(f"Updated record in Supabase {table_name}")
                    return result
                return None
            else:
                logger.debug(f"Updating record in primary database {table_name}")
                for key, value in updates.items():
                    setattr(db_instance, key, value)
                db.commit()
                db.refresh(db_instance)
                logger.info(f"Updated record in primary database {table_name}")
                return db_instance
        except Exception as e:
            logger.error(f"Update failed for {table_name}: {e}")
            if not self.use_supabase:
                db.rollback()
            return None
    
    def delete_with_fallback(
        self,
        db: Session,
        db_instance,
        table_name: str,
        id_value: int
    ) -> bool:
        """
        Delete a record using the database determined at initialization.
        No fallback attempts during operation - uses Supabase if available at startup, otherwise local DB.
        
        Args:
            db: SQLAlchemy session
            db_instance: SQLAlchemy model instance to delete
            table_name: Name of the table
            id_value: ID of the record being deleted
        
        Returns:
            True if deletion succeeded, False otherwise
        """
        try:
            if self.use_supabase:
                logger.debug(f"Deleting record from Supabase {table_name}")
                result = supabase_fallback.delete(table_name, id_value)
                if result:
                    logger.info(f"Deleted record from Supabase {table_name}")
                    return True
                return False
            else:
                logger.debug(f"Deleting record from primary database {table_name}")
                db.delete(db_instance)
                db.commit()
                logger.info(f"Deleted record from primary database {table_name}")
                return True
        except Exception as e:
            logger.error(f"Delete failed for {table_name}: {e}")
            if not self.use_supabase:
                db.rollback()
            return False


# Global database fallback instance
db_fallback = DatabaseFallback()
