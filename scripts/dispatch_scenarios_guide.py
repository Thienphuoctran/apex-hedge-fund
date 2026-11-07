#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCH SCENARIO ACTION PLAN & MOBILE OPERATION GUIDE TO TELEGRAM JAMES HQ (TOPIC 6) & PRIVATE CHAT
File: scripts/dispatch_scenarios_guide.py
Cơ quan chủ quản: Master CIO James & Palmer Governance Desk
"""

import sys
import os
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message, send_raw_telegram, load_config

def main():
    cfg = load_config()
    bot_token = cfg.get("bot_token")
    private_chat_id = cfg.get("private_chat_id")

    # Bản Kế Hoạch Phần 1: Chi tiết 3 Kịch Bản Hành Động Chiều Nay
    part1 = (
        "📑 *[BỘ CHỈ HUY MASTER CIO JAMES — BẢN KẾ HOẠCH TÁC CHIẾN CHI TIẾT TỪNG KỊCH BẢN]*\n"
        "🏛️ *Cơ quan*: Master CIO Supreme Execution Desk\n"
        "👤 *Kính trình*: Chủ tịch Phước Trần (Tài khoản TCBS: `105C307855`)\n"
        "⏰ *Khung giờ thực thi*: `14h00 – 14h25` Chiều nay (05/11/2026)\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 *I. CHI TIẾT 3 KỊCH BẢN TÁC CHIẾN*:\n\n"
        "🟢 *KỊCH BẢN A: THỊ TRƯỜNG BÙNG NỔ — GIỮ NGUYÊN 100% SANG THỨ SÁU (TỐI ĐA HÓA LỢI NHUẬN)*\n"
        "• *Dấu hiệu lúc 14h00 - 14h15*: Lực mua chủ động áp đảo (*Buy Up ≥ 65%*), cả 3 mã mở rộng đà tăng: `MBB` giữ vững trên `19.45 – 19.50`, `TCB` công phá `22.00 – 22.10`, `HPG` đảo chiều xanh vượt `21.60`.\n"
        "• *Hành động*: *KHÔNG BÁN GÌ CẢ — GIỮ NGUYÊN 900 CP*.\n"
        "• *Kế hoạch Thứ Sáu (06/11)*: Canh nhịp hưng phấn đầu sáng mai (09h15 – 09h45) khi F0 đua lệnh giá xanh để chốt lời vùng đỉnh ngắn hạn:\n"
        "  + `MBB`: Chốt `19.80 – 20.00` (Lãi `+6.4% đến +7.5%`)\n"
        "  + `TCB`: Chốt `22.30 – 22.50` (Lãi `+4.4% đến +5.3%`)\n"
        "  + `HPG`: Chốt `21.80 – 22.00` (Lãi `+3.0% đến +4.0%`)\n"
        "  👉 *Tổng lãi dự phóng thu về*: *+750,000 ₫ đến +950,000 ₫*!\n\n"
        "🟡 *KỊCH BẢN B: LỰC CUNG T+2 GIA TĂNG — SCALING OUT CHỐT LỜI 50% TP1 (KHUYẾN NGHỊ TỐI ƯU)*\n"
        "• *Dấu hiệu lúc 14h00 - 14h15*: Thị trường xuất hiện nến rụt đầu, áp lực chốt lời hàng T+2 dồn dập khiến giá bị ép lùi: `MBB` chững ở `19.40 – 19.45`, `TCB` bị chặn ở `21.90 – 22.00`, `HPG` lùi về `21.40 – 21.45`.\n"
        "• *Hành động*: *BẤM LỆNH BÁN CHỐT LỜI 50% VỊ THẾ TẠI TP1*:\n"
        "  + `HPG`: Bán *200 CP* (còn giữ 200 CP) | Giá LO: `21.50 – 21.55` ➔ Thu về `~4,300,000 ₫`\n"
        "  + `TCB`: Bán *100 CP* (hoặc 150 CP) | Giá LO: `21.95 – 22.00` ➔ Thu về `~2,200,000 ₫`\n"
        "  + `MBB`: Bán *100 CP* (còn giữ 100 CP) | Giá LO: `19.45 – 19.50` ➔ Thu về `~1,950,000 ₫`\n"
        "• *Thành quả thu được*:\n"
        "  👉 Đút túi ngay *~250,000 ₫ tiền lãi tươi*, triệt tiêu hoàn toàn rủi ro đảo chiều!\n"
        "  👉 Nâng tiền mặt lên *~10,000,000 ₫ - 11,000,000 ₫ (50% NAV)* sẵn sàng gom hàng mới!\n"
        "  👉 Lô cổ phiếu còn lại gồng lãi sang Thứ Sáu *hoàn toàn miễn phí rủi ro* (*Risk-Free*) vì điểm Stop Loss đã dời lên giá vốn!\n\n"
        "🔴 *KỊCH BẢN C: RỦI RO THIÊN NGA ĐEN ĐẢO CHIỀU (PHÒNG THỦ KHẨN CẤP)*\n"
        "• *Dấu hiệu*: VN-Index bất ngờ lao dốc > 15 điểm, bán tháo hoảng loạn.\n"
        "• *Hành động*: Bán 100% toàn bộ 900 CP bằng lệnh LO khớp thẳng Giá 1 bên mua để bảo toàn 100% gốc!"
    )

    # Bản Kế Hoạch Phần 2: Cẩm Nang Thao Tác Từng Bước Trên App TCBS Điện Thoại
    part2 = (
        "📱 *II. CẨM NANG THAO TÁC 4 BƯỚC TRÊN APP TCBS MOBILE (CHUẨN TỪNG NÚT BẤM)*:\n"
        "Chủ tịch đang dùng điện thoại chỉ cần thao tác đơn giản theo 4 bước sau:\n\n"
        "🔹 *BƯỚC 1: KIỂM TRA ĐÚNG TIỂU KHOẢN*\n"
        "• Mở app TCBS ➔ Nhìn góc trên cùng màn hình:\n"
        "• Đảm bảo đang hiển thị **Tiểu khoản Thường** (số tài khoản `105C307855`). (Không chọn nhầm phái sinh hay ký quỹ margin).\n\n"
        "🔹 *BƯỚC 2: VÀO MỤC ĐẶT LỆNH BÁN*\n"
        "• Bấm nút đỏ nổi bật **ĐẶT LỆNH** (ở giữa phía dưới hoặc trong tab Cổ phiếu).\n"
        "• Chọn tab **BÁN** (Nút chuyển màu đỏ).\n\n"
        "🔹 *BƯỚC 3: NHẬP THÔNG SỐ LỆNH CHUẨN XÁC (CHO KỊCH BẢN B)*\n"
        "1. *Lệnh 1 — Cổ phiếu `HPG`*:\n"
        "   - Nhập mã: `HPG`\n"
        "   - Khối lượng: Nhập `200` CP (Lô chẵn 100)\n"
        "   - Loại lệnh: Chọn **LO** (Lệnh giới hạn)\n"
        "   - Giá: Nhập giá thị trường đang hiện (ví dụ `21.50` hoặc `21.55`)\n"
        "   - Bấm nút: **ĐẶT BÁN** ➔ Xác nhận mã OTP / FaceID.\n\n"
        "2. *Lệnh 2 — Cổ phiếu `TCB`*:\n"
        "   - Nhập mã: `TCB`\n"
        "   - Khối lượng: Nhập `100` CP (Khuyến nghị chẵn 100 CP để khớp trong 1 giây! Còn giữ 200 CP)\n"
        "   - Loại lệnh: Chọn **LO**\n"
        "   - Giá: Nhập `21.95` hoặc `22.00`\n"
        "   - Bấm nút: **ĐẶT BÁN** ➔ Xác nhận OTP.\n\n"
        "3. *Lệnh 3 — Cổ phiếu `MBB`*:\n"
        "   - Nhập mã: `MBB`\n"
        "   - Khối lượng: Nhập `100` CP (Lô chẵn, còn giữ 100 CP)\n"
        "   - Loại lệnh: Chọn **LO**\n"
        "   - Giá: Nhập `19.45` hoặc `19.50`\n"
        "   - Bấm nút: **ĐẶT BÁN** ➔ Xác nhận OTP.\n\n"
        "🔹 *BƯỚC 4: KIỂM TRA SỔ LỆNH*\n"
        "• Bấm sang tab **\"Sổ Lệnh\"** ngay cạnh mục Đặt lệnh:\n"
        "• Thấy trạng thái chuyển sang **\"Đã khớp\"** (Màu xanh lá) là hoàn tất 100%!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 *LƯU Ý ĐẶC BIỆT TỪ MASTER CIO JAMES*:\n"
        "• Hiện tại lúc `13h00 - 13h45`: Chủ tịch KHÔNG CẦN BẤM GÌ CẢ. Hãy để Sentinel Victor đo áp lực xả hàng T+2.\n"
        "• Đúng `14h00`, Master CIO James sẽ bắn tín hiệu chốt hạ: *\"Chủ tịch thực thi Kịch bản A\"* hoặc *\"Chủ tịch thực thi Kịch bản B\"* ngay vào Telegram này để Chủ tịch chỉ việc bấm theo kịch bản!"
    )

    print("[*] Đang gửi Bản Kế Hoạch Kịch Bản & Cẩm Nang Mobile sang Telegram James...")

    # Gửi vào Topic 6 (James HQ)
    ok1 = dispatch_message("james_hq", part1)
    ok2 = dispatch_message("james_hq", part2)

    # Gửi vào Private Chat để có Push Notification trực tiếp trên điện thoại
    ok_p1 = send_raw_telegram(bot_token, str(private_chat_id), part1, parse_mode="Markdown")
    ok_p2 = send_raw_telegram(bot_token, str(private_chat_id), part2, parse_mode="Markdown")

    print(f"[+] Kết quả gửi Topic 6: Part1={ok1}, Part2={ok2}")
    print(f"[+] Kết quả gửi Private Chat: Part1={ok_p1}, Part2={ok_p2}")

    if ok1 and ok2:
        print("[SUCCESS] Đã gửi trọn vẹn Kế Hoạch Từng Kịch Bản & Thao Tác Mobile tới Telegram Chủ tịch!")
        return 0
    else:
        print("[!] Có lỗi trong quá trình gửi tin nhắn.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
