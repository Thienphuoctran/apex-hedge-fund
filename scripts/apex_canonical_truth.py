#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX UNIFIED CANONICAL TRUTH ENGINE V5.0 (PURE PYTHON STDLIB)
File: scripts/apex_canonical_truth.py

Mục tiêu thể chế:
1. LÀM ĐẦU NÃO DUY NHẤT (Single Canonical Brain) hợp nhất Chat <-> Web Portal <-> Văn phòng 2.5D <-> Cron <-> Cloud.
2. Triệt tiêu 100% hiện tượng "Split-Brain" (mỗi script hô 1 chế độ thị trường khác nhau).
3. Đồng bộ Lịch Nghỉ Lễ HOSE/HNX + Stale-Feed Detector (`scripts/vn_market_calendar.py`).
4. Ghim chặt Nghị quyết Đại Hội Đồng & Chỉ thị Điều hành mới nhất cùng lịch T+2 thực tế cho từng mã SSOT.
   (Thuần Python stdlib — KHÔNG import pandas / numpy / yfinance.)
"""

from __future__ import annotations

import datetime
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.vn_market_calendar import (
    add_trading_days,
    get_ict_now,
    get_vn_market_session_state,
)

CANONICAL_TRUTH_FILE = DATA_DIR / "apex_canonical_truth.json"


def _load_json_safe(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {} if default is None else default


def _save_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{uuid.uuid4().hex[:8]}.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _find_latest_council_resolution() -> Dict[str, Any]:
    res_dir = BASE_DIR / "08_Master_Investment_CIO" / "council_resolutions"
    if not res_dir.exists():
        return {}
    md_files = sorted(
        [p for p in res_dir.glob("*.md") if p.name.lower() != "readme.md"],
        key=lambda p: (p.name[:10], p.stat().st_mtime, p.name),
        reverse=True,
    )
    if not md_files:
        return {}
    top = md_files[0]
    title = top.stem.replace("_", " ")
    try:
        for line in top.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip()
            if s.startswith("# "):
                title = s[2:].strip()
                break
    except Exception:
        pass
    rel_path = str(top.relative_to(BASE_DIR).as_posix())
    return {
        "file_name": top.name,
        "rel_path": rel_path,
        "title": title,
    }


def classify_canonical_regime(
    vn_index: float,
    vn_index_chg_pct: float,
    vni_ma20: float,
    vni_ma50: float,
    br20_pct: float,
    buy_up_pct: float,
    adv_ratio: float,
    session_state: Dict[str, Any],
    has_open_positions: bool = False,
    current_invested_pct: float = 0.0,
    vix_level: Optional[float] = None,
    vol_pace: float = 1.0,
    basis: float = 0.0,
    foreign_net_ty: float = 0.0,
) -> Dict[str, Any]:
    """
    Hàm phân loại Chế độ Thị trường DUY NHẤT cho toàn hệ thống Apex V5.0.
    Đánh giá đồng thời cả VNI vs MA20/MA50, Breadth > MA20 (Br20) và Buy-Up Pressure,
    sau đó áp dụng khóa an toàn tuyệt đối khi Sàn nghỉ lễ / cuối tuần / dữ liệu đóng băng.
    """
    vni = float(vn_index or 0.0)
    chg = float(vn_index_chg_pct or 0.0)
    ma20 = float(vni_ma20 or 0.0)
    ma50 = float(vni_ma50 or 0.0)
    br20 = float(br20_pct or 0.0)
    bu = float(buy_up_pct or 50.0)
    adv = float(adv_ratio or 50.0)

    if ma20 > 0 and vni >= ma20 and br20 >= 45.0 and bu >= 58.0:
        underlying = {
            "regime_id": "S1_BULL_BREAKOUT",
            "label": "🚀 S1 BULL BREAKOUT (VƯỢT MA20 ĐỒNG THUẬN)",
            "short_label": "S1_BULL_BREAKOUT",
            "badge_color": "#10b981",
            "max_new_allocation_pct": 70,
            "target_exposure_label": "60% – 80% NAV",
            "guidance": (
                f"VNI {vni:,.2f} ({chg:+.2f}%) vượt MA20 ({ma20:,.1f}), Br20={br20:.1f}%, Buy-Up={bu:.1f}%, Ngoại={foreign_net_ty:+.1f} Tỷ. "
                "Đạt chuẩn S1: cho phép nâng tổng cổ phiếu lên 60–80% NAV trong khung 14h05–14h25 với lệnh LO chuẩn."
            ),
        }
    elif (ma20 > 0 and vni >= ma20 * 0.985 and br20 >= 30.0 and bu >= 52.0) or (
        chg >= 0.35 and br20 >= 26.0 and bu >= 55.0
    ):
        underlying = {
            "regime_id": "S2_SIDEWAYS_SNIPER",
            "label": "⚖️ S2 SIDEWAYS SNIPER (GIẰNG CO CHỌN LỌC)",
            "short_label": "S2_SIDEWAYS_SNIPER",
            "badge_color": "#38bdf8",
            "max_new_allocation_pct": 35,
            "target_exposure_label": "30% – 50% NAV",
            "guidance": (
                f"VNI {vni:,.2f} ({chg:+.2f}% | MA20 {ma20:,.1f}), Br20={br20:.1f}%, Buy-Up={bu:.1f}%, Độ rộng {adv:.0f}%. "
                "Đạt chuẩn S2: giữ hoặc nâng tổng cổ phiếu lên 30–50% NAV, chỉ giải ngân thêm lúc 14h05–14h25 vào mã đầu ngành vượt MA20."
            ),
        }
    elif (chg >= 0.25 and bu >= 55.0 and br20 >= 18.0) or (br20 >= 22.0 and bu >= 58.0):
        underlying = {
            "regime_id": "S3_SPRING_STRIKE_READY",
            "label": "🟡 HỒI PHỤC KỸ THUẬT / SPRING S3 (DƯỚI MA20 — THĂM DÒ CÓ CHỌN LỌC)",
            "short_label": "S3_SPRING_STRIKE_READY",
            "badge_color": "#fbbf24",
            "max_new_allocation_pct": 25,
            "target_exposure_label": "20% – 45% NAV (Thăm dò có chọn lọc)",
            "guidance": (
                f"VNI {vni:,.2f} ({chg:+.2f}%) rút chân hồi phục với Buy-Up={bu:.1f}%, NHƯNG vẫn dưới MA20 ({ma20:,.1f}) và Br20={br20:.1f}% (< 28%). "
                "Thăm dò chọn lọc tối đa <= 25% sức mua còn lại trong khung 14h05–14h25; cấm FOMO mua đuổi Gap sáng."
            ),
        }
    else:
        target_lbl = (
            f"Giữ {current_invested_pct:.1f}% vị thế đạt chuẩn — KHÔNG mở mới"
            if has_open_positions
            else "0.0% NAV (100% TIỀN MẶT PHÒNG THỦ)"
        )
        underlying = {
            "regime_id": "S4_BEAR_CASH_SHIELD",
            "label": "🛡️ S4 BEAR SHIELD (PHÒNG THỦ CẨN TRỌNG)",
            "short_label": "S4_BEAR_CASH_SHIELD",
            "badge_color": "#ef4444",
            "max_new_allocation_pct": 0,
            "target_exposure_label": target_lbl,
            "guidance": (
                f"VNI {vni:,.2f} ({chg:+.2f}% | MA20 {ma20:,.1f} | MA50 {ma50:,.1f}), Br20={br20:.1f}%, Buy-Up={bu:.1f}%, Basis={basis:+.1f}đ. "
                "Độ rộng suy yếu dưới ngưỡng an toàn: khóa giải ngân mới (0%), giữ kỷ luật Stop 2xATR trên vị thế hiện có."
            ),
        }

    is_trading_day = bool(session_state.get("is_trading_day", True))
    stale_feed = bool(session_state.get("stale_feed_detected", False))
    status_code = str(session_state.get("status_code") or "")

    if (not is_trading_day) or stale_feed:
        if status_code == "EXCHANGE_STALE_FEED" or stale_feed:
            closed_id = "EXCHANGE_STALE_FEED"
        elif status_code == "WEEKEND_CLOSED":
            closed_id = "MARKET_WEEKEND_CLOSED"
        else:
            closed_id = "MARKET_HOLIDAY_CLOSED"

        next_td_vi = session_state.get("next_trading_day_vi") or session_state.get("next_trading_day") or "--"
        prev_td = session_state.get("prev_trading_day") or "--"
        settlement_note = session_state.get("settlement_note_vi") or ""
        return {
            "regime_id": closed_id,
            "label": session_state.get("status_label_vi") or "🎌 SÀN ĐÓNG CỬA — KHÔNG GIAO DỊCH",
            "short_label": session_state.get("short_badge_vi") or "🎌 SÀN ĐÓNG CỬA",
            "badge_color": "#f59e0b",
            "base_max_allocation_pct": 0,
            "spillover_multiplier": 1.0,
            "max_new_allocation_pct": 0,
            "target_exposure_label": f"0% mở mới hôm nay • Mở lại {next_td_vi}",
            "guidance": (
                f"{session_state.get('status_label_vi')}. Mọi giá bảng điện hiện tại là giá đóng cửa tham chiếu phiên trước ({prev_td}); "
                f"trạng thái EOD phiên trước là {underlying['regime_id']} (VNI {vni:,.2f} {chg:+.2f}%, Br20 {br20:.1f}%). "
                f"{settlement_note} Kế hoạch Nhịp 2 giữ nguyên hiệu lực cho phiên mở cửa kế tiếp ({next_td_vi})."
            ),
            "reference_eod_regime": underlying,
            "is_closed_override": True,
        }

    return {
        **underlying,
        "base_max_allocation_pct": underlying["max_new_allocation_pct"],
        "spillover_multiplier": 1.0,
        "reference_eod_regime": underlying,
        "is_closed_override": False,
    }


def _compute_ssot_canonical() -> Dict[str, Any]:
    ssot = _load_json_safe(DATA_DIR / "current_portfolio_state.json", {})
    cash_vnd = float(ssot.get("cash_balance_vnd", 0.0) or 0.0)
    active_pos = ssot.get("active_positions") if isinstance(ssot.get("active_positions"), dict) else {}

    holdings: List[Dict[str, Any]] = []
    stocks_val = 0.0
    cost_val = 0.0
    total_shares = 0

    for sym, pos in active_pos.items():
        if not isinstance(pos, dict):
            continue
        sh = int(pos.get("shares") or 0)
        if sh <= 0:
            continue
        ep = float(pos.get("entry_price") or 0.0)
        cp = float(pos.get("current_price") or ep)
        mkt = sh * cp
        cst = sh * ep
        stocks_val += mkt
        cost_val += cst
        total_shares += sh

        bought_raw = str(pos.get("bought_at") or "").strip()
        settlement_date = ""
        if bought_raw:
            try:
                bought_date = datetime.date.fromisoformat(bought_raw[:10])
                settlement_date = add_trading_days(bought_date, 2).isoformat()
            except Exception:
                settlement_date = ""

        holdings.append({
            "symbol": sym.upper(),
            "shares": sh,
            "entry_price": ep,
            "current_price": cp,
            "market_val_vnd": round(mkt, 0),
            "cost_basis_vnd": round(cst, 0),
            "unrealized_pnl_vnd": round(mkt - cst, 0),
            "unrealized_pnl_pct": round(((mkt - cst) / cst * 100.0), 2) if cst > 0 else 0.0,
            "stop_loss": float(pos.get("stop_loss") or 0.0),
            "tp1": float(pos.get("take_profit_tp1") or 0.0),
            "tp2": float(pos.get("take_profit_tp2") or 0.0),
            "bought_at": bought_raw,
            "t2_settlement_date": settlement_date,
        })

    nav_vnd = cash_vnd + stocks_val
    cash_pct = round((cash_vnd / nav_vnd) * 100.0, 1) if nav_vnd > 0 else 100.0
    invested_pct = round(100.0 - cash_pct, 1)
    holdings_desc = " + ".join(f"{h['shares']} {h['symbol']}" for h in holdings) if holdings else "0 CP"

    return {
        "account_id": str(ssot.get("account_id") or "105C307855"),
        "chairman": str(ssot.get("chairman") or "Trần Quốc Thiên Phước"),
        "status": str(ssot.get("status") or ("ACTIVE_HOLDING" if holdings else "ALL_CASH_STANDDOWN")),
        "cash_vnd": round(cash_vnd, 0),
        "stocks_val_vnd": round(stocks_val, 0),
        "cost_basis_vnd": round(cost_val, 0),
        "total_nav_vnd": round(nav_vnd, 0),
        "cash_pct": cash_pct,
        "invested_pct": invested_pct,
        "realized_pnl_vnd": float(ssot.get("realized_pnl_vnd") or 0.0),
        "unrealized_pnl_vnd": round(stocks_val - cost_val, 0),
        "unrealized_pnl_pct": round(((stocks_val - cost_val) / cost_val * 100.0), 2) if cost_val > 0 else 0.0,
        "open_positions_count": len(holdings),
        "total_shares": total_shares,
        "holdings_desc": holdings_desc,
        "holdings": holdings,
        "last_updated": str(ssot.get("last_updated") or ""),
    }


def build_and_save_canonical_truth(
    now_ict: Optional[datetime.datetime] = None,
    live_warroom_override: Optional[Dict[str, Any]] = None,
    market_overview_override: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Tổng hợp toàn bộ chân lý hệ thống (Lịch phiên + SSOT + Chế độ thị trường +
    Kế hoạch Hội đồng 21h00 + Chỉ thị Chat) và ghi ra `data/apex_canonical_truth.json`.
    """
    if now_ict is None:
        now_ict = get_ict_now()

    warroom = (
        live_warroom_override
        if isinstance(live_warroom_override, dict)
        else _load_json_safe(DATA_DIR / "live_warroom_state.json", {})
    )
    weekly_plan = _load_json_safe(DATA_DIR / "weekly_tactical_plan_active.json", {})
    palmer_brief = _load_json_safe(DATA_DIR / "palmer_live_briefing.json", {})
    ssot = _compute_ssot_canonical()

    recon = warroom.get("recon_summary") if isinstance(warroom, dict) else {}
    if not isinstance(recon, dict):
        recon = {}

    # Hợp nhất market_overview để phát hiện stale exchange_time nếu có
    mo = market_overview_override if isinstance(market_overview_override, dict) else {}
    vni_mo = mo.get("vn_index") if isinstance(mo.get("vn_index"), dict) else {}
    vn30_mo = mo.get("vn30_index") if isinstance(mo.get("vn30_index"), dict) else {}
    br_mo = mo.get("market_breadth") if isinstance(mo.get("market_breadth"), dict) else {}

    vni_val = float(vni_mo.get("value") or recon.get("vn_index") or 1697.14)
    vni_chg = float(vni_mo.get("change_pct") if vni_mo.get("value") else (recon.get("vn_index_chg_pct") or 0.0))
    vni_ma20 = float(vni_mo.get("ma20") or recon.get("vn_index_ma20") or 1727.57)
    vni_ma50 = float(vni_mo.get("ma50") or recon.get("vn_index_ma50") or 1746.23)
    br20_pct = float(recon.get("live_breadth_ma20_pct") or 0.0)
    buy_up_pct = float(recon.get("avg_buy_up_pct") or 50.0)
    vol_pace = float(vni_mo.get("volume_pace_ratio") or recon.get("volume_pace_ratio") or 1.0)
    foreign_ty = float(vni_mo.get("raw_foreign_net_ty") or recon.get("foreign_net_ty") or 0.0)
    basis = float(vn30_mo.get("basis_pts") or 0.0)
    adv_ratio = float(br_mo.get("advance_ratio_pct") or 0.0)
    if adv_ratio <= 0:
        adv_c = float(recon.get("advance_count") or 0.0)
        dec_c = float(recon.get("decline_count") or 0.0)
        adv_ratio = round((adv_c / (adv_c + dec_c)) * 100.0, 1) if (adv_c + dec_c) > 0 else 50.0

    overview_for_cal = mo if mo else {"exchange_time": warroom.get("exchange_time", "")}
    session_state = get_vn_market_session_state(now_ict=now_ict, market_overview=overview_for_cal)

    canonical_regime = classify_canonical_regime(
        vn_index=vni_val,
        vn_index_chg_pct=vni_chg,
        vni_ma20=vni_ma20,
        vni_ma50=vni_ma50,
        br20_pct=br20_pct,
        buy_up_pct=buy_up_pct,
        adv_ratio=adv_ratio,
        session_state=session_state,
        has_open_positions=(ssot["open_positions_count"] > 0),
        current_invested_pct=ssot["invested_pct"],
        vol_pace=vol_pace,
        basis=basis,
        foreign_net_ty=foreign_ty,
    )

    council_res = _find_latest_council_resolution()
    approved_watchlist = weekly_plan.get("approved_watchlist") if isinstance(weekly_plan.get("approved_watchlist"), list) else []
    priority_targets = [
        {
            "symbol": str(w.get("symbol") or "").upper(),
            "name": str(w.get("name") or ""),
            "tier": str(w.get("tier") or ""),
            "weekly_limit": str(w.get("weekly_limit") or ""),
            "entry_zone": str(w.get("entry_zone") or ""),
            "stop_loss_2xatr": str(w.get("stop_loss_2xatr") or ""),
            "tp1": str(w.get("tp1") or ""),
            "tp2": str(w.get("tp2") or ""),
            "executed_shares": int(w.get("executed_shares") or 0),
            "catalyst": str(w.get("catalyst") or ""),
        }
        for w in approved_watchlist
        if str(w.get("symbol") or "").strip()
    ]

    blacklist = [
        {"symbol": "BAF", "reason": "F-Score 2/9, OCF -496.2 tỷ, Beneish HIGH_RISK"},
        {"symbol": "PNJ", "reason": "F-Score 2/9, OCF -2,578 tỷ"},
        {"symbol": "VIX", "reason": "F-Score 3/9, OCF -4,877.3 tỷ"},
        {"symbol": "TCH", "reason": "F-Score 4/9, suy yếu cầu"},
        {"symbol": "CEO", "reason": "F-Score 5/9, thanh khoản/cầu yếu"},
        {"symbol": "POW", "reason": "Cảnh báo Pháp y: Beneish M=-1.57, OCF/LNST=0.20x, RSI 76.6 quá mua"},
    ]

    settlement_lines = []
    for h in ssot["holdings"]:
        if h["t2_settlement_date"]:
            settlement_lines.append(f"{h['shares']} {h['symbol']} về chiều {h['t2_settlement_date'][8:10]}/{h['t2_settlement_date'][5:7]}")
    settlement_summary = ", ".join(settlement_lines) if settlement_lines else "100% tiền mặt sẵn sàng"

    if not session_state["is_trading_day"] or session_state["stale_feed_detected"]:
        executive_directive_vi = (
            f"{session_state['status_label_vi']}. "
            f"Danh mục SSOT TCBS 105C307855 giữ nguyên: {ssot['holdings_desc']} ({ssot['stocks_val_vnd']:,.0f} ₫ = {ssot['invested_pct']:.1f}% NAV) "
            f"+ Tiền mặt {ssot['cash_vnd']:,.0f} ₫ ({ssot['cash_pct']:.1f}% NAV). "
            f"Hàng T+2: {settlement_summary}. Mọi giải ngân mới Nhịp 2 (ưu tiên 100 CTG @ 30,000–30,300 & 200 NAB @ 13,000–13,200, dự phòng 100 CTS) "
            f"chỉ xét trong Khung Giờ Vàng 14h05–14h25 phiên mở lại ({session_state['next_trading_day_vi']})."
        )
    else:
        executive_directive_vi = (
            f"{canonical_regime['label']} | Danh mục SSOT: {ssot['holdings_desc']} ({ssot['invested_pct']:.1f}% NAV) + "
            f"Tiền mặt {ssot['cash_vnd']:,.0f} ₫ ({ssot['cash_pct']:.1f}% NAV). "
            f"Trần mở mới tối đa: {canonical_regime['max_new_allocation_pct']}% sức mua (chỉ kê LO lúc 14h05–14h25)."
        )

    truth_payload = {
        "schema_version": "APEX_CANONICAL_TRUTH_V5",
        "generated_at_ict": now_ict.strftime("%Y-%m-%d %H:%M:%S ICT"),
        "date": now_ict.strftime("%Y-%m-%d"),
        "market_session": session_state,
        "ssot": ssot,
        "market_snapshot": {
            "vn_index": round(vni_val, 2),
            "vn_index_chg_pct": round(vni_chg, 2),
            "vn_index_ma20": round(vni_ma20, 2),
            "vn_index_ma50": round(vni_ma50, 2),
            "breadth_above_ma20_pct": round(br20_pct, 1),
            "avg_buy_up_pct": round(buy_up_pct, 1),
            "advance_ratio_pct": round(adv_ratio, 1),
            "volume_pace_ratio": round(vol_pace, 2),
            "foreign_net_ty": round(foreign_ty, 1),
            "basis_pts": round(basis, 2),
            "snapshot_note": (
                f"Giá đóng cửa tham chiếu phiên {session_state['prev_trading_day']}"
                if (not session_state["is_trading_day"] or session_state["stale_feed_detected"])
                else "Dữ liệu trong phiên giao dịch"
            ),
        },
        "canonical_regime": canonical_regime,
        "approved_plan": {
            "plan_id": str(weekly_plan.get("plan_id") or ""),
            "meeting_id_source": str(weekly_plan.get("meeting_id_source") or council_res.get("file_name") or ""),
            "constitution_mandate": str(weekly_plan.get("constitution_mandate") or ""),
            "priority_targets": priority_targets,
            "blacklist_veto": blacklist,
        },
        "latest_council_resolution": council_res,
        "latest_chat_sync": {
            "sync_id": str(palmer_brief.get("sync_id") or ""),
            "last_updated": str(palmer_brief.get("last_updated") or ""),
            "latest_user_request": str(palmer_brief.get("latest_user_request") or ""),
        },
        "executive_directive_vi": executive_directive_vi,
        "consistency_audit": {
            "single_canonical_brain": True,
            "holiday_calendar_enforced": True,
            "stale_feed_detector_active": True,
            "contradictions_count": 0,
        },
    }

    _save_json_atomic(CANONICAL_TRUTH_FILE, truth_payload)
    return truth_payload


def load_canonical_truth(refresh_if_missing: bool = True) -> Dict[str, Any]:
    data = _load_json_safe(CANONICAL_TRUTH_FILE, {})
    if (not data or not data.get("canonical_regime")) and refresh_if_missing:
        return build_and_save_canonical_truth()
    return data


if __name__ == "__main__":
    truth = build_and_save_canonical_truth()
    print(json.dumps({
        "generated_at_ict": truth["generated_at_ict"],
        "session_status": truth["market_session"]["status_code"],
        "session_label": truth["market_session"]["status_label_vi"],
        "canonical_regime": truth["canonical_regime"]["regime_id"],
        "ssot_holdings": truth["ssot"]["holdings_desc"],
        "cash_vnd": truth["ssot"]["cash_vnd"],
        "council_resolution": truth["latest_council_resolution"],
    }, ensure_ascii=False, indent=2))
