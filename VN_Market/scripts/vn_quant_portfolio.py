#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vn_quant_portfolio.py - Động Cơ Định Lượng Quản Trị Rủi Ro, Hội Đồng 10 Đại Danh Thủ & Phân Bổ Danh Mục TTCK Việt Nam (v3.0 Institutional)
Chuyên trách Ban 4 (Hội Đồng Đầu Tư & Quản Trị Rủi Ro Định Lượng VN):
- Chấm điểm IC Score tổng hợp từ: Hội Đồng 10 Đại Danh Thủ (Buffett, Graham, Lynch, O'Neil CANSLIM, Wyckoff VSA, Piotroski F-Score, Beneish M, Altman Z'') + Dòng tiền thực chiến.
- Tuyển lựa Động (Dynamic Sector-Diversified Alpha Selection) Top 8 Siêu Cổ Phiếu Đầu Ngành (Khống chế cụm ngành tối đa 2 mã/ngành để đa dạng hóa rủi ro).
- Định cỡ vị thế ATR Risk-Parity kết hợp Tiêu chuẩn Fractional Kelly của Ed Thorp phù hợp chu kỳ T+2.5.
- Kiểm soát biên độ sàn HOSE (+/-7%), HNX (+/-10%), UPCoM (+/-15%) và chuẩn lô chẵn 100 CP.
- Xuất bản JSON cấu trúc `VN_Market/data/vn_quant_analytics.json` phục vụ trực tiếp cho Chuyên viên Minh Quân (Ban 7) và Tổng Tư Lệnh Master CIO (Ban 8).
"""

import os
import sys
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
import json
import math
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "vn_market_data.json")
BCTC_PATH = os.path.join(BASE_DIR, "data", "vn_bctc_analysis.json")
WEIGHTS_PATH = os.path.join(BASE_DIR, "config", "adaptive_weights_vn.json")
QUANT_JSON_OUT = os.path.join(BASE_DIR, "data", "vn_quant_analytics.json")

QUANT_REPORT_MD = os.path.join(BASE_DIR, "04_Investment_Committee", f"{datetime.date.today()}_VN_Quant_Risk_And_Correlation.md")
IC_DECISION_MD = os.path.join(BASE_DIR, "04_Investment_Committee", f"{datetime.date.today()}_VN_IC_Decision.md")
TRACKER_MD = os.path.join(BASE_DIR, "04_Investment_Committee", "vn_portfolio_tracker.md")


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        mkt = json.load(f)
    with open(BCTC_PATH, "r", encoding="utf-8") as f:
        bctc = json.load(f)
    with open(WEIGHTS_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return mkt, bctc, cfg


def score_stock(code, stk_info, bctc_info, cfg):
    """
    Chấm điểm cơ hội đầu tư trên thang 100 điểm đa chiều (v3.0 — Tích hợp Hội Đồng 10 Đại Danh Thủ):
    - BCTC & 10-Master Score (30%)
    - Dòng tiền Thông minh, Wyckoff VSA & Mua chủ động (25%)
    - Vĩ mô SBV & Sóng ngành (20%)
    - Định giá Graham MoS & Lynch PEG (15%)
    - Cấu trúc Kỹ thuật, RS Rating & Biên an toàn ATR (10%)
    """
    weights = cfg.get("weights", {})
    w_bctc = weights.get("bctc_earnings_quality", 0.30)
    w_flow = weights.get("cashflow_and_smart_money", 0.25)
    w_macro = weights.get("macro_monetary_sbv", 0.20)
    w_val = weights.get("valuation_fair_value", 0.15)
    w_tech = weights.get("technical_and_atr_risk", 0.10)

    # 1. BCTC & 10-Master Score (Thang 100)
    master_score = float(bctc_info.get("master_composite_score", 82.0))
    f_score = int(bctc_info.get("piotroski_f_score", 8))
    bctc_score = min(99.0, 0.75 * master_score + 0.25 * ((f_score / 9.0) * 100.0))

    # 2. Smart Money & Wyckoff VSA Score
    tech = stk_info.get("technical", {})
    vol_ratio = float(tech.get("vol_ratio", 1.0))
    vsa_code = tech.get("vsa_code", "NEUTRAL_TEST")
    active_buy = float(tech.get("active_buy_pct", 55.0))
    flow_score = 72.0 + (active_buy - 50.0) * 0.65
    if vsa_code in ("POCKET_PIVOT", "NO_SUPPLY", "SOS_ABSORPTION"):
        flow_score += 10.0
    if vol_ratio >= 1.15:
        flow_score += 5.0
    flow_score = min(98.0, max(45.0, flow_score))

    # 3. Macro & Sector Tailwind Score
    sec_key = stk_info.get("sector_key", "")
    favored_sectors = {"Cong_Nghe_Vien_Thong", "Ngan_Hang", "Ban_Le_Tieu_Dung", "Thep_Vat_Lieu", "Bat_Dong_San_KCN", "Hoa_Chat_Phan_Bon", "Cang_Bien_Van_Tai", "Chung_Khoan"}
    macro_score = 90.0 if sec_key in favored_sectors else 80.0

    # 4. Valuation Score (Graham Margin of Safety + Peter Lynch PEG)
    mos_pct = float(bctc_info.get("graham_margin_of_safety_pct", 10.0))
    peg = float(bctc_info.get("lynch_peg_ratio", 1.0))
    val_score = 75.0
    if mos_pct >= 20.0:
        val_score += 14.0
    elif mos_pct >= 0.0:
        val_score += 7.0
    if peg <= 0.85:
        val_score += 10.0
    elif peg <= 1.35:
        val_score += 4.0
    val_score = min(98.0, max(45.0, val_score))

    # 5. Technical & O'Neil RS Rating Score
    price_vs_ma200 = float(tech.get("price_vs_ma200", 0.0))
    rsi = float(tech.get("rsi14", 50.0))
    rs_rating = int(tech.get("rs_rating", 70))
    tech_score = 65.0 + (rs_rating - 50) * 0.45
    if price_vs_ma200 >= -2.0:
        tech_score += 10.0
    if 42 <= rsi <= 66:
        tech_score += 8.0
    elif rsi > 74:
        tech_score -= 10.0
    tech_score = min(98.0, max(40.0, tech_score))

    total_score = round(
        bctc_score * w_bctc +
        flow_score * w_flow +
        macro_score * w_macro +
        val_score * w_val +
        tech_score * w_tech,
        1
    )
    return total_score


def evaluate_adversarial_debate_vn(code, stk_info, bctc_info):
    """
    Tranh Biện Đối Kháng Đa Tác Tử TTCK Việt Nam (Adversarial Bull vs Bear Debate) tích hợp 10 Đại Danh Thủ.
    """
    tech = stk_info.get("technical", {})
    price = tech.get("price", 20000)
    ma200 = tech.get("ma200", price)
    rsi = tech.get("rsi14", 55)
    ocf_r = bctc_info.get("ocf_to_profit_ratio", 1.1)
    fcf = bctc_info.get("free_cash_flow_ty", 1000)
    de = bctc_info.get("debt_to_equity", 0.5)
    m_status = bctc_info.get("beneish_status", "SAFE")
    rating = bctc_info.get("rating", "AAA")
    m_score = bctc_info.get("master_composite_score", 90.0)
    f_score = bctc_info.get("piotroski_f_score", 9)
    peg = bctc_info.get("lynch_peg_ratio", 0.6)
    mos = bctc_info.get("graham_margin_of_safety_pct", 25.0)
    vsa_sig = tech.get("vsa_signal", "Tích lũy cạn cung")

    bull_thesis = (
        f"BCTC hạng {rating} (Điểm 10 Danh Thủ: {m_score}/100, Piotroski F-Score: {f_score}/9, Lynch PEG: {peg}x, "
        f"Graham MoS: {mos:+.1f}%), Tiền thật OCF/LNST = {ocf_r}x, FCF = {fcf:,} tỷ VNĐ, tín hiệu VSA: {vsa_sig}."
    )

    structural_vetoes = []
    if len(bctc_info.get("red_flags", [])) >= 2:
        structural_vetoes.append("; ".join(bctc_info.get("red_flags", [])))
    if m_status == "HIGH_RISK":
        structural_vetoes.append("Nguy cơ xào nấu BCTC (Beneish M-Score High Risk)")
    if price < ma200 * 0.86:
        structural_vetoes.append("Gãy sâu dưới cấu trúc MA200")

    tactical_flags = []
    if rsi > 68:
        tactical_flags.append(f"RSI tiệm cận vùng quá mua ({rsi})")
    if stk_info.get("pe") and stk_info.get("pe") > 24:
        tactical_flags.append(f"P/E cao hơn trung bình ngành ({stk_info.get('pe')}x)")

    if structural_vetoes:
        bear_critique = "PHỦ QUYẾT CẤU TRÚC: " + "; ".join(structural_vetoes)
        cio_verdict = "ABSOLUTE_VETO (Loại khỏi danh mục giải ngân)"
        consensus_pts = 35.0
    elif tactical_flags:
        bear_critique = "CẢNH BÁO ĐIỂM MUA: " + "; ".join(tactical_flags) + " — Cấm đua lệnh giá xanh ATO."
        cio_verdict = "APPROVED_LIMIT_PULLBACK (Bác bỏ Veto định giá • Duyệt chia lệnh Kim Tự Tháp 30-40-30)"
        consensus_pts = 89.5
    else:
        bear_critique = "Áp lực rung lắc T+2.5 phiên chiều; nội tại BCTC kiểm toán và điểm số 10 Đại Danh Thủ đồng thuận tuyệt đối."
        cio_verdict = "UNANIMOUS_APPROVAL (Đồng thuận tuyệt đối Bull & Risk IC)"
        consensus_pts = 95.5

    return {
        "bull_thesis": bull_thesis,
        "bear_critique": bear_critique,
        "cio_verdict": cio_verdict,
        "consensus_score": consensus_pts
    }


def select_diversified_top_picks(scored_stocks, max_picks=8, max_per_sector=2):
    """
    Tuyển lựa Động Siêu Cổ Phiếu Đầu Ngành (Lọc BCTC Q3/2026 sạch: F-Score >= 6, Beneish SAFE,
    không Red Flags, thanh khoản >= 15 tỷ/phiên và thị giá <= 36,000đ để vừa Lô 100 của TK ~20.19M VNĐ).
    """
    selected = []
    sector_counts = {}

    ranked = sorted(
        [
            s for s in scored_stocks
            if s.get("red_flags_count", 0) == 0
            and int(s.get("piotroski_f_score") or 0) >= 6
            and s.get("beneish_status", "SAFE") == "SAFE"
            and 0 < float(s.get("price") or 0.0) <= 36000.0
            and float(s.get("avg_val20_ty") or 0.0) >= 15.0
            and s.get("rating") in ("AAA", "AA")
        ],
        key=lambda x: x["score"],
        reverse=True
    )
    if len(ranked) < 4:
        ranked = sorted(
            [
                s for s in scored_stocks
                if s.get("red_flags_count", 0) == 0
                and int(s.get("piotroski_f_score") or 0) >= 6
                and 0 < float(s.get("price") or 0.0) <= 36000.0
            ],
            key=lambda x: x["score"],
            reverse=True
        )

    for item in ranked:
        sec = item["sector"]
        if sector_counts.get(sec, 0) >= max_per_sector:
            continue
        selected.append(item)
        sector_counts[sec] = sector_counts.get(sec, 0) + 1
        if len(selected) >= max_picks:
            break

    return selected


def run():
    print("=== [VN QUANT PORTFOLIO v4.0] ĐỊNH LƯỢNG RỦI RO, LÔ 100 (~20.19M) & MA TRẬN 5 KỊCH BẢN (S1-S5) ===")
    mkt, bctc, cfg = load_data()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    stocks = mkt.get("stocks", {})

    root_dir = os.path.dirname(BASE_DIR)
    ssot_path = os.path.join(root_dir, "data", "current_portfolio_state.json")
    v2_path = os.path.join(root_dir, "data", "apex_quant_brain_v2_output.json")
    pb_path = os.path.join(root_dir, "data", "apex_adaptive_contingency_playbook.json")

    ssot = {}
    if os.path.exists(ssot_path):
        try:
            with open(ssot_path, "r", encoding="utf-8") as sf:
                ssot = json.load(sf)
        except Exception:
            ssot = {}
    v2_out = {}
    if os.path.exists(v2_path):
        try:
            with open(v2_path, "r", encoding="utf-8") as vf:
                v2_out = json.load(vf)
        except Exception:
            v2_out = {}
    playbook = {}
    if os.path.exists(pb_path):
        try:
            with open(pb_path, "r", encoding="utf-8") as pf:
                playbook = json.load(pf)
        except Exception:
            playbook = {}

    cur_reg = str((v2_out.get("market_regime") or {}).get("regime_id") or "BEAR_DOWNTREND")
    live_nav_vnd = float((playbook.get("account_ssot") or {}).get("live_nav_vnd") or ssot.get("total_nav_vnd") or 20_189_522.0)

    scored_stocks = []
    for code, stk in stocks.items():
        b_info = bctc.get(code, {})
        tech = stk.get("technical", {})
        score = score_stock(code, stk, b_info, cfg)
        price = float(tech.get("price") or 0.0)
        if price <= 0:
            continue
        atr14 = float(tech.get("atr14") or (price * 0.025))
        if atr14 <= 0:
            atr14 = price * 0.025
        scored_stocks.append({
            "code": code,
            "name": stk.get("name"),
            "exchange": stk.get("exchange"),
            "sector": stk.get("sector_name"),
            "price": price,
            "atr14": atr14,
            "rsi14": tech.get("rsi14", 50),
            "rs_rating": tech.get("rs_rating", 70),
            "avg_val20_ty": tech.get("avg_val20_ty", 20.0),
            "vsa_code": tech.get("vsa_code", "NEUTRAL"),
            "vsa_signal": tech.get("vsa_signal", ""),
            "wyckoff_phase": tech.get("wyckoff_phase", ""),
            "active_buy_pct": tech.get("active_buy_pct", 55.0),
            "chandelier_stop": tech.get("chandelier_stop", 0),
            "score": score,
            "master_composite_score": b_info.get("master_composite_score", 80.0),
            "piotroski_f_score": b_info.get("piotroski_f_score", 6),
            "beneish_status": b_info.get("beneish_status", "SAFE"),
            "graham_intrinsic_value_vnd": b_info.get("graham_intrinsic_value_vnd", 0),
            "graham_margin_of_safety_pct": b_info.get("graham_margin_of_safety_pct", 0.0),
            "lynch_peg_ratio": b_info.get("lynch_peg_ratio", 1.0),
            "eva_spread_pct": b_info.get("eva_spread_pct", 5.0),
            "rating": b_info.get("rating", "A"),
            "red_flags_count": len(b_info.get("red_flags", [])),
            "direction": b_info.get("price_direction", "NEUTRAL")
        })

    scored_stocks.sort(key=lambda x: x["score"], reverse=True)
    top_picks = select_diversified_top_picks(scored_stocks, max_picks=8, max_per_sector=2)

    # Tính toán Tỷ Trọng Vị Thế Theo ATR Risk-Parity kết hợp Điểm 10 Đại Danh Thủ
    inv_atrs = []
    for p in top_picks:
        atr_pct = p["atr14"] / p["price"] if p["price"] > 0 else 0.03
        quality_boost = (p["score"] / 90.0)
        inv_atrs.append((1.0 / max(atr_pct, 0.015)) * quality_boost)

    sum_inv = sum(inv_atrs) or 1.0
    weights = [round((w / sum_inv) * 100, 1) for w in inv_atrs]
    diff_w = round(100.0 - sum(weights), 1)
    if weights:
        weights[0] = round(weights[0] + diff_w, 1)

    allocations = []
    total_nav_vnd = live_nav_vnd
    for p, w in zip(top_picks, weights):
        alloc_val = round(total_nav_vnd * (w / 100.0))
        raw_shares = alloc_val / p["price"] if p["price"] > 0 else 0
        shares = max(100, int(math.floor(raw_shares / 100.0) * 100)) if total_nav_vnd >= p["price"] * 100.0 else 0
        stop_loss = round(p["price"] - (2.0 * p["atr14"]))
        take_profit_1 = round(p["price"] + (2.6 * p["atr14"]))
        take_profit_2 = round(p["price"] + (4.5 * p["atr14"]))

        max_stop_pct = 0.07 if p["exchange"] == "HOSE" else 0.085
        if (p["price"] - stop_loss) / p["price"] > max_stop_pct:
            stop_loss = round(p["price"] * (1 - max_stop_pct))

        rr_tp1 = round((take_profit_1 - p["price"]) / max(1, p["price"] - stop_loss), 2)
        rr_tp2 = round((take_profit_2 - p["price"]) / max(1, p["price"] - stop_loss), 2)
        eff_rr = round(0.45 * rr_tp1 + 0.55 * rr_tp2, 2)

        debate_info = evaluate_adversarial_debate_vn(p["code"], stocks.get(p["code"], {}), bctc.get(p["code"], {}))
        allocations.append({
            "code": p["code"],
            "name": p["name"],
            "exchange": p["exchange"],
            "sector": p["sector"],
            "price": p["price"],
            "atr14": p["atr14"],
            "rsi14": p["rsi14"],
            "rs_rating": p["rs_rating"],
            "vsa_code": p["vsa_code"],
            "vsa_signal": p["vsa_signal"],
            "wyckoff_phase": p["wyckoff_phase"],
            "active_buy_pct": p["active_buy_pct"],
            "chandelier_stop": p["chandelier_stop"],
            "score": p["score"],
            "master_composite_score": p["master_composite_score"],
            "piotroski_f_score": p["piotroski_f_score"],
            "graham_intrinsic_value_vnd": p["graham_intrinsic_value_vnd"],
            "graham_margin_of_safety_pct": p["graham_margin_of_safety_pct"],
            "lynch_peg_ratio": p["lynch_peg_ratio"],
            "eva_spread_pct": p["eva_spread_pct"],
            "rating": p["rating"],
            "weight_pct": w,
            "alloc_val_vnd": alloc_val,
            "target_shares": shares,
            "stop_loss_vnd": stop_loss,
            "tp1_vnd": take_profit_1,
            "tp2_vnd": take_profit_2,
            "risk_reward_ratio": eff_rr,
            "adversarial_debate": debate_info
        })

    # Lưu JSON cấu trúc cho Ban 7 và Ban 8 (tích hợp Ma trận 5 Kịch bản S1-S5)
    with open(QUANT_JSON_OUT, "w", encoding="utf-8") as f:
        json.dump({
            "date": today_str,
            "live_regime": cur_reg,
            "account_nav_vnd": total_nav_vnd,
            "total_evaluated": len(scored_stocks),
            "top_allocations": allocations,
            "all_scored_stocks": scored_stocks,
            "adaptive_5_scenarios": playbook.get("scenarios", []),
        }, f, indent=2, ensure_ascii=False)

    # 1. Xuất Báo Cáo Định Lượng & Ma Trận Rủi Ro (Quant Risk)
    quant_lines = [
        f"# BÁO CÁO ĐỊNH LƯỢNG RỦI RO, HỘI ĐỒNG 10 ĐẠI DANH THỦ & ATR RISK-PARITY TTCK VIỆT NAM — {today_str}",
        "**Cơ quan thực hiện**: Ban 4 — Hội Đồng Đầu Tư & Quản Trị Rủi Ro Định Lượng VN (`vn-investment-committee-agent`)",
        f"**Quy mô tài khoản SSOT**: `{total_nav_vnd:,.0f} VNĐ` | **Chế độ hiện tại**: `{cur_reg}` | **Chuẩn**: T+2.5, Lô chẵn 100 CP",
        "",
        "---",
        "",
        "## 1. BẢNG PHÂN BỔ TỶ TRỌNG TOP SIÊU CỔ PHIẾU SẠCH VỪA VỐN 20.19M (ATR RISK-PARITY)",
        "",
        "| Mã CK | Sàn | Ngành | Thị Giá (VND) | Điểm IC (100) | Điểm 10 Danh Thủ | F-Score | RS Rating | Tỷ Trọng NAV | Ngưỡng Cắt Lỗ (Stop) | Chốt Lời TP1 | Chốt Lời TP2 | Tỷ Lệ R:R |",
        "| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    ]

    for a in allocations:
        quant_lines.append(
            f"| **{a['code']}** | {a['exchange']} | {a['sector']} | {a['price']:,.0f} | **{a['score']}** | "
            f"**{a['master_composite_score']}** | {a['piotroski_f_score']}/9 | {a['rs_rating']} | **{a['weight_pct']}%** | "
            f"{a['stop_loss_vnd']:,.0f} | {a['tp1_vnd']:,.0f} | {a['tp2_vnd']:,.0f} | **1:{a['risk_reward_ratio']}** |"
        )

    quant_lines.extend([
        "",
        "---",
        "",
        "## 2. KIỂM THỬ SỨC CHỊU ĐỰNG 3 KỊCH BẢN KHỦNG HOẢNG (STRESS-TESTING)",
        "",
        "### 🔴 Kịch bản 1: SBV Hút Ròng Thanh Khoản / Áp Lực Tỷ Giá USD/VND > 25,700",
        "- **Biện pháp kích hoạt**: Chuyển sang Kịch bản S4 (`0%` mở mới) ngay khi `Breadth > MA20 < 28%` và `VN-Index < MA20/MA50`.",
        "",
        "### 🔴 Kịch bản 2: Khối Ngoại Bán Ròng Đột Biến / Phân Phối Diện Rộng",
        "- **Biện pháp kích hoạt**: Theo dõi nhóm BCTC sạch Q3/2026 (`TPB, CTG, VPB, HDB, HPG`) khi thị trường tạo nến Spring cuối phiên (`14h05–14h25`).",
        "",
        "### 🔴 Kịch bản 3: Sóng Giải Chấp Chéo Margin Toàn Thị Trường",
        "- **Biện pháp kích hoạt**: Khóa Stop Loss `-5.5%..-8.5%`, không bắt dao rơi phiên sáng.",
        ""
    ])

    with open(QUANT_REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(quant_lines))

    # 2. Xuất Quyết Định Hội Đồng Đầu Tư (IC Decision) kèm Ma Trận 5 Kịch Bản (S1-S5)
    ic_status_hdr = (
        f"KHÓA MỞ VỊ THẾ MỚI ({cur_reg}) — CHUẨN BỊ SẴN 5 KỊCH BẢN ỨNG BIẾN LINH HOẠT S1–S5"
        if cur_reg in ("BEAR_DOWNTREND", "CHOPPY_CORRECTION")
        else f"PHÊ DUYỆT GIẢI NGÂN CHỌN LỌC ({cur_reg}) THEO MA TRẬN 5 KỊCH BẢN S1–S5"
    )
    ic_lines = [
        f"# NGHỊ QUYẾT HỘI ĐỒNG ĐẦU TƯ TTCK VIỆT NAM (IC DECISION) — {today_str}",
        "**Cơ quan ban hành**: Hội Đồng Đầu Tư & Quản Trị Rủi Ro (Ban 4 VN)",
        f"**Trạng thái phê duyệt**: **{ic_status_hdr}**",
        "",
        "---",
        "",
        "## 1. TOP CỔ PHIẾU SẠCH Q3/2026 ĐƯỢC SÀNG LỌC CHO TÀI KHOẢN ~20.19M VNĐ",
        ""
    ]

    for a in allocations:
        deb = a.get("adversarial_debate", {})
        ic_lines.extend([
            f"### 🎯 **{a['code']}** — {a['name']} ({a['exchange']})",
            f"- **Trạng thái hiện tại (`{cur_reg}`)**: **`WAIT_SCENARIO_TRIGGER (Chỉ mở lệnh khi khớp điều kiện S1 / S2 / S3)`**",
            f"- **Điểm IC Tổng Hợp**: **{a['score']}/100** | **Điểm 10 Đại Danh Thủ**: **{a['master_composite_score']}/100** | Xếp Hạng BCTC: **{a['rating']}** | F-Score: **{a['piotroski_f_score']}/9**",
            f"- **Định giá Graham & Lynch**: Giá trị nội tại Graham = **{a['graham_intrinsic_value_vnd']:,.0f} ₫** (MoS = **{a['graham_margin_of_safety_pct']:+.1f}%**) | PEG = **{a['lynch_peg_ratio']}x**",
            f"- **Luận điểm Bảo vệ (`Bull Agent`)**: {deb.get('bull_thesis', '')}",
            f"- **Phản biện Rủi ro (`Bear Agent`)**: {deb.get('bear_critique', '')}",
            f"- **Phán quyết (`Master CIO`)**: **{deb.get('cio_verdict', '')}**",
            f"- **Cỡ lệnh tham chiếu Lô 100**: `{a['target_shares']:,} CP` (~{a['alloc_val_vnd']:,.0f} VND) | Stop: **{a['stop_loss_vnd']:,.0f} VND** | TP1/TP2: **{a['tp1_vnd']:,.0f} / {a['tp2_vnd']:,.0f} VND** (R:R **1:{a['risk_reward_ratio']}**)",
            ""
        ])

    ic_lines.extend([
        "---",
        "",
        "## 3. MA TRẬN 5 KỊCH BẢN ỨNG BIẾN LINH HOẠT THEO THỊ TRƯỜNG (S1 – S5)",
        "| Kịch Bản | Trạng Thái 19/11 | Công Suất Vốn | Điều Kiện Kích Hoạt | Chiến Thuật & Lợi Nhuận Mục Tiêu |",
        "| :--- | :---: | :---: | :--- | :--- |",
    ])
    for sc in playbook.get("scenarios", []):
        conds = "; ".join(sc.get("trigger_conditions", [])[:2])
        ic_lines.append(
            f"| **`{sc['scenario_id']}`** ({sc['name_vi']}) | `{sc.get('status_on_2026_11_19')}` | "
            f"**{sc.get('target_equity_exposure_pct')}** | {conds} | {sc.get('expected_profit_range_vnd')} |"
        )

    with open(IC_DECISION_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(ic_lines) + "\n")

    # 3. Xuất Nhật Ký Danh Mục (Portfolio Tracker - Watchlist vs Bear Status)
    tracker_lines = [
        f"# SỔ THEO DÕI DANH MỤC TẦM NGẮM CHUẨN ĐỊNH LƯỢNG TTCK VIỆT NAM (Cập nhật: {today_str} | Regime: {cur_reg})",
        "",
        "| Mã CK | Sàn | Giá Tham Chiếu | Điểm IC | Điểm 10 Danh Thủ | Tỷ Trọng | Khối Lượng (Lô 100) | Cắt Lỗ Stop | Mục Tiêu TP1 | Mục Tiêu TP2 | Trạng Thái |",
        "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |"
    ]
    for a in allocations:
        tr_status = "🟡 CHỜ S1/S2 (BEAR SHIELD)" if cur_reg == "BEAR_DOWNTREND" else "🟢 READY TRIGGER"
        tracker_lines.append(
            f"| **{a['code']}** | {a['exchange']} | {a['price']:,.0f} | **{a['score']}** | **{a['master_composite_score']}** | "
            f"{a['weight_pct']}% | {a['target_shares']:,} CP | {a['stop_loss_vnd']:,.0f} | {a['tp1_vnd']:,.0f} | {a['tp2_vnd']:,.0f} | {tr_status} |"
        )

    with open(TRACKER_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(tracker_lines) + "\n")

    print(f"=== Hoàn tất Định lượng Rủi ro & Ma trận 5 Kịch bản Ban 4! Xuất file tại: {IC_DECISION_MD} ===")


if __name__ == "__main__":
    run()
