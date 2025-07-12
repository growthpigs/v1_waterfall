"""
Content Cluster Attribution System for Brand BOS
Tracks pillar article → supporting content → social promotion performance across platforms
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

from ..database.cartwheel_models import ContentCluster, ContentPiece, ContentFormat
from ..integrations.google_analytics import GoogleAnalyticsClient, ContentPerformance
from ..integrations.google_search_console import GoogleSearchConsoleClient, ContentSearchPerformance
from ..integrations.utm_automation import UTMAnalyzer

logger = logging.getLogger(__name__)


class ContentStage(Enum):
    """Content stages in the cluster attribution flow"""
    PILLAR = "pillar"           # Epic pillar article / AI search blog
    SUPPORTING = "supporting"   # Supporting blog content
    SOCIAL = "social"           # Social promotion content
    AMPLIFICATION = "amplification"  # Paid/email amplification


@dataclass
class AttributionMetrics:
    """Metrics for content attribution analysis"""
    sessions: int = 0
    users: int = 0
    page_views: int = 0
    time_on_page: float = 0.0
    bounce_rate: float = 0.0
    conversions: int = 0
    conversion_value: float = 0.0
    social_shares: int = 0
    backlinks: int = 0
    
    # Search metrics
    search_clicks: int = 0
    search_impressions: int = 0
    search_ctr: float = 0.0
    avg_search_position: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @property
    def engagement_score(self) -> float:
        """Calculate engagement score (0-100)"""
        if self.sessions == 0:
            return 0.0
        
        # Time on page score (normalized to 0-25)
        time_score = min(self.time_on_page / 180, 1) * 25  # 3 minutes = max score
        
        # Bounce rate score (inverse, 0-25)
        bounce_score = (1 - min(self.bounce_rate, 1)) * 25
        
        # Pages per session score (0-25)
        pages_per_session = self.page_views / self.sessions
        pages_score = min(pages_per_session / 3, 1) * 25  # 3 pages = max score
        
        # Conversion score (0-25)
        conversion_rate = self.conversions / self.sessions
        conversion_score = min(conversion_rate * 100, 1) * 25
        
        return time_score + bounce_score + pages_score + conversion_score


@dataclass
class ContentAttribution:
    """Attribution data for a single content piece"""
    content_id: str
    content_title: str
    content_format: ContentFormat
    content_stage: ContentStage
    url: str
    cluster_id: str
    
    # Performance metrics
    metrics: AttributionMetrics
    
    # Attribution data
    referral_sources: List[Tuple[str, int]]  # (source, sessions)
    utm_breakdown: Dict[str, AttributionMetrics]  # source -> metrics
    
    # Timing
    publish_date: datetime
    analysis_date: datetime
    days_since_publish: int
    
    @property
    def performance_score(self) -> float:
        """Calculate overall performance score"""
        base_score = self.metrics.engagement_score
        
        # Bonus for search performance
        if self.metrics.search_impressions > 0:
            search_bonus = min(self.metrics.search_ctr * 10, 10)  # Max 10 points
            base_score += search_bonus
        
        # Bonus for social amplification
        if self.metrics.social_shares > 0:
            social_bonus = min(self.metrics.social_shares / 10, 5)  # Max 5 points
            base_score += social_bonus
        
        return min(base_score, 100)


@dataclass
class ClusterAttribution:
    """Attribution analysis for an entire content cluster"""
    cluster_id: str
    cluster_topic: str
    cluster_keywords: List[str]
    
    # Content pieces by stage
    pillar_content: List[ContentAttribution]
    supporting_content: List[ContentAttribution]
    social_content: List[ContentAttribution]
    amplification_content: List[ContentAttribution]
    
    # Aggregate metrics
    total_metrics: AttributionMetrics
    stage_metrics: Dict[ContentStage, AttributionMetrics]
    
    # Attribution flow analysis
    funnel_conversion: Dict[str, float]  # stage -> conversion rate to next stage
    cross_content_referrals: List[Tuple[str, str, int]]  # (from_content, to_content, sessions)
    
    # Performance insights
    best_performing_content: ContentAttribution
    improvement_opportunities: List[Dict[str, Any]]
    
    # Timing
    cluster_start_date: datetime
    analysis_period: Tuple[datetime, datetime]
    
    @property
    def cluster_authority_score(self) -> float:
        """Calculate overall cluster authority impact"""
        if not self.pillar_content:
            return 0.0
        
        # Start with pillar content performance
        pillar_score = sum(content.performance_score for content in self.pillar_content) / len(self.pillar_content)
        
        # Add supporting content amplification
        if self.supporting_content:
            supporting_score = sum(content.performance_score for content in self.supporting_content) / len(self.supporting_content)
            pillar_score += supporting_score * 0.3
        
        # Add social amplification
        if self.social_content:
            social_score = sum(content.performance_score for content in self.social_content) / len(self.social_content)
            pillar_score += social_score * 0.2
        
        # Add search authority (backlinks, rankings)
        total_backlinks = sum(content.metrics.backlinks for content in self.pillar_content + self.supporting_content)
        backlink_bonus = min(total_backlinks, 20)  # Max 20 points
        
        return min(pillar_score + backlink_bonus, 100)


class ContentAttributionEngine:
    """Engine for analyzing content cluster attribution and performance"""
    
    def __init__(
        self,
        ga_client: GoogleAnalyticsClient,
        gsc_client: GoogleSearchConsoleClient,
        utm_analyzer: UTMAnalyzer
    ):
        """
        Initialize attribution engine
        
        Args:
            ga_client: Google Analytics client
            gsc_client: Google Search Console client  
            utm_analyzer: UTM analysis engine
        """
        self.ga_client = ga_client
        self.gsc_client = gsc_client
        self.utm_analyzer = utm_analyzer
    
    async def analyze_content_attribution(
        self,
        content_piece: ContentPiece,
        client_id: str,
        start_date: str,
        end_date: str,
        ga_property_id: Optional[str] = None,
        gsc_site_url: Optional[str] = None
    ) -> ContentAttribution:
        """
        Analyze attribution for a single content piece
        
        Args:
            content_piece: Content piece to analyze
            client_id: Client identifier
            start_date: Analysis start date
            end_date: Analysis end date
            ga_property_id: GA4 property ID
            gsc_site_url: Search Console site URL
            
        Returns:
            Content attribution analysis
        """
        try:
            # Get content URL (would come from content piece in real implementation)
            content_url = f"/content/{content_piece.id}"
            
            # Get GA4 performance data
            ga_performance = await self.ga_client.get_content_performance(
                client_id=client_id,
                page_path=content_url,
                property_id=ga_property_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Get Search Console data
            search_performance = await self.gsc_client.get_content_search_performance(
                client_id=client_id,
                page_url=content_url,
                site_url=gsc_site_url,
                start_date=start_date,
                end_date=end_date
            )
            
            # Combine metrics
            combined_metrics = self._combine_metrics(ga_performance, search_performance)
            
            # Analyze UTM breakdown
            utm_breakdown = self._analyze_utm_breakdown(ga_performance.utm_breakdown)
            
            # Determine content stage
            content_stage = self._determine_content_stage(content_piece.format)
            
            # Calculate days since publish
            publish_date = getattr(content_piece, 'created_at', datetime.now())
            days_since_publish = (datetime.now() - publish_date).days
            
            return ContentAttribution(
                content_id=content_piece.id,
                content_title=content_piece.title,
                content_format=content_piece.format,
                content_stage=content_stage,
                url=content_url,
                cluster_id=content_piece.cluster_id,
                metrics=combined_metrics,
                referral_sources=ga_performance.top_sources,
                utm_breakdown=utm_breakdown,
                publish_date=publish_date,
                analysis_date=datetime.now(),
                days_since_publish=days_since_publish
            )
            
        except Exception as e:
            logger.error(f"Content attribution analysis failed for {content_piece.id}: {e}")
            raise
    
    async def analyze_cluster_attribution(
        self,
        content_cluster: ContentCluster,
        content_pieces: List[ContentPiece],
        client_id: str,
        start_date: str,
        end_date: str,
        ga_property_id: Optional[str] = None,
        gsc_site_url: Optional[str] = None
    ) -> ClusterAttribution:
        """
        Analyze attribution for an entire content cluster
        
        Args:
            content_cluster: Content cluster to analyze
            content_pieces: List of content pieces in cluster
            client_id: Client identifier
            start_date: Analysis start date
            end_date: Analysis end date
            ga_property_id: GA4 property ID
            gsc_site_url: Search Console site URL
            
        Returns:
            Cluster attribution analysis
        """
        try:
            # Analyze each content piece
            content_attributions = []
            for content_piece in content_pieces:
                attribution = await self.analyze_content_attribution(
                    content_piece=content_piece,
                    client_id=client_id,
                    start_date=start_date,
                    end_date=end_date,
                    ga_property_id=ga_property_id,
                    gsc_site_url=gsc_site_url
                )
                content_attributions.append(attribution)
            
            # Group by content stage
            stage_groups = self._group_by_stage(content_attributions)
            
            # Calculate aggregate metrics
            total_metrics = self._aggregate_metrics(content_attributions)
            stage_metrics = {
                stage: self._aggregate_metrics(attributions)
                for stage, attributions in stage_groups.items()
            }
            
            # Analyze funnel conversion (simplified for now)
            funnel_conversion = self._analyze_funnel_conversion(stage_groups)
            
            # Find cross-content referrals (placeholder implementation)
            cross_referrals = self._analyze_cross_referrals(content_attributions)
            
            # Identify best performing content
            best_content = max(content_attributions, key=lambda x: x.performance_score) if content_attributions else None
            
            # Generate improvement opportunities
            opportunities = self._identify_opportunities(content_attributions, stage_groups)
            
            return ClusterAttribution(
                cluster_id=content_cluster.id,
                cluster_topic=content_cluster.cluster_topic,
                cluster_keywords=getattr(content_cluster, 'seo_keywords', []),
                pillar_content=stage_groups.get(ContentStage.PILLAR, []),
                supporting_content=stage_groups.get(ContentStage.SUPPORTING, []),
                social_content=stage_groups.get(ContentStage.SOCIAL, []),
                amplification_content=stage_groups.get(ContentStage.AMPLIFICATION, []),
                total_metrics=total_metrics,
                stage_metrics=stage_metrics,
                funnel_conversion=funnel_conversion,
                cross_content_referrals=cross_referrals,
                best_performing_content=best_content,
                improvement_opportunities=opportunities,
                cluster_start_date=getattr(content_cluster, 'created_at', datetime.now()),
                analysis_period=(
                    datetime.strptime(start_date, "%Y-%m-%d"),
                    datetime.strptime(end_date, "%Y-%m-%d")
                )
            )
            
        except Exception as e:
            logger.error(f"Cluster attribution analysis failed for {content_cluster.id}: {e}")
            raise
    
    def _combine_metrics(
        self,
        ga_performance: ContentPerformance,
        search_performance: ContentSearchPerformance
    ) -> AttributionMetrics:
        """Combine GA4 and Search Console metrics"""
        
        return AttributionMetrics(
            sessions=ga_performance.total_metrics.sessions,
            users=ga_performance.total_metrics.users,
            page_views=ga_performance.total_metrics.page_views,
            time_on_page=ga_performance.total_metrics.avg_session_duration,
            bounce_rate=ga_performance.total_metrics.bounce_rate,
            conversions=ga_performance.total_metrics.conversions,
            conversion_value=ga_performance.total_metrics.revenue,
            search_clicks=search_performance.total_metrics.clicks,
            search_impressions=search_performance.total_metrics.impressions,
            search_ctr=search_performance.total_metrics.ctr,
            avg_search_position=search_performance.total_metrics.position,
            social_shares=0,  # Would come from social APIs
            backlinks=0       # Would come from backlink APIs
        )
    
    def _analyze_utm_breakdown(self, utm_data) -> Dict[str, AttributionMetrics]:
        """Analyze UTM traffic breakdown"""
        utm_breakdown = {}
        
        for utm_perf in utm_data:
            source = utm_perf.utm_source
            
            if source not in utm_breakdown:
                utm_breakdown[source] = AttributionMetrics()
            
            # Aggregate metrics by source
            utm_breakdown[source].sessions += utm_perf.metrics.sessions
            utm_breakdown[source].users += utm_perf.metrics.users
            utm_breakdown[source].conversions += utm_perf.metrics.conversions
        
        return utm_breakdown
    
    def _determine_content_stage(self, content_format: ContentFormat) -> ContentStage:
        """Determine content stage based on format"""
        pillar_formats = [
            ContentFormat.EPIC_PILLAR_ARTICLE,
            ContentFormat.AI_SEARCH_BLOG,
            ContentFormat.PILLAR_PODCAST
        ]
        
        supporting_formats = [
            ContentFormat.BLOG_SUPPORTING_1,
            ContentFormat.BLOG_SUPPORTING_2,
            ContentFormat.BLOG_SUPPORTING_3,
            ContentFormat.ADVERTORIAL
        ]
        
        social_formats = [
            ContentFormat.LINKEDIN_ARTICLE,
            ContentFormat.X_THREAD,
            ContentFormat.INSTAGRAM_POST,
            ContentFormat.META_FACEBOOK_POST,
            ContentFormat.YOUTUBE_SHORTS,
            ContentFormat.TIKTOK_UGC,
            ContentFormat.TIKTOK_SHORTS
        ]
        
        if content_format in pillar_formats:
            return ContentStage.PILLAR
        elif content_format in supporting_formats:
            return ContentStage.SUPPORTING
        elif content_format in social_formats:
            return ContentStage.SOCIAL
        else:
            return ContentStage.AMPLIFICATION
    
    def _group_by_stage(self, attributions: List[ContentAttribution]) -> Dict[ContentStage, List[ContentAttribution]]:
        """Group content attributions by stage"""
        stage_groups = {}
        
        for attribution in attributions:
            stage = attribution.content_stage
            if stage not in stage_groups:
                stage_groups[stage] = []
            stage_groups[stage].append(attribution)
        
        return stage_groups
    
    def _aggregate_metrics(self, attributions: List[ContentAttribution]) -> AttributionMetrics:
        """Aggregate metrics across multiple content pieces"""
        if not attributions:
            return AttributionMetrics()
        
        total = AttributionMetrics()
        
        for attribution in attributions:
            metrics = attribution.metrics
            total.sessions += metrics.sessions
            total.users += metrics.users
            total.page_views += metrics.page_views
            total.conversions += metrics.conversions
            total.conversion_value += metrics.conversion_value
            total.search_clicks += metrics.search_clicks
            total.search_impressions += metrics.search_impressions
            total.social_shares += metrics.social_shares
            total.backlinks += metrics.backlinks
        
        # Calculate averages for rate-based metrics
        count = len(attributions)
        total.time_on_page = sum(a.metrics.time_on_page for a in attributions) / count
        total.bounce_rate = sum(a.metrics.bounce_rate for a in attributions) / count
        total.search_ctr = sum(a.metrics.search_ctr for a in attributions) / count
        total.avg_search_position = sum(a.metrics.avg_search_position for a in attributions) / count
        
        return total
    
    def _analyze_funnel_conversion(self, stage_groups: Dict[ContentStage, List[ContentAttribution]]) -> Dict[str, float]:
        """Analyze conversion rates between content stages"""
        funnel = {}
        
        # Simplified funnel analysis
        pillar_sessions = sum(a.metrics.sessions for a in stage_groups.get(ContentStage.PILLAR, []))
        supporting_sessions = sum(a.metrics.sessions for a in stage_groups.get(ContentStage.SUPPORTING, []))
        social_sessions = sum(a.metrics.sessions for a in stage_groups.get(ContentStage.SOCIAL, []))
        
        if pillar_sessions > 0:
            funnel["pillar_to_supporting"] = (supporting_sessions / pillar_sessions) * 100
            funnel["pillar_to_social"] = (social_sessions / pillar_sessions) * 100
        
        if supporting_sessions > 0:
            funnel["supporting_to_social"] = (social_sessions / supporting_sessions) * 100
        
        return funnel
    
    def _analyze_cross_referrals(self, attributions: List[ContentAttribution]) -> List[Tuple[str, str, int]]:
        """Analyze cross-content referrals (placeholder)"""
        # This would analyze referral traffic between content pieces
        # For now, return empty list as placeholder
        return []
    
    def _identify_opportunities(
        self,
        attributions: List[ContentAttribution],
        stage_groups: Dict[ContentStage, List[ContentAttribution]]
    ) -> List[Dict[str, Any]]:
        """Identify content optimization opportunities"""
        opportunities = []
        
        # Low engagement content
        for attribution in attributions:
            if attribution.metrics.engagement_score < 30:
                opportunities.append({
                    "type": "low_engagement",
                    "content_id": attribution.content_id,
                    "content_title": attribution.content_title,
                    "current_score": attribution.metrics.engagement_score,
                    "recommendation": "Improve content structure, add more engaging elements",
                    "priority": "high" if attribution.content_stage == ContentStage.PILLAR else "medium"
                })
        
        # Poor search performance
        for attribution in attributions:
            if attribution.metrics.search_impressions > 100 and attribution.metrics.search_ctr < 2.0:
                opportunities.append({
                    "type": "low_search_ctr",
                    "content_id": attribution.content_id,
                    "content_title": attribution.content_title,
                    "current_ctr": attribution.metrics.search_ctr,
                    "recommendation": "Optimize title and meta description for higher CTR",
                    "priority": "medium"
                })
        
        # Missing social amplification
        pillar_content = stage_groups.get(ContentStage.PILLAR, [])
        social_content = stage_groups.get(ContentStage.SOCIAL, [])
        
        if len(pillar_content) > len(social_content):
            opportunities.append({
                "type": "missing_social_amplification",
                "recommendation": f"Create {len(pillar_content) - len(social_content)} more social content pieces",
                "priority": "high"
            })
        
        return opportunities


# Utility functions for content attribution
async def analyze_content_cluster_performance(
    cluster_id: str,
    client_id: str,
    attribution_engine: ContentAttributionEngine,
    days: int = 30
) -> Dict[str, Any]:
    """Analyze performance for a content cluster"""
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # In real implementation, would fetch from database
    # For now, return mock analysis structure
    
    return {
        "cluster_id": cluster_id,
        "analysis_period": {"start": start_date, "end": end_date},
        "performance_summary": {
            "total_sessions": 0,
            "total_conversions": 0,
            "authority_score": 0.0,
            "content_pieces": 0
        },
        "stage_breakdown": {
            "pillar": {"sessions": 0, "conversions": 0},
            "supporting": {"sessions": 0, "conversions": 0},
            "social": {"sessions": 0, "conversions": 0}
        },
        "opportunities": [],
        "timestamp": datetime.now().isoformat()
    }


def calculate_cluster_roi(cluster_attribution: ClusterAttribution, content_cost: float = 1000.0) -> Dict[str, float]:
    """Calculate ROI for content cluster"""
    
    total_value = cluster_attribution.total_metrics.conversion_value
    total_sessions = cluster_attribution.total_metrics.sessions
    
    # Estimate content value based on sessions and authority
    estimated_value = (total_sessions * 2.5) + (cluster_attribution.cluster_authority_score * 10)
    
    roi = ((estimated_value - content_cost) / content_cost) * 100 if content_cost > 0 else 0
    
    return {
        "content_cost": content_cost,
        "estimated_value": estimated_value,
        "conversion_value": total_value,
        "total_value": estimated_value + total_value,
        "roi_percentage": roi,
        "authority_contribution": cluster_attribution.cluster_authority_score * 10
    }