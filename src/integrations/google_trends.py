"""
Google Trends API Integration for long-term pattern analysis
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)

# Trend analysis configuration
DEFAULT_TIMEFRAME = "now 7-d"  # Last 7 days
MOMENTUM_THRESHOLDS = {
    "rising": 1.2,    # 20% increase
    "declining": 0.8  # 20% decrease
}


class GoogleTrendsAnalyzer:
    """Google Trends API integration for long-term pattern analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.timeframe = DEFAULT_TIMEFRAME
        self._cache = {}  # Simple in-memory cache
        self._cache_ttl = 3600  # 1 hour cache TTL
    
    async def analyze_trend_momentum(
        self, keywords: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze trend momentum for given keywords
        
        Args:
            keywords: List of keywords to analyze
            
        Returns:
            Dictionary mapping keywords to trend data
        """
        if not keywords:
            return {}
        
        trend_data = {}
        
        # Process keywords in batches to avoid rate limits
        batch_size = 5
        for i in range(0, len(keywords), batch_size):
            batch = keywords[i:i + batch_size]
            
            for keyword in batch:
                # Check cache first
                cached_data = self._get_from_cache(keyword)
                if cached_data:
                    trend_data[keyword] = cached_data
                    continue
                
                # Get trend data
                try:
                    if self.api_key:
                        keyword_trends = await self._get_keyword_trends(keyword)
                    else:
                        keyword_trends = self._get_mock_trends(keyword)
                    
                    # Process trend data
                    processed_data = {
                        "current_interest": keyword_trends.get("current_score", 0),
                        "momentum": self._calculate_momentum(keyword_trends.get("timeline", [])),
                        "related_queries": keyword_trends.get("related_queries", [])[:5],
                        "geographic_interest": keyword_trends.get("geo_data", {}),
                        "seasonality": keyword_trends.get("seasonality", "none"),
                        "breakout_terms": keyword_trends.get("breakout_terms", [])
                    }
                    
                    trend_data[keyword] = processed_data
                    self._add_to_cache(keyword, processed_data)
                    
                except Exception as e:
                    logger.error(f"Error analyzing trends for '{keyword}': {str(e)}")
                    trend_data[keyword] = self._get_default_trend_data()
            
            # Small delay between batches
            if i + batch_size < len(keywords):
                await asyncio.sleep(0.5)
        
        return trend_data
    
    async def get_rising_topics(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get currently rising topics in a category
        
        Args:
            category: Optional category filter (e.g., "business", "technology")
            
        Returns:
            List of rising topics with momentum data
        """
        if self.api_key:
            # In production, would call actual Google Trends API
            return []
        else:
            return self._get_mock_rising_topics(category)
    
    async def _get_keyword_trends(self, keyword: str) -> Dict[str, Any]:
        """Get trend data for a specific keyword from API"""
        # In production, this would call the actual Google Trends API
        # For now, return mock data
        return self._get_mock_trends(keyword)
    
    def _calculate_momentum(self, timeline: List[Dict]) -> str:
        """Calculate trend momentum from timeline data"""
        if len(timeline) < 2:
            return "insufficient_data"
        
        # Get recent and older averages
        mid_point = len(timeline) // 2
        recent_data = timeline[mid_point:]
        older_data = timeline[:mid_point]
        
        recent_avg = sum(point.get("value", 0) for point in recent_data) / len(recent_data)
        older_avg = sum(point.get("value", 0) for point in older_data) / len(older_data)
        
        if older_avg == 0:
            return "stable"
        
        ratio = recent_avg / older_avg
        
        if ratio >= MOMENTUM_THRESHOLDS["rising"]:
            return "rising"
        elif ratio <= MOMENTUM_THRESHOLDS["declining"]:
            return "declining"
        else:
            return "stable"
    
    def _get_from_cache(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Get trend data from cache if available and not expired"""
        if keyword in self._cache:
            cached_time, cached_data = self._cache[keyword]
            if (datetime.now() - cached_time).seconds < self._cache_ttl:
                return cached_data
        return None
    
    def _add_to_cache(self, keyword: str, data: Dict[str, Any]):
        """Add trend data to cache"""
        self._cache[keyword] = (datetime.now(), data)
    
    def _get_default_trend_data(self) -> Dict[str, Any]:
        """Get default trend data for errors"""
        return {
            "current_interest": 0,
            "momentum": "insufficient_data",
            "related_queries": [],
            "geographic_interest": {},
            "seasonality": "none",
            "breakout_terms": []
        }
    
    def _get_mock_trends(self, keyword: str) -> Dict[str, Any]:
        """Get mock trend data for testing"""
        # Generate mock data based on keyword
        keyword_lower = keyword.lower()
        
        # Define some mock patterns
        if "ai" in keyword_lower or "chatgpt" in keyword_lower:
            return {
                "current_score": 85,
                "timeline": [
                    {"date": "2025-01-01", "value": 45},
                    {"date": "2025-01-02", "value": 52},
                    {"date": "2025-01-03", "value": 58},
                    {"date": "2025-01-04", "value": 65},
                    {"date": "2025-01-05", "value": 72},
                    {"date": "2025-01-06", "value": 78},
                    {"date": "2025-01-07", "value": 85}
                ],
                "related_queries": [
                    "ai tools", "chatgpt prompts", "ai marketing",
                    "ai automation", "best ai tools"
                ],
                "geo_data": {
                    "US": 100, "UK": 85, "CA": 78, "AU": 72
                },
                "seasonality": "none",
                "breakout_terms": ["ai agent", "gpt-4", "claude"]
            }
        elif "marketing" in keyword_lower:
            return {
                "current_score": 72,
                "timeline": [
                    {"date": "2025-01-01", "value": 68},
                    {"date": "2025-01-02", "value": 70},
                    {"date": "2025-01-03", "value": 69},
                    {"date": "2025-01-04", "value": 71},
                    {"date": "2025-01-05", "value": 73},
                    {"date": "2025-01-06", "value": 72},
                    {"date": "2025-01-07", "value": 72}
                ],
                "related_queries": [
                    "digital marketing", "marketing strategy", "content marketing",
                    "social media marketing", "marketing automation"
                ],
                "geo_data": {
                    "US": 100, "UK": 92, "IN": 88, "CA": 85
                },
                "seasonality": "q1_high",
                "breakout_terms": ["tiktok marketing", "ai marketing"]
            }
        elif "google" in keyword_lower:
            return {
                "current_score": 78,
                "timeline": [
                    {"date": "2025-01-01", "value": 82},
                    {"date": "2025-01-02", "value": 79},
                    {"date": "2025-01-03", "value": 77},
                    {"date": "2025-01-04", "value": 75},
                    {"date": "2025-01-05", "value": 76},
                    {"date": "2025-01-06", "value": 77},
                    {"date": "2025-01-07", "value": 78}
                ],
                "related_queries": [
                    "google ads", "google algorithm", "google seo",
                    "google business", "google analytics"
                ],
                "geo_data": {
                    "US": 100, "IN": 95, "UK": 90, "BR": 85
                },
                "seasonality": "none",
                "breakout_terms": ["google bard", "sge"]
            }
        else:
            # Default pattern
            return {
                "current_score": 50,
                "timeline": [
                    {"date": "2025-01-01", "value": 48},
                    {"date": "2025-01-02", "value": 49},
                    {"date": "2025-01-03", "value": 50},
                    {"date": "2025-01-04", "value": 51},
                    {"date": "2025-01-05", "value": 50},
                    {"date": "2025-01-06", "value": 49},
                    {"date": "2025-01-07", "value": 50}
                ],
                "related_queries": [keyword + " tips", keyword + " guide"],
                "geo_data": {"US": 100, "UK": 80},
                "seasonality": "none",
                "breakout_terms": []
            }
    
    def _get_mock_rising_topics(self, category: Optional[str]) -> List[Dict[str, Any]]:
        """Get mock rising topics for testing"""
        base_topics = [
            {
                "topic": "AI Customer Service",
                "growth_rate": 250,
                "current_interest": 68,
                "category": "technology",
                "description": "Automated customer support using AI"
            },
            {
                "topic": "Local SEO 2025",
                "growth_rate": 180,
                "current_interest": 75,
                "category": "marketing",
                "description": "New local search optimization strategies"
            },
            {
                "topic": "Business Automation Tools",
                "growth_rate": 220,
                "current_interest": 82,
                "category": "business",
                "description": "Tools for automating business processes"
            },
            {
                "topic": "TikTok for B2B",
                "growth_rate": 340,
                "current_interest": 58,
                "category": "marketing",
                "description": "B2B marketing strategies on TikTok"
            },
            {
                "topic": "Revenue Operations",
                "growth_rate": 195,
                "current_interest": 71,
                "category": "business",
                "description": "Aligning sales, marketing, and CS operations"
            }
        ]
        
        if category:
            return [t for t in base_topics if t["category"] == category]
        return base_topics


async def test_trends_analyzer():
    """Test Google Trends analyzer"""
    analyzer = GoogleTrendsAnalyzer()
    
    # Test keyword analysis
    keywords = ["ai marketing", "chatgpt", "content strategy", "google ads"]
    print("Analyzing trend momentum for keywords...")
    trends = await analyzer.analyze_trend_momentum(keywords)
    
    for keyword, data in trends.items():
        print(f"\nKeyword: {keyword}")
        print(f"  Current Interest: {data['current_interest']}")
        print(f"  Momentum: {data['momentum']}")
        print(f"  Related Queries: {', '.join(data['related_queries'][:3])}")
    
    # Test rising topics
    print("\n\nRising topics in marketing:")
    rising = await analyzer.get_rising_topics("marketing")
    for topic in rising:
        print(f"\n{topic['topic']}")
        print(f"  Growth Rate: {topic['growth_rate']}%")
        print(f"  Current Interest: {topic['current_interest']}")
        print(f"  Description: {topic['description']}")


if __name__ == "__main__":
    asyncio.run(test_trends_analyzer())