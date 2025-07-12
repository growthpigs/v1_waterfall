"""
Slack Notification Service
Mock implementation for testing
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Mock Slack notification service for testing"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or "https://hooks.slack.com/mock"
        self.enabled = False  # Disabled for testing
    
    async def send_budget_rotation_notification(
        self,
        campaign_id: str,
        old_budget: float,
        new_budget: float,
        reason: str,
        **kwargs
    ) -> bool:
        """Mock budget rotation notification"""
        message = f"Budget rotation for campaign {campaign_id}: ${old_budget:.2f} → ${new_budget:.2f} ({reason})"
        logger.info(f"[MOCK SLACK] {message}")
        return True
    
    async def send_campaign_performance_alert(
        self,
        campaign_id: str,
        performance_score: float,
        threshold: float,
        **kwargs
    ) -> bool:
        """Mock performance alert"""
        message = f"Campaign {campaign_id} performance alert: {performance_score:.1f} below threshold {threshold:.1f}"
        logger.info(f"[MOCK SLACK] {message}")
        return True
    
    async def send_message(self, message: str, channel: Optional[str] = None) -> bool:
        """Mock generic message sending"""
        logger.info(f"[MOCK SLACK] {message}")
        return True