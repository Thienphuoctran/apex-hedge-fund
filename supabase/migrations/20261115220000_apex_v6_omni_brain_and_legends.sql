-- ============================================================================
-- APEX INSTITUTIONAL OMNI-BRAIN & SELF-EVOLUTION V6.0 — CLOUD DB PERSISTENCE
-- Phục vụ: Chủ tịch Trần Quốc Thiên Phước (TCBS: 105C307855)
-- Tuân thủ chuẩn bảo mật Supabase RLS & Postgres Best Practices:
--   * Bật RLS trên tất cả bảng exposed trong schema public
--   * Chỉ backend dùng SERVICE_ROLE_KEY mới có quyền ghi/đọc (anon bị chặn hoàn toàn)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.apex_v6_intelligence_snapshots (
    snapshot_key TEXT PRIMARY KEY,
    pillar_type TEXT NOT NULL,
    trading_date DATE NOT NULL,
    total_tickers INTEGER NOT NULL DEFAULT 0,
    maturity_score NUMERIC(6, 2) NOT NULL DEFAULT 0,
    collective_iq NUMERIC(6, 2) NOT NULL DEFAULT 0,
    payload_json JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_apex_v6_snapshots_pillar_date
    ON public.apex_v6_intelligence_snapshots (pillar_type, trading_date DESC);

CREATE TABLE IF NOT EXISTS public.apex_live_catalyst_alerts (
    alert_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    market TEXT NOT NULL DEFAULT 'VN',
    is_holding BOOLEAN NOT NULL DEFAULT FALSE,
    priority TEXT NOT NULL DEFAULT 'ALPHA_CATALYST',
    category TEXT NOT NULL DEFAULT 'MARKET_GENERAL',
    estimated_fair_value_impact_pct NUMERIC(6, 2) NOT NULL DEFAULT 0,
    recommended_action TEXT NOT NULL DEFAULT 'HOLD_AND_MONITOR',
    title TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_apex_v6_alerts_sym_prio
    ON public.apex_live_catalyst_alerts (symbol, priority, detected_at DESC);

ALTER TABLE public.apex_signal_slippage_tracker
    ADD COLUMN IF NOT EXISTS t10_price NUMERIC(14, 2),
    ADD COLUMN IF NOT EXISTS t10_return_pct NUMERIC(8, 2),
    ADD COLUMN IF NOT EXISTS t20_price NUMERIC(14, 2),
    ADD COLUMN IF NOT EXISTS t20_return_pct NUMERIC(8, 2);

-- BẮT BUỘC BẬT ROW LEVEL SECURITY TRÊN MỌI BẢNG EXPOSED TRONG PUBLIC
ALTER TABLE public.apex_v6_intelligence_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.apex_live_catalyst_alerts ENABLE ROW LEVEL SECURITY;

-- Thu hồi toàn bộ quyền truy cập trực tiếp từ anon / authenticated (chỉ backend service_role được phép)
REVOKE ALL ON public.apex_v6_intelligence_snapshots FROM anon, authenticated;
REVOKE ALL ON public.apex_live_catalyst_alerts FROM anon, authenticated;
