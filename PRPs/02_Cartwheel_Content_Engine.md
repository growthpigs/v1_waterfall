name: "Cartwheel Content Engine - Viral Content Multiplication System"
description: |
  Comprehensive PRP for implementing the Cartwheel system that detects weekly viral convergence opportunities and multiplies them into 12+ content formats with automated publishing pipeline.

## Core Principles
1. **Convergence Detection**: Systematic viral opportunity identification through multi-source analysis
2. **Content Multiplication**: Single topic transformed into 12+ optimized formats  
3. **CIA Intelligence Integration**: All content generation informed by comprehensive business intelligence
4. **Publishing Automation**: Seamless distribution across all platforms with human approval workflows
5. **Client Configuration**: Granular control over content formats and publishing preferences

---

## Goal
Build the complete Cartwheel content multiplication engine that detects weekly viral convergence opportunities and transforms them into comprehensive content clusters with automated publishing across all platforms.

## Why
- **Viral Content Scaling**: Systematically identify and capitalize on viral opportunities without manual monitoring
- **Content Efficiency**: Generate 12+ content pieces from single convergence analysis
- **CIA Integration**: Leverage comprehensive business intelligence for targeted content creation
- **Publishing Automation**: Eliminate manual content distribution and posting workflows
- **Client Scalability**: Enable unlimited client content generation with checkbox controls

## What
A complete content multiplication system that:
- Detects weekly convergence opportunities through Grok API, Reddit MCP, and Google Trends
- Generates 12+ content formats from single cluster topics
- Integrates CIA intelligence for targeted content creation
- Automates publishing through Notion/BuildFast and GHL MCP
- Provides client configuration controls for content formats and scheduling
- Includes human approval workflows for content quality control

### Success Criteria
- [ ] Weekly convergence analysis completes automatically within 1 hour
- [ ] Content multiplication generates 12+ formats within 2 hours
- [ ] Publishing pipeline delivers content to Notion within 24 hours via BuildFast
- [ ] Social distribution completes within 30 minutes via GHL MCP
- [ ] Client configuration enables/disables content formats via checkboxes
- [ ] All content integrates CIA intelligence for business-specific targeting
- [ ] Human approval workflow functional for content quality control

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- doc: Project Waterfall Complete Technical Specification
  file: documents/Project Waterfall - Complete Technical Specification.md
  sections: [Cartwheel system architecture, content multiplication pipeline]
  critical: [12+ content formats, convergence detection, publishing automation]
  
- doc: Content Multiplication Pipeline Examples
  file: examples/content_multiplication_pipeline.py
  sections: [Content format generation, publishing workflows]
  critical: [Format-specific generation patterns, platform optimization]

- doc: Publishing Automation Examples
  file: examples/publishing_automation.py
  sections: [Notion/BuildFast integration, GHL MCP posting]
  critical: [24-hour sync limitation, image generation workflow]

- doc: Cartwheel Convergence Engine Examples
  file: examples/cartwheel_convergence_engine.py
  sections: [Viral detection algorithms, multi-source analysis]
  critical: [Grok API integration, convergence scoring methodology]

- doc: Client Configuration Examples
  file: examples/client_configuration.py
  sections: [Content format controls, platform preferences]
  critical: [Checkbox controls, publishing schedules, brand voice]

- doc: Grok API Documentation
  url: https://api.grok.com/v1/docs
  sections: [Trending posts API, media filtering, rate limits]
  critical: [Media-only filtering, engagement thresholds]

- doc: GoHighLevel MCP Documentation
  url: https://docs.gohighlevel.com/
  sections: [Social media posting, multi-platform automation]
  critical: [Platform-specific formatting, posting schedules]

- doc: BuildFast Documentation
  url: https://buildfast.com/docs
  sections: [Notion integration, blog publishing, sync timing]
  critical: [24-hour sync limitation, template structure]
