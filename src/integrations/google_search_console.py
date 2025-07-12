"""
Google Search Console Integration for Brand BOS
Tracks organic search performance and keyword data for content attribution
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
class SearchMetrics:
    """Search Console metrics container"""
    clicks: int = 0
    impressions: int = 0
    ctr: float = 0.0
    position: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class KeywordPerformance:
    """Keyword performance data from Search Console"""
    query: str
    page: str
    metrics: SearchMetrics
    date_range: Tuple[str, str]
    
    @property
    def click_value(self) -> float:
        """Estimated value per click based on position"""
        # Higher positions (lower numbers) are more valuable
        position_multiplier = max(1.0, (11 - min(self.metrics.position, 10)) / 10)
        return self.metrics.clicks * position_multiplier


@dataclass
class ContentSearchPerformance:
    """Search performance for specific content"""
    page_url: str
    total_metrics: SearchMetrics
    top_keywords: List[KeywordPerformance]
    keyword_count: int
    date_range: Tuple[str, str]
    
    @property
    def authority_score(self) -> float:
        """Calculate authority score based on search performance"""
        # Base score from CTR and position
        base_score = (self.total_metrics.ctr * 100) + (max(0, 20 - self.total_metrics.position) * 2)
        
        # Bonus for high impression volume
        impression_bonus = min(self.total_metrics.impressions / 1000, 10)
        
        # Bonus for keyword diversity
        keyword_bonus = min(self.keyword_count / 10, 5)
        
        return min(base_score + impression_bonus + keyword_bonus, 100)


class GoogleSearchConsoleClient:
    """Google Search Console API client for Brand BOS"""
    
    def __init__(self, oauth_manager: GoogleOAuthManager):
        """
        Initialize Search Console client
        
        Args:
            oauth_manager: Google OAuth manager instance
        """
        self.oauth_manager = oauth_manager
        self._property_cache: Dict[str, str] = {}
    
    async def get_search_console_properties(self, client_id: str) -> List[Dict[str, Any]]:
        """
        Get available Search Console properties for a client
        
        Args:
            client_id: Client identifier
            
        Returns:
            List of Search Console properties
        """
        try:
            service = await self.oauth_manager.get_search_console_service(client_id)
            
            # List properties
            request = service.sites().list()
            response = request.execute()
            
            properties = []
            for site in response.get('siteEntry', []):
                properties.append({
                    'site_url': site.get('siteUrl', ''),
                    'permission_level': site.get('permissionLevel', ''),
                    'verification_method': 'Search Console'
                })
            
            logger.info(f"Found {len(properties)} Search Console properties for client {client_id}")
            return properties
            
        except HttpError as e:
            logger.error(f"Search Console properties request failed: {e}")
            raise GoogleAPIException(f"Failed to get Search Console properties: {e}", e)
    
    async def set_default_property(self, client_id: str, site_url: str):
        """Set default Search Console property for a client"""
        self._property_cache[client_id] = site_url
        logger.info(f"Set default Search Console property {site_url} for client {client_id}")
    
    async def get_search_performance(
        self,
        client_id: str,
        site_url: Optional[str] = None,
        start_date: str = None,
        end_date: str = None,
        dimensions: List[str] = None,
        filters: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get search performance data from Search Console
        
        Args:
            client_id: Client identifier
            site_url: Site URL (uses default if None)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            dimensions: Dimensions to group by (query, page, country, device)
            filters: Filters to apply
            
        Returns:
            Search performance data
        """
        try:
            service = await self.oauth_manager.get_search_console_service(client_id)
            
            if not site_url:
                site_url = self._property_cache.get(client_id)
                if not site_url:
                    raise ValueError(f"No default Search Console property set for client {client_id}")
            
            # Set default date range if not provided
            if not start_date or not end_date:
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=30)
                start_date = start_dt.strftime("%Y-%m-%d")
                end_date = end_dt.strftime("%Y-%m-%d")
            
            # Set default dimensions
            if not dimensions:
                dimensions = ['query', 'page']
            
            # Build request body
            request_body = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': dimensions,
                'rowLimit': 25000  # Maximum allowed
            }
            
            # Add filters if provided
            if filters:
                request_body['dimensionFilterGroups'] = [{'filters': filters}]
            
            # Execute request
            request = service.searchanalytics().query(siteUrl=site_url, body=request_body)
            response = request.execute()
            
            logger.info(f"Retrieved {len(response.get('rows', []))} search performance rows")
            return response.get('rows', [])
            
        except HttpError as e:
            logger.error(f"Search performance request failed: {e}")
            raise GoogleAPIException(f"Failed to get search performance: {e}", e)
    
    async def get_keyword_performance(
        self,
        client_id: str,
        site_url: Optional[str] = None,
        start_date: str = None,
        end_date: str = None,
        min_impressions: int = 10
    ) -> List[KeywordPerformance]:
        """
        Get keyword performance data
        
        Args:
            client_id: Client identifier
            site_url: Site URL
            start_date: Start date
            end_date: End date
            min_impressions: Minimum impressions filter
            
        Returns:
            List of keyword performance data
        """
        try:
            # Get raw search data
            search_data = await self.get_search_performance(
                client_id=client_id,
                site_url=site_url,
                start_date=start_date,
                end_date=end_date,
                dimensions=['query', 'page']
            )
            
            keyword_performance = []
            
            for row in search_data:
                keys = row.get('keys', [])
                metrics = row
                
                if len(keys) >= 2:
                    impressions = metrics.get('impressions', 0)
                    
                    # Filter by minimum impressions
                    if impressions >= min_impressions:
                        keyword_perf = KeywordPerformance(
                            query=keys[0],
                            page=keys[1],
                            metrics=SearchMetrics(
                                clicks=metrics.get('clicks', 0),
                                impressions=impressions,
                                ctr=metrics.get('ctr', 0) * 100,  # Convert to percentage
                                position=metrics.get('position', 0)
                            ),
                            date_range=(start_date or "30daysAgo", end_date or "today")
                        )
                        keyword_performance.append(keyword_perf)
            
            # Sort by click value (most valuable first)
            keyword_performance.sort(key=lambda x: x.click_value, reverse=True)
            
            logger.info(f"Processed {len(keyword_performance)} keyword performance records")
            return keyword_performance
            
        except Exception as e:
            logger.error(f"Keyword performance analysis failed: {e}")
            raise
    
    async def get_content_search_performance(
        self,
        client_id: str,
        page_url: str,
        site_url: Optional[str] = None,
        start_date: str = None,
        end_date: str = None
    ) -> ContentSearchPerformance:
        """
        Get search performance for specific content page
        
        Args:
            client_id: Client identifier
            page_url: Specific page URL to analyze
            site_url: Site URL
            start_date: Start date
            end_date: End date
            
        Returns:
            Content search performance data
        """
        try:
            # Filter for specific page
            page_filter = {
                'dimension': 'page',
                'operator': 'equals',
                'expression': page_url
            }
            
            # Get overall page performance
            page_data = await self.get_search_performance(
                client_id=client_id,
                site_url=site_url,
                start_date=start_date,
                end_date=end_date,
                dimensions=['page'],
                filters=[page_filter]
            )
            
            # Get keyword breakdown for this page
            keyword_data = await self.get_search_performance(
                client_id=client_id,
                site_url=site_url,
                start_date=start_date,
                end_date=end_date,
                dimensions=['query', 'page'],
                filters=[page_filter]
            )
            
            # Parse overall metrics
            total_metrics = SearchMetrics()
            if page_data:
                total_metrics = SearchMetrics(
                    clicks=page_data[0].get('clicks', 0),
                    impressions=page_data[0].get('impressions', 0),
                    ctr=page_data[0].get('ctr', 0) * 100,
                    position=page_data[0].get('position', 0)
                )
            
            # Parse top keywords
            top_keywords = []
            for row in keyword_data[:20]:  # Top 20 keywords
                keys = row.get('keys', [])
                if len(keys) >= 2:
                    keyword_perf = KeywordPerformance(
                        query=keys[0],
                        page=keys[1],
                        metrics=SearchMetrics(
                            clicks=row.get('clicks', 0),
                            impressions=row.get('impressions', 0),
                            ctr=row.get('ctr', 0) * 100,
                            position=row.get('position', 0)
                        ),
                        date_range=(start_date or "30daysAgo", end_date or "today")
                    )
                    top_keywords.append(keyword_perf)
            
            return ContentSearchPerformance(
                page_url=page_url,
                total_metrics=total_metrics,
                top_keywords=top_keywords,
                keyword_count=len(keyword_data),
                date_range=(start_date or "30daysAgo", end_date or "today")
            )
            
        except Exception as e:
            logger.error(f"Content search performance analysis failed: {e}")
            raise
    
    async def get_branded_search_performance(
        self,
        client_id: str,
        brand_terms: List[str],
        site_url: Optional[str] = None,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Analyze branded search performance for authority impact
        
        Args:
            client_id: Client identifier
            brand_terms: List of brand-related search terms
            site_url: Site URL
            start_date: Start date
            end_date: End date
            
        Returns:
            Branded search analysis data
        """
        try:
            branded_performance = {}
            total_branded_clicks = 0
            total_branded_impressions = 0
            
            for brand_term in brand_terms:
                # Filter for queries containing brand term
                brand_filter = {
                    'dimension': 'query',
                    'operator': 'contains',
                    'expression': brand_term.lower()
                }
                
                brand_data = await self.get_search_performance(
                    client_id=client_id,
                    site_url=site_url,
                    start_date=start_date,
                    end_date=end_date,
                    dimensions=['query'],
                    filters=[brand_filter]
                )
                
                # Aggregate metrics for this brand term
                brand_clicks = sum(row.get('clicks', 0) for row in brand_data)
                brand_impressions = sum(row.get('impressions', 0) for row in brand_data)
                
                branded_performance[brand_term] = {
                    'clicks': brand_clicks,
                    'impressions': brand_impressions,
                    'ctr': (brand_clicks / brand_impressions * 100) if brand_impressions > 0 else 0,
                    'query_count': len(brand_data)
                }
                
                total_branded_clicks += brand_clicks
                total_branded_impressions += brand_impressions
            
            # Calculate overall branded search metrics
            return {
                'brand_terms': branded_performance,
                'total_branded_clicks': total_branded_clicks,
                'total_branded_impressions': total_branded_impressions,
                'overall_branded_ctr': (total_branded_clicks / total_branded_impressions * 100) if total_branded_impressions > 0 else 0,
                'date_range': (start_date or "30daysAgo", end_date or "today")
            }
            
        except Exception as e:
            logger.error(f"Branded search analysis failed: {e}")
            raise
    
    async def get_content_keyword_opportunities(
        self,
        client_id: str,
        site_url: Optional[str] = None,
        min_position: float = 4.0,
        max_position: float = 20.0,
        min_impressions: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Identify keyword opportunities for content optimization
        
        Args:
            client_id: Client identifier
            site_url: Site URL
            min_position: Minimum position to consider (higher numbers = lower positions)
            max_position: Maximum position to consider
            min_impressions: Minimum impressions required
            
        Returns:
            List of keyword opportunities
        """
        try:
            # Get all search performance data
            search_data = await self.get_search_performance(
                client_id=client_id,
                site_url=site_url,
                dimensions=['query', 'page']
            )
            
            opportunities = []
            
            for row in search_data:
                keys = row.get('keys', [])
                position = row.get('position', 0)
                impressions = row.get('impressions', 0)
                clicks = row.get('clicks', 0)
                ctr = row.get('ctr', 0) * 100
                
                # Filter for opportunity criteria
                if (len(keys) >= 2 and 
                    min_position <= position <= max_position and 
                    impressions >= min_impressions):
                    
                    # Calculate opportunity score
                    # Higher impressions + lower position = better opportunity
                    opportunity_score = (impressions / 100) * (21 - position) / 20
                    
                    opportunities.append({
                        'query': keys[0],
                        'page': keys[1],
                        'current_position': position,
                        'impressions': impressions,
                        'clicks': clicks,
                        'ctr': ctr,
                        'opportunity_score': opportunity_score,
                        'potential_clicks': impressions * 0.1,  # Estimate 10% CTR improvement
                        'ranking_improvement_needed': max(0, position - 3)  # Target top 3
                    })
            
            # Sort by opportunity score
            opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
            
            logger.info(f"Identified {len(opportunities)} keyword opportunities")
            return opportunities[:50]  # Top 50 opportunities
            
        except Exception as e:
            logger.error(f"Keyword opportunity analysis failed: {e}")
            raise


# Utility functions for Search Console data processing
async def get_site_search_summary(
    oauth_manager: GoogleOAuthManager,
    client_id: str,
    site_url: str,
    days: int = 30
) -> Dict[str, Any]:
    """Get summary search data for a site"""
    
    gsc_client = GoogleSearchConsoleClient(oauth_manager)
    
    try:
        # Set date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Get overall site performance
        search_data = await gsc_client.get_search_performance(
            client_id=client_id,
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=[]  # No dimensions = total metrics
        )
        
        # Get top pages
        page_data = await gsc_client.get_search_performance(
            client_id=client_id,
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=['page']
        )
        
        # Get top queries
        query_data = await gsc_client.get_search_performance(
            client_id=client_id,
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=['query']
        )
        
        # Parse overall metrics
        total_metrics = SearchMetrics()
        if search_data:
            total_metrics = SearchMetrics(
                clicks=search_data[0].get('clicks', 0),
                impressions=search_data[0].get('impressions', 0),
                ctr=search_data[0].get('ctr', 0) * 100,
                position=search_data[0].get('position', 0)
            )
        
        return {
            "site_url": site_url,
            "period_days": days,
            "total_metrics": total_metrics.to_dict(),
            "top_pages": page_data[:10],
            "top_queries": query_data[:10],
            "page_count": len(page_data),
            "query_count": len(query_data),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get search summary for {site_url}: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


def calculate_content_authority_score(search_performance: ContentSearchPerformance) -> float:
    """Calculate authority score based on search performance"""
    return search_performance.authority_score