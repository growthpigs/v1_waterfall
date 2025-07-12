"""
Scheduling API Routes for Brand BOS
Handles content calendar and social media scheduling
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, time
from uuid import UUID
from pydantic import BaseModel, Field

from ...scheduling.content_calendar import (
    ContentCalendar,
    PostingFrequency,
    ScheduleStatus,
    create_and_execute_weekly_schedule,
    get_weekly_schedule_overview
)
from ...integrations.ghl_mcp_client import GHLMCPClient, GHLSocialPlatform
from ...database.cartwheel_models import ContentCluster, ContentPiece, ContentFormat

router = APIRouter()

# Dependency injection
async def get_ghl_client() -> GHLMCPClient:
    """Get GHL MCP client instance"""
    # In production, this would come from app state or configuration
    return GHLMCPClient(
        mcp_endpoint="http://localhost:3000",
        api_key="your-ghl-api-key"
    )

async def get_content_calendar(ghl_client: GHLMCPClient = Depends(get_ghl_client)) -> ContentCalendar:
    """Get content calendar instance"""
    return ContentCalendar(ghl_client)


# Request/Response Models
class WeeklyScheduleRequest(BaseModel):
    """Request to create a weekly schedule"""
    cluster_id: str
    location_id: str
    week_start_date: str  # YYYY-MM-DD format
    posting_frequency: PostingFrequency = PostingFrequency.DAILY
    custom_posting_times: Optional[Dict[str, List[str]]] = None  # platform -> ["HH:MM", ...]
    auto_approve: bool = False

class ContentApprovalRequest(BaseModel):
    """Request to approve/reject content"""
    item_id: str
    approved: bool
    feedback: Optional[str] = None

class ScheduleExecutionRequest(BaseModel):
    """Request to execute a schedule"""
    cluster_id: str
    week_start_date: str
    auto_approve: bool = False


# Schedule Management Endpoints
@router.post("/weekly-schedule/create")
async def create_weekly_schedule(
    request: WeeklyScheduleRequest,
    calendar: ContentCalendar = Depends(get_content_calendar)
):
    """Create a weekly content schedule"""
    try:
        # Parse week start date
        week_start = datetime.strptime(request.week_start_date, "%Y-%m-%d")
        
        # Mock content cluster and pieces (in production, fetch from database)
        content_cluster = ContentCluster(
            id=request.cluster_id,
            cluster_topic="Marketing Strategy",
            client_id=UUID("00000000-0000-0000-0000-000000000000"),
            cia_session_id=UUID("00000000-0000-0000-0000-000000000000"),
            target_date=datetime.now() + timedelta(days=7),
            content_count=5,
            status="active"
        )
        
        # Mock content pieces
        content_pieces = [
            ContentPiece(
                id=f"content_{i}",
                title=f"Marketing Content {i+1}",
                format=ContentFormat.AI_SEARCH_BLOG,
                cluster_id=request.cluster_id,
                client_id=UUID("00000000-0000-0000-0000-000000000000"),
                content_brief=f"Content brief for piece {i+1}",
                target_word_count=1000,
                seo_keywords=[f"keyword{i+1}", "marketing", "business"],
                content_status="ready"
            )
            for i in range(5)
        ]
        
        # Parse custom posting times if provided
        custom_times = None
        if request.custom_posting_times:
            custom_times = {}
            for platform_str, time_strings in request.custom_posting_times.items():
                try:
                    platform = GHLSocialPlatform(platform_str)
                    times = [
                        time(*map(int, time_str.split(":")))
                        for time_str in time_strings
                    ]
                    custom_times[platform] = times
                except ValueError:
                    continue
        
        # Create schedule
        schedule = await calendar.create_weekly_schedule(
            content_cluster=content_cluster,
            content_pieces=content_pieces,
            location_id=request.location_id,
            week_start=week_start,
            posting_frequency=request.posting_frequency,
            custom_times=custom_times
        )
        
        # Auto-execute if requested
        execution_results = None
        if request.auto_approve:
            execution_results = await calendar.execute_schedule(schedule, auto_approve=True)
        
        return {
            "schedule": schedule.to_dict(),
            "execution_results": execution_results,
            "status": "created",
            "message": f"Weekly schedule created for cluster {request.cluster_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create weekly schedule: {str(e)}")


@router.post("/schedule/execute")
async def execute_schedule(
    request: ScheduleExecutionRequest,
    calendar: ContentCalendar = Depends(get_content_calendar)
):
    """Execute a created schedule"""
    try:
        week_start = datetime.strptime(request.week_start_date, "%Y-%m-%d")
        schedule_key = f"{request.cluster_id}_{week_start.strftime('%Y-%m-%d')}"
        
        schedule = calendar.schedules.get(schedule_key)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        execution_results = await calendar.execute_schedule(schedule, request.auto_approve)
        
        return {
            "execution_results": execution_results,
            "schedule_summary": {
                "cluster_id": schedule.cluster_id,
                "total_posts": schedule.total_posts,
                "scheduled": execution_results["scheduled"],
                "failed": execution_results["failed"],
                "completion_rate": schedule.completion_rate
            },
            "status": "executed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule execution failed: {str(e)}")


@router.get("/schedule/status/{cluster_id}")
async def get_schedule_status(
    cluster_id: str,
    week_start_date: str = Query(..., description="Week start date (YYYY-MM-DD)"),
    calendar: ContentCalendar = Depends(get_content_calendar)
):
    """Get status of a weekly schedule"""
    try:
        week_start = datetime.strptime(week_start_date, "%Y-%m-%d")
        status = await calendar.get_schedule_status(cluster_id, week_start)
        
        if not status:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        return status
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schedule status: {str(e)}")


@router.get("/schedule/overview")
async def get_weekly_overview(
    location_id: str = Query(..., description="GHL location ID"),
    week_start_date: str = Query(..., description="Week start date (YYYY-MM-DD)"),
    calendar: ContentCalendar = Depends(get_content_calendar)
):
    """Get overview of all schedules for a week"""
    try:
        week_start = datetime.strptime(week_start_date, "%Y-%m-%d")
        overview = await get_weekly_schedule_overview(calendar, week_start, location_id)
        
        return overview
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weekly overview: {str(e)}")


# Content Approval Endpoints
@router.post("/content/approve")
async def approve_content(
    request: ContentApprovalRequest,
    calendar: ContentCalendar = Depends(get_content_calendar)
):
    """Approve or reject content for posting"""
    try:
        success = await calendar.approve_content(
            item_id=request.item_id,
            approved=request.approved,
            feedback=request.feedback
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Content item not found")
        
        return {
            "item_id": request.item_id,
            "approved": request.approved,
            "feedback": request.feedback,
            "status": "approval_updated"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content approval failed: {str(e)}")


@router.get("/content/pending-approval/{location_id}")
async def get_pending_approvals(
    location_id: str,
    calendar: ContentCalendar = Depends(get_content_calendar)
):
    """Get all content pending approval for a location"""
    try:
        pending_items = []
        
        for schedule in calendar.schedules.values():
            if schedule.location_id == location_id:
                for item in schedule.schedule_items:
                    if item.approval_status == "pending":
                        pending_items.append({
                            "item_id": item.id,
                            "content_title": item.content_piece.title,
                            "content_format": item.content_piece.format.value,
                            "scheduled_time": item.scheduled_time.isoformat(),
                            "platforms": [p.value for p in item.platforms],
                            "cluster_id": schedule.cluster_id,
                            "week_start": schedule.week_start.isoformat()
                        })
        
        return {
            "location_id": location_id,
            "pending_items": pending_items,
            "count": len(pending_items)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending approvals: {str(e)}")


# GHL Integration Endpoints
@router.get("/ghl/connected-platforms/{location_id}")
async def get_connected_platforms(
    location_id: str,
    ghl_client: GHLMCPClient = Depends(get_ghl_client)
):
    """Get connected social platforms for a GHL location"""
    try:
        platforms = await ghl_client.get_connected_platforms(location_id)
        
        return {
            "location_id": location_id,
            "connected_platforms": platforms,
            "count": len(platforms),
            "available_for_scheduling": [
                p["platform"] for p in platforms if p.get("connected", False)
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connected platforms: {str(e)}")


@router.get("/ghl/test-connection")
async def test_ghl_connection(
    ghl_client: GHLMCPClient = Depends(get_ghl_client)
):
    """Test GHL MCP connection"""
    try:
        connection_result = await ghl_client.test_connection()
        
        return {
            "ghl_mcp_status": connection_result,
            "scheduling_available": connection_result.get("connected", False),
            "capabilities": connection_result.get("capabilities", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GHL connection test failed: {str(e)}")


# Quick Actions
@router.post("/quick/create-and-execute")
async def quick_create_and_execute(
    request: WeeklyScheduleRequest,
    calendar: ContentCalendar = Depends(get_content_calendar)
):
    """Quick action: Create and execute a weekly schedule in one call"""
    try:
        week_start = datetime.strptime(request.week_start_date, "%Y-%m-%d")
        
        # Mock content data (same as in create_weekly_schedule)
        content_cluster = ContentCluster(
            id=request.cluster_id,
            cluster_topic="Marketing Strategy",
            client_id=UUID("00000000-0000-0000-0000-000000000000"),
            cia_session_id=UUID("00000000-0000-0000-0000-000000000000"),
            target_date=datetime.now() + timedelta(days=7),
            content_count=5,
            status="active"
        )
        
        content_pieces = [
            ContentPiece(
                id=f"content_{i}",
                title=f"Marketing Content {i+1}",
                format=ContentFormat.AI_SEARCH_BLOG,
                cluster_id=request.cluster_id,
                client_id=UUID("00000000-0000-0000-0000-000000000000"),
                content_brief=f"Content brief for piece {i+1}",
                target_word_count=1000,
                seo_keywords=[f"keyword{i+1}", "marketing", "business"],
                content_status="ready"
            )
            for i in range(5)
        ]
        
        # Use utility function
        result = await create_and_execute_weekly_schedule(
            ghl_client=calendar.ghl_client,
            content_cluster=content_cluster,
            content_pieces=content_pieces,
            location_id=request.location_id,
            week_start=week_start,
            auto_approve=request.auto_approve
        )
        
        return {
            **result,
            "status": "created_and_executed",
            "message": "Weekly schedule created and executed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick create and execute failed: {str(e)}")


@router.get("/optimal-times/{platform}")
async def get_optimal_posting_times(
    platform: str,
    calendar: ContentCalendar = Depends(get_content_calendar)
):
    """Get optimal posting times for a platform"""
    try:
        platform_enum = GHLSocialPlatform(platform)
        optimal_times = calendar.default_posting_times.get(platform_enum, [])
        
        return {
            "platform": platform,
            "optimal_times": [
                {
                    "time": slot.time.strftime("%H:%M"),
                    "engagement_score": slot.engagement_score,
                    "timezone": slot.timezone
                }
                for slot in optimal_times
            ],
            "recommended_time": optimal_times[0].time.strftime("%H:%M") if optimal_times else "12:00"
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get optimal times: {str(e)}")