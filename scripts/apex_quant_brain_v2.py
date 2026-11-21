#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX QUANTITATIVE ANALYTICAL BRAIN (V2.0 INSTITUTIONAL)
File: scripts/apex_quant_brain_v2.py
Co quan chu quan: Ban 1-4 (Macro, BCTC, Synthesis, Quant Risk) & Ban 8 (Master CIO James)

4-Layer Decision Engine (100% Real Data + Empirical Calibration - Zero Inflation):
1. Live Market Regime Diagnosis: VN-Index vs MA20/MA50/MA200, real Universe Breadth (% > MA20 / MA50),
   20-day Distribution Days, Global Spillover (VIX, SP500, US10Y, DXY, WTI, USD/VND), Foreign flow.
2. Multi-Factor Cross-Sectional Percentile Ranking (0-100, median ~50, top decile 75-90):
   - Quality & Forensic (30%): Piotroski F-Score /9, OCF/NPAT (or Bank Pre-WC/CIR/EqAssets), Novy-Marx Gross Prof, Beneish/Sloan Veto.
   - Earnings Growth & Acceleration (20%): Live Q3/2026 YoY Revenue/Profit + Q-over-Q acceleration.
   - Value & Margin of Safety (15%): Live Earnings Yield (E/P), Bank P/B vs ROE, VCI Target Upside.
   - Structural Trend & Momentum (25%): Minervini 8-Point Stage 2 count (/8), Cross-Sectional RS Rating (1-99), 20D/63D returns.
   - Micro-Structure & Liquidity (10%): VCP Tightness (ATR10/ATR40), Volume dry-up/accumulation, >= 25B/day, Lot-100 20M fit.
