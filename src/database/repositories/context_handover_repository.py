"""
Repository for Context Handover operations.
Manages context window limits and session recovery states.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import logging
import json

from .base import BaseRepository
from ..models import (
    ContextHandover,
    ContextHandoverCreate,
    ContextHandoverUpdate,
    ContextHandoverSummary
)
from ...config.constants import CIAPhase, TABLE_CONTEXT_HANDOVERS

logger = logging.getLogger(__name__)


class ContextHandoverRepository(BaseRepository[ContextHandover, ContextHandoverCreate, ContextHandoverUpdate]):
    """Repository for context handover database operations."""
    
    def __init__(self):
        """Initialize context handover repository."""
        super().__init__(
            model=ContextHandover,
            table_name=TABLE_CONTEXT_HANDOVERS
        )
    
    async def create_handover(
        self,
        session_id: UUID,
        current_phase: CIAPhase,
        context_usage: float,
        total_tokens: int,
        completed_phases: List[CIAPhase],
        pending_phases: List[CIAPhase],
        critical_state: Dict[str, Any],
        next_action: str,
        client_id: UUID,
        latest_archive_id: Optional[UUID] = None,
        preserved_archives: Optional[List[UUID]] = None
    ) -> ContextHandover:
        """Create a new context handover."""
        try:
            # Get previous handover count
            previous_handovers = await self.get_session_handovers(session_id, client_id)
            handover_number = len(previous_handovers) + 1
            
            # Get previous handover ID if exists
            previous_handover_id = previous_handovers[-1].id if previous_handovers else None
            
            handover_data = ContextHandoverCreate(
                session_id=session_id,
                current_phase=current_phase,
                context_usage_percentage=context_usage,
                total_tokens_used=total_tokens,
                completed_phases=completed_phases,
                pending_phases=pending_phases,
                critical_state=critical_state,
                next_action=next_action,
                handover_number=handover_number,
                previous_handover_id=previous_handover_id,
                latest_archive_id=latest_archive_id,
                preserved_archives=preserved_archives or []
            )
            
            handover = await self.create(handover_data, client_id)
            
            logger.info(f"Created handover #{handover_number} for session {session_id} at phase {current_phase}")
            return handover
            
        except Exception as e:
            logger.error(f"Failed to create handover: {e}")
            raise
    
    async def get_session_handovers(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> List[ContextHandover]:
        """Get all handovers for a session in order."""
        try:
            result = self.table.select("*") \
                .eq("session_id", str(session_id)) \
                .eq("client_id", str(client_id)) \
                .order("handover_number", asc=True) \
                .execute()
            
            return [ContextHandover(**record) for record in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get session handovers: {e}")
            return []
    
    async def get_latest_handover(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> Optional[ContextHandover]:
        """Get the most recent handover for a session."""
        try:
            result = self.table.select("*") \
                .eq("session_id", str(session_id)) \
                .eq("client_id", str(client_id)) \
                .order("handover_number", desc=True) \
                .limit(1) \
                .execute()
            
            if result.data:
                return ContextHandover(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest handover: {e}")
            return None
    
    async def get_unrecovered_handovers(
        self,
        client_id: Optional[UUID] = None
    ) -> List[ContextHandover]:
        """Get all handovers that haven't been recovered."""
        try:
            query = self.table.select("*").eq("recovered", False)
            
            if client_id:
                query = query.eq("client_id", str(client_id))
            
            result = query.order("created_at", desc=True).execute()
            
            return [ContextHandover(**record) for record in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get unrecovered handovers: {e}")
            return []
    
    async def mark_as_recovered(
        self,
        handover_id: UUID,
        recovery_session_id: UUID,
        client_id: UUID
    ) -> Optional[ContextHandover]:
        """Mark a handover as recovered."""
        try:
            update_data = ContextHandoverUpdate(
                recovered=True,
                recovered_at=datetime.utcnow(),
                recovery_session_id=recovery_session_id
            )
            
            return await self.update(handover_id, update_data, client_id)
            
        except Exception as e:
            logger.error(f"Failed to mark handover as recovered: {e}")
            return None
    
    async def add_intelligence_summary(
        self,
        handover_id: UUID,
        intelligence_summary: Dict[str, Any],
        framework_status: Dict[str, Dict[str, Any]],
        client_id: UUID
    ) -> Optional[ContextHandover]:
        """Add intelligence summary to handover."""
        try:
            handover = await self.get_by_id(handover_id, client_id)
            if not handover:
                return None
            
            # Update with new intelligence data
            update_data = {
                "intelligence_summary": intelligence_summary,
                "framework_status": framework_status
            }
            
            return await self.update(handover_id, ContextHandoverUpdate(**update_data), client_id)
            
        except Exception as e:
            logger.error(f"Failed to add intelligence summary: {e}")
            return None
    
    async def add_recovery_instructions(
        self,
        handover_id: UUID,
        instructions: Dict[str, Any],
        notes: Optional[str],
        client_id: UUID
    ) -> Optional[ContextHandover]:
        """Add recovery instructions to handover."""
        try:
            update_data = ContextHandoverUpdate(
                recovery_instructions=instructions,
                handover_notes=notes
            )
            
            return await self.update(handover_id, update_data, client_id)
            
        except Exception as e:
            logger.error(f"Failed to add recovery instructions: {e}")
            return None
    
    async def get_handover_chain(
        self,
        handover_id: UUID,
        client_id: UUID
    ) -> List[ContextHandover]:
        """Get the complete handover chain for a session."""
        try:
            handover = await self.get_by_id(handover_id, client_id)
            if not handover:
                return []
            
            # Get all handovers for the session
            return await self.get_session_handovers(handover.session_id, client_id)
            
        except Exception as e:
            logger.error(f"Failed to get handover chain: {e}")
            return []
    
    async def export_handover_document(
        self,
        handover_id: UUID,
        client_id: UUID
    ) -> Optional[str]:
        """Export handover as a formatted document."""
        try:
            handover = await self.get_by_id(handover_id, client_id)
            if not handover:
                return None
            
            document = f"""
# CIA CONTEXT HANDOVER DOCUMENT
Generated: {datetime.utcnow().isoformat()}

## Session Information
- Session ID: {handover.session_id}
- Handover Number: {handover.handover_number}
- Current Phase: {handover.current_phase}
- Context Usage: {handover.context_usage_percentage}%
- Total Tokens: {handover.total_tokens_used:,}

## Progress Status
### Completed Phases
{chr(10).join(f"- {phase}" for phase in handover.completed_phases)}

### Pending Phases
{chr(10).join(f"- {phase}" for phase in handover.pending_phases)}

## Next Action
{handover.next_action}

## Critical State
```json
{json.dumps(handover.critical_state, indent=2)}
```

## Intelligence Summary
```json
{json.dumps(handover.intelligence_summary, indent=2)}
```

## Framework Status
```json
{json.dumps(handover.framework_status, indent=2)}
```

## Recovery Instructions
```json
{json.dumps(handover.recovery_instructions, indent=2)}
```

## Notes
{handover.handover_notes or "No additional notes"}

---
To recover this session, use the recovery context provided above.
            """
            
            return document.strip()
            
        except Exception as e:
            logger.error(f"Failed to export handover document: {e}")
            return None
    
    async def get_handover_summaries(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> List[ContextHandoverSummary]:
        """Get summary view of all handovers for a session."""
        try:
            handovers = await self.get_session_handovers(session_id, client_id)
            
            summaries = []
            for handover in handovers:
                summary = ContextHandoverSummary(
                    id=handover.id,
                    session_id=handover.session_id,
                    current_phase=handover.current_phase,
                    context_usage_percentage=handover.context_usage_percentage,
                    handover_number=handover.handover_number,
                    recovered=handover.recovered,
                    created_at=handover.created_at,
                    recovered_at=handover.recovered_at
                )
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to get handover summaries: {e}")
            return []
    
    async def cleanup_old_handovers(
        self,
        days_old: int = 30,
        client_id: Optional[UUID] = None
    ) -> int:
        """Clean up old recovered handovers."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            query = self.table.delete() \
                .eq("recovered", True) \
                .lt("created_at", cutoff_date.isoformat())
            
            if client_id:
                query = query.eq("client_id", str(client_id))
            
            result = query.execute()
            
            deleted_count = len(result.data) if result.data else 0
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old handovers")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old handovers: {e}")
            return 0