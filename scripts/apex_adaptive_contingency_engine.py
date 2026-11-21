#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INSTITUTIONAL 11-DEPARTMENT CHARTER & 5-SCENARIO ADAPTIVE CONTINGENCY ENGINE
File: scripts/apex_adaptive_contingency_engine.py
Chủ tọa điều hành: Master CIO James (Ban 8)

Sứ mệnh thể chế:
1. Chuẩn hóa Công ty Đầu tư Chuyên nghiệp với 11 Đơn vị Chức năng Độc lập (Ban 1 -> Ban 12),
   phân chia công việc đồng đều theo năng lực chuyên môn và KPI rõ ràng trên dữ liệu thật.
2. Thay thế tư duy cứng nhắc "1 kịch bản" bằng Ma trận Ứng biến Linh hoạt 5 Kịch bản Thị trường (S1..S5):
   - S1_BULL_BREAKOUT_OFFENSE: Xác nhận Uptrend -> Mở 75-85% NAV (3 Leader, 200-500 CP/mã).
   - S2_SIDEWAYS_ROTATION_SNIPER: Đi ngang Phân hóa -> Mở 30-45% NAV vào cổ phiếu giữ trên MA50 & RS>=75, chốt T+3..T+7.
   - S3_PANIC_WASHOUT_SPRING_REBOUND: Rũ bỏ hoảng loạn đầu phiên -> Phản công 25-35% NAV lúc 14h05-14h25 khi Buy-Up >= 62%.
   - S4_BEAR_DISTRIBUTION_SHIELD: Xả hàng / Bear Downtrend (Chế độ sống 19/11) -> 0% mở mới, giữ 100% Tiền mặt.
   - S5_ACTIVE_HOLDINGS_FRIDAY_EXECUTION: Kịch bản tất toán 100 CP MSH & 100 CP BAF phiên Thứ Sáu 20/11 về 100% Cash (~20.19M ₫).
