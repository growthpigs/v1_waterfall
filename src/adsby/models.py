"""
Adsby Data Models
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator


class CampaignStatus(Enum):
    """Campaign status states"""
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    FAILED = "failed"


class PerformanceMetric(Enum):
    """Performance metric types"""
    CTR = "ctr"  # Click-through rate
    CONVERSION_RATE = "conversion_rate"
    AUTHORITY_IMPACT = "authority_impact"
    COST_PER_ACQUISITION = "cpa"
    QUALITY_SCORE = "quality_score"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    SPEND = "spend"
    ROAS = "roas"  # Return on ad spend


class AdGroup(BaseModel):
    """Ad group within a campaign"""
    name: str
    keywords: List[Dict[str, Any]]  # keyword text, match type, bid
    max_cpc: float = Field(default=2.50, ge=0)
    target_cpa: Optional[float] = Field(default=50.0, ge=0)
    ads: List[Dict[str, str]] = Field(default_factory=list)
    status: str = "enabled"


class AdCampaign(BaseModel):
    """Google Ads campaign model"""
    campaign_id: str
    cluster_id: str
    client_id: str
    title: str
    budget_allocated: float = Field(ge=0)
    spend_to_date: float = Field(default=0.0, ge=0)
    daily_budget: float = Field(ge=0)
    start_date: datetime
    end_date: Optional[datetime] = None
    status: CampaignStatus
    performance_metrics: Dict[PerformanceMetric, float] = Field(default_factory=dict)
    keywords: List[str]
    negative_keywords: List[str] = Field(default_factory=list)
    ad_groups: List[AdGroup] = Field(default_factory=list)
    landing_page_url: str
    tracking_parameters: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('daily_budget')
    def validate_daily_budget(cls, v, values):
        """Ensure daily budget aligns with allocated budget"""
        if 'budget_allocated' in values:
            # Assuming 30-day month
            max_daily = values['budget_allocated'] / 30
            if v > max_daily * 1.1:  # Allow 10% flexibility
                raise ValueError(f'Daily budget ${v} exceeds allocation limit ${max_daily:.2f}')
        return v
    
    @property
    def budget_utilization(self) -> float:
        """Calculate budget utilization percentage"""
        if self.budget_allocated == 0:
            return 0.0
        return (self.spend_to_date / self.budget_allocated) * 100
    
    @property
    def days_active(self) -> int:
        """Calculate days campaign has been active"""
        if self.status != CampaignStatus.ACTIVE:
            return 0
        return (datetime.now() - self.start_date).days
    
    @property
    def is_underperforming(self) -> bool:
        """Check if campaign is underperforming"""
        ctr = self.performance_metrics.get(PerformanceMetric.CTR, 0)
        conv_rate = self.performance_metrics.get(PerformanceMetric.CONVERSION_RATE, 0)
        return ctr < 1.5 or conv_rate < 2.0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            CampaignStatus: lambda v: v.value,
            PerformanceMetric: lambda v: v.value
        }


class BudgetRotation(BaseModel):
    """Weekly budget rotation decision"""
    rotation_id: str
    week_date: str  # Format: YYYY-W##
    current_campaigns: List[str]  # Campaign IDs
    campaign_to_pause: Optional[str] = None
    campaign_to_promote: Optional[str] = None
    reasoning: str
    projected_performance: Dict[str, Any]
    rotation_date: datetime
    requires_action: bool = False
    executed_at: Optional[datetime] = None
    executed_by: Optional[str] = None
    
    @property
    def is_executed(self) -> bool:
        """Check if rotation has been executed"""
        return self.executed_at is not None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CampaignPerformance(BaseModel):
    """Detailed campaign performance data"""
    campaign_id: str
    date_range: Dict[str, datetime]
    metrics: Dict[PerformanceMetric, float]
    daily_breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    keyword_performance: List[Dict[str, Any]] = Field(default_factory=list)
    ad_performance: List[Dict[str, Any]] = Field(default_factory=list)
    authority_metrics: Dict[str, float] = Field(default_factory=dict)
    measured_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def composite_score(self) -> float:
        """Calculate composite performance score"""
        weights = {
            PerformanceMetric.CTR: 0.25,
            PerformanceMetric.CONVERSION_RATE: 0.30,
            PerformanceMetric.AUTHORITY_IMPACT: 0.25,
            PerformanceMetric.COST_PER_ACQUISITION: 0.20
        }
        
        score = 0.0
        for metric, weight in weights.items():
            value = self.metrics.get(metric, 0)
            
            # Normalize CPA (lower is better)
            if metric == PerformanceMetric.COST_PER_ACQUISITION:
                value = max(0, 100 - value)
            
            score += value * weight
        
        return min(score, 100.0)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            PerformanceMetric: lambda v: v.value
        }


@dataclass
class AuthorityImpactMetrics:
    """Metrics for measuring authority building impact"""
    branded_search_increase: float = 0.0  # Percentage increase
    direct_traffic_increase: float = 0.0
    return_visitor_rate: float = 0.0
    content_engagement_score: float = 0.0  # Based on time on site, pages viewed
    social_amplification: float = 0.0  # Shares, mentions
    backlink_acquisition: int = 0  # New backlinks generated
    
    @property
    def overall_impact_score(self) -> float:
        """Calculate overall authority impact (0-100)"""
        score = (
            self.branded_search_increase * 0.3 +
            self.direct_traffic_increase * 0.2 +
            self.return_visitor_rate * 0.2 +
            self.content_engagement_score * 0.2 +
            self.social_amplification * 0.1
        )
        
        # Bonus for backlinks
        if self.backlink_acquisition > 0:
            score += min(self.backlink_acquisition * 2, 10)
        
        return min(score, 100.0)


class OptimizationRecommendation(BaseModel):
    """Campaign optimization recommendation"""
    campaign_id: str
    recommendation_type: str  # "pause", "increase_budget", "modify_keywords", etc.
    priority: str  # "high", "medium", "low"
    reason: str
    expected_impact: Dict[str, Any]
    specific_actions: List[str]
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }