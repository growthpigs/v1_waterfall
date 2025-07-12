"""
Blog Publishing System for Brand BOS
Formats and publishes Cartwheel-generated content to Notion
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import re
from uuid import UUID

from ..database.cartwheel_models import ContentPiece, ContentCluster, ContentFormat
from ..database.models import CIASession
from ..integrations.notion_mcp_client import (
    NotionMCPClient,
    NotionBlogPost,
    NotionBlock,
    NotionBlockType,
    NotionRichText,
    PublishStatus
)
from ..integrations.utm_automation import UTMGenerator, UTMSource, UTMMedium

logger = logging.getLogger(__name__)


class ContentStructure(Enum):
    """Blog content structure types"""
    PILLAR = "pillar"
    SUPPORTING = "supporting"
    STANDALONE = "standalone"


@dataclass
class BlogFormattingConfig:
    """Configuration for blog formatting"""
    # Structure settings
    add_table_of_contents: bool = True
    add_introduction: bool = True
    add_conclusion: bool = True
    add_cta_sections: bool = True
    
    # SEO settings
    target_meta_length: int = 155
    focus_keyword_density: float = 0.02  # 2%
    internal_link_count: int = 3
    
    # Visual settings
    add_featured_image: bool = True
    add_section_images: bool = True
    image_alt_optimization: bool = True
    
    # Branding
    brand_voice: str = "professional"
    cta_style: str = "soft"  # soft, medium, hard
    
    @classmethod
    def from_cia_session(cls, cia_session: CIASession) -> 'BlogFormattingConfig':
        """Create config from CIA intelligence"""
        # Extract brand voice and style from CIA data
        intelligence_data = getattr(cia_session, 'intelligence_data', {})
        
        return cls(
            brand_voice=intelligence_data.get('brand_voice', 'professional'),
            cta_style=intelligence_data.get('cta_intensity', 'medium'),
            focus_keyword_density=intelligence_data.get('keyword_density', 0.02)
        )


@dataclass
class InternalLink:
    """Internal link structure"""
    anchor_text: str
    target_url: str
    target_content_id: str
    relevance_score: float


class BlogPublisher:
    """Main blog publishing engine for Brand BOS"""
    
    def __init__(
        self,
        notion_client: NotionMCPClient,
        utm_generator: UTMGenerator,
        default_config: Optional[BlogFormattingConfig] = None
    ):
        """
        Initialize blog publisher
        
        Args:
            notion_client: Notion MCP client
            utm_generator: UTM parameter generator
            default_config: Default formatting configuration
        """
        self.notion_client = notion_client
        self.utm_generator = utm_generator
        self.config = default_config or BlogFormattingConfig()
        
        # Content patterns for formatting
        self.heading_pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
        self.list_pattern = re.compile(r'^[-*]\s+(.+)$', re.MULTILINE)
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    async def publish_content_piece(
        self,
        database_id: str,
        content_piece: ContentPiece,
        cia_session: Optional[CIASession] = None,
        related_content: Optional[List[ContentPiece]] = None,
        config_override: Optional[BlogFormattingConfig] = None
    ) -> Dict[str, Any]:
        """
        Publish a formatted content piece as a blog post
        
        Args:
            database_id: Notion database ID
            content_piece: Content to publish
            cia_session: CIA session for intelligence
            related_content: Related content for internal linking
            config_override: Override default config
            
        Returns:
            Publishing result
        """
        try:
            # Use override config or create from CIA session
            config = config_override or (
                BlogFormattingConfig.from_cia_session(cia_session) 
                if cia_session else self.config
            )
            
            # Format content into blog structure
            formatted_blocks = await self._format_content_to_blog(
                content_piece,
                cia_session,
                related_content,
                config
            )
            
            # Generate SEO metadata
            seo_metadata = self._generate_seo_metadata(
                content_piece,
                cia_session,
                config
            )
            
            # Create blog post
            blog_post = NotionBlogPost(
                title=content_piece.title,
                content_blocks=formatted_blocks,
                meta_description=seo_metadata['meta_description'],
                slug=seo_metadata['slug'],
                tags=seo_metadata['tags'],
                category=seo_metadata['category'],
                author=cia_session.kpoi if cia_session else "Brand BOS Team",
                publish_date=datetime.now() if content_piece.content_status == "ready" else None,
                status=PublishStatus.PUBLISHED if content_piece.content_status == "ready" else PublishStatus.DRAFT,
                featured_image=seo_metadata.get('featured_image'),
                content_id=content_piece.id,
                cluster_id=content_piece.cluster_id,
                utm_parameters=self._generate_utm_params(content_piece),
                internal_links=seo_metadata.get('internal_links')
            )
            
            # Publish to Notion
            result = await self.notion_client.create_blog_post(database_id, blog_post)
            
            if result.get("success"):
                logger.info(f"Successfully published blog post: {content_piece.title}")
                return {
                    "success": True,
                    "content_id": content_piece.id,
                    "page_id": result.get("page_id"),
                    "url": result.get("url"),
                    "seo_score": self._calculate_seo_score(blog_post, config),
                    "internal_links_added": len(seo_metadata.get('internal_links', [])),
                    "publish_status": blog_post.status.value
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Failed to publish content piece: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def publish_content_cluster(
        self,
        database_id: str,
        content_cluster: ContentCluster,
        content_pieces: List[ContentPiece],
        cia_session: Optional[CIASession] = None,
        stagger_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Publish an entire content cluster with proper interlinking
        
        Args:
            database_id: Notion database ID
            content_cluster: Content cluster
            content_pieces: List of content pieces
            cia_session: CIA session for intelligence
            stagger_hours: Hours between publishing
            
        Returns:
            Cluster publishing results
        """
        try:
            results = []
            published_content = {}  # Track published content for linking
            base_time = datetime.now()
            
            # Sort content by type (pillar first, then supporting)
            sorted_pieces = self._sort_content_by_hierarchy(content_pieces)
            
            for i, content_piece in enumerate(sorted_pieces):
                # Calculate publish time
                publish_time = base_time + timedelta(hours=i * stagger_hours)
                
                # Get already published content for internal linking
                related_content = [
                    piece for piece in sorted_pieces[:i]
                    if piece.id in published_content
                ]
                
                # Publish content
                result = await self.publish_content_piece(
                    database_id=database_id,
                    content_piece=content_piece,
                    cia_session=cia_session,
                    related_content=related_content
                )
                
                if result.get("success"):
                    published_content[content_piece.id] = result.get("url")
                
                results.append({
                    "content_piece_id": content_piece.id,
                    "title": content_piece.title,
                    "format": content_piece.format.value,
                    "publish_time": publish_time.isoformat(),
                    "result": result
                })
                
                # Small delay between API calls
                await asyncio.sleep(0.5)
            
            # Calculate cluster-wide metrics
            successful_publishes = sum(1 for r in results if r["result"].get("success"))
            
            return {
                "success": successful_publishes > 0,
                "cluster_id": content_cluster.id,
                "total_pieces": len(content_pieces),
                "published": successful_publishes,
                "failed": len(content_pieces) - successful_publishes,
                "publishing_schedule": results,
                "internal_link_network": self._generate_link_network_summary(results)
            }
            
        except Exception as e:
            logger.error(f"Failed to publish content cluster: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _format_content_to_blog(
        self,
        content_piece: ContentPiece,
        cia_session: Optional[CIASession],
        related_content: Optional[List[ContentPiece]],
        config: BlogFormattingConfig
    ) -> List[NotionBlock]:
        """Format content piece into structured blog blocks"""
        blocks = []
        
        # Add table of contents for long content
        if config.add_table_of_contents and content_piece.target_word_count > 1500:
            blocks.append(NotionBlock(NotionBlockType.TABLE_OF_CONTENTS, {}))
        
        # Add introduction if configured
        if config.add_introduction:
            intro_block = self._create_introduction(content_piece, cia_session)
            blocks.append(intro_block)
            blocks.append(NotionBlock(NotionBlockType.DIVIDER, {}))
        
        # Parse and format main content
        main_blocks = self._parse_content_structure(content_piece.content_brief)
        
        # Add internal links if related content available
        if related_content:
            main_blocks = self._add_internal_links(main_blocks, related_content)
        
        blocks.extend(main_blocks)
        
        # Add conclusion if configured
        if config.add_conclusion:
            blocks.append(NotionBlock(NotionBlockType.DIVIDER, {}))
            conclusion_block = self._create_conclusion(content_piece, cia_session)
            blocks.append(conclusion_block)
        
        # Add CTA sections if configured
        if config.add_cta_sections:
            blocks.append(NotionBlock(NotionBlockType.DIVIDER, {}))
            cta_blocks = self._create_cta_section(content_piece, cia_session, config)
            blocks.extend(cta_blocks)
        
        return blocks
    
    def _parse_content_structure(self, content: str) -> List[NotionBlock]:
        """Parse content into structured blocks"""
        blocks = []
        lines = content.split('\n')
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # Empty line - end current paragraph
                if current_paragraph:
                    blocks.append(NotionBlock(
                        NotionBlockType.PARAGRAPH,
                        ' '.join(current_paragraph)
                    ))
                    current_paragraph = []
                continue
            
            # Check for headings
            heading_match = self.heading_pattern.match(line)
            if heading_match:
                # Save current paragraph first
                if current_paragraph:
                    blocks.append(NotionBlock(
                        NotionBlockType.PARAGRAPH,
                        ' '.join(current_paragraph)
                    ))
                    current_paragraph = []
                
                # Add heading
                level = len(heading_match.group(1))
                heading_type = [
                    NotionBlockType.HEADING_1,
                    NotionBlockType.HEADING_2,
                    NotionBlockType.HEADING_3
                ][level - 1]
                
                blocks.append(NotionBlock(
                    heading_type,
                    heading_match.group(2)
                ))
                continue
            
            # Check for lists
            list_match = self.list_pattern.match(line)
            if list_match:
                # Save current paragraph first
                if current_paragraph:
                    blocks.append(NotionBlock(
                        NotionBlockType.PARAGRAPH,
                        ' '.join(current_paragraph)
                    ))
                    current_paragraph = []
                
                blocks.append(NotionBlock(
                    NotionBlockType.BULLETED_LIST_ITEM,
                    list_match.group(1)
                ))
                continue
            
            # Regular text - add to current paragraph
            current_paragraph.append(line)
        
        # Don't forget last paragraph
        if current_paragraph:
            blocks.append(NotionBlock(
                NotionBlockType.PARAGRAPH,
                ' '.join(current_paragraph)
            ))
        
        return blocks
    
    def _create_introduction(
        self,
        content_piece: ContentPiece,
        cia_session: Optional[CIASession]
    ) -> NotionBlock:
        """Create engaging introduction paragraph"""
        intro_text = f"Welcome to our comprehensive guide on {content_piece.title}. "
        
        if cia_session:
            intro_text += f"At {cia_session.company_name}, we understand the importance of this topic for businesses in {cia_session.country}. "
        
        intro_text += "In this article, we'll explore the key insights and strategies you need to succeed."
        
        return NotionBlock(NotionBlockType.PARAGRAPH, intro_text)
    
    def _create_conclusion(
        self,
        content_piece: ContentPiece,
        cia_session: Optional[CIASession]
    ) -> NotionBlock:
        """Create compelling conclusion"""
        conclusion_text = f"We've covered the essential aspects of {content_piece.title}. "
        
        if hasattr(content_piece, 'seo_keywords') and content_piece.seo_keywords:
            conclusion_text += f"Remember the key points about {', '.join(content_piece.seo_keywords[:2])}. "
        
        if cia_session:
            conclusion_text += f"At {cia_session.company_name}, we're committed to helping you implement these strategies effectively."
        
        return NotionBlock(NotionBlockType.PARAGRAPH, conclusion_text)
    
    def _create_cta_section(
        self,
        content_piece: ContentPiece,
        cia_session: Optional[CIASession],
        config: BlogFormattingConfig
    ) -> List[NotionBlock]:
        """Create call-to-action section"""
        blocks = []
        
        # CTA heading
        blocks.append(NotionBlock(
            NotionBlockType.HEADING_2,
            "Ready to Take Action?"
        ))
        
        # CTA text based on style
        if config.cta_style == "soft":
            cta_text = "If you found this article helpful, we'd love to hear from you. Feel free to reach out with any questions."
        elif config.cta_style == "medium":
            cta_text = "Ready to implement these strategies in your business? Contact our team for personalized guidance and support."
        else:  # hard
            cta_text = "Don't wait to transform your business. Schedule a free consultation today and discover how we can help you achieve exceptional results."
        
        blocks.append(NotionBlock(NotionBlockType.PARAGRAPH, cta_text))
        
        # CTA callout
        blocks.append(NotionBlock(
            NotionBlockType.CALLOUT,
            {
                "text": "📞 Contact us today for a free consultation",
                "emoji": "🚀",
                "color": "blue_background"
            }
        ))
        
        return blocks
    
    def _add_internal_links(
        self,
        blocks: List[NotionBlock],
        related_content: List[ContentPiece]
    ) -> List[NotionBlock]:
        """Add internal links to related content"""
        # For now, return blocks as-is
        # In production, would analyze text and add relevant links
        return blocks
    
    def _generate_seo_metadata(
        self,
        content_piece: ContentPiece,
        cia_session: Optional[CIASession],
        config: BlogFormattingConfig
    ) -> Dict[str, Any]:
        """Generate comprehensive SEO metadata"""
        # Generate slug
        slug = self._generate_seo_slug(content_piece.title)
        
        # Create meta description
        meta_description = self._create_meta_description(
            content_piece,
            config.target_meta_length
        )
        
        # Extract and optimize tags
        tags = self._optimize_tags(content_piece)
        
        # Determine category
        category = self._determine_category(content_piece.format)
        
        # Generate featured image placeholder
        featured_image = f"https://source.unsplash.com/1200x630/?{tags[0] if tags else 'business'}"
        
        return {
            "slug": slug,
            "meta_description": meta_description,
            "tags": tags,
            "category": category,
            "featured_image": featured_image,
            "internal_links": []  # Would be populated by link analysis
        }
    
    def _generate_seo_slug(self, title: str) -> str:
        """Generate SEO-optimized slug"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        # Limit length
        if len(slug) > 60:
            words = slug.split('-')
            slug = '-'.join(words[:8])
        
        return slug
    
    def _create_meta_description(
        self,
        content_piece: ContentPiece,
        target_length: int
    ) -> str:
        """Create optimized meta description"""
        brief = content_piece.content_brief
        
        # Clean and truncate
        meta = ' '.join(brief.split())
        
        if len(meta) > target_length:
            meta = meta[:target_length-3]
            last_space = meta.rfind(' ')
            if last_space > 0:
                meta = meta[:last_space]
            meta += "..."
        
        # Ensure it includes a keyword if possible
        if hasattr(content_piece, 'seo_keywords') and content_piece.seo_keywords:
            keyword = content_piece.seo_keywords[0].lower()
            if keyword not in meta.lower():
                # Try to naturally include the keyword
                if len(meta) + len(keyword) + 5 < target_length:
                    meta = f"{keyword.capitalize()} - {meta}"
        
        return meta
    
    def _optimize_tags(self, content_piece: ContentPiece) -> List[str]:
        """Optimize tags for SEO and discoverability"""
        tags = []
        
        # Start with SEO keywords
        if hasattr(content_piece, 'seo_keywords'):
            tags.extend(content_piece.seo_keywords[:5])
        
        # Add format-based tags
        format_tags = {
            ContentFormat.EPIC_PILLAR_ARTICLE: ["pillar-content", "ultimate-guide"],
            ContentFormat.AI_SEARCH_BLOG: ["seo-content", "search-optimized"],
            ContentFormat.BLOG_SUPPORTING_1: ["how-to", "tutorial"],
            ContentFormat.BLOG_SUPPORTING_2: ["tips", "best-practices"],
            ContentFormat.BLOG_SUPPORTING_3: ["guide", "resources"]
        }
        
        if content_piece.format in format_tags:
            tags.extend(format_tags[content_piece.format])
        
        # Clean and deduplicate
        tags = list(set(tag.lower().replace(' ', '-') for tag in tags))
        
        return tags[:10]  # Limit to 10 tags
    
    def _determine_category(self, content_format: ContentFormat) -> str:
        """Determine blog category from content format"""
        category_map = {
            ContentFormat.EPIC_PILLAR_ARTICLE: "Ultimate Guides",
            ContentFormat.AI_SEARCH_BLOG: "SEO Resources",
            ContentFormat.BLOG_SUPPORTING_1: "How-To Guides",
            ContentFormat.BLOG_SUPPORTING_2: "Tips & Tricks",
            ContentFormat.BLOG_SUPPORTING_3: "Industry Insights",
            ContentFormat.ADVERTORIAL: "Partner Content",
            ContentFormat.PILLAR_PODCAST: "Podcast Episodes"
        }
        
        return category_map.get(content_format, "Blog Posts")
    
    def _generate_utm_params(self, content_piece: ContentPiece) -> Dict[str, str]:
        """Generate UTM parameters for blog post"""
        utm_params = self.utm_generator.generate_content_utm(
            content_piece=content_piece,
            source=UTMSource.BLOG,
            medium=UTMMedium.ORGANIC,
            variation="A",
            version="v1"
        )
        
        return utm_params.to_dict()
    
    def _calculate_seo_score(
        self,
        blog_post: NotionBlogPost,
        config: BlogFormattingConfig
    ) -> float:
        """Calculate SEO optimization score"""
        score = 0.0
        max_score = 100.0
        
        # Title optimization (20 points)
        if len(blog_post.title) > 30 and len(blog_post.title) < 60:
            score += 20
        elif len(blog_post.title) > 20:
            score += 10
        
        # Meta description (20 points)
        if len(blog_post.meta_description) > 120 and len(blog_post.meta_description) < 160:
            score += 20
        elif len(blog_post.meta_description) > 50:
            score += 10
        
        # Slug optimization (10 points)
        if len(blog_post.slug) < 60 and '-' in blog_post.slug:
            score += 10
        
        # Tags present (10 points)
        if len(blog_post.tags) >= 3:
            score += 10
        elif len(blog_post.tags) >= 1:
            score += 5
        
        # Content structure (20 points)
        heading_count = sum(
            1 for block in blog_post.content_blocks
            if block.block_type in [
                NotionBlockType.HEADING_1,
                NotionBlockType.HEADING_2,
                NotionBlockType.HEADING_3
            ]
        )
        if heading_count >= 3:
            score += 20
        elif heading_count >= 1:
            score += 10
        
        # Internal links (10 points)
        if blog_post.internal_links and len(blog_post.internal_links) >= config.internal_link_count:
            score += 10
        elif blog_post.internal_links and len(blog_post.internal_links) >= 1:
            score += 5
        
        # Featured image (10 points)
        if blog_post.featured_image:
            score += 10
        
        return (score / max_score) * 100
    
    def _sort_content_by_hierarchy(self, content_pieces: List[ContentPiece]) -> List[ContentPiece]:
        """Sort content pieces by hierarchy (pillar first)"""
        hierarchy_order = {
            ContentFormat.EPIC_PILLAR_ARTICLE: 1,
            ContentFormat.AI_SEARCH_BLOG: 2,
            ContentFormat.PILLAR_PODCAST: 3,
            ContentFormat.BLOG_SUPPORTING_1: 4,
            ContentFormat.BLOG_SUPPORTING_2: 5,
            ContentFormat.BLOG_SUPPORTING_3: 6,
            ContentFormat.ADVERTORIAL: 7
        }
        
        # Add other formats with default order
        for piece in content_pieces:
            if piece.format not in hierarchy_order:
                hierarchy_order[piece.format] = 10
        
        return sorted(
            content_pieces,
            key=lambda p: hierarchy_order.get(p.format, 10)
        )
    
    def _generate_link_network_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of internal link network"""
        successful_posts = [
            r for r in results
            if r["result"].get("success")
        ]
        
        return {
            "total_posts": len(successful_posts),
            "pillar_content": len([
                r for r in successful_posts
                if "pillar" in r["format"].lower()
            ]),
            "supporting_content": len([
                r for r in successful_posts
                if "supporting" in r["format"].lower()
            ]),
            "potential_internal_links": len(successful_posts) * (len(successful_posts) - 1) // 2,
            "link_density": "optimal" if len(successful_posts) >= 3 else "low"
        }


