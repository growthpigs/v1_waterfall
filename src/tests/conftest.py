"""
Pytest configuration and fixtures for CIA system tests.
Provides common test utilities and mock data.
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from uuid import UUID, uuid4
from datetime import datetime
import os
from unittest.mock import Mock, AsyncMock, patch

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["SUPABASE_SERVICE_KEY"] = "test-service-key"
os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
os.environ["SECRET_KEY"] = "test-secret-key"

from ..config.settings import settings
from ..config.constants import CIAPhase, PhaseStatus, HumanLoopType
from ..database.models import (
    CIASession, CIASessionCreate,
    PhaseResponse, PhaseResponseCreate,
    MasterArchive, MasterArchiveCreate,
    HumanLoopState, HumanLoopStateCreate,
    ContextHandover, ContextHandoverCreate
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client_id() -> UUID:
    """Provide a test client ID."""
    return uuid4()


@pytest.fixture
def test_session_id() -> UUID:
    """Provide a test session ID."""
    return uuid4()


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    with patch('src.database.supabase_client.get_supabase') as mock:
        client = Mock()
        
        # Mock table operations
        table_mock = Mock()
        table_mock.select.return_value = table_mock
        table_mock.insert.return_value = table_mock
        table_mock.update.return_value = table_mock
        table_mock.delete.return_value = table_mock
        table_mock.eq.return_value = table_mock
        table_mock.neq.return_value = table_mock
        table_mock.gt.return_value = table_mock
        table_mock.gte.return_value = table_mock
        table_mock.lt.return_value = table_mock
        table_mock.lte.return_value = table_mock
        table_mock.in_.return_value = table_mock
        table_mock.order.return_value = table_mock
        table_mock.limit.return_value = table_mock
        table_mock.single.return_value = table_mock
        table_mock.range.return_value = table_mock
        
        # Default execute response
        table_mock.execute.return_value = Mock(data=[], count=0)
        
        client.table.return_value = table_mock
        mock.return_value = client
        
        yield client


@pytest.fixture
def sample_cia_session_data() -> dict:
    """Sample CIA session data for testing."""
    return {
        "url": "https://example.com",
        "company_name": "Example Corp",
        "kpoi": "John Doe",
        "country": "United States",
        "testimonials_url": "https://example.com/testimonials"
    }


@pytest.fixture
def sample_cia_session(test_client_id: UUID, sample_cia_session_data: dict) -> CIASession:
    """Create a sample CIA session instance."""
    return CIASession(
        id=uuid4(),
        client_id=test_client_id,
        **sample_cia_session_data,
        status=PhaseStatus.PENDING,
        completed_phases=[],
        failed_phases=[],
        total_tokens_used=0,
        handover_count=0,
        progress_percentage=0.0,
        human_inputs_pending=[],
        human_inputs_completed=[],
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_phase_response(test_client_id: UUID, test_session_id: UUID) -> PhaseResponse:
    """Create a sample phase response instance."""
    return PhaseResponse(
        id=uuid4(),
        client_id=test_client_id,
        session_id=test_session_id,
        phase_id=CIAPhase.PHASE_1A,
        prompt_used="Test prompt for phase 1A",
        response_content={"test": "response"},
        extracted_frameworks={"benson": {"pain_points": ["test"]}},
        prompt_tokens=100,
        response_tokens=200,
        total_tokens=300,
        context_usage_percentage=15.0,
        status=PhaseStatus.COMPLETED,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_master_archive(test_client_id: UUID, test_session_id: UUID) -> MasterArchive:
    """Create a sample master archive instance."""
    return MasterArchive(
        id=uuid4(),
        client_id=test_client_id,
        session_id=test_session_id,
        phase_number=CIAPhase.PHASE_1EB,
        intelligence_summary={
            "phase_synthesis": {"key": "insights"},
            "accumulated_insights": ["insight1", "insight2"]
        },
        customer_psychology={
            "pain_points": ["pain1", "pain2"],
            "desires": ["desire1", "desire2"],
            "beliefs": ["belief1"],
            "values": ["value1"],
            "behaviors": ["behavior1"]
        },
        competitive_analysis={"competitors": ["comp1", "comp2"]},
        authority_positioning={
            "pitch": "test",
            "publish": "test",
            "product": "test",
            "profile": "test",
            "partnership": "test"
        },
        content_strategy={"themes": ["theme1", "theme2"]},
        context_tokens_used=5000,
        phases_included=[CIAPhase.PHASE_1A, CIAPhase.PHASE_1B, CIAPhase.PHASE_1C, CIAPhase.PHASE_1D],
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_human_loop_state(test_client_id: UUID, test_session_id: UUID) -> HumanLoopState:
    """Create a sample human loop state instance."""
    return HumanLoopState(
        id=uuid4(),
        client_id=test_client_id,
        session_id=test_session_id,
        phase_id="2A",
        loop_type=HumanLoopType.DATAFORSEO_KEYWORDS,
        request_data={"keywords": ["keyword1", "keyword2"]},
        request_message="Please lookup these keywords in DataForSEO",
        notification_channels=["slack", "email"],
        status="waiting",
        sent_at=datetime.utcnow(),
        timeout_minutes=30,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_context_handover(test_client_id: UUID, test_session_id: UUID) -> ContextHandover:
    """Create a sample context handover instance."""
    return ContextHandover(
        id=uuid4(),
        client_id=test_client_id,
        session_id=test_session_id,
        current_phase=CIAPhase.PHASE_3C,
        context_usage_percentage=75.0,
        total_tokens_used=150000,
        completed_phases=[
            CIAPhase.PHASE_1A, CIAPhase.PHASE_1B, CIAPhase.PHASE_1C,
            CIAPhase.PHASE_1D, CIAPhase.PHASE_1EB, CIAPhase.PHASE_2A,
            CIAPhase.PHASE_2B, CIAPhase.PHASE_2EB, CIAPhase.PHASE_3A,
            CIAPhase.PHASE_3B
        ],
        pending_phases=[
            CIAPhase.PHASE_3C, CIAPhase.PHASE_3EB, CIAPhase.PHASE_4A,
            CIAPhase.PHASE_5A, CIAPhase.PHASE_6A
        ],
        critical_state={
            "company_url": "https://example.com",
            "insights_collected": 42,
            "frameworks_preserved": True
        },
        next_action="Resume from Phase 3C with accumulated intelligence",
        handover_number=1,
        created_at=datetime.utcnow()
    )


@pytest.fixture
async def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    with patch('anthropic.AsyncAnthropic') as mock_class:
        client = AsyncMock()
        
        # Mock message creation
        mock_response = Mock()
        mock_response.content = [Mock(text="Test AI response")]
        mock_response.usage = Mock(
            input_tokens=100,
            output_tokens=200,
            total_tokens=300
        )
        
        client.messages.create = AsyncMock(return_value=mock_response)
        mock_class.return_value = client
        
        yield client


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    with patch('redis.asyncio.Redis') as mock_class:
        client = AsyncMock()
        
        # Mock common Redis operations
        client.get = AsyncMock(return_value=None)
        client.set = AsyncMock(return_value=True)
        client.delete = AsyncMock(return_value=1)
        client.exists = AsyncMock(return_value=0)
        client.expire = AsyncMock(return_value=True)
        client.ttl = AsyncMock(return_value=-1)
        
        mock_class.from_url.return_value = client
        
        yield client


@pytest.fixture
def mock_slack_client():
    """Mock Slack client for testing."""
    with patch('httpx.AsyncClient') as mock_class:
        client = AsyncMock()
        
        # Mock webhook post
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"ok": True})
        
        client.post = AsyncMock(return_value=mock_response)
        mock_class.return_value = client
        
        yield client


@pytest.fixture
def mock_email_client():
    """Mock email client for testing."""
    with patch('aiosmtplib.SMTP') as mock_class:
        client = AsyncMock()
        
        # Mock SMTP operations
        client.connect = AsyncMock(return_value=(220, "Ready"))
        client.starttls = AsyncMock(return_value=(220, "Ready"))
        client.login = AsyncMock(return_value=(235, "Authenticated"))
        client.send_message = AsyncMock(return_value={})
        client.quit = AsyncMock(return_value=(221, "Bye"))
        
        mock_class.return_value = client
        
        yield client


# Test data generators
def generate_phase_responses(session_id: UUID, client_id: UUID, count: int = 5) -> list[PhaseResponse]:
    """Generate multiple phase responses for testing."""
    responses = []
    phases = list(CIAPhase)[:count]
    
    for i, phase in enumerate(phases):
        response = PhaseResponse(
            id=uuid4(),
            client_id=client_id,
            session_id=session_id,
            phase_id=phase,
            prompt_used=f"Test prompt for {phase}",
            response_content={"phase": phase.value, "index": i},
            extracted_frameworks={},
            prompt_tokens=100 * (i + 1),
            response_tokens=200 * (i + 1),
            total_tokens=300 * (i + 1),
            context_usage_percentage=15.0 * (i + 1),
            status=PhaseStatus.COMPLETED,
            created_at=datetime.utcnow()
        )
        responses.append(response)
    
    return responses