"""
Performance Tracker
Monitors campaign performance and calculates authority impact
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from .models import (
    PerformanceMetric, CampaignPerformance,
    AuthorityImpactMetrics
)
from ..integrations.google_ads_api import GoogleAdsClient

logger = logging.getLogger(__name__)

# Performance thresholds
GOOD_CTR = 2.5
GOOD_CONVERSION_RATE = 3.0
GOOD_QUALITY_SCORE = 7.0
MAX_CPA = 75.0


class PerformanceTracker:
    """
    Tracks campaign performance metrics and calculates
    authority building impact for optimization decisions
    """
    
    def __init__(self, google_ads_client: Optional[GoogleAdsClient] = None):
        self.google_ads = google_ads_client
        self._performance_cache = {}  # Simple caching
        self._cache_ttl = 3600  # 1 hour cache
    
    async def get_campaign_metrics(
        self, campaign_id: str, use_cache: bool = True
    ) -> Dict[PerformanceMetric, float]:
        """
        Get current performance metrics for a campaign
        
        Args:
            campaign_id: Campaign to analyze
            use_cache: Whether to use cached data
            
        Returns:
            Dictionary of performance metrics
        """
        try:
            # Check cache
            if use_cache and self._is_cached(campaign_id):
                return self._get_from_cache(campaign_id)
            
            # Get performance data
            if self.google_ads:
                performance_data = await self.google_ads.get_campaign_performance(
                    campaign_id=campaign_id,
                    date_range="LAST_7_DAYS"
                )
            else:
                # Mock data for testing
                performance_data = self._get_mock_performance()
            
            # Calculate metrics
            metrics = await self._calculate_metrics(performance_data)
            
            # Calculate authority impact
            authority_impact = await self._calculate_authority_impact(
                campaign_id, performance_data
            )
            metrics[PerformanceMetric.AUTHORITY_IMPACT] = authority_impact
            
            # Cache results
            self._cache_metrics(campaign_id, metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting campaign metrics: {str(e)}")
            return {}
    
    async def get_detailed_performance(
        self,
        campaign_id: str,
        date_range: Tuple[datetime, datetime]
    ) -> CampaignPerformance:
        """
        Get detailed performance data with daily breakdown
        
        Args:
            campaign_id: Campaign to analyze
            date_range: Start and end dates
            
        Returns:
            Detailed CampaignPerformance object
        """
        try:
            # Get comprehensive data
            if self.google_ads:
                # Get daily breakdown
                daily_data = await self.google_ads.get_campaign_performance_report(
                    campaign_id=campaign_id,
                    start_date=date_range[0],
                    end_date=date_range[1],
                    segment="DAY"
                )
                
                # Get keyword performance
                keyword_data = await self.google_ads.get_keyword_performance(
                    campaign_id=campaign_id,
                    date_range=date_range
                )
                
                # Get ad performance
                ad_data = await self.google_ads.get_ad_performance(
                    campaign_id=campaign_id,
                    date_range=date_range
                )
            else:
                # Mock data
                daily_data = self._get_mock_daily_data()
                keyword_data = self._get_mock_keyword_data()
                ad_data = self._get_mock_ad_data()
            
            # Calculate aggregate metrics
            metrics = await self._calculate_metrics(daily_data)
            
            # Calculate authority metrics
            authority_metrics = await self._calculate_detailed_authority_metrics(
                campaign_id, daily_data
            )
            
            # Build performance object
            performance = CampaignPerformance(
                campaign_id=campaign_id,
                date_range={
                    "start": date_range[0],
                    "end": date_range[1]
                },
                metrics=metrics,
                daily_breakdown=daily_data,
                keyword_performance=keyword_data,
                ad_performance=ad_data,
                authority_metrics=authority_metrics
            )
            
            return performance
            
        except Exception as e:
            logger.error(f"Error getting detailed performance: {str(e)}")
            raise
    
    async def track_conversion_events(
        self,
        campaign_id: str,
        conversion_type: str,
        value: float
    ):
        """
        Track custom conversion events for authority building
        
        Args:
            campaign_id: Campaign that drove the conversion
            conversion_type: Type of conversion
            value: Conversion value
        """
        try:
            # In production, this would send to analytics
            logger.info(
                f"Conversion tracked - Campaign: {campaign_id}, "
                f"Type: {conversion_type}, Value: ${value}"
            )
            
            # Update authority impact calculations
            if conversion_type in ["newsletter_signup", "content_download", "webinar_registration"]:
                # These indicate authority building
                await self._update_authority_score(campaign_id, 5.0)
            
        except Exception as e:
            logger.error(f"Error tracking conversion: {str(e)}")
    
    async def generate_performance_report(
        self,
        campaign_ids: List[str],
        date_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report for campaigns
        
        Args:
            campaign_ids: Campaigns to include
            date_range: Report period
            
        Returns:
            Performance report data
        """
        try:
            report = {
                "period": {
                    "start": date_range[0].isoformat(),
                    "end": date_range[1].isoformat()
                },
                "summary": {},
                "campaigns": [],
                "insights": [],
                "recommendations": []
            }
            
            # Aggregate metrics
            total_spend = 0
            total_conversions = 0
            total_clicks = 0
            total_impressions = 0
            
            # Get data for each campaign
            for campaign_id in campaign_ids:
                perf = await self.get_detailed_performance(campaign_id, date_range)
                
                # Add to report
                report["campaigns"].append({
                    "campaign_id": campaign_id,
                    "metrics": perf.metrics,
                    "composite_score": perf.composite_score,
                    "top_keywords": perf.keyword_performance[:5],
                    "best_ad": perf.ad_performance[0] if perf.ad_performance else None
                })
                
                # Aggregate
                total_spend += perf.metrics.get(PerformanceMetric.SPEND, 0)
                total_conversions += perf.metrics.get(PerformanceMetric.CONVERSIONS, 0)
                total_clicks += perf.metrics.get(PerformanceMetric.CLICKS, 0)
                total_impressions += perf.metrics.get(PerformanceMetric.IMPRESSIONS, 0)
            
            # Calculate summary
            report["summary"] = {
                "total_spend": total_spend,
                "total_conversions": total_conversions,
                "overall_cpa": total_spend / max(total_conversions, 1),
                "overall_ctr": (total_clicks / max(total_impressions, 1)) * 100,
                "overall_conversion_rate": (total_conversions / max(total_clicks, 1)) * 100
            }
            
            # Generate insights
            report["insights"] = await self._generate_insights(report)
            
            # Generate recommendations
            report["recommendations"] = await self._generate_recommendations(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _calculate_metrics(
        self, performance_data: Dict[str, Any]
    ) -> Dict[PerformanceMetric, float]:
        """Calculate standard performance metrics"""
        
        impressions = performance_data.get("impressions", 0)
        clicks = performance_data.get("clicks", 0)
        conversions = performance_data.get("conversions", 0)
        cost = performance_data.get("cost", 0)
        
        metrics = {
            PerformanceMetric.IMPRESSIONS: impressions,
            PerformanceMetric.CLICKS: clicks,
            PerformanceMetric.CONVERSIONS: conversions,
            PerformanceMetric.SPEND: cost
        }
        
        # Calculate rates
        if impressions > 0:
            metrics[PerformanceMetric.CTR] = (clicks / impressions) * 100
        else:
            metrics[PerformanceMetric.CTR] = 0.0
        
        if clicks > 0:
            metrics[PerformanceMetric.CONVERSION_RATE] = (conversions / clicks) * 100
        else:
            metrics[PerformanceMetric.CONVERSION_RATE] = 0.0
        
        if conversions > 0:
            metrics[PerformanceMetric.COST_PER_ACQUISITION] = cost / conversions
        else:
            metrics[PerformanceMetric.COST_PER_ACQUISITION] = 0.0
        
        # Quality score (if available)
        metrics[PerformanceMetric.QUALITY_SCORE] = performance_data.get("quality_score", 7.0)
        
        # ROAS
        revenue = performance_data.get("conversion_value", conversions * 100)  # Assume $100 per conversion
        if cost > 0:
            metrics[PerformanceMetric.ROAS] = revenue / cost
        else:
            metrics[PerformanceMetric.ROAS] = 0.0
        
        return metrics
    
    async def _calculate_authority_impact(
        self,
        campaign_id: str,
        performance_data: Dict[str, Any]
    ) -> float:
        """Calculate authority building impact score"""
        
        # Get analytics data (mock for now)
        analytics_data = await self._get_analytics_data(campaign_id)
        
        # Build authority metrics
        authority = AuthorityImpactMetrics(
            branded_search_increase=analytics_data.get("branded_search_lift", 0),
            direct_traffic_increase=analytics_data.get("direct_traffic_lift", 0),
            return_visitor_rate=analytics_data.get("return_visitor_rate", 0),
            content_engagement_score=await self._calculate_engagement_score(analytics_data),
            social_amplification=analytics_data.get("social_shares", 0) / 100,  # Normalize
            backlink_acquisition=analytics_data.get("new_backlinks", 0)
        )
        
        return authority.overall_impact_score
    
    async def _calculate_engagement_score(
        self, analytics_data: Dict[str, Any]
    ) -> float:
        """Calculate content engagement score"""
        
        # Factors for engagement
        avg_time_on_page = analytics_data.get("avg_time_on_page", 0)
        pages_per_session = analytics_data.get("pages_per_session", 1)
        bounce_rate = analytics_data.get("bounce_rate", 50)
        
        # Normalize to 0-100 scale
        time_score = min(avg_time_on_page / 300, 1.0) * 100  # 5 min = perfect
        depth_score = min(pages_per_session / 5, 1.0) * 100  # 5 pages = perfect
        bounce_score = max(0, 100 - bounce_rate)  # Lower bounce is better
        
        # Weighted average
        engagement_score = (
            time_score * 0.4 +
            depth_score * 0.3 +
            bounce_score * 0.3
        )
        
        return engagement_score
    
    async def _calculate_detailed_authority_metrics(
        self,
        campaign_id: str,
        daily_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate detailed authority building metrics"""
        
        # Aggregate over period
        total_days = len(daily_data)
        
        # Mock calculations - in production would use real analytics
        return {
            "branded_search_trend": 15.5,  # % increase
            "domain_authority_change": 2.0,  # Point increase
            "thought_leadership_score": 72.0,  # 0-100
            "content_virality_score": 45.0,  # 0-100
            "audience_quality_score": 83.0,  # 0-100
            "engagement_depth": 68.0  # 0-100
        }
    
    async def _get_analytics_data(self, campaign_id: str) -> Dict[str, Any]:
        """Get analytics data for authority calculations"""
        
        # In production, integrate with Google Analytics
        # Mock data for now
        return {
            "branded_search_lift": 12.5,
            "direct_traffic_lift": 8.0,
            "return_visitor_rate": 35.0,
            "avg_time_on_page": 245,  # seconds
            "pages_per_session": 3.2,
            "bounce_rate": 42.0,
            "social_shares": 156,
            "new_backlinks": 3
        }
    
    async def _generate_insights(self, report: Dict[str, Any]) -> List[str]:
        """Generate insights from performance data"""
        insights = []
        
        # CTR insights
        overall_ctr = report["summary"].get("overall_ctr", 0)
        if overall_ctr > GOOD_CTR:
            insights.append(
                f"Strong CTR of {overall_ctr:.2f}% indicates effective ad copy and targeting"
            )
        elif overall_ctr < 1.5:
            insights.append(
                f"Low CTR of {overall_ctr:.2f}% suggests ad copy or keyword relevance issues"
            )
        
        # Conversion insights
        conv_rate = report["summary"].get("overall_conversion_rate", 0)
        if conv_rate > GOOD_CONVERSION_RATE:
            insights.append(
                f"Excellent conversion rate of {conv_rate:.2f}% shows strong landing page performance"
            )
        
        # Cost insights
        cpa = report["summary"].get("overall_cpa", 0)
        if cpa > MAX_CPA:
            insights.append(
                f"CPA of ${cpa:.2f} exceeds target - consider optimization"
            )
        
        # Authority insights
        for campaign in report["campaigns"]:
            authority = campaign["metrics"].get(PerformanceMetric.AUTHORITY_IMPACT, 0)
            if authority > 70:
                insights.append(
                    f"Campaign {campaign['campaign_id']} showing strong authority building impact"
                )
        
        return insights
    
    async def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check for underperformers
        for campaign in report["campaigns"]:
            score = campaign.get("composite_score", 0)
            if score < 50:
                recommendations.append(
                    f"Consider pausing campaign {campaign['campaign_id']} due to low performance"
                )
        
        # Budget recommendations
        total_spend = report["summary"]["total_spend"]
        if total_spend < 8000:  # Under 80% of budget
            recommendations.append(
                "Budget underutilization - consider expanding keyword targeting"
            )
        
        # Keyword recommendations
        for campaign in report["campaigns"]:
            if campaign.get("top_keywords"):
                top_kw = campaign["top_keywords"][0]
                if top_kw.get("ctr", 0) > 5:
                    recommendations.append(
                        f"Increase bids on high-performing keyword: {top_kw.get('keyword')}"
                    )
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _is_cached(self, campaign_id: str) -> bool:
        """Check if metrics are cached and fresh"""
        if campaign_id not in self._performance_cache:
            return False
        
        cached_time, _ = self._performance_cache[campaign_id]
        age = (datetime.now() - cached_time).seconds
        
        return age < self._cache_ttl
    
    def _get_from_cache(self, campaign_id: str) -> Dict[PerformanceMetric, float]:
        """Get metrics from cache"""
        _, metrics = self._performance_cache[campaign_id]
        return metrics
    
    def _cache_metrics(self, campaign_id: str, metrics: Dict[PerformanceMetric, float]):
        """Cache metrics with timestamp"""
        self._performance_cache[campaign_id] = (datetime.now(), metrics)
    
    async def _update_authority_score(self, campaign_id: str, increment: float):
        """Update authority score for a campaign"""
        # In production, this would persist to database
        logger.info(f"Authority score increased by {increment} for campaign {campaign_id}")
    
    # Mock data methods for testing
    
    def _get_mock_performance(self) -> Dict[str, Any]:
        """Get mock performance data"""
        import random
        
        return {
            "impressions": random.randint(10000, 50000),
            "clicks": random.randint(200, 1500),
            "conversions": random.randint(10, 100),
            "cost": random.uniform(500, 2500),
            "quality_score": random.uniform(6, 9),
            "conversion_value": random.uniform(1000, 10000)
        }
    
    def _get_mock_daily_data(self) -> List[Dict[str, Any]]:
        """Get mock daily performance data"""
        daily_data = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            daily_data.append({
                "date": date.isoformat(),
                "impressions": 5000 + i * 100,
                "clicks": 150 + i * 10,
                "conversions": 8 + i,
                "cost": 300 + i * 20
            })
        return daily_data
    
    def _get_mock_keyword_data(self) -> List[Dict[str, Any]]:
        """Get mock keyword performance data"""
        keywords = [
            "marketing automation",
            "business growth solutions",
            "professional services marketing",
            "b2b lead generation",
            "content marketing strategy"
        ]
        
        keyword_data = []
        for kw in keywords:
            keyword_data.append({
                "keyword": kw,
                "impressions": 1000,
                "clicks": 50,
                "conversions": 3,
                "ctr": 5.0,
                "avg_cpc": 2.50,
                "quality_score": 8
            })
        
        return keyword_data
    
    def _get_mock_ad_data(self) -> List[Dict[str, Any]]:
        """Get mock ad performance data"""
        return [
            {
                "ad_id": "ad_001",
                "headline": "Transform Your Business Today",
                "impressions": 5000,
                "clicks": 250,
                "conversions": 15,
                "ctr": 5.0,
                "conversion_rate": 6.0
            }
        ]