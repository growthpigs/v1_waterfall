-- Brand BOS CIA System - Initial Schema Migration
-- Creates all tables for CIA intelligence pipeline

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create client_id type for multi-tenant isolation
CREATE TYPE phase_status AS ENUM (
    'pending',
    'executing',
    'paused',
    'completed',
    'failed',
    'handover_required'
);

CREATE TYPE human_loop_type AS ENUM (
    'dataforseo_keywords',
    'perplexity_trends',
    'testimonials_request',
    'context_handover'
);

-- CIA Sessions table
CREATE TABLE IF NOT EXISTS cia_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL,
    
    -- Business information
    url TEXT NOT NULL,
    company_name TEXT NOT NULL,
    kpoi TEXT NOT NULL,
    country TEXT NOT NULL,
    testimonials_url TEXT,
    
    -- Session state
    status phase_status NOT NULL DEFAULT 'pending',
    current_phase TEXT,
    completed_phases TEXT[] DEFAULT '{}',
    failed_phases TEXT[] DEFAULT '{}',
    
    -- Progress tracking
    total_phases INTEGER DEFAULT 15,
    progress_percentage DECIMAL(5,2) DEFAULT 0.0,
    
    -- Context management
    total_tokens_used INTEGER DEFAULT 0,
    handover_count INTEGER DEFAULT 0,
    last_handover_at TIMESTAMPTZ,
    
    -- Timing
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    paused_at TIMESTAMPTZ,
    
    -- Human-in-loop tracking
    human_inputs_pending TEXT[] DEFAULT '{}',
    human_inputs_completed TEXT[] DEFAULT '{}',
    
    -- Configuration
    auto_resume BOOLEAN DEFAULT true,
    notification_channels TEXT[] DEFAULT '{slack,email}',
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    
    -- Indexes
    CONSTRAINT cia_sessions_client_id_key INDEX (client_id),
    CONSTRAINT cia_sessions_status_key INDEX (status),
    CONSTRAINT cia_sessions_created_at_key INDEX (created_at DESC)
);

-- Phase Responses table
CREATE TABLE IF NOT EXISTS phase_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL,
    session_id UUID NOT NULL REFERENCES cia_sessions(id) ON DELETE CASCADE,
    phase_id TEXT NOT NULL,
    
    -- Execution details
    prompt_used TEXT NOT NULL,
    response_content JSONB NOT NULL DEFAULT '{}',
    
    -- Framework extraction
    extracted_frameworks JSONB DEFAULT '{}',
    
    -- Token tracking
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    response_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    context_usage_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    
    -- Status tracking
    status phase_status NOT NULL DEFAULT 'pending',
    attempt_number INTEGER DEFAULT 1,
    
    -- Timing
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds DECIMAL(10,2),
    
    -- Human-in-loop
    requires_human_input BOOLEAN DEFAULT false,
    human_input_type TEXT,
    human_input_received_at TIMESTAMPTZ,
    human_input_data JSONB,
    
    -- Error tracking
    error_message TEXT,
    error_details JSONB,
    
    -- Quality metrics
    framework_preservation_score DECIMAL(3,2),
    response_quality_score DECIMAL(3,2),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    
    -- Indexes
    CONSTRAINT phase_responses_session_phase_key UNIQUE (session_id, phase_id, attempt_number),
    CONSTRAINT phase_responses_client_id_key INDEX (client_id),
    CONSTRAINT phase_responses_session_id_key INDEX (session_id)
);

-- Master Archives table
CREATE TABLE IF NOT EXISTS master_archives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL,
    session_id UUID NOT NULL REFERENCES cia_sessions(id) ON DELETE CASCADE,
    phase_number TEXT NOT NULL,
    
    -- Core intelligence synthesis
    intelligence_summary JSONB NOT NULL DEFAULT '{}',
    
    -- Framework preservation
    customer_psychology JSONB NOT NULL DEFAULT '{}',
    competitive_analysis JSONB NOT NULL DEFAULT '{}',
    authority_positioning JSONB NOT NULL DEFAULT '{}',
    content_strategy JSONB NOT NULL DEFAULT '{}',
    
    -- Token tracking
    context_tokens_used INTEGER NOT NULL DEFAULT 0,
    phases_included TEXT[] NOT NULL DEFAULT '{}',
    
    -- Quality metrics
    framework_integrity_scores JSONB DEFAULT '{}',
    synthesis_quality_score DECIMAL(3,2) DEFAULT 0.0,
    
    -- Intelligence metrics
    insights_count INTEGER DEFAULT 0,
    opportunities_identified INTEGER DEFAULT 0,
    implementation_priorities JSONB DEFAULT '[]',
    
    -- Chain tracking
    previous_archive_id UUID,
    archive_version INTEGER DEFAULT 1,
    
    -- Validation
    validated_at TIMESTAMPTZ,
    validation_notes TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    
    -- Indexes
    CONSTRAINT master_archives_client_id_key INDEX (client_id),
    CONSTRAINT master_archives_session_id_key INDEX (session_id),
    CONSTRAINT master_archives_version_key INDEX (session_id, archive_version)
);

-- Human Loop States table
CREATE TABLE IF NOT EXISTS human_loop_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL,
    session_id UUID NOT NULL REFERENCES cia_sessions(id) ON DELETE CASCADE,
    phase_id TEXT NOT NULL,
    loop_type human_loop_type NOT NULL,
    
    -- Request details
    request_data JSONB NOT NULL DEFAULT '{}',
    request_message TEXT NOT NULL,
    
    -- Notification settings
    notification_channels TEXT[] DEFAULT '{slack,email}',
    notification_recipients TEXT[] DEFAULT '{}',
    
    -- Status tracking
    status TEXT DEFAULT 'waiting',
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    responded_at TIMESTAMPTZ,
    expired_at TIMESTAMPTZ,
    
    -- Response tracking
    response_data JSONB,
    response_validated BOOLEAN DEFAULT false,
    validation_errors TEXT[],
    
    -- Notification tracking
    notifications_sent JSONB DEFAULT '{}',
    notification_errors JSONB DEFAULT '{}',
    
    -- Retry tracking
    retry_count INTEGER DEFAULT 0,
    last_retry_at TIMESTAMPTZ,
    
    -- Timeout configuration
    timeout_minutes INTEGER DEFAULT 30,
    reminder_sent BOOLEAN DEFAULT false,
    reminder_sent_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    
    -- Indexes
    CONSTRAINT human_loop_states_client_id_key INDEX (client_id),
    CONSTRAINT human_loop_states_session_id_key INDEX (session_id),
    CONSTRAINT human_loop_states_status_key INDEX (status)
);

-- Context Handovers table
CREATE TABLE IF NOT EXISTS context_handovers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL,
    session_id UUID NOT NULL REFERENCES cia_sessions(id) ON DELETE CASCADE,
    current_phase TEXT NOT NULL,
    
    -- Context state
    context_usage_percentage DECIMAL(5,2) NOT NULL,
    total_tokens_used INTEGER NOT NULL,
    
    -- Session state
    completed_phases TEXT[] NOT NULL DEFAULT '{}',
    pending_phases TEXT[] NOT NULL DEFAULT '{}',
    
    -- Critical state for resumption
    critical_state JSONB NOT NULL DEFAULT '{}',
    next_action TEXT NOT NULL,
    
    -- Archive references
    latest_archive_id UUID,
    preserved_archives UUID[] DEFAULT '{}',
    
    -- Intelligence summary
    intelligence_summary JSONB DEFAULT '{}',
    framework_status JSONB DEFAULT '{}',
    
    -- Human-in-loop state
    pending_human_inputs JSONB DEFAULT '[]',
    
    -- Recovery instructions
    recovery_instructions JSONB DEFAULT '{}',
    handover_notes TEXT,
    
    -- Usage tracking
    handover_number INTEGER DEFAULT 1,
    previous_handover_id UUID,
    
    -- Recovery status
    recovered BOOLEAN DEFAULT false,
    recovered_at TIMESTAMPTZ,
    recovery_session_id UUID,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    
    -- Indexes
    CONSTRAINT context_handovers_client_id_key INDEX (client_id),
    CONSTRAINT context_handovers_session_id_key INDEX (session_id),
    CONSTRAINT context_handovers_recovered_key INDEX (recovered)
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to all tables
CREATE TRIGGER update_cia_sessions_updated_at BEFORE UPDATE ON cia_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_phase_responses_updated_at BEFORE UPDATE ON phase_responses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_master_archives_updated_at BEFORE UPDATE ON master_archives 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_human_loop_states_updated_at BEFORE UPDATE ON human_loop_states 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_context_handovers_updated_at BEFORE UPDATE ON context_handovers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE cia_sessions IS 'Main CIA analysis sessions tracking business intelligence pipeline execution';
COMMENT ON TABLE phase_responses IS 'Individual phase execution results with token tracking and framework extraction';
COMMENT ON TABLE master_archives IS 'Intelligence synthesis archives preserving frameworks between phases';
COMMENT ON TABLE human_loop_states IS 'Human-in-loop workflow states for DataForSEO and Perplexity integrations';
COMMENT ON TABLE context_handovers IS 'Context window management for session recovery across token limits';