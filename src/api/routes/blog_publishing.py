"""
Blog Publishing API Routes for Brand BOS
Handles Notion MCP blog publishing operations
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from pydantic import BaseModel, Field

from ...integrations.notion_mcp_client import (
    NotionMCPClient,
    NotionBlogPost,
    PublishStatus,
    test_notion_mcp_connection,
    quick_publish_to_notion
)
from ...publishing.blog_publisher import (
    BlogPublisher,
    BlogFormattingConfig,
    test_blog_formatting,
    publish_with_buildfast_sync
)
from ...integrations.utm_automation import UTMGenerator
from ...database.cartwheel_models import ContentPiece, ContentCluster, ContentFormat
from ...database.models import CIASession

router = APIRouter()

# Dependency injection
async def get_notion_client() -> NotionMCPClient:
    """Get Notion MCP client instance"""
    return NotionMCPClient(
        mcp_endpoint="http://localhost:3001",
        api_key="your-notion-api-key"
    )

async def get_blog_publisher(notion_client: NotionMCPClient = Depends(get_notion_client)) -> BlogPublisher:
    """Get blog publisher instance"""
    utm_generator = UTMGenerator()
    return BlogPublisher(notion_client, utm_generator)


# Request/Response Models
class BlogPublishRequest(BaseModel):
    """Request to publish a blog post"""
    database_id: str
    content_id: str
    title: str
    content_brief: str
    seo_keywords: List[str] = Field(default_factory=list)
    target_word_count: int = 1000
    content_format: str = "ai_search_blog"
    publish_immediately: bool = False

class BlogClusterPublishRequest(BaseModel):
    """Request to publish a content cluster"""
    database_id: str
    cluster_id: str
    content_pieces: List[Dict[str, Any]]
    cia_session_data: Optional[Dict[str, Any]] = None
    stagger_hours: int = 24

class BlogUpdateRequest(BaseModel):
    """Request to update blog post"""
    page_id: str
    updates: Dict[str, Any]

class BuildFastSyncRequest(BaseModel):
    """Request to sync with BuildFast"""
    page_ids: List[str]
    buildfast_config: Dict[str, Any] = Field(default_factory=dict)


# Blog Publishing Endpoints
@router.post("/blog/publish")
async def publish_blog_post(
    request: BlogPublishRequest,
    publisher: BlogPublisher = Depends(get_blog_publisher)
):
    """Publish a single blog post to Notion"""
    try:
        # Create content piece from request
        content_piece = ContentPiece(
            id=request.content_id,
            title=request.title,
            content_brief=request.content_brief,
            format=ContentFormat(request.content_format),
            cluster_id="standalone",
            client_id=UUID("00000000-0000-0000-0000-000000000000"),
            target_word_count=request.target_word_count,
            seo_keywords=request.seo_keywords,
            content_status="ready" if request.publish_immediately else "draft"
        )
        
        # Publish to Notion
        result = await publisher.publish_content_piece(
            database_id=request.database_id,
            content_piece=content_piece
        )
        
        return {
            **result,
            "message": "Blog post published successfully" if result.get("success") else "Publishing failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blog publishing failed: {str(e)}")


@router.post("/blog/publish-cluster")
async def publish_blog_cluster(
    request: BlogClusterPublishRequest,
    publisher: BlogPublisher = Depends(get_blog_publisher)
):
    """Publish an entire content cluster with interlinking"""
    try:
        # Create content cluster
        content_cluster = ContentCluster(
            id=request.cluster_id,
            cluster_topic="Content Cluster",
            client_id=UUID("00000000-0000-0000-0000-000000000000"),
            cia_session_id=UUID("00000000-0000-0000-0000-000000000000"),
            target_date=datetime.now() + timedelta(days=7),
            content_count=len(request.content_pieces),
            status="active"
        )
        
        # Create content pieces
        content_pieces = []
        for piece_data in request.content_pieces:
            content_piece = ContentPiece(
                id=piece_data.get("id", f"content_{len(content_pieces)}"),
                title=piece_data.get("title", "Untitled"),
                content_brief=piece_data.get("content_brief", ""),
                format=ContentFormat(piece_data.get("format", "ai_search_blog")),
                cluster_id=request.cluster_id,
                client_id=UUID("00000000-0000-0000-0000-000000000000"),
                target_word_count=piece_data.get("target_word_count", 1000),
                seo_keywords=piece_data.get("seo_keywords", []),
                content_status=piece_data.get("content_status", "ready")
            )
            content_pieces.append(content_piece)
        
        # Create CIA session if provided
        cia_session = None
        if request.cia_session_data:
            cia_session = CIASession(
                id=UUID(request.cia_session_data.get("id", "00000000-0000-0000-0000-000000000000")),
                company_name=request.cia_session_data.get("company_name", "Company"),
                url=request.cia_session_data.get("url", "https://example.com"),
                kpoi=request.cia_session_data.get("kpoi", "Owner"),
                country=request.cia_session_data.get("country", "US"),
                client_id=UUID("00000000-0000-0000-0000-000000000000"),
                session_status="completed"
            )
        
        # Publish cluster
        result = await publisher.publish_content_cluster(
            database_id=request.database_id,
            content_cluster=content_cluster,
            content_pieces=content_pieces,
            cia_session=cia_session,
            stagger_hours=request.stagger_hours
        )
        
        return {
            **result,
            "message": f"Published {result.get('published', 0)} of {len(content_pieces)} blog posts"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cluster publishing failed: {str(e)}")


@router.get("/blog/status/{page_id}")
async def get_blog_status(
    page_id: str,
    notion_client: NotionMCPClient = Depends(get_notion_client)
):
    """Get blog post status from Notion"""
    try:
        result = await notion_client.get_blog_post(page_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get blog status: {str(e)}")


@router.patch("/blog/update")
async def update_blog_post(
    request: BlogUpdateRequest,
    notion_client: NotionMCPClient = Depends(get_notion_client)
):
    """Update an existing blog post"""
    try:
        result = await notion_client.update_blog_post(
            page_id=request.page_id,
            updates=request.updates
        )
        
        return {
            **result,
            "message": "Blog post updated successfully" if result.get("success") else "Update failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blog update failed: {str(e)}")


# BuildFast Integration
@router.post("/blog/buildfast-sync")
async def sync_with_buildfast(
    request: BuildFastSyncRequest,
    notion_client: NotionMCPClient = Depends(get_notion_client)
):
    """Prepare blog posts for BuildFast auto-sync"""
    try:
        result = await notion_client.sync_with_buildfast(
            page_ids=request.page_ids,
            buildfast_config=request.buildfast_config
        )
        
        return {
            **result,
            "message": f"Prepared {result.get('sync_ready', 0)} posts for BuildFast sync"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BuildFast sync failed: {str(e)}")


# Testing and Debug Endpoints
@router.get("/blog/test-connection")
async def test_notion_connection(
    notion_client: NotionMCPClient = Depends(get_notion_client)
):
    """Test Notion MCP connection"""
    try:
        connection_result = await notion_client.test_connection()
        
        return {
            "notion_mcp_status": connection_result,
            "blog_publishing_available": connection_result.get("connected", False),
            "capabilities": connection_result.get("capabilities", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notion connection test failed: {str(e)}")


@router.get("/blog/databases")
async def get_notion_databases(
    notion_client: NotionMCPClient = Depends(get_notion_client)
):
    """Get available Notion databases for blog posts"""
    try:
        databases = await notion_client.get_databases()
        
        return {
            "databases": databases,
            "count": len(databases),
            "blog_compatible": [
                db for db in databases
                if any(prop in db.get("properties", {}) 
                      for prop in ["Title", "Status", "Tags"])
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get databases: {str(e)}")


@router.post("/blog/test-formatting")
async def test_blog_formatting_endpoint(
    title: str = Query(..., description="Blog post title"),
    content_brief: str = Query(..., description="Content brief"),
    seo_keywords: List[str] = Query(default=["test"], description="SEO keywords")
):
    """Test blog formatting without publishing"""
    try:
        # Create test content piece
        content_piece = ContentPiece(
            id="test_content",
            title=title,
            content_brief=content_brief,
            format=ContentFormat.AI_SEARCH_BLOG,
            cluster_id="test",
            client_id=UUID("00000000-0000-0000-0000-000000000000"),
            target_word_count=1000,
            seo_keywords=seo_keywords,
            content_status="draft"
        )
        
        # Test formatting
        result = await test_blog_formatting(content_piece)
        
        return {
            **result,
            "test_mode": True,
            "message": "Formatting test completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Formatting test failed: {str(e)}")


@router.post("/blog/quick-publish")
async def quick_publish_blog(
    database_id: str,
    title: str,
    content: str,
    tags: List[str] = Query(default=["blog"]),
    notion_client: NotionMCPClient = Depends(get_notion_client)
):
    """Quick publish a simple blog post"""
    try:
        result = await quick_publish_to_notion(
            notion_client=notion_client,
            database_id=database_id,
            title=title,
            content=content,
            tags=tags
        )
        
        return {
            **result,
            "quick_publish": True,
            "message": "Quick publish completed" if result.get("success") else "Quick publish failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick publish failed: {str(e)}")


# Integrated Publishing Endpoints
@router.post("/publish/blog-and-social")
async def publish_blog_and_social(
    notion_database_id: str,
    ghl_location_id: str,
    cluster_id: str,
    content_pieces: List[Dict[str, Any]],
    auto_approve_social: bool = False,
    background_tasks: BackgroundTasks = None
):
    """Publish to both blog and social channels"""
    try:
        # This would integrate with the full workflow
        # For now, return mock response
        return {
            "blog_publishing": {
                "status": "scheduled",
                "database_id": notion_database_id,
                "content_count": len(content_pieces)
            },
            "social_publishing": {
                "status": "scheduled",
                "location_id": ghl_location_id,
                "auto_approve": auto_approve_social
            },
            "unified_campaign": {
                "cluster_id": cluster_id,
                "total_touchpoints": len(content_pieces) * 2,  # Blog + Social
                "attribution_enabled": True
            },
            "message": "Unified publishing pipeline initiated"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unified publishing failed: {str(e)}")


@router.get("/blog/formatting-config")
async def get_formatting_config():
    """Get current blog formatting configuration"""
    try:
        default_config = BlogFormattingConfig()
        
        return {
            "config": {
                "structure": {
                    "add_table_of_contents": default_config.add_table_of_contents,
                    "add_introduction": default_config.add_introduction,
                    "add_conclusion": default_config.add_conclusion,
                    "add_cta_sections": default_config.add_cta_sections
                },
                "seo": {
                    "target_meta_length": default_config.target_meta_length,
                    "focus_keyword_density": default_config.focus_keyword_density,
                    "internal_link_count": default_config.internal_link_count
                },
                "visual": {
                    "add_featured_image": default_config.add_featured_image,
                    "add_section_images": default_config.add_section_images,
                    "image_alt_optimization": default_config.image_alt_optimization
                },
                "branding": {
                    "brand_voice": default_config.brand_voice,
                    "cta_style": default_config.cta_style
                }
            },
            "customizable": True,
            "cia_integration": "available"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get config: {str(e)}")