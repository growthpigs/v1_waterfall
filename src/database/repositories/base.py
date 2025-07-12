"""
Base repository class with common CRUD operations.
Provides reusable patterns for all repositories.
"""

from typing import TypeVar, Generic, Type, List, Optional, Dict, Any
from uuid import UUID
import logging
from datetime import datetime

from pydantic import BaseModel
from supabase import Client

from ..supabase_client import get_supabase, get_supabase_service
from ...config.settings import settings

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository with common CRUD operations."""
    
    def __init__(
        self,
        model: Type[ModelType],
        table_name: str,
        use_service_role: bool = False
    ):
        """Initialize repository with model and table name."""
        self.model = model
        self.table_name = table_name
        self.use_service_role = use_service_role
        self._client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Get Supabase client instance."""
        if self._client is None:
            self._client = get_supabase_service() if self.use_service_role else get_supabase()
        return self._client
    
    @property
    def table(self):
        """Get table reference."""
        return self.client.table(self.table_name)
    
    async def create(self, data: CreateSchemaType, client_id: Optional[UUID] = None) -> ModelType:
        """Create a new record."""
        try:
            # Convert Pydantic model to dict
            record_data = data.model_dump(mode='json', exclude_unset=True)
            
            # Add client_id if provided and not in data
            if client_id and 'client_id' not in record_data:
                record_data['client_id'] = str(client_id)
            
            # Ensure UUIDs are strings
            record_data = self._serialize_uuids(record_data)
            
            # Insert record
            result = self.table.insert(record_data).execute()
            
            if result.data:
                return self.model(**result.data[0])
            else:
                raise ValueError("No data returned from insert")
                
        except Exception as e:
            logger.error(f"Failed to create {self.model.__name__}: {e}")
            raise
    
    async def get_by_id(self, id: UUID, client_id: Optional[UUID] = None) -> Optional[ModelType]:
        """Get a record by ID."""
        try:
            query = self.table.select("*").eq("id", str(id))
            
            # Add client_id filter if provided
            if client_id:
                query = query.eq("client_id", str(client_id))
            
            result = query.single().execute()
            
            if result.data:
                return self.model(**result.data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get {self.model.__name__} by id {id}: {e}")
            return None
    
    async def get_all(
        self,
        client_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> List[ModelType]:
        """Get all records with pagination."""
        try:
            query = self.table.select("*")
            
            # Add client_id filter if provided
            if client_id:
                query = query.eq("client_id", str(client_id))
            
            # Add ordering
            query = query.order(order_by, desc=order_desc)
            
            # Add pagination
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            
            return [self.model(**record) for record in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get all {self.model.__name__}: {e}")
            return []
    
    async def update(
        self,
        id: UUID,
        data: UpdateSchemaType,
        client_id: Optional[UUID] = None
    ) -> Optional[ModelType]:
        """Update a record by ID."""
        try:
            # Convert update data to dict
            update_data = data.model_dump(mode='json', exclude_unset=True)
            
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Ensure UUIDs are strings
            update_data = self._serialize_uuids(update_data)
            
            # Build query
            query = self.table.update(update_data).eq("id", str(id))
            
            # Add client_id filter if provided
            if client_id:
                query = query.eq("client_id", str(client_id))
            
            result = query.execute()
            
            if result.data:
                return self.model(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to update {self.model.__name__} {id}: {e}")
            return None
    
    async def delete(self, id: UUID, client_id: Optional[UUID] = None) -> bool:
        """Delete a record by ID."""
        try:
            query = self.table.delete().eq("id", str(id))
            
            # Add client_id filter if provided
            if client_id:
                query = query.eq("client_id", str(client_id))
            
            result = query.execute()
            
            # Check if any rows were deleted
            return len(result.data) > 0 if result.data else False
            
        except Exception as e:
            logger.error(f"Failed to delete {self.model.__name__} {id}: {e}")
            return False
    
    async def exists(self, id: UUID, client_id: Optional[UUID] = None) -> bool:
        """Check if a record exists."""
        try:
            query = self.table.select("id").eq("id", str(id))
            
            # Add client_id filter if provided
            if client_id:
                query = query.eq("client_id", str(client_id))
            
            result = query.execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to check existence of {self.model.__name__} {id}: {e}")
            return False
    
    async def count(self, client_id: Optional[UUID] = None, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters."""
        try:
            query = self.table.select("id", count="exact")
            
            # Add client_id filter if provided
            if client_id:
                query = query.eq("client_id", str(client_id))
            
            # Add additional filters
            if filters:
                for key, value in filters.items():
                    if isinstance(value, (list, tuple)):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            result = query.execute()
            
            return result.count or 0
            
        except Exception as e:
            logger.error(f"Failed to count {self.model.__name__}: {e}")
            return 0
    
    def _serialize_uuids(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert UUID objects to strings recursively."""
        for key, value in data.items():
            if isinstance(value, UUID):
                data[key] = str(value)
            elif isinstance(value, dict):
                data[key] = self._serialize_uuids(value)
            elif isinstance(value, list):
                data[key] = [
                    str(item) if isinstance(item, UUID) else item
                    for item in value
                ]
        return data
    
    async def bulk_create(self, items: List[CreateSchemaType], client_id: Optional[UUID] = None) -> List[ModelType]:
        """Create multiple records in bulk."""
        try:
            # Convert all items to dicts
            records_data = []
            for item in items:
                record_data = item.model_dump(mode='json', exclude_unset=True)
                if client_id and 'client_id' not in record_data:
                    record_data['client_id'] = str(client_id)
                record_data = self._serialize_uuids(record_data)
                records_data.append(record_data)
            
            # Bulk insert
            result = self.table.insert(records_data).execute()
            
            return [self.model(**record) for record in result.data]
            
        except Exception as e:
            logger.error(f"Failed to bulk create {self.model.__name__}: {e}")
            return []