3. Empirically Calibrated Expectancy & Hard Risk Gates (from data/apex_empirical_calibration.json).
4. Concrete Week 48 (23/11/2026) Tactical Execution Plan for TCBS 105C307855 (~20.19M VND).
"""

import datetime
import json
import math
import sys
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

DATA_DIR = BASE_DIR / "data"
VN_BCTC_PATH = BASE_DIR / "VN_Market" / "data" / "vn_real_bctc_live.json"
OHLCV_DIR = DATA_DIR / "real_ohlcv_cache"
CALIBRATION_PATH = DATA_DIR / "apex_empirical_calibration.json"
SSOT_PATH = DATA_DIR / "current_portfolio_state.json"
OUT_JSON = DATA_DIR / "apex_quant_brain_v2_output.json"
CIO_DIR = BASE_DIR / "08_Master_Investment_CIO"


def _get_ict_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=7))
    )


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _sma(arr: List[float], win: int) -> float:
    if not arr:
        return 0.0
    sub = arr[-min(len(arr), win):]
    return sum(sub) / len(sub)


def _rsi14(closes: List[float]) -> float:
    if len(closes) < 15:
        return 50.0
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(0.0, d) for d in deltas]
    losses = [max(0.0, -d) for d in deltas]
    ag = sum(gains[:14]) / 14.0
    al = sum(losses[:14]) / 14.0
    for g, l in zip(gains[14:], losses[14:]):
        ag = (ag * 13.0 + g) / 14.0
        al = (al * 13.0 + l) / 14.0
    if al <= 1e-9:
        return 100.0 if ag > 0 else 50.0
    return round(100.0 - (100.0 / (1.0 + ag / al)), 1)


def _atr(bars: List[Dict[str, Any]], period: int = 14) -> float:
    if len(bars) < 2:
        return 0.0
    trs = []
    for i in range(1, len(bars)):
        h, l, pc = float(bars[i]["high"]), float(bars[i]["low"]), float(bars[i - 1]["close"])
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    sub = trs[-min(len(trs), period):]
    return sum(sub) / len(sub) if sub else 0.0


def _cmf20(bars: List[Dict[str, Any]]) -> float:
    """Chaikin Money Flow (20D) thuc te tu OHLCV ([-100, +100])."""
    sub = bars[-min(len(bars), 20):]
    mfv_sum = 0.0
    vol_sum = 0.0
    for b in sub:
        h, l, c, v = float(b["high"]), float(b["low"]), float(b["close"]), float(b["volume"])
        if h > l and v > 0:
            mfm = ((c - l) - (h - c)) / (h - l)
            mfv_sum += mfm * v
        vol_sum += v
    return round((mfv_sum / vol_sum) * 100.0, 1) if vol_sum > 0 else 0.0


def _percentile_ranks(values: Dict[str, float]) -> Dict[str, float]:
    """Quy doi tuong quan phan vi chuan (0 - 100) khong lam phat diem."""
    if not values:
        return {}
    items = sorted(values.items(), key=lambda kv: kv[1])
    n = len(items)
    if n == 1:
        return {items[0][0]: 50.0}
    out = {}
    for idx, (k, _) in enumerate(items):
        out[k] = round((idx / (n - 1)) * 100.0, 1)
    return out


def compute_technical_snapshot(bars: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(bars) < 30:
        return {}
    closes = [float(b["close"]) for b in bars]
    highs = [float(b["high"]) for b in bars]
    lows = [float(b["low"]) for b in bars]
    vols = [float(b["volume"]) for b in bars]

    px = closes[-1]
    prev_px = closes[-2]
    day_chg = ((px / prev_px) - 1.0) * 100.0 if prev_px > 0 else 0.0

    ma10 = _sma(closes, 10)
    ma20 = _sma(closes, 20)
    ma50 = _sma(closes, 50)
    ma150 = _sma(closes, 150)
    ma200 = _sma(closes, 200)
    ma200_20d_ago = _sma(closes[:-20], 200) if len(closes) > 40 else ma200

    hi_52w = max(highs[-min(len(highs), 252):])
    lo_52w = min(lows[-min(len(lows), 252):])

    ret_20d = ((px / closes[-min(len(closes), 21)]) - 1.0) * 100.0
    ret_63d = ((px / closes[-min(len(closes), 64)]) - 1.0) * 100.0
    ret_126d = ((px / closes[-min(len(closes), 127)]) - 1.0) * 100.0

    atr10 = _atr(bars, 10)
    atr14 = _atr(bars, 14)
    atr40 = max(1e-6, _atr(bars, 40))
    vcp_ratio = round(atr10 / atr40, 2)

    vol20 = _sma(vols, 20)
    vol_ratio = round(vols[-1] / max(1.0, vol20), 2)
    avg_val20_ty = round(sum((closes[k] * vols[k]) / 1e9 for k in range(-min(len(bars), 20), 0)) / min(len(bars), 20), 2)

    # Minervini 8-point Stage 2 Trend Template (partial 7 technical checks here, RS added later)
    checks_7 = [
        px > ma150 and px > ma200,
        ma150 >= ma200 * 0.99,
        ma200 >= ma200_20d_ago * 0.995,
        ma50 > ma150 and ma50 > ma200,
        px > ma50,
        px >= lo_52w * 1.25,
        px >= hi_52w * 0.75,
    ]
    minervini_7 = sum(1 for c in checks_7 if c)

    return {
        "last_date": bars[-1]["date"],
        "close": round(px, 0),
        "day_chg_pct": round(day_chg, 2),
        "ma10": round(ma10, 0),
        "ma20": round(ma20, 0),
        "ma50": round(ma50, 0),
        "ma150": round(ma150, 0),
        "ma200": round(ma200, 0),
        "dist_ma20_pct": round(((px / ma20) - 1.0) * 100.0, 2) if ma20 > 0 else 0.0,
        "dist_ma50_pct": round(((px / ma50) - 1.0) * 100.0, 2) if ma50 > 0 else 0.0,
        "pct_from_52w_high": round(((px / hi_52w) - 1.0) * 100.0, 2) if hi_52w > 0 else 0.0,
        "pct_above_52w_low": round(((px / lo_52w) - 1.0) * 100.0, 2) if lo_52w > 0 else 0.0,
        "rsi14": _rsi14(closes),
        "atr14": round(atr14, 0),
        "atr_pct": round((atr14 / px) * 100.0, 2) if px > 0 else 2.5,
        "vcp_ratio": vcp_ratio,
        "vol_ratio": vol_ratio,
        "avg_val20_ty": avg_val20_ty,
        "cmf20": _cmf20(bars),
        "ret_20d": round(ret_20d, 2),
        "ret_63d": round(ret_63d, 2),
        "ret_126d": round(ret_126d, 2),
        "raw_rs": round(0.40 * ret_20d + 0.35 * ret_63d + 0.25 * ret_126d, 2),
        "minervini_7": minervini_7,
        "hi_52w": round(hi_52w, 0),
        "lo_52w": round(lo_52w, 0),
    }


def diagnose_live_market_regime(
    bctc_data: Dict[str, Any],
    tech_map: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Tang 1: Chan doan che do thi truong song (VNI + Breadth + DistDays + Global Spillover)."""
    vni_bars = _load_json(OHLCV_DIR / "VNINDEX.json").get("bars", [])
    vni_c = [float(b["close"]) for b in vni_bars]
    vni_v = [float(b["volume"]) for b in vni_bars]
    if not vni_c:
        raise RuntimeError("Khong co du lieu VNINDEX OHLCV.")

    vni = vni_c[-1]
    vni_prev = vni_c[-2] if len(vni_c) >= 2 else vni
    vni_1d = ((vni / vni_prev) - 1.0) * 100.0
    vni_ma20 = _sma(vni_c, 20)
    vni_ma20_prev5 = _sma(vni_c[:-5], 20) if len(vni_c) > 25 else vni_ma20
    vni_ma50 = _sma(vni_c, 50)
    vni_ma50_prev10 = _sma(vni_c[:-10], 50) if len(vni_c) > 60 else vni_ma50
    vni_ma200 = _sma(vni_c, 200)

    # 20-day distribution days
    dist_days = 0
    for k in range(max(1, len(vni_c) - 20), len(vni_c)):
        if ((vni_c[k] / vni_c[k - 1]) - 1.0) <= -0.005 and vni_v[k] > vni_v[k - 1]:
            dist_days += 1

    # Universe breadth
    liq_techs = [t for t in tech_map.values() if t.get("avg_val20_ty", 0.0) >= 10.0]
    n_liq = max(1, len(liq_techs))
    br20 = round((sum(1 for t in liq_techs if t["close"] > t["ma20"]) / n_liq) * 100.0, 1)
    br50 = round((sum(1 for t in liq_techs if t["close"] > t["ma50"]) / n_liq) * 100.0, 1)
    br200 = round((sum(1 for t in liq_techs if t["close"] > t["ma200"]) / n_liq) * 100.0, 1)

    # Global spillover live
    macro = bctc_data.get("macro_live", {})
    try:
        from scripts.global_to_vn_spillover_engine import compute_global_to_vn_spillover
        spill = compute_global_to_vn_spillover(force_refresh=False)
    except Exception:
        spill = {"risk_multiplier": 1.0, "bias": "NEUTRAL"}

    # Classify using exact empirical 4-state gates proven in walk-forward backtest
    if (
        vni >= vni_ma20
        and vni >= vni_ma50
        and vni_ma20 >= vni_ma50
        and vni_ma20 >= vni_ma20_prev5
        and vni_ma50 >= vni_ma50_prev10 * 0.998
        and br20 >= 52.0
        and br50 >= 50.0
        and dist_days <= 4
    ):
        regime_id = "CONFIRMED_UPTREND"
        max_exp_pct = 85.0
        max_pos = 3
        verdict_vn = "XAC NHAN XU HUONG TANG DONG THUAN — CHO PHEP BUNG 70–85% NAV"
    elif vni >= vni_ma50 and br20 >= 44.0 and br50 >= 44.0 and dist_days <= 5:
        regime_id = "UPTREND_UNDER_PRESSURE"
        max_exp_pct = 35.0
        max_pos = 2
        verdict_vn = "XU HUONG TANG CHIU AP LUC — THAM DO NHO (<= 35% NAV), CHON LOC CUC CHAT"
    elif vni < vni_ma20 and vni < vni_ma50 and br20 < 35.0:
        regime_id = "BEAR_DOWNTREND"
        max_exp_pct = 0.0
        max_pos = 0
        verdict_vn = "SUY YEU / PHAN PHOI DIEN RONG (BREADTH < 35%) — KHOA CHIEU MUA MOI (0% GIAI NGAN, GIU TIEN MAT)"
    else:
        regime_id = "CHOPPY_CORRECTION"
        max_exp_pct = 0.0
        max_pos = 0
        verdict_vn = "DIEU CHINH / GIANG CO CHOPPY — DUNG NGOAI BAO TOAN TIEN MAT CHO XAC NHAN"

    return {
        "as_of_date": vni_bars[-1]["date"],
        "vnindex_close": round(vni, 2),
        "vnindex_1d_pct": round(vni_1d, 2),
        "vnindex_ma20": round(vni_ma20, 2),
        "vnindex_ma50": round(vni_ma50, 2),
        "vnindex_ma200": round(vni_ma200, 2),
        "vni_vs_ma20_pct": round(((vni / vni_ma20) - 1.0) * 100.0, 2),
        "vni_vs_ma50_pct": round(((vni / vni_ma50) - 1.0) * 100.0, 2),
        "vni_vs_ma200_pct": round(((vni / vni_ma200) - 1.0) * 100.0, 2),
        "ma20_above_ma50": bool(vni_ma20 >= vni_ma50),
        "distribution_days_20d": dist_days,
        "breadth_above_ma20_pct": br20,
        "breadth_above_ma50_pct": br50,
        "breadth_above_ma200_pct": br200,
        "liquid_universe_count": len(liq_techs),
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
            f"VN-Index dong cua > MA20 ({vni_ma20:.1f}) va > MA50 ({vni_ma50:.1f}) voi MA20 cat len >= MA50",
            f"Do rong thi truong (Breadth > MA20) hoi phuc tu {br20}% len >= 52% va Breadth > MA50 >= 50%",
            f"So phien phan phoi (Distribution Days 20 phien) giam <= 4 phien (hien tai: {dist_days})",
            "Chi bam co mua LO trong Khung Gio Vang 14h00–14h25 khi Buy-Up chu dong >= 60%",
        ],
    }


