"""
Base models and mixins for CIA system.
Provides common fields and functionality for all models.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class UUIDMixin(BaseModel):
    """Mixin for UUID primary keys."""
    id: UUID = Field(default_factory=uuid4)


class ClientMixin(BaseModel):
    """Mixin for multi-tenant client association."""
    client_id: UUID = Field(..., description="Client identifier for multi-tenant isolation")


class BaseORMModel(BaseModel):
    """Base model with ORM mode configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )


class BaseCIAModel(BaseORMModel, UUIDMixin, TimestampMixin, ClientMixin):
    """Base model for all CIA entities with common fields."""
    pass


class MetadataMixin(BaseModel):
    """Mixin for flexible metadata storage."""
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)