"""
Human Loop Coordinator for CIA system.
Manages human-in-loop workflows for DataForSEO and Perplexity.
"""

import logging
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from ..config.constants import HumanLoopType, NotificationType
from ..database.models import HumanLoopState, HumanLoopStateCreate
from ..database.repositories import HumanLoopRepository

logger = logging.getLogger(__name__)


class HumanLoopCoordinator:
    """Coordinates human-in-loop workflows for CIA phases."""
    
    def __init__(self, human_loop_repository: HumanLoopRepository):
        """Initialize the coordinator.
        
        Args:
            human_loop_repository: Repository for human loop states
        """
        self.repository = human_loop_repository
    
    async def initiate_workflow(
        self,
        session_id: UUID,
        phase_id: str,
        loop_type: HumanLoopType,
        request_data: Dict[str, Any],
        client_id: UUID,
        notification_channels: Optional[List[str]] = None
    ) -> HumanLoopState:
        """Initiate a human-in-loop workflow.
        
        Args:
            session_id: CIA session ID
            phase_id: Phase requiring human input
            loop_type: Type of human input needed
            request_data: Data for the request
            client_id: Client ID
            notification_channels: Channels for notifications
            
        Returns:
            Created HumanLoopState
        """
        # Build request message based on type
        request_message = self._build_request_message(loop_type, request_data)
        
        # Create human loop state
        loop_state = await self.repository.create_loop_state(
            session_id=session_id,
            phase_id=phase_id,
            loop_type=loop_type,
            request_data=request_data,
            request_message=request_message,
            client_id=client_id,
            notification_channels=notification_channels
        )
        
        logger.info(f"Initiated {loop_type.value} workflow for session {session_id}")
        
        # TODO: Send notifications (Slack/Email) - would be implemented here
        # For now, just log the requirement
        logger.warning(f"HUMAN INPUT REQUIRED: {request_message}")
        
        return loop_state
    
    def _build_request_message(
        self,
        loop_type: HumanLoopType,
        request_data: Dict[str, Any]
    ) -> str:
        """Build human-readable request message.
        
        Args:
            loop_type: Type of human input needed
            request_data: Request data
            
        Returns:
            Human-readable message
        """
        if loop_type == HumanLoopType.DATAFORSEO_KEYWORDS:
            keywords = request_data.get("keywords", [])
            return (
                f"Phase 2A requires DataForSEO keyword lookup.\n"
                f"Please search for the following keywords and provide search volume, "
                f"competition, and CPC data:\n" + 
                "\n".join(f"- {kw}" for kw in keywords)
            )
        
        elif loop_type == HumanLoopType.PERPLEXITY_TRENDS:
            prompt = request_data.get("research_prompt", "")
            return (
                f"Phase 3A requires Perplexity trend research.\n"
                f"Please run the following prompt in Perplexity with Claude 3 Beta model:\n\n"
                f"{prompt}\n\n"
                f"Paste the complete research results back when ready."
            )
        
        elif loop_type == HumanLoopType.TESTIMONIALS_REQUEST:
            company = request_data.get("company_name", "the company")
            return (
                f"Phase 3B requires testimonials for {company}.\n"
                f"Please provide customer testimonials, reviews, and success stories.\n"
                f"If testimonials are not available, type 'continue' to proceed with framework only."
            )
        
        else:
            return f"Human input required for {loop_type.value}"
    
    async def process_response(
        self,
        loop_id: UUID,
        response_data: Dict[str, Any],
        client_id: UUID
    ) -> bool:
        """Process human response for a loop.
        
        Args:
            loop_id: Human loop state ID
            response_data: Response from human
            client_id: Client ID
            
        Returns:
            True if processed successfully
        """
        try:
            # Submit response
            loop_state = await self.repository.submit_response(
                loop_id=loop_id,
                response_data=response_data,
                client_id=client_id
            )
            
            if not loop_state:
                logger.error(f"Failed to submit response for loop {loop_id}")
                return False
            
            # Validate response
            if not loop_state.response_validated:
                logger.error(f"Response validation failed: {loop_state.validation_errors}")
                return False
            
            logger.info(f"Successfully processed response for loop {loop_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing human response: {e}")
            return False
    
    async def check_pending_loops(
        self,
        client_id: Optional[UUID] = None
    ) -> List[HumanLoopState]:
        """Check for pending human input requests.
        
        Args:
            client_id: Optional client ID filter
            
        Returns:
            List of pending loops
        """
        return await self.repository.get_pending_loops(client_id, include_expired=False)
    
    async def send_reminders(self, client_id: Optional[UUID] = None) -> int:
        """Send reminders for pending loops.
        
        Args:
            client_id: Optional client ID filter
            
        Returns:
            Number of reminders sent
        """
        loops_needing_reminder = await self.repository.get_loops_needing_reminder(client_id)
        
        reminder_count = 0
        for loop in loops_needing_reminder:
            try:
                # TODO: Send actual reminder notification
                logger.info(f"Sending reminder for loop {loop.id}")
                
                # Mark reminder as sent
                await self.repository.send_reminder(loop.id, loop.client_id)
                reminder_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send reminder for loop {loop.id}: {e}")
        
        return reminder_count
    
    async def handle_expired_loops(
        self,
        client_id: Optional[UUID] = None
    ) -> List[HumanLoopState]:
        """Handle expired human input loops.
        
        Args:
            client_id: Optional client ID filter
            
        Returns:
            List of expired loops
        """
        expired = await self.repository.expire_old_loops(client_id)
        
        for loop in expired:
            logger.warning(f"Human loop {loop.id} expired for session {loop.session_id}")
            
            # TODO: Could trigger automatic fallback or notification
        
        return expired
    
    async def get_response_stats(
        self,
        client_id: Optional[UUID] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get statistics on human response times.
        
        Args:
            client_id: Optional client ID filter
            days: Number of days to analyze
            
        Returns:
            Statistics dictionary
        """
        return await self.repository.get_response_time_stats(client_id, days)
    
    def validate_dataforseo_response(self, response_data: Dict[str, Any]) -> bool:
        """Validate DataForSEO response format.
        
        Args:
            response_data: Response to validate
            
        Returns:
            True if valid
        """
        required = ["search_volume", "competition", "cpc"]
        return all(field in response_data for field in required)
    
    def validate_perplexity_response(self, response_data: Dict[str, Any]) -> bool:
        """Validate Perplexity response format.
        
        Args:
            response_data: Response to validate
            
        Returns:
            True if valid
        """
        return "research_results" in response_data and bool(response_data["research_results"])
    
    def format_dataforseo_for_cia(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format DataForSEO data for CIA processing.
        
        Args:
            raw_data: Raw DataForSEO response
            
        Returns:
            Formatted data for CIA
        """
        formatted = {
            "keywords_data": {},
            "total_search_volume": 0,
            "avg_competition": 0.0,
            "avg_cpc": 0.0
        }
        
        # Process keyword data
        if "keywords" in raw_data:
            for kw_data in raw_data["keywords"]:
                keyword = kw_data.get("keyword", "")
                formatted["keywords_data"][keyword] = {
                    "search_volume": kw_data.get("search_volume", 0),
                    "competition": kw_data.get("competition", 0),
                    "cpc": kw_data.get("cpc", 0)
                }
                formatted["total_search_volume"] += kw_data.get("search_volume", 0)
        
        # Calculate averages
        if formatted["keywords_data"]:
            num_keywords = len(formatted["keywords_data"])
            total_competition = sum(kw["competition"] for kw in formatted["keywords_data"].values())
            total_cpc = sum(kw["cpc"] for kw in formatted["keywords_data"].values())
            
            formatted["avg_competition"] = total_competition / num_keywords
            formatted["avg_cpc"] = total_cpc / num_keywords
        
        return formatted
    
    def format_perplexity_for_cia(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format Perplexity data for CIA processing.
        
        Args:
            raw_data: Raw Perplexity response
            
        Returns:
            Formatted data for CIA
        """
        formatted = {
            "trending_topics": [],
            "viral_content": [],
            "engagement_patterns": [],
            "research_summary": ""
        }
        
        research_results = raw_data.get("research_results", "")
        
        # Extract structured data from research results
        # This is simplified - actual implementation would use NLP
        if research_results:
            formatted["research_summary"] = research_results
            
            # Look for trending topics
            if "trending" in research_results.lower():
                # Extract trending mentions
                lines = research_results.split('\n')
                for line in lines:
                    if "trend" in line.lower():
                        formatted["trending_topics"].append(line.strip())
            
            # Look for viral content mentions
            if "viral" in research_results.lower():
                lines = research_results.split('\n')
                for line in lines:
                    if "viral" in line.lower():
                        formatted["viral_content"].append(line.strip())
        
        return formatted