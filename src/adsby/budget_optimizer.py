"""
Budget Optimization Engine
Analyzes campaign performance and recommends budget rotations
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from .models import (
    AdCampaign, BudgetRotation, PerformanceMetric,
    CampaignStatus, OptimizationRecommendation
)

logger = logging.getLogger(__name__)

# Optimization parameters
PERFORMANCE_WEIGHTS = {
    PerformanceMetric.CTR: 0.25,
    PerformanceMetric.CONVERSION_RATE: 0.30,
    PerformanceMetric.AUTHORITY_IMPACT: 0.25,
    PerformanceMetric.COST_PER_ACQUISITION: 0.20
}

ROTATION_THRESHOLD = 20.0  # Minimum performance gap for rotation
MIN_CAMPAIGN_AGE_DAYS = 7  # Minimum days before rotation eligible
UNDERPERFORMANCE_THRESHOLD = 50.0  # Composite score below this triggers review


class BudgetOptimizer:
    """
    Optimizes $10k monthly budget allocation across campaigns
    based on performance metrics and authority impact
    """
    
    def __init__(self):
        self.performance_weights = PERFORMANCE_WEIGHTS
        self.rotation_threshold = ROTATION_THRESHOLD
        self.min_campaign_age = MIN_CAMPAIGN_AGE_DAYS
    
    async def analyze_weekly_performance(
        self,
        campaigns: List[AdCampaign],
        campaign_queue: List[Dict[str, Any]]
    ) -> BudgetRotation:
        """
        Analyze campaign performance and recommend budget rotation
        
        Args:
            campaigns: Active campaigns to analyze
            campaign_queue: Queue of pending campaigns
            
        Returns:
            BudgetRotation recommendation
        """
        try:
            logger.info(f"Analyzing performance for {len(campaigns)} campaigns")
            
            # Calculate composite scores for all campaigns
            campaign_scores = await self._calculate_campaign_scores(campaigns)
            
            # Sort by performance
            sorted_campaigns = sorted(
                campaign_scores.items(),
                key=lambda x: x[1]["composite_score"],
                reverse=True
            )
            
            # Generate rotation recommendation
            rotation = await self._generate_rotation_recommendation(
                sorted_campaigns,
                campaign_queue
            )
            
            return rotation
            
        except Exception as e:
            logger.error(f"Error analyzing weekly performance: {str(e)}")
            raise
    
    async def get_optimization_recommendations(
        self, campaigns: List[AdCampaign]
    ) -> List[OptimizationRecommendation]:
        """
        Generate specific optimization recommendations for campaigns
        
        Args:
            campaigns: Campaigns to analyze
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        for campaign in campaigns:
            # Analyze individual campaign performance
            issues = await self._identify_campaign_issues(campaign)
            
            for issue in issues:
                recommendation = OptimizationRecommendation(
                    campaign_id=campaign.campaign_id,
                    recommendation_type=issue["type"],
                    priority=issue["priority"],
                    reason=issue["reason"],
                    expected_impact=issue["impact"],
                    specific_actions=issue["actions"]
                )
                recommendations.append(recommendation)
        
        # Sort by priority
        recommendations.sort(
            key=lambda x: {"high": 0, "medium": 1, "low": 2}[x.priority]
        )
        
        return recommendations
    
    async def calculate_budget_reallocation(
        self, campaigns: List[AdCampaign]
    ) -> Dict[str, float]:
        """
        Calculate optimal budget reallocation based on performance
        
        Args:
            campaigns: Campaigns to reallocate budget between
            
        Returns:
            Dictionary of campaign_id to new budget allocation
        """
        if not campaigns:
            return {}
        
        # Get total available budget
        total_budget = sum(c.budget_allocated for c in campaigns)
        
        # Calculate performance scores
        scores = await self._calculate_campaign_scores(campaigns)
        
        # Calculate performance-based allocation
        total_score = sum(s["composite_score"] for s in scores.values())
        
        if total_score == 0:
            # Equal distribution if no performance data
            equal_budget = total_budget / len(campaigns)
            return {c.campaign_id: equal_budget for c in campaigns}
        
        # Allocate proportionally to performance
        allocations = {}
        for campaign_id, score_data in scores.items():
            score_ratio = score_data["composite_score"] / total_score
            
            # Apply minimum and maximum constraints
            min_budget = total_budget * 0.15  # Minimum 15%
            max_budget = total_budget * 0.40  # Maximum 40%
            
            allocated = total_budget * score_ratio
            allocated = max(min_budget, min(allocated, max_budget))
            
            allocations[campaign_id] = round(allocated, 2)
        
        # Ensure total equals available budget (handle rounding)
        total_allocated = sum(allocations.values())
        if total_allocated != total_budget:
            # Adjust highest performer
            top_campaign = max(allocations.items(), key=lambda x: x[1])[0]
            allocations[top_campaign] += (total_budget - total_allocated)
        
        return allocations
    
    # Private helper methods
    
    async def _calculate_campaign_scores(
        self, campaigns: List[AdCampaign]
    ) -> Dict[str, Dict[str, Any]]:
        """Calculate composite scores for all campaigns"""
        scores = {}
        
        for campaign in campaigns:
            # Calculate composite score
            composite_score = await self._calculate_composite_score(
                campaign.performance_metrics
            )
            
            # Add campaign age factor
            age_factor = min(campaign.days_active / 30, 1.0)  # Full weight after 30 days
            adjusted_score = composite_score * (0.7 + 0.3 * age_factor)
            
            scores[campaign.campaign_id] = {
                "campaign": campaign,
                "composite_score": adjusted_score,
                "raw_score": composite_score,
                "metrics": campaign.performance_metrics,
                "age_days": campaign.days_active
            }
        
        return scores
    
    async def _calculate_composite_score(
        self, metrics: Dict[PerformanceMetric, float]
    ) -> float:
        """Calculate weighted composite performance score"""
        score = 0.0
        
        for metric, weight in self.performance_weights.items():
            value = metrics.get(metric, 0.0)
            
            # Normalize values
            if metric == PerformanceMetric.CTR:
                # CTR: 0-5% normalized to 0-100
                normalized = min(value * 20, 100)
            elif metric == PerformanceMetric.CONVERSION_RATE:
                # Conversion: 0-10% normalized to 0-100
                normalized = min(value * 10, 100)
            elif metric == PerformanceMetric.AUTHORITY_IMPACT:
                # Already 0-100
                normalized = value
            elif metric == PerformanceMetric.COST_PER_ACQUISITION:
                # CPA: Lower is better, $100 = 0, $0 = 100
                normalized = max(0, 100 - value)
            else:
                normalized = value
            
            score += normalized * weight
        
        return min(score, 100.0)
    
    async def _generate_rotation_recommendation(
        self,
        sorted_campaigns: List[Tuple[str, Dict[str, Any]]],
        campaign_queue: List[Dict[str, Any]]
    ) -> BudgetRotation:
        """Generate rotation recommendation based on performance analysis"""
        
        current_campaign_ids = [item[0] for item in sorted_campaigns]
        
        # Check if rotation is warranted
        if len(sorted_campaigns) < 2:
            # Not enough campaigns to rotate
            return self._create_no_action_rotation(current_campaign_ids)
        
        # Get best and worst performers
        best_campaign = sorted_campaigns[0]
        worst_campaign = sorted_campaigns[-1]
        
        # Calculate performance gap
        performance_gap = (
            best_campaign[1]["composite_score"] - 
            worst_campaign[1]["composite_score"]
        )
        
        # Check if worst performer is eligible for rotation
        worst_age = worst_campaign[1]["age_days"]
        worst_score = worst_campaign[1]["composite_score"]
        
        if (performance_gap > self.rotation_threshold and 
            worst_age >= self.min_campaign_age and
            worst_score < UNDERPERFORMANCE_THRESHOLD and
            campaign_queue):  # Must have campaigns in queue
            
            # Recommend rotation
            return BudgetRotation(
                rotation_id=f"rot_{datetime.now().strftime('%Y%m%d_%H%M')}",
                week_date=datetime.now().strftime("%Y-W%U"),
                current_campaigns=current_campaign_ids,
                campaign_to_pause=worst_campaign[0],
                campaign_to_promote="next_in_queue",
                reasoning=(
                    f"Campaign '{worst_campaign[1]['campaign'].title}' "
                    f"underperforming with score {worst_score:.1f} vs "
                    f"top performer at {best_campaign[1]['composite_score']:.1f}. "
                    f"Performance gap of {performance_gap:.1f} points."
                ),
                projected_performance={
                    "expected_improvement": performance_gap * 0.5,
                    "confidence": "high" if performance_gap > 30 else "medium",
                    "risk_level": "low"
                },
                rotation_date=datetime.now() + timedelta(days=1),
                requires_action=True
            )
        else:
            # No rotation needed
            reasons = []
            if performance_gap <= self.rotation_threshold:
                reasons.append(
                    f"Performance gap ({performance_gap:.1f}) below threshold"
                )
            if worst_age < self.min_campaign_age:
                reasons.append(
                    f"Newest campaign only {worst_age} days old"
                )
            if not campaign_queue:
                reasons.append("No campaigns in queue")
            
            return BudgetRotation(
                rotation_id=f"no_rot_{datetime.now().strftime('%Y%m%d_%H%M')}",
                week_date=datetime.now().strftime("%Y-W%U"),
                current_campaigns=current_campaign_ids,
                campaign_to_pause=None,
                campaign_to_promote=None,
                reasoning=". ".join(reasons) or "All campaigns performing acceptably",
                projected_performance={
                    "status": "maintain_current",
                    "avg_score": sum(s[1]["composite_score"] for s in sorted_campaigns) / len(sorted_campaigns)
                },
                rotation_date=datetime.now() + timedelta(days=7),
                requires_action=False
            )
    
    async def _identify_campaign_issues(
        self, campaign: AdCampaign
    ) -> List[Dict[str, Any]]:
        """Identify specific issues with a campaign"""
        issues = []
        metrics = campaign.performance_metrics
        
        # Check CTR
        ctr = metrics.get(PerformanceMetric.CTR, 0)
        if ctr < 1.5:
            issues.append({
                "type": "improve_ad_copy",
                "priority": "high",
                "reason": f"CTR {ctr:.2f}% is below target 1.5%",
                "impact": {"ctr_improvement": "50-100%"},
                "actions": [
                    "Test new ad headlines focusing on benefits",
                    "Include numbers and specific outcomes",
                    "Add emotional triggers from CIA analysis"
                ]
            })
        
        # Check conversion rate
        conv_rate = metrics.get(PerformanceMetric.CONVERSION_RATE, 0)
        if conv_rate < 2.0:
            issues.append({
                "type": "optimize_landing_page",
                "priority": "high",
                "reason": f"Conversion rate {conv_rate:.2f}% is below target 2%",
                "impact": {"conversion_improvement": "30-50%"},
                "actions": [
                    "Simplify landing page form",
                    "Add trust signals and testimonials",
                    "Improve mobile responsiveness",
                    "Match ad copy to landing page headline"
                ]
            })
        
        # Check CPA
        cpa = metrics.get(PerformanceMetric.COST_PER_ACQUISITION, 0)
        if cpa > 75:
            issues.append({
                "type": "reduce_cpa",
                "priority": "medium",
                "reason": f"CPA ${cpa:.2f} exceeds target $75",
                "impact": {"cost_reduction": "20-30%"},
                "actions": [
                    "Add negative keywords to reduce waste",
                    "Pause underperforming keywords",
                    "Test automated bidding strategies",
                    "Improve Quality Score"
                ]
            })
        
        # Check authority impact
        authority = metrics.get(PerformanceMetric.AUTHORITY_IMPACT, 0)
        if authority < 30:
            issues.append({
                "type": "boost_authority",
                "priority": "medium",
                "reason": f"Authority impact {authority:.1f} is low",
                "impact": {"brand_lift": "25-40%"},
                "actions": [
                    "Create more educational content",
                    "Focus on thought leadership keywords",
                    "Encourage content sharing",
                    "Build retargeting campaigns"
                ]
            })
        
        return issues
    
    def _create_no_action_rotation(
        self, current_campaigns: List[str]
    ) -> BudgetRotation:
        """Create a no-action rotation recommendation"""
        return BudgetRotation(
            rotation_id=f"no_action_{datetime.now().strftime('%Y%m%d_%H%M')}",
            week_date=datetime.now().strftime("%Y-W%U"),
            current_campaigns=current_campaigns,
            campaign_to_pause=None,
            campaign_to_promote=None,
            reasoning="Insufficient campaigns for rotation analysis",
            projected_performance={"status": "insufficient_data"},
            rotation_date=datetime.now() + timedelta(days=7),
            requires_action=False
        )