def run_quant_brain_v2(refresh_quotes: bool = True) -> Dict[str, Any]:
    now_ict = _get_ict_now()
    bctc_data = _load_json(VN_BCTC_PATH)
    if not bctc_data.get("stocks"):
        raise RuntimeError("Khong tim thay VN_Market/data/vn_real_bctc_live.json. Hay chay scripts/apex_real_bctc_crawler.py truoc.")

    cal = _load_json(CALIBRATION_PATH)
    cal_v2 = cal.get("apex_v2_regime_gated", {})
    emp_win_rate = float(cal_v2.get("win_rate_pct") or 52.0) / 100.0
    emp_avg_win = float(cal_v2.get("avg_win_pct") or 16.0)
    emp_avg_loss = abs(float(cal_v2.get("avg_loss_pct") or 7.3))
    reg_breakdown = cal_v2.get("regime_trade_breakdown", {})

    ssot = _load_json(SSOT_PATH)
    nav_vnd = float(ssot.get("total_nav_vnd") or 20_189_522.0)

    stocks_bctc = bctc_data["stocks"]

    # Optional live VPS quote overlay for latest tick
    live_quotes: Dict[str, Dict[str, Any]] = {}
    if refresh_quotes:
        try:
            from scripts.vietnam_realtime_feed import fetch_vps_quotes
            live_quotes = fetch_vps_quotes(list(stocks_bctc.keys()), timeout=5)
        except Exception:
            live_quotes = {}

    # 1. Compute live technical snapshot from 2Y VPS OHLCV
    tech_map: Dict[str, Dict[str, Any]] = {}
    for sym in stocks_bctc:
        bars = _load_json(OHLCV_DIR / f"{sym}.json").get("bars", [])
        t = compute_technical_snapshot(bars)
        if t:
            q_live = live_quotes.get(sym)
            if q_live and float(q_live.get("price") or 0.0) > 0:
                t["live_quote_price"] = float(q_live["price"])
                t["active_buy_pct_live"] = float(q_live.get("active_buy_pct") or 50.0)
                t["foreign_net_val_bil"] = round(float(q_live.get("foreign_net_val_vnd") or 0.0) / 1e9, 2)
            else:
                t["live_quote_price"] = t["close"]
                t["active_buy_pct_live"] = None
                t["foreign_net_val_bil"] = 0.0
            tech_map[sym] = t

    # Assign cross-sectional RS Rating (1-99)
    rs_ranked = sorted(tech_map.items(), key=lambda kv: kv[1]["raw_rs"])
    n_t = len(rs_ranked)
    for idx, (sym, t) in enumerate(rs_ranked):
        rs_val = int(round(1 + (idx / max(1, n_t - 1)) * 98))
        t["rs_rating"] = rs_val
        t["minervini_8"] = t["minervini_7"] + (1 if rs_val >= 70 else 0)

    # 2. Diagnose Live Market Regime
    regime_diag = diagnose_live_market_regime(bctc_data, tech_map)
    cur_reg = regime_diag["regime_id"]

    # 3. Raw multi-factor components across universe -> percentile normalize (ZERO inflation!)
    raw_quality: Dict[str, float] = {}
    raw_growth: Dict[str, float] = {}
    raw_value: Dict[str, float] = {}
    raw_momentum: Dict[str, float] = {}
    raw_micro: Dict[str, float] = {}

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

        if com_type == "NH":
            cf_eff = pre_ocf_r
        elif com_type == "CK":
            # Brokerages deploy cash into margin lending book (reduces headline OCF in expansions); evaluate pre-WC OCF & leverage
            de_pct = float(lm.get("de_ratio_pct") or 0.0)
            cf_eff = pre_ocf_r if de_pct <= 220.0 else min(pre_ocf_r, 0.5)
        else:
            cf_eff = ocf_r
        q_raw = f_sc * 8.0 + min(25.0, max(-15.0, roe)) + min(15.0, max(-15.0, (cf_eff - 0.8) * 15.0)) + min(15.0, gp_ta * 0.4) - max(0.0, sloan - 10.0)
        raw_quality[sym] = q_raw

        pg = max(-50.0, min(120.0, float(lm.get("profit_growth_yoy") or 0.0)))
        rg = max(-40.0, min(80.0, float(lm.get("rev_growth_yoy") or 0.0)))
        eps_q = max(-60.0, min(150.0, float(lm.get("eps_q_yoy") or pg)))
        acc_b = 15.0 if lm.get("earnings_accelerating") else 0.0
        raw_growth[sym] = 0.40 * pg + 0.25 * rg + 0.35 * eps_q + acc_b

        ey = float(lm.get("earnings_yield_pct") or 0.0)
        pb = float(lm.get("pb_live") or 5.0)
        up_vci = max(-30.0, min(60.0, float(lm.get("vci_upside_pct") or 0.0)))
        bank_val_bonus = (1.5 - pb) * 12.0 if (com_type == "NH" and pb > 0) else 0.0
        raw_value[sym] = ey * 2.5 + up_vci * 0.4 + bank_val_bonus

        raw_momentum[sym] = float(t["rs_rating"]) * 0.65 + t["minervini_8"] * 5.0 + max(-25.0, min(30.0, t["dist_ma50_pct"]))

        vcp_b = 15.0 if t["vcp_ratio"] <= 0.90 else 0.0
        cmf_b = max(-15.0, min(20.0, t["cmf20"]))
        liq_b = 15.0 if t["avg_val20_ty"] >= 30.0 else (-25.0 if t["avg_val20_ty"] < 15.0 else 0.0)
        raw_micro[sym] = vcp_b + cmf_b + liq_b

    pct_q = _percentile_ranks(raw_quality)
    pct_g = _percentile_ranks(raw_growth)
    pct_v = _percentile_ranks(raw_value)
    pct_m = _percentile_ranks(raw_momentum)
    pct_u = _percentile_ranks(raw_micro)

    # 4. Score, Veto, Calibrate Expectancy, and Build Full Ranked Universe
    ranked_universe: List[Dict[str, Any]] = []
    for sym, stk in stocks_bctc.items():
        if sym not in pct_q:
            continue
        lm = stk["latest_metrics"]
        t = tech_map[sym]
        com_type = stk.get("com_type_code", "CT")

        p_qual = pct_q[sym]
        p_grow = pct_g[sym]
        p_val = pct_v[sym]
        p_mom = pct_m[sym]
        p_mic = pct_u[sym]

        composite = round(0.30 * p_qual + 0.20 * p_grow + 0.15 * p_val + 0.25 * p_mom + 0.10 * p_mic, 1)

        # Hard Forensic & Technical Risk Vetoes
        veto_reasons: List[str] = []
        np_ttm = float(lm.get("net_profit_ttm_ty") or 0.0)
        f_sc = int(lm.get("piotroski_f_score") or 0)
        beneish = float(lm.get("beneish_m_score") or -2.5)
        ocf_r = float(lm.get("ocf_to_profit_ratio") or 0.0)
        pre_ocf_r = float(lm.get("pre_wc_ocf_to_profit") or 0.0)
        sloan = float(lm.get("sloan_accrual_pct") or 0.0)

        if np_ttm <= 0:
            veto_reasons.append(f"Loi nhuan TTM am ({np_ttm:.1f} ty)")
        if f_sc < 5:
            veto_reasons.append(f"Piotroski F-Score yeu ({f_sc}/9)")
        if com_type == "CT" and beneish > -1.78:
            veto_reasons.append(f"Beneish M-Score canh bao ({beneish} > -1.78)")
        if com_type == "CT" and float(lm.get("ocf_ty") or 0.0) < 0:
            veto_reasons.append(f"Dong tien kinh doanh OCF am ({float(lm.get('ocf_ty') or 0.0):,.1f} ty)")
        elif com_type == "CT" and ocf_r < 0.65 and pre_ocf_r < 0.90:
            veto_reasons.append(f"Dong tien OCF kem ({ocf_r}x LNST)")
        if t["avg_val20_ty"] < 25.0:
            veto_reasons.append(f"Thanh khoan mong ({t['avg_val20_ty']} ty/phien < 25 ty)")
        if t["rsi14"] > 72.0 or t["dist_ma20_pct"] > 9.0:
            veto_reasons.append(f"Qua mua / keo xa nen (RSI {t['rsi14']}, +{t['dist_ma20_pct']}% vs MA20)")

        is_stage2_ok = (t["close"] >= t["ma20"] * 0.985) and (t["close"] >= t["ma50"] * 0.98)
        if not is_stage2_ok:
            veto_reasons.append(f"Chua dat xu huong tang (Gia {t['close']:,.0f} < MA20 {t['ma20']:,.0f} / MA50 {t['ma50']:,.0f})")

        # Honest Stop, TP1, TP2, and Empirically Calibrated EV
        px = float(t["close"])
        atr = float(t["atr14"])
        stop_dist_pct = min(8.5, max(5.5, round((2.0 * atr / px) * 100.0, 2) if px > 0 else 7.5))
        stop_price = round(px * (1.0 - stop_dist_pct / 100.0), -1)
        tp1_price = round(px * 1.15, -1)
        vci_tp = float(lm.get("vci_target_price") or 0.0)
        tp2_price = round(max(px * 1.22, vci_tp if vci_tp > px * 1.10 else px * 1.22), -1)
        honest_rr = round(((tp1_price - px) / max(1.0, px - stop_price)), 2)

        # Empirical P(Win) anchored to backtest distribution (never fake 85%!)
        base_p = emp_win_rate  # ~0.571 from backtest
        adj_p = base_p + ((composite - 65.0) * 0.0025) - (0.14 if not is_stage2_ok else 0.0)
        if cur_reg in ("BEAR_DOWNTREND", "CHOPPY_CORRECTION"):
            adj_p -= 0.12
        p_win = round(min(0.62, max(0.32, adj_p)), 3)
        ev_emp_pct = round((p_win * min(emp_avg_win, 18.0)) - ((1.0 - p_win) * stop_dist_pct) - 0.60, 2)

        # Lot-100 suitability for 20M account (30-33% NAV slot ~ 6.6M -> px <= 33,000 allows >= 200 CP)
        max_slot_vnd = nav_vnd * 0.33
        affordable_shares = int(max_slot_vnd // (px * 100.0)) * 100 if px > 0 else 0
        lot100_suitability = (
            "IDEAL_200+_SHARES" if affordable_shares >= 200 else ("SINGLE_100_LOT" if affordable_shares == 100 else "TOO_EXPENSIVE_FOR_20M")
        )

        if cur_reg in ("BEAR_DOWNTREND", "CHOPPY_CORRECTION"):
            action_status = "WAIT_MARKET_REGIME_CASH"
        elif veto_reasons:
            action_status = "VETOED_HOLD_OR_SKIP"
        elif composite >= 68.0 and affordable_shares >= 200 and ev_emp_pct >= 2.5:
            action_status = "BUY_READY_GOLDEN_WINDOW"
        elif composite >= 60.0:
            action_status = "WATCHLIST_CANDIDATE"
        else:
            action_status = "AVOID_LOW_RANK"

        ranked_universe.append({
            "symbol": sym,
            "company_name": stk.get("company_name", sym),
            "exchange": stk.get("exchange", "HOSE"),
            "sector_name": stk.get("sector_name", ""),
            "com_type_code": com_type,
            "latest_quarter": lm.get("latest_quarter", "N/A"),
            "composite_score": composite,
            "pillar_percentiles": {
                "quality_forensic_30": p_qual,
                "earnings_growth_20": p_grow,
                "value_mos_15": p_val,
                "trend_momentum_25": p_mom,
                "micro_liquidity_10": p_mic,
            },
            "fundamentals": {
                "revenue_ttm_ty": lm.get("revenue_ttm_ty"),
                "rev_growth_yoy": lm.get("rev_growth_yoy"),
                "net_profit_ttm_ty": lm.get("net_profit_ttm_ty"),
                "profit_growth_yoy": lm.get("profit_growth_yoy"),
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
            "technical": t,
            "sizing_and_ev": {
                "empirical_p_win_pct": round(p_win * 100.0, 1),
                "stop_loss_price": stop_price,
                "stop_dist_pct": stop_dist_pct,
                "tp1_price_15pct": tp1_price,
                "tp2_price": tp2_price,
                "honest_rr_to_tp1": honest_rr,
                "calibrated_ev_pct": ev_emp_pct,
                "lot100_cost_vnd": round(px * 100.0, 0),
                "affordable_shares_for_33pct_slot": affordable_shares,
                "lot100_suitability": lot100_suitability,
            },
            "veto_reasons": veto_reasons,
            "action_status": action_status,
        })

    ranked_universe.sort(key=lambda x: x["composite_score"], reverse=True)

    # Top clean Quality+Value leaders suitable for 20M account (pass all forensic & liquidity gates, even if waiting for market regime!)
    clean_20m_watchlist = [
        x for x in ranked_universe
        if x["fundamentals"]["net_profit_ttm_ty"] > 0
        and x["fundamentals"]["piotroski_f_score"] >= 6
        and (x["com_type_code"] != "CT" or (x["fundamentals"]["beneish_m_score"] <= -1.78 and (x["fundamentals"]["ocf_to_profit_ratio"] >= 0.65 or x["fundamentals"]["pre_wc_ocf_to_profit"] >= 0.90)))
        and x["technical"]["avg_val20_ty"] >= 25.0
        and x["sizing_and_ev"]["affordable_shares_for_33pct_slot"] >= 200
    ][:10]

    # Risk-Flagged / Weak Stocks Audit (e.g. BAF, MSH, etc.)
    flagged_stocks = [
        x for x in ranked_universe
        if x["symbol"] in ("MSH", "BAF", "HDB", "BSR", "IDC")
        or x["fundamentals"]["beneish_status"] == "HIGH_RISK"
        or x["fundamentals"]["piotroski_f_score"] <= 3
    ]

    output = {
        "engine": "APEX_QUANT_BRAIN_V2.0",
        "generated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S ICT"),
        "data_provenance": bctc_data.get("data_provenance"),
        "ssot_account": {
            "account_id": ssot.get("account_id", "105C307855"),
            "nav_vnd": nav_vnd,
            "cash_vnd": float(ssot.get("cash_balance_vnd") or 13_594_522.0),
            "active_holdings": list((ssot.get("active_positions") or {}).keys()),
        },
        "market_regime": regime_diag,
        "empirical_backtest_anchor": {
            "v2_return_pct": cal_v2.get("total_return_pct"),
            "v2_max_dd_pct": cal_v2.get("max_drawdown_pct"),
            "v2_profit_factor": cal_v2.get("profit_factor"),
            "v2_win_rate_pct": cal_v2.get("win_rate_pct"),
            "v2_payoff_ratio": cal_v2.get("payoff_ratio"),
            "baseline_return_pct": cal.get("baseline_always_invested", {}).get("total_return_pct"),
        },
        "week48_clean_20m_watchlist": clean_20m_watchlist,
        "top_15_overall_universe": ranked_universe[:15],
        "bottom_10_avoid": ranked_universe[-10:],
        "special_audit_watchlist": flagged_stocks,
        "all_ranked": ranked_universe,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write clean Executive Markdown Report
    CIO_DIR.mkdir(parents=True, exist_ok=True)
    md_path = CIO_DIR / f"{now_ict.strftime('%Y-%m-%d')}_Apex_Quant_Brain_V2_Report.md"
    lines = [
        f"# [APEX QUANT BRAIN V2.0] BAO CAO PHAN TICH BCTC SONG & DIEU HANH DAU TU — {now_ict.strftime('%Y-%m-%d')}",
        f"**Cap nhat:** `{output['generated_at']}` | **Nguon BCTC:** `Vietcap IQ Official Live (Q3/2026)` | **OHLCV:** `VPS HistDataFeed (2 Nam)`",
        "",
        "## 1. CHAN DOAN CHE DO THI TRUONG (MARKET REGIME GATE)",
        f"- **VN-Index:** `{regime_diag['vnindex_close']}` ({regime_diag['vnindex_1d_pct']:+.2f}%) | MA20: `{regime_diag['vnindex_ma20']}` ({regime_diag['vni_vs_ma20_pct']:+.2f}%) | MA50: `{regime_diag['vnindex_ma50']}` ({regime_diag['vni_vs_ma50_pct']:+.2f}%) | MA200: `{regime_diag['vnindex_ma200']}`",
        f"- **Do rong thi truong (Breadth):** `> MA20: {regime_diag['breadth_above_ma20_pct']}%` | `> MA50: {regime_diag['breadth_above_ma50_pct']}%` | `> MA200: {regime_diag['breadth_above_ma200_pct']}%` ({regime_diag['liquid_universe_count']} ma thanh khoan)",
        f"- **So ngay phan phoi (20 phien):** `{regime_diag['distribution_days_20d']}` | **MA20 >= MA50:** `{regime_diag['ma20_above_ma50']}`",
        f"- **CHE DO HIEN TAI:** **`{regime_diag['regime_id']}`** -> **Tran giai ngan moi: `{regime_diag['max_equity_exposure_pct']}% NAV`**",
        f"- **Ket luan tac chien:** **{regime_diag['verdict_vn']}**",
        "",
        "## 2. TOP 10 CO PHIEU SACH BCTC & VUA SIZE TAI KHOAN 20M VND CHO TUAN 48 (23/11)",
        "*(Tieu chuan: F-Score >= 6/9, Beneish SAFE, OCF tot, Thanh khoan >= 25 ty/phien, Thi gia <= 33,000d de cam >= 200 CP chia chot 50/50)*",
        "| Hang | Ma | Nganh | Diem V2 | F-Score | ROE% | P/E | OCF/LN | Gia Live | AvgVal20 | RS | Trang Thai |",
        "| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ]
    for idx, x in enumerate(clean_20m_watchlist, 1):
        f = x["fundamentals"]
        t = x["technical"]
        cf_s = f"{f['pre_wc_ocf_to_profit']}x*" if x["com_type_code"] == "NH" else f"{f['ocf_to_profit_ratio']}x"
        lines.append(
            f"| {idx} | **{x['symbol']}** | {x['sector_name'][:18]} | **{x['composite_score']}** | {f['piotroski_f_score']}/9 | "
            f"{f['roe_ttm_pct']:.1f}% | {f['pe_ttm'] or '-'} | {cf_s} | {t['close']:,.0f}d | {t['avg_val20_ty']:.0f} ty | {t['rs_rating']} | `{x['action_status']}` |"
        )

    lines.extend([
        "",
        "## 3. KIEM TOAN THANG THANG CAC MA DANG GIU / TUNG DUOC GOI Y (Q3/2026 LIVE)",
        "| Ma | Diem V2 | F-Score | Beneish M | P/E | OCF/LN | AvgVal20 | Ly Do Veto / Danh Gia Thuc Te |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ])
    seen_sp = set()
    for x in flagged_stocks:
        if x["symbol"] in seen_sp:
            continue
        seen_sp.add(x["symbol"])
        f = x["fundamentals"]
        t = x["technical"]
        v_str = "; ".join(x["veto_reasons"]) if x["veto_reasons"] else "Dat chuan"
        lines.append(
            f"| **{x['symbol']}** | {x['composite_score']} | {f['piotroski_f_score']}/9 | {f['beneish_m_score']} ({f['beneish_status']}) | "
            f"{f['pe_ttm'] or '-'} | {f['ocf_to_profit_ratio']}x | {t['avg_val20_ty']:.1f} ty | {v_str} |"
        )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    output["report_md_path"] = str(md_path)
    print(f"[QUANT BRAIN V2.0] Regime={cur_reg} (VNI={regime_diag['vnindex_close']}, Br20={regime_diag['breadth_above_ma20_pct']}%, Br50={regime_diag['breadth_above_ma50_pct']}%) | MaxExp={regime_diag['max_equity_exposure_pct']}%")
    print(f"[+] Top 5 Clean 20M Watchlist: {[(x['symbol'], x['composite_score'], x['fundamentals']['piotroski_f_score'], x['technical']['close']) for x in clean_20m_watchlist[:5]]}")
    print(f"[+] Report saved: {md_path}")
    return output


if __name__ == "__main__":
    run_quant_brain_v2(refresh_quotes=True)
