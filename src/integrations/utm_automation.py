"""
UTM Automation System for Brand BOS
Implements A-[variation]_BBOS_[task]_[version] naming convention for cross-platform attribution
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from urllib.parse import urlencode, urlparse, parse_qs
import hashlib

from ..database.cartwheel_models import ContentFormat, ContentPiece
from ..database.models import CIASession

logger = logging.getLogger(__name__)


class UTMSource(Enum):
    """UTM Source values for different platforms"""
    ORGANIC_SOCIAL = "organic_social"
    PAID_SOCIAL = "paid_social" 
    EMAIL = "email"
    DIRECT = "direct"
    GOOGLE_ADS = "google_ads"
    FACEBOOK_ADS = "facebook_ads"
    LINKEDIN_ADS = "linkedin_ads"
    YOUTUBE = "youtube"
    PODCAST = "podcast"
    REFERRAL = "referral"
    NEWSLETTER = "newsletter"


class UTMMedium(Enum):
    """UTM Medium values for traffic categorization"""
    SOCIAL = "social"
    CPC = "cpc"
    EMAIL = "email"
    ORGANIC = "organic"
    REFERRAL = "referral"
    VIDEO = "video"
    PODCAST = "audio"
    DIRECT = "direct"
    DISPLAY = "display"


class BBOSTask(Enum):
    """Brand BOS task types for campaign naming"""
    PILLAR_ARTICLE = "pillar_article"
    SUPPORTING_CONTENT = "supporting_content"
    SOCIAL_PROMOTION = "social_promotion"
    EMAIL_NURTURE = "email_nurture"
    PAID_AMPLIFICATION = "paid_amplification"
    CONVERGENCE_CAPTURE = "convergence_capture"
    AUTHORITY_BUILDING = "authority_building"
    LEAD_GENERATION = "lead_generation"


@dataclass
class UTMParameters:
    """UTM parameter container"""
    source: str
    medium: str
    campaign: str
    term: Optional[str] = None
    content: Optional[str] = None
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for URL encoding"""
        params = {
            'utm_source': self.source,
            'utm_medium': self.medium,
            'utm_campaign': self.campaign
        }
        
        if self.term:
            params['utm_term'] = self.term
        if self.content:
            params['utm_content'] = self.content
            
        return params
    
    def to_url_params(self) -> str:
        """Convert to URL query string"""
        return urlencode(self.to_dict())


@dataclass
class BBOSCampaignName:
    """Brand BOS campaign naming structure: A-[variation]_BBOS_[task]_[version]"""
    variation: str  # A, B, C, etc. for testing
    task: BBOSTask
    version: str    # v1, v2, etc.
    
    @property
    def campaign_name(self) -> str:
        """Generate full campaign name"""
        return f"A-{self.variation}_BBOS_{self.task.value}_{self.version}"
    
    @classmethod
    def from_string(cls, campaign_name: str) -> Optional['BBOSCampaignName']:
        """Parse campaign name string back to components"""
        pattern = r"A-([A-Z]+)_BBOS_([a-z_]+)_([v\d]+)"
        match = re.match(pattern, campaign_name)
        
        if not match:
            return None
        
        variation, task_str, version = match.groups()
        
        try:
            task = BBOSTask(task_str)
            return cls(variation=variation, task=task, version=version)
        except ValueError:
            return None