```

### Current Codebase Structure
```bash
V1_Waterfall/
├── .claude/                    # Context engineering framework
├── PRPs/                      # Product Requirements Prompts  
├── examples/                  # Implementation patterns (COMPLETE)
│   ├── cartwheel_convergence_engine.py  # Viral detection and scoring
│   ├── content_multiplication_pipeline.py  # 12+ format generation
│   ├── publishing_automation.py     # Notion/BuildFast/GHL workflow
│   ├── client_configuration.py      # Content format controls
│   └── cia_phase_structure.py       # CIA intelligence integration
├── src/                       # Source code (EXISTING + TO BE CREATED)
│   ├── cia/                  # CIA intelligence engine (IMPLEMENTED)
│   ├── cartwheel/            # Cartwheel content engine (TO BE CREATED)
│   ├── integrations/         # External API integrations (EXTEND)
│   ├── database/            # Supabase schemas (EXTEND)
│   ├── notifications/       # Human approval workflows (EXTEND)
│   └── web/                 # React dashboard interface (EXTEND)
├── tests/                   # Test suites
└── docs/                    # Project documentation
```

### Desired Implementation Structure
```bash
# Files to be added for Cartwheel system
src/
├── cartwheel/
│   ├── __init__.py
│   ├── convergence_engine.py        # Multi-source viral detection
│   ├── content_multiplier.py        # 12+ format generation engine
│   ├── publishing_coordinator.py    # Notion/BuildFast/GHL orchestration
│   ├── approval_workflow.py         # Human content review system
│   └── scheduling_manager.py        # Content scheduling and timing
├── integrations/
│   ├── grok_api.py                 # X trending posts integration
│   ├── reddit_mcp.py               # Reddit viral content analysis
│   ├── google_trends.py            # Long-term trend analysis
│   ├── glif_image_generator.py     # Image generation for content
│   ├── ghl_social_poster.py        # GoHighLevel posting automation
│   └── buildfast_notion.py         # Notion/BuildFast blog publishing
├── database/
│   ├── cartwheel_models.py         # Content cluster and piece models
│   ├── cartwheel_repository.py     # Database operations for content
│   └── content_approval_models.py  # Approval workflow data models
└── web/
    ├── components/CartwheelDashboard.tsx  # Content generation interface
    ├── components/ContentApproval.tsx     # Human approval interface
    ├── components/PublishingPipeline.tsx  # Publishing status tracking
    └── components/ConvergenceAnalysis.tsx # Weekly opportunity display
```

### Known Gotchas & Framework Requirements
```python
# CRITICAL: Cartwheel System Requirements
# - Convergence detection MUST run weekly automatically without human intervention
# - All content generation MUST integrate CIA intelligence for business-specific targeting
# - Publishing pipeline MUST handle 24-hour BuildFast sync limitation gracefully
# - Content formats MUST be client-configurable via checkbox controls
# - Human approval workflow MUST allow content review before publishing

# CRITICAL: API Integration Patterns
# - Grok API: Media-only filtering for X trending posts, rate limit handling
# - Reddit MCP: Viral content analysis from marketing-relevant subreddits
# - Google Trends: Long-term pattern analysis for convergence validation
# - GHL MCP: Multi-platform posting with platform-specific formatting
# - Glif.com: Image generation with brand consistency and style requirements

# CRITICAL: Content Generation Requirements
# - 12+ Content Formats: AI Search Blog, Epic Pillar, Podcast, Social posts, etc.
# - CIA Intelligence Integration: Customer psychology, authority positioning, competitive insights
# - Platform Optimization: Format-specific requirements (character limits, hashtags, etc.)
# - Brand Voice Consistency: All content must match client brand voice and visual style
# - SEO Integration: Content must incorporate keywords and SEO strategy from CIA Phase 2

# CRITICAL: Publishing Pipeline Requirements
# - Notion Integration: Content must be formatted for BuildFast template structure
# - 24-Hour Sync: BuildFast limitation requires proper scheduling and status tracking
# - Image Generation: Glif.com integration for consistent visual content creation
# - Social Posting: GHL MCP for automated posting across all enabled platforms
# - Approval Gates: Human review required before publishing (configurable per client)

