name: "CIA System - Complete Intelligence Engine"
description: |
  Comprehensive PRP for implementing the complete CIA (Central Intelligence Arsenal) 6-phase intelligence pipeline with context management, human-in-loop workflows, and Master Archive synthesis.

## Core Principles
1. **Intelligence Preservation**: All customer psychology frameworks (Benson 1-77+, Frank Kern, Priestley) must be maintained
2. **Context Management**: Design for 70% usage handovers with automatic session continuity  
3. **Human-in-Loop**: Mandatory pause points for DataForSEO (Phase 2A) and Perplexity (Phase 3A)
4. **Master Archives**: Intelligence synthesis between phases prevents data loss
5. **Framework Integration**: Systematic preservation of proven methodologies

---

## Goal
Build the complete CIA intelligence engine that transforms any business URL into comprehensive marketing intelligence through a systematic 6-phase pipeline with proper context window management and human-in-loop workflows.

## Why
- **Foundation for All Systems**: CIA provides the intelligence foundation for Cartwheel content generation and Adsby campaign optimization
- **Scalable Intelligence**: Enables consistent analysis across unlimited clients without manual research
- **Framework Preservation**: Maintains proven customer psychology methodologies at scale
- **Context Engineering**: Handles AI limitations through systematic handover and session management

## What
A complete 6-phase intelligence pipeline that:
- Executes compressed prompts with 70-85% reduction while maintaining analytical depth
- Automatically creates Master Archives between phases to preserve intelligence
- Handles human-in-loop workflows for real-time data integration (DataForSEO, Perplexity)
- Manages context windows with automatic handovers at 70% usage
- Stores all intelligence in Supabase with proper client isolation
- Provides session resumption capability across context limits

### Success Criteria
- [ ] All 6 phases execute successfully with compressed prompts (70-85% reduction achieved)
- [ ] Context usage monitoring triggers handovers at 70% threshold automatically
- [ ] Human-in-loop workflows deliver Slack + Email notifications reliably
- [ ] Master Archives preserve all intelligence frameworks (Benson, Kern, Priestley)
- [ ] Session state recoverable across context limits with zero intelligence loss
- [ ] Performance: Each phase completes within 2-3 minutes (excluding human pauses)
- [ ] Database integration: All intelligence stored with proper client isolation

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- doc: CIA Framework Documentation
  file: documents/CIA Waterfall System - Compressed Prompts Handover.md
  sections: [6-phase structure, compressed prompts, memory chain protocol]
  critical: [Context window management, human-in-loop workflows, Master Archive synthesis]
  
- doc: Enhanced SEO Research Report Prompt
  file: documents/Enhanced SEO Research Report Prompt.md
  sections: [DataForSEO integration, keyword analysis patterns]
  critical: [Phase 2A workflow, keyword extraction, SERP analysis]

- doc: Daniel Priestley KPI Methodology
  file: documents/Daniel Priestley's Key Person of Influence.md
  sections: [5 P's framework, authority building, business integration]
  critical: [Phase 1C assessment, authority positioning]

- doc: Supabase Documentation
  url: https://docs.supabase.com/
  sections: [Database, Auth, Real-time subscriptions, Row Level Security]
  critical: [Multi-tenant isolation, performance optimization]

- doc: DataForSEO API Documentation
  url: https://docs.dataforseo.com/
  sections: [Keywords API, SERP API, authentication]
  critical: [Rate limiting, response formats, Phase 2A integration]

- file: examples/cia_phase_structure.py
  why: [Phase execution patterns, context management, Master Archive synthesis]
  
- file: examples/human_in_loop_workflow.py  
  why: [Notification patterns, pause/resume logic, Slack integration]

- file: examples/client_configuration.py
  why: [Client preference management, configuration validation]
```

### Current Codebase Structure
```bash
V1_Waterfall/
├── .claude/                    # Context engineering framework
├── PRPs/                      # Product Requirements Prompts  
├── examples/                  # Implementation patterns (COMPLETE)
│   ├── cia_phase_structure.py       # Phase execution and context management
│   ├── human_in_loop_workflow.py    # Slack/Email notification workflows
│   ├── cartwheel_convergence_engine.py  # For future Cartwheel integration
│   ├── content_multiplication_pipeline.py  # For content generation context
│   ├── publishing_automation.py     # For publishing integration context
│   ├── adsby_optimization.py        # For ad campaign context
│   └── client_configuration.py      # Client preference patterns
├── src/                       # Source code (TO BE CREATED)
│   ├── cia/                  # CIA intelligence engine
│   ├── integrations/         # External API integrations
│   ├── database/            # Supabase schemas and queries
│   ├── notifications/       # Slack/Email for human-in-loop
│   └── web/                 # React dashboard interface
├── tests/                   # Test suites
└── docs/                    # Project documentation
```

### Desired Implementation Structure
```bash
# Files to be added for CIA system
src/
├── cia/
│   ├── __init__.py
│   ├── phase_engine.py              # Core 6-phase execution engine
│   ├── compressed_prompts.py        # Compressed prompt management
│   ├── master_archive.py            # Master Archive synthesis
│   ├── context_monitor.py           # Context window monitoring
│   ├── session_manager.py           # Session state and handovers
│   └── human_loop_coordinator.py    # Human-in-loop workflow coordination
├── integrations/
│   ├── __init__.py
│   ├── dataforseo.py               # DataForSEO API integration
│   ├── perplexity.py               # Perplexity API integration
│   ├── slack_notifier.py           # Slack notifications
│   └── email_notifier.py           # Email backup notifications
├── database/
│   ├── __init__.py
│   ├── supabase_client.py          # Supabase connection management
│   ├── cia_models.py               # Pydantic models for CIA data
│   ├── cia_repository.py           # Database operations for CIA
│   └── migrations/                 # Database schema migrations
└── notifications/
    ├── __init__.py
    ├── notification_service.py     # Unified notification service
    └── templates/                  # Notification templates
```

### Known Gotchas & Framework Requirements
```python
# CRITICAL: CIA System Requirements
# - Each phase MUST produce Master Archive before proceeding to preserve intelligence
# - Context usage monitoring required for handovers at 70% to prevent mid-analysis failures
# - Human-in-loop workflows MUST include both Slack AND Email notifications for redundancy
# - All customer psychology frameworks must be preserved (Benson 1-77+, Frank Kern, Priestley)
# - Phase 2A and 3A require MANDATORY human-in-loop pauses - cannot proceed without real data

# CRITICAL: Database Patterns
# - Use Supabase for all persistence (user's own account, NOT War Room shared account)
# - Row Level Security MUST be implemented for multi-tenant client data isolation
# - Master Archives stored separately from individual phase responses to prevent bloat
# - Session state must be recoverable across context limits with complete intelligence preservation

# CRITICAL: Integration Patterns  
# - DataForSEO credentials: eca1d1f1229a0603 / team@badaboostadgrants.org
# - All external API calls need retry logic with exponential backoff for reliability
# - Phase 2A requires DataForSEO keyword data, Phase 3A requires Perplexity trend research
# - Human-in-loop workflows must handle 30-minute timeout with graceful fallback

# CRITICAL: Context Window Management
# - Monitor token usage precisely to avoid mid-analysis failures that lose intelligence
# - Create handover documents automatically at 70% usage before hitting limits
# - Session state must be recoverable across context limits with zero data loss
# - Compressed prompts achieve 70-85% reduction while maintaining analytical depth

# CRITICAL: Framework Preservation Requirements
# - Benson Points 1-77+: Complete customer psychology framework must be extracted and preserved
# - Frank Kern Methodology: Narrative-driven customer journey analysis maintained
# - Daniel Priestley 5 P's: Authority building framework integration (Pitch, Publish, Product, Profile, Partnership)
# - Golden Hippo Methodology: Offer development and positioning frameworks
# - All intelligence must accumulate across phases with no framework degradation
```

## Implementation Blueprint

### Data Models and Structure
```python
# Core CIA data models ensuring type safety and intelligence preservation
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class PhaseStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing" 
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class HumanLoopType(Enum):
    DATAFORSEO_KEYWORDS = "dataforseo_keywords"
    PERPLEXITY_TRENDS = "perplexity_trends"
    TESTIMONIALS_REQUEST = "testimonials_request"

@dataclass
class CIASession:
    id: str
    client_id: str
    url: str
    company_name: str
    kpoi: str  # Key Person of Interest
    country: str
    testimonials_url: Optional[str]
    current_phase: str
    status: PhaseStatus
    context_usage: float
    session_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class PhaseResponse:
    id: str
    session_id: str
    phase_number: str
    response_data: Dict[str, Any]
    context_tokens_used: int
    execution_time_seconds: float
    requires_human_input: bool = False
    human_input_type: Optional[HumanLoopType] = None
    created_at: datetime

@dataclass
class MasterArchive:
    id: str
    session_id: str
    phase_number: str
    intelligence_summary: Dict[str, Any]
    customer_psychology: Dict[str, Any]  # Benson points 1-77+
    competitive_analysis: Dict[str, Any]
    authority_positioning: Dict[str, Any]  # Priestley 5 P's
    content_strategy: Dict[str, Any]
    frank_kern_insights: Dict[str, Any]  # Narrative psychology
    golden_hippo_framework: Dict[str, Any]  # Offer development
    created_at: datetime

@dataclass
class HumanLoopState:
    id: str
    session_id: str
    phase_number: str
    loop_type: HumanLoopType
    status: str  # "waiting", "completed", "timeout"
    notification_sent: bool
    slack_message_ts: Optional[str]
    email_sent: bool
    data_payload: Dict[str, Any]
    response_data: Optional[Dict[str, Any]]
    timeout_at: datetime
    created_at: datetime
```

### Implementation Tasks
```yaml
Task 1: [Database Schema and Models Setup]
CREATE src/database/supabase_schema.sql:
  - CREATE CIA session management tables with proper indexing
  - CREATE phase responses table with JSONB for flexible data storage
  - CREATE master archives table with intelligence preservation structure
  - CREATE human loop state table for workflow management
  - IMPLEMENT Row Level Security policies for client data isolation
  - CREATE indexes for performance optimization (session_id, phase_number, created_at)

CREATE src/database/cia_models.py:
  - DEFINE Pydantic models for all CIA data structures with validation
  - INCLUDE validation for intelligence quality requirements
  - PRESERVE customer psychology framework structure (Benson, Kern, Priestley)
  - IMPLEMENT serialization/deserialization for complex data types

CREATE src/database/cia_repository.py:
  - IMPLEMENT CRUD operations for all CIA entities
  - INCLUDE optimized queries for Master Archive retrieval
  - HANDLE session state persistence and recovery
  - IMPLEMENT client data isolation through RLS

Task 2: [Core CIA Phase Engine]
CREATE src/cia/phase_engine.py:
  - IMPLEMENT 6-phase execution pipeline with compressed prompts
  - INCLUDE context window monitoring at 70% usage threshold
  - ENSURE Master Archive synthesis between phases (1EB, 2EB, 3EB, etc.)
  - HANDLE human-in-loop workflow integration points
  - IMPLEMENT session state management across context limits
  - PRESERVE all intelligence frameworks through phase transitions

CREATE src/cia/compressed_prompts.py:
  - LOAD compressed prompts from database or configuration
  - IMPLEMENT prompt optimization for context efficiency (70-85% reduction)
  - MAINTAIN analytical depth while reducing token usage
  - INCLUDE prompt versioning and A/B testing capability

CREATE src/cia/master_archive.py:
  - IMPLEMENT intelligence synthesis algorithms
  - PRESERVE Benson points 1-77+ customer psychology framework
  - MAINTAIN Frank Kern narrative psychology insights
  - INTEGRATE Daniel Priestley authority building assessment
  - SYNTHESIZE competitive intelligence with actionable insights
  - CREATE comprehensive content strategy recommendations

Task 3: [Context Window Management]
CREATE src/cia/context_monitor.py:
  - IMPLEMENT precise token usage tracking across all operations
  - TRIGGER automatic handover creation at 70% usage threshold
  - INCLUDE context optimization algorithms for efficient usage
  - MONITOR cumulative context across all phases in session

CREATE src/cia/session_manager.py:
  - IMPLEMENT session state serialization and recovery
  - CREATE handover document generation with complete context preservation
  - HANDLE session resumption across context limits
  - ENSURE zero intelligence loss during handovers
  - IMPLEMENT session cleanup and optimization routines

Task 4: [Human-in-Loop Workflow System]
CREATE src/cia/human_loop_coordinator.py:
  - IMPLEMENT workflow coordination for Phase 2A (DataForSEO) and 3A (Perplexity)
  - HANDLE pause/resume logic with state preservation
  - COORDINATE multiple notification channels (Slack + Email)
  - IMPLEMENT timeout handling with graceful fallback
  - TRACK human response integration with validation

CREATE src/integrations/slack_notifier.py:
  - IMPLEMENT Slack webhook integration with rich message formatting
  - CREATE notification templates for different human-in-loop types
  - HANDLE interactive button responses for workflow continuation
  - INCLUDE error handling and retry logic for message delivery
  - IMPLEMENT thread management for ongoing conversations

CREATE src/integrations/email_notifier.py:
  - IMPLEMENT SMTP email backup notifications
  - CREATE HTML email templates with branding
  - HANDLE email delivery confirmation and tracking
  - IMPLEMENT fallback when Slack notifications fail
  - INCLUDE attachment support for handover documents

Task 5: [External API Integrations]
CREATE src/integrations/dataforseo.py:
  - IMPLEMENT DataForSEO API integration with authentication
  - HANDLE keyword research workflow for Phase 2A
  - INCLUDE rate limiting and error handling with exponential backoff
  - PROCESS keyword data for SEO intelligence synthesis
  - IMPLEMENT response caching for performance optimization

CREATE src/integrations/perplexity.py:
  - IMPLEMENT Perplexity API integration for trend research
  - HANDLE Phase 3A trend analysis workflow
  - PROCESS viral content and trending topic analysis
  - INCLUDE error handling and fallback strategies
  - IMPLEMENT result validation and quality scoring

Task 6: [Web Dashboard Interface]
CREATE src/web/components/CIADashboard.tsx:
  - IMPLEMENT real-time progress tracking through all 6 phases
  - DISPLAY Master Archive navigation and export functionality
  - HANDLE human-in-loop pause notifications with clear action items
  - INCLUDE session management with handover document access
  - IMPLEMENT performance monitoring and analytics display

CREATE src/web/components/PhaseProgress.tsx:
  - DISPLAY current phase execution with progress indicators
  - SHOW context usage monitoring with visual warnings
  - INCLUDE estimated completion times and next steps
  - HANDLE error states and recovery options
  - IMPLEMENT interactive controls for session management

CREATE src/web/components/MasterArchiveViewer.tsx:
  - DISPLAY comprehensive intelligence in organized sections
  - INCLUDE customer psychology framework visualization
  - SHOW competitive analysis with actionable insights
  - IMPLEMENT export functionality (PDF, JSON, etc.)
  - INCLUDE search and filtering capabilities for large archives
```

### Phase-Specific Implementation
```python
# Detailed implementation for each CIA phase with context management
async def execute_cia_phase_1a(session_id: str, url: str, company_name: str) -> PhaseResponse:
    """
    Phase 1A: Foundational Business Intelligence
    Uses compressed prompt with Benson framework integration
    """
    # PATTERN: Load compressed prompt (88% reduction achieved)
    prompt = await load_compressed_prompt("1A_foundational_business_intelligence")
    
    # PATTERN: Check context usage before execution
    current_usage = await monitor_context_usage()
    if current_usage > 0.7:
        handover = await create_handover_document(session_id, "1A")
        raise ContextLimitReached(f"Handover created: {handover['id']}")
    
    # PATTERN: Execute phase with web research and business analysis
    context = {
        "prompt": prompt,
        "company_url": url,
        "company_name": company_name,
        "benson_framework": "Extract all 77+ customer psychology points",
        "competitive_context": "Identify key competitors and positioning"
    }
    
    # Execute Claude analysis with comprehensive business intelligence
    response = await claude_analysis(context)
    
    # CRITICAL: Extract and validate Benson points preservation
    benson_points = extract_benson_framework(response)
    if len(benson_points) < 50:  # Quality threshold
        raise IntelligenceQualityError("Insufficient Benson points extracted")
    
    return PhaseResponse(
        session_id=session_id,
        phase_number="1A",
        response_data=response,
        context_tokens_used=estimate_token_usage(response),
        execution_time_seconds=await get_execution_time(),
        requires_human_input=False
    )

async def execute_cia_phase_2a(session_id: str, previous_archives: List[MasterArchive]) -> PhaseResponse:
    """
    Phase 2A: SEO Intelligence Analysis
    MANDATORY PAUSE for DataForSEO human-in-loop workflow
    """
    # PATTERN: Build context with ALL previous intelligence
    accumulated_intelligence = synthesize_previous_archives(previous_archives)
    
    # PATTERN: Load compressed prompt (60% reduction achieved)
    prompt = await load_compressed_prompt("2A_seo_intelligence")
    
    context = {
        "prompt": prompt,
        "previous_intelligence": accumulated_intelligence,
        "customer_psychology": accumulated_intelligence["customer_psychology"],
        "competitive_analysis": accumulated_intelligence["competitive_analysis"]
    }
    
    # Execute initial analysis to extract keywords for DataForSEO
    initial_response = await claude_analysis(context)
    keywords = extract_keywords_for_dataforseo(initial_response)
    
    # MANDATORY PAUSE: Send human-in-loop notification
    human_loop_state = await create_human_loop_state(
        session_id=session_id,
        phase_number="2A",
        loop_type=HumanLoopType.DATAFORSEO_KEYWORDS,
        data_payload={"keywords": keywords}
    )
    
    # Send notifications (Slack + Email)
    await send_slack_notification(
        session_id=session_id,
        message=f"Phase 2A requires DataForSEO lookup for keywords: {', '.join(keywords)}",
        action_buttons=["Continue with DataForSEO", "Skip Phase 2A"]
    )
    await send_email_notification(
        session_id=session_id,
        subject="CIA Phase 2A - DataForSEO Input Required",
        keywords=keywords
    )
    
    return PhaseResponse(
        session_id=session_id,
        phase_number="2A",
        response_data={"keywords_extracted": keywords, "initial_analysis": initial_response},
        context_tokens_used=estimate_token_usage(initial_response),
        execution_time_seconds=await get_execution_time(),
        requires_human_input=True,
        human_input_type=HumanLoopType.DATAFORSEO_KEYWORDS
    )

async def complete_cia_phase_2a(session_id: str, dataforseo_results: Dict[str, Any]) -> PhaseResponse:
    """
    Complete Phase 2A after receiving DataForSEO results
    """
    # Retrieve initial analysis and context
    initial_response = await get_phase_response(session_id, "2A")
    previous_archives = await get_previous_master_archives(session_id)
    
    # Build enhanced context with real keyword data
    enhanced_context = {
        "initial_analysis": initial_response.response_data["initial_analysis"],
        "dataforseo_results": dataforseo_results,
        "search_volumes": dataforseo_results.get("search_volume_data", {}),
        "serp_analysis": dataforseo_results.get("serp_data", {}),
        "competition_data": dataforseo_results.get("competition_analysis", {}),
        "previous_intelligence": synthesize_previous_archives(previous_archives)
    }
    
    # Complete SEO analysis with real data
    final_response = await claude_analysis_with_real_data(enhanced_context)
    
    return PhaseResponse(
        session_id=session_id,
        phase_number="2A_completed",
        response_data=final_response,
        context_tokens_used=estimate_token_usage(final_response),
        execution_time_seconds=await get_execution_time(),
        requires_human_input=False
    )

async def synthesize_master_archive_phase_1(session_id: str) -> MasterArchive:
    """
    Create Master Archive for Phase 1 (1EB) preserving all intelligence frameworks
    """
    # Retrieve all Phase 1 responses
    phase_responses = await get_phase_responses(session_id, ["1A", "1B", "1C", "1D"])
    
    # Extract and synthesize intelligence with framework preservation
    customer_psychology = synthesize_benson_framework(phase_responses)
    competitive_analysis = synthesize_competitive_intelligence(phase_responses)
    authority_positioning = synthesize_priestley_framework(phase_responses)
    frank_kern_insights = extract_narrative_psychology(phase_responses)
    
    # Create comprehensive intelligence summary
    intelligence_summary = {
        "business_foundation": extract_business_foundation(phase_responses),
        "market_positioning": extract_market_positioning(phase_responses),
        "competitive_advantages": identify_competitive_advantages(phase_responses),
        "growth_opportunities": identify_growth_opportunities(phase_responses),
        "strategic_priorities": prioritize_strategic_actions(phase_responses)
    }
    
    return MasterArchive(
        session_id=session_id,
        phase_number="1EB",
        intelligence_summary=intelligence_summary,
        customer_psychology=customer_psychology,
        competitive_analysis=competitive_analysis,
        authority_positioning=authority_positioning,
        content_strategy={},  # Will be populated in later phases
        frank_kern_insights=frank_kern_insights,
        golden_hippo_framework={},  # Will be populated in Phase 4
        created_at=datetime.now()
    )
```

### Integration Points
```yaml
DATABASE:
  - tables: cia_sessions, phase_responses, master_archives, human_loop_states
  - indexes: session_id, phase_number, client_id, created_at for performance
  - RLS: Client-specific data isolation with user-based policies
  - performance: Connection pooling, query optimization, read replicas
  
EXTERNAL_APIS:
  - DataForSEO: Keywords and SERP data for Phase 2A with rate limiting
  - Perplexity: Trend research integration for Phase 3A with caching
  - Slack: Human-in-loop notifications with interactive components
  - Email: SMTP backup notifications with HTML templates

INTERNAL_SERVICES:
  - Context Monitor: 70% usage tracking with automatic handover creation
  - Intelligence Synthesizer: Master Archive creation between phases
  - Session Manager: State persistence across context limits with recovery
  - Human Loop Coordinator: Workflow orchestration with timeout handling

FUTURE_INTEGRATIONS:
  - Cartwheel: Master Archives feed convergence detection algorithm
  - Adsby: Intelligence provides campaign targeting and optimization data
  - Analytics: Performance tracking integration for authority building metrics
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check src/ --fix           # Auto-fix Python formatting
mypy src/                       # Type checking for data model safety
pytest src/ --cov=src/ --cov-report=html  # Unit test coverage

# Expected: No errors, 90%+ test coverage. Fix issues before Level 2.
```

### Level 2: CIA Intelligence Quality Tests
```python
# CREATE comprehensive test suites for intelligence preservation:

def test_cia_phase_1_benson_framework_extraction():
    """Test that Phase 1 preserves all Benson customer psychology points"""
    session = create_test_session()
    response = await execute_cia_phase_1a(session.id, "https://test-company.com", "Test Company")
    
    benson_points = extract_benson_framework(response.response_data)
    assert len(benson_points) >= 50, "Insufficient Benson points extracted"
    assert "pain_points" in benson_points, "Pain points not identified"
    assert "false_solutions" in benson_points, "False solutions not identified"
    assert "success_myths" in benson_points, "Success myths not identified"

def test_master_archive_intelligence_preservation():
    """Test that Master Archives preserve all intelligence frameworks"""
    session = create_test_session()
    master_archive = await synthesize_master_archive_phase_1(session.id)
    
    # Validate all frameworks preserved
    assert master_archive.customer_psychology is not None
    assert master_archive.competitive_analysis is not None
    assert master_archive.authority_positioning is not None
    assert master_archive.frank_kern_insights is not None
    
    # Validate framework completeness
    assert len(master_archive.customer_psychology) >= 10, "Customer psychology incomplete"
    assert "priestley_5ps" in master_archive.authority_positioning, "Priestley framework missing"

def test_context_window_handover_creation():
    """Test automatic handover creation at 70% context usage"""
    session = create_test_session()
    
    # Mock high context usage
    mock_context_usage(0.75)
    
    with pytest.raises(ContextLimitReached) as exc_info:
        await execute_cia_phase_1a(session.id, "https://test-company.com", "Test Company")
    
    # Validate handover document created
    handover = get_handover_document(exc_info.value.handover_id)
    assert handover is not None
    assert handover["session_id"] == session.id
    assert handover["current_phase"] == "1A"
    assert "critical_state" in handover

def test_human_loop_dataforseo_workflow():
    """Test Phase 2A human-in-loop workflow for DataForSEO integration"""
    session = create_test_session()
    previous_archives = [create_test_master_archive()]
    
    response = await execute_cia_phase_2a(session.id, previous_archives)
    
    assert response.requires_human_input is True
    assert response.human_input_type == HumanLoopType.DATAFORSEO_KEYWORDS
    assert "keywords_extracted" in response.response_data
    
    # Validate notifications sent
    notifications = get_test_notifications()
    assert len(notifications) == 2  # Slack + Email
    assert "dataforseo" in notifications[0].content.lower()
```

```bash
# Run and iterate until passing:
pytest tests/cia/ -v --cov=src/cia/
# Target: 95% coverage, all intelligence framework tests passing
```

### Level 3: Integration and Performance Tests
```bash
# Test complete CIA pipeline with external integrations
python -m pytest tests/integration/test_cia_complete_pipeline.py

# Test Supabase connection and RLS policies
python -m pytest tests/integration/test_supabase_cia_storage.py

# Test human-in-loop notification delivery
python -m pytest tests/integration/test_human_loop_notifications.py

# Test context window management and handovers
python -m pytest tests/integration/test_context_management.py

# Test DataForSEO and Perplexity API integrations
python -m pytest tests/integration/test_external_apis.py

# Expected: All integrations working, no API failures, proper error handling
```

### Level 4: Performance and Scale Testing
```bash
# Test performance requirements
python -m pytest tests/performance/test_cia_performance.py
# Target: <3 minutes per phase (excluding human pauses)

# Test concurrent session handling
python -m pytest tests/performance/test_concurrent_sessions.py
# Target: Handle 5 concurrent CIA sessions

# Test context usage optimization
python -m pytest tests/performance/test_context_optimization.py
# Target: 70-85% prompt compression achieved, <70% usage per phase
```

## Final Validation Checklist
- [ ] All 6 CIA phases execute successfully: `pytest tests/test_cia_complete.py`
- [ ] Context management triggers handovers at 70%: Manual test with context monitoring
- [ ] Human-in-loop notifications delivered reliably: Test Slack + Email delivery
- [ ] Master Archives preserve all intelligence frameworks: Validate Benson/Kern/Priestley retention
- [ ] Supabase integration functional: Test data persistence and RLS policies
- [ ] DataForSEO integration working: Test Phase 2A workflow with real API
- [ ] Perplexity integration functional: Test Phase 3A workflow
- [ ] Performance requirements met: <3 minute phases, <70% context usage
- [ ] Session recovery across context limits: Test handover and resumption
- [ ] Intelligence quality maintained: Validate framework preservation across phases

## Anti-Patterns to Avoid
- ❌ Don't create new customer psychology frameworks - use existing Benson/Kern/Priestley
- ❌ Don't skip Master Archive creation - intelligence preservation is critical
- ❌ Don't ignore context usage monitoring - handovers prevent analysis failures
- ❌ Don't bypass human-in-loop workflows - they provide essential real-time data
- ❌ Don't use shared/War Room Supabase - must be user's own account
- ❌ Don't design for 100% context usage - design for 70% handover threshold
- ❌ Don't skip phase dependencies - each phase requires previous Master Archives
- ❌ Don't compress prompts beyond recognition - maintain analytical depth
- ❌ Don't lose intelligence between phases - Master Archives are the continuity mechanism
