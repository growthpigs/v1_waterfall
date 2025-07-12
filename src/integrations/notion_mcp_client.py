"""
Notion MCP Integration Client for Brand BOS
Handles blog post creation and management in Notion databases
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import httpx
from uuid import UUID

from ..database.cartwheel_models import ContentPiece, ContentFormat
from ..database.models import CIASession
from ..integrations.utm_automation import UTMGenerator, BBOSCampaignName

logger = logging.getLogger(__name__)


class NotionBlockType(Enum):
    """Supported Notion block types"""
    PARAGRAPH = "paragraph"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    BULLETED_LIST_ITEM = "bulleted_list_item"
    NUMBERED_LIST_ITEM = "numbered_list_item"
    IMAGE = "image"
    CODE = "code"
    QUOTE = "quote"
    CALLOUT = "callout"
    DIVIDER = "divider"
    TABLE_OF_CONTENTS = "table_of_contents"


class PublishStatus(Enum):
    """Blog post publish status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class NotionRichText:
    """Notion rich text element"""
    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    code: bool = False
    link: Optional[str] = None
    
    def to_notion_format(self) -> Dict[str, Any]:
        """Convert to Notion API format"""
        rich_text = {
            "type": "text",
            "text": {"content": self.text}
        }
        
        annotations = {}
        if self.bold:
            annotations["bold"] = True
        if self.italic:
            annotations["italic"] = True
        if self.underline:
            annotations["underline"] = True
        if self.code:
            annotations["code"] = True
        
        if annotations:
            rich_text["annotations"] = annotations
        
        if self.link:
            rich_text["text"]["link"] = {"url": self.link}
        
        return rich_text


@dataclass
class NotionBlock:
    """Notion content block"""
    block_type: NotionBlockType
    content: Union[str, List[NotionRichText], Dict[str, Any]]
    
    def to_notion_format(self) -> Dict[str, Any]:
        """Convert to Notion API format"""
        block = {
            "object": "block",
            "type": self.block_type.value
        }
        
        # Handle text-based blocks
        if self.block_type in [
            NotionBlockType.PARAGRAPH,
            NotionBlockType.HEADING_1,
            NotionBlockType.HEADING_2,
            NotionBlockType.HEADING_3,
            NotionBlockType.BULLETED_LIST_ITEM,
            NotionBlockType.NUMBERED_LIST_ITEM,
            NotionBlockType.QUOTE
        ]:
            if isinstance(self.content, str):
                rich_text = [NotionRichText(text=self.content).to_notion_format()]
            else:
                rich_text = [rt.to_notion_format() for rt in self.content]
            
            block[self.block_type.value] = {"rich_text": rich_text}
        
        # Handle image blocks
        elif self.block_type == NotionBlockType.IMAGE:
            if isinstance(self.content, dict):
                block["image"] = {
                    "type": "external",
                    "external": {"url": self.content.get("url", "")}
                }
                if self.content.get("caption"):
                    block["image"]["caption"] = [
                        NotionRichText(text=self.content["caption"]).to_notion_format()
                    ]
        
        # Handle callout blocks
        elif self.block_type == NotionBlockType.CALLOUT:
            if isinstance(self.content, dict):
                block["callout"] = {
                    "rich_text": [NotionRichText(text=self.content.get("text", "")).to_notion_format()],
                    "icon": {"emoji": self.content.get("emoji", "💡")},
                    "color": self.content.get("color", "gray_background")
                }
        
        # Handle divider
        elif self.block_type == NotionBlockType.DIVIDER:
            block["divider"] = {}
        
        # Handle table of contents
        elif self.block_type == NotionBlockType.TABLE_OF_CONTENTS:
            block["table_of_contents"] = {"color": "gray"}
        
        return block


@dataclass
class NotionBlogPost:
    """Notion blog post structure"""
    title: str
    content_blocks: List[NotionBlock]
    
    # SEO metadata
    meta_description: str
    slug: str
    tags: List[str]
    category: str
    
    # Publishing metadata
    author: str
    publish_date: Optional[datetime] = None
    status: PublishStatus = PublishStatus.DRAFT
    featured_image: Optional[str] = None
    
    # Brand BOS specific
    content_id: Optional[str] = None
    cluster_id: Optional[str] = None
    utm_parameters: Optional[Dict[str, str]] = None
    internal_links: Optional[List[Dict[str, str]]] = None
    
    def to_notion_page(self, database_id: str) -> Dict[str, Any]:
        """Convert to Notion page format"""
        properties = {
            "Title": {
                "title": [{"text": {"content": self.title}}]
            },
            "Meta Description": {
                "rich_text": [{"text": {"content": self.meta_description}}]
            },
            "Slug": {
                "rich_text": [{"text": {"content": self.slug}}]
            },
            "Tags": {
                "multi_select": [{"name": tag} for tag in self.tags]
            },
            "Category": {
                "select": {"name": self.category}
            },
            "Author": {
                "rich_text": [{"text": {"content": self.author}}]
            },
            "Status": {
                "select": {"name": self.status.value}
            }
        }
        
        # Add publish date if provided
        if self.publish_date:
            properties["Publish Date"] = {
                "date": {"start": self.publish_date.isoformat()}
            }
        
        # Add featured image if provided
        if self.featured_image:
            properties["Featured Image"] = {
                "url": self.featured_image
            }
        
        # Add Brand BOS metadata
        if self.content_id:
            properties["Content ID"] = {
                "rich_text": [{"text": {"content": self.content_id}}]
            }
        
        if self.cluster_id:
            properties["Cluster ID"] = {
                "rich_text": [{"text": {"content": self.cluster_id}}]
            }
        
        # Create page object
        page = {
            "parent": {"database_id": database_id},
            "properties": properties,
            "children": [block.to_notion_format() for block in self.content_blocks]
        }
        
        return page


