"""
Repository for Human Loop State operations.
Manages human-in-loop workflows, notifications, and response tracking.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
import logging

from .base import BaseRepository
from ..models import (
    HumanLoopState,
    HumanLoopStateCreate,
    HumanLoopStateUpdate,
    HumanLoopResponse
)
from ...config.constants import HumanLoopType, TABLE_HUMAN_LOOP_STATES

logger = logging.getLogger(__name__)


class HumanLoopRepository(BaseRepository[HumanLoopState, HumanLoopStateCreate, HumanLoopStateUpdate]):
    """Repository for human loop state database operations."""
    
    def __init__(self):
        """Initialize human loop repository."""
        super().__init__(
            model=HumanLoopState,
            table_name=TABLE_HUMAN_LOOP_STATES
        )
    
    async def create_loop_state(
        self,
        session_id: UUID,
        phase_id: str,
        loop_type: HumanLoopType,
        request_data: Dict[str, Any],
        request_message: str,
        client_id: UUID,
        notification_channels: Optional[List[str]] = None,
        timeout_minutes: int = 30
    ) -> HumanLoopState:
        """Create a new human loop state."""
        try:
            loop_data = HumanLoopStateCreate(
                session_id=session_id,
                phase_id=phase_id,
                loop_type=loop_type,
                request_data=request_data,
                request_message=request_message,
                notification_channels=notification_channels or ["slack", "email"],
                timeout_minutes=timeout_minutes
            )
            
            loop_state = await self.create(loop_data, client_id)
            
            logger.info(f"Created human loop state for session {session_id}, type {loop_type}")
            return loop_state
            
        except Exception as e:
            logger.error(f"Failed to create human loop state: {e}")
            raise
    
    async def get_pending_loops(
        self,
        client_id: Optional[UUID] = None,
        include_expired: bool = False
    ) -> List[HumanLoopState]:
        """Get all pending human loop states."""
        try:
            query = self.table.select("*").eq("status", "waiting")
            
            if client_id:
                query = query.eq("client_id", str(client_id))
            
            result = query.order("sent_at", asc=True).execute()
            
            loops = [HumanLoopState(**record) for record in result.data]
            
            # Filter out expired if requested
            if not include_expired:
                loops = [loop for loop in loops if not loop.is_expired()]
            
            return loops
            
        except Exception as e:
            logger.error(f"Failed to get pending loops: {e}")
            return []
    
    async def get_loops_by_session(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> List[HumanLoopState]:
        """Get all human loop states for a session."""
        try:
            result = self.table.select("*") \
                .eq("session_id", str(session_id)) \
                .eq("client_id", str(client_id)) \
                .order("created_at", desc=True) \
                .execute()
            
            return [HumanLoopState(**record) for record in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get loops by session: {e}")
            return []
    
    async def submit_response(
        self,
        loop_id: UUID,
        response_data: Dict[str, Any],
        client_id: UUID
    ) -> Optional[HumanLoopState]:
        """Submit human response to a loop state."""
        try:
            # Get the loop state
            loop_state = await self.get_by_id(loop_id, client_id)
            if not loop_state:
                return None
            
            # Update with response
            update_data = HumanLoopStateUpdate(
                response_data=response_data,
                responded_at=datetime.utcnow(),
                status="completed"
            )
            
            loop_state = await self.update(loop_id, update_data, client_id)
            
            # Validate the response
            if loop_state and loop_state.validate_response():
                logger.info(f"Human response validated for loop {loop_id}")
            else:
                logger.warning(f"Human response validation failed for loop {loop_id}")
            
            return loop_state
            
        except Exception as e:
            logger.error(f"Failed to submit response: {e}")
            return None
    
    async def update_notification_status(
        self,
        loop_id: UUID,
        channel: str,
        success: bool,
        error_message: Optional[str],
        client_id: UUID
    ) -> Optional[HumanLoopState]:
        """Update notification delivery status."""
        try:
            loop_state = await self.get_by_id(loop_id, client_id)
            if not loop_state:
                return None
            
            # Update notification tracking
            notifications_sent = dict(loop_state.notifications_sent)
            notifications_sent[channel] = success
            
            notification_errors = dict(loop_state.notification_errors)
            if error_message:
                notification_errors[channel] = error_message
            elif channel in notification_errors:
                del notification_errors[channel]
            
            update_data = {
                "notifications_sent": notifications_sent,
                "notification_errors": notification_errors
            }
            
            return await self.update(loop_id, HumanLoopStateUpdate(**update_data), client_id)
            
        except Exception as e:
            logger.error(f"Failed to update notification status: {e}")
            return None
    
    async def send_reminder(
        self,
        loop_id: UUID,
        client_id: UUID
    ) -> Optional[HumanLoopState]:
        """Mark that a reminder has been sent."""
        try:
            update_data = HumanLoopStateUpdate(
                reminder_sent=True,
                reminder_sent_at=datetime.utcnow()
            )
            
            return await self.update(loop_id, update_data, client_id)
            
        except Exception as e:
            logger.error(f"Failed to mark reminder sent: {e}")
            return None
    
    async def retry_notification(
        self,
        loop_id: UUID,
        client_id: UUID
    ) -> Optional[HumanLoopState]:
        """Increment retry count for notifications."""
        try:
            loop_state = await self.get_by_id(loop_id, client_id)
            if not loop_state:
                return None
            
            update_data = HumanLoopStateUpdate(
                retry_count=loop_state.retry_count + 1,
                last_retry_at=datetime.utcnow()
            )
            
            return await self.update(loop_id, update_data, client_id)
            
        except Exception as e:
            logger.error(f"Failed to retry notification: {e}")
            return None
    
    async def get_loops_needing_reminder(
        self,
        client_id: Optional[UUID] = None
    ) -> List[HumanLoopState]:
        """Get loops that need reminder notifications."""
        try:
            pending_loops = await self.get_pending_loops(client_id, include_expired=False)
            
            loops_needing_reminder = []
            for loop in pending_loops:
                if loop.needs_reminder():
                    loops_needing_reminder.append(loop)
            
            return loops_needing_reminder
            
        except Exception as e:
            logger.error(f"Failed to get loops needing reminder: {e}")
            return []
    
    async def expire_old_loops(
        self,
        client_id: Optional[UUID] = None
    ) -> List[HumanLoopState]:
        """Mark expired loops and return them."""
        try:
            pending_loops = await self.get_pending_loops(client_id, include_expired=True)
            
            expired_loops = []
            for loop in pending_loops:
                if loop.is_expired():
                    update_data = HumanLoopStateUpdate(status="expired")
                    updated = await self.update(loop.id, update_data, loop.client_id)
                    if updated:
                        expired_loops.append(updated)
            
            if expired_loops:
                logger.info(f"Expired {len(expired_loops)} human loop states")
            
            return expired_loops
            
        except Exception as e:
            logger.error(f"Failed to expire old loops: {e}")
            return []
    
    async def get_response_time_stats(
        self,
        client_id: Optional[UUID] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get statistics on human response times."""
        try:
            # Calculate date range
            start_date = datetime.utcnow() - timedelta(days=days)
            
            query = self.table.select("*") \
                .eq("status", "completed") \
                .gte("created_at", start_date.isoformat())
            
            if client_id:
                query = query.eq("client_id", str(client_id))
            
            result = query.execute()
            
            completed_loops = [HumanLoopState(**record) for record in result.data]
            
            if not completed_loops:
                return {
                    "total_completed": 0,
                    "average_response_minutes": 0,
                    "min_response_minutes": 0,
                    "max_response_minutes": 0,
                    "by_type": {}
                }
            
            # Calculate response times
            response_times = []
            by_type = {}
            
            for loop in completed_loops:
                if loop.responded_at and loop.sent_at:
                    response_time = (loop.responded_at - loop.sent_at).total_seconds() / 60
                    response_times.append(response_time)
                    
                    # Group by type
                    loop_type = loop.loop_type.value if hasattr(loop.loop_type, 'value') else str(loop.loop_type)
                    if loop_type not in by_type:
                        by_type[loop_type] = []
                    by_type[loop_type].append(response_time)
            
            # Calculate statistics
            avg_response = sum(response_times) / len(response_times) if response_times else 0
            
            # Calculate per-type averages
            type_stats = {}
            for loop_type, times in by_type.items():
                type_stats[loop_type] = {
                    "count": len(times),
                    "average_minutes": sum(times) / len(times) if times else 0
                }
            
            return {
                "total_completed": len(completed_loops),
                "average_response_minutes": avg_response,
                "min_response_minutes": min(response_times) if response_times else 0,
                "max_response_minutes": max(response_times) if response_times else 0,
                "by_type": type_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get response time stats: {e}")
            return {}