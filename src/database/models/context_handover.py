"""
Context Handover model for managing context window limits.
Creates recoverable session state when approaching token limits.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import Field, validator, model_validator

from .base import BaseCIAModel, MetadataMixin, BaseModel
from ...config.constants import CIAPhase


class ContextHandoverBase(BaseModel):
    """Base fields for context handover creation."""
    session_id: UUID = Field(..., description="Associated CIA session ID")
    current_phase: CIAPhase = Field(..., description="Phase when handover was created")
    
    # Context state
    context_usage_percentage: float = Field(
        ...,
        description="Context window usage percentage at handover"
    )
    total_tokens_used: int = Field(
        ...,
        description="Total tokens consumed before handover"
    )
    
    # Session state
    completed_phases: List[CIAPhase] = Field(
        ...,
        description="List of completed phases"
    )
    pending_phases: List[CIAPhase] = Field(
        ...,
        description="List of pending phases"
    )
    
    # Critical state for resumption
    critical_state: Dict[str, Any] = Field(
        ...,
        description="Essential state data for session recovery"
    )
    next_action: str = Field(
        ...,
        description="Clear instruction for next action on resume"
    )
    
    @validator('context_usage_percentage')
    def validate_usage(cls, v):
        """Ensure context usage is valid percentage."""
        if not 0 <= v <= 100:
            raise ValueError("Context usage must be between 0 and 100")
        return v


class ContextHandover(BaseCIAModel, ContextHandoverBase, MetadataMixin):
    """Complete context handover model with all fields."""
    
    # Archive references
    latest_archive_id: Optional[UUID] = Field(
        None,
        description="ID of most recent Master Archive"
    )
    preserved_archives: List[UUID] = Field(
        default_factory=list,
        description="All Master Archive IDs to preserve"
    )
    
    # Intelligence summary
    intelligence_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Condensed intelligence from completed phases"
    )
    framework_status: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Status of framework preservation"
    )
    
    # Human-in-loop state
    pending_human_inputs: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Any pending human input requirements"
    )
    
    # Recovery instructions
    recovery_instructions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed instructions for session recovery"
    )
    handover_notes: Optional[str] = Field(
        None,
        description="Human-readable notes about handover"
    )
    
    # Usage tracking
    handover_number: int = Field(
        default=1,
        description="Sequential handover number for this session"
    )
    previous_handover_id: Optional[UUID] = Field(
        None,
        description="ID of previous handover if exists"
    )
    
    # Recovery status
    recovered: bool = Field(default=False, description="Whether handover has been recovered")
    recovered_at: Optional[datetime] = Field(None)
    recovery_session_id: Optional[UUID] = Field(None, description="New session ID if recovered")
    
    def generate_recovery_prompt(self) -> str:
        """Generate a prompt for recovering this handover."""
        prompt = f"""
        CONTEXT HANDOVER RECOVERY - Session {self.session_id}
        
        Current Status:
        - Phase: {self.current_phase}
        - Completed Phases: {', '.join(self.completed_phases)}
        - Context Usage: {self.context_usage_percentage}%
        - Handover Number: {self.handover_number}
        
        Next Action: {self.next_action}
        
        Critical State:
        {self.critical_state}
        
        Recovery Instructions:
        {self.recovery_instructions}
        
        Please continue the CIA analysis from this point.
        """
        return prompt.strip()
    
    def get_recovery_context(self) -> Dict[str, Any]:
        """Get minimal context needed for recovery."""
        return {
            "session_id": str(self.session_id),
            "current_phase": self.current_phase,
            "completed_phases": self.completed_phases,
            "latest_archive_id": str(self.latest_archive_id) if self.latest_archive_id else None,
            "critical_state": self.critical_state,
            "intelligence_summary": self.intelligence_summary,
            "framework_status": self.framework_status,
            "pending_human_inputs": self.pending_human_inputs,
        }
    
    def validate_recovery_readiness(self) -> Dict[str, bool]:
        """Validate handover has all required data for recovery."""
        checks = {
            "has_critical_state": bool(self.critical_state),
            "has_next_action": bool(self.next_action),
            "has_completed_phases": bool(self.completed_phases),
            "has_intelligence_summary": bool(self.intelligence_summary),
            "has_recovery_instructions": bool(self.recovery_instructions),
        }
        checks["ready_for_recovery"] = all(checks.values())
        return checks
    
    class Config:
        json_encoders = {
            CIAPhase: lambda v: v.value,
        }


class ContextHandoverCreate(ContextHandoverBase):
    """Schema for creating a new context handover."""
    handover_number: Optional[int] = Field(default=1)
    previous_handover_id: Optional[UUID] = None
    latest_archive_id: Optional[UUID] = None
    preserved_archives: Optional[List[UUID]] = Field(default_factory=list)
    intelligence_summary: Optional[Dict[str, Any]] = Field(default_factory=dict)
    framework_status: Optional[Dict[str, Dict[str, Any]]] = Field(default_factory=dict)
    recovery_instructions: Optional[Dict[str, Any]] = Field(default_factory=dict)
    handover_notes: Optional[str] = None


class ContextHandoverUpdate(BaseModel):
    """Schema for updating a context handover."""
    recovered: Optional[bool] = None
    recovered_at: Optional[datetime] = None
    recovery_session_id: Optional[UUID] = None
    handover_notes: Optional[str] = None


class ContextHandoverSummary(BaseModel):
    """Summary view of context handover for listing."""
    id: UUID
    session_id: UUID
    current_phase: CIAPhase
    context_usage_percentage: float
    handover_number: int
    recovered: bool
    created_at: datetime
    recovered_at: Optional[datetime]
    
    class Config:
        json_encoders = {
            CIAPhase: lambda v: v.value,
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }