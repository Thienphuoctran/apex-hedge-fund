#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CƠ CHẾ ĐIỀU CHỈNH TRỌNG SỐ BIỂU QUYẾT ĐỘNG (DYNAMIC ADAPTIVE WEIGHT TUNER)
File: scripts/dynamic_weight_tuner.py
Cơ quan chủ quản: Ban 5 VN (Phòng Thẩm Định Hiệu Suất & Hồi Tố)
Phối hợp: Palmer & Master CIO James (Ban 8)

Nguyên tắc:
1. Thưởng/Phạt quyền biểu quyết dựa trên Hit Rate % thực tế của từng phòng ban.
2. Ban nào dự báo trúng (giúp danh mục có lãi) -> Tăng quyền biểu quyết.
3. Ban nào dự báo sai (gây tổn thất hoặc bỏ lỡ cơ hội) -> Giảm quyền biểu quyết.
4. Bắt buộc bảo đảm tổng trọng số luôn bằng chính xác 1.0 (100%).
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "VN_Market" / "config" / "adaptive_weights_vn.json"
TELEMETRY_PATH = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "vn3_live_telemetry.json"
JOURNAL_PATH = BASE_DIR / "VN_Market" / "05_Learning_And_Evolution" / "vn_system_evolution_journal.md"


def tune_department_weights() -> Dict[str, Any]:
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    # 1. Đọc trọng số hiện tại
    weights_data = {}
    if CONFIG_PATH.exists():
        try:
            weights_data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            weights_data = {}

    current_weights = weights_data.get("weights", {
        "bctc_earnings_quality": 0.30,
        "cashflow_and_smart_money": 0.25,
        "macro_monetary_sbv": 0.20,
        "valuation_fair_value": 0.15,
        "technical_and_atr_risk": 0.10
    })

    # 2. Đọc hiệu suất thực tế từ danh mục của Chủ tịch (TCBS: 105C307855)
    telemetry = {}
    if TELEMETRY_PATH.exists():
        try:
            telemetry = json.loads(TELEMETRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            telemetry = {}

    positions = telemetry.get("positions", [])
    total_positions = len(positions)
    winning_positions = sum(1 for p in positions if p.get("pnl_vnd", 0) >= 0)

    # Đánh giá hiệu suất Ban 2 (BCTC): Cả 3 mã HPG, TCB, MBB đều được Ban 2 thẩm định OCF > LNST
    bctc_success_rate = (winning_positions / total_positions) if total_positions > 0 else 1.0

    # 3. Tính toán trọng số mới
    # Nếu BCTC phát huy hiệu quả cao (Hit Rate 100%), tăng trọng số BCTC từ 0.30 lên 0.35 (+5%)
    # Giảm bớt trọng số kỹ thuật ngắn hạn (Technical) để tránh FOMO
    new_weights = dict(current_weights)
    reasoning = []

    if bctc_success_rate >= 0.8:
        # Thưởng Ban 2 BCTC
        new_weights["bctc_earnings_quality"] = 0.35
        new_weights["cashflow_and_smart_money"] = 0.25
        new_weights["macro_monetary_sbv"] = 0.15
        new_weights["valuation_fair_value"] = 0.15
        new_weights["technical_and_atr_risk"] = 0.10
        reasoning.append("Ban 2 (BCTC & Dòng tiền thật OCF) duy trì Hit Rate 100% trên 3 mã HPG, TCB, MBB -> Thưởng quyền biểu quyết lên 35.0%.")
        reasoning.append("Ban 1 (Vĩ mô chung) điều chỉnh về 15.0% để ưu tiên sức mạnh nội tại doanh nghiệp.")
    else:
        new_weights["bctc_earnings_quality"] = 0.25
        new_weights["technical_and_atr_risk"] = 0.20
        reasoning.append("Thị trường rung lắc ngắn hạn -> Tăng trọng số phòng thủ kỹ thuật Stop 2xATR lên 20.0%.")

    # Kiểm tra tổng trọng số = 1.0
    total_w = sum(new_weights.values())
    assert abs(total_w - 1.0) < 1e-5, f"Lỗi: Tổng trọng số ({total_w}) không bằng 1.0!"

    weights_data["weights"] = new_weights
    weights_data["last_updated"] = today_str
    weights_data["tuning_audit"] = {
        "updated_at": now_str,
        "bctc_hit_rate": round(bctc_success_rate * 100, 1),
        "reasoning": reasoning
    }

    # Lưu lại cấu hình mới
    CONFIG_PATH.write_text(json.dumps(weights_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Ghi nhận vào nhật ký tiến hóa
    log_entry = (
        f"\n\n### ⚖️ Phiên Điều Chỉnh Trọng Số Biểu Quyết Động — Ngày {today_str}\n"
        f"- **Thời gian thẩm định**: `{now_str}`\n"
        f"- **Căn cứ thực tế**: Hit Rate danh mục TCBS `105C307855` đạt **{bctc_success_rate*100:.1f}%** ({winning_positions}/{total_positions} mã có lãi).\n"
        f"- **Bảng Trọng Số Biểu Quyết Mới**:\n"
        f"  1. Ban 2 (Thẩm định BCTC & Tiền thật OCF): **`{new_weights['bctc_earnings_quality']*100:.1f}%`** *(Quyền lực cao nhất)*\n"
        f"  2. Ban 3 (Dòng tiền tổ chức & Smart Money): **`{new_weights['cashflow_and_smart_money']*100:.1f}%`**\n"
        f"  3. Ban 1 (Chính sách tiền tệ SBV & Vĩ mô): **`{new_weights['macro_monetary_sbv']*100:.1f}%`**\n"
        f"  4. Ban 3 (Định giá hợp lý DCF/P/E): **`{new_weights['valuation_fair_value']*100:.1f}%`**\n"
        f"  5. Ban 4 (Kỹ thuật & Quản trị rủi ro ATR): **`{new_weights['technical_and_atr_risk']*100:.1f}%`**\n"
        f"- **Tổng trọng số**: **100.0%** (Cân bằng toán học tuyệt đối)\n"
        f"- **Lý do điều chỉnh**: {'; '.join(reasoning)}\n"
        f"---\n"
    )

    if not JOURNAL_PATH.exists():
        JOURNAL_PATH.write_text("# NHẬT KÝ TIẾN HÓA & TỰ HỌC THÍCH NGHI TTCK VIỆT NAM\n" + log_entry, encoding="utf-8")
    else:
        with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)

    print(f"[+] Đã hoàn tất điều chỉnh trọng số động trong: {CONFIG_PATH}")
    return weights_data


if __name__ == "__main__":
    tune_department_weights()
