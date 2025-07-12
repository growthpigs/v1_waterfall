name: "Project Waterfall CIA PRP Template"
description: |
  Optimized for implementing CIA (Central Intelligence Arsenal) features with comprehensive context and validation loops for Project Waterfall system.

## Core Principles
1. **CIA Intelligence Focus**: All features must support the 6-phase intelligence pipeline
2. **Context Management**: Design for 70% usage handovers and session continuity  
3. **Human-in-Loop**: Include Slack/Email notification workflows where needed
4. **Master Archives**: Preserve intelligence synthesis between phases
5. **Framework Integration**: Maintain Benson points, Frank Kern, Priestley methodologies

---

## Goal
[What needs to be built - specific CIA component or supporting system]

## Why
- [Business intelligence value and Project Waterfall integration]
- [CIA pipeline enhancement or foundation requirement]
- [Automation capability this enables]

## What
[User-visible behavior and technical requirements for CIA system]

### Success Criteria
- [ ] [Specific measurable outcomes for CIA intelligence quality]
- [ ] [Performance requirements (context usage, response time)]
- [ ] [Integration requirements (Supabase, DataForSEO, etc.)]

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- doc: CIA Framework Documentation
  sections: [Compressed prompts, Benson points 1-77+, Frank Kern methodology]
  critical: [Customer psychology frameworks, authority building patterns]
  
- doc: DataForSEO API Documentation  
  url: https://docs.dataforseo.com/
  sections: [Keywords API, SERP API, authentication]
  critical: [Rate limiting, response formats, error handling]

- doc: Supabase Documentation
  url: https://docs.supabase.com/
  sections: [Database, Auth, Real-time subscriptions]
  critical: [Row Level Security, performance optimization]

- doc: Slack API Documentation
  url: https://api.slack.com/
  sections: [Web API, Webhooks, message formatting]
  critical: [Human-in-loop notification patterns]

- file: examples/cia_phase_structure.py
  why: [Phase execution patterns, context management]
  
- file: examples/human_in_loop_workflow.py  
  why: [Notification patterns, pause/resume logic]

- file: examples/master_archive_synthesis.py
  why: [Intelligence synthesis patterns between phases]
```

### Current Codebase Structure
```bash
# Run `tree` in project root to get overview
V1_Waterfall/
├── .claude/                    # Context engineering framework
├── PRPs/                      # Product Requirements Prompts  
├── examples/                  # Implementation patterns
├── src/
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
# Files to be added for this feature
[Add specific file structure based on feature requirements]
```

### Known Gotchas & Framework Requirements
```python
# CRITICAL: CIA System Requirements
# - Each phase MUST produce Master Archive before proceeding
# - Context usage monitoring required for handovers at 70%
# - Human-in-loop workflows MUST include Slack AND Email notifications
# - All customer psychology frameworks must be preserved (Benson 1-77+)

# CRITICAL: Database Patterns
# - Use Supabase for all persistence (user's account, NOT War Room)
# - Consider Pinecone for RAG if performance requires vector search
# - Master Archives stored separately from individual phase responses

# CRITICAL: Integration Patterns  
# - DataForSEO credentials: eca1d1f1229a0603 / team@badaboostadgrants.org
# - All external API calls need retry logic with exponential backoff
# - Phase 2A and 3A require mandatory human-in-loop pauses

# CRITICAL: Context Window Management
# - Monitor token usage precisely to avoid mid-analysis failures
# - Create handover documents automatically at 70% usage
# - Session state must be recoverable across context limits
```

## Implementation Blueprint

### Data Models and Structure
```python
# Core CIA data models ensuring type safety and intelligence preservation
# Examples:
# - cia_session: Session state and progress tracking
# - phase_response: Individual phase outputs  
# - master_archive: Synthesized intelligence between phases
# - human_loop_state: Pause/resume state for notifications
```

### Implementation Tasks
```yaml
Task 1: [Database Schema Setup]
MODIFY src/database/supabase_schema.sql:
  - CREATE tables for CIA session management
  - CREATE tables for phase responses and Master Archives
  - CREATE indexes for performance optimization
  - ENSURE Row Level Security configured

CREATE src/database/cia_models.py:
  - DEFINE Pydantic models for all CIA data structures
  - INCLUDE validation for intelligence quality requirements
  - PRESERVE customer psychology framework structure

Task 2: [CIA Phase Engine]
CREATE src/cia/phase_engine.py:
  - IMPLEMENT 6-phase execution pipeline
  - INCLUDE context window monitoring at 70% usage
  - ENSURE Master Archive synthesis between phases
  - HANDLE human-in-loop workflow integration

Task 3: [Human-in-Loop Notifications]
CREATE src/notifications/human_loop.py:
  - IMPLEMENT Slack notification service
  - IMPLEMENT Email backup notifications  
  - HANDLE pause/resume workflow for Phase 2A and 3A
  - ENSURE notification templates for different pause types