# CRITICAL: Quality Control Requirements
# - Content Quality Validation: Ensure all generated content meets standards
# - CIA Alignment: Content must reflect business intelligence and positioning
# - Platform Compliance: Content must meet platform-specific requirements
# - Brand Consistency: Visual and voice consistency across all formats
# - Performance Tracking: Monitor content performance for optimization
```

## Implementation Blueprint

### Data Models and Structure
```python
# Core Cartwheel data models for content generation and publishing
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
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

class ConvergenceSource(Enum):
    GROK_X_TRENDING = "grok_x_trending"
    REDDIT_VIRAL = "reddit_viral"
    GOOGLE_TRENDS = "google_trends"

class PublishingStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    NOTION_CREATED = "notion_created"
    BUILDFAST_SYNCED = "buildfast_synced"
    LIVE = "live"
    SOCIAL_POSTED = "social_posted"
    FAILED = "failed"

@dataclass
class ConvergenceOpportunity:
    id: str
    client_id: str
    week_date: str
    topic: str
    convergence_score: float
    viral_sources: List[Dict[str, Any]]
    seo_keywords: List[str]
    trend_momentum: str
    content_opportunity: Dict[str, Any]
    recommended_formats: List[ContentFormat]
    urgency_level: str
    created_at: datetime

@dataclass
class ContentCluster:
    id: str
    client_id: str
    convergence_id: str
    cluster_topic: str
    cia_intelligence_summary: Dict[str, Any]
    content_pieces: List['ContentPiece']
    publishing_schedule: Dict[str, Any]
    approval_status: str
    created_at: datetime
    approved_at: Optional[datetime]

@dataclass
class ContentPiece:
    id: str
    cluster_id: str
    format_type: ContentFormat
    title: str
    content_body: str
    hook: str
    call_to_action: str
    seo_keywords: List[str]
    hashtags: List[str]
    images_needed: List[str]
    platform_specs: Dict[str, Any]
    approval_status: str
    publishing_status: PublishingStatus
    notion_page_id: Optional[str]
    published_url: Optional[str]
    performance_metrics: Dict[str, Any]
    created_at: datetime
    published_at: Optional[datetime]

@dataclass
class ContentApproval:
    id: str
    content_piece_id: str
    reviewer_id: str
    status: str  # "pending", "approved", "rejected", "needs_revision"
    feedback: Optional[str]
    revision_notes: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
```

### Implementation Tasks
```yaml
Task 1: [Database Schema Extension for Cartwheel]
EXTEND src/database/supabase_schema.sql:
  - CREATE convergence_opportunities table for weekly viral detection
  - CREATE content_clusters table for grouping content pieces
  - CREATE content_pieces table for individual format storage
  - CREATE content_approvals table for human review workflow
  - CREATE publishing_jobs table for tracking distribution status
  - ADD indexes for performance (client_id, week_date, format_type, status)

CREATE src/database/cartwheel_models.py:
  - DEFINE Pydantic models for all Cartwheel data structures
  - INCLUDE validation for content quality and CIA integration
  - IMPLEMENT serialization for complex content data types
  - VALIDATE platform-specific requirements per format

CREATE src/database/cartwheel_repository.py:
  - IMPLEMENT CRUD operations for convergence opportunities
  - HANDLE content cluster creation and management
  - MANAGE content piece lifecycle (generation → approval → publishing)
  - IMPLEMENT performance tracking and analytics queries

Task 2: [Convergence Detection Engine]
CREATE src/cartwheel/convergence_engine.py:
  - IMPLEMENT weekly convergence analysis orchestrator
  - INTEGRATE Grok API for X trending posts (media-only)
  - INTEGRATE Reddit MCP for viral marketing content
  - INTEGRATE Google Trends for long-term pattern validation
  - CALCULATE convergence scores using multi-source algorithm
  - IDENTIFY top opportunities for content generation

