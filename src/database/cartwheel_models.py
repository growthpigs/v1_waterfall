"""
Cartwheel Content Engine Data Models
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator


class ContentFormat(Enum):
    """Supported content formats for multiplication"""
    AI_SEARCH_BLOG = "ai_search_blog"
    EPIC_PILLAR_ARTICLE = "epic_pillar_article"
    PILLAR_PODCAST = "pillar_podcast"
    ADVERTORIAL = "advertorial"
    INSTAGRAM_POST = "instagram_post"
    X_THREAD = "x_thread"
    LINKEDIN_ARTICLE = "linkedin_article"
    META_FACEBOOK_POST = "meta_facebook_post"
    TIKTOK_UGC = "tiktok_ugc"
    BLOG_SUPPORTING_1 = "blog_supporting_1"
    BLOG_SUPPORTING_2 = "blog_supporting_2"
    BLOG_SUPPORTING_3 = "blog_supporting_3"
    YOUTUBE_SHORTS = "youtube_shorts"
    TIKTOK_SHORTS = "tiktok_shorts"


class ConvergenceSource(Enum):
    """Sources for viral content detection"""
    GROK_X_TRENDING = "grok_x_trending"
    REDDIT_VIRAL = "reddit_viral"
    GOOGLE_TRENDS = "google_trends"


class PublishingStatus(Enum):
    """Content publishing status"""
    PENDING = "pending"
    APPROVED = "approved"
    NOTION_CREATED = "notion_created"
    BUILDFAST_SYNCED = "buildfast_synced"
    LIVE = "live"
    SOCIAL_POSTED = "social_posted"
    FAILED = "failed"


class ApprovalStatus(Enum):
    """Content approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


@dataclass
class ViralContent:
    """Single piece of viral content from any source"""
    source: ConvergenceSource
    content_id: str
    title: str
    engagement_score: float  # 0-100
    viral_velocity: float  # 0-1 (rate of engagement growth)
    topic_keywords: List[str]
    sentiment: str  # positive, negative, neutral
    platform_specific_data: Dict[str, Any]
    detected_at: datetime


class ConvergenceOpportunity(BaseModel):
    """Database model for convergence opportunities"""
    id: str
    client_id: str
    week_date: str  # Format: YYYY-W##
    topic: str
    convergence_score: float = Field(ge=0, le=100)
    viral_sources: List[Dict[str, Any]]
    seo_keywords: List[str]
    trend_momentum: str  # rising, peak, stable, declining
    content_opportunity: Dict[str, Any]
    recommended_formats: List[str]
    urgency_level: str  # immediate, this_week, planned
    created_at: datetime
    
    @validator('convergence_score')
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Convergence score must be between 0 and 100')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContentCluster(BaseModel):
    """Database model for content clusters"""
    id: str
    client_id: str
    convergence_id: str
    cluster_topic: str
    cia_intelligence_summary: Dict[str, Any]
    content_piece_ids: List[str] = Field(default_factory=list)
    publishing_schedule: Dict[str, Any]
    approval_status: str
    created_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContentPiece(BaseModel):
    """Database model for individual content pieces"""
    id: str
    cluster_id: str
    client_id: str
    format_type: ContentFormat
    title: str
    content_body: str
    hook: str
    call_to_action: str
    seo_keywords: List[str]
    hashtags: List[str] = Field(default_factory=list)
    images_needed: List[str] = Field(default_factory=list)
    generated_images: List[Dict[str, str]] = Field(default_factory=list)
    platform_specs: Dict[str, Any]
    approval_status: ApprovalStatus
    publishing_status: PublishingStatus
    notion_page_id: Optional[str] = None
    published_url: Optional[str] = None
    social_post_ids: Dict[str, str] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    published_at: Optional[datetime] = None
    
    @validator('seo_keywords')
    def validate_keywords(cls, v):
        # Limit to 10 keywords
        return v[:10] if v else []
    
    @validator('hashtags')
    def validate_hashtags(cls, v):
        # Ensure hashtags start with #
        return [tag if tag.startswith('#') else f'#{tag}' for tag in v]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ContentFormat: lambda v: v.value,
            ApprovalStatus: lambda v: v.value,
            PublishingStatus: lambda v: v.value
        }


