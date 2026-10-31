#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vn_mentor_engine.py - Học Viện Đào Tạo Thực Chiến & Huấn Luyện Viên Cá Nhân Cho NĐT Việt Nam
Chuyên trách Ban 6:
- Phát hành Bản Tin Khai Sáng Buổi Sáng lúc 7h30 sáng hàng ngày (trước giờ giao dịch).
- Đào tạo phương pháp mổ xẻ BCTC (Bảng CĐKT, KQKD, LCTT OCF/FCF) từ lý thuyết đến thực chiến.
- Kèm cặp tâm lý học hành vi: Vượt qua hội chứng FOMO ATO, sợ cắt lỗ, bắt dao rơi.
- Đặt câu hỏi phản biện Socratic và quản lý Sổ tay giao dịch cá nhân.
"""

import os
import sys
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
import json
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "vn_market_data.json")
BCTC_PATH = os.path.join(BASE_DIR, "data", "vn_bctc_analysis.json")
MENTOR_DIR = os.path.join(BASE_DIR, "06_Investor_Academy", "daily_mentorship")
BRIEFING_MD = os.path.join(MENTOR_DIR, f"{datetime.date.today()}_VN_Mentor_Briefing.md")

def run():
    print("=== [VN MENTOR ENGINE] BIÊN SOẠN BẢN TIN KHAI SÁNG 7H30 SÁNG CHO NHÀ ĐẦU TƯ ===")
    os.makedirs(MENTOR_DIR, exist_ok=True)
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        mkt = json.load(f)
    with open(BCTC_PATH, "r", encoding="utf-8") as f:
        bctc = json.load(f)

    macro = mkt.get("macro_vietnam", {})
    stocks = mkt.get("stocks", {})

    lines = [
        f"# BẢN TIN KHAI SÁNG BUỔI SÁNG & HUẤN LUYỆN ĐẦU TƯ THỰC CHIẾN (7H30 AM) — {today_str}",
        f"**Người hướng dẫn**: Huấn Luyện Viên Trưởng Học Viện Đầu Tư Thực Chiến (Ban 6 VN)",
        f"**Khung giờ phát hành**: **7h30 Sáng** (Dành 60 phút đọc kỹ BCTC & Chiến lược trước phiên giao ban 8h30 của Chuyên viên Minh Quân)",
        "",
        "---",
        "",
        "## 🌅 1. TỔNG QUAN TÂM LÝ ĐẦU NGÀY: THẾ GIỚI ĐÊM QUA TÁC ĐỘNG THẾ NÀO ĐẾN VN-INDEX?",
        f"- **Chỉ số S&P 500 & Chứng khoán Mỹ**: Tiếp tục xu hướng tích lũy, tâm lý giới đầu tư toàn cầu duy trì ổn định.",
        f"- **Chỉ số Đô la Mỹ (DXY)**: Đang neo quanh mức **{macro.get('DXY', {}).get('value')}**. Áp lực tỷ giá USD/VND đang được NHNN (SBV) kiểm soát chặt chẽ thông qua các công cụ điều tiết linh hoạt.",
        f"- **Giá Dầu thô WTI**: Ở mức **${macro.get('WTI_OIL', {}).get('value')}/thùng**. Tác động phân hóa tích cực lên nhóm cổ phiếu Dầu khí thượng nguồn (PVS, PVD).",
        f"- **Thông điệp mở phiên ATO**: Nhà đầu tư tuyệt đối không mua đuổi giá xanh tím trong 15 phút mở phiên ATO. Hãy quan sát lực cung cầu thực tế sau 9h30 khi dòng tiền tổ chức nhập cuộc.",
        "",
        "---",
        "",
        "## 🔍 2. BÀI HỌC THỰC CHIẾN HÔM NAY: 'NGHỆ THUẬT BÓC TÁCH DÒNG TIỀN THỰC OCF TRONG BCTC'",
        "",
        "> *'Doanh thu là phù phiếm, Lợi nhuận là ảo tưởng, chỉ có Tiền Mặt trong két sắt mới là Sự Thật.'*",
        "",
        "### 💡 Khái niệm cần nhớ:",
        "Nhiều nhà đầu tư mới (F0) thường chỉ nhìn vào con số **Lợi nhuận sau thuế (LNST)** trên Báo cáo Kết quả Kinh doanh. Nhưng một doanh nghiệp có thể báo lãi hàng nghìn tỷ đồng nhưng thực chất không có một đồng tiền mặt nào!",
        "",
        "### ⚠️ 3 Dấu hiệu Cảnh Báo Nguy Hiểm trên BCTC Doanh nghiệp Việt Nam:",
        "1. **Tỷ lệ OCF / LNST < 0**: Lợi nhuận dương nhưng Dòng tiền thuần từ Hoạt động Kinh doanh lại âm liên tiếp 2-3 năm. Đây là dấu hiệu doanh nghiệp bán chịu chưa thu được tiền hoặc bị đối tác chiếm dụng vốn.",
        "2. **Khoản Phải thu ngắn hạn tăng vọt**: Nếu Phải thu tăng nhanh gấp đôi tốc độ tăng trưởng Doanh thu, hãy đặt nghi vấn về tính xác thực của các hợp đồng bán hàng.",
        "3. **Tỷ lệ Dồn tích (Sloan Accrual Ratio) > 10%**: Sự chênh lệch quá lớn giữa Lợi nhuận kế toán và Dòng tiền OCF báo hiệu chất lượng lợi nhuận đang ở mức báo động.",
        "",
        "### 🏆 Ví dụ Cổ Phiếu Kiểu Mẫu Trong Danh Mục Hôm Nay:",
        "- **FPT**: OCF đạt hơn 9.400 tỷ VND, FCF > 5.200 tỷ VND, lượng tiền mặt và tiền gửi ngân hàng lên tới 29.000 tỷ VND.",
        "- **DGC**: Tiền mặt ròng dồi dào, nợ vay gần như bằng 0, OCF vượt LNST.",
        "- **HPG**: OCF đạt hơn 16.500 tỷ VND, đủ sức tự tài trợ phần lớn cho đại dự án Dung Quất 2 mà không bị căng thẳng đòn bẩy.",
        "",
        "---",
        "",
        "## 🧠 3. CÂU HỎI TƯ DUY PHẢN BIỆN SOCRATIC DÀNH CHO BẠN HÔM NAY",
        "",
        "1. *Nếu cổ phiếu bạn đang theo dõi tăng vọt 5% ngay trong phiên ATO nhưng BCTC của nó có dòng tiền OCF âm triền miên và nợ vay cao, bạn sẽ làm gì: Đua lệnh theo đám đông hay kiên nhẫn đứng ngoài?*",
        "2. *Bạn đã thiết lập mức dừng lỗ Stop 2xATR cho các vị thế trong tài khoản của mình trước giờ thị trường mở cửa chưa?*",
        "",
        "---",
        "",
        "## ⏰ LỊCH TRÌNH TIẾP THEO:",
        "- **7h30 - 8h30**: Thời gian dành riêng cho Nhà đầu tư nghiên cứu kỹ Báo cáo BCTC Ban 2 và Bản tin Huấn luyện này.",
        "- **8h30**: **Chuyên viên Đầu tư Trưởng Minh Quân (Ban 7)** sẽ kích hoạt Hội nghị Giao ban và ban hành **Bản Kế Hoạch Lệnh Thực Thi Khoa Học Trong Ngày (Pre-ATO Execution Blotter)** sẵn sàng cho phiên giao dịch 9h00!",
        ""
    ]

    with open(BRIEFING_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"=== Đã hoàn tất Bản tin Khai sáng 7h30 sáng tại: {BRIEFING_MD} ===")

if __name__ == "__main__":
    run()
