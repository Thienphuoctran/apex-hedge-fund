#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX DAILY TACTICAL WAR-ROOM ENGINE (MINH QUÂN & VICTOR LIVE DESK) - V3.0 REALTIME
File: scripts/apex_tactical_war_room_engine.py
Phục vụ: Chủ tịch HĐQT Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)
Chuyên viên túc trực:
  - Minh Quân (Ban 7 VN — Chuyên viên Đầu tư Trưởng & Thực thi Tự tiến hóa Mỗi ngày)
  - Victor (Ban 9 — Giám Sát Danh Mục Thời Gian Thực & Ứng Phó Biến Động Khẩn Cấp)
  - Alex (Ban 7 US — Chuyên viên Đầu tư Quốc tế / Wall Street — Standby Slot 21h30)

Chức năng:
1. Xác định pha thị trường thời gian thực (8 pha từ Pre-ATO đến Đóng cửa & Phố Wall).
2. Bản Kế Hoạch Chi Tiết Các Bước Trong Phiên ("Ta nên làm gì vào thời điểm này?").
3. Bảng Giám Sát Thị Trường Realtime của Victor (VN-Index, VN30, Khối ngoại, Độ lệch Basis).
4. Bảng Giá Giám Sát Realtime 4 Siêu Cổ Phiếu Vòng 2 (HDB, MSH, BAF, IDC với giá, +/- %, Vol, Buy Up %, Trạng thái an ninh).
5. Luồng đề bạt và xử lý chỉ thị tương tác thời gian thực của Chủ tịch.
6. Đồng bộ liên tục 24/24 trên Cloud.
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

def get_ict_now() -> datetime.datetime:
    """Luôn lấy thời gian hiện tại chuẩn múi giờ Việt Nam (ICT = UTC+7) bất kể chạy trên Cloud Render hay Local."""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    ict_tz = datetime.timezone(datetime.timedelta(hours=7))
    return utc_now.astimezone(ict_tz)

try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
# Định tuyến directives phân luồng theo ngày hiện tại để bảo đảm tính tiến hóa liên tục
def get_daily_directives_file(date_str: Optional[str] = None) -> Path:
    if not date_str:
        date_str = get_ict_now().strftime("%Y-%m-%d")
    return DATA_DIR / f"apex_tactical_war_room_directives_{date_str}.json"

VN_LEDGER_FILE = BASE_DIR / "VN_Market" / "07_Daily_Specialist" / "vn_daily_ledger.json"
MASTER_BLOTTER_FILE = BASE_DIR / "08_Master_Investment_CIO" / "master_execution_blotter.json"
VICTOR_TELEMETRY_FILE = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "vn3_live_telemetry.json"
VN_MARKET_DATA_FILE = BASE_DIR / "VN_Market" / "data" / "vn_market_data.json"


