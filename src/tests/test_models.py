"""
Tests for CIA system Pydantic models.
Validates model creation, validation, and business logic.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from pydantic import ValidationError

from ..database.models import (
    CIASession, CIASessionCreate, CIASessionUpdate,
    PhaseResponse, PhaseResponseCreate,
    MasterArchive, MasterArchiveCreate,
    HumanLoopState, HumanLoopStateCreate,
    ContextHandover, ContextHandoverCreate
)
from ..config.constants import CIAPhase, PhaseStatus, HumanLoopType


class TestCIASessionModel:
    """Test CIASession model functionality."""
    
    def test_session_creation_valid(self, test_client_id, sample_cia_session_data):
        """Test creating a valid CIA session."""
        session = CIASession(
            id=uuid4(),
            client_id=test_client_id,
            **sample_cia_session_data
        )
        
        assert session.url == sample_cia_session_data["url"]
        assert session.company_name == sample_cia_session_data["company_name"]
        assert session.status == PhaseStatus.PENDING
        assert session.progress_percentage == 0.0
        assert len(session.completed_phases) == 0
    
    def test_session_url_validation(self, test_client_id):
        """Test URL validation in session creation."""
        with pytest.raises(ValidationError) as exc_info:
            CIASessionCreate(
                url="not-a-url",
                company_name="Test",
                kpoi="Test Person",
                country="USA"
            )
        
        assert "URL must start with http://" in str(exc_info.value)
    
    def test_session_progress_calculation(self, sample_cia_session):
        """Test progress percentage calculation."""
        # Add completed phases
        sample_cia_session.completed_phases = [
            CIAPhase.PHASE_1A,
            CIAPhase.PHASE_1B,
            CIAPhase.PHASE_1C
        ]
        sample_cia_session.total_phases = 15
        
        # Trigger validation
        validated = sample_cia_session.model_validate(sample_cia_session.model_dump())
        
        expected_progress = (3 / 15) * 100
        assert validated.progress_percentage == expected_progress
    
    def test_session_is_complete(self, sample_cia_session):
        """Test session completion check."""
        assert not sample_cia_session.is_complete()
        
        # Complete all phases
        sample_cia_session.completed_phases = [phase for phase in CIAPhase]
        sample_cia_session.total_phases = len(CIAPhase)
        
        assert sample_cia_session.is_complete()
    
    def test_session_requires_human_input(self, sample_cia_session):
        """Test human input requirement check."""
        assert not sample_cia_session.requires_human_input()
        
        sample_cia_session.human_inputs_pending = ["dataforseo_keywords"]
        assert sample_cia_session.requires_human_input()
    
    def test_session_get_next_phase(self, sample_cia_session):
        """Test getting next phase to execute."""
        # No phases completed
        next_phase = sample_cia_session.get_next_phase()
        assert next_phase == CIAPhase.PHASE_1A
        
        # Some phases completed
        sample_cia_session.completed_phases = [
            CIAPhase.PHASE_1A,
            CIAPhase.PHASE_1B
        ]
        next_phase = sample_cia_session.get_next_phase()
        assert next_phase == CIAPhase.PHASE_1C
        
        # All phases completed
        sample_cia_session.completed_phases = list(CIAPhase)
        next_phase = sample_cia_session.get_next_phase()
        assert next_phase is None


class TestPhaseResponseModel:
    """Test PhaseResponse model functionality."""
    
    def test_phase_response_creation(self, test_client_id, test_session_id):
        """Test creating a valid phase response."""
        response = PhaseResponse(
            id=uuid4(),
            client_id=test_client_id,
            session_id=test_session_id,
            phase_id=CIAPhase.PHASE_1A,
            prompt_used="Test prompt",
            response_content={"test": "data"},
            prompt_tokens=100,
            response_tokens=200,
            total_tokens=300,
            context_usage_percentage=15.0
        )
        
        assert response.phase_id == CIAPhase.PHASE_1A
        assert response.total_tokens == 300
        assert response.status == PhaseStatus.PENDING
    
    def test_context_usage_validation(self, test_client_id, test_session_id):
        """Test context usage percentage validation."""
        with pytest.raises(ValidationError) as exc_info:
            PhaseResponseCreate(
                session_id=test_session_id,
                phase_id=CIAPhase.PHASE_1A,
                prompt_used="Test",
                response_content={},
                prompt_tokens=100,
                response_tokens=200,
                total_tokens=300,
                context_usage_percentage=150.0  # Invalid
            )
        
        assert "Context usage must be between 0 and 100" in str(exc_info.value)
    
    def test_duration_calculation(self, sample_phase_response):
        """Test automatic duration calculation."""
        sample_phase_response.started_at = datetime.utcnow()
        sample_phase_response.completed_at = datetime.utcnow() + timedelta(seconds=120)
        
        validated = sample_phase_response.model_validate(sample_phase_response.model_dump())
        
        assert validated.duration_seconds is not None
        assert 119 <= validated.duration_seconds <= 121  # Allow for small time differences
    
    def test_phase_success_check(self, sample_phase_response):
        """Test phase success validation."""
        assert sample_phase_response.is_successful()
        
        sample_phase_response.error_message = "Test error"
        assert not sample_phase_response.is_successful()
    
    def test_context_threshold_check(self, sample_phase_response):
        """Test context threshold exceeded check."""
        sample_phase_response.context_usage_percentage = 65.0
        assert not sample_phase_response.exceeded_context_threshold()
        
        sample_phase_response.context_usage_percentage = 75.0
        assert sample_phase_response.exceeded_context_threshold()


class TestMasterArchiveModel:
    """Test MasterArchive model functionality."""
    
    def test_archive_creation(self, test_client_id, test_session_id):
        """Test creating a valid master archive."""
        archive = MasterArchive(
            id=uuid4(),
            client_id=test_client_id,
            session_id=test_session_id,
            phase_number=CIAPhase.PHASE_1EB,
            intelligence_summary={"key": "value"},
            customer_psychology={"pain_points": ["test"]},
            competitive_analysis={},
            authority_positioning={},
            content_strategy={},
            context_tokens_used=5000,
            phases_included=[CIAPhase.PHASE_1A, CIAPhase.PHASE_1B]
        )
        
        assert archive.phase_number == CIAPhase.PHASE_1EB
        assert archive.archive_version == 1
        assert len(archive.phases_included) == 2
    
    def test_metrics_calculation(self, sample_master_archive):
        """Test automatic metrics calculation."""
        validated = sample_master_archive.model_validate(sample_master_archive.model_dump())
        
        assert validated.insights_count == 2  # From accumulated_insights
        assert validated.opportunities_identified == 0  # No opportunities in test data
    
    def test_framework_validation(self, sample_master_archive):
        """Test framework integrity validation."""
        validation = sample_master_archive.validate_framework_integrity()
        
        assert validation["benson_points"] is True  # Has all required categories
        assert validation["priestley_5ps"] is True  # Has all 5 P's
        assert validation["frank_kern"] is False  # Missing in test data
        assert validation["golden_hippo"] is False  # Missing in test data
    
    def test_get_framework_names(self, sample_master_archive):
        """Test getting preserved framework names."""
        names = sample_master_archive.get_framework_names()
        
        assert "Benson Customer Psychology" in names
        assert "Priestley 5 P's" in names
        assert "Competitive Intelligence" in names
        assert "Content Strategy" in names


class TestHumanLoopStateModel:
    """Test HumanLoopState model functionality."""
    
    def test_loop_state_creation(self, test_client_id, test_session_id):
        """Test creating a valid human loop state."""
        loop_state = HumanLoopState(
            id=uuid4(),
            client_id=test_client_id,
            session_id=test_session_id,
            phase_id="2A",
            loop_type=HumanLoopType.DATAFORSEO_KEYWORDS,
            request_data={"keywords": ["test"]},
            request_message="Test request"
        )
        
        assert loop_state.loop_type == HumanLoopType.DATAFORSEO_KEYWORDS
        assert loop_state.status == "waiting"
        assert loop_state.timeout_minutes == 30
    
    def test_expiration_calculation(self, sample_human_loop_state):
        """Test automatic expiration time calculation."""
        validated = sample_human_loop_state.model_validate(sample_human_loop_state.model_dump())
        
        assert validated.expired_at is not None
        expected_expiration = validated.sent_at + timedelta(minutes=30)
        assert abs((validated.expired_at - expected_expiration).total_seconds()) < 1
    
    def test_is_expired_check(self, sample_human_loop_state):
        """Test expiration status check."""
        # Not expired yet
        assert not sample_human_loop_state.is_expired()
        
        # Set expiration to past
        sample_human_loop_state.expired_at = datetime.utcnow() - timedelta(minutes=1)
        assert sample_human_loop_state.is_expired()
    
    def test_needs_reminder_check(self, sample_human_loop_state):
        """Test reminder requirement check."""
        # Just sent
        assert not sample_human_loop_state.needs_reminder()
        
        # Set sent time to 20 minutes ago (past half timeout)
        sample_human_loop_state.sent_at = datetime.utcnow() - timedelta(minutes=20)
        assert sample_human_loop_state.needs_reminder()
        
        # Already sent reminder
        sample_human_loop_state.reminder_sent = True
        assert not sample_human_loop_state.needs_reminder()
    
    def test_response_validation_dataforseo(self, sample_human_loop_state):
        """Test DataForSEO response validation."""
        # Invalid response
        sample_human_loop_state.response_data = {"invalid": "data"}
        assert not sample_human_loop_state.validate_response()
        assert sample_human_loop_state.validation_errors is not None
        
        # Valid response
        sample_human_loop_state.response_data = {
            "search_volume": 1000,
            "competition": 0.5,
            "cpc": 2.50
        }
        assert sample_human_loop_state.validate_response()
        assert sample_human_loop_state.response_validated


class TestContextHandoverModel:
    """Test ContextHandover model functionality."""
    
    def test_handover_creation(self, test_client_id, test_session_id):
        """Test creating a valid context handover."""
        handover = ContextHandover(
            id=uuid4(),
            client_id=test_client_id,
            session_id=test_session_id,
            current_phase=CIAPhase.PHASE_3C,
            context_usage_percentage=75.0,
            total_tokens_used=150000,
            completed_phases=[CIAPhase.PHASE_1A],
            pending_phases=[CIAPhase.PHASE_3C],
            critical_state={"key": "value"},
            next_action="Continue analysis"
        )
        
        assert handover.context_usage_percentage == 75.0
        assert handover.handover_number == 1
        assert not handover.recovered
    
    def test_context_usage_validation(self, test_client_id, test_session_id):
        """Test context usage percentage validation."""
        with pytest.raises(ValidationError) as exc_info:
            ContextHandoverCreate(
                session_id=test_session_id,
                current_phase=CIAPhase.PHASE_3C,
                context_usage_percentage=150.0,  # Invalid
                total_tokens_used=150000,
                completed_phases=[],
                pending_phases=[],
                critical_state={},
                next_action="Test"
            )
        
        assert "Context usage must be between 0 and 100" in str(exc_info.value)
    
    def test_recovery_prompt_generation(self, sample_context_handover):
        """Test recovery prompt generation."""
        prompt = sample_context_handover.generate_recovery_prompt()
        
        assert f"Session {sample_context_handover.session_id}" in prompt
        assert f"Phase: {sample_context_handover.current_phase}" in prompt
        assert "Context Usage: 75.0%" in prompt
        assert sample_context_handover.next_action in prompt
    
    def test_recovery_context_extraction(self, sample_context_handover):
        """Test getting minimal recovery context."""
        context = sample_context_handover.get_recovery_context()
        
        assert context["session_id"] == str(sample_context_handover.session_id)
        assert context["current_phase"] == sample_context_handover.current_phase
        assert len(context["completed_phases"]) == 10
        assert context["critical_state"] == sample_context_handover.critical_state
    
    def test_recovery_readiness_validation(self, sample_context_handover):
        """Test handover recovery readiness check."""
        checks = sample_context_handover.validate_recovery_readiness()
        
        assert checks["has_critical_state"] is True
        assert checks["has_next_action"] is True
        assert checks["has_completed_phases"] is True
        assert checks["ready_for_recovery"] is True
        
        # Remove critical state
        sample_context_handover.critical_state = {}
        checks = sample_context_handover.validate_recovery_readiness()
        assert checks["has_critical_state"] is False
        assert checks["ready_for_recovery"] is False