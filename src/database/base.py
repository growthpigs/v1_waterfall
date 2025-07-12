"""
Base database connection utilities for Brand BOS
Provides Supabase connection management
"""

from supabase import Client
from .supabase_client import get_supabase


class SupabaseConnection:
    """Supabase connection manager"""
    
    def __init__(self):
        self._client = None
    
    def get_client(self) -> Client:
        """Get Supabase client instance"""
        if self._client is None:
            self._client = get_supabase()
        return self._client