class ContentApproval(BaseModel):
    """Database model for content approval workflow"""
    id: str
    content_piece_id: str
    cluster_id: str
    reviewer_id: str
    status: ApprovalStatus
    feedback: Optional[str] = None
    revision_notes: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ApprovalStatus: lambda v: v.value
        }


class PublishingJob(BaseModel):
    """Database model for publishing job tracking"""
    id: str
    content_piece_id: str
    cluster_id: str
    client_id: str
    platform: str  # notion, instagram, x, linkedin, etc.
    status: str  # queued, processing, completed, failed
    scheduled_for: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    platform_response: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContentPerformance(BaseModel):
    """Database model for content performance tracking"""
    id: str
    content_piece_id: str
    platform: str
    metric_type: str  # views, likes, shares, comments, clicks, conversions
    metric_value: float
    measured_at: datetime
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Helper functions for content format categorization
def is_blog_format(format_type: ContentFormat) -> bool:
    """Check if format is a blog type"""
    blog_formats = {
        ContentFormat.AI_SEARCH_BLOG,
        ContentFormat.EPIC_PILLAR_ARTICLE,
        ContentFormat.BLOG_SUPPORTING_1,
        ContentFormat.BLOG_SUPPORTING_2,
        ContentFormat.BLOG_SUPPORTING_3,
        ContentFormat.ADVERTORIAL
    }
    return format_type in blog_formats


def is_social_format(format_type: ContentFormat) -> bool:
    """Check if format is a social media type"""
    social_formats = {
        ContentFormat.INSTAGRAM_POST,
        ContentFormat.X_THREAD,
        ContentFormat.LINKEDIN_ARTICLE,
        ContentFormat.META_FACEBOOK_POST,
        ContentFormat.TIKTOK_UGC,
        ContentFormat.YOUTUBE_SHORTS,
        ContentFormat.TIKTOK_SHORTS
    }
    return format_type in social_formats


def is_video_format(format_type: ContentFormat) -> bool:
    """Check if format requires video content"""
    video_formats = {
        ContentFormat.YOUTUBE_SHORTS,
        ContentFormat.TIKTOK_SHORTS,
        ContentFormat.TIKTOK_UGC
    }
    return format_type in video_formats


def is_long_form_format(format_type: ContentFormat) -> bool:
    """Check if format is long-form content"""
    long_form_formats = {
        ContentFormat.EPIC_PILLAR_ARTICLE,
        ContentFormat.PILLAR_PODCAST,
        ContentFormat.LINKEDIN_ARTICLE
    }
    return format_type in long_form_formats


# Content format specifications
CONTENT_FORMAT_SPECS = {
    ContentFormat.AI_SEARCH_BLOG: {
        "word_count": (1500, 2000),
        "requires_images": True,
        "image_count": 3,
        "platform": "blog",
        "seo_optimized": True
    },
    ContentFormat.EPIC_PILLAR_ARTICLE: {
        "word_count": (3000, 5000),
        "requires_images": True,
        "image_count": 5,
        "platform": "blog",
        "seo_optimized": True
    },
    ContentFormat.INSTAGRAM_POST: {
        "character_limit": 2200,
        "requires_images": True,
        "image_count": 1,
        "platform": "instagram",
        "hashtag_limit": 30
    },
    ContentFormat.X_THREAD: {
        "character_limit": 280,  # Per tweet
        "max_tweets": 10,
        "requires_images": False,
        "platform": "x"
    },
    ContentFormat.LINKEDIN_ARTICLE: {
        "word_count": (1000, 3000),
        "requires_images": True,
        "image_count": 2,
        "platform": "linkedin"
    },
    ContentFormat.TIKTOK_UGC: {
        "duration_seconds": (15, 60),
        "requires_video": True,
        "platform": "tiktok",
        "hashtag_limit": 5
    },
    ContentFormat.YOUTUBE_SHORTS: {
        "duration_seconds": (15, 60),
        "requires_video": True,
        "platform": "youtube"
    }
}