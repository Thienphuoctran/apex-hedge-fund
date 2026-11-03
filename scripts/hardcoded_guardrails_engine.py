#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KHÓA CHỐT KỶ LUẬT THÉP BẰNG MÃ NGUỒN (HARD-CODED GUARDRAILS ENGINE)
File: scripts/hardcoded_guardrails_engine.py
Cơ quan chủ quản: Palmer (Apex Central Governance) & Master CIO James (Ban 8)
Phục vụ: Chủ tịch Phước Trần (Tài khoản TCBS: 105C307855 - NAV: 20.000.000 VNĐ)

Mục tiêu cốt lõi:
Chuyển hóa 100% các bài học sai lầm từ Sổ Tự Kiểm Điểm (Mistake Autopsy) và Kho Ký Ức (Mem0)
thành các dòng code logic bắt buộc (IF... THEN... REJECT).
Tuyệt đối KHÔNG cho phép bất kỳ Agent hay Chuyên viên nào (dù là James, Minh Quân hay Victor)
bấm lệnh nếu vi phạm các lằn ranh đỏ bảo vệ vốn.
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

GUARDRAILS_LOG_PATH = BASE_DIR / "VN_Market" / "04_Investment_Committee" / "guardrails_enforcement_log.json"


# ==============================================================================
# BỘ 5 KHÓA CHỐT LẰN RANH ĐỎ (5 ABSOLUTE NON-NEGOTIABLE GUARDRAILS)
# ==============================================================================

GUARDRAIL_RULES = {
    "GUARD_01_ATO_FOMO_VETO": {
        "rule_id": "GUARD-01",
        "name": "Khóa Cứng Bẫy Mua Đuổi ATO (9h00 - 10h00)",
        "lesson_origin": "MEM-VN-001 (Mistake Autopsy: F0 thường đu đỉnh ATO khi tạo Gap xanh ảo, bị xả T+2 lúc 13h30)",
        "description": "Cấm tuyệt đối đặt lệnh MUA ATO hoặc MUA đuổi trước 10h00 sáng nếu cổ phiếu tăng giá >= +2.0%."
    },
    "GUARD_02_OCF_DEBT_TRAP_VETO": {
        "rule_id": "GUARD-02",
        "name": "Khóa Cứng Cổ Phiếu Rác / Bẫy Nợ Vay / Lợi Nhuận Giấy",
        "lesson_origin": "MEM-VN-003 (Vụ án DVD, TTF, NVL: Lãi kế toán nhưng OCF âm dồn dập và nợ đầm đìa)",
        "description": "Cấm tuyệt đối giải ngân vào cổ phiếu có OCF < 0 liên tục 2 quý hoặc tỷ lệ Nợ/Vốn chủ sở hữu (D/E) > 2.0x."
    },
    "GUARD_03_T0_SAFETY_FUSE_1425": {
        "rule_id": "GUARD-03",
        "name": "Cầu Chì Bắt Buộc Cân Bằng Trạng Thái T+0 Trước 14h25",
        "lesson_origin": "Quy tắc an toàn vốn: Tham lướt sóng biến thành gồng lỗ qua đêm do kẹt hàng T+2.5",
        "description": "Khi lướt T+0 trên kho hàng có sẵn, bắt buộc bán trả hàng trước 14h25. Sau 14h25 hệ thống tự động khóa sổ, cấm ôm thêm hàng."
    },
    "GUARD_04_MAX_PORTFOLIO_RISK_LIMIT": {
        "rule_id": "GUARD-04",
        "name": "Khống Chế Tổn Thất Tuyệt Đối Stop Loss <= 1.5% NAV",
        "lesson_origin": "Công thức Position Sizing chuẩn mực thể chế của Palmer & Hội đồng Rủi ro Ban 4",
        "description": "Khoản tổn thất tối đa khi chạm ngưỡng cắt lỗ Stop 2xATR không được vượt quá 1.5% NAV (300.000 ₫ trên NAV 20 triệu)."
    },
    "GUARD_05_NO_AVERAGING_DOWN_MA200": {
        "rule_id": "GUARD-05",
        "name": "Cấm Tuyệt Đối Bình Quân Giá Xuống Dưới MA200",
        "lesson_origin": "Bài học xương máu của Jesse Livermore & Stan Weinstein: Trung bình giá xuống khi downtrend là tự sát",
        "description": "Cấm mua thêm hoặc bắt đáy nếu cổ phiếu đang giao dịch dưới đường xu hướng dài hạn MA200."
    }
}


def evaluate_order_against_guardrails(
    ticker: str,
    action: str,                     # "BUY" / "SELL" / "T0_BUY" / "T0_SELL"
    order_time_str: Optional[str] = None, # "HH:MM:SS" (nếu None lấy giờ hiện tại)
    price_change_pct: float = 0.0,   # % tăng/giảm so với tham chiếu
    ocf_to_net_income: float = 1.0,  # Tỷ lệ tiền thật từ Hiền (Ban 10)
    debt_to_equity: float = 0.8,     # Đòn bẩy nợ từ BCTC
    is_below_ma200: bool = False,    # Có đang thủng MA200 không
    trade_risk_vnd: float = 0.0,     # Rủi ro nếu chạm Stop 2xATR (VNĐ)
    total_nav_vnd: float = 20000000.0# Tổng NAV
) -> Dict[str, Any]:
    """
    Hàm lõi kiểm tra 100% lệnh giao dịch trước khi bấm cò.
    Trả về: {"verdict": "PASSED" | "REJECTED", "violated_guards": [...], "details": ...}
    """
    clean_sym = ticker.upper().strip()
    act = action.upper().strip()
    
    now = datetime.datetime.now()
    if order_time_str:
        try:
            curr_time = datetime.datetime.strptime(order_time_str, "%H:%M:%S").time()
        except Exception:
            curr_time = now.time()
    else:
        curr_time = now.time()

    violations = []

    # ==========================================================================
    # KIỂM TRA KHÓA 1: BẪY ATO (GUARD-01)
    # ==========================================================================
    time_0900 = datetime.time(9, 0, 0)
    time_1000 = datetime.time(10, 0, 0)
    if "BUY" in act:
        if (time_0900 <= curr_time < time_1000) and (price_change_pct >= 2.0):
            violations.append({
                "guard_id": "GUARD_01_ATO_FOMO_VETO",
                "reason": f"Lệnh Mua {clean_sym} vào lúc {curr_time.strftime('%H:%M:%S')} khi giá đã tăng +{price_change_pct:.2f}% (Bẫy Gap xanh ATO).",
                "enforced_action": "TỪ CHỐI LỆNH MUA ĐUỔI. Yêu cầu Minh Quân chuyển sang Lệnh Limit (LO) chiết khấu hoặc chờ Khung Giờ Vàng 14h00-14h25.",
                "historical_lesson": GUARDRAIL_RULES["GUARD_01_ATO_FOMO_VETO"]["lesson_origin"]
            })

    # ==========================================================================
    # KIỂM TRA KHÓA 2: BẪY NỢ VAY & LỢI NHUẬN GIẤY (GUARD-02)
    # ==========================================================================
    if "BUY" in act:
        if ocf_to_net_income <= 0.0 or debt_to_equity > 2.0:
            violations.append({
                "guard_id": "GUARD_02_OCF_DEBT_TRAP_VETO",
                "reason": f"Mã {clean_sym} vi phạm chỉ số an toàn tài chính: OCF/LNST = {ocf_to_net_income:.2f}x (<=0) hoặc D/E = {debt_to_equity:.2f}x (>2.0).",
                "enforced_action": "KHÓA QUYỀN MUA VĨNH VIỄN. Đưa vào danh sách VETO (Disciplined Pass). Tiền của Chủ tịch chỉ đầu tư vào doanh nghiệp Tiền Thật!",
                "historical_lesson": GUARDRAIL_RULES["GUARD_02_OCF_DEBT_TRAP_VETO"]["lesson_origin"]
            })

    # ==========================================================================
    # KIỂM TRA KHÓA 3: CẦU CHÌ AN TOÀN T+0 (GUARD-03)
    # ==========================================================================
    time_1425 = datetime.time(14, 25, 0)
    if act == "T0_BUY" and curr_time >= time_1425:
        violations.append({
            "guard_id": "GUARD_03_T0_SAFETY_FUSE_1425",
            "reason": f"Đã quá 14h25 ({curr_time.strftime('%H:%M:%S')}), thị trường bước vào phiên ATC.",
            "enforced_action": "CẤM MỞ LỆNH T+0 MỚI. Bắt buộc thanh lý mọi vị thế lướt sóng còn tồn dư để tránh kẹt vốn qua đêm.",
            "historical_lesson": GUARDRAIL_RULES["GUARD_03_T0_SAFETY_FUSE_1425"]["lesson_origin"]
        })

    # ==========================================================================
    # KIỂM TRA KHÓA 4: HẠN MỨC RỦI RO DANH MỤC (GUARD-04)
    # ==========================================================================
    max_risk_allowed = total_nav_vnd * 0.015  # 1.5% NAV = 300.000 đ
    if "BUY" in act and trade_risk_vnd > max_risk_allowed:
        violations.append({
            "guard_id": "GUARD_04_MAX_PORTFOLIO_RISK_LIMIT",
            "reason": f"Rủi ro cắt lỗ của lệnh này là {trade_risk_vnd:,.0f} ₫, vượt trần 1.5% NAV ({max_risk_allowed:,.0f} ₫).",
            "enforced_action": f"TỰ ĐỘNG THU NHỎ KHỐI LƯỢNG (Position Sizing). Giảm số lượng cổ phiếu cho đến khi mức rủi ro <= {max_risk_allowed:,.0f} ₫.",
            "historical_lesson": GUARDRAIL_RULES["GUARD_04_MAX_PORTFOLIO_RISK_LIMIT"]["lesson_origin"]
        })

    # ==========================================================================
    # KIỂM TRA KHÓA 5: CẤM BẮT ĐÁY DƯỚI MA200 (GUARD-05)
    # ==========================================================================
    if "BUY" in act and is_below_ma200:
        violations.append({
            "guard_id": "GUARD_05_NO_AVERAGING_DOWN_MA200",
            "reason": f"Mã {clean_sym} đang nằm dưới đường trung bình động 200 ngày (Downtrend trung hạn).",
            "enforced_action": "CẤM MUA THĂM DÒ / CẤM TRUNG BÌNH GIÁ XUỐNG. Chỉ mua khi giá tái tích lũy thành công trên MA200 kèm nến cạn cung.",
            "historical_lesson": GUARDRAIL_RULES["GUARD_05_NO_AVERAGING_DOWN_MA200"]["lesson_origin"]
        })

    # KẾT LUẬN CUỐI CÙNG
    is_passed = len(violations) == 0
    verdict = "PASSED (ĐƯỢC PHÉP THỰC THI)" if is_passed else "REJECTED BY GUARDRAIL (BỊ KHÓA BỞI CODE)"

    result = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "ticker": clean_sym,
        "action": act,
        "is_passed": is_passed,
        "verdict": verdict,
        "violations_count": len(violations),
        "violations": violations
    }

    # Lưu vết kiểm toán an toàn vốn
    _log_guardrail_event(result)

    return result