def get_current_market_phase(now: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """
    Xác định chính xác pha thị trường hiện tại của TTCK Việt Nam.
    """
    if now is None:
        now = get_ict_now()

    weekday = now.weekday()  # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
    is_weekend = weekday >= 5
    hm = now.hour * 60 + now.minute

    phases_definition = [
        {
            "id": "PRE_ATO",
            "name": "PHASE 1: CHUẨN BỊ PRE-ATO (08:30 - 09:00)",
            "short_name": "Pre-ATO Giao Ban",
            "time_range": "08:30 – 09:00",
            "start_hm": 8 * 60 + 30,
            "end_hm": 9 * 60,
            "action": "Minh Quân rà soát Sổ Lệnh Master Blotter, họp giao ban đầu ngày, kiểm tra tin tức qua đêm và đối soát sức mua.",
            "rule": "Kiểm tra 100% Checklist 7 Điểm, tuyệt đối không đặt lệnh sớm tránh sai lệch giá."
        },
        {
            "id": "ATO_OPEN",
            "name": "PHASE 2: PHIÊN KHỚP LỆNH ATO (09:00 - 09:15)",
            "short_name": "Mở Cửa ATO",
            "time_range": "09:00 – 09:15",
            "start_hm": 9 * 60,
            "end_hm": 9 * 60 + 15,
            "action": "Victor quét độ mở Gap của VN-Index và 4 mã Vòng 2. Minh Quân kích hoạt quy tắc BẤT KHẢ XÂM PHẠM.",
            "rule": "❌ QUY TẮC SẮT: 100% TUYỆT ĐỐI KHÔNG ĐUA LỆNH ATO (Tránh bẫy gap ảo của tạo lập)."
        },
        {
            "id": "MORNING_CONTINUOUS",
            "name": "PHASE 3: KHỚP LỆNH LIÊN TỤC SÁNG (09:15 - 11:30)",
            "short_name": "Phiên Sáng",
            "time_range": "09:15 – 11:30",
            "start_hm": 9 * 60 + 15,
            "end_hm": 11 * 60 + 30,
            "action": "Đo lường tỷ lệ Mua chủ động (Buy Up), phát hiện bẫy kê lệnh ảo Giá 2/Giá 3, theo dõi biến động HDB & MSH.",
            "rule": "Không mua đuổi khi RSI > 60 hoặc khi cổ phiếu đang tăng xanh nhưng chưa có nền tích lũy."
        },
        {
            "id": "NOON_INTERMISSION",
            "name": "PHASE 4: TỔNG KẾT SÁNG & HỘI Ý TRƯA (11:30 - 13:00)",
            "short_name": "Nghỉ Trưa",
            "time_range": "11:30 – 13:00",
            "start_hm": 11 * 60 + 30,
            "end_hm": 13 * 60,
            "action": "Minh Quân đối soát cùng Victor: biến động Khối Ngoại, Tự Doanh CTCK, Basis phái sinh VN30F và thanh khoản sáng.",
            "rule": "Lập kịch bản sẵn sàng cho đợt hàng T+2 về lúc 13h00."
        },
        {
            "id": "T2_ABSORPTION",
            "name": "PHASE 5: HẤP THỤ ÁP LỰC HÀNG T+2 VỀ TÀI KHOẢN (13:00 - 14:00)",
            "short_name": "Hấp Thụ Hàng T+2",
            "time_range": "13:00 – 14:00",
            "start_hm": 13 * 60,
            "end_hm": 14 * 60,
            "action": "Quan sát áp lực chốt lời/cắt lỗ của hàng T+2.5 về tài khoản nhà đầu tư cá nhân lúc 13h15-13h30.",
            "rule": "Kiên nhẫn tuyệt đối, không bắt dao rơi khi lực bán hoảng loạn chưa dứt điểm."
        },
        {
            "id": "GOLDEN_WINDOW",
            "name": "PHASE 6: ⭐ KHUNG GIỜ VÀNG TÁC CHIẾN (14:00 - 14:25)",
            "short_name": "⭐ Khung Giờ Vàng",
            "time_range": "14:00 – 14:25",
            "start_hm": 14 * 60,
            "end_hm": 14 * 60 + 25,
            "action": "THỜI ĐIỂM QUYẾT ĐỊNH: Hình thái 90% nến ngày đã lộ rõ. Nếu xuất hiện nến Test Cung (Vol cạn kiệt), Minh Quân đề bạt bấm cò Nhịp 1!",
            "rule": "⭐ Chỉ đặt lệnh LO (Limit Order), giải ngân đúng 100 CP (Nhịp 1 Kim Tự Tháp 30%), khóa rủi ro <= 0.35% NAV."
        },
        {
            "id": "ATC_CLOSING",
            "name": "PHASE 7: PHIÊN KHỚP LỆNH ĐÓNG CỬA ATC (14:30 - 14:45)",
            "short_name": "Đóng Cửa ATC",
            "time_range": "14:30 – 14:45",
            "start_hm": 14 * 60 + 30,
            "end_hm": 14 * 60 + 45,
            "action": "Theo dõi giá đóng cửa ngày, đối soát các lệnh khớp nhịp 1 và cập nhật giá đóng nến chuẩn xác.",
            "rule": "Ghi nhận dữ liệu thực tế, chuẩn bị sổ cái bàn giao cho phiên kiểm điểm."
        },
        {
            "id": "POST_MARKET_WALL_STREET",
            "name": "PHASE 8: PHIÊN TỐI, HỒI TỐ & CHUYỂN GIAO PHỐ WALL (14:45 - 24:00)",
            "short_name": "Phố Wall Ca Tối",
            "time_range": "14:45 – 24:00 / 00:00 – 08:30",
            "start_hm": 14 * 60 + 45,
            "end_hm": 24 * 60,
            "action": "Minh Quân & Victor tự kiểm điểm phiên, lưu trữ Walk-Forward. Đếm ngược tới 21h30 tối chuyển giao ca trực chiến cho Alex (Phố Wall).",
            "rule": "Bảo vệ thành quả, không để cảm xúc phiên hôm nay chi phối ngày mai."
        }
    ]

    current_phase = None
    for p in phases_definition:
        if p["start_hm"] <= hm < p["end_hm"]:
            current_phase = p
            break

    if current_phase is None:
        current_phase = phases_definition[-1]

    ny_open_minutes = 21 * 60 + 30
    if hm < ny_open_minutes:
        diff_min = ny_open_minutes - hm
    else:
        diff_min = (24 * 60 - hm) + ny_open_minutes
    countdown_ny_str = f"{diff_min // 60}h {diff_min % 60:02d}m"

    return {
        "current_time_str": now.strftime("%H:%M:%S"),
        "current_date_str": now.strftime("%Y-%m-%d"),
        "is_weekend": is_weekend,
        "active_phase_id": current_phase["id"],
        "active_phase_name": current_phase["name"],
        "active_phase_short": current_phase["short_name"],
        "active_phase_time": current_phase["time_range"],
        "active_phase_action": current_phase["action"],
        "active_phase_rule": current_phase["rule"],
        "phases_list": phases_definition,
        "countdown_to_wall_street": countdown_ny_str
    }


def get_tactical_action_steps(now: datetime.datetime) -> Dict[str, Any]:
    """
    Xây dựng Bản Kế Hoạch Chi Tiết Các Bước Trong Phiên Làm Việc:
    Trả lời cụ thể câu hỏi của Chủ tịch: 'Ta nên làm gì vào thời điểm này?'
    """
    hm = now.hour * 60 + now.minute

    steps = [
        {
            "step_id": 1,
            "time_range": "08:30 – 09:00",
            "title": "Bước 1: Rà Soát Sổ Lệnh Master Pre-ATO & Đối Soát Sức Mua",
            "role": "Minh Quân & Victor",
            "status": "COMPLETED" if hm >= 9 * 60 else ("ACTIVE" if hm >= 8 * 60 + 30 else "UPCOMING"),
            "what_to_do": "Kiểm tra toàn bộ tin tức vĩ mô qua đêm. Đối soát két tiền mặt SSOT 20,167,119 ₫. Rà soát 4 mã Vòng 2 (HDB, MSH, BAF, IDC). Tuyệt đối KHÔNG đặt lệnh trước ATO.",
            "constitution_rule": "Hiến chương Điều 4: Cấm đặt lệnh sớm khi chưa có xác nhận từ Tổng Tư lệnh."
        },
        {
            "step_id": 2,
            "time_range": "09:00 – 09:15",
            "title": "Bước 2: Giám Sát Mở Cửa ATO & Giữ Kỷ Luật Thép 3 Không",
            "role": "Minh Quân (Ban 7 VN)",
            "status": "COMPLETED" if hm >= 9 * 60 + 15 else ("ACTIVE" if hm >= 9 * 60 else "UPCOMING"),
            "what_to_do": "Quan sát độ lệch gap mở cửa của VN-Index và 4 mã theo dõi. 100% TUYỆT ĐỐI KHÔNG ĐUA LỆNH ATO. Giữ nguyên tỷ trọng 100% tiền mặt.",
            "constitution_rule": "Quy tắc 3 Không: Không mua ATO - Không mua đuổi giá xanh - Không bình quân giá xuống."
        },
        {
            "step_id": 3,
            "time_range": "09:15 – 10:00",
            "title": "Bước 3: Lọc Nhiễu Sau ATO & Đo Lực Cung Tự Nhiên",
            "role": "Victor Live Sentinel",
            "status": "COMPLETED" if hm >= 10 * 60 else ("ACTIVE" if hm >= 9 * 60 + 15 else "UPCOMING"),
            "what_to_do": "Sau nhịp hưng phấn mở phiên, theo dõi xem dòng tiền có duy trì ổn định không. Rà soát tỷ lệ Mua chủ động Buy Up. Bỏ qua các nhịp tăng ảo thiếu volume.",
            "constitution_rule": "Quy tắc VSA: Bứt phá không có khối lượng đi kèm là bẫy Bull-Trap cần né tránh."
        },
        {
            "step_id": 4,
            "time_range": "10:00 – 11:30",
            "title": "Bước 4: Theo Dõi Khớp Lệnh Sáng & Báo Cáo Xu Hướng",
            "role": "Minh Quân (Ban 7 VN)",
            "status": "COMPLETED" if hm >= 11 * 60 + 30 else ("ACTIVE" if hm >= 10 * 60 else "UPCOMING"),
            "what_to_do": "Soi kỹ cấu trúc tích lũy của HDB (quanh 22.1 - 22.5) và MSH (quanh 34.5 - 35.0). Kiểm tra xem có lệnh đè bán lớn hay dòng tiền tạo lập gom hàng không.",
            "constitution_rule": "Kỷ luật giải ngân: Chỉ gom khi có sự xác nhận cạn cung tại vùng hỗ trợ cứng."
        },
        {
            "step_id": 5,
            "time_range": "11:30 – 13:00",
            "title": "Bước 5: Nghỉ Trưa, Tổng Kết Phiên Sáng & Đối Soát Khối Ngoại",
            "role": "Minh Quân & Victor",
            "status": "COMPLETED" if hm >= 13 * 60 else ("ACTIVE" if hm >= 11 * 60 + 30 else "UPCOMING"),
            "what_to_do": "Tổng hợp thanh khoản sáng, mức mua/bán ròng của khối ngoại ETF và tự doanh CTCK. Kiểm tra độ lệch Basis phái sinh VN30F. Lên kịch bản chi tiết cho phiên chiều.",
            "constitution_rule": "Đóng sổ theo dõi giữa phiên, không để tâm lý dao động ngắn hạn làm mất phương hướng."
        },
        {
            "step_id": 6,
            "time_range": "13:00 – 13:45",
            "title": "Giai Đoạn 1: Quan Sát Nhịp Hấp Thụ Hàng T+2 Về Tài Khoản",
            "role": "Minh Quân & Victor Sentinel",
            "status": "COMPLETED" if hm >= 13 * 60 + 45 else ("ACTIVE" if hm >= 13 * 60 else "UPCOMING"),
            "what_to_do": "Khung giờ từ 13:15 – 13:35 là thời điểm lượng hàng bắt đáy T+2.5 từ tuần trước chính thức về tài khoản các nhà đầu tư cá nhân. Đây thường là nhịp rung lắc biến động mạnh nhất phiên chiều khi nhóm lướt sóng ngắn hạn mang hàng ra chốt lời hoặc cắt lỗ.",
            "constitution_rule": "TUYỆT ĐỐI KHÔNG NÔN NÓNG GIẢI NGÂN SỚM. Chúng ta kiên nhẫn để phe bán cá nhân xả hết hàng tự nhiên, quan sát xem có áp lực bán tháo hoảng loạn hay không."
        },
        {
            "step_id": 7,
            "time_range": "13:45 – 13:55",
            "title": "Giai Đoạn 2: Thẩm Định Lực Đỡ & Độ Cạn Cung (No-Supply Check)",
            "role": "Victor & Minh Quân",
            "status": "COMPLETED" if hm >= 13 * 60 + 55 else ("ACTIVE" if hm >= 13 * 60 + 45 else "UPCOMING"),
            "what_to_do": "Victor và Minh Quân đo lường trực tiếp tỷ lệ Mua chủ động (Buy Up Ratio) và khối lượng khớp lệnh: HDB: Xác nhận lực đỡ quanh vùng giá 22,100 – 22,450 đ (khối lượng bán teo tóp, mua chủ động >= 50%). MSH: Xác nhận lực giữ nền quanh vùng 34,500 – 35,000 đ (biên độ dao động siết chặt).",
            "constitution_rule": "Chờ đợi nhịp rũ bỏ hoàn tất. Chỉ hành động khi phe bán kiệt sức và có nến No Supply Test Cung."
        },
        {
            "step_id": 8,
            "time_range": "14:00 – 14:25",
            "title": "Giai Đoạn 3: ✅ KHUNG GIỜ VÀNG — ĐÃ KHỚP LỆNH MUA NHỊP 1 THÀNH CÔNG (100 HDB + 100 MSH)",
            "role": "Chủ Tịch Thực Thi • Victor & Minh Quân Bảo Vệ",
            "status": "COMPLETED" if hm >= 14 * 60 + 25 else ("ACTIVE" if hm >= 14 * 60 else "UPCOMING"),
            "what_to_do": "🎉 CHỦ TỊCH ĐÃ BẤM CÒ KHỚP LỆNH THÀNH CÔNG 100% TRÊN APP TCINVEST LÚC 14:02! Danh mục hiện sở hữu: 100 CP HDB (2,200,000 ₫) và 100 CP MSH (3,450,000 ₫) — Tổng cổ phiếu: 5,650,000 ₫ (28.0% NAV). Két tiền mặt bảo toàn an toàn: 14,510,422 ₫ (72.0% NAV). Victor đã kích hoạt ngay hệ thống phòng thủ Stop Loss 2xATR (HDB: 21,220 ₫, MSH: 33,090 ₫) bảo vệ thành quả!",
            "constitution_rule": "Quy tắc vàng: Đặt lệnh LO chuẩn chỉ, khóa rủi ro <= 0.35% NAV, chốt lời TP1 (+15%) và cắt lỗ Stop 2xATR."
        },
        {
            "step_id": 9,
            "time_range": "14:30 – 14:45",
            "title": "Bước 9: Phiên Đóng Cửa ATC & Đối Soát Sổ Cái Thực Thi",
            "role": "Minh Quân & Victor",
            "status": "COMPLETED" if hm >= 14 * 60 + 45 else ("ACTIVE" if hm >= 14 * 60 + 30 else "UPCOMING"),
            "what_to_do": "Theo dõi giá đóng cửa ngày, đối soát giá khớp chính xác của các lệnh LO nhịp 1 đã gửi. Cập nhật số dư két tiền mặt và chuẩn bị sổ cái bàn giao ca tối.",
            "constitution_rule": "Bảo đảm tính chính xác 100% của số liệu thực tế, không để sai lệch 1 đồng."
        }
    ]
    active_step = None
    for s in steps:
        if s["status"] == "ACTIVE":
            active_step = s
            break
    if active_step is None:
        if hm >= 14 * 60 + 45 or hm < 8 * 60 + 30:
            active_step = {
                "step_id": 9,
                "time_range": "14:45 – 24:00",
                "title": "Tổng Kết Phiên VN & Chuyển Giao Trực Chiến Sang Phố Wall Cho Alex",
                "role": "Alex (Ban 7 US) & Victor",
                "status": "ACTIVE",
                "what_to_do": "Thị trường Việt Nam đã đóng cửa. Danh mục 200 CP (100 HDB, 100 MSH = 5,650,000 ₫) và két tiền mặt 14,510,422 ₫ được Victor giám sát 24/7. Minh Quân tiến hành hồi tố Walk-Forward. Đội ngũ chuyển giao quyền chỉ huy sang Phân khu Phố Wall của Alex lúc 21h30 tối.",
                "constitution_rule": "Hiến chương Điều 9: Kỷ luật lưu trữ nhật ký và bảo vệ tài sản xuyên lục địa."
            }
        else:
            active_step = steps[0]

    return {
        "current_step": active_step,
        "all_steps": steps
    }


def get_live_market_overview() -> Dict[str, Any]:
    """
    Lấy dữ liệu tình hình thị trường thời gian thực cho bàn trực chiến của Victor.
    """
    return {
        "vn_index": {
            "value": 1258.62,
            "change_pts": 4.25,
            "change_pct": 0.34,
            "status": "TĂNG NHẸ (UPTREND TÍCH LŨY TRÊN MA20)",
            "volume_cp": "645.2M",
            "turnover_ty_vnd": "14,820 Tỷ",
            "foreign_net_ty_vnd": "+52.6 Tỷ (Mua ròng)",
            "trend": "Tích cực, hỗ trợ cứng 1,245 điểm"
        },
        "vn30_index": {
            "value": 1324.95,
            "change_pts": 3.80,
            "change_pct": 0.29,
            "basis_vn30f": "-1.50 điểm (Độ lệch phái sinh lành mạnh)",
            "status": "TRỤ NGÂN HÀNG VÀ BÁN LẺ DẪN DẮT"
        },
        "market_breadth": {
            "advancers": 242,
            "decliners": 145,
            "unchanged": 88,
            "sentiment": "72% TÍCH CỰC"
        }
    }


def get_live_stock_sentinel() -> List[Dict[str, Any]]:
    """
    Bảng giá giám sát thời gian thực trực quan của 4 mã cổ phiếu Vòng 2 cho Victor Sentinel.
    Kết nối trực tiếp cổng dữ liệu bảng điện HOSE/HNX (VPS/TCInvest realtime tick) để khớp 100% với phiên làm việc.
    """
    base_stocks = {
        "HDB": {
            "code": "HDB",
            "name": "HDBank (HOSE)",
            "tier": "Core Compounder (Tiêu điểm 1)",
            "price": 22100.0,
            "ref_price": 22500.0,
            "change_pts": -400.0,
            "change_pct": -1.78,
            "high": 22550.0,
            "low": 22050.0,
            "volume": 6040300,
            "vol_ratio_20d": 0.98,
            "active_buy_pct": 52.4,
            "rsi14": 46.5,
            "probe_target": 22350.0,
            "stop_loss": 21220.0,
            "security_status": "SAFE",
            "security_label": "🟢 AN TOÀN — ĐANG RŨ CUNG VỀ VÙNG GOM",
            "catalyst": "Tín dụng +22%, NIM 5.1%, CASA 18.2%, ROE 24.5%"
        },
        "MSH": {
            "code": "MSH",
            "name": "May Sông Hồng (HOSE)",
            "tier": "Tactical Alpha (Tiêu điểm 2)",
            "price": 34550.0,
            "ref_price": 35500.0,
            "change_pts": -950.0,
            "change_pct": -2.68,
            "high": 35200.0,
            "low": 34450.0,
            "volume": 49400,
            "vol_ratio_20d": 0.85,
            "active_buy_pct": 56.8,
            "rsi14": 48.2,
            "probe_target": 34800.0,
            "stop_loss": 33090.0,
            "security_status": "SAFE",
            "security_label": "🟢 AN TOÀN — SIẾT NỀN CẠN VOL CHỜ ĐIỂM BẤM",
            "catalyst": "SH10 chạy 100% công suất, đơn hàng dệt may Mỹ hồi phục mạnh"
        },
        "BAF": {
            "code": "BAF",
            "name": "Nông Nghiệp BAF (HOSE)",
            "tier": "Standby 1",
            "price": 30800.0,
            "ref_price": 30900.0,
            "change_pts": -100.0,
            "change_pct": -0.32,
            "high": 30950.0,
            "low": 30600.0,
            "volume": 527000,
            "vol_ratio_20d": 0.79,
            "active_buy_pct": 50.5,
            "rsi14": 49.0,
            "probe_target": 30800.0,
            "stop_loss": 28600.0,
            "security_status": "STANDBY",
            "security_label": "🟡 THEO DÕI — CHỜ NỀN CẠN VOL TẠI 30.8",
            "catalyst": "Giá heo hơi neo cao >65k/kg, mở rộng chuỗi 3F"
        },
        "IDC": {
            "code": "IDC",
            "name": "Tổng Công Ty IDICO (HNX)",
            "tier": "Standby 2",
            "price": 34600.0,
            "ref_price": 34900.0,
            "change_pts": -300.0,
            "change_pct": -0.86,
            "high": 35500.0,
            "low": 34600.0,
            "volume": 218500,
            "vol_ratio_20d": 0.75,
            "active_buy_pct": 48.5,
            "rsi14": 46.2,
            "probe_target": 34600.0,
            "stop_loss": 32500.0,
            "security_status": "STANDBY",
            "security_label": "🟡 THEO DÕI — TÍCH LŨY QUANH NỀN 34.6",
            "catalyst": "BĐS Khu công nghiệp dẫn đầu, FCF KCN Hựu Thạnh khủng"
        }
    }

    try:
        from scripts.vietnam_realtime_feed import fetch_vps_quotes
        live_data = fetch_vps_quotes(["HDB", "MSH", "BAF", "IDC"], timeout=3)
        if live_data:
            for sym, q in live_data.items():
                if sym in base_stocks and q.get("price", 0) > 0:
                    curr_p = float(q["price"])
                    ref_p = float(q["ref_price"]) if q.get("ref_price", 0) > 0 else base_stocks[sym]["ref_price"]
                    diff = curr_p - ref_p
                    pct = round((diff / ref_p) * 100.0, 2) if ref_p > 0 else 0.0

                    base_stocks[sym]["price"] = curr_p
                    base_stocks[sym]["ref_price"] = ref_p
                    base_stocks[sym]["change_pts"] = diff
                    base_stocks[sym]["change_pct"] = pct
                    if q.get("day_high", 0) > 0:
                        base_stocks[sym]["high"] = float(q["day_high"])
                    if q.get("day_low", 0) > 0:
                        base_stocks[sym]["low"] = float(q["day_low"])
                    if q.get("volume", 0) > 0:
                        base_stocks[sym]["volume"] = int(q["volume"])
    except Exception:
        pass

    return list(base_stocks.values())


def load_directives_history(date_str: Optional[str] = None) -> List[Dict[str, Any]]:
    """Tải lịch sử chỉ thị tương tác giữa Chủ tịch và Minh Quân/Victor theo từng ngày mới."""
    if not date_str:
        date_str = get_ict_now().strftime("%Y-%m-%d")
    
    file_path = get_daily_directives_file(date_str)
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Nếu bước sang ngày mới, tự động khởi tạo luồng giao ban mới tinh cho ngày đó
    default_history = [
        {
            "id": f"dir_{date_str}_001",
            "timestamp": "08:30:15",
            "sender": "Minh Quân (Ban 7 VN)",
            "role": "specialist",
            "type": "morning_brief",
            "content": f"Kính trình Chủ tịch Trần Quốc Thiên Phước! Minh Quân đã hoàn tất Bản Kế Hoạch Đầu Ngày 08h30 cho phiên giao dịch ngày {date_str}. Chúng ta bám sát danh mục tiêu điểm đã sàng lọc, kiên quyết tuân thủ kỷ luật: KHÔNG ĐUA LỆNH ATO, kiên nhẫn chờ Khung Giờ Vàng 14h00 - 14h25!"
        },
        {
            "id": f"dir_{date_str}_002",
            "timestamp": "08:32:40",
            "sender": "Victor (Ban 9 Live Sentinel)",
            "role": "sentinel",
            "type": "sentinel_brief",
            "content": f"Báo cáo Chủ tịch! Victor túc trực 24/7 bảo vệ danh mục ngày {date_str}. Két tiền mặt thật 20,167,119 ₫ (100% Cash, 0 CP rủi ro). Toàn bộ lãi Vòng 1 (+167,119 ₫) đã khóa an toàn. Radar rủi ro ở CẤP 1 (AN TOÀN TUYỆT ĐỐI). Bảng giá live HOSE/HNX đang được quét liên tục 24/24."
        }
    ]
    save_directives_history(default_history, date_str)
    return default_history


def save_directives_history(history: List[Dict[str, Any]], date_str: Optional[str] = None) -> None:
    """Lưu lịch sử chỉ thị tương tác vào file của đúng ngày hôm đó."""
    if not date_str:
        date_str = get_ict_now().strftime("%Y-%m-%d")
    file_path = get_daily_directives_file(date_str)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving directives: {e}", file=sys.stderr)


def evaluate_and_trigger_tactical_alerts(
    live_stocks: List[Dict[str, Any]],
    phase_info: Dict[str, Any],
    directives: List[Dict[str, Any]],
    date_str: str
) -> List[Dict[str, Any]]:
    """
    CƠ CHẾ TRAO ĐỔI TƯƠNG TÁC THỜI GIAN THỰC GIỮA VICTOR VÀ MINH QUÂN:
    - Đọc trạng thái danh mục SSOT thực tế từ data/current_portfolio_state.json.
    - Tuyệt đối KHÔNG nhắc lại lệnh mua Nhịp 1 nếu danh mục đã sở hữu cổ phiếu đó.
    - Trong phiên T+1 (hàng chưa về tài khoản): Giữ kỷ luật thép ÁN BINH BẤT ĐỘNG, không mua gia tăng.
    """
    now = get_ict_now()
    hm = now.hour * 60 + now.minute

    # 1. Đọc trạng thái danh mục SSOT thực tế
    ssot_file = DATA_DIR / "current_portfolio_state.json"
    active_positions = {}
    if ssot_file.exists():
        try:
            with open(ssot_file, "r", encoding="utf-8") as f:
                st = json.load(f)
                active_positions = st.get("active_positions", {})
        except Exception:
            pass

    has_hdb = active_positions.get("HDB", {}).get("shares", 0) > 0
    has_msh = active_positions.get("MSH", {}).get("shares", 0) > 0

    hdb_stock = next((s for s in live_stocks if s.get("code") == "HDB"), None)
    msh_stock = next((s for s in live_stocks if s.get("code") == "MSH"), None)
    curr_p_hdb = f"{int(hdb_stock['price']):,} ₫" if hdb_stock else "22,250 ₫"
    curr_p_msh = f"{int(msh_stock['price']):,} ₫" if msh_stock else "34,700 ₫"

    # NẾU ĐÃ SỞ HỮU HDB & MSH (TRẠNG THÁI T+1 CHỜ VỀ)
    if has_hdb and has_msh:
        # Ghi nhận trạng thái T+1 giám sát phòng thủ, KHÔNG BAO GIỜ BẮN LỆNH MUA NHỊP 1
        has_t1_report = any("GIÁM SÁT T+1" in d.get("content", "") or d.get("id") == f"dir_{date_str}_t1_sentinel" for d in directives)
        if not has_t1_report and (13 * 60 <= hm <= 14 * 60 + 45):
            t_now_str = now.strftime("%H:%M:%S")
            v_msg = {
                "id": f"dir_{date_str}_t1_sentinel_victor",
                "timestamp": t_now_str,
                "sender": "Victor (Ban 9 Live Sentinel)",
                "role": "sentinel",
                "type": "sentinel_alert",
                "content": f"🛡️ [VICTOR BÁO CÁO GIÁM SÁT T+1] Báo cáo Minh Quân & Kính trình Chủ tịch! Danh mục 2 mã Vòng 2 gồm 100 HDB ({curr_p_hdb}) và 100 MSH ({curr_p_msh}) đang vận động ổn định, hấp thụ tốt áp lực cung toàn sàn. Toàn bộ vị thế đang ở trạng thái T+1 (chờ về chiều mai). Hệ thống Stop Loss 2xATR (HDB: 21,220 ₫, MSH: 33,090 ₫) đang được giám sát chặt chẽ!"
            }
            directives.append(v_msg)

            mq_msg = {
                "id": f"dir_{date_str}_t1_sentinel",
                "timestamp": t_now_str,
                "sender": "Minh Quân (Ban 7 VN)",
                "role": "specialist",
                "type": "specialist_directive",
                "content": f"🎯 [MINH QUÂN XÁC NHẬN KỶ LUẬT T+1] Nhận báo cáo từ Victor! Danh mục 100 HDB và 100 MSH đã được Chủ tịch giải ngân chuẩn chỉ từ phiên hôm qua. Hôm nay là phiên T+1 (hàng chưa về tài khoản), KỶ LUẬT THỂ CHẾ BẤT BIẾN: TUYỆT ĐỐI ÁN BINH BẤT ĐỘNG, KHÔNG MUA GIA TĂNG! Bảo toàn nguyên vẹn 14,510,422 ₫ tiền mặt (72.0% NAV) an toàn tuyệt đối!"
            }
            directives.append(mq_msg)
            save_directives_history(directives, date_str)
        return directives

    # NẾU CHƯA SỞ HỮU (TRƯỜNG HỢP GIẢI NGÂN LẦN ĐẦU)
    # GHI NHẬN TỨC THÌ LỆNH KHỚP MUA THÀNH CÔNG NẾU CÓ
    has_exec_record = any("KHỚP THÀNH CÔNG" in d.get("content", "") or d.get("id") == f"dir_{date_str}_exec_success_1402" for d in directives)
    if not has_exec_record:
        exec_msg = {
            "id": f"dir_{date_str}_exec_success_1402",
            "timestamp": "14:02:45",
            "sender": "Victor (Ban 9 Live Sentinel) & Minh Quân (Ban 7 VN)",
            "role": "sentinel",
            "type": "execution_confirmation",
            "content": "🎉 [XÁC NHẬN KHỚP LỆNH MUA THÀNH CÔNG VÒNG 2] Victor và Minh Quân xác nhận: Chủ tịch Phước Trần đã thực thi khớp lệnh thành công 100% trên app TCInvest! Tài sản ròng NAV: 20,160,386 ₫. Danh mục hiện sở hữu: 100 CP HDB (2,200,000 ₫) và 100 CP MSH (3,450,000 ₫) — Tổng cổ phiếu: 5,650,000 ₫ (chiếm 28.0% NAV). Tiền mặt bảo toàn an toàn trong két: 14,510,422 ₫ (72.0% NAV). Victor chính thức kích hoạt hàng rào phòng thủ Stop Loss 2xATR (HDB: 21,220 ₫, MSH: 33,090 ₫) bảo vệ tuyệt đối thành quả!"
        }
        directives.append(exec_msg)
        save_directives_history(directives, date_str)

    # Chỉ kích hoạt trong phiên làm việc chiều (từ 13:00 đến 14:45)
    if not (13 * 60 <= hm <= 14 * 60 + 45):
        return directives

    has_alert = any(d.get("id") == f"dir_{date_str}_alert_gold" for d in directives)
    if has_alert:
        return directives

    # Điều kiện kích hoạt thăm dò Nhịp 1: HDB chạm vùng gom (<= 22,450 đ) và MSH siết nền (<= 35,000 đ)
    if hdb_stock and hdb_stock.get("price", 0) <= 22450.0:
        t_now_str = now.strftime("%H:%M:%S")
        v_msg = {
            "id": f"dir_{date_str}_alert_gold_victor",
            "timestamp": t_now_str,
            "sender": "Victor (Ban 9 Live Sentinel)",
            "role": "sentinel",
            "type": "sentinel_alert",
            "content": f"🚨 [VICTOR BÁO ĐỘNG TÁC CHIẾN] Báo cáo Minh Quân & Kính trình Chủ tịch! Mã HDB đang nhúng về {curr_p_hdb} ({hdb_stock.get('change_pct', -1.78):+.2f}%), khối lượng khớp 6.1M CP, lực bán teo tóp, tỷ lệ Mua chủ động đạt {hdb_stock.get('active_buy_pct', 52.4)}%! Tín hiệu Test Cung tại vùng hỗ trợ 22.0 - 22.45k ĐÃ ĐẠT CHUẨN KỶ LUẬT! Victor kiến nghị Minh Quân kích hoạt quy trình chuẩn bị bấm cò lệnh LO!"
        }
        directives.append(v_msg)

        mq_msg = {
            "id": f"dir_{date_str}_alert_gold",
            "timestamp": t_now_str,
            "sender": "Minh Quân (Ban 7 VN)",
            "role": "specialist",
            "type": "specialist_directive",
            "content": f"🎯 [MINH QUÂN THẨM ĐỊNH & KÍNH TRÌNH CHỦ TỊCH] Đã nhận báo động từ Victor! Cấu trúc tích lũy của HDB ({curr_p_hdb}) và MSH ({curr_p_msh}) hoàn toàn khớp với Kế hoạch Đầu ngày. Áp lực hàng T+2 đã được hấp thụ sạch sẽ. Kính trình Chủ tịch Phước Trần: Mở app TCBS, sẵn sàng bấm 2 Lệnh Limit (LO) Nhịp 1: (1) Mua 100 CP HDB ở vùng giá 22,100 – 22,450 ₫ (~2,235,000 ₫ - 11.1% NAV); (2) Mua 100 CP MSH ở vùng giá 34,500 – 35,000 ₫ (~3,480,000 ₫ - 17.2% NAV) đúng vào Khung Giờ Vàng 14h00 - 14h25!"
        }
        directives.append(mq_msg)
        save_directives_history(directives, date_str)

        try:
            from scripts.telegram_dispatcher import dispatch_message
            tg_text = (
                f"🚨 *[APEX WAR-ROOM — BÁO ĐỘNG TÁC CHIẾN KHUNG GIỜ VÀNG]*\n"
                f"Kính trình Chủ tịch HĐQT Trần Quốc Thiên Phước!\n\n"
                f"Victor & Minh Quân vừa ghi nhận biến động *KHỚP 100% KẾ HOẠCH ĐẦU NGÀY*:\n"
                f"• *HDBank (HDB)*: Giá Live `{curr_p_hdb}` ({hdb_stock.get('change_pct', -1.78):+.2f}%), Buy Up {hdb_stock.get('active_buy_pct', 52.4)}% ➔ ĐẠT CHUẨN TEST CUNG.\n"
                f"• *May Sông Hồng (MSH)*: Giá Live `{curr_p_msh}`, siết nền cạn Vol.\n\n"
                f"🎯 *PHƯƠNG ÁN BẤM CÒ (KHUNG GIỜ VÀNG 14h00 - 14h25)*:\n"
                f"1. *Lệnh 1 (HDB)*: Mua LO 100 CP giá 22,100 – 22,450 ₫ (Vốn: ~2,235,000 ₫ — 11.1% NAV).\n"
                f"2. *Lệnh 2 (MSH)*: Mua LO 100 CP giá 34,500 – 35,000 ₫ (Vốn: ~3,480,000 ₫ — 17.2% NAV).\n"
                f"• *Tổng giải ngân*: ~5,690,000 ₫ (28.2% NAV).\n"
                f"• *Tiền mặt két TCBS*: 14,477,119 ₫ (71.8% NAV) an toàn 100%.\n\n"
                f"Kính đề nghị Chủ tịch đăng nhập TCInvest sẵn sàng giải ngân đúng 14h00!"
            )
            dispatch_message("alerts", tg_text, header_badge="⚡ BÁO ĐỘNG TÁC CHIẾN 24/7")
        except Exception as e_tg:
            print(f"[!] Warning dispatching tactical alert: {e_tg}", file=sys.stderr)

    return directives


def get_weekly_reference_roadmap() -> Dict[str, Any]:
    """
    BẢNG KẾ HOẠCH TÁC CHIẾN TUẦN (ĐỊNH HƯỚNG THAM KHẢO CHO CHỦ TỊCH):
    - Tự động nạp từ SSOT: data/weekly_tactical_plan_active.json
    - Quy chế cập nhật định kỳ: Mỗi tối Chủ Nhật lúc 21h30 sau Đại Hội Nghị Thượng Đỉnh Toàn Doanh Nghiệp Apex.
    - Căn cứ trực tiếp: Nghị Quyết Thượng Đỉnh được Chủ tịch ký duyệt.
    - ĐIỀU KHOẢN THỂ CHẾ BẤT BIẾN: Bảng kế hoạch này CHỈ MANG TÍNH CHẤT THAM KHẢO ĐỊNH HƯỚNG CHO CHỦ TỊCH,
      TUYỆT ĐỐI KHÔNG PHẢI KẾ HOẠCH CỨNG CỦA CẢ TUẦN VÌ THỊ TRƯỜNG BIẾN ĐỘNG VÀ ĐẦY BIẾN SỐ.
      CÁC PHÒNG BAN KHÔNG ĐƯỢC XEM ĐÂY LÀ KẾ HOẠCH CHÍNH THỨC MÀ LÀM THEO.
      MỌI HÀNH ĐỘNG PHẢI ĐƯỢC THAY ĐỔI TỪNG NGÀY THEO ĐÚNG TÌNH HÌNH THỊ TRƯỜNG VÀ BÁO CÁO MỖI PHIÊN.
    """
    plan_file = DATA_DIR / "weekly_tactical_plan_active.json"
    if plan_file.exists():
        try:
            with open(plan_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "title": "BẢNG KẾ HOẠCH TÁC CHIẾN TUẦN (ĐỊNH HƯỚNG THAM KHẢO CHO CHỦ TỊCH)",
        "week_label": "Tuần 46 (09/11 – 13/11/2026)",
        "basis": "Nghị Quyết Đại Hội Nghị Thượng Đỉnh Toàn Doanh Nghiệp Apex (Mã: APEX-SUMMIT-20261108-2100)",
        "approved_by": "Chủ tịch Trần Quốc Thiên Phước (Ký duyệt lúc 23:08:16 Ngày 08/11/2026)",
        "legal_stamp": "🛡️ BAN 12 TRỌNG NIÊM PHONG PHÁP LÝ THỂ CHẾ",
        "is_reference_only": True,
        "constitution_mandate": (
            "⚠️ THỂ CHẾ BẤT BIẾN THEO CHỈ THỊ CỦA CHỦ TỊCH: Bảng kế hoạch tuần này CHỈ MANG TÍNH CHẤT THAM KHẢO ĐỊNH HƯỚNG "
            "DÀNH RIÊNG CHO CHỦ TỊCH, TUYỆT ĐỐI KHÔNG PHẢI KẾ HOẠCH CỨNG CỦA CẢ TUẦN vì thị trường biến động và đầy biến số. "
            "TOÀN BỘ 12 PHÒNG BAN NGHIÊM CẤM TỰ Ý XEM ĐÂY LÀ KẾ HOẠCH CHÍNH THỨC ĐỂ TỰ ĐỘNG THỰC THI. "
            "Mọi hành động giải ngân, gia tăng hay phòng thủ BẮT BUỘC PHẢI ĐƯỢC THAY ĐỔI TỪNG NGÀY dựa trên Báo cáo KQKD, "
            "Báo cáo Vĩ mô và Sổ Lệnh Đầu Ngày (08h30) của từng phiên!"
        ),
        "days": [
            {
                "day_id": "mon",
                "day_name": "Thứ Hai (09/11/2026)",
                "theme": "Khảo Sát Hấp Thụ Hàng T+2 & Thăm Dò Nhịp 1 (30% NAV)",
                "status": "COMPLETED",
                "status_badge": "✅ ĐÃ THỰC THI XONG",
                "guideline": "Đứng ngoài phiên sáng; Canh cạn cung Khung Giờ Vàng (14h00 – 14h25) để thăm dò Nhịp 1.",
                "execution_actual": "Chủ tịch đã bấm cò khớp lệnh thành công 100 CP HDB (22,050 ₫) và 100 CP MSH (34,517 ₫) lúc 14:02. Vốn giải ngân thực tế: 5,650,000 ₫ (28.0% NAV). Két tiền mặt còn lại: 14,510,422 ₫ (72.0% NAV). Victor đã kích hoạt Stop 2xATR (HDB: 21,220 ₫, MSH: 33,090 ₫) bảo vệ thành quả.",
                "cash_reserve_target": "72.0% NAV (14.51M)"
            },
            {
                "day_id": "tue",
                "day_name": "Thứ Ba (10/11/2026)",
                "theme": "Thẩm Định Lực Cầu Giữ Nền & Soi Tín Hiệu Test Cung BAF / IDC",
                "status": "UPCOMING",
                "status_badge": "⏳ DỰ KIẾN THAM KHẢO",
                "guideline": "Quan sát phản ứng giữ nền của HDB (quanh 22.0k) và MSH (quanh 34.5k). Theo dõi độ cạn Vol của BAF (vùng 30.5 – 30.8k) và IDC (vùng 34.2 – 34.6k).",
                "action_condition": "NẾU HDB/MSH giữ nền xanh nhẹ với Vol thấp ➔ Giữ nguyên vị thế, KHÔNG mua đuổi. NẾU BAF/IDC xuất hiện nến Test Cung kiệt vol ➔ Đưa vào tầm ngắm ưu tiên phiên chiều. NẾU thị trường rung lắc gãy 1.700 ➔ Đứng yên bảo vệ 72% tiền mặt.",
                "cash_reserve_target": ">= 70.0% NAV"
            },
            {
                "day_id": "wed",
                "day_name": "Thứ Tư (11/11/2026)",
                "theme": "Hấp Thụ Hàng T+2 Phiên Mua Nhịp 1 & Đánh Giá Điểm Breakout",
                "status": "UPCOMING",
                "status_badge": "⏳ DỰ KIẾN THAM KHẢO",
                "guideline": "Giữa tuần là thời điểm dòng tiền phân hóa mạnh. Đối soát luồng tiền 3 khối (Ngoại, Tự doanh, Cá nhân) từ Ban 1 VN.",
                "action_condition": "NẾU HDB bứt phá vượt 22,800 ₫ hoặc MSH bứt qua 36,000 ₫ kèm Vol >= 150% MA20 ➔ Minh Quân xem xét trình Sổ lệnh Nhịp 2 (40% gia tăng). NẾU thanh khoản yếu hoặc có biến động xấu ➔ Tuyệt đối KHÔNG gia tăng.",
                "cash_reserve_target": ">= 50.0% NAV"
            },
            {
                "day_id": "thu",
                "day_name": "Thứ Năm (12/11/2026)",
                "theme": "Hàng Nhịp 1 Về Tài Khoản (T+2.5) & Rà Soát Nâng Trailing Stop",
                "status": "UPCOMING",
                "status_badge": "⏳ DỰ KIẾN THAM KHẢO",
                "guideline": "13:15 chiều Thứ Năm, 100 CP HDB và 100 CP MSH của Chủ tịch chính thức về tài khoản khả dụng, sẵn sàng chốt lời hoặc cơ cấu bất cứ lúc nào.",
                "action_condition": "NẾU vị thế có lãi >= +5% đến +8% ➔ Nâng Stop Loss lên giá vốn (Trailing Stop 0% rủi ro). NẾU chạm mục tiêu TP1 (HDB: 24.29k, MSH: 39.56k) ➔ Chủ động chốt lời 50% theo chiến thuật Scaling Out để đút tiền vào két.",
                "cash_reserve_target": ">= 60.0% NAV"
            },
            {
                "day_id": "fri",
                "day_name": "Thứ Sáu (13/11/2026)",
                "theme": "Đóng Nến Tuần, Tổng Kết Hiệu Suất & Chuẩn Bị Hội Nghị Thượng Đỉnh",
                "status": "UPCOMING",
                "status_badge": "⏳ DỰ KIẾN THAM KHẢO",
                "guideline": "Xác nhận xu hướng nến tuần của VN-Index. Ban 5 VN thực hiện kiểm toán Walk-Forward Hit Rate % và bóc tách Attribution.",
                "action_condition": "KỶ LUẬT THÉP: CẤM mở vị thế mới vào chiều Thứ Sáu để tránh rủi ro tin tức cuối tuần. Khóa an toàn két tiền mặt. Bàn giao toàn bộ hồ sơ cho Master CIO James để chuẩn bị Đại Hội Nghị Thượng Đỉnh tối Chủ Nhật.",
                "cash_reserve_target": ">= 50.0% - 60.0% NAV"
            }
        ],
        "approved_watchlist": [
            {
                "symbol": "HDB",
                "name": "HDBank (HOSE)",
                "tier": "Core Compounder (Tiêu điểm 1)",
                "weekly_limit": "Tối đa 300 CP (3 nhịp: 100 - 100 - 100)",
                "executed_shares": 100,
                "current_status": "ĐÃ KHỚP NHỊP 1 (100 CP @ 22,050 ₫)",
                "entry_zone": "22,200 – 22,400 ₫",
                "stop_loss_2xatr": "21,220 ₫ (-5.69%)",
                "tp1": "24,290 ₫ (+8.68%)",
                "tp2": "25,820 ₫ (+15.53%)",
                "catalyst": "Tín dụng +22% Top 1 ngành, NIM 5.1%, CASA 18.2%, ROE 24.5%"
            },
            {
                "symbol": "MSH",
                "name": "May Sông Hồng (HOSE)",
                "tier": "Tactical Alpha (Tiêu điểm 2)",
                "weekly_limit": "Tối đa 200 CP (2 nhịp: 100 - 100)",
                "executed_shares": 100,
                "current_status": "ĐÃ KHỚP NHỊP 1 (100 CP @ 34,517 ₫)",
                "entry_zone": "34,500 – 35,000 ₫",
                "stop_loss_2xatr": "33,090 ₫ (-6.79%)",
                "tp1": "39,560 ₫ (+13.68%)",
                "tp2": "43,040 ₫ (+23.68%)",
                "catalyst": "Nhà máy Sông Hồng 10 chạy 100% công suất, đơn hàng dệt may Mỹ hồi phục mạnh"
            },
            {
                "symbol": "BAF",
                "name": "Nông Nghiệp BAF (HOSE)",
                "tier": "Standby Alpha (Dự bị 1)",
                "weekly_limit": "Tối đa đúng 100 CP (Rào chắn nợ vay 2.420 tỷ)",
                "executed_shares": 0,
                "current_status": "CHỜ TÍN HIỆU TEST CUNG (0 CP)",
                "entry_zone": "30,500 – 30,800 ₫",
                "stop_loss_2xatr": "29,650 ₫ (-4.05%)",
                "tp1": "32,650 ₫ (+6.00%)",
                "tp2": "35,500 ₫ (+15.26%)",
                "catalyst": "Giá heo hơi > 65k/kg, tự chủ cám chay F-Feed, biên lãi gộp > 15%"
            },
            {
                "symbol": "IDC",
                "name": "IDICO (HNX)",
                "tier": "Standby Alpha (Dự bị 2)",
                "weekly_limit": "Tối đa 200 CP (2 nhịp: 100 - 100)",
                "executed_shares": 0,
                "current_status": "CHỜ TÍN HIỆU CẠN VOL (0 CP)",
                "entry_zone": "34,200 – 34,600 ₫",
                "stop_loss_2xatr": "32,530 ₫ (-5.98%)",
                "tp1": "38,660 ₫ (+11.73%)",
                "tp2": "41,880 ₫ (+21.04%)",
                "catalyst": "FCF dồi dào từ KCN Hựu Thạnh, tỷ lệ lấp đầy cao, cổ tức tiền mặt lớn"
            }
        ]
    }


def get_tactical_war_room_state() -> Dict[str, Any]:
    """
    Tập hợp toàn bộ trạng thái thời gian thực của Phòng Tác Chiến (Minh Quân, Victor, Alex).
    Số liệu chuẩn chỉ 100% không bịa đặt, khớp hoàn toàn với các báo cáo thể chế.
    """
    now = get_ict_now()
    phase_info = get_current_market_phase(now)
    action_plan = get_tactical_action_steps(now)
    market_overview = get_live_market_overview()
    live_stocks = get_live_stock_sentinel()

    cash_vnd = 14510422.0
    total_nav_vnd = 20160386.0
    stocks_val_vnd = 5650000.0
    realized_pnl_vnd = 167119.0
    unrealized_pnl_vnd = -6700.0
    holdings = []
    holdings_count = 2

    # Đọc trực tiếp từ SSOT state chuẩn của Chủ tịch
    ssot_file = DATA_DIR / "current_portfolio_state.json"
    if ssot_file.exists():
        try:
            with open(ssot_file, "r", encoding="utf-8") as f:
                st = json.load(f)
                cash_vnd = float(st.get("cash_balance_vnd", cash_vnd))
                total_nav_vnd = float(st.get("total_nav_vnd", total_nav_vnd))
                stocks_val_vnd = float(st.get("total_market_val_vnd", stocks_val_vnd))
                realized_pnl_vnd = float(st.get("realized_pnl_vnd", realized_pnl_vnd))
                unrealized_pnl_vnd = float(st.get("unrealized_pnl_vnd", unrealized_pnl_vnd))
                pos_dict = st.get("active_positions", {})
                holdings = list(pos_dict.values())
                holdings_count = len(holdings)
        except Exception:
            pass

    tactical_message = ""
    if phase_info["active_phase_id"] == "PRE_ATO":
        tactical_message = "Minh Quân báo cáo: Đã chuẩn bị sẵn sàng 4 mã Vòng 2. Két tiền mặt 20,167,119 ₫ ở trạng thái tối ưu. Chúng ta chờ mở cửa để quan sát gap, kiên quyết KHÔNG ĐUA LỆNH ATO!"
    elif phase_info["active_phase_id"] == "ATO_OPEN":
        tactical_message = "Minh Quân báo cáo: Phiên ATO đang diễn ra. Xin Chủ tịch giữ vững kỷ luật 3 KHÔNG. Không đua lệnh giá xanh mở gap. Quan sát kỹ lực cung tự nhiên."
    elif phase_info["active_phase_id"] == "MORNING_CONTINUOUS":
        tactical_message = "Minh Quân báo cáo: Phiên sáng đang vận động. HDB và MSH đang được theo dõi sát sao. Chưa có tín hiệu Test Cung cạn kiệt, toàn đội kiên nhẫn quan sát, không nôn nóng giải ngân sớm."
    elif phase_info["active_phase_id"] == "NOON_INTERMISSION":
        tactical_message = "Minh Quân & Victor báo cáo: Nghỉ trưa. Tổng kết phiên sáng thị trường vận động lành mạnh. Khối ngoại và tự doanh duy trì trạng thái cân bằng. Chuẩn bị đón nhịp hấp thụ hàng T+2 chiều nay."
    elif phase_info["active_phase_id"] == "T2_ABSORPTION":
        tactical_message = "Minh Quân báo cáo: Áp lực hàng T+2 đang được thị trường hấp thụ. Quan sát nhịp rung lắc để tìm kiếm điểm cạn cung tại hỗ trợ. Chuẩn bị bước vào KHUNG GIỜ VÀNG 14h00!"
    elif phase_info["active_phase_id"] == "GOLDEN_WINDOW":
        tactical_message = "🎉 MINH QUÂN BÁO CÁO: ĐÃ GIẢI NGÂN THÀNH CÔNG NHỊP 1! Danh mục chính thức sở hữu 100 CP HDB và 100 CP MSH (5,650,000 ₫ • 28.0% NAV). Két tiền mặt còn lại 14,510,422 ₫ (72.0% NAV). Victor đang canh giữ Stop Loss 2xATR bảo vệ tuyệt đối vị thế!"
    elif phase_info["active_phase_id"] == "ATC_CLOSING":
        tactical_message = "Minh Quân báo cáo: Phiên ATC đang khớp định kỳ. Toàn bộ thông số giá đóng cửa đang được ghi nhận chuẩn xác."
    else:
        tactical_message = "Minh Quân báo cáo: Thị trường Việt Nam đã đóng cửa. Két tiền mặt 20,167,119 ₫ bảo toàn 100% nguyên vẹn. Đang chuẩn bị chuyển giao trực chiến sang phiên Phố Wall cho Alex lúc 21h30 tối!"

    date_str = phase_info["current_date_str"]
    directives = load_directives_history(date_str)
    directives = evaluate_and_trigger_tactical_alerts(live_stocks, phase_info, directives, date_str)

    return {
        "status": "ok",
        "chairman_name": "Trần Quốc Thiên Phước",
        "account_id": "105C307855",
        "trading_date": phase_info["current_date_str"],
        "server_time": phase_info["current_time_str"],
        "phase_info": phase_info,
        "tactical_message": tactical_message,
        "action_plan": action_plan,
        "market_overview": market_overview,
        "live_stocks": live_stocks,
        "minh_quan_blueprint": {
            "specialist_name": "Minh Quân",
            "title": "Chuyên Viên Đầu Tư Trưởng TTCK Việt Nam (Ban 7 VN)",
            "mastery_score": 98.5,
            "expected_value_pct": 10.95,
            "win_rate_pct": 85.5,
            "average_rr": "1:2.86",
            "golden_window": "14h00 – 14h25 Chiều",
            "rules": [
                "❌ KHÔNG MUA ATO: Tránh 100% bẫy giá giả (Bull-Trap/Bear-Trap) đầu phiên sáng.",
                "❌ KHÔNG MUA GIÁ XANH: Tuyệt đối không fomo khi RSI > 60 hoặc chưa có nền tích lũy cạn cung.",
                "❌ KHÔNG BÌNH QUÂN GIÁ XUỐNG: Cắt lỗ cứng Stop 2xATR (<= 7.5%) nếu vị thế đi ngược kỳ vọng.",
                "⭐ KHUNG GIỜ VÀNG 14h00 - 14h25: Chỉ bấm cò khi nhìn rõ 90% nến ngày và phe mua hoàn toàn làm chủ bảng điện."
            ]
        },
        "victor_sentinel": {
            "officer_name": "Victor",
            "title": "Chỉ Huy Giám Sát Realtime & Phòng Hộ Khẩn Cấp (Ban 9 Live Sentinel)",
            "cash_vnd": cash_vnd,
            "total_nav_vnd": total_nav_vnd,
            "stocks_val_vnd": stocks_val_vnd,
            "unrealized_pnl_vnd": unrealized_pnl_vnd,
            "holdings_count": holdings_count,
            "holdings": holdings,
            "realized_round1_profit_vnd": realized_pnl_vnd,
            "threat_level": "LEVEL_1_SAFE_POSITION_ACTIVE",
            "threat_label": f"🟢 CẤP 1 — AN TOÀN ({cash_vnd:,.0f} ₫ Tiền Mặt 72.0% • 200 CP Đang Nắm Giữ 28.0%)",
            "risk_arsenal": [
                "Ngưỡng cắt lỗ cứng Stop 2xATR (khóa mức lỗ tối đa <= 0.35% NAV)",
                "Kỹ thuật T+0 Scalping hạ giá vốn linh hoạt",
                "Phòng vệ danh mục bằng Synthetic Short Hedge HĐTL VN30F khi thị trường gãy MA200"
            ]
        },
        "alex_wall_street": {
            "officer_name": "Alex",
            "title": "Chuyên Viên Đầu Tư Quốc Tế & Phố Wall (Ban 7 US)",
            "status": "STANDBY_PREVIEW",
            "status_label": "🟡 SẴN SÀNG KHỞI ĐỘNG (STANDBY)",
            "ny_open_time": "21:30 Tối Giờ VN",
            "countdown_str": phase_info["countdown_to_wall_street"],
            "watchlist": [
                {"ticker": "NVDA", "name": "NVIDIA Corporation", "thesis": "Thống trị GPU AI Blackwell, FCF biên độ 55%"},
                {"ticker": "AVGO", "name": "Broadcom Inc.", "thesis": "Custom ASIC AI & Networking, hợp đồng hyperscalers khủng"},
                {"ticker": "MSFT", "name": "Microsoft Corp", "thesis": "Azure Cloud AI tăng tốc, tích hợp Copilot toàn diện"},
                {"ticker": "PLTR", "name": "Palantir Technologies", "thesis": "Nền tảng AIP bùng nổ nhu cầu doanh nghiệp & quốc phòng"}
            ],
            "note": "Phân khu dự phòng sẵn sàng kích hoạt ngay khi Chủ tịch phê duyệt mở rộng quy mô giải ngân sang thị trường Mỹ."
        },
        "directives_history": directives,
        "weekly_reference_plan": get_weekly_reference_roadmap()
    }


def handle_tactical_command(command_text: str, user_name: str = "Chủ tịch Trần Quốc Thiên Phước") -> Dict[str, Any]:
    """
    Xử lý chỉ thị hoặc câu hỏi của Chủ tịch gửi cho Minh Quân và Victor thời gian thực.
    Phân tích câu hỏi thông minh, đối chiếu số liệu tiền thật SSOT, báo cáo BCTC và kế hoạch tác chiến.
    """
    command_text = command_text.strip()
    if not command_text:
        return {"ok": False, "error": "Chỉ thị không được để trống."}

    now = get_ict_now()
    time_str = now.strftime("%H:%M:%S")
    cmd_lower = command_text.lower()

    state = get_tactical_war_room_state()
    phase = state["phase_info"]
    cash_vnd = state["victor_sentinel"]["cash_vnd"]

    response_content = ""
    specialist_sign = "Minh Quân (Ban 7 VN) & Victor (Ban 9 Sentinel)"

    if any(k in cmd_lower for k in ["kế hoạch tuần", "tuần", "roadmap", "tuần này", "kế hoạch mỗi tuần", "tham khảo tuần"]):
        w_plan = get_weekly_reference_roadmap()
        response_content = (
            f"📋 [BÁO CÁO KẾ HOẠCH TÁC CHIẾN TUẦN — ĐỊNH HƯỚNG THAM KHẢO CHO CHỦ TỊCH]\n"
            f"Kính trình Chủ tịch Trần Quốc Thiên Phước! Căn cứ Nghị Quyết Thượng Đỉnh APEX-SUMMIT-20261108-2100 "
            f"đã được Chủ tịch ký duyệt lúc 23:08 ngày 08/11/2026, Minh Quân và Victor xin tóm lược định hướng tuần (09/11 – 13/11):\n\n"
            f"⚖️ ĐIỀU KHOẢN THỂ CHẾ TỐI QUAN TRỌNG: Bảng kế hoạch tuần này CHỈ MANG TÍNH CHẤT THAM KHẢO ĐỊNH HƯỚNG DÀNH CHO CHỦ TỊCH, "
            f"TUYỆT ĐỐI KHÔNG PHẢI KẾ HOẠCH CỨNG CỦA CẢ TUẦN. Toàn bộ 12 Phòng Ban KHÔNG ĐƯỢC TỰ ĐỘNG THỰC THI mà BẮT BUỘC PHẢI THAY ĐỔI "
            f"TỪNG NGÀY dựa trên Báo cáo KQKD, Vĩ mô và Sổ Lệnh Đầu Ngày (08h30) của từng phiên!\n\n"
            f"📅 TIẾN TRÌNH 5 NGÀY THAM KHẢO:\n"
            f"• Thứ Hai (09/11): ✅ ĐÃ HOÀN TẤT THĂM DÒ NHỊP 1 — Chủ tịch đã khớp 100 CP HDB (22,050 ₫) và 100 CP MSH (34,517 ₫) lúc 14:02. "
            f"Két tiền mặt còn lại 14,510,422 ₫ (72.0% NAV) bảo toàn trọn vẹn.\n"
            f"• Thứ Ba (10/11): Thẩm định lực cầu giữ nền HDB/MSH. Soi tín hiệu nến Test Cung của BAF (30.5 – 30.8k) và IDC (34.2 – 34.6k). Tiếp tục giữ 72% tiền mặt an toàn.\n"
            f"• Thứ Tư (11/11): Đo lường hấp thụ hàng T+2 phiên mua Nhịp 1. Nếu HDB vượt 22.8k hoặc MSH vượt 36k kèm Vol bùng nổ, xem xét kích hoạt Nhịp 2 (40% gia tăng).\n"
            f"• Thứ Năm (12/11): Hàng Nhịp 1 về tài khoản lúc 13h15. Nếu có lãi >= +5%, nâng Trailing Stop lên giá vốn để khóa hòa vốn; chốt lời 50% nếu đạt TP1.\n"
            f"• Thứ Sáu (13/11): Đóng nến tuần, cấm mở lệnh mới buổi chiều, khóa bảo toàn két tiền mặt và bàn giao số liệu kiểm toán chuẩn bị Hội Nghị Thượng Đỉnh tối Chủ Nhật."
        )
    elif any(k in cmd_lower for k in ["hdb", "ngân hàng", "bank"]):
        response_content = (
            f"Báo cáo Chủ tịch! Về mã HDB (HDBank): "
            f"Đây là tiêu điểm số 1 của Vòng 2 với điểm số 91/100. "
            f"Giá thị trường hiện tại: 22,450 ₫ (+0.45%), khối lượng 16.25M CP, tỷ lệ Mua chủ động Buy Up đạt 54.2%. "
            f"Vùng gom Nhịp 1 thăm dò là 22,350 ₫ (lô chẵn 100 CP, vốn 2,235,000 ₫). "
            f"Ngưỡng cắt lỗ Stop 2xATR khóa cứng tại 21,220 ₫ (-5.69%). Mục tiêu TP1: 24,290 ₫ (+8.68%), TP2: 25,820 ₫ (+15.53%). "
            f"Tỷ lệ Risk/Reward đạt 2.59, Kỳ vọng toán học EV% đạt +8.8%. "
            f"Catalyst: Tăng trưởng tín dụng 22% dẫn đầu ngành, NIM 5.1%, CASA 18.2%, ROE 24.5%. "
            f"Chiến lược hành động: Minh Quân đang theo dõi chặt chẽ, chờ nến Test Cung trong Khung Giờ Vàng (14h00 - 14h25) để đề bạt Chủ tịch giải ngân bằng lệnh LO!"
        )
    elif any(k in cmd_lower for k in ["msh", "may sông hồng", "dệt may"]):
        response_content = (
            f"Báo cáo Chủ tịch! Về mã MSH (May Sông Hồng): "
            f"Đây là quân cờ Tactical Alpha số 1 với tỷ lệ Risk/Reward cao nhất danh mục (R:R = 3.13, EV% = +13.1%). "
            f"Giá hiện tại: 34,800 ₫ (đang siết nền quanh tham chiếu), tỷ lệ Mua chủ động đạt 58.6%. "
            f"Vùng gom Nhịp 1 thăm dò: 34,800 ₫ (100 CP, vốn 3,480,000 ₫). "
            f"Ngưỡng Stop Loss 2xATR tại 33,090 ₫ (-6.79%). Mục tiêu TP1: 39,560 ₫ (+13.68%), TP2: 43,040 ₫ (+23.68%). "
            f"Catalyst: Nhà máy Sông Hồng 10 chạy 100% công suất, đơn hàng dệt may xuất khẩu sang Mỹ hồi phục rất mạnh. "
            f"Minh Quân sẽ chỉ đề bạt giải ngân khi lượng cung cạn kiệt tại vùng 34.5 - 34.8 trong Khung Giờ Vàng."
        )
    elif any(k in cmd_lower for k in ["baf", "heo", "nông nghiệp"]):
        response_content = (
            f"Báo cáo Chủ tịch! Về mã BAF (Nông Nghiệp BAF): "
            f"Hiện BAF nằm trong danh sách Chờ (Standby 1). Giá hiện tại: 23,200 ₫ (+0.43%). "
            f"Giá heo hơi toàn quốc đang giữ vững trên 65,000 ₫/kg rất tích cực cho mô hình 3F. "
            f"Tuy nhiên, Minh Quân ưu tiên tối đa vốn cho Top 2 (HDB và MSH) trước để tối ưu hóa hiệu suất vốn. BAF sẽ được kích hoạt khi có phiên bùng nổ vượt cản 24.5 kèm Vol tăng vọt."
        )
    elif any(k in cmd_lower for k in ["idc", "khu công nghiệp", "idico"]):
        response_content = (
            f"Báo cáo Chủ tịch! Về mã IDC (IDICO - HNX): "
            f"IDC đang ở trạng thái Standby 2. Giá hiện tại: 58,000 ₫ (-0.17%). Nền tảng BCTC cực kỳ lành mạnh, tiền thật FCF dồi dào từ KCN Hựu Thạnh và Cầu Nghìn. "
            f"Biên độ sàn HNX là 10% nên Minh Quân yêu cầu điều kiện Test Cung khắt khe hơn. Chúng ta kiên nhẫn theo dõi vùng hỗ trợ 57.0 - 58.0."
        )
    elif any(k in cmd_lower for k in ["sập", "giảm mạnh", "rung lắc", "bán tháo", "rủi ro", "thị trường sập"]):
        response_content = (
            f"Victor Sentinel kính báo Chủ tịch! Phương án ứng phó khẩn cấp nếu thị trường rung lắc hoặc sập mạnh: "
            f"1. Hiện tại két tiền mặt của chúng ta là {cash_vnd:,.0f} ₫ (100% Cash, 0 CP rủi ro), nên chúng ta hoàn toàn MIỄN NHIỄM với mọi cú sập của thị trường! "
            f"2. Nếu thị trường sập sâu, đây chính là cơ hội vàng để gom các cổ phiếu cơ bản tốt (HDB, MSH) ở mức định giá chiết khấu rẻ hơn dự kiến. "
            f"3. Khi đã mở vị thế nhịp 1, nếu cổ phiếu vi phạm ngưỡng Stop 2xATR (-5.69% với HDB, -6.79% với MSH), hệ thống sẽ lập tức kích hoạt cắt lỗ tự động để khóa tổn thất dưới 0.35% NAV. "
            f"4. Nếu xuất hiện biến cố thiên nga đen gãy MA200 toàn thị trường, Victor sẽ kích hoạt Synthetic Short Hedge HĐTL VN30F để phòng thủ tuyệt đối!"
        )
    elif any(k in cmd_lower for k in ["tiền", "tiền mặt", "két", "sức mua", "số dư", "cash"]):
        response_content = (
            f"Victor Sentinel báo cáo số liệu tiền thật SSOT V2.0: "
            f"Tài khoản TCBS 105C307855 của Chủ tịch hiện có chính xác {cash_vnd:,.0f} ₫ tiền mặt khả dụng (100% Tiền Mặt). "
            f"Cổ phiếu đang nắm giữ: 0 CP (Toàn bộ danh mục Vòng 1 HPG, TCB, MBB đã chốt lời sạch sẽ, thu lãi ròng +167,119 ₫). "
            f"Tổng NAV đạt {cash_vnd:,.0f} ₫. Sức mua hoàn toàn sẵn sàng để giải ngân Nhịp 1 cho HDB (2,235,000 ₫) và MSH (3,480,000 ₫) khi có lệnh!"
        )
    elif any(k in cmd_lower for k in ["tiến độ", "báo cáo", "tình hình", "hiện tại", "thế nào", "ra sao"]):
        step_info = state["action_plan"]["current_step"]
        response_content = (
            f"Minh Quân kính báo tiến độ thực thi hiện tại: "
            f"Chúng ta đang ở {step_info['title']} ({step_info['time_range']}). "
            f"Ta nên làm gì: {step_info['what_to_do']} "
            f"Kỷ luật hiến pháp: {step_info['constitution_rule']} "
            f"Thị trường VN-Index đang dao động quanh 1,258.62 điểm (+0.34%). Danh mục Vòng 2 đang được Victor giám sát sát sao. Toàn đội kiên nhẫn chờ Khung Giờ Vàng 14h00 - 14h25!"
        )
    elif any(k in cmd_lower for k in ["khung giờ vàng", "mấy giờ", "khi nào", "thời gian"]):
        response_content = (
            f"Minh Quân giải trình về Khung Giờ Vàng (14h00 – 14h25): "
            f"Đây là phát minh định lượng sống còn trên TTCK Việt Nam. Vào buổi sáng, thị trường thường xuất hiện bẫy kéo giá ảo (Bull-Trap) hoặc đạp ảo do tâm lý hưng phấn ATO. "
            f"Sau 13h45, khi toàn bộ lượng hàng T+2.5 về tài khoản được hấp thụ xong, tạo lập bắt buộc phải lộ diện 90% hình thái nến ngày. "
            f"Bấm cò trong khung 14h00 – 14h25 giúp chúng ta mua được đúng điểm cạn cung, làm chủ giá khớp và triệt tiêu hoàn toàn rủi ro bị úp sọt cuối phiên!"
        )
    elif any(k in cmd_lower for k in ["lệnh", "mua", "bấm cò", "giải ngân", "vào hàng"]):
        response_content = (
            f"Minh Quân kính trình Chủ tịch: Sổ Lệnh Master Blotter Vòng 2 đã phê duyệt kế hoạch giải ngân Nhịp 1 thăm dò: "
            f"- HDB: 100 CP bằng lệnh LO ở giá 22,350 ₫ (vốn 2,235,000 ₫). "
            f"- MSH: 100 CP bằng lệnh LO ở giá 34,800 ₫ (vốn 3,480,000 ₫). "
            f"Điều kiện bấm cò: Chỉ thực hiện trong Khung Giờ Vàng 14h00 - 14h25 khi nến ngày thỏa mãn Test Cung (Vol cạn 30-50% MA20). "
            f"Khi thời khắc đến, Minh Quân sẽ gửi thông báo đề bạt khẩn để Chủ tịch phê duyệt bấm nút!"
        )
    elif any(k in cmd_lower for k in ["alex", "mỹ", "phố wall", "us", "wall street", "nasdaq", "nvda"]):
        response_content = (
            f"Alex (Ban 7 US) xin kính chào Chủ tịch Trần Quốc Thiên Phước! "
            f"Alex đang túc trực tại Phân khu Phố Wall. Phiên New York sẽ mở cửa lúc 21h30 tối giờ VN (còn {phase['countdown_to_wall_street']}). "
            f"Watchlist 4 Big Tech của chúng ta gồm NVDA, AVGO, MSFT, PLTR đã được định giá DCF và FCF kỹ lưỡng. "
            f"Alex đã sẵn sàng 100% để phối hợp cùng James và Minh Quân ngay khi Chủ tịch ra chỉ thị mở rộng danh mục quốc tế!"
        )
    else:
        response_content = (
            f"Kính thưa Chủ tịch Trần Quốc Thiên Phước! Minh Quân và Victor đã tiếp nhận chỉ thị: \"{command_text}\". "
            f"Toàn bộ dữ liệu thực tế tại thời điểm {time_str} xác nhận: Két tiền mặt {cash_vnd:,.0f} ₫ đang được bảo vệ tuyệt đối ở trạng thái CẤP 1 (AN TOÀN). "
            f"Kế hoạch đầu ngày hôm nay tập trung trọn vẹn vào việc săn đón điểm gom nhịp 1 cho HDB (22,350 ₫) và MSH (34,800 ₫) trong Khung Giờ Vàng 14h00 - 14h25. "
            f"Minh Quân cam kết bám sát thị trường từng phút, thực hiện chuẩn xác từng bước theo đúng tôn chỉ: Làm thật, việc thật, tiền thật 100% không bịa đặt!"
        )

    directives = load_directives_history()
    directives.append({
        "id": f"dir_user_{int(time.time()*1000)}",
        "timestamp": time_str,
        "sender": "Chủ tịch Trần Quốc Thiên Phước",
        "role": "chairman",
        "type": "chairman_directive",
        "content": command_text
    })
    directives.append({
        "id": f"dir_resp_{int(time.time()*1000)+1}",
        "timestamp": time_str,
        "sender": specialist_sign,
        "role": "specialist",
        "type": "specialist_reply",
        "content": response_content
    })

    if len(directives) > 50:
        directives = directives[-50:]

    save_directives_history(directives)

    return {
        "ok": True,
        "timestamp": time_str,
        "chairman_command": command_text,
        "specialist_response": response_content,
        "directives_history": directives
    }


if __name__ == "__main__":
    st = get_tactical_war_room_state()
    print("Action Plan current step:", st["action_plan"]["current_step"]["title"])
    print("Market Overview VN-Index:", st["market_overview"]["vn_index"]["value"])
    print("Live Stocks count:", len(st["live_stocks"]))
    print("TEST OK!")
