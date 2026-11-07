#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH DEEP FORENSIC REPORT OF VIDEO 9 & 10 TO TELEGRAM
File: scripts/dispatch_video9_10_forensic.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.telegram_dispatcher import dispatch_message

sys.stdout.reconfigure(encoding='utf-8')

# Message: Master CIO James (Topic 6 & Private Chat)
msg_forensic = (
    "🔍 [BỘ CHỈ HUY TỔNG TƯ LỆNH JAMES] GIÁM ĐỊNH CHUYÊN SÂU 2 VIDEO KỸ THUẬT & ĐỊNH LƯỢNG MỚI\n\n"
    "Kính gửi: Chủ tịch Trần Quốc Thiên Phước\n"
    "Hội đồng 11 Phòng ban và Ban 12 (Tổng Kiểm Sát Viên Trọng) đã mổ xẻ chi tiết 2 video Chủ tịch cung cấp:\n\n"
    "1. VIDEO 1 (@SAMURAI.INVEST.PREMIUM — MÃ NKG):\n"
    "• Điểm hay: Rất minh bạch, dám show cả lệnh cắt lỗ (Vào 14.68 -> Ra 14.09); phân biệt rạch ròi giữa biến động 1 phiên (-2.80%) và vị thế giữ theo trend (+8.48% từ mốc 11.20).\n"
    "• Hạn chế: Thuần Price Action, bỏ qua BCTC & chu kỳ ngành thép; không khuyến nghị chốt lời từng phần (Scaling Out) dễ làm bốc hơi lãi.\n"
    "• Đánh giá tính xác thực: 90% (Dữ liệu khớp thực tế phiên 06/11).\n\n"
    "2. VIDEO 2 (@YIN.TP.TRADE — BẪY SIDEWAY ĐÁY CHỮ b):\n"
    "• Điểm cực hay: Kiến thức Volume Profile kinh điển! Bóc trần bẫy chữ 'b' — Sideway ở đáy đôi khi chỉ để gom thêm người mua bắt đáy rồi rơi tiếp theo bậc thang (Staircase dump)!\n"
    "• Bài học sống còn cho Quỹ: TUYỆT ĐỐI KHÔNG BẮT ĐÁY VỘI VÀNG khi VN-Index về 1.700 đầu tuần tới! Phải chờ tín hiệu bứt phá thoát khỏi vùng chữ 'b' mới giải ngân!\n"
    "• Đánh giá tính xác thực: 95%.\n\n"
    "🏆 GIÚP ÍCH TRỰC TIẾP CHO QUỸ: Giúp Quỹ tránh bẫy bắt dao rơi vào Thứ Hai, bảo vệ trọn vẹn 20.2M tiền mặt để gom hàng ở điểm an toàn nhất!\n\n"
    "Kính báo Chủ tịch!"
)

print("Dispatching Forensic Report to Topic 6 (james_hq)...")
dispatch_message("james_hq", msg_forensic)

print("Dispatching Forensic Report to Topic 4 (morning_blotter)...")
dispatch_message("morning_blotter", msg_forensic)

print("Dispatching Forensic Report to Topic 189 (hien_desk)...")
dispatch_message("hien_desk", msg_forensic)

print("Dispatching Forensic Report to Private Chat...")
dispatch_message("james_hq", msg_forensic, force_private=True)

print("--- FORENSIC REPORT DISPATCH COMPLETED ---")
