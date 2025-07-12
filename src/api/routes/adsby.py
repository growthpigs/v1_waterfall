"""
Adsby System API Routes
Endpoints for $10k Google Ads management
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field

from ...adsby import CampaignManager
from ...adsby.models import BudgetRotation, PerformanceMetric
from ...database.cartwheel_repository import CartwheelRepository
from ...database.repositories import CIASessionRepository

router = APIRouter()


# Request/Response Models
class CreateCampaignRequest(BaseModel):
    """Request to create campaign from content cluster"""
    cluster_id: str
    client_id: UUID
    cia_session_id: UUID
    auto_activate: bool = False


class BudgetRotationApproval(BaseModel):
    """Budget rotation approval request"""
    rotation_id: str
    approved: bool
    approved_by: str = "api_user"
    notes: Optional[str] = None


class CampaignActionRequest(BaseModel):
    """Campaign action request"""
    campaign_id: str
    action: str = Field(..., regex="^(pause|activate|update_budget)$")
    reason: Optional[str] = None
    new_budget: Optional[float] = None
    action_by: str = "api_user"


class PerformanceReportRequest(BaseModel):
    """Performance report request"""
    client_id: UUID
    start_date: date
    end_date: date
    include_keywords: bool = True
    include_ads: bool = True


# Dependency injection
async def get_campaign_manager() -> CampaignManager:
    """Get campaign manager instance"""
    # In production, would initialize with real clients
    return CampaignManager()


@router.post("/campaigns/create")
async def create_campaign_from_cluster(
    request: CreateCampaignRequest,
    background_tasks: BackgroundTasks,
    manager: CampaignManager = Depends(get_campaign_manager)
) -> Dict[str, Any]:
    """
    Create Google Ads campaign from content cluster
    """
    try:
        # Get content cluster
        cartwheel_repo = CartwheelRepository()
        cluster = await cartwheel_repo.get_content_cluster(request.cluster_id)
        
        if not cluster:
            raise HTTPException(status_code=404, detail="Content cluster not found")
        
        # Get CIA intelligence
        cia_repo = CIASessionRepository()
        cia_session = await cia_repo.get_by_id(request.cia_session_id)
        
        if not cia_session:
            raise HTTPException(status_code=404, detail="CIA session not found")
        
        # Build CIA intelligence summary
        cia_intelligence = {
            "client_name": cia_session.company_data.get("name", "Client"),
            "industry": cia_session.company_data.get("industry", "General"),
            "target_locations": ["United States"],  # Default
            "target_audience": cia_session.company_data.get("target_audience", {}),
            "website_url": cia_session.company_data.get("website_url", "https://example.com")
        }
        
        # Process campaign creation
        campaign = await manager.process_content_cluster(
            content_cluster=cluster,
            cia_intelligence=cia_intelligence,
            client_id=request.client_id
        )
        
        return {
            "status": "success",
            "campaign_id": campaign.campaign_id,
            "title": campaign.title,
            "budget": campaign.budget_allocated,
            "status": campaign.status.value,
            "keywords": len(campaign.keywords),
            "ad_groups": len(campaign.ad_groups),
            "message": f"Campaign {'activated' if campaign.status.value == 'active' else 'queued'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{client_id}")
async def get_client_campaigns(
    client_id: UUID,
    status: Optional[str] = None,
    manager: CampaignManager = Depends(get_campaign_manager)
) -> Dict[str, Any]:
    """Get campaigns for a client"""
    try:
        dashboard_data = await manager.get_campaign_dashboard_data(client_id)
        
        # Filter by status if provided
        if status:
            dashboard_data["active_campaigns"] = [
                c for c in dashboard_data["active_campaigns"]
                if c["status"] == status
            ]
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimization/analyze/{client_id}")
async def run_optimization_analysis(
    client_id: UUID,
    manager: CampaignManager = Depends(get_campaign_manager)
) -> Dict[str, Any]:
    """
    Run weekly optimization analysis for client campaigns
    """
    try:
        rotation = await manager.run_weekly_optimization(client_id)
        
        if not rotation:
            return {
                "status": "no_campaigns",
                "message": "No active campaigns to optimize"
            }
        
        return {
            "status": "analysis_complete",
            "rotation_id": rotation.rotation_id,
            "week_date": rotation.week_date,
            "requires_action": rotation.requires_action,
            "recommendation": {
                "action": "rotation" if rotation.campaign_to_pause else "maintain",
                "campaign_to_pause": rotation.campaign_to_pause,
                "reasoning": rotation.reasoning,
                "expected_improvement": rotation.projected_performance.get("expected_improvement", 0)
            },
            "current_campaigns": len(rotation.current_campaigns)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimization/approve")
async def approve_budget_rotation(
    approval: BudgetRotationApproval,
    manager: CampaignManager = Depends(get_campaign_manager)
) -> Dict[str, Any]:
    """Approve or reject budget rotation recommendation"""
    try:
        if not approval.approved:
            return {
                "status": "rejected",
                "rotation_id": approval.rotation_id,
                "message": "Budget rotation rejected"
            }
        
        # Get rotation details (would fetch from DB in production)
        # For now, create mock rotation
        rotation = BudgetRotation(
            rotation_id=approval.rotation_id,
            week_date=datetime.now().strftime("%Y-W%U"),
            current_campaigns=["camp_1", "camp_2"],
            campaign_to_pause="camp_1",
            campaign_to_promote="next_in_queue",
            reasoning="Performance optimization",
            projected_performance={"expected_improvement": 15.0},
            rotation_date=datetime.now(),
            requires_action=True
        )
        
        # Execute rotation
        results = await manager.execute_budget_rotation(
            rotation=rotation,
            approved_by=approval.approved_by
        )
        
        return {
            "status": "executed",
            "rotation_id": approval.rotation_id,
            "actions_taken": results["actions_taken"],
            "campaigns_paused": results["campaigns_paused"],
            "campaigns_activated": results["campaigns_activated"],
            "executed_at": results["executed_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/action")
async def perform_campaign_action(
    request: CampaignActionRequest,
    manager: CampaignManager = Depends(get_campaign_manager)
) -> Dict[str, str]:
    """Perform action on a campaign (pause, activate, update budget)"""
    try:
        if request.action == "pause":
            success = await manager.pause_campaign_manually(
                campaign_id=request.campaign_id,
                reason=request.reason or "Manual pause",
                paused_by=request.action_by
            )
        elif request.action == "activate":
            # Would implement activate_campaign_manually
            success = True
        elif request.action == "update_budget":
            if not request.new_budget:
                raise HTTPException(
                    status_code=400,
                    detail="new_budget required for update_budget action"
                )
            # Would implement update_campaign_budget
            success = True
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        return {
            "status": "success" if success else "failed",
            "campaign_id": request.campaign_id,
            "action": request.action,
            "message": f"Campaign {request.action} {'successful' if success else 'failed'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/{campaign_id}")
async def get_campaign_performance(
    campaign_id: str,
    days: int = 7
) -> Dict[str, Any]:
    """Get performance metrics for a specific campaign"""
    try:
        # In production, would use performance tracker
        # Mock response for now
        return {
            "campaign_id": campaign_id,
            "period_days": days,
            "metrics": {
                "impressions": 15000,
                "clicks": 450,
                "ctr": 3.0,
                "conversions": 25,
                "conversion_rate": 5.56,
                "cost": 875.50,
                "cpa": 35.02,
                "quality_score": 7.8,
                "authority_impact": 68.5
            },
            "daily_trend": [
                {"date": "2025-01-06", "clicks": 65, "conversions": 3},
                {"date": "2025-01-07", "clicks": 72, "conversions": 4},
                {"date": "2025-01-08", "clicks": 58, "conversions": 3},
                {"date": "2025-01-09", "clicks": 81, "conversions": 5},
                {"date": "2025-01-10", "clicks": 69, "conversions": 4},
                {"date": "2025-01-11", "clicks": 55, "conversions": 3},
                {"date": "2025-01-12", "clicks": 50, "conversions": 3}
            ],
            "top_keywords": [
                {"keyword": "marketing automation", "clicks": 85, "conversions": 6},
                {"keyword": "business growth solutions", "clicks": 72, "conversions": 5},
                {"keyword": "professional services", "clicks": 68, "conversions": 4}
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/performance/report")
async def generate_performance_report(
    request: PerformanceReportRequest
) -> Dict[str, Any]:
    """Generate comprehensive performance report"""
    try:
        # In production, would use performance tracker
        # Mock response for now
        return {
            "client_id": str(request.client_id),
            "report_period": {
                "start": request.start_date.isoformat(),
                "end": request.end_date.isoformat()
            },
            "summary": {
                "total_spend": 2456.78,
                "total_conversions": 89,
                "overall_cpa": 27.60,
                "overall_ctr": 3.2,
                "overall_conversion_rate": 5.8,
                "authority_impact_avg": 72.5
            },
            "campaigns": [
                {
                    "campaign_id": "camp_001",
                    "name": "Growth Solutions - 202501",
                    "spend": 1234.56,
                    "conversions": 45,
                    "performance_score": 82.5
                },
                {
                    "campaign_id": "camp_002",
                    "name": "Marketing Automation - 202501",
                    "spend": 1222.22,
                    "conversions": 44,
                    "performance_score": 78.3
                }
            ],
            "insights": [
                "Strong performance in 'growth solutions' keywords",
                "Mobile traffic showing 20% higher conversion rate",
                "Authority impact scores increasing week-over-week"
            ],
            "recommendations": [
                "Increase budget allocation to top-performing campaign",
                "Add more mobile-optimized ad copy",
                "Test new landing page variations"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budget/status/{client_id}")
async def get_budget_status(client_id: UUID) -> Dict[str, Any]:
    """Get current budget utilization status"""
    try:
        # Mock response
        return {
            "client_id": str(client_id),
            "month": datetime.now().strftime("%Y-%m"),
            "budget_allocation": {
                "total_monthly": 10000.00,
                "allocated": 8750.00,
                "spent_to_date": 4325.67,
                "remaining": 5674.33,
                "utilization_percentage": 43.26
            },
            "campaign_budgets": [
                {
                    "campaign_id": "camp_001",
                    "allocated": 2500.00,
                    "spent": 1234.56,
                    "remaining": 1265.44
                },
                {
                    "campaign_id": "camp_002",
                    "allocated": 2500.00,
                    "spent": 1222.22,
                    "remaining": 1277.78
                }
            ],
            "projected_month_end": 8651.34,
            "budget_health": "optimal"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/{client_id}")
async def get_campaign_queue(
    client_id: UUID,
    manager: CampaignManager = Depends(get_campaign_manager)
) -> Dict[str, Any]:
    """Get queued campaigns waiting for budget allocation"""
    try:
        # Get from campaign manager
        dashboard = await manager.get_campaign_dashboard_data(client_id)
        
        return {
            "client_id": str(client_id),
            "queued_campaigns": dashboard.get("queued_campaigns", []),
            "queue_size": len(dashboard.get("queued_campaigns", [])),
            "next_rotation_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))