CREATE src/integrations/grok_api.py:
  - IMPLEMENT Grok API integration with authentication
  - HANDLE trending posts retrieval with media filtering
  - PROCESS engagement metrics and viral indicators
  - INCLUDE rate limiting and error handling
  - CACHE trending data for performance optimization

CREATE src/integrations/reddit_mcp.py:
  - IMPLEMENT Reddit MCP integration for viral content
  - ANALYZE marketing-relevant subreddits for trending topics
  - EXTRACT engagement patterns and discussion themes
  - IDENTIFY viral opportunities in professional services content
  - HANDLE API rate limits and content filtering

CREATE src/integrations/google_trends.py:
  - IMPLEMENT Google Trends API integration
  - ANALYZE long-term keyword and topic momentum
  - VALIDATE convergence opportunities with trend data
  - PROVIDE seasonality and geographic insights
  - SUPPORT convergence scoring algorithm with trend validation

Task 3: [Content Multiplication Engine]
CREATE src/cartwheel/content_multiplier.py:
  - IMPLEMENT 12+ content format generation engine
  - INTEGRATE CIA intelligence for business-specific targeting
  - GENERATE platform-optimized content for each format
  - MAINTAIN brand voice consistency across all formats
  - INCLUDE SEO keyword integration from CIA analysis
  - VALIDATE content quality and CIA alignment

CREATE src/cartwheel/format_generators/ai_search_blog.py:
  - GENERATE AI Search optimized blog posts
  - OPTIMIZE for ChatGPT/Perplexity discovery
  - INTEGRATE authority signals from CIA intelligence
  - INCLUDE internal linking opportunities
  - MAINTAIN 1500-2000 word count requirement

CREATE src/cartwheel/format_generators/epic_pillar.py:
  - GENERATE comprehensive pillar articles (3000+ words)
  - STRUCTURE with multiple sections and takeaways
  - INTEGRATE competitive insights from CIA analysis
  - INCLUDE downloadable resources and lead magnets
  - OPTIMIZE for maximum authority positioning

CREATE src/cartwheel/format_generators/social_content.py:
  - GENERATE platform-specific social media content
  - HANDLE character limits and hashtag requirements
  - OPTIMIZE posting times per platform
  - INTEGRATE viral hooks from convergence analysis
  - MAINTAIN brand voice across all social platforms

Task 4: [Publishing Coordination System]
CREATE src/cartwheel/publishing_coordinator.py:
  - ORCHESTRATE complete publishing pipeline
  - COORDINATE Notion/BuildFast blog publishing
  - MANAGE GHL MCP social media posting
  - HANDLE image generation via Glif.com
  - TRACK publishing status across all platforms
  - IMPLEMENT retry logic for failed publishes

CREATE src/integrations/buildfast_notion.py:
  - IMPLEMENT Notion integration with BuildFast template structure
  - FORMAT content for proper Notion block structure
  - HANDLE image placement and internal linking
  - TRACK 24-hour BuildFast sync status
  - PROVIDE live blog URL once synced

CREATE src/integrations/ghl_social_poster.py:
  - IMPLEMENT GoHighLevel MCP integration
  - HANDLE multi-platform posting automation
  - FORMAT content per platform requirements
  - SCHEDULE posts for optimal engagement times
  - TRACK posting status and engagement metrics

CREATE src/integrations/glif_image_generator.py:
  - IMPLEMENT Glif.com image generation integration
  - GENERATE brand-consistent images for content
  - HANDLE image descriptions and style requirements
  - INTEGRATE client brand guidelines and visual style
  - PROVIDE images for all content formats requiring visuals

Task 5: [Human Approval Workflow System]
CREATE src/cartwheel/approval_workflow.py:
  - IMPLEMENT content approval pipeline
  - SEND approval notifications via Slack + Email
  - HANDLE reviewer feedback and revision requests
  - TRACK approval status across all content pieces
  - ENABLE bulk approval for content clusters
  - IMPLEMENT approval timeouts and escalation

