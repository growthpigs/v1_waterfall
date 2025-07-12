"""
Content Calendar System for Brand BOS
Manages weekly content cluster scheduling and GHL MCP integration
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, time
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from uuid import UUID, uuid4

from ..database.cartwheel_models import ContentPiece, ContentCluster, ContentFormat
from ..database.models import CIASession
from ..integrations.ghl_mcp_client import GHLMCPClient, GHLSocialPost, GHLSocialPlatform
from ..analytics.content_attribution import ContentAttributionEngine

logger = logging.getLogger(__name__)


class ScheduleStatus(Enum):
    """Content schedule status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PostingFrequency(Enum):
    """Posting frequency options"""
    DAILY = "daily"
    EVERY_OTHER_DAY = "every_other_day"
    WEEKDAYS_ONLY = "weekdays_only"
    CUSTOM = "custom"


@dataclass
class PostingTimeSlot:
    """Optimal posting time for a platform"""
    platform: GHLSocialPlatform
    time: time
    timezone: str = "UTC"
    engagement_score: float = 0.0
    
    def to_datetime(self, date: datetime) -> datetime:
        """Convert to datetime on specific date"""
        return date.replace(
            hour=self.time.hour,
            minute=self.time.minute,
            second=0,
            microsecond=0
        )


@dataclass
class ContentScheduleItem:
    """Individual content piece in the schedule"""
    id: str
    content_piece: ContentPiece
    scheduled_time: datetime
    platforms: List[GHLSocialPlatform]
    status: ScheduleStatus
    ghl_post_id: Optional[str] = None
    utm_parameters: Optional[Dict[str, str]] = None
    performance_data: Optional[Dict[str, Any]] = None
    
    # Posting metadata
    hashtags: List[str] = None
    mentions: List[str] = None
    media_urls: List[str] = None
    approval_status: str = "pending"  # pending, approved, rejected
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "content_id": self.content_piece.id,
            "content_title": self.content_piece.title,
            "content_format": self.content_piece.format.value,
            "scheduled_time": self.scheduled_time.isoformat(),
            "platforms": [p.value for p in self.platforms],
            "status": self.status.value,
            "ghl_post_id": self.ghl_post_id,
            "utm_parameters": self.utm_parameters,
            "hashtags": self.hashtags or [],
            "mentions": self.mentions or [],
            "media_urls": self.media_urls or [],
            "approval_status": self.approval_status
        }


@dataclass
class WeeklySchedule:
    """Weekly content schedule"""
    week_start: datetime  # Monday
    cluster_id: str
    location_id: str
    schedule_items: List[ContentScheduleItem]
    
    # Schedule metadata
    posting_frequency: PostingFrequency
    optimal_times: Dict[GHLSocialPlatform, List[PostingTimeSlot]]
    total_posts: int
    
    # Performance tracking
    scheduled_count: int = 0
    published_count: int = 0
    failed_count: int = 0
    
    @property
    def week_end(self) -> datetime:
        """End of week (Sunday)"""
        return self.week_start + timedelta(days=6)
    
    @property
    def completion_rate(self) -> float:
        """Completion rate percentage"""
        if self.total_posts == 0:
            return 0.0
        return (self.published_count / self.total_posts) * 100
    
    def get_schedule_by_day(self) -> Dict[str, List[ContentScheduleItem]]:
        """Group schedule items by day"""
        schedule_by_day = {}
        
        for item in self.schedule_items:
            day_key = item.scheduled_time.strftime("%Y-%m-%d")
            if day_key not in schedule_by_day:
                schedule_by_day[day_key] = []
            schedule_by_day[day_key].append(item)
        
        return schedule_by_day
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "week_start": self.week_start.isoformat(),
            "week_end": self.week_end.isoformat(),
            "cluster_id": self.cluster_id,
            "location_id": self.location_id,
            "posting_frequency": self.posting_frequency.value,
            "total_posts": self.total_posts,
            "scheduled_count": self.scheduled_count,
            "published_count": self.published_count,
            "failed_count": self.failed_count,
            "completion_rate": self.completion_rate,
            "schedule_items": [item.to_dict() for item in self.schedule_items],
            "schedule_by_day": self.get_schedule_by_day()
        }


class ContentCalendar:
    """Main content calendar system"""
    
    def __init__(self, ghl_client: GHLMCPClient):
        """
        Initialize content calendar
        
        Args:
            ghl_client: GHL MCP client for posting
        """
        self.ghl_client = ghl_client
        self.schedules: Dict[str, WeeklySchedule] = {}
        
        # Default optimal posting times
        self.default_posting_times = {
            GHLSocialPlatform.FACEBOOK: [
                PostingTimeSlot(GHLSocialPlatform.FACEBOOK, time(9, 0), engagement_score=85.0),
                PostingTimeSlot(GHLSocialPlatform.FACEBOOK, time(15, 0), engagement_score=90.0),
                PostingTimeSlot(GHLSocialPlatform.FACEBOOK, time(20, 0), engagement_score=88.0)
            ],
            GHLSocialPlatform.INSTAGRAM: [
                PostingTimeSlot(GHLSocialPlatform.INSTAGRAM, time(11, 0), engagement_score=92.0),
                PostingTimeSlot(GHLSocialPlatform.INSTAGRAM, time(14, 0), engagement_score=87.0),
                PostingTimeSlot(GHLSocialPlatform.INSTAGRAM, time(17, 0), engagement_score=89.0)
            ],
            GHLSocialPlatform.LINKEDIN: [
                PostingTimeSlot(GHLSocialPlatform.LINKEDIN, time(8, 0), engagement_score=91.0),
                PostingTimeSlot(GHLSocialPlatform.LINKEDIN, time(12, 0), engagement_score=94.0),
                PostingTimeSlot(GHLSocialPlatform.LINKEDIN, time(17, 0), engagement_score=88.0)
            ],
            GHLSocialPlatform.TWITTER: [
                PostingTimeSlot(GHLSocialPlatform.TWITTER, time(9, 0), engagement_score=86.0),
                PostingTimeSlot(GHLSocialPlatform.TWITTER, time(13, 0), engagement_score=89.0),
                PostingTimeSlot(GHLSocialPlatform.TWITTER, time(18, 0), engagement_score=91.0)
            ],
            GHLSocialPlatform.TIKTOK: [
                PostingTimeSlot(GHLSocialPlatform.TIKTOK, time(16, 0), engagement_score=93.0),
                PostingTimeSlot(GHLSocialPlatform.TIKTOK, time(19, 0), engagement_score=95.0),
                PostingTimeSlot(GHLSocialPlatform.TIKTOK, time(21, 0), engagement_score=92.0)
            ]
        }
    
    async def create_weekly_schedule(
        self,
        content_cluster: ContentCluster,
        content_pieces: List[ContentPiece],
        location_id: str,
        week_start: datetime,
        posting_frequency: PostingFrequency = PostingFrequency.DAILY,
        custom_times: Optional[Dict[GHLSocialPlatform, List[time]]] = None
    ) -> WeeklySchedule:
        """
        Create a weekly content schedule
        
        Args:
            content_cluster: Content cluster to schedule
            content_pieces: List of content pieces to schedule
            location_id: GHL location ID
            week_start: Start of week (Monday)
            posting_frequency: How often to post
            custom_times: Custom posting times override
            
        Returns:
            Weekly schedule
        """
        try:
            # Get connected platforms for location
            connected_platforms = await self.ghl_client.get_connected_platforms(location_id)
            available_platforms = [
                GHLSocialPlatform(p["platform"]) 
                for p in connected_platforms 
                if p.get("connected", False)
            ]
            
            if not available_platforms:
                logger.warning(f"No connected platforms found for location {location_id}")
                available_platforms = [GHLSocialPlatform.FACEBOOK]  # Fallback
            
            # Generate posting schedule
            schedule_items = self._generate_schedule_items(
                content_pieces=content_pieces,
                week_start=week_start,
                available_platforms=available_platforms,
                posting_frequency=posting_frequency,
                custom_times=custom_times
            )
            
            # Create weekly schedule
            weekly_schedule = WeeklySchedule(
                week_start=week_start,
                cluster_id=content_cluster.id,
                location_id=location_id,
                schedule_items=schedule_items,
                posting_frequency=posting_frequency,
                optimal_times=self._get_optimal_times(available_platforms, custom_times),
                total_posts=len(schedule_items)
            )
            
            # Store schedule
            schedule_key = f"{content_cluster.id}_{week_start.strftime('%Y-%m-%d')}"
            self.schedules[schedule_key] = weekly_schedule
            
            logger.info(f"Created weekly schedule for cluster {content_cluster.id} with {len(schedule_items)} posts")
            return weekly_schedule
            
        except Exception as e:
            logger.error(f"Failed to create weekly schedule: {e}")
            raise
    
    async def execute_schedule(
        self,
        schedule: WeeklySchedule,
        auto_approve: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a weekly schedule by posting to GHL
        
        Args:
            schedule: Weekly schedule to execute
            auto_approve: Auto-approve all content
            
        Returns:
            Execution results
        """
        try:
            results = {
                "scheduled": 0,
                "failed": 0,
                "skipped": 0,
                "posts": []
            }
            
            for item in schedule.schedule_items:
                # Check approval status
                if not auto_approve and item.approval_status != "approved":
                    results["skipped"] += 1
                    continue
                
                # Create GHL social post
                ghl_post = GHLSocialPost(
                    content=self._format_social_content(item.content_piece),
                    platforms=item.platforms,
                    scheduled_time=item.scheduled_time,
                    hashtags=item.hashtags or self._generate_hashtags(item.content_piece),
                    mentions=item.mentions,
                    media_urls=item.media_urls,
                    link_url=f"https://example.com/content/{item.content_piece.id}",
                    content_id=item.content_piece.id,
                    cluster_id=schedule.cluster_id,
                    campaign_name=f"BBOS_cluster_{schedule.cluster_id}",
                    utm_parameters=item.utm_parameters
                )
                
                # Post to GHL
                post_result = await self.ghl_client.create_social_post(
                    location_id=schedule.location_id,
                    post=ghl_post
                )
                
                if post_result.get("success"):
                    item.status = ScheduleStatus.SCHEDULED
                    item.ghl_post_id = post_result.get("post_id")
                    results["scheduled"] += 1
                    schedule.scheduled_count += 1
                else:
                    item.status = ScheduleStatus.FAILED
                    results["failed"] += 1
                    schedule.failed_count += 1
                
                results["posts"].append({
                    "item_id": item.id,
                    "content_title": item.content_piece.title,
                    "scheduled_time": item.scheduled_time.isoformat(),
                    "platforms": [p.value for p in item.platforms],
                    "status": item.status.value,
                    "ghl_post_id": item.ghl_post_id,
                    "result": post_result
                })
            
            logger.info(f"Schedule execution completed: {results['scheduled']} scheduled, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Schedule execution failed: {e}")
            raise
    
    async def get_schedule_status(
        self,
        cluster_id: str,
        week_start: datetime
    ) -> Optional[Dict[str, Any]]:
        """Get status of a weekly schedule"""
        schedule_key = f"{cluster_id}_{week_start.strftime('%Y-%m-%d')}"
        schedule = self.schedules.get(schedule_key)
        
        if not schedule:
            return None
        
        # Update status counts
        schedule.scheduled_count = sum(1 for item in schedule.schedule_items if item.status == ScheduleStatus.SCHEDULED)
        schedule.published_count = sum(1 for item in schedule.schedule_items if item.status == ScheduleStatus.PUBLISHED)
        schedule.failed_count = sum(1 for item in schedule.schedule_items if item.status == ScheduleStatus.FAILED)
        
        return {
            "schedule": schedule.to_dict(),
            "next_posts": [
                item.to_dict() for item in schedule.schedule_items
                if item.scheduled_time > datetime.now() and item.status == ScheduleStatus.SCHEDULED
            ][:5],  # Next 5 posts
            "recent_activity": [
                item.to_dict() for item in schedule.schedule_items
                if item.status in [ScheduleStatus.PUBLISHED, ScheduleStatus.FAILED]
            ][-10:]  # Last 10 activities
        }
    
    async def approve_content(
        self,
        item_id: str,
        approved: bool,
        feedback: Optional[str] = None
    ) -> bool:
        """Approve or reject content for posting"""
        try:
            # Find schedule item
            for schedule in self.schedules.values():
                for item in schedule.schedule_items:
                    if item.id == item_id:
                        item.approval_status = "approved" if approved else "rejected"
                        if feedback:
                            item.performance_data = item.performance_data or {}
                            item.performance_data["approval_feedback"] = feedback
                        
                        logger.info(f"Content {item_id} {'approved' if approved else 'rejected'}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Content approval failed: {e}")
            return False
    
    def _generate_schedule_items(
        self,
        content_pieces: List[ContentPiece],
        week_start: datetime,
        available_platforms: List[GHLSocialPlatform],
        posting_frequency: PostingFrequency,
        custom_times: Optional[Dict[GHLSocialPlatform, List[time]]] = None
    ) -> List[ContentScheduleItem]:
        """Generate schedule items for content pieces"""
        
        schedule_items = []
        current_date = week_start
        
        # Determine posting days based on frequency
        posting_days = self._get_posting_days(posting_frequency)
        
        for i, content_piece in enumerate(content_pieces):
            # Determine platforms for this content format
            platforms = self._get_platforms_for_format(content_piece.format, available_platforms)
            
            # Calculate posting day
            day_index = i % len(posting_days)
            posting_date = week_start + timedelta(days=posting_days[day_index])
            
            # Get optimal time for primary platform
            primary_platform = platforms[0] if platforms else available_platforms[0]
            optimal_time_slot = self._get_optimal_time_slot(primary_platform, custom_times)
            posting_time = optimal_time_slot.to_datetime(posting_date)
            
            # Generate UTM parameters
            utm_params = {
                "utm_source": "social_media",
                "utm_medium": "organic",
                "utm_campaign": f"cluster_{content_piece.cluster_id}",
                "utm_content": content_piece.id
            }
            
            schedule_item = ContentScheduleItem(
                id=str(uuid4()),
                content_piece=content_piece,
                scheduled_time=posting_time,
                platforms=platforms,
                status=ScheduleStatus.DRAFT,
                utm_parameters=utm_params,
                hashtags=self._generate_hashtags(content_piece)
            )
            
            schedule_items.append(schedule_item)
        
        return schedule_items
    
    def _get_posting_days(self, frequency: PostingFrequency) -> List[int]:
        """Get posting days based on frequency (0=Monday, 6=Sunday)"""
        if frequency == PostingFrequency.DAILY:
            return [0, 1, 2, 3, 4, 5, 6]  # Every day
        elif frequency == PostingFrequency.EVERY_OTHER_DAY:
            return [0, 2, 4, 6]  # Mon, Wed, Fri, Sun
        elif frequency == PostingFrequency.WEEKDAYS_ONLY:
            return [0, 1, 2, 3, 4]  # Mon-Fri
        else:  # CUSTOM
            return [0, 2, 4]  # Default to Mon, Wed, Fri
    
    def _get_platforms_for_format(
        self,
        content_format: ContentFormat,
        available_platforms: List[GHLSocialPlatform]
    ) -> List[GHLSocialPlatform]:
        """Determine optimal platforms for content format"""
        format_platform_map = {
            ContentFormat.LINKEDIN_ARTICLE: [GHLSocialPlatform.LINKEDIN],
            ContentFormat.X_THREAD: [GHLSocialPlatform.TWITTER],
            ContentFormat.INSTAGRAM_POST: [GHLSocialPlatform.INSTAGRAM],
            ContentFormat.META_FACEBOOK_POST: [GHLSocialPlatform.FACEBOOK],
            ContentFormat.TIKTOK_UGC: [GHLSocialPlatform.TIKTOK],
            ContentFormat.YOUTUBE_SHORTS: [GHLSocialPlatform.YOUTUBE],
            # Multi-platform for blog content
            ContentFormat.AI_SEARCH_BLOG: [GHLSocialPlatform.LINKEDIN, GHLSocialPlatform.FACEBOOK],
            ContentFormat.EPIC_PILLAR_ARTICLE: [GHLSocialPlatform.LINKEDIN, GHLSocialPlatform.FACEBOOK]
        }
        
        preferred_platforms = format_platform_map.get(content_format, [GHLSocialPlatform.FACEBOOK])
        
        # Filter by available platforms
        return [p for p in preferred_platforms if p in available_platforms]
    
    def _get_optimal_times(
        self,
        platforms: List[GHLSocialPlatform],
        custom_times: Optional[Dict[GHLSocialPlatform, List[time]]] = None
    ) -> Dict[GHLSocialPlatform, List[PostingTimeSlot]]:
        """Get optimal posting times for platforms"""
        optimal_times = {}
        
        for platform in platforms:
            if custom_times and platform in custom_times:
                # Use custom times
                optimal_times[platform] = [
                    PostingTimeSlot(platform, t, engagement_score=80.0)
                    for t in custom_times[platform]
                ]
            else:
                # Use default optimal times
                optimal_times[platform] = self.default_posting_times.get(
                    platform,
                    [PostingTimeSlot(platform, time(12, 0), engagement_score=75.0)]
                )
        
        return optimal_times
    
    def _get_optimal_time_slot(
        self,
        platform: GHLSocialPlatform,
        custom_times: Optional[Dict[GHLSocialPlatform, List[time]]] = None
    ) -> PostingTimeSlot:
        """Get single optimal time slot for platform"""
        if custom_times and platform in custom_times:
            return PostingTimeSlot(platform, custom_times[platform][0], engagement_score=80.0)
        
        platform_times = self.default_posting_times.get(platform)
        if platform_times:
            # Return highest engagement time
            return max(platform_times, key=lambda x: x.engagement_score)
        
        return PostingTimeSlot(platform, time(12, 0), engagement_score=75.0)
    
    def _format_social_content(self, content_piece: ContentPiece) -> str:
        """Format content piece for social media posting"""
        brief = getattr(content_piece, 'content_brief', content_piece.title)
        
        social_content = f"🚀 {content_piece.title}\n\n"
        
        if len(brief) > 100:
            social_content += f"{brief[:100]}...\n\n"
        else:
            social_content += f"{brief}\n\n"
        
        social_content += "Read more 👇"
        
        return social_content
    
    def _generate_hashtags(self, content_piece: ContentPiece) -> List[str]:
        """Generate hashtags for content piece"""
        keywords = getattr(content_piece, 'seo_keywords', [])
        
        hashtags = [f"#{keyword.replace(' ', '').lower()}" for keyword in keywords[:5]]
        hashtags.extend(["#business", "#growth", "#brandBOS"])
        
        return hashtags[:10]


# Utility functions
async def create_and_execute_weekly_schedule(
    ghl_client: GHLMCPClient,
    content_cluster: ContentCluster,
    content_pieces: List[ContentPiece],
    location_id: str,
    week_start: datetime,
    auto_approve: bool = False
) -> Dict[str, Any]:
    """Create and execute a weekly schedule in one operation"""
    
    calendar = ContentCalendar(ghl_client)
    
    # Create schedule
    schedule = await calendar.create_weekly_schedule(
        content_cluster=content_cluster,
        content_pieces=content_pieces,
        location_id=location_id,
        week_start=week_start
    )
    
    # Execute schedule
    execution_results = await calendar.execute_schedule(schedule, auto_approve)
    
    return {
        "schedule": schedule.to_dict(),
        "execution": execution_results,
        "summary": {
            "total_content_pieces": len(content_pieces),
            "posts_scheduled": execution_results["scheduled"],
            "posts_failed": execution_results["failed"],
            "completion_rate": schedule.completion_rate
        }
    }


async def get_weekly_schedule_overview(
    content_calendar: ContentCalendar,
    week_start: datetime,
    location_id: str
) -> Dict[str, Any]:
    """Get overview of all schedules for a week"""
    
    week_schedules = []
    
    for schedule_key, schedule in content_calendar.schedules.items():
        if (schedule.week_start.strftime('%Y-%m-%d') == week_start.strftime('%Y-%m-%d') and
            schedule.location_id == location_id):
            
            week_schedules.append({
                "cluster_id": schedule.cluster_id,
                "total_posts": schedule.total_posts,
                "scheduled_count": schedule.scheduled_count,
                "published_count": schedule.published_count,
                "completion_rate": schedule.completion_rate,
                "next_post": min(
                    [item.scheduled_time for item in schedule.schedule_items 
                     if item.scheduled_time > datetime.now()],
                    default=None
                )
            })
    
    return {
        "week_start": week_start.isoformat(),
        "location_id": location_id,
        "schedules": week_schedules,
        "total_schedules": len(week_schedules),
        "overall_completion": sum(s["completion_rate"] for s in week_schedules) / len(week_schedules) if week_schedules else 0
    }