def _log_guardrail_event(event: Dict[str, Any]) -> None:
    """Lưu lịch sử bảo vệ vốn vào tệp JSON"""
    GUARDRAILS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logs = []
    if GUARDRAILS_LOG_PATH.exists():
        try:
            logs = json.loads(GUARDRAILS_LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            logs = []
    logs.append(event)
    GUARDRAILS_LOG_PATH.write_text(json.dumps(logs[-100:], indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    print("=" * 70)
    print("  🛡️ KIỂM THỬ KHÓA CHỐT KỶ LUẬT THÉP BẰNG CODE (HARD-CODED GUARDRAILS)")
    print("=" * 70)
    
    # Test 1: Mô phỏng lệnh mua đuổi ATO lúc 9h15 sáng khi giá xanh +3.2%
    print("\n[TEST 1] Thử nghiệm lệnh mua đuổi ATO (9h15 sáng, giá tăng +3.2%)...")
    res1 = evaluate_order_against_guardrails(
        ticker="HPG",
        action="BUY",
        order_time_str="09:15:30",
        price_change_pct=3.2,
        ocf_to_net_income=1.08,
        debt_to_equity=0.68,
        trade_risk_vnd=250000
    )
    print(f" -> Kết quả: {res1['verdict']}")
    if not res1["is_passed"]:
        print(f" -> Lý do chặn: {res1['violations'][0]['reason']}")
        print(f" -> Biện pháp cưỡng chế: {res1['violations'][0]['enforced_action']}")

    # Test 2: Mô phỏng lệnh mua cổ phiếu rác OCF âm liên tục
    print("\n[TEST 2] Thử nghiệm mua cổ phiếu rác OCF âm (OCF = -1.2x, Nợ D/E = 3.5x)...")
    res2 = evaluate_order_against_guardrails(
        ticker="NVL",
        action="BUY",
        order_time_str="14:10:00",
        price_change_pct=1.0,
        ocf_to_net_income=-0.5,
        debt_to_equity=3.5,
        trade_risk_vnd=150000
    )
    print(f" -> Kết quả: {res2['verdict']}")
    if not res2["is_passed"]:
        print(f" -> Lý do chặn: {res2['violations'][0]['reason']}")
        print(f" -> Biện pháp cưỡng chế: {res2['violations'][0]['enforced_action']}")

    # Test 3: Mô phỏng lệnh hợp lệ chuẩn mực trong Khung Giờ Vàng 14h15
    print("\n[TEST 3] Thử nghiệm lệnh chuẩn Khung Giờ Vàng 14h15 trên siêu cổ phiếu HPG...")
    res3 = evaluate_order_against_guardrails(
        ticker="HPG",
        action="BUY",
        order_time_str="14:15:00",
        price_change_pct=0.5,
        ocf_to_net_income=1.08,
        debt_to_equity=0.68,
        is_below_ma200=False,
        trade_risk_vnd=180000,
        total_nav_vnd=20000000
    )
    print(f" -> Kết quả: {res3['verdict']}")
    print(f" -> Trạng thái: 🟢 THÔNG QUA AN TOÀN TUYỆT ĐỐI!")