CREATE src/notifications/content_approval_notifier.py:
  - SEND content approval notifications to designated reviewers
  - INCLUDE content preview and approval links
  - HANDLE approval confirmation and feedback collection
  - SEND publishing completion notifications
  - TRACK notification delivery and response rates

Task 6: [Client Configuration Integration]
CREATE src/cartwheel/client_config_manager.py:
  - INTEGRATE with existing client configuration system
  - HANDLE content format enable/disable controls
  - MANAGE publishing schedule preferences per platform
  - APPLY brand voice and visual style to content generation
  - VALIDATE client configuration for content requirements

CREATE src/cartwheel/scheduling_manager.py:
  - IMPLEMENT intelligent content scheduling
  - OPTIMIZE posting times per platform and audience
  - HANDLE content distribution across multiple days
  - PREVENT content overlap and cannibalization
  - INTEGRATE with client timezone preferences

Task 7: [Web Dashboard Interface]
CREATE src/web/components/CartwheelDashboard.tsx:
  - DISPLAY weekly convergence opportunities
  - SHOW content generation progress
  - PROVIDE content cluster management interface
  - TRACK publishing status across all platforms
  - IMPLEMENT performance analytics display

CREATE src/web/components/ContentApproval.tsx:
  - DISPLAY content pieces awaiting approval
  - PROVIDE content preview and editing interface
  - HANDLE approval/rejection workflow
  - SHOW revision history and feedback
  - ENABLE bulk approval actions

CREATE src/web/components/PublishingPipeline.tsx:
  - TRACK content through complete publishing pipeline
  - DISPLAY publishing status per platform
  - SHOW BuildFast sync status and live URLs
  - MONITOR social media posting completion
  - PROVIDE retry options for failed publishes

CREATE src/web/components/ConvergenceAnalysis.tsx:
  - VISUALIZE weekly convergence detection results
  - DISPLAY viral source analysis and trending topics
  - SHOW convergence scoring methodology
  - ENABLE manual convergence opportunity selection
  - PROVIDE convergence history and performance tracking
```

### Content Generation Implementation
```python
# Detailed implementation for content multiplication with CIA integration
async def generate_content_cluster(
    convergence_opportunity: ConvergenceOpportunity,
    cia_intelligence: Dict[str, Any],
    client_config: Dict[str, Any]
) -> ContentCluster:
    """
    Generate complete content cluster from convergence opportunity
    """
    # Get enabled content formats from client configuration
    enabled_formats = get_enabled_content_formats(client_config)
    
    # Build content generation context with CIA intelligence
    generation_context = {
        "convergence_topic": convergence_opportunity.topic,
        "viral_hooks": convergence_opportunity.content_opportunity["hook_opportunities"],
        "seo_keywords": convergence_opportunity.seo_keywords,
        "customer_psychology": cia_intelligence["customer_psychology"],
        "authority_positioning": cia_intelligence["authority_positioning"],
        "competitive_insights": cia_intelligence["competitive_analysis"],
        "brand_voice": client_config["brand_voice"],
        "target_audience": client_config["target_audience"]
    }
    
    # Generate content for each enabled format
    content_pieces = []
    for format_type in enabled_formats:
        try:
            piece = await generate_content_piece(format_type, generation_context)
            content_pieces.append(piece)
        except Exception as e:
            log_content_generation_error(format_type, str(e))
            continue
    
    # Create content cluster
    cluster = ContentCluster(
        id=generate_cluster_id(),
        client_id=convergence_opportunity.client_id,
        convergence_id=convergence_opportunity.id,
        cluster_topic=convergence_opportunity.topic,
        cia_intelligence_summary=extract_intelligence_summary(cia_intelligence),
        content_pieces=content_pieces,
        publishing_schedule=create_publishing_schedule(content_pieces, client_config),
        approval_status="pending",
        created_at=datetime.now(),
        approved_at=None
    )
    
    # Save to database
    await save_content_cluster(cluster)
    
    # Send approval notification
    await send_content_approval_notification(cluster)
    
    return cluster

