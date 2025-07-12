# Brand BOS - Phase 1: CIA System Foundation Development Plan

## Executive Summary
**Phase Duration:** Weeks 1-4 (20 development days)
**Complexity:** 4/5 (Architectural complexity with context management)
**Time Required:** 4/5 (160-200 hours total implementation)
**Confidence:** 4/5 (Well-defined requirements with some integration uncertainties)

## System Overview
The CIA (Central Intelligence Arsenal) is a 6-phase business intelligence pipeline that transforms any URL into comprehensive marketing intelligence. It features advanced context window management, human-in-loop workflows, and systematic preservation of customer psychology frameworks.

## Directory Structure & File Organization

### Week 1: Foundation Setup (Days 1-5)
```
src/
├── __init__.py
├── config/
│   ├── __init__.py
│   ├── settings.py                  # Environment configuration
│   └── constants.py                 # CIA phases, thresholds
├── database/
│   ├── __init__.py
│   ├── supabase_client.py          # Database connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cia_session.py          # Session data model
│   │   ├── phase_response.py       # Phase execution results
│   │   ├── master_archive.py       # Intelligence preservation
│   │   └── human_loop_state.py     # Human workflow tracking
│   └── repositories/
│       ├── __init__.py
│       ├── session_repository.py    # Session CRUD operations
│       └── archive_repository.py    # Archive management
└── tests/
    ├── __init__.py
    └── test_database_setup.py
```

### Week 2: Core CIA Engine (Days 6-10)
```
src/
├── cia/
│   ├── __init__.py
│   ├── phase_engine.py              # Core 6-phase execution
│   ├── compressed_prompts.py        # 70-85% prompt compression
│   ├── master_archive.py            # Intelligence synthesis
│   ├── context_monitor.py           # Token usage tracking
│   ├── session_manager.py           # State persistence
│   └── intelligence_extractor.py    # Framework extraction
├── prompts/
│   ├── __init__.py
│   ├── phase_1a.py                 # Foundational Intelligence
│   ├── phase_1b.py                 # DNA & ICP Discovery
│   ├── phase_1c.py                 # KPI Assessment
│   ├── phase_1d.py                 # Competitive Intelligence
│   ├── phase_1eb.py                # Master Archive 1
│   └── [additional phase prompts...]
└── tests/
    ├── test_phase_engine.py
    └── test_context_monitor.py
```

### Week 3: Human-in-Loop & Integrations (Days 11-15)
```
src/
├── integrations/
│   ├── __init__.py
│   ├── dataforseo/
│   │   ├── __init__.py
│   │   ├── client.py               # API client wrapper
│   │   ├── keyword_extractor.py    # Keyword extraction logic
│   │   └── serp_analyzer.py        # SERP data processing
│   ├── perplexity/
│   │   ├── __init__.py
│   │   ├── client.py               # Perplexity API wrapper
│   │   └── trend_analyzer.py       # Trend extraction
│   └── anthropic/
│       ├── __init__.py
│       └── claude_client.py        # Claude API integration
├── notifications/
│   ├── __init__.py
│   ├── notification_service.py     # Unified notification layer
│   ├── slack/
│   │   ├── __init__.py
│   │   ├── slack_client.py         # Slack webhook integration
│   │   └── templates.py            # Message templates
│   ├── email/
│   │   ├── __init__.py
│   │   ├── smtp_client.py          # Email service
│   │   └── templates.py            # Email templates
│   └── human_loop_manager.py       # Workflow coordination
└── tests/
    ├── test_integrations.py
    └── test_notifications.py
```

### Week 4: Session Management & Testing (Days 16-20)
```
src/
├── cia/
│   ├── handover_manager.py         # Context limit handovers
│   └── validation/
│       ├── __init__.py
│       ├── framework_validator.py   # Benson/Kern/Priestley
│       └── quality_checker.py       # Output validation
├── api/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── cia_router.py           # CIA endpoints
│   │   └── human_loop_router.py    # Human input endpoints
│   └── dependencies.py             # Shared dependencies
├── migrations/
│   ├── 001_initial_schema.sql
│   ├── 002_row_level_security.sql
│   └── 003_indexes.sql
└── tests/
    ├── test_end_to_end.py
    ├── test_handover_recovery.py
    └── test_framework_preservation.py
```

## Implementation Order & Dependencies

### Week 1: Foundation (Days 1-5)
**Day 1-2: Environment & Database Setup**
- Complexity: 2/5, Time: 2/5 (4-6 hours)
- Set up Python environment with Poetry/pip
- Configure Supabase connection
- Create initial database schemas
- Implement Row Level Security policies

**Day 3-4: Core Data Models**
- Complexity: 2/5, Time: 2/5 (6-8 hours)
- Implement Pydantic models for all entities
- Create repository pattern for database operations
- Set up model validation and serialization
- Write unit tests for models

**Day 5: Configuration Management**
- Complexity: 1/5, Time: 1/5 (3-4 hours)
- Environment variable management
- CIA phase definitions and constants
- Logging configuration
- Error handling setup

### Week 2: CIA Engine Core (Days 6-10)
**Day 6-7: Phase Engine Foundation**
- Complexity: 4/5, Time: 3/5 (10-12 hours)
- Implement phase execution orchestrator
- Create phase state management
- Build error recovery mechanisms
- Set up phase boundary detection

**Day 8: Compressed Prompts System**
- Complexity: 3/5, Time: 2/5 (6-8 hours)
- Implement prompt compression algorithms
- Create prompt template management
- Validate 70-85% compression targets
- Build prompt injection system

**Day 9: Context Monitoring**
- Complexity: 4/5, Time: 3/5 (8-10 hours)
- Implement token counting system
- Create 70% threshold detection
- Build automatic handover triggers
- Develop usage statistics tracking

**Day 10: Master Archive Synthesis**
- Complexity: 5/5, Time: 3/5 (10-12 hours)
- Implement intelligence extraction
- Create framework preservation logic
- Build cumulative synthesis algorithms
- Validate framework integrity

### Week 3: Integrations & Human-in-Loop (Days 11-15)
**Day 11-12: External API Integrations**
- Complexity: 3/5, Time: 3/5 (10-12 hours)
- Implement DataForSEO client
- Create Perplexity integration
- Add retry logic and rate limiting
- Build response parsing and validation

**Day 13: Notification Services**
- Complexity: 2/5, Time: 2/5 (6-8 hours)
- Implement Slack webhook integration
- Create email SMTP service
- Build notification templates
- Add delivery confirmation tracking

**Day 14-15: Human Loop Coordination**
- Complexity: 4/5, Time: 3/5 (10-12 hours)
- Create pause/resume workflow logic
- Implement timeout handling (30 min)
- Build response validation
- Create fallback mechanisms

### Week 4: Integration & Quality Assurance (Days 16-20)
**Day 16-17: Session Management & Handovers**
- Complexity: 4/5, Time: 3/5 (10-12 hours)
- Implement session state serialization
- Create handover document generation
- Build session recovery logic
- Test cross-context continuity

**Day 18: API Development**
- Complexity: 2/5, Time: 2/5 (6-8 hours)
- Create FastAPI application structure
- Implement CIA execution endpoints
- Add human input endpoints
- Build API documentation

**Day 19-20: Testing & Validation**
- Complexity: 3/5, Time: 3/5 (10-12 hours)
- End-to-end workflow testing
- Framework preservation validation
- Performance benchmarking
- 95% test coverage achievement

## Technical Specifications

### Core Dependencies
```python
# requirements.txt
fastapi==0.104.1
pydantic==2.5.0
supabase==2.0.3
anthropic==0.11.0
aiohttp==3.9.1
redis==5.0.1
pytest==7.4.3
pytest-asyncio==0.21.1
python-dotenv==1.0.0
tenacity==8.2.3  # For retry logic
croniter==2.0.1  # For scheduled tasks
```

### Performance Requirements
- **Phase Execution:** <3 minutes per phase (excluding human pauses)
- **Context Usage:** <70% per phase with automatic handover
- **API Response:** <500ms for status checks
- **Database Queries:** <100ms for standard operations
- **Notification Delivery:** <5 seconds for Slack/Email

### Security Requirements
- **Multi-tenant Isolation:** Supabase RLS on all tables
- **API Authentication:** JWT tokens with refresh
- **Credential Management:** Environment variables only
- **Data Encryption:** TLS for all external communications
- **Audit Logging:** All phase executions and data access

## Risk Mitigation Strategies

### Technical Risks
1. **Context Window Overflow**
   - Mitigation: Aggressive prompt compression, early handover triggers
   - Fallback: Manual phase splitting if compression insufficient

2. **API Rate Limiting**
   - Mitigation: Exponential backoff, request queuing
   - Fallback: Manual data input workflow for affected phases

3. **Framework Degradation**
   - Mitigation: Explicit validation after each phase
   - Fallback: Framework reinforcement prompts if degradation detected

### Integration Risks
1. **DataForSEO API Changes**
   - Mitigation: Version locking, response validation
   - Fallback: Manual keyword research workflow

2. **Notification Delivery Failures**
   - Mitigation: Dual channel (Slack + Email)
   - Fallback: Database polling for pending workflows

## Success Metrics
- [ ] All 6 CIA phases execute with <3 minute completion
- [ ] Context usage stays below 70% with successful handovers
- [ ] 100% framework preservation across all phases
- [ ] Human-in-loop notifications delivered within 5 seconds
- [ ] Session recovery works across context limits
- [ ] 95% test coverage achieved
- [ ] Zero data leakage between clients (RLS validation)

## Development Tools & Environment
```bash
# Development setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Environment variables (.env)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
ANTHROPIC_API_KEY=your_claude_key
DATAFORSEO_LOGIN=eca1d1f1229a0603
DATAFORSEO_PASSWORD=team@badaboostadgrants.org
SLACK_WEBHOOK_URL=your_webhook_url
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=notifications@modernfoundry.com
SMTP_PASSWORD=your_app_password
REDIS_URL=redis://localhost:6379

# Testing
pytest tests/ -v --cov=src --cov-report=html
```

## Next Steps After Phase 1
1. **Week 5:** Begin Cartwheel integration planning
2. **Week 6:** Implement convergence detection engine
3. **Week 7:** Build content multiplication pipeline
4. **Week 8:** Create publishing automation workflows

---

**Total Estimated Effort:** 160-200 hours over 4 weeks
**Critical Path:** Database → Models → Phase Engine → Context Monitor → Integrations → Testing

This plan provides a systematic approach to building the CIA System Foundation with clear dependencies, risk mitigation, and success criteria. The modular structure allows for parallel development where possible while maintaining architectural integrity.