class UTMGenerator:
    """Generates UTM parameters for Brand BOS content and campaigns"""
    
    def __init__(self, base_domain: str = "brandsos.com"):
        """
        Initialize UTM generator
        
        Args:
            base_domain: Base domain for campaign attribution
        """
        self.base_domain = base_domain
        
    def generate_content_utm(
        self,
        content_piece: ContentPiece,
        source: UTMSource,
        medium: UTMMedium,
        variation: str = "A",
        version: str = "v1",
        custom_term: Optional[str] = None
    ) -> UTMParameters:
        """
        Generate UTM parameters for content piece
        
        Args:
            content_piece: Content piece from Cartwheel
            source: Traffic source
            medium: Traffic medium
            variation: A/B test variation (A, B, C, etc.)
            version: Version number (v1, v2, etc.)
            custom_term: Custom term override
            
        Returns:
            UTM parameters for tracking
        """
        # Determine task based on content format
        task = self._get_task_from_format(content_piece.format)
        
        # Generate campaign name
        campaign_name = BBOSCampaignName(
            variation=variation,
            task=task,
            version=version
        )
        
        # Generate content identifier
        content_id = self._generate_content_id(content_piece)
        
        return UTMParameters(
            source=source.value,
            medium=medium.value,
            campaign=campaign_name.campaign_name,
            term=custom_term or self._generate_term(content_piece),
            content=content_id
        )
    
    def generate_campaign_utm(
        self,
        campaign_name: str,
        source: UTMSource,
        medium: UTMMedium,
        ad_group: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> UTMParameters:
        """
        Generate UTM parameters for paid campaigns
        
        Args:
            campaign_name: Campaign name (should follow BBOS convention)
            source: Traffic source
            medium: Traffic medium  
            ad_group: Ad group name for paid campaigns
            keyword: Target keyword
            
        Returns:
            UTM parameters for campaign tracking
        """
        return UTMParameters(
            source=source.value,
            medium=medium.value,
            campaign=campaign_name,
            term=keyword,
            content=ad_group
        )
    
    def generate_cross_platform_utm(
        self,
        base_campaign: str,
        platforms: List[Tuple[UTMSource, UTMMedium]],
        variation: str = "A"
    ) -> Dict[str, UTMParameters]:
        """
        Generate UTM parameters for cross-platform campaigns
        
        Args:
            base_campaign: Base campaign name
            platforms: List of (source, medium) tuples
            variation: A/B test variation
            
        Returns:
            Dictionary mapping platform names to UTM parameters
        """
        utm_set = {}
        
        for source, medium in platforms:
            platform_key = f"{source.value}_{medium.value}"
            
            utm_set[platform_key] = UTMParameters(
                source=source.value,
                medium=medium.value,
                campaign=f"{base_campaign}_{variation}",
                content=platform_key
            )
        
        return utm_set
    
    def add_utm_to_url(self, base_url: str, utm_params: UTMParameters) -> str:
        """
        Add UTM parameters to URL
        
        Args:
            base_url: Base URL to add parameters to
            utm_params: UTM parameters to add
            
        Returns:
            URL with UTM parameters
        """
        # Parse existing URL
        parsed = urlparse(base_url)
        existing_params = parse_qs(parsed.query)
        
        # Add UTM parameters
        utm_dict = utm_params.to_dict()
        for key, value in utm_dict.items():
            existing_params[key] = [value]
        
        # Rebuild URL
        query_string = urlencode(existing_params, doseq=True)
        
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query_string}"
    
    def generate_social_utm_set(
        self,
        content_piece: ContentPiece,
        variation: str = "A"
    ) -> Dict[str, str]:
        """
        Generate complete UTM set for social promotion
        
        Args:
            content_piece: Content to promote
            variation: A/B test variation
            
        Returns:
            Dictionary of platform -> UTM-enabled URLs
        """
        base_url = getattr(content_piece, 'canonical_url', f"https://{self.base_domain}/content/{content_piece.id}")
        
        social_platforms = [
            ("linkedin", UTMSource.ORGANIC_SOCIAL, UTMMedium.SOCIAL),
            ("twitter", UTMSource.ORGANIC_SOCIAL, UTMMedium.SOCIAL),
            ("facebook", UTMSource.ORGANIC_SOCIAL, UTMMedium.SOCIAL),
            ("instagram", UTMSource.ORGANIC_SOCIAL, UTMMedium.SOCIAL),
            ("youtube", UTMSource.YOUTUBE, UTMMedium.VIDEO),
        ]
        
        utm_urls = {}
        
        for platform, source, medium in social_platforms:
            utm_params = self.generate_content_utm(
                content_piece=content_piece,
                source=source,
                medium=medium,
                variation=variation
            )
            
            utm_urls[platform] = self.add_utm_to_url(base_url, utm_params)
        
        return utm_urls
    
    def _get_task_from_format(self, content_format: ContentFormat) -> BBOSTask:
        """Map content format to BBOS task"""
        format_task_map = {
            ContentFormat.EPIC_PILLAR_ARTICLE: BBOSTask.PILLAR_ARTICLE,
            ContentFormat.AI_SEARCH_BLOG: BBOSTask.PILLAR_ARTICLE,
            ContentFormat.BLOG_SUPPORTING_1: BBOSTask.SUPPORTING_CONTENT,
            ContentFormat.BLOG_SUPPORTING_2: BBOSTask.SUPPORTING_CONTENT,
            ContentFormat.BLOG_SUPPORTING_3: BBOSTask.SUPPORTING_CONTENT,
            ContentFormat.LINKEDIN_ARTICLE: BBOSTask.SOCIAL_PROMOTION,
            ContentFormat.X_THREAD: BBOSTask.SOCIAL_PROMOTION,
            ContentFormat.INSTAGRAM_POST: BBOSTask.SOCIAL_PROMOTION,
            ContentFormat.META_FACEBOOK_POST: BBOSTask.SOCIAL_PROMOTION,
            ContentFormat.YOUTUBE_SHORTS: BBOSTask.SOCIAL_PROMOTION,
            ContentFormat.TIKTOK_UGC: BBOSTask.SOCIAL_PROMOTION,
            ContentFormat.TIKTOK_SHORTS: BBOSTask.SOCIAL_PROMOTION,
            ContentFormat.PILLAR_PODCAST: BBOSTask.AUTHORITY_BUILDING,
            ContentFormat.ADVERTORIAL: BBOSTask.PAID_AMPLIFICATION,
        }
        
        return format_task_map.get(content_format, BBOSTask.SUPPORTING_CONTENT)
    
    def _generate_content_id(self, content_piece: ContentPiece) -> str:
        """Generate short content identifier for UTM content parameter"""
        # Create hash from content piece ID and title
        content_string = f"{content_piece.id}_{content_piece.title}"
        content_hash = hashlib.md5(content_string.encode()).hexdigest()[:8]
        
        # Format: format_hash
        format_short = content_piece.format.value.split('_')[0][:4]  # First 4 chars
        return f"{format_short}_{content_hash}"
    
    def _generate_term(self, content_piece: ContentPiece) -> str:
        """Generate UTM term from content keywords"""
        if hasattr(content_piece, 'seo_keywords') and content_piece.seo_keywords:
            # Use first keyword as term
            return content_piece.seo_keywords[0].replace(' ', '_').lower()
        
        # Fallback to content format
        return content_piece.format.value


