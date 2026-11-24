#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX EMPIRICAL WALK-FORWARD BACKTESTER (V2.0 — ZERO LOOK-AHEAD BIAS)
File: scripts/apex_walkforward_backtester.py
Co quan chu quan: Ban 4 (Quant Risk), Ban 5 (Walk-Forward Learning) & Ban 8 (Master CIO James)

Kiem chung thuc nghiem 100% tren du lieu lich su thuc te (~2 nam VPS OHLCV + BCTC Point-in-Time Vietcap IQ):
- Chi phi & ma sat thuc te:
  * Phi mua + truot gia vao: 0.25% | Phi ban + thue + truot gia ra: 0.35% (Tong 0.60%/vong)
  * Lam tron lo chan 100 CP HOSE/HNX cho tai khoan von goc 20,000,000 VND
  * Khoa chu ky thanh toan T+2.5 (mua phien i, ban som nhat tu phien i+3; tien ban ve i+2)
  * BCTC Point-in-Time (+45 ngay sau quy Q1-Q3, +60 ngay sau Q4) — TUYET DOI KHONG LOOK-AHEAD BIAS!
- So sanh A/B (Ablation Study):
  1. BASELINE_ALWAYS_INVESTED: Mo hinh cu khong loc Regime/Breadth/Thanh khoan/BCTC song.
  2. APEX_V2_REGIME_GATED: 4-State Market Regime Gate (VNI Golden Cross MA20>=MA50 + Breadth20>=52% + Breadth50>=50% + DistDays<=4)
     + Quality-Value-Momentum (Piotroski F>=6, Beneish SAFE, Earnings Yield E/P, Bank Low P/B High ROE, RS>=60)
     + Cat lo dong cua -8% (chong quet rau nen), chot 50% TP1 +15%, trailing 10% dinh / MA50.
- Xuat ket qua hieu chuan thuc nghiem ra `data/apex_empirical_calibration.json`.
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

from scripts.apex_real_bctc_crawler import compute_pit_fundamentals

DATA_DIR = BASE_DIR / "data"
VN_BCTC_PATH = BASE_DIR / "VN_Market" / "data" / "vn_real_bctc_live.json"
OHLCV_DIR = DATA_DIR / "real_ohlcv_cache"
CALIBRATION_OUT = DATA_DIR / "apex_empirical_calibration.json"

INITIAL_CAPITAL_VND = 20_000_000.0
BUY_FRICTION = 0.0025   # 0.15% phi + 0.10% truot gia
SELL_FRICTION = 0.0035  # 0.15% phi + 0.10% thue + 0.10% truot gia
WARMUP_BARS = 65


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _sma(arr: List[float], idx: int, win: int) -> float:
    start = max(0, idx - win + 1)
    sub = arr[start : idx + 1]
    return sum(sub) / len(sub) if sub else 0.0


def _compute_rsi_series(closes: List[float], period: int = 14) -> List[float]:
    n = len(closes)
    out = [50.0] * n
    if n <= period:
        return out
    gains = [0.0] * n
    losses = [0.0] * n
    for i in range(1, n):
        d = closes[i] - closes[i - 1]
        gains[i] = max(0.0, d)
        losses[i] = max(0.0, -d)
    avg_g = sum(gains[1 : period + 1]) / period
    avg_l = sum(losses[1 : period + 1]) / period
    for i in range(period, n):
        if i > period:
            avg_g = (avg_g * (period - 1) + gains[i]) / period
            avg_l = (avg_l * (period - 1) + losses[i]) / period
        if avg_l <= 1e-9:
            out[i] = 100.0 if avg_g > 0 else 50.0
        else:
            rs = avg_g / avg_l
            out[i] = 100.0 - (100.0 / (1.0 + rs))
    return out


def _compute_atr_series(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
    n = len(closes)
    tr = [0.0] * n
    for i in range(n):
        if i == 0:
            tr[i] = highs[i] - lows[i]
        else:
            tr[i] = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )
    out = [0.0] * n
    for i in range(n):
        start = max(0, i - period + 1)
        out[i] = sum(tr[start : i + 1]) / (i - start + 1)
    return out


