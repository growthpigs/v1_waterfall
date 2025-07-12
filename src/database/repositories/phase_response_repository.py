"""
Repository for Phase Response operations.
Manages phase execution results, token tracking, and framework extraction.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import logging

from .base import BaseRepository
from ..models import (
    PhaseResponse,
    PhaseResponseCreate,
    PhaseResponseUpdate,
    PhaseResponseSummary
)
from ...config.constants import CIAPhase, PhaseStatus, TABLE_PHASE_RESPONSES

logger = logging.getLogger(__name__)


class PhaseResponseRepository(BaseRepository[PhaseResponse, PhaseResponseCreate, PhaseResponseUpdate]):
    """Repository for phase response database operations."""
    
    def __init__(self):
        """Initialize phase response repository."""
        super().__init__(
            model=PhaseResponse,
            table_name=TABLE_PHASE_RESPONSES
        )
    
    async def create_phase_response(
        self,
        session_id: UUID,
        phase_id: CIAPhase,
        prompt_used: str,
        client_id: UUID
    ) -> PhaseResponse:
        """Create a new phase response record."""
        try:
            response_data = PhaseResponseCreate(
                session_id=session_id,
                phase_id=phase_id,
                prompt_used=prompt_used,
                response_content={},
                prompt_tokens=0,
                response_tokens=0,
                total_tokens=0,
                context_usage_percentage=0.0,
                status=PhaseStatus.EXECUTING,
                started_at=datetime.utcnow()
            )
            
            response = await self.create(response_data, client_id)
            
            logger.info(f"Created phase response for session {session_id}, phase {phase_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create phase response: {e}")
            raise
    
    async def get_by_session_and_phase(
        self,
        session_id: UUID,
        phase_id: CIAPhase,
        client_id: UUID
    ) -> Optional[PhaseResponse]:
        """Get phase response by session and phase ID."""
        try:
            result = self.table.select("*") \
                .eq("session_id", str(session_id)) \
                .eq("phase_id", phase_id.value) \
                .eq("client_id", str(client_id)) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()
            
            if result.data:
                return PhaseResponse(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get phase response: {e}")
            return None
    
    async def get_session_responses(
        self,
        session_id: UUID,
        client_id: UUID,
        include_failed: bool = False
    ) -> List[PhaseResponse]:
        """Get all phase responses for a session."""
        try:
            query = self.table.select("*") \
                .eq("session_id", str(session_id)) \
                .eq("client_id", str(client_id))
            
            if not include_failed:
                query = query.neq("status", PhaseStatus.FAILED.value)
            
            result = query.order("created_at", asc=True).execute()
            
            return [PhaseResponse(**record) for record in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get session responses: {e}")
            return []
    
    async def update_with_response(
        self,
        response_id: UUID,
        response_content: Dict[str, Any],
        extracted_frameworks: Dict[str, Any],
        tokens: Dict[str, int],
        client_id: UUID
    ) -> Optional[PhaseResponse]:
        """Update phase response with execution results."""
        try:
            update_data = PhaseResponseUpdate(
                response_content=response_content,
                extracted_frameworks=extracted_frameworks,
                prompt_tokens=tokens.get("prompt_tokens", 0),
                response_tokens=tokens.get("response_tokens", 0),
                total_tokens=tokens.get("total_tokens", 0),
                context_usage_percentage=tokens.get("context_usage_percentage", 0.0),
                status=PhaseStatus.COMPLETED,
                completed_at=datetime.utcnow()
            )
            
            return await self.update(response_id, update_data, client_id)
            
        except Exception as e:
            logger.error(f"Failed to update phase response: {e}")
            return None
    
    async def mark_as_failed(
        self,
        response_id: UUID,
        error_message: str,
        error_details: Optional[Dict[str, Any]],
        client_id: UUID
    ) -> Optional[PhaseResponse]:
        """Mark phase response as failed."""
        try:
            update_data = PhaseResponseUpdate(
                status=PhaseStatus.FAILED,
                error_message=error_message,
                error_details=error_details or {},
                completed_at=datetime.utcnow()
            )
            
            return await self.update(response_id, update_data, client_id)
            
        except Exception as e:
            logger.error(f"Failed to mark phase as failed: {e}")
            return None
    
    async def mark_human_input_required(
        self,
        response_id: UUID,
        input_type: str,
        client_id: UUID
    ) -> Optional[PhaseResponse]:
        """Mark phase as requiring human input."""
        try:
            update_data = PhaseResponseUpdate(
                status=PhaseStatus.PAUSED,
                requires_human_input=True,
                human_input_type=input_type
            )
            
            return await self.update(response_id, update_data, client_id)
            
        except Exception as e:
            logger.error(f"Failed to mark human input required: {e}")
            return None
    
    async def add_human_input(
        self,
        response_id: UUID,
        input_data: Dict[str, Any],
        client_id: UUID
    ) -> Optional[PhaseResponse]:
        """Add human input data to phase response."""
        try:
            update_data = PhaseResponseUpdate(
                human_input_data=input_data,
                human_input_received_at=datetime.utcnow()
            )
            
            return await self.update(response_id, update_data, client_id)
            
        except Exception as e:
            logger.error(f"Failed to add human input: {e}")
            return None
    
    async def update_quality_scores(
        self,
        response_id: UUID,
        framework_score: float,
        quality_score: float,
        client_id: UUID
    ) -> Optional[PhaseResponse]:
        """Update quality and framework preservation scores."""
        try:
            update_data = PhaseResponseUpdate(
                framework_preservation_score=framework_score,
                response_quality_score=quality_score
            )
            
            return await self.update(response_id, update_data, client_id)
            
        except Exception as e:
            logger.error(f"Failed to update quality scores: {e}")
            return None
    
    async def get_total_tokens_for_session(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> int:
        """Get total tokens used across all phases for a session."""
        try:
            responses = await self.get_session_responses(session_id, client_id, include_failed=False)
            return sum(r.total_tokens for r in responses)
            
        except Exception as e:
            logger.error(f"Failed to get total tokens: {e}")
            return 0
    
    async def get_phases_exceeding_threshold(
        self,
        session_id: UUID,
        threshold: float,
        client_id: UUID
    ) -> List[PhaseResponse]:
        """Get phases that exceeded context usage threshold."""
        try:
            result = self.table.select("*") \
                .eq("session_id", str(session_id)) \
                .eq("client_id", str(client_id)) \
                .gt("context_usage_percentage", threshold * 100) \
                .execute()
            
            return [PhaseResponse(**record) for record in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get phases exceeding threshold: {e}")
            return []
    
    async def get_phase_summaries(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> List[PhaseResponseSummary]:
        """Get summary view of all phase responses for a session."""
        try:
            responses = await self.get_session_responses(session_id, client_id, include_failed=True)
            
            summaries = []
            for response in responses:
                summary = PhaseResponseSummary(
                    id=response.id,
                    session_id=response.session_id,
                    phase_id=response.phase_id,
                    status=response.status,
                    total_tokens=response.total_tokens,
                    context_usage_percentage=response.context_usage_percentage,
                    duration_seconds=response.duration_seconds,
                    created_at=response.created_at,
                    completed_at=response.completed_at,
                    requires_human_input=response.requires_human_input,
                    error_message=response.error_message
                )
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to get phase summaries: {e}")
            return []
    
    async def retry_phase(
        self,
        session_id: UUID,
        phase_id: CIAPhase,
        prompt_used: str,
        client_id: UUID,
        attempt_number: int
    ) -> PhaseResponse:
        """Create a retry attempt for a phase."""
        try:
            response_data = PhaseResponseCreate(
                session_id=session_id,
                phase_id=phase_id,
                prompt_used=prompt_used,
                response_content={},
                prompt_tokens=0,
                response_tokens=0,
                total_tokens=0,
                context_usage_percentage=0.0,
                status=PhaseStatus.EXECUTING,
                started_at=datetime.utcnow(),
                attempt_number=attempt_number
            )
            
            response = await self.create(response_data, client_id)
            
            logger.info(f"Created retry attempt {attempt_number} for phase {phase_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create retry phase response: {e}")
            raise