"""
Cartwheel Content Multiplication Engine
Generates 12+ content formats from convergence opportunities
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from uuid import uuid4
import asyncio
import logging

from ..database.cartwheel_models import (
    ContentFormat, ContentPiece, ContentCluster,
    ConvergenceOpportunity, ApprovalStatus, PublishingStatus,
    CONTENT_FORMAT_SPECS, is_blog_format, is_social_format
)
from ..cia.claude_client import ClaudeClient
from ..database.cartwheel_repository import CartwheelRepository

logger = logging.getLogger(__name__)


class ContentMultiplier:
    """Engine for multiplying content across 12+ formats"""
    
    def __init__(
        self,
        claude_client: Optional[ClaudeClient] = None,
        repository: Optional[CartwheelRepository] = None
    ):
        self.claude = claude_client or ClaudeClient()
        self.repository = repository
        self.format_generators = self._initialize_generators()
    
    def _initialize_generators(self) -> Dict[ContentFormat, Any]:
        """Initialize format-specific generators"""
        return {
            ContentFormat.AI_SEARCH_BLOG: self._generate_ai_search_blog,
            ContentFormat.EPIC_PILLAR_ARTICLE: self._generate_epic_pillar,
            ContentFormat.PILLAR_PODCAST: self._generate_podcast_script,
            ContentFormat.ADVERTORIAL: self._generate_advertorial,
            ContentFormat.INSTAGRAM_POST: self._generate_instagram_post,
            ContentFormat.X_THREAD: self._generate_x_thread,
            ContentFormat.LINKEDIN_ARTICLE: self._generate_linkedin_article,
            ContentFormat.META_FACEBOOK_POST: self._generate_facebook_post,
            ContentFormat.TIKTOK_UGC: self._generate_tiktok_script,
            ContentFormat.BLOG_SUPPORTING_1: self._generate_supporting_blog,
            ContentFormat.BLOG_SUPPORTING_2: self._generate_supporting_blog,
            ContentFormat.BLOG_SUPPORTING_3: self._generate_supporting_blog,
            ContentFormat.YOUTUBE_SHORTS: self._generate_youtube_shorts,
            ContentFormat.TIKTOK_SHORTS: self._generate_tiktok_shorts
        }
    
    async def generate_content_cluster(
        self,
        opportunity: ConvergenceOpportunity,
        cia_intelligence: Dict[str, Any],
        client_config: Dict[str, Any]
    ) -> ContentCluster:
        """
        Generate complete content cluster from convergence opportunity
        
        Args:
            opportunity: Convergence opportunity to build from
            cia_intelligence: CIA analysis data for context
            client_config: Client configuration and preferences
            
        Returns:
            ContentCluster with all generated content pieces
        """
        try:
            # Get enabled content formats
            enabled_formats = self._get_enabled_formats(client_config, opportunity)
            
            logger.info(
                f"Generating content cluster for topic: {opportunity.topic} "
                f"with {len(enabled_formats)} formats"
            )
            
            # Build generation context
            generation_context = self._build_generation_context(
                opportunity, cia_intelligence, client_config
            )
            
            # Generate content pieces
            content_pieces = await self._generate_all_content(
                enabled_formats, generation_context
            )
            
            # Create content cluster
            cluster = ContentCluster(
                id=str(uuid4()),
                client_id=opportunity.client_id,
                convergence_id=opportunity.id,
                cluster_topic=opportunity.topic,
                cia_intelligence_summary=self._extract_intelligence_summary(cia_intelligence),
                content_piece_ids=[piece.id for piece in content_pieces],
                publishing_schedule=self._create_publishing_schedule(content_pieces, client_config),
                approval_status="pending",
                created_at=datetime.now()
            )
            
            # Save to database if repository available
            if self.repository:
                cluster = await self.repository.create_content_cluster(cluster)
                
                # Save content pieces
                for piece in content_pieces:
                    piece.cluster_id = cluster.id
                    piece.client_id = cluster.client_id
                    await self.repository.save_content_piece(piece)
            
            logger.info(f"Generated content cluster with {len(content_pieces)} pieces")
            return cluster
            
        except Exception as e:
            logger.error(f"Error generating content cluster: {str(e)}")
            raise
    
    def _get_enabled_formats(
        self,
        client_config: Dict[str, Any],
        opportunity: ConvergenceOpportunity
    ) -> List[ContentFormat]:
        """Get enabled content formats based on config and opportunity"""
        # Start with client's enabled formats
        enabled_formats = client_config.get("enabled_content_formats", [])
        
        # If none specified, use recommended formats
        if not enabled_formats:
            enabled_formats = opportunity.recommended_formats
        
        # Convert strings to ContentFormat enums
        format_enums = []
        for format_str in enabled_formats:
            try:
                format_enums.append(ContentFormat(format_str))
            except ValueError:
                logger.warning(f"Unknown content format: {format_str}")
        
        # Apply convergence score filters
        if opportunity.convergence_score < 70:
            # Lower scores get fewer formats
            format_enums = [f for f in format_enums if is_blog_format(f)][:3]
        
        return format_enums
    
    def _build_generation_context(
        self,
        opportunity: ConvergenceOpportunity,
        cia_intelligence: Dict[str, Any],
        client_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build comprehensive context for content generation"""
        return {
            # Convergence data
            "topic": opportunity.topic,
            "viral_hooks": opportunity.content_opportunity.get("hook_opportunities", []),
            "content_angles": opportunity.content_opportunity.get("angle_variations", []),
            "emotional_drivers": opportunity.content_opportunity.get("target_emotions", []),
            "seo_keywords": opportunity.seo_keywords,
            "urgency": opportunity.urgency_level,
            
            # CIA intelligence
            "customer_psychology": cia_intelligence.get("customer_psychology", {}),
            "pain_points": cia_intelligence.get("pain_points", []),
            "authority_positioning": cia_intelligence.get("authority_positioning", {}),
            "competitive_insights": cia_intelligence.get("competitive_analysis", {}),
            "service_offerings": cia_intelligence.get("service_offerings", []),
            "unique_value_props": cia_intelligence.get("unique_value_propositions", []),
            
            # Client configuration
            "brand_voice": client_config.get("brand_voice", {}),
            "target_audience": client_config.get("target_audience", {}),
            "content_guidelines": client_config.get("content_guidelines", {}),
            "visual_style": client_config.get("visual_style", {}),
            "cta_preferences": client_config.get("cta_preferences", {})
        }
    
    async def _generate_all_content(
        self,
        formats: List[ContentFormat],
        context: Dict[str, Any]
    ) -> List[ContentPiece]:
        """Generate content for all enabled formats"""
        content_pieces = []
        
        # Generate content concurrently for efficiency
        tasks = []
        for format_type in formats:
            if format_type in self.format_generators:
                task = self._generate_content_piece(format_type, context)
                tasks.append(task)
        
        # Wait for all generation to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error generating {formats[i].value}: {str(result)}")
            elif result:
                content_pieces.append(result)
        
        return content_pieces
    
    async def _generate_content_piece(
        self,
        format_type: ContentFormat,
        context: Dict[str, Any]
    ) -> Optional[ContentPiece]:
        """Generate a single content piece"""
        try:
            generator = self.format_generators.get(format_type)
            if not generator:
                logger.warning(f"No generator for format: {format_type.value}")
                return None
            
            return await generator(context)
            
        except Exception as e:
            logger.error(f"Error generating {format_type.value}: {str(e)}")
            return None
    
    async def _generate_ai_search_blog(self, context: Dict[str, Any]) -> ContentPiece:
        """Generate AI Search optimized blog post"""
        prompt = self._build_ai_search_prompt(context)
        
        content_result, token_usage = await self.claude.complete(
            prompt=prompt,
            max_tokens=4096
        )
        
        # Parse generated content
        parsed = self._parse_generated_content(content_result)
        
        return ContentPiece(
            id=str(uuid4()),
            cluster_id="",  # Set by parent
            client_id="",   # Set by parent
            format_type=ContentFormat.AI_SEARCH_BLOG,
            title=parsed.get("title", f"AI Search: {context['topic']}"),
            content_body=parsed.get("body", ""),
            hook=parsed.get("hook", context.get("viral_hooks", [""])[0]),
            call_to_action=parsed.get("cta", "Learn more about our solutions"),
            seo_keywords=context["seo_keywords"][:5],
            hashtags=[],
            images_needed=parsed.get("image_descriptions", [
                "Hero image showing the main concept",
                "Supporting visual for key point 1",
                "Infographic summarizing benefits"
            ]),
            platform_specs={
                "optimization_type": "ai_search",
                "word_count": len(parsed.get("body", "").split()),
                "reading_time": self._calculate_reading_time(parsed.get("body", "")),
                "internal_links": parsed.get("internal_links", []),
                "meta_description": parsed.get("meta_description", "")
            },
            approval_status=ApprovalStatus.PENDING,
            publishing_status=PublishingStatus.PENDING,
            created_at=datetime.now()
        )
    
    async def _generate_epic_pillar(self, context: Dict[str, Any]) -> ContentPiece:
        """Generate epic pillar article (3000+ words)"""
        prompt = self._build_epic_pillar_prompt(context)
        
        content_result, token_usage = await self.claude.complete(
            prompt=prompt,
            max_tokens=8192  # Larger token limit for longer content
        )
        
        parsed = self._parse_generated_content(content_result)
        
        return ContentPiece(
            id=str(uuid4()),
            cluster_id="",
            client_id="",
            format_type=ContentFormat.EPIC_PILLAR_ARTICLE,
            title=parsed.get("title", f"The Ultimate Guide to {context['topic']}"),
            content_body=parsed.get("body", ""),
            hook=parsed.get("hook", ""),
            call_to_action=parsed.get("cta", ""),
            seo_keywords=context["seo_keywords"][:8],
            hashtags=[],
            images_needed=parsed.get("image_descriptions", [
                "Hero image",
                "Section 1 visual",
                "Section 2 visual", 
                "Data visualization",
                "Summary infographic"
            ]),
            platform_specs={
                "word_count": len(parsed.get("body", "").split()),
                "sections": parsed.get("sections", []),
                "table_of_contents": parsed.get("toc", []),
                "downloadable_resource": parsed.get("lead_magnet", "")
            },
            approval_status=ApprovalStatus.PENDING,
            publishing_status=PublishingStatus.PENDING,
            created_at=datetime.now()
        )
    
    async def _generate_instagram_post(self, context: Dict[str, Any]) -> ContentPiece:
        """Generate Instagram post with caption"""
        prompt = self._build_instagram_prompt(context)
        
        content_result, token_usage = await self.claude.complete(
            prompt=prompt,
            max_tokens=1024
        )
        
        parsed = self._parse_generated_content(content_result)
        
        # Generate hashtags
        hashtags = self._generate_hashtags(context, platform="instagram")
        
        return ContentPiece(
            id=str(uuid4()),
            cluster_id="",
            client_id="",
            format_type=ContentFormat.INSTAGRAM_POST,
            title=f"IG: {context['topic'][:50]}",
            content_body=parsed.get("caption", ""),
            hook=parsed.get("hook", ""),
            call_to_action=parsed.get("cta", "Link in bio! 🔗"),
            seo_keywords=[],  # Not applicable for Instagram
            hashtags=hashtags[:30],  # Instagram limit
            images_needed=[parsed.get("image_description", f"Visual representation of {context['topic']}")],
            platform_specs={
                "character_count": len(parsed.get("caption", "")),
                "emoji_count": self._count_emojis(parsed.get("caption", "")),
                "posting_time": self._suggest_posting_time("instagram", context)
            },
            approval_status=ApprovalStatus.PENDING,
            publishing_status=PublishingStatus.PENDING,
            created_at=datetime.now()
        )
    
    async def _generate_x_thread(self, context: Dict[str, Any]) -> ContentPiece:
        """Generate X (Twitter) thread"""
        prompt = self._build_x_thread_prompt(context)
        
        content_result, token_usage = await self.claude.complete(
            prompt=prompt,
            max_tokens=2048
        )
        
        parsed = self._parse_generated_content(content_result)
        tweets = parsed.get("tweets", [])
        
        # Ensure each tweet is under 280 chars
        validated_tweets = [self._truncate_tweet(tweet) for tweet in tweets[:10]]
        
        return ContentPiece(
            id=str(uuid4()),
            cluster_id="",
            client_id="",
            format_type=ContentFormat.X_THREAD,
            title=f"Thread: {context['topic'][:50]}",
            content_body="\n\n".join(validated_tweets),
            hook=validated_tweets[0] if validated_tweets else "",
            call_to_action=parsed.get("cta", "What are your thoughts? 👇"),
            seo_keywords=[],
            hashtags=self._generate_hashtags(context, platform="x")[:5],
            images_needed=[],  # Optional for threads
            platform_specs={
                "tweet_count": len(validated_tweets),
                "thread_structure": parsed.get("thread_structure", []),
                "engagement_hooks": parsed.get("engagement_hooks", [])
            },
            approval_status=ApprovalStatus.PENDING,
            publishing_status=PublishingStatus.PENDING,
            created_at=datetime.now()
        )
    
    async def _generate_linkedin_article(self, context: Dict[str, Any]) -> ContentPiece:
        """Generate LinkedIn article"""
        prompt = self._build_linkedin_prompt(context)
        
        content_result, token_usage = await self.claude.complete(
            prompt=prompt,
            max_tokens=4096
        )
        
        parsed = self._parse_generated_content(content_result)
        
        return ContentPiece(
            id=str(uuid4()),
            cluster_id="",
            client_id="",
            format_type=ContentFormat.LINKEDIN_ARTICLE,
            title=parsed.get("title", ""),
            content_body=parsed.get("body", ""),
            hook=parsed.get("hook", ""),
            call_to_action=parsed.get("cta", "What's been your experience? Share in the comments."),
            seo_keywords=context["seo_keywords"][:3],
            hashtags=self._generate_hashtags(context, platform="linkedin")[:5],
            images_needed=parsed.get("image_descriptions", [
                "Professional header image",
                "Supporting data visualization"
            ]),
            platform_specs={
                "word_count": len(parsed.get("body", "").split()),
                "professional_tone_score": parsed.get("tone_score", 0.8),
                "industry_keywords": parsed.get("industry_keywords", [])
            },
            approval_status=ApprovalStatus.PENDING,
            publishing_status=PublishingStatus.PENDING,
            created_at=datetime.now()
        )
    
    async def _generate_podcast_script(self, context: Dict[str, Any]) -> ContentPiece:
        """Generate podcast script"""
        prompt = self._build_podcast_prompt(context)
        
        content_result, token_usage = await self.claude.complete(
            prompt=prompt,
            max_tokens=6144
        )
        
        parsed = self._parse_generated_content(content_result)
        
        return ContentPiece(
            id=str(uuid4()),
            cluster_id="",
            client_id="",
            format_type=ContentFormat.PILLAR_PODCAST,
            title=parsed.get("episode_title", ""),
            content_body=parsed.get("script", ""),
            hook=parsed.get("intro_hook", ""),
            call_to_action=parsed.get("outro_cta", ""),
            seo_keywords=context["seo_keywords"][:5],
            hashtags=[],
            images_needed=[
                "Episode cover art",
                "Audiogram visual"
            ],
            platform_specs={
                "duration_estimate": parsed.get("duration_minutes", 20),
                "segment_breakdown": parsed.get("segments", []),
                "key_talking_points": parsed.get("talking_points", []),
                "show_notes": parsed.get("show_notes", "")
            },
            approval_status=ApprovalStatus.PENDING,
            publishing_status=PublishingStatus.PENDING,
            created_at=datetime.now()
        )
    
    async def _generate_supporting_blog(self, context: Dict[str, Any]) -> ContentPiece:
        """Generate supporting blog post"""
        # Modify context to focus on a specific angle
        angle_index = hash(str(datetime.now())) % len(context.get("content_angles", ["General"]))
        specific_angle = context.get("content_angles", ["General"])[angle_index]
        
        prompt = self._build_supporting_blog_prompt(context, specific_angle)
        
        content_result, token_usage = await self.claude.complete(
            prompt=prompt,
            max_tokens=3072
        )
        
        parsed = self._parse_generated_content(content_result)
        
        return ContentPiece(
            id=str(uuid4()),
            cluster_id="",
            client_id="",
            format_type=ContentFormat.BLOG_SUPPORTING_1,
            title=parsed.get("title", ""),
            content_body=parsed.get("body", ""),
            hook=parsed.get("hook", ""),
            call_to_action=parsed.get("cta", ""),
            seo_keywords=context["seo_keywords"][3:8],  # Different keywords
            hashtags=[],
            images_needed=parsed.get("image_descriptions", [
                "Header image",
                "Supporting visual"
            ]),
            platform_specs={
                "angle": specific_angle,
                "word_count": len(parsed.get("body", "").split()),
                "internal_links_to_pillar": True
            },
            approval_status=ApprovalStatus.PENDING,
            publishing_status=PublishingStatus.PENDING,
            created_at=datetime.now()
        )
    
    async def _generate_advertorial(self, context: Dict[str, Any]) -> ContentPiece:
        """Generate advertorial content"""
        prompt = self._build_advertorial_prompt(context)
        
        content_result, token_usage = await self.claude.complete(
            prompt=prompt,
            max_tokens=3072
        )
        
        parsed = self._parse_generated_content(content_result)
        
        return ContentPiece(
            id=str(uuid4()),
            cluster_id="",
            client_id="",
            format_type=ContentFormat.ADVERTORIAL,
            title=parsed.get("title", ""),
            content_body=parsed.get("body", ""),
            hook=parsed.get("hook", ""),
            call_to_action=parsed.get("cta", ""),
            seo_keywords=[],  # Advertorials typically don't focus on SEO
            hashtags=[],
            images_needed=parsed.get("image_descriptions", [
                "Hero image",
                "Product/service visual",
                "Results visualization"
            ]),
            platform_specs={
                "publication_target": parsed.get("publication", "General"),
                "native_style_score": parsed.get("native_score", 0.85),
                "disclosure_included": True
            },
            approval_status=ApprovalStatus.PENDING,
            publishing_status=PublishingStatus.PENDING,
            created_at=datetime.now()
        )
    
    async def _generate_facebook_post(self, context: Dict[str, Any]) -> ContentPiece:
        """Generate Facebook post"""
        prompt = self._build_facebook_prompt(context)
        
        content_result, token_usage = await self.claude.complete(
            prompt=prompt,
            max_tokens=1024
        )
        
        parsed = self._parse_generated_content(content_result)
        
        return ContentPiece(
            id=str(uuid4()),
            cluster_id="",
            client_id="",
            format_type=ContentFormat.META_FACEBOOK_POST,
            title=f"FB: {context['topic'][:50]}",
            content_body=parsed.get("post_text", ""),
            hook=parsed.get("hook", ""),
            call_to_action=parsed.get("cta", ""),
            seo_keywords=[],
            hashtags=self._generate_hashtags(context, platform="facebook")[:10],
            images_needed=[parsed.get("image_description", "")],
            platform_specs={
                "post_type": parsed.get("post_type", "link"),
                "engagement_question": parsed.get("question", ""),
                "optimal_length": True if len(parsed.get("post_text", "")) < 250 else False
            },
            approval_status=ApprovalStatus.PENDING,
            publishing_status=PublishingStatus.PENDING,
            created_at=datetime.now()
        )
    
    async def _generate_tiktok_script(self, context: Dict[str, Any]) -> ContentPiece:
        """Generate TikTok UGC script"""
        prompt = self._build_tiktok_prompt(context)
        
        content_result, token_usage = await self.claude.complete(
            prompt=prompt,
            max_tokens=1024
        )
        
        parsed = self._parse_generated_content(content_result)
        
        return ContentPiece(
            id=str(uuid4()),
            cluster_id="",
            client_id="",
            format_type=ContentFormat.TIKTOK_UGC,
            title=f"TikTok: {context['topic'][:30]}",
            content_body=parsed.get("script", ""),
            hook=parsed.get("hook", ""),
            call_to_action=parsed.get("cta", "Follow for more tips!"),
            seo_keywords=[],
            hashtags=self._generate_hashtags(context, platform="tiktok")[:5],
            images_needed=[],  # Video format
            platform_specs={
                "duration_seconds": parsed.get("duration", 30),
                "scene_breakdown": parsed.get("scenes", []),
                "music_suggestion": parsed.get("music", "Trending audio"),
                "effects_needed": parsed.get("effects", [])
            },
            approval_status=ApprovalStatus.PENDING,
            publishing_status=PublishingStatus.PENDING,
            created_at=datetime.now()
        )
    
    async def _generate_youtube_shorts(self, context: Dict[str, Any]) -> ContentPiece:
        """Generate YouTube Shorts script"""
        prompt = self._build_youtube_shorts_prompt(context)
        
        content_result, token_usage = await self.claude.complete(
            prompt=prompt,
            max_tokens=1024
        )
        
        parsed = self._parse_generated_content(content_result)
        
        return ContentPiece(
            id=str(uuid4()),
            cluster_id="",
            client_id="",
            format_type=ContentFormat.YOUTUBE_SHORTS,
            title=parsed.get("title", ""),
            content_body=parsed.get("script", ""),
            hook=parsed.get("hook", ""),
            call_to_action=parsed.get("cta", "Subscribe for more!"),
            seo_keywords=context["seo_keywords"][:3],
            hashtags=self._generate_hashtags(context, platform="youtube")[:15],
            images_needed=[],  # Video format
            platform_specs={
                "duration_seconds": parsed.get("duration", 45),
                "thumbnail_text": parsed.get("thumbnail_text", ""),
                "chapters": parsed.get("chapters", []),
                "end_screen_elements": parsed.get("end_screen", [])
            },
            approval_status=ApprovalStatus.PENDING,
            publishing_status=PublishingStatus.PENDING,
            created_at=datetime.now()
        )
    
    async def _generate_tiktok_shorts(self, context: Dict[str, Any]) -> ContentPiece:
        """Generate TikTok Shorts script (different from UGC)"""
        # Similar to TikTok UGC but more polished/branded
        return await self._generate_tiktok_script(context)
    
    # Helper methods for content generation
    
    def _build_ai_search_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for AI search blog generation"""
        return f"""
