"""
Reddit MCP Integration for viral content analysis
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass

from ..database.cartwheel_models import ViralContent, ConvergenceSource

logger = logging.getLogger(__name__)

# Reddit configuration
TRENDING_SUBREDDITS = [
    "marketing", "entrepreneur", "business", "startups",
    "socialmedia", "contentmarketing", "digitalmarketing",
    "smallbusiness", "ecommerce", "growmybusiness",
    "sales", "b2bmarketing", "marketingautomation"
]

VIRAL_THRESHOLDS = {
    "min_upvotes": 100,
    "min_comments": 20,
    "min_upvote_ratio": 0.8,
    "min_awards": 1
}


@dataclass
class RedditPost:
    """Reddit post data structure"""
    id: str
    title: str
    selftext: str
    subreddit: str
    ups: int
    num_comments: int
    upvote_ratio: float
    total_awards_received: int
    created_utc: float
    author: str
    is_video: bool
    is_self: bool
    link_flair_text: Optional[str]


class RedditMCP:
    """Reddit MCP integration for viral content analysis"""
    
    def __init__(self, mcp_endpoint: Optional[str] = None):
        self.mcp_endpoint = mcp_endpoint
        self.trending_subreddits = TRENDING_SUBREDDITS
        self.viral_thresholds = VIRAL_THRESHOLDS
    
    async def get_viral_posts(
        self, hours: int = 24, subreddits: Optional[List[str]] = None
    ) -> List[ViralContent]:
        """
        Get viral posts from relevant marketing subreddits
        
        Args:
            hours: Timeframe to check (default 24)
            subreddits: Optional list of specific subreddits
            
        Returns:
            List of viral content from Reddit
        """
        if not self.mcp_endpoint:
            logger.info("Reddit MCP not configured, using mock data")
            return self._get_mock_viral_posts()
        
        subreddits_to_check = subreddits or self.trending_subreddits
        viral_content = []
        
        for subreddit in subreddits_to_check:
            try:
                posts = await self._get_subreddit_hot_posts(subreddit, hours)
                
                for post in posts:
                    if self._meets_viral_criteria(post):
                        content = await self._post_to_viral_content(post)
                        if content:
                            viral_content.append(content)
                            
            except Exception as e:
                logger.error(f"Error fetching posts from r/{subreddit}: {str(e)}")
                continue
        
        logger.info(f"Found {len(viral_content)} viral posts across {len(subreddits_to_check)} subreddits")
        return viral_content
    
    async def _get_subreddit_hot_posts(
        self, subreddit: str, hours: int
    ) -> List[RedditPost]:
        """Get hot posts from a specific subreddit"""
        # In production, this would call the Reddit MCP endpoint
        # For now, return empty list when not mocked
        return []
    
    def _meets_viral_criteria(self, post: RedditPost) -> bool:
        """Check if post meets viral content criteria"""
        return (
            post.ups >= self.viral_thresholds["min_upvotes"] and
            post.num_comments >= self.viral_thresholds["min_comments"] and
            post.upvote_ratio >= self.viral_thresholds["min_upvote_ratio"]
        )
    
    async def _post_to_viral_content(self, post: RedditPost) -> Optional[ViralContent]:
        """Convert Reddit post to ViralContent"""
        try:
            # Combine title and selftext for keyword extraction
            full_text = f"{post.title} {post.selftext}"
            keywords = await self._extract_keywords(full_text)
            
            # Analyze sentiment
            sentiment = await self._analyze_sentiment(full_text)
            
            # Calculate scores
            engagement_score = self._calculate_reddit_score(post)
            viral_velocity = self._calculate_velocity(post)
            
            return ViralContent(
                source=ConvergenceSource.REDDIT_VIRAL,
                content_id=post.id,
                title=post.title,
                engagement_score=engagement_score,
                viral_velocity=viral_velocity,
                topic_keywords=keywords,
                sentiment=sentiment,
                platform_specific_data={
                    "subreddit": post.subreddit,
                    "upvotes": post.ups,
                    "comments": post.num_comments,
                    "upvote_ratio": post.upvote_ratio,
                    "awards": post.total_awards_received,
                    "is_self_post": post.is_self,
                    "flair": post.link_flair_text,
                    "author": post.author
                },
                detected_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error converting Reddit post to viral content: {str(e)}")
            return None
    
    def _calculate_reddit_score(self, post: RedditPost) -> float:
        """Calculate normalized engagement score for Reddit post"""
        # Base score from upvotes
        upvote_score = min(post.ups / 1000 * 20, 40)  # Max 40 points
        
        # Comment engagement score
        comment_score = min(post.num_comments / 100 * 15, 30)  # Max 30 points
        
        # Upvote ratio bonus
        ratio_bonus = (post.upvote_ratio - 0.5) * 20  # Max 10 points
        
        # Award bonus
        award_bonus = min(post.total_awards_received * 5, 20)  # Max 20 points
        
        total_score = upvote_score + comment_score + ratio_bonus + award_bonus
        
        return min(total_score, 100.0)
    
    def _calculate_velocity(self, post: RedditPost) -> float:
        """Calculate viral velocity based on age and engagement"""
        # Calculate post age in hours
        post_age_hours = (datetime.now().timestamp() - post.created_utc) / 3600
        
        if post_age_hours <= 0:
            return 0.0
        
        # Engagement per hour
        engagement_rate = (post.ups + post.num_comments * 2) / post_age_hours
        
        # Normalize to 0-1 scale
        # 500+ engagement per hour = maximum velocity
        velocity = min(engagement_rate / 500, 1.0)
        
        # Boost for very new posts with high engagement
        if post_age_hours < 6 and engagement_rate > 100:
            velocity = min(velocity * 1.2, 1.0)
        
        return velocity
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from Reddit post text"""
        import re
        
        # Clean text
        text_lower = text.lower()
        
        # Common Reddit-specific terms to exclude
        reddit_stop_words = {
            'reddit', 'redditor', 'upvote', 'downvote', 'comment', 'post',
            'edit', 'update', 'tldr', 'ama', 'eli5', 'til', 'lpt',
            'anyone', 'else', 'thoughts', 'advice', 'question', 'help'
        }
        
        # General stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'then', 'once', 'is', 'are', 'was', 'were', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare'
        }
        
        all_stop_words = stop_words | reddit_stop_words
        
        # Extract words
        words = re.findall(r'\b[a-z]+\b', text_lower)
        
        # Filter and count
        word_freq = {}
        for word in words:
            if len(word) > 3 and word not in all_stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top keywords
        keywords = [word for word, _ in sorted_words[:10]]
        
        # Look for common marketing/business terms
        priority_terms = {
            'marketing', 'growth', 'strategy', 'content', 'social', 'media',
            'business', 'startup', 'entrepreneur', 'sales', 'customer',
            'brand', 'digital', 'automation', 'campaign', 'audience',
            'engagement', 'conversion', 'analytics', 'roi', 'lead'
        }
        
        # Prioritize marketing terms
        priority_keywords = [k for k in keywords if k in priority_terms]
        other_keywords = [k for k in keywords if k not in priority_terms]
        
        return (priority_keywords + other_keywords)[:8]
    
    async def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of Reddit post"""
        text_lower = text.lower()
        
        # Reddit-specific positive indicators
        positive_indicators = {
            'amazing', 'awesome', 'excellent', 'love', 'fantastic', 'brilliant',
            'helpful', 'thanks', 'grateful', 'success', 'working', 'solved',
            'recommend', 'best', 'great', 'good', 'useful', 'valuable'
        }
        
        # Reddit-specific negative indicators
        negative_indicators = {
            'hate', 'terrible', 'awful', 'waste', 'scam', 'avoid', 'warning',
            'failed', 'broken', 'disappointed', 'frustrating', 'useless',
            'problem', 'issue', 'bug', 'error', 'wrong', 'bad'
        }
        
        # Count occurrences
        positive_count = sum(1 for word in positive_indicators if word in text_lower)
        negative_count = sum(1 for word in negative_indicators if word in text_lower)
        
        # Check for question posts (often neutral)
        if '?' in text and text.strip().endswith('?'):
            if positive_count == 0 and negative_count == 0:
                return "neutral"
        
        if positive_count > negative_count + 1:
            return "positive"
        elif negative_count > positive_count + 1:
            return "negative"
        else:
            return "neutral"
    
    def _get_mock_viral_posts(self) -> List[ViralContent]:
        """Return mock viral Reddit posts for testing"""
        mock_posts = [
            ViralContent(
                source=ConvergenceSource.REDDIT_VIRAL,
                content_id="reddit_mock_1",
                title="How I grew my agency from 0 to $50k MRR using AI automation",
                engagement_score=88.5,
                viral_velocity=0.72,
                topic_keywords=["agency", "growth", "mrr", "ai", "automation", "revenue"],
                sentiment="positive",
                platform_specific_data={
                    "subreddit": "entrepreneur",
                    "upvotes": 842,
                    "comments": 156,
                    "upvote_ratio": 0.92,
                    "awards": 3,
                    "is_self_post": True,
                    "flair": "Success Story",
                    "author": "startup_founder"
                },
                detected_at=datetime.now()
            ),
            ViralContent(
                source=ConvergenceSource.REDDIT_VIRAL,
                content_id="reddit_mock_2",
                title="Warning: New Google Ads policy changes affecting small businesses",
                engagement_score=76.3,
                viral_velocity=0.85,
                topic_keywords=["google", "ads", "policy", "warning", "business", "changes"],
                sentiment="negative",
                platform_specific_data={
                    "subreddit": "marketing",
                    "upvotes": 523,
                    "comments": 89,
                    "upvote_ratio": 0.88,
                    "awards": 1,
                    "is_self_post": True,
                    "flair": "News",
                    "author": "digital_marketer"
                },
                detected_at=datetime.now()
            ),
            ViralContent(
                source=ConvergenceSource.REDDIT_VIRAL,
                content_id="reddit_mock_3",
                title="The complete guide to content repurposing - Turn 1 piece into 20",
                engagement_score=82.7,
                viral_velocity=0.68,
                topic_keywords=["content", "repurposing", "guide", "strategy", "marketing"],
                sentiment="positive",
                platform_specific_data={
                    "subreddit": "contentmarketing",
                    "upvotes": 687,
                    "comments": 124,
                    "upvote_ratio": 0.94,
                    "awards": 2,
                    "is_self_post": True,
                    "flair": "Guide",
                    "author": "content_strategist"
                },
                detected_at=datetime.now()
            ),
            ViralContent(
                source=ConvergenceSource.REDDIT_VIRAL,
                content_id="reddit_mock_4",
                title="What marketing automation tools are actually worth it in 2025?",
                engagement_score=79.2,
                viral_velocity=0.78,
                topic_keywords=["marketing", "automation", "tools", "software", "2025"],
                sentiment="neutral",
                platform_specific_data={
                    "subreddit": "smallbusiness",
                    "upvotes": 412,
                    "comments": 187,
                    "upvote_ratio": 0.85,
                    "awards": 1,
                    "is_self_post": True,
                    "flair": "Question",
                    "author": "small_biz_owner"
                },
                detected_at=datetime.now()
            )
        ]
        
        return mock_posts


async def test_reddit_integration():
    """Test Reddit MCP integration"""
    reddit = RedditMCP()
    
    # Test with mock data
    posts = await reddit.get_viral_posts(hours=24)
    
    print(f"Found {len(posts)} viral Reddit posts")
    for post in posts:
        print(f"\nPost: {post.title}")
        print(f"Subreddit: r/{post.platform_specific_data['subreddit']}")
        print(f"Engagement Score: {post.engagement_score:.1f}")
        print(f"Viral Velocity: {post.viral_velocity:.2f}")
        print(f"Keywords: {', '.join(post.topic_keywords)}")
        print(f"Sentiment: {post.sentiment}")


if __name__ == "__main__":
    asyncio.run(test_reddit_integration())