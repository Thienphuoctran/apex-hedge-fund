#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message

def main():
    msg = (
        "📚 *[HỘI ĐỒNG VIỆN SĨ APEX: KÍCH HOẠT GIỜ NGHIÊN CỨU & NẠP TRI THỨC ĐỈNH CAO 22H00]*\n\n"
        "Kính gửi: *Chủ tịch Phước Trần* (TCBS: `105C307855`)\n"
        "Cơ quan chủ trì: *Palmer (Governance) & Ban 6 (Học Viện Đào Tạo Thực Chiến)*\n\n"
        "Thực hiện ý tưởng xuất sắc của Chủ tịch về cơ chế *Tự động nghiên cứu & Nâng cấp chuyên môn mỗi ngày*, hệ thống đã chính thức kích hoạt:\n\n"
        "📖 *CHUYÊN ĐỀ HÔM NAY*: *VĨ MÔ TIỀN TỆ & MÔ HÌNH CHU KỲ NỢ LỚN (RAY DALIO)*\n"
        "• *Vấn đề bóc tách*: Cơ chế dòng tiền CASA của ngân hàng làm lá chắn chống sốc lãi suất.\n"
        "• *Ứng dụng danh mục*: Thẩm định nguồn vốn CASA 40.5% của Techcombank (TCB) và OCF 11.770 tỷ của MBBank (MBB).\n"
        "• *Đúc rút vào bộ não*: Ban hành Nguyên Lý Apex #12: *\"Lợi nhuận là phù phiếm, dòng tiền mới là sự thật!\"*\n\n"
        "📂 Thư viện nghiên cứu: `06_Investor_Academy_And_Mentorship/research_library/2026-11-03_Autonomous_Research_Digest.md`\n"
        "🏛️ Bách khoa tri thức: `data/apex_knowledge_vault/apex_institutional_encyclopedia.md`"
    )

    ok1 = dispatch_message("academy_learning", msg)
    ok2 = dispatch_message("james_hq", "📚 *[JAMES BẢO CHỨNG TRI THỨC]*: James đã phê duyệt tài liệu nghiên cứu hôm nay của Ban 6 và Ban 1. Kiến thức đã được nạp vào Bách Khoa Viện Sĩ để nâng cấp năng lực cho toàn bộ 11 phòng ban!")
    print(f"DISPATCH TO ACADEMY (Topic 112): {ok1} | TO JAMES (Topic 6): {ok2}")

if __name__ == "__main__":
    main()