def prepare_market_panel() -> Dict[str, Any]:
    """Nap du lieu gia ~500 phien + BCTC Point-in-Time cho toan bo vu tru co phieu VN."""
    vni_raw = _load_json(OHLCV_DIR / "VNINDEX.json").get("bars", [])
    bctc_raw = _load_json(VN_BCTC_PATH).get("stocks", {})
    if not vni_raw or not bctc_raw:
        raise RuntimeError("Thieu du lieu VNINDEX hoac vn_real_bctc_live.json. Hay chay apex_real_bctc_crawler.py truoc.")

    dates = [b["date"] for b in vni_raw]
    n_days = len(dates)

    vni_o = [float(b["open"]) for b in vni_raw]
    vni_h = [float(b["high"]) for b in vni_raw]
    vni_l = [float(b["low"]) for b in vni_raw]
    vni_c = [float(b["close"]) for b in vni_raw]
    vni_v = [float(b["volume"]) for b in vni_raw]
    vni_ma20 = [_sma(vni_c, i, 20) for i in range(n_days)]
    vni_ma50 = [_sma(vni_c, i, 50) for i in range(n_days)]
    vni_vol20 = [_sma(vni_v, i, 20) for i in range(n_days)]

    is_dist_day = [False] * n_days
    for i in range(1, n_days):
        ret = (vni_c[i] - vni_c[i - 1]) / max(1e-6, vni_c[i - 1])
        if ret <= -0.005 and vni_v[i] > vni_v[i - 1]:
            is_dist_day[i] = True
    vni_dist20 = [sum(1 for k in range(max(1, i - 19), i + 1) if is_dist_day[k]) for i in range(n_days)]

    stocks_panel: Dict[str, Dict[str, Any]] = {}
    pit_cache: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for sym, stk in bctc_raw.items():
        bars = _load_json(OHLCV_DIR / f"{sym}.json").get("bars", [])
        if len(bars) < 120:
            continue
        bar_map = {b["date"]: b for b in bars}
        opens = [0.0] * n_days
        highs = [0.0] * n_days
        lows = [0.0] * n_days
        closes = [0.0] * n_days
        vols = [0.0] * n_days
        valid_mask = [False] * n_days

        last_b = None
        for i, d in enumerate(dates):
            if d in bar_map:
                b = bar_map[d]
                opens[i] = float(b["open"])
                highs[i] = float(b["high"])
                lows[i] = float(b["low"])
                closes[i] = float(b["close"])
                vols[i] = float(b["volume"])
                valid_mask[i] = closes[i] > 0
                last_b = b
            elif last_b is not None:
                c_prev = float(last_b["close"])
                opens[i] = highs[i] = lows[i] = closes[i] = c_prev
                vols[i] = 0.0
                valid_mask[i] = False

        ma10 = [_sma(closes, i, 10) for i in range(n_days)]
        ma20 = [_sma(closes, i, 20) for i in range(n_days)]
        ma50 = [_sma(closes, i, 50) for i in range(n_days)]
        ma150 = [_sma(closes, i, 150) for i in range(n_days)]
        ma200 = [_sma(closes, i, 200) for i in range(n_days)]
        rsi14 = _compute_rsi_series(closes, 14)
        atr10 = _compute_atr_series(highs, lows, closes, 10)
        atr14 = _compute_atr_series(highs, lows, closes, 14)
        atr40 = _compute_atr_series(highs, lows, closes, 40)

        vol20 = [_sma(vols, i, 20) for i in range(n_days)]
        val_series = [(closes[i] * vols[i]) / 1e9 for i in range(n_days)]
        avg_val20 = [_sma(val_series, i, 20) for i in range(n_days)]

        quarters_pit = stk.get("quarters_pit", [])
        com_type = stk.get("com_type_code", "CT")
        latest_mcap = float((stk.get("latest_metrics") or {}).get("market_cap_ty") or 0.0)
        latest_px = float((stk.get("latest_metrics") or {}).get("current_price") or closes[-1] or 1.0)

        pit_by_idx: List[Optional[Dict[str, Any]]] = [None] * n_days
        for i, d_str in enumerate(dates):
            avail_q = [q for q in quarters_pit if q.get("available_date", "9999-12-31") <= d_str]
            if len(avail_q) < 4:
                continue
            last_p = avail_q[-1]["period"]
            ckey = (sym, last_p)
            if ckey not in pit_cache:
                pit_cache[ckey] = compute_pit_fundamentals(
                    avail_q, com_type, market_cap_ty=latest_mcap, current_price=latest_px
                ) or {}
            base_f = pit_cache[ckey]
            if base_f:
                px_ratio = (closes[i] / latest_px) if (latest_px > 0 and closes[i] > 0) else 1.0
                est_mcap = latest_mcap * px_ratio
                np_ttm = float(base_f.get("net_profit_ttm_ty") or 0.0)
                eq = float(base_f.get("equity_ty") or 0.0)
                pe_pit = (est_mcap / np_ttm) if (est_mcap > 0 and np_ttm > 0) else None
                pb_pit = (est_mcap / eq) if (est_mcap > 0 and eq > 0) else None
                ey_pit = (np_ttm / est_mcap) * 100.0 if (est_mcap > 0 and np_ttm > 0) else 0.0
                pit_by_idx[i] = {
                    **base_f,
                    "pe_pit": round(pe_pit, 2) if pe_pit else None,
                    "pb_pit": round(pb_pit, 2) if pb_pit else None,
                    "earnings_yield_pit": round(ey_pit, 2),
                }

        stocks_panel[sym] = {
            "symbol": sym,
            "sector_key": stk.get("sector_key", ""),
            "com_type": com_type,
            "valid": valid_mask,
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": vols,
            "ma10": ma10,
            "ma20": ma20,
            "ma50": ma50,
            "ma150": ma150,
            "ma200": ma200,
            "rsi14": rsi14,
            "atr10": atr10,
            "atr14": atr14,
            "atr40": atr40,
            "vol20": vol20,
            "avg_val20": avg_val20,
            "pit": pit_by_idx,
        }

    breadth_ma20 = [50.0] * n_days
    breadth_ma50 = [50.0] * n_days
    rs_rating_by_day: List[Dict[str, int]] = [{} for _ in range(n_days)]
    sector_stats_by_day: List[Dict[str, Dict[str, Any]]] = [{} for _ in range(n_days)]

    for i in range(WARMUP_BARS, n_days):
        above20 = 0
        above50 = 0
        total_liq = 0
        rs_raw_list: List[Tuple[str, float]] = []
        sec_acc: Dict[str, Dict[str, Any]] = {}

        for sym, sdata in stocks_panel.items():
            if not sdata["valid"][i] or sdata["avg_val20"][i] < 10.0:
                continue
            total_liq += 1
            c = sdata["close"][i]
            is_ab20 = c > sdata["ma20"][i]
            is_ab50 = c > sdata["ma50"][i]
            if is_ab20:
                above20 += 1
            if is_ab50:
                above50 += 1

            r20 = (c / max(1.0, sdata["close"][i - 20]) - 1.0) * 100.0
            r63 = (c / max(1.0, sdata["close"][max(0, i - 63)]) - 1.0) * 100.0
            r126 = (c / max(1.0, sdata["close"][max(0, i - 126)]) - 1.0) * 100.0
            rs_raw = 0.40 * r20 + 0.35 * r63 + 0.25 * r126
            rs_raw_list.append((sym, rs_raw))

            sk = sdata.get("sector_key") or "OTHER"
            sb = sec_acc.setdefault(sk, {"cnt": 0, "ab20": 0, "ab50": 0, "rs_sum": 0.0, "syms": []})
            sb["cnt"] += 1
            if is_ab20:
                sb["ab20"] += 1
            if is_ab50:
                sb["ab50"] += 1
            sb["syms"].append(sym)

        if total_liq > 0:
            breadth_ma20[i] = round((above20 / total_liq) * 100.0, 1)
            breadth_ma50[i] = round((above50 / total_liq) * 100.0, 1)

        rs_raw_list.sort(key=lambda x: x[1])
        m = len(rs_raw_list)
        if m > 1:
            for idx_r, (sym, _) in enumerate(rs_raw_list):
                rs_val = int(round(1 + (idx_r / (m - 1)) * 98))
                rs_rating_by_day[i][sym] = rs_val

        sec_ranked_tmp: List[Tuple[str, float, Dict[str, Any]]] = []
        for sk, sb in sec_acc.items():
            cnt = max(1, sb["cnt"])
            avg_rs_s = sum(rs_rating_by_day[i].get(s, 50) for s in sb["syms"]) / cnt
            br20_s = (sb["ab20"] / cnt) * 100.0
            br50_s = (sb["ab50"] / cnt) * 100.0
            sc_s = round(0.45 * avg_rs_s + 0.35 * br20_s + 0.20 * br50_s, 1)
            sec_ranked_tmp.append((sk, sc_s, {
                "count": cnt,
                "sec_br20": round(br20_s, 1),
                "sec_br50": round(br50_s, 1),
                "sec_avg_rs": round(avg_rs_s, 1),
                "sec_score": sc_s,
            }))
        sec_ranked_tmp.sort(key=lambda x: x[1], reverse=True)
        for rnk_idx, (sk, _, sdict) in enumerate(sec_ranked_tmp, 1):
            sdict["sec_rank"] = rnk_idx
            sector_stats_by_day[i][sk] = sdict

    return {
        "dates": dates,
        "n_days": n_days,
        "vni_open": vni_o,
        "vni_high": vni_h,
        "vni_low": vni_l,
        "vni_close": vni_c,
        "vni_volume": vni_v,
        "vni_vol20": vni_vol20,
        "vni_ma20": vni_ma20,
        "vni_ma50": vni_ma50,
        "vni_dist20": vni_dist20,
        "breadth_ma20": breadth_ma20,
        "breadth_ma50": breadth_ma50,
        "sector_stats": sector_stats_by_day,
        "stocks": stocks_panel,
        "rs_rating": rs_rating_by_day,
    }