Generate an AI Search optimized blog post about "{context['topic']}" that will rank well in ChatGPT, Perplexity, and other AI search engines.

Context:
- Viral Hooks: {', '.join(context.get('viral_hooks', [])[:3])}
- SEO Keywords: {', '.join(context['seo_keywords'][:5])}
- Target Audience: {context.get('target_audience', {}).get('description', 'Business professionals')}
- Authority Positioning: {context.get('authority_positioning', {}).get('key_expertise', 'Industry expertise')}
- Pain Points: {', '.join(context.get('pain_points', [])[:3])}

Requirements:
1. Title: Compelling, keyword-rich, question-based when possible
2. Hook: Opening 2-3 sentences that grab attention using viral hook
3. Body: 1500-2000 words, structured with clear headers
4. Include "Quick Answer" section near the beginning
5. Use bullet points and numbered lists for scannability
6. Include data, statistics, and expert insights
7. Natural keyword integration (1-2% density)
8. Meta Description: 150-160 characters
9. 3 Image Descriptions for visual breaks
10. 3-5 Internal link opportunities
11. Strong CTA related to services

Format the response as JSON with keys: title, hook, body, meta_description, image_descriptions, internal_links, cta
"""
    
    def _build_epic_pillar_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for epic pillar article generation"""
        return f"""
Create a comprehensive epic pillar article (3000+ words) about "{context['topic']}" that serves as the ultimate resource.

Context:
- Content Angles: {', '.join(context.get('content_angles', [])[:3])}
- Authority Areas: {context.get('authority_positioning', {}).get('expertise_areas', 'Industry leadership')}
- Competitive Insights: {context.get('competitive_insights', {}).get('key_differentiators', 'Unique approach')}
- Service Offerings: {', '.join(context.get('service_offerings', [])[:3])}

Requirements:
1. Title: "Ultimate Guide" or "Everything You Need to Know" format
2. Hook: Powerful opening that establishes this as THE resource
3. Table of Contents with jump links
4. 5-7 Major sections with subsections
5. Include case studies, examples, and data visualizations
6. Actionable takeaways in each section
7. Downloadable resource/checklist as lead magnet
8. Expert quotes and citations
9. FAQ section
10. Comprehensive conclusion with next steps
11. 5 Image descriptions (hero + section images)

Format as JSON with keys: title, hook, body, toc, sections, lead_magnet, image_descriptions, cta
"""
    
    def _build_instagram_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for Instagram post generation"""
        return f"""
