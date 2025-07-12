"""
GoHighLevel MCP Integration Client for Brand BOS
Connects to GHL MCP for social media posting automation and brand settings management
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import httpx

from ..database.cartwheel_models import ContentPiece, ContentFormat
from ..database.models import CIASession

logger = logging.getLogger(__name__)


class GHLSocialPlatform(Enum):
    """Supported GHL social platforms"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    GOOGLE_MY_BUSINESS = "google_my_business"


class PostStatus(Enum):
    """Post scheduling status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class GHLSocialPost:
    """GHL social media post structure"""
    content: str
    platforms: List[GHLSocialPlatform]
    media_urls: List[str] = None
    scheduled_time: Optional[datetime] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    link_url: Optional[str] = None
    
    # Brand BOS specific fields
    content_id: Optional[str] = None
    cluster_id: Optional[str] = None
    campaign_name: Optional[str] = None
    utm_parameters: Optional[Dict[str, str]] = None
    
    def to_ghl_format(self) -> Dict[str, Any]:
        """Convert to GHL MCP format"""
        post_data = {
            "message": self.content,
            "platforms": [platform.value for platform in self.platforms],
            "status": "scheduled" if self.scheduled_time else "draft"
        }
        
        if self.media_urls:
            post_data["media"] = self.media_urls
        
        if self.scheduled_time:
            post_data["scheduledAt"] = self.scheduled_time.isoformat()
        
        if self.hashtags:
            post_data["hashtags"] = self.hashtags
        
        if self.link_url:
            post_data["linkUrl"] = self.link_url
        
        # Add Brand BOS metadata
        if self.content_id or self.cluster_id:
            post_data["metadata"] = {
                "brandBOS": {
                    "contentId": self.content_id,
                    "clusterId": self.cluster_id,
                    "campaignName": self.campaign_name,
                    "utmParameters": self.utm_parameters
                }
            }
        
        return post_data


@dataclass
class GHLBrandSettings:
    """GHL brand settings for consistent posting"""
    business_name: str
    brand_voice: str
    brand_colors: List[str]
    logo_url: str
    website_url: str
    
    # Messaging
    value_proposition: str
    key_messages: List[str]
    call_to_action: str
    
    # Platform-specific settings
    platform_handles: Dict[str, str]  # platform -> handle
    platform_bio: Dict[str, str]     # platform -> bio
    
    # Posting preferences
    optimal_times: Dict[str, List[str]]  # platform -> times
    hashtag_strategy: Dict[str, List[str]]  # platform -> hashtags
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class GHLMCPClient:
    """GoHighLevel MCP client for Brand BOS integration"""
    
    def __init__(self, mcp_endpoint: str = "http://localhost:3000", api_key: Optional[str] = None):
        """
        Initialize GHL MCP client
        
        Args:
            mcp_endpoint: GHL MCP server endpoint
            api_key: API key for authentication
        """
        self.mcp_endpoint = mcp_endpoint.rstrip('/')
        self.api_key = api_key
        self.session = httpx.AsyncClient(timeout=30.0)
        
        # Headers for requests
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "BrandBOS/1.0"
        }
        
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to GHL MCP server"""
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
            logger.error(f"GHL MCP connection test failed: {e}")
            return {
                "connected": False,
                "status": "error", 
                "error": str(e)
            }
    
    async def get_connected_platforms(self, location_id: str) -> List[Dict[str, Any]]:
        """Get connected social platforms for a GHL location"""
        try:
            response = await self.session.get(
                f"{self.mcp_endpoint}/social/platforms/{location_id}",
                headers=self.headers
            )
            response.raise_for_status()
            
            platforms = response.json().get("platforms", [])
            
            logger.info(f"Found {len(platforms)} connected platforms for location {location_id}")
            return platforms
            
        except Exception as e:
            logger.error(f"Failed to get connected platforms: {e}")
            return []
    
    async def create_social_post(
        self,
        location_id: str,
        post: GHLSocialPost
    ) -> Dict[str, Any]:
        """Create a social media post in GHL"""
        try:
            post_data = post.to_ghl_format()
            post_data["locationId"] = location_id
            
            response = await self.session.post(
                f"{self.mcp_endpoint}/social/posts",
                headers=self.headers,
                json=post_data
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"Created social post for platforms: {[p.value for p in post.platforms]}")
            return {
                "success": True,
                "post_id": result.get("id"),
                "status": result.get("status"),
                "scheduled_for": post.scheduled_time.isoformat() if post.scheduled_time else None,
                "platforms": [p.value for p in post.platforms]
            }
            
        except Exception as e:
            logger.error(f"Failed to create social post: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def schedule_content_cluster(
        self,
        location_id: str,
        content_pieces: List[ContentPiece],
        start_date: datetime,
        posting_schedule: Dict[str, List[str]]  # platform -> times
    ) -> List[Dict[str, Any]]:
        """Schedule an entire content cluster across platforms"""
        try:
            scheduled_posts = []
            current_date = start_date
            
            for i, content_piece in enumerate(content_pieces):
                # Determine optimal platforms for content format
                platforms = self._get_platforms_for_format(content_piece.format)
                
                # Calculate posting time
                posting_time = self._calculate_posting_time(
                    current_date, 
                    platforms[0] if platforms else GHLSocialPlatform.FACEBOOK,
                    posting_schedule
                )
                
                # Create post content
                post_content = self._format_content_for_social(content_piece)
                
                # Create GHL post
                ghl_post = GHLSocialPost(
                    content=post_content,
                    platforms=platforms,
                    scheduled_time=posting_time,
                    hashtags=self._generate_hashtags(content_piece),
                    link_url=f"https://example.com/content/{content_piece.id}",
                    content_id=content_piece.id,
                    cluster_id=content_piece.cluster_id,
                    campaign_name=f"BBOS_cluster_{content_piece.cluster_id}",
                    utm_parameters={
                        "utm_source": "social_media",
                        "utm_medium": "organic",
                        "utm_campaign": f"cluster_{content_piece.cluster_id}",
                        "utm_content": content_piece.id
                    }
                )
                
                # Schedule the post
                result = await self.create_social_post(location_id, ghl_post)
                scheduled_posts.append({
                    "content_piece_id": content_piece.id,
                    "scheduled_time": posting_time.isoformat(),
                    "platforms": [p.value for p in platforms],
                    "result": result
                })
                
                # Increment date for next post (spread across days)
                current_date += timedelta(days=1)
            
            logger.info(f"Scheduled {len(scheduled_posts)} posts for content cluster")
            return scheduled_posts
            
        except Exception as e:
            logger.error(f"Failed to schedule content cluster: {e}")
            return []
    
    async def update_brand_settings(
        self,
        location_id: str,
        brand_settings: GHLBrandSettings
    ) -> Dict[str, Any]:
        """Update GHL brand settings with CIA intelligence"""
        try:
            settings_data = brand_settings.to_dict()
            settings_data["locationId"] = location_id
            
            response = await self.session.put(
                f"{self.mcp_endpoint}/brand/settings/{location_id}",
                headers=self.headers,
                json=settings_data
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"Updated brand settings for location {location_id}")
            return {
                "success": True,
                "updated_settings": result.get("settings", {}),
                "changes_applied": result.get("changes", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to update brand settings: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_post_performance(
        self,
        location_id: str,
        start_date: datetime,
        end_date: datetime,
        platforms: Optional[List[GHLSocialPlatform]] = None
    ) -> Dict[str, Any]:
        """Get social media performance data from GHL"""
        try:
            params = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat()
            }
            
            if platforms:
                params["platforms"] = [p.value for p in platforms]
            
            response = await self.session.get(
                f"{self.mcp_endpoint}/social/analytics/{location_id}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            performance_data = response.json()
            
            logger.info(f"Retrieved performance data for {len(performance_data.get('posts', []))} posts")
            return performance_data
            
        except Exception as e:
            logger.error(f"Failed to get post performance: {e}")
            return {"error": str(e)}
    
    async def sync_cia_to_brand_settings(
        self,
        location_id: str,
        cia_session: CIASession
    ) -> Dict[str, Any]:
        """Sync CIA intelligence to GHL brand settings"""
        try:
            # Extract brand intelligence from CIA session
            # This would be populated from actual CIA analysis
            cia_data = getattr(cia_session, 'intelligence_data', {})
            
            # Create enhanced brand settings
            brand_settings = GHLBrandSettings(
                business_name=cia_session.company_name,
                brand_voice=cia_data.get("brand_voice", "Professional and authoritative"),
                brand_colors=cia_data.get("brand_colors", ["#1f2937", "#3b82f6"]),
                logo_url=cia_data.get("logo_url", ""),
                website_url=cia_session.url,
                value_proposition=cia_data.get("value_proposition", "Leading solutions for business growth"),
                key_messages=cia_data.get("key_messages", ["Innovation", "Quality", "Results"]),
                call_to_action=cia_data.get("cta", "Learn more"),
                platform_handles={
                    "facebook": f"@{cia_session.company_name.lower().replace(' ', '')}",
                    "instagram": f"@{cia_session.company_name.lower().replace(' ', '')}",
                    "linkedin": f"@{cia_session.company_name.lower().replace(' ', '')}"
                },
                platform_bio={
                    "facebook": f"{cia_data.get('value_proposition', 'Business solutions')} | {cia_session.country}",
                    "instagram": f"{cia_data.get('value_proposition', 'Business solutions')} ✨",
                    "linkedin": f"{cia_data.get('value_proposition', 'Business solutions')} | Connect with {cia_session.kpoi}"
                },
                optimal_times={
                    "facebook": ["09:00", "15:00", "20:00"],
                    "instagram": ["11:00", "14:00", "17:00"],
                    "linkedin": ["08:00", "12:00", "17:00"]
                },
                hashtag_strategy=cia_data.get("hashtag_strategy", {
                    "facebook": ["#business", "#growth", "#innovation"],
                    "instagram": ["#business", "#entrepreneur", "#success"],
                    "linkedin": ["#business", "#leadership", "#growth"]
                })
            )
            
            # Update GHL brand settings
            result = await self.update_brand_settings(location_id, brand_settings)
            
            if result.get("success"):
                logger.info(f"Successfully synced CIA intelligence to GHL brand settings")
                return {
                    "success": True,
                    "cia_session_id": cia_session.id,
                    "location_id": location_id,
                    "brand_improvements": [
                        "Updated value proposition",
                        "Enhanced platform bios",
                        "Optimized posting times",
                        "Strategic hashtag sets"
                    ],
                    "settings_updated": result.get("updated_settings", {})
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Failed to sync CIA to brand settings: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_capabilities(self) -> List[str]:
        """Get GHL MCP server capabilities"""
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
            return ["basic_posting"]
    
    def _get_platforms_for_format(self, content_format: ContentFormat) -> List[GHLSocialPlatform]:
        """Determine optimal platforms based on content format"""
        platform_map = {
            ContentFormat.LINKEDIN_ARTICLE: [GHLSocialPlatform.LINKEDIN],
            ContentFormat.X_THREAD: [GHLSocialPlatform.TWITTER],
            ContentFormat.INSTAGRAM_POST: [GHLSocialPlatform.INSTAGRAM],
            ContentFormat.META_FACEBOOK_POST: [GHLSocialPlatform.FACEBOOK],
            ContentFormat.TIKTOK_UGC: [GHLSocialPlatform.TIKTOK],
            ContentFormat.YOUTUBE_SHORTS: [GHLSocialPlatform.YOUTUBE],
            # Default multi-platform for blog content
            ContentFormat.AI_SEARCH_BLOG: [GHLSocialPlatform.LINKEDIN, GHLSocialPlatform.FACEBOOK],
            ContentFormat.EPIC_PILLAR_ARTICLE: [GHLSocialPlatform.LINKEDIN, GHLSocialPlatform.FACEBOOK]
        }
        
        return platform_map.get(content_format, [GHLSocialPlatform.FACEBOOK])
    
    def _calculate_posting_time(
        self,
        base_date: datetime,
        platform: GHLSocialPlatform,
        posting_schedule: Dict[str, List[str]]
    ) -> datetime:
        """Calculate optimal posting time for platform"""
        platform_times = posting_schedule.get(platform.value, ["12:00"])
        optimal_time = platform_times[0]  # Use first optimal time
        
        # Parse time and set on base date
        hour, minute = optimal_time.split(":")
        posting_time = base_date.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
        
        return posting_time
    
    def _format_content_for_social(self, content_piece: ContentPiece) -> str:
        """Format content piece for social media posting"""
        # Extract key points from content brief
        brief = getattr(content_piece, 'content_brief', content_piece.title)
        
        # Create engaging social post
        social_content = f"🚀 {content_piece.title}\n\n"
        
        # Add brief excerpt (first 100 characters)
        if len(brief) > 100:
            social_content += f"{brief[:100]}...\n\n"
        else:
            social_content += f"{brief}\n\n"
        
        social_content += "Read more 👇"
        
        return social_content
    
    def _generate_hashtags(self, content_piece: ContentPiece) -> List[str]:
        """Generate hashtags based on content keywords"""
        keywords = getattr(content_piece, 'seo_keywords', [])
        
        # Convert keywords to hashtags
        hashtags = [f"#{keyword.replace(' ', '').lower()}" for keyword in keywords[:5]]
        
        # Add general brand hashtags
        hashtags.extend(["#business", "#growth", "#brandBOS"])
        
        return hashtags[:10]  # Limit to 10 hashtags
    
    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()


# Utility functions for GHL integration
async def test_ghl_mcp_connection(mcp_endpoint: str = "http://localhost:3000") -> Dict[str, Any]:
    """Test GHL MCP connection and capabilities"""
    client = GHLMCPClient(mcp_endpoint)
    
    try:
        connection_test = await client.test_connection()
        return connection_test
    finally:
        await client.close()


async def schedule_weekly_content_cluster(
    ghl_client: GHLMCPClient,
    location_id: str,
    content_pieces: List[ContentPiece],
    start_monday: datetime
) -> Dict[str, Any]:
    """Schedule a week's worth of content cluster posts"""
    
    # Default posting schedule (optimal times per platform)
    posting_schedule = {
        "facebook": ["09:00", "15:00", "20:00"],
        "instagram": ["11:00", "14:00", "17:00"],  
        "linkedin": ["08:00", "12:00", "17:00"],
        "twitter": ["09:00", "13:00", "18:00"],
        "tiktok": ["16:00", "19:00", "21:00"]
    }
    
    try:
        scheduled_posts = await ghl_client.schedule_content_cluster(
            location_id=location_id,
            content_pieces=content_pieces,
            start_date=start_monday,
            posting_schedule=posting_schedule
        )
        
        return {
            "success": True,
            "cluster_id": content_pieces[0].cluster_id if content_pieces else None,
            "week_start": start_monday.isoformat(),
            "scheduled_posts": len(scheduled_posts),
            "posts_detail": scheduled_posts
        }
        
    except Exception as e:
        logger.error(f"Failed to schedule weekly content cluster: {e}")
        return {
            "success": False,
            "error": str(e)
        }