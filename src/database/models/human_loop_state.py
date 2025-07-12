"""
Human Loop State model for tracking human-in-loop workflows.
Manages pause points, notifications, and response data.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import Field, validator, model_validator

from .base import BaseCIAModel, MetadataMixin, BaseModel
from ...config.constants import HumanLoopType, NotificationType


class HumanLoopStateBase(BaseModel):
    """Base fields for human loop state creation."""
    session_id: UUID = Field(..., description="Associated CIA session ID")
    phase_id: str = Field(..., description="Phase requiring human input")
    loop_type: HumanLoopType = Field(..., description="Type of human intervention required")
    
    # Request details
    request_data: Dict[str, Any] = Field(
        ...,
        description="Data sent with human input request"
    )
    request_message: str = Field(
        ...,
        description="Human-readable message describing required action"
    )
    
    # Notification settings
    notification_channels: List[str] = Field(
        default_factory=lambda: ["slack", "email"],
        description="Channels to send notifications"
    )
    notification_recipients: List[str] = Field(
        default_factory=list,
        description="Specific recipients for notifications"
    )


class HumanLoopState(BaseCIAModel, HumanLoopStateBase, MetadataMixin):
    """Complete human loop state model with all fields."""
    
    # Status tracking
    status: str = Field(default="waiting", description="Status: waiting, completed, expired, error")
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = Field(None)
    expired_at: Optional[datetime] = Field(None)
    
    # Response tracking
    response_data: Optional[Dict[str, Any]] = Field(None, description="Human-provided response data")
    response_validated: bool = Field(default=False, description="Whether response passed validation")
    validation_errors: Optional[List[str]] = Field(None, description="Validation error messages")
    
    # Notification tracking
    notifications_sent: Dict[str, bool] = Field(
        default_factory=dict,
        description="Track which notifications were sent successfully"
    )
    notification_errors: Dict[str, str] = Field(
        default_factory=dict,
        description="Any errors during notification delivery"
    )
    
    # Retry tracking
    retry_count: int = Field(default=0, description="Number of notification retry attempts")
    last_retry_at: Optional[datetime] = Field(None)
    
    # Timeout configuration
    timeout_minutes: int = Field(default=30, description="Minutes before expiration")
    reminder_sent: bool = Field(default=False, description="Whether reminder was sent")
    reminder_sent_at: Optional[datetime] = Field(None)
    
    @model_validator(mode='after')
    def calculate_expiration(self) -> 'HumanLoopState':
        """Calculate expiration time based on timeout."""
        if self.sent_at and self.timeout_minutes and not self.expired_at:
            from datetime import timedelta
            self.expired_at = self.sent_at + timedelta(minutes=self.timeout_minutes)
        return self
    
    def is_expired(self) -> bool:
        """Check if the human loop has expired."""
        if self.expired_at:
            return datetime.utcnow() > self.expired_at
        return False
    
    def is_complete(self) -> bool:
        """Check if human input has been received and validated."""
        return self.status == "completed" and self.response_validated
    
    def needs_reminder(self) -> bool:
        """Check if a reminder should be sent."""
        if self.reminder_sent or self.status != "waiting":
            return False
        
        if self.sent_at and self.timeout_minutes:
            from datetime import timedelta
            half_timeout = timedelta(minutes=self.timeout_minutes / 2)
            return datetime.utcnow() > (self.sent_at + half_timeout)
        
        return False
    
    def get_elapsed_minutes(self) -> float:
        """Get minutes elapsed since notification sent."""
        if self.sent_at:
            elapsed = datetime.utcnow() - self.sent_at
            return elapsed.total_seconds() / 60
        return 0.0
    
    def validate_response(self) -> bool:
        """Validate the response data based on loop type."""
        if not self.response_data:
            self.validation_errors = ["No response data provided"]
            return False
        
        validation_errors = []
        
        if self.loop_type == HumanLoopType.DATAFORSEO_KEYWORDS:
            # Validate DataForSEO response
            required_fields = ["search_volume", "competition", "cpc"]
            for field in required_fields:
                if field not in self.response_data:
                    validation_errors.append(f"Missing required field: {field}")
        
        elif self.loop_type == HumanLoopType.PERPLEXITY_TRENDS:
            # Validate Perplexity response
            if "research_results" not in self.response_data:
                validation_errors.append("Missing research_results field")
            elif not isinstance(self.response_data["research_results"], str):
                validation_errors.append("research_results must be a string")
        
        elif self.loop_type == HumanLoopType.TESTIMONIALS_REQUEST:
            # Validate testimonials response
            if "testimonials" not in self.response_data and "skip" not in self.response_data:
                validation_errors.append("Must provide testimonials or skip flag")
        
        self.validation_errors = validation_errors if validation_errors else None
        self.response_validated = len(validation_errors) == 0
        return self.response_validated
    
    class Config:
        json_encoders = {
            HumanLoopType: lambda v: v.value,
        }


class HumanLoopStateCreate(HumanLoopStateBase):
    """Schema for creating a new human loop state."""
    timeout_minutes: Optional[int] = Field(default=30)


class HumanLoopStateUpdate(BaseModel):
    """Schema for updating a human loop state."""
    status: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    responded_at: Optional[datetime] = None
    reminder_sent: Optional[bool] = None
    reminder_sent_at: Optional[datetime] = None
    retry_count: Optional[int] = None
    last_retry_at: Optional[datetime] = None


class HumanLoopResponse(BaseModel):
    """Schema for human input response submission."""
    session_id: UUID
    loop_id: UUID
    response_data: Dict[str, Any]
    
    class Config:
        json_encoders = {
            UUID: lambda v: str(v),
        }