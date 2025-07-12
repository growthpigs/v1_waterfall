"""
CIA Phase Engine - Core orchestrator for 6-phase intelligence pipeline.
Executes phases with context management and human-in-loop workflows.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

from ..config.constants import (
    CIAPhase,
    PhaseStatus,
    CIA_PHASE_ORDER,
    CIA_PHASE_CONFIG,
    HUMAN_INPUT_PHASES,
    ARCHIVE_PHASES,
    HumanLoopType
)
from ..database.models import (
    CIASession,
    PhaseResponse,
    PhaseResponseCreate,
    MasterArchive,
    HumanLoopState
)
from ..database.repositories import (
    CIASessionRepository,
    PhaseResponseRepository,
    MasterArchiveRepository,
    HumanLoopRepository,
    ContextHandoverRepository
)
from ..integrations.anthropic.claude_client import ClaudeClient, TokenUsage
from .compressed_prompts import CompressedPromptsLoader
from .context_monitor import ContextMonitor
from .master_archive import MasterArchiveBuilder
from .human_loop_coordinator import HumanLoopCoordinator

logger = logging.getLogger(__name__)


@dataclass
class PhaseExecutionResult:
    """Result from executing a single phase."""
    phase_id: CIAPhase
    success: bool
    response_content: Dict[str, Any]
    token_usage: TokenUsage
    requires_human_input: bool = False
    human_input_type: Optional[HumanLoopType] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None


class CIAPhaseEngine:
    """Core engine for executing CIA 6-phase analysis."""
    
    def __init__(
        self,
        session_repository: CIASessionRepository,
        phase_repository: PhaseResponseRepository,
        archive_repository: MasterArchiveRepository,
        human_loop_repository: HumanLoopRepository,
        handover_repository: ContextHandoverRepository,
        claude_client: Optional[ClaudeClient] = None,
        prompts_loader: Optional[CompressedPromptsLoader] = None,
        context_monitor: Optional[ContextMonitor] = None
    ):
        """Initialize the phase engine with required dependencies.
        
        Args:
            session_repository: Repository for CIA sessions
            phase_repository: Repository for phase responses
            archive_repository: Repository for master archives
            human_loop_repository: Repository for human-in-loop states
            handover_repository: Repository for context handovers
            claude_client: Claude API client (created if None)
            prompts_loader: Prompts loader (created if None)
            context_monitor: Context monitor (created if None)
        """
        self.session_repo = session_repository
        self.phase_repo = phase_repository
        self.archive_repo = archive_repository
        self.human_loop_repo = human_loop_repository
        self.handover_repo = handover_repository
        
        # Initialize components
        self.claude = claude_client or ClaudeClient()
        self.prompts = prompts_loader or CompressedPromptsLoader()
        self.context_monitor = context_monitor or ContextMonitor(handover_repository)
        self.archive_builder = MasterArchiveBuilder()
        self.human_loop = HumanLoopCoordinator(human_loop_repository)
        
        # Load all prompts
        self.prompts.load_all_prompts()
    
    async def execute_session(
        self,
        session: CIASession,
        client_id: UUID,
        start_from_phase: Optional[CIAPhase] = None
    ) -> Dict[str, Any]:
        """Execute a complete CIA analysis session.
        
        Args:
            session: The CIA session to execute
            client_id: The client ID
            start_from_phase: Optional phase to start from (for resume)
            
        Returns:
            Dictionary with execution results
        """
        logger.info(f"Starting CIA analysis for session {session.id}")
        
        # Initialize context monitoring
        all_phases = [phase.value for phase in CIA_PHASE_ORDER]
        context_state = self.context_monitor.start_session(session.id, all_phases)
        
        # Update session status
        await self.session_repo.start_session(session.id, client_id)
        
        # Get starting point
        phases_to_execute = self._get_phases_to_execute(session, start_from_phase)
        
        # Track results
        results = {
            "session_id": str(session.id),
            "phases_completed": [],
            "phases_failed": [],
            "archives_created": [],
            "human_inputs_required": [],
            "handover_created": False,
            "total_duration_seconds": 0
        }
        
        session_start = datetime.utcnow()
        
        # Execute phases
        for phase in phases_to_execute:
            try:
                # Check context usage before phase
                capacity = self.context_monitor.estimate_remaining_capacity(session.id)
                if capacity["percentage_remaining"] < 10:
                    logger.warning(f"Low context capacity before {phase}: {capacity['percentage_remaining']:.1f}% remaining")
                
                # Execute phase
                phase_result = await self._execute_phase(
                    session=session,
                    phase=phase,
                    client_id=client_id
                )
                
                if phase_result.success:
                    results["phases_completed"].append(phase.value)
                    
                    # Check if this phase creates an archive
                    if phase in ARCHIVE_PHASES:
                        archive = await self._create_master_archive(
                            session_id=session.id,
                            phase=phase,
                            client_id=client_id
                        )
                        if archive:
                            results["archives_created"].append(str(archive.id))
                    
                    # Check if human input required
                    if phase_result.requires_human_input:
                        results["human_inputs_required"].append({
                            "phase": phase.value,
                            "type": phase_result.human_input_type.value if phase_result.human_input_type else None
                        })
                        
                        # Pause session for human input
                        await self.session_repo.pause_session(
                            session.id, 
                            client_id,
                            f"Human input required for {phase.value}"
                        )
                        
                        logger.info(f"Session {session.id} paused for human input at {phase}")
                        break  # Stop execution until human input received
                    
                else:
                    results["phases_failed"].append({
                        "phase": phase.value,
                        "error": phase_result.error_message
                    })
                    logger.error(f"Phase {phase} failed: {phase_result.error_message}")
                
                # Check if handover needed
                _, needs_handover = self.context_monitor.add_tokens(
                    session.id,
                    phase.value,
                    phase_result.token_usage.input_tokens,
                    phase_result.token_usage.output_tokens
                )
                
                if needs_handover:
                    handover = await self._create_handover(session, client_id)
                    results["handover_created"] = True
                    results["handover_id"] = str(handover.id) if handover else None
                    
                    logger.warning(f"Context limit reached - handover created for session {session.id}")
                    break
                
            except Exception as e:
                logger.error(f"Error executing phase {phase}: {e}")
                results["phases_failed"].append({
                    "phase": phase.value,
                    "error": str(e)
                })
        
        # Calculate total duration
        results["total_duration_seconds"] = (datetime.utcnow() - session_start).total_seconds()
        
        # Get final context summary
        results["context_summary"] = self.context_monitor.get_summary(session.id)
        
        logger.info(f"CIA analysis completed for session {session.id}: {len(results['phases_completed'])} phases completed")
        
        return results
    
    async def _execute_phase(
        self,
        session: CIASession,
        phase: CIAPhase,
        client_id: UUID
    ) -> PhaseExecutionResult:
        """Execute a single CIA phase.
        
        Args:
            session: The CIA session
            phase: The phase to execute
            client_id: The client ID
            
        Returns:
            PhaseExecutionResult
        """
        logger.info(f"Executing phase {phase} for session {session.id}")
        phase_start = datetime.utcnow()
        
        try:
            # Update context monitor
            self.context_monitor.update_phase_start(session.id, phase.value)
            
            # Get prompt for this phase
            prompt = self.prompts.get_prompt_with_substitutions(
                phase=phase,
                company_name=session.company_name,
                company_url=session.url,
                kpoi=session.kpoi,
                country=session.country,
                testimonials_url=session.testimonials_url
            )
            
            if not prompt:
                raise ValueError(f"No prompt found for phase {phase}")
            
            # Compress prompt
            compressed_prompt = self.prompts.compress_prompt(prompt)
            
            # Create phase response record
            phase_response = await self.phase_repo.create_phase_response(
                session_id=session.id,
                phase_id=phase,
                prompt_used=compressed_prompt,
                client_id=client_id
            )
            
            # Check if this phase requires human input
            if phase in HUMAN_INPUT_PHASES:
                phase_config = CIA_PHASE_CONFIG.get(phase, {})
                human_loop_type = phase_config.get("human_input_type")
                
                # Create human loop state
                loop_state = await self.human_loop.initiate_workflow(
                    session_id=session.id,
                    phase_id=phase.value,
                    loop_type=human_loop_type,
                    request_data={"phase": phase.value, "session": str(session.id)},
                    client_id=client_id
                )
                
                # Mark phase as requiring human input
                await self.phase_repo.mark_human_input_required(
                    phase_response.id,
                    human_loop_type.value,
                    client_id
                )
                
                return PhaseExecutionResult(
                    phase_id=phase,
                    success=True,
                    response_content={"status": "waiting_for_human_input"},
                    token_usage=TokenUsage(0, 0),
                    requires_human_input=True,
                    human_input_type=human_loop_type
                )
            
            # Get context for this phase
            context = await self._build_phase_context(session.id, phase, client_id)
            
            # Execute with Claude
            response_text, token_usage, extracted_data = await self.claude.complete_with_context(
                prompt=compressed_prompt,
                context=context,
                max_tokens=4096,
                temperature=0.7
            )
            
            # Update phase response with results
            await self.phase_repo.update_with_response(
                response_id=phase_response.id,
                response_content={
                    "response": response_text,
                    "extracted": extracted_data
                },
                extracted_frameworks=extracted_data.get("frameworks", {}),
                tokens={
                    "prompt_tokens": token_usage.input_tokens,
                    "response_tokens": token_usage.output_tokens,
                    "total_tokens": token_usage.total_tokens,
                    "context_usage_percentage": (token_usage.total_tokens / 200000) * 100
                },
                client_id=client_id
            )
            
            # Mark phase complete in context monitor
            self.context_monitor.complete_phase(session.id, phase.value)
            
            # Update session progress
            await self.session_repo.update_phase_progress(
                session_id=session.id,
                phase=phase,
                completed=True,
                tokens_used=token_usage.total_tokens,
                client_id=client_id
            )
            
            duration = (datetime.utcnow() - phase_start).total_seconds()
            
            return PhaseExecutionResult(
                phase_id=phase,
                success=True,
                response_content={
                    "response": response_text,
                    "extracted": extracted_data
                },
                token_usage=token_usage,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Error in phase {phase}: {e}")
            
            # Mark phase as failed
            if 'phase_response' in locals():
                await self.phase_repo.mark_as_failed(
                    phase_response.id,
                    str(e),
                    {"exception_type": type(e).__name__},
                    client_id
                )
            
            # Update session with failed phase
            await self.session_repo.update_phase_progress(
                session_id=session.id,
                phase=phase,
                completed=False,
                tokens_used=0,
                client_id=client_id
            )
            
            return PhaseExecutionResult(
                phase_id=phase,
                success=False,
                response_content={},
                token_usage=TokenUsage(0, 0),
                error_message=str(e)
            )
    
    async def _build_phase_context(
        self,
        session_id: UUID,
        phase: CIAPhase,
        client_id: UUID
    ) -> Dict[str, Any]:
        """Build context for phase execution.
        
        Args:
            session_id: The session ID
            phase: Current phase
            client_id: The client ID
            
        Returns:
            Context dictionary
        """
        context = {
            "current_phase": phase.value,
            "phase_name": CIA_PHASE_CONFIG.get(phase, {}).get("name", phase.value)
        }
        
        # Get previous archives
        archives = await self.archive_repo.get_session_archives(session_id, client_id)
        if archives:
            context["previous_archives"] = [
                {
                    "phase": archive.phase_number,
                    "summary": archive.intelligence_summary.get("phase_synthesis", {})
                }
                for archive in archives[-3:]  # Last 3 archives for context
            ]
        
        # Get completed phases
        completed_responses = await self.phase_repo.get_session_responses(
            session_id, client_id, include_failed=False
        )
        context["completed_phases"] = [r.phase_id for r in completed_responses]
        
        return context
    
    async def _create_master_archive(
        self,
        session_id: UUID,
        phase: CIAPhase,
        client_id: UUID
    ) -> Optional[MasterArchive]:
        """Create a master archive for the current phase.
        
        Args:
            session_id: The session ID
            phase: The phase that triggers archive creation
            client_id: The client ID
            
        Returns:
            Created MasterArchive or None
        """
        try:
            # Get all phase responses up to this point
            phase_responses = await self.phase_repo.get_session_responses(
                session_id, client_id, include_failed=False
            )
            
            # Get previous archives
            previous_archives = await self.archive_repo.get_session_archives(
                session_id, client_id
            )
            
            # Build archive using the archive builder
            archive_data = self.archive_builder.build_archive(
                phase=phase,
                phase_responses=phase_responses,
                previous_archives=previous_archives
            )
            
            # Get latest archive for chaining
            latest_archive = previous_archives[-1] if previous_archives else None
            
            # Calculate total tokens
            total_tokens = sum(r.total_tokens for r in phase_responses)
            
            # Create archive
            archive = await self.archive_repo.create_archive(
                session_id=session_id,
                phase_number=phase,
                intelligence_data=archive_data["intelligence"],
                frameworks=archive_data["frameworks"],
                tokens_used=total_tokens,
                phases_included=[r.phase_id for r in phase_responses],
                client_id=client_id,
                previous_archive_id=latest_archive.id if latest_archive else None
            )
            
            logger.info(f"Created master archive for phase {phase}, session {session_id}")
            return archive
            
        except Exception as e:
            logger.error(f"Failed to create master archive: {e}")
            return None
    
    async def _create_handover(
        self,
        session: CIASession,
        client_id: UUID
    ) -> Optional[ContextHandover]:
        """Create a context handover for the session.
        
        Args:
            session: The CIA session
            client_id: The client ID
            
        Returns:
            Created handover or None
        """
        try:
            # Get latest archive
            archives = await self.archive_repo.get_session_archives(session.id, client_id)
            latest_archive = archives[-1] if archives else None
            
            # Build critical state
            critical_state = {
                "session_data": {
                    "company_name": session.company_name,
                    "company_url": session.url,
                    "kpoi": session.kpoi,
                    "country": session.country,
                    "testimonials_url": session.testimonials_url
                },
                "completed_phases": session.completed_phases,
                "human_inputs_completed": session.human_inputs_completed
            }
            
            # Create handover
            handover = await self.context_monitor.create_handover(
                session_id=session.id,
                client_id=client_id,
                critical_state=critical_state,
                latest_archive_id=latest_archive.id if latest_archive else None,
                preserved_archives=[a.id for a in archives]
            )
            
            # Update session
            await self.session_repo.increment_handover_count(session.id, client_id)
            
            return handover
            
        except Exception as e:
            logger.error(f"Failed to create handover: {e}")
            return None
    
    def _get_phases_to_execute(
        self,
        session: CIASession,
        start_from: Optional[CIAPhase] = None
    ) -> List[CIAPhase]:
        """Determine which phases to execute.
        
        Args:
            session: The CIA session
            start_from: Optional phase to start from
            
        Returns:
            List of phases to execute
        """
        # Get all phases
        all_phases = list(CIA_PHASE_ORDER)
        
        # Filter out completed phases
        completed = set(session.completed_phases)
        phases_to_execute = [p for p in all_phases if p.value not in completed]
        
        # If starting from specific phase, skip earlier ones
        if start_from and start_from in phases_to_execute:
            start_index = phases_to_execute.index(start_from)
            phases_to_execute = phases_to_execute[start_index:]
        
        return phases_to_execute
    
    async def resume_after_human_input(
        self,
        session_id: UUID,
        loop_id: UUID,
        response_data: Dict[str, Any],
        client_id: UUID
    ) -> Dict[str, Any]:
        """Resume session after receiving human input.
        
        Args:
            session_id: The session ID
            loop_id: The human loop state ID
            response_data: Human-provided response data
            client_id: The client ID
            
        Returns:
            Resume result dictionary
        """
        # Process human input
        success = await self.human_loop.process_response(
            loop_id=loop_id,
            response_data=response_data,
            client_id=client_id
        )
        
        if not success:
            return {"error": "Failed to process human input"}
        
        # Get session
        session = await self.session_repo.get_by_id(session_id, client_id)
        if not session:
            return {"error": "Session not found"}
        
        # Resume session
        await self.session_repo.resume_session(session_id, client_id)
        
        # Continue execution from next phase
        return await self.execute_session(session, client_id)
    
    async def get_phase_metrics(self, session_id: UUID) -> Dict[str, Any]:
        """Get execution metrics for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Metrics dictionary
        """
        return self.context_monitor.get_phase_metrics(session_id)