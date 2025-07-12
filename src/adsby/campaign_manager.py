"""
Adsby Campaign Manager
Orchestrates $10k Google Ad Grant budget rotation across campaigns
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import asyncio
import logging

from ..database.cartwheel_models import ContentCluster
from .models import AdCampaign, CampaignStatus, BudgetRotation, PerformanceMetric
from .campaign_creator import CampaignCreator
from .budget_optimizer import BudgetOptimizer
from .performance_tracker import PerformanceTracker
from ..integrations.google_ads_api import GoogleAdsClient
from ..notifications.slack_notifier import SlackNotifier

logger = logging.getLogger(__name__)

# Campaign configuration
MONTHLY_BUDGET = 10000.0  # $10k Google Ad Grant
MAX_ACTIVE_CAMPAIGNS = 4  # Maximum concurrent campaigns
CAMPAIGN_BUDGET = 2500.0  # $2.5k per campaign
ROTATION_THRESHOLD = 20.0  # Performance gap threshold for rotation
MIN_CAMPAIGN_DURATION = 7  # Minimum days before rotation eligible


class CampaignManager:
    """
    Main orchestrator for Adsby campaign management
    Handles campaign lifecycle, budget rotation, and optimization
    """
    
    def __init__(
        self,
        google_ads_client: Optional[GoogleAdsClient] = None,
        slack_notifier: Optional[SlackNotifier] = None
    ):
        self.google_ads = google_ads_client
        self.campaign_creator = CampaignCreator(google_ads_client)
        self.budget_optimizer = BudgetOptimizer()
        self.performance_tracker = PerformanceTracker(google_ads_client)
        self.slack = slack_notifier
        
        # Campaign management state
        self.active_campaigns: List[AdCampaign] = []
        self.campaign_queue: List[Dict[str, Any]] = []
        self.total_monthly_budget = MONTHLY_BUDGET
        self.max_active_campaigns = MAX_ACTIVE_CAMPAIGNS
    
    async def process_content_cluster(
        self,
        content_cluster: ContentCluster,
        cia_intelligence: Dict[str, Any],
        client_id: UUID
    ) -> AdCampaign:
        """
        Process a new content cluster for ad campaign creation
        
        Args:
            content_cluster: Generated content cluster
            cia_intelligence: CIA analysis for targeting
            client_id: Client identifier
            
        Returns:
            Created AdCampaign instance
        """
        try:
            logger.info(f"Processing content cluster for campaign: {content_cluster.cluster_topic}")
            
            # Create campaign from content cluster
            campaign = await self.campaign_creator.create_from_cluster(
                content_cluster=content_cluster,
                cia_intelligence=cia_intelligence,
                client_id=client_id,
                budget=CAMPAIGN_BUDGET
            )
            
            # Check if we can activate immediately
            if len(self.active_campaigns) < self.max_active_campaigns:
                # Activate campaign immediately
                await self._activate_campaign(campaign)
                self.active_campaigns.append(campaign)
                
                # Send notification
                if self.slack:
                    await self.slack.send_campaign_notification(
                        f"✅ Campaign Activated: {campaign.title}",
                        {
                            "Client": str(client_id),
                            "Budget": f"${campaign.budget_allocated:,.2f}",
                            "Keywords": len(campaign.keywords),
                            "Landing Page": campaign.landing_page_url
                        }
                    )
            else:
                # Add to queue for next rotation
                self.campaign_queue.append({
                    "campaign": campaign,
                    "cluster": content_cluster,
                    "intelligence": cia_intelligence,
                    "queued_at": datetime.now()
                })
                
                logger.info(f"Campaign queued: {campaign.title} (Queue size: {len(self.campaign_queue)})")
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error processing content cluster: {str(e)}")
            raise
    
    async def run_weekly_optimization(self, client_id: UUID) -> BudgetRotation:
        """
        Run weekly performance analysis and budget optimization
        
        Args:
            client_id: Client identifier
            
        Returns:
            BudgetRotation recommendation
        """
        try:
            logger.info(f"Running weekly optimization for client {client_id}")
            
            # Update performance metrics for all active campaigns
            for campaign in self.active_campaigns:
                if campaign.client_id == str(client_id):
                    metrics = await self.performance_tracker.get_campaign_metrics(
                        campaign.campaign_id
                    )
                    campaign.performance_metrics = metrics
            
            # Get client's active campaigns
            client_campaigns = [
                c for c in self.active_campaigns 
                if c.client_id == str(client_id)
            ]
            
            if not client_campaigns:
                logger.warning(f"No active campaigns for client {client_id}")
                return None
            
            # Analyze performance and get rotation recommendation
            rotation = await self.budget_optimizer.analyze_weekly_performance(
                campaigns=client_campaigns,
                campaign_queue=self.campaign_queue
            )
            
            # Send notification for review
            if self.slack and rotation.requires_action:
                await self._send_rotation_notification(rotation, client_id)
            
            return rotation
            
        except Exception as e:
            logger.error(f"Error in weekly optimization: {str(e)}")
            raise
    
    async def execute_budget_rotation(
        self, rotation: BudgetRotation, approved_by: str
    ) -> Dict[str, Any]:
        """
        Execute approved budget rotation
        
        Args:
            rotation: Approved rotation plan
            approved_by: User who approved the rotation
            
        Returns:
            Results of rotation execution
        """
        try:
            logger.info(f"Executing budget rotation {rotation.rotation_id}")
            
            results = {
                "rotation_id": rotation.rotation_id,
                "executed_at": datetime.now(),
                "approved_by": approved_by,
                "actions_taken": [],
                "campaigns_paused": [],
                "campaigns_activated": []
            }
            
            # Pause underperforming campaign if specified
            if rotation.campaign_to_pause:
                campaign = await self._find_campaign(rotation.campaign_to_pause)
                if campaign:
                    await self._pause_campaign(campaign)
                    self.active_campaigns.remove(campaign)
                    results["campaigns_paused"].append({
                        "campaign_id": campaign.campaign_id,
                        "title": campaign.title,
                        "total_spend": campaign.spend_to_date
                    })
                    results["actions_taken"].append(
                        f"Paused campaign: {campaign.title}"
                    )
            
            # Activate new campaign from queue if specified
            if rotation.campaign_to_promote and self.campaign_queue:
                # Find specific campaign or take next from queue
                next_campaign = None
                if rotation.campaign_to_promote == "next_in_queue":
                    next_campaign = self.campaign_queue.pop(0)["campaign"]
                else:
                    # Find specific campaign in queue
                    for i, queued in enumerate(self.campaign_queue):
                        if queued["campaign"].campaign_id == rotation.campaign_to_promote:
                            next_campaign = self.campaign_queue.pop(i)["campaign"]
                            break
                
                if next_campaign:
                    await self._activate_campaign(next_campaign)
                    self.active_campaigns.append(next_campaign)
                    results["campaigns_activated"].append({
                        "campaign_id": next_campaign.campaign_id,
                        "title": next_campaign.title,
                        "budget": next_campaign.budget_allocated
                    })
                    results["actions_taken"].append(
                        f"Activated campaign: {next_campaign.title}"
                    )
            
            # Update rotation status
            rotation.executed_at = datetime.now()
            rotation.executed_by = approved_by
            
            # Send completion notification
            if self.slack:
                await self.slack.send_campaign_notification(
                    "🔄 Budget Rotation Completed",
                    {
                        "Actions": ", ".join(results["actions_taken"]),
                        "Approved By": approved_by,
                        "Queue Size": len(self.campaign_queue)
                    }
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing budget rotation: {str(e)}")
            raise
    
    async def get_campaign_dashboard_data(
        self, client_id: UUID
    ) -> Dict[str, Any]:
        """
        Get comprehensive campaign data for dashboard display
        
        Args:
            client_id: Client identifier
            
        Returns:
            Dashboard data dictionary
        """
        try:
            # Get client's campaigns
            active = [c for c in self.active_campaigns if c.client_id == str(client_id)]
            queued = [
                q for q in self.campaign_queue 
                if q["campaign"].client_id == str(client_id)
            ]
            
            # Calculate budget utilization
            total_allocated = sum(c.budget_allocated for c in active)
            total_spent = sum(c.spend_to_date for c in active)
            
            # Get performance summary
            performance_summary = await self._calculate_performance_summary(active)
            
            return {
                "summary": {
                    "active_campaigns": len(active),
                    "queued_campaigns": len(queued),
                    "budget_allocated": total_allocated,
                    "budget_spent": total_spent,
                    "budget_remaining": total_allocated - total_spent,
                    "avg_performance_score": performance_summary["avg_score"]
                },
                "active_campaigns": [
                    {
                        "campaign_id": c.campaign_id,
                        "title": c.title,
                        "status": c.status.value,
                        "budget_allocated": c.budget_allocated,
                        "spend_to_date": c.spend_to_date,
                        "performance_score": c.performance_metrics.get("composite_score", 0),
                        "ctr": c.performance_metrics.get(PerformanceMetric.CTR, 0),
                        "conversion_rate": c.performance_metrics.get(PerformanceMetric.CONVERSION_RATE, 0),
                        "authority_impact": c.performance_metrics.get(PerformanceMetric.AUTHORITY_IMPACT, 0),
                        "days_active": (datetime.now() - c.start_date).days
                    }
                    for c in active
                ],
                "queued_campaigns": [
                    {
                        "campaign_id": q["campaign"].campaign_id,
                        "title": q["campaign"].title,
                        "cluster_topic": q["cluster"].cluster_topic,
                        "queued_at": q["queued_at"],
                        "queue_position": i + 1
                    }
                    for i, q in enumerate(queued)
                ],
                "performance_trends": performance_summary["trends"],
                "optimization_opportunities": await self._identify_opportunities(active)
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {}
    
    async def pause_campaign_manually(
        self, campaign_id: str, reason: str, paused_by: str
    ) -> bool:
        """
        Manually pause a campaign
        
        Args:
            campaign_id: Campaign to pause
            reason: Reason for pausing
            paused_by: User initiating pause
            
        Returns:
            Success status
        """
        try:
            campaign = await self._find_campaign(campaign_id)
            if not campaign:
                logger.error(f"Campaign not found: {campaign_id}")
                return False
            
            await self._pause_campaign(campaign)
            self.active_campaigns.remove(campaign)
            
            # Log manual action
            logger.info(
                f"Campaign manually paused: {campaign.title} "
                f"by {paused_by} - Reason: {reason}"
            )
            
            # Send notification
            if self.slack:
                await self.slack.send_campaign_notification(
                    "⏸️ Campaign Manually Paused",
                    {
                        "Campaign": campaign.title,
                        "Paused By": paused_by,
                        "Reason": reason,
                        "Total Spend": f"${campaign.spend_to_date:,.2f}"
                    }
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error pausing campaign: {str(e)}")
            return False
    
    # Private helper methods
    
    async def _activate_campaign(self, campaign: AdCampaign):
        """Activate campaign through Google Ads"""
        if self.google_ads:
            await self.google_ads.activate_campaign(
                campaign_id=campaign.campaign_id,
                budget=campaign.budget_allocated
            )
        
        campaign.status = CampaignStatus.ACTIVE
        campaign.start_date = datetime.now()
        logger.info(f"Campaign activated: {campaign.title}")
    
    async def _pause_campaign(self, campaign: AdCampaign):
        """Pause campaign through Google Ads"""
        if self.google_ads:
            await self.google_ads.pause_campaign(campaign.campaign_id)
        
        campaign.status = CampaignStatus.PAUSED
        campaign.end_date = datetime.now()
        logger.info(f"Campaign paused: {campaign.title}")
    
    async def _find_campaign(self, campaign_id: str) -> Optional[AdCampaign]:
        """Find campaign by ID in active campaigns"""
        return next(
            (c for c in self.active_campaigns if c.campaign_id == campaign_id),
            None
        )
    
    async def _send_rotation_notification(
        self, rotation: BudgetRotation, client_id: UUID
    ):
        """Send Slack notification for rotation review"""
        if not self.slack:
            return
        
        # Build notification message
        if rotation.campaign_to_pause:
            action = f"Pause '{rotation.campaign_to_pause}' and activate new campaign"
        else:
            action = "No rotation needed - all campaigns performing well"
        
        await self.slack.send_approval_request(
            title="Weekly Budget Rotation Review",
            fields={
                "Client": str(client_id),
                "Week": rotation.week_date,
                "Recommendation": action,
                "Reasoning": rotation.reasoning,
                "Expected Impact": f"{rotation.projected_performance.get('expected_improvement', 0):.1f}% improvement"
            },
            approval_id=rotation.rotation_id
        )
    
    async def _calculate_performance_summary(
        self, campaigns: List[AdCampaign]
    ) -> Dict[str, Any]:
        """Calculate aggregate performance metrics"""
        if not campaigns:
            return {"avg_score": 0, "trends": {}}
        
        # Calculate averages
        total_score = sum(
            c.performance_metrics.get("composite_score", 0) 
            for c in campaigns
        )
        avg_score = total_score / len(campaigns)
        
        # Calculate trends (simplified for now)
        trends = {
            "ctr": "stable",
            "conversions": "rising",
            "authority": "rising"
        }
        
        return {
            "avg_score": avg_score,
            "trends": trends
        }
    
    async def _identify_opportunities(
        self, campaigns: List[AdCampaign]
    ) -> List[Dict[str, str]]:
        """Identify optimization opportunities"""
        opportunities = []
        
        for campaign in campaigns:
            # Check for low CTR
            ctr = campaign.performance_metrics.get(PerformanceMetric.CTR, 0)
            if ctr < 2.0:
                opportunities.append({
                    "campaign": campaign.title,
                    "issue": "Low CTR",
                    "recommendation": "Review ad copy and keyword relevance"
                })
            
            # Check for high CPA
            cpa = campaign.performance_metrics.get(PerformanceMetric.COST_PER_ACQUISITION, 0)
            if cpa > 50:
                opportunities.append({
                    "campaign": campaign.title,
                    "issue": "High CPA",
                    "recommendation": "Optimize landing page conversion"
                })
        
        return opportunities[:5]  # Top 5 opportunities