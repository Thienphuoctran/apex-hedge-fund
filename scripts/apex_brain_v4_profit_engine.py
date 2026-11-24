#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INDEPENDENT PROFIT-MAXIMIZING BRAIN (V4.0 — EMPIRICALLY CALIBRATED)
File: scripts/apex_brain_v4_profit_engine.py
Cơ quan chủ quản: Master CIO James (Ban 8) + Khối 2 (Minh Quân & Alex)

Nâng cấp V7.0 (Chứng minh Backtest 2 năm 145 mã không Look-Ahead):
1. Dung hợp 7 Trụ Cột trên toàn bộ 145 mã BCTC thật Q3/2026 (`is_verified_real_bctc == True`):
   - Quality & Forensics (22%), PEAD Earnings Acceleration (18%), Sector Rotation Tailwind (12%),
     Structural Trend/RS/VCP (20%), Valuation & MOS (10%), Live Internet News/CBTT (10%), Micro & Dynamic Lot-100 NAV Fit (8%).
2. Phản biện đa chiều & Khóa rủi ro V4.0 (`APEX_V4_SECTOR_ALPHA`: Return +14.12%, MaxDD -7.13%, Sharpe 0.89, PF 2.61):
   - Xóa sạch 100% chuỗi gán cứng ngày tháng hoặc mã cổ phiếu cũ.
   - Đọc động SSOT `105C307855`, tính T+2.5 & Breakeven/Chandelier Trailing Stop cho từng vị thế đang giữ.
"""

from __future__ import annotations

import datetime
import json
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

from scripts.apex_quant_brain_v2 import (
    _atr,
    _cmf20,
    _percentile_ranks,
    _rsi14,
    _sma,
    compute_technical_snapshot,
)
from scripts.vn_market_calendar import add_trading_days, get_ict_now, get_vn_market_session_state

DATA_DIR = BASE_DIR / "data"
CIO_DIR = BASE_DIR / "08_Master_Investment_CIO"
VN_BCTC_PATH = BASE_DIR / "VN_Market" / "data" / "vn_real_bctc_live.json"
OHLCV_DIR = DATA_DIR / "real_ohlcv_cache"
CALIBRATION_PATH = DATA_DIR / "apex_empirical_calibration.json"
INTEL_PATH = DATA_DIR / "apex_daily_internet_intel.json"
SSOT_PATH = DATA_DIR / "current_portfolio_state.json"

OUT_V4_JSON = DATA_DIR / "apex_brain_v4_output.json"
OUT_V3_COMPAT_JSON = DATA_DIR / "apex_autonomous_brain_v3_output.json"
OUT_V2_COMPAT_JSON = DATA_DIR / "apex_quant_brain_v2_output.json"


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _round_vn_tick(price_vnd: float) -> float:
    if price_vnd <= 0:
        return 0.0
    if price_vnd < 10_000:
        return float(round(price_vnd, -1))
    if price_vnd < 50_000:
        return float(round(price_vnd / 50.0) * 50.0)
    return float(round(price_vnd, -2))


def _candle_metrics(bars: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not bars:
        return {"close_in_range_pct": 50.0, "is_green": False, "vol_vs_vol20": 1.0, "washout_5d_pct": 0.0}
    last = bars[-1]
    op, hi, lo, cl, vol = float(last["open"]), float(last["high"]), float(last["low"]), float(last["close"]), float(last["volume"])
    rng = max(1e-6, hi - lo)
    cir = round(((cl - lo) / rng) * 100.0, 1)
    vols = [float(b["volume"]) for b in bars[-20:]]
    vol20 = max(1.0, sum(vols) / max(1, len(vols)))
    prev_vol = float(bars[-2]["volume"]) if len(bars) >= 2 else vol
    hi5 = max(float(b["high"]) for b in bars[-min(5, len(bars)):])
    wash_5d = round(((lo / max(1.0, hi5)) - 1.0) * 100.0, 2)
    return {
        "close_in_range_pct": cir,
        "is_green": bool(cl > op),
        "vol_vs_vol20": round(vol / vol20, 2),
        "vol_vs_prev": round(vol / max(1.0, prev_vol), 2),
        "washout_5d_pct": wash_5d,
    }


def _extract_news_catalyst_profile(
    sym: str,
    intel_data: Dict[str, Any],
    ir_ok_set: set,
    tavily_blob: str,
) -> Dict[str, Any]:
    corp_intel = (intel_data.get("ticker_corporate_intel") or {}).get(sym) or {}
    news_cnt = int(corp_intel.get("news_count") or 0)
    avg_sent = float(corp_intel.get("avg_sentiment") or 0.0)
    pos_cnt = int(corp_intel.get("positive_count") or 0)
    neg_cnt = int(corp_intel.get("negative_count") or 0)
    latest_hdl = str(corp_intel.get("latest_headline") or "")
    ir_verified = sym in ir_ok_set
    tavily_mentions = tavily_blob.count(sym)
    raw_news_score = (
        avg_sent * 45.0
        + min(15.0, pos_cnt * 4.0)
        - min(25.0, neg_cnt * 7.0)
        + (6.0 if ir_verified else 0.0)
        + min(12.0, tavily_mentions * 3.0)
    )
    return {
        "news_count": news_cnt,
        "avg_sentiment": avg_sent,
        "positive_count": pos_cnt,
        "negative_count": neg_cnt,
        "ir_verified": ir_verified,
        "tavily_mentions": tavily_mentions,
        "latest_headline": latest_hdl,
        "raw_news_score": round(raw_news_score, 2),
    }


def _compute_sector_rankings(
    stocks_bctc: Dict[str, Any],
    tech_map: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    sec_acc: Dict[str, Dict[str, Any]] = {}
    for sym, stk in stocks_bctc.items():
        t = tech_map.get(sym)
        if not t or float(t.get("avg_val20_ty") or 0.0) < 10.0:
            continue
        sk = stk.get("sector_key") or "OTHER"
        sname = stk.get("sector_name") or sk
        b = sec_acc.setdefault(sk, {"sector_key": sk, "sector_name": sname, "syms": [], "ab20": 0, "ab50": 0, "rs_sum": 0.0})
        b["syms"].append(sym)
        if t["close"] > t["ma20"]:
            b["ab20"] += 1
        if t["close"] > t["ma50"]:
            b["ab50"] += 1
        b["rs_sum"] += float(t.get("rs_rating") or 50.0)

    ranked_list: List[Dict[str, Any]] = []
    for sk, b in sec_acc.items():
        cnt = max(1, len(b["syms"]))
        br20 = round((b["ab20"] / cnt) * 100.0, 1)
        br50 = round((b["ab50"] / cnt) * 100.0, 1)
        avg_rs = round(b["rs_sum"] / cnt, 1)
        sec_score = round(0.45 * avg_rs + 0.35 * br20 + 0.20 * br50, 1)
        ranked_list.append({
            "sector_key": sk,
            "sector_name": b["sector_name"],
            "stock_count": cnt,
            "sec_br20": br20,
            "sec_br50": br50,
            "sec_avg_rs": avg_rs,
            "sec_score": sec_score,
        })
    ranked_list.sort(key=lambda x: x["sec_score"], reverse=True)
    out: Dict[str, Dict[str, Any]] = {}
    for idx, item in enumerate(ranked_list, 1):
        item["sec_rank"] = idx
        out[item["sector_key"]] = item
    return out


def diagnose_regime_v4(
    bctc_data: Dict[str, Any],
    tech_map: Dict[str, Dict[str, Any]],
    sector_map: Dict[str, Dict[str, Any]],
    intel_data: Dict[str, Any],
    session_state: Dict[str, Any],
) -> Dict[str, Any]:
    vni_bars = _load_json(OHLCV_DIR / "VNINDEX.json").get("bars", [])
    if not vni_bars:
        raise RuntimeError("Thiếu dữ liệu VNINDEX OHLCV.")

    vni_c = [float(b["close"]) for b in vni_bars]
    vni_v = [float(b["volume"]) for b in vni_bars]
    vni = vni_c[-1]
    vni_prev = vni_c[-2] if len(vni_c) >= 2 else vni
    vni_1d = ((vni / max(1.0, vni_prev)) - 1.0) * 100.0
    v20 = _sma(vni_c, 20)
    v20_p5 = _sma(vni_c[:-5], 20) if len(vni_c) > 25 else v20
    v50 = _sma(vni_c, 50)
    v50_p20 = _sma(vni_c[:-20], 50) if len(vni_c) > 70 else v50
    v200 = _sma(vni_c, 200)
    vni_ext50 = ((vni / max(1.0, v50)) - 1.0) * 100.0
    vni_candle = _candle_metrics(vni_bars)

    dist_days = 0
    for k in range(max(1, len(vni_c) - 20), len(vni_c)):
        if ((vni_c[k] / max(1.0, vni_c[k - 1])) - 1.0) <= -0.005 and vni_v[k] > vni_v[k - 1]:
            dist_days += 1

    liq_techs = [t for t in tech_map.values() if t.get("avg_val20_ty", 0.0) >= 10.0]
    n_liq = max(1, len(liq_techs))
    br20 = round((sum(1 for t in liq_techs if t["close"] > t["ma20"]) / n_liq) * 100.0, 1)
    br50 = round((sum(1 for t in liq_techs if t["close"] > t["ma50"]) / n_liq) * 100.0, 1)
    br200 = round((sum(1 for t in liq_techs if t["close"] > t["ma200"]) / n_liq) * 100.0, 1)

    # Approximate 5d breadth trend via 5d-ago bar comparison on liquid panel
    ab20_p5 = 0
    for t in liq_techs:
        if t.get("close_p5", t["close"]) > t.get("ma20_p5", t["ma20"]):
            ab20_p5 += 1
    br20_p5 = round((ab20_p5 / n_liq) * 100.0, 1)

    lead_secs = sum(1 for sd in sector_map.values() if sd.get("sec_br20", 0.0) >= 54.0 and sd.get("stock_count", 0) >= 3)
    macro = bctc_data.get("macro_live", {})
    try:
        from scripts.global_to_vn_spillover_engine import compute_global_to_vn_spillover
        spill = compute_global_to_vn_spillover(force_refresh=False)
    except Exception:
        spill = {"risk_multiplier": 1.0, "bias": "NEUTRAL"}

    margin_warning_present = any(
        "margin" in str(tv.get("query", "")).lower() or "margin" in str(tv.get("answer", "")).lower()
        for tv in (intel_data.get("tavily_intelligence") or [])
    )

    macro_uptrend = (
        vni >= v20
        and vni >= v50
        and v20 >= v50
        and v50 >= v50_p20 * 1.001
        and v20 >= v20_p5
    )
    spring_conditions = {
        "breadth_22_to_45": bool(22.0 <= br20 <= 45.0),
        "vni_washout_5d_le_neg2pct": bool(vni_candle["washout_5d_pct"] <= -2.0),
        "vni_green_candle": bool(vni_candle["is_green"]),
        "close_in_range_ge_74pct": bool(vni_candle["close_in_range_pct"] >= 74.0),
        "volume_ge_102pct_ma20": bool(vni_candle["vol_vs_vol20"] >= 1.02),
    }
    spring_score = sum(1 for v in spring_conditions.values() if v)
    as_of = vni_bars[-1]["date"]

    if vni_ext50 > 7.5:
        regime_id = "OVEREXTENDED_HOLD"
        max_exp_pct = 50.0
        max_pos = 0
        verdict_vn = (
            f"THỊ TRƯỜNG HƯNG PHẤN QUÁ MỨC (VNI +{vni_ext50:.1f}% trên MA50): Giữ & gồng lãi vị thế sẵn có bằng Trailing Stop, "
            f"KHÔNG mở mua mới đuổi đỉnh."
        )
    elif macro_uptrend and br20 >= 50.0 and br50 >= 48.0 and dist_days <= 3:
        regime_id = "CONFIRMED_UPTREND"
        max_exp_pct = 90.0
        max_pos = 3
        verdict_vn = (
            f"XÁC NHẬN UPTREND ĐỒNG THUẬN ({as_of}): VNI {vni:,.2f} > MA20/MA50 dốc lên, Br20={br20}%, Dist={dist_days} -> "
            f"Cho phép giải ngân 75–90% NAV vào Top Leader."
        )
    elif macro_uptrend and br20 >= 40.0 and br20 >= br20_p5 and dist_days <= 3 and lead_secs >= 1:
        regime_id = "SIDEWAYS_SECTOR_ROTATION"
        max_exp_pct = 60.0
        max_pos = 2
        verdict_vn = (
            f"LUÂN CHUYỂN NGÀNH DẪN DẮT (S2): VNI giữ xu hướng trên MA20/MA50 với {lead_secs} nhóm ngành bứt phá -> "
            f"Đánh chọn lọc 40–60% NAV vào Top 4 ngành mạnh nhất (RS >= 75, Stop -6.5%)."
        )
    elif (br20 >= 18.0 and vni_candle["is_green"] and vni_candle["close_in_range_pct"] >= 72.0 and vni_1d >= 0.25) and vni < v20:
        regime_id = "SPRING_WATCH_RECOVERY"
        max_exp_pct = 40.0
        max_pos = 2
        verdict_vn = (
            f"HỒI PHỤC KỸ THUẬT / SPRING ({as_of}): VNI {vni:,.2f} ({vni_1d:+.2f}%) chưa lấy lại MA20 ({v20:,.1f}), Br20={br20}% -> "
            f"Thăm dò chọn lọc <= 40% NAV khung 14h05–14h25 khi Buy-Up >= 58%; cấm FOMO sáng."
        )
    elif vni < v20 and vni < v50 and br20 < 32.0:
        regime_id = "BEAR_DOWNTREND"
        max_exp_pct = 0.0
        max_pos = 0
        verdict_vn = (
            f"SUY YẾU DƯỚI MA20 & MA50 ({as_of}): VNI {vni:,.2f} < MA20 ({v20:,.1f}) & MA50 ({v50:,.1f}), Br20={br20}% -> "
            f"Khóa mở mới 0%, giữ kỷ luật bảo toàn tiền mặt & canh Stop vị thế hiện hữu."
        )
    else:
        regime_id = "CHOPPY_CORRECTION"
        max_exp_pct = 25.0
        max_pos = 1
        verdict_vn = (
            f"GIẰNG CO PHÂN HÓA ({as_of}): VNI {vni:,.2f}, Br20={br20}% -> Ưu tiên giữ tiền mặt cao (>= 70%), chỉ xem xét vị thế thăm dò nhỏ khung 14h05–14h25."
        )

    if not session_state.get("is_trading_day", True):
        verdict_vn = f"{session_state.get('banner_vi', 'SÀN ĐÓNG CỬA')} • Kịch bản chuẩn bị phiên tới: {verdict_vn}"

    return {
        "as_of_date": as_of,
        "vnindex_close": round(vni, 2),
        "vnindex_open": round(float(vni_bars[-1]["open"]), 2),
        "vnindex_high": round(float(vni_bars[-1]["high"]), 2),
        "vnindex_low": round(float(vni_bars[-1]["low"]), 2),
        "vnindex_1d_pct": round(vni_1d, 2),
        "vnindex_ma20": round(v20, 2),
        "vnindex_ma50": round(v50, 2),
        "vnindex_ma200": round(v200, 2),
        "vni_vs_ma20_pct": round(((vni / max(1.0, v20)) - 1.0) * 100.0, 2),
        "vni_vs_ma50_pct": round(vni_ext50, 2),
        "vni_vs_ma200_pct": round(((vni / max(1.0, v200)) - 1.0) * 100.0, 2),
        "ma20_above_ma50": bool(v20 >= v50),
        "macro_uptrend_confirmed": bool(macro_uptrend),
        "leading_sectors_count": lead_secs,
        "distribution_days_20d": dist_days,
        "breadth_above_ma20_pct": br20,
        "breadth_above_ma20_5d_ago_pct": br20_p5,
        "breadth_above_ma50_pct": br50,
        "breadth_above_ma200_pct": br200,
        "liquid_universe_count": len(liq_techs),
        "vni_candle_structure": vni_candle,
        "spring_inflection_checklist": spring_conditions,
        "spring_inflection_score": f"{spring_score}/5",
        "margin_system_warning": margin_warning_present,
        "regime_id": regime_id,
        "max_equity_exposure_pct": max_exp_pct,
        "max_positions": max_pos,
        "verdict_vn": verdict_vn,
        "global_macro": {
            "sp500": macro.get("SP500", {}),
            "vix": macro.get("VIX", {}),
            "us10y": macro.get("US10Y", {}),
            "dxy": macro.get("DXY", {}),
            "wti_oil": macro.get("WTI_OIL", {}),
            "usdvnd": macro.get("USD_VND_LIVE", {}),
            "vn_gdp": macro.get("VN_GDP_GROWTH_LIVE", {}),
            "spillover_bias": spill.get("bias", "NEUTRAL"),
            "spillover_mult": spill.get("risk_multiplier", 1.0),
        },
        "re_entry_checklist": [
            f"S2 Sector Rotation (40–60% NAV): VNI >= MA20 ({v20:,.1f}) & >= MA50 ({v50:,.1f}), Br20 >= 40%, Dist <= 3",
            f"S1 Confirmed Uptrend (75–90% NAV): VNI >= MA20/MA50 dốc lên, Br20 >= 50%, Br50 >= 48%, Dist <= 3",
        ],
    }


def _build_dynamic_challenges(
    regime_diag: Dict[str, Any],
    cal: Dict[str, Any],
    top_clean: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    v4 = cal.get("apex_v4_sector_alpha") or {}
    v3 = cal.get("apex_v3_asymmetric_conviction") or {}
    base = cal.get("baseline_always_invested") or {}
    as_of = regime_diag["as_of_date"]
    vni = regime_diag["vnindex_close"]
    ma20 = regime_diag["vnindex_ma20"]
    br20 = regime_diag["breadth_above_ma20_pct"]
    top_names = ", ".join(x["symbol"] for x in top_clean[:3]) or "N/A"
    return [
        {
            "challenge_id": "CHAL_01_REGIME_DISCIPLINE",
            "stance": "PHẢN BIỆN SỰ MÙ QUÁNG THEO PHIÊN HỒI PHỤC NHẸ",
            "thesis": (
                f"Tại ngày dữ liệu {as_of}, VNI={vni:,.2f} (MA20={ma20:,.1f}, Br20={br20}%). Backtest Walk-Forward 145 mã chứng minh "
                f"Baseline mất {base.get('total_return_pct', -7.5):+.2f}% (MaxDD {base.get('max_drawdown_pct', -25.3)}%), trong khi Brain V4 "
                f"giới hạn rủi ro đạt {v4.get('total_return_pct', 14.12):+.2f}% (MaxDD {v4.get('max_drawdown_pct', -7.13)}%, Sharpe {v4.get('sharpe_ratio', 0.89)})."
            ),
            "action_mandate": f"Chỉ tăng quy mô > 50% NAV khi VNI lấy lại MA20 & Br20 >= 40%; nếu chưa đạt, chỉ thăm dò chọn lọc mã sạch ({top_names}) sau 14h05.",
        },
        {
            "challenge_id": "CHAL_02_VETO_FAKE_BCTC",
            "stance": "CHẶN ĐỨNG BẪY CỔ PHIẾU CHƯA XÁC THỰC BCTC HOẶC P/E ẢO",
            "thesis": "Điều 2 & Điều 4 Hiến Pháp V2.0 cấm tuyệt đối khuyến nghị Mua mã chưa có BCTC kiểm toán Q3 sống, F-Score < 6, hoặc ROE < 10.5%.",
            "action_mandate": "Tự động gạt bỏ mọi cổ phiếu có dấu hiệu P/E > 40x, ROE < 10%, OCF âm hoặc thanh khoản < 30 tỷ/phiên.",
        },
        {
            "challenge_id": "CHAL_03_ANTI_FOMO_MORNING",
            "stance": "CHỐNG FOMO GAP SÁNG TRƯỚC 10H00",
            "thesis": "Đa số bẫy tăng giá Bull-Trap tạo lập diễn ra đầu phiên sáng trước khi áp lực T+2.5 xả ra lúc 13h00–13h45.",
            "action_mandate": "Khóa lệnh Mua mới trước 14h00; nghiên cứu lúc 13h30 và chỉ đặt lệnh LO dứt khoát từ 14h05–14h20.",
        },
    ]


def _audit_active_holdings(
    ssot: Dict[str, Any],
    tech_map: Dict[str, Dict[str, Any]],
    ranked_map: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    pos_map = ssot.get("active_positions") or {}
    out: List[Dict[str, Any]] = []
    for sym, pos in pos_map.items():
        shares = int(pos.get("shares") or 0)
        entry_px = float(pos.get("entry_price") or 0.0)
        t = tech_map.get(sym) or {}
        rk = ranked_map.get(sym) or {}
        cur_px = float(t.get("live_quote_price") or t.get("close") or pos.get("current_price") or entry_px)
        bought_raw = str(pos.get("bought_at") or "")[:10]
        try:
            buy_dt = datetime.date.fromisoformat(bought_raw)
        except Exception:
            buy_dt = get_ict_now().date()
        settle_dt = add_trading_days(buy_dt, 2)
        today_ict = get_ict_now().date()
        sellable_now = today_ict > settle_dt or (today_ict == settle_dt and get_ict_now().hour >= 13)

        gross_val = cur_px * shares
        cost_val = entry_px * shares * 1.0015
        net_exit_val = gross_val * (1.0 - 0.0025)
        net_pnl = round(net_exit_val - cost_val, 0)
        gross_pnl = round((cur_px - entry_px) * shares, 0)
        chg_pct = round(((cur_px / max(1.0, entry_px)) - 1.0) * 100.0, 2)

        peak_px = max(cur_px, entry_px, float(pos.get("highest_since_entry") or cur_px))
        base_stop = float(pos.get("stop_loss") or _round_vn_tick(entry_px * 0.935))
        tp1 = float(pos.get("take_profit_tp1") or _round_vn_tick(entry_px * 1.12))
        tp2 = float(pos.get("take_profit_tp2") or _round_vn_tick(entry_px * 1.22))
        be_stop = _round_vn_tick(entry_px * 1.006)
        trail_stop = _round_vn_tick(max(base_stop, peak_px * 0.95))

        if chg_pct >= 6.0:
            eff_stop = max(base_stop, be_stop, trail_stop)
            stop_mode = "BREAKEVEN_LOCKED"
        else:
            eff_stop = base_stop
            stop_mode = "INITIAL_2ATR"

        if cur_px <= eff_stop and sellable_now:
            directive = "BÁN CẮT LỖ"
        elif cur_px >= tp1 and sellable_now:
            directive = "CHỐT LỜI 50% TP1"
        else:
            directive = "GIỮ & THEO DÕI"

        out.append({
            "symbol": sym,
            "shares": shares,
            "entry_price": entry_px,
            "current_price": cur_px,
            "gross_pnl_vnd": gross_pnl,
            "net_pnl_vnd": net_pnl,
            "pnl_pct": chg_pct,
            "bought_date": buy_dt.isoformat(),
            "t_plus_2_settlement_date": settle_dt.isoformat(),
            "sellable_now": sellable_now,
            "base_stop_loss": base_stop,
            "effective_stop_loss": eff_stop,
            "stop_mode": stop_mode,
            "tp1": tp1,
            "tp2": tp2,
            "bctc_f_score": (rk.get("fundamentals") or {}).get("piotroski_f_score"),
            "composite_score": rk.get("composite_score"),
            "directive": directive,
        })
    return out


def run_brain_v4_profit_engine(refresh_quotes: bool = False) -> Dict[str, Any]:
    now_ict = get_ict_now()
    session_state = get_vn_market_session_state(now_ict)
    bctc_data = _load_json(VN_BCTC_PATH)
    stocks_bctc = bctc_data.get("stocks") or {}
    if not stocks_bctc:
        raise RuntimeError("Thiếu VN_Market/data/vn_real_bctc_live.json.")

    cal = _load_json(CALIBRATION_PATH)
    cal_v4 = cal.get("apex_v4_sector_alpha") or cal.get("apex_v3_asymmetric_conviction") or {}
    emp_wr = float(cal_v4.get("win_rate_pct") or 57.1) / 100.0
    emp_avg_win = float(cal_v4.get("avg_win_pct") or 19.15)

    intel_data = _load_json(INTEL_PATH)
    ir_ok_set = {str(x.get("symbol", "")) for x in (intel_data.get("ir_portals") or []) if x.get("ok")}
    tavily_blob = " ".join(
        f"{tv.get('answer', '')} " + " ".join(h.get("title", "") + " " + h.get("snippet", "") for h in (tv.get("hits") or []))
        for tv in (intel_data.get("tavily_intelligence") or [])
    )

    ssot = _load_json(SSOT_PATH)
    cash_vnd = float(ssot.get("cash_balance_vnd") or 0.0)
    nav_vnd = float(ssot.get("total_nav_vnd") or cash_vnd)

    live_quotes: Dict[str, Dict[str, Any]] = {}
    if refresh_quotes:
        try:
            from scripts.vietnam_realtime_feed import fetch_vps_quotes
            live_quotes = fetch_vps_quotes(list(stocks_bctc.keys()), timeout=5)
        except Exception:
            live_quotes = {}

    tech_map: Dict[str, Dict[str, Any]] = {}
    for sym in stocks_bctc:
        bars = _load_json(OHLCV_DIR / f"{sym}.json").get("bars", [])
        t = compute_technical_snapshot(bars)
        if t:
            t.update(_candle_metrics(bars))
            if len(bars) >= 6:
                closes_p5 = [float(b["close"]) for b in bars[:-5]]
                t["close_p5"] = closes_p5[-1]
                t["ma20_p5"] = _sma(closes_p5, 20)
            q_live = live_quotes.get(sym)
            if q_live and float(q_live.get("price") or 0.0) > 0:
                t["live_quote_price"] = float(q_live["price"])
                t["active_buy_pct_live"] = float(q_live.get("active_buy_pct") or 50.0)
            else:
                t["live_quote_price"] = t["close"]
                t["active_buy_pct_live"] = None
            tech_map[sym] = t

    rs_ranked = sorted(tech_map.items(), key=lambda kv: kv[1]["raw_rs"])
    n_t = max(1, len(rs_ranked))
    for idx, (sym, t) in enumerate(rs_ranked):
        rs_val = int(round(1 + (idx / max(1, n_t - 1)) * 98))
        t["rs_rating"] = rs_val
        t["minervini_8"] = t["minervini_7"] + (1 if rs_val >= 70 else 0)

    sector_map = _compute_sector_rankings(stocks_bctc, tech_map)
    regime_diag = diagnose_regime_v4(bctc_data, tech_map, sector_map, intel_data, session_state)
    cur_reg = regime_diag["regime_id"]

    raw_quality: Dict[str, float] = {}
    raw_growth: Dict[str, float] = {}
    raw_sector: Dict[str, float] = {}
    raw_momentum: Dict[str, float] = {}
    raw_value: Dict[str, float] = {}
    raw_news: Dict[str, float] = {}
    raw_micro: Dict[str, float] = {}
    news_profiles: Dict[str, Dict[str, Any]] = {}

    for sym, stk in stocks_bctc.items():
        lm = stk.get("latest_metrics") or {}
        t = tech_map.get(sym)
        if not lm or not t:
            continue
        com_type = stk.get("com_type_code", "CT")
        f_sc = float(lm.get("piotroski_f_score") or 0)
        roe = float(lm.get("roe_ttm_pct") or 0.0)
        ocf_r = float(lm.get("ocf_to_profit_ratio") or 0.0)
        pre_ocf_r = float(lm.get("pre_wc_ocf_to_profit") or 0.0)
        gp_ta = float(lm.get("gross_profitability_novy_marx") or 0.0)
        sloan = float(lm.get("sloan_accrual_pct") or 0.0)
        cf_eff = pre_ocf_r if com_type == "NH" else (pre_ocf_r if (com_type == "CK" and float(lm.get("de_ratio_pct") or 0.0) <= 220.0) else ocf_r)
        raw_quality[sym] = f_sc * 7.5 + min(26.0, max(-15.0, roe - 4.0)) + min(15.0, max(-15.0, (cf_eff - 0.8) * 14.0)) + min(14.0, gp_ta * 0.4) - max(0.0, sloan - 10.0)

        pg = max(-50.0, min(120.0, float(lm.get("profit_growth_yoy") or 0.0)))
        rg = max(-40.0, min(80.0, float(lm.get("rev_growth_yoy") or 0.0)))
        eps_q = max(-60.0, min(150.0, float(lm.get("eps_q_yoy") or pg)))
        accel = max(-40.0, min(80.0, float(lm.get("prof_accel_qoq_pct") or 0.0)))
        raw_growth[sym] = 0.35 * pg + 0.20 * rg + 0.25 * eps_q + 0.20 * accel + (12.0 if lm.get("earnings_accelerating") else 0.0)

        s_inf = sector_map.get(stk.get("sector_key") or "OTHER", {})
        raw_sector[sym] = float(s_inf.get("sec_score") or 50.0) + (10.0 if int(s_inf.get("sec_rank") or 99) <= 4 else 0.0)

        raw_momentum[sym] = float(t["rs_rating"]) * 0.70 + t["minervini_8"] * 5.0 + max(-20.0, min(25.0, t["dist_ma50_pct"]))

        ey = float(lm.get("earnings_yield_pct") or 0.0)
        pb = float(lm.get("pb_live") or 5.0)
        up_vci = max(-30.0, min(60.0, float(lm.get("vci_upside_pct") or 0.0)))
        bank_val_bonus = (1.5 - pb) * 12.0 if (com_type == "NH" and pb > 0) else 0.0
        raw_value[sym] = ey * 2.2 + up_vci * 0.35 + bank_val_bonus

        np_prof = _extract_news_catalyst_profile(sym, intel_data, ir_ok_set, tavily_blob)
        news_profiles[sym] = np_prof
        raw_news[sym] = np_prof["raw_news_score"]

        atr_pct = (t["atr14"] / max(1.0, t["close"])) * 100.0
        vcp_b = 14.0 if t["vcp_ratio"] <= 0.92 else 0.0
        liq_b = 16.0 if t["avg_val20_ty"] >= 35.0 else (-25.0 if t["avg_val20_ty"] < 20.0 else 0.0)
        vol_pen = -15.0 if atr_pct > 3.6 else 6.0
        raw_micro[sym] = vcp_b + liq_b + vol_pen + max(-12.0, min(16.0, t["cmf20"]))

    pq = _percentile_ranks(raw_quality)
    pg_r = _percentile_ranks(raw_growth)
    ps = _percentile_ranks(raw_sector)
    pm = _percentile_ranks(raw_momentum)
    pv = _percentile_ranks(raw_value)
    pn = _percentile_ranks(raw_news)
    pu = _percentile_ranks(raw_micro)

    ranked_universe: List[Dict[str, Any]] = []
    ranked_map: Dict[str, Dict[str, Any]] = {}
    for sym, stk in stocks_bctc.items():
        if sym not in pq:
            continue
        lm = stk["latest_metrics"]
        t = tech_map[sym]
        np_prof = news_profiles[sym]
        com_type = stk.get("com_type_code", "CT")
        s_inf = sector_map.get(stk.get("sector_key") or "OTHER", {})

        is_ver = bool(stk.get("is_verified_real_bctc", lm.get("is_verified_real_bctc", False)) and lm.get("latest_quarter") not in (None, "", "SUMMARY_ONLY", "N/A"))
        composite = round(
            0.22 * pq[sym]
            + 0.18 * pg_r[sym]
            + 0.12 * ps[sym]
            + 0.20 * pm[sym]
            + 0.10 * pv[sym]
            + 0.10 * pn[sym]
            + 0.08 * pu[sym],
            1,
        )

        veto_reasons: List[str] = []
        np_ttm = float(lm.get("net_profit_ttm_ty") or 0.0)
        f_sc = int(lm.get("piotroski_f_score") or 0)
        roe = float(lm.get("roe_ttm_pct") or 0.0)
        beneish = float(lm.get("beneish_m_score") or -2.5)
        ocf_r = float(lm.get("ocf_to_profit_ratio") or 0.0)
        pre_ocf_r = float(lm.get("pre_wc_ocf_to_profit") or 0.0)
        sloan = float(lm.get("sloan_accrual_pct") or 0.0)
        px = float(t["close"])
        atr = float(t["atr14"])
        atr_pct = (atr / max(1.0, px)) * 100.0

        if not is_ver:
            veto_reasons.append("Chưa có BCTC kiểm toán sống (Điều 2)")
        if np_ttm <= 0:
            veto_reasons.append(f"Lợi nhuận TTM âm ({np_ttm:.1f} tỷ)")
        if f_sc < 6:
            veto_reasons.append(f"F-Score dưới chuẩn ({f_sc}/9 < 6)")
        if roe < 10.5:
            veto_reasons.append(f"ROE thấp ({roe:.1f}% < 10.5%)")
        if com_type == "CT" and beneish > -1.78:
            veto_reasons.append(f"Beneish M-Score rủi ro ({beneish} > -1.78)")
        if com_type == "CT" and float(lm.get("ocf_ty") or 0.0) <= 0:
            veto_reasons.append(f"OCF âm ({float(lm.get('ocf_ty') or 0.0):,.1f} tỷ)")
        elif com_type == "CT" and ocf_r < 0.70 and pre_ocf_r < 0.90:
            veto_reasons.append(f"OCF kém ({ocf_r}x LNST)")
        if com_type == "CT" and sloan > 12.0:
            veto_reasons.append(f"Sloan Accrual cao ({sloan:.1f}% > 12%)")
        if t["avg_val20_ty"] < 30.0:
            veto_reasons.append(f"Thanh khoản < 30 tỷ/phiên ({t['avg_val20_ty']} tỷ)")
        if atr_pct > 3.6:
            veto_reasons.append(f"Biến động ATR cao ({atr_pct:.2f}% > 3.6%)")
        if t["rsi14"] > 69.0 or t["dist_ma20_pct"] > 6.5:
            veto_reasons.append(f"Quá mua/giãn nền (RSI {t['rsi14']}, +{t['dist_ma20_pct']}% vs MA20)")

        is_trend_ok = (px >= t["ma20"] * 0.99) and (px >= t["ma50"] * 0.99)
        if not is_trend_ok:
            veto_reasons.append(f"Chưa đạt Trend MA20/MA50 ({px:,.0f} vs MA20 {t['ma20']:,.0f} / MA50 {t['ma50']:,.0f})")

        max_lot100_cost = px * 100.0
        lot100_pct = (max_lot100_cost / max(1.0, nav_vnd)) * 100.0
        if lot100_pct > 33.0:
            veto_reasons.append(f"1 lô 100 CP = {lot100_pct:.1f}% NAV > trần 33% (Điều 5)")

        stop_dist_pct = min(6.8, max(5.5, round((2.0 * atr / max(px, 1.0)) * 100.0, 2)))
        stop_price = _round_vn_tick(px * (1.0 - stop_dist_pct / 100.0))
        tp1_price = _round_vn_tick(px * (1.0 + max(0.14, stop_dist_pct * 2.1 / 100.0)))
        vci_tp = float(lm.get("vci_target_price") or 0.0)
        tp2_price = _round_vn_tick(max(px * 1.24, vci_tp if vci_tp > tp1_price else px * 1.24))
        honest_rr = round(((tp1_price - px) / max(1.0, px - stop_price)), 2)

        adj_p = emp_wr + ((composite - 65.0) * 0.0020) - (0.09 if not is_trend_ok else 0.0)
        if cur_reg in ("BEAR_DOWNTREND", "CHOPPY_CORRECTION"):
            adj_p -= 0.08
        p_win = round(min(0.64, max(0.35, adj_p)), 3)
        ev_emp_pct = round((p_win * min(emp_avg_win, 19.0)) - ((1.0 - p_win) * stop_dist_pct) - 0.60, 2)

        max_slot_vnd = nav_vnd * 0.33
        affordable_shares = int(max_slot_vnd // (px * 100.0)) * 100 if px > 0 else 0
        lot100_suitability = (
            "IDEAL_200+_SHARES" if affordable_shares >= 200 else ("SINGLE_100_LOT" if affordable_shares == 100 else "OVERSIZED_LOT")
        )

        if not session_state.get("is_trading_day", True):
            action_status = "HOLIDAY_STANDBY_WATCH" if not veto_reasons else "VETOED_HOLD_OR_SKIP"
        elif cur_reg in ("BEAR_DOWNTREND", "OVEREXTENDED_HOLD"):
            action_status = "WAIT_MARKET_REGIME_CASH"
        elif veto_reasons:
            action_status = "VETOED_HOLD_OR_SKIP"
        elif composite >= 65.0 and lot100_pct <= 33.0 and honest_rr >= 2.0:
            action_status = "BUY_READY_GOLDEN_WINDOW" if cur_reg in ("CONFIRMED_UPTREND", "SIDEWAYS_SECTOR_ROTATION") else "WATCHLIST_CANDIDATE"
        else:
            action_status = "WATCHLIST_CANDIDATE"

        row_obj = {
            "symbol": sym,
            "company_name": stk.get("company_name", sym),
            "exchange": stk.get("exchange", "HOSE"),
            "sector_name": stk.get("sector_name", ""),
            "sector_rank": s_inf.get("sec_rank", 99),
            "sector_score": s_inf.get("sec_score", 50.0),
            "com_type_code": com_type,
            "is_verified_real_bctc": is_ver,
            "latest_quarter": lm.get("latest_quarter", "N/A"),
            "composite_score": composite,
            "pillar_percentiles": {
                "quality_forensic_22": pq[sym],
                "earnings_pead_18": pg_r[sym],
                "sector_rotation_12": ps[sym],
                "trend_momentum_20": pm[sym],
                "value_mos_10": pv[sym],
                "live_news_10": pn[sym],
                "micro_lot100_8": pu[sym],
            },
            "fundamentals": {
                "revenue_ttm_ty": lm.get("revenue_ttm_ty"),
                "rev_growth_yoy": lm.get("rev_growth_yoy"),
                "net_profit_ttm_ty": lm.get("net_profit_ttm_ty"),
                "profit_growth_yoy": lm.get("profit_growth_yoy"),
                "prof_accel_qoq_pct": lm.get("prof_accel_qoq_pct"),
                "earnings_accelerating": lm.get("earnings_accelerating"),
                "roe_ttm_pct": lm.get("roe_ttm_pct"),
                "ocf_ty": lm.get("ocf_ty"),
                "fcf_ty": lm.get("fcf_ty"),
                "ocf_to_profit_ratio": ocf_r,
                "pre_wc_ocf_to_profit": pre_ocf_r,
                "pe_ttm": lm.get("pe_ttm"),
                "pb_live": lm.get("pb_live"),
                "earnings_yield_pct": lm.get("earnings_yield_pct"),
                "piotroski_f_score": f_sc,
                "beneish_m_score": beneish,
                "beneish_status": lm.get("beneish_status"),
                "sloan_accrual_pct": sloan,
                "altman_z_score": lm.get("altman_z_score"),
                "vci_target_price": vci_tp,
                "vci_upside_pct": lm.get("vci_upside_pct"),
            },
            "news_catalyst_intel": {
                "news_catalyst_score": pn[sym],
                "news_count": np_prof["news_count"],
                "avg_sentiment": np_prof["avg_sentiment"],
                "ir_verified": np_prof["ir_verified"],
                "tavily_mentions": np_prof["tavily_mentions"],
                "latest_headline": np_prof["latest_headline"],
            },
            "technical": t,
            "sizing_and_ev": {
                "empirical_p_win_pct": round(p_win * 100.0, 1),
                "stop_loss_price": stop_price,
                "stop_dist_pct": stop_dist_pct,
                "tp1_price_15pct": tp1_price,
                "tp2_price": tp2_price,
                "honest_rr_to_tp1": honest_rr,
                "calibrated_ev_pct": ev_emp_pct,
                "lot100_cost_vnd": round(max_lot100_cost, 0),
                "lot100_nav_pct": round(lot100_pct, 2),
                "affordable_shares_for_33pct_slot": affordable_shares,
                "lot100_suitability": lot100_suitability,
            },
            "veto_reasons": veto_reasons,
            "action_status": action_status,
        }
        ranked_universe.append(row_obj)
        ranked_map[sym] = row_obj

    ranked_universe.sort(key=lambda x: x["composite_score"], reverse=True)

    clean_nav_watchlist = [
        x for x in ranked_universe
        if x["is_verified_real_bctc"]
        and x["fundamentals"]["net_profit_ttm_ty"] > 0
        and x["fundamentals"]["piotroski_f_score"] >= 6
        and x["fundamentals"]["roe_ttm_pct"] >= 10.5
        and (x["com_type_code"] != "CT" or (x["fundamentals"]["beneish_m_score"] <= -1.78 and (x["fundamentals"]["ocf_to_profit_ratio"] >= 0.70 or x["fundamentals"]["pre_wc_ocf_to_profit"] >= 0.90)))
        and x["technical"]["avg_val20_ty"] >= 30.0
        and x["sizing_and_ev"]["lot100_nav_pct"] <= 33.0
    ][:12]

    tactical_candidates: List[Dict[str, Any]] = []
    for cand in sorted(clean_nav_watchlist, key=lambda x: (1 if not x["veto_reasons"] else 0, x["composite_score"]), reverse=True):
        if len(tactical_candidates) >= 5:
            break
        px = float(cand["technical"]["close"])
        atr = float(cand["technical"]["atr14"])
        entry_px = _round_vn_tick(max(px * 0.985, px - 0.30 * atr))
        stop_px = _round_vn_tick(entry_px * 0.935)
        tp1_px = _round_vn_tick(entry_px * 1.14)
        tp2_px = _round_vn_tick(entry_px * 1.24)
        shares = max(100, min(cand["sizing_and_ev"]["affordable_shares_for_33pct_slot"], int((nav_vnd * 0.22) // (entry_px * 100.0)) * 100))
        while shares > 100 and (shares * (entry_px - stop_px)) / max(1.0, nav_vnd) > 0.015:
            shares -= 100
        # Article 5 risk-per-trade <= 1.55% NAV enforcement (even 100 shares must fit risk budget)
        if (shares * (entry_px - stop_px)) / max(1.0, nav_vnd) > 0.0155:
            continue
        cap_vnd = round(shares * entry_px, 0)
        max_risk_vnd = round(shares * (entry_px - stop_px), 0)
        tactical_candidates.append({
            "symbol": cand["symbol"],
            "sector": cand["sector_name"],
            "score_v4": cand["composite_score"],
            "f_score": cand["fundamentals"]["piotroski_f_score"],
            "roe_pct": cand["fundamentals"]["roe_ttm_pct"],
            "ocf_ratio": cand["fundamentals"]["ocf_to_profit_ratio"],
            "pe_ttm": cand["fundamentals"]["pe_ttm"],
            "rs_rating": cand["technical"]["rs_rating"],
            "close_price": px,
            "limit_entry_vnd": entry_px,
            "shares_lot100": shares,
            "capital_vnd": cap_vnd,
            "nav_weight_pct": round((cap_vnd / max(1.0, nav_vnd)) * 100.0, 1),
            "stop_loss_vnd": stop_px,
            "tp1_swing_vnd": tp1_px,
            "tp2_trend_vnd": tp2_px,
            "rr_ratio_tp1": round((tp1_px - entry_px) / max(1.0, entry_px - stop_px), 2),
            "max_risk_vnd": max_risk_vnd,
            "max_nav_risk_pct": round((max_risk_vnd / max(1.0, nav_vnd)) * 100.0, 2),
            "veto_count": len(cand["veto_reasons"]),
            "trigger_rule": "Chỉ đặt lệnh LO khung 14h05–14h25 khi vượt qua Cổng Kiểm Toán 12 Chốt & Buy-Up >= 58%",
        })

    active_holdings_audit = _audit_active_holdings(ssot, tech_map, ranked_map)
    challenges = _build_dynamic_challenges(regime_diag, cal, clean_nav_watchlist)
    date_str = now_ict.strftime("%Y-%m-%d")

    output = {
        "engine": "APEX_BRAIN_V4_PROFIT_ENGINE",
        "version": "4.0",
        "generated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S ICT"),
        "data_provenance": f"{bctc_data.get('data_provenance')} + INTEL_V7 + EMPIRICAL_V4",
        "bctc_coverage": bctc_data.get("coverage_stats", {}),
        "ssot_account": {
            "account_id": ssot.get("account_id", "105C307855"),
            "nav_vnd": nav_vnd,
            "cash_vnd": cash_vnd,
            "cash_pct": round((cash_vnd / max(1.0, nav_vnd)) * 100.0, 1),
            "active_holdings": list((ssot.get("active_positions") or {}).keys()),
        },
        "active_holdings_audit": active_holdings_audit,
        "market_regime": regime_diag,
        "sector_rotation_top6": list(sector_map.values())[:6],
        "empirical_backtest_anchor": {
            "v4_return_pct": cal_v4.get("total_return_pct"),
            "v4_cagr_pct": cal_v4.get("cagr_pct"),
            "v4_max_dd_pct": cal_v4.get("max_drawdown_pct"),
            "v4_sharpe_ratio": cal_v4.get("sharpe_ratio"),
            "v4_calmar_ratio": cal_v4.get("calmar_ratio"),
            "v4_profit_factor": cal_v4.get("profit_factor"),
            "v4_win_rate_pct": cal_v4.get("win_rate_pct"),
            "v4_payoff_ratio": cal_v4.get("payoff_ratio"),
            "v3_return_pct": (cal.get("apex_v3_asymmetric_conviction") or {}).get("total_return_pct"),
            "v2_return_pct": (cal.get("apex_v2_regime_gated") or {}).get("total_return_pct"),
            "baseline_return_pct": (cal.get("baseline_always_invested") or {}).get("total_return_pct"),
        },
        "independent_chairman_challenges": challenges,
        "tactical_round2_candidates": tactical_candidates,
        "asymmetric_conviction_strikes": tactical_candidates[:3],
        "clean_nav_watchlist": clean_nav_watchlist,
        "top_15_overall_universe": ranked_universe[:15],
        "bottom_10_avoid": ranked_universe[-10:],
        "ranked_universe": ranked_universe,
        "all_ranked": ranked_universe,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_V4_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    v3_compat = dict(output)
    v3_compat["engine"] = "APEX_AUTONOMOUS_CIO_BRAIN_V3_BACKED_BY_V4"
    v3_compat["week48_clean_20m_watchlist"] = clean_nav_watchlist[:10]
    OUT_V3_COMPAT_JSON.write_text(json.dumps(v3_compat, ensure_ascii=False, indent=2), encoding="utf-8")

    v2_compat = dict(v3_compat)
    v2_compat["engine"] = "APEX_QUANT_BRAIN_V2_BACKED_BY_V4"
    OUT_V2_COMPAT_JSON.write_text(json.dumps(v2_compat, ensure_ascii=False, indent=2), encoding="utf-8")

    CIO_DIR.mkdir(parents=True, exist_ok=True)
    md_path = CIO_DIR / f"{date_str}_Apex_Brain_V4_Profit_Report.md"
    lines = [
        f"# [BRAIN V4.0] BÁO CÁO ĐẦU NÃO ĐỊNH LƯỢNG & TỐI ƯU LỢI NHUẬN ({date_str})",
        f"> **Cập nhật:** `{output['generated_at']}` | **BCTC xác thực:** `{output['bctc_coverage'].get('bctc_verified_count', 0)}/{output['bctc_coverage'].get('requested_vn_tickers', 145)}` mã | **EOD:** `{regime_diag['as_of_date']}`",
        f"> **Tài khoản TCBS `{output['ssot_account']['account_id']}`:** NAV `{nav_vnd:,.0f} ₫` | Tiền mặt `{cash_vnd:,.0f} ₫` (`{output['ssot_account']['cash_pct']}%`)",
        "",
        "## 1. TRẠNG THÁI THỊ TRƯỜNG & LUÂN CHUYỂN NGÀNH",
        f"- **Chế độ hiện tại:** `{cur_reg}` — {regime_diag['verdict_vn']}",
        f"- **VN-Index:** `{regime_diag['vnindex_close']:,.2f}` (`{regime_diag['vnindex_1d_pct']:+.2f}%` | MA20 `{regime_diag['vnindex_ma20']:,.1f}` | MA50 `{regime_diag['vnindex_ma50']:,.1f}` | Br20 `{regime_diag['breadth_above_ma20_pct']}%`)",
        f"- **Kiểm chứng Backtest 145 mã:** V4 **`{output['empirical_backtest_anchor']['v4_return_pct']:+.2f}%`** (MaxDD `{output['empirical_backtest_anchor']['v4_max_dd_pct']}%`, Sharpe `{output['empirical_backtest_anchor']['v4_sharpe_ratio']}`, PF `{output['empirical_backtest_anchor']['v4_profit_factor']}`) vs V3 `{output['empirical_backtest_anchor']['v3_return_pct']:+.2f}%`",
        "",
        "## 2. DANH MỤC ĐANG GIỮ & QUẢN TRỊ LÃI/LỖ (T+2.5 & TRAILING STOP)",
        "| Mã | SL | Giá Vốn | Thị Giá | Lãi/Lỗ Ròng | Ngày T+2 | Stop Hiệu Lực | Hành Động |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ]
    for h in active_holdings_audit:
        lines.append(
            f"| **{h['symbol']}** | `{h['shares']}` | `{h['entry_price']:,.0f}₫` | `{h['current_price']:,.0f}₫` | "
            f"`{h['net_pnl_vnd']:+,.0f}₫ ({h['pnl_pct']:+.2f}%)` | `{h['t_plus_2_settlement_date']}` (`{'Sẵn bán' if h['sellable_now'] else 'Chờ về'}`) | "
            f"`{h['effective_stop_loss']:,.0f}₫` (`{h['stop_mode']}`) | **{h['directive']}** |"
        )
    lines.extend([
        "",
        "## 3. TOP 10 CỔ PHIẾU SẠCH BCTC Q3/2026 & PHÙ HỢP VỐN LÔ 100",
        "| Hạng | Mã | Điểm V4 | F-Score | ROE% | OCF/LNST | Giá | Lô 100 (%NAV) | RS | Trạng Thái |",
        "| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ])
    for idx, x in enumerate(clean_nav_watchlist[:10], 1):
        lines.append(
            f"| {idx} | **{x['symbol']}** | **{x['composite_score']}** | `{x['fundamentals']['piotroski_f_score']}/9` | "
            f"`{x['fundamentals']['roe_ttm_pct']:.1f}%` | `{x['fundamentals']['ocf_to_profit_ratio']}x` | "
            f"`{x['technical']['close']:,.0f}₫` | `{x['sizing_and_ev']['lot100_nav_pct']}%` | `{x['technical']['rs_rating']}` | `{x['action_status']}` |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        f"[BRAIN V4.0] Regime={cur_reg} ({regime_diag['as_of_date']}) | VNI={regime_diag['vnindex_close']:,.2f} Br20={regime_diag['breadth_above_ma20_pct']}% | "
        f"Top5={[(x['symbol'], x['composite_score']) for x in clean_nav_watchlist[:5]]}"
    )
    return output


if __name__ == "__main__":
    run_brain_v4_profit_engine(refresh_quotes=False)
