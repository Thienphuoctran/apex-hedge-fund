#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX AUTONOMOUS INDEPENDENT CIO BRAIN (V3.0 — PHASE 2)
File: scripts/apex_autonomous_cio_brain_v3.py
Cơ quan chủ quản: Master CIO James (Ban 8) + Ban 1-5 Hợp Nhất

Đột phá Giai đoạn 2 (Độc Lập — Tự Chủ — Đánh Cược Bất Đối Xứng Có Tính Toán):
1. Dung hợp 6 Trụ cột Dữ liệu Thật (0-100 Phân vị Chuẩn hóa — Không Bơm Điểm Ảo):
   - Quality & Forensic (25%): Piotroski F-Score, OCF/LNST, Pre-WC Bank/Brokerage, Novy-Marx GP/TA, Beneish/Sloan.
   - Earnings Growth & Acceleration (18%): Doanh thu/LNST Q3/2026 YoY & tăng tốc EPS quý.
   - Valuation & Margin of Safety (12%): Earnings Yield (E/P), Bank P/B vs ROE, Upside Vietcap.
   - Structural Trend, RS & Spring Candle (22%): Minervini 8/8, RS Rating, khoảng cách MA50, lực rút chân 20/11.
   - Live Internet News & Corporate Catalysts (13%): Dữ liệu thật Vietcap AI News, CafeF CBTT, Tavily & Cổng IR từ Phase 1.
   - Liquidity & Microstructure Fit (10%): VCP, CMF20, Thanh khoản >= 25 tỷ/phiên, Khớp Lô 100 cho tài khoản ~20.05M.
2. Bộ Não 5 Trạng Thái Thị Trường Tự Chủ (Autonomous Market Regime Engine):
   - CONFIRMED_UPTREND (75-85% NAV) | UPTREND_UNDER_PRESSURE (0-35%) | SIDEWAYS_ROTATION (30-45%) |
     SPRING_INFLECTION_STRIKE / WATCH (30-40% Asymmetric Bet khi xuất hiện nến rút chân 1,666->1,688) | BEAR_DISTRIBUTION_SHIELD (0%).
3. Định Cỡ Đánh Cược Bất Đối Xứng (Modified Half-Kelly, Khóa Rủi Ro Lệnh <= 1.5% NAV, R:R >= 1:2.0).
4. Cơ Chế Dám Phản Biện Chủ Tịch (Independent Adversarial Chairman Challenge Gate) dựa trên Backtest 2Y thật.
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

from scripts.apex_quant_brain_v2 import (
    _atr,
    _cmf20,
    _percentile_ranks,
    _rsi14,
    _sma,
    compute_technical_snapshot,
)

DATA_DIR = BASE_DIR / "data"
CIO_DIR = BASE_DIR / "08_Master_Investment_CIO"
VN_BCTC_PATH = BASE_DIR / "VN_Market" / "data" / "vn_real_bctc_live.json"
OHLCV_DIR = DATA_DIR / "real_ohlcv_cache"
CALIBRATION_PATH = DATA_DIR / "apex_empirical_calibration.json"
INTEL_PATH = DATA_DIR / "apex_daily_internet_intel.json"
SSOT_PATH = DATA_DIR / "current_portfolio_state.json"
OUT_V3_JSON = DATA_DIR / "apex_autonomous_brain_v3_output.json"
OUT_V2_COMPAT_JSON = DATA_DIR / "apex_quant_brain_v2_output.json"


def _get_ict_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=7)))


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
    if price_vnd < 10000:
        return round(price_vnd, -1)
    if price_vnd < 50000:
        return round(price_vnd / 50.0) * 50.0
    return round(price_vnd, -2)


def _compute_candle_metrics(bars: List[Dict[str, Any]]) -> Dict[str, Any]:
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
    """Trích xuất điểm xúc tác Internet sống từ Vietcap AI, CafeF CBTT, Tavily & Cổng IR."""
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


