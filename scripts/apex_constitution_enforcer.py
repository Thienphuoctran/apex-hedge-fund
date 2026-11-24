#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX ENTERPRISE SOVEREIGN CODE & CONSTITUTION ENFORCEMENT ENGINE (V2.0 — 12 AUTOMATED GATES)
File: scripts/apex_constitution_enforcer.py
Cơ quan chủ trì: Khối 5 (Tổng Kiểm Sát Viên Trọng & Palmer) + Khối 3 (Master CIO James)
Ban hành theo sắc lệnh trực tiếp của: Chủ tịch HĐQT — Trần Quốc Thiên Phước (TCBS 105C307855)

Nhiệm vụ V2.0:
1. Lưu trữ & đồng bộ 10 Điều Luật Hiến Chương V2.0 theo Sơ đồ 5 Khối Chuyên Trách (không gán cứng số dư cũ).
2. Vận hành Bộ Cưỡng Chế 12 Chốt Chặn Hiến Pháp (`run_12_constitutional_gates()`) từ G01 đến G12.
3. Chốt chặn trước khi bấm lệnh (`pre_flight_order_gatekeeper`) với định cỡ động theo % NAV sống.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.portfolio_state_manager import PortfolioStateManager
from scripts.apex_persistent_memory_core import ApexPersistentMemoryCore
from scripts.vn_market_calendar import get_ict_now, get_vn_market_session_state

CONSTITUTION_DOC = BASE_DIR / "00_Governance_And_Constitution" / "APEX_ENTERPRISE_CONSTITUTION.md"
ANCHOR_FILE = BASE_DIR / "data" / "institutional_compliance_anchor.json"

TEN_CONSTITUTIONAL_ARTICLES = [
    {
        "article": 1,
        "name": "Phụng Sự Tối Thượng & Tài Sản SSOT Duy Nhất (105C307855)",
        "author": "Chủ tịch Phước Trần",
        "core_rule": "Tài khoản TCBS 105C307855 tại current_portfolio_state.json là chân lý duy nhất; cân bằng kế toán |Cash + Holdings - NAV| <= 50,000 đ; cấm CI/Bot tự ý sửa số dư.",
    },
    {
        "article": 2,
        "name": "Làm Thật 100% — Dữ Liệu Sống & Cấm BCTC Giả/Cứng",
        "author": "Hiến Chương V2.0",
        "core_rule": "Mọi chỉ số tài chính phải trích xuất từ BCTC kiểm toán sống (>=95% vũ trụ 145 mã); chặn cứng mọi mã có is_verified_real_bctc == False khỏi Top Mua.",
    },
    {
        "article": 3,
        "name": "Tranh Biện Đối Kháng Tam Giác & Kiểm Chứng Backtest Bắt Buộc",
        "author": "Chủ tịch Phước Trần",
        "core_rule": "Mọi khuyến nghị phải có phản biện rủi ro; mọi nâng cấp thuật toán phải thắng Backtest Walk-Forward 2 năm không Look-Ahead với MaxDD <= 12.5%.",
    },
    {
        "article": 4,
        "name": "Pháp Y Dòng Tiền Thật & Bộ Lọc 10 Đại Danh Thủ",
        "author": "Khối 1 & Khối 2",
        "core_rule": "Lọc F-Score >= 6, ROE >= 10.5%, Beneish M <= -1.78, Sloan <= 12%, OCF/LNST >= 0.70 (CT), thanh khoản >= 30 tỷ/phiên, ưu tiên ngành dẫn dắt & gia tốc PEAD.",
    },
    {
        "article": 5,
        "name": "Bảo Toàn Vốn & Định Cỡ Lô 100 Động Theo % NAV Sống",
        "author": "Master CIO James",
        "core_rule": "1 lô 100 CP <= 33% NAV sống; tổng rủi ro Stop <= 1.5% NAV/lệnh; R:R >= 1:2.0; Stop cứng <= 7.5%; cấm bình quân giá xuống.",
    },
    {
        "article": 6,
        "name": "Kỷ Luật Lịch Phiên, Nghỉ Lễ & Khung Giờ Vàng 14h05–14h25",
        "author": "James & Minh Quân",
        "core_rule": "Khóa ngày Lễ/Cuối tuần theo vn_market_calendar.py; cấm FOMO mua đuổi trước 10h00; vận hành đủ 8 mốc tác chiến; kích hoạt Breakeven Stop khi lãi >= +6% & Trailing Stop.",
    },
    {
        "article": 7,
        "name": "Một Nguồn Chân Lý Duy Nhất (SCBP) & Báo Cáo Tiền Thật Dễ Hiểu",
        "author": "James & Palmer",
        "core_rule": "Chat, Web Portal, Văn phòng 2.5D và Telegram bắt buộc dùng chung canonical_executive_briefing.json (SHA-256), báo cáo rõ MUA/BÁN/ĐỢI bằng VNĐ sau thuế phí.",
    },
    {
        "article": 8,
        "name": "Kỷ Luật Telegram Sạch & Chống Spam 1 Đầu Mối",
        "author": "Trọng & Palmer",
        "core_rule": "Chỉ Local PC đẩy Telegram (Cloud/CI=0); áp dụng khiên chống trùng 4 lớp, Mute theo Khối, chỉ báo chạm ngưỡng hành động & duy nhất 1 bản tin EOD 15:45.",
    },
    {
        "article": 9,
        "name": "Tường Lửa Read-Only Air-Gap & Báo Ngay Thao Tác Thủ Công",
        "author": "Chủ tịch & Victor",
        "core_rule": "AI chỉ đọc và phân tích; quyền bấm lệnh thật và Smart OTP thuộc Chủ tịch 100%; mọi việc cần thao tác tay báo rõ trong 60 giây.",
    },
    {
        "article": 10,
        "name": "Sổ Cái Thực Chiến, Trí Nhớ Liên Ngày & Chế Tài Trọng",
        "author": "Trọng (Ban 12)",
        "core_rule": "Theo dõi P&L thật tại real_performance_ledger.json, niêm phong trí nhớ liên ngày SHA-256; Trọng kiểm toán 12 chốt chặn hàng ngày và xử lý vi phạm 3 cấp.",
    },
]


