"""
Context window monitoring for CIA system.
Tracks token usage and triggers handovers at threshold.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from dataclasses import dataclass, field

from ..config.constants import (
    CONTEXT_WINDOW_SIZE,
    HANDOVER_THRESHOLD,
    TOKEN_COMPRESSION_RATIO
)
from ..database.models import ContextHandover, ContextHandoverCreate
from ..database.repositories import ContextHandoverRepository

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Track token usage for a phase."""
    prompt_tokens: int = 0
    response_tokens: int = 0
    total_tokens: int = 0
    
    def add(self, prompt: int, response: int) -> None:
        """Add token usage."""
        self.prompt_tokens += prompt
        self.response_tokens += response
        self.total_tokens += (prompt + response)


@dataclass
class ContextState:
    """Current context window state."""
    session_id: UUID
    current_phase: str
    total_tokens_used: int = 0
    context_percentage: float = 0.0
    phase_tokens: Dict[str, TokenUsage] = field(default_factory=dict)
    completed_phases: List[str] = field(default_factory=list)
    pending_phases: List[str] = field(default_factory=list)
    
    def calculate_percentage(self) -> float:
        """Calculate context usage percentage."""
        self.context_percentage = (self.total_tokens_used / CONTEXT_WINDOW_SIZE) * 100
        return self.context_percentage


