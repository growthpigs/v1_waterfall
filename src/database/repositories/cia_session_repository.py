"""
Repository for CIA Session operations.
Handles session lifecycle, state management, and phase progression.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import logging

from .base import BaseRepository
from ..models import (
    CIASession,
    CIASessionCreate,
    CIASessionUpdate,
    CIASessionResponse
)
from ...config.constants import (
    CIAPhase,
    PhaseStatus,
    TABLE_CIA_SESSIONS,
    CIA_PHASE_ORDER
)

logger = logging.getLogger(__name__)


class CIASessionRepository(BaseRepository[CIASession, CIASessionCreate, CIASessionUpdate]):
    """Repository for CIA session database operations."""
    
    def __init__(self):
        """Initialize CIA session repository."""
        super().__init__(
            model=CIASession,
            table_name=TABLE_CIA_SESSIONS
        )
    
    async def create_session(
        self,
        session_data: CIASessionCreate,
        client_id: UUID
    ) -> CIASession:
        """Create a new CIA session."""
        try:
            # Set initial session state
            data = session_data.model_dump()
            data.update({
                "client_id": str(client_id),
                "status": PhaseStatus.PENDING.value,
                "completed_phases": [],
                "failed_phases": [],
                "human_inputs_pending": [],
                "human_inputs_completed": [],
                "total_tokens_used": 0,
                "handover_count": 0,
                "progress_percentage": 0.0,
            })
            
            # Create session
            session = await self.create(CIASessionCreate(**data), client_id)
            
            logger.info(f"Created CIA session {session.id} for client {client_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create CIA session: {e}")
            raise
    
    async def get_active_sessions(
        self,
        client_id: UUID,
        limit: int = 10
    ) -> List[CIASession]:
        """Get active sessions for a client."""
        try:
            # Query active sessions
            result = self.table.select("*") \
                .eq("client_id", str(client_id)) \
                .in_("status", [
                    PhaseStatus.PENDING.value,
                    PhaseStatus.EXECUTING.value,
                    PhaseStatus.PAUSED.value
                ]) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            return [CIASession(**record) for record in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get active sessions: {e}")
            return []
    
    async def start_session(self, session_id: UUID, client_id: UUID) -> Optional[CIASession]:
        """Start a pending session."""
        try:
            update_data = {
                "status": PhaseStatus.EXECUTING.value,
                "started_at": datetime.utcnow().isoformat(),
                "current_phase": CIA_PHASE_ORDER[0].value,  # Start with phase 1A
            }
            
            return await self.update(
                session_id,
                CIASessionUpdate(**update_data),
                client_id
            )
            
        except Exception as e:
            logger.error(f"Failed to start session {session_id}: {e}")
            return None
    
    async def update_phase_progress(
        self,
        session_id: UUID,
        phase: CIAPhase,
        completed: bool,
        tokens_used: int,
        client_id: UUID
    ) -> Optional[CIASession]:
        """Update session after phase completion."""
        try:
            # Get current session
            session = await self.get_by_id(session_id, client_id)
            if not session:
                return None
            
            # Update phase lists
            completed_phases = list(session.completed_phases)
            failed_phases = list(session.failed_phases)
            
            if completed:
                if phase not in completed_phases:
                    completed_phases.append(phase)
                # Remove from failed if it was there
                if phase in failed_phases:
                    failed_phases.remove(phase)
            else:
                if phase not in failed_phases:
                    failed_phases.append(phase)
            
            # Calculate progress
            progress = (len(completed_phases) / session.total_phases) * 100
            
            # Determine next phase
            next_phase = None
            for p in CIA_PHASE_ORDER:
                if p not in completed_phases and p not in failed_phases:
                    next_phase = p
                    break
            
            # Check if session is complete
            status = session.status
            if len(completed_phases) == session.total_phases:
                status = PhaseStatus.COMPLETED
            elif next_phase is None and len(failed_phases) > 0:
                status = PhaseStatus.FAILED
            
            # Update session
            update_data = {
                "completed_phases": [p.value for p in completed_phases],
                "failed_phases": [p.value for p in failed_phases],
                "current_phase": next_phase.value if next_phase else None,
                "total_tokens_used": session.total_tokens_used + tokens_used,
                "progress_percentage": progress,
                "status": status.value,
            }
            
            if status == PhaseStatus.COMPLETED:
                update_data["completed_at"] = datetime.utcnow().isoformat()
            
            return await self.update(
                session_id,
                CIASessionUpdate(**update_data),
                client_id
            )
            
        except Exception as e:
            logger.error(f"Failed to update phase progress: {e}")
            return None
    
    async def pause_session(
        self,
        session_id: UUID,
        client_id: UUID,
        reason: str = "Manual pause"
    ) -> Optional[CIASession]:
        """Pause an active session."""
        try:
            update_data = {
                "status": PhaseStatus.PAUSED.value,
                "paused_at": datetime.utcnow().isoformat(),
                "metadata": {"pause_reason": reason}
            }
            
            return await self.update(
                session_id,
                CIASessionUpdate(**update_data),
                client_id
            )
            
        except Exception as e:
            logger.error(f"Failed to pause session {session_id}: {e}")
            return None
    
    async def resume_session(self, session_id: UUID, client_id: UUID) -> Optional[CIASession]:
        """Resume a paused session."""
        try:
            update_data = {
                "status": PhaseStatus.EXECUTING.value,
                "paused_at": None,
            }
            
            return await self.update(
                session_id,
                CIASessionUpdate(**update_data),
                client_id
            )
            
        except Exception as e:
            logger.error(f"Failed to resume session {session_id}: {e}")
            return None
    
    async def add_human_input_pending(
        self,
        session_id: UUID,
        input_type: str,
        client_id: UUID
    ) -> Optional[CIASession]:
        """Add a pending human input requirement."""
        try:
            session = await self.get_by_id(session_id, client_id)
            if not session:
                return None
            
            pending = list(session.human_inputs_pending)
            if input_type not in pending:
                pending.append(input_type)
            
            update_data = {
                "human_inputs_pending": pending,
                "status": PhaseStatus.PAUSED.value,
            }
            
            return await self.update(
                session_id,
                CIASessionUpdate(**update_data),
                client_id
            )
            
        except Exception as e:
            logger.error(f"Failed to add pending human input: {e}")
            return None
    
    async def complete_human_input(
        self,
        session_id: UUID,
        input_type: str,
        client_id: UUID
    ) -> Optional[CIASession]:
        """Mark a human input as completed."""
        try:
            session = await self.get_by_id(session_id, client_id)
            if not session:
                return None
            
            pending = list(session.human_inputs_pending)
            completed = list(session.human_inputs_completed)
            
            if input_type in pending:
                pending.remove(input_type)
                if input_type not in completed:
                    completed.append(input_type)
            
            # Resume if no more pending inputs and auto_resume is enabled
            status = session.status
            if len(pending) == 0 and session.auto_resume:
                status = PhaseStatus.EXECUTING
            
            update_data = {
                "human_inputs_pending": pending,
                "human_inputs_completed": completed,
                "status": status.value,
            }
            
            return await self.update(
                session_id,
                CIASessionUpdate(**update_data),
                client_id
            )
            
        except Exception as e:
            logger.error(f"Failed to complete human input: {e}")
            return None
    
    async def increment_handover_count(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> Optional[CIASession]:
        """Increment the handover count for a session."""
        try:
            session = await self.get_by_id(session_id, client_id)
            if not session:
                return None
            
            update_data = {
                "handover_count": session.handover_count + 1,
                "last_handover_at": datetime.utcnow().isoformat(),
            }
            
            return await self.update(
                session_id,
                CIASessionUpdate(**update_data),
                client_id
            )
            
        except Exception as e:
            logger.error(f"Failed to increment handover count: {e}")
            return None
    
    async def get_sessions_by_status(
        self,
        status: PhaseStatus,
        client_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[CIASession]:
        """Get sessions by status."""
        try:
            query = self.table.select("*").eq("status", status.value)
            
            if client_id:
                query = query.eq("client_id", str(client_id))
            
            result = query.order("created_at", desc=True).limit(limit).execute()
            
            return [CIASession(**record) for record in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get sessions by status: {e}")
            return []
    
    async def get_session_with_response(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> Optional[CIASessionResponse]:
        """Get session with computed response fields."""
        try:
            session = await self.get_by_id(session_id, client_id)
            if not session:
                return None
            
            # Convert to response model with computed fields
            return CIASessionResponse(**session.model_dump())
            
        except Exception as e:
            logger.error(f"Failed to get session response: {e}")
            return None