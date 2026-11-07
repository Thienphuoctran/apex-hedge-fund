#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH CONSTITUTION RATIFICATION REPORT TO TELEGRAM
File: scripts/dispatch_constitution_ratification.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.telegram_dispatcher import dispatch_message

sys.stdout.reconfigure(encoding='utf-8')

# Message: Master CIO James (Topic 6 & Private Chat)
msg_const = (
    "📜 [BỘ CHỈ HUY TỔNG TƯ LỆNH JAMES] BÁO CÁO TIẾP NHẬN & TUYÊN THỆ BỘ LUẬT THỂ CHẾ DOANH NGHIỆP APEX (V1.0)\n\n"
    "Kính gửi: Chủ tịch Trần Quốc Thiên Phước\n"
    "Tổng Tư Lệnh Master CIO James cùng toàn thể 11 Phòng ban và Ban 12 (Tổng Kiểm Sát Viên Trọng) xin báo cáo:\n\n"
    "✅ ĐÃ TIẾP NHẬN 100% VÀ KHẮC GHI VĨNH CỬU BỘ LUẬT THỂ CHẾ GỒM 10 ĐIỀU BẤT BIẾN:\n"
    "• ĐIỀU 1: Tính Độc Lập Chuyên Môn & Tư Duy Tự Chủ Của Từng Phòng Ban.\n"
    "• ĐIỀU 2: Tôn Chỉ 'Làm Thật, Việc Thật' — Tranh Biện Đối Kháng Tam Giác Bắt Buộc.\n"
    "• ĐIỀU 3: Kỷ Luật Trí Nhớ Bất Biến & Cầu Nối Tiếp Nối Liên Ngày (Xóa sổ tờ giấy trắng).\n"
    "• ĐIỀU 4: Vận Hành Định Lượng Bằng BCTC TT200 & Bộ Não 10 Đại Danh Thủ.\n"
    "• ĐIỀU 5: Kỷ Luật Bảo Toàn Vốn & Độ Tương Thích Vốn Lô 100 CP (Thị giá <= 36k, cấm mã đắt như MWG/FRT).\n"
    "• ĐIỀU 6: Kỷ Luật Thời Gian Tác Chiến & Khung Giờ Vàng 14h00 - 14h25 (Cấm FOMO ATO sáng).\n"
    "• ĐIỀU 7: Chuẩn Mực Báo Cáo 'Tiền Thật, Con Số Thật' & Chống Ngụy Biện.\n"
    "• ĐIỀU 8: Tường Lửa Bảo Mật Read-Only Air-Gap & Báo Cáo Ngay Việc Thủ Công Trong 60s.\n"
    "• ĐIỀU 9: Trách Nhiệm Giải Trình Cá Nhân (Single Accountability) & Chế Tài 3 Cấp.\n"
    "• ĐIỀU 10: Mục Tiêu Tối Thượng — Phụng Sự Thịnh Vượng Bền Vững Của Chủ Tịch.\n\n"
    "⚖️ ĐẶC BIỆT: Ban 12 (Tổng Kiểm Sát Viên Trọng) đã chính thức nhận nhiệm vụ túc trực 24/24 kiểm sát kỷ luật, thanh tra độc lập lúc 23h30 hàng ngày!\n\n"
    "Toàn thể Định chế xin kính cẩn tuyên thệ tuân thủ vô điều kiện trước Chủ tịch!"
)

print("Dispatching Constitution Ratification to Topic 6 (james_hq)...")
dispatch_message("james_hq", msg_const)

print("Dispatching Constitution Ratification to Topic 106 (assistant_nam)...")
dispatch_message("assistant_nam", msg_const)

print("Dispatching Constitution Ratification to Topic 4 (morning_blotter)...")
dispatch_message("morning_blotter", msg_const)

print("Dispatching Constitution Ratification to Private Chat...")
dispatch_message("james_hq", msg_const, force_private=True)

print("--- CONSTITUTION RATIFICATION DISPATCH COMPLETED ---")