class UTMAnalyzer:
    """Analyzes UTM performance data for Brand BOS attribution"""
    
    def __init__(self):
        self.campaign_pattern = re.compile(r"A-([A-Z]+)_BBOS_([a-z_]+)_([v\d]+)")
    
    def parse_campaign_name(self, campaign_name: str) -> Optional[Dict[str, str]]:
        """Parse Brand BOS campaign name into components"""
        match = self.campaign_pattern.match(campaign_name)
        
        if not match:
            return None
        
        variation, task, version = match.groups()
        
        return {
            "variation": variation,
            "task": task,
            "version": version,
            "full_name": campaign_name
        }
    
    def analyze_performance_by_variation(
        self,
        utm_data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze performance by A/B test variation
        
        Args:
            utm_data: List of UTM performance records
            
        Returns:
            Performance data grouped by variation
        """
        variation_performance = {}
        
        for record in utm_data:
            campaign_name = record.get('utm_campaign', '')
            parsed = self.parse_campaign_name(campaign_name)
            
            if not parsed:
                continue
            
            variation = parsed['variation']
            
            if variation not in variation_performance:
                variation_performance[variation] = {
                    'sessions': 0,
                    'conversions': 0,
                    'revenue': 0.0,
                    'campaigns': set(),
                    'tasks': set()
                }
            
            # Aggregate metrics
            variation_performance[variation]['sessions'] += record.get('sessions', 0)
            variation_performance[variation]['conversions'] += record.get('conversions', 0)
            variation_performance[variation]['revenue'] += record.get('revenue', 0.0)
            variation_performance[variation]['campaigns'].add(campaign_name)
            variation_performance[variation]['tasks'].add(parsed['task'])
        
        # Convert sets to lists for JSON serialization
        for variation in variation_performance:
            variation_performance[variation]['campaigns'] = list(variation_performance[variation]['campaigns'])
            variation_performance[variation]['tasks'] = list(variation_performance[variation]['tasks'])
        
        return variation_performance
    
    def get_best_performing_variation(
        self,
        utm_data: List[Dict[str, Any]],
        metric: str = 'conversions'
    ) -> Optional[str]:
        """
        Identify best performing variation based on metric
        
        Args:
            utm_data: UTM performance data
            metric: Metric to optimize for (sessions, conversions, revenue)
            
        Returns:
            Best performing variation identifier
        """
        performance = self.analyze_performance_by_variation(utm_data)
        
        if not performance:
            return None
        
        best_variation = max(
            performance.keys(),
            key=lambda v: performance[v].get(metric, 0)
        )
        
        return best_variation


# Utility functions for common UTM operations
def create_social_promotion_urls(
    content_piece: ContentPiece,
    base_url: str,
    variation: str = "A"
) -> Dict[str, str]:
    """Create UTM-tracked URLs for social promotion"""
    generator = UTMGenerator()
    return generator.generate_social_utm_set(content_piece, variation)


def validate_bbos_campaign_name(campaign_name: str) -> bool:
    """Validate if campaign name follows BBOS convention"""
    pattern = r"A-[A-Z]+_BBOS_[a-z_]+_v\d+"
    return bool(re.match(pattern, campaign_name))


def extract_variation_from_campaign(campaign_name: str) -> Optional[str]:
    """Extract A/B test variation from campaign name"""
    parsed = BBOSCampaignName.from_string(campaign_name)
    return parsed.variation if parsed else None