"""
Master Archive model for intelligence synthesis between phases.
Preserves accumulated knowledge and frameworks across phase boundaries.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import Field, validator, model_validator

from .base import BaseCIAModel, MetadataMixin, BaseModel
from ...config.constants import CIAPhase


class MasterArchiveBase(BaseModel):
    """Base fields for master archive creation."""
    session_id: UUID = Field(..., description="Associated CIA session ID")
    phase_number: CIAPhase = Field(..., description="Phase that created this archive")
    
    # Core intelligence synthesis
    intelligence_summary: Dict[str, Any] = Field(
        ..., 
        description="Synthesized intelligence from completed phases"
    )
    
    # Framework preservation
    customer_psychology: Dict[str, Any] = Field(
        ...,
        description="Preserved Benson points 1-77+ customer psychology"
    )
    competitive_analysis: Dict[str, Any] = Field(
        ...,
        description="Accumulated competitive intelligence"
    )
    authority_positioning: Dict[str, Any] = Field(
        ...,
        description="Priestley 5 P's framework analysis"
    )
    content_strategy: Dict[str, Any] = Field(
        ...,
        description="Content strategy insights and patterns"
    )
    
    # Token tracking
    context_tokens_used: int = Field(
        ...,
        description="Total tokens at time of archive creation"
    )
    phases_included: List[CIAPhase] = Field(
        ...,
        description="All phases synthesized in this archive"
    )


class MasterArchive(BaseCIAModel, MasterArchiveBase, MetadataMixin):
    """Complete master archive model with all fields."""
    
    # Quality metrics
    framework_integrity_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Integrity scores for each preserved framework (0-1)"
    )
    synthesis_quality_score: float = Field(
        default=0.0,
        description="Overall synthesis quality score (0-1)"
    )
    
    # Intelligence metrics
    insights_count: int = Field(default=0, description="Number of key insights preserved")
    opportunities_identified: int = Field(default=0, description="Strategic opportunities found")
    implementation_priorities: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Prioritized action items"
    )
    
    # Chain tracking
    previous_archive_id: Optional[UUID] = Field(
        None,
        description="ID of previous archive in chain"
    )
    archive_version: int = Field(
        default=1,
        description="Version number in archive chain"
    )
    
    # Validation
    validated_at: Optional[datetime] = Field(None)
    validation_notes: Optional[str] = Field(None)
    
    @model_validator(mode='after')
    def calculate_metrics(self) -> 'MasterArchive':
        """Calculate archive metrics from content."""
        # Count insights
        if 'accumulated_insights' in self.intelligence_summary:
            self.insights_count = len(self.intelligence_summary['accumulated_insights'])
        
        # Count opportunities
        if 'strategic_opportunities' in self.intelligence_summary:
            self.opportunities_identified = len(self.intelligence_summary['strategic_opportunities'])
        
        return self
    
    def get_framework_names(self) -> List[str]:
        """Get list of preserved framework names."""
        frameworks = []
        if self.customer_psychology:
            frameworks.append("Benson Customer Psychology")
        if self.authority_positioning:
            frameworks.append("Priestley 5 P's")
        if self.competitive_analysis:
            frameworks.append("Competitive Intelligence")
        if self.content_strategy:
            frameworks.append("Content Strategy")
        return frameworks
    
    def validate_framework_integrity(self) -> Dict[str, bool]:
        """Validate that all required frameworks are preserved."""
        validation = {
            "benson_points": self._validate_benson_points(),
            "priestley_5ps": self._validate_priestley_framework(),
            "frank_kern": self._validate_frank_kern_methodology(),
            "golden_hippo": self._validate_golden_hippo_framework(),
        }
        return validation
    
    def _validate_benson_points(self) -> bool:
        """Validate Benson points preservation."""
        if not self.customer_psychology:
            return False
        # Check for key Benson point categories
        required_categories = ["pain_points", "desires", "beliefs", "values", "behaviors"]
        return all(cat in self.customer_psychology for cat in required_categories)
    
    def _validate_priestley_framework(self) -> bool:
        """Validate Priestley 5 P's preservation."""
        if not self.authority_positioning:
            return False
        required_ps = ["pitch", "publish", "product", "profile", "partnership"]
        return all(p in self.authority_positioning for p in required_ps)
    
    def _validate_frank_kern_methodology(self) -> bool:
        """Validate Frank Kern methodology preservation."""
        if not self.customer_psychology:
            return False
        kern_elements = ["narrative_structure", "customer_journey", "transformation_story"]
        return any(elem in str(self.customer_psychology) for elem in kern_elements)
    
    def _validate_golden_hippo_framework(self) -> bool:
        """Validate Golden Hippo framework preservation."""
        if not self.content_strategy:
            return False
        hippo_elements = ["offer_structure", "value_stacking", "urgency_creation"]
        return any(elem in str(self.content_strategy) for elem in hippo_elements)
    
    class Config:
        json_encoders = {
            CIAPhase: lambda v: v.value,
        }


class MasterArchiveCreate(MasterArchiveBase):
    """Schema for creating a new master archive."""
    framework_integrity_scores: Optional[Dict[str, float]] = Field(default_factory=dict)
    previous_archive_id: Optional[UUID] = None
    archive_version: Optional[int] = Field(default=1)


class MasterArchiveUpdate(BaseModel):
    """Schema for updating a master archive."""
    synthesis_quality_score: Optional[float] = None
    validated_at: Optional[datetime] = None
    validation_notes: Optional[str] = None
    framework_integrity_scores: Optional[Dict[str, float]] = None


class MasterArchiveSummary(BaseModel):
    """Summary view of master archive for listing."""
    id: UUID
    session_id: UUID
    phase_number: CIAPhase
    archive_version: int
    phases_included: List[CIAPhase]
    context_tokens_used: int
    insights_count: int
    opportunities_identified: int
    synthesis_quality_score: float
    created_at: datetime
    
    class Config:
        json_encoders = {
            CIAPhase: lambda v: v.value,
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }