#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message

def main():
    msg_t6 = (
        "🎖️ *[BỘ CHỈ HUY MASTER CIO JAMES & PALMER: CHÍNH THỨC KÍCH HOẠT HỆ THỐNG KHÓA CHỐT GUARDRAILS & GIAO BAN SOI GƯƠNG 8H30]*\n\n"
        "Kính gửi: *Chủ tịch Phước Trần* (TCBS: `105C307855`)\n\n"
        "Thực hiện lệnh phê duyệt của Chủ tịch, Palmer và James đã chuyển hóa 100% các bài học sai lầm thành *Cơ chế Khóa Chốt Bằng Mã Nguồn (Hard-Coded Guardrails)*:\n\n"
        "🛡️ *5 LẰN RANH ĐỎ ĐÃ ĐƯỢC ÉP BẰNG CODE (IF... THEN... REJECT)*:\n"
        "1. *GUARD-01*: Tự động chặn 100% lệnh mua đuổi ATO trước 10h00 nếu giá tăng >= +2.0%.\n"
        "2. *GUARD-02*: Khóa quyền mua vĩnh viễn với cổ phiếu OCF âm hoặc Nợ D/E > 2.0x.\n"
        "3. *GUARD-03*: Kích hoạt cầu chì 14h25, ép buộc cân bằng vị thế T+0 trước phiên ATC.\n"
        "4. *GUARD-04*: Khóa trần rủi ro cắt lỗ Stop 2xATR <= 1.5% NAV (tối đa 300k đ trên 20tr).\n"
        "5. *GUARD-05*: Cấm tuyệt đối trung bình giá xuống dưới MA200.\n\n"
        "🏛️ *HỘI NGHỊ GIAO BAN 8H30 SÁNG*: Bắt đầu từ 8h30 sáng mai, Minh Quân bắt buộc đọc to 3 bài học sai lầm hôm trước trước khi Sổ lệnh được James phê duyệt!\n\n"
        "⚖️ *TRỌNG SỐ BIỂU QUYẾT ĐỘNG*: Ban 2 (BCTC & Tiền thật) được tăng quyền biểu quyết lên *35.0%* nhờ Hit Rate 100% trên 3 mã HPG, TCB, MBB!\n\n"
        "📂 Biên bản chi tiết: `08_Master_Investment_CIO/2026-11-03_Morning_War_Room_Pact.md`"
    )

    msg_t4 = (
        "☀️ *[MINH QUÂN BAN 7 VN — TUYÊN THỆ CHẤP HÀNH 5 KHÓA CHỐT GUARDRAILS]*:\n"
        "Minh Quân đã tiếp thu chỉ đạo của Chủ tịch và James. Toàn bộ sổ lệnh ngày mai sẽ được kiểm duyệt qua 5 chốt chặn an toàn vốn, kiên quyết kỷ luật trong Khung Giờ Vàng 14h00-14h25!"
    )

    ok6 = dispatch_message("james_hq", msg_t6)
    ok4 = dispatch_message("morning_blotter", msg_t4)
    print(f"DISPATCH TOPIC 6 (James): {ok6} | TOPIC 4 (Minh Quan): {ok4}")

if __name__ == "__main__":
    main()
