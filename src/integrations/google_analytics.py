"""
Google Analytics 4 Data Retrieval for Brand BOS
Fetches performance data for content attribution and cross-platform analysis
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import asyncio

from googleapiclient.errors import HttpError
from .google_oauth import GoogleOAuthManager, GoogleAPIException

logger = logging.getLogger(__name__)


@dataclass
class GAMetrics:
    """Google Analytics metrics container"""
    sessions: int = 0
    users: int = 0
    page_views: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    conversions: int = 0
    conversion_rate: float = 0.0
    revenue: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class UTMPerformance:
    """UTM campaign performance data"""
    utm_source: str
    utm_medium: str 
    utm_campaign: str
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None
    metrics: GAMetrics = None
    date_range: Tuple[str, str] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = GAMetrics()


@dataclass
class ContentPerformance:
    """Content piece performance across platforms"""
    content_id: str
    title: str
    url: str
    total_metrics: GAMetrics
    utm_breakdown: List[UTMPerformance]
    top_sources: List[Tuple[str, int]]  # (source, sessions)
    date_range: Tuple[str, str]


class GoogleAnalyticsClient:
    """Google Analytics 4 API client for Brand BOS"""
    
    def __init__(self, oauth_manager: GoogleOAuthManager):
        """
        Initialize GA4 client
        
        Args:
            oauth_manager: Google OAuth manager instance
        """
        self.oauth_manager = oauth_manager
        self._property_cache: Dict[str, str] = {}
    
    async def get_ga4_properties(self, client_id: str) -> List[Dict[str, Any]]:
        """
        Get available GA4 properties for a client
        
        Args:
            client_id: Client identifier
            
        Returns:
            List of GA4 properties with metadata
        """
        try:
            service = await self.oauth_manager.get_analytics_service(client_id)
            
            # List GA4 properties
            request = service.properties().list()
            response = request.execute()
            
            properties = []
            for prop in response.get('properties', []):
                properties.append({
                    'property_id': prop['name'].split('/')[-1],
                    'display_name': prop.get('displayName', ''),
                    'create_time': prop.get('createTime', ''),
                    'currency_code': prop.get('currencyCode', 'USD'),
                    'time_zone': prop.get('timeZone', 'UTC')
                })
            
            logger.info(f"Found {len(properties)} GA4 properties for client {client_id}")
            return properties
            
        except HttpError as e:
            logger.error(f"GA4 properties request failed: {e}")
            raise GoogleAPIException(f"Failed to get GA4 properties: {e}", e)
    
    async def set_default_property(self, client_id: str, property_id: str):
        """Set default GA4 property for a client"""
        self._property_cache[client_id] = property_id
        logger.info(f"Set default GA4 property {property_id} for client {client_id}")
    
    async def get_utm_performance(
        self,
        client_id: str,
        property_id: Optional[str] = None,
        start_date: str = "30daysAgo",
        end_date: str = "today",
        utm_campaign_filter: Optional[str] = None
    ) -> List[UTMPerformance]:
        """
        Get UTM campaign performance data
        
        Args:
            client_id: Client identifier
            property_id: GA4 property ID (uses default if None)
            start_date: Start date for data (GA4 format)
            end_date: End date for data (GA4 format)
            utm_campaign_filter: Filter for specific campaign pattern
            
        Returns:
            List of UTM performance data
        """
        try:
            service = await self.oauth_manager.get_analytics_service(client_id)
            
            if not property_id:
                property_id = self._property_cache.get(client_id)
                if not property_id:
                    raise ValueError(f"No default GA4 property set for client {client_id}")
            
            # Build request
            request_body = {
                "requests": [{
                    "property": f"properties/{property_id}",
                    "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                    "dimensions": [
                        {"name": "firstUserSource"},
                        {"name": "firstUserMedium"}, 
                        {"name": "firstUserCampaignName"},
                        {"name": "firstUserGoogleAdsKeyword"},
                        {"name": "firstUserSourceMedium"}
                    ],
                    "metrics": [
                        {"name": "sessions"},
                        {"name": "totalUsers"},
                        {"name": "screenPageViews"},
                        {"name": "bounceRate"},
                        {"name": "averageSessionDuration"},
                        {"name": "conversions"},
                        {"name": "conversionRate"},
                        {"name": "totalRevenue"}
                    ]
                }]
            }
            
            # Add campaign filter if specified
            if utm_campaign_filter:
                request_body["requests"][0]["dimensionFilter"] = {
                    "filter": {
                        "fieldName": "firstUserCampaignName",
                        "stringFilter": {
                            "matchType": "CONTAINS",
                            "value": utm_campaign_filter
                        }
                    }
                }
            
            # Execute request
            response = service.batchRunReports(body=request_body).execute()
            
            utm_performance = []
            
            for report in response.get("reports", []):
                for row in report.get("rows", []):
                    dimensions = row.get("dimensionValues", [])
                    metrics = row.get("metricValues", [])
                    
                    if len(dimensions) >= 3 and len(metrics) >= 8:
                        utm_perf = UTMPerformance(
                            utm_source=dimensions[0].get("value", ""),
                            utm_medium=dimensions[1].get("value", ""),
                            utm_campaign=dimensions[2].get("value", ""),
                            utm_term=dimensions[3].get("value") if len(dimensions) > 3 else None,
                            metrics=GAMetrics(
                                sessions=int(metrics[0].get("value", 0)),
                                users=int(metrics[1].get("value", 0)),
                                page_views=int(metrics[2].get("value", 0)),
                                bounce_rate=float(metrics[3].get("value", 0)),
                                avg_session_duration=float(metrics[4].get("value", 0)),
                                conversions=int(metrics[5].get("value", 0)),
                                conversion_rate=float(metrics[6].get("value", 0)),
                                revenue=float(metrics[7].get("value", 0))
                            ),
                            date_range=(start_date, end_date)
                        )
                        utm_performance.append(utm_perf)
            
            logger.info(f"Retrieved {len(utm_performance)} UTM performance records")
            return utm_performance
            
        except HttpError as e:
            logger.error(f"UTM performance request failed: {e}")
            raise GoogleAPIException(f"Failed to get UTM performance: {e}", e)
    
    async def get_content_performance(
        self,
        client_id: str,
        page_path: str,
        property_id: Optional[str] = None,
        start_date: str = "30daysAgo",
        end_date: str = "today"
    ) -> ContentPerformance:
        """
        Get performance data for specific content page
        
        Args:
            client_id: Client identifier
            page_path: Page path to analyze
            property_id: GA4 property ID
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Content performance data with UTM breakdown
        """
        try:
            service = await self.oauth_manager.get_analytics_service(client_id)
            
            if not property_id:
                property_id = self._property_cache.get(client_id)
            
            # Get overall content performance
            overall_request = {
                "requests": [{
                    "property": f"properties/{property_id}",
                    "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                    "dimensions": [{"name": "pagePath"}],
                    "metrics": [
                        {"name": "sessions"},
                        {"name": "totalUsers"},
                        {"name": "screenPageViews"},
                        {"name": "bounceRate"},
                        {"name": "averageSessionDuration"},
                        {"name": "conversions"},
                        {"name": "totalRevenue"}
                    ],
                    "dimensionFilter": {
                        "filter": {
                            "fieldName": "pagePath",
                            "stringFilter": {
                                "matchType": "EXACT",
                                "value": page_path
                            }
                        }
                    }
                }]
            }
            
            overall_response = service.batchRunReports(body=overall_request).execute()
            
            # Parse overall metrics
            total_metrics = GAMetrics()
            
            for report in overall_response.get("reports", []):
                for row in report.get("rows", []):
                    metrics = row.get("metricValues", [])
                    if len(metrics) >= 7:
                        total_metrics = GAMetrics(
                            sessions=int(metrics[0].get("value", 0)),
                            users=int(metrics[1].get("value", 0)),
                            page_views=int(metrics[2].get("value", 0)),
                            bounce_rate=float(metrics[3].get("value", 0)),
                            avg_session_duration=float(metrics[4].get("value", 0)),
                            conversions=int(metrics[5].get("value", 0)),
                            revenue=float(metrics[6].get("value", 0))
                        )
                        break
            
            # Get UTM breakdown for this content
            utm_request = {
                "requests": [{
                    "property": f"properties/{property_id}",
                    "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                    "dimensions": [
                        {"name": "pagePath"},
                        {"name": "firstUserSource"},
                        {"name": "firstUserMedium"},
                        {"name": "firstUserCampaignName"}
                    ],
                    "metrics": [
                        {"name": "sessions"},
                        {"name": "totalUsers"},
                        {"name": "conversions"}
                    ],
                    "dimensionFilter": {
                        "filter": {
                            "fieldName": "pagePath",
                            "stringFilter": {
                                "matchType": "EXACT", 
                                "value": page_path
                            }
                        }
                    }
                }]
            }
            
            utm_response = service.batchRunReports(body=utm_request).execute()
            
            # Parse UTM breakdown
            utm_breakdown = []
            source_sessions = {}
            
            for report in utm_response.get("reports", []):
                for row in report.get("rows", []):
                    dimensions = row.get("dimensionValues", [])
                    metrics = row.get("metricValues", [])
                    
                    if len(dimensions) >= 4 and len(metrics) >= 3:
                        source = dimensions[1].get("value", "")
                        sessions = int(metrics[0].get("value", 0))
                        
                        # Track top sources
                        source_sessions[source] = source_sessions.get(source, 0) + sessions
                        
                        utm_breakdown.append(UTMPerformance(
                            utm_source=source,
                            utm_medium=dimensions[2].get("value", ""),
                            utm_campaign=dimensions[3].get("value", ""),
                            metrics=GAMetrics(
                                sessions=sessions,
                                users=int(metrics[1].get("value", 0)),
                                conversions=int(metrics[2].get("value", 0))
                            ),
                            date_range=(start_date, end_date)
                        ))
            
            # Get top sources
            top_sources = sorted(source_sessions.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return ContentPerformance(
                content_id=page_path.split('/')[-1],
                title=page_path,
                url=page_path,
                total_metrics=total_metrics,
                utm_breakdown=utm_breakdown,
                top_sources=top_sources,
                date_range=(start_date, end_date)
            )
            
        except HttpError as e:
            logger.error(f"Content performance request failed: {e}")
            raise GoogleAPIException(f"Failed to get content performance: {e}", e)
    
    async def get_bbos_campaign_performance(
        self,
        client_id: str,
        property_id: Optional[str] = None,
        start_date: str = "30daysAgo",
        end_date: str = "today"
    ) -> Dict[str, List[UTMPerformance]]:
        """
        Get performance data for all Brand BOS campaigns
        
        Args:
            client_id: Client identifier
            property_id: GA4 property ID
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary mapping campaign variations to performance data
        """
        try:
            # Get all UTM data with BBOS filter
            utm_data = await self.get_utm_performance(
                client_id=client_id,
                property_id=property_id,
                start_date=start_date,
                end_date=end_date,
                utm_campaign_filter="BBOS"
            )
            
            # Group by campaign variation
            variation_performance = {}
            
            for utm_perf in utm_data:
                campaign_name = utm_perf.utm_campaign
                
                # Extract variation from campaign name (A-A_BBOS_task_v1 -> A)
                if campaign_name.startswith("A-") and "_BBOS_" in campaign_name:
                    parts = campaign_name.split("_")
                    if len(parts) >= 3:
                        variation = parts[0].replace("A-", "")
                        
                        if variation not in variation_performance:
                            variation_performance[variation] = []
                        
                        variation_performance[variation].append(utm_perf)
            
            logger.info(f"Found BBOS campaigns for {len(variation_performance)} variations")
            return variation_performance
            
        except Exception as e:
            logger.error(f"BBOS campaign performance analysis failed: {e}")
            raise
    
    async def get_authority_impact_metrics(
        self,
        client_id: str,
        property_id: Optional[str] = None,
        start_date: str = "30daysAgo",
        end_date: str = "today"
    ) -> Dict[str, float]:
        """
        Calculate authority impact metrics from GA4 data
        
        Args:
            client_id: Client identifier
            property_id: GA4 property ID
            start_date: Start date for comparison
            end_date: End date for analysis
            
        Returns:
            Authority impact metrics for Adsby scoring
        """
        try:
            service = await self.oauth_manager.get_analytics_service(client_id)
            
            if not property_id:
                property_id = self._property_cache.get(client_id)
            
            # Calculate comparison period (previous 30 days)
            start_dt = datetime.strptime(start_date.replace("daysAgo", ""), "%d") if "daysAgo" in start_date else datetime.strptime(start_date, "%Y-%m-%d")
            comparison_start = start_dt - timedelta(days=30)
            comparison_end = start_dt - timedelta(days=1)
            
            # Get current period data
            current_request = {
                "requests": [{
                    "property": f"properties/{property_id}",
                    "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                    "dimensions": [{"name": "firstUserSource"}],
                    "metrics": [
                        {"name": "sessions"},
                        {"name": "totalUsers"},
                        {"name": "newUsers"},
                        {"name": "screenPageViews"},
                        {"name": "averageSessionDuration"},
                        {"name": "bounceRate"}
                    ]
                }]
            }
            
            # Get comparison period data
            comparison_request = {
                "requests": [{
                    "property": f"properties/{property_id}",
                    "dateRanges": [{"startDate": comparison_start.strftime("%Y-%m-%d"), "endDate": comparison_end.strftime("%Y-%m-%d")}],
                    "dimensions": [{"name": "firstUserSource"}],
                    "metrics": [
                        {"name": "sessions"},
                        {"name": "totalUsers"},
                        {"name": "newUsers"},
                        {"name": "screenPageViews"},
                        {"name": "averageSessionDuration"},
                        {"name": "bounceRate"}
                    ]
                }]
            }
            
            current_response = service.batchRunReports(body=current_request).execute()
            comparison_response = service.batchRunReports(body=comparison_request).execute()
            
            # Parse current period metrics
            current_metrics = {"direct": 0, "organic": 0, "total_sessions": 0, "engagement_score": 0}
            comparison_metrics = {"direct": 0, "organic": 0, "total_sessions": 0}
            
            # Process current period
            for report in current_response.get("reports", []):
                for row in report.get("rows", []):
                    source = row.get("dimensionValues", [{}])[0].get("value", "")
                    metrics = row.get("metricValues", [])
                    
                    if len(metrics) >= 6:
                        sessions = int(metrics[0].get("value", 0))
                        current_metrics["total_sessions"] += sessions
                        
                        if source == "(direct)":
                            current_metrics["direct"] += sessions
                        elif source in ["google", "organic"]:
                            current_metrics["organic"] += sessions
                        
                        # Calculate engagement score
                        avg_duration = float(metrics[4].get("value", 0))
                        bounce_rate = float(metrics[5].get("value", 0))
                        pages_per_session = float(metrics[3].get("value", 0)) / max(sessions, 1)
                        
                        engagement = (avg_duration / 60) * (1 - bounce_rate) * pages_per_session
                        current_metrics["engagement_score"] += engagement * sessions
            
            # Process comparison period
            for report in comparison_response.get("reports", []):
                for row in report.get("rows", []):
                    source = row.get("dimensionValues", [{}])[0].get("value", "")
                    metrics = row.get("metricValues", [])
                    
                    if len(metrics) >= 1:
                        sessions = int(metrics[0].get("value", 0))
                        comparison_metrics["total_sessions"] += sessions
                        
                        if source == "(direct)":
                            comparison_metrics["direct"] += sessions
                        elif source in ["google", "organic"]:
                            comparison_metrics["organic"] += sessions
            
            # Calculate authority impact metrics
            authority_metrics = {}
            
            # Direct traffic increase
            if comparison_metrics["direct"] > 0:
                authority_metrics["direct_traffic_increase"] = (
                    (current_metrics["direct"] - comparison_metrics["direct"]) / comparison_metrics["direct"]
                ) * 100
            else:
                authority_metrics["direct_traffic_increase"] = 0.0
            
            # Branded search increase (approximated by organic growth)
            if comparison_metrics["organic"] > 0:
                authority_metrics["branded_search_increase"] = (
                    (current_metrics["organic"] - comparison_metrics["organic"]) / comparison_metrics["organic"]
                ) * 100
            else:
                authority_metrics["branded_search_increase"] = 0.0
            
            # Content engagement score (0-100)
            if current_metrics["total_sessions"] > 0:
                authority_metrics["content_engagement_score"] = min(
                    (current_metrics["engagement_score"] / current_metrics["total_sessions"]) * 10, 100
                )
            else:
                authority_metrics["content_engagement_score"] = 0.0
            
            # Return visitor rate (approximated by total users vs new users ratio)
            authority_metrics["return_visitor_rate"] = 35.0  # Default placeholder
            
            logger.info(f"Calculated authority impact metrics for client {client_id}")
            return authority_metrics
            
        except HttpError as e:
            logger.error(f"Authority metrics calculation failed: {e}")
            raise GoogleAPIException(f"Failed to calculate authority metrics: {e}", e)


# Utility functions for GA4 data processing
async def get_client_ga4_summary(
    oauth_manager: GoogleOAuthManager,
    client_id: str,
    days: int = 30
) -> Dict[str, Any]:
    """Get summary analytics data for a client"""
    
    ga_client = GoogleAnalyticsClient(oauth_manager)
    
    try:
        # Get UTM performance for last 30 days
        utm_data = await ga_client.get_utm_performance(
            client_id=client_id,
            start_date=f"{days}daysAgo",
            end_date="today"
        )
        
        # Get BBOS campaign performance
        bbos_data = await ga_client.get_bbos_campaign_performance(
            client_id=client_id,
            start_date=f"{days}daysAgo",
            end_date="today"
        )
        
        # Calculate summary metrics
        total_sessions = sum(utm.metrics.sessions for utm in utm_data)
        total_conversions = sum(utm.metrics.conversions for utm in utm_data)
        total_revenue = sum(utm.metrics.revenue for utm in utm_data)
        
        return {
            "period_days": days,
            "total_sessions": total_sessions,
            "total_conversions": total_conversions,
            "total_revenue": total_revenue,
            "conversion_rate": (total_conversions / total_sessions * 100) if total_sessions > 0 else 0,
            "utm_campaigns": len(utm_data),
            "bbos_variations": len(bbos_data),
            "top_sources": _get_top_sources(utm_data),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get GA4 summary for {client_id}: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


def _get_top_sources(utm_data: List[UTMPerformance]) -> List[Dict[str, Any]]:
    """Extract top traffic sources from UTM data"""
    source_metrics = {}
    
    for utm in utm_data:
        source = utm.utm_source
        if source not in source_metrics:
            source_metrics[source] = {"sessions": 0, "conversions": 0}
        
        source_metrics[source]["sessions"] += utm.metrics.sessions
        source_metrics[source]["conversions"] += utm.metrics.conversions
    
    # Sort by sessions and return top 5
    top_sources = sorted(
        [{"source": k, **v} for k, v in source_metrics.items()],
        key=lambda x: x["sessions"],
        reverse=True
    )[:5]
    
    return top_sources