class NotionMCPClient:
    """Notion MCP client for Brand BOS blog publishing"""
    
    def __init__(
        self,
        mcp_endpoint: str = "http://localhost:3001",
        api_key: Optional[str] = None,
        notion_version: str = "2022-06-28"
    ):
        """
        Initialize Notion MCP client
        
        Args:
            mcp_endpoint: Notion MCP server endpoint
            api_key: API key for authentication
            notion_version: Notion API version
        """
        self.mcp_endpoint = mcp_endpoint.rstrip('/')
        self.api_key = api_key
        self.notion_version = notion_version
        self.session = httpx.AsyncClient(timeout=30.0)
        
        # Headers for requests
        self.headers = {
            "Content-Type": "application/json",
            "Notion-Version": self.notion_version,
            "User-Agent": "BrandBOS/1.0"
        }
        
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Notion MCP server"""
        try:
            response = await self.session.get(
                f"{self.mcp_endpoint}/health",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {
                    "connected": True,
                    "status": "healthy",
                    "server_info": response.json(),
                    "capabilities": await self._get_capabilities()
                }
            else:
                return {
                    "connected": False,
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Notion MCP connection test failed: {e}")
            return {
                "connected": False,
                "status": "error",
                "error": str(e)
            }
    
    async def get_databases(self) -> List[Dict[str, Any]]:
        """Get available Notion databases for blog posts"""
        try:
            response = await self.session.get(
                f"{self.mcp_endpoint}/databases",
                headers=self.headers
            )
            response.raise_for_status()
            
            databases = response.json().get("databases", [])
            
            logger.info(f"Found {len(databases)} Notion databases")
            return databases
            
        except Exception as e:
            logger.error(f"Failed to get Notion databases: {e}")
            return []
    
    async def create_blog_post(
        self,
        database_id: str,
        blog_post: NotionBlogPost
    ) -> Dict[str, Any]:
        """Create a blog post in Notion"""
        try:
            page_data = blog_post.to_notion_page(database_id)
            
            response = await self.session.post(
                f"{self.mcp_endpoint}/pages",
                headers=self.headers,
                json=page_data
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"Created blog post: {blog_post.title}")
            return {
                "success": True,
                "page_id": result.get("id"),
                "url": result.get("url"),
                "title": blog_post.title,
                "status": blog_post.status.value,
                "published_date": blog_post.publish_date.isoformat() if blog_post.publish_date else None
            }
            
        except Exception as e:
            logger.error(f"Failed to create blog post: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_blog_post(
        self,
        page_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing blog post"""
        try:
            response = await self.session.patch(
                f"{self.mcp_endpoint}/pages/{page_id}",
                headers=self.headers,
                json={"properties": updates}
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"Updated blog post: {page_id}")
            return {
                "success": True,
                "page_id": page_id,
                "updated_properties": list(updates.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to update blog post: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_blog_post(self, page_id: str) -> Dict[str, Any]:
        """Get blog post details from Notion"""
        try:
            response = await self.session.get(
                f"{self.mcp_endpoint}/pages/{page_id}",
                headers=self.headers
            )
            response.raise_for_status()
            
            page_data = response.json()
            
            # Extract properties
            properties = page_data.get("properties", {})
            
            return {
                "success": True,
                "page_id": page_id,
                "title": self._extract_title(properties),
                "status": self._extract_select(properties, "Status"),
                "publish_date": self._extract_date(properties, "Publish Date"),
                "url": page_data.get("url"),
                "last_edited": page_data.get("last_edited_time")
            }
            
        except Exception as e:
            logger.error(f"Failed to get blog post: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def publish_content_piece(
        self,
        database_id: str,
        content_piece: ContentPiece,
        cia_session: Optional[CIASession] = None,
        utm_generator: Optional[UTMGenerator] = None
    ) -> Dict[str, Any]:
        """Publish a content piece as a Notion blog post"""
        try:
            # Generate blog post from content piece
            blog_post = self._content_piece_to_blog_post(
                content_piece,
                cia_session,
                utm_generator
            )
            
            # Create in Notion
            result = await self.create_blog_post(database_id, blog_post)
            
            if result.get("success"):
                logger.info(f"Successfully published content piece {content_piece.id} to Notion")
                return {
                    "success": True,
                    "content_id": content_piece.id,
                    "page_id": result.get("page_id"),
                    "url": result.get("url"),
                    "blog_post": {
                        "title": blog_post.title,
                        "slug": blog_post.slug,
                        "status": blog_post.status.value
                    }
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Failed to publish content piece: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def batch_publish_cluster(
        self,
        database_id: str,
        content_pieces: List[ContentPiece],
        cluster_id: str,
        stagger_minutes: int = 30
    ) -> List[Dict[str, Any]]:
        """Batch publish a content cluster with staggered timing"""
        try:
            results = []
            base_time = datetime.now()
            
            for i, content_piece in enumerate(content_pieces):
                # Calculate publish time with stagger
                publish_time = base_time + timedelta(minutes=i * stagger_minutes)
                
                # Create blog post
                blog_post = self._content_piece_to_blog_post(content_piece)
                blog_post.publish_date = publish_time
                blog_post.cluster_id = cluster_id
                
                # Publish to Notion
                result = await self.create_blog_post(database_id, blog_post)
                
                results.append({
                    "content_piece_id": content_piece.id,
                    "publish_time": publish_time.isoformat(),
                    "result": result
                })
                
                # Add small delay between API calls
                await asyncio.sleep(0.5)
            
            logger.info(f"Batch published {len(results)} blog posts for cluster {cluster_id}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to batch publish cluster: {e}")
            return []
    
    async def sync_with_buildfast(
        self,
        page_ids: List[str],
        buildfast_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare blog posts for BuildFast auto-sync"""
        try:
            # Update blog posts with BuildFast metadata
            sync_results = []
            
            for page_id in page_ids:
                updates = {
                    "BuildFast Ready": {
                        "checkbox": True
                    },
                    "Sync Status": {
                        "select": {"name": "pending"}
                    }
                }
                
                result = await self.update_blog_post(page_id, updates)
                sync_results.append({
                    "page_id": page_id,
                    "sync_ready": result.get("success", False)
                })
            
            return {
                "success": True,
                "total_pages": len(page_ids),
                "sync_ready": sum(1 for r in sync_results if r["sync_ready"]),
                "buildfast_pickup": "24_hours",
                "sync_results": sync_results
            }
            
        except Exception as e:
            logger.error(f"Failed to sync with BuildFast: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _content_piece_to_blog_post(
        self,
        content_piece: ContentPiece,
        cia_session: Optional[CIASession] = None,
        utm_generator: Optional[UTMGenerator] = None
    ) -> NotionBlogPost:
        """Convert content piece to Notion blog post"""
        
        # Parse content brief into blocks
        content_blocks = self._parse_content_to_blocks(content_piece.content_brief)
        
        # Generate slug from title
        slug = self._generate_slug(content_piece.title)
        
        # Extract tags from SEO keywords
        tags = content_piece.seo_keywords[:5] if hasattr(content_piece, 'seo_keywords') else []
        
        # Determine category based on content format
        category = self._get_category_from_format(content_piece.format)
        
        # Generate meta description
        meta_description = self._generate_meta_description(content_piece)
        
        # Generate UTM parameters if generator provided
        utm_params = None
        if utm_generator:
            from ..integrations.utm_automation import UTMSource, UTMMedium
            utm_params = utm_generator.generate_content_utm(
                content_piece=content_piece,
                source=UTMSource.BLOG,
                medium=UTMMedium.ORGANIC
            ).to_dict()
        
        # Set author from CIA session or default
        author = cia_session.kpoi if cia_session else "Brand BOS Team"
        
        return NotionBlogPost(
            title=content_piece.title,
            content_blocks=content_blocks,
            meta_description=meta_description,
            slug=slug,
            tags=tags,
            category=category,
            author=author,
            content_id=content_piece.id,
            cluster_id=content_piece.cluster_id,
            utm_parameters=utm_params,
            status=PublishStatus.DRAFT if content_piece.content_status != "ready" else PublishStatus.SCHEDULED
        )
    
    def _parse_content_to_blocks(self, content: str) -> List[NotionBlock]:
        """Parse content string into Notion blocks"""
        blocks = []
        
        # Add table of contents for long content
        if len(content) > 2000:
            blocks.append(NotionBlock(NotionBlockType.TABLE_OF_CONTENTS, {}))
            blocks.append(NotionBlock(NotionBlockType.DIVIDER, {}))
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            if not para.strip():
                continue
            
            # Check for headings (simple pattern matching)
            if para.startswith('# '):
                blocks.append(NotionBlock(
                    NotionBlockType.HEADING_1,
                    para[2:].strip()
                ))
            elif para.startswith('## '):
                blocks.append(NotionBlock(
                    NotionBlockType.HEADING_2,
                    para[3:].strip()
                ))
            elif para.startswith('### '):
                blocks.append(NotionBlock(
                    NotionBlockType.HEADING_3,
                    para[4:].strip()
                ))
            elif para.startswith('- '):
                # Bullet points
                items = para.split('\n')
                for item in items:
                    if item.startswith('- '):
                        blocks.append(NotionBlock(
                            NotionBlockType.BULLETED_LIST_ITEM,
                            item[2:].strip()
                        ))
            else:
                # Regular paragraph
                blocks.append(NotionBlock(
                    NotionBlockType.PARAGRAPH,
                    para.strip()
                ))
        
        # Add call-to-action at the end
        blocks.append(NotionBlock(NotionBlockType.DIVIDER, {}))
        blocks.append(NotionBlock(
            NotionBlockType.CALLOUT,
            {
                "text": "Ready to transform your business? Contact us to learn more about our solutions.",
                "emoji": "🚀",
                "color": "blue_background"
            }
        ))
        
        return blocks
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')
    
    def _get_category_from_format(self, content_format: ContentFormat) -> str:
        """Determine blog category from content format"""
        category_map = {
            ContentFormat.EPIC_PILLAR_ARTICLE: "Pillar Content",
            ContentFormat.AI_SEARCH_BLOG: "SEO Content",
            ContentFormat.BLOG_SUPPORTING_1: "Supporting Content",
            ContentFormat.BLOG_SUPPORTING_2: "Supporting Content",
            ContentFormat.BLOG_SUPPORTING_3: "Supporting Content",
            ContentFormat.ADVERTORIAL: "Sponsored Content",
            ContentFormat.PILLAR_PODCAST: "Podcast"
        }
        
        return category_map.get(content_format, "Blog Post")
    
    def _generate_meta_description(self, content_piece: ContentPiece) -> str:
        """Generate SEO meta description"""
        brief = content_piece.content_brief
        
        # Take first 150 characters and clean up
        if len(brief) > 150:
            meta = brief[:147] + "..."
        else:
            meta = brief
        
        # Remove line breaks and extra spaces
        meta = ' '.join(meta.split())
        
        return meta
    
    def _extract_title(self, properties: Dict[str, Any]) -> str:
        """Extract title from Notion properties"""
        title_prop = properties.get("Title", {})
        if title_prop.get("title"):
            return title_prop["title"][0].get("text", {}).get("content", "")
        return ""
    
    def _extract_select(self, properties: Dict[str, Any], property_name: str) -> str:
        """Extract select value from Notion properties"""
        select_prop = properties.get(property_name, {})
        if select_prop.get("select"):
            return select_prop["select"].get("name", "")
        return ""
    
    def _extract_date(self, properties: Dict[str, Any], property_name: str) -> Optional[str]:
        """Extract date from Notion properties"""
        date_prop = properties.get(property_name, {})
        if date_prop.get("date"):
            return date_prop["date"].get("start")
        return None
    
    async def _get_capabilities(self) -> List[str]:
        """Get Notion MCP server capabilities"""
        try:
            response = await self.session.get(
                f"{self.mcp_endpoint}/capabilities",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json().get("capabilities", [])
            else:
                return ["unknown"]
                
        except Exception:
            return ["basic_operations"]
    
    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()


# Utility functions
async def test_notion_mcp_connection(mcp_endpoint: str = "http://localhost:3001") -> Dict[str, Any]:
    """Test Notion MCP connection and capabilities"""
    client = NotionMCPClient(mcp_endpoint)
    
    try:
        connection_test = await client.test_connection()
        return connection_test
    finally:
        await client.close()


async def quick_publish_to_notion(
    notion_client: NotionMCPClient,
    database_id: str,
    title: str,
    content: str,
    tags: List[str] = None
) -> Dict[str, Any]:
    """Quick utility to publish a simple blog post"""
    
    blog_post = NotionBlogPost(
        title=title,
        content_blocks=[NotionBlock(NotionBlockType.PARAGRAPH, content)],
        meta_description=content[:150],
        slug=notion_client._generate_slug(title),
        tags=tags or ["blog"],
        category="Blog Post",
        author="Brand BOS",
        status=PublishStatus.PUBLISHED
    )
    
    return await notion_client.create_blog_post(database_id, blog_post)