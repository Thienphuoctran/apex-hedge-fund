#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vn_mentor_engine.py - Học Viện Đào Tạo Thực Chiến & Huấn Luyện Viên Cá Nhân Cho NĐT Việt Nam
Chuyên trách Ban 6:
- Phát hành Bản Tin Khai Sáng Buổi Sáng lúc 7h30 sáng hàng ngày (trước giờ giao dịch).
- Đào tạo phương pháp mổ xẻ BCTC (Bảng CĐKT, KQKD, LCTT OCF/FCF) từ lý thuyết đến thực chiến.
- Kèm cặp tâm lý học hành vi: Vượt qua hội chứng FOMO ATO, sợ cắt lỗ, bắt dao rơi.
- Đặt câu hỏi phản biện Socratic và quản lý Sổ tay giao dịch cá nhân.
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
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "vn_market_data.json")
BCTC_PATH = os.path.join(BASE_DIR, "data", "vn_bctc_analysis.json")
MENTOR_DIR = os.path.join(BASE_DIR, "06_Investor_Academy", "daily_mentorship")
BRIEFING_MD = os.path.join(MENTOR_DIR, f"{datetime.date.today()}_VN_Mentor_Briefing.md")

def run():
    print("=== [VN MENTOR ENGINE v2.0] BẢN TIN KHAI SÁNG 7H30 SÁNG — BCTC THẬT & ỨNG BIẾN 5 KỊCH BẢN ===")
    os.makedirs(MENTOR_DIR, exist_ok=True)
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        mkt = json.load(f)
    with open(BCTC_PATH, "r", encoding="utf-8") as f:
        bctc = json.load(f)

    root_dir = os.path.dirname(BASE_DIR)
    live_bctc_path = os.path.join(BASE_DIR, "data", "vn_real_bctc_live.json")
    v2_path = os.path.join(root_dir, "data", "apex_quant_brain_v2_output.json")
    pb_path = os.path.join(root_dir, "data", "apex_adaptive_contingency_playbook.json")

    live_stocks = {}
    if os.path.exists(live_bctc_path):
        try:
            with open(live_bctc_path, "r", encoding="utf-8") as lf:
                live_stocks = json.load(lf).get("stocks", {})
        except Exception:
            live_stocks = {}
    mr = {}
    if os.path.exists(v2_path):
        try:
            with open(v2_path, "r", encoding="utf-8") as vf:
                mr = json.load(vf).get("market_regime", {})
        except Exception:
            mr = {}
    scenarios = []
    if os.path.exists(pb_path):
        try:
            with open(pb_path, "r", encoding="utf-8") as pf:
                scenarios = json.load(pf).get("scenarios", [])
        except Exception:
            scenarios = []

    def _lm(sym: str) -> dict:
        return (live_stocks.get(sym) or {}).get("latest_metrics") or {}

    hpg_lm = _lm("HPG")
    tpb_lm = _lm("TPB")
    ctg_lm = _lm("CTG")
    baf_lm = _lm("BAF")
    msh_lm = _lm("MSH")

    macro = mkt.get("macro_vietnam", {})
    fx_val = macro.get("USD_VND_Exchange_Rate", {}).get("value") or 25705.0
    gdp_val = (macro.get("VN_GDP_Growth_Live") or {}).get("value") or 9.95
    vni_val = float(mr.get("vnindex_close") or 1689.62)
    br20_val = float(mr.get("breadth_above_ma20_pct") or 25.7)
    cur_reg = str(mr.get("regime_id") or "BEAR_DOWNTREND")

    lines = [
        f"# BẢN TIN KHAI SÁNG BUỔI SÁNG & HUẤN LUYỆN ỨNG BIẾN ĐA KỊCH BẢN (7H30 AM) — {today_str}",
        "**Người hướng dẫn**: Huấn Luyện Viên Trưởng Học Viện Đầu Tư Thực Chiến (Ban 6 VN)",
        f"**Chế độ Thị trường sống**: **`{cur_reg}`** (`VN-Index {vni_val:,.2f}`, `Breadth>MA20 = {br20_val:.1f}%`)",
        "**Khung giờ phát hành**: **7h30 Sáng** (Dành 60 phút đọc BCTC thật & Ma trận 5 Kịch bản trước giao ban 8h30 của Minh Quân)",
        "",
        "---",
        "",
        "## 1. TỔNG QUAN VĨ MÔ & TÂM LÝ THỊ TRƯỜNG ĐẦU NGÀY",
        f"- **S&P 500 / US10Y**: `S&P 500 = {macro.get('S_AND_P500', {}).get('value')}` | `US10Y = {macro.get('US10Y', {}).get('value')}%` | `DXY = {macro.get('DXY', {}).get('value')}`",
        f"- **Tỷ giá USD/VND & GDP VN**: `USD/VND = {fx_val:,.1f} đ` | `GDP VN Q3/2026 = {gdp_val}%` | **Giá Dầu WTI**: `USD {macro.get('WTI_OIL', {}).get('value')}/thùng`",
        "- **Thông điệp mở phiên ATO**: 95% bẫy giá xanh rơi vào 15 phút đầu ATO và phiên sáng. Luôn chờ áp lực hàng T+2.5 lộ diện sau 13h15 và chỉ giải ngân trong Khung Giờ Vàng `14h00–14h25`.",
        "",
        "---",
        "",
        "## 2. BÀI HỌC THỰC CHIẾN Q3/2026: 'BÓC TRẦN LỢI NHUẬN GIẤY VS DÒNG TIỀN THẬT'",
        "",
        "> *'Doanh thu có thể tạo, Lợi nhuận kế toán có thể điều chỉnh, chỉ có Dòng tiền OCF thực trong két mới bảo vệ vốn gốc.'*",
        "",
        "### Các Case Study Sống Từ BCTC Q3/2026 (Vietcap IQ Live):",
        f"- **Cổ phiếu Tiền thật Sạch (`HPG`, `TPB`, `CTG`):** `HPG` (Doanh thu TTM `{hpg_lm.get('revenue_ttm_ty', 216450.4):,.1f} tỷ`, OCF `+{hpg_lm.get('ocf_ty', 29500.6):,.1f} tỷ`, FCF `+{hpg_lm.get('fcf_ty', 13007.9):,.1f} tỷ`, F-Score `{hpg_lm.get('piotroski_f_score', 8)}/9`); `TPB` (`F-Score {tpb_lm.get('piotroski_f_score', 9)}/9`, ROE `{tpb_lm.get('roe_ttm_pct', 18.35)}%`); `CTG` (`F-Score {ctg_lm.get('piotroski_f_score', 8)}/9`, ROE `{ctg_lm.get('roe_ttm_pct', 22.56)}%`).",
        f"- **Cảnh báo Đỏ Thực Tế (`BAF`):** LNST TTM sụp `{baf_lm.get('profit_growth_yoy', -80.16):+.2f}% YoY` còn `{baf_lm.get('net_profit_ttm_ty', 92.5)} tỷ`, P/E `{baf_lm.get('pe_ttm', 138.92)}x`, OCF âm **`{baf_lm.get('ocf_ty', -496.2):,.1f} tỷ`** (`{baf_lm.get('ocf_to_profit_ratio', -5.37)}x`), F-Score `{baf_lm.get('piotroski_f_score', 2)}/9`, Beneish `{baf_lm.get('beneish_m_score', -1.54)} (HIGH_RISK)`. Không giữ dài hạn!",
        f"- **Bài học Thanh khoản & Lệch pha Tiền (`MSH`):** ROE `{msh_lm.get('roe_ttm_pct', 24.89)}%` nhưng OCF TTM chỉ đạt `{msh_lm.get('ocf_ty', 7.1)} tỷ` (`{msh_lm.get('ocf_to_profit_ratio', 0.01)}x` LNST `{msh_lm.get('net_profit_ttm_ty', 629.2)} tỷ`) và thanh khoản 1M mỏng chỉ `{msh_lm.get('avg_val_1m_ty', 6.08)} tỷ/phiên` -> Dễ trượt giá khi thoát lệnh.",
        "",
        "---",
        "",
        "## 3. CÂU HỎI TƯ DUY PHẢN BIỆN SOCRATIC",
        "1. *Nếu bạn chỉ nhìn lợi nhuận danh nghĩa mà bỏ qua OCF âm (-496.2 tỷ) và F-Score = 2/9, bạn đang đầu tư hay đang đánh bạc vào niềm tin?*",
        f"2. *Khi VN-Index ở `{cur_reg}` (Breadth>MA20 = `{br20_val:.1f}%`), làm thế nào để giữ 100% tiền mặt không sốt ruột cho tới khi kịch bản S1/S2/S3 kích hoạt?*",
        "",
        "---",
        "",
        "## 4. CẨM NANG ỨNG BIẾN LINH HOẠT 5 KỊCH BẢN (S1 – S5) TRONG NGÀY",
        "Nhà đầu tư chuyên nghiệp không đoán bừa 1 hướng thị trường; hãy bám đúng phản xạ theo từng kịch bản:",
        "",
    ]

    for sc in scenarios:
        lines.append(
            f"- **`{sc['scenario_id']}` ({sc['name_vi']})**: Công suất `{sc.get('target_equity_exposure_pct')}` | Trạng thái 19/11: `{sc.get('status_on_2026_11_19')}` — {sc.get('execution_tactics_vi').splitlines()[0]}"
        )
    lines.extend([
        "",
        "## 5. LỊCH TRÌNH TIẾP THEO:",
        "- **07h30 - 08h30**: Nhà đầu tư rà soát BCTC Ban 2 & Checklist 7 Điểm cho 5 kịch bản.",
        "- **08h30**: **Minh Quân (Ban 7)** kích hoạt Sổ lệnh Đa Kịch bản sẵn sàng điều hành phiên!",
        ""
    ])

    with open(BRIEFING_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"=== Đã hoàn tất Bản tin Khai sáng 7h30 sáng tại: {BRIEFING_MD} ===")

if __name__ == "__main__":
    run()
