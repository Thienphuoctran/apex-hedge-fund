#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH EMERGENCY FORENSIC HEARING & SELF-CRITICISM SUMMARY TO TELEGRAM
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message

def dispatch_emergency_hearing():
    msg = (
        "🏛️ *[BIÊN BẢN HỘI NGHỊ LUẬN TỘI, TỰ KIỂM ĐIỂM NĂNG LỰC & CẢI TỔ THỂ CHẾ TỐI CAO]*\n"
        "👑 *Chủ tịch*: **Trần Quốc Thiên Phước** | Tiểu khoản: `105C307855` (TCBS)\n"
        "⏰ *Thời gian*: `09:55 - 10:00 AM (06/11/2026)` | *Chủ tọa*: **Master CIO James** & **Palmer**\n\n"
        "💥 *1. KẾT LUẬN NGUỒN CƠN SAI LẦM: SAI BẮT ĐẦU TỪ ĐÂU?*\n"
        "• *Người tham mưu sai đầu tiên*: **Minh Quân (Ban 7 VN)** lúc 13:45 hôm qua, quá tự tin vào nến ngày, nảy sinh lòng tham muốn rướn ăn dày hơn và đui mù trước quy luật rủi ro phiên Thứ Sáu (Friday Weekend De-risking).\n"
        "• *Người chịu trách nhiệm cao nhất*: **Master CIO James (Ban 8)** đã mềm lòng duyệt giữ lệnh qua đêm thay vì chốt lời tại đỉnh chiều qua.\n"
        "• *Ban 4 (Quản trị rủi ro)*: Thiếu cầu chì 'Lock-in Profit' khi danh mục đã lãi > 2.5%.\n"
        "• *Hậu quả*: Bốc hơi 335.000 ₫ tiền lãi (từ +534k xuống +199.6k ₫)!\n\n"
        "🛠️ *2. BỘ 3 CẦU CHÌ KỸ THUẬT KHÓA BẰNG MÃ CODE (ZERO-FORGETTING)*:\n"
        "1. 🔒 `[RULE-TPLF-01]`: Chiều Thứ Năm lãi >= +2.0%, BẮT BUỘC chốt lời tối thiểu 50% đến 100%. CẤM ôm hàng qua đêm vào Thứ Sáu!\n"
        "2. 🔒 `[RULE-REALITY-02]`: Bảng điện đỏ > 50%, CẤM dùng từ ngữ phóng đại tô hồng. Chỉ báo cáo giá khớp thực tế!\n"
        "3. 🔒 `[RULE-ZERO-FORGET-03]`: Mọi Agent bắt buộc chạy `pre_flight_compliance_check.py` trước mọi phiên giao dịch, triệt tiêu 100% bệnh quên lãng!\n\n"
        "📝 *3. GHI DANH BÀI HỌC SỬA SAI THỂ CHẾ SỐ 15 VÀO SỔ NHẬT KÝ BAN 5*:\n"
        "• Đã lưu trữ vật lý tại `08_Master_Investment_CIO/2026-11-06_Emergency_Council_Forensic_Hearing.md`.\n"
        "• Toàn thể 11 Trưởng phòng ban đồng thanh cam kết trước Chủ tịch: ĐÂY LÀ LẦN CUỐI CÙNG!"
    )

    print("[*] Dispatching Emergency Forensic Hearing to Telegram...")
    res_james = dispatch_message("james_hq", msg)
    res_academy = dispatch_message("academy_learning", msg)
    res_private = dispatch_message("copilot_chat", msg)
    print(f"[+] Results: JamesHQ={res_james}, Academy={res_academy}, Private={res_private}")

if __name__ == "__main__":
    dispatch_emergency_hearing()
