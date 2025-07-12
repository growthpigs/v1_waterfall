"""
Workflow API Routes for Brand BOS
Handles complete posting workflow orchestration
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from pydantic import BaseModel, Field

from ...workflows.posting_workflow import (
    PostingWorkflowEngine,
    WorkflowStatus,
    WorkflowStage,
    quick_post_content_cluster,
    monitor_workflow_execution
)
from ...integrations.ghl_mcp_client import GHLMCPClient
from ...scheduling.content_calendar import ContentCalendar, PostingFrequency
from ...database.cartwheel_models import ContentCluster, ContentPiece, ContentFormat
from ...database.models import CIASession

router = APIRouter()

# Dependency injection
async def get_ghl_client() -> GHLMCPClient:
    """Get GHL MCP client instance"""
    return GHLMCPClient(
        mcp_endpoint="http://localhost:3000",
        api_key="your-ghl-api-key"
    )

async def get_workflow_engine(ghl_client: GHLMCPClient = Depends(get_ghl_client)) -> PostingWorkflowEngine:
    """Get workflow engine instance"""
    content_calendar = ContentCalendar(ghl_client)
    return PostingWorkflowEngine(ghl_client, content_calendar)


# Request/Response Models
class FullWorkflowRequest(BaseModel):
    """Request to execute full posting workflow"""
    cluster_id: str
    location_id: str
    client_id: UUID
    content_pieces_data: List[Dict[str, Any]]
    cia_session_data: Optional[Dict[str, Any]] = None
    week_start_date: Optional[str] = None  # YYYY-MM-DD
    posting_frequency: PostingFrequency = PostingFrequency.DAILY
    auto_approve: bool = False

class QuickPostRequest(BaseModel):
    """Request for quick content cluster posting"""
    cluster_id: str
    location_id: str
    client_id: UUID
    content_titles: List[str]
    cluster_topic: str = "Content Marketing"
    auto_approve: bool = True

class WorkflowControlRequest(BaseModel):
    """Request for workflow control operations"""
    workflow_id: str
    action: str  # cancel, retry, monitor
    reason: Optional[str] = None


# Main Workflow Endpoints
@router.post("/execute-full-workflow")
async def execute_full_posting_workflow(
    request: FullWorkflowRequest,
    background_tasks: BackgroundTasks,
    workflow_engine: PostingWorkflowEngine = Depends(get_workflow_engine)
):
    """Execute the complete posting workflow"""
    try:
        # Create content cluster
        content_cluster = ContentCluster(
            id=request.cluster_id,
            cluster_topic="Marketing Content Cluster",
            client_id=request.client_id,
            cia_session_id=UUID("00000000-0000-0000-0000-000000000000"),
            target_date=datetime.now() + timedelta(days=7),
            content_count=len(request.content_pieces_data),
            status="active"
        )
        
        # Create content pieces from request data
        content_pieces = []
        for i, piece_data in enumerate(request.content_pieces_data):
            content_piece = ContentPiece(
                id=piece_data.get("id", f"content_{i}"),
                title=piece_data.get("title", f"Content {i+1}"),
                format=ContentFormat(piece_data.get("format", "ai_search_blog")),
                cluster_id=request.cluster_id,
                client_id=request.client_id,
                content_brief=piece_data.get("content_brief", "Content brief"),
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
                company_name=request.cia_session_data.get("company_name", "Test Company"),
                url=request.cia_session_data.get("url", "https://example.com"),
                kpoi=request.cia_session_data.get("kpoi", "Business Owner"),
                country=request.cia_session_data.get("country", "US"),
                client_id=request.client_id,
                session_status="completed"
            )
        
        # Parse week start date
        week_start = None
        if request.week_start_date:
            week_start = datetime.strptime(request.week_start_date, "%Y-%m-%d")
        
        # Execute workflow
        workflow = await workflow_engine.execute_full_posting_workflow(
            content_cluster=content_cluster,
            content_pieces=content_pieces,
            location_id=request.location_id,
            cia_session=cia_session,
            week_start=week_start,
            posting_frequency=request.posting_frequency,
            auto_approve=request.auto_approve
        )
        
        return {
            "workflow": workflow.to_dict(),
            "success": workflow.status == WorkflowStatus.COMPLETED,
            "message": f"Workflow executed with status: {workflow.status.value}",
            "next_actions": _get_next_actions(workflow)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.post("/quick-post")
async def quick_post_cluster(
    request: QuickPostRequest,
    workflow_engine: PostingWorkflowEngine = Depends(get_workflow_engine)
):
    """Quick post content cluster with minimal setup"""
    try:
        # Create content cluster
        content_cluster = ContentCluster(
            id=request.cluster_id,
            cluster_topic=request.cluster_topic,
            client_id=request.client_id,
            cia_session_id=UUID("00000000-0000-0000-0000-000000000000"),
            target_date=datetime.now() + timedelta(days=7),
            content_count=len(request.content_titles),
            status="active"
        )
        
        # Create content pieces from titles
        content_pieces = [
            ContentPiece(
                id=f"quick_content_{i}",
                title=title,
                format=ContentFormat.AI_SEARCH_BLOG,
                cluster_id=request.cluster_id,
                client_id=request.client_id,
                content_brief=f"Quick content: {title}",
                target_word_count=1000,
                seo_keywords=["marketing", "business"],
                content_status="ready"
            )
            for i, title in enumerate(request.content_titles)
        ]
        
        # Use quick post utility
        result = await quick_post_content_cluster(
            ghl_client=workflow_engine.ghl_client,
            content_cluster=content_cluster,
            content_pieces=content_pieces,
            location_id=request.location_id,
            auto_approve=request.auto_approve
        )
        
        return {
            **result,
            "message": "Quick post completed",
            "cluster_topic": request.cluster_topic
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick post failed: {str(e)}")


# Workflow Management Endpoints
@router.get("/status/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    workflow_engine: PostingWorkflowEngine = Depends(get_workflow_engine)
):
    """Get status of a workflow execution"""
    try:
        status = await workflow_engine.get_workflow_status(workflow_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "workflow_status": status,
            "next_actions": _get_next_actions_from_status(status)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")


@router.post("/control")
async def control_workflow(
    request: WorkflowControlRequest,
    background_tasks: BackgroundTasks,
    workflow_engine: PostingWorkflowEngine = Depends(get_workflow_engine)
):
    """Control workflow execution (cancel, retry, monitor)"""
    try:
        if request.action == "cancel":
            success = await workflow_engine.cancel_workflow(
                request.workflow_id, 
                request.reason or "User requested cancellation"
            )
            
            if not success:
                raise HTTPException(status_code=400, detail="Failed to cancel workflow")
            
            return {
                "action": "cancelled",
                "workflow_id": request.workflow_id,
                "reason": request.reason
            }
            
        elif request.action == "retry":
            success = await workflow_engine.retry_failed_stage(request.workflow_id)
            
            if not success:
                raise HTTPException(status_code=400, detail="Failed to retry workflow")
            
            return {
                "action": "retried",
                "workflow_id": request.workflow_id,
                "message": "Workflow retry initiated"
            }
            
        elif request.action == "monitor":
            # Start background monitoring
            background_tasks.add_task(
                _monitor_workflow_background,
                workflow_engine,
                request.workflow_id
            )
            
            return {
                "action": "monitoring_started",
                "workflow_id": request.workflow_id,
                "message": "Background monitoring initiated"
            }
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow control failed: {str(e)}")


@router.get("/active-workflows")
async def get_active_workflows(
    workflow_engine: PostingWorkflowEngine = Depends(get_workflow_engine)
):
    """Get all active workflows"""
    try:
        active_workflows = []
        
        for workflow_id, workflow in workflow_engine.active_workflows.items():
            active_workflows.append({
                "workflow_id": workflow_id,
                "cluster_id": workflow.cluster_id,
                "location_id": workflow.location_id,
                "status": workflow.status.value,
                "current_stage": workflow.current_stage.value,
                "created_at": workflow.created_at.isoformat(),
                "success_rate": workflow.success_rate,
                "content_count": len(workflow.content_pieces),
                "errors_count": len(workflow.errors)
            })
        
        return {
            "active_workflows": active_workflows,
            "count": len(active_workflows),
            "statuses": {
                status.value: len([w for w in active_workflows if w["status"] == status.value])
                for status in WorkflowStatus
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active workflows: {str(e)}")


# Brand Intelligence Integration
@router.post("/sync-brand-intelligence")
async def sync_brand_intelligence(
    location_id: str,
    cia_session_data: Dict[str, Any],
    workflow_engine: PostingWorkflowEngine = Depends(get_workflow_engine)
):
    """Sync CIA intelligence to GHL brand settings"""
    try:
        # Create CIA session from data
        cia_session = CIASession(
            id=UUID(cia_session_data.get("id", "00000000-0000-0000-0000-000000000000")),
            company_name=cia_session_data.get("company_name", "Company"),
            url=cia_session_data.get("url", "https://example.com"),
            kpoi=cia_session_data.get("kpoi", "Owner"),
            country=cia_session_data.get("country", "US"),
            client_id=UUID(cia_session_data.get("client_id", "00000000-0000-0000-0000-000000000000")),
            session_status="completed"
        )
        
        # Sync to GHL
        sync_result = await workflow_engine.ghl_client.sync_cia_to_brand_settings(
            location_id=location_id,
            cia_session=cia_session
        )
        
        return {
            "sync_result": sync_result,
            "location_id": location_id,
            "cia_session_id": str(cia_session.id),
            "success": sync_result.get("success", False)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brand intelligence sync failed: {str(e)}")


# Testing and Debug Endpoints
@router.get("/test/workflow-components")
async def test_workflow_components(
    workflow_engine: PostingWorkflowEngine = Depends(get_workflow_engine)
):
    """Test all workflow components"""
    try:
        # Test GHL connection
        ghl_test = await workflow_engine.ghl_client.test_connection()
        
        # Test content calendar
        calendar_available = workflow_engine.content_calendar is not None
        
        # Test attribution engine
        attribution_available = workflow_engine.attribution_engine is not None
        
        return {
            "component_tests": {
                "ghl_mcp_client": {
                    "available": True,
                    "connected": ghl_test.get("connected", False),
                    "capabilities": ghl_test.get("capabilities", [])
                },
                "content_calendar": {
                    "available": calendar_available,
                    "default_times_configured": len(workflow_engine.content_calendar.default_posting_times) > 0
                },
                "attribution_engine": {
                    "available": attribution_available,
                    "enabled": attribution_available
                }
            },
            "workflow_ready": (
                ghl_test.get("connected", False) and 
                calendar_available
            ),
            "recommendations": _get_component_recommendations(ghl_test, calendar_available, attribution_available)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Component test failed: {str(e)}")


# Helper functions
def _get_next_actions(workflow) -> List[str]:
    """Get recommended next actions based on workflow status"""
    if workflow.status == WorkflowStatus.COMPLETED:
        return [
            "Monitor post performance",
            "Schedule next content cluster",
            "Review engagement metrics"
        ]
    elif workflow.status == WorkflowStatus.FAILED:
        return [
            "Review error logs",
            "Retry failed stage",
            "Check GHL connection"
        ]
    elif workflow.status == WorkflowStatus.IN_PROGRESS:
        return [
            "Monitor progress",
            "Prepare next content batch"
        ]
    else:
        return ["Execute workflow"]

def _get_next_actions_from_status(status: Dict[str, Any]) -> List[str]:
    """Get next actions from status dictionary"""
    workflow_status = status.get("status")
    
    if workflow_status == "completed":
        return [
            "Monitor post performance",
            "Schedule next content cluster",
            "Review engagement metrics"
        ]
    elif workflow_status == "failed":
        return [
            "Review error logs",
            "Retry failed stage",
            "Check GHL connection"
        ]
    elif workflow_status == "in_progress":
        return [
            "Monitor progress",
            "Prepare next content batch"
        ]
    else:
        return ["Execute workflow"]

def _get_component_recommendations(ghl_test: Dict, calendar_available: bool, attribution_available: bool) -> List[str]:
    """Get recommendations for component setup"""
    recommendations = []
    
    if not ghl_test.get("connected", False):
        recommendations.append("Configure GHL MCP connection")
    
    if not calendar_available:
        recommendations.append("Initialize content calendar")
    
    if not attribution_available:
        recommendations.append("Set up attribution tracking (optional)")
    
    if not recommendations:
        recommendations.append("All components ready - start posting workflows")
    
    return recommendations

async def _monitor_workflow_background(workflow_engine: PostingWorkflowEngine, workflow_id: str):
    """Background task for workflow monitoring"""
    try:
        monitoring_result = await monitor_workflow_execution(workflow_engine, workflow_id)
        # In production, you might want to store or notify about monitoring results
        logger.info(f"Workflow {workflow_id} monitoring completed: {monitoring_result}")
    except Exception as e:
        logger.error(f"Workflow monitoring failed for {workflow_id}: {e}")


# Import logging
import logging
logger = logging.getLogger(__name__)