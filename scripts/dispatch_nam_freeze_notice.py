#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message

msg = (
    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
    "   💼 VĂN PHÒNG TRỢ LÝ NAM (APEX)\n"
    "   XÁC NHẬN TIẾP NHẬN LỆNH CHỦ TỊCH\n"
    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
    "Kính gửi: **Chủ tịch Phước Trần** (*Tài khoản TCBS: `105C307855`*)\n"
    "Người gửi: **Trợ Lý Nam** (*Văn phòng Trợ lý Cá nhân Topic 106*)\n\n"
    "Dạ em Nam xin long trọng báo cáo Chủ tịch:\n"
    "1. **Tiếp nhận chỉ thị**: Em đã ghi nhận lệnh ĐÓNG BĂNG DỰ ÁN 'Vũ trang Agent Zero Core Suite cho 11 phòng ban' để bảo toàn tuyệt đối hạn mức Token tuần này cho Chủ tịch.\n"
    "2. **Lưu trữ hồ sơ vĩnh viễn**: Em cùng anh Palmer đã đóng dấu và cất giữ toàn bộ 4 mô-đun thiết kế chi tiết tại:\n"
    "   📁 `08_Master_Investment_CIO/PROJECT_AGENT_ZERO_EXPANSION_BLUEPRINT.md` (Đã đồng bộ lên GitHub).\n"
    "3. **Lịch hẹn báo thức tự động**: Em đã cài đặt đồng hồ hệ thống. **ĐÚNG 08:00 SÁNG NGÀY 07/11/2026** (ngay khi Token tuần reset đầy bình), em Nam sẽ chủ động xuất bản thông báo đánh thức dự án tại phòng làm việc này để kính trình Chủ tịch phê duyệt bấm nút thi công ngay!\n"
    "4. **Cam kết chất lượng**: Em cam kết đến ngày đó sẽ không thiếu sót bất kỳ chi tiết nào, hồ sơ chuyên môn đạt chuẩn Quỹ đầu tư cao nhất, không sơ sài!\n\n"
    "Dạ chúc Chủ tịch một tuần làm việc thật thảnh thơi, mọi công việc vận hành hàng ngày của Quỹ em và các phòng ban vẫn túc trực 24/7 ạ!"
)

buttons = {
    "inline_keyboard": [
        [
            {"text": "📑 Xem Hồ Sơ Agent Zero Blueprint", "url": "https://github.com/Thienphuoctran/apex-hedge-fund/blob/main/08_Master_Investment_CIO/PROJECT_AGENT_ZERO_EXPANSION_BLUEPRINT.md"}
        ],
        [
            {"text": "⚡ Xem FounderOS Dashboard", "url": "https://github.com/Thienphuoctran/apex-hedge-fund/blob/main/dashboard/founderos.html"}
        ]
    ]
}

res = dispatch_message("assistant_nam", msg, reply_markup=buttons)
print("DISPATCH RESULT:", res)