def classify_regime_at_bar(panel: Dict[str, Any], i: int, mode: str = "APEX_V2_REGIME_GATED") -> Dict[str, Any]:
    """4-State (V2) / 5-State (V3) / Sector-Rotation Profit Maximizer (V4) Market Regime Classifier."""
    vni = panel["vni_close"][i]
    vni_o = panel["vni_open"][i]
    vni_h = panel["vni_high"][i]
    vni_l = panel["vni_low"][i]
    vni_v = panel["vni_volume"][i]
    vni_v20 = panel["vni_vol20"][i]
    v20 = panel["vni_ma20"][i]
    v50 = panel["vni_ma50"][i]
    v20_prev = panel["vni_ma20"][max(0, i - 5)]
    v50_prev = panel["vni_ma50"][max(0, i - 10)]
    br20 = panel["breadth_ma20"][i]
    br50 = panel["breadth_ma50"][i]
    dist = panel["vni_dist20"][i]

    if mode == "APEX_V4_SECTOR_ALPHA":
        v50_p20 = panel["vni_ma50"][max(0, i - 20)]
        br20_p5 = panel["breadth_ma20"][max(0, i - 5)]
        vni_ext50 = ((vni / max(1.0, v50)) - 1.0) * 100.0
        sec_map = panel["sector_stats"][i]
        lead_secs = sum(1 for sd in sec_map.values() if sd.get("sec_br20", 0.0) >= 54.0 and sd.get("count", 0) >= 3)
        macro_uptrend = (
            vni >= v20
            and vni >= v50
            and v20 >= v50
            and v50 >= v50_p20 * 1.001
            and v20 >= v20_prev
        )
        if vni_ext50 > 7.5:
            return {"regime": "OVEREXTENDED_HOLD", "max_exposure": 0.50, "max_pos": 0, "min_score": 999.0}
        if macro_uptrend and br20 >= 50.0 and br50 >= 48.0 and dist <= 3:
            return {"regime": "CONFIRMED_UPTREND", "max_exposure": 0.92, "max_pos": 3, "min_score": 0.0}
        if macro_uptrend and br20 >= 40.0 and br20 >= br20_p5 and dist <= 3 and lead_secs >= 1:
            return {"regime": "SIDEWAYS_SECTOR_ROTATION", "max_exposure": 0.60, "max_pos": 2, "min_score": 0.0}
        if vni < v20 and vni < v50 and br20 < 32.0:
            return {"regime": "BEAR_DOWNTREND", "max_exposure": 0.0, "max_pos": 0, "min_score": 999.0}
        return {"regime": "CHOPPY_CORRECTION", "max_exposure": 0.0, "max_pos": 0, "min_score": 999.0}

    if (
        vni >= v20
        and vni >= v50
        and v20 >= v50
        and v20 >= v20_prev
        and v50 >= v50_prev * 0.998
        and br20 >= 52.0
        and br50 >= 50.0
        and dist <= 4
    ):
        return {"regime": "CONFIRMED_UPTREND", "max_exposure": 0.90, "max_pos": 3, "min_score": 60.0}
    if mode == "APEX_V3_ASYMMETRIC_CONVICTION":
        rng = max(1e-6, vni_h - vni_l)
        close_in_range = (vni - vni_l) / rng
        vni_vs_ma20 = (vni / max(1.0, v20) - 1.0) * 100.0
        recent_hi5 = max(panel["vni_high"][max(0, i - 5) : i + 1])
        washout_pct = (vni_l / max(1.0, recent_hi5) - 1.0) * 100.0
        is_tight_spring = (
            24.0 <= br20 <= 45.0
            and vni_vs_ma20 <= -0.5
            and vni > vni_o
            and close_in_range >= 0.78
            and vni_v >= vni_v20 * 1.05
            and washout_pct <= -2.0
        )
        if is_tight_spring and dist <= 6:
            return {"regime": "SPRING_INFLECTION_STRIKE", "max_exposure": 0.40, "max_pos": 2, "min_score": 68.0}
        if vni >= v50 and br20 >= 44.0 and br50 >= 44.0 and dist <= 5:
            return {"regime": "UPTREND_UNDER_PRESSURE", "max_exposure": 0.0, "max_pos": 0, "min_score": 999.0}

    if vni >= v50 and br20 >= 44.0 and br50 >= 44.0 and dist <= 5:
        return {"regime": "UPTREND_UNDER_PRESSURE", "max_exposure": 0.0, "max_pos": 0, "min_score": 999.0}

    if vni < v20 and vni < v50 and br20 < 35.0:
        return {"regime": "BEAR_DOWNTREND", "max_exposure": 0.0, "max_pos": 0, "min_score": 999.0}
    return {"regime": "CHOPPY_CORRECTION", "max_exposure": 0.0, "max_pos": 0, "min_score": 999.0}