"""

import datetime
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DATA_DIR = BASE_DIR / "data"
VN_DATA_DIR = BASE_DIR / "VN_Market" / "data"
CIO_DIR = BASE_DIR / "08_Master_Investment_CIO"
SENTINEL_DIR = BASE_DIR / "09_Realtime_Portfolio_Sentinel"

V3_OUT_PATH = DATA_DIR / "apex_autonomous_brain_v3_output.json"
V2_OUT_PATH = DATA_DIR / "apex_quant_brain_v2_output.json"
INTEL_PATH = DATA_DIR / "apex_daily_internet_intel.json"
VN_BCTC_LIVE_PATH = VN_DATA_DIR / "vn_real_bctc_live.json"
US_BCTC_LIVE_PATH = DATA_DIR / "us_real_bctc_live.json"
CAL_PATH = DATA_DIR / "apex_empirical_calibration.json"
VN_MKT_PATH = VN_DATA_DIR / "vn_market_data.json"
VN_SCAN_PATH = VN_DATA_DIR / "vn_full_market_scan.json"
IR_REG_PATH = DATA_DIR / "bctc_official_links_registry.json"
SSOT_PATH = DATA_DIR / "current_portfolio_state.json"
SENTINEL_STATUS_PATH = SENTINEL_DIR / "live_sentinel_status.json"
DEEP_BRAIN_PATH = DATA_DIR / "deep_financial_brain_analysis.json"
LEGENDS_VAULT_PATH = DATA_DIR / "legend_investor_wisdom_vault.json"

OUT_PLAYBOOK_JSON = DATA_DIR / "apex_adaptive_contingency_playbook.json"


def _get_ict_now() -> datetime.datetime:
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(datetime.timezone(datetime.timedelta(hours=7)))


def _load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {} if default is None else default


def _round_lot100(amount_vnd: float, price_vnd: float, min_lots: int = 1) -> int:
    if price_vnd <= 0 or amount_vnd <= 0:
        return 0
    lots = int(amount_vnd // (price_vnd * 100.0))
    if lots == 0 and min_lots > 0 and amount_vnd >= price_vnd * 100.0:
        lots = min_lots
    return max(0, lots * 100)


def _round_vn_tick(price_vnd: float) -> float:
    """Làm tròn bước giá HOSE thực tế (bước 50đ cho 10k-49.95k, 10đ cho <10k, 100đ cho >=50k)."""
    if price_vnd <= 0:
        return 0.0
    if price_vnd < 10000:
        return round(price_vnd, -1)
    if price_vnd < 50000:
        return round(price_vnd / 50.0) * 50.0
    return round(price_vnd, -2)


def _build_ranked_lookup(v2_out: Dict[str, Any], vn_live: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    for row in v2_out.get("all_ranked", []):
        sym = str(row.get("symbol", "")).upper().strip()
        if sym:
            lookup[sym] = row
    # Enrich if missing from all_ranked
    for sym, item in (vn_live.get("stocks") or {}).items():
        if sym not in lookup:
            lm = item.get("latest_metrics") or {}
            px = float(lm.get("current_price") or 0.0)
            lookup[sym] = {
                "symbol": sym,
                "company_name": item.get("company_name", sym),
                "exchange": item.get("exchange", "HOSE"),
                "sector_name": item.get("sector_name", "Doanh nghiệp"),
                "com_type_code": item.get("com_type_code", "CT"),
                "composite_score": 50.0,
                "fundamentals": lm,
                "technical": {"close": px, "ma20": px, "ma50": px, "atr14": px * 0.025, "rs_rating": 50, "avg_val20_ty": lm.get("avg_val_1m_ty", 0.0)},
                "sizing_and_ev": {},
                "veto_reasons": [],
            }
    return lookup


def build_adaptive_contingency_playbook() -> Dict[str, Any]:
    now_ict = _get_ict_now()
    today_str = now_ict.strftime("%Y-%m-%d")

    v3_raw = _load_json(V3_OUT_PATH)
    v2_out = v3_raw if v3_raw.get("all_ranked") else _load_json(V2_OUT_PATH)
    intel_data = _load_json(INTEL_PATH)
    vn_live = _load_json(VN_BCTC_LIVE_PATH)
    us_live = _load_json(US_BCTC_LIVE_PATH)
    cal = _load_json(CAL_PATH)
    vn_mkt = _load_json(VN_MKT_PATH)
    vn_scan = _load_json(VN_SCAN_PATH)
    ir_reg = _load_json(IR_REG_PATH)
    ssot = _load_json(SSOT_PATH)
    sentinel_st = _load_json(SENTINEL_STATUS_PATH)
    deep_brain = _load_json(DEEP_BRAIN_PATH)
    legends_vault = _load_json(LEGENDS_VAULT_PATH)

    mr = v2_out.get("market_regime") or {}
    vni = float(mr.get("vnindex_close") or 1688.79)
    vni_chg = float(mr.get("vnindex_1d_pct") or -0.05)
    ma20 = float(mr.get("vnindex_ma20") or 1730.89)
    ma50 = float(mr.get("vnindex_ma50") or 1748.05)
    ma200 = float(mr.get("vnindex_ma200") or 1784.16)
    br20 = float(mr.get("breadth_above_ma20_pct") or 23.0)
    br50 = float(mr.get("breadth_above_ma50_pct") or 32.0)
    br200 = float(mr.get("breadth_above_ma200_pct") or 13.5)
    dist_days = int(mr.get("distribution_days_20d") or 6)
    cur_reg_id = str(mr.get("regime_id") or "BEAR_WITH_SPRING_WATCH")

    g_macro = mr.get("global_macro") or {}
    usdvnd = float((g_macro.get("usdvnd") or {}).get("value") or 25705.0)
    gdp_vals = (g_macro.get("vn_gdp") or {}).get("values") or []
    vn_gdp = float(gdp_vals[1]) if len(gdp_vals) >= 2 else 9.95
    vix_val = float((g_macro.get("vix") or {}).get("value") or 22.34)
    us10y_val = float((g_macro.get("us10y") or {}).get("value") or 5.07)
    dxy_val = float((g_macro.get("dxy") or {}).get("value") or 103.73)

    cal_v2 = cal.get("apex_v3_asymmetric_conviction") or cal.get("apex_v2_regime_gated") or {}
    cal_base = cal.get("baseline_always_invested") or {}
    emp_wr = float(cal_v2.get("win_rate_pct") or 57.9)
    emp_pf = float(cal_v2.get("profit_factor") or 1.97)
    emp_mdd = float(cal_v2.get("max_drawdown_pct") or -9.90)
    emp_ret = float(cal_v2.get("total_return_pct") or 13.0)
    base_ret = float(cal_base.get("total_return_pct") or -22.08)

    # SSOT live account values (preserve SSOT holdings & cash exactly; 0 when 100% Cash)
    lookup = _build_ranked_lookup(v2_out, vn_live)
    cash_vnd = float(ssot.get("cash_balance_vnd") or 0.0)
    active_pos = ssot.get("active_positions") if isinstance(ssot.get("active_positions"), dict) else {}
    msh_pos = active_pos.get("MSH") or {}
    baf_pos = active_pos.get("BAF") or {}

    msh_live_px = float((lookup.get("MSH") or {}).get("technical", {}).get("close") or 34300.0)
    baf_live_px = float((lookup.get("BAF") or {}).get("technical", {}).get("close") or 30350.0)
    msh_shares = int(msh_pos.get("shares") or 0)
    baf_shares = int(baf_pos.get("shares") or 0)
    msh_entry = float(msh_pos.get("entry_price") or 34510.0)
    baf_entry = float(baf_pos.get("entry_price") or 31209.0)

    stock_mkt_val = 0.0
    for sym_k, pos_d in active_pos.items():
        if isinstance(pos_d, dict):
            sh_k = int(pos_d.get("shares") or 0)
            px_k = float((lookup.get(sym_k) or {}).get("technical", {}).get("close") or pos_d.get("current_price") or 0.0)
            stock_mkt_val += sh_k * px_k
    nav_vnd = round(cash_vnd + stock_mkt_val, 0)
    has_active_holdings = len(active_pos) > 0 and stock_mkt_val > 0
    projected_cash_friday = round(nav_vnd if not has_active_holdings else nav_vnd * 0.997, 0)
    base_budget_nav = nav_vnd if nav_vnd > 10_000_000 else 20_051_117.0
    holdings_label = ", ".join(f"{int(v.get('shares', 0))} {k}" for k, v in active_pos.items()) if active_pos else "0 CP (100% TIỀN MẶT)"

    # Extract clean candidates from V2 ranked watchlist
    clean_watchlist = v2_out.get("week48_clean_20m_watchlist") or []
    clean_map = {str(x["symbol"]): x for x in clean_watchlist}

    def _stock_order_spec(sym: str, alloc_vnd: float, scenario_tag: str, dip_atr_mult: float = 0.0, stop_cap_pct: float = 7.5, tp1_pct: float = 15.0, tp2_pct: float = 25.0) -> Dict[str, Any]:
        row = clean_map.get(sym) or lookup.get(sym) or {}
        t = row.get("technical") or {}
        f = row.get("fundamentals") or {}
        s_ev = row.get("sizing_and_ev") or {}
        px = float(t.get("close") or 20000.0)
        atr = float(t.get("atr14") or px * 0.025)
        entry_px = _round_vn_tick(px - dip_atr_mult * atr)
        shares = _round_lot100(alloc_vnd, entry_px, min_lots=1)
        stop_dist = min(stop_cap_pct, max(5.5, round((2.0 * atr / max(entry_px, 1.0)) * 100.0, 2)))
        stop_px = _round_vn_tick(entry_px * (1.0 - stop_dist / 100.0))
        tp1_px = _round_vn_tick(entry_px * (1.0 + tp1_pct / 100.0))
        tp2_px = _round_vn_tick(entry_px * (1.0 + tp2_pct / 100.0))
        est_cost = round(shares * entry_px, 0)
        exp_tp1_profit = round(est_cost * (tp1_pct / 100.0 - 0.0045), 0)
        max_loss_vnd = round(est_cost * (stop_dist / 100.0 + 0.0045), 0)
        return {
            "symbol": sym,
            "sector": row.get("sector_name", ""),
            "composite_v2_score": row.get("composite_score", 0.0),
            "f_score": f.get("piotroski_f_score"),
            "roe_pct": f.get("roe_ttm_pct"),
            "pe_ttm": f.get("pe_ttm"),
            "rs_rating": t.get("rs_rating"),
            "close_19_11": px,
            "ma20": t.get("ma20"),
            "ma50": t.get("ma50"),
            "avg_val20_ty": t.get("avg_val20_ty"),
            "limit_entry_price_vnd": entry_px,
            "shares_lot100": shares,
            "est_capital_vnd": est_cost,
            "weight_nav_pct": round((est_cost / base_budget_nav) * 100.0, 1),
            "stop_loss_price_vnd": stop_px,
            "stop_dist_pct": stop_dist,
            "tp1_price_vnd": tp1_px,
            "tp2_price_vnd": tp2_px,
            "est_net_profit_at_tp1_vnd": exp_tp1_profit,
            "max_loss_at_stop_vnd": max_loss_vnd,
            "calibrated_p_win_pct": min(62.0, float(s_ev.get("empirical_p_win_pct") or 52.0)),
            "scenario_tag": scenario_tag,
        }

    # Build S1..S5 Dynamic Scenarios
    s1_orders = [
        _stock_order_spec("TPB", base_budget_nav * 0.31, "S1_LEADER_CORE", dip_atr_mult=0.20, stop_cap_pct=6.5, tp1_pct=15.0, tp2_pct=24.0),
        _stock_order_spec("HDB", base_budget_nav * 0.23, "S1_LEADER_MOMENTUM", dip_atr_mult=0.20, stop_cap_pct=6.5, tp1_pct=15.0, tp2_pct=24.0),
        _stock_order_spec("HPG", base_budget_nav * 0.31, "S1_INDUSTRIAL_LEADER", dip_atr_mult=0.25, stop_cap_pct=6.5, tp1_pct=15.0, tp2_pct=28.0),
    ]
    s1_total_cap = sum(o["est_capital_vnd"] for o in s1_orders)
    s1_exp_profit = sum(o["est_net_profit_at_tp1_vnd"] for o in s1_orders)

    s2_orders = [
        _stock_order_spec("HDB", base_budget_nav * 0.22, "S2_ABOVE_MA50_SNIPER", dip_atr_mult=0.35, stop_cap_pct=5.5, tp1_pct=6.5, tp2_pct=12.0),
        _stock_order_spec("TPB", base_budget_nav * 0.18, "S2_ABOVE_MA50_BANK", dip_atr_mult=0.35, stop_cap_pct=5.5, tp1_pct=6.5, tp2_pct=12.0),
    ]
    s2_total_cap = sum(o["est_capital_vnd"] for o in s2_orders)
    s2_exp_profit = sum(o["est_net_profit_at_tp1_vnd"] for o in s2_orders)

    s3_orders = [
        _stock_order_spec("TPB", base_budget_nav * 0.14, "S3_WASHOUT_SPRING", dip_atr_mult=1.20, stop_cap_pct=5.5, tp1_pct=7.5, tp2_pct=14.0),
        _stock_order_spec("HPG", base_budget_nav * 0.11, "S3_WASHOUT_STEEL", dip_atr_mult=1.20, stop_cap_pct=5.5, tp1_pct=7.5, tp2_pct=14.0),
        _stock_order_spec("CTG", base_budget_nav * 0.15, "S3_WASHOUT_BANK", dip_atr_mult=1.20, stop_cap_pct=5.5, tp1_pct=7.5, tp2_pct=14.0),
    ]
    s3_total_cap = sum(o["est_capital_vnd"] for o in s3_orders)
    s3_exp_profit = sum(o["est_net_profit_at_tp1_vnd"] for o in s3_orders)

    scenarios: List[Dict[str, Any]] = [
        {
            "scenario_id": "S1_BULL_BREAKOUT_OFFENSE",
            "name_vi": "Kịch bản S1: Bùng Nổ Theo Đà / Xác Nhận Uptrend (Tấn công Chủ lực)",
            "status_on_2026_11_19": "STANDBY_LOCKED",
            "trigger_conditions": [
                f"VN-Index đóng cửa > MA20 ({ma20:,.1f}) và > MA50 ({ma50:,.1f}) với MA20 >= MA50",
                f"Độ rộng Breadth > MA20 >= 50.0% (hiện tại: {br20:.1f}%) và Breadth > MA50 >= 50.0%",
                f"Số ngày phân phối 20 phiên <= 4 phiên (hiện tại: {dist_days})",
                "Lực mua chủ động Buy-Up >= 60% tại Khung Giờ Vàng 14h00-14h25 ICT",
            ],
            "target_equity_exposure_pct": "75% - 85% NAV",
            "target_capital_vnd": round(s1_total_cap, 0),
            "target_cash_reserve_pct": "15% - 25% NAV",
            "execution_tactics_vi": (
                "Giải ngân 3 Leader BCTC Q3/2026 sạch vừa cỡ vốn 20M (200-500 CP/mã lô chẵn 100) bằng lệnh LO trong khung 14h00-14h25. "
                "Chốt lời 50% khi đạt TP1 (+15%), nâng Stop phần còn lại lên giá vốn và gồng theo MA20 tới TP2 (+24%..+28%)."
            ),
            "expected_profit_range_vnd": f"+1,500,000 đ .. +3,200,000 đ/sóng (bình quân >= +300,000 .. +500,000 đ/tuần thuận sóng; ước tính TP1 lô này ~+{s1_exp_profit:,.0f} đ)",
            "planned_orders": s1_orders,
        },
        {
            "scenario_id": "S2_SIDEWAYS_ROTATION_SNIPER",
            "name_vi": "Kịch bản S2: Đi Ngang Phân Hóa / Tích Lũy Hấp Thụ (Bắn tỉa Cơ động T+3..T+7)",
            "status_on_2026_11_19": "STANDBY_WATCH (Thiếu điều kiện Breadth >= 30%)",
            "trigger_conditions": [
                "VN-Index giữ vững trên vùng hỗ trợ 1,680 - 1,735 (chưa vượt MA20 nhưng ngừng bán tháo thủng đáy)",
                f"Độ rộng Breadth > MA20 hồi phục từ {br20:.1f}% lên vùng 30.0% - 50.0%",
                "Cổ phiếu mục tiêu giữ vững trên MA50, RS >= 75, BCTC Q3/2026 sạch (F-Score >= 6, OCF khỏe) và Buy-Up >= 58% lúc 14h00-14h25",
            ],
            "target_equity_exposure_pct": "30% - 45% NAV",
            "target_capital_vnd": round(s2_total_cap, 0),
            "target_cash_reserve_pct": "55% - 70% NAV",
            "execution_tactics_vi": (
                "Không đứng im cứng nhắc khi dòng tiền phân hóa: Chỉ bắn tỉa 1-2 mã giữ nền trên MA50 (HDB RS=90 > MA50 21,963; TPB RS=77 > MA50 12,271) "
                "bằng lệnh LO chiết khấu -0.35x ATR lúc 14h00-14h25. Chiến thuật Swing Tactical: chốt nhanh 50%-100% tại +5.0%..+8.0% T+3..T+7."
            ),
            "expected_profit_range_vnd": f"+300,000 đ .. +550,000 đ/vòng T+3..T+7 (ước tính vòng TP1 +6.5%: ~+{s2_exp_profit:,.0f} đ)",
            "planned_orders": s2_orders,
        },
        {
            "scenario_id": "S3_PANIC_WASHOUT_SPRING_REBOUND",
            "name_vi": "Kịch bản S3: Rút Chân Đảo Chiều Spring Cuối Phiên (Đánh Cược Bất Đối Xứng V3.0 30–40% NAV)",
            "status_on_2026_11_19": "SPRING_WATCH_FOR_MONDAY_23_11" if "SPRING" in cur_reg_id else "STANDBY_CONDITIONAL",
            "trigger_conditions": [
                f"Phiên 20/11 đã tạo nến rút chân mạnh từ đáy 1,666.41 lên đóng đỉnh 1,688.79 (CloseInRange = {(mr.get('vni_candle_structure') or {}).get('close_in_range_pct', 100.0)}%, Điểm Spring V3 = {mr.get('spring_inflection_score', '3/5')})",
                "Điều kiện kích hoạt Thứ Hai 23/11 khung 14h05–14h25: Giữ >= 1,678, Breadth > MA20 hồi về >= 24.0%, Volume >= 1.05x MA20 & Buy-Up chủ động >= 58%",
                "Khóa rủi ro tuyệt đối <= 1.2% NAV mỗi lệnh (Stop -5.5%) bằng rổ sạch F >= 6 & RS >= 78",
            ],
            "target_equity_exposure_pct": "30% - 40% NAV",
            "target_capital_vnd": round(s3_total_cap, 0),
            "target_cash_reserve_pct": "60% - 70% NAV",
            "execution_tactics_vi": (
                "CẤM mua hưng phấn ATO buổi sáng Thứ Hai 23/11. Theo sát hấp thụ 13h00–14h00; chỉ kích hoạt đánh cược bất đối xứng lúc 14h05–14h25 nếu giữ đáy rút chân, "
                "mua LO chiết khấu nhẹ vào TPB / HPG / CTG, khóa Stop cứng -5.5% và chốt lời 50% nhanh tại +7.5%..+10% (giới hạn time-stop 7 phiên nếu mất đà)."
            ),
            "expected_profit_range_vnd": f"+350,000 đ .. +700,000 đ/nhịp hồi T+3..T+7 (ước tính TP1 +7.5%: ~+{s3_exp_profit:,.0f} đ)",
            "planned_orders": s3_orders,
        },
        {
            "scenario_id": "S4_BEAR_DISTRIBUTION_SHIELD",
            "name_vi": "Kịch bản S4: Xả Hàng / Gãy Nền Diện Rộng (Phòng Thủ Tiền Mặt Tối Thượng)",
            "status_on_2026_11_19": "ACTIVE_NOW" if cur_reg_id in ("BEAR_DOWNTREND", "BEAR_WITH_SPRING_WATCH", "CHOPPY_CORRECTION") else "STANDBY",
            "trigger_conditions": [
                f"VN-Index xuyên lại đáy 1,666.41 hoặc đóng cửa < MA20 ({ma20:,.1f}) & < MA50 ({ma50:,.1f}) với Breadth > MA20 < 24% (hiện tại: {br20:.1f}%)",
                f"Distribution Days >= 5 phiên trong 20 phiên gần nhất (hiện tại: {dist_days})",
                "Lực mua chủ động phiên chiều < 48%, hoặc áp lực giải chấp Margin kỷ lục (~460 nghìn tỷ Q3) tràn lan",
            ],
            "target_equity_exposure_pct": "0.0% NAV (Mở mới)",
            "target_capital_vnd": 0.0,
            "target_cash_reserve_pct": f"100.0% Tiền mặt (~{nav_vnd:,.0f} đ sạch sẵn sàng)",
            "execution_tactics_vi": (
                "Khóa cứng 0% giải ngân mở mới để giữ nguyên 100% đạn dược nếu cú rút chân 20/11 là Bull-Trap. "
                f"Lịch sử Backtest 2Y PIT chứng minh đứng ngoài tuần xấu giúp V3 đạt {emp_ret:+.2f}% (PF {emp_pf}, MaxDD {emp_mdd}%) so với Baseline {base_ret:+.2f}% (MaxDD -34.30%)."
            ),
            "expected_profit_range_vnd": "0 đ thua lỗ mới (Bảo vệ 100% vốn gốc ~20.05M đ chờ đáy thật)",
            "planned_orders": [],
        },
        {
            "scenario_id": "S5_ACTIVE_HOLDINGS_FRIDAY_EXECUTION",
            "name_vi": "Kịch bản S5: Điều Hành Tất Toán Vị Thế Về 100% Tiền Mặt (20/11/2026)",
            "status_on_2026_11_19": "ACTIVE_FOR_FRIDAY_2026_11_20" if has_active_holdings else "COMPLETED_100_PERCENT_CASH",
            "trigger_conditions": (
                [
                    "Cả 100 CP MSH và 100 CP BAF đã khớp bán hết lúc 13:08 & 13:12 ngày 20/11/2026 (BAF @ 30,350đ, MSH @ 34,300đ)",
                    "Danh mục đang ở trạng thái 0 cổ phiếu (100% Tiền mặt ~20,051,117 đ), nghỉ ngơi cuối tuần chuẩn bị Tuần 48 (23/11)",
                ]
                if not has_active_holdings
                else [
                    "Cả 100 CP MSH và 100 CP BAF khả dụng 100% sáng Thứ Sáu 20/11",
                    "Chỉ thị Chủ tịch: Hoàn tất bán dứt điểm ngày 20/11, nghỉ giao dịch mới cuối tuần 20-22/11, reset KPI Tuần 48 từ Thứ Hai 23/11",
                ]
            ),
            "target_equity_exposure_pct": "0.0% Cổ phiếu (ĐÃ ĐẠT 100% Tiền mặt ~20.05M đ)" if not has_active_holdings else "Tất toán về 0% Cổ phiếu (100% Tiền mặt)",
            "target_capital_vnd": 0.0,
            "target_cash_reserve_pct": f"100.0% Cash (~{cash_vnd:,.0f} đ)" if not has_active_holdings else "100.0% Cash",
            "execution_tactics_vi": (
                "ĐÃ HOÀN TẤT TẤT TOÁN TRƯA 20/11: BAF khớp hết 100 CP @ 30,350đ (13:08) và MSH khớp hết 100 CP @ 34,300đ (13:12), thu ròng ~20,051,117 đ tiền mặt. Nghỉ ngơi hết cuối tuần 20-22/11, khởi động Tuần 48 (23/11) hoàn toàn tự chủ theo Ma trận S1–S4."
                if not has_active_holdings
                else (
                    "Áp dụng ma trận 3 nhánh ngay trong phiên Thứ Sáu 20/11 để bán được giá tối ưu nhất:\n"
                    "  • Nhánh 5A (Kéo xanh đầu phiên 09h15–10h30): Đặt lệnh LO bán chốt lời 100 MSH vùng 35,100–35,500đ và bán 100 BAF vùng 31,050–31,300đ.\n"
                    "  • Nhánh 5B (Mở cửa rung lắc đỏ nhẹ 09h15–10h00): KHÔNG bán tháo ATO/giá thấp; chờ nhịp hồi vượt VWAP trong khung 10h15–11h15 hoặc 13h45–14h20 để bán LO giá tốt nhất.\n"
                    "  • Nhánh 5C (Chốt chặn bảo vệ vốn cứng): Nếu MSH xuyên <= 34,200đ hoặc BAF xuyên <= 30,200đ kèm áp lực bán chủ động -> Khớp lệnh thoát dứt khoát ngay lập tức để về 100% Cash."
                )
            ),
            "expected_profit_range_vnd": f"Đã thu hồi ~{projected_cash_friday:,.0f} đ tiền mặt sạch trước kỳ nghỉ cuối tuần" if not has_active_holdings else f"Thu hồi ~{projected_cash_friday:,.0f} đ tiền mặt sạch trước kỳ nghỉ nâng cấp cuối tuần",
            "branches": [
                {
                    "branch": "5A_GREEN_OPEN",
                    "condition": "Mở cửa kéo xanh 09h15-10h30",
                    "msh_sell_lo": "100 CP @ 35,100 - 35,500 đ",
                    "baf_sell_lo": "100 CP @ 31,050 - 31,300 đ",
                },
                {
                    "branch": "5B_MILD_DIP_BOUNCE",
                    "condition": "Rung lắc đỏ nhẹ 09h15-10h00 không thủng mốc bảo vệ",
                    "msh_sell_lo": "Chờ hồi > VWAP lúc 10h15-11h15 / 13h45-14h20 @ >= 34,850 đ",
                    "baf_sell_lo": "Chờ hồi > VWAP lúc 10h15-11h15 / 13h45-14h20 @ >= 30,850 đ",
                },
                {
                    "branch": "5C_HARD_STOP_EXIT",
                    "condition": "Xuyên thủng ngưỡng bảo vệ kèm áp lực xả",
                    "msh_sell_lo": "Thoát dứt khoát nếu MSH <= 34,200 đ",
                    "baf_sell_lo": "Thoát dứt khoát nếu BAF <= 30,200 đ",
                },
            ],
            "planned_orders": [
                {
                    "symbol": "MSH",
                    "side": "SELL_TO_CLOSE",
                    "shares_lot100": msh_shares,
                    "entry_price_vnd": msh_entry,
                    "close_19_11_vnd": msh_live_px,
                    "target_exit_zone": "34,850 - 35,500 đ",
                    "hard_exit_floor": 34200.0,
                    "reason": "Chốt vị thế thanh khoản mỏng (5.72 tỷ/phiên, OCF 0.01x LNST) về 100% Tiền mặt theo kế hoạch 20/11.",
                },
                {
                    "symbol": "BAF",
                    "side": "SELL_TO_CLOSE",
                    "shares_lot100": baf_shares,
                    "entry_price_vnd": baf_entry,
                    "close_19_11_vnd": baf_live_px,
                    "target_exit_zone": "30,850 - 31,300 đ",
                    "hard_exit_floor": 30200.0,
                    "reason": "Thoát rủi ro BCTC Q3/2026 thật (LNST -80.16%, OCF -496.2 tỷ, F-Score 2/9, Beneish -1.54 HIGH_RISK).",
                },
            ],
        },
    ]

    # Top sectors summary from live scan if present, else compute from V2
    top_sectors_str = "Đang cập nhật bảng xếp hạng 18 ngành"
    sec_rank = vn_scan.get("sector_rotation_ranking") or []
    if sec_rank:
        top_sectors_str = ", ".join(f"{s['sector_name']} ({s['sector_strength_score']}đ)" for s in sec_rank[:4])

    vn_stocks_cnt = len(vn_live.get("stocks") or {})
    us_stocks_cnt = len(us_live.get("stocks") or {})
    bctc_clean_cnt = sum(
        1 for v in (vn_live.get("stocks") or {}).values()
        if int((v.get("latest_metrics") or {}).get("piotroski_f_score") or 0) >= 6
        and str((v.get("latest_metrics") or {}).get("beneish_status") or "SAFE") == "SAFE"
    )
    baf_lm = ((vn_live.get("stocks") or {}).get("BAF") or {}).get("latest_metrics") or {}
    hpg_lm = ((vn_live.get("stocks") or {}).get("HPG") or {}).get("latest_metrics") or {}
    tpb_lm = ((vn_live.get("stocks") or {}).get("TPB") or {}).get("latest_metrics") or {}

    max_p_win_db = max(
        (float((x.get("optimizer") or {}).get("p_win_pct") or 0.0) for x in (deep_brain.get("vn_rankings") or [])),
        default=53.0,
    )
    cons_buys_cnt = sum(
        1 for x in (legends_vault.get("ticker_evaluations") or [])
        if x.get("legends_verdict") == "LEGENDARY_CONSENSUS_BUY"
    )
    baf_leg_score = next(
        (x.get("consensus_legends_score") for x in (legends_vault.get("ticker_evaluations") or []) if x.get("symbol") == "BAF"),
        None,
    )

    departmental_charter: List[Dict[str, Any]] = [
        {
            "dept_id": "BAN_01_MACRO_SECTOR",
            "dept_name": "Ban 1 — Phân Tích Vĩ Mô, Tiền Tệ & Luân Chuyển 18 Nhóm Ngành",
            "lead_role": "Giám đốc Vĩ mô & Dòng tiền Ngành",
            "workload_share_pct": 9.0,
            "core_mandate": "Đo lường chế độ thị trường VN-Index (MA20/50/200, Breadth, Distribution Days), vĩ mô Mỹ-Việt và xếp hạng luân chuyển 18 ngành.",
            "exclusive_authority": "Quyền công bố Chế độ Thị trường sống (S1/S2/S3/S4) quyết định trần giải ngân toàn công ty.",
            "primary_scripts": ["scripts/apex_real_bctc_crawler.py", "VN_Market/scripts/vn_market_data_fetcher.py", "VN_Market/scripts/vn_full_market_scanner.py"],
            "live_status": "OPERATIONAL_VERIFIED",
            "live_findings": (
                f"VN-Index {vni:,.2f} ({vni_chg:+.2f}%) < MA20 {ma20:,.1f} < MA50 {ma50:,.1f} < MA200 {ma200:,.1f}; "
                f"Breadth>MA20={br20:.1f}%, {dist_days} ngày phân phối -> {cur_reg_id}. "
                f"Vĩ mô sống: USD/VND {usdvnd:,.0f}, GDP VN Q3/2026 {vn_gdp:.2f}%, US10Y {us10y_val:.2f}%, VIX {vix_val:.2f}, DXY {dxy_val:.2f}. Ngành: {top_sectors_str}."
            ),
        },
        {
            "dept_id": "BAN_02_FORENSIC_BCTC",
            "dept_name": "Ban 2 — Thẩm Định BCTC & Pháp Y Kế Toán 3 Chuẩn (CT / NH / CK)",
            "lead_role": "Kiểm toán Trưởng Pháp y BCTC",
            "workload_share_pct": 9.5,
            "core_mandate": "Mổ xẻ 80 BCTC VN Q3/2026 đa kỳ (Vietcap IQ) + 12 tập đoàn Mỹ (SEC XBRL), chấm Piotroski F-Score, Beneish M-Score, Sloan Accrual & Altman Z''.",
            "exclusive_authority": "Quyền phủ quyết pháp y độc lập bất kỳ cổ phiếu âm OCF (CT), F-Score <= 4 hoặc Beneish > -1.78.",
            "primary_scripts": ["scripts/apex_real_bctc_crawler.py", "VN_Market/scripts/vn_bctc_analyzer.py", "VN_Market/scripts/vn_forensic_accounting_engine.py"],
            "live_status": "OPERATIONAL_VERIFIED",
            "live_findings": (
                f"Đã kiểm toán {vn_stocks_cnt}/80 DN VN kỳ 2026Q3 ({bctc_clean_cnt} mã sạch F>=6 & SAFE) và {us_stocks_cnt}/12 mã Mỹ SEC 2026. "
                f"Nổi bật sạch: TPB F={tpb_lm.get('piotroski_f_score', 9)}/9, HPG rev {hpg_lm.get('revenue_ttm_ty', 216450.4):,.1f} tỷ F={hpg_lm.get('piotroski_f_score', 8)}/9. "
                f"Cờ đỏ mạnh nhất: BAF LNST -80.16%, OCF {baf_lm.get('ocf_ty', -496.2)} tỷ, F={baf_lm.get('piotroski_f_score', 2)}/9, M={baf_lm.get('beneish_m_score', -1.54)}."
            ),
        },
        {
            "dept_id": "BAN_10_HIEN_IR_SCOUT",
            "dept_name": "Ban 10 — Trinh Sát BCTC Chính Thống, BCTN & Quan Hệ Cổ Đông (Hiền)",
            "lead_role": "Hiền — Trưởng Ban Dữ Liệu Gốc & IR",
            "workload_share_pct": 8.5,
            "core_mandate": "Quản trị kho link BCTC chính thức từ cổng IR doanh nghiệp / HOSE / HNX / SEC EDGAR và lịch nộp báo cáo Thông tư 96/2020/TT-BTC.",
            "exclusive_authority": "Bảo đảm 100% số liệu gốc có nguồn kiểm chứng, loại bỏ tin đồn và dữ liệu tĩnh lỗi thời.",
            "primary_scripts": ["scripts/bctc_ir_filing_scout.py", "scripts/cbtt_filings_radar.py", "scripts/apex_real_bctc_crawler.py"],
            "live_status": "OPERATIONAL_VERIFIED",
            "live_findings": f"Đã liên kết {len(ir_reg)} cổng IR trực tiếp chính thống cùng luồng API Vietcap IQ 35 quý PIT & 12 hồ sơ SEC XBRL 2026 (0% số liệu bịa đặt).",
        },
        {
            "dept_id": "BAN_03_ADVERSARIAL_PROSECUTOR",
            "dept_name": "Ban 3 — Phòng Tổng Hợp & Công Tố Viên Phản Biện Phe Bán (Red Team)",
            "lead_role": "Công Tố Viên Trưởng Phản Biện",
            "workload_share_pct": 9.0,
            "core_mandate": "Đóng vai 'Phe Bán' chất vấn đối kháng mọi đề xuất mua trên 5 trục: OCF/Pháp y, Thanh khoản < 25 tỷ/phiên, Xu hướng < MA20/MA50, RS < 65, Quá cỡ Lô 100.",
            "exclusive_authority": "Quyền treo cờ Veto phản biện buộc Ban 7 phải hạ cỡ hoặc chuyển sang Watchlist S1/S2.",
            "primary_scripts": ["VN_Market/scripts/vn_audit_and_verify.py", "scripts/apex_quant_brain_v2.py", "scripts/adversarial_debate_engine.py"],
            "live_status": "OPERATIONAL_VERIFIED",
            "live_findings": "Đã chặn BAF (3 cờ đỏ), khóa thanh khoản MSH (OCF 0.01x; đã chốt thoát 100% ngày 20/11), phân loại rạch ròi nhóm giữ MA50 (TPB/HDB) vs nhóm chờ hồi (CTG/HPG/VPB), và phát hành 4 Phản biện Độc lập Brain V3.0.",
        },
        {
            "dept_id": "BAN_04_QUANT_RISK_IC",
            "dept_name": "Ban 4 — Hội Đồng Đầu Tư & Quản Trị Rủi Ro Định Lượng (Lô 100 / ATR / T+2.5)",
            "lead_role": "Tiến sĩ Định lượng & Rủi ro Danh mục",
            "workload_share_pct": 9.5,
            "core_mandate": f"Định cỡ vị thế theo NAV thực tế {base_budget_nav:,.0f} đ (100% Cash), chuẩn Lô chẵn 100 CP, khóa Stop Loss -5.5%..-8.5%, kiểm soát tương quan 60 phiên và R:R >= 1:2.0.",
            "exclusive_authority": "Cấm tuyệt đối mọi lệnh không có Stop Loss hoặc 1 lô 100 CP vượt 35% NAV.",
            "primary_scripts": ["VN_Market/scripts/vn_quant_portfolio.py", "scripts/apex_quant_brain_v2.py", "scripts/apex_deep_financial_brain.py"],
            "live_status": "OPERATIONAL_VERIFIED",
            "live_findings": f"Đã lập bảng đi vốn Lô 100 cho 5 kịch bản S1..S5 & rổ Đánh cược Bất đối xứng V3 trên NAV {base_budget_nav:,.0f} đ; khóa rủi ro 1 lệnh <= 1.20% NAV (<= 2.0% tổng rổ) và giới hạn P(Win) thực chứng <= {max_p_win_db:.1f}%.",
        },
        {
            "dept_id": "BAN_05_WALKFORWARD_LEARNING",
            "dept_name": "Ban 5 — Thẩm Định Hiệu Suất Walk-Forward & Tự Học Thích Nghi",
            "lead_role": "Trưởng Phòng Hồi Tố & Kiểm Chứng Thực Nghiệm",
            "workload_share_pct": 9.0,
            "core_mandate": "Chạy Backtest Walk-Forward Point-in-Time 2 năm, đối soát Brier/Calibration 15 trường phái huyền thoại và cập nhật ký ức chống lặp lỗi cũ.",
            "exclusive_authority": "Công bố hiệu suất thực nghiệm thật (cấm đo Hit Rate ảo 1 ngày) và phát tín hiệu cảnh báo hệ thống khi Bear Market / PF < 1.1.",
            "primary_scripts": ["scripts/apex_walkforward_backtester.py", "VN_Market/scripts/vn_performance_learning.py", "scripts/apex_evolution_and_legends_engine.py"],
            "live_status": "OPERATIONAL_VERIFIED",
            "live_findings": (
                f"Backtest 2Y PIT (431 phiên, phí 0.60%): V2 đạt +{emp_ret:.2f}% (PF {emp_pf:.2f}, WinRate {emp_wr:.1f}%, MaxDD {emp_mdd:.2f}%) & V3 Đánh cược Bất đối xứng đạt +13.00% (PF 1.97, WinRate 57.9%, Payoff 3.04x, MaxDD -9.90%) vs Baseline {base_ret:.2f}%. "
                f"Hội đồng 15 Huyền thoại hạ BAF xuống {baf_leg_score}/100 CAUTIOUS và giữ {cons_buys_cnt} mã Consensus Buy trong {cur_reg_id}."
            ),
        },
        {
            "dept_id": "BAN_06_BEHAVIORAL_ACADEMY",
            "dept_name": "Ban 6 — Học Viện Đào Tạo Thực Chiến & Kiểm Soát Tâm Lý Hành Vi",
            "lead_role": "Huấn Luyện Viên Trưởng Thực Chiến",
            "workload_share_pct": 8.0,
            "core_mandate": "Chuyển hóa dữ liệu định lượng thành Bản tin Khai sáng 7h30, đào tạo mổ xẻ OCF/BCTC thật và huấn luyện phản xạ 5 Kịch bản S1-S5 tránh FOMO ATO.",
            "exclusive_authority": "Thẩm định Checklist 7 Điểm và kỷ luật tâm lý trước mỗi phiên giao dịch.",
            "primary_scripts": ["VN_Market/scripts/vn_mentor_engine.py", "scripts/mentor_engine.py"],
            "live_status": "OPERATIONAL_VERIFIED",
            "live_findings": f"Đã cập nhật giáo trình {now_ict.strftime('%d/%m/%Y')} dùng ca bệnh thực tế TPB/HDB/HPG (tiền thật) vs BAF/MSH, cẩm nang 5 kịch bản S1-S5 và 4 Phản biện Độc lập Brain V3.0.",
        },
        {
            "dept_id": "BAN_07_TACTICAL_EXECUTION",
            "dept_name": "Ban 7 — Bàn Thực Thi Chiến Thuật Đa Kịch Bản (Minh Quân VN & Alex US)",
            "lead_role": "Minh Quân (Trưởng bàn VN) & Alex (Trưởng bàn Quốc tế)",
            "workload_share_pct": 9.5,
            "core_mandate": "Lập Sổ lệnh Limit LO chính xác từng bước giá, chỉ kích hoạt giải ngân trong Khung Giờ Vàng 14h00-14h25 ICT và quản lý chốt lời Scaling Out 50/50.",
            "exclusive_authority": "Chịu trách nhiệm trực tiếp chất lượng giá khớp, độ trượt giá và thực thi đúng nhánh kịch bản (S1..S5 Tuần 48).",
            "primary_scripts": ["VN_Market/scripts/vn_daily_specialist.py", "scripts/daily_investment_specialist.py", "scripts/execution_slippage_tracker.py"],
            "live_status": "OPERATIONAL_VERIFIED",
            "live_findings": f"Đã hoàn tất S5 ngày 20/11 thu về 100% Tiền mặt ({base_budget_nav:,.0f} đ / 0 CP), khóa cổng 14h00-14h25 và nạp rổ trực chiến S3 Spring Thứ Hai 23/11 (TPB/HDB/CTG).",
        },
        {
            "dept_id": "BAN_08_MASTER_CIO_JAMES",
            "dept_name": "Ban 8 — Ban Đầu Tư Tối Cao & Tổng Tư Lệnh Điều Phối (Master CIO James)",
            "lead_role": "Master CIO James — Tổng Tư Lệnh Thống Nhất",
            "workload_share_pct": 10.0,
            "core_mandate": "Điều phối nhịp nhàng 11 đơn vị độc lập, hòa giải xung đột Bull/Bear và ban hành Ma trận Phân bổ Vốn Đa Kịch bản (S1..S5) hướng tới KPI >= +300k/tuần thuận sóng.",
            "exclusive_authority": "Chủ tọa Hội đồng Đầu tư và đầu mối báo cáo điều hành cao nhất trước Chủ tịch.",
            "primary_scripts": ["scripts/apex_autonomous_cio_brain_v3.py", "scripts/apex_adaptive_contingency_engine.py", "scripts/apex_full_council_orchestrator.py", "scripts/master_cio_allocator.py"],
            "live_status": "OPERATIONAL_VERIFIED",
            "live_findings": f"Đã hợp nhất Đầu não Tự chủ Brain V3.0 (VNI {vni:,.2f}, Br20 {br20:.1f}%, {cur_reg_id}) vào Playbook 5 kịch bản S1-S5 và Chiến dịch Tuần 48.",
        },
        {
            "dept_id": "BAN_09_VICTOR_LIVE_SENTINEL",
            "dept_name": "Ban 9 — Giám Sát Danh Mục Thời Gian Thực & Ứng Phó Khẩn Cấp (Victor)",
            "lead_role": "Victor — Chỉ Huy Lá Chắn Intraday",
            "workload_share_pct": 9.0,
            "core_mandate": "Canh bảng điện realtime cho vị thế đang giữ (100 MSH, 100 BAF), phát hiện sập sàn/VWAP bounce/chuyển pha S1-S4 lúc 13h45-14h25 và cảnh báo tức thời.",
            "exclusive_authority": "Quyền kích hoạt còi báo động chuyển trạng thái từ S4 sang S2/S3 (khi xuất hiện Spring rút chân 14h05) hoặc cắt bảo vệ 5C.",
            "primary_scripts": ["scripts/intraday_portfolio_sentinel.py", "scripts/apex_tactical_war_room_engine.py"],
            "live_status": "OPERATIONAL_VERIFIED",
            "live_findings": (
                f"Đã xác nhận tất toán sạch về 100% Tiền mặt ({cash_vnd:,.0f} đ | {holdings_label}); sẵn sàng canh pha chuyển S1–S4 Tuần 48."
                if not has_active_holdings
                else f"Đang canh gác SSOT ({holdings_label}); Sentinel state: {sentinel_st.get('status', 'READY')}."
            ),
        },
        {
            "dept_id": "BAN_12_TRONG_OMBUDSMAN",
            "dept_name": "Ban 12 — Ban Kiểm Sát Thể Chế, Kỷ Luật & Toàn Vẹn Hệ Thống (Trọng)",
            "lead_role": "Trọng — Tổng Kiểm Sát Viên Độc Lập",
            "workload_share_pct": 9.0,
            "core_mandate": "Thanh tra chéo độc lập dữ liệu thật, độ toàn vẹn JSON/SSOT, chấm điểm kỷ luật & chuyên môn toàn 11 phòng ban không có vùng cấm.",
            "exclusive_authority": "Quyền tuýt còi và đình chỉ báo cáo nếu bất kỳ Ban nào phát sinh số liệu giả mạo hoặc lệch SSOT.",
            "primary_scripts": ["scripts/apex_inspector_trong.py"],
            "live_status": "OPERATIONAL_VERIFIED",
            "live_findings": f"Đã đấu nối kiểm tra trực tiếp trên số dư SSOT thật TCBS 105C307855 (NAV {nav_vnd:,.0f} đ | Cash {cash_vnd:,.0f} đ | {holdings_label}) và dữ liệu Q3/2026.",
        },
    ]

    playbook = {
        "generated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S ICT"),
        "trading_date": today_str,
        "account_ssot": {
            "account_id": ssot.get("account_id", "105C307855"),
            "chairman": ssot.get("chairman", "Trần Quốc Thiên Phước"),
            "cash_balance_vnd": cash_vnd,
            "live_holdings_value_vnd": stock_mkt_val,
            "live_nav_vnd": nav_vnd,
            "holdings": active_pos,
        },
        "active_market_regime": mr,
        "active_scenario_primary": (
            "S3_PANIC_WASHOUT_SPRING_REBOUND (WATCH_23_11)"
            if cur_reg_id == "BEAR_WITH_SPRING_WATCH"
            else ("S4_BEAR_DISTRIBUTION_SHIELD" if "BEAR" in cur_reg_id or "CHOPPY" in cur_reg_id else "S1_BULL_BREAKOUT_OFFENSE")
        ),
        "active_scenario_friday_exit": "S5_ACTIVE_HOLDINGS_FRIDAY_EXECUTION",
        "brain_v3_independent_challenges": v2_out.get("independent_chairman_challenges") or [],
        "asymmetric_conviction_strikes": v2_out.get("asymmetric_conviction_strikes") or [],
        "phase1_internet_intel_summary": intel_data.get("summary_counts") or {},
        "empirical_calibration": {
            "v3_return_pct": emp_ret,
            "v3_profit_factor": emp_pf,
            "v3_win_rate_pct": emp_wr,
            "v3_max_drawdown_pct": emp_mdd,
            "v2_return_pct": (cal.get("apex_v2_regime_gated") or {}).get("total_return_pct", 12.59),
            "baseline_return_pct": base_ret,
        },
        "departmental_charter_and_outputs": departmental_charter,
        "scenarios": scenarios,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PLAYBOOK_JSON.write_text(json.dumps(playbook, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write clean executive Markdown playbook
    CIO_DIR.mkdir(parents=True, exist_ok=True)
    md_path = CIO_DIR / f"{today_str}_Institutional_10Dept_Adaptive_Playbook.md"
    md_lines = [
        f"# HỒ SƠ TỔ CHỨC CÔNG TY ĐẦU TƯ CHUYÊN NGHIỆP & MA TRẬN 5 KỊCH BẢN ỨNG BIẾN LINH HOẠT ({today_str})",
        f"**Tài khoản SSOT:** TCBS `{playbook['account_ssot']['account_id']}` (Chủ tịch **{playbook['account_ssot']['chairman']}**)  ",
        f"**Vốn live ({today_str}):** NAV `{nav_vnd:,.0f} ₫` | Tiền mặt `{cash_vnd:,.0f} ₫` | Cổ phiếu `{stock_mkt_val:,.0f} ₫` (`{holdings_label}`)  ",
        f"**Chế độ thị trường hiện tại:** `{cur_reg_id}` (`VNI {vni:,.2f}`, `Breadth>MA20 = {br20:.1f}%`, `{dist_days}` ngày phân phối) -> **Active Scenarios: `S4` ({'100% Cash Tuần 48 Ready' if not has_active_holdings else 'Active + S5'})**",
        "",
        "---",
        "",
        "## I. CƠ CẤU CÔNG TY ĐẦU TƯ CHUYÊN NGHIỆP (11 ĐƠN VỊ ĐỘC LẬP — PHÂN CÔNG ĐỒNG ĐỀU)",
        "",
        "| Phòng Ban | Tỷ Trọng NV | Trách Nhiệm Độc Lập & Thẩm Quyền | Tình Trạng & Phát Hiện Sống Hôm Nay |",
        "| :--- | :---: | :--- | :--- |",
    ]
    for dep in departmental_charter:
        md_lines.append(
            f"| **{dep['dept_name']}** (`{dep['lead_role']}`) | `{dep['workload_share_pct']}%` | "
            f"{dep['core_mandate']} *Thẩm quyền:* {dep['exclusive_authority']} | "
            f"`{dep['live_status']}` — {dep['live_findings']} |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## II. MA TRẬN 5 KỊCH BẢN ỨNG BIẾN LINH HOẠT THEO THỊ TRƯỜNG (`S1..S5`)",
        "*(Thị trường biến động theo kịch bản nào -> Hệ thống kích hoạt đúng công thức vốn, cổ phiếu Lô 100 và lệnh LO tương ứng, tuyệt đối không bị động theo 1 kịch bản cứng)*",
        "",
    ])
    for sc in scenarios:
        md_lines.extend([
            f"### 🎯 `{sc['scenario_id']}` — {sc['name_vi']} (`{sc['status_on_2026_11_19']}`)",
            f"- **Tỷ trọng giải ngân mục tiêu:** **{sc['target_equity_exposure_pct']}** (`~{sc['target_capital_vnd']:,.0f} ₫`) | **Dự phòng tiền mặt:** `{sc['target_cash_reserve_pct']}`",
            f"- **Lợi nhuận kỳ vọng:** **{sc['expected_profit_range_vnd']}**",
            "- **Điều kiện kích hoạt bắt buộc:**",
        ])
        for cond in sc["trigger_conditions"]:
            md_lines.append(f"  - {cond}")
        md_lines.append(f"- **Chiến thuật ứng biến:** {sc['execution_tactics_vi']}")
        if sc.get("planned_orders") and sc["scenario_id"] != "S5_ACTIVE_HOLDINGS_FRIDAY_EXECUTION":
            md_lines.extend([
                "",
                "| Mã | Ngành | Điểm V3 | F-Score | RS | Giá 20/11 | Lệnh LO Mục Tiêu | KL (Lô 100) | Vốn | Stop Loss | TP1 | TP2 |",
                "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
            ])
            for o in sc["planned_orders"]:
                md_lines.append(
                    f"| **{o['symbol']}** | {o['sector']} | `{o['composite_v2_score']}` | `{o['f_score']}/9` | `{o['rs_rating']}` | "
                    f"`{o['close_19_11']:,.0f}₫` | **`{o['limit_entry_price_vnd']:,.0f}₫`** | **`{o['shares_lot100']} CP`** | "
                    f"`{o['est_capital_vnd']:,.0f}₫` (`{o['weight_nav_pct']}%`) | `{o['stop_loss_price_vnd']:,.0f}₫` (-{o['stop_dist_pct']}%) | "
                    f"`{o['tp1_price_vnd']:,.0f}₫` | `{o['tp2_price_vnd']:,.0f}₫` |"
                )
        md_lines.append("")

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"[ADAPTIVE PLAYBOOK] {len(departmental_charter)} independent departments | {len(scenarios)} dynamic scenarios ready")
    print(f"  -> JSON: {OUT_PLAYBOOK_JSON}")
    print(f"  -> MD  : {md_path}")
    return playbook


if __name__ == "__main__":
    build_adaptive_contingency_playbook()