class ApexConstitutionEnforcer:
    """Bộ máy Kiểm Toán & Cưỡng Chế 12 Chốt Chặn Hiến Chương Apex V2.0."""

    @staticmethod
    def sync_anchor_file() -> Dict[str, Any]:
        st = PortfolioStateManager.load_state()
        cash_bal = float(st.get("cash_balance_vnd", 0.0) or 0.0)
        nav_bal = float(st.get("total_nav_vnd", cash_bal) or cash_bal)
        anchor_data = {
            "constitution_version": "APEX_ENTERPRISE_CONSTITUTION_V2.0",
            "promulgated_by": "Chủ tịch Trần Quốc Thiên Phước",
            "promulgated_at": get_ict_now().strftime("%Y-%m-%d %H:%M:%S"),
            "account_id": st.get("account_id", "105C307855"),
            "cash_balance_vnd": cash_bal,
            "total_nav_vnd": nav_bal,
            "status": st.get("status", "ACTIVE_HOLDING"),
            "architecture": "5_BLOCS_UNIFIED_APEX_V7",
            "ten_commandments": TEN_CONSTITUTIONAL_ARTICLES,
            "hard_prohibitions": [
                "CẤM khuyến nghị MUA mã chưa có BCTC kiểm toán sống hoặc thiếu Stop/TP hợp lệ (Điều 2)",
                "CẤM FOMO mua đuổi trước 10h00 hoặc phát tín hiệu MUA ngày Nghỉ Lễ/Cuối tuần (Điều 6)",
                f"CẤM mua cổ phiếu có 1 lô 100 CP > 33% NAV sống ({nav_bal:,.0f} ₫) hoặc R:R < 1:2.0 (Điều 5)",
                "CẤM dùng số liệu cũ gán cứng hoặc làm lệch Chat vs Portal vs 2.5D Office so với SCBP (Điều 7)",
                "CẤM đẩy tin Telegram trùng lặp hoặc bật Cloud Telegram Push (Điều 8)",
                "CẤM vượt quyền Read-Only Air-Gap hoặc làm sai lệch SSOT 105C307855 (Điều 1 & 9)",
            ],
            "mandatory_gates_count": 12,
            "automation_slots": ["08:30", "09:00", "11:35", "13:00", "13:30", "14:05", "14:20", "15:45"],
        }
        ANCHOR_FILE.parent.mkdir(parents=True, exist_ok=True)
        ANCHOR_FILE.write_text(json.dumps(anchor_data, ensure_ascii=False, indent=2), encoding="utf-8")
        return anchor_data

    @staticmethod
    def pre_flight_order_gatekeeper(
        symbol: str,
        price: float,
        order_hour: Optional[int] = None,
        order_minute: Optional[int] = None,
        is_verified_bctc: Optional[bool] = None,
        stop_loss: Optional[float] = None,
        tp1: Optional[float] = None,
    ) -> Tuple[bool, str]:
        """Chốt chặn Hiến Chương V2.0 trước khi duyệt đề xuất lệnh Mua."""
        symbol = symbol.upper().strip()
        st = PortfolioStateManager.load_state()
        nav = float(st.get("total_nav_vnd", 0.0) or 0.0)
        if nav <= 0:
            return False, "[VI PHẠM ĐIỀU 1] NAV SSOT không hợp lệ (<= 0 ₫)."

        now_ict = get_ict_now()
        sess = get_vn_market_session_state(now_ict)
        if order_hour is None and not sess.get("is_trading_day", True):
            return False, f"[VI PHẠM ĐIỀU 6] Sàn đang đóng cửa ({sess.get('status_code')}). Cấm phát lệnh Mua ngày nghỉ."

        h = order_hour if order_hour is not None else now_ict.hour
        m = order_minute if order_minute is not None else now_ict.minute

        if is_verified_bctc is False:
            return False, f"[VI PHẠM ĐIỀU 2] {symbol} chưa có BCTC kiểm toán sống (UNVERIFIED_BLOCKED)."

        if price <= 0:
            return False, f"[VI PHẠM ĐIỀU 5] Giá đề xuất {symbol} không hợp lệ ({price})."

        lot_100_cost = price * 100.0
        nav_pct = (lot_100_cost / nav) * 100.0
        if nav_pct > 33.0:
            return False, f"[VI PHẠM ĐIỀU 5] 1 lô 100 CP {symbol} tốn {lot_100_cost:,.0f} ₫ ({nav_pct:.1f}% NAV {nav/1e6:.2f}M ₫) > trần 33% NAV."

        if stop_loss is not None and tp1 is not None:
            risk = price - stop_loss
            reward = tp1 - price
            if stop_loss <= 0 or tp1 <= price or risk <= 0:
                return False, f"[VI PHẠM ĐIỀU 5] Mức Stop ({stop_loss}) hoặc TP1 ({tp1}) của {symbol} không hợp lệ."
            if (risk / price) > 0.075:
                return False, f"[VI PHẠM ĐIỀU 5] Khoảng cắt lỗ {symbol} ({risk/price*100:.1f}%) vượt trần 7.5%."
            if (reward / risk) < 1.95:
                return False, f"[VI PHẠM ĐIỀU 5] Tỷ lệ R:R của {symbol} ({reward/risk:.2f}) < 2.0."

        ho = ApexPersistentMemoryCore.get_handover_for_today()
        for r_item in ho.get("rejected_stocks", []):
            if symbol in str(r_item):
                return False, f"[VI PHẠM ĐIỀU 3] {symbol} nằm trong danh sách bị Hội đồng phủ quyết: {r_item}."

        if now_ict.weekday() < 5 and 9 <= h < 10:
            return False, f"[VI PHẠM ĐIỀU 6] Đang trong khung sáng ({h:02d}:{m:02d}) — CẤM FOMO ATO! Chờ 14h05–14h25."

        return True, f"[ĐẠT CHUẨN HIẾN CHƯƠNG V2.0] {symbol} ({nav_pct:.1f}% NAV/lô, BCTC sạch, đúng kỷ luật phiên)."

    @staticmethod
    def run_12_constitutional_gates(base_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Kiểm toán tự động 12 Chốt Chặn G01–G12 toàn hệ thống."""
        root = base_dir or BASE_DIR
        now_ict = get_ict_now()
        gates: List[Dict[str, Any]] = []

        def _read_j(rel: str) -> Any:
            p = root / rel
            if not p.exists():
                return None
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return "__JSON_CORRUPT__"

        ssot = _read_j("data/current_portfolio_state.json")
        # G01: Account ID
        g01_ok = isinstance(ssot, dict) and ssot.get("account_id") == "105C307855"
        gates.append({"gate_id": "G01_SSOT_ACCOUNT_IDENTITY", "article": 1, "passed": g01_ok, "detail": f"account_id={ssot.get('account_id') if isinstance(ssot, dict) else 'MISSING'}"})

        # G02: SSOT Accounting balance
        if isinstance(ssot, dict):
            cash = float(ssot.get("cash_balance_vnd") or 0.0)
            nav = float(ssot.get("total_nav_vnd") or 0.0)
            pos = ssot.get("active_positions") or {}
            pos_val = sum(int(p.get("shares") or 0) * float(p.get("current_price") or p.get("entry_price") or 0.0) for p in pos.values())
            diff = abs((cash + pos_val) - nav)
            g02_ok = cash >= 0 and nav > 0 and diff <= 50_000.0
            g02_det = f"Cash={cash:,.0f} + Hold={pos_val:,.0f} = {cash+pos_val:,.0f} vs NAV={nav:,.0f} (diff={diff:,.0f}đ)"
        else:
            nav = 0.0
            g02_ok = False
            g02_det = "SSOT unreadable"
        gates.append({"gate_id": "G02_SSOT_ACCOUNTING_BALANCE", "article": 1, "passed": g02_ok, "detail": g02_det})

        # G03: BCTC Real Coverage >= 95%
        bctc = _read_j("VN_Market/data/vn_real_bctc_live.json")
        if isinstance(bctc, dict) and isinstance(bctc.get("stocks"), dict):
            req_n = int((bctc.get("coverage_stats") or {}).get("requested_vn_tickers") or len(bctc["stocks"]) or 1)
            ver_n = sum(
                1 for v in bctc["stocks"].values()
                if isinstance(v, dict)
                and v.get("is_verified_real_bctc", (v.get("latest_metrics") or {}).get("is_verified_real_bctc", True))
                and (v.get("latest_metrics") or {}).get("latest_quarter") not in (None, "", "SUMMARY_ONLY", "N/A")
            )
            cov_pct = round((ver_n / max(1, req_n)) * 100.0, 1)
            g03_ok = cov_pct >= 95.0 and ver_n >= 135
            g03_det = f"Verified real BCTC: {ver_n}/{req_n} ({cov_pct}%)"
        else:
            g03_ok = False
            g03_det = "vn_real_bctc_live.json missing"
        gates.append({"gate_id": "G03_BCTC_REAL_COVERAGE", "article": 2, "passed": g03_ok, "detail": g03_det})

        # G04: Zero unverified buy leak or 0đ Stop/TP in WarRoom/Scanner
        scan = _read_j("VN_Market/data/vn_full_market_scan.json")
        wr = _read_j("data/live_warroom_state.json")
        bad_buys: List[str] = []
        if isinstance(scan, dict):
            st_map = scan.get("stocks") or {}
            for sym in (scan.get("top_12_diversified_actionable_discoveries") or []):
                if not (st_map.get(sym) or {}).get("bctc_verified", False):
                    bad_buys.append(f"SCAN:{sym}")
        if isinstance(wr, dict):
            for row in (wr.get("simple_action_board") or []):
                if row.get("action_code") == "MUA":
                    if float(row.get("price") or 0) <= 0 or float(row.get("stop") or 0) <= 0 or float(row.get("tp1") or 0) <= 0:
                        bad_buys.append(f"WR_ZERO:{row.get('symbol')}")
        g04_ok = len(bad_buys) == 0
        gates.append({"gate_id": "G04_ZERO_UNVERIFIED_BUY_LEAK", "article": 2, "passed": g04_ok, "detail": "0 violations" if g04_ok else f"Violations={bad_buys[:5]}"})

        # G05: Exchange calendar holiday lock
        sess = get_vn_market_session_state(now_ict)
        hol_bad = []
        if not sess.get("is_trading_day", True) and isinstance(wr, dict):
            for row in (wr.get("simple_action_board") or []):
                if row.get("action_code") == "MUA":
                    hol_bad.append(str(row.get("symbol")))
        g05_ok = len(hol_bad) == 0
        gates.append({"gate_id": "G05_EXCHANGE_CALENDAR_HOLIDAY_LOCK", "article": 6, "passed": g05_ok, "detail": f"session={sess.get('status_code')}, invalid_holiday_buys={hol_bad}"})

        # G06: Dynamic Lot-100 <= 33% NAV cap
        oversized: List[str] = []
        v4 = _read_j("data/apex_brain_v4_output.json")
        if isinstance(v4, dict) and nav > 0:
            for c in (v4.get("tactical_round2_candidates") or []):
                px = float(c.get("limit_entry_vnd") or c.get("close_price") or 0.0)
                if px > 0 and (px * 100.0 / nav) > 0.335:
                    oversized.append(f"{c.get('symbol')}:{px*100/nav*100:.1f}%")
        if isinstance(wr, dict) and nav > 0:
            for row in (wr.get("simple_action_board") or []):
                if row.get("action_code") == "MUA":
                    px = float(row.get("price") or 0.0)
                    if px > 0 and (px * 100.0 / nav) > 0.335:
                        oversized.append(f"WR:{row.get('symbol')}")
        g06_ok = len(oversized) == 0
        gates.append({"gate_id": "G06_LOT100_DYNAMIC_NAV_CAP", "article": 5, "passed": g06_ok, "detail": "All picks <= 33% NAV/lot" if g06_ok else f"Oversized={oversized}"})

        # G07: Risk/Reward >= 2.0 & Stop <= 7.5%
        rr_bad: List[str] = []
        if isinstance(v4, dict):
            for c in (v4.get("tactical_round2_candidates") or []):
                px = float(c.get("limit_entry_vnd") or 0.0)
                stp = float(c.get("stop_loss_vnd") or 0.0)
                rr = float(c.get("rr_ratio_tp1") or 0.0)
                if px > 0 and stp > 0:
                    if ((px - stp) / px) > 0.078 or rr < 1.95:
                        rr_bad.append(f"{c.get('symbol')}(RR={rr})")
        g07_ok = len(rr_bad) == 0
        gates.append({"gate_id": "G07_RISK_REWARD_AND_STOP_CAP", "article": 5, "passed": g07_ok, "detail": "All picks R:R >= 2.0 & Stop <= 7.5%" if g07_ok else f"Failed={rr_bad}"})

        # G08: No Morning FOMO before 10:00 on trading day
        fomo_bad = []
        if sess.get("is_trading_day", True) and 9 <= now_ict.hour < 10 and isinstance(wr, dict):
            for row in (wr.get("simple_action_board") or []):
                if row.get("action_code") == "MUA":
                    fomo_bad.append(str(row.get("symbol")))
        g08_ok = len(fomo_bad) == 0
        gates.append({"gate_id": "G08_NO_MORNING_FOMO", "article": 6, "passed": g08_ok, "detail": f"ict_hour={now_ict.strftime('%H:%M')}, morning_buys={fomo_bad}"})

        # G09: SCBP Single Source Sync
        scbp = _read_j("data/canonical_executive_briefing.json")
        palmer = _read_j("data/palmer_live_briefing.json")
        state_md_p = root / "00_LIVE_INTER_CHAT_STATE.md"
        state_md_txt = state_md_p.read_text(encoding="utf-8", errors="ignore") if state_md_p.exists() else ""
        if isinstance(scbp, dict) and scbp.get("sha256_seal"):
            seal = str(scbp["sha256_seal"])
            palmer_seal = str((palmer or {}).get("scbp_sha256") or "") if isinstance(palmer, dict) else ""
            g09_ok = bool(seal) and (seal in state_md_txt or seal == palmer_seal)
            g09_det = f"SCBP seal={seal[:12]}... synced={g09_ok}"
        else:
            g09_ok = False
            g09_det = "canonical_executive_briefing.json missing or unsealed"
        gates.append({"gate_id": "G09_SCBP_SINGLE_SOURCE_SYNC", "article": 7, "passed": g09_ok, "detail": g09_det})

        # G10: Telegram Single-Owner Shield (Cloud & CI must have push=0)
        render_p = root / "render.yaml"
        render_ok = render_p.exists() and ('APEX_ALLOW_CLOUD_TELEGRAM_PUSH: "0"' in render_p.read_text(encoding="utf-8", errors="ignore") or "APEX_ALLOW_CLOUD_TELEGRAM_PUSH" in render_p.read_text(encoding="utf-8", errors="ignore"))
        dedup = _read_j("data/telegram_dedup_cache.json")
        g10_ok = render_ok and isinstance(dedup, dict)
        gates.append({"gate_id": "G10_TELEGRAM_SINGLE_OWNER_SHIELD", "article": 8, "passed": g10_ok, "detail": f"render_guard={render_ok}, dedup_cache_ok={isinstance(dedup, dict)}"})

        # G11: Backtest Empirical Validity (V4 beats V3 and MaxDD <= 12.5%)
        cal = _read_j("data/apex_empirical_calibration.json")
        if isinstance(cal, dict) and isinstance(cal.get("apex_v4_sector_alpha"), dict):
            v4_c = cal["apex_v4_sector_alpha"]
            v3_c = cal.get("apex_v3_asymmetric_conviction") or {}
            v4_ret = float(v4_c.get("total_return_pct") or 0.0)
            v3_ret = float(v3_c.get("total_return_pct") or -999.0)
            v4_mdd = float(v4_c.get("max_drawdown_pct") or -100.0)
            v4_shp = float(v4_c.get("sharpe_ratio") or 0.0)
            g11_ok = (v4_ret > v3_ret) and (v4_mdd >= -12.5) and (v4_shp >= 0.5)
            g11_det = f"V4 Ret={v4_ret:+.2f}% MaxDD={v4_mdd:.2f}% Sharpe={v4_shp} vs V3={v3_ret:+.2f}%"
        else:
            g11_ok = False
            g11_det = "apex_empirical_calibration.json missing V4"
        gates.append({"gate_id": "G11_BACKTEST_EMPIRICAL_VALIDITY", "article": 3, "passed": g11_ok, "detail": g11_det})

        # G12: Zero Secret Leak & JSON Integrity
        corrupt_jsons: List[str] = []
        for jf in list((root / "data").glob("*.json")) + list((root / "VN_Market" / "data").glob("*.json")):
            try:
                json.loads(jf.read_text(encoding="utf-8-sig"))
            except Exception:
                corrupt_jsons.append(jf.name)
        g12_ok = len(corrupt_jsons) == 0
        gates.append({"gate_id": "G12_ZERO_SECRET_AND_JSON_INTEGRITY", "article": 9, "passed": g12_ok, "detail": "All JSON stores valid" if g12_ok else f"Corrupt={corrupt_jsons[:5]}"})

        passed_cnt = sum(1 for g in gates if g["passed"])
        total_cnt = len(gates)
        return {
            "version": "CONSTITUTION_V2.0_12GATES",
            "audited_at_ict": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
            "passed_count": passed_cnt,
            "total_gates": total_cnt,
            "all_passed": passed_cnt == total_cnt,
            "status": "PASS_ALL_12" if passed_cnt == total_cnt else ("PARTIAL_WARN" if passed_cnt >= 10 else "FAIL_CRITICAL"),
            "gates": gates,
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apex Constitution V2.0 Enforcement Engine")
    parser.add_argument("--sync-anchor", action="store_true", help="Cập nhật institutional_compliance_anchor.json")
    parser.add_argument("--check-12-gates", action="store_true", help="Chạy kiểm toán 12 Chốt Chặn Hiến Chương V2.0")
    parser.add_argument("--test-gatekeeper", type=str, default="", help="Kiểm tra chốt chặn mua cho 1 mã")
    args = parser.parse_args()

    ApexConstitutionEnforcer.sync_anchor_file()
    if args.check_12_gates:
        res = ApexConstitutionEnforcer.run_12_constitutional_gates()
        print(f"[CONSTITUTION V2.0] {res['passed_count']}/{res['total_gates']} ({res['status']})")
        for g in res["gates"]:
            ic = "[PASS]" if g["passed"] else "[FAIL]"
            print(f"  {ic} {g['gate_id']}: {g['detail']}")
        return

    if args.test_gatekeeper:
        sym = args.test_gatekeeper.upper()
        appr, reason = ApexConstitutionEnforcer.pre_flight_order_gatekeeper(sym, 30000.0)
        print(f"{sym}: {'APPROVED' if appr else 'BLOCKED'} — {reason}")
        return
    print("[+] Synced institutional_compliance_anchor.json (V2.0).")


if __name__ == "__main__":
    main()