Create an engaging Instagram post about "{context['topic']}" optimized for maximum engagement.

Context:
- Viral Hooks: {', '.join(context.get('viral_hooks', [])[:2])}
- Emotional Drivers: {', '.join(context.get('emotional_drivers', [])[:2])}
- Brand Voice: {context.get('brand_voice', {}).get('tone', 'Professional yet approachable')}
- Visual Style: {context.get('visual_style', {}).get('aesthetic', 'Clean and modern')}

Requirements:
1. Hook: First line that stops the scroll
2. Caption: 150-300 words, conversational tone
3. Include 3-5 emoji for visual breaks
4. Ask engagement question
5. Clear CTA (link in bio, DM, save, share)
6. Image Description: Specific visual that complements text
7. Format with line breaks for readability

Format as JSON with keys: hook, caption, cta, image_description
"""
    
    def _build_x_thread_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for X thread generation"""
        return f"""
Create a viral X (Twitter) thread about "{context['topic']}" that drives engagement and shares.

Context:
- Viral Hooks: {', '.join(context.get('viral_hooks', [])[:2])}
- Key Points: {', '.join(context.get('content_angles', [])[:3])}
- Target Emotions: {', '.join(context.get('emotional_drivers', [])[:2])}

Requirements:
1. Opening tweet: Strong hook with numbers/controversy/curiosity
2. 5-8 follow-up tweets (each under 280 chars)
3. Use "Here's why:", "The truth is:", "But here's the thing:" transitions
4. Include specific examples or data points
5. Build to climactic insight
6. End with CTA tweet
7. Suggest thread structure and engagement hooks

Format as JSON with keys: tweets (array), thread_structure, engagement_hooks, cta
"""
    
    def _build_linkedin_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for LinkedIn article generation"""
        return f"""
