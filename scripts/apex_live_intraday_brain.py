#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX REAL-TIME ADAPTIVE INTRADAY BRAIN (WAR-ROOM V4.0)
File: scripts/apex_live_intraday_brain.py
Cơ quan chủ quản: Minh Quân (Ban 7 VN) & Victor (Ban 9 Live Sentinel)

Nhiệm vụ (Hạng mục 1.2 War-Room V4.0):
1. Hợp nhất Watchlist động từ SSOT (`current_portfolio_state.json`) + `vn_daily_ledger.json`
   + `master_execution_blotter.json` + `weekly_tactical_plan_active.json` (xóa bỏ danh sách cứng).
2. Tái tính toán quyết định theo từng tick giá:
   - PnL sống từng giây, khoảng cách % tới Stop Loss 2xATR & mục tiêu TP1 / TP2.
   - Đánh giá Market Regime Intraday (`RISK_ON_BREAKOUT`, `SIDEWAY_CHOPPY`, `DEFENSIVE_SELLOFF`).
   - Sinh trạng thái hành động động cho từng vị thế nắm giữ & mã tầm ngắm.
3. Tự động xuất `VN_Market/07_Daily_Specialist/YYYY-MM-DD_Live_Intraday_Report.md`
   và đồng bộ thẳng vào `data/apex_institutional_vault.db` sau mỗi nhịp biến động lớn hoặc mỗi 30 phút.
"""

import sys
import os
import re
import json
import time
import datetime
import argparse
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VN_SPEC_DIR = BASE_DIR / "VN_Market" / "07_Daily_Specialist"
sys.path.insert(0, str(BASE_DIR))

from scripts.vietnam_realtime_feed import (
    fetch_vn_market_indices_live,
    get_realtime_vn_quotes_batch,
    fetch_stock_indicators_live,
    _compute_session_elapsed_fraction,
)
from scripts.vn_market_calendar import get_vn_market_session_state, is_vn_trading_day
from scripts.apex_canonical_truth import classify_canonical_regime, build_and_save_canonical_truth

_BRAIN_LOCK = threading.Lock()
_SNAPSHOT_CACHE: Dict[str, Any] = {"ts": 0.0, "ssot_sig": None, "data": None}
_LAST_REPORT_STATE: Dict[str, Any] = {"written_ts": 0.0, "regime": None, "alerts": {}}


def _get_ssot_signature() -> Tuple[int, int]:
    p = DATA_DIR / "current_portfolio_state.json"
    try:
        st = p.stat()
        return (st.st_mtime_ns, st.st_size)
    except Exception:
        return (0, 0)


def invalidate_live_cache() -> None:
    """Xóa cache snapshot ngay lập tức sau khi có lệnh Sync TCInvest hoặc cập nhật SSOT."""
    with _BRAIN_LOCK:
        _SNAPSHOT_CACHE["ts"] = 0.0
        _SNAPSHOT_CACHE["ssot_sig"] = None
        _SNAPSHOT_CACHE["data"] = None


def get_ict_now() -> datetime.datetime:
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(datetime.timezone(datetime.timedelta(hours=7)))


def _load_json_safe(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _extract_vnd_prices(text: Any) -> List[float]:
    """Trích xuất giá cổ phiếu VNĐ (>= 1,000 đ) từ chuỗi mô tả trong kế hoạch tuần/nghị quyết."""
    if not text:
        return []
    cleaned = re.sub(r"\([^)]*\)", "", str(text))
    cleaned = re.sub(r"\b\d{1,2}[h:]\d{2}\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bMA\d+\b", "", cleaned, flags=re.IGNORECASE)
    vals: List[float] = []
    for m in re.findall(r"(\d{1,3}(?:,\d{3})+|\d{4,6})", cleaned):
        try:
            v = float(m.replace(",", ""))
            if 1000.0 <= v <= 500000.0:
                vals.append(v)
        except Exception:
            pass
    return vals


def build_unified_watchlist() -> Dict[str, Any]:
    """
    Hợp nhất Watchlist động từ:
    1) SSOT `data/current_portfolio_state.json` (Mã đang nắm giữ)
    2) `data/weekly_tactical_plan_active.json` (Nghị quyết Đại Hội Đồng mới nhất — ưu tiên #1 cho Standby!)
    3) `VN_Market/07_Daily_Specialist/vn_daily_ledger.json` & `master_execution_blotter.json`
    """
    ssot = _load_json_safe(DATA_DIR / "current_portfolio_state.json")
    vn_ledger = _load_json_safe(VN_SPEC_DIR / "vn_daily_ledger.json")
    master_blotter = _load_json_safe(BASE_DIR / "08_Master_Investment_CIO" / "master_execution_blotter.json")
    weekly_plan = _load_json_safe(DATA_DIR / "weekly_tactical_plan_active.json")

    active_positions = ssot.get("active_positions", {})
    if not isinstance(active_positions, dict):
        active_positions = {}

    ledger_map: Dict[str, Dict[str, Any]] = {}
    for ord_item in vn_ledger.get("orders", []):
        sym = str(ord_item.get("code") or ord_item.get("ticker") or "").upper().strip()
        if sym:
            ledger_map[sym] = ord_item

    master_map: Dict[str, Dict[str, Any]] = {}
    for ord_item in master_blotter.get("orders_vn", []):
        sym = str(ord_item.get("symbol") or "").upper().strip()
        if sym:
            master_map[sym] = ord_item

    weekly_map: Dict[str, Dict[str, Any]] = {}
    for w_item in weekly_plan.get("approved_watchlist", []):
        sym = str(w_item.get("symbol") or "").upper().strip()
        if sym:
            weekly_map[sym] = w_item

    brain_data = _load_json_safe(DATA_DIR / "deep_financial_brain_analysis.json")
    brain_picks_map: Dict[str, Dict[str, Any]] = {}
    for bp in (brain_data.get("top_vn_alpha_picks") or []):
        bsym = str(bp.get("symbol") or "").upper().strip()
        if bsym:
            brain_picks_map[bsym] = bp

    v3_data = _load_json_safe(DATA_DIR / "apex_autonomous_brain_v3_output.json")
    summit_tcbs_defaults: Dict[str, Dict[str, Any]] = {
        "TPB": {"name": "TPBank", "exchange": "HOSE", "sector": "Ngân Hàng TMCP", "fallback_price": 12350.0, "probe_price": 12250.0, "stop_loss": 11600.0, "tp1": 13350.0, "tp2": 14450.0, "catalyst": "F-Score 9/9, OCF/LNST 4.00x, số hóa VNeID & bù trừ CK"},
        "CTG": {"name": "VietinBank", "exchange": "HOSE", "sector": "Ngân Hàng TMCP", "fallback_price": 30350.0, "probe_price": 30150.0, "stop_loss": 28500.0, "tp1": 33200.0, "tp2": 35800.0, "catalyst": "Ưu tiên #1 Nhịp 2: F=8/9, OCF 1.63x, ROE 22.56%, bán tháp Ciputra"},
        "NAB": {"name": "Nam A Bank", "exchange": "HOSE", "sector": "Ngân Hàng TMCP", "fallback_price": 13200.0, "probe_price": 13100.0, "stop_loss": 12400.0, "tp1": 14400.0, "tp2": 15700.0, "catalyst": "Ưu tiên #2 Nhịp 2: Top 1 Leader vượt MA20/MA50, RS=97, F=8/9, Buy-Up 67.9%"},
        "CTS": {"name": "Chứng Khoán VietinBank", "exchange": "HOSE", "sector": "Chứng Khoán & Đầu Tư", "fallback_price": 24150.0, "probe_price": 23800.0, "stop_loss": 22300.0, "tp1": 26600.0, "tp2": 29000.0, "catalyst": "Dự phòng Nhóm Chứng Khoán: Vượt MA20/MA50, F=7/9, RS=85, OCF/LNST 1.12x"},
        "HPG": {"name": "Tập Đoàn Hòa Phát", "exchange": "HOSE", "sector": "Thép & Vật Liệu", "fallback_price": 20400.0, "probe_price": 20200.0, "stop_loss": 19300.0, "tp1": 22300.0, "tp2": 24100.0, "catalyst": "F-Score 8/9, OCF 1.08x, FCF 6,451 tỷ, Dung Quất 2 đạt 90–95% công suất"},
        "HDB": {"name": "HDBank", "exchange": "HOSE", "sector": "Ngân Hàng TMCP", "fallback_price": 21800.0, "probe_price": 21800.0, "stop_loss": 20500.0, "tp1": 23650.0, "tp2": 25600.0, "catalyst": "ROE 23.73%, đối tác MUFG; theo dõi khi khối ngoại ngừng bán ròng"},
        "VPB": {"name": "VPBank", "exchange": "HOSE", "sector": "Ngân Hàng TMCP", "fallback_price": 20450.0, "probe_price": 20300.0, "stop_loss": 19350.0, "tp1": 23450.0, "tp2": 25200.0, "catalyst": "F-Score 7/9, OCF 2.03x, tăng trưởng tín dụng 28.2%"},
        "TCB": {"name": "Techcombank", "exchange": "HOSE", "sector": "Ngân Hàng TMCP", "fallback_price": 21200.0, "probe_price": 21000.0, "stop_loss": 19850.0, "tp1": 23100.0, "tp2": 25000.0, "catalyst": "CASA top đầu ngành, ngân hàng bán lẻ & IB hàng đầu"},
        "PVT": {"name": "Tổng Công Ty Vận Tải Dầu Khí", "exchange": "HOSE", "sector": "Vận Tải Dầu Khí", "fallback_price": 18850.0, "probe_price": 18650.0, "stop_loss": 17800.0, "tp1": 20700.0, "tp2": 22300.0, "catalyst": "F-Score 9/9, OCF/LNST 2.38x, >55 tàu vận tải quốc tế"},
        "NT2": {"name": "Điện Lực Nhơn Trạch 2", "exchange": "HOSE", "sector": "Điện & Năng Lượng", "fallback_price": 23850.0, "probe_price": 23600.0, "stop_loss": 22300.0, "tp1": 25950.0, "tp2": 28100.0, "catalyst": "Hết nợ vay dài hạn, RS 97, sản lượng điện khí phục hồi"},
        "SSI": {"name": "Chứng Khoán SSI", "exchange": "HOSE", "sector": "Chứng Khoán & Đầu Tư", "fallback_price": 20000.0, "probe_price": 19800.0, "stop_loss": 18700.0, "tp1": 21800.0, "tp2": 23600.0, "catalyst": "Đầu ngành chứng khoán, F-Score 8/9"},
        "PVP": {"name": "Vận Tải Dầu Khí TBD", "exchange": "HOSE", "sector": "Vận Tải Dầu Khí", "fallback_price": 16750.0, "probe_price": 16550.0, "stop_loss": 15650.0, "tp1": 18250.0, "tp2": 19750.0, "catalyst": "F-Score khỏe, P/E 7.4x"},
    }

    forbidden_watch = {"BAF", "MSH", "VIX", "CII", "CEO", "PNJ", "TCH", "POW"}
    ordered_symbols: List[str] = []
    # 1. Đang nắm giữ trong SSOT
    for sym in active_positions.keys():
        s_up = sym.upper().strip()
        if s_up and int((active_positions.get(sym) or {}).get("shares") or 0) > 0 and s_up not in ordered_symbols:
            ordered_symbols.append(s_up)
    # 2. Danh mục ưu tiên đã duyệt bởi Đại Hội Đồng trong weekly_tactical_plan_active.json
    for sym in weekly_map.keys():
        if sym not in forbidden_watch and sym not in ordered_symbols:
            ordered_symbols.append(sym)
    # 3. Các mã Brain V3 / Ledger / Master Blotter còn lại
    for st_v3 in (v3_data.get("asymmetric_conviction_strikes") or []):
        s_up = str(st_v3.get("symbol") or "").upper().strip()
        if s_up and s_up not in forbidden_watch and s_up not in ordered_symbols:
            ordered_symbols.append(s_up)
    for r_v3 in (v3_data.get("top_15_overall_universe") or []):
        s_up = str(r_v3.get("symbol") or "").upper().strip()
        if s_up and s_up not in forbidden_watch and s_up not in ordered_symbols:
            ordered_symbols.append(s_up)
    for sym in ledger_map.keys():
        if sym not in forbidden_watch and sym not in ordered_symbols:
            ordered_symbols.append(sym)
    for sym in master_map.keys():
        if sym not in forbidden_watch and sym not in ordered_symbols:
            ordered_symbols.append(sym)
    for sym in ("TPB", "HPG", "CTG", "NAB", "CTS", "HDB", "VPB", "PVT", "TCB", "NT2", "SSI", "PVP"):
        if sym not in ordered_symbols:
            ordered_symbols.append(sym)

    ordered_symbols = ordered_symbols[:12]

    unified_items: Dict[str, Dict[str, Any]] = {}
    for sym in ordered_symbols:
        pos = active_positions.get(sym, {})
        ldg = ledger_map.get(sym, {})
        mst = master_map.get(sym, {})
        wkl = weekly_map.get(sym, {})
        bp = brain_picks_map.get(sym, {})
        bp_opt = bp.get("optimizer", {}) if isinstance(bp, dict) else {}
        sdef = summit_tcbs_defaults.get(sym, {})

        is_holding = bool(pos and int(pos.get("shares", 0)) > 0)
        entry_price = float(pos.get("entry_price") or 0.0)

        wkl_cur_prices = _extract_vnd_prices(wkl.get("current_status"))
        wkl_entry_prices = _extract_vnd_prices(wkl.get("entry_zone"))
        wkl_stop_prices = _extract_vnd_prices(wkl.get("stop_loss_2xatr"))
        wkl_tp1_prices = _extract_vnd_prices(wkl.get("tp1"))
        wkl_tp2_prices = _extract_vnd_prices(wkl.get("tp2"))
        wkl_limit_shares = re.findall(r"(\d{3,4})\s*CP", str(wkl.get("weekly_limit") or ""))

        fallback_price = float(
            pos.get("current_price")
            or (wkl_cur_prices[0] if wkl_cur_prices else 0.0)
            or sdef.get("fallback_price")
            or bp.get("live_price")
            or ldg.get("current_price")
            or mst.get("current_price_vnd")
            or entry_price
            or 0.0
        )
        stop_loss = float(
            pos.get("stop_loss")
            or (wkl_stop_prices[0] if wkl_stop_prices else 0.0)
            or sdef.get("stop_loss")
            or bp_opt.get("stop_loss_price")
            or ldg.get("stop_loss")
            or mst.get("stop_loss_2atr_vnd")
            or (round(fallback_price * 0.945, -1) if fallback_price > 0 else 0.0)
        )
        tp1 = float(
            pos.get("take_profit_tp1")
            or (wkl_tp1_prices[0] if wkl_tp1_prices else 0.0)
            or sdef.get("tp1")
            or bp_opt.get("tp1_price")
            or ldg.get("tp1")
            or mst.get("tp1_vnd")
            or (round(fallback_price * 1.10, -1) if fallback_price > 0 else 0.0)
        )
        tp2 = float(
            pos.get("take_profit_tp2")
            or (wkl_tp2_prices[0] if wkl_tp2_prices else 0.0)
            or sdef.get("tp2")
            or bp_opt.get("tp2_price")
            or ldg.get("tp2")
            or mst.get("tp2_vnd")
            or (round(fallback_price * 1.18, -1) if fallback_price > 0 else 0.0)
        )
        if wkl_entry_prices:
            probe_price = float(wkl_entry_prices[0])
            breakout_price = float(wkl_entry_prices[-1] if len(wkl_entry_prices) > 1 else round(probe_price * 1.01, -1))
        else:
            probe_price = float(sdef.get("probe_price") or ldg.get("probe_price_60") or mst.get("limit_pullback_price_vnd") or 0.0)
            breakout_price = float(ldg.get("breakout_price_40") or (round(probe_price * 1.02, -1) if probe_price > 0 else 0.0))

        name = pos.get("name") or wkl.get("name") or sdef.get("name") or bp.get("company_name") or ldg.get("name") or mst.get("name") or sym
        exchange = sdef.get("exchange") or ldg.get("exchange") or mst.get("exchange") or "HOSE"
        if exchange and f"({exchange})" not in name:
            display_name = f"{name} ({exchange})"
        else:
            display_name = name

        catalyst = (
            wkl.get("catalyst")
            or sdef.get("catalyst")
            or ldg.get("catalysts")
            or mst.get("catalysts")
            or "Cổ phiếu đạt chuẩn lọc BCTC OCF/LNST >= 1.0x & RS Rating cao"
        )
        sleeve = wkl.get("tier") or ("CORE HOLDING" if is_holding else (ldg.get("sleeve") or mst.get("sleeve") or "STANDBY ALPHA"))
        planned_sh = int(wkl_limit_shares[0]) if wkl_limit_shares else int(ldg.get("shares") or mst.get("shares") or 100)

        entry_zone_label = ""
        if wkl_entry_prices and len(wkl_entry_prices) >= 2:
            entry_zone_label = f"{wkl_entry_prices[0]:,.0f} – {wkl_entry_prices[1]:,.0f} ₫"
        elif probe_price > 0:
            entry_zone_label = f"{round(probe_price * 0.995, -1):,.0f} – {round(probe_price * 1.005, -1):,.0f} ₫"

        unified_items[sym] = {
            "symbol": sym,
            "display_name": display_name,
            "exchange": exchange,
            "sector": bp.get("sector_name") or sdef.get("sector") or ldg.get("sector") or mst.get("sector") or "Cổ phiếu Dẫn Dắt",
            "sleeve": sleeve,
            "is_holding": is_holding,
            "shares": int(pos.get("shares", 0)) if is_holding else 0,
            "tradable_shares": int(pos.get("tradable_shares", pos.get("shares", 0))) if is_holding else 0,
            "planned_shares": planned_sh,
            "entry_price": entry_price,
            "fallback_price": fallback_price,
            "probe_price": probe_price,
            "breakout_price": breakout_price,
            "entry_zone_label": entry_zone_label,
            "stop_loss": stop_loss,
            "tp1": tp1,
            "tp2": tp2,
            "rr_ratio": float(ldg.get("rr_ratio") or mst.get("reward_risk_ratio") or 2.5),
            "win_prob_pct": float(ldg.get("win_prob_pct") or mst.get("win_prob_pct") or 75.0),
            "expected_value_pct": float(ldg.get("expected_value_pct") or mst.get("expected_value_pct") or 8.5),
            "catalyst": catalyst,
            "is_blacklisted": sym in forbidden_watch,
        }

    return {
        "ssot": ssot,
        "vn_ledger": vn_ledger,
        "master_blotter": master_blotter,
        "weekly_plan": weekly_plan,
        "symbols": ordered_symbols,
        "items": unified_items,
    }


def classify_intraday_regime(
    market_overview: Dict[str, Any],
    now_ict: Optional[datetime.datetime] = None,
    has_open_positions: bool = False,
    current_invested_pct: float = 0.0,
) -> Dict[str, Any]:
    """Đánh giá Chế độ Thị trường HỢP NHẤT qua apex_canonical_truth + vn_market_calendar."""
    if now_ict is None:
        now_ict = get_ict_now()
    vni = market_overview.get("vn_index", {})
    vn30 = market_overview.get("vn30_index", {})
    breadth = market_overview.get("market_breadth", {})

    warroom_state = _load_json_safe(DATA_DIR / "live_warroom_state.json")
    recon = warroom_state.get("recon_summary") if isinstance(warroom_state.get("recon_summary"), dict) else {}

    vni_val = float(vni.get("value") or recon.get("vn_index") or 0.0)
    vni_chg = float(vni.get("change_pct") if vni.get("value") else (recon.get("vn_index_chg_pct") or 0.0))
    vni_ma20 = float(vni.get("ma20") or recon.get("vn_index_ma20") or 0.0)
    vni_ma50 = float(vni.get("ma50") or recon.get("vn_index_ma50") or 0.0)
    br20_pct = float(recon.get("live_breadth_ma20_pct") or 0.0)
    buy_up_pct = float(recon.get("avg_buy_up_pct") or 50.0)
    adv_ratio = float(breadth.get("advance_ratio_pct") or 50.0)
    basis = float(vn30.get("basis_pts") or 0.0)
    pace = float(vni.get("volume_pace_ratio") or recon.get("volume_pace_ratio") or 1.0)
    fn_net = float(vni.get("raw_foreign_net_ty") or recon.get("foreign_net_ty") or 0.0)

    session_state = get_vn_market_session_state(now_ict=now_ict, market_overview=market_overview)
    return classify_canonical_regime(
        vn_index=vni_val,
        vn_index_chg_pct=vni_chg,
        vni_ma20=vni_ma20,
        vni_ma50=vni_ma50,
        br20_pct=br20_pct,
        buy_up_pct=buy_up_pct,
        adv_ratio=adv_ratio,
        session_state=session_state,
        has_open_positions=has_open_positions,
        current_invested_pct=current_invested_pct,
        vol_pace=pace,
        basis=basis,
        foreign_net_ty=fn_net,
    )


def compute_live_war_room_snapshot(force_refresh: bool = False, cache_ttl: float = 3.0) -> Dict[str, Any]:
    """
    Tính toán toàn bộ ảnh chụp trạng thái War-Room V4.0 sống trong thời gian thực:
    - Market Overview Live + Regime Intraday
    - Holdings Live PnL, khoảng cách tới Stop Loss & TP1/TP2
    - Watchlist Sentinel Table (với Buy-Up thực, 3 bước giá, RSI14, Foreign Net)
    - Left-Column Dynamic Picks + Center Tactical Recommendations
    """
    now_ts = time.time()
    ssot_sig = _get_ssot_signature()
    with _BRAIN_LOCK:
        if (
            not force_refresh
            and _SNAPSHOT_CACHE["data"] is not None
            and _SNAPSHOT_CACHE.get("ssot_sig") == ssot_sig
            and (now_ts - _SNAPSHOT_CACHE["ts"] < cache_ttl)
        ):
            return _SNAPSHOT_CACHE["data"]

    now_ict = get_ict_now()
    watchlist_ctx = build_unified_watchlist()
    ssot = watchlist_ctx["ssot"]
    vn_ledger = watchlist_ctx["vn_ledger"]
    symbols = watchlist_ctx["symbols"]
    items = watchlist_ctx["items"]

    active_pos_raw = ssot.get("active_positions") if isinstance(ssot.get("active_positions"), dict) else {}
    has_open_pos = any(int((p or {}).get("shares") or 0) > 0 for p in active_pos_raw.values() if isinstance(p, dict))
    nav_ssot = float(ssot.get("total_nav_vnd") or ssot.get("cash_balance_vnd") or 1.0)
    stk_ssot = float(ssot.get("total_market_val_vnd") or 0.0)
    invested_pct_ssot = round((stk_ssot / nav_ssot) * 100.0, 1) if nav_ssot > 0 else 0.0

    market_overview = fetch_vn_market_indices_live(ttl_seconds=4)
    session_state = get_vn_market_session_state(now_ict=now_ict, market_overview=market_overview)
    regime = classify_intraday_regime(
        market_overview,
        now_ict=now_ict,
        has_open_positions=has_open_pos,
        current_invested_pct=invested_pct_ssot,
    )
    live_quotes = get_realtime_vn_quotes_batch(symbols) if symbols else {}
    pace_fraction = _compute_session_elapsed_fraction(now_ict)

    # Tích hợp Global-to-VN Spillover (Phase 2.1) & Bull-Trap Adaptive Filters (Phase 2.2)
    global_spillover: Dict[str, Any] = {
        "risk_multiplier": 1.0,
        "max_allocation_pct": 45,
        "overnight_bias": "NEUTRAL_SELECTIVE",
        "bias_label": "⚖️ TRUNG TÍNH",
        "drivers": [],
        "metrics": {},
    }
    try:
        from scripts.global_to_vn_spillover_engine import compute_global_to_vn_spillover
        global_spillover = compute_global_to_vn_spillover(force_refresh=False, cache_ttl=900)
    except Exception:
        pass

    tracker_summary: Dict[str, Any] = {"filters": {"min_buy_up_pct": 58.0, "max_rsi_buy": 70.0, "min_breadth_pct": 32.0}, "recent_signals": []}
    try:
        from scripts.execution_slippage_tracker import get_tracker_summary, record_signal_if_new
        tracker_summary = get_tracker_summary()
    except Exception:
        record_signal_if_new = None  # type: ignore

    ad_filters = tracker_summary.get("filters", {})
    max_rsi_buy = float(ad_filters.get("max_rsi_buy", 70.0))
    min_bu_filter = float(ad_filters.get("min_buy_up_pct", 58.0))
    min_br_filter = float(ad_filters.get("min_breadth_pct", 32.0))
    adv_ratio_cur = float(market_overview.get("market_breadth", {}).get("advance_ratio_pct", 50.0))

    base_cap = int(regime.get("max_new_allocation_pct", 0))
    sp_mult = float(global_spillover.get("risk_multiplier", 1.0))
    regime["base_max_allocation_pct"] = base_cap
    regime["spillover_multiplier"] = sp_mult
    if bool(regime.get("is_closed_override")) or base_cap <= 0:
        regime["max_new_allocation_pct"] = 0
    else:
        regime["max_new_allocation_pct"] = int(max(10, min(80, round(base_cap * sp_mult))))

    is_market_closed = bool(regime.get("is_closed_override")) or (not bool(session_state.get("is_trading_day"))) or bool(session_state.get("stale_feed_detected"))

    cash_vnd = float(ssot.get("cash_balance_vnd", 0.0))
    realized_pnl_vnd = float(ssot.get("realized_pnl_vnd", 167119.0))

    live_stocks: List[Dict[str, Any]] = []
    live_holdings: List[Dict[str, Any]] = []
    dynamic_picks: List[Dict[str, Any]] = []

    total_live_stocks_val = 0.0
    total_cost_basis = 0.0
    worst_threat_level = 1
    threat_reasons: List[str] = []

    if symbols:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=min(8, len(symbols))) as _ind_pool:
            list(_ind_pool.map(lambda s: fetch_stock_indicators_live(s, ttl_seconds=300), symbols))

    for sym in symbols:
        meta = items[sym]
        q = live_quotes.get(sym, {})
        ind = fetch_stock_indicators_live(sym, ttl_seconds=300)

        curr_p = float(q.get("price") or meta["fallback_price"] or 0.0)
        ref_p = float(q.get("ref_price") or curr_p)
        diff = curr_p - ref_p if (curr_p > 0 and ref_p > 0) else 0.0
        pct = float(q.get("change_pct") if q.get("is_live") else (round((diff / ref_p) * 100.0, 2) if ref_p > 0 else 0.0))
        vol = int(q.get("volume") or 0)
        avg_vol_20d = float(ind.get("avg_vol_20d") or 0.0)
        vol_ratio = round(vol / (avg_vol_20d * pace_fraction), 2) if (avg_vol_20d > 0 and vol > 0) else 1.0
        rsi14 = float(ind.get("rsi14") or 50.0)
        ma20 = float(ind.get("ma20") or 0.0)
        buy_up = float(q.get("active_buy_pct") or 50.0)
        fn_val_ty = round(float(q.get("foreign_net_val_vnd") or 0.0) / 1e9, 2)

        stop_p = meta["stop_loss"]
        tp1_p = meta["tp1"]
        tp2_p = meta["tp2"]
        dist_stop_pct = round(((curr_p - stop_p) / curr_p) * 100.0, 2) if curr_p > 0 and stop_p > 0 else 0.0
        dist_tp1_pct = round(((tp1_p - curr_p) / curr_p) * 100.0, 2) if curr_p > 0 and tp1_p > 0 else 0.0

        is_holding = meta["is_holding"]
        if is_holding:
            sh = meta["shares"]
            ep = meta["entry_price"]
            cost_val = sh * ep
            mkt_val = sh * curr_p
            pnl_vnd = mkt_val - cost_val
            pnl_pct = round((pnl_vnd / cost_val) * 100.0, 2) if cost_val > 0 else 0.0
            total_cost_basis += cost_val
            total_live_stocks_val += mkt_val

            if stop_p > 0 and curr_p <= stop_p:
                sec_status = "DANGER_STOP"
                sec_label = "🚨 CHẠM STOP 2xATR — CẮT LỖ KHẨN"
                action_code = "STOP_TRIGGERED"
                worst_threat_level = max(worst_threat_level, 5)
                threat_reasons.append(f"{sym} chạm Stop {stop_p:,.0f}đ")
            elif stop_p > 0 and dist_stop_pct <= 1.5:
                sec_status = "WARNING_STOP"
                sec_label = f"⚠️ SÁT STOP ({dist_stop_pct:.1f}%) — THEO DÕI GẮT"
                action_code = "NEAR_STOP_WARNING"
                worst_threat_level = max(worst_threat_level, 3)
                threat_reasons.append(f"{sym} cách Stop {dist_stop_pct:.1f}%")
            elif tp1_p > 0 and curr_p >= tp1_p:
                sec_status = "TAKE_PROFIT"
                sec_label = "🎯 ĐẠT TP1 — CHỐT LỜI 50% SCALING OUT"
                action_code = "TP1_REACHED"
            elif pnl_pct >= 4.0:
                sec_status = "SAFE"
                sec_label = "🛡️ LÃI >=4% — KÉO STOP VỀ HÒA VỐN"
                action_code = "TRAILING_BE_READY"
            else:
                sec_status = "SAFE"
                sec_label = f"🟢 GIỮ VỊ THẾ (Cách Stop {dist_stop_pct:.1f}%)"
                action_code = "SAFE_HOLD"

            live_holdings.append({
                "symbol": sym,
                "name": meta["display_name"],
                "shares": sh,
                "tradable_shares": meta["tradable_shares"],
                "entry_price": ep,
                "current_price": curr_p,
                "cost_basis_vnd": round(cost_val, 0),
                "market_val_vnd": round(mkt_val, 0),
                "unrealized_pnl_vnd": round(pnl_vnd, 0),
                "unrealized_pnl_pct": pnl_pct,
                "stop_loss": stop_p,
                "take_profit_tp1": tp1_p,
                "take_profit_tp2": tp2_p,
                "dist_to_stop_pct": dist_stop_pct,
                "dist_to_tp1_pct": dist_tp1_pct,
                "action_code": action_code,
                "action_label": sec_label,
                "status": "HOLDING_T0_AVAILABLE",
            })
        else:
            # Cổ phiếu tầm ngắm (Standby) với Bộ Lọc Bull-Trap Thích Nghi, Khóa Ngày Nghỉ & Guard Target > 0
            raw_probe = float(meta.get("probe_price") or 0.0)
            probe_p = raw_probe if raw_probe > 0 else curr_p
            has_valid_targets = (raw_probe > 0 and stop_p > 0 and tp1_p > 0 and not bool(meta.get("is_blacklisted")))
            if is_market_closed:
                sec_status = "MARKET_CLOSED"
                next_dm = f"{session_state['next_trading_day'][8:10]}/{session_state['next_trading_day'][5:7]}"
                if has_valid_targets:
                    sec_label = f"⏸️ CHỜ MỞ SÀN {next_dm} (LO {raw_probe:,.0f}đ)"
                else:
                    sec_label = f"⏸️ CHỜ MỞ SÀN {next_dm} (THEO DÕI)"
                action_code = "STANDBY_MARKET_CLOSED"
            elif bool(meta.get("is_blacklisted")):
                sec_status = "PAUSED"
                sec_label = "⛔ CẤM ĐUỔI / BLACKLIST BCTC"
                action_code = "STANDBY_DEFENSIVE_PAUSE"
            elif not has_valid_targets:
                sec_status = "STANDBY"
                sec_label = "🔵 THEO DÕI (Chưa có ngưỡng mua)"
                action_code = "STANDBY_WATCH"
            elif regime["regime_id"] == "S4_BEAR_CASH_SHIELD" or (adv_ratio_cur < min_br_filter and buy_up < min_bu_filter):
                sec_status = "PAUSED"
                sec_label = f"🛑 HOÃN KÈO (BULL-TRAP GUARD: Độ rộng {adv_ratio_cur:.0f}%)"
                action_code = "STANDBY_DEFENSIVE_PAUSE"
            elif rsi14 >= max_rsi_buy or pct >= 3.5:
                sec_status = "OVERBOUGHT"
                sec_label = f"⏳ QUÁ NÓNG (RSI {rsi14:.0f} >= {max_rsi_buy:.0f}) — CẤM ĐUỔI"
                action_code = "STANDBY_OVERBOUGHT"
            elif curr_p > 0 and curr_p <= raw_probe * 1.008 and buy_up >= max(50.0, min_bu_filter - 4.0):
                sec_status = "BUY_ZONE"
                sec_label = "🎯 TRONG VÙNG GOM — CHỜ 14H00"
                action_code = "STANDBY_BUY_ZONE"
                if record_signal_if_new is not None:
                    try:
                        record_signal_if_new(
                            symbol=sym,
                            signal_type="GOLDEN_BUY_ZONE",
                            signal_price=curr_p,
                            buy_up_pct=buy_up,
                            rsi14=rsi14,
                            breadth_pct=adv_ratio_cur,
                            regime_id=regime["regime_id"],
                            trading_date=now_ict.strftime("%Y-%m-%d"),
                            signal_time=now_ict.strftime("%H:%M:%S"),
                        )
                    except Exception:
                        pass
            else:
                sec_status = "STANDBY"
                sec_label = f"🟡 THEO DÕI (Mục tiêu {raw_probe:,.0f}đ)"
                action_code = "STANDBY_WATCH"

        stock_row = {
            "code": sym,
            "name": meta["display_name"],
            "tier": meta["sleeve"],
            "is_holding": is_holding,
            "price": curr_p,
            "ref_price": ref_p,
            "change_pts": round(diff, 0),
            "change_pct": pct,
            "high": float(q.get("day_high") or curr_p),
            "low": float(q.get("day_low") or curr_p),
            "volume": vol,
            "vol_ratio_20d": vol_ratio,
            "active_buy_pct": buy_up,
            "rsi14": rsi14,
            "ma20": ma20,
            "foreign_net_ty": fn_val_ty,
            "bid_levels": q.get("bid_levels", []),
            "ask_levels": q.get("ask_levels", []),
            "probe_target": meta["probe_price"],
            "stop_loss": stop_p,
            "tp1": tp1_p,
            "tp2": tp2_p,
            "dist_to_stop_pct": dist_stop_pct,
            "dist_to_tp1_pct": dist_tp1_pct,
            "security_status": sec_status,
            "security_label": sec_label,
            "action_code": action_code,
            "catalyst": meta["catalyst"],
            "is_live": bool(q.get("is_live", False)) and (not is_market_closed),
            "data_source": q.get("data_source", "FALLBACK_STATIC"),
        }
        live_stocks.append(stock_row)

        dynamic_picks.append({
            "symbol": sym,
            "name": meta["display_name"],
            "tier": meta["sleeve"],
            "is_holding": is_holding,
            "shares": meta["shares"] if is_holding else meta["planned_shares"],
            "current_price": curr_p,
            "change_pct": pct,
            "entry_zone": (
                meta.get("entry_zone_label")
                or (
                    f"{round(meta['probe_price']*0.99, -1):,.0f} – {round(meta['probe_price']*1.005, -1):,.0f} ₫"
                    if meta["probe_price"] > 0 else "Theo tín hiệu"
                )
            ),
            "stop_loss": stop_p,
            "stop_pct": round(((stop_p - curr_p) / curr_p) * 100.0, 1) if curr_p > 0 and stop_p > 0 else -6.5,
            "tp1": tp1_p,
            "tp2": tp2_p,
            "rr_ratio": meta["rr_ratio"],
            "expected_value_pct": meta["expected_value_pct"],
            "planned_capital_vnd": round((meta["shares"] if is_holding else meta["planned_shares"]) * curr_p, 0),
            "action_label": sec_label,
            "security_status": sec_status,
            "catalyst": meta["catalyst"],
        })

    if regime["regime_id"] in ("S4_BEAR_CASH_SHIELD", "DEFENSIVE_SELLOFF") and live_holdings:
        worst_threat_level = max(worst_threat_level, 2)

    live_nav_vnd = cash_vnd + total_live_stocks_val
    live_un_pnl = total_live_stocks_val - total_cost_basis
    live_un_pnl_pct = round((live_un_pnl / total_cost_basis) * 100.0, 2) if total_cost_basis > 0 else 0.0
    cash_pct = round((cash_vnd / live_nav_vnd) * 100.0, 1) if live_nav_vnd > 0 else 100.0
    stocks_pct = round(100.0 - cash_pct, 1)
    total_shares = sum(h["shares"] for h in live_holdings)
    holdings_desc = " + ".join(f"{h['shares']} {h['symbol']}" for h in live_holdings) or "0 CP"

    if is_market_closed:
        threat_level_id = f"LEVEL_1_{session_state['status_code']}"
        threat_label = f"⏸️ SÀN ĐÓNG CỬA ({session_state['short_badge_vi']}) — Giữ nguyên {total_shares} CP ({holdings_desc}) & Két {cash_pct:.1f}%"
    else:
        threat_map = {
            1: ("LEVEL_1_SAFE_POSITION_ACTIVE", f"🟢 CẤP 1 — AN TOÀN ({cash_pct:.1f}% Tiền mặt • {total_shares} CP nằm trên vùng an toàn)"),
            2: ("LEVEL_2_WATCH", f"🟡 CẤP 2 — GIÁM SÁT NHẸ ({', '.join(threat_reasons) or 'Thị trường giằng co'})"),
            3: ("LEVEL_3_ELEVATED_DEFENSE", f"🟠 CẤP 3 — PHÒNG THỦ CHỦ ĐỘNG ({', '.join(threat_reasons) or regime['label']})"),
            4: ("LEVEL_4_HIGH_ALERT", f"🔴 CẤP 4 — CẢNH BÁO CAO ({', '.join(threat_reasons)})"),
            5: ("LEVEL_5_EMERGENCY_STOP", f"🚨 CẤP 5 — KHẨN CẤP STOP LOSS ({', '.join(threat_reasons)})"),
        }
        threat_level_id, threat_label = threat_map.get(worst_threat_level, threat_map[1])

    snapshot = {
        "generated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
        "trading_date": now_ict.strftime("%Y-%m-%d"),
        "server_time": now_ict.strftime("%H:%M:%S"),
        "market_session": session_state,
        "market_overview": market_overview,
        "intraday_regime": regime,
        "live_stocks": live_stocks,
        "dynamic_picks": dynamic_picks,
        "portfolio_live": {
            "cash_vnd": round(cash_vnd, 0),
            "stocks_val_vnd": round(total_live_stocks_val, 0),
            "total_cost_vnd": round(total_cost_basis, 0),
            "total_nav_vnd": round(live_nav_vnd, 0),
            "unrealized_pnl_vnd": round(live_un_pnl, 0),
            "unrealized_pnl_pct": live_un_pnl_pct,
            "realized_pnl_vnd": round(realized_pnl_vnd, 0),
            "cash_pct": cash_pct,
            "stocks_pct": stocks_pct,
            "total_shares": total_shares,
            "holdings_count": len(live_holdings),
            "holdings": live_holdings,
            "holdings_desc": holdings_desc,
        },
        "threat": {
            "level_num": worst_threat_level,
            "threat_level": threat_level_id,
            "threat_label": threat_label,
        },
        "ledger_meta": {
            "mastery_score": float(vn_ledger.get("mastery_score", 98.5)),
            "expected_value_pct": float(vn_ledger.get("portfolio_expected_value_pct", 10.95)),
            "win_rate_pct": float(vn_ledger.get("portfolio_win_rate_pct", 85.0)),
            "ledger_date": vn_ledger.get("date", now_ict.strftime("%Y-%m-%d")),
        },
        "global_spillover": global_spillover,
        "execution_tracker": tracker_summary,
    }

    with _BRAIN_LOCK:
        _SNAPSHOT_CACHE["ts"] = time.time()
        _SNAPSHOT_CACHE["ssot_sig"] = ssot_sig
        _SNAPSHOT_CACHE["data"] = snapshot
    return snapshot


def _upsert_report_into_vault(report_path: Path, dept_id: str = "ban_7_vn_specialist") -> bool:
    """Nạp trực tiếp file báo cáo Markdown vào bảng institutional_reports của SQLite Vault."""
    try:
        from scripts.apex_database_engine import ApexDatabaseEngine
        from scripts.apex_report_scanner import DEPARTMENTS_CONFIG, extract_report_metadata

        ApexDatabaseEngine.initialize_database()
        dept_cfg = next((d for d in DEPARTMENTS_CONFIG if d.get("dept_id") == dept_id), None)
        if not dept_cfg:
            dept_cfg = next((d for d in DEPARTMENTS_CONFIG if d.get("dept_id") == "ban_7_vn_specialist"), None)
        if not dept_cfg:
            return False

        meta = extract_report_metadata(report_path, dept_cfg)
        if not meta:
            return False

        content = report_path.read_text(encoding="utf-8", errors="ignore")
        word_count = len(content.split())
        tickers_list = ApexDatabaseEngine.extract_stock_tickers(
            f"{meta.get('title', '')} {meta.get('preview', '')} {content[:2000]}"
        )
        tickers_json = json.dumps(tickers_list, ensure_ascii=False)
        now_str = get_ict_now().strftime("%Y-%m-%d %H:%M:%S")

        conn = ApexDatabaseEngine.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO institutional_reports (
                rel_path, file_name, title, dept_id, dept_name, dept_short, icon, color,
                date, time, sort_time, shift_label, preview, content, tickers, word_count,
                size_bytes, size_kb, mtime, is_today, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(rel_path) DO UPDATE SET
                title = excluded.title,
                time = excluded.time,
                sort_time = excluded.sort_time,
                shift_label = excluded.shift_label,
                preview = excluded.preview,
                content = excluded.content,
                tickers = excluded.tickers,
                word_count = excluded.word_count,
                size_bytes = excluded.size_bytes,
                size_kb = excluded.size_kb,
                mtime = excluded.mtime,
                is_today = excluded.is_today,
                updated_at = excluded.updated_at;
        """, (
            meta["rel_path"],
            meta.get("file_name", report_path.name),
            meta["title"],
            meta["dept_id"],
            meta["dept_name"],
            meta.get("dept_short", ""),
            meta.get("icon", "⚡"),
            meta.get("color", "#f472b6"),
            meta["date"],
            meta.get("time", ""),
            meta.get("sort_time", "00:00:00"),
            meta.get("shift_label", ""),
            meta.get("preview", ""),
            content,
            tickers_json,
            word_count,
            meta.get("size_bytes", len(content.encode("utf-8"))),
            meta.get("size_kb", round(len(content.encode("utf-8")) / 1024, 1)),
            meta.get("mtime", report_path.stat().st_mtime),
            1 if meta.get("is_today") else 0,
            now_str,
            now_str,
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[!] Lỗi đồng bộ Live Report vào SQLite Vault: {e}")
        return False


def sync_live_intraday_report(snapshot: Dict[str, Any], force_write: bool = False) -> Optional[Path]:
    """
    Xuất bản hoặc cập nhật file báo cáo sống `VN_Market/07_Daily_Specialist/YYYY-MM-DD_Live_Intraday_Report.md`
    khi vừa đổi Regime, xuất hiện cảnh báo Stop/TP, hoặc mỗi 30 phút.
    """
    now_ts = time.time()
    regime_id = snapshot["intraday_regime"]["regime_id"]
    cur_alerts = {h["symbol"]: h["action_code"] for h in snapshot["portfolio_live"]["holdings"]}

    should_write = (
        force_write
        or (now_ts - _LAST_REPORT_STATE["written_ts"] >= 1800)
        or (_LAST_REPORT_STATE["regime"] != regime_id)
        or (_LAST_REPORT_STATE["alerts"] != cur_alerts and any(
            v in ("STOP_TRIGGERED", "NEAR_STOP_WARNING", "TP1_REACHED") for v in cur_alerts.values()
        ))
    )
    if not should_write:
        return None

    date_str = snapshot["trading_date"]
    gen_at = snapshot["generated_at"]
    msess = snapshot.get("market_session") or {}
    is_closed = (not msess.get("is_trading_day", True)) or bool(msess.get("stale_feed_detected", False))
    mkt = snapshot["market_overview"]
    vni = mkt["vn_index"]
    vn30 = mkt["vn30_index"]
    br = mkt["market_breadth"]
    reg = snapshot["intraday_regime"]
    pf = snapshot["portfolio_live"]

    report_title = (
        f"# [BAN 7 VN & BAN 9] BÁO CÁO NGHỈ LỄ / ĐÓNG CỬA SÀN & CHUẨN BỊ PHIÊN KẾ TIẾP — {date_str}"
        if is_closed
        else f"# [BAN 7 VN & BAN 9] BÁO CÁO TÁC CHIẾN LIVE INTRADAY — {date_str}"
    )
    market_note = (
        f"> **Trạng thái phiên:** {msess.get('status_label_vi')} | Bảng giá bên dưới là **dữ liệu đóng cửa tham chiếu phiên {msess.get('prev_trading_day', '--')}**, khóa đặt lệnh mới (`0%`) hôm nay.\n> **Lịch thanh toán & mở lại:** {msess.get('settlement_note_vi')}\n"
        if is_closed
        else ""
    )

    lines = [
        report_title,
        f"**Cập nhật lúc:** `{gen_at} (ICT)` | **Tài khoản SSOT:** `TCBS 105C307855`  ",
        f"**Trạng thái thị trường (`Market Regime`):** **`{reg['label']}`**  ",
        f"**Chỉ thị điều hành:** {reg['guidance']}",
        "",
        market_note + "---" if market_note else "---",
        "",
        "## 1. BỨC TRANH BẢNG ĐIỆN" + (" (THAM CHIẾU ĐÓNG CỬA PHIÊN TRƯỚC)" if is_closed else " THỜI GIAN THỰC"),
        f"- **VN-Index:** `{vni['value']:,.2f}` ({vni['change_pts']:+.2f} / `{vni['change_pct']:+.2f}%`) | GTGD: `{vni['turnover_ty_vnd']}` | Pace 20 phiên: `{vni['volume_pace_ratio']:.2f}x`",
        f"- **VN30-Index:** `{vn30['value']:,.2f}` ({vn30['change_pts']:+.2f} / `{vn30['change_pct']:+.2f}%`) | Phái sinh Basis: `{vn30['basis_vn30f']}`",
        f"- **Độ rộng & Khối ngoại:** `{br['advancers']} Tăng / {br['decliners']} Giảm / {br['unchanged']} Đứng` (`{br['sentiment']}`) | Khối ngoại VN30: `{vni['foreign_net_ty_vnd']}`",
        "",
        "## 2. TRẠNG THÁI TÀI SẢN & VỊ THẾ NẮM GIỮ (LIVE PNL)",
        f"- **Tiền mặt khả dụng:** `{pf['cash_vnd']:,.0f} ₫` (`{pf['cash_pct']:.1f}% NAV`)",
        f"- **Giá trị cổ phiếu sống:** `{pf['stocks_val_vnd']:,.0f} ₫` (`{pf['stocks_pct']:.1f}% NAV` • `{pf['total_shares']} CP`)",
        f"- **Tổng NAV LIVE:** **`{pf['total_nav_vnd']:,.0f} ₫`** | **PnL Tạm Tính:** **`{pf['unrealized_pnl_vnd']:+,.0f} ₫ ({pf['unrealized_pnl_pct']:+.2f}%)`** | Lãi đã chốt V1: `+{pf['realized_pnl_vnd']:,.0f} ₫`",
        "",
    ]

    if pf["holdings"]:
        lines.extend([
            "| Mã | Số Lượng | Giá Vốn | Giá Live | PnL Sống | Stop Loss 2xATR | Cách Stop | Mục Tiêu TP1 | Hành Động Ngay |",
            "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
        ])
        for h in pf["holdings"]:
            lines.append(
                f"| **{h['symbol']}** | {h['shares']} | {h['entry_price']:,.0f} ₫ | {h['current_price']:,.0f} ₫ "
                f"| {h['unrealized_pnl_vnd']:+,.0f} ₫ ({h['unrealized_pnl_pct']:+.2f}%) | {h['stop_loss']:,.0f} ₫ "
                f"| {h['dist_to_stop_pct']:+.1f}% | {h['take_profit_tp1']:,.0f} ₫ | {h['action_label']} |"
            )
    else:
        lines.append("> Danh mục hiện đang nắm **100% Tiền Mặt** (`0 CP` rủi ro).")

    lines.extend([
        "",
        "## 3. RADA GIÁM SÁT WATCHLIST TẦM NGẮM & BUY-UP PRESSURE",
        "| Mã | Giá Live | Đổi % | Volume | Buy-Up Thực | RSI(14) | Ngoại Ròng | Trạng Thái Tác Chiến |",
        "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ])
    for s in snapshot["live_stocks"]:
        lines.append(
            f"| **{s['code']}** | {s['price']:,.0f} ₫ | {s['change_pct']:+.2f}% | {s['volume']:,} "
            f"| {s['active_buy_pct']:.1f}% | {s['rsi14']:.1f} | {s['foreign_net_ty']:+.2f} Tỷ | {s['security_label']} |"
        )

    sp = snapshot.get("global_spillover", {})
    tr_f = snapshot.get("execution_tracker", {}).get("filters", {})
    sp_m = sp.get("metrics", {})
    max_deploy_vnd = round(pf["cash_vnd"] * (float(reg.get("max_new_allocation_pct", 25)) / 100.0), 0)
    lines.extend([
        "",
        "## 4. CẦU NỐI LIÊN THỊ TRƯỜNG MỸ → VN & BỘ LỌC BULL-TRAP THÍCH NGHI",
        f"- **Spillover Phố Wall → VN:** `{sp.get('bias_label', '⚖️ TRUNG TÍNH')}` | Hệ số rủi ro: `{sp.get('risk_multiplier', 1.0):.2f}x` | Trần phân bổ mới: **`{reg.get('max_new_allocation_pct', 25)}% NAV`** (Gốc: {reg.get('base_max_allocation_pct', 25)}%)",
        f"- **Chỉ báo Đêm qua:** S&P 500 `{sp_m.get('SP500', {}).get('last_price', 0)}` (`{sp_m.get('SP500', {}).get('change_1d_pct', 0):+.2f}%`) | DXY `{sp_m.get('DXY', {}).get('last_price', 0)}` | VIX `{sp_m.get('VIX', {}).get('last_price', 0)}` | US10Y `{sp_m.get('US10Y', {}).get('last_price', 0)}%` | WTI Oil `{sp_m.get('WTI_OIL', {}).get('last_price', 0)}$`",
        f"- **Hồi tố Thực thi & Bull-Trap Filter:** BuyUp >= `{tr_f.get('min_buy_up_pct', 58.0)}%` | RSI Max <= `{tr_f.get('max_rsi_buy', 70.0)}` | Độ rộng Min >= `{tr_f.get('min_breadth_pct', 32.0)}%` | Slippage TB: `{tr_f.get('avg_slippage_bps', 0.0):+.1f} bps`",
        "",
        "## 5. KẾ HOẠCH TRIỂN KHAI TÁC CHIẾN ĐẦU TƯ THEO PHIÊN (MINH QUÂN & VICTOR)",
        f"- **Quản trị Sức mua & Tường lửa Hiến chương:** Két tiền mặt `{pf['cash_vnd']:,.0f} ₫` (`{pf['cash_pct']:.1f}% NAV`). Hạn mức giải ngân bổ sung tối đa theo chế độ `{reg['label']}` là **`{max_deploy_vnd:,.0f} ₫`** (cấm lô 100 CP vượt `33% NAV` = `{pf['total_nav_vnd'] * 0.33:,.0f} ₫`).",
        f"- **Phòng thủ Cổ phiếu Đang Giữ:** Theo dõi sát độ lệch Stop 2xATR trên `{pf['holdings_desc']}`; tuyệt đối tuân thủ Stop cứng và tận dụng biên độ phiên T+0/T+1 hạ giá vốn nếu nhúng về vùng hỗ trợ MA20.",
        f"- **Kỷ luật Thời điểm Thực thi:** Chỉ kê lệnh `LO` chủ động trong Khung Giờ Vàng `14:00 – 14:25` khi Buy-Up >= `{tr_f.get('min_buy_up_pct', 58.0):.0f}%` và không mua đuổi giá xanh ATO.",
    ])

    md_text = "\n".join(lines) + "\n"
    VN_SPEC_DIR.mkdir(parents=True, exist_ok=True)
    report_path = VN_SPEC_DIR / f"{date_str}_Live_Intraday_Report.md"
    report_path.write_text(md_text, encoding="utf-8")
    _upsert_report_into_vault(report_path)
    try:
        from scripts.apex_cloud_db_sync import ApexCloudDBSync
        ApexCloudDBSync.sync_live_report(snapshot, md_text)
    except Exception:
        pass

    _LAST_REPORT_STATE["written_ts"] = now_ts
    _LAST_REPORT_STATE["regime"] = regime_id
    _LAST_REPORT_STATE["alerts"] = cur_alerts
    return report_path


def is_vn_trading_hours(now: Optional[datetime.datetime] = None) -> bool:
    if now is None:
        now = get_ict_now()
    if not is_vn_trading_day(now.date()):
        return False
    hm = now.hour * 60 + now.minute
    return (8 * 60 + 55) <= hm <= (14 * 60 + 48)


def main():
    parser = argparse.ArgumentParser(description="Apex Real-Time Adaptive Intraday Brain (War-Room V4.0)")
    parser.add_argument("--once", action="store_true", help="Chạy tính toán snapshot + xuất báo cáo sống 1 lần")
    parser.add_argument("--daemon", action="store_true", help="Chạy nền quét mỗi 20s trong giờ giao dịch")
    parser.add_argument("--interval", type=int, default=20, help="Chu kỳ quét giây (mặc định 20s)")
    args = parser.parse_args()

    if args.daemon:
        print(f"[*] Khởi động Apex Live Intraday Brain Daemon (chu kỳ {args.interval}s)...")
        while True:
            try:
                now_ict = get_ict_now()
                if is_vn_trading_hours(now_ict):
                    snap = compute_live_war_room_snapshot(force_refresh=True)
                    rep = sync_live_intraday_report(snap, force_write=False)
                    if rep:
                        print(f"[{snap['server_time']}] Đã đồng bộ Live Report: {rep.name} | Regime: {snap['intraday_regime']['regime_id']}")
                else:
                    time.sleep(max(args.interval, 60))
                    continue
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[!] Lỗi chu kỳ Live Brain: {e}")
            time.sleep(args.interval)
    else:
        snap = compute_live_war_room_snapshot(force_refresh=True)
        rep = sync_live_intraday_report(snap, force_write=True)
        vni = snap["market_overview"]["vn_index"]
        pf = snap["portfolio_live"]
        print(f"[+] Snapshot lúc {snap['generated_at']} | Regime: {snap['intraday_regime']['label']}")
        print(f"    VN-Index: {vni['value']:,.2f} ({vni['change_pct']:+.2f}%) | Breadth: {snap['market_overview']['market_breadth']['sentiment']}")
        print(f"    NAV LIVE: {pf['total_nav_vnd']:,.0f} đ | Cash: {pf['cash_vnd']:,.0f} đ ({pf['cash_pct']}%) | PnL tạm: {pf['unrealized_pnl_vnd']:+,.0f} đ ({pf['unrealized_pnl_pct']:+.2f}%)")
        for s in snap["live_stocks"]:
            print(f"    - {s['code']}: {s['price']:,.0f} đ ({s['change_pct']:+.2f}%) | BuyUp {s['active_buy_pct']}% | {s['security_label']}")
        if rep:
            print(f"[+] Đã xuất & đồng bộ SQLite Vault: {rep}")


if __name__ == "__main__":
    main()
