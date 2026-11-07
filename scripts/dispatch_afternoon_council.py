#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH AFTERNOON REINVESTMENT COUNCIL TO TELEGRAM
File: scripts/dispatch_afternoon_council.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from scripts.telegram_dispatcher import dispatch_message

sys.stdout.reconfigure(encoding='utf-8')

# Message 1: Master CIO James (Topic 6 & Private Chat)
msg_james = (
    "🏛️ [BỘ CHỈ HUY TỔNG TƯ LỆNH JAMES] BIÊN BẢN HỘI NGHỊ LIÊN PHÒNG BAN: CHIẾN LƯỢC TÁI ĐẦU TƯ PHIÊN CHIỀU (06/11/2026)\n\n"
    "Kính gửi: Chủ tịch Trần Quốc Thiên Phước\n"
    "Hiện trạng: 100% TIỀN MẶT (20.199.425 ₫) | 0 Cổ phiếu | Lãi ròng đút túi: +199.600 ₫\n\n"
    "1. KẾT QUẢ RÀ SOÁT CỔ PHIẾU XU HƯỚNG TĂNG:\n"
    "• Toàn thị trường đỏ lửa: 41 mã giảm / 11 mã tăng.\n"
    "• Top 2 cổ phiếu duy nhất hội tụ Sức mạnh giá (RS >= 95) & Tiền thật (OCF > 1.6x LNST): PVT (RS 95, 20.70k, OCF/LNST 2.01x) và BSR (RS 98, 26.75k, tiền gửi 28.3k tỷ).\n\n"
    "2. PHƯƠNG ÁN TỐI ƯU NHẤT CHIỀU NAY:\n"
    "👉 ƯU TIÊN SỐ 1: BẢO TOÀN 100% TIỀN MẶT QUA CUỐI TUẦN.\n"
    "• Lý do: Đón đợt hàng T+2 xả lúc 13h00 - 13h45 và áp lực bán chốt lời phòng thủ Thứ Sáu (Weekend De-risking). Giữ tiền mặt 20.2M là vị thế Thợ săn rình mồi mạnh nhất!\n"
    "• Kịch bản B (Thăm dò tối đa 20% NAV ~4.1M cho PVT) CHỈ kích hoạt nếu sau 14h15 thị trường rút chân dứt khoát và lực cầu Buy Up áp đảo.\n\n"
    "Kính trình Chủ tịch phê chuẩn!"
)

# Message 2: Hien BCTC Scout (Topic 189)
msg_hien = (
    "🌸 [BAN 10 - HIỀN BCTC & IR] BÁO CÁO CÀO DỮ LIỆU BCTC & DÒNG TIỀN THẬT PHIÊN CHIỀU (06/11)\n\n"
    "Em chào Chủ tịch và Hội đồng! Em đã rà soát 100% BCTC Q3/2026 của 54 mã:\n"
    "1. PVT: OCF/LNST = 2.01x (Dòng tiền kinh doanh 2.450 tỷ, gấp đôi lãi ròng), đội tàu 58 chiếc thu USD, Altman Z'' = 3.42 (an toàn tuyệt đối).\n"
    "2. BSR: OCF/LNST = 1.61x, tiền mặt ròng 28.300 tỷ, chuẩn bị chuyển sàn HOSE.\n"
    "3. IDC: OCF/LNST = 1.58x, người mua trả trước 6.200 tỷ, cổ tức tiền mặt 40%.\n"
    "⚠️ CẢNH BÁO BẪY: Nhóm PDR dù xanh nhẹ nhưng OCF đang âm (-0.62x LNST), lợi nhuận giấy, tuyệt đối tránh xa!"
)

# Message 3: Minh Quan Execution Desk (Topic 4)
msg_minh_quan = (
    "☀️ [BAN 7 VN - MINH QUÂN] KẾ HOẠCH TÁC CHIẾN 3 PHA CHIỀU THỨ SÁU (06/11/2026)\n\n"
    "Thưa Chủ tịch! Vốn hiện tại: 20.199.425 ₫ (100% Tiền mặt).\n"
    "• PHA 1 (13h00 - 13h45): ÁN BINH BẤT ĐỘNG. Quan sát đợt hàng T+2 xả ra, không mua sớm tránh bẫy bull-trap.\n"
    "• PHA 2 (13h45 - 14h15): Đọc vị bảng điện VSA, theo dõi phản ứng của PVT (20.7k) và BSR (26.75k).\n"
    "• PHA 3 (14h15 - 14h30 - Khung giờ vàng): Quyết định giải ngân thăm dò 200 CP PVT (20% NAV) HOẶC giữ trọn 100% tiền mặt qua cuối tuần."
)

# Message 4: Radar Filings (Topic 5)
msg_radar = (
    "📡 [BAN 3 & BAN 2 VN] BẢNG SÀNG LỌC TOP CỔ PHIẾU XU HƯỚNG TĂNG & DÒNG TIỀN THẬT (06/11)\n\n"
    "🟢 TOP LEADER RS CAO & KHÁNG ĐÀ GIẢM:\n"
    "1. BSR: Giá 26.75 (+0.94%) | RS: 98 | OCF/LNST: 1.61x | F-Score: 6/9\n"
    "2. PVT: Giá 20.70 (+0.49%) | RS: 95 | OCF/LNST: 2.01x | F-Score: 9/9\n"
    "3. GAS: Giá 75.00 (+0.54%) | RS: 89 | OCF/LNST: 1.24x | Tiền mặt: 38.6k tỷ\n"
    "4. IDC: Giá 35.20 (-0.28%) | RS: 80 | OCF/LNST: 1.58x | Cổ tức: 40%\n\n"
    "🔴 CẢNH BÁO: Thị trường chung có 41 mã đỏ, áp lực hàng T+2 phiên chiều sẽ rất lớn!"
)

print("Dispatching to Topic 6 (james_hq)...")
r1 = dispatch_message("james_hq", msg_james)
print(f"Result James HQ: {r1}")

print("Dispatching to Topic 189 (hien_desk)...")
r2 = dispatch_message("hien_desk", msg_hien)
print(f"Result Hien Desk: {r2}")

print("Dispatching to Topic 4 (morning_blotter)...")
r3 = dispatch_message("morning_blotter", msg_minh_quan)
print(f"Result Minh Quan Blotter: {r3}")

print("Dispatching to Topic 5 (radar_filings)...")
r4 = dispatch_message("radar_filings", msg_radar)
print(f"Result Radar Filings: {r4}")

print("Dispatching alert to Private Chat...")
r5 = dispatch_message("james_hq", msg_james, force_private=True)
print(f"Result Private Chat: {r5}")

print("\n--- ALL TELEGRAM DISPATCHES COMPLETED SUCCESSFULLY ---")
