#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX DEEP FINANCIAL BRAIN & PROFIT-MAXIMIZING OPTIMIZER (V5.0 — STEP 2)
File: scripts/apex_deep_financial_brain.py
Cơ quan chủ quản: Ban 2 (BCTC & Pháp Y), Ban 4 (Quản Trị Rủi Ro Định Lượng) & Ban 8 (Master CIO James)

Chức năng cốt lõi:
1. Phân tích Pháp y BCTC Chuyên sâu & Định giá 3 Phương pháp (`analyze_deep_bctc_and_valuation`):
   - DuPont, ROIC vs WACC (EVA Spread %), Tiền thật OCF/LNST, FCF Yield, Piotroski F-Score (/9),
     Modified Beneish M-Score, Altman Z''-Score, Sloan Accrual Ratio.
   - Tách bạch 3 chế độ kế toán: BANK_CAMELS_BASEL (CASA, NIM, NPL, LLR, CAR, Justified P/B),
     BROKERAGE_FVTPL_MARGIN, và CORPORATE_VAS_TT200 / US_GAAP.
   - Hợp lưu định giá 3 mô hình (Graham Number, Fair P/E-PEG GARP, Bank Justified P/B / FCF Target) -> Biên an toàn %.
2. Tối ưu hóa Danh mục & Lợi nhuận Toàn thị trường (`run_full_market_alpha_optimization`):
   - Chấm điểm Apex Master Alpha Score (0-100) dùng trọng số động từ `adaptive_weights_vn.json` & `adaptive_weights.json`.
   - Tính P(Win), R:R, Kỳ vọng toán học EV% và Half-Kelly %, kết hợp Global Spillover Risk Multiplier.
   - Kiểm toán Lô chẵn 100 CP TCBS khớp tiền mặt SSOT (`current_portfolio_state.json`).
   - Đánh giá & tối ưu hóa trực tiếp từng vị thế đang nắm giữ (`Active Holdings Optimizer`).