[Continue with specific tasks based on feature requirements...]
```

### Phase-Specific Pseudocode
```python
# Example for CIA Phase execution with context management
async def execute_cia_phase(phase_num: int, session_id: str, previous_archives: List[MasterArchive]) -> PhaseResult:
    # PATTERN: Load compressed prompts from database
    prompt = await load_compressed_prompt(phase_num)
    
    # PATTERN: Check context usage before execution
    current_usage = monitor_context_usage()
    if current_usage > 0.7:
        await create_handover_document(session_id, phase_num)
        raise ContextLimitReached("Handover created, resume in new session")
    
    # PATTERN: Execute phase with all previous intelligence
    context = build_phase_context(prompt, previous_archives)
    
    # GOTCHA: Phase 2A and 3A require human-in-loop pauses
    if phase_num == "2A":
        keywords = await extract_keywords_for_dataforseo(context)
        await send_human_loop_notification(session_id, "dataforseo", keywords)
        return await wait_for_human_input(session_id, "dataforseo_results")
    
    # PATTERN: Execute standard phase analysis
    response = await claude_analysis(context)
    
    # PATTERN: Create Master Archive at phase completion
    if is_phase_boundary(phase_num):
        archive = await synthesize_master_archive(session_id, phase_num)
        await store_master_archive(session_id, archive)
        
    return PhaseResult(response=response, archive=archive)
```

### Integration Points
```yaml
DATABASE:
  - tables: cia_sessions, phase_responses, master_archives, human_loop_states
  - indexes: session_id, phase_num, created_at for performance
  - RLS: User-specific data isolation
  
EXTERNAL_APIS:
  - DataForSEO: Keywords and SERP data for Phase 2A
  - Slack: Human-in-loop notifications with custom templates
  - Email: Backup notifications for human-in-loop workflows
  - Perplexity: Trend research integration for Phase 3A

INTERNAL_SERVICES:
  - Context Monitor: 70% usage tracking with handover creation
  - Intelligence Synthesizer: Master Archive creation between phases
  - Session Manager: State persistence across context limits
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check src/ --fix           # Auto-fix Python formatting
mypy src/                       # Type checking
eslint src/web/ --fix          # JavaScript/React linting

# Expected: No errors. If errors exist, READ and fix before proceeding.
```

### Level 2: Unit Tests
```python
# CREATE comprehensive test suites following CIA requirements:

def test_cia_phase_execution():
    """Test complete phase execution with context monitoring"""
    session = create_test_session()
    result = await execute_cia_phase(1, session.id, [])
    assert result.master_archive is not None
    assert result.context_usage < 0.7

def test_human_loop_workflow():
    """Test human-in-loop notifications and pause/resume"""
    session = create_test_session()
    await execute_cia_phase("2A", session.id, [])
    notifications = get_test_notifications()
    assert len(notifications) == 2  # Slack + Email
    assert "dataforseo" in notifications[0].content

def test_master_archive_synthesis():
    """Test intelligence preservation between phases"""
    archives = create_test_archives([1, 2])
    synthesis = await synthesize_master_archive(session_id, 3)
    assert all_benson_points_preserved(synthesis)
    assert customer_psychology_intact(synthesis)
```

```bash
# Run and iterate until passing:
pytest tests/ -v --cov=src/
# Target: 90% coverage, all tests passing
```

### Level 3: Integration Tests
```bash
# Test complete CIA pipeline with external integrations
python -m pytest tests/integration/test_cia_pipeline.py

# Test Supabase connection and data persistence
python -m pytest tests/integration/test_database.py

# Test human-in-loop notification delivery
python -m pytest tests/integration/test_notifications.py

# Expected: All integrations working, no external API failures
```

## Final Validation Checklist
- [ ] All 6 CIA phases execute successfully: `pytest tests/test_cia_complete.py`
- [ ] Context management works: Manual test of 70% handover creation
- [ ] Human-in-loop notifications delivered: Test Slack + Email delivery
- [ ] Master Archives preserve intelligence: Validate Benson points retention
- [ ] Supabase integration working: Test data persistence and retrieval
- [ ] DataForSEO integration functional: Test Phase 2A workflow
- [ ] Performance requirements met: <3 minute phases, <70% context usage

---

## Anti-Patterns to Avoid
- ❌ Don't create new customer psychology frameworks - use existing Benson/Kern
- ❌ Don't skip Master Archive creation - intelligence MUST be preserved
- ❌ Don't ignore context usage monitoring - handovers are critical
- ❌ Don't bypass human-in-loop workflows - they provide essential real-time data
- ❌ Don't use War Room Supabase connection - must be user's own account
- ❌ Don't design for 100% context usage - design for 70% handovers
- ❌ Don't skip phase dependencies - each phase needs previous Master Archives