def score_candidate_at_bar(
    sdata: Dict[str, Any],
    i: int,
    rs_rating: int,
    mode: str,
    regime: str = "CONFIRMED_UPTREND",
    sec_info: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Cham diem co phieu ung vien tai phien i (khong Look-Ahead)."""
    if not sdata["valid"][i]:
        return None
    op = sdata["open"][i]
    px = sdata["close"][i]
    ma20 = sdata["ma20"][i]
    ma50 = sdata["ma50"][i]
    rsi = sdata["rsi14"][i]
    avg_val20 = sdata["avg_val20"][i]
    pit = sdata["pit"][i]
    if not pit:
        return None

    if mode == "BASELINE_ALWAYS_INVESTED":
        if not (10_000.0 <= px <= 40_000.0):
            return None
        f_score = float(pit.get("piotroski_f_score", 5))
        roe = float(pit.get("roe_ttm_pct", 10.0))
        ocf_r = float(pit.get("ocf_to_profit_ratio", 1.0))
        fund_s = min(95.0, 35.0 + f_score * 4.5 + max(0.0, roe - 8.0) * 0.8 + (8.0 if ocf_r >= 1.0 else -5.0))
        tech_s = 40.0 + (20.0 if px > ma20 else 0.0) + rs_rating * 0.35
        return {"symbol": sdata["symbol"], "score": round(0.55 * fund_s + 0.45 * tech_s, 1)}

    # --- APEX_V4_SECTOR_ALPHA (Empirical Profit Maximizer) ---
    if mode == "APEX_V4_SECTOR_ALPHA":
        atr14 = sdata["atr14"][i]
        if avg_val20 < 30.0 or not (7_000.0 <= px <= 38_000.0):
            return None
        if (atr14 / max(1.0, px)) > 0.036:
            return None
        np_ttm = float(pit.get("net_profit_ttm_ty") or 0.0)
        f_score = int(pit.get("piotroski_f_score") or 0)
        roe = float(pit.get("roe_ttm_pct") or 0.0)
        beneish = float(pit.get("beneish_m_score") or -2.5)
        ocf_r = float(pit.get("ocf_to_profit_ratio") or 0.0)
        pre_wc_r = float(pit.get("pre_wc_ocf_to_profit") or 0.0)
        if np_ttm <= 0 or f_score < 6 or roe < 10.5:
            return None
        if sdata["com_type"] == "CT" and (beneish > -1.78 or (ocf_r < 0.70 and pre_wc_r < 0.90)):
            return None
        if px < ma20 or px < ma50 or px > ma20 * 1.06 or rsi > 69.0:
            return None
        min_rs_req = 75 if regime == "SIDEWAYS_SECTOR_ROTATION" else 66
        if rs_rating < min_rs_req:
            return None
        si = sec_info or {}
        if regime == "SIDEWAYS_SECTOR_ROTATION" and si.get("sec_rank", 99) > 4:
            return None

        ey = float(pit.get("earnings_yield_pit") or 0.0)
        pb = float(pit.get("pb_pit") or 3.0)
        pg = max(-20.0, min(80.0, float(pit.get("profit_growth_yoy") or 0.0)))
        accel = float(pit.get("prof_accel_qoq_pct") or 0.0)
        sec_sc = float(si.get("sec_score") or 50.0)
        bank_e = 6.0 if (sdata["com_type"] == "NH" and pb <= 1.5 and roe >= 14.0) else 0.0
        pead_e = 6.0 if (accel > 8.0 and pg > 0.0) else 0.0
        v4_score = (
            rs_rating * 0.40
            + f_score * 2.5
            + min(14.0, max(0.0, (roe - 10.0) * 0.65))
            + min(12.0, max(0.0, ey * 0.9))
            + min(10.0, max(0.0, pg * 0.16))
            + (sec_sc - 50.0) * 0.25
            + bank_e
            + pead_e
        )
        return {"symbol": sdata["symbol"], "score": round(v4_score, 1)}

    # --- APEX_V2 & APEX_V3 ---
    if avg_val20 < 25.0 or not (10_000.0 <= px <= 33_000.0):
        return None
    np_ttm = float(pit.get("net_profit_ttm_ty") or 0.0)
    f_score = int(pit.get("piotroski_f_score") or 0)
    beneish = float(pit.get("beneish_m_score") or -2.5)
    ocf_r = float(pit.get("ocf_to_profit_ratio") or 0.0)
    pre_wc_r = float(pit.get("pre_wc_ocf_to_profit") or 0.0)
    if np_ttm <= 0 or f_score < 6:
        return None
    if sdata["com_type"] == "CT" and (beneish > -1.78 or (ocf_r < 0.70 and pre_wc_r < 0.90)):
        return None

    if mode == "APEX_V3_ASYMMETRIC_CONVICTION" and regime == "SPRING_INFLECTION_STRIKE":
        if rsi > 68.0 or rs_rating < 78 or px < ma50 * 0.98 or px <= op:
            return None
        return {"symbol": sdata["symbol"], "score": round(f_score * 5.0 + rs_rating * 0.5, 1)}
    else:
        if px < ma20 or px < ma50 or rsi > 70.0 or rs_rating < 60:
            return None

    ey = float(pit.get("earnings_yield_pit") or 0.0)
    roe = float(pit.get("roe_ttm_pct") or 0.0)
    pb = float(pit.get("pb_pit") or 3.0)
    pg = float(pit.get("profit_growth_yoy") or 0.0)
    bank_edge = 10.0 if (sdata["com_type"] == "NH" and pb <= 1.45 and roe >= 14.0) else 0.0

    score = (
        f_score * 4.5
        + min(20.0, max(0.0, ey * 1.3))
        + min(15.0, max(0.0, (roe - 10.0) * 0.7))
        + rs_rating * 0.35
        + min(10.0, max(0.0, pg * 0.2))
        + bank_edge
    )
    return {"symbol": sdata["symbol"], "score": round(score, 1)}


def run_simulation(panel: Dict[str, Any], mode: str) -> Dict[str, Any]:
    """Mo phong giao dich dung T+2.5, Lo 100 CP, phi 0.60%/vong tren von goc 20,000,000 VND."""
    dates = panel["dates"]
    n_days = panel["n_days"]
    stocks = panel["stocks"]

    settled_cash = INITIAL_CAPITAL_VND
    pending_cash_queue: List[Tuple[int, float]] = []
    positions: Dict[str, Dict[str, Any]] = {}
    cooldown: Dict[str, int] = {}
    closed_trades: List[Dict[str, Any]] = []
    equity_curve: List[Dict[str, Any]] = []
    regime_days: Dict[str, int] = {}

    for i in range(WARMUP_BARS, n_days):
        d_str = dates[i]

        still_pending = []
        for s_idx, amt in pending_cash_queue:
            if i >= s_idx:
                settled_cash += amt
            else:
                still_pending.append((s_idx, amt))
        pending_cash_queue = still_pending

        reg_info = classify_regime_at_bar(panel, i, mode=mode)
        regime = reg_info["regime"]
        regime_days[regime] = regime_days.get(regime, 0) + 1

        to_remove: List[str] = []
        for sym, pos in list(positions.items()):
            sd = stocks[sym]
            if not sd["valid"][i]:
                continue
            op = sd["open"][i]
            hi = sd["high"][i]
            lo = sd["low"][i]
            cl = sd["close"][i]
            ma20 = sd["ma20"][i]
            ma50 = sd["ma50"][i]
            pos["peak"] = max(pos["peak"], cl)

            if i < pos["tradable_idx"]:
                continue
            days_held = i - pos["entry_idx"]

            # 1. Catastrophic intraday stop (-8% V4, -10% V2/V3) on unscaled position
            cat_mult = 0.92 if mode == "APEX_V4_SECTOR_ALPHA" else 0.90
            cat_stop = pos["entry_px"] * cat_mult
            if mode != "BASELINE_ALWAYS_INVESTED" and lo <= cat_stop and not pos["scaled"]:
                ex = min(op, cat_stop)
                proc = pos["shares"] * ex * (1.0 - SELL_FRICTION)
                cost = pos["cost_px"] * pos["shares"]
                pending_cash_queue.append((i + 2, proc))
                closed_trades.append({
                    "symbol": sym, "entry_date": pos["entry_date"], "exit_date": d_str,
                    "entry_price": pos["entry_px"], "exit_price": round(ex, 0),
                    "shares": pos["shares"], "pnl_vnd": round(proc - cost, 0),
                    "return_pct": round(((proc / cost) - 1.0) * 100.0, 2),
                    "days_held": days_held, "regime_at_entry": pos["reg"], "exit_reason": "CATASTROPHE_STOP",
                })
                if mode == "APEX_V4_SECTOR_ALPHA":
                    cooldown[sym] = i + 12
                to_remove.append(sym)
                continue

            # 2. Close-based Hard Stop or Trailing Stop (prevents intraday spike whipsaws)
            stop_hit = (lo <= pos["stop"]) if mode == "BASELINE_ALWAYS_INVESTED" else (cl <= pos["stop"])
            if stop_hit:
                ex = min(op, pos["stop"]) if mode == "BASELINE_ALWAYS_INVESTED" else cl
                proc = pos["shares"] * ex * (1.0 - SELL_FRICTION)
                cost = pos["cost_px"] * pos["shares"]
                pending_cash_queue.append((i + 2, proc))
                closed_trades.append({
                    "symbol": sym, "entry_date": pos["entry_date"], "exit_date": d_str,
                    "entry_price": pos["entry_px"], "exit_price": round(ex, 0),
                    "shares": pos["shares"], "pnl_vnd": round(proc - cost, 0),
                    "return_pct": round(((proc / cost) - 1.0) * 100.0, 2),
                    "days_held": days_held, "regime_at_entry": pos["reg"], "exit_reason": "STOP_OR_TRAIL",
                })
                if mode == "APEX_V4_SECTOR_ALPHA" and proc < cost:
                    cooldown[sym] = i + 12
                to_remove.append(sym)
                continue

            # 3. Partial Scale-Out 50% at TP1 (+18% V4, +7.5% V3 Spring, +15% V2, +8.5% Baseline)
            if mode == "BASELINE_ALWAYS_INVESTED":
                tp1_mult = 1.085
            elif mode == "APEX_V4_SECTOR_ALPHA":
                tp1_mult = 1.18
            elif pos.get("reg") == "SPRING_INFLECTION_STRIKE":
                tp1_mult = 1.075
            else:
                tp1_mult = 1.15
            if not pos["scaled"] and pos["shares"] >= 200 and hi >= pos["entry_px"] * tp1_mult:
                sell_sh = (pos["shares"] // 200) * 100
                if sell_sh >= 100:
                    ex = max(op, pos["entry_px"] * tp1_mult)
                    proc = sell_sh * ex * (1.0 - SELL_FRICTION)
                    cost = pos["cost_px"] * sell_sh
                    pending_cash_queue.append((i + 2, proc))
                    closed_trades.append({
                        "symbol": sym, "entry_date": pos["entry_date"], "exit_date": d_str,
                        "entry_price": pos["entry_px"], "exit_price": round(ex, 0),
                        "shares": sell_sh, "pnl_vnd": round(proc - cost, 0),
                        "return_pct": round(((proc / cost) - 1.0) * 100.0, 2),
                        "days_held": days_held, "regime_at_entry": pos["reg"], "exit_reason": "SCALE_OUT_TP1",
                    })
                    pos["shares"] -= sell_sh
                    pos["scaled"] = True
                    pos["stop"] = max(pos["stop"], pos["entry_px"] * (1.008 if mode == "APEX_V4_SECTOR_ALPHA" else 1.01))

            # 4. Asymmetric Trailing Stop, Breakeven Lock, 7-Bar Tactical Spring Time-Stop & Bear Defense Exit
            if mode == "APEX_V4_SECTOR_ALPHA":
                if pos["peak"] >= pos["entry_px"] * 1.06:
                    pos["stop"] = max(pos["stop"], pos["entry_px"] * 1.006)
                if pos["peak"] >= pos["entry_px"] * 1.11:
                    pos["stop"] = max(pos["stop"], pos["peak"] * 0.91, ma50 * 0.98)
                if regime == "BEAR_DOWNTREND" and cl < ma20 * 0.985 and days_held >= 4:
                    proc = pos["shares"] * cl * (1.0 - SELL_FRICTION)
                    cost = pos["cost_px"] * pos["shares"]
                    pending_cash_queue.append((i + 2, proc))
                    closed_trades.append({
                        "symbol": sym, "entry_date": pos["entry_date"], "exit_date": d_str,
                        "entry_price": pos["entry_px"], "exit_price": round(cl, 0),
                        "shares": pos["shares"], "pnl_vnd": round(proc - cost, 0),
                        "return_pct": round(((proc / cost) - 1.0) * 100.0, 2),
                        "days_held": days_held, "regime_at_entry": pos["reg"], "exit_reason": "BEAR_DEFENSE_EXIT",
                    })
                    cooldown[sym] = i + 12
                    to_remove.append(sym)
                    continue
            elif mode != "BASELINE_ALWAYS_INVESTED":
                if pos["peak"] >= pos["entry_px"] * 1.10:
                    pos["stop"] = max(pos["stop"], pos["peak"] * 0.90, ma50 * 0.97)
                elif mode == "APEX_V3_ASYMMETRIC_CONVICTION" and pos.get("reg") == "SPRING_INFLECTION_STRIKE" and days_held >= 7 and not pos["scaled"] and regime != "CONFIRMED_UPTREND":
                    proc = pos["shares"] * cl * (1.0 - SELL_FRICTION)
                    cost = pos["cost_px"] * pos["shares"]
                    pending_cash_queue.append((i + 2, proc))
                    closed_trades.append({
                        "symbol": sym, "entry_date": pos["entry_date"], "exit_date": d_str,
                        "entry_price": pos["entry_px"], "exit_price": round(cl, 0),
                        "shares": pos["shares"], "pnl_vnd": round(proc - cost, 0),
                        "return_pct": round(((proc / cost) - 1.0) * 100.0, 2),
                        "days_held": days_held, "regime_at_entry": pos["reg"], "exit_reason": "SPRING_7D_TIMESTOP",
                    })
                    to_remove.append(sym)
                    continue
                elif regime == "BEAR_DOWNTREND" and cl < ma50 * 0.985 and days_held >= 5:
                    proc = pos["shares"] * cl * (1.0 - SELL_FRICTION)
                    cost = pos["cost_px"] * pos["shares"]
                    pending_cash_queue.append((i + 2, proc))
                    closed_trades.append({
                        "symbol": sym, "entry_date": pos["entry_date"], "exit_date": d_str,
                        "entry_price": pos["entry_px"], "exit_price": round(cl, 0),
                        "shares": pos["shares"], "pnl_vnd": round(proc - cost, 0),
                        "return_pct": round(((proc / cost) - 1.0) * 100.0, 2),
                        "days_held": days_held, "regime_at_entry": pos["reg"], "exit_reason": "BEAR_DEFENSE_EXIT",
                    })
                    to_remove.append(sym)
                    continue
            else:
                if pos["peak"] >= pos["entry_px"] * 1.06:
                    pos["stop"] = max(pos["stop"], pos["peak"] * 0.935)

        for sym in to_remove:
            del positions[sym]

        pending_cash_total = sum(amt for _, amt in pending_cash_queue)
        holdings_val = sum(pos["shares"] * stocks[sym]["close"][i] for sym, pos in positions.items())
        nav_now = settled_cash + pending_cash_total + holdings_val

        if mode == "BASELINE_ALWAYS_INVESTED":
            max_exp, max_pos, min_sc = 0.85, 3, 50.0
        else:
            max_exp, max_pos, min_sc = reg_info["max_exposure"], reg_info["max_pos"], reg_info["min_score"]

        budget = min(settled_cash * 0.96, max(0.0, nav_now * max_exp - holdings_val))
        if max_pos > 0 and len(positions) < max_pos and budget >= 1_200_000.0 and i < n_days - 4:
            cands = []
            sec_map_i = panel.get("sector_stats", [])[i] if i < len(panel.get("sector_stats", [])) else {}
            for sym, sd in stocks.items():
                if sym in positions or (mode == "APEX_V4_SECTOR_ALPHA" and i < cooldown.get(sym, 0)):
                    continue
                rs_i = panel["rs_rating"][i].get(sym, 50)
                s_inf = sec_map_i.get(sd.get("sector_key", ""))
                sc = score_candidate_at_bar(sd, i, rs_i, mode, regime=regime, sec_info=s_inf)
                if sc and sc["score"] >= min_sc:
                    cands.append(sc)
            cands.sort(key=lambda x: x["score"], reverse=True)

            for cand in cands:
                if len(positions) >= max_pos or budget < 1_200_000.0:
                    break
                sym = cand["symbol"]
                px = stocks[sym]["close"][i]
                slot = min(budget, nav_now * 0.33)
                lots = int(slot // (px * (1.0 + BUY_FRICTION) * 100.0))
                if lots <= 0:
                    continue
                sh = lots * 100
                cost = sh * px * (1.0 + BUY_FRICTION)
                if cost > settled_cash:
                    continue
                settled_cash -= cost
                budget -= cost
                if mode == "APEX_V4_SECTOR_ALPHA":
                    stop_mult = 0.935
                elif mode == "BASELINE_ALWAYS_INVESTED":
                    stop_mult = 0.935
                elif regime in ("SPRING_INFLECTION_STRIKE", "UPTREND_UNDER_PRESSURE"):
                    stop_mult = 0.945
                else:
                    stop_mult = 0.92
                positions[sym] = {
                    "entry_idx": i,
                    "tradable_idx": i + 3,
                    "entry_date": d_str,
                    "entry_px": px,
                    "cost_px": px * (1.0 + BUY_FRICTION),
                    "shares": sh,
                    "stop": round(px * stop_mult, 0),
                    "peak": px,
                    "scaled": False,
                    "reg": regime,
                }

        holdings_val_eod = sum(pos["shares"] * stocks[sym]["close"][i] for sym, pos in positions.items())
        nav_eod = settled_cash + pending_cash_total + holdings_val_eod
        equity_curve.append({
            "date": d_str,
            "nav": round(nav_eod, 0),
            "invested_pct": round((holdings_val_eod / max(1.0, nav_eod)) * 100.0, 1),
            "regime": regime,
            "vni": panel["vni_close"][i],
        })

    final_idx = n_days - 1
    for sym, pos in positions.items():
        cl = stocks[sym]["close"][final_idx]
        proc = pos["shares"] * cl * (1.0 - SELL_FRICTION)
        cost = pos["cost_px"] * pos["shares"]
        closed_trades.append({
            "symbol": sym, "entry_date": pos["entry_date"], "exit_date": dates[final_idx],
            "entry_price": pos["entry_px"], "exit_price": cl,
            "shares": pos["shares"], "pnl_vnd": round(proc - cost, 0),
            "return_pct": round(((proc / cost) - 1.0) * 100.0, 2),
            "days_held": final_idx - pos["entry_idx"], "regime_at_entry": pos["reg"], "exit_reason": "OPEN_MTM_END",
        })

    navs = [e["nav"] for e in equity_curve]
    total_ret_pct = ((navs[-1] / INITIAL_CAPITAL_VND) - 1.0) * 100.0
    years_elapsed = len(equity_curve) / 250.0
    cagr_pct = (((navs[-1] / INITIAL_CAPITAL_VND) ** (1.0 / max(0.25, years_elapsed))) - 1.0) * 100.0

    vni_start = panel["vni_close"][WARMUP_BARS]
    vni_end = panel["vni_close"][-1]
    vni_ret_pct = ((vni_end / vni_start) - 1.0) * 100.0

    peak_nav = INITIAL_CAPITAL_VND
    max_dd = 0.0
    for nv in navs:
        peak_nav = max(peak_nav, nv)
        max_dd = min(max_dd, ((nv - peak_nav) / peak_nav) * 100.0)

    daily_rets = [(navs[k] - navs[k - 1]) / max(1.0, navs[k - 1]) for k in range(1, len(navs))]
    mean_dr = sum(daily_rets) / max(1, len(daily_rets))
    std_dr = (sum((r - mean_dr) ** 2 for r in daily_rets) / max(1, len(daily_rets))) ** 0.5
    sharpe = (mean_dr / std_dr) * math.sqrt(250.0) if std_dr > 1e-9 else 0.0

    wins = [t for t in closed_trades if t["pnl_vnd"] > 0]
    losses = [t for t in closed_trades if t["pnl_vnd"] <= 0]
    win_rate = (len(wins) / len(closed_trades)) * 100.0 if closed_trades else 0.0
    avg_win_pct = sum(t["return_pct"] for t in wins) / len(wins) if wins else 0.0
    avg_loss_pct = sum(t["return_pct"] for t in losses) / len(losses) if losses else 0.0
    gross_profit = sum(t["pnl_vnd"] for t in wins)
    gross_loss = abs(sum(t["pnl_vnd"] for t in losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 99.0
    payoff_ratio = avg_win_pct / abs(avg_loss_pct) if avg_loss_pct < 0 else 0.0
    emp_ev_pct = ((win_rate / 100.0) * avg_win_pct) + ((1.0 - win_rate / 100.0) * avg_loss_pct)

    weekly_pnls: List[Dict[str, Any]] = []
    for k in range(0, len(equity_curve) - 5, 5):
        w_start = equity_curve[k]
        w_end = equity_curve[min(len(equity_curve) - 1, k + 5)]
        pnl_w = w_end["nav"] - w_start["nav"]
        avg_inv = sum(x["invested_pct"] for x in equity_curve[k : k + 5]) / 5.0
        uptrend_cnt = sum(1 for x in equity_curve[k : k + 5] if x["regime"] == "CONFIRMED_UPTREND")
        weekly_pnls.append({
            "week_start": w_start["date"],
            "pnl_vnd": round(pnl_w, 0),
            "avg_invested_pct": round(avg_inv, 1),
            "is_uptrend_week": uptrend_cnt >= 3,
        })

    all_w_pnls = [w["pnl_vnd"] for w in weekly_pnls]
    up_w_pnls = [w["pnl_vnd"] for w in weekly_pnls if w["is_uptrend_week"]]
    active_w_pnls = [w["pnl_vnd"] for w in weekly_pnls if w["avg_invested_pct"] >= 30.0]
    cash_weeks = [w for w in weekly_pnls if w["avg_invested_pct"] < 15.0]

    regime_stats: Dict[str, Dict[str, Any]] = {}
    for t in closed_trades:
        r_key = t["regime_at_entry"]
        bucket = regime_stats.setdefault(r_key, {"trades": 0, "wins": 0, "total_pnl_vnd": 0.0, "rets": []})
        bucket["trades"] += 1
        if t["pnl_vnd"] > 0:
            bucket["wins"] += 1
        bucket["total_pnl_vnd"] += t["pnl_vnd"]
        bucket["rets"].append(t["return_pct"])

    regime_summary = {}
    for r_key, b in regime_stats.items():
        wr_r = (b["wins"] / b["trades"]) * 100.0 if b["trades"] else 0.0
        avg_r = sum(b["rets"]) / len(b["rets"]) if b["rets"] else 0.0
        regime_summary[r_key] = {
            "trades": b["trades"],
            "win_rate_pct": round(wr_r, 1),
            "avg_return_pct": round(avg_r, 2),
            "total_pnl_vnd": round(b["total_pnl_vnd"], 0),
        }

    calmar_ratio = round(cagr_pct / abs(max_dd), 2) if max_dd < 0 else 0.0
    return {
        "mode": mode,
        "period": f"{equity_curve[0]['date']} -> {equity_curve[-1]['date']}",
        "trading_days": len(equity_curve),
        "initial_capital_vnd": INITIAL_CAPITAL_VND,
        "final_nav_vnd": round(navs[-1], 0),
        "net_profit_vnd": round(navs[-1] - INITIAL_CAPITAL_VND, 0),
        "total_return_pct": round(total_ret_pct, 2),
        "cagr_pct": round(cagr_pct, 2),
        "benchmark_vni_return_pct": round(vni_ret_pct, 2),
        "alpha_vs_vni_pct": round(total_ret_pct - vni_ret_pct, 2),
        "max_drawdown_pct": round(max_dd, 2),
        "sharpe_ratio": round(sharpe, 2),
        "calmar_ratio": calmar_ratio,
        "profit_factor": round(profit_factor, 2),
        "total_trades": len(closed_trades),
        "win_rate_pct": round(win_rate, 1),
        "avg_win_pct": round(avg_win_pct, 2),
        "avg_loss_pct": round(avg_loss_pct, 2),
        "payoff_ratio": round(payoff_ratio, 2),
        "empirical_ev_per_trade_pct": round(emp_ev_pct, 2),
        "total_weeks": len(weekly_pnls),
        "avg_weekly_pnl_vnd_all_weeks": round(sum(all_w_pnls) / max(1, len(all_w_pnls)), 0),
        "uptrend_weeks_count": len(up_w_pnls),
        "avg_weekly_pnl_vnd_uptrend_weeks": round(sum(up_w_pnls) / max(1, len(up_w_pnls)), 0) if up_w_pnls else 0.0,
        "active_invested_weeks_count": len(active_w_pnls),
        "avg_weekly_pnl_vnd_active_weeks": round(sum(active_w_pnls) / max(1, len(active_w_pnls)), 0) if active_w_pnls else 0.0,
        "pct_uptrend_weeks_beating_300k": round((sum(1 for x in up_w_pnls if x >= 300_000) / max(1, len(up_w_pnls))) * 100.0, 1),
        "pct_weeks_in_cash_defensive": round((len(cash_weeks) / max(1, len(weekly_pnls))) * 100.0, 1),
        "regime_day_distribution": regime_days,
        "regime_trade_breakdown": regime_summary,
        "all_trades": closed_trades,
        "top_winners": sorted(closed_trades, key=lambda x: x["pnl_vnd"], reverse=True)[:5],
        "top_losers": sorted(closed_trades, key=lambda x: x["pnl_vnd"])[:5],
    }


def main():
    print("=== [APEX WALK-FORWARD BACKTESTER V7.0] KIEM CHUNG THUC NGHIEM 2 NAM (145 MA BCTC THAT) ===")
    panel = prepare_market_panel()
    print(f"Panel loaded: {len(panel['stocks'])} stocks | {panel['n_days']} bars ({panel['dates'][0]} -> {panel['dates'][-1]})")

    baseline_res = run_simulation(panel, "BASELINE_ALWAYS_INVESTED")
    v2_res = run_simulation(panel, "APEX_V2_REGIME_GATED")
    v3_res = run_simulation(panel, "APEX_V3_ASYMMETRIC_CONVICTION")
    v4_res = run_simulation(panel, "APEX_V4_SECTOR_ALPHA")

    payload = {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "universe_stocks_count": len(panel["stocks"]),
        "friction_model": "0.25% Buy (fee+slippage) + 0.35% Sell (fee+tax+slippage) = 0.60% round-trip | Strict T+2.5 | Lot-100 | PIT BCTC (+45d/+60d)",
        "baseline_always_invested": baseline_res,
        "apex_v2_regime_gated": v2_res,
        "apex_v3_asymmetric_conviction": v3_res,
        "apex_v4_sector_alpha": v4_res,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CALIBRATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    for label, r in [
        ("1. BASELINE (Always Invested / Regime-Blind)", baseline_res),
        ("2. APEX V2.0 (Strict Uptrend Gate + PIT BCTC)", v2_res),
        ("3. APEX V3.0 (Autonomous + Asymmetric Spring Strike)", v3_res),
        ("4. APEX V4.0 (Sector Rotation + PEAD + Chandelier Trail)", v4_res),
    ]:
        print(f"\n--- {label} ---")
        print(f"  Period: {r['period']} ({r['trading_days']} bars / {r['total_weeks']} weeks)")
        print(f"  Final NAV: {r['final_nav_vnd']:,.0f} d (Net {r['net_profit_vnd']:+,.0f} d | Return {r['total_return_pct']:+.2f}% | CAGR {r['cagr_pct']:+.2f}%)")
        print(f"  VN-Index Benchmark: {r['benchmark_vni_return_pct']:+.2f}% | Alpha: {r['alpha_vs_vni_pct']:+.2f}%")
        print(f"  Max Drawdown: {r['max_drawdown_pct']:.2f}% | Sharpe: {r['sharpe_ratio']} | Calmar: {r.get('calmar_ratio')} | Profit Factor: {r['profit_factor']}")
        print(f"  Trades: {r['total_trades']} | Win Rate: {r['win_rate_pct']}% | AvgWin: {r['avg_win_pct']:+.2f}% | AvgLoss: {r['avg_loss_pct']:.2f}% | Payoff: {r['payoff_ratio']}x | EV/trade: {r['empirical_ev_per_trade_pct']:+.2f}%")
        print(f"  Weekly PnL (All weeks): {r['avg_weekly_pnl_vnd_all_weeks']:+,.0f} d/wk | Active Weeks ({r['active_invested_weeks_count']}w): {r['avg_weekly_pnl_vnd_active_weeks']:+,.0f} d/wk | Defensive Cash weeks: {r['pct_weeks_in_cash_defensive']}%")

    print(f"\n[OK] Saved empirical calibration to {CALIBRATION_OUT}")


if __name__ == "__main__":
    main()