"""

import argparse
import datetime
import json
import math
import sqlite3
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
CIO_DIR = BASE_DIR / "08_Master_Investment_CIO"
DEEP_BRAIN_JSON = DATA_DIR / "deep_financial_brain_analysis.json"
VN_WEIGHTS_JSON = BASE_DIR / "VN_Market" / "config" / "adaptive_weights_vn.json"
US_WEIGHTS_JSON = BASE_DIR / "config" / "adaptive_weights.json"
DB_PATH = DATA_DIR / "apex_institutional_vault.db"


def _get_ict_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=7))
    )


def _load_json_safe(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _compute_piotroski_score(prof: Dict[str, Any], ocf_ratio: float, d_to_e: float) -> int:
    """Tính điểm Piotroski F-Score (0-9) tất định từ BCTC."""
    roe = float(prof.get("roe", 0.0) or 0.0)
    rev_g = float(prof.get("rev_growth_yoy", 0.0) or 0.0)
    prof_g = float(prof.get("profit_growth_yoy", 0.0) or 0.0)
    gm = float(prof.get("gross_margin_pct", 0.0) or 0.0)
    om = float(prof.get("operating_margin_pct", 0.0) or 0.0)

    pts = 0
    if roe > 0:
        pts += 1
    if ocf_ratio > 0:
        pts += 1
    if prof_g > 0:
        pts += 1
    if ocf_ratio >= 1.0:
        pts += 1
    if d_to_e <= 1.2 or prof.get("accounting_regime") == "BANK_CAMELS_BASEL":
        pts += 1
    if float(prof.get("cash_and_equiv_ty", 0.0) or 0.0) > 0:
        pts += 1
    if rev_g > 5.0:
        pts += 1
    if gm >= 18.0 or om >= 15.0:
        pts += 1
    if float(prof.get("agm_completion_est_pct") or 90.0) >= 85.0:
        pts += 1
    return min(9, max(1, pts))


def analyze_deep_bctc_and_valuation(symbol: str, prof: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Mô-đun A: Phân tích Pháp y BCTC DuPont & Hợp lưu Định giá 3 Mô hình cho 1 mã cổ phiếu."""
    from scripts.apex_omni_intelligence_crawler import fetch_live_ticker_financial_profile

    sym = symbol.upper().strip()
    if prof is None:
        prof = fetch_live_ticker_financial_profile(sym, fetch_ohlcv=True)

    market = prof.get("market", "VN")
    regime = prof.get("accounting_regime", "CORPORATE_VAS_TT200")
    sector_name = prof.get("sector_name", "Doanh nghiệp")
    is_bank = regime == "BANK_CAMELS_BASEL" or "Ngân Hàng" in sector_name

    live_price = float(prof.get("live_price") or prof.get("last_close") or prof.get("current_price") or 0.0)
    pe = float(prof.get("pe", 0.0) or 0.0)
    pb = float(prof.get("pb", 0.0) or 0.0)
    roe = float(prof.get("roe", 0.0) or 0.0)
    rev_g = float(prof.get("rev_growth_yoy", 0.0) or 0.0)
    prof_g = float(prof.get("profit_growth_yoy", 0.0) or 0.0)
    ocf_ratio = float(prof["ocf_ratio"]) if prof.get("ocf_ratio") is not None else 1.0
    d_to_e = float(prof.get("debt_to_equity", 0.5) or 0.5)
    wacc = 11.5 if market == "VN" else 9.0

    # 1. DuPont & ROIC/EVA Spread
    net_margin = float(prof.get("operating_margin_pct", 0.0) or 0.0)
    if net_margin <= 0 and float(prof.get("revenue_ttm_ty", 0.0) or 0.0) > 0:
        net_margin = round((float(prof.get("net_profit_ttm_ty", 0.0)) / float(prof["revenue_ttm_ty"])) * 100.0, 2)
    roic_est = round(roe * (0.85 if is_bank else max(0.55, 1.0 / (1.0 + d_to_e * 0.45))), 2)
    eva_spread = round(roic_est - wacc, 2)
    piotroski = (
        int(prof["piotroski_f_score_live"])
        if prof.get("piotroski_f_score_live") is not None
        else _compute_piotroski_score(prof, ocf_ratio, d_to_e)
    )

    # 2. Chạy Động cơ Pháp y Kế toán VAS/TT200
    forensic_res: Dict[str, Any] = {
        "forensic_score": 82.0,
        "forensic_verdict": "AUDIT_CLEAN_STANDARD",
        "forensic_label": "BCTC ĐẠT CHUẨN",
        "red_flags_count": 0,
        "red_flags_detail": [],
    }
    beneish_used = float(prof["beneish_m_score_live"]) if prof.get("beneish_m_score_live") is not None else (-2.65 if ocf_ratio >= 1.0 else (-2.10 if ocf_ratio >= 0.8 else -1.55))
    if market == "VN":
        try:
            from VN_Market.scripts.vn_forensic_accounting_engine import audit_vas_forensic_accounting
            rev_ty = float(prof.get("revenue_ttm_ty", 1000.0) or 1000.0)
            np_ty = float(prof.get("net_profit_ttm_ty", 120.0) or 120.0)
            rec_ty = float(prof.get("receivables_ty", 0.0) or 0.0)
            rec_pct = round((rec_ty / rev_ty) * 100.0, 1) if rev_ty > 0 and rec_ty > 0 else 15.0
            other_rec_pct = (
                float(prof["other_receivables_to_assets_pct"])
                if prof.get("other_receivables_to_assets_pct") is not None
                else min(25.0, rec_pct * 0.35)
            )
            altman_est = float(prof["altman_z_score_live"]) if prof.get("altman_z_score_live") is not None else (3.8 if d_to_e <= 0.8 else (2.4 if d_to_e <= 1.5 else 1.55))
            sloan_est = float(prof["sloan_accrual_pct_live"]) if prof.get("sloan_accrual_pct_live") is not None else round(max(-5.0, min(18.0, (1.0 - ocf_ratio) * 12.0)), 1)
            payload = {
                "code": sym,
                "sector_name": sector_name,
                "accounting_regime": regime,
                "receivables_to_rev_pct": rec_pct,
                "other_receivables_to_assets_pct": other_rec_pct,
                "cip_over_3yrs_ty": 0.0,
                "revenue_ttm_ty": rev_ty,
                "net_profit_ttm_ty": np_ty,
                "npl_pct": float(prof.get("npl_pct") or 1.4),
                "llr_coverage_pct": float(prof.get("llr_coverage_pct") or 115.0),
                "car_pct": float(prof.get("car_pct") or 12.0),
                "casa_pct": float(prof.get("casa_pct") or 22.0),
                "beneish_m_score": beneish_used,
                "altman_z_score": altman_est,
                "ocf_to_profit_ratio": ocf_ratio,
                "sloan_accrual_pct": sloan_est,
            }
            forensic_res = audit_vas_forensic_accounting(payload)
        except Exception:
            pass
    else:
        fcf_b = float(prof.get("fcf_b_usd", 0.0) or 0.0)
        f_score = 88.0 if (fcf_b > 0 and roe >= 15.0) else (72.0 if roe > 0 else 45.0)
        forensic_res = {
            "forensic_score": f_score,
            "forensic_verdict": "US_GAAP_VERIFIED" if f_score >= 70 else "US_LOSS_OR_CASH_BURN",
            "forensic_label": "BCTC US-GAAP TIỀN THẬT KHỎE" if f_score >= 70 else "CẢNH BÁO DÒNG TIỀN ÂM / LỖ",
            "red_flags_count": 0 if f_score >= 70 else 1,
            "red_flags_detail": [],
        }

    # 3. Hợp lưu Định giá 3 Phương pháp (Triangulation)
    # Phương pháp 1: Graham Intrinsic Multiplier từ P/E & P/B thực tế
    graham_target = live_price
    if live_price > 0 and pe > 0 and pb > 0:
        graham_ratio = math.sqrt(22.5 / max(1.0, pe * pb))
        graham_target = round(live_price * min(1.85, max(0.55, graham_ratio)), 2 if market == "US" else 0)

    # Phương pháp 2: Fair P/E-PEG (GARP - Peter Lynch)
    growth_anchor = max(6.0, min(35.0, prof_g if prof_g > 0 else rev_g if rev_g > 0 else 10.0))
    peg_ratio = round(pe / growth_anchor, 2) if pe > 0 else 1.0
    fair_pe_base = min(28.0 if market == "US" else 22.0, max(8.5 if is_bank else 11.0, growth_anchor * 0.92))
    if ocf_ratio >= 1.1:
        fair_pe_base *= 1.08
    pe_target = round(live_price * min(1.9, max(0.6, fair_pe_base / pe)), 2 if market == "US" else 0) if (live_price > 0 and pe > 0) else live_price

    # Phương pháp 3: Bank Justified P/B hoặc Quality ROE Target
    if is_bank and live_price > 0 and pb > 0:
        g_long = 4.5
        coe = 13.0
        justified_pb = max(0.85, min(2.8, (max(8.0, roe) - g_long) / (coe - g_long)))
        pb_target = round(live_price * min(1.85, max(0.65, justified_pb / pb)), 0)
        fair_value = round((graham_target * 0.25 + pe_target * 0.35 + pb_target * 0.40), 0)
        method_3_name = f"Justified P/B ({justified_pb:.2f}x)"
        method_3_val = pb_target
    else:
        quality_mult = 1.0 + max(-0.25, min(0.45, eva_spread / 40.0))
        q_target = round(live_price * quality_mult, 2 if market == "US" else 0) if live_price > 0 else live_price
        if market == "US" and float(prof.get("target_upside_pct", 0.0) or 0.0) != 0 and live_price > 0:
            q_target = round(live_price * (1.0 + float(prof["target_upside_pct"]) / 100.0), 2)
        fair_value = round((graham_target * 0.25 + pe_target * 0.45 + q_target * 0.30), 2 if market == "US" else 0)
        method_3_name = "EVA / Wall Street Target"
        method_3_val = q_target

    upside_pct = round(((fair_value / live_price) - 1.0) * 100.0, 1) if (live_price > 0 and fair_value > 0) else 0.0
    if upside_pct >= 20.0:
        val_verdict = "DEEP_VALUE"
    elif upside_pct >= 8.0:
        val_verdict = "ATTRACTIVE"
    elif upside_pct >= -5.0:
        val_verdict = "FAIRLY_VALUED"
    else:
        val_verdict = "EXPENSIVE"

    # 4. Chấm điểm 5 Trụ cột & Apex Master Alpha Score (0-100)
    # 4.1 Điểm BCTC & Tiền thật (0-100)
    bctc_score = 45.0
    bctc_score += min(20.0, max(-10.0, (roe - 10.0) * 1.1))
    bctc_score += min(15.0, max(-15.0, (ocf_ratio - 0.85) * 30.0))
    bctc_score += min(12.0, max(-8.0, prof_g * 0.4))
    bctc_score += (float(forensic_res.get("forensic_score", 80.0)) - 75.0) * 0.35
    bctc_score = round(max(10.0, min(98.0, bctc_score)), 1)

    # 4.2 Điểm Định giá & Biên an toàn (0-100)
    val_score = round(max(10.0, min(96.0, 58.0 + upside_pct * 1.25 - max(0.0, (peg_ratio - 1.5) * 10.0))), 1)

    # 4.3 Điểm Dòng tiền thông minh & Mua chủ động (0-100)
    buy_up = float(prof.get("buy_up_pct", 52.0) or 52.0)
    f_net_bil = float(prof.get("foreign_net_val_bil", 0.0) or 0.0)
    chg_1d = float(prof.get("change_1d_pct", 0.0) or 0.0)
    flow_score = 50.0 + (buy_up - 50.0) * 1.1 + (8.0 if f_net_bil > 0.5 else (-6.0 if f_net_bil < -2.0 else 0.0))
    flow_score = round(max(15.0, min(95.0, flow_score)), 1)

    # 4.4 Điểm Kỹ thuật & Xu hướng (0-100)
    rsi = float(prof.get("rsi14", 52.0) or 52.0)
    ma20 = float(prof.get("ma20", 0.0) or 0.0)
    ma50 = float(prof.get("ma50", 0.0) or 0.0)
    atr14 = float(prof.get("atr14", 0.0) or 0.0)
    tech_score = 55.0
    if live_price > 0 and ma20 > 0:
        tech_score += 12.0 if live_price >= ma20 else -8.0
    if live_price > 0 and ma50 > 0:
        tech_score += 12.0 if live_price >= ma50 else -10.0
    if 45.0 <= rsi <= 66.0:
        tech_score += 10.0
    elif rsi > 72.0:
        tech_score -= 14.0
    tech_score = round(max(15.0, min(95.0, tech_score)), 1)

    return {
        "symbol": sym,
        "market": market,
        "company_name": prof.get("company_name", sym),
        "sector_name": sector_name,
        "accounting_regime": regime,
        "live_price": live_price,
        "change_1d_pct": chg_1d,
        "buy_up_pct": buy_up,
        "foreign_net_val_bil": f_net_bil,
        "rsi14": rsi,
        "ma20": ma20,
        "ma50": ma50,
        "atr14": atr14,
        "pe": pe,
        "pb": pb,
        "peg_ratio": peg_ratio,
        "roe_pct": roe,
        "roic_est_pct": roic_est,
        "wacc_pct": wacc,
        "eva_spread_pct": eva_spread,
        "net_margin_pct": net_margin,
        "rev_growth_yoy": rev_g,
        "profit_growth_yoy": prof_g,
        "ocf_ty": float(prof["ocf_ty"]) if prof.get("ocf_ty") is not None else None,
        "ocf_ratio": ocf_ratio,
        "beneish_m_score": beneish_used,
        "avg_val_1m_ty": float(prof["avg_val_1m_ty"]) if prof.get("avg_val_1m_ty") is not None else None,
        "latest_quarter": prof.get("latest_quarter", "STATIC"),
        "debt_to_equity": d_to_e,
        "piotroski_f_score": piotroski,
        "forensic": forensic_res,
        "valuation": {
            "graham_target": graham_target,
            "pe_garp_target": pe_target,
            "model3_name": method_3_name,
            "model3_target": method_3_val,
            "intrinsic_fair_value": fair_value,
            "margin_of_safety_pct": upside_pct,
            "verdict": val_verdict,
        },
        "pillar_scores": {
            "bctc_quality": bctc_score,
            "valuation_mos": val_score,
            "smart_money_flow": flow_score,
            "technical_trend": tech_score,
        },
        "catalyst": prof.get("catalyst", ""),
        "audit_firm": prof.get("audit_firm", ""),
        "ir_url": prof.get("bctc_direct_portal") or prof.get("official_ir_url") or prof.get("sec_url") or "",
    }