async def generate_ai_search_blog(context: Dict[str, Any]) -> ContentPiece:
    """
    Generate AI Search optimized blog post for ChatGPT/Perplexity discovery
    """
    # Build comprehensive prompt with CIA intelligence
    prompt = build_ai_search_blog_prompt(
        topic=context["convergence_topic"],
        keywords=context["seo_keywords"],
        customer_psychology=context["customer_psychology"],
        authority_signals=context["authority_positioning"]["expertise_areas"],
        viral_hooks=context["viral_hooks"]
    )
    
    # Generate content via Claude with specific requirements
    content_result = await claude_generate_content(
        prompt=prompt,
        requirements={
            "word_count": "1500-2000",
            "keyword_density": "1-2%",
            "ai_discovery_optimization": True,
            "internal_linking": True,
            "authority_positioning": "maximum"
        }
    )
    
    # Generate images for content
    images = await generate_content_images(
        descriptions=content_result["image_descriptions"],
        brand_style=context["brand_voice"]["visual_style"]
    )
    
    return ContentPiece(
        id=generate_content_id(),
        cluster_id="",  # Will be set by parent cluster
        format_type=ContentFormat.AI_SEARCH_BLOG,
        title=content_result["title"],
        content_body=content_result["body"],
        hook=context["viral_hooks"][0] if context["viral_hooks"] else content_result["hook"],
        call_to_action=content_result["cta"],
        seo_keywords=context["seo_keywords"][:5],
        hashtags=[],  # Not applicable for blog posts
        images_needed=content_result["image_descriptions"],
        platform_specs={
            "optimization_type": "ai_search",
            "internal_links": content_result["internal_link_opportunities"],
            "meta_description": content_result["meta_description"],
            "reading_time": content_result["estimated_reading_time"]
        },
        approval_status="pending",
        publishing_status=PublishingStatus.PENDING,
        notion_page_id=None,
        published_url=None,
        performance_metrics={},
        created_at=datetime.now(),
        published_at=None
    )

async def run_weekly_convergence_analysis(client_id: str) -> List[ConvergenceOpportunity]:
    """
    Execute complete weekly convergence detection workflow
    """
    # Get client's CIA intelligence for context
    cia_intelligence = await get_latest_cia_intelligence(client_id)
    
    # Initialize convergence engine
    engine = ConvergenceDetectionEngine()
    
    # Gather viral data from all sources
    grok_data = await engine.get_grok_trending_posts(hours=24, media_only=True)
    reddit_data = await engine.get_reddit_viral_content(hours=24)
    
    # Extract keywords for Google Trends analysis
    all_keywords = extract_keywords_from_viral_data(grok_data + reddit_data)
    trends_data = await engine.analyze_google_trends(all_keywords)
    
    # Detect convergence opportunities
    opportunities = await engine.detect_convergence_opportunities(
        grok_data=grok_data,
        reddit_data=reddit_data,
        trends_data=trends_data,
        cia_intelligence=cia_intelligence
    )
    
    # Filter and rank opportunities
    qualified_opportunities = [
        opp for opp in opportunities 
        if opp.convergence_score >= CONVERGENCE_THRESHOLD
    ]
    
    # Save opportunities to database
    for opportunity in qualified_opportunities:
        await save_convergence_opportunity(opportunity)
    
    return qualified_opportunities[:3]  # Return top 3 opportunities

