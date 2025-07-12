"""
Phase Response model for storing individual phase execution results.
Tracks responses, token usage, and execution metrics for each phase.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import Field, validator, model_validator

from .base import BaseCIAModel, MetadataMixin, BaseModel
from ...config.constants import CIAPhase, PhaseStatus


class PhaseResponseBase(BaseModel):
    """Base fields for phase response creation."""
    session_id: UUID = Field(..., description="Associated CIA session ID")
    phase_id: CIAPhase = Field(..., description="CIA phase identifier")
    
    # Execution details
    prompt_used: str = Field(..., description="Compressed prompt used for this phase")
    response_content: Dict[str, Any] = Field(..., description="Phase analysis response")
    
    # Framework extraction
    extracted_frameworks: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted customer psychology frameworks"
    )
    
    # Token tracking
    prompt_tokens: int = Field(..., description="Tokens used in prompt")
    response_tokens: int = Field(..., description="Tokens in response")
    total_tokens: int = Field(..., description="Total tokens for phase")
    context_usage_percentage: float = Field(..., description="Percentage of context window used")
    
    @validator('context_usage_percentage')
    def validate_context_usage(cls, v):
        """Ensure context usage is between 0 and 100."""
        if not 0 <= v <= 100:
            raise ValueError("Context usage must be between 0 and 100")
        return v


class PhaseResponse(BaseCIAModel, PhaseResponseBase, MetadataMixin):
    """Complete phase response model with all fields."""
    
    # Status tracking
    status: PhaseStatus = Field(default=PhaseStatus.PENDING)
    attempt_number: int = Field(default=1, description="Retry attempt number")
    
    # Timing
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    duration_seconds: Optional[float] = Field(None)
    
    # Human-in-loop
    requires_human_input: bool = Field(default=False)
    human_input_type: Optional[str] = Field(None)
    human_input_received_at: Optional[datetime] = Field(None)
    human_input_data: Optional[Dict[str, Any]] = Field(None)
    
    # Error tracking
    error_message: Optional[str] = Field(None)
    error_details: Optional[Dict[str, Any]] = Field(None)
    
    # Quality metrics
    framework_preservation_score: Optional[float] = Field(
        None, 
        description="Score indicating framework preservation quality (0-1)"
    )
    response_quality_score: Optional[float] = Field(
        None,
        description="AI-evaluated response quality score (0-1)"
    )
    
    @model_validator(mode='after')
    def calculate_duration(self) -> 'PhaseResponse':
        """Calculate duration if both timestamps are present."""
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            self.duration_seconds = duration.total_seconds()
        return self
    
    def is_successful(self) -> bool:
        """Check if phase completed successfully."""
        return self.status == PhaseStatus.COMPLETED and self.error_message is None
    
    def exceeded_context_threshold(self, threshold: float = 0.70) -> bool:
        """Check if context usage exceeded threshold."""
        return self.context_usage_percentage > (threshold * 100)
    
    def get_framework_types(self) -> List[str]:
        """Get list of extracted framework types."""
        return list(self.extracted_frameworks.keys())
    
    class Config:
        json_encoders = {
            CIAPhase: lambda v: v.value,
            PhaseStatus: lambda v: v.value,
        }


class PhaseResponseCreate(PhaseResponseBase):
    """Schema for creating a new phase response."""
    status: Optional[PhaseStatus] = Field(default=PhaseStatus.EXECUTING)
    started_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class PhaseResponseUpdate(BaseModel):
    """Schema for updating a phase response."""
    status: Optional[PhaseStatus] = None
    response_content: Optional[Dict[str, Any]] = None
    extracted_frameworks: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None
    human_input_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    framework_preservation_score: Optional[float] = None
    response_quality_score: Optional[float] = None
    
    class Config:
        json_encoders = {
            PhaseStatus: lambda v: v.value if v else None,
        }


class PhaseResponseSummary(BaseModel):
    """Summary view of phase response for listing."""
    id: UUID
    session_id: UUID
    phase_id: CIAPhase
    status: PhaseStatus
    total_tokens: int
    context_usage_percentage: float
    duration_seconds: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]
    requires_human_input: bool
    error_message: Optional[str]
    
    class Config:
        json_encoders = {
            CIAPhase: lambda v: v.value,
            PhaseStatus: lambda v: v.value,
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }