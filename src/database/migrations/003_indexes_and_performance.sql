-- Brand BOS CIA System - Performance Indexes and Optimizations
-- Creates additional indexes for query performance

-- CIA Sessions performance indexes
CREATE INDEX IF NOT EXISTS idx_cia_sessions_status_client ON cia_sessions(status, client_id);
CREATE INDEX IF NOT EXISTS idx_cia_sessions_current_phase ON cia_sessions(current_phase) WHERE current_phase IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cia_sessions_started_at ON cia_sessions(started_at DESC) WHERE started_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cia_sessions_progress ON cia_sessions(progress_percentage) WHERE progress_percentage > 0;

-- Composite index for active session queries
CREATE INDEX IF NOT EXISTS idx_cia_sessions_active ON cia_sessions(client_id, status, created_at DESC) 
    WHERE status IN ('pending', 'executing', 'paused');

-- Phase Responses performance indexes
CREATE INDEX IF NOT EXISTS idx_phase_responses_session_status ON phase_responses(session_id, status);
CREATE INDEX IF NOT EXISTS idx_phase_responses_phase_id ON phase_responses(phase_id);
CREATE INDEX IF NOT EXISTS idx_phase_responses_context_usage ON phase_responses(context_usage_percentage) 
    WHERE context_usage_percentage > 70;
CREATE INDEX IF NOT EXISTS idx_phase_responses_human_input ON phase_responses(session_id, requires_human_input) 
    WHERE requires_human_input = true;

-- Master Archives performance indexes
CREATE INDEX IF NOT EXISTS idx_master_archives_phase ON master_archives(phase_number);
CREATE INDEX IF NOT EXISTS idx_master_archives_quality ON master_archives(synthesis_quality_score) 
    WHERE synthesis_quality_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_master_archives_chain ON master_archives(session_id, archive_version);

-- Human Loop States performance indexes
CREATE INDEX IF NOT EXISTS idx_human_loop_states_type ON human_loop_states(loop_type);
CREATE INDEX IF NOT EXISTS idx_human_loop_states_pending ON human_loop_states(status, sent_at) 
    WHERE status = 'waiting';
CREATE INDEX IF NOT EXISTS idx_human_loop_states_expired ON human_loop_states(expired_at) 
    WHERE status = 'waiting' AND expired_at IS NOT NULL;

-- Context Handovers performance indexes
CREATE INDEX IF NOT EXISTS idx_context_handovers_unrecovered ON context_handovers(client_id, recovered, created_at DESC) 
    WHERE recovered = false;
CREATE INDEX IF NOT EXISTS idx_context_handovers_session_number ON context_handovers(session_id, handover_number);

-- Full text search indexes for intelligence content
CREATE INDEX IF NOT EXISTS idx_master_archives_intelligence_gin ON master_archives 
    USING GIN (intelligence_summary);
CREATE INDEX IF NOT EXISTS idx_master_archives_frameworks_gin ON master_archives 
    USING GIN (customer_psychology, competitive_analysis, authority_positioning, content_strategy);

-- Partial indexes for common queries
CREATE INDEX IF NOT EXISTS idx_cia_sessions_incomplete ON cia_sessions(client_id, created_at DESC) 
    WHERE status != 'completed' AND status != 'failed';

CREATE INDEX IF NOT EXISTS idx_phase_responses_errors ON phase_responses(session_id, phase_id) 
    WHERE error_message IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_human_loop_reminder ON human_loop_states(sent_at) 
    WHERE status = 'waiting' AND reminder_sent = false;

-- Function to analyze table sizes and suggest maintenance
CREATE OR REPLACE FUNCTION analyze_cia_tables()
RETURNS TABLE (
    table_name TEXT,
    row_count BIGINT,
    total_size TEXT,
    index_size TEXT,
    toast_size TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        schemaname||'.'||tablename AS table_name,
        n_live_tup AS row_count,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
        pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS index_size,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - 
            pg_relation_size(schemaname||'.'||tablename) - 
            pg_indexes_size(schemaname||'.'||tablename)) AS toast_size
    FROM pg_stat_user_tables
    WHERE schemaname = 'public' 
    AND tablename IN ('cia_sessions', 'phase_responses', 'master_archives', 
                      'human_loop_states', 'context_handovers')
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get index usage statistics
CREATE OR REPLACE FUNCTION get_index_usage_stats()
RETURNS TABLE (
    table_name TEXT,
    index_name TEXT,
    index_scans BIGINT,
    index_size TEXT,
    usage_ratio NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        schemaname||'.'||tablename AS table_name,
        indexrelname AS index_name,
        idx_scan AS index_scans,
        pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
        ROUND(100.0 * idx_scan / NULLIF(seq_scan + idx_scan, 0), 2) AS usage_ratio
    FROM pg_stat_user_indexes
    JOIN pg_stat_user_tables USING (schemaname, tablename)
    WHERE schemaname = 'public'
    AND tablename IN ('cia_sessions', 'phase_responses', 'master_archives', 
                      'human_loop_states', 'context_handovers')
    ORDER BY tablename, idx_scan DESC;
END;
$$ LANGUAGE plpgsql;

-- Create materialized view for session analytics (refresh periodically)
CREATE MATERIALIZED VIEW IF NOT EXISTS cia_session_analytics AS
SELECT 
    s.client_id,
    DATE(s.created_at) as session_date,
    COUNT(DISTINCT s.id) as total_sessions,
    COUNT(DISTINCT s.id) FILTER (WHERE s.status = 'completed') as completed_sessions,
    COUNT(DISTINCT s.id) FILTER (WHERE s.status = 'failed') as failed_sessions,
    AVG(s.progress_percentage) as avg_progress,
    AVG(s.total_tokens_used) as avg_tokens_used,
    AVG(s.handover_count) as avg_handovers,
    AVG(EXTRACT(EPOCH FROM (s.completed_at - s.started_at))/60) 
        FILTER (WHERE s.completed_at IS NOT NULL) as avg_duration_minutes,
    COUNT(DISTINCT pr.id) as total_phase_responses,
    COUNT(DISTINCT ma.id) as total_archives,
    COUNT(DISTINCT hl.id) as total_human_loops
FROM cia_sessions s
LEFT JOIN phase_responses pr ON s.id = pr.session_id
LEFT JOIN master_archives ma ON s.id = ma.session_id
LEFT JOIN human_loop_states hl ON s.id = hl.session_id
GROUP BY s.client_id, DATE(s.created_at);

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS idx_session_analytics_client_date 
    ON cia_session_analytics(client_id, session_date DESC);

-- Add comment
COMMENT ON MATERIALIZED VIEW cia_session_analytics IS 
    'Pre-aggregated analytics for CIA sessions - refresh daily with: REFRESH MATERIALIZED VIEW cia_session_analytics;';