async def execute_publishing_pipeline(content_cluster: ContentCluster) -> Dict[str, Any]:
    """
    Execute complete publishing pipeline for approved content cluster
    """
    publishing_results = {
        "cluster_id": content_cluster.id,
        "blog_posts_created": 0,
        "social_posts_scheduled": 0,
        "images_generated": 0,
        "publishing_errors": []
    }
    
    # Generate images for all content pieces
    for piece in content_cluster.content_pieces:
        if piece.images_needed:
            try:
                images = await generate_content_images(
                    descriptions=piece.images_needed,
                    brand_style=get_client_brand_style(content_cluster.client_id)
                )
                piece.platform_specs["generated_images"] = images
                publishing_results["images_generated"] += len(images)
            except Exception as e:
                publishing_results["publishing_errors"].append(f"Image generation failed for {piece.id}: {e}")
    
    # Publish blog content via Notion/BuildFast
    blog_pieces = [p for p in content_cluster.content_pieces if is_blog_format(p.format_type)]
    for piece in blog_pieces:
        try:
            notion_page_id = await publish_to_notion_buildfast(piece)
            piece.notion_page_id = notion_page_id
            piece.publishing_status = PublishingStatus.NOTION_CREATED
            publishing_results["blog_posts_created"] += 1
        except Exception as e:
            publishing_results["publishing_errors"].append(f"Blog publishing failed for {piece.id}: {e}")
    
    # Schedule social media posts via GHL MCP
    social_pieces = [p for p in content_cluster.content_pieces if is_social_format(p.format_type)]
    for piece in social_pieces:
        try:
            post_id = await schedule_social_post(piece)
            piece.platform_specs["ghl_post_id"] = post_id
            piece.publishing_status = PublishingStatus.SOCIAL_POSTED
            publishing_results["social_posts_scheduled"] += 1
        except Exception as e:
            publishing_results["publishing_errors"].append(f"Social posting failed for {piece.id}: {e}")
    
    # Update content cluster status
    content_cluster.approval_status = "published"
    await update_content_cluster(content_cluster)
    
    # Send completion notification
    await send_publishing_completion_notification(content_cluster, publishing_results)
    
    return publishing_results
```

### Integration Points
```yaml
DATABASE:
  - EXTEND existing Supabase schema with Cartwheel tables
  - LINK content clusters to CIA intelligence via client_id
  - TRACK publishing status across all platforms
  - STORE approval workflow state and feedback

EXTERNAL_APIS:
  - Grok API: X trending posts with media filtering
  - Reddit MCP: Viral content from marketing subreddits
  - Google Trends: Long-term pattern validation
  - Glif.com: Brand-consistent image generation
  - GHL MCP: Multi-platform social media posting
  - BuildFast/Notion: Blog publishing with 24-hour sync

INTERNAL_SERVICES:
  - CIA Intelligence: Customer psychology and authority positioning
  - Client Configuration: Content format controls and brand settings
  - Notification Service: Approval and completion notifications
  - Publishing Coordinator: Cross-platform distribution management

FUTURE_INTEGRATIONS:
  - Adsby: Content clusters feed ad campaign creation
  - Analytics: Performance tracking and optimization
  - CRM: Lead generation and attribution tracking
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check src/cartwheel/ --fix    # Auto-fix Python formatting
mypy src/cartwheel/               # Type checking for content models
pytest src/cartwheel/ --cov=src/cartwheel/ --cov-report=html

# Expected: No errors, 90%+ test coverage. Fix issues before Level 2.
```

### Level 2: Content Generation Quality Tests
```python
# CREATE comprehensive test suites for content quality:

def test_convergence_detection_algorithm():
    """Test convergence scoring across multiple sources"""
    mock_grok_data = create_mock_trending_posts()
    mock_reddit_data = create_mock_viral_posts()
    mock_trends_data = create_mock_trends_data()
    
    engine = ConvergenceDetectionEngine()
    opportunities = await engine.detect_convergence_opportunities(
        mock_grok_data, mock_reddit_data, mock_trends_data, {}
    )
    
    assert len(opportunities) > 0, "No convergence opportunities detected"
    assert all(opp.convergence_score >= 0 for opp in opportunities), "Invalid convergence scores"
    assert all(len(opp.seo_keywords) > 0 for opp in opportunities), "Missing SEO keywords"

