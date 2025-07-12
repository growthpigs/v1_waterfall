# Example Implementation Patterns for CIA System

This directory contains example code patterns that should be followed when implementing Project Waterfall CIA features.

## Core Patterns

### CIA Phase Structure (`cia_phase_structure.py`)
- Phase execution with context monitoring
- Master Archive synthesis between phases
- Session state management across context limits
- Error handling and recovery patterns

### Human-in-Loop Workflows (`human_in_loop_workflow.py`)
- Slack notification integration
- Email backup notifications
- Pause/resume logic for Phase 2A (DataForSEO) and 3A (Perplexity)
- Notification templates and formatting

### Supabase Integration (`supabase_intelligence_storage.py`)
- Database schema for CIA sessions and responses
- Master Archive storage and retrieval
- Performance optimization patterns
- Row Level Security implementation

### Context Management (`context_handover_system.py`)
- 70% usage monitoring and automatic handover creation
- Session continuity across context limits
- State serialization and recovery
- Handover document generation

### DataForSEO Integration (`dataforseo_integration.py`)
- API authentication and rate limiting
- Keyword processing workflow for Phase 2A
- Error handling and retry logic
- Response parsing and validation

### Frontend Dashboard (`react_cia_dashboard.tsx`)
- React component patterns for CIA analysis interface
- Real-time progress tracking through phases
- Human-in-loop pause notifications
- Master Archive viewing and export

### Master Archive Synthesis (`master_archive_synthesis.py`)
- Intelligence synthesis patterns between phases
- Benson points framework preservation
- Customer psychology data structure maintenance
- Archive quality validation

## Usage Guidelines

1. **Don't Copy Directly**: These are patterns and structures to follow, not code to copy
2. **Adapt for CIA**: Modify patterns to fit specific CIA intelligence requirements
3. **Maintain Frameworks**: Ensure all customer psychology frameworks are preserved
4. **Follow Validation**: Use the validation patterns for quality assurance
5. **Consider Context**: Always design with context window management in mind

## Framework Requirements

All implementations must maintain:
- **Benson Points 1-77+**: Complete customer psychology framework
- **Frank Kern Methodology**: Narrative-driven customer journey analysis
- **Daniel Priestley 5 P's**: Authority building framework integration
- **Golden Hippo Methodology**: Offer development and positioning
- **Context Engineering**: Proper handover and session management