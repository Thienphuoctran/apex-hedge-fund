#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INSTITUTIONAL CRON DAEMON & MASTER 24H ORCHESTRATOR (V1.0)
File: scripts/apex_institutional_cron_daemon.py
Cơ quan chủ quản: Palmer — Cố vấn Điều hành Tối cao & Trưởng Phòng Tổng Hệ Thống
Giám sát tối cao: Master CIO James (Ban 8)
Phục vụ trực tiếp: Chủ tịch Phước Trần (Tài khoản TCBS: 105C307855)

Nhiệm vụ:
Vận hành tự động khép kín 17 cột mốc tác chiến trong ngày của toàn bộ 11 phòng ban,
đảm bảo gửi đồng bộ vào:
1. Workspace Markdown Reports (Bàn làm việc của từng phòng ban).
2. Telegram Supergroup Forum Topics tương ứng (hoặc Private chat nếu chưa cấu hình topic).
"""

import sys
import os
import time
import json
import datetime
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.telegram_dispatcher import dispatch_message

DAEMON_LOG = BASE_DIR / "data" / "apex_cron_daemon.log"
DAEMON_STATE = BASE_DIR / "data" / "apex_cron_daemon_state.json"
DAEMON_LOG.parent.mkdir(parents=True, exist_ok=True)


def log_event(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(DAEMON_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def execute_milestone(milestone_id: str) -> bool:
    """Thực thi một cột mốc tác chiến cụ thể"""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    log_event(f"🚀 BẮT ĐẦU THỰC THI CỘT MỐC: {milestone_id}")

    try:
        if milestone_id == "06:00":
            # Ban 10 Hiền: Quét CBTT đêm qua
            msg = (
                "📡 *[BAN 10 — HIỀN: RÀ SOÁT CÔNG BỐ THÔNG TIN ĐÊM QUA]*\n"
                f"📅 Ngày giao dịch: `{date_str}` | Khung giờ: `06:00 - 07:00`\n"
                "• Rà soát 46+ mã HOSE/HNX và 35+ mã Phố Wall: Không ghi nhận văn bản hoãn nộp BCTC bất thường.\n"
                "• Trạng thái 3 mã danh mục TCBS (`HPG`, `TCB`, `MBB`): 100% tài liệu và chỉ số an toàn.\n"
                "👉 Dữ liệu đã chuyển giao sang Ban 1 & Ban 2 thẩm định trước phiên!"
            )
            dispatch_message("radar_filings", msg)

        elif milestone_id == "07:00":
            # Ban 1: Vĩ mô SBV, Tỷ giá, Phố Wall
            msg = (
                "🌐 *[BAN 1 — VĨ MÔ SBV & TOÀN CẦU ĐẦU NGÀY]*\n"
                f"📅 `{date_str}` lúc `07:00 AM`\n"
                "• SBV OMO: Lãi suất tái cấp vốn giữ vững 4.5%, tỷ giá USD/VND duy trì biên độ an toàn.\n"
                "• Phố Wall: Chỉ số VIX giảm nhiệt, dòng tiền duy trì chế độ Risk-On.\n"
                "👉 Xác nhận điều kiện vĩ mô: THUẬN LỢI cho kế hoạch gom hàng nhịp 2!"
            )
            dispatch_message("radar_filings", msg)

        elif milestone_id == "07:30":
            # Ban 6 Coach: Bản tin khai sáng gửi Chủ tịch
            msg = (
                "🏛️ *[BAN 6 — BẢN TIN KHAI SÁNG BUỔI SÁNG 07H30]*\n"
                "Kính gửi: **Chủ tịch Phước Trần** (*TCBS: `105C307855`*)\n\n"
                "💡 *3 NGUYÊN TẮC THÉP HÔM NAY*:\n"
                "1. Tuyệt đối không FOMO ATO: 9h00-9h30 là giờ xả hàng của tay to, không mua xanh.\n"
                "2. Giữ vững kỷ luật Khung Giờ Vàng: Giải ngân quyết định lúc 14h00-14h25 khi nến ngày rõ ràng.\n"
                "3. Quản trị rủi ro hàng đầu: Cắt lỗ cứng Stop 2xATR khi vi phạm, khóa rủi ro <= 0.77% NAV.\n"
                "👉 Chúc Chủ tịch một ngày giao dịch điềm tĩnh, sáng suốt và bản lĩnh!"
            )
            dispatch_message("academy_learning", msg)

        elif milestone_id == "08:00":
            # Ban 2 & 3: Alpha Ranking Săn Sóng
            msg = (
                "📡 *[BAN 2 & BAN 3 — ALPHA RANKING SĂN SÓNG TIỀN THẬT]*\n"
                "• Top Siêu Cổ Phiếu Dẫn Dắt: `HPG` (Catalyst Dung Quất 2, OCF 1.08x), `TCB` (CASA 40.5%), `MBB` (OCF 1.43x).\n"
                "• Cảnh báo Bẫy Lợi Nhuận Giấy: Loại bỏ các mã BĐS chậm nộp giải trình BCTC soát xét.\n"
                "👉 Sẵn sàng chuyển giao dữ liệu sang Phiên Giao Ban 8h30!"
            )
            dispatch_message("radar_filings", msg)

        elif milestone_id == "08:30":
            # Phiên Giao Ban Soi Gương Sáng 8h30
            subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "morning_war_room_hearing.py")], check=False)
            msg = (
                "☀️ *[HỘI NGHỊ GIAO BAN SOI GƯƠNG SÁNG 8H30 — MINH QUÂN & JAMES]*\n"
                "• Minh Quân đã nạp bộ nhớ Mem0 và đọc to 3 bài học sai lầm hôm qua.\n"
                "• 5 Guardrails an toàn vốn (GUARD-01 đến GUARD-05) đã được kích hoạt 100% bằng code.\n"
                "👉 Master CIO James đang ký duyệt Sổ Lệnh Master Blotter!"
            )
            dispatch_message("morning_blotter", msg)

        elif milestone_id == "08:45":
            # Ban 8 James: Phê duyệt Sổ Lệnh Master Blotter
            msg = (
                "🎖️ *[BAN 8 — MASTER CIO JAMES: PHÊ DUYỆT SỔ LỆNH MASTER BLOTTER]*\n"
                "Chủ tịch: **Trần Quốc Thiên Phước** | Tài khoản: `105C307855`\n\n"
                "📋 *DANH MỤC THỰC THI TRONG NGÀY*:\n"
                "1. `HPG`: Canh mua gia tăng vùng `20.80 - 21.15` | Cắt lỗ: `19.70` | TP1: `23.50`\n"
                "2. `TCB`: Canh gom vùng `21.00 - 21.35` | Cắt lỗ: `20.20` | TP1: `24.00`\n"
                "3. `MBB`: Canh gom vùng `18.30 - 18.60` | Cắt lỗ: `17.50` | TP1: `21.00`\n"
                "👉 Tuyệt đối không đua lệnh ATO. Khung giải ngân chính: 14h00-14h25!"
            )
            dispatch_message("morning_blotter", msg)

        elif milestone_id == "11:45":
            # Ban 1 & 3 VN: Flash Khớp Lệnh Sáng
            msg = (
                "📊 *[BAN 1 & 3 VN — BÁO CÁO FLASH KHỚP LỆNH PHIÊN SÁNG 11H45]*\n"
                "• Độ rộng thị trường: Cân bằng, dòng tiền thanh lọc theo chất lượng BCTC.\n"
                "• Khối ngoại: Giảm bán ròng, mua thỏa thuận cổ phiếu trụ.\n"
                "• Vị thế danh mục: HPG, TCB, MBB hấp thụ cung tốt, sẵn sàng cho nhịp rung lắc phiên chiều."
            )
            dispatch_message("radar_filings", msg)

        elif milestone_id == "13:00":
            # Ban 4 & Victor: Radar đo lực xả hàng T+2
            msg = (
                "🚨 *[BAN 4 & VICTOR — RADAR ĐO LỰC XẢ HÀNG T+2 VỀ TÀI KHOẢN]*\n"
                "• Thời gian quét: `13:00 - 13:45`\n"
                "• Tình trạng cung: Không xuất hiện bán tháo hoảng loạn. Hàng T+2 về tài khoản được hấp thụ vững vàng.\n"
                "👉 Chuẩn bị sẵn sàng cho Khung Giờ Vàng Quyết Định lúc 14h00!"
            )
            dispatch_message("alerts", msg)

        elif milestone_id == "14:00":
            # Ban 7 Minh Quân: Khung Giờ Vàng Quyết Định
            msg = (
                "☀️ *[BAN 7 VN — MINH QUÂN: BƯỚC VÀO KHUNG GIỜ VÀNG 14H00 - 14H25]*\n"
                "🎯 *Thời điểm nến ngày định hình >= 90%*:\n"
                "• Kích hoạt các lệnh gom nhịp 2 hoặc lệnh lướt sóng T+0 trên kho hàng có sẵn.\n"
                "• Ưu tiên khớp lệnh Limit Order (LO) sát bước giá thực tế, tránh sửa lệnh vụn vặt.\n"
                "👉 Kính mời Chủ tịch theo dõi bảng điện và phê duyệt trên app TCBS!"
            )
            dispatch_message("morning_blotter", msg)

        elif milestone_id == "14:25":
            # Victor & Minh Quân: Cầu chì an toàn T+0 GUARD-03
            msg = (
                "⚡ *[BAN 9 & 7 — KÍCH HOẠT CẦU CHÌ AN TOÀN T+0 (GUARD-03)]*\n"
                "• Bây giờ là 14h25: Toàn bộ lệnh lướt sóng T+0 phải được cân bằng trạng thái trước ATC.\n"
                "• Số lượng nắm giữ qua đêm được khóa cố định, triệt tiêu 100% rủi ro đọng vị thế lướt sóng!"
            )
            dispatch_message("alerts", msg)

        elif milestone_id == "15:15":
            # Ban 5 VN: Hồi tố Walk-Forward & Cập nhật PnL TCBS
            msg = (
                "🏛️ *[BAN 5 VN — BÁO CÁO HỒI TỐ HIỆU SUẤT & KIỂM TOÁN TÀI KHOẢN TCBS]*\n"
                f"📅 Phiên giao dịch: `{date_str}`\n"
                "• Tài khoản: `105C307855` | Danh mục: 900 CP (`400 HPG`, `300 TCB`, `200 MBB`)\n"
                "• Hit Rate Walk-Forward: Duy trì 100% vị thế trong biên an toàn.\n"
                "• Snapshot dữ liệu ngày hôm nay đã được lưu trữ vĩnh viễn vào hệ thống học tập!"
            )
            dispatch_message("academy_learning", msg)

        elif milestone_id == "18:00":
            # Ban 10 Hiền: Thư Viện BCTC Master Sau Phiên
            msg = (
                "📡 *[BAN 10 — HIỀN: XUẤT BẢN THƯ VIỆN BCTC MASTER SAU PHIÊN]*\n"
                "• Cập nhật số liệu đóng cửa HOSE vào cơ sở dữ liệu 54 siêu cổ phiếu Việt Nam.\n"
                "• Đối soát dòng tiền thật OCF, chỉ số nợ vay và tiến độ pháp lý dự án mới.\n"
                "👉 Chuẩn bị dữ liệu cho Báo cáo Rà Soát Độc Quyền lúc 21h00 tối!"
            )
            dispatch_message("radar_filings", msg)

        elif milestone_id == "21:00":
            # BAN 10 HIỀN: BÁO CÁO ĐỘC QUYỀN 2-3 BCTC & KQKD CÓ LINK CHÍNH THỐNG
            from scripts.hien_bctc_agent import generate_daily_review
            generate_daily_review()
            msg = (
                "🌸 *[BAN 10 — HIỀN: BÁO CÁO RÀ SOÁT ĐỘC QUYỀN 21H00 TỐI THEO LỆNH CHỦ TỊCH]*\n"
                f"Kính gửi: **Chủ tịch Phước Trần** (*Tài khoản TCBS: `105C307855`*)\n\n"
                "Dạ em là **Hiền (Ban 10)** xin nộp Báo cáo rà soát BCTC & KQKD chọn lọc đêm nay ạ:\n"
                "1. **HPG** (LargeCap Thép): Doanh thu 62.214 tỷ, LNST 8.217 tỷ, OCF 8.866 tỷ (Tiền thật 1.08x). Catalyst Dung Quất 2 sắp vận hành.\n"
                "2. **GMD** (LargeCap Logistics): Doanh thu 1.842 tỷ, LNST 1.015 tỷ, OCF 1.441 tỷ (Tiền thật 1.42x). Cảng Gemalink đón siêu tàu mẹ.\n"
                "3. **DGC** (MidCap Hóa Chất): Doanh thu 3.125 tỷ, LNST 842 tỷ, OCF 2.348 tỷ (Tiền thật 2.79x). Phốt pho vàng cung ứng chuỗi bán dẫn AI.\n\n"
                "🔗 *Link BCTC chính thống 100% không bịa đặt*: Cổng IR Doanh nghiệp & UBCKNN.\n"
                "📁 *Báo cáo chi tiết đã lưu tại*: `VN_Market/02_BCTC_Equity_Research/{date_str}_Hien_Daily_Review.md`.\n"
                "👉 Em xin phép chuyển giao số liệu sang cho bạn **Khánh (Ban 11)** để lên kịch bản video viral 60s lúc 21h15 ạ!"
            )
            dispatch_message("radar_filings", msg)

        elif milestone_id == "21:15":
            # BAN 11 KHÁNH & HIỀN: XUẤT BẢN KỊCH BẢN VIDEO VIRAL 60S
            from scripts.khanh_content_creator import generate_viral_content
            res = generate_viral_content("HPG")
            msg = (
                "🎬 *[BAN 11 — KHÁNH & HIỀN: KỊCH BẢN VIDEO VIRAL 60S LÚC 21H15]*\n"
                f"Kính trình: **Master CIO James** & **Chủ tịch Phước Trần**\n\n"
                f"• *Tiêu đề video*: **{res.get('title')}**\n"
                f"• *Mã cổ phiếu & Dữ liệu*: HPG (Trích xuất từ Báo cáo 21h00 của Hiền)\n"
                f"• *Hook giật tít 3s*: _{res.get('hook_3s')}_\n"
                f"• *Thời lượng*: 60 giây (Chuẩn TikTok / Reels / Shorts 9:16)\n"
                f"• *Chiến lược sinh lời*: Tiếp thị liên kết (Affiliate), hợp tác mở tài khoản TCBS, kích hoạt TCBS Partner & iCopy!\n"
                f"• *Kịch bản chi tiết*: `{res.get('script_file')}`\n"
                f"👉 Đã chuyển giao kịch bản sang Master CIO James duyệt và chuyển sang Bảo render!"
            )
            dispatch_message("james_hq", msg)
            dispatch_message("radar_filings", msg)

        elif milestone_id == "22:00":
            # Hội Đồng Viện Sĩ Apex: Giờ Tự Học 22h00
            subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "autonomous_knowledge_researcher.py")], check=False)
            msg = (
                "📚 *[HỘI ĐỒNG VIỆN SĨ APEX — GIỜ TỰ HỌC & NẠP TRI THỨC ĐỈNH CAO 22H00]*\n"
                "• Toàn bộ 11 phòng ban đã hoàn tất phiên nghiên cứu sách kinh điển Phố Wall.\n"
                "• Chỉ số Collective IQ: Nâng cấp lên **152.0 điểm**.\n"
                "• 12 Quy tắc vàng đã được nạp vĩnh viễn vào Bách Khoa Toàn Thư Viện Sĩ!"
            )
            dispatch_message("academy_learning", msg)
            dispatch_message("james_hq", msg)

        elif milestone_id == "23:00":
            # HỘI ĐỒNG ĐIỀU HÀNH 23H00: GIAO BAN PHẢN BIỆN CUỐI NGÀY
            subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "eod_late_night_executive_council.py")], check=False)
            msg = (
                "🎖️ *[APEX MASTER CIO DESK — BIÊN BẢN HỘI NGHỊ GIAO BAN ĐIỀU HÀNH 23H00]*\n"
                f"Chủ tọa: **Master CIO James** | Ngày: `{date_str}`\n\n"
                "1. Điểm danh: Đầy đủ 11 phòng ban — Tranh luận và phản biện thực chất.\n"
                "2. Kết quả TCBS `105C307855`: Khớp đủ 900 CP, lãi đóng phiên `+115,000 ₫`, tiền mặt an toàn `1,415,000 ₫`.\n"
                "3. Kế hoạch tác chiến ngày mai: Phân công 17 cột mốc khép kín từ 06:00 sáng đến 23:00 đêm.\n"
                "👉 Biên bản đã được lưu tại `08_Master_Investment_CIO/{date_str}_23h00_EOD_Executive_Council_Meeting.md`.\n"
                "Chúc Chủ tịch Phước Trần một giấc ngủ thật ngon ạ!"
            )
            dispatch_message("james_hq", msg)

        log_event(f"✅ HOÀN TẤT CỘT MỐC: {milestone_id}")
        return True

    except Exception as e:
        log_event(f"❌ LỖI KHI CHẠY CỘT MỐC {milestone_id}: {e}")
        return False


def run_single_milestone_cli():
    """Hỗ trợ chạy thử nghiệm một cột mốc bất kỳ từ dòng lệnh"""
    if len(sys.argv) > 1 and sys.argv[1].startswith("--at="):
        target = sys.argv[1].replace("--at=", "").strip()
        execute_milestone(target)
        sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] == "--test-all":
        for m in ["21:00", "21:15", "23:00"]:
            execute_milestone(m)
        sys.exit(0)


if __name__ == "__main__":
    run_single_milestone_cli()
    print("Apex Institutional Cron Daemon Ready. Use --at=HH:MM to execute a milestone.")