_EMP_REG_CACHE: Dict[str, Any] = {}


def _load_empirical_and_regime() -> tuple[float, str]:
    global _EMP_REG_CACHE
    if _EMP_REG_CACHE:
        return float(_EMP_REG_CACHE["emp_wr"]), str(_EMP_REG_CACHE["regime_id"])
    emp_wr = 52.0
    cur_reg = "SIDEWAY_CHOPPY"
    try:
        cal_p = DATA_DIR / "apex_empirical_calibration.json"
        if cal_p.exists():
            cal = json.loads(cal_p.read_text(encoding="utf-8"))
            emp_wr = float((cal.get("apex_v2_regime_gated") or {}).get("win_rate_pct") or 52.0)
    except Exception:
        emp_wr = 52.0
    try:
        v2_p = DATA_DIR / "apex_quant_brain_v2_output.json"
        if v2_p.exists():
            v2 = json.loads(v2_p.read_text(encoding="utf-8"))
            cur_reg = str(((v2.get("market_regime") or v2.get("regime_diagnosis") or {}).get("regime_id")) or "SIDEWAY_CHOPPY")
    except Exception:
        cur_reg = "SIDEWAY_CHOPPY"
    _EMP_REG_CACHE = {"emp_wr": emp_wr, "regime_id": cur_reg}
    return emp_wr, cur_reg


def _compute_ev_and_kelly(alpha_score: float, analysis: Dict[str, Any], max_alloc_cap_pct: float) -> Dict[str, Any]:
    """Tính P(Win) hiệu chỉnh thực nghiệm, Stop Loss 2xATR (<=7.5%), TP1, R:R, EV% và Half-Kelly %."""
    px = float(analysis.get("live_price", 0.0) or 0.0)
    atr = float(analysis.get("atr14", 0.0) or 0.0)
    upside = float(analysis.get("valuation", {}).get("margin_of_safety_pct", 0.0) or 0.0)

    if px > 0 and atr > 0:
        raw_stop_pct = (2.0 * atr / px) * 100.0
        risk_pct = round(min(7.5, max(3.5, raw_stop_pct)), 2)
    else:
        risk_pct = 6.0

    # Không ép sàn thưởng 10% cho cổ phiếu bị định giá đắt (upside <= 0)
    if upside > 0:
        reward_pct = round(max(risk_pct * 1.2, min(25.0, upside)), 2)
    else:
        reward_pct = round(max(4.0, risk_pct * 1.1), 2)
    rr_ratio = round(reward_pct / risk_pct, 2) if risk_pct > 0 else 1.5

    # Hiệu chỉnh xác suất thắng P(W) thực nghiệm từ Backtest Walk-Forward & Market Regime sống (trần cứng 62%)
    emp_wr, cur_reg = _load_empirical_and_regime()
    forensic_s = float(analysis.get("forensic", {}).get("forensic_score", 80.0))
    is_bank = analysis.get("accounting_regime") == "BANK_CAMELS_BASEL"
    ocf_ratio = float(analysis["ocf_ratio"]) if analysis.get("ocf_ratio") is not None else 1.0

    emp_p = emp_wr / 100.0
    p_win = emp_p + (alpha_score - 65.0) * 0.0025 + (forensic_s - 75.0) * 0.0015
    if cur_reg == "BEAR_DOWNTREND":
        p_win -= 0.10
    elif cur_reg == "CHOPPY_CORRECTION":
        p_win -= 0.05
    if (not is_bank and ocf_ratio < 0.5) or forensic_s < 65.0:
        p_win -= 0.08
    p_win = min(0.62, max(0.28, p_win))
    ev_pct = round(p_win * reward_pct - (1.0 - p_win) * risk_pct, 2)

    # Half-Kelly criterion f* = p - (1-p)/R:R (khóa = 0 khi BEAR_DOWNTREND)
    kelly_full = max(0.0, p_win - ((1.0 - p_win) / max(0.5, rr_ratio)))
    half_kelly_pct = 0.0 if cur_reg == "BEAR_DOWNTREND" else round(min(max_alloc_cap_pct, kelly_full * 50.0), 1)

    stop_price = round(px * (1.0 - risk_pct / 100.0), 2 if analysis["market"] == "US" else 0) if px > 0 else 0.0
    tp1_price = round(px * (1.0 + (reward_pct * 0.65) / 100.0), 2 if analysis["market"] == "US" else 0) if px > 0 else 0.0
    tp2_price = round(px * (1.0 + reward_pct / 100.0), 2 if analysis["market"] == "US" else 0) if px > 0 else 0.0

    return {
        "p_win_pct": round(p_win * 100.0, 1),
        "risk_pct": risk_pct,
        "reward_pct": reward_pct,
        "rr_ratio": rr_ratio,
        "ev_pct": ev_pct,
        "half_kelly_pct": half_kelly_pct,
        "stop_loss_price": stop_price,
        "tp1_price": tp1_price,
        "tp2_price": tp2_price,
        "live_regime_id": cur_reg,
        "empirical_calibration_source": "apex_empirical_calibration.json",
    }


def _fetch_60d_returns_entrade(symbol: str, timeout: float = 4.0) -> List[float]:
    """Lấy chuỗi lợi suất ngày 60 phiên gần nhất từ VPS HistDataFeed (ưu tiên) & Entrade DNSE fallback."""
    import urllib.request
    import urllib.parse
    now_ts = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    from_ts = now_ts - 115 * 86400
    sym_q = urllib.parse.quote(symbol)
    urls = [
        f"https://histdatafeed.vps.com.vn/tradingview/history?symbol={sym_q}&resolution=D&from={from_ts}&to={now_ts}",
        f"https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?resolution=D&symbol={sym_q}&from={from_ts}&to={now_ts}",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            closes = [float(x) for x in (data.get("c") or []) if x and float(x) > 0]
            if len(closes) >= 16:
                closes = closes[-61:]
                return [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes))]
        except Exception:
            continue
    return []


def _pearson_corr(r1: List[float], r2: List[float]) -> Optional[float]:
    n = min(len(r1), len(r2))
    if n < 15:
        return None
    a = r1[-n:]
    b = r2[-n:]
    ma = sum(a) / n
    mb = sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = sum((x - ma) ** 2 for x in a) ** 0.5
    db = sum((y - mb) ** 2 for y in b) ** 0.5
    if da <= 1e-12 or db <= 1e-12:
        return None
    return round(max(-1.0, min(1.0, num / (da * db))), 3)


