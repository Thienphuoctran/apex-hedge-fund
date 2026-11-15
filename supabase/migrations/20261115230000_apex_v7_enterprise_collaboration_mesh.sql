-- APEX V7.0: LIVING ENTERPRISE & INTER-DEPARTMENTAL COLLABORATION MESH
-- Stores audited 5-stage multi-department sessions, quantitative packets, roll-call votes & SHA-256 constitutional seals.

CREATE TABLE IF NOT EXISTS public.apex_enterprise_work_sessions (
    session_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    trigger_source TEXT NOT NULL DEFAULT 'CHAIRMAN_DIRECTIVE',
    target_ticker TEXT,
    directive TEXT NOT NULL,
    final_verdict TEXT NOT NULL,
    quorum_count INTEGER NOT NULL DEFAULT 14,
    packet_count INTEGER NOT NULL DEFAULT 0,
    dissent_count INTEGER NOT NULL DEFAULT 0,
    veto_triggered BOOLEAN NOT NULL DEFAULT FALSE,
    ombudsman_audit_score TEXT NOT NULL DEFAULT '10/10',
    constitutional_seal_sha256 TEXT NOT NULL,
    payload_json JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_apex_enterprise_sessions_created
    ON public.apex_enterprise_work_sessions (updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_apex_enterprise_sessions_ticker
    ON public.apex_enterprise_work_sessions (target_ticker);

ALTER TABLE public.apex_enterprise_work_sessions ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON public.apex_enterprise_work_sessions FROM anon, authenticated;
GRANT ALL ON public.apex_enterprise_work_sessions TO service_role;