# Utility functions
import asyncio

async def test_blog_formatting(content_piece: ContentPiece) -> Dict[str, Any]:
    """Test blog formatting without publishing"""
    
    notion_client = NotionMCPClient()
    utm_generator = UTMGenerator()
    publisher = BlogPublisher(notion_client, utm_generator)
    
    try:
        # Format content
        blocks = await publisher._format_content_to_blog(
            content_piece,
            None,
            None,
            BlogFormattingConfig()
        )
        
        # Generate metadata
        metadata = publisher._generate_seo_metadata(
            content_piece,
            None,
            BlogFormattingConfig()
        )
        
        return {
            "success": True,
            "block_count": len(blocks),
            "block_types": list(set(block.block_type.value for block in blocks)),
            "seo_metadata": metadata,
            "estimated_read_time": content_piece.target_word_count // 200  # 200 words per minute
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        await notion_client.close()


async def publish_with_buildfast_sync(
    publisher: BlogPublisher,
    database_id: str,
    content_pieces: List[ContentPiece],
    buildfast_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Publish content and prepare for BuildFast sync"""
    
    # Publish content
    published_pages = []
    
    for content_piece in content_pieces:
        result = await publisher.publish_content_piece(
            database_id,
            content_piece
        )
        
        if result.get("success"):
            published_pages.append(result.get("page_id"))
    
    # Sync with BuildFast
    if published_pages:
        sync_result = await publisher.notion_client.sync_with_buildfast(
            published_pages,
            buildfast_config
        )
        
        return {
            "published_count": len(published_pages),
            "buildfast_sync": sync_result,
            "next_sync": "24_hours"
        }
    
    return {
        "published_count": 0,
        "buildfast_sync": {"success": False},
        "error": "No pages published"
    }