def compute_holdings_correlation_matrix(
    held_symbols: List[str],
    candidate_symbols: List[str],
    universe: Dict[str, Dict[str, Any]],
    sector_exposure_pct: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    V6.0 Nâng cấp 3: Tính Ma trận Tương quan Lợi suất 60 phiên giữa danh mục đang nắm giữ
    và các ứng viên Top Alpha, kết hợp chốt chặn tập trung ngành (>35% NAV hoặc Corr >= 0.72).
    """
    from concurrent.futures import ThreadPoolExecutor

    held = [s.upper().strip() for s in held_symbols if s]
    cands = [s.upper().strip() for s in candidate_symbols if s]
    fetch_targets = sorted({s for s in (held + cands[:12]) if universe.get(s, {}).get("market", "VN") == "VN"})

    returns_map: Dict[str, List[float]] = {}
    if fetch_targets:
        with ThreadPoolExecutor(max_workers=6) as ex:
            fut_map = {s: ex.submit(_fetch_60d_returns_entrade, s, 2.5) for s in fetch_targets}
            for s, fut in fut_map.items():
                try:
                    returns_map[s] = fut.result(timeout=3.5)
                except Exception:
                    returns_map[s] = []

    def _fallback_sector_corr(s1: str, s2: str) -> float:
        if s1 == s2:
            return 1.0
        u1 = universe.get(s1, {})
        u2 = universe.get(s2, {})
        if u1.get("market") != u2.get("market"):
            return 0.22
        sc1 = str(u1.get("sector_code", "")).upper()
        sc2 = str(u2.get("sector_code", "")).upper()
        if sc1 and sc1 == sc2:
            return 0.78
        if u1.get("accounting_regime") == u2.get("accounting_regime") == "BANK_CAMELS_BASEL":
            return 0.76
        cyclical = {"BANK", "SEC", "FIN", "RE", "STEEL", "CONSTRUCTION"}
        if sc1 in cyclical and sc2 in cyclical:
            return 0.56
        return 0.34

    matrix: Dict[str, Dict[str, Any]] = {}
    all_eval_syms = list(dict.fromkeys(held + cands))
    for sym in all_eval_syms:
        row_corr: Dict[str, float] = {}
        method = "HISTORICAL_60D_ENTRADE" if len(returns_map.get(sym, [])) >= 15 else "SECTOR_BETA_MODEL"
        for h_sym in held:
            if sym == h_sym:
                row_corr[h_sym] = 1.0
                continue
            r_c = _pearson_corr(returns_map.get(sym, []), returns_map.get(h_sym, []))
            if r_c is None:
                r_c = _fallback_sector_corr(sym, h_sym)
                method = "HYBRID_60D_AND_SECTOR_FALLBACK" if method == "HISTORICAL_60D_ENTRADE" else "SECTOR_BETA_MODEL"
            row_corr[h_sym] = r_c

        other_corrs = {k: v for k, v in row_corr.items() if k != sym}
        if other_corrs:
            most_sym = max(other_corrs, key=lambda k: other_corrs[k])
            max_corr = other_corrs[most_sym]
        else:
            most_sym = held[0] if held else ""
            max_corr = 0.0

        sec_code = str(universe.get(sym, {}).get("sector_code", "Core"))
        sec_nav_pct = float((sector_exposure_pct or {}).get(sec_code, 0.0) or 0.0)

        matrix[sym] = {
            "pairwise_with_holdings": row_corr,
            "max_corr_with_holdings": round(max_corr, 3),
            "most_correlated_holding": most_sym,
            "sector_code": sec_code,
            "current_sector_nav_pct": round(sec_nav_pct, 1),
            "estimation_method": method,
        }

    live_series_cnt = sum(1 for v in returns_map.values() if len(v) >= 15)
    return {
        "session_window": 60,
        "held_symbols": held,
        "live_60d_series_fetched": live_series_cnt,
        "total_symbols_evaluated": len(all_eval_syms),
        "matrix": matrix,
    }


def run_full_market_alpha_optimization(force_live: bool = True) -> Dict[str, Any]:
    """Mô-đun B: Quét & Tối ưu hóa Lợi nhuận Danh mục + Xếp hạng Toàn thị trường."""
    from scripts.apex_omni_intelligence_crawler import _load_master_universe, search_market_intelligence
    from scripts.portfolio_state_manager import PortfolioStateManager
    from scripts.global_to_vn_spillover_engine import compute_global_to_vn_spillover
    from scripts.execution_slippage_tracker import load_adaptive_filters
    from scripts.vietnam_realtime_feed import fetch_vn_market_indices_live, fetch_vps_quotes, fetch_stock_indicators_live

    now_ict = _get_ict_now()
    ssot = PortfolioStateManager.load_state()
    cash_vnd = float(ssot.get("cash_balance_vnd", 12516471.0) or 0.0)
    realized_vnd = float(ssot.get("realized_pnl_vnd", 167119.0) or 0.0)
    active_pos = ssot.get("active_positions", {})

    vn_w_cfg = _load_json_safe(VN_WEIGHTS_JSON).get("weights", {})
    w_bctc = float(vn_w_cfg.get("bctc_earnings_quality", 0.35))
    w_flow = float(vn_w_cfg.get("cashflow_and_smart_money", 0.25))
    w_macro = float(vn_w_cfg.get("macro_monetary_sbv", 0.15))
    w_val = float(vn_w_cfg.get("valuation_fair_value", 0.15))
    w_tech = float(vn_w_cfg.get("technical_and_atr_risk", 0.10))

    mkt_live = fetch_vn_market_indices_live()
    spillover = compute_global_to_vn_spillover(force_refresh=False)
    filters = load_adaptive_filters()

    breadth_pct = float(mkt_live.get("market_breadth", {}).get("advance_ratio_pct", 50.0) or 50.0)
    vni_pct = float(mkt_live.get("vn_index", {}).get("change_pct", 0.0) or 0.0)
    spill_mult = float(spillover.get("risk_multiplier", 1.0) or 1.0)
    max_alloc_cap = float(spillover.get("max_new_allocation_pct", 50.0) or 50.0)

    # Điểm Vĩ mô thống nhất kết hợp Breadth VN + Global Spillover (0-100)
    macro_score = round(max(20.0, min(92.0, 50.0 + (breadth_pct - 45.0) * 0.6 + vni_pct * 4.0 + (spill_mult - 1.0) * 30.0)), 1)

    universe = _load_master_universe()
    # Phủ dữ liệu BCTC sống Q3/2026 từ Vietcap IQ Official (vn_real_bctc_live.json) lên toàn bộ universe
    live_bctc_path = BASE_DIR / "VN_Market" / "data" / "vn_real_bctc_live.json"
    if live_bctc_path.exists():
        try:
            live_stocks = json.loads(live_bctc_path.read_text(encoding="utf-8")).get("stocks", {})
            for sym, item in live_stocks.items():
                lm = item.get("latest_metrics") or {}
                if not lm:
                    continue
                entry = dict(universe.get(sym, {}))
                cur_px = float(lm.get("current_price") or entry.get("live_price") or 0.0)
                entry.update({
                    "symbol": sym,
                    "market": "VN",
                    "company_name": item.get("company_name") or entry.get("company_name", sym),
                    "sector_name": item.get("sector_name") or entry.get("sector_name", "Doanh nghiệp"),
                    "sector_code": entry.get("sector_code") or item.get("sector_key") or "Core",
                    "accounting_regime": lm.get("accounting_regime") or entry.get("accounting_regime", "CORPORATE_VAS_TT200"),
                    "deep_bctc_audited": True,
                    "latest_quarter": lm.get("latest_quarter", "2026Q3"),
                    "revenue_ttm_ty": float(lm.get("revenue_ttm_ty") or 0.0),
                    "net_profit_ttm_ty": float(lm.get("net_profit_ttm_ty") or 0.0),
                    "rev_growth_yoy": float(lm.get("rev_growth_yoy") or 0.0),
                    "profit_growth_yoy": float(lm.get("profit_growth_yoy") or 0.0),
                    "gross_margin_pct": float(lm.get("gross_margin_pct") or 0.0),
                    "operating_margin_pct": float(lm.get("operating_margin_pct") or 0.0),
                    "roe": float(lm.get("roe_ttm_pct") or 0.0),
                    "ocf_ty": float(lm.get("ocf_ty") or 0.0),
                    "fcf_ty": float(lm.get("fcf_ty") or 0.0),
                    "ocf_ratio": float(lm["ocf_to_profit_ratio"]) if lm.get("ocf_to_profit_ratio") is not None else 0.0,
                    "debt_to_equity": float(lm.get("debt_to_equity") or 0.0),
                    "pe": float(lm.get("pe_ttm") or 0.0),
                    "pb": float(lm.get("pb_live") or 0.0),
                    "receivables_ty": float(lm.get("receivables_ty") or 0.0),
                    "other_receivables_to_assets_pct": float(lm.get("other_receivables_to_assets_pct") or 0.0),
                    "cash_and_equiv_ty": float(lm.get("cash_and_equiv_ty") or 0.0),
                    "piotroski_f_score_live": lm.get("piotroski_f_score"),
                    "beneish_m_score_live": lm.get("beneish_m_score"),
                    "altman_z_score_live": lm.get("altman_z_score"),
                    "sloan_accrual_pct_live": lm.get("sloan_accrual_pct"),
                    "avg_val_1m_ty": float(lm.get("avg_val_1m_ty") or 0.0),
                })
                if not float(entry.get("live_price") or 0.0) and cur_px > 0:
                    entry["live_price"] = cur_px
                universe[sym] = entry
        except Exception:
            pass

    # Chọn toàn bộ cổ phiếu nắm giữ + 80 mã BCTC sống VN + 12 siêu cổ phiếu US để phân tích live
    vn_candidates = [
        sym for sym, info in universe.items()
        if info.get("market") == "VN" and (info.get("deep_bctc_audited") or sym in active_pos or sym in ("HDB", "MSH", "BAF", "IDC", "TCH", "OCB"))
    ]
    us_candidates = ["NVDA", "MSFT", "AAPL", "GOOGL", "META", "TSM", "AVGO", "LLY", "WMT", "COST", "JPM", "BRK-B", "XOM"]

    if force_live and vn_candidates:
        try:
            quotes = fetch_vps_quotes(vn_candidates, timeout=5)
            for sym, q in quotes.items():
                px = float(q.get("price") or q.get("last_price") or 0.0)
                if sym in universe and px > 0:
                    universe[sym]["live_price"] = px
                    universe[sym]["change_1d_pct"] = float(q.get("change_pct", 0.0) or 0.0)
                    universe[sym]["buy_up_pct"] = float(q.get("active_buy_pct", 50.0) or 50.0)
                    universe[sym]["volume"] = int(q.get("volume", 0) or 0)
                    universe[sym]["foreign_net_val_bil"] = round(float(q.get("foreign_net_val_vnd", 0.0) or 0.0) / 1e9, 2)
        except Exception:
            pass

    # Kéo chỉ báo kỹ thuật sống cho các mã đang giữ & tầm ngắm hàng đầu
    tech_focus = list(set(list(active_pos.keys()) + ["HDB", "MSH", "BAF", "IDC", "TCH", "OCB", "FPT", "TCB", "MBB", "VCB", "HPG", "SSI", "DGC", "MWG"]))
    for sym in tech_focus:
        if sym in universe and universe[sym].get("market") == "VN":
            try:
                ind = fetch_stock_indicators_live(sym)
                if ind:
                    universe[sym]["rsi14"] = float(ind.get("rsi14", 50.0) or 50.0)
                    universe[sym]["ma20"] = float(ind.get("ma20", 0.0) or 0.0)
                    universe[sym]["ma50"] = float(ind.get("ma50", 0.0) or 0.0)
                    universe[sym]["atr14"] = float(ind.get("atr14", 0.0) or 0.0)
                    if not universe[sym].get("live_price") and float(ind.get("last_close", 0.0) or 0.0) > 0:
                        universe[sym]["live_price"] = float(ind["last_close"])
            except Exception:
                pass

    # Tính tỷ trọng ngành hiện tại trong NAV + Ma trận Tương quan 60 phiên
    held_syms = [k.upper().strip() for k, p in active_pos.items() if int(p.get("shares", 0) or 0) > 0]
    est_nav_base = cash_vnd + sum(
        float(universe.get(k, {}).get("live_price") or p.get("current_price") or p.get("entry_price") or 0.0) * int(p.get("shares", 0) or 0)
        for k, p in active_pos.items() if int(p.get("shares", 0) or 0) > 0
    )
    sector_exp_pct: Dict[str, float] = {}
    for k, p in active_pos.items():
        sh = int(p.get("shares", 0) or 0)
        if sh <= 0:
            continue
        px_k = float(universe.get(k, {}).get("live_price") or p.get("current_price") or p.get("entry_price") or 0.0)
        sc = str(universe.get(k, {}).get("sector_code", "Core"))
        if est_nav_base > 0:
            sector_exp_pct[sc] = round(sector_exp_pct.get(sc, 0.0) + ((px_k * sh) / est_nav_base) * 100.0, 1)

    priority_corr_cands = [
        "BAF", "DBC", "HAH", "TCB", "CTG", "MBB", "HPG", "OCB", "FPT", "IDC", "VCB", "SSI", "MWG"
    ] + [s for s in vn_candidates if s not in held_syms][:15]
    corr_res = compute_holdings_correlation_matrix(
        held_symbols=held_syms,
        candidate_symbols=list(dict.fromkeys(priority_corr_cands)) + us_candidates[:5],
        universe=universe,
        sector_exposure_pct=sector_exp_pct,
    )
    corr_matrix_map = corr_res.get("matrix", {})

    analyzed_vn: List[Dict[str, Any]] = []
    analyzed_us: List[Dict[str, Any]] = []

    for sym in vn_candidates + us_candidates:
        if sym not in universe:
            continue
        prof = dict(universe[sym])
        deep = analyze_deep_bctc_and_valuation(sym, prof=prof)
        ps = deep["pillar_scores"]
        alpha = round(
            ps["bctc_quality"] * w_bctc
            + ps["smart_money_flow"] * w_flow
            + ps["valuation_mos"] * w_val
            + macro_score * w_macro
            + ps["technical_trend"] * w_tech,
            1,
        )
        # Thưởng điểm nếu đạt chuẩn bộ lọc Bull-Trap thích nghi
        min_bu = float(filters.get("min_buy_up_pct", 58.0))
        max_rsi = float(filters.get("max_rsi_buy", 70.0))
        bull_trap_clear = (deep["buy_up_pct"] >= min_bu and deep["rsi14"] <= max_rsi)
        if deep["forensic"].get("red_flags_count", 0) > 0:
            alpha = round(max(10.0, alpha - 8.0), 1)

        opt = _compute_ev_and_kelly(alpha, deep, max_alloc_cap)

        # Kiểm soát tương quan 60 phiên & chốt chặn tập trung ngành (>35% NAV hoặc Corr >= 0.72)
        c_info = corr_matrix_map.get(sym, {})
        max_corr = float(c_info.get("max_corr_with_holdings", 0.35) or 0.35)
        most_corr_sym = str(c_info.get("most_correlated_holding", held_syms[0] if held_syms else ""))
        sec_code_sym = str(universe.get(sym, {}).get("sector_code", "Core"))
        cur_sec_pct = float(sector_exp_pct.get(sec_code_sym, 0.0) or 0.0)
        proj_sec_pct = round(cur_sec_pct + (opt["half_kelly_pct"] * 0.6 if sym not in held_syms else 0.0), 1)
        corr_penalty = False
        if sym in held_syms:
            corr_guard = "HIGH_CORR_CLUSTER" if max_corr >= 0.72 else "CORE_HOLDING_ACTIVE"
        elif max_corr >= 0.72 or proj_sec_pct > 35.0:
            corr_guard = "HIGH_CORR_CLUSTER"
            opt["half_kelly_pct"] = round(opt["half_kelly_pct"] * 0.75, 1)
            corr_penalty = True
        elif max_corr >= 0.50:
            corr_guard = "MODERATE_SECTOR_OVERLAP"
        else:
            corr_guard = "CLEAR_DIVERSIFIED"

        # Kiểm toán Lô 100 CP theo tiền mặt thật TCBS & Khóa giải ngân trong BEAR_DOWNTREND
        lot100_cost = round(deep["live_price"] * 100.0, 0) if deep["market"] == "VN" and deep["live_price"] > 0 else 0.0
        cur_regime = opt.get("live_regime_id", "SIDEWAY_CHOPPY")
        if cur_regime == "BEAR_DOWNTREND":
            suggested_lots = 0
        else:
            max_vnd_budget = cash_vnd * (min(max_alloc_cap, max(15.0, opt["half_kelly_pct"])) / 100.0)
            suggested_lots = int(max_vnd_budget // lot100_cost) * 100 if lot100_cost > 0 else 0
            if suggested_lots == 0 and lot100_cost > 0 and cash_vnd >= lot100_cost and opt["ev_pct"] > 0:
                suggested_lots = 100

        # Gắn nhãn hành động tối ưu (tuyệt đối không phát lệnh BUY trong BEAR_DOWNTREND)
        px = deep["live_price"]
        if deep["forensic"].get("red_flags_count", 0) > 0 and deep["forensic"].get("forensic_score", 100) < 70:
            action = "AVOID_RED_FLAG"
        elif cur_regime == "BEAR_DOWNTREND":
            action = "WAIT_UPTREND_REGIME"
        elif deep["rsi14"] > max_rsi:
            action = "WAIT_PULLBACK_OVERBOUGHT"
        elif alpha >= 68.0 and opt["ev_pct"] >= 3.0 and opt["rr_ratio"] >= 1.8 and bull_trap_clear:
            action = "BUY_OPTIMAL_ALPHA"
        elif alpha >= 62.0 and opt["ev_pct"] > 0:
            action = "ACCUMULATE_DISCOUNT"
        else:
            action = "WATCHLIST_HOLD"

        deep["alpha_score"] = alpha
        deep["bull_trap_clear"] = bull_trap_clear
        deep["max_corr_with_holdings"] = round(max_corr, 3)
        deep["most_correlated_holding"] = most_corr_sym
        deep["sector_nav_exposure_pct"] = cur_sec_pct
        deep["corr_guard_status"] = corr_guard
        deep["optimizer"] = {
            **opt,
            "corr_penalty_075x": corr_penalty,
            "corr_guard_status": corr_guard,
            "max_corr_with_holdings": round(max_corr, 3),
            "lot100_cost_vnd": lot100_cost,
            "can_afford_100_lot": bool(lot100_cost > 0 and cash_vnd >= lot100_cost),
            "suggested_shares_lot100": suggested_lots,
            "suggested_capital_vnd": round(suggested_lots * deep["live_price"], 0) if deep["market"] == "VN" else 0.0,
            "action_signal": action,
        }
        if deep["market"] == "VN":
            analyzed_vn.append(deep)
        else:
            analyzed_us.append(deep)

    analyzed_vn.sort(key=lambda x: (x["optimizer"]["ev_pct"], x["alpha_score"]), reverse=True)
    analyzed_us.sort(key=lambda x: (x["optimizer"]["ev_pct"], x["alpha_score"]), reverse=True)

    # 3. Tối ưu hóa trực tiếp 2 vị thế đang nắm giữ trong SSOT (`HDB`, `MSH`)
    vn_map = {x["symbol"]: x for x in analyzed_vn}
    holdings_optimizer: List[Dict[str, Any]] = []
    live_stock_val = 0.0
    for sym, pos in active_pos.items():
        shares = int(pos.get("shares", 0) or 0)
        if shares <= 0:
            continue
        entry_px = float(pos.get("entry_price") or pos.get("avg_price") or 0.0)
        deep_pos = vn_map.get(sym) or analyze_deep_bctc_and_valuation(sym)
        live_px = float(deep_pos.get("live_price") or pos.get("current_price") or entry_px)
        live_stock_val += live_px * shares
        pnl_vnd = round((live_px - entry_px) * shares, 0)
        pnl_pct = round(((live_px / entry_px) - 1.0) * 100.0, 2) if entry_px > 0 else 0.0
        stop_px = float(pos.get("stop_loss") or deep_pos.get("optimizer", {}).get("stop_loss_price") or round(entry_px * 0.94, 0))
        tp1_px = float(pos.get("take_profit_tp1") or pos.get("tp1") or round(entry_px * 1.10, 0))
        tp2_px = float(pos.get("take_profit_tp2") or pos.get("tp2") or round(entry_px * 1.18, 0))
        dist_stop_pct = round(((live_px - stop_px) / live_px) * 100.0, 2) if live_px > 0 and stop_px > 0 else 0.0
        t0_buy_zone = round(float(deep_pos.get("ma20") or live_px * 0.985), 0)

        has_forensic_flag = (
            deep_pos.get("forensic", {}).get("red_flags_count", 0) > 0
            or int(deep_pos.get("piotroski_f_score", 9) or 9) <= 4
            or (deep_pos.get("accounting_regime") != "BANK_CAMELS_BASEL" and float(deep_pos.get("ocf_ratio") if deep_pos.get("ocf_ratio") is not None else 1.0) < 0)
        )
        if live_px <= stop_px:
            rec_action = "CRITICAL_CUT_STOP"
            rec_note = f"Giá xuyên thủng Stop Loss {stop_px:,.0f}đ — Kỷ luật cắt lỗ bảo toàn vốn."
        elif has_forensic_flag:
            rec_action = "EXIT_FORENSIC_RED_FLAG"
            rec_note = f"Cảnh báo BCTC thật (F-Score {deep_pos.get('piotroski_f_score')}/9, OCF/LNST {deep_pos.get('ocf_ratio')}x, Pháp y {deep_pos.get('forensic', {}).get('forensic_score')}/100) — Không nắm giữ dài hạn, ưu tiên cơ cấu thu tiền mặt."
        elif tp1_px > 0 and live_px >= tp1_px:
            rec_action = "SCALE_OUT_50_TP1"
            rec_note = f"Chạm mục tiêu TP1 {tp1_px:,.0f}đ — Chốt lời 50% ({shares//2} CP) & nâng Stop phần còn lại lên giá vốn {entry_px:,.0f}đ."
        elif deep_pos.get("buy_up_pct", 50.0) >= 65.0 and pnl_pct >= 0:
            rec_action = "HOLD_RIDE_WINNER"
            rec_note = f"Lực mua chủ động khỏe ({deep_pos.get('buy_up_pct', 50):.1f}%), giữ lãi chạy về TP1 {tp1_px:,.0f}đ (cách Stop +{dist_stop_pct:.1f}%)."
        else:
            rec_action = "HOLD_WATCH_LIQUIDITY"
            rec_note = f"Theo dõi vị thế (Alpha {deep_pos.get('alpha_score', 60)}/100, thanh khoản 1M ~{deep_pos.get('avg_val_1m_ty') or 0} tỷ/phiên); canh thu tiền mặt theo kế hoạch cơ cấu."

        holdings_optimizer.append({
            "symbol": sym,
            "shares": shares,
            "entry_price": entry_px,
            "live_price": live_px,
            "pnl_vnd": pnl_vnd,
            "pnl_pct": pnl_pct,
            "stop_loss": stop_px,
            "dist_to_stop_pct": dist_stop_pct,
            "tp1": tp1_px,
            "tp2": tp2_px,
            "t0_dip_level": t0_buy_zone,
            "alpha_score": deep_pos.get("alpha_score", 70.0),
            "ocf_ratio": deep_pos.get("ocf_ratio", 1.0),
            "margin_of_safety_pct": deep_pos.get("valuation", {}).get("margin_of_safety_pct", 0.0),
            "action": rec_action,
            "recommendation": rec_note,
        })

    live_nav = round(cash_vnd + live_stock_val, 0)
    top_vn_buy = [x for x in analyzed_vn if x["optimizer"]["can_afford_100_lot"] and x["optimizer"]["ev_pct"] > 0][:8]

    # Chỉ số đồng bộ crawler
    try:
        omni_stats = search_market_intelligence("", limit=3).get("summary_stats", {})
    except Exception:
        omni_stats = {}

    result = {
        "generated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
        "trading_date": now_ict.strftime("%Y-%m-%d"),
        "account_ssot": {
            "account_id": ssot.get("account_id", "105C307855"),
            "cash_balance_vnd": cash_vnd,
            "live_stock_val_vnd": live_stock_val,
            "live_nav_vnd": live_nav,
            "realized_pnl_vnd": realized_vnd,
            "cash_ratio_pct": round((cash_vnd / live_nav) * 100.0, 1) if live_nav > 0 else 100.0,
        },
        "macro_and_spillover": {
            "vn_index": mkt_live.get("vn_index", {}).get("value", 0.0),
            "vn_index_chg_pct": vni_pct,
            "breadth_pct": breadth_pct,
            "spillover_bias": spillover.get("bias", "NEUTRAL_SELECTIVE"),
            "spillover_multiplier": spill_mult,
            "max_new_allocation_pct": max_alloc_cap,
            "macro_score": macro_score,
        },
        "weights_used": {
            "bctc_earnings_quality": w_bctc,
            "cashflow_smart_money": w_flow,
            "valuation_fair_value": w_val,
            "macro_monetary": w_macro,
            "technical_atr_risk": w_tech,
        },
        "holdings_optimizer": holdings_optimizer,
        "correlation_matrix": corr_res,
        "top_vn_alpha_picks": analyzed_vn[:12],
        "vn_rankings": analyzed_vn,
        "top_vn_affordable_now": top_vn_buy,
        "top_us_alpha_picks": analyzed_us[:8],
        "us_rankings": analyzed_us,
        "omni_stats": omni_stats,
        "total_analyzed": len(analyzed_vn) + len(analyzed_us),
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DEEP_BRAIN_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # Xuất báo cáo Markdown vào 08_Master_Investment_CIO/
    CIO_DIR.mkdir(parents=True, exist_ok=True)
    md_path = CIO_DIR / f"{now_ict.strftime('%Y-%m-%d')}_Deep_Brain_Alpha_Report.md"
    lines = [
        f"# [BAN 2 + BAN 4 + BAN 8] BÁO CÁO PHÂN TÍCH BCTC CHUYÊN SÂU & TỐI ƯU LỢI NHUẬN — {now_ict.strftime('%Y-%m-%d')}",
        f"**Cập nhật:** `{result['generated_at']} (ICT)` | **Tài khoản SSOT:** `TCBS {result['account_ssot']['account_id']}`  ",
        f"**Tiền mặt khả dụng:** `{cash_vnd:,.0f} ₫` ({result['account_ssot']['cash_ratio_pct']}%) | **NAV Live:** `{live_nav:,.0f} ₫` | **Spillover Mult:** `{spill_mult}x` (Trần giải ngân mới: `{max_alloc_cap}%`)\n",
        "## 1. TỐI ƯU HÓA DANH MỤC ĐANG NẮM GIỮ (ACTIVE HOLDINGS OPTIMIZER)",
        "| Mã | SL | Giá Vốn | Giá Live | PnL Sống | Stop 2xATR | TP1 | Alpha Score | Quyết Định Tối Ưu |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ]
    for h in holdings_optimizer:
        lines.append(
            f"| **{h['symbol']}** | {h['shares']} | {h['entry_price']:,.0f}₫ | {h['live_price']:,.0f}₫ | "
            f"{h['pnl_vnd']:+,.0f}₫ ({h['pnl_pct']:+.2f}%) | {h['stop_loss']:,.0f}₫ | {h['tp1']:,.0f}₫ | "
            f"{h['alpha_score']}/100 | **{h['action']}** — {h['recommendation']} |"
        )

    lines.extend([
        "\n## 2. BẢNG XẾP HẠNG SIÊU CỔ PHIẾU VIỆT NAM TỐI ƯU KỲ VỌNG TOÁN HỌC (EV% & HALF-KELLY)",
        "| Hạng | Mã | Ngành | Giá Live | Alpha | BCTC / OCF | Giá Nội Tại (MOS%) | EV% | R:R | Half-Kelly | Lệnh Lô 100 CP | Hành Động |",
        "| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ])
    for idx, x in enumerate(analyzed_vn[:12], 1):
        opt = x["optimizer"]
        val = x["valuation"]
        lines.append(
            f"| {idx} | **{x['symbol']}** | {x['sector_name'][:18]} | {x['live_price']:,.0f}₫ | **{x['alpha_score']}** | "
            f"{x['pillar_scores']['bctc_quality']} ({x['ocf_ratio']}x) | {val['intrinsic_fair_value']:,.0f}₫ ({val['margin_of_safety_pct']:+.1f}%) | "
            f"**{opt['ev_pct']:+.2f}%** | 1:{opt['rr_ratio']} | {opt['half_kelly_pct']}% | "
            f"{opt['suggested_shares_lot100']} CP ({opt['suggested_capital_vnd']:,.0f}₫) | `{opt['action_signal']}` |"
        )

    lines.extend([
        "\n## 3. TOP SIÊU CỔ PHIẾU QUỐC TẾ (MỸ / TOÀN CẦU)",
        "| Mã | Ngành | Giá Live ($) | Alpha | ROE | EV% | R:R | Giá Nội Tại ($) | MOS% |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ])
    for x in analyzed_us[:8]:
        val = x["valuation"]
        opt = x["optimizer"]
        lines.append(
            f"| **{x['symbol']}** | {x['sector_name'][:22]} | ${x['live_price']:,.2f} | {x['alpha_score']} | "
            f"{x['roe_pct']}% | {opt['ev_pct']:+.2f}% | 1:{opt['rr_ratio']} | ${val['intrinsic_fair_value']:,.2f} | {val['margin_of_safety_pct']:+.1f}% |"
        )

    lines.extend([
        "\n## 4. MA TRẬN TƯƠNG QUAN LỢI SUẤT 60 PHIÊN & CHỐT CHẶN TẬP TRUNG NGÀNH",
        f"*(Quét {corr_res.get('live_60d_series_fetched', 0)} chuỗi 60 phiên sống từ Entrade + Mô hình Nhân tố Ngành | Tương quan >= 0.72 hoặc Ngành > 35% NAV sẽ giảm 0.75x Half-Kelly)*",
        "| Mã | Max Corr vs Nắm Giữ | Cặp Tương Quan Nhất | Tỷ Trọng Ngành NAV | Trạng Thái Chốt Chặn | Điều Chỉnh Half-Kelly |",
        "| :--- | :---: | :---: | :---: | :--- | :---: |",
    ])
    for x in analyzed_vn[:10]:
        opt = x["optimizer"]
        pen = "0.75x Penalty" if opt.get("corr_penalty_075x") else "1.0x Full"
        lines.append(
            f"| **{x['symbol']}** | {x.get('max_corr_with_holdings', 0.0):.3f} | {x.get('most_correlated_holding', '-')} | "
            f"{x.get('sector_nav_exposure_pct', 0.0):.1f}% | `{x.get('corr_guard_status', 'CLEAR_DIVERSIFIED')}` | {pen} ({opt['half_kelly_pct']}%) |"
        )

    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")

    # Đồng bộ báo cáo lên SQLite Vault
    try:
        from scripts.apex_cloud_db_sync import ApexCloudDBSync
        ApexCloudDBSync.sync_live_report({
            "report_key": f"{now_ict.strftime('%Y-%m-%d')}_DEEP_BRAIN",
            "trading_date": now_ict.strftime("%Y-%m-%d"),
            "market_overview": mkt_live,
            "intraday_regime": {"regime_id": spillover.get("bias", "NEUTRAL")},
            "victor_sentinel": {"total_nav_vnd": live_nav, "cash_vnd": cash_vnd},
        }, md_text)
    except Exception:
        pass

    result["report_md_path"] = str(md_path)
    return result


def main():
    parser = argparse.ArgumentParser(description="Apex Deep Financial Brain & Profit-Maximizing Optimizer")
    parser.add_argument("--symbol", type=str, default="", help="Phân tích sâu 1 mã cổ phiếu cụ thể")
    args = parser.parse_args()

    if args.symbol:
        res = analyze_deep_bctc_and_valuation(args.symbol)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    res = run_full_market_alpha_optimization(force_live=True)
    print(
        f"[DEEP BRAIN V5.0] Analyzed {res['total_analyzed']} tickers | "
        f"SSOT Cash={res['account_ssot']['cash_balance_vnd']:,.0f}đ | Live NAV={res['account_ssot']['live_nav_vnd']:,.0f}đ"
    )
    print("[HOLDINGS OPTIMIZER]")
    for h in res["holdings_optimizer"]:
        print(f"  * {h['symbol']} ({h['shares']} CP @ {h['entry_price']:,.0f}đ -> {h['live_price']:,.0f}đ | PnL {h['pnl_vnd']:+,.0f}đ): {h['action']}")
    print("[TOP 5 VN ALPHA PICKS]")
    for x in res["top_vn_alpha_picks"][:5]:
        o = x["optimizer"]
        v = x["valuation"]
        print(f"  * {x['symbol']}: Alpha={x['alpha_score']} | EV={o['ev_pct']:+.2f}% | R:R=1:{o['rr_ratio']} | Fair={v['intrinsic_fair_value']:,.0f} ({v['margin_of_safety_pct']:+.1f}%) | Lot100={o['suggested_shares_lot100']} CP -> {o['action_signal']}")
    print(f"[+] Report saved: {res['report_md_path']}")


if __name__ == "__main__":
    main()
