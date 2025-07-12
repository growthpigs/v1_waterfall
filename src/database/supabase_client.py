"""
Supabase client configuration and connection management.
Provides singleton client instance with connection pooling.
"""

import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import logging

from supabase import create_client, Client
from supabase.client import ClientOptions
import httpx

from ..config.settings import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Manages Supabase client connection with singleton pattern."""
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    _service_client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Supabase clients if not already initialized."""
        if self._client is None:
            self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize both anon and service role clients."""
        try:
            # Configure client options
            client_options = ClientOptions(
                postgrest_client_timeout=30,
                storage_client_timeout=30,
            )
            
            # Create anon/public client for general operations
            self._client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_key,
                options=client_options
            )
            
            # Create service role client for admin operations
            self._service_client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_service_key,
                options=client_options
            )
            
            logger.info("Supabase clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase clients: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """Get the anon/public Supabase client."""
        if self._client is None:
            self._initialize_clients()
        return self._client
    
    @property
    def service_client(self) -> Client:
        """Get the service role Supabase client."""
        if self._service_client is None:
            self._initialize_clients()
        return self._service_client
    
    async def test_connection(self) -> bool:
        """Test the Supabase connection."""
        try:
            # Test with a simple query
            result = self.client.table('cia_sessions').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    async def execute_rpc(self, function_name: str, params: Dict[str, Any]) -> Any:
        """Execute a Supabase RPC function."""
        try:
            result = self.client.rpc(function_name, params).execute()
            return result.data
        except Exception as e:
            logger.error(f"RPC execution failed for {function_name}: {e}")
            raise
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for database transactions (placeholder for future implementation)."""
        # Note: Supabase doesn't directly support transactions through the client library
        # This is a placeholder for potential future implementation or workaround
        yield self.client
    
    def get_table(self, table_name: str, use_service_role: bool = False):
        """Get a table reference with appropriate client."""
        client = self.service_client if use_service_role else self.client
        return client.table(table_name)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check."""
        health_status = {
            "status": "healthy",
            "checks": {
                "database": False,
                "auth": False,
                "storage": False,
            }
        }
        
        try:
            # Check database connection
            await self.test_connection()
            health_status["checks"]["database"] = True
            
            # Check auth service
            try:
                self.client.auth.get_session()
                health_status["checks"]["auth"] = True
            except:
                pass  # Auth might not be configured yet
            
            # Check storage service
            try:
                self.client.storage.list_buckets()
                health_status["checks"]["storage"] = True
            except:
                pass  # Storage might not be configured yet
            
            # Determine overall status
            if not all(health_status["checks"].values()):
                health_status["status"] = "degraded"
                
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Health check failed: {e}")
        
        return health_status


# Global Supabase client instance
supabase_client = SupabaseClient()

# Convenience functions for direct access
def get_supabase() -> Client:
    """Get the Supabase client instance."""
    return supabase_client.client

def get_supabase_service() -> Client:
    """Get the Supabase service role client instance."""
    return supabase_client.service_client