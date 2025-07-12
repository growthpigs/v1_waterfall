"""
Tests for Supabase client configuration and connection.
Validates singleton pattern and connection management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from ..database.supabase_client import SupabaseClient, get_supabase, get_supabase_service


class TestSupabaseClient:
    """Test SupabaseClient functionality."""
    
    def test_singleton_pattern(self):
        """Test that SupabaseClient follows singleton pattern."""
        client1 = SupabaseClient()
        client2 = SupabaseClient()
        
        assert client1 is client2
        assert id(client1) == id(client2)
    
    @patch('src.database.supabase_client.create_client')
    def test_client_initialization(self, mock_create_client):
        """Test client initialization with proper configuration."""
        # Clear existing instance
        SupabaseClient._instance = None
        SupabaseClient._client = None
        SupabaseClient._service_client = None
        
        # Configure mock
        mock_anon_client = Mock()
        mock_service_client = Mock()
        mock_create_client.side_effect = [mock_anon_client, mock_service_client]
        
        # Initialize client
        client = SupabaseClient()
        
        # Verify two clients created
        assert mock_create_client.call_count == 2
        
        # Verify correct parameters
        calls = mock_create_client.call_args_list
        
        # First call - anon client
        assert calls[0][0][0] == os.environ.get("SUPABASE_URL")
        assert calls[0][0][1] == os.environ.get("SUPABASE_KEY")
        
        # Second call - service client
        assert calls[1][0][0] == os.environ.get("SUPABASE_URL")
        assert calls[1][0][1] == os.environ.get("SUPABASE_SERVICE_KEY")
    
    @patch('src.database.supabase_client.create_client')
    def test_client_properties(self, mock_create_client):
        """Test client property accessors."""
        # Clear existing instance
        SupabaseClient._instance = None
        SupabaseClient._client = None
        SupabaseClient._service_client = None
        
        # Configure mock
        mock_anon_client = Mock()
        mock_service_client = Mock()
        mock_create_client.side_effect = [mock_anon_client, mock_service_client]
        
        # Initialize and access clients
        client = SupabaseClient()
        anon_client = client.client
        service_client = client.service_client
        
        # Verify
        assert anon_client == mock_anon_client
        assert service_client == mock_service_client
    
    @patch('src.database.supabase_client.create_client')
    async def test_connection_test(self, mock_create_client):
        """Test database connection testing."""
        # Clear existing instance
        SupabaseClient._instance = None
        SupabaseClient._client = None
        SupabaseClient._service_client = None
        
        # Configure mock
        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"id": "test"}])
        
        mock_anon_client = Mock()
        mock_anon_client.table.return_value = mock_table
        
        mock_create_client.side_effect = [mock_anon_client, Mock()]
        
        # Test connection
        client = SupabaseClient()
        result = await client.test_connection()
        
        # Verify
        assert result is True
        mock_anon_client.table.assert_called_with('cia_sessions')
        mock_table.select.assert_called_with('id')
        mock_table.limit.assert_called_with(1)
    
    @patch('src.database.supabase_client.create_client')
    async def test_connection_test_failure(self, mock_create_client):
        """Test connection test handling failures."""
        # Clear existing instance
        SupabaseClient._instance = None
        SupabaseClient._client = None
        SupabaseClient._service_client = None
        
        # Configure mock to raise exception
        mock_anon_client = Mock()
        mock_anon_client.table.side_effect = Exception("Connection failed")
        
        mock_create_client.side_effect = [mock_anon_client, Mock()]
        
        # Test connection
        client = SupabaseClient()
        result = await client.test_connection()
        
        # Verify
        assert result is False
    
    @patch('src.database.supabase_client.create_client')
    async def test_execute_rpc(self, mock_create_client):
        """Test RPC function execution."""
        # Clear existing instance
        SupabaseClient._instance = None
        SupabaseClient._client = None
        SupabaseClient._service_client = None
        
        # Configure mock
        mock_result = Mock(data={"result": "success"})
        mock_anon_client = Mock()
        mock_anon_client.rpc.return_value.execute.return_value = mock_result
        
        mock_create_client.side_effect = [mock_anon_client, Mock()]
        
        # Execute RPC
        client = SupabaseClient()
        result = await client.execute_rpc("test_function", {"param": "value"})
        
        # Verify
        assert result == {"result": "success"}
        mock_anon_client.rpc.assert_called_with("test_function", {"param": "value"})
    
    @patch('src.database.supabase_client.create_client')
    def test_get_table(self, mock_create_client):
        """Test getting table references."""
        # Clear existing instance
        SupabaseClient._instance = None
        SupabaseClient._client = None
        SupabaseClient._service_client = None
        
        # Configure mock
        mock_anon_table = Mock()
        mock_service_table = Mock()
        
        mock_anon_client = Mock()
        mock_anon_client.table.return_value = mock_anon_table
        
        mock_service_client = Mock()
        mock_service_client.table.return_value = mock_service_table
        
        mock_create_client.side_effect = [mock_anon_client, mock_service_client]
        
        # Get tables
        client = SupabaseClient()
        anon_table = client.get_table("test_table", use_service_role=False)
        service_table = client.get_table("test_table", use_service_role=True)
        
        # Verify
        assert anon_table == mock_anon_table
        assert service_table == mock_service_table
        mock_anon_client.table.assert_called_with("test_table")
        mock_service_client.table.assert_called_with("test_table")
    
    @patch('src.database.supabase_client.create_client')
    async def test_health_check(self, mock_create_client):
        """Test comprehensive health check."""
        # Clear existing instance
        SupabaseClient._instance = None
        SupabaseClient._client = None
        SupabaseClient._service_client = None
        
        # Configure mock
        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"id": "test"}])
        
        mock_auth = Mock()
        mock_auth.get_session.return_value = {"user": "test"}
        
        mock_storage = Mock()
        mock_storage.list_buckets.return_value = [{"name": "test-bucket"}]
        
        mock_anon_client = Mock()
        mock_anon_client.table.return_value = mock_table
        mock_anon_client.auth = mock_auth
        mock_anon_client.storage = mock_storage
        
        mock_create_client.side_effect = [mock_anon_client, Mock()]
        
        # Perform health check
        client = SupabaseClient()
        health = await client.health_check()
        
        # Verify
        assert health["status"] == "healthy"
        assert health["checks"]["database"] is True
        assert health["checks"]["auth"] is True
        assert health["checks"]["storage"] is True
    
    @patch('src.database.supabase_client.create_client')
    async def test_health_check_partial_failure(self, mock_create_client):
        """Test health check with partial service failures."""
        # Clear existing instance
        SupabaseClient._instance = None
        SupabaseClient._client = None
        SupabaseClient._service_client = None
        
        # Configure mock
        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"id": "test"}])
        
        mock_auth = Mock()
        mock_auth.get_session.side_effect = Exception("Auth error")
        
        mock_storage = Mock()
        mock_storage.list_buckets.side_effect = Exception("Storage error")
        
        mock_anon_client = Mock()
        mock_anon_client.table.return_value = mock_table
        mock_anon_client.auth = mock_auth
        mock_anon_client.storage = mock_storage
        
        mock_create_client.side_effect = [mock_anon_client, Mock()]
        
        # Perform health check
        client = SupabaseClient()
        health = await client.health_check()
        
        # Verify
        assert health["status"] == "degraded"
        assert health["checks"]["database"] is True
        assert health["checks"]["auth"] is False
        assert health["checks"]["storage"] is False


class TestSupabaseHelperFunctions:
    """Test helper functions for Supabase access."""
    
    @patch('src.database.supabase_client.supabase_client')
    def test_get_supabase(self, mock_client_instance):
        """Test get_supabase helper function."""
        mock_anon_client = Mock()
        mock_client_instance.client = mock_anon_client
        
        client = get_supabase()
        
        assert client == mock_anon_client
    
    @patch('src.database.supabase_client.supabase_client')
    def test_get_supabase_service(self, mock_client_instance):
        """Test get_supabase_service helper function."""
        mock_service_client = Mock()
        mock_client_instance.service_client = mock_service_client
        
        client = get_supabase_service()
        
        assert client == mock_service_client