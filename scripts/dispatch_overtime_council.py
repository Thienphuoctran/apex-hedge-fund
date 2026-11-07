#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH OVERTIME MARKET INTELLIGENCE COUNCIL TO TELEGRAM
File: scripts/dispatch_overtime_council.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.telegram_dispatcher import dispatch_message

sys.stdout.reconfigure(encoding='utf-8')

# Message 1: Master CIO James (Topic 6 & Private Chat)
msg_james = (
    "🏛️ [BỘ CHỈ HUY TỔNG TƯ LỆNH JAMES] BÁO CÁO HỘI NGHỊ TĂNG CA: THẨM ĐỊNH THÔNG TIN KINH TẾ & TÀI CHÍNH TIKTOK\n\n"
    "Kính gửi: Chủ tịch Trần Quốc Thiên Phước\n"
    "Hội đồng 11 phòng ban đã họp tăng ca khẩn cấp lúc nửa đêm theo lệnh Chủ tịch để mổ xẻ dữ liệu từ 3 nguồn video:\n\n"
    "1. CHUẨN HÓA DỮ LIỆU ĐÓNG PHIÊN THỨ SÁU (06/11):\n"
    "• VN-INDEX đóng cửa 1.725,36 (-15,37 điểm / -0,88%), thủng MA20 (1.731).\n"
    "• Trụ kéo lùi: Phố Wall đỏ, FPT giảm sâu -3,97%, VIC bị bán.\n"
    "• Khối ngoại bán ròng -305 tỷ (chuỗi 10 phiên bán ròng), duy nhất VIX được mua ròng +452 tỷ.\n"
    "• Sóng đầu cơ cá biệt: VND (+5,28%), KDH (+5,23%).\n\n"
    "2. Ý NGHĨA SỐNG CÒN ĐỐI VỚI QUỸ APEX:\n"
    "👉 Quyết định BÁN HẾT 900 CP sáng nay đút túi +199.600 ₫ là THIÊN TÀI & BẢO VỆ TUYỆT ĐỐI VỐN GỐC!\n"
    "• Nếu sáng nay tham lam ôm hàng hoặc chiều nay bắt đáy sớm thì đã bị bốc hơi tiền lãi và kẹp T+2.5 qua cuối tuần.\n"
    "• Hiện tại Quỹ cầm 100% TIỀN MẶT (20.199.425 ₫) — vị thế Thợ săn mạnh nhất để gom siêu cổ phiếu giá rẻ quanh mốc 1.700 điểm vào tuần tới!\n\n"
    "Toàn thể Hội đồng kính chúc Chủ tịch ngủ thật ngon giấc!"
)

# Message 2: Hien Desk (Topic 189)
msg_hien = (
    "🌸 [BAN 10 - HIỀN BCTC & IR] BÓC TÁCH CHẤT LƯỢNG LỢI NHUẬN TỪ NGUỒN TIKTOK\n\n"
    "Thưa Chủ tịch! Về các mã xanh mạnh hôm nay:\n"
    "• KDH (+5,23%): Khớp 28M CP, nhưng RS chỉ 21 điểm (đáy bảng). Là nhịp hồi kỹ thuật từ đáy, chưa phải Uptrend bền vững.\n"
    "• VND (+5,28%): Hưởng lợi câu chuyện tăng vốn, P/B chiết khấu sâu.\n"
    "⚠️ CẢNH BÁO: Các mã PDR, DXG có OCF âm nặng (-0.6x đến -1.8x LNST), tuyệt đối không đua lệnh theo sóng đầu cơ!"
)

# Message 3: Minh Quan Hunting Plan (Topic 4)
msg_minh_quan = (
    "☀️ [BAN 7 VN - MINH QUÂN] KẾ HOẠCH SĂN MỒI GIÁ RẺ ĐẦU TUẦN TỚI (1.700 - 1.710 ĐIỂM)\n\n"
    "Kính báo Chủ tịch! Quỹ đang có 20.199.425 ₫ Tiền mặt tươi rói.\n"
    "Khi VN-Index quán tính điều chỉnh về vùng hỗ trợ cứng 1.700 - 1.710 điểm vào Thứ Hai, các siêu cổ phiếu tiền thật PVT, BSR, IDC, TCB sẽ chiết khấu về điểm mua Kim Tự Tháp cực kỳ hấp dẫn!"
)

print("Dispatching Overtime Hearing to Topic 6 (james_hq)...")
dispatch_message("james_hq", msg_james)

print("Dispatching Overtime Hearing to Topic 189 (hien_desk)...")
dispatch_message("hien_desk", msg_hien)

print("Dispatching Overtime Hearing to Topic 4 (morning_blotter)...")
dispatch_message("morning_blotter", msg_minh_quan)

print("Dispatching Overtime Hearing to Private Chat...")
dispatch_message("james_hq", msg_james, force_private=True)

print("--- OVERTIME COUNCIL DISPATCH COMPLETED ---")
