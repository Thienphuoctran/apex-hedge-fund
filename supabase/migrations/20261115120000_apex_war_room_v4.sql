-- ============================================================================
-- APEX INSTITUTIONAL WAR-ROOM V4.0 — CLOUD DB PERSISTENCE (SUPABASE POSTGRES)
-- Phục vụ: Chủ tịch Trần Quốc Thiên Phước (TCBS: 105C307855)
-- Tuân thủ chuẩn bảo mật Supabase RLS & Postgres Best Practices:
--   * Bật RLS trên tất cả bảng exposed trong schema public
--   * Chỉ backend dùng SERVICE_ROLE_KEY mới có quyền ghi/đọc (anon bị chặn hoàn toàn)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.apex_portfolio_ssot (
    account_id TEXT PRIMARY KEY,
    chairman TEXT NOT NULL DEFAULT 'Trần Quốc Thiên Phước',
    status TEXT NOT NULL DEFAULT 'ACTIVE_HOLDING',
    cash_balance_vnd NUMERIC(18, 2) NOT NULL DEFAULT 0,
    total_nav_vnd NUMERIC(18, 2) NOT NULL DEFAULT 0,
    total_market_val_vnd NUMERIC(18, 2) NOT NULL DEFAULT 0,
    realized_pnl_vnd NUMERIC(18, 2) NOT NULL DEFAULT 0,
    unrealized_pnl_vnd NUMERIC(18, 2) NOT NULL DEFAULT 0,
    state_json JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.apex_war_room_directives (
    id TEXT PRIMARY KEY,
    trading_date DATE NOT NULL,
    timestamp_str TEXT NOT NULL,
    sender TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'specialist',
    type TEXT NOT NULL DEFAULT 'directive',
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_apex_wr_directives_date
    ON public.apex_war_room_directives (trading_date, created_at);

CREATE TABLE IF NOT EXISTS public.apex_live_intraday_reports (
    report_key TEXT PRIMARY KEY,
    trading_date DATE NOT NULL,
    regime_id TEXT NOT NULL,
    vn_index NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total_nav_vnd NUMERIC(18, 2) NOT NULL DEFAULT 0,
    cash_vnd NUMERIC(18, 2) NOT NULL DEFAULT 0,
    markdown_content TEXT NOT NULL,
    snapshot_json JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_apex_live_reports_date
    ON public.apex_live_intraday_reports (trading_date DESC);

CREATE TABLE IF NOT EXISTS public.apex_signal_slippage_tracker (
    signal_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    signal_date DATE NOT NULL,
    signal_time TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    signal_price NUMERIC(14, 2) NOT NULL,
    buy_up_pct NUMERIC(6, 2) NOT NULL DEFAULT 50,
    rsi14 NUMERIC(6, 2) NOT NULL DEFAULT 50,
    breadth_pct NUMERIC(6, 2) NOT NULL DEFAULT 50,
    regime_id TEXT NOT NULL DEFAULT 'SIDEWAY_CHOPPY',
    executed_price NUMERIC(14, 2),
    slippage_bps NUMERIC(10, 2),
    t3_price NUMERIC(14, 2),
    t3_return_pct NUMERIC(8, 2),
    t5_price NUMERIC(14, 2),
    t5_return_pct NUMERIC(8, 2),
    outcome TEXT NOT NULL DEFAULT 'PENDING',
    meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_apex_signals_sym_date
    ON public.apex_signal_slippage_tracker (symbol, signal_date DESC);

CREATE INDEX IF NOT EXISTS idx_apex_signals_outcome
    ON public.apex_signal_slippage_tracker (outcome, signal_date DESC);

CREATE TABLE IF NOT EXISTS public.apex_global_spillover_snapshots (
    snapshot_date DATE PRIMARY KEY,
    risk_multiplier NUMERIC(6, 3) NOT NULL DEFAULT 1.0,
    max_allocation_pct INTEGER NOT NULL DEFAULT 40,
    overnight_bias TEXT NOT NULL DEFAULT 'NEUTRAL_SELECTIVE',
    payload_json JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- BẮT BUỘC BẬT ROW LEVEL SECURITY TRÊN MỌI BẢNG EXPOSED TRONG PUBLIC
ALTER TABLE public.apex_portfolio_ssot ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.apex_war_room_directives ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.apex_live_intraday_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.apex_signal_slippage_tracker ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.apex_global_spillover_snapshots ENABLE ROW LEVEL SECURITY;

-- Thu hồi toàn bộ quyền truy cập trực tiếp từ anon / authenticated (chỉ backend service_role được phép)
REVOKE ALL ON public.apex_portfolio_ssot FROM anon, authenticated;
REVOKE ALL ON public.apex_war_room_directives FROM anon, authenticated;
REVOKE ALL ON public.apex_live_intraday_reports FROM anon, authenticated;
REVOKE ALL ON public.apex_signal_slippage_tracker FROM anon, authenticated;
REVOKE ALL ON public.apex_global_spillover_snapshots FROM anon, authenticated;