def test_content_multiplication_quality():
    """Test content generation maintains CIA intelligence integration"""
    convergence_opp = create_test_convergence_opportunity()
    cia_intelligence = create_test_cia_intelligence()
    client_config = create_test_client_config()
    
    cluster = await generate_content_cluster(convergence_opp, cia_intelligence, client_config)
    
    assert len(cluster.content_pieces) >= 3, "Insufficient content pieces generated"
    
    # Validate CIA integration in content
    for piece in cluster.content_pieces:
        assert piece.content_body, "Empty content body"
        assert piece.seo_keywords, "Missing SEO keywords"
        assert contains_authority_signals(piece.content_body, cia_intelligence), "Missing authority positioning"

def test_publishing_pipeline_workflow():
    """Test complete publishing pipeline execution"""
    cluster = create_test_content_cluster()
    
    results = await execute_publishing_pipeline(cluster)
    
    assert results["blog_posts_created"] > 0, "No blog posts created"
    assert results["images_generated"] > 0, "No images generated"
    assert len(results["publishing_errors"]) == 0, "Publishing errors occurred"

def test_human_approval_workflow():
    """Test content approval notifications and tracking"""
    cluster = create_test_content_cluster()
    
    await send_content_approval_notification(cluster)
    
    notifications = get_test_notifications()
    assert len(notifications) > 0, "No approval notifications sent"
    assert "content approval" in notifications[0].content.lower(), "Invalid notification content"
```

```bash
# Run and iterate until passing:
pytest tests/cartwheel/ -v --cov=src/cartwheel/
# Target: 95% coverage, all content quality tests passing
```

### Level 3: Integration and Performance Tests
```bash
# Test external API integrations
python -m pytest tests/integration/test_grok_api_integration.py
python -m pytest tests/integration/test_reddit_mcp_integration.py
python -m pytest tests/integration/test_buildfast_notion_integration.py
python -m pytest tests/integration/test_ghl_social_posting.py

# Test content generation performance
python -m pytest tests/performance/test_content_generation_speed.py
# Target: 12+ formats generated within 2 hours

# Test publishing pipeline performance
python -m pytest tests/performance/test_publishing_pipeline_speed.py
# Target: Social posting within 30 minutes, Notion publishing tracked

# Expected: All integrations working, performance targets met
```

### Level 4: End-to-End Content Workflow Tests
```bash
# Test complete weekly workflow
python -m pytest tests/e2e/test_weekly_convergence_workflow.py

# Test content approval workflow
python -m pytest tests/e2e/test_content_approval_workflow.py

# Test multi-client content generation
python -m pytest tests/e2e/test_multi_client_content_generation.py

# Target: Complete workflow from convergence detection to publishing
```

## Final Validation Checklist
- [ ] Weekly convergence analysis completes automatically: Test full detection workflow
- [ ] Content multiplication generates 12+ formats: Validate all enabled formats
- [ ] CIA intelligence properly integrated: Check authority positioning in content
- [ ] Publishing pipeline functional: Test Notion/BuildFast and GHL MCP integration
- [ ] Human approval workflow operational: Test notification and approval tracking
- [ ] Client configuration controls working: Test format enable/disable functionality
- [ ] Image generation functional: Test Glif.com integration with brand consistency
- [ ] Performance requirements met: <1 hour convergence, <2 hour content generation
- [ ] Quality control effective: Validate content meets standards and CIA alignment

## Anti-Patterns to Avoid
- ❌ Don't generate content without CIA intelligence integration - all content must be business-specific
- ❌ Don't bypass human approval workflow - quality control is essential
- ❌ Don't ignore platform-specific requirements - content must be optimized per platform
- ❌ Don't skip convergence validation - ensure genuine viral opportunities
- ❌ Don't overlook brand consistency - visual and voice must align across all formats
- ❌ Don't ignore publishing failures - implement proper retry and error handling
- ❌ Don't generate content without enabled format validation - respect client preferences
- ❌ Don't skip performance tracking - monitor content success for optimization