Write a professional LinkedIn article about "{context['topic']}" that positions the author as a thought leader.

Context:
- Professional Audience: {context.get('target_audience', {}).get('professional_level', 'Business leaders')}
- Authority Positioning: {context.get('authority_positioning', {}).get('credentials', 'Industry expertise')}
- Business Impact: {', '.join(context.get('pain_points', [])[:2])}

Requirements:
1. Title: Professional, benefit-driven
2. Hook: Personal story or industry insight
3. Body: 1000-1500 words, professional tone
4. Include industry data and trends
5. Share lessons learned
6. Actionable business insights
7. End with thought-provoking question
8. 2 Image descriptions (header + data viz)

Format as JSON with keys: title, hook, body, image_descriptions, cta, industry_keywords
"""
    
    def _parse_generated_content(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from Claude"""
        import json
        try:
            # Handle potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except:
            # Fallback to basic parsing if JSON fails
            return {"body": content}
    
    def _generate_hashtags(
        self, context: Dict[str, Any], platform: str
    ) -> List[str]:
        """Generate platform-appropriate hashtags"""
        base_tags = []
        
        # Add keyword-based tags
        for keyword in context.get("seo_keywords", [])[:3]:
            tag = keyword.replace(" ", "").lower()
            base_tags.append(f"#{tag}")
        
        # Platform-specific tags
        if platform == "instagram":
            base_tags.extend([
                "#marketingtips", "#businessgrowth", "#entrepreneur",
                "#digitalmarketing", "#contentmarketing"
            ])
        elif platform == "tiktok":
            base_tags.extend([
                "#businesstok", "#marketinghacks", "#fyp",
                "#learnontiktok", "#businesstips"
            ])
        elif platform == "linkedin":
            base_tags.extend([
                "#leadership", "#businessstrategy", "#innovation",
                "#thoughtleadership", "#professionaldevelopment"
            ])
        
        return list(set(base_tags))
    
    def _calculate_reading_time(self, text: str) -> int:
        """Calculate estimated reading time in minutes"""
        words = len(text.split())
        # Average reading speed: 200-250 words per minute
        return max(1, words // 225)
    
    def _count_emojis(self, text: str) -> int:
        """Count emojis in text"""
        import re
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+"
        )
        return len(emoji_pattern.findall(text))
    
    def _truncate_tweet(self, tweet: str, max_length: int = 280) -> str:
        """Truncate tweet to character limit"""
        if len(tweet) <= max_length:
            return tweet
        return tweet[:max_length-3] + "..."
    
    def _suggest_posting_time(self, platform: str, context: Dict[str, Any]) -> str:
        """Suggest optimal posting time based on platform and audience"""
        # Simple logic - in production would use analytics data
        platform_times = {
            "instagram": "12:00 PM or 7:00 PM",
            "x": "9:00 AM or 3:00 PM",
            "linkedin": "7:30 AM or 5:30 PM",
            "facebook": "1:00 PM or 8:00 PM",
            "tiktok": "6:00 AM or 7:00 PM"
        }
        return platform_times.get(platform, "12:00 PM")
    
    def _extract_intelligence_summary(self, cia_intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key intelligence points for cluster summary"""
        return {
            "target_audience": cia_intelligence.get("target_audience", {}),
            "key_pain_points": cia_intelligence.get("pain_points", [])[:5],
            "authority_areas": cia_intelligence.get("authority_positioning", {}).get("expertise_areas", []),
            "competitive_advantages": cia_intelligence.get("competitive_analysis", {}).get("advantages", []),
            "psychological_triggers": cia_intelligence.get("customer_psychology", {}).get("triggers", [])
        }
    
    def _create_publishing_schedule(
        self, content_pieces: List[ContentPiece], client_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create publishing schedule for content cluster"""
        schedule = {
            "start_date": datetime.now().isoformat(),
            "duration_days": 7,
            "platform_schedule": {}
        }
        
        # Group by platform
        for piece in content_pieces:
            platform = CONTENT_FORMAT_SPECS.get(piece.format_type, {}).get("platform", "other")
            if platform not in schedule["platform_schedule"]:
                schedule["platform_schedule"][platform] = []
            
            schedule["platform_schedule"][platform].append({
                "content_id": piece.id,
                "format": piece.format_type.value,
                "suggested_time": piece.platform_specs.get("posting_time", "12:00 PM"),
                "day_offset": len(schedule["platform_schedule"][platform])  # Spread across days
            })
        
        return schedule
    
    # Additional prompt builders for other formats
    
    def _build_supporting_blog_prompt(self, context: Dict[str, Any], angle: str) -> str:
        """Build prompt for supporting blog posts"""
        return f"""
Write a supporting blog post about "{context['topic']}" focused on the angle: "{angle}"

This should complement the main pillar content by diving deep into this specific aspect.

Context:
- Main topic: {context['topic']}
- Specific angle: {angle}
- Keywords to include: {', '.join(context['seo_keywords'][3:8])}
- Target audience: {context.get('target_audience', {}).get('description', '')}

Requirements:
1. Title: Specific to the angle, includes main keyword
2. Hook: Ties to the specific angle
3. Body: 1000-1500 words focused on this aspect
4. Link opportunities back to pillar content
5. 2 Image descriptions
6. Specific CTA related to this angle

Format as JSON with keys: title, hook, body, image_descriptions, cta
"""
    
    def _build_podcast_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for podcast script"""
        return f"""
Create a podcast episode script about "{context['topic']}" (15-20 minutes).

Context:
- Key insights: {', '.join(context.get('content_angles', [])[:3])}
- Authority positioning: {context.get('authority_positioning', {}).get('key_expertise', '')}
- Emotional drivers: {', '.join(context.get('emotional_drivers', []))}

Requirements:
1. Episode title: Intriguing and benefit-focused
2. Intro hook (30 seconds)
3. Episode structure with 3-4 segments
4. Key talking points for each segment
5. Stories/examples to illustrate points
6. Interview questions if applicable
7. Outro with CTA (30 seconds)
8. Show notes summary
9. Duration estimate

Format as JSON with keys: episode_title, intro_hook, script, segments, talking_points, show_notes, outro_cta, duration_minutes
"""
    
    def _build_advertorial_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for advertorial content"""
        return f"""
Write a native advertorial about "{context['topic']}" that subtly promotes our services while providing value.

Context:
- Service offerings: {', '.join(context.get('service_offerings', [])[:3])}
- Unique value props: {', '.join(context.get('unique_value_props', [])[:3])}
- Pain points addressed: {', '.join(context.get('pain_points', [])[:3])}

Requirements:
1. Title: Native-style, not overtly promotional
2. Hook: Story or problem-based opening
3. Body: 1200-1500 words, journalistic tone
4. Weave in service benefits naturally
5. Include case study or success story
6. Data and research to support points
7. Soft CTA - "Learn more" style
8. Disclosure: "Sponsored content" notation
9. 3 Image descriptions

Format as JSON with keys: title, hook, body, image_descriptions, cta, publication, native_score
"""
    
    def _build_facebook_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for Facebook post"""
        return f"""
Create an engaging Facebook post about "{context['topic']}" optimized for shares and comments.

Context:
- Viral hooks: {', '.join(context.get('viral_hooks', [])[:2])}
- Emotional drivers: {', '.join(context.get('emotional_drivers', []))}
- Brand voice: {context.get('brand_voice', {}).get('tone', '')}

Requirements:
1. Hook: Question or statement that sparks curiosity
2. Post text: 100-250 words, conversational
3. Include engagement question
4. Use 1-2 relevant emojis
5. Clear CTA (comment, share, visit link)
6. Image description for visual
7. Consider video option if applicable

Format as JSON with keys: hook, post_text, question, cta, image_description, post_type
"""
    
    def _build_tiktok_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for TikTok script"""
        return f"""
Create a TikTok video script about "{context['topic']}" (15-60 seconds) that will go viral.

Context:
- Viral hooks: {', '.join(context.get('viral_hooks', [])[:2])}
- Target audience: {context.get('target_audience', {}).get('age_range', '25-45')}
- Emotional drivers: {', '.join(context.get('emotional_drivers', []))}

Requirements:
1. Hook: First 3 seconds must grab attention
2. Script: Quick-paced, value-packed
3. Scene breakdown (3-5 scenes)
4. On-screen text suggestions
5. Music/audio recommendations
6. Effects or transitions needed
7. CTA: Follow, save, share
8. Duration in seconds

Format as JSON with keys: hook, script, scenes, duration, music, effects, cta
"""
    
    def _build_youtube_shorts_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for YouTube Shorts"""
        return f"""
Create a YouTube Shorts script about "{context['topic']}" (30-60 seconds) optimized for views and engagement.

Context:
- Key insight: {context.get('content_angles', ['General insight'])[0]}
- Keywords: {', '.join(context['seo_keywords'][:3])}
- Authority: {context.get('authority_positioning', {}).get('credentials', '')}

Requirements:
1. Title: SEO-optimized, curiosity-driven
2. Hook: Visual or verbal in first 3 seconds
3. Script: Clear value delivery
4. Thumbnail text overlay suggestion
5. Chapter markers if applicable
6. End screen elements
7. CTA: Subscribe + related video
8. Duration in seconds

Format as JSON with keys: title, hook, script, thumbnail_text, chapters, end_screen, cta, duration
"""