#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HỆ THỐNG TỔNG KIỂM TRA TOÀN VẸN THỂ CHẾ VÀ RÀ SOÁT CÁC NÂNG CẤP (APEX FULL AUDIT SUITE)
Chủ trì: Master CIO James (Ban 8) & Tổng Kiểm Sát Viên Trọng (Ban 12)
Phục vụ: Chủ tịch Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)
"""

import sys
import os

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
import time
import argparse
import datetime
import py_compile
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

parser = argparse.ArgumentParser(description="Apex Full System & Living War-Room V4.0 Audit")
parser.add_argument("--url", default="https://apex-hedge-fund.onrender.com", help="Target portal URL (local or Render)")
args, _ = parser.parse_known_args()
live_url = args.url.rstrip("/")

audit_results = {
    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "target_url": live_url,
    "officers": ["Master CIO James (Ban 8)", "Tổng Kiểm Sát Viên Trọng (Ban 12)"],
    "account": "TCBS 105C307855 (Chủ tịch Trần Quốc Thiên Phước)",
    "modules_tested": [],
    "total_checks": 0,
    "passed_checks": 0,
    "warnings": [],
    "errors": []
}


def record_check(module_name, check_name, passed, details=""):
    audit_results["total_checks"] += 1
    if passed:
        audit_results["passed_checks"] += 1
    else:
        audit_results["errors"].append({
            "module": module_name,
            "check": check_name,
            "details": details
        })
    audit_results["modules_tested"].append({
        "module": module_name,
        "check": check_name,
        "status": "PASSED" if passed else "FAILED",
        "details": details
    })


print("=" * 70)
print(f"BẮT ĐẦU TỔNG RÀ SOÁT THỰC TẾ HỆ THỐNG APEX V4.0 ({live_url})")
print("=" * 70)

# 1. KIỂM TRA TÍNH TOÀN VẸN SSOT ĐỘNG (KHÔNG HARDCODE SỐ TĨNH)
ssot_cash = 0.0
ssot_nav = 0.0
ssot_pos = {}
try:
    from scripts.portfolio_state_manager import PortfolioStateManager
    st = PortfolioStateManager.load_state()
    ssot_cash = float(st.get("cash_balance_vnd", 0.0))
    ssot_mkt_val = float(st.get("total_market_val_vnd", 0.0))
    ssot_nav = float(st.get("total_nav_vnd", 0.0))
    acc_id = st.get("account_id")
    ssot_pos = st.get("active_positions", {}) or {}

    check_acc = (acc_id == "105C307855")
    record_check("SSOT_Integrity", "Mã tài khoản TCBS chính chủ", check_acc, f"Account: {acc_id}")

    check_cash = (ssot_cash >= 0.0)
    record_check("SSOT_Integrity", "Số dư tiền mặt SSOT hợp lệ (>= 0)", check_cash, f"Cash: {ssot_cash:,.0f} đ")

    nav_diff = abs(ssot_nav - (ssot_cash + ssot_mkt_val))
    check_nav_math = (nav_diff < 100.0 and ssot_nav > 0.0)
    record_check("SSOT_Integrity", "Cân bằng kế toán NAV = Cash + MarketVal", check_nav_math, f"NAV: {ssot_nav:,.0f} đ (diff {nav_diff:.2f})")

    pos_valid = all(
        int(p.get("shares", 0)) > 0 and float(p.get("avg_cost", p.get("entry_price", 0))) > 0
        for p in ssot_pos.values()
    )
    record_check("SSOT_Integrity", "Cấu trúc danh mục đang nắm giữ hợp lệ", pos_valid, f"Holdings: {len(ssot_pos)} mã ({', '.join(ssot_pos.keys()) or '0 CP'})")
except Exception as e:
    record_check("SSOT_Integrity", "Nạp PortfolioStateManager", False, str(e))

# 1B. KIỂM TRA LIVING INTRADAY BRAIN & SQLITE VAULT SYNC
try:
    from scripts.apex_live_intraday_brain import compute_live_war_room_snapshot, sync_live_intraday_report
    snap = compute_live_war_room_snapshot(force_refresh=True)
    port_live = snap.get("portfolio_live", {})
    brain_cash = float(port_live.get("cash_vnd", -1.0))
    check_brain_ssot = (abs(brain_cash - ssot_cash) < 10.0 and len(snap.get("live_stocks", [])) > 0)
    record_check(
        "Living_Brain",
        "Snapshot Brain khớp SSOT & Watchlist động",
        check_brain_ssot,
        f"Brain Cash: {brain_cash:,.0f} đ | Stocks: {len(snap.get('live_stocks', []))} | Regime: {snap.get('intraday_regime', {}).get('regime_id')}"
    )
    rep_path = sync_live_intraday_report(snap, force_write=True)
    check_rep_written = bool(rep_path and rep_path.exists())
    record_check("Living_Brain", "Xuất Live Intraday Report & Sync SQLite Vault", check_rep_written, str(rep_path))
except Exception as e:
    record_check("Living_Brain", "Kiểm tra Apex Living Intraday Brain", False, str(e))

# 2. KIỂM TRA LIVE ENDPOINTS (HEALTH, WAR-ROOM, SSE STREAM, REPORTS, COMMANDS)
try:
    req = urllib.request.Request(f"{live_url}/api/health", headers={"User-Agent": "ApexAudit/4.0"})
    res = urllib.request.urlopen(req, timeout=15)
    body = json.loads(res.read().decode("utf-8"))
    api_cash = float(body.get("cash_vnd", -1.0))
    check_health = (res.status == 200 and body.get("status") == "ok" and abs(api_cash - ssot_cash) < 100.0)
    record_check("Live_Endpoint", "GET /api/health khớp SSOT Cash", check_health, f"Status: {body.get('status')}, Health Cash: {api_cash:,.0f} vs SSOT {ssot_cash:,.0f}")
except Exception as e:
    record_check("Live_Endpoint", "GET /api/health", False, str(e))

try:
    req = urllib.request.Request(f"{live_url}/api/tactical_war_room", headers={"User-Agent": "ApexAudit/4.0"})
    res = urllib.request.urlopen(req, timeout=20)
    raw_wr = res.read().decode("utf-8")
    wr = json.loads(raw_wr)
    wr_cash = float(wr.get("victor_sentinel", {}).get("cash_vnd", -1.0))
    no_mock_index = ("1258.62" not in raw_wr and "1324.95" not in raw_wr)
    check_wr = (
        res.status == 200
        and wr.get("status") == "ok"
        and abs(wr_cash - ssot_cash) < 100.0
        and bool(wr.get("intraday_regime", {}).get("regime_id"))
        and len(wr.get("live_stocks", [])) > 0
        and no_mock_index
    )
    record_check(
        "Live_Endpoint",
        "GET /api/tactical_war_room khớp SSOT & không mock index",
        check_wr,
        f"WR Cash: {wr_cash:,.0f} | VN-Index: {wr.get('market_overview', {}).get('vn_index', {}).get('value')} | Picks: {len(wr.get('dynamic_picks', []))}"
    )
except Exception as e:
    record_check("Live_Endpoint", "GET /api/tactical_war_room", False, str(e))

try:
    req = urllib.request.Request(f"{live_url}/api/tactical_war_room/stream?max_frames=1", headers={"User-Agent": "ApexAudit/4.0"})
    res = urllib.request.urlopen(req, timeout=20)
    ctype = res.headers.get("Content-Type", "")
    sse_body = res.read().decode("utf-8")
    check_sse = (res.status == 200 and "text/event-stream" in ctype and "war_room_tick" in sse_body and "data:" in sse_body)
    record_check("Live_Endpoint", "GET /api/tactical_war_room/stream (SSE)", check_sse, f"Content-Type: {ctype}, Bytes: {len(sse_body)}")
except Exception as e:
    record_check("Live_Endpoint", "GET /api/tactical_war_room/stream (SSE)", False, str(e))

try:
    req = urllib.request.Request(f"{live_url}/api/reports", headers={"User-Agent": "ApexAudit/4.0"})
    res = urllib.request.urlopen(req, timeout=15)
    data = json.loads(res.read().decode("utf-8"))
    reps = data.get("reports", []) if isinstance(data, dict) else data
    check_reps = (res.status == 200 and len(reps) > 0)
    record_check("Live_Endpoint", "GET /api/reports", check_reps, f"Tổng số báo cáo: {len(reps)}")
except Exception as e:
    record_check("Live_Endpoint", "GET /api/reports", False, str(e))

try:
    cmd_data = json.dumps({"command": "/tcbs"}).encode("utf-8")
    req = urllib.request.Request(f"{live_url}/api/command", data=cmd_data, headers={"Content-Type": "application/json", "User-Agent": "ApexAudit/4.0"})
    res = urllib.request.urlopen(req, timeout=20)
    cmd_res = json.loads(res.read().decode("utf-8"))
    check_cmd = (res.status == 200 and cmd_res.get("ok") is True and "105C307855" in cmd_res.get("response", ""))
    record_check("Live_Endpoint", "POST /api/command (/tcbs)", check_cmd, f"Officer: {cmd_res.get('officer')}, Ok: {cmd_res.get('ok')}")
except Exception as e:
    record_check("Live_Endpoint", "POST /api/command (/tcbs)", False, str(e))

try:
    cmd_data = json.dumps({"command": "/solenh"}).encode("utf-8")
    req = urllib.request.Request(f"{live_url}/api/command", data=cmd_data, headers={"Content-Type": "application/json", "User-Agent": "ApexAudit/4.0"})
    res = urllib.request.urlopen(req, timeout=20)
    cmd_res = json.loads(res.read().decode("utf-8"))
    resp_text = cmd_res.get("response", "")
    check_solenh = (res.status == 200 and cmd_res.get("ok") is True and len(resp_text) > 50)
    record_check("Live_Endpoint", "POST /api/command (/solenh)", check_solenh, f"Response length: {len(resp_text)}")
except Exception as e:
    record_check("Live_Endpoint", "POST /api/command (/solenh)", False, str(e))

try:
    cmd_data = json.dumps({"command": "/hop FPT"}).encode("utf-8")
    req = urllib.request.Request(f"{live_url}/api/command", data=cmd_data, headers={"Content-Type": "application/json", "User-Agent": "ApexAudit/4.0"})
    res = urllib.request.urlopen(req, timeout=20)
    cmd_res = json.loads(res.read().decode("utf-8"))
    check_hop = (res.status == 200 and cmd_res.get("ok") is True and "FPT" in cmd_res.get("response", ""))
    record_check("Live_Endpoint", "POST /api/command (/hop FPT)", check_hop, f"Debate length: {len(cmd_res.get('response', ''))}")
except Exception as e:
    record_check("Live_Endpoint", "POST /api/command (/hop FPT)", False, str(e))

# 3. KIỂM TRA CẦU CHÌ KHÓA THỜI GIAN THỰC (TIME-GATING EMBARGO)
try:
    from scripts.apex_report_scanner import scan_all_institutional_reports
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time_str = datetime.datetime.now().strftime("%H:%M:%S")
    scanned = scan_all_institutional_reports(date_filter=today_str)

    future_leaks = [r for r in scanned if r["date"] == today_str and r["sort_time"] > current_time_str]
    check_embargo = (len(future_leaks) == 0)
    record_check("TimeGating_Embargo", "Cầu chì khóa thời gian thực (0 rò rỉ báo cáo tương lai)", check_embargo, f"Báo cáo tương lai rò rỉ: {len(future_leaks)}")
except Exception as e:
    record_check("TimeGating_Embargo", "Cầu chì khóa thời gian thực", False, str(e))

# 4. KIỂM TRA BỘ GIÁM SÁT NGƯỠNG NÂNG CẤP DATABASE
try:
    cfg_file = BASE_DIR / "config" / "database_scaling_sentinel.json"
    check_cfg_exists = cfg_file.exists()
    record_check("Database_Sentinel", "Tệp quy chuẩn database_scaling_sentinel.json", check_cfg_exists, str(cfg_file))

    if check_cfg_exists:
        with open(cfg_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        arch = cfg.get("active_database_architecture", "")
        t_min = cfg.get("threshold_warning_min")
        t_max = cfg.get("threshold_warning_max")
        if arch == "SQLITE_LAKEHOUSE_VAULT_V5":
            check_thresholds = (t_min == 50000 and t_max == 100000)
            chk_label = "Ngưỡng giám sát SQLite Vault V5 (50k - 100k)"
        else:
            check_thresholds = (t_min == 300 and t_max == 500)
            chk_label = "Ngưỡng giám sát 300 - 500"
        record_check("Database_Sentinel", chk_label, check_thresholds, f"Arch: {arch}, Min: {t_min}, Max: {t_max}")

    from scripts.apex_inspector_trong import ApexInspectorTrong
    audit_res = ApexInspectorTrong.audit_system_technical_integrity_247()
    check_trong_check6 = (audit_res.get("checks_performed", 0) >= 6)
    record_check("Database_Sentinel", "Check 6 trong Bộ Não Thanh Tra Của Trọng", check_trong_check6, f"Checks performed: {audit_res.get('checks_performed')}")
except Exception as e:
    record_check("Database_Sentinel", "Kiểm tra Sentinel Nâng Cấp DB", False, str(e))

# 5. KIỂM TRA MÃ NGUỒN PYTHON (SYNTAX COMPILATION TOÀN BỘ SCRIPTS)
py_files = list((BASE_DIR / "scripts").glob("*.py"))
syntax_errors = []
for pf in py_files:
    try:
        py_compile.compile(str(pf), doraise=True)
    except Exception as e:
        syntax_errors.append(f"{pf.name}: {e}")

check_syntax = (len(syntax_errors) == 0)
record_check("Python_Code_Integrity", f"Biên dịch sạch {len(py_files)} scripts trong scripts/", check_syntax, f"Lỗi: {len(syntax_errors)}")

# 6. KIỂM TRA WEB PORTAL FRONTEND (LIVING WAR-ROOM V4.0 + SYNC FORM + SSE)
try:
    req = urllib.request.Request(f"{live_url}/", headers={"User-Agent": "ApexAudit/4.0"})
    html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8")

    has_v4 = ("V4.0" in html)
    record_check("Web_Portal_UI", "Giao diện V4.0 Bloomberg-Grade đã kích hoạt", has_v4, "V4.0 badge on live HTML")

    has_tv = ("tv_chart_container" in html and "tradingview" in html.lower())
    record_check("Web_Portal_UI", "TradingView HOSE Live Widget tích hợp", has_tv, "Found tv_chart_container")

    has_split = ("james-split-container" in html and "james-sidebar-panel" in html)
    record_check("Web_Portal_UI", "Bàn Chỉ Huy James 2 Cột (Split-View)", has_split, "Found split layout classes")

    has_war_room_v4 = (
        "wr-stream-status-badge" in html
        and "wr-regime-pill" in html
        and "sync-tcinvest-panel" in html
        and "wr-spillover-slippage-box" in html
        and "EventSource('/api/tactical_war_room/stream')" in html
        and "1258.62" not in html
        and "1324.95" not in html
    )
    record_check("Web_Portal_UI", "Living War-Room V4.0 SSE + Sync TCInvest + Spillover + Không mock tĩnh", has_war_room_v4, "Verified SSE, Sync form, Regime pill, Spillover, 0 mock index")

    has_smart_formatter = ("formatJamesResponseHtml" in html and "exec-kpi-banner" in html)
    record_check("Web_Portal_UI", "Smart Formatter bóc tách KPI & Stock Cards cho James", has_smart_formatter, "Found formatJamesResponseHtml")
except Exception as e:
    record_check("Web_Portal_UI", "Kiểm tra Web Portal Frontend", False, str(e))

# 7. KIỂM TRA PHASE 2 (GLOBAL SPILLOVER, SLIPPAGE TRACKER, CLOUD DB, PORTAL AUTH, KEEP-ALIVE)
try:
    from scripts.global_to_vn_spillover_engine import compute_global_to_vn_spillover
    sp = compute_global_to_vn_spillover(force_refresh=False)
    check_sp = (0.3 <= float(sp.get("risk_multiplier", 0)) <= 1.2 and bool(sp.get("overnight_bias")))
    record_check("Phase2_Spillover", "Global-to-VN Spillover Engine (US -> VN)", check_sp, f"Bias: {sp.get('overnight_bias')} | Mult: {sp.get('risk_multiplier')}x | Cap: {sp.get('max_allocation_pct')}%")
except Exception as e:
    record_check("Phase2_Spillover", "Global-to-VN Spillover Engine", False, str(e))

try:
    from scripts.execution_slippage_tracker import get_tracker_summary
    tr = get_tracker_summary()
    f_tr = tr.get("filters", {})
    check_tr = (float(f_tr.get("min_buy_up_pct", 0)) >= 50.0 and float(f_tr.get("max_rsi_buy", 0)) > 0)
    record_check("Phase2_Slippage", "Execution Slippage & Bull-Trap Tracker", check_tr, f"BuyUp>={f_tr.get('min_buy_up_pct')}% | RSI<={f_tr.get('max_rsi_buy')} | Signals={f_tr.get('total_signals_tracked')}")
except Exception as e:
    record_check("Phase2_Slippage", "Execution Slippage Tracker", False, str(e))

try:
    from scripts.apex_cloud_db_sync import ApexCloudDBSync
    mig_file = BASE_DIR / "supabase" / "migrations" / "20261115120000_apex_war_room_v4.sql"
    cdb = ApexCloudDBSync.get_cloud_status()
    check_cdb = (mig_file.exists() and "ENABLE ROW LEVEL SECURITY" in mig_file.read_text(encoding="utf-8") and bool(cdb.get("local_sqlite_mirror")))
    record_check("Phase2_CloudDB", "Cloud DB Schema (RLS) & Local SQLite Mirror", check_cdb, f"Mode: {cdb.get('mode')} | Vault: {cdb.get('vault_db_exists')}")
except Exception as e:
    record_check("Phase2_CloudDB", "Cloud DB Persistence", False, str(e))

try:
    from scripts.apex_portal_auth import hash_pin, verify_pin_hash
    h_pin = hash_pin("998877")
    check_auth_crypto = verify_pin_hash("998877", h_pin) and not verify_pin_hash("000000", h_pin)
    ka_file = BASE_DIR / ".github" / "workflows" / "apex_keep_alive.yml"
    check_ka = ka_file.exists() and "/api/health" in ka_file.read_text(encoding="utf-8")
    record_check("Phase2_Security_KeepAlive", "Portal PIN Crypto + GitHub Actions Keep-Alive", check_auth_crypto and check_ka, f"PBKDF2 Verified: {check_auth_crypto} | Keep-Alive YML: {check_ka}")
except Exception as e:
    record_check("Phase2_Security_KeepAlive", "Portal Security & Keep-Alive", False, str(e))

# 8. KIỂM TRA V5.0 (OMNI CRAWLER, DEEP FINANCIAL BRAIN, SELF-EVOLUTION & 15 LEGENDS, LIVE V5 ENDPOINTS)
try:
    from scripts.apex_omni_intelligence_crawler import _load_master_universe, search_market_intelligence
    univ = _load_master_universe()
    omni_file = BASE_DIR / "data" / "omni_market_intelligence.json"
    sr_hdb = search_market_intelligence("HDB", limit=5)
    t_syms = [t.get("symbol") for t in sr_hdb.get("matched_tickers", [])]
    check_omni = (len(univ) >= 175 and omni_file.exists() and sr_hdb.get("ok") is True and "HDB" in t_syms)
    record_check(
        "Phase3_OmniCrawler",
        "Omni-Market Crawler 180 mã & FTS5 Search Engine",
        check_omni,
        f"Universe: {len(univ)} | File: {omni_file.exists()} | HDB Match: {'HDB' in t_syms}"
    )
except Exception as e:
    record_check("Phase3_OmniCrawler", "Omni-Market Crawler & FTS5", False, str(e))

try:
    from scripts.apex_deep_financial_brain import analyze_deep_bctc_and_valuation
    hdb_b = analyze_deep_bctc_and_valuation("HDB")
    nvda_b = analyze_deep_bctc_and_valuation("NVDA")
    db_file = BASE_DIR / "data" / "deep_financial_brain_analysis.json"
    db_json = json.loads(db_file.read_text(encoding="utf-8")) if db_file.exists() else {}
    check_db_v5 = (
        hdb_b.get("valuation", {}).get("intrinsic_fair_value", 0) > 0
        and float(nvda_b.get("roe_pct", 0)) > 50.0
        and float(nvda_b.get("valuation", {}).get("intrinsic_fair_value", 0)) > 0
        and int(db_json.get("total_analyzed", 0)) >= 70
        and len(db_json.get("holdings_optimizer", [])) > 0
    )
    record_check(
        "Phase3_DeepBrain",
        "Deep Financial Brain (DuPont, 3-Model Valuation, EV%/Half-Kelly)",
        check_db_v5,
        f"Analyzed: {db_json.get('total_analyzed', 0)} | NVDA ROE: {nvda_b.get('roe_pct')}% | HDB Fair: {hdb_b.get('valuation', {}).get('intrinsic_fair_value')}"
    )
except Exception as e:
    record_check("Phase3_DeepBrain", "Deep Financial Brain", False, str(e))

try:
    from scripts.apex_evolution_and_legends_engine import run_self_reflection_and_mistake_autopsy
    sr_dry = run_self_reflection_and_mistake_autopsy(dry_run=True)
    lv_file = BASE_DIR / "data" / "legend_investor_wisdom_vault.json"
    lv_json = json.loads(lv_file.read_text(encoding="utf-8")) if lv_file.exists() else {}
    us_w = json.loads((BASE_DIR / "config" / "adaptive_weights.json").read_text(encoding="utf-8")).get("scoring_weights", {})
    vn_w = json.loads((BASE_DIR / "VN_Market" / "config" / "adaptive_weights_vn.json").read_text(encoding="utf-8")).get("weights", {})
    iq_m = sr_dry.get("system_maturity_iq", {})
    check_evo = (
        float(iq_m.get("maturity_score", 0)) > 50.0
        and int(lv_json.get("total_legends", 0)) == 15
        and len(lv_json.get("ticker_evaluations", [])) >= 9
        and sum(us_w.values()) == 100
        and round(sum(vn_w.values()), 2) == 1.0
    )
    record_check(
        "Phase3_EvolutionLegends",
        "Self-Evolution Maturity IQ, Weights Invariants & 15 World Legends",
        check_evo,
        f"Maturity: {iq_m.get('maturity_score')}/100 | IQ: {iq_m.get('collective_iq')} | Legends: {lv_json.get('total_legends')} | US={sum(us_w.values())} VN={round(sum(vn_w.values()), 2)}"
    )
except Exception as e:
    record_check("Phase3_EvolutionLegends", "Self-Evolution & 15 Legends", False, str(e))

try:
    req_s = urllib.request.Request(f"{live_url}/api/intelligence/search?q=HDB", headers={"User-Agent": "ApexAudit/5.0"})
    res_s = urllib.request.urlopen(req_s, timeout=20)
    s_json = json.loads(res_s.read().decode("utf-8"))

    req_b = urllib.request.Request(f"{live_url}/api/deep_brain?ticker=HDB", headers={"User-Agent": "ApexAudit/5.0"})
    res_b = urllib.request.urlopen(req_b, timeout=20)
    b_json = json.loads(res_b.read().decode("utf-8"))

    html_ok = ("wr-omni-brain-panel" in html and "omni-search-input" in html) if "html" in globals() else False
    wr_ok = bool(wr.get("deep_brain_summary", {}).get("top_vn_alpha_picks")) if "wr" in globals() else False
    check_v5_live = (
        res_s.status == 200
        and s_json.get("ok") is True
        and any(t.get("symbol") == "HDB" for t in s_json.get("matched_tickers", []))
        and res_b.status == 200
        and b_json.get("ok") is True
        and float(b_json.get("analysis", {}).get("roe_pct", 0)) > 0
        and html_ok
        and wr_ok
    )
    record_check(
        "Phase3_LiveEndpoints",
        "V5 Live Endpoints (/api/intelligence/search, /api/deep_brain, UI Panel)",
        check_v5_live,
        f"Search Ok: {s_json.get('ok')} | DeepBrain Ok: {b_json.get('ok')} | UI: {html_ok} | WR Summary: {wr_ok}"
    )
except Exception as e:
    record_check("Phase3_LiveEndpoints", "V5 Live Endpoints & UI", False, str(e))

# =========================================================================
# 9. PHASE 4 (V6.0): LIVE BCTC, CATALYST ALERTS, WALK-FORWARD T+3..T+20, CORR 60D & CLOUD V6 (4 CHECKS -> 35/35)
# =========================================================================
print("\n[9/9] Kiểm tra Nâng cấp V6.0 (Live BCTC, Catalyst Alerts, Walk-Forward T+20, Corr 60D & Cloud DB V6)...")

try:
    bctc_u_p = BASE_DIR / "data" / "live_bctc_quarterly_updates.json"
    alerts_u_p = BASE_DIR / "data" / "live_catalyst_alerts.json"
    bctc_u = json.loads(bctc_u_p.read_text(encoding="utf-8")) if bctc_u_p.exists() else {}
    alerts_u = json.loads(alerts_u_p.read_text(encoding="utf-8")) if alerts_u_p.exists() else {}
    check_v6_cat = (
        bctc_u_p.exists()
        and int(bctc_u.get("total_tickers_updated", 0) or 0) >= 1
        and alerts_u_p.exists()
        and isinstance(alerts_u.get("alerts"), list)
        and "HDB" in alerts_u.get("held_symbols", [])
    )
    record_check(
        "Phase4_LiveBCTC_Catalysts",
        "Live Quarterly BCTC Auto-Refresher & Instant Catalyst/Risk Alerts",
        check_v6_cat,
        f"BCTC patched: {bctc_u.get('total_tickers_updated', 0)} | Alerts: {alerts_u.get('total_alerts', 0)} (Holding: {alerts_u.get('holding_alerts_count', 0)})"
    )
except Exception as e:
    record_check("Phase4_LiveBCTC_Catalysts", "Live BCTC & Catalyst Alerts", False, str(e))

try:
    evo_state_p = BASE_DIR / "data" / "system_evolution_and_legends_state.json"
    flt_p = BASE_DIR / "config" / "war_room_adaptive_filters.json"
    evo_st = json.loads(evo_state_p.read_text(encoding="utf-8")) if evo_state_p.exists() else {}
    flt_st = json.loads(flt_p.read_text(encoding="utf-8")) if flt_p.exists() else {}
    wf = evo_st.get("multi_horizon_walk_forward", {})
    mh = flt_st.get("multi_horizon_attribution", {})
    sch_m = evo_st.get("school_attribution_matrix", {})
    check_v6_wf = (
        evo_state_p.exists()
        and all(k in wf for k in ("T+3", "T+5", "T+10", "T+20"))
        and all(k in mh for k in ("T+3", "T+5", "T+10", "T+20"))
        and len(sch_m) == 5
    )
    record_check(
        "Phase4_MultiHorizon_WalkForward",
        "Walk-Forward Attribution T+3/T+5/T+10/T+20 & 5-School Matrix",
        check_v6_wf,
        f"Horizons: {list(wf.keys())} | Schools: {len(sch_m)}"
    )
except Exception as e:
    record_check("Phase4_MultiHorizon_WalkForward", "Walk-Forward T+3..T+20", False, str(e))

try:
    db_file = BASE_DIR / "data" / "deep_financial_brain_analysis.json"
    db_json = json.loads(db_file.read_text(encoding="utf-8")) if db_file.exists() else {}
    cm = db_json.get("correlation_matrix", {})
    mat = cm.get("matrix", {})
    vn_picks = db_json.get("top_vn_alpha_picks", [])
    check_v6_corr = (
        int(cm.get("session_window", 0) or 0) == 60
        and int(cm.get("live_60d_series_fetched", 0) or 0) >= 1
        and "HDB" in mat
        and "MSH" in mat
        and bool(vn_picks)
        and all("corr_guard_status" in p for p in vn_picks[:5])
    )
    record_check(
        "Phase4_CorrelationMatrix_Guard",
        "60-Session Portfolio Return Correlation Matrix & Sector Concentration Guard",
        check_v6_corr,
        f"60D Live Series: {cm.get('live_60d_series_fetched', 0)} | Evaluated: {cm.get('total_symbols_evaluated', 0)}"
    )
except Exception as e:
    record_check("Phase4_CorrelationMatrix_Guard", "60D Correlation Matrix", False, str(e))

try:
    from scripts.apex_cloud_db_sync import ApexCloudDBSync, VAULT_DB_PATH
    sync_v6 = ApexCloudDBSync.sync_v6_intelligence_to_vault()
    mig_p = BASE_DIR / "supabase" / "migrations" / "20261115220000_apex_v6_omni_brain_and_legends.sql"
    mig_ok = mig_p.exists() and ("ENABLE ROW LEVEL SECURITY" in mig_p.read_text(encoding="utf-8"))

    req_al = urllib.request.Request(f"{live_url}/api/intelligence/alerts", headers={"User-Agent": "ApexAudit/6.0"})
    res_al = urllib.request.urlopen(req_al, timeout=15)
    al_json = json.loads(res_al.read().decode("utf-8"))

    import sqlite3
    with sqlite3.connect(VAULT_DB_PATH, timeout=10) as conn:
        snap_cnt = conn.execute("SELECT COUNT(*) FROM apex_v6_intelligence_snapshots").fetchone()[0]

    ui_v6_ok = ("wr-omni-catalyst-strip" in html and "omni-walk-forward-strip" in html) if "html" in globals() else False
    check_v6_cloud = (
        sync_v6.get("ok") is True
        and sync_v6.get("snapshots_saved", 0) >= 2
        and snap_cnt >= 2
        and mig_ok
        and res_al.status == 200
        and al_json.get("ok") is True
        and ui_v6_ok
    )
    record_check(
        "Phase4_CloudDB_V6_And_AlertsAPI",
        "Cloud DB V6 Vault Sync, Supabase RLS Migration & /api/intelligence/alerts",
        check_v6_cloud,
        f"Snapshots DB: {snap_cnt} | Migration RLS: {mig_ok} | Alerts API: {al_json.get('ok')} | UI V6: {ui_v6_ok}"
    )
except Exception as e:
    record_check("Phase4_CloudDB_V6_And_AlertsAPI", "Cloud DB V6 & Alerts API", False, str(e))

# =========================================================================
# 10. PHASE 5 (V7.0): LIVING ENTERPRISE & 14-DEPARTMENT COLLABORATION MESH (5 CHECKS -> 40/40)
# =========================================================================
print("\n[10/10] Kiểm tra Nâng cấp V7.0 (Doanh Nghiệp Sống 14 Thực Thể, Tranh Biện VETO, Trọng Audit & Cloud V7)...")

_v7_latest_session = {}
try:
    from scripts.apex_enterprise_collaboration_mesh import (
        ENTERPRISE_DEPARTMENT_ROSTER,
        get_enterprise_mesh_summary,
    )
    mesh_sum = get_enterprise_mesh_summary()
    _v7_latest_session = mesh_sum.get("latest_session") or {}
    seal_str = str(_v7_latest_session.get("constitutional_seal_sha256") or "")
    check_v7_roster = (
        len(ENTERPRISE_DEPARTMENT_ROSTER) == 14
        and int(_v7_latest_session.get("quorum_count", 0) or 0) == 14
        and int(_v7_latest_session.get("packet_count", 0) or 0) >= 10
        and _v7_latest_session.get("ombudsman_audit_score") == "10/10"
        and len(seal_str) == 64
    )
    record_check(
        "Phase5_EnterpriseRosterAndPackets",
        "14 Thực Thể Độc Lập, Quorum 14/14, Data Packets & Niêm Phong SHA-256",
        check_v7_roster,
        f"Roster: {len(ENTERPRISE_DEPARTMENT_ROSTER)} | Quorum: {_v7_latest_session.get('quorum_count')}/14 | Packets: {_v7_latest_session.get('packet_count')} | Audit: {_v7_latest_session.get('ombudsman_audit_score')} | Seal: {seal_str[:12]}..."
    )
except Exception as e:
    record_check("Phase5_EnterpriseRosterAndPackets", "14 Thực Thể & Data Packets V7", False, str(e))

try:
    from scripts.apex_enterprise_collaboration_mesh import run_enterprise_work_session
    mwg_sess = run_enterprise_work_session("Kiểm tra MWG", ticker="MWG", trigger_source="AUDIT", sync_cloud=False)
    fpt_sess = run_enterprise_work_session("Kiểm tra FPT", ticker="FPT", trigger_source="AUDIT", sync_cloud=False)
    port_sess = run_enterprise_work_session(
        "Họp giao ban toàn doanh nghiệp đánh giá danh mục 105C307855",
        ticker=None,
        trigger_source="AUDIT",
        sync_cloud=False,
    )
    _v7_latest_session = port_sess or _v7_latest_session
    check_v7_veto = (
        mwg_sess.get("veto_triggered") is True
        and mwg_sess.get("final_verdict") == "VETOED_CAPITAL_FIT_VIOLATION"
        and fpt_sess.get("veto_triggered") is True
        and int(port_sess.get("quorum_count", 0) or 0) == 14
        and port_sess.get("ombudsman_audit_score") == "10/10"
    )
    record_check(
        "Phase5_AdversarialDebateAndVeto",
        "Tranh Biện Đối Kháng & Quyền Phủ Quyết VETO Hiến Chương (MWG/FPT)",
        check_v7_veto,
        f"MWG: {mwg_sess.get('final_verdict')} (Veto={mwg_sess.get('veto_triggered')}) | FPT: {fpt_sess.get('final_verdict')} (Veto={fpt_sess.get('veto_triggered')}) | Portfolio: {port_sess.get('final_verdict')}"
    )
except Exception as e:
    record_check("Phase5_AdversarialDebateAndVeto", "Tranh Biện Đối Kháng & VETO V7", False, str(e))

try:
    from scripts.apex_directive_intelligence_engine import ApexDirectiveIntelligenceEngine
    from scripts.apex_summit_meeting_engine import get_realtime_meeting_state
    tcbs_reply = ApexDirectiveIntelligenceEngine.generate_executive_directive_reply("/tcbs")
    rt_state = get_realtime_meeting_state(preview_mode=True)
    tcbs_txt = tcbs_reply if isinstance(tcbs_reply, str) else json.dumps(tcbs_reply, ensure_ascii=False)
    rt_txt = json.dumps(rt_state, ensure_ascii=False)
    nav_str_chk = f"{ssot_nav:,.0f}" if ssot_nav > 0 else "18,151,471"
    cash_str_chk = f"{ssot_cash:,.0f}" if ssot_cash > 0 else "12,516,471"
    check_v7_ssot = (
        nav_str_chk in tcbs_txt
        and cash_str_chk in tcbs_txt
        and nav_str_chk in rt_txt
        and cash_str_chk in rt_txt
        and "20,167,119" not in tcbs_txt
        and "100% TIỀN MẶT" not in tcbs_txt
        and "20,167,119" not in rt_txt
        and "100% TIỀN MẶT" not in rt_txt
    )
    record_check(
        "Phase5_ConstitutionalOmbudsmanAndZeroStaleSSOT",
        "Kiểm Toán Viên Trọng & 0% Chuỗi Cứng Lỗi Thời SSOT (Directive + Summit)",
        check_v7_ssot,
        f"Live NAV/Cash ({nav_str_chk}/{cash_str_chk}) synced; 0 stale strings in /tcbs & Summit state"
    )
except Exception as e:
    record_check("Phase5_ConstitutionalOmbudsmanAndZeroStaleSSOT", "Zero Stale SSOT Audit", False, str(e))

try:
    req_es = urllib.request.Request(f"{live_url}/api/enterprise/state", headers={"User-Agent": "ApexAudit/7.0"})
    res_es = urllib.request.urlopen(req_es, timeout=20)
    es_json = json.loads(res_es.read().decode("utf-8"))

    convene_payload = json.dumps({
        "ticker": "HDB",
        "directive": "Audit kiểm tra hợp lưu đa phòng ban HDB",
        "trigger_source": "AUDIT_SCRIPT",
        "sync_cloud": False,
    }).encode("utf-8")
    req_ec = urllib.request.Request(
        f"{live_url}/api/enterprise/convene",
        data=convene_payload,
        headers={"Content-Type": "application/json", "User-Agent": "ApexAudit/7.0"},
    )
    res_ec = urllib.request.urlopen(req_ec, timeout=25)
    ec_json = json.loads(res_ec.read().decode("utf-8"))
    ec_sess = ec_json.get("session") or {}

    ui_v7_ok = ("wr-enterprise-mesh-panel" in html and "conveneEnterpriseMesh" in html) if "html" in globals() else False
    wr_v7_ok = bool((wr.get("enterprise_mesh_summary") or {}).get("latest_session")) if "wr" in globals() else False

    check_v7_live = (
        res_es.status == 200
        and es_json.get("ok") is True
        and int(es_json.get("roster_count", 0) or 0) == 14
        and res_ec.status == 200
        and ec_json.get("ok") is True
        and int(ec_sess.get("quorum_count", 0) or 0) == 14
        and ec_sess.get("ombudsman_audit_score") == "10/10"
        and ui_v7_ok
        and wr_v7_ok
    )
    record_check(
        "Phase5_LiveEnterpriseEndpoints",
        "V7 Live Endpoints (/api/enterprise/state, /api/enterprise/convene, War-Room & UI Panel)",
        check_v7_live,
        f"State OK={es_json.get('ok')} | Convene HDB={ec_sess.get('final_verdict')} | WR={wr_v7_ok} | UI={ui_v7_ok}"
    )
except Exception as e:
    record_check("Phase5_LiveEnterpriseEndpoints", "V7 Live Enterprise Endpoints & UI", False, str(e))

try:
    from scripts.apex_cloud_db_sync import ApexCloudDBSync, VAULT_DB_PATH
    sync_v7 = ApexCloudDBSync.sync_enterprise_session(_v7_latest_session)
    mig_v7_p = BASE_DIR / "supabase" / "migrations" / "20261115230000_apex_v7_enterprise_collaboration_mesh.sql"
    mig_v7_ok = mig_v7_p.exists() and ("ENABLE ROW LEVEL SECURITY" in mig_v7_p.read_text(encoding="utf-8"))

    import sqlite3
    with sqlite3.connect(VAULT_DB_PATH, timeout=10) as conn:
        ent_cnt = conn.execute("SELECT COUNT(*) FROM apex_enterprise_work_sessions").fetchone()[0]

    check_v7_cloud = (
        sync_v7.get("ok") is True
        and sync_v7.get("local_saved") is True
        and mig_v7_ok
        and ent_cnt >= 1
    )
    record_check(
        "Phase5_CloudDB_V7_EnterpriseSync",
        "Cloud DB V7 Enterprise Sessions Sync, SQLite Vault & Supabase RLS Migration",
        check_v7_cloud,
        f"LocalSaved={sync_v7.get('local_saved')} | VaultRows={ent_cnt} | MigrationRLS={mig_v7_ok} | CloudSynced={sync_v7.get('cloud_synced')}"
    )
except Exception as e:
    record_check("Phase5_CloudDB_V7_EnterpriseSync", "Cloud DB V7 Enterprise Sync", False, str(e))

# =========================================================================
# 11. PHASE 6 (V8.0): WEB PORTAL LIVE SYNC & MULTI-DEPARTMENT WAR-ROOM (5 CHECKS -> 45/45)
# =========================================================================
print("\n[11/11] Kiểm tra Nâng cấp V8.0 (Zero Stale Strings, Victor Deep Surveillance, Live Execution Plan, 14-Dept Workstation & Publisher)...")

try:
    import re as _re
    portal_html_text = str(globals().get("html", "") or "")
    ui_html_only = _re.sub(r"let allReports = \[.*\];", "let allReports = [];", portal_html_text)
    stale_tokens = [
        "14,477,119",
        "20,167,119",
        "21,220 đ",
        "NGÀY 09/11/2026",
        "THỨ BA 10/11/2026",
        "09:00 Thứ Hai (09/11)",
        "Tiền Mặt 20M",
    ]
    found_stale = [tok for tok in stale_tokens if tok in ui_html_only]
    check_zero_stale = (len(portal_html_text) > 50000 and len(found_stale) == 0)
    record_check(
        "Phase6_ZeroStaleHardcodedWebStrings",
        "Zero stale hardcoded dates, prices, or old cash numbers in Portal HTML",
        check_zero_stale,
        f"HTML Bytes: {len(portal_html_text)} | StaleFound: {found_stale}"
    )
except Exception as e:
    record_check("Phase6_ZeroStaleHardcodedWebStrings", "Zero Stale Hardcoded Strings", False, str(e))

try:
    wr_payload = globals().get("wr", {}) or {}
    v_surv = wr_payload.get("victor_deep_surveillance", {}) or {}
    held_book = v_surv.get("held_positions_book", []) or []
    watch_book = v_surv.get("alpha_watchlist_book", []) or []
    held_syms = {str(x.get("symbol", "")).upper() for x in held_book}
    watch_fields_ok = (
        len(watch_book) >= 4
        and all(
            ("lot_100_cost_vnd" in w and "mos_pct" in w and "victor_signal" in w)
            for w in watch_book
        )
    )
    check_victor_v8 = ({"HDB", "MSH"}.issubset(held_syms) and watch_fields_ok)
    record_check(
        "Phase6_VictorDeepSurveillanceAndAlphaWatchlist",
        "Victor 2-Tier Deep Surveillance (Held Positions + Alpha Watchlist Lot-100 Check)",
        check_victor_v8,
        f"Held: {sorted(held_syms)} | WatchlistCount: {len(watch_book)} | FieldsOK: {watch_fields_ok}"
    )
except Exception as e:
    record_check("Phase6_VictorDeepSurveillanceAndAlphaWatchlist", "Victor Deep Surveillance V8", False, str(e))

try:
    wr_payload = globals().get("wr", {}) or {}
    m_plan = wr_payload.get("live_execution_master_plan", {}) or {}
    h_items = m_plan.get("holdings_action_items", []) or []
    d_orders = m_plan.get("new_deployment_orders", []) or []
    scens = m_plan.get("contingency_scenarios", []) or []
    check_plan_v8 = (len(h_items) >= 1 and len(d_orders) >= 1 and len(scens) == 3)
    record_check(
        "Phase6_LiveExecutionMasterPlan",
        "Dynamic Market-Adaptive Live Execution Master Plan & 3 Contingency Scenarios",
        check_plan_v8,
        f"PlanID: {m_plan.get('plan_id')} | HoldActions: {len(h_items)} | Orders: {len(d_orders)} | Scenarios: {len(scens)}"
    )
except Exception as e:
    record_check("Phase6_LiveExecutionMasterPlan", "Live Execution Master Plan V8", False, str(e))

try:
    wr_payload = globals().get("wr", {}) or {}
    depts_ws = wr_payload.get("department_live_workstation", []) or []
    rep_feed = wr_payload.get("latest_reports_feed", []) or []
    all_ws_exist = all(
        bool(d.get("latest_report_path")) and (BASE_DIR / str(d.get("latest_report_path"))).exists()
        for d in depts_ws
    )
    all_feed_exist = (
        len(rep_feed) >= 1
        and all(
            bool(r.get("rel_path")) and (BASE_DIR / str(r.get("rel_path"))).exists()
            for r in rep_feed
        )
    )
    check_ws_v8 = (len(depts_ws) == 14 and all_ws_exist and all_feed_exist)
    record_check(
        "Phase6_DepartmentWorkstationAndReportAuthenticity",
        "14-Department Operations Workstation & 100% Verified Disk Report Authenticity",
        check_ws_v8,
        f"Departments: {len(depts_ws)}/14 | Feed: {len(rep_feed)} | WsExist: {all_ws_exist} | FeedExist: {all_feed_exist}"
    )
except Exception as e:
    record_check("Phase6_DepartmentWorkstationAndReportAuthenticity", "14-Dept Workstation & Reports", False, str(e))

try:
    portal_html_text = str(globals().get("html", "") or "")
    cloud_srv_src = (BASE_DIR / "scripts" / "start_apex_cloud_247.py").read_text(encoding="utf-8")
    required_ui_tokens = [
        "publishWarRoomReportNow",
        "victor-deep-surveillance-panel",
        "wr-live-execution-master-plan-panel",
        "wr-dept-workstation-panel",
    ]
    missing_ui = [t for t in required_ui_tokens if t not in portal_html_text]
    endpoint_wired = ("/api/war_room/publish_report" in cloud_srv_src)
    check_pub_v8 = (len(missing_ui) == 0 and endpoint_wired)
    record_check(
        "Phase6_PublishWarRoomReportEndpointAndJS",
        "V8 War-Room UI Panels, 1-Click Publish JS & /api/war_room/publish_report Endpoint",
        check_pub_v8,
        f"MissingUITokens: {missing_ui} | EndpointWired: {endpoint_wired}"
    )
except Exception as e:
    record_check("Phase6_PublishWarRoomReportEndpointAndJS", "Publish War Room Endpoint & JS", False, str(e))

# 7. KIỂM TRA PHASE 7 V9.0: PHÒNG HỌP THƯỢNG ĐỈNH 14 PHÒNG BAN, CHUẨN BỊ T-15P & LỊCH HỌP 23H45 TUẦN SAU
summit_preview_data = {}
try:
    req = urllib.request.Request(f"{live_url}/api/summit_meeting?preview=1", headers={"User-Agent": "ApexAudit/4.0"})
    res = urllib.request.urlopen(req, timeout=20)
    summit_preview_data = json.loads(res.read().decode("utf-8"))
    dossiers = summit_preview_data.get("pre_summit_prep_dossiers", []) or []
    prep_stream = summit_preview_data.get("prep_timeline_stream", []) or []
    all_prep_paths_exist = all(
        bool(d.get("report_path")) and (BASE_DIR / str(d.get("report_path"))).exists()
        for d in dossiers
    )
    check_prep_15m = (
        res.status == 200
        and len(dossiers) >= 14
        and len(prep_stream) >= 14
        and all_prep_paths_exist
    )
    record_check(
        "Phase7_SummitPreMeetingPrep15mDossiers",
        "Giai đoạn Chuẩn bị T-15 Phút (14/14 Phòng Ban quét dữ liệu thật & nộp hồ sơ)",
        check_prep_15m,
        f"PrepDossiers: {len(dossiers)}/14 | PrepLogs: {len(prep_stream)} | ReportPathsExist: {all_prep_paths_exist}"
    )
except Exception as e:
    record_check("Phase7_SummitPreMeetingPrep15mDossiers", "Summit T-15m Prep Dossiers", False, str(e))

try:
    roster = summit_preview_data.get("attendance_roster", []) or []
    t_stream = summit_preview_data.get("timeline_stream", []) or []
    present_bans = [r for r in roster if r.get("present") and str(r.get("id", "")).startswith("BAN_")]
    speakers = {str(m.get("department", "")) for m in t_stream if m.get("department")}
    check_debate_v9 = (
        len(present_bans) >= 14
        and len(t_stream) >= 30
        and len(speakers) >= 12
    )
    record_check(
        "Phase7_SummitFull14DepartmentAttendanceAndDebate",
        "Điểm danh 14/14 Phòng Ban có mặt 100% & Tranh biện đa chiều (>= 30 lượt)",
        check_debate_v9,
        f"PresentBans: {len(present_bans)}/14 | TotalTurns: {len(t_stream)} | ActiveDeptVoices: {len(speakers)}"
    )
except Exception as e:
    record_check("Phase7_SummitFull14DepartmentAttendanceAndDebate", "14-Dept Attendance & Debate", False, str(e))

try:
    s_time = str(summit_preview_data.get("start_time", ""))
    s_dur = int(summit_preview_data.get("duration_minutes", 0) or 0)
    s_topic = str(summit_preview_data.get("topic", ""))
    res_rel = str(summit_preview_data.get("resolution_report_path", ""))
    res_disk_ok = bool(res_rel) and (BASE_DIR / res_rel).exists()
    check_sched_2345 = (
        "23:45" in s_time
        and s_dur == 30
        and ("Tuần Sau" in s_topic or "Tuần Mới" in s_topic)
        and res_disk_ok
    )
    record_check(
        "Phase7_SummitNextWeek2345ScheduleAndResolution",
        "Lịch họp 23h45 (30p) Chiến lược Thị trường Tuần Sau & Nghị quyết Markdown thật",
        check_sched_2345,
        f"Start: {s_time} | Dur: {s_dur}m | ResolutionOnDisk: {res_disk_ok} ({res_rel})"
    )
except Exception as e:
    record_check("Phase7_SummitNextWeek2345ScheduleAndResolution", "Summit 23h45 Schedule & Resolution", False, str(e))

try:
    sched_payload = json.dumps({
        "start_time": "2026-11-15T23:45:00+07:00",
        "duration_minutes": 30,
        "topic": "Dự Báo Thị Trường Tuần Sau (16/11 – 20/11/2026), Tranh Biện Chiến Lược & Đề Xuất Phương Án Đầu Tư Tối Ưu Hóa Lợi Nhuận Tuần Mới",
        "trigger_prep_now": True
    }).encode("utf-8")
    req_sched = urllib.request.Request(
        f"{live_url}/api/summit/schedule",
        data=sched_payload,
        headers={"Content-Type": "application/json", "User-Agent": "ApexAudit/4.0"}
    )
    res_sched = urllib.request.urlopen(req_sched, timeout=20)
    sched_body = json.loads(res_sched.read().decode("utf-8"))

    portal_html_text = str(globals().get("html", "") or "")
    summit_start_idx = portal_html_text.find('id="tab-summit-room"')
    summit_end_idx = portal_html_text.find('id="tab-timeline"')
    summit_section_html = portal_html_text[summit_start_idx:summit_end_idx] if summit_start_idx != -1 and summit_end_idx != -1 else portal_html_text
    no_stale_20261108 = ("2026-11-08" not in summit_section_html)
    required_v9_tokens = [
        "summit-schedule-bar",
        "summit-attendance-panel",
        "summit-prep-dossiers-panel",
        "scheduleNewSummitMeeting",
        "openCurrentSummitResolution",
    ]
    missing_v9 = [t for t in required_v9_tokens if t not in portal_html_text]
    check_api_ui_v9 = (
        res_sched.status == 200
        and sched_body.get("ok") is True
        and int(sched_body.get("prep_dossiers_count", 0) or 0) >= 14
        and no_stale_20261108
        and len(missing_v9) == 0
    )
    record_check(
        "Phase7_SummitScheduleAPIAndDynamicResolution",
        "Endpoint POST /api/summit/schedule & Giao diện Tab 5 động 100% (Sạch 2026-11-08)",
        check_api_ui_v9,
        f"ScheduleOK: {sched_body.get('ok')} | PrepCount: {sched_body.get('prep_dossiers_count')} | CleanSummitSection: {no_stale_20261108} | MissingV9: {missing_v9}"
    )
except Exception as e:
    record_check("Phase7_SummitScheduleAPIAndDynamicResolution", "Summit Schedule API & Dynamic UI", False, str(e))

try:
    dir_payload = json.dumps({"message": "Báo cáo ngắn phương án phòng thủ HDB tuần sau"}).encode("utf-8")
    req_dir = urllib.request.Request(
        f"{live_url}/api/summit_message",
        data=dir_payload,
        headers={"Content-Type": "application/json", "User-Agent": "ApexAudit/4.0"}
    )
    res_dir = urllib.request.urlopen(req_dir, timeout=20)
    dir_body = json.loads(res_dir.read().decode("utf-8"))
    resps = dir_body.get("responses", []) or []
    check_dir_v9 = (res_dir.status == 200 and dir_body.get("ok") is True and len(resps) >= 2)
    record_check(
        "Phase7_SummitLiveInteractiveDirective",
        "Tương tác chỉ thị Chủ tịch trực tiếp trong Phòng Họp Thượng Đỉnh (Đa Ban phản hồi)",
        check_dir_v9,
        f"Ok: {dir_body.get('ok')} | MultiDeptReplies: {len(resps)}"
    )
except Exception as e:
    record_check("Phase7_SummitLiveInteractiveDirective", "Summit Live Interactive Directive", False, str(e))

print("=" * 70)
print(f"KẾT QUẢ TỔNG KIỂM TOÁN: {audit_results['passed_checks']}/{audit_results['total_checks']} HẠNG MỤC ĐẠT CHUẨN!")
if audit_results["errors"]:
    print(f"CÁC LỖI PHÁT HIỆN: {len(audit_results['errors'])}")
    for err in audit_results["errors"]:
        print(f"  - [{err['module']}] {err['check']}: {err['details']}")
else:
    print("HOÀN TOÀN KHÔNG CÓ LỖI! 100% CÁC NÂNG CẤP HOẠT ĐỘNG TRƠN TRU & HOÀN THIỆN!")
print("=" * 70)

audit_log_path = BASE_DIR / "12_Institutional_Ombudsman_And_Inspectorate" / "daily_audits" / f"{datetime.datetime.now().strftime('%Y-%m-%d')}_Comprehensive_Audit_Report.json"
audit_log_path.parent.mkdir(parents=True, exist_ok=True)
with open(audit_log_path, "w", encoding="utf-8") as f:
    json.dump(audit_results, f, ensure_ascii=False, indent=2)
print(f"Đã lưu hồ sơ kiểm toán: {audit_log_path}")
sys.exit(1 if audit_results["errors"] else 0)