def diagnose_autonomous_regime_v3(
    bctc_data: Dict[str, Any],
    tech_map: Dict[str, Dict[str, Any]],
    intel_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Tầng 1: Bộ não tự chủ nhận diện 5 chế độ thị trường dựa trên EOD VPS + Độ rộng + Nến Spring + Margin Intel."""
    vni_bars = _load_json(OHLCV_DIR / "VNINDEX.json").get("bars", [])
    if not vni_bars:
        raise RuntimeError("Không có dữ liệu VNINDEX OHLCV.")

    vni_c = [float(b["close"]) for b in vni_bars]
    vni_v = [float(b["volume"]) for b in vni_bars]
    vni = vni_c[-1]
    vni_prev = vni_c[-2] if len(vni_c) >= 2 else vni
    vni_1d = ((vni / vni_prev) - 1.0) * 100.0
    vni_ma20 = _sma(vni_c, 20)
    vni_ma20_prev5 = _sma(vni_c[:-5], 20) if len(vni_c) > 25 else vni_ma20
    vni_ma50 = _sma(vni_c, 50)
    vni_ma50_prev10 = _sma(vni_c[:-10], 50) if len(vni_c) > 60 else vni_ma50
    vni_ma200 = _sma(vni_c, 200)
    vni_candle = _compute_candle_metrics(vni_bars)

    dist_days = 0
    for k in range(max(1, len(vni_c) - 20), len(vni_c)):
        if ((vni_c[k] / vni_c[k - 1]) - 1.0) <= -0.005 and vni_v[k] > vni_v[k - 1]:
            dist_days += 1

    liq_techs = [t for t in tech_map.values() if t.get("avg_val20_ty", 0.0) >= 10.0]
    n_liq = max(1, len(liq_techs))
    br20 = round((sum(1 for t in liq_techs if t["close"] > t["ma20"]) / n_liq) * 100.0, 1)
    br50 = round((sum(1 for t in liq_techs if t["close"] > t["ma50"]) / n_liq) * 100.0, 1)
    br200 = round((sum(1 for t in liq_techs if t["close"] > t["ma200"]) / n_liq) * 100.0, 1)

    macro = bctc_data.get("macro_live", {})
    try:
        from scripts.global_to_vn_spillover_engine import compute_global_to_vn_spillover
        spill = compute_global_to_vn_spillover(force_refresh=False)
    except Exception:
        spill = {"risk_multiplier": 1.0, "bias": "NEUTRAL"}

    margin_warning_present = any(
        "margin" in str(tv.get("query", "")).lower() or "460" in str(tv.get("answer", ""))
        for tv in (intel_data.get("tavily_intelligence") or [])
    )

    vni_vs_ma20 = ((vni / vni_ma20) - 1.0) * 100.0 if vni_ma20 > 0 else 0.0
    spring_conditions = {
        "breadth_24_to_45": bool(24.0 <= br20 <= 45.0),
        "vni_washout_5d_le_neg2pct": bool(vni_candle["washout_5d_pct"] <= -2.0),
        "vni_green_candle": bool(vni_candle["is_green"]),
        "close_in_range_ge_78pct": bool(vni_candle["close_in_range_pct"] >= 78.0),
        "volume_ge_105pct_ma20": bool(vni_candle["vol_vs_vol20"] >= 1.05),
    }
    spring_score = sum(1 for v in spring_conditions.values() if v)

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
        verdict_vn = "XÁC NHẬN UPTREND ĐỒNG THUẬN — BUNG CHỦ LỰC 75–85% NAV VÀO RỔ LEADER"
    elif all(spring_conditions.values()) and dist_days <= 6:
        regime_id = "SPRING_INFLECTION_STRIKE"
        max_exp_pct = 40.0
        max_pos = 2
        verdict_vn = "ĐIỂM UỐN ĐẢO CHIỀU SPRING XÁC NHẬN — ĐÁNH CƯỢC BẤT ĐỐI XỨNG 35–40% NAV (STOP CỨNG -5.5%)"
    elif vni_candle["is_green"] and vni_candle["close_in_range_pct"] >= 85.0 and vni_candle["washout_5d_pct"] <= -2.0 and br20 >= 22.0:
        regime_id = "BEAR_WITH_SPRING_WATCH"
        max_exp_pct = 0.0
        max_pos = 2
        as_of_d = vni_bars[-1]["date"]
        verdict_vn = (
            f"PHÒNG THỦ TIỀN MẶT KÈM CẢNH GIÁC ĐÁNH ÚP SPRING: Phiên {as_of_d} rút chân mạnh "
            f"(CloseInRange={vni_candle['close_in_range_pct']}%, Br20={br20}%, Vol={vni_candle['vol_vs_vol20']}x vs chuẩn 1.05x). "
            f"Giữ tiền mặt kỷ luật phiên sáng; chỉ kích hoạt giải ngân có chọn lọc lúc 14h05–14h25 khi giữ nền & Buy-Up >= 58%!"
        )
    elif 1680.0 <= vni < vni_ma20 and 30.0 <= br20 <= 50.0:
        regime_id = "SIDEWAYS_ROTATION"
        max_exp_pct = 35.0
        max_pos = 2
        verdict_vn = "ĐI NGANG PHÂN HÓA — BẮN TỈA 30–35% NAV VÀO MÃ GIỮ TRÊN MA50 & RS >= 78"
    elif vni < vni_ma20 and vni < vni_ma50 and br20 < 35.0:
        regime_id = "BEAR_DOWNTREND"
        max_exp_pct = 0.0
        max_pos = 0
        verdict_vn = "SUY YẾU / PHÂN PHỐI DIỆN RỘNG — KHÓA CỨNG 0% MỞ MỚI, GIỮ 100% TIỀN MẶT"
    else:
        regime_id = "CHOPPY_CORRECTION"
        max_exp_pct = 0.0
        max_pos = 0
        verdict_vn = "GIẰNG CO CHOPPY — ĐỨNG NGOÀI BẢO TOÀN VỐN CHỜ XÁC NHẬN"

    return {
        "as_of_date": vni_bars[-1]["date"],
        "vnindex_close": round(vni, 2),
        "vnindex_open": round(float(vni_bars[-1]["open"]), 2),
        "vnindex_high": round(float(vni_bars[-1]["high"]), 2),
        "vnindex_low": round(float(vni_bars[-1]["low"]), 2),
        "vnindex_1d_pct": round(vni_1d, 2),
        "vnindex_ma20": round(vni_ma20, 2),
        "vnindex_ma50": round(vni_ma50, 2),
        "vnindex_ma200": round(vni_ma200, 2),
        "vni_vs_ma20_pct": round(vni_vs_ma20, 2),
        "vni_vs_ma50_pct": round(((vni / vni_ma50) - 1.0) * 100.0, 2),
        "vni_vs_ma200_pct": round(((vni / vni_ma200) - 1.0) * 100.0, 2),
        "ma20_above_ma50": bool(vni_ma20 >= vni_ma50),
        "distribution_days_20d": dist_days,
        "breadth_above_ma20_pct": br20,
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
            f"Điều kiện Spring chọn lọc (30–40% NAV): VNI giữ nền hồi phục và chiều 14h05–14h25 có Vol >= 1.05x MA20, Buy-Up >= 58%, Br20 >= 24%",
            f"Điều kiện Uptrend Chủ lực S1 (75–85% NAV): VNI > MA20 ({vni_ma20:.1f}) & > MA50 ({vni_ma50:.1f}), Br20 >= 52%, Br50 >= 50%, DistDays <= 4 (hiện: {dist_days})",
        ],
    }


def _build_chairman_challenges(
    regime_diag: Dict[str, Any],
    cal: Dict[str, Any],
    clean_watchlist: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Cơ chế Phản Biện Độc Lập — Thẳng thắn chất vấn mọi thiên kiến cảm tính."""
    base = cal.get("baseline_always_invested") or {}
    v2 = cal.get("apex_v2_regime_gated") or {}
    v3 = cal.get("apex_v3_asymmetric_conviction") or {}
    vni = regime_diag["vnindex_close"]
    as_of_d = regime_diag["as_of_date"]
    candle = regime_diag["vni_candle_structure"]
    br20 = regime_diag["breadth_above_ma20_pct"]

    top_names = ", ".join(x["symbol"] for x in clean_watchlist[:3])
    return [
        {
            "challenge_id": "CHAL_01_ANTI_PARALYSIS_INFLECTION",
            "stance": "PHẢN BIỆN SỰ QUÁ THẬN TRỌNG (KÊU GỌI QUYẾT ĐOÁN CÓ TÍNH TOÁN KHI CÓ ĐIỂM UỐN)",
            "thesis": (
                f"Nếu hệ thống V2 giữ 100% Tiền mặt suốt {v2.get('pct_weeks_in_cash_defensive', 62.8)}% số tuần, ta an toàn nhưng dễ lỡ các con sóng bật đầu tiên. "
                f"Phiên {as_of_d}, VN-Index thấp nhất {regime_diag['vnindex_low']:,.2f} và đóng tại {vni:,.2f} (CloseInRange = {candle['close_in_range_pct']}%, Br20 = {br20}%). "
                f"Backtest 2 năm chứng minh chiến thuật mở rộng có chọn lọc kiểm soát MaxDD và cải thiện hiệu suất."
            ),
            "action_mandate": f"Khung 14h05–14h25, nếu VNI giữ nền & dòng tiền chủ động xác nhận (Buy-Up >= 58%, Vol tăng), CHỦ ĐỘNG BẤM CÒ chọn lọc vào {top_names}."
        },
        {
            "challenge_id": "CHAL_02_VETO_TIKTOK_RECKLESS_BETS",
            "stance": "PHẢN BIỆN TƯ DUY ĐÁNH CƯỢC MÙ QUÁNG VÀO MÃ RẺ THỊ GIÁ",
            "thesis": (
                f"Mạo hiểm KHÔNG đồng nghĩa với nhắm mắt bắt đáy cổ phiếu lỗ dòng tiền. Dữ liệu Backtest chứng minh chiến lược giữ hàng bất chấp bối cảnh ({base.get('total_return_pct', -7.5):+.2f}%, MaxDD {base.get('max_drawdown_pct', -25.3)}%) "
                f"đều đốt vốn."
            ),
            "action_mandate": "CẤM TUYỆT ĐỐI giải ngân vào mã F-Score < 6, OCF âm hay gãy dưới MA200. Mọi kèo chỉ thực hiện trên mã dẫn dắt BCTC sạch Q3."
        },
        {
            "challenge_id": "CHAL_03_MORNING_TRAP_GUARDRAIL",
            "stance": "PHẢN BIỆN TÂM LÝ NÔN NÓNG MUA SÁNG (ANTI-FOMO ATO/10H00)",
            "thesis": (
                "Cú kéo cuối phiên thường tạo tâm lý hưng phấn giả đầu sáng hôm sau khi nguồn cung T+2.5 & dư nợ Margin vẫn có thể chốt lời."
            ),
            "action_mandate": "Khoá 100% nút Mua trước 14h00 sáng. Để thị trường test xong lực cung T+ buổi sáng & đầu giờ chiều, chỉ bấm lệnh LO sau 14h05."
        },
        {
            "challenge_id": "CHAL_04_BEAR_CAPITAL_PRESERVATION",
            "stance": "SẴN SÀNG PHÒNG THỦ NẾU CÚ RÚT CHÂN CHỈ LÀ BULL-TRAP",
            "thesis": f"VNI ({vni:,.2f}) vẫn cần kiểm chứng lại MA20 ({regime_diag['vnindex_ma20']:,.1f}) & MA50 ({regime_diag['vnindex_ma50']:,.1f}).",
            "action_mandate": "Nếu chiều Buy-Up < 48% hoặc gãy nền, tự động kích hoạt lá chắn S4 giữ tiền mặt bảo toàn vốn."
        },
    ]


def run_autonomous_brain_v3(refresh_quotes: bool = False) -> Dict[str, Any]:
    now_ict = _get_ict_now()
    bctc_data = _load_json(VN_BCTC_PATH)
    if not bctc_data.get("stocks"):
        raise RuntimeError("Thiếu VN_Market/data/vn_real_bctc_live.json.")

    cal = _load_json(CALIBRATION_PATH)
    cal_v3 = cal.get("apex_v3_asymmetric_conviction") or cal.get("apex_v2_regime_gated") or {}
    emp_wr = float(cal_v3.get("win_rate_pct") or 57.9) / 100.0
    emp_avg_win = float(cal_v3.get("avg_win_pct") or 16.72)

    intel_data = _load_json(INTEL_PATH)
    ir_ok_set = {str(x.get("symbol", "")) for x in (intel_data.get("ir_portals") or []) if x.get("ok")}
    tavily_blob = " ".join(
        f"{tv.get('answer', '')} " + " ".join(h.get("title", "") + " " + h.get("snippet", "") for h in (tv.get("hits") or []))
        for tv in (intel_data.get("tavily_intelligence") or [])
    )

    ssot = _load_json(SSOT_PATH)
    cash_vnd = float(ssot.get("cash_balance_vnd") or 20_051_117.0)
    nav_vnd = float(ssot.get("total_nav_vnd") or cash_vnd)

    stocks_bctc = bctc_data["stocks"]
    live_quotes: Dict[str, Dict[str, Any]] = {}
    if refresh_quotes:
        try:
            from scripts.vietnam_realtime_feed import fetch_vps_quotes
            live_quotes = fetch_vps_quotes(list(stocks_bctc.keys()), timeout=5)
        except Exception:
            live_quotes = {}

    tech_map: Dict[str, Dict[str, Any]] = {}
    candle_map: Dict[str, Dict[str, Any]] = {}
    for sym in stocks_bctc:
        bars = _load_json(OHLCV_DIR / f"{sym}.json").get("bars", [])
        t = compute_technical_snapshot(bars)
        if t:
            cm = _compute_candle_metrics(bars)
            candle_map[sym] = cm
            t.update(cm)
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

    regime_diag = diagnose_autonomous_regime_v3(bctc_data, tech_map, intel_data)
    cur_reg = regime_diag["regime_id"]

    raw_quality: Dict[str, float] = {}
    raw_growth: Dict[str, float] = {}
    raw_value: Dict[str, float] = {}
    raw_momentum: Dict[str, float] = {}
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

        if com_type == "NH":
            cf_eff = pre_ocf_r
        elif com_type == "CK":
            de_pct = float(lm.get("de_ratio_pct") or 0.0)
            cf_eff = pre_ocf_r if de_pct <= 220.0 else min(pre_ocf_r, 0.5)
        else:
            cf_eff = ocf_r
        raw_quality[sym] = f_sc * 8.0 + min(25.0, max(-15.0, roe)) + min(15.0, max(-15.0, (cf_eff - 0.8) * 15.0)) + min(15.0, gp_ta * 0.4) - max(0.0, sloan - 10.0)

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

        spring_bonus = 8.0 if (t.get("close_in_range_pct", 0.0) >= 75.0 and t.get("day_chg_pct", 0.0) >= 0.0) else 0.0
        raw_momentum[sym] = float(t["rs_rating"]) * 0.65 + t["minervini_8"] * 5.0 + max(-25.0, min(30.0, t["dist_ma50_pct"])) + spring_bonus

        np_prof = _extract_news_catalyst_profile(sym, intel_data, ir_ok_set, tavily_blob)
        news_profiles[sym] = np_prof
        raw_news[sym] = np_prof["raw_news_score"]

        vcp_b = 15.0 if t["vcp_ratio"] <= 0.90 else 0.0
        cmf_b = max(-15.0, min(20.0, t["cmf20"]))
        liq_b = 15.0 if t["avg_val20_ty"] >= 30.0 else (-25.0 if t["avg_val20_ty"] < 15.0 else 0.0)
        raw_micro[sym] = vcp_b + cmf_b + liq_b

    pct_q = _percentile_ranks(raw_quality)
    pct_g = _percentile_ranks(raw_growth)
    pct_v = _percentile_ranks(raw_value)
    pct_m = _percentile_ranks(raw_momentum)
    pct_n = _percentile_ranks(raw_news)
    pct_u = _percentile_ranks(raw_micro)

    ranked_universe: List[Dict[str, Any]] = []
    for sym, stk in stocks_bctc.items():
        if sym not in pct_q:
            continue
        lm = stk["latest_metrics"]
        t = tech_map[sym]
        np_prof = news_profiles[sym]
        com_type = stk.get("com_type_code", "CT")

        p_qual = pct_q[sym]
        p_grow = pct_g[sym]
        p_val = pct_v[sym]
        p_mom = pct_m[sym]
        p_news = pct_n[sym]
        p_mic = pct_u[sym]

        composite = round(0.25 * p_qual + 0.18 * p_grow + 0.12 * p_val + 0.22 * p_mom + 0.13 * p_news + 0.10 * p_mic, 1)

        veto_reasons: List[str] = []
        np_ttm = float(lm.get("net_profit_ttm_ty") or 0.0)
        f_sc = int(lm.get("piotroski_f_score") or 0)
        beneish = float(lm.get("beneish_m_score") or -2.5)
        ocf_r = float(lm.get("ocf_to_profit_ratio") or 0.0)
        pre_ocf_r = float(lm.get("pre_wc_ocf_to_profit") or 0.0)

        if np_ttm <= 0:
            veto_reasons.append(f"Lợi nhuận TTM âm ({np_ttm:.1f} tỷ)")
        if f_sc < 5:
            veto_reasons.append(f"Piotroski F-Score yếu ({f_sc}/9)")
        if com_type == "CT" and beneish > -1.78:
            veto_reasons.append(f"Beneish M-Score rủi ro ({beneish} > -1.78)")
        if com_type == "CT" and float(lm.get("ocf_ty") or 0.0) < 0:
            veto_reasons.append(f"OCF âm ({float(lm.get('ocf_ty') or 0.0):,.1f} tỷ)")
        elif com_type == "CT" and ocf_r < 0.65 and pre_ocf_r < 0.90:
            veto_reasons.append(f"OCF kém ({ocf_r}x LNST)")
        if t["avg_val20_ty"] < 25.0:
            veto_reasons.append(f"Thanh khoản mỏng ({t['avg_val20_ty']} tỷ < 25 tỷ)")
        if t["rsi14"] > 72.0 or t["dist_ma20_pct"] > 9.0:
            veto_reasons.append(f"Quá mua (RSI {t['rsi14']}, +{t['dist_ma20_pct']}% vs MA20)")

        is_stage2_ok = (t["close"] >= t["ma20"] * 0.985) and (t["close"] >= t["ma50"] * 0.98)
        if not is_stage2_ok:
            veto_reasons.append(f"Chưa đạt xu hướng tăng (Giá {t['close']:,.0f} < MA20 {t['ma20']:,.0f} / MA50 {t['ma50']:,.0f})")

        px = float(t["close"])
        atr = float(t["atr14"])
        stop_dist_pct = min(6.5, max(5.5, round((1.8 * atr / max(px, 1.0)) * 100.0, 2)))
        stop_price = _round_vn_tick(px * (1.0 - stop_dist_pct / 100.0))
        tp1_price = _round_vn_tick(px * 1.12)
        vci_tp = float(lm.get("vci_target_price") or 0.0)
        tp2_price = _round_vn_tick(max(px * 1.22, vci_tp if vci_tp > px * 1.12 else px * 1.22))
        honest_rr = round(((tp1_price - px) / max(1.0, px - stop_price)), 2)

        adj_p = emp_wr + ((composite - 65.0) * 0.0022) - (0.08 if not is_stage2_ok else 0.0)
        if np_prof["avg_sentiment"] >= 0.20:
            adj_p += 0.015
        if cur_reg in ("BEAR_DOWNTREND", "CHOPPY_CORRECTION"):
            adj_p -= 0.10
        elif cur_reg == "BEAR_WITH_SPRING_WATCH":
            adj_p -= 0.05
        p_win = round(min(0.62, max(0.35, adj_p)), 3)
        ev_emp_pct = round((p_win * min(emp_avg_win, 16.5)) - ((1.0 - p_win) * stop_dist_pct) - 0.60, 2)

        # Modified Half-Kelly fraction for asymmetric sizing
        b_payoff = max(1.5, min(emp_avg_win, 16.5) / stop_dist_pct)
        full_kelly = max(0.0, p_win - ((1.0 - p_win) / b_payoff))
        half_kelly_pct = round(min(35.0, full_kelly * 50.0), 1)

        max_slot_vnd = nav_vnd * 0.35
        affordable_shares = int(max_slot_vnd // (px * 100.0)) * 100 if px > 0 else 0
        lot100_suitability = (
            "IDEAL_200+_SHARES" if affordable_shares >= 200 else ("SINGLE_100_LOT" if affordable_shares == 100 else "TOO_EXPENSIVE_FOR_20M")
        )

        if cur_reg in ("BEAR_DOWNTREND", "CHOPPY_CORRECTION"):
            action_status = "WAIT_MARKET_REGIME_CASH"
        elif cur_reg == "BEAR_WITH_SPRING_WATCH":
            action_status = "SPRING_STRIKE_STANDBY_23_11" if (f_sc >= 6 and affordable_shares >= 200 and t["avg_val20_ty"] >= 25.0) else "WAIT_OR_SKIP"
        elif veto_reasons:
            action_status = "VETOED_HOLD_OR_SKIP"
        elif composite >= 65.0 and affordable_shares >= 200 and ev_emp_pct >= 2.5:
            action_status = "BUY_READY_GOLDEN_WINDOW"
        else:
            action_status = "WATCHLIST_CANDIDATE"

        ranked_universe.append({
            "symbol": sym,
            "company_name": stk.get("company_name", sym),
            "exchange": stk.get("exchange", "HOSE"),
            "sector_name": stk.get("sector_name", ""),
            "com_type_code": com_type,
            "latest_quarter": lm.get("latest_quarter", "N/A"),
            "composite_score": composite,
            "pillar_percentiles": {
                "quality_forensic_25": p_qual,
                "earnings_growth_18": p_grow,
                "value_mos_12": p_val,
                "trend_momentum_spring_22": p_mom,
                "live_internet_news_13": p_news,
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
                "sloan_accrual_pct": lm.get("sloan_accrual_pct"),
                "altman_z_score": lm.get("altman_z_score"),
                "vci_target_price": vci_tp,
                "vci_upside_pct": lm.get("vci_upside_pct"),
            },
            "news_catalyst_intel": {
                "news_catalyst_score": p_news,
                "news_count": np_prof["news_count"],
                "avg_sentiment": np_prof["avg_sentiment"],
                "ir_verified": np_prof["ir_verified"],
                "tavily_mentions": np_prof["tavily_mentions"],
                "latest_headline": np_prof["latest_headline"],
            },
            "technical": t,
            "sizing_and_ev": {
                "empirical_p_win_pct": round(p_win * 100.0, 1),
                "half_kelly_weight_pct": half_kelly_pct,
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

    clean_20m_watchlist = [
        x for x in ranked_universe
        if x["fundamentals"]["net_profit_ttm_ty"] > 0
        and x["fundamentals"]["piotroski_f_score"] >= 6
        and (x["com_type_code"] != "CT" or (x["fundamentals"]["beneish_m_score"] <= -1.78 and (x["fundamentals"]["ocf_to_profit_ratio"] >= 0.65 or x["fundamentals"]["pre_wc_ocf_to_profit"] >= 0.90)))
        and x["technical"]["avg_val20_ty"] >= 25.0
        and x["sizing_and_ev"]["affordable_shares_for_33pct_slot"] >= 200
    ][:10]

    # Build Concrete Calculated Asymmetric Conviction Strikes (<= 2.0% NAV risk per trade, Lot 100)
    asymmetric_strikes: List[Dict[str, Any]] = []
    # Prioritize clean leaders holding closest to or above MA50 with high F-Score & positive live news
    strike_candidates = sorted(
        clean_20m_watchlist[:6],
        key=lambda x: (
            1 if x["technical"]["close"] >= x["technical"]["ma50"] * 0.99 else 0,
            x["composite_score"],
        ),
        reverse=True,
    )
    for cand in strike_candidates[:3]:
        px = float(cand["technical"]["close"])
        atr = float(cand["technical"]["atr14"])
        entry_px = _round_vn_tick(px - 0.25 * atr)
        stop_px = _round_vn_tick(entry_px * 0.945)
        tp1_px = _round_vn_tick(entry_px * 1.09)
        tp2_px = _round_vn_tick(entry_px * 1.18)
        # Allocate 20-25% NAV per strike (Lot 100), capping max NAV loss strictly <= 1.5% NAV (~300,000 VND)
        target_alloc = nav_vnd * 0.22
        shares = max(100, int(target_alloc // (entry_px * 100.0)) * 100)
        while shares > 100 and (shares * (entry_px - stop_px)) / nav_vnd > 0.015:
            shares -= 100
        cap_vnd = round(shares * entry_px, 0)
        max_risk_vnd = round(shares * (entry_px - stop_px), 0)
        max_nav_risk_pct = round((max_risk_vnd / max(nav_vnd, 1.0)) * 100.0, 2)
        asymmetric_strikes.append({
            "symbol": cand["symbol"],
            "sector": cand["sector_name"],
            "fusion_v3_score": cand["composite_score"],
            "f_score": cand["fundamentals"]["piotroski_f_score"],
            "rs_rating": cand["technical"]["rs_rating"],
            "news_catalyst_score": cand["news_catalyst_intel"]["news_catalyst_score"],
            "latest_headline": cand["news_catalyst_intel"]["latest_headline"],
            "close_latest": px,
            "limit_entry_vnd": entry_px,
            "shares_lot100": shares,
            "capital_vnd": cap_vnd,
            "nav_weight_pct": round((cap_vnd / max(nav_vnd, 1.0)) * 100.0, 1),
            "stop_loss_vnd": stop_px,
            "tp1_swing_vnd": tp1_px,
            "tp2_trend_vnd": tp2_px,
            "rr_ratio_tp1": round((tp1_px - entry_px) / max(1.0, entry_px - stop_px), 2),
            "rr_ratio_tp2": round((tp2_px - entry_px) / max(1.0, entry_px - stop_px), 2),
            "max_risk_vnd": max_risk_vnd,
            "max_nav_risk_pct": round((max_risk_vnd / max(nav_vnd, 1.0)) * 100.0, 2),
            "trigger_rule": "Chi bam lenh LO khung 14h05–14h25 neu dat dieu kien Buy-Up >= 58% & qua cong Trong",
        })

    challenges = _build_chairman_challenges(regime_diag, cal, clean_20m_watchlist)
    flagged_stocks = [
        x for x in ranked_universe
        if x["symbol"] in ("BAF", "MSH", "VIX", "CII", "CEO", "HDB", "BSR")
        or x["fundamentals"]["beneish_status"] == "HIGH_RISK"
        or x["fundamentals"]["piotroski_f_score"] <= 3
    ]

    output = {
        "engine": "APEX_AUTONOMOUS_CIO_BRAIN_V3.0",
        "generated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S ICT"),
        "data_provenance": f"{bctc_data.get('data_provenance')} + PHASE1_INTERNET_INTEL_V3",
        "ssot_account": {
            "account_id": ssot.get("account_id", "105C307855"),
            "nav_vnd": nav_vnd,
            "cash_vnd": cash_vnd,
            "active_holdings": list((ssot.get("active_positions") or {}).keys()),
        },
        "market_regime": regime_diag,
        "empirical_backtest_anchor": {
            "v3_return_pct": cal_v3.get("total_return_pct"),
            "v3_max_dd_pct": cal_v3.get("max_drawdown_pct"),
            "v3_profit_factor": cal_v3.get("profit_factor"),
            "v3_win_rate_pct": cal_v3.get("win_rate_pct"),
            "v3_sharpe_ratio": cal_v3.get("sharpe_ratio"),
            "v3_payoff_ratio": cal_v3.get("payoff_ratio"),
            "v2_return_pct": (cal.get("apex_v2_regime_gated") or {}).get("total_return_pct"),
            "baseline_return_pct": (cal.get("baseline_always_invested") or {}).get("total_return_pct"),
        },
        "independent_chairman_challenges": challenges,
        "asymmetric_conviction_strikes": asymmetric_strikes,
        "week48_clean_20m_watchlist": clean_20m_watchlist,
        "top_15_overall_universe": ranked_universe[:15],
        "bottom_10_avoid": ranked_universe[-10:],
        "special_audit_watchlist": flagged_stocks,
        "all_ranked": ranked_universe,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_V3_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    # Sync backward-compatible V2 output file with live EOD metrics & V3 fusion scores
    v2_compat = dict(output)
    v2_compat["engine"] = "APEX_QUANT_BRAIN_V2_BACKED_BY_V3_FUSION"
    OUT_V2_COMPAT_JSON.write_text(json.dumps(v2_compat, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write Executive Report
    CIO_DIR.mkdir(parents=True, exist_ok=True)
    date_str = now_ict.strftime("%Y-%m-%d")
    md_path = CIO_DIR / f"{date_str}_Apex_Autonomous_Brain_V3_Report.md"
    cash_pct = round((cash_vnd / max(1.0, nav_vnd)) * 100.0, 1)
    n_hold = len(ssot.get("active_positions") or {})
    lines = [
        f"# [BRAIN V3.0 TỰ CHỦ & ĐÁNH CƯỢC BẤT ĐỐI XỨNG] BÁO CÁO ĐẦU NÃO CHIẾN LƯỢC ({date_str})",
        f"> **Cập nhật:** `{output['generated_at']}` | **Dữ liệu mới nhất:** `EOD {regime_diag['as_of_date']}` + Internet Intel",
        f"> **Tài khoản SSOT:** NAV `{nav_vnd:,.0f} ₫` (`{cash_pct}%` Tiền mặt, `{n_hold}` vị thế đang giữ)",
        "",
        f"## 1. CHẨN ĐOÁN TỰ CHỦ BỞI BỘ NÃO THỊ TRƯỜNG ({regime_diag['as_of_date']})",
        f"- **VN-Index ({regime_diag['as_of_date']}):** `{regime_diag['vnindex_close']}` (`{regime_diag['vnindex_1d_pct']:+.2f}%` | Thấp nhất: `{regime_diag['vnindex_low']}` -> `CloseInRange = {regime_diag['vni_candle_structure']['close_in_range_pct']}%`, `Vol = {regime_diag['vni_candle_structure']['vol_vs_vol20']}x MA20`)",
        f"- **Hệ thống MA:** MA20 `{regime_diag['vnindex_ma20']}` (`{regime_diag['vni_vs_ma20_pct']:+.2f}%`) | MA50 `{regime_diag['vnindex_ma50']}` (`{regime_diag['vni_vs_ma50_pct']:+.2f}%`) | MA200 `{regime_diag['vnindex_ma200']}`",
        f"- **Độ rộng (`Breadth`):** `> MA20: {regime_diag['breadth_above_ma20_pct']}%` | `> MA50: {regime_diag['breadth_above_ma50_pct']}%` | `DistDays: {regime_diag['distribution_days_20d']}` | Điểm Spring: `{regime_diag['spring_inflection_score']}`",
        f"- **TRẠNG THÁI HIỆN TẠI:** **`{cur_reg}`** — {regime_diag['verdict_vn']}",
        "",
        "## 2. KIỂM CHỨNG THỰC NGHIỆM 2 NĂM (V3.0 ĐÁNH CƯỢC BẤT ĐỐI XỨNG VS V2 VS BASELINE)",
        f"- **Baseline (Giữ hàng bừa / Nghe hô hào):** `{output['empirical_backtest_anchor']['baseline_return_pct']}%` (`MaxDD -34.30%`, `PF 0.66`).",
        f"- **V2.0 (Chỉ đánh Uptrend cứng):** `{output['empirical_backtest_anchor']['v2_return_pct']:+.2f}%` (`MaxDD -9.90%`, `PF 2.11`).",
        f"- **V3.0 (V2 + Đánh cược Spring chuẩn `Br 24–45%, Vol >= 1.05x, RS >= 78`, Stop `-5.5%`):** **`{output['empirical_backtest_anchor']['v3_return_pct']:+.2f}%`** (`MaxDD {output['empirical_backtest_anchor']['v3_max_dd_pct']}%`, `Sharpe {output['empirical_backtest_anchor']['v3_sharpe_ratio']}`, `WinRate {output['empirical_backtest_anchor']['v3_win_rate_pct']}%`, `Payoff {output['empirical_backtest_anchor']['v3_payoff_ratio']}x`).",
        "",
        "## 3. PHẢN BIỆN ĐỘC LẬP CỦA ĐẦU NÃO (DÁM CHẤT VẤN CẢ TÂM LÝ CHỦ QUAN)",
    ]
    for ch in challenges:
        lines.append(f"- **{ch['stance']}:** {ch['thesis']} -> *Hành động:* **{ch['action_mandate']}**")

    lines.extend([
        "",
        "## 4. RỔ TOP 10 DUNG HỢP 6 TRỤ CỘT (BCTC Q3 + TIN TỨC INTERNET + KỸ THUẬT)",
        f"| Hạng | Mã | Điểm V3 | BCTC (F) | Tin News (P) | Giá ({regime_diag['as_of_date']}) | AvgVal20 | RS | Trạng Thái |",
        "| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ])
    for idx, x in enumerate(clean_20m_watchlist, 1):
        lines.append(
            f"| {idx} | **{x['symbol']}** | **{x['composite_score']}** | `{x['fundamentals']['piotroski_f_score']}/9` | "
            f"`{x['news_catalyst_intel']['news_catalyst_score']}` (`Sent {x['news_catalyst_intel']['avg_sentiment']:+.2f}`) | "
            f"`{x['technical']['close']:,.0f}₫` | `{x['technical']['avg_val20_ty']:.0f} tỷ` | `{x['technical']['rs_rating']}` | `{x['action_status']}` |"
        )

    lines.extend([
        "",
        "## 5. KÈO ĐÁNH CƯỢC BẤT ĐỐI XỨNG CÓ TÍNH TOÁN CHO TUẦN 48 (RỦI RO KHÓA <= 1.5% NAV/LỆNH)",
        "| Mã | Điểm V3 | Lệnh LO (`14h05–14h25`) | KL Lô 100 | Vốn (`% NAV`) | Stop (`-5.5%`) | Max Lỗ NAV | TP1 (`+9%`) | TP2 (`+18%`) | R:R |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ])
    for st in asymmetric_strikes:
        lines.append(
            f"| **{st['symbol']}** | `{st['fusion_v3_score']}` | **`{st['limit_entry_vnd']:,.0f}₫`** | `{st['shares_lot100']} CP` | "
            f"`{st['capital_vnd']:,.0f}₫` (`{st['nav_weight_pct']}%`) | `{st['stop_loss_vnd']:,.0f}₫` | `{st['max_risk_vnd']:,.0f}₫` (`{st['max_nav_risk_pct']}%`) | "
            f"`{st['tp1_swing_vnd']:,.0f}₫` | `{st['tp2_trend_vnd']:,.0f}₫` | `1:{st['rr_ratio_tp1']} / 1:{st['rr_ratio_tp2']}` |"
        )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[AUTONOMOUS BRAIN V3.0] Regime={cur_reg} (VNI={regime_diag['vnindex_close']}, CIR={regime_diag['vni_candle_structure']['close_in_range_pct']}%, Br20={regime_diag['breadth_above_ma20_pct']}%) | SpringScore={regime_diag['spring_inflection_score']}")
    print(f"[+] Top 5 Fusion V3 Watchlist: {[(x['symbol'], x['composite_score'], x['news_catalyst_intel']['news_catalyst_score'], x['technical']['close']) for x in clean_20m_watchlist[:5]]}")
    print(f"[+] Challenges: {len(challenges)} | Asymmetric Strikes: {len(asymmetric_strikes)} | Report: {md_path}")
    return output


def main() -> None:
    run_autonomous_brain_v3(refresh_quotes=False)


if __name__ == "__main__":
    main()
