"""
CIA System API Routes
Endpoints for Central Intelligence Arsenal operations
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from ...cia import CIAPhaseEngine
from ...database.models import CIASession, CIAPhase
from ...database.repositories import (
    CIASessionRepository,
    ClientRepository,
    PhaseResponseRepository,
    MasterArchiveRepository,
    HumanLoopRepository,
    HandoverRepository
)

router = APIRouter()


# Request/Response Models
class StartCIAAnalysisRequest(BaseModel):
    """Request to start CIA analysis"""
    client_id: UUID
    company_name: str
    industry: str
    target_audience: Dict[str, Any]
    website_url: Optional[str] = None
    starting_phase: Optional[CIAPhase] = CIAPhase.PHASE_1A
    
    class Config:
        json_encoders = {
            UUID: str,
            CIAPhase: lambda v: v.value
        }


class CIASessionResponse(BaseModel):
    """CIA session response"""
    session_id: UUID
    status: str
    current_phase: str
    progress_percentage: float
    created_at: datetime
    message: str
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


class HumanLoopSubmission(BaseModel):
    """Human loop response submission"""
    session_id: UUID
    phase: CIAPhase
    response_data: Dict[str, Any]
    submitted_by: str = "user"


# Dependency injection
async def get_cia_engine() -> CIAPhaseEngine:
    """Get CIA engine instance"""
    # Initialize repositories
    session_repo = CIASessionRepository()
    phase_repo = PhaseResponseRepository()
    archive_repo = MasterArchiveRepository()
    human_loop_repo = HumanLoopRepository()
    handover_repo = HandoverRepository()
    
    return CIAPhaseEngine(
        session_repo=session_repo,
        phase_repo=phase_repo,
        archive_repo=archive_repo,
        human_loop_repo=human_loop_repo,
        handover_repo=handover_repo
    )


@router.post("/analysis/start", response_model=CIASessionResponse)
async def start_cia_analysis(
    request: StartCIAAnalysisRequest,
    background_tasks: BackgroundTasks,
    engine: CIAPhaseEngine = Depends(get_cia_engine)
) -> CIASessionResponse:
    """
    Start a new CIA analysis session
    
    This initiates the 6-phase intelligence analysis process
    """
    try:
        # Verify client exists
        client_repo = ClientRepository()
        client = await client_repo.get_by_id(request.client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Create CIA session
        session = CIASession(
            client_id=request.client_id,
            status="active",
            current_phase=request.starting_phase,
            company_data={
                "name": request.company_name,
                "industry": request.industry,
                "target_audience": request.target_audience,
                "website_url": request.website_url
            },
            created_at=datetime.now()
        )
        
        # Save session
        session_repo = CIASessionRepository()
        saved_session = await session_repo.create(session)
        
        # Start analysis in background
        background_tasks.add_task(
            engine.execute_session,
            session=saved_session,
            client_id=request.client_id,
            start_from_phase=request.starting_phase
        )
        
        return CIASessionResponse(
            session_id=saved_session.id,
            status="started",
            current_phase=saved_session.current_phase.value,
            progress_percentage=0.0,
            created_at=saved_session.created_at,
            message="CIA analysis started successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{session_id}/status", response_model=Dict[str, Any])
async def get_analysis_status(
    session_id: UUID,
    engine: CIAPhaseEngine = Depends(get_cia_engine)
) -> Dict[str, Any]:
    """Get current status of CIA analysis session"""
    try:
        session_repo = CIASessionRepository()
        session = await session_repo.get_by_id(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get phase responses
        phase_repo = PhaseResponseRepository()
        responses = await phase_repo.get_session_responses(session_id)
        
        # Calculate progress
        total_phases = 15  # Total CIA phases
        completed_phases = len(responses)
        progress = (completed_phases / total_phases) * 100
        
        # Check for human loop requirements
        human_loop_repo = HumanLoopRepository()
        pending_loops = await human_loop_repo.get_pending_by_session(session_id)
        
        return {
            "session_id": str(session_id),
            "status": session.status,
            "current_phase": session.current_phase.value,
            "progress_percentage": progress,
            "completed_phases": [r.phase.value for r in responses],
            "pending_human_loops": [
                {
                    "phase": loop.phase.value,
                    "loop_type": loop.loop_type,
                    "created_at": loop.created_at.isoformat()
                }
                for loop in pending_loops
            ],
            "created_at": session.created_at.isoformat(),
            "last_updated": session.last_updated.isoformat() if session.last_updated else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analysis/{session_id}/human-loop")
async def submit_human_loop_response(
    session_id: UUID,
    submission: HumanLoopSubmission,
    engine: CIAPhaseEngine = Depends(get_cia_engine)
) -> Dict[str, str]:
    """Submit human-in-loop response for DataForSEO or Perplexity phases"""
    try:
        # Validate session
        session_repo = CIASessionRepository()
        session = await session_repo.get_by_id(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Submit response
        human_loop_repo = HumanLoopRepository()
        await human_loop_repo.submit_response(
            session_id=session_id,
            phase=submission.phase,
            response_data=submission.response_data
        )
        
        # Resume analysis if applicable
        if session.status == "waiting_human_input":
            await engine.resume_from_human_loop(session_id)
        
        return {
            "status": "success",
            "message": "Human loop response submitted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{session_id}/results")
async def get_analysis_results(
    session_id: UUID,
    phase: Optional[CIAPhase] = None
) -> Dict[str, Any]:
    """Get CIA analysis results for a session or specific phase"""
    try:
        phase_repo = PhaseResponseRepository()
        
        if phase:
            # Get specific phase results
            response = await phase_repo.get_by_session_and_phase(session_id, phase)
            if not response:
                raise HTTPException(
                    status_code=404,
                    detail=f"No results found for phase {phase.value}"
                )
            
            return {
                "session_id": str(session_id),
                "phase": response.phase.value,
                "prompt_tokens": response.prompt_tokens,
                "response_tokens": response.response_tokens,
                "response_data": response.response_data,
                "framework_extraction": response.framework_extraction,
                "created_at": response.created_at.isoformat()
            }
        else:
            # Get all phase results
            responses = await phase_repo.get_session_responses(session_id)
            
            return {
                "session_id": str(session_id),
                "total_phases": len(responses),
                "phases": [
                    {
                        "phase": r.phase.value,
                        "tokens": r.prompt_tokens + r.response_tokens,
                        "created_at": r.created_at.isoformat()
                    }
                    for r in responses
                ],
                "master_archives": await _get_master_archives(session_id)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_cia_sessions(
    client_id: Optional[UUID] = None,
    status: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """List CIA sessions with optional filtering"""
    try:
        session_repo = CIASessionRepository()
        
        if client_id:
            sessions = await session_repo.get_by_client(client_id, limit=limit)
        else:
            # Get recent sessions
            sessions = await session_repo.get_recent_sessions(limit=limit)
        
        # Filter by status if provided
        if status:
            sessions = [s for s in sessions if s.status == status]
        
        return {
            "total": len(sessions),
            "sessions": [
                {
                    "session_id": str(s.id),
                    "client_id": str(s.client_id),
                    "status": s.status,
                    "current_phase": s.current_phase.value,
                    "company_name": s.company_data.get("name", "Unknown"),
                    "created_at": s.created_at.isoformat()
                }
                for s in sessions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analysis/{session_id}/cancel")
async def cancel_analysis(session_id: UUID) -> Dict[str, str]:
    """Cancel an active CIA analysis session"""
    try:
        session_repo = CIASessionRepository()
        session = await session_repo.get_by_id(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.status not in ["active", "waiting_human_input"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel session in {session.status} status"
            )
        
        # Update session status
        session.status = "cancelled"
        await session_repo.update(session)
        
        return {
            "status": "success",
            "message": "CIA analysis cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
async def _get_master_archives(session_id: UUID) -> List[Dict[str, Any]]:
    """Get master archives for a session"""
    archive_repo = MasterArchiveRepository()
    archives = await archive_repo.get_by_session(session_id)
    
    return [
        {
            "phase_boundary": a.phase_boundary,
            "created_at": a.created_at.isoformat(),
            "key_insights": a.synthesis_data.get("key_insights", [])[:3]
        }
        for a in archives
    ]