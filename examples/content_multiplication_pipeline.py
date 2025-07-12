"""
Example: Content Multiplication Pipeline
Shows patterns for transforming single convergence cluster into 12+ content formats.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime

class ContentFormat(Enum):
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

@dataclass
class ContentPiece:
    """Single piece of generated content"""
    format_type: ContentFormat
    title: str
    content_body: str
    hook: str
    call_to_action: str
    seo_keywords: List[str]
    hashtags: List[str]
    images_needed: List[str]  # Descriptions for image generation
    platform_specs: Dict[str, Any]  # Platform-specific requirements
    approval_status: str = "pending"
    generated_at: datetime = None

@dataclass
class ContentCluster:
    """Complete cluster of 12+ content pieces from single topic"""
    cluster_id: str
    source_topic: str
    convergence_data: Dict[str, Any]
    cia_intelligence: Dict[str, Any]
    content_pieces: List[ContentPiece]
    publishing_schedule: Dict[str, Any]
    performance_tracking: Dict[str, Any]

class ContentMultiplicationEngine:
    """Engine for generating 12+ content formats from convergence cluster"""
    
    def __init__(self):
        self.format_generators = {
            ContentFormat.AI_SEARCH_BLOG: self._generate_ai_search_blog,
            ContentFormat.EPIC_PILLAR_ARTICLE: self._generate_epic_pillar,
            ContentFormat.PILLAR_PODCAST: self._generate_pillar_podcast,
            ContentFormat.ADVERTORIAL: self._generate_advertorial,
            ContentFormat.INSTAGRAM_POST: self._generate_instagram_post,
            ContentFormat.X_THREAD: self._generate_x_thread,
            ContentFormat.LINKEDIN_ARTICLE: self._generate_linkedin_article,
            ContentFormat.META_FACEBOOK_POST: self._generate_facebook_post,
            ContentFormat.TIKTOK_UGC: self._generate_tiktok_ugc,
            ContentFormat.BLOG_SUPPORTING_1: self._generate_supporting_blog_1,
            ContentFormat.BLOG_SUPPORTING_2: self._generate_supporting_blog_2,
            ContentFormat.BLOG_SUPPORTING_3: self._generate_supporting_blog_3,
            ContentFormat.YOUTUBE_SHORTS: self._generate_youtube_shorts,
            ContentFormat.TIKTOK_SHORTS: self._generate_tiktok_shorts,
        }
    
    async def multiply_content(
        self,
        convergence_cluster: Dict[str, Any],
        cia_intelligence: Dict[str, Any],
        enabled_formats: List[ContentFormat]
    ) -> ContentCluster:
        """Generate all enabled content formats from convergence cluster"""
        
        content_pieces = []
        
        # Generate content for each enabled format
        for format_type in enabled_formats:
            if format_type in self.format_generators:
                try:
                    piece = await self.format_generators[format_type](
                        convergence_cluster, cia_intelligence
                    )
                    content_pieces.append(piece)
                except Exception as e:
                    print(f"Failed to generate {format_type}: {e}")
                    # Continue with other formats
        
        # Create content cluster
        cluster = ContentCluster(
            cluster_id=convergence_cluster["cluster_id"],
            source_topic=convergence_cluster["topic"],
            convergence_data=convergence_cluster,
            cia_intelligence=cia_intelligence,
            content_pieces=content_pieces,
            publishing_schedule=self._create_publishing_schedule(content_pieces),
            performance_tracking={}
        )
        
        return cluster
    
    async def _generate_ai_search_blog(
        self, 
        convergence_cluster: Dict[str, Any], 
        cia_intelligence: Dict[str, Any]
    ) -> ContentPiece:
        """Generate AI Search optimized blog post for ChatGPT/Perplexity discovery"""
        
        topic = convergence_cluster["topic"]
        keywords = convergence_cluster["seo_keywords"]
        viral_hooks = convergence_cluster["content_opportunity"]["hook_opportunities"]
        
        # Build context for AI search optimization
        context = {
            "topic": topic,
            "target_keywords": keywords,
            "viral_hooks": viral_hooks,
            "customer_psychology": cia_intelligence["customer_psychology"],
            "authority_positioning": cia_intelligence["authority_positioning"],
            "search_intent": "informational_with_commercial_angle"
        }
        
        # Generate optimized content
        content = await self._claude_generate_content(
            template="ai_search_blog_template",
            context=context,
            requirements={
                "word_count": "1500-2000",
                "keyword_density": "1-2%",
                "ai_search_phrases": ["according to experts", "research shows", "best practices include"],
                "authority_signals": cia_intelligence["authority_positioning"]["expertise_areas"],
                "conversational_tone": True
            }
        )
        
        return ContentPiece(
            format_type=ContentFormat.AI_SEARCH_BLOG,
            title=content["title"],
            content_body=content["body"],
            hook=viral_hooks[0] if viral_hooks else content["hook"],
            call_to_action=content["cta"],
            seo_keywords=keywords[:5],
            hashtags=[],  # Not applicable for blog
            images_needed=content["image_descriptions"],
            platform_specs={
                "optimization": "ai_search",
                "internal_links": content["internal_link_opportunities"],
                "meta_description": content["meta_description"],
                "schema_markup": "article"
            }
        )
    
    async def _generate_epic_pillar(
        self, 
        convergence_cluster: Dict[str, Any], 
        cia_intelligence: Dict[str, Any]
    ) -> ContentPiece:
        """Generate comprehensive pillar article (3000+ words)"""
        
        topic = convergence_cluster["topic"]
        
        context = {
            "topic": topic,
            "depth_level": "comprehensive",
            "authority_framework": cia_intelligence["authority_positioning"],
            "competitive_insights": cia_intelligence["competitive_analysis"],
            "customer_journey": cia_intelligence["customer_psychology"]["journey_stages"]
        }
        
        content = await self._claude_generate_content(
            template="epic_pillar_template",
            context=context,
            requirements={
                "word_count": "3000-5000",
                "sections": ["introduction", "problem_analysis", "solution_framework", "implementation", "case_studies", "conclusion"],
                "authority_signals": "maximum",
                "internal_linking": "comprehensive",
                "actionable_takeaways": "minimum_10"
            }
        )
        
        return ContentPiece(
            format_type=ContentFormat.EPIC_PILLAR_ARTICLE,
            title=content["title"],
            content_body=content["body"],
            hook=content["hook"],
            call_to_action=content["cta"],
            seo_keywords=convergence_cluster["seo_keywords"],
            hashtags=[],
            images_needed=content["image_descriptions"],
            platform_specs={
                "table_of_contents": content["toc"],
                "reading_time": content["estimated_reading_time"],
                "related_articles": content["related_content_opportunities"],
                "downloadable_resources": content["lead_magnets"]
            }
        )
    
    async def _generate_instagram_post(
        self, 
        convergence_cluster: Dict[str, Any], 
        cia_intelligence: Dict[str, Any]
    ) -> ContentPiece:
        """Generate Instagram post with carousel potential"""
        
        viral_hooks = convergence_cluster["content_opportunity"]["hook_opportunities"]
        emotional_drivers = convergence_cluster["content_opportunity"]["target_emotions"]
        
        context = {
            "viral_hooks": viral_hooks,
            "emotional_drivers": emotional_drivers,
            "brand_voice": cia_intelligence["brand_voice"],
            "visual_style": cia_intelligence.get("visual_preferences", {})
        }
        
        content = await self._claude_generate_content(
            template="instagram_post_template",
            context=context,
            requirements={
                "character_limit": 2200,
                "carousel_slides": "3-5",
                "hashtag_count": "20-30",
                "call_to_action": "story_or_comment",
                "visual_elements": "required"
            }
        )
        
        return ContentPiece(
            format_type=ContentFormat.INSTAGRAM_POST,
            title=content["title"],
            content_body=content["body"],
            hook=viral_hooks[0] if viral_hooks else content["hook"],
            call_to_action=content["cta"],
            seo_keywords=[],  # Not applicable
            hashtags=content["hashtags"],
            images_needed=content["carousel_images"],
            platform_specs={
                "carousel_count": content["slide_count"],
                "optimal_posting_time": "6-9 PM",
                "engagement_strategy": content["engagement_hooks"],
                "story_integration": content["story_followup"]
            }
        )
    
    async def _generate_x_thread(
        self, 
        convergence_cluster: Dict[str, Any], 
        cia_intelligence: Dict[str, Any]
    ) -> ContentPiece:
        """Generate X (Twitter) thread optimized for engagement"""
        
        topic = convergence_cluster["topic"]
        viral_velocity = convergence_cluster.get("viral_velocity", 0)
        
        context = {
            "topic": topic,
            "viral_potential": viral_velocity,
            "authority_signals": cia_intelligence["authority_positioning"],
            "trending_context": convergence_cluster["trend_momentum"]
        }
        
        content = await self._claude_generate_content(
            template="x_thread_template",
            context=context,
            requirements={
                "thread_length": "8-12 tweets",
                "character_limit_per_tweet": 280,
                "hook_tweet": "pattern_interrupt",
                "engagement_hooks": "questions_and_cliffhangers",
                "authority_positioning": "subtle"
            }
        )
        
        return ContentPiece(
            format_type=ContentFormat.X_THREAD,
            title=content["thread_topic"],
            content_body=content["thread_tweets"],
            hook=content["hook_tweet"],
            call_to_action=content["final_cta"],
            seo_keywords=[],
            hashtags=content["hashtags"],
            images_needed=content["visual_elements"],
            platform_specs={
                "tweet_count": content["thread_length"],
                "optimal_timing": "9-10 AM or 7-9 PM",
                "engagement_strategy": content["reply_strategy"],
                "retweet_hooks": content["shareability_elements"]
            }
        )
    
    async def _generate_tiktok_ugc(
        self, 
        convergence_cluster: Dict[str, Any], 
        cia_intelligence: Dict[str, Any]
    ) -> ContentPiece:
        """Generate TikTok UGC-style content script"""
        
        emotional_drivers = convergence_cluster["content_opportunity"]["target_emotions"]
        viral_hooks = convergence_cluster["content_opportunity"]["hook_opportunities"]
        
        context = {
            "emotional_drivers": emotional_drivers,
            "viral_hooks": viral_hooks,
            "ugc_style": "authentic_recommendation",
            "target_demo": cia_intelligence["target_audience"]
        }
        
        content = await self._claude_generate_content(
            template="tiktok_ugc_template",
            context=context,
            requirements={
                "video_length": "15-30 seconds",
                "hook_duration": "3 seconds",
                "story_arc": "problem_agitation_solution",
                "authenticity_level": "high",
                "trending_sounds": "optional"
            }
        )
        
        return ContentPiece(
            format_type=ContentFormat.TIKTOK_UGC,
            title=content["video_concept"],
            content_body=content["script"],
            hook=content["opening_hook"],
            call_to_action=content["cta"],
            seo_keywords=[],
            hashtags=content["hashtags"],
            images_needed=content["visual_elements"],
            platform_specs={
                "video_duration": content["duration"],
                "trending_sounds": content["sound_recommendations"],
                "visual_style": "ugc_authentic",
                "captions": content["on_screen_text"]
            }
        )
    
    def _create_publishing_schedule(self, content_pieces: List[ContentPiece]) -> Dict[str, Any]:
        """Create optimal publishing schedule for content cluster"""
        
        # Priority order for publishing
        priority_order = [
            ContentFormat.AI_SEARCH_BLOG,  # Published first for SEO foundation
            ContentFormat.EPIC_PILLAR_ARTICLE,  # Core authority piece
            ContentFormat.LINKEDIN_ARTICLE,  # Professional network
            ContentFormat.X_THREAD,  # Quick viral potential
            ContentFormat.INSTAGRAM_POST,  # Visual engagement
            ContentFormat.TIKTOK_UGC,  # Viral amplification
            ContentFormat.META_FACEBOOK_POST,  # Broad reach
            ContentFormat.YOUTUBE_SHORTS,  # Video discovery
            ContentFormat.BLOG_SUPPORTING_1,  # SEO support
            ContentFormat.BLOG_SUPPORTING_2,  # SEO support
            ContentFormat.BLOG_SUPPORTING_3,  # SEO support
        ]
        
        schedule = {}
        day_counter = 0
        
        for piece in content_pieces:
            if piece.format_type in priority_order:
                priority_index = priority_order.index(piece.format_type)
                # Spread content over multiple days based on priority
                publish_day = priority_index // 2  # 2 pieces per day max
                
                schedule[f"day_{publish_day + 1}"] = schedule.get(f"day_{publish_day + 1}", [])
                schedule[f"day_{publish_day + 1}"].append({
                    "content_id": piece.format_type.value,
                    "title": piece.title,
                    "platform": self._get_platform_for_format(piece.format_type),
                    "optimal_time": self._get_optimal_posting_time(piece.format_type)
                })
        
        return schedule
    
    def _get_platform_for_format(self, format_type: ContentFormat) -> str:
        """Map content format to publishing platform"""
        platform_mapping = {
            ContentFormat.AI_SEARCH_BLOG: "blog",
            ContentFormat.EPIC_PILLAR_ARTICLE: "blog",
            ContentFormat.INSTAGRAM_POST: "instagram",
            ContentFormat.X_THREAD: "x_twitter",
            ContentFormat.LINKEDIN_ARTICLE: "linkedin",
            ContentFormat.META_FACEBOOK_POST: "facebook",
            ContentFormat.TIKTOK_UGC: "tiktok",
            ContentFormat.YOUTUBE_SHORTS: "youtube",
            ContentFormat.BLOG_SUPPORTING_1: "blog",
            ContentFormat.BLOG_SUPPORTING_2: "blog",
            ContentFormat.BLOG_SUPPORTING_3: "blog",
        }
        return platform_mapping.get(format_type, "blog")
    
    async def _claude_generate_content(
        self, 
        template: str, 
        context: Dict[str, Any], 
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content using Claude with specific template and requirements"""
        
        # This would integrate with Claude API for actual content generation
        # Mock implementation for example
        return {
            "title": f"Generated title for {context.get('topic', 'content')}",
            "body": f"Generated content body based on {template}",
            "hook": f"Hook based on {context.get('viral_hooks', ['generic'])[0]}",
            "cta": "Learn more about our solutions",
            "image_descriptions": ["Hero image", "Supporting graphic"],
            "hashtags": ["#marketing", "#business", "#growth"],
            "meta_description": "Meta description for SEO",
            "internal_link_opportunities": ["related-article-1", "related-article-2"]
        }

# Example usage pattern:
async def run_content_multiplication(convergence_cluster: Dict, cia_intelligence: Dict, client_config: Dict):
    """Example of complete content multiplication workflow"""
    
    engine = ContentMultiplicationEngine()
    
    # Get enabled formats from client configuration
    enabled_formats = []
    for format_name, enabled in client_config.get("content_formats", {}).items():
        if enabled:
            try:
                format_enum = ContentFormat(format_name)
                enabled_formats.append(format_enum)
            except ValueError:
                continue
    
    # Generate content cluster
    content_cluster = await engine.multiply_content(
        convergence_cluster, cia_intelligence, enabled_formats
    )
    
    return content_cluster
