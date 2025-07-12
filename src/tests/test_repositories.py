"""
Tests for CIA system database repositories.
Validates CRUD operations and business logic.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch

from ..database.repositories import (
    CIASessionRepository,
    PhaseResponseRepository,
    MasterArchiveRepository,
    HumanLoopRepository,
    ContextHandoverRepository
)
from ..database.models import (
    CIASessionCreate, CIASessionUpdate,
    PhaseResponseCreate, PhaseResponseUpdate,
    MasterArchiveCreate, MasterArchiveUpdate,
    HumanLoopStateCreate, HumanLoopStateUpdate,
    ContextHandoverCreate, ContextHandoverUpdate
)
from ..config.constants import CIAPhase, PhaseStatus, HumanLoopType


class TestCIASessionRepository:
    """Test CIASessionRepository functionality."""
    
    @pytest.fixture
    def repository(self, mock_supabase_client):
        """Create repository instance with mocked client."""
        return CIASessionRepository()
    
    async def test_create_session(self, repository, test_client_id, sample_cia_session_data, mock_supabase_client):
        """Test creating a new CIA session."""
        # Configure mock response
        mock_response_data = {
            "id": str(uuid4()),
            "client_id": str(test_client_id),
            **sample_cia_session_data,
            "status": "pending",
            "completed_phases": [],
            "failed_phases": [],
            "total_tokens_used": 0,
            "handover_count": 0,
            "progress_percentage": 0.0,
            "human_inputs_pending": [],
            "human_inputs_completed": [],
            "created_at": datetime.utcnow().isoformat()
        }
        mock_supabase_client.table().execute.return_value = Mock(data=[mock_response_data])
        
        # Create session
        session_data = CIASessionCreate(**sample_cia_session_data)
        session = await repository.create_session(session_data, test_client_id)
        
        # Verify
        assert session.url == sample_cia_session_data["url"]
        assert session.company_name == sample_cia_session_data["company_name"]
        assert session.status == PhaseStatus.PENDING
        mock_supabase_client.table().insert.assert_called_once()
    
    async def test_get_active_sessions(self, repository, test_client_id, mock_supabase_client):
        """Test retrieving active sessions."""
        # Configure mock response
        mock_sessions = [
            {
                "id": str(uuid4()),
                "client_id": str(test_client_id),
                "url": "https://example1.com",
                "company_name": "Example 1",
                "kpoi": "Person 1",
                "country": "USA",
                "status": "executing",
                "completed_phases": [],
                "failed_phases": [],
                "total_tokens_used": 1000,
                "handover_count": 0,
                "progress_percentage": 20.0,
                "human_inputs_pending": [],
                "human_inputs_completed": [],
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid4()),
                "client_id": str(test_client_id),
                "url": "https://example2.com",
                "company_name": "Example 2",
                "kpoi": "Person 2",
                "country": "UK",
                "status": "paused",
                "completed_phases": ["1A", "1B"],
                "failed_phases": [],
                "total_tokens_used": 2000,
                "handover_count": 0,
                "progress_percentage": 13.3,
                "human_inputs_pending": ["dataforseo_keywords"],
                "human_inputs_completed": [],
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        mock_supabase_client.table().execute.return_value = Mock(data=mock_sessions)
        
        # Get active sessions
        sessions = await repository.get_active_sessions(test_client_id)
        
        # Verify
        assert len(sessions) == 2
        assert sessions[0].status in [PhaseStatus.EXECUTING, PhaseStatus.PAUSED]
        assert sessions[1].requires_human_input()
        mock_supabase_client.table().in_.assert_called_once()
    
    async def test_update_phase_progress(self, repository, test_session_id, test_client_id, sample_cia_session, mock_supabase_client):
        """Test updating session after phase completion."""
        # Configure mock for get_by_id
        session_data = sample_cia_session.model_dump(mode='json')
        mock_supabase_client.table().execute.side_effect = [
            Mock(data=session_data),  # get_by_id response
            Mock(data=[{**session_data, "completed_phases": ["1A"], "progress_percentage": 6.67}])  # update response
        ]
        
        # Update progress
        session = await repository.update_phase_progress(
            test_session_id,
            CIAPhase.PHASE_1A,
            completed=True,
            tokens_used=500,
            test_client_id
        )
        
        # Verify
        assert session is not None
        assert CIAPhase.PHASE_1A in session.completed_phases
        assert session.total_tokens_used == 500
        assert session.progress_percentage > 0
    
    async def test_pause_resume_session(self, repository, test_session_id, test_client_id, mock_supabase_client):
        """Test pausing and resuming a session."""
        # Configure mock
        paused_data = {
            "id": str(test_session_id),
            "status": "paused",
            "paused_at": datetime.utcnow().isoformat()
        }
        resumed_data = {
            "id": str(test_session_id),
            "status": "executing",
            "paused_at": None
        }
        
        # Test pause
        mock_supabase_client.table().execute.return_value = Mock(data=[paused_data])
        paused = await repository.pause_session(test_session_id, test_client_id)
        assert paused.status == PhaseStatus.PAUSED
        
        # Test resume
        mock_supabase_client.table().execute.return_value = Mock(data=[resumed_data])
        resumed = await repository.resume_session(test_session_id, test_client_id)
        assert resumed.status == PhaseStatus.EXECUTING


class TestPhaseResponseRepository:
    """Test PhaseResponseRepository functionality."""
    
    @pytest.fixture
    def repository(self, mock_supabase_client):
        """Create repository instance with mocked client."""
        return PhaseResponseRepository()
    
    async def test_create_phase_response(self, repository, test_session_id, test_client_id, mock_supabase_client):
        """Test creating a new phase response."""
        # Configure mock
        mock_response_data = {
            "id": str(uuid4()),
            "client_id": str(test_client_id),
            "session_id": str(test_session_id),
            "phase_id": "1A",
            "prompt_used": "Test prompt",
            "response_content": {},
            "prompt_tokens": 0,
            "response_tokens": 0,
            "total_tokens": 0,
            "context_usage_percentage": 0.0,
            "status": "executing",
            "started_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        mock_supabase_client.table().execute.return_value = Mock(data=[mock_response_data])
        
        # Create response
        response = await repository.create_phase_response(
            test_session_id,
            CIAPhase.PHASE_1A,
            "Test prompt",
            test_client_id
        )
        
        # Verify
        assert response.phase_id == CIAPhase.PHASE_1A
        assert response.status == PhaseStatus.EXECUTING
        mock_supabase_client.table().insert.assert_called_once()
    
    async def test_update_with_response(self, repository, test_client_id, mock_supabase_client):
        """Test updating phase response with execution results."""
        response_id = uuid4()
        
        # Configure mock
        updated_data = {
            "id": str(response_id),
            "response_content": {"test": "result"},
            "extracted_frameworks": {"benson": {"pain_points": ["test"]}},
            "prompt_tokens": 100,
            "response_tokens": 200,
            "total_tokens": 300,
            "context_usage_percentage": 15.0,
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat()
        }
        mock_supabase_client.table().execute.return_value = Mock(data=[updated_data])
        
        # Update response
        tokens = {
            "prompt_tokens": 100,
            "response_tokens": 200,
            "total_tokens": 300,
            "context_usage_percentage": 15.0
        }
        updated = await repository.update_with_response(
            response_id,
            {"test": "result"},
            {"benson": {"pain_points": ["test"]}},
            tokens,
            test_client_id
        )
        
        # Verify
        assert updated.status == PhaseStatus.COMPLETED
        assert updated.total_tokens == 300
        assert "benson" in updated.extracted_frameworks
    
    async def test_get_phases_exceeding_threshold(self, repository, test_session_id, test_client_id, mock_supabase_client):
        """Test retrieving phases that exceeded context threshold."""
        # Configure mock
        mock_phases = [
            {
                "id": str(uuid4()),
                "session_id": str(test_session_id),
                "phase_id": "3C",
                "context_usage_percentage": 75.0,
                "total_tokens": 150000
            },
            {
                "id": str(uuid4()),
                "session_id": str(test_session_id),
                "phase_id": "3EB",
                "context_usage_percentage": 82.0,
                "total_tokens": 164000
            }
        ]
        mock_supabase_client.table().execute.return_value = Mock(data=mock_phases)
        
        # Get phases
        phases = await repository.get_phases_exceeding_threshold(
            test_session_id,
            0.70,
            test_client_id
        )
        
        # Verify
        assert len(phases) == 2
        assert all(p.context_usage_percentage > 70 for p in phases)


class TestMasterArchiveRepository:
    """Test MasterArchiveRepository functionality."""
    
    @pytest.fixture
    def repository(self, mock_supabase_client):
        """Create repository instance with mocked client."""
        return MasterArchiveRepository()
    
    async def test_create_archive(self, repository, test_session_id, test_client_id, mock_supabase_client):
        """Test creating a new master archive."""
        # Configure mock
        mock_archive_data = {
            "id": str(uuid4()),
            "client_id": str(test_client_id),
            "session_id": str(test_session_id),
            "phase_number": "1EB",
            "intelligence_summary": {"key": "value"},
            "customer_psychology": {"pain_points": ["test"]},
            "competitive_analysis": {},
            "authority_positioning": {},
            "content_strategy": {},
            "context_tokens_used": 5000,
            "phases_included": ["1A", "1B", "1C", "1D"],
            "archive_version": 1,
            "created_at": datetime.utcnow().isoformat()
        }
        mock_supabase_client.table().execute.return_value = Mock(data=[mock_archive_data])
        
        # Create archive
        archive = await repository.create_archive(
            test_session_id,
            CIAPhase.PHASE_1EB,
            {"intelligence_summary": {"key": "value"}},
            {"customer_psychology": {"pain_points": ["test"]}},
            5000,
            [CIAPhase.PHASE_1A, CIAPhase.PHASE_1B, CIAPhase.PHASE_1C, CIAPhase.PHASE_1D],
            test_client_id
        )
        
        # Verify
        assert archive.phase_number == CIAPhase.PHASE_1EB
        assert archive.archive_version == 1
        assert len(archive.phases_included) == 4
    
    async def test_validate_archive(self, repository, test_client_id, sample_master_archive, mock_supabase_client):
        """Test archive validation with framework checks."""
        archive_id = sample_master_archive.id
        
        # Configure mock
        mock_supabase_client.table().execute.side_effect = [
            Mock(data=sample_master_archive.model_dump(mode='json')),  # get_by_id
            Mock(data=[{**sample_master_archive.model_dump(mode='json'), "validated_at": datetime.utcnow().isoformat()}])  # update
        ]
        
        # Validate archive
        validated = await repository.validate_archive(
            archive_id,
            "Validation passed",
            test_client_id
        )
        
        # Verify
        assert validated.validated_at is not None
        assert validated.synthesis_quality_score > 0
        assert "benson_points" in validated.framework_integrity_scores


class TestHumanLoopRepository:
    """Test HumanLoopRepository functionality."""
    
    @pytest.fixture
    def repository(self, mock_supabase_client):
        """Create repository instance with mocked client."""
        return HumanLoopRepository()
    
    async def test_create_loop_state(self, repository, test_session_id, test_client_id, mock_supabase_client):
        """Test creating a human loop state."""
        # Configure mock
        mock_loop_data = {
            "id": str(uuid4()),
            "client_id": str(test_client_id),
            "session_id": str(test_session_id),
            "phase_id": "2A",
            "loop_type": "dataforseo_keywords",
            "request_data": {"keywords": ["test1", "test2"]},
            "request_message": "Please lookup keywords",
            "notification_channels": ["slack", "email"],
            "status": "waiting",
            "sent_at": datetime.utcnow().isoformat(),
            "timeout_minutes": 30,
            "created_at": datetime.utcnow().isoformat()
        }
        mock_supabase_client.table().execute.return_value = Mock(data=[mock_loop_data])
        
        # Create loop state
        loop_state = await repository.create_loop_state(
            test_session_id,
            "2A",
            HumanLoopType.DATAFORSEO_KEYWORDS,
            {"keywords": ["test1", "test2"]},
            "Please lookup keywords",
            test_client_id
        )
        
        # Verify
        assert loop_state.loop_type == HumanLoopType.DATAFORSEO_KEYWORDS
        assert loop_state.status == "waiting"
        assert len(loop_state.request_data["keywords"]) == 2
    
    async def test_submit_response(self, repository, test_client_id, sample_human_loop_state, mock_supabase_client):
        """Test submitting human response."""
        loop_id = sample_human_loop_state.id
        response_data = {
            "search_volume": 1000,
            "competition": 0.5,
            "cpc": 2.50
        }
        
        # Configure mock
        mock_supabase_client.table().execute.side_effect = [
            Mock(data=sample_human_loop_state.model_dump(mode='json')),  # get_by_id
            Mock(data=[{**sample_human_loop_state.model_dump(mode='json'), 
                       "response_data": response_data,
                       "status": "completed",
                       "response_validated": True}])  # update
        ]
        
        # Submit response
        updated = await repository.submit_response(
            loop_id,
            response_data,
            test_client_id
        )
        
        # Verify
        assert updated.status == "completed"
        assert updated.response_validated
        assert updated.response_data == response_data


class TestContextHandoverRepository:
    """Test ContextHandoverRepository functionality."""
    
    @pytest.fixture
    def repository(self, mock_supabase_client):
        """Create repository instance with mocked client."""
        return ContextHandoverRepository()
    
    async def test_create_handover(self, repository, test_session_id, test_client_id, mock_supabase_client):
        """Test creating a context handover."""
        # Configure mock - first call returns empty list (no previous handovers)
        mock_supabase_client.table().execute.side_effect = [
            Mock(data=[]),  # get_session_handovers
            Mock(data=[{
                "id": str(uuid4()),
                "client_id": str(test_client_id),
                "session_id": str(test_session_id),
                "current_phase": "3C",
                "context_usage_percentage": 75.0,
                "total_tokens_used": 150000,
                "completed_phases": ["1A", "1B", "1C"],
                "pending_phases": ["3C", "3EB", "4A"],
                "critical_state": {"key": "value"},
                "next_action": "Continue from 3C",
                "handover_number": 1,
                "created_at": datetime.utcnow().isoformat()
            }])  # create
        ]
        
        # Create handover
        handover = await repository.create_handover(
            test_session_id,
            CIAPhase.PHASE_3C,
            75.0,
            150000,
            [CIAPhase.PHASE_1A, CIAPhase.PHASE_1B, CIAPhase.PHASE_1C],
            [CIAPhase.PHASE_3C, CIAPhase.PHASE_3EB, CIAPhase.PHASE_4A],
            {"key": "value"},
            "Continue from 3C",
            test_client_id
        )
        
        # Verify
        assert handover.current_phase == CIAPhase.PHASE_3C
        assert handover.context_usage_percentage == 75.0
        assert handover.handover_number == 1
    
    async def test_export_handover_document(self, repository, test_client_id, sample_context_handover, mock_supabase_client):
        """Test exporting handover as document."""
        # Configure mock
        mock_supabase_client.table().execute.return_value = Mock(
            data=sample_context_handover.model_dump(mode='json')
        )
        
        # Export document
        document = await repository.export_handover_document(
            sample_context_handover.id,
            test_client_id
        )
        
        # Verify
        assert document is not None
        assert "CIA CONTEXT HANDOVER DOCUMENT" in document
        assert f"Session ID: {sample_context_handover.session_id}" in document
        assert "Context Usage: 75.0%" in document
        assert sample_context_handover.next_action in document