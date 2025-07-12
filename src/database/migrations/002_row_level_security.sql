-- Brand BOS CIA System - Row Level Security Policies
-- Implements multi-tenant isolation for all tables

-- Enable RLS on all tables
ALTER TABLE cia_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE master_archives ENABLE ROW LEVEL SECURITY;
ALTER TABLE human_loop_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_handovers ENABLE ROW LEVEL SECURITY;

-- Create a function to get the current user's client_id
CREATE OR REPLACE FUNCTION auth.client_id() 
RETURNS UUID AS $$
BEGIN
    -- Extract client_id from JWT claims
    -- This assumes the JWT contains a 'client_id' claim
    RETURN COALESCE(
        auth.jwt() ->> 'client_id',
        auth.jwt() -> 'user_metadata' ->> 'client_id'
    )::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to check if user is service role
CREATE OR REPLACE FUNCTION auth.is_service_role()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN auth.jwt() ->> 'role' = 'service_role';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- CIA Sessions RLS Policies
CREATE POLICY "Users can view their own CIA sessions"
    ON cia_sessions FOR SELECT
    USING (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can create their own CIA sessions"
    ON cia_sessions FOR INSERT
    WITH CHECK (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can update their own CIA sessions"
    ON cia_sessions FOR UPDATE
    USING (client_id = auth.client_id() OR auth.is_service_role())
    WITH CHECK (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can delete their own CIA sessions"
    ON cia_sessions FOR DELETE
    USING (client_id = auth.client_id() OR auth.is_service_role());

-- Phase Responses RLS Policies
CREATE POLICY "Users can view their own phase responses"
    ON phase_responses FOR SELECT
    USING (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can create their own phase responses"
    ON phase_responses FOR INSERT
    WITH CHECK (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can update their own phase responses"
    ON phase_responses FOR UPDATE
    USING (client_id = auth.client_id() OR auth.is_service_role())
    WITH CHECK (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can delete their own phase responses"
    ON phase_responses FOR DELETE
    USING (client_id = auth.client_id() OR auth.is_service_role());

-- Master Archives RLS Policies
CREATE POLICY "Users can view their own master archives"
    ON master_archives FOR SELECT
    USING (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can create their own master archives"
    ON master_archives FOR INSERT
    WITH CHECK (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can update their own master archives"
    ON master_archives FOR UPDATE
    USING (client_id = auth.client_id() OR auth.is_service_role())
    WITH CHECK (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can delete their own master archives"
    ON master_archives FOR DELETE
    USING (client_id = auth.client_id() OR auth.is_service_role());

-- Human Loop States RLS Policies
CREATE POLICY "Users can view their own human loop states"
    ON human_loop_states FOR SELECT
    USING (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can create their own human loop states"
    ON human_loop_states FOR INSERT
    WITH CHECK (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can update their own human loop states"
    ON human_loop_states FOR UPDATE
    USING (client_id = auth.client_id() OR auth.is_service_role())
    WITH CHECK (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can delete their own human loop states"
    ON human_loop_states FOR DELETE
    USING (client_id = auth.client_id() OR auth.is_service_role());

-- Context Handovers RLS Policies
CREATE POLICY "Users can view their own context handovers"
    ON context_handovers FOR SELECT
    USING (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can create their own context handovers"
    ON context_handovers FOR INSERT
    WITH CHECK (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can update their own context handovers"
    ON context_handovers FOR UPDATE
    USING (client_id = auth.client_id() OR auth.is_service_role())
    WITH CHECK (client_id = auth.client_id() OR auth.is_service_role());

CREATE POLICY "Users can delete their own context handovers"
    ON context_handovers FOR DELETE
    USING (client_id = auth.client_id() OR auth.is_service_role());

-- Create indexes for RLS performance
CREATE INDEX IF NOT EXISTS idx_cia_sessions_client_id ON cia_sessions(client_id);
CREATE INDEX IF NOT EXISTS idx_phase_responses_client_id ON phase_responses(client_id);
CREATE INDEX IF NOT EXISTS idx_master_archives_client_id ON master_archives(client_id);
CREATE INDEX IF NOT EXISTS idx_human_loop_states_client_id ON human_loop_states(client_id);
CREATE INDEX IF NOT EXISTS idx_context_handovers_client_id ON context_handovers(client_id);

-- Add comments for documentation
COMMENT ON POLICY "Users can view their own CIA sessions" ON cia_sessions IS 
    'Ensures users can only access CIA sessions belonging to their client_id';
COMMENT ON POLICY "Users can view their own phase responses" ON phase_responses IS 
    'Ensures users can only access phase responses belonging to their client_id';
COMMENT ON POLICY "Users can view their own master archives" ON master_archives IS 
    'Ensures users can only access master archives belonging to their client_id';
COMMENT ON POLICY "Users can view their own human loop states" ON human_loop_states IS 
    'Ensures users can only access human loop states belonging to their client_id';
COMMENT ON POLICY "Users can view their own context handovers" ON context_handovers IS 
    'Ensures users can only access context handovers belonging to their client_id';