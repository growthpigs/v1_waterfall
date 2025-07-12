"""
Brand BOS Posting Workflow System
Orchestrates the complete content posting pipeline: Content → Calendar → GHL MCP → Live Posts
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from uuid import UUID, uuid4

from ..database.cartwheel_models import ContentPiece, ContentCluster, ContentFormat
from ..database.models import CIASession
from ..integrations.ghl_mcp_client import GHLMCPClient, GHLSocialPost, GHLBrandSettings
from ..scheduling.content_calendar import ContentCalendar, WeeklySchedule, PostingFrequency
from ..analytics.content_attribution import ContentAttributionEngine

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Workflow execution stages"""
    CONTENT_PREP = "content_preparation"
    CALENDAR_SCHEDULE = "calendar_scheduling"
    BRAND_SYNC = "brand_synchronization"
    GHL_POSTING = "ghl_posting"
    PERFORMANCE_TRACKING = "performance_tracking"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStatus(Enum):
    """Overall workflow status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowExecution:
    """Workflow execution tracking"""
    id: str
    cluster_id: str
    location_id: str
    client_id: str
    
    # Workflow metadata
    status: WorkflowStatus
    current_stage: WorkflowStage
    stages_completed: List[WorkflowStage]
    
    # Content data
    content_pieces: List[ContentPiece]
    cia_session: Optional[CIASession]
    
    # Execution results
    schedule_id: Optional[str] = None
    posted_content: List[Dict[str, Any]] = None
    performance_data: Optional[Dict[str, Any]] = None
    
    # Timing
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Error tracking
    errors: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.posted_content is None:
            self.posted_content = []
        if self.errors is None:
            self.errors = []
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Get workflow execution duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of posted content"""
        if not self.posted_content:
            return 0.0
        
        successful = sum(1 for post in self.posted_content if post.get("success", False))
        return (successful / len(self.posted_content)) * 100
    
    def add_error(self, stage: WorkflowStage, error: str, details: Optional[Dict] = None):
        """Add error to workflow"""
        self.errors.append({
            "stage": stage.value,
            "error": error,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "cluster_id": self.cluster_id,
            "location_id": self.location_id,
            "client_id": self.client_id,
            "status": self.status.value,
            "current_stage": self.current_stage.value,
            "stages_completed": [stage.value for stage in self.stages_completed],
            "content_count": len(self.content_pieces),
            "posted_content": self.posted_content,
            "performance_data": self.performance_data,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration.total_seconds() if self.duration else None,
            "success_rate": self.success_rate,
            "errors": self.errors
        }


class PostingWorkflowEngine:
    """Main posting workflow orchestration engine"""
    
    def __init__(
        self,
        ghl_client: GHLMCPClient,
        content_calendar: ContentCalendar,
        attribution_engine: Optional[ContentAttributionEngine] = None
    ):
        """
        Initialize posting workflow engine
        
        Args:
            ghl_client: GHL MCP client for posting
            content_calendar: Content calendar system
            attribution_engine: Optional attribution tracking
        """
        self.ghl_client = ghl_client
        self.content_calendar = content_calendar
        self.attribution_engine = attribution_engine
        self.active_workflows: Dict[str, WorkflowExecution] = {}
    
    async def execute_full_posting_workflow(
        self,
        content_cluster: ContentCluster,
        content_pieces: List[ContentPiece],
        location_id: str,
        cia_session: Optional[CIASession] = None,
        week_start: Optional[datetime] = None,
        posting_frequency: PostingFrequency = PostingFrequency.DAILY,
        auto_approve: bool = False
    ) -> WorkflowExecution:
        """
        Execute the complete posting workflow
        
        Args:
            content_cluster: Content cluster to post
            content_pieces: List of content pieces
            location_id: GHL location ID
            cia_session: CIA session with brand intelligence
            week_start: Week start date (defaults to next Monday)
            posting_frequency: How often to post
            auto_approve: Auto-approve all content
            
        Returns:
            Workflow execution result
        """
        
        # Create workflow execution
        workflow = WorkflowExecution(
            id=str(uuid4()),
            cluster_id=content_cluster.id,
            location_id=location_id,
            client_id=str(content_cluster.client_id),
            status=WorkflowStatus.PENDING,
            current_stage=WorkflowStage.CONTENT_PREP,
            stages_completed=[],
            content_pieces=content_pieces,
            cia_session=cia_session,
            created_at=datetime.now()
        )
        
        self.active_workflows[workflow.id] = workflow
        
        try:
            logger.info(f"Starting posting workflow {workflow.id} for cluster {content_cluster.id}")
            
            workflow.status = WorkflowStatus.IN_PROGRESS
            workflow.started_at = datetime.now()
            
            # Stage 1: Content Preparation
            await self._stage_content_preparation(workflow)
            
            # Stage 2: Calendar Scheduling
            await self._stage_calendar_scheduling(
                workflow, content_cluster, week_start, posting_frequency
            )
            
            # Stage 3: Brand Synchronization (if CIA session provided)
            if cia_session:
                await self._stage_brand_synchronization(workflow, cia_session)
            
            # Stage 4: GHL Posting
            await self._stage_ghl_posting(workflow, auto_approve)
            
            # Stage 5: Performance Tracking Setup
            await self._stage_performance_tracking(workflow)
            
            # Complete workflow
            workflow.status = WorkflowStatus.COMPLETED
            workflow.current_stage = WorkflowStage.COMPLETED
            workflow.completed_at = datetime.now()
            
            logger.info(f"Posting workflow {workflow.id} completed successfully")
            return workflow
            
        except Exception as e:
            logger.error(f"Posting workflow {workflow.id} failed: {e}")
            workflow.status = WorkflowStatus.FAILED
            workflow.current_stage = WorkflowStage.FAILED
            workflow.add_error(workflow.current_stage, str(e))
            workflow.completed_at = datetime.now()
            return workflow
    
    async def _stage_content_preparation(self, workflow: WorkflowExecution):
        """Stage 1: Prepare content for posting"""
        try:
            logger.info(f"Workflow {workflow.id}: Starting content preparation")
            workflow.current_stage = WorkflowStage.CONTENT_PREP
            
            # Validate content pieces
            valid_content = []
            for content_piece in workflow.content_pieces:
                if self._validate_content_piece(content_piece):
                    valid_content.append(content_piece)
                else:
                    workflow.add_error(
                        WorkflowStage.CONTENT_PREP,
                        f"Invalid content piece: {content_piece.id}",
                        {"content_title": content_piece.title}
                    )
            
            if not valid_content:
                raise Exception("No valid content pieces found")
            
            workflow.content_pieces = valid_content
            workflow.stages_completed.append(WorkflowStage.CONTENT_PREP)
            
            logger.info(f"Workflow {workflow.id}: Content preparation completed ({len(valid_content)} pieces)")
            
        except Exception as e:
            workflow.add_error(WorkflowStage.CONTENT_PREP, str(e))
            raise
    
    async def _stage_calendar_scheduling(
        self,
        workflow: WorkflowExecution,
        content_cluster: ContentCluster,
        week_start: Optional[datetime],
        posting_frequency: PostingFrequency
    ):
        """Stage 2: Create calendar schedule"""
        try:
            logger.info(f"Workflow {workflow.id}: Starting calendar scheduling")
            workflow.current_stage = WorkflowStage.CALENDAR_SCHEDULE
            
            # Default to next Monday if no week start provided
            if not week_start:
                today = datetime.now().date()
                days_until_monday = (7 - today.weekday()) % 7
                if days_until_monday == 0:  # If today is Monday, use next Monday
                    days_until_monday = 7
                week_start = datetime.combine(today + timedelta(days=days_until_monday), datetime.min.time())
            
            # Create schedule
            schedule = await self.content_calendar.create_weekly_schedule(
                content_cluster=content_cluster,
                content_pieces=workflow.content_pieces,
                location_id=workflow.location_id,
                week_start=week_start,
                posting_frequency=posting_frequency
            )
            
            workflow.schedule_id = f"{content_cluster.id}_{week_start.strftime('%Y-%m-%d')}"
            workflow.stages_completed.append(WorkflowStage.CALENDAR_SCHEDULE)
            
            logger.info(f"Workflow {workflow.id}: Calendar scheduling completed")
            
        except Exception as e:
            workflow.add_error(WorkflowStage.CALENDAR_SCHEDULE, str(e))
            raise
    
    async def _stage_brand_synchronization(
        self,
        workflow: WorkflowExecution,
        cia_session: CIASession
    ):
        """Stage 3: Synchronize brand settings with CIA intelligence"""
        try:
            logger.info(f"Workflow {workflow.id}: Starting brand synchronization")
            workflow.current_stage = WorkflowStage.BRAND_SYNC
            
            # Sync CIA intelligence to GHL brand settings
            sync_result = await self.ghl_client.sync_cia_to_brand_settings(
                location_id=workflow.location_id,
                cia_session=cia_session
            )
            
            if not sync_result.get("success"):
                workflow.add_error(
                    WorkflowStage.BRAND_SYNC,
                    "Brand synchronization failed",
                    sync_result
                )
            
            workflow.stages_completed.append(WorkflowStage.BRAND_SYNC)
            
            logger.info(f"Workflow {workflow.id}: Brand synchronization completed")
            
        except Exception as e:
            workflow.add_error(WorkflowStage.BRAND_SYNC, str(e))
            raise
    
    async def _stage_ghl_posting(self, workflow: WorkflowExecution, auto_approve: bool):
        """Stage 4: Post content to GHL"""
        try:
            logger.info(f"Workflow {workflow.id}: Starting GHL posting")
            workflow.current_stage = WorkflowStage.GHL_POSTING
            
            if not workflow.schedule_id:
                raise Exception("No schedule found for posting")
            
            # Get schedule
            schedule = self.content_calendar.schedules.get(workflow.schedule_id)
            if not schedule:
                raise Exception(f"Schedule {workflow.schedule_id} not found")
            
            # Execute schedule
            execution_results = await self.content_calendar.execute_schedule(
                schedule, auto_approve=auto_approve
            )
            
            # Track posted content
            workflow.posted_content = execution_results.get("posts", [])
            
            # Update workflow based on results
            if execution_results.get("failed", 0) > 0:
                workflow.add_error(
                    WorkflowStage.GHL_POSTING,
                    f"{execution_results['failed']} posts failed",
                    execution_results
                )
            
            workflow.stages_completed.append(WorkflowStage.GHL_POSTING)
            
            logger.info(f"Workflow {workflow.id}: GHL posting completed")
            
        except Exception as e:
            workflow.add_error(WorkflowStage.GHL_POSTING, str(e))
            raise
    
    async def _stage_performance_tracking(self, workflow: WorkflowExecution):
        """Stage 5: Set up performance tracking"""
        try:
            logger.info(f"Workflow {workflow.id}: Starting performance tracking setup")
            workflow.current_stage = WorkflowStage.PERFORMANCE_TRACKING
            
            # Initialize performance tracking structure
            workflow.performance_data = {
                "tracking_setup_date": datetime.now().isoformat(),
                "posts_to_track": len(workflow.posted_content),
                "attribution_enabled": self.attribution_engine is not None,
                "utm_tracking": all(
                    post.get("utm_parameters") for post in workflow.posted_content
                ),
                "platforms": list(set([
                    platform for post in workflow.posted_content 
                    for platform in post.get("platforms", [])
                ]))
            }
            
            workflow.stages_completed.append(WorkflowStage.PERFORMANCE_TRACKING)
            
            logger.info(f"Workflow {workflow.id}: Performance tracking setup completed")
            
        except Exception as e:
            workflow.add_error(WorkflowStage.PERFORMANCE_TRACKING, str(e))
            raise
    
    def _validate_content_piece(self, content_piece: ContentPiece) -> bool:
        """Validate content piece for posting"""
        required_fields = ["id", "title", "format", "cluster_id"]
        
        for field in required_fields:
            if not hasattr(content_piece, field) or getattr(content_piece, field) is None:
                return False
        
        # Check content status
        if hasattr(content_piece, "content_status"):
            if content_piece.content_status not in ["ready", "published"]:
                return False
        
        return True
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow execution"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return None
        
        return workflow.to_dict()
    
    async def cancel_workflow(self, workflow_id: str, reason: str = "User cancelled") -> bool:
        """Cancel an active workflow"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False
        
        if workflow.status != WorkflowStatus.IN_PROGRESS:
            return False
        
        workflow.status = WorkflowStatus.CANCELLED
        workflow.add_error(workflow.current_stage, f"Workflow cancelled: {reason}")
        workflow.completed_at = datetime.now()
        
        logger.info(f"Workflow {workflow_id} cancelled: {reason}")
        return True
    
    async def retry_failed_stage(self, workflow_id: str) -> bool:
        """Retry a failed workflow stage"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow or workflow.status != WorkflowStatus.FAILED:
            return False
        
        try:
            # Reset status for retry
            workflow.status = WorkflowStatus.IN_PROGRESS
            
            # Retry the stage that failed
            if workflow.current_stage == WorkflowStage.CONTENT_PREP:
                await self._stage_content_preparation(workflow)
            elif workflow.current_stage == WorkflowStage.GHL_POSTING:
                await self._stage_ghl_posting(workflow, auto_approve=True)
            # Add other stages as needed
            
            logger.info(f"Workflow {workflow_id} stage {workflow.current_stage.value} retried successfully")
            return True
            
        except Exception as e:
            workflow.add_error(workflow.current_stage, f"Retry failed: {str(e)}")
            logger.error(f"Workflow {workflow_id} retry failed: {e}")
            return False


# Utility functions
async def quick_post_content_cluster(
    ghl_client: GHLMCPClient,
    content_cluster: ContentCluster,
    content_pieces: List[ContentPiece],
    location_id: str,
    cia_session: Optional[CIASession] = None,
    auto_approve: bool = True
) -> Dict[str, Any]:
    """Quick utility to post a content cluster with default settings"""
    
    content_calendar = ContentCalendar(ghl_client)
    workflow_engine = PostingWorkflowEngine(ghl_client, content_calendar)
    
    workflow = await workflow_engine.execute_full_posting_workflow(
        content_cluster=content_cluster,
        content_pieces=content_pieces,
        location_id=location_id,
        cia_session=cia_session,
        auto_approve=auto_approve
    )
    
    return {
        "workflow": workflow.to_dict(),
        "success": workflow.status == WorkflowStatus.COMPLETED,
        "posts_scheduled": len([p for p in workflow.posted_content if p.get("success")]),
        "total_content": len(content_pieces),
        "execution_time": workflow.duration.total_seconds() if workflow.duration else None
    }


async def monitor_workflow_execution(
    workflow_engine: PostingWorkflowEngine,
    workflow_id: str,
    check_interval: int = 30
) -> Dict[str, Any]:
    """Monitor workflow execution with periodic status updates"""
    
    monitoring_results = []
    
    while True:
        status = await workflow_engine.get_workflow_status(workflow_id)
        if not status:
            break
        
        monitoring_results.append({
            "timestamp": datetime.now().isoformat(),
            "status": status["status"],
            "current_stage": status["current_stage"],
            "success_rate": status["success_rate"]
        })
        
        # Stop monitoring if workflow is complete or failed
        if status["status"] in ["completed", "failed", "cancelled"]:
            break
        
        await asyncio.sleep(check_interval)
    
    return {
        "workflow_id": workflow_id,
        "monitoring_duration": len(monitoring_results) * check_interval,
        "status_updates": monitoring_results,
        "final_status": monitoring_results[-1] if monitoring_results else None
    }