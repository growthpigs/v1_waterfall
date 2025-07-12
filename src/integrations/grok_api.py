"""
Grok API Integration for X trending posts
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import aiohttp
import logging
from enum import Enum

from ..database.cartwheel_models import ViralContent, ConvergenceSource

logger = logging.getLogger(__name__)

# API configuration
GROK_API_BASE_URL = "https://api.grok.com/v1"
DEFAULT_ENGAGEMENT_THRESHOLD = 1000
DEFAULT_POST_LIMIT = 50
RATE_LIMIT_DELAY = 1.0  # Seconds between requests


class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    GIF = "gif"
    NONE = "none"


class GrokIntegration:
    """Grok API integration for X trending posts"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = GROK_API_BASE_URL
        self.session = None
        self._rate_limit_lock = asyncio.Lock()
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self._get_headers()
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def get_trending_posts(
        self,
        hours: int = 24,
        media_only: bool = True,
        engagement_threshold: int = DEFAULT_ENGAGEMENT_THRESHOLD,
        limit: int = DEFAULT_POST_LIMIT
    ) -> List[ViralContent]:
        """
        Get trending X posts with optional media filtering
        
        Args:
            hours: Timeframe in hours (default 24)
            media_only: Only return posts with media
            engagement_threshold: Minimum engagement for consideration
            limit: Maximum number of posts to return
            
        Returns:
            List of viral content from X
        """
        if not self.api_key:
            logger.warning("Grok API key not configured, returning mock data")
            return self._get_mock_trending_posts()
        
        params = {
            "timeframe": f"{hours}h",
            "media_filter": "required" if media_only else "optional",
            "engagement_threshold": engagement_threshold,
            "limit": limit
        }
        
        try:
            # Create session if not exists
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self._get_headers())
            
            trending_posts = await self._make_grok_request("/trending/posts", params)
            
            viral_content = []
            for post in trending_posts:
                content = await self._post_to_viral_content(post)
                if content:
                    viral_content.append(content)
            
            logger.info(f"Retrieved {len(viral_content)} trending posts from Grok")
            return viral_content
            
        except Exception as e:
            logger.error(f"Error fetching trending posts: {str(e)}")
            return []
    
    async def _make_grok_request(
        self, endpoint: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Make API request to Grok with rate limiting"""
        async with self._rate_limit_lock:
            url = f"{self.base_url}{endpoint}"
            
            try:
                async with self.session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Rate limiting
                    await asyncio.sleep(RATE_LIMIT_DELAY)
                    
                    return data.get("posts", [])
                    
            except aiohttp.ClientError as e:
                logger.error(f"Grok API request failed: {str(e)}")
                raise
    
    async def _post_to_viral_content(self, post: Dict[str, Any]) -> Optional[ViralContent]:
        """Convert Grok post data to ViralContent"""
        try:
            # Extract keywords from post text
            keywords = await self._extract_keywords(post.get("text", ""))
            
            # Analyze sentiment
            sentiment = await self._analyze_sentiment(post.get("text", ""))
            
            # Calculate scores
            engagement_score = self._calculate_engagement_score(post)
            viral_velocity = self._calculate_viral_velocity(post)
            
            return ViralContent(
                source=ConvergenceSource.GROK_X_TRENDING,
                content_id=post["id"],
                title=post["text"][:100],  # First 100 chars as title
                engagement_score=engagement_score,
                viral_velocity=viral_velocity,
                topic_keywords=keywords,
                sentiment=sentiment,
                platform_specific_data={
                    "retweets": post.get("retweet_count", 0),
                    "likes": post.get("like_count", 0),
                    "replies": post.get("reply_count", 0),
                    "quotes": post.get("quote_count", 0),
                    "media_type": post.get("media_type", MediaType.NONE.value),
                    "author_followers": post.get("author_followers", 0),
                    "author_verified": post.get("author_verified", False)
                },
                detected_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error converting post to viral content: {str(e)}")
            return None
    
    def _calculate_engagement_score(self, post: Dict) -> float:
        """Calculate normalized engagement score (0-100)"""
        # Get engagement metrics
        retweets = post.get("retweet_count", 0)
        likes = post.get("like_count", 0)
        replies = post.get("reply_count", 0)
        quotes = post.get("quote_count", 0)
        
        total_engagement = retweets + likes + replies + quotes
        
        # Normalize based on follower count
        author_followers = max(post.get("author_followers", 1), 1)
        follower_ratio = total_engagement / author_followers
        
        # Weight different engagement types
        weighted_score = (
            retweets * 3 +  # Retweets have highest value
            quotes * 2.5 +  # Quotes show deep engagement
            replies * 1.5 + # Replies show discussion
            likes * 1       # Likes are easiest engagement
        ) / author_followers
        
        # Normalize to 0-100 scale
        normalized_score = min(weighted_score * 10000, 100.0)
        
        return normalized_score
    
    def _calculate_viral_velocity(self, post: Dict) -> float:
        """Calculate rate of engagement growth"""
        # In production, this would analyze engagement over time
        # For now, use a simple heuristic based on recency and engagement
        
        post_age_hours = post.get("age_hours", 24)
        total_engagement = (
            post.get("retweet_count", 0) +
            post.get("like_count", 0) +
            post.get("reply_count", 0) +
            post.get("quote_count", 0)
        )
        
        # Engagement per hour
        if post_age_hours > 0:
            engagement_per_hour = total_engagement / post_age_hours
            
            # Normalize to 0-1 scale
            # 1000+ engagements per hour = maximum velocity
            velocity = min(engagement_per_hour / 1000, 1.0)
        else:
            velocity = 0.0
        
        return velocity
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from post text"""
        # Simple keyword extraction - in production use NLP
        import re
        
        # Remove URLs and mentions
        cleaned_text = re.sub(r'http\S+|@\S+', '', text)
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        
        # Extract significant words (simple approach)
        words = cleaned_text.lower().split()
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'then', 'once', 'is', 'are', 'was', 'were', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'ought', 'used', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them',
            'their', 'this', 'that', 'these', 'those', 'what', 'which', 'who',
            'when', 'where', 'why', 'how', 'all', 'each', 'every', 'some', 'any',
            'few', 'more', 'most', 'other', 'such', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 'just', 'now'
        }
        
        keywords = []
        
        # Add hashtags first (high priority)
        keywords.extend(hashtags[:3])
        
        # Add significant words
        significant_words = [
            word for word in words
            if len(word) > 3 and word not in stop_words and word.isalpha()
        ]
        
        # Count word frequency
        word_freq = {}
        for word in significant_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and add top words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords.extend([word for word, _ in sorted_words[:5]])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:8]  # Return top 8 keywords
    
    async def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of post text"""
        # Simple sentiment analysis - in production use NLP model
        text_lower = text.lower()
        
        positive_words = {
            'amazing', 'awesome', 'excellent', 'good', 'great', 'love', 'wonderful',
            'fantastic', 'happy', 'beautiful', 'excited', 'brilliant', 'perfect',
            'best', 'win', 'success', 'congratulations', 'achievement', 'proud'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'hate', 'horrible', 'disgusting', 'ugly',
            'fail', 'failure', 'wrong', 'error', 'mistake', 'problem', 'issue',
            'crisis', 'disaster', 'unfortunate', 'sad', 'angry', 'frustrated'
        }
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _get_mock_trending_posts(self) -> List[ViralContent]:
        """Return mock trending posts for testing"""
        mock_posts = [
            ViralContent(
                source=ConvergenceSource.GROK_X_TRENDING,
                content_id="mock_1",
                title="AI is revolutionizing small business marketing - here's how",
                engagement_score=85.5,
                viral_velocity=0.75,
                topic_keywords=["ai", "marketing", "smallbusiness", "automation"],
                sentiment="positive",
                platform_specific_data={
                    "retweets": 2500,
                    "likes": 8500,
                    "replies": 450,
                    "quotes": 180,
                    "media_type": "image",
                    "author_followers": 50000,
                    "author_verified": True
                },
                detected_at=datetime.now()
            ),
            ViralContent(
                source=ConvergenceSource.GROK_X_TRENDING,
                content_id="mock_2",
                title="New Google algorithm update impacts local businesses",
                engagement_score=78.2,
                viral_velocity=0.82,
                topic_keywords=["google", "seo", "algorithm", "localbusiness"],
                sentiment="neutral",
                platform_specific_data={
                    "retweets": 1800,
                    "likes": 5200,
                    "replies": 680,
                    "quotes": 220,
                    "media_type": "none",
                    "author_followers": 25000,
                    "author_verified": False
                },
                detected_at=datetime.now()
            ),
            ViralContent(
                source=ConvergenceSource.GROK_X_TRENDING,
                content_id="mock_3",
                title="Thread: 10 ChatGPT prompts every marketer needs",
                engagement_score=92.3,
                viral_velocity=0.88,
                topic_keywords=["chatgpt", "prompts", "marketing", "ai", "thread"],
                sentiment="positive",
                platform_specific_data={
                    "retweets": 4200,
                    "likes": 12000,
                    "replies": 320,
                    "quotes": 580,
                    "media_type": "image",
                    "author_followers": 80000,
                    "author_verified": True
                },
                detected_at=datetime.now()
            )
        ]
        
        return mock_posts


async def test_grok_integration():
    """Test Grok API integration"""
    # Test with mock data (no API key)
    async with GrokIntegration() as grok:
        posts = await grok.get_trending_posts(hours=24, media_only=True)
        
        print(f"Found {len(posts)} trending posts")
        for post in posts:
            print(f"\nPost: {post.title}")
            print(f"Engagement Score: {post.engagement_score:.1f}")
            print(f"Viral Velocity: {post.viral_velocity:.2f}")
            print(f"Keywords: {', '.join(post.topic_keywords)}")
            print(f"Sentiment: {post.sentiment}")


if __name__ == "__main__":
    asyncio.run(test_grok_integration())