class ContextMonitor:
    """Monitor context window usage and manage handovers."""
    
    def __init__(self, handover_repository: Optional[ContextHandoverRepository] = None):
        """Initialize context monitor.
        
        Args:
            handover_repository: Repository for saving handovers. 
                               If None, handovers won't be persisted.
        """
        self.handover_repository = handover_repository
        self._active_contexts: Dict[UUID, ContextState] = {}
    
    def start_session(self, session_id: UUID, all_phases: List[str]) -> ContextState:
        """Start monitoring a new session.
        
        Args:
            session_id: The CIA session ID
            all_phases: List of all phases to be executed
            
        Returns:
            New ContextState instance
        """
        context = ContextState(
            session_id=session_id,
            current_phase="",
            pending_phases=all_phases.copy()
        )
        self._active_contexts[session_id] = context
        logger.info(f"Started context monitoring for session {session_id}")
        return context
    
    def get_context(self, session_id: UUID) -> Optional[ContextState]:
        """Get context state for a session.
        
        Args:
            session_id: The CIA session ID
            
        Returns:
            ContextState or None if not found
        """
        return self._active_contexts.get(session_id)
    
    def update_phase_start(self, session_id: UUID, phase: str) -> ContextState:
        """Update context when starting a phase.
        
        Args:
            session_id: The CIA session ID
            phase: The phase being started
            
        Returns:
            Updated ContextState
        """
        context = self.get_context(session_id)
        if not context:
            raise ValueError(f"No context found for session {session_id}")
        
        context.current_phase = phase
        if phase not in context.phase_tokens:
            context.phase_tokens[phase] = TokenUsage()
        
        logger.info(f"Starting phase {phase} for session {session_id}")
        return context
    
    def add_tokens(
        self, 
        session_id: UUID, 
        phase: str,
        prompt_tokens: int, 
        response_tokens: int
    ) -> Tuple[ContextState, bool]:
        """Add token usage and check if handover needed.
        
        Args:
            session_id: The CIA session ID
            phase: Current phase
            prompt_tokens: Tokens in prompt
            response_tokens: Tokens in response
            
        Returns:
            Tuple of (updated ContextState, needs_handover bool)
        """
        context = self.get_context(session_id)
        if not context:
            raise ValueError(f"No context found for session {session_id}")
        
        # Update phase tokens
        if phase not in context.phase_tokens:
            context.phase_tokens[phase] = TokenUsage()
        
        context.phase_tokens[phase].add(prompt_tokens, response_tokens)
        
        # Update total
        context.total_tokens_used += (prompt_tokens + response_tokens)
        context.calculate_percentage()
        
        # Check if handover needed
        needs_handover = context.context_percentage >= (HANDOVER_THRESHOLD * 100)
        
        logger.info(
            f"Session {session_id} phase {phase}: "
            f"+{prompt_tokens + response_tokens} tokens "
            f"(total: {context.total_tokens_used}, {context.context_percentage:.1f}%)"
        )
        
        if needs_handover:
            logger.warning(
                f"Session {session_id} approaching context limit: "
                f"{context.context_percentage:.1f}% used"
            )
        
        return context, needs_handover
    
    def complete_phase(self, session_id: UUID, phase: str) -> ContextState:
        """Mark a phase as completed.
        
        Args:
            session_id: The CIA session ID
            phase: The completed phase
            
        Returns:
            Updated ContextState
        """
        context = self.get_context(session_id)
        if not context:
            raise ValueError(f"No context found for session {session_id}")
        
        if phase not in context.completed_phases:
            context.completed_phases.append(phase)
        
        if phase in context.pending_phases:
            context.pending_phases.remove(phase)
        
        logger.info(f"Completed phase {phase} for session {session_id}")
        return context
    
    def estimate_remaining_capacity(self, session_id: UUID) -> Dict[str, Any]:
        """Estimate remaining context capacity.
        
        Args:
            session_id: The CIA session ID
            
        Returns:
            Dictionary with capacity metrics
        """
        context = self.get_context(session_id)
        if not context:
            return {
                "tokens_used": 0,
                "tokens_remaining": CONTEXT_WINDOW_SIZE,
                "percentage_used": 0.0,
                "percentage_remaining": 100.0,
                "estimated_phases_remaining": 0
            }
        
        tokens_remaining = CONTEXT_WINDOW_SIZE - context.total_tokens_used
        percentage_remaining = 100 - context.context_percentage
        
        # Estimate average tokens per phase
        completed_count = len(context.completed_phases)
        if completed_count > 0:
            avg_tokens_per_phase = context.total_tokens_used / completed_count
            estimated_phases_remaining = int(tokens_remaining / avg_tokens_per_phase)
        else:
            # Use a conservative estimate
            avg_tokens_per_phase = CONTEXT_WINDOW_SIZE / 15  # Assume 15 phases total
            estimated_phases_remaining = int(tokens_remaining / avg_tokens_per_phase)
        
        return {
            "tokens_used": context.total_tokens_used,
            "tokens_remaining": tokens_remaining,
            "percentage_used": context.context_percentage,
            "percentage_remaining": percentage_remaining,
            "estimated_phases_remaining": estimated_phases_remaining,
            "average_tokens_per_phase": int(avg_tokens_per_phase) if completed_count > 0 else None
        }
    
    async def create_handover(
        self,
        session_id: UUID,
        client_id: UUID,
        critical_state: Dict[str, Any],
        latest_archive_id: Optional[UUID] = None,
        preserved_archives: Optional[List[UUID]] = None
    ) -> Optional[ContextHandover]:
        """Create a context handover for session recovery.
        
        Args:
            session_id: The CIA session ID
            client_id: The client ID
            critical_state: Essential state data for recovery
            latest_archive_id: Most recent Master Archive ID
            preserved_archives: List of all archive IDs to preserve
            
        Returns:
            Created ContextHandover or None if no repository
        """
        context = self.get_context(session_id)
        if not context:
            raise ValueError(f"No context found for session {session_id}")
        
        if not self.handover_repository:
            logger.warning("No handover repository configured - handover not persisted")
            return None
        
        # Determine next action
        next_phase = context.pending_phases[0] if context.pending_phases else None
        next_action = f"Resume CIA analysis from phase {next_phase}" if next_phase else "All phases completed"
        
        # Create handover
        handover = await self.handover_repository.create_handover(
            session_id=session_id,
            current_phase=context.current_phase,
            context_usage=context.context_percentage,
            total_tokens=context.total_tokens_used,
            completed_phases=context.completed_phases,
            pending_phases=context.pending_phases,
            critical_state=critical_state,
            next_action=next_action,
            client_id=client_id,
            latest_archive_id=latest_archive_id,
            preserved_archives=preserved_archives
        )
        
        logger.info(f"Created handover for session {session_id}")
        return handover
    
    def get_phase_metrics(self, session_id: UUID) -> Dict[str, Dict[str, int]]:
        """Get token usage metrics by phase.
        
        Args:
            session_id: The CIA session ID
            
        Returns:
            Dictionary of phase -> token usage metrics
        """
        context = self.get_context(session_id)
        if not context:
            return {}
        
        metrics = {}
        for phase, usage in context.phase_tokens.items():
            metrics[phase] = {
                "prompt_tokens": usage.prompt_tokens,
                "response_tokens": usage.response_tokens,
                "total_tokens": usage.total_tokens,
                "percentage_of_total": (usage.total_tokens / context.total_tokens_used * 100) 
                                     if context.total_tokens_used > 0 else 0
            }
        
        return metrics
    
    def apply_compression(self, original_tokens: int) -> int:
        """Apply compression ratio to estimate compressed token count.
        
        Args:
            original_tokens: Original token count
            
        Returns:
            Estimated compressed token count
        """
        return int(original_tokens * TOKEN_COMPRESSION_RATIO)
    
    def clear_session(self, session_id: UUID) -> None:
        """Clear context tracking for a session.
        
        Args:
            session_id: The CIA session ID to clear
        """
        if session_id in self._active_contexts:
            del self._active_contexts[session_id]
            logger.info(f"Cleared context for session {session_id}")
    
    def get_all_sessions(self) -> List[UUID]:
        """Get all sessions being monitored.
        
        Returns:
            List of session IDs
        """
        return list(self._active_contexts.keys())
    
    def get_summary(self, session_id: UUID) -> Dict[str, Any]:
        """Get a summary of context usage for a session.
        
        Args:
            session_id: The CIA session ID
            
        Returns:
            Summary dictionary
        """
        context = self.get_context(session_id)
        if not context:
            return {"error": "Session not found"}
        
        capacity = self.estimate_remaining_capacity(session_id)
        
        return {
            "session_id": str(session_id),
            "current_phase": context.current_phase,
            "completed_phases": context.completed_phases,
            "pending_phases": context.pending_phases,
            "total_tokens_used": context.total_tokens_used,
            "context_percentage": round(context.context_percentage, 2),
            "tokens_remaining": capacity["tokens_remaining"],
            "estimated_phases_remaining": capacity["estimated_phases_remaining"],
            "needs_handover": context.context_percentage >= (HANDOVER_THRESHOLD * 100),
            "phase_count": {
                "completed": len(context.completed_phases),
                "pending": len(context.pending_phases),
                "total": len(context.completed_phases) + len(context.pending_phases)
            }
        }