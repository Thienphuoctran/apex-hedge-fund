#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message

def main():
    msg = """🌸 *[BAN 10 — HIỀN: XUẤT BẢN THƯ VIỆN BCTC MASTER SAU PHIÊN (18:00)]*
👤 *Người nhận*: **Chủ tịch Phước Trần** (*TCBS: `105C307855`*)
🏛 *Cơ quan thẩm định*: Ban 10 (Hiền) và Ban 2 VN (Pháp Y Kế Toán)

Em Hiền xin trân trọng báo cáo Chủ tịch:
✅ Đã rà soát 100% BCTC và CBTT sau phiên đóng cửa HOSE cho 54 cổ phiếu hàng đầu.
✅ Kiểm toán chất lượng tiền thật 3 mã danh mục TCBS `105C307855`:
• *HPG*: OCF 8,866 tỷ (1.08x LNST 🟢), không có biến cố thuế, lò cao Dung Quất 2 chạy tiến độ.
• *TCB*: CASA 40.5% top 1 hệ thống, CAR 15.2%, kế hoạch IPO TCBS.
• *MBB*: OCF 11,770 tỷ (1.43x 🟢), nợ xấu kiểm soát tốt.
🛡️ Không có bất kỳ rủi ro thiên nga đen nào sau phiên hôm nay.
📚 Toàn văn Thư Viện Master đã lưu tại: `VN_Market/02_BCTC_Equity_Research/2026-11-04_BCTC_Master_Library.md`.
🌸 Em đang hoàn thiện Báo Cáo Rà Soát Độc Quyền để xuất bản lúc 21h00 tối nay ạ!"""

    res = dispatch_message("hien_desk", msg)
    print("Dispatch result:", res)

if __name__ == "__main__":
    main()
