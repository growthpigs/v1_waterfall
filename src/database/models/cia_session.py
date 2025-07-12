"""
CIA Session model for managing analysis sessions.
Tracks session state, configuration, and progress through phases.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import Field, validator, model_validator

from .base import BaseCIAModel, MetadataMixin
from ...config.constants import CIAPhase, PhaseStatus
from pydantic import BaseModel


class CIASessionBase(BaseModel):
    """Base fields for CIA session creation and updates."""
    url: str = Field(..., description="Target business URL for analysis")
    company_name: str = Field(..., description="Company or brand name")
    kpoi: str = Field(..., description="Key Person of Influence name")
    country: str = Field(..., description="Primary country of operation")
    testimonials_url: Optional[str] = Field(None, description="URL for testimonials page")
    
    @validator('url')
    def validate_url(cls, v):
        """Ensure URL is properly formatted."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v.strip()
    
    @validator('country')
    def validate_country(cls, v):
        """Ensure country is properly formatted."""
        return v.strip().title()


class CIASession(BaseCIAModel, CIASessionBase, MetadataMixin):
    """Complete CIA session model with all fields."""
    
    # Session state
    status: PhaseStatus = Field(default=PhaseStatus.PENDING)
    current_phase: Optional[CIAPhase] = Field(None, description="Current phase being executed")
    completed_phases: List[CIAPhase] = Field(default_factory=list)
    failed_phases: List[CIAPhase] = Field(default_factory=list)
    
    # Progress tracking
    total_phases: int = Field(default=15, description="Total number of phases")
    progress_percentage: float = Field(default=0.0, description="Overall completion percentage")
    
    # Context management
    total_tokens_used: int = Field(default=0, description="Total tokens consumed across all phases")
    handover_count: int = Field(default=0, description="Number of context handovers created")
    last_handover_at: Optional[datetime] = Field(None)
    
    # Timing
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    paused_at: Optional[datetime] = Field(None)
    
    # Human-in-loop tracking
    human_inputs_pending: List[str] = Field(default_factory=list)
    human_inputs_completed: List[str] = Field(default_factory=list)
    
    # Configuration
    auto_resume: bool = Field(default=True, description="Automatically resume after human input")
    notification_channels: List[str] = Field(default_factory=lambda: ["slack", "email"])
    
    @model_validator(mode='after')
    def calculate_progress(self) -> 'CIASession':
        """Calculate progress percentage based on completed phases."""
        if self.total_phases > 0:
            self.progress_percentage = (len(self.completed_phases) / self.total_phases) * 100
        return self
    
    def is_complete(self) -> bool:
        """Check if all phases are completed."""
        return len(self.completed_phases) == self.total_phases
    
    def requires_human_input(self) -> bool:
        """Check if session is waiting for human input."""
        return len(self.human_inputs_pending) > 0
    
    def can_proceed(self) -> bool:
        """Check if session can proceed to next phase."""
        return (
            self.status not in [PhaseStatus.FAILED, PhaseStatus.COMPLETED] 
            and not self.requires_human_input()
        )
    
    def get_next_phase(self) -> Optional[CIAPhase]:
        """Determine the next phase to execute."""
        from ...config.constants import CIA_PHASE_ORDER
        
        for phase in CIA_PHASE_ORDER:
            if phase not in self.completed_phases and phase not in self.failed_phases:
                return phase
        return None
    
    class Config:
        json_encoders = {
            CIAPhase: lambda v: v.value,
            PhaseStatus: lambda v: v.value,
        }


class CIASessionCreate(CIASessionBase):
    """Schema for creating a new CIA session."""
    notification_channels: Optional[List[str]] = Field(default_factory=lambda: ["slack", "email"])
    auto_resume: Optional[bool] = Field(default=True)


class CIASessionUpdate(BaseModel):
    """Schema for updating a CIA session."""
    status: Optional[PhaseStatus] = None
    current_phase: Optional[CIAPhase] = None
    notification_channels: Optional[List[str]] = None
    auto_resume: Optional[bool] = None
    
    class Config:
        json_encoders = {
            CIAPhase: lambda v: v.value if v else None,
            PhaseStatus: lambda v: v.value if v else None,
        }


class CIASessionResponse(CIASession):
    """Response schema for CIA session with computed fields."""
    
    # Computed fields
    duration_minutes: Optional[float] = Field(None)
    estimated_completion_time: Optional[datetime] = Field(None)
    
    @model_validator(mode='after')
    def compute_fields(self) -> 'CIASessionResponse':
        """Compute additional response fields."""
        # Calculate duration
        if self.started_at:
            end_time = self.completed_at or datetime.utcnow()
            duration = end_time - self.started_at
            self.duration_minutes = duration.total_seconds() / 60
        
        # Estimate completion time
        if self.status == PhaseStatus.EXECUTING and self.progress_percentage > 0:
            elapsed = datetime.utcnow() - self.started_at if self.started_at else None
            if elapsed:
                total_estimated = elapsed * (100 / self.progress_percentage)
                self.estimated_completion_time = self.started_at + total_estimated
        
        return self