"""
Supabase client for fallback database operations.
This module provides fallback database connectivity when the primary database is unavailable.
"""

import os
import logging
from typing import Optional, List, Dict, Any


logger = logging.getLogger(__name__)

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase library not installed. Supabase fallback will not be available.")


class SupabaseClient:
    """Wrapper for Supabase operations with fallback capability."""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.is_connected = False
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize Supabase client with credentials from environment."""
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase is not available. Install with: pip install supabase")
            return
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.info(
                "SUPABASE_URL and/or SUPABASE_KEY not set. "
                "Set these env variables to enable Supabase fallback."
            )
            return
        
        try:
            self.client = create_client(supabase_url, supabase_key)
            self.is_connected = True
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.is_connected = False
    
    def insert(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Insert a record into a Supabase table."""
        if not self.is_connected or not self.client:
            logger.warning(f"Supabase not connected. Cannot insert into {table}")
            return None
        
        try:
            response = self.client.table(table).insert(data).execute()
            logger.debug(f"Inserted into {table}: {response.data}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error inserting into {table}: {e}")
            return None
    
    def select(self, table: str, query: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Select records from a Supabase table."""
        if not self.is_connected or not self.client:
            logger.warning(f"Supabase not connected. Cannot select from {table}")
            return None
        
        try:
            result = self.client.table(table).select("*")
            if query:
                # Apply simple query like: "id=eq.5"
                result = result.filter(query)
            response = result.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error selecting from {table}: {e}")
            return None
    
    def get_by_id(self, table: str, id_value: int, id_column: str = "id") -> Optional[Dict[str, Any]]:
        """Get a single record by ID from a Supabase table."""
        if not self.is_connected or not self.client:
            logger.warning(f"Supabase not connected. Cannot fetch from {table}")
            return None
        
        try:
            response = self.client.table(table).select("*").eq(id_column, id_value).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching {id_column}={id_value} from {table}: {e}")
            return None
    
    def get_by_email(self, table: str, email: str) -> Optional[Dict[str, Any]]:
        """Get a single record by email from a Supabase table."""
        if not self.is_connected or not self.client:
            logger.warning(f"Supabase not connected. Cannot fetch from {table}")
            return None
        
        try:
            response = self.client.table(table).select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching email={email} from {table}: {e}")
            return None
    
    def update(self, table: str, id_value: int, data: Dict[str, Any], id_column: str = "id") -> Optional[Dict[str, Any]]:
        """Update a record in a Supabase table."""
        if not self.is_connected or not self.client:
            logger.warning(f"Supabase not connected. Cannot update {table}")
            return None
        
        try:
            response = self.client.table(table).update(data).eq(id_column, id_value).execute()
            logger.debug(f"Updated {table}: {response.data}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating {table}: {e}")
            return None
    
    def delete(self, table: str, id_value: int, id_column: str = "id") -> bool:
        """Delete a record from a Supabase table."""
        if not self.is_connected or not self.client:
            logger.warning(f"Supabase not connected. Cannot delete from {table}")
            return False
        
        try:
            response = self.client.table(table).delete().eq(id_column, id_value).execute()
            logger.debug(f"Deleted from {table}: {id_column}={id_value}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from {table}: {e}")
            return False
    
    def filter_by(self, table: str, **filters) -> Optional[List[Dict[str, Any]]]:
        """Filter records from a Supabase table."""
        if not self.is_connected or not self.client:
            logger.warning(f"Supabase not connected. Cannot filter {table}")
            return None
        
        try:
            query = self.client.table(table).select("*")
            for key, value in filters.items():
                query = query.eq(key, value)
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error filtering {table}: {e}")
            return None


# Global Supabase client instance
supabase_fallback = SupabaseClient()
