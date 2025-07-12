"""
Cartwheel System API Routes
Endpoints for content multiplication and viral detection
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from ...cartwheel import ConvergenceDetectionEngine, ContentMultiplier
from ...database.cartwheel_models import (
    ConvergenceOpportunity, ContentCluster, ContentPiece,
    ContentFormat, PublishingStatus, ApprovalStatus
)
from ...database.cartwheel_repository import CartwheelRepository
from ...database.repositories import CIASessionRepository

router = APIRouter()


# Request/Response Models
class ConvergenceAnalysisRequest(BaseModel):
    """Request to run convergence analysis"""
    client_id: UUID
    cia_session_id: UUID
    use_mock_data: bool = True  # For testing without API keys


class ContentGenerationRequest(BaseModel):
    """Request to generate content from convergence"""
    convergence_id: str
    client_id: UUID
    cia_session_id: UUID
    enabled_formats: Optional[List[ContentFormat]] = None


class ContentApprovalRequest(BaseModel):
    """Request to approve/reject content"""
    content_piece_id: str
    action: str = Field(..., regex="^(approve|reject|revise)$")
    feedback: Optional[str] = None
    reviewer_id: str = "api_user"


class PublishingRequest(BaseModel):
    """Request to publish content"""
    cluster_id: str
    platforms: List[str] = ["all"]
    schedule_type: str = "immediate"  # immediate, scheduled
    scheduled_time: Optional[datetime] = None


# Dependency injection
async def get_cartwheel_repo() -> CartwheelRepository:
    """Get Cartwheel repository instance"""
    return CartwheelRepository()


async def get_convergence_engine() -> ConvergenceDetectionEngine:
    """Get convergence detection engine"""
    # In production, would get API keys from config
    return ConvergenceDetectionEngine(
        grok_api_key=None,  # Will use mock data
        repository=await get_cartwheel_repo()
    )


async def get_content_multiplier() -> ContentMultiplier:
    """Get content multiplication engine"""
    return ContentMultiplier(
        repository=await get_cartwheel_repo()
    )


@router.post("/convergence/analyze")
async def run_convergence_analysis(
    request: ConvergenceAnalysisRequest,
    background_tasks: BackgroundTasks,
    engine: ConvergenceDetectionEngine = Depends(get_convergence_engine)
) -> Dict[str, Any]:
    """
    Run weekly convergence analysis to detect viral opportunities
    """
    try:
        # Get CIA intelligence
        cia_repo = CIASessionRepository()
        cia_session = await cia_repo.get_by_id(request.cia_session_id)
        
        if not cia_session:
            raise HTTPException(status_code=404, detail="CIA session not found")
        
        # Get intelligence data (simplified for API)
        cia_intelligence = {
            "target_audience": cia_session.company_data.get("target_audience", {}),
            "pain_points": ["growth", "efficiency", "automation"],  # Mock
            "service_offerings": ["consulting", "software", "training"],  # Mock
            "authority_positioning": {"expertise": "industry leader"}
        }
        
        # Run convergence detection
        opportunities = await engine.detect_weekly_convergence(
            client_id=request.client_id,
            cia_intelligence=cia_intelligence
        )
        
        return {
            "status": "success",
            "week_date": datetime.now().strftime("%Y-W%U"),
            "opportunities_found": len(opportunities),
            "opportunities": [
                {
                    "id": opp.id,
                    "topic": opp.topic,
                    "convergence_score": opp.convergence_score,
                    "urgency": opp.urgency_level,
                    "recommended_formats": opp.recommended_formats,
                    "seo_keywords": opp.seo_keywords[:5]
                }
                for opp in opportunities
            ],
            "message": f"Found {len(opportunities)} convergence opportunities"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/convergence/opportunities/{client_id}")
async def get_convergence_opportunities(
    client_id: UUID,
    week_date: Optional[str] = None,
    repo: CartwheelRepository = Depends(get_cartwheel_repo)
) -> Dict[str, Any]:
    """Get convergence opportunities for a client"""
    try:
        if week_date:
            opportunities = await repo.get_weekly_opportunities(client_id, week_date)
        else:
            opportunities = await repo.get_latest_opportunities(client_id, limit=10)
        
        return {
            "client_id": str(client_id),
            "total": len(opportunities),
            "opportunities": [
                {
                    "id": opp.id,
                    "topic": opp.topic,
                    "convergence_score": opp.convergence_score,
                    "urgency": opp.urgency_level,
                    "created_at": opp.created_at.isoformat()
                }
                for opp in opportunities
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/generate")
async def generate_content_cluster(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    multiplier: ContentMultiplier = Depends(get_content_multiplier),
    repo: CartwheelRepository = Depends(get_cartwheel_repo)
) -> Dict[str, Any]:
    """
    Generate content cluster from convergence opportunity
    """
    try:
        # Get convergence opportunity
        opportunity = await repo.get_convergence_opportunity(request.convergence_id)
        if not opportunity:
            raise HTTPException(status_code=404, detail="Convergence opportunity not found")
        
        # Get CIA intelligence
        cia_repo = CIASessionRepository()
        cia_session = await cia_repo.get_by_id(request.cia_session_id)
        
        if not cia_session:
            raise HTTPException(status_code=404, detail="CIA session not found")
        
        # Build CIA intelligence (simplified)
        cia_intelligence = {
            "customer_psychology": {"triggers": ["success", "growth", "efficiency"]},
            "authority_positioning": {"expertise": "industry leader"},
            "pain_points": ["scaling", "automation", "competition"],
            "service_offerings": ["consulting", "software"],
            "unique_value_props": ["proven results", "expert team"]
        }
        
        # Build client config
        client_config = {
            "enabled_content_formats": request.enabled_formats or [
                ContentFormat.AI_SEARCH_BLOG,
                ContentFormat.EPIC_PILLAR_ARTICLE,
                ContentFormat.INSTAGRAM_POST,
                ContentFormat.X_THREAD,
                ContentFormat.LINKEDIN_ARTICLE
            ],
            "brand_voice": {"tone": "professional yet approachable"},
            "target_audience": cia_session.company_data.get("target_audience", {})
        }
        
        # Generate content in background
        background_tasks.add_task(
            multiplier.generate_content_cluster,
            opportunity=opportunity,
            cia_intelligence=cia_intelligence,
            client_config=client_config
        )
        
        return {
            "status": "started",
            "convergence_id": request.convergence_id,
            "topic": opportunity.topic,
            "formats_requested": len(client_config["enabled_content_formats"]),
            "message": "Content generation started in background"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/clusters/{client_id}")
async def get_content_clusters(
    client_id: UUID,
    status: Optional[str] = None,
    repo: CartwheelRepository = Depends(get_cartwheel_repo)
) -> Dict[str, Any]:
    """Get content clusters for a client"""
    try:
        if status == "pending":
            clusters = await repo.get_pending_clusters(client_id)
        else:
            # Get all recent clusters
            clusters = []  # TODO: Implement get_recent_clusters
        
        return {
            "client_id": str(client_id),
            "total": len(clusters),
            "clusters": [
                {
                    "id": cluster.id,
                    "topic": cluster.cluster_topic,
                    "status": cluster.approval_status,
                    "content_pieces": len(cluster.content_piece_ids),
                    "created_at": cluster.created_at.isoformat()
                }
                for cluster in clusters
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/cluster/{cluster_id}/pieces")
async def get_cluster_content(
    cluster_id: str,
    repo: CartwheelRepository = Depends(get_cartwheel_repo)
) -> Dict[str, Any]:
    """Get all content pieces in a cluster"""
    try:
        pieces = await repo.get_cluster_content(cluster_id)
        
        return {
            "cluster_id": cluster_id,
            "total_pieces": len(pieces),
            "content": [
                {
                    "id": piece.id,
                    "format": piece.format_type.value,
                    "title": piece.title,
                    "approval_status": piece.approval_status.value,
                    "publishing_status": piece.publishing_status.value,
                    "word_count": len(piece.content_body.split()) if piece.content_body else 0
                }
                for piece in pieces
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/approve")
async def approve_content(
    request: ContentApprovalRequest,
    repo: CartwheelRepository = Depends(get_cartwheel_repo)
) -> Dict[str, str]:
    """Approve, reject, or request revision for content"""
    try:
        # Get content piece
        piece = await repo.get_content_piece(request.content_piece_id)
        if not piece:
            raise HTTPException(status_code=404, detail="Content piece not found")
        
        # Update approval status
        if request.action == "approve":
            piece.approval_status = ApprovalStatus.APPROVED
        elif request.action == "reject":
            piece.approval_status = ApprovalStatus.REJECTED
        else:  # revise
            piece.approval_status = ApprovalStatus.NEEDS_REVISION
        
        await repo.update_content_piece(piece)
        
        # Create approval record
        from ...database.cartwheel_models import ContentApproval
        approval = ContentApproval(
            id=str(UUID()),
            content_piece_id=request.content_piece_id,
            cluster_id=piece.cluster_id,
            reviewer_id=request.reviewer_id,
            status=piece.approval_status,
            feedback=request.feedback,
            approved_at=datetime.now() if request.action == "approve" else None,
            created_at=datetime.now()
        )
        
        await repo.create_approval(approval)
        
        return {
            "status": "success",
            "action": request.action,
            "content_piece_id": request.content_piece_id,
            "message": f"Content {request.action}d successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/publish")
async def publish_content(
    request: PublishingRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Initiate publishing workflow for content cluster"""
    try:
        # In production, this would trigger the publishing coordinator
        # For now, return mock response
        
        background_tasks.add_task(
            _mock_publishing_workflow,
            cluster_id=request.cluster_id,
            platforms=request.platforms
        )
        
        return {
            "status": "publishing_initiated",
            "cluster_id": request.cluster_id,
            "platforms": request.platforms,
            "schedule_type": request.schedule_type,
            "message": "Publishing workflow started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/{client_id}")
async def get_content_performance(
    client_id: UUID,
    days: int = 30,
    repo: CartwheelRepository = Depends(get_cartwheel_repo)
) -> Dict[str, Any]:
    """Get content performance statistics"""
    try:
        stats = await repo.get_content_stats(client_id, days)
        
        return {
            "client_id": str(client_id),
            "period_days": days,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
async def _mock_publishing_workflow(cluster_id: str, platforms: List[str]):
    """Mock publishing workflow for testing"""
    import asyncio
    await asyncio.sleep(2)  # Simulate processing
    logger.info(f"Mock publishing completed for cluster {cluster_id} on platforms: {platforms}")