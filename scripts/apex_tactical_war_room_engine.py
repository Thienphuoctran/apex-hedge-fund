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


def _ensure_project_root_in_path() -> None:
    root_str = str(BASE_DIR)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def _get_live_snapshot(force_refresh: bool = False) -> Dict[str, Any]:
    """Lấy toàn bộ snapshot thời gian thực từ Living Intraday Brain (cache 10s trong phiên, 30s ngoài giờ)."""
    _ensure_project_root_in_path()
    from scripts.apex_live_intraday_brain import compute_live_war_room_snapshot
    now_ict = get_ict_now()
    hm = now_ict.hour * 60 + now_ict.minute
    in_session = (now_ict.weekday() < 5) and (8 * 60 + 45 <= hm <= 15 * 60)
    ttl = 10.0 if in_session else 30.0
    return compute_live_war_room_snapshot(force_refresh=force_refresh, cache_ttl=ttl)


def get_tactical_action_steps(
    now: datetime.datetime,
    snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Xây dựng Bản Kế Hoạch Chi Tiết Các Bước Trong Phiên Làm Việc (100% Live Dynamic SSOT + Regime).
    Trả lời cụ thể câu hỏi của Chủ tịch: 'Ta nên làm gì vào thời điểm này?'
    """
    hm = now.hour * 60 + now.minute
    snap = snapshot or _get_live_snapshot()
    port = snap.get("portfolio_live", {})
    regime = snap.get("intraday_regime", {})
    live_stocks = snap.get("live_stocks", [])
    dynamic_picks = snap.get("dynamic_picks", [])

    cash_vnd = float(port.get("cash_vnd", 0.0))
    cash_pct = float(port.get("cash_pct", 100.0))
    stocks_val_vnd = float(port.get("stocks_val_vnd", 0.0))
    stocks_pct = float(port.get("stocks_pct", 0.0))
    total_nav_vnd = float(port.get("total_nav_vnd", cash_vnd))
    total_shares = int(port.get("total_shares", 0))
    holdings = port.get("holdings", [])
    holdings_desc = port.get("holdings_desc", "0 CP")

    picks_codes = ", ".join(p.get("code", "") for p in dynamic_picks[:4]) or ", ".join(s.get("code", "") for s in live_stocks[:4]) or "Watchlist SSOT"
    if holdings:
        hold_details = " | ".join(
            f"{h.get('shares', 0)} {h.get('symbol', '')} (Live {float(h.get('current_price', 0)):,.0f} đ, PnL {float(h.get('pnl_pct', 0)):+.2f}%, Stop {float(h.get('stop_loss', 0)):,.0f} đ)"
            for h in holdings
        )
    else:
        hold_details = "0 CP (100% Tiền mặt bảo toàn)"

    buy_candidates = [s for s in live_stocks if not s.get("is_holding") and s.get("action_code") in ("BUY_ZONE", "NEAR_BUY_WATCH")]
    standby_text = " | ".join(
        f"{s['code']} (Giá {s['price']:,.0f} đ, Mục tiêu gom {s['probe_target']:,.0f} đ, BuyUp {s['active_buy_pct']:.1f}%)"
        for s in (buy_candidates[:2] or live_stocks[:2])
    ) or "Chờ tín hiệu cạn cung"

    alert_stocks = [s for s in live_stocks if s.get("action_code") in ("STOP_TRIGGERED", "NEAR_STOP_WARNING", "TP1_REACHED", "TP2_REACHED")]
    if alert_stocks:
        alert_summary = " ⚠️ CẢNH BÁO LIVE: " + "; ".join(
            f"{s['code']} [{s['security_label']}]" for s in alert_stocks
        )
    else:
        alert_summary = f"Trạng thái vị thế ổn định ({hold_details})."

    max_alloc = int(regime.get("max_new_allocation_pct", 30))
    regime_label = regime.get("label", "GIẰNG CO PHÂN HÓA")
    regime_guidance = regime.get("guidance", "")

    steps = [
        {
            "step_id": 1,
            "time_range": "08:30 – 09:00",
            "title": "Bước 1: Rà Soát Sổ Lệnh Master Pre-ATO & Đối Soát Sức Mua SSOT",
            "role": "Minh Quân & Victor",
            "status": "COMPLETED" if hm >= 9 * 60 else ("ACTIVE" if hm >= 8 * 60 + 30 else "UPCOMING"),
            "what_to_do": (
                f"Đối soát két tiền mặt SSOT {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV) & vị thế đang giữ: {hold_details}. "
                f"Theo dõi rổ mục tiêu động: {picks_codes}. Tuyệt đối KHÔNG đặt lệnh trước ATO."
            ),
            "constitution_rule": "Hiến chương Điều 4: Cấm đặt lệnh sớm khi chưa qua lọc nhiễu ATO."
        },
        {
            "step_id": 2,
            "time_range": "09:00 – 09:15",
            "title": "Bước 2: Giám Sát Mở Cửa ATO & Giữ Kỷ Luật Thép 3 Không",
            "role": "Minh Quân (Ban 7 VN)",
            "status": "COMPLETED" if hm >= 9 * 60 + 15 else ("ACTIVE" if hm >= 9 * 60 else "UPCOMING"),
            "what_to_do": (
                f"Victor quét độ lệch Gap mở cửa của VN-Index và rổ {len(live_stocks)} mã SSOT. "
                f"100% TUYỆT ĐỐI KHÔNG ĐUA LỆNH ATO. Bảo toàn nguyên vẹn {cash_vnd:,.0f} đ tiền mặt ({cash_pct:.1f}% NAV)."
            ),
            "constitution_rule": "Quy tắc 3 Không: Không mua ATO - Không mua đuổi giá xanh - Không bình quân giá xuống."
        },
        {
            "step_id": 3,
            "time_range": "09:15 – 10:00",
            "title": "Bước 3: Lọc Nhiễu Sau ATO & Đo Lực Cung Tự Nhiên",
            "role": "Victor Live Sentinel",
            "status": "COMPLETED" if hm >= 10 * 60 else ("ACTIVE" if hm >= 9 * 60 + 15 else "UPCOMING"),
            "what_to_do": (
                f"Đo lường 3 bước giá (Bid/Ask 1-3) và tỷ lệ Mua chủ động (Buy Up %). "
                f"Chế độ thị trường hiện tại: {regime_label} (Hạn mức giải ngân mới tối đa {max_alloc}% Cash). {alert_summary}"
            ),
            "constitution_rule": "Quy tắc VSA: Bứt phá không có khối lượng đi kèm là bẫy Bull-Trap cần né tránh."
        },
        {
            "step_id": 4,
            "time_range": "10:00 – 11:30",
            "title": "Bước 4: Theo Dõi Khớp Lệnh Sáng & Độ Rộng Thị Trường",
            "role": "Minh Quân (Ban 7 VN)",
            "status": "COMPLETED" if hm >= 11 * 60 + 30 else ("ACTIVE" if hm >= 10 * 60 else "UPCOMING"),
            "what_to_do": (
                f"Giám sát sát sao vị thế hiện hữu ({holdings_desc} • {stocks_val_vnd:,.0f} đ) và radar Standby: {standby_text}. "
                f"{regime_guidance}"
            ),
            "constitution_rule": "Kỷ luật giải ngân: Chỉ gom khi phe bán kiệt sức tại vùng hỗ trợ cứng."
        },
        {
            "step_id": 5,
            "time_range": "11:30 – 13:00",
            "title": "Bước 5: Nghỉ Trưa, Tổng Kết Phiên Sáng & Đối Soát Khối Ngoại / Phái Sinh",
            "role": "Minh Quân & Victor",
            "status": "COMPLETED" if hm >= 13 * 60 else ("ACTIVE" if hm >= 11 * 60 + 30 else "UPCOMING"),
            "what_to_do": (
                f"Tổng hợp thanh khoản, mua/bán ròng khối ngoại, Basis VN30F1M và cập nhật NAV live ({total_nav_vnd:,.0f} đ). "
                f"Chuẩn bị kịch bản đón nhịp hàng T+2.5 về tài khoản lúc 13h00."
            ),
            "constitution_rule": "Đóng sổ theo dõi giữa phiên, tránh dao động cảm xúc ngắn hạn."
        },
        {
            "step_id": 6,
            "time_range": "13:00 – 13:45",
            "title": "Giai Đoạn 1: Quan Sát Nhịp Hấp Thụ Hàng T+2.5 Về Tài Khoản",
            "role": "Minh Quân & Victor Sentinel",
            "status": "COMPLETED" if hm >= 13 * 60 + 45 else ("ACTIVE" if hm >= 13 * 60 else "UPCOMING"),
            "what_to_do": (
                f"Theo dõi lực chốt lời/cắt lỗ khung 13:15 – 13:35. Danh mục hiện có {total_shares} CP ({holdings_desc}) "
                f"và tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV). Kiên nhẫn chờ phe bán xả xong."
            ),
            "constitution_rule": "TUYỆT ĐỐI KHÔNG BẮT DAO RƠI khi lực bán hoảng loạn chưa dứt điểm."
        },
        {
            "step_id": 7,
            "time_range": "13:45 – 13:55",
            "title": "Giai Đoạn 2: Thẩm Định Lực Đỡ & Độ Cạn Cung (No-Supply Check)",
            "role": "Victor & Minh Quân",
            "status": "COMPLETED" if hm >= 13 * 60 + 55 else ("ACTIVE" if hm >= 13 * 60 + 45 else "UPCOMING"),
            "what_to_do": (
                f"Đo Buy Up % và RSI14 trực tiếp: {standby_text}. "
                f"Kiểm tra khoảng cách tới ngưỡng Stop Loss 2xATR cho các vị thế đang giữ: {hold_details}."
            ),
            "constitution_rule": "Chỉ bấm cò khi xuất hiện nến Test Cung / Buy Up >= 55% và chế độ thị trường cho phép."
        },
        {
            "step_id": 8,
            "time_range": "14:00 – 14:25",
            "title": f"Giai Đoạn 3: ⭐ KHUNG GIỜ VÀNG TÁC CHIẾN ({regime_label})",
            "role": "Chủ Tịch Thực Thi • Victor & Minh Quân Bảo Vệ",
            "status": "COMPLETED" if hm >= 14 * 60 + 25 else ("ACTIVE" if hm >= 14 * 60 else "UPCOMING"),
            "what_to_do": (
                f"Thời điểm quyết định (90% nến ngày lộ rõ). Hạn mức giải ngân mới tối đa theo Regime: {max_alloc}% Cash "
                f"trên két {cash_vnd:,.0f} đ. Trạng thái danh mục: {hold_details}. Radar mục tiêu: {standby_text}."
            ),
            "constitution_rule": "Đặt lệnh LO chuẩn chỉ, khóa rủi ro Stop Loss <= 0.35% NAV cho mỗi lệnh mới."
        },
        {
            "step_id": 9,
            "time_range": "14:30 – 14:45",
            "title": "Bước 9: Phiên Đóng Cửa ATC & Đối Soát Sổ Cái Thực Thi",
            "role": "Minh Quân & Victor",
            "status": "COMPLETED" if hm >= 14 * 60 + 45 else ("ACTIVE" if hm >= 14 * 60 + 30 else "UPCOMING"),
            "what_to_do": (
                f"Chốt giá đóng cửa ATC, cập nhật NAV live ({total_nav_vnd:,.0f} đ), đối soát lệnh khớp thực tế trên TCInvest "
                f"(bằng Form Sync 1-Click) và bàn giao sổ cái ca tối."
            ),
            "constitution_rule": "Bảo đảm SSOT chính xác 100% đến từng đồng."
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
                "what_to_do": (
                    f"Thị trường Việt Nam đã đóng cửa. Danh mục live gồm {total_shares} CP ({holdings_desc} • {stocks_val_vnd:,.0f} đ) "
                    f"và két tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV) — Tổng NAV: {total_nav_vnd:,.0f} đ. "
                    f"Victor giám sát 24/7, chuyển giao ca tối sang Phân khu Phố Wall của Alex lúc 21h30."
                ),
                "constitution_rule": "Hiến chương Điều 9: Kỷ luật lưu trữ nhật ký và bảo vệ tài sản xuyên lục địa."
            }
        else:
            active_step = steps[0]

    return {
        "current_step": active_step,
        "all_steps": steps
    }


def get_live_market_overview(snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Lấy dữ liệu tình hình thị trường thời gian thực từ VPS/Entrade cho bàn trực chiến của Victor.
    """
    snap = snapshot or _get_live_snapshot()
    return snap.get("market_overview", {})


def get_live_stock_sentinel(snapshot: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Bảng giá giám sát thời gian thực SSOT động (Holdings + Minh Quân + Master Blotter) cho Victor Sentinel.
    """
    snap = snapshot or _get_live_snapshot()
    return snap.get("live_stocks", [])


def load_directives_history(
    date_str: Optional[str] = None,
    portfolio_live: Optional[Dict[str, Any]] = None,
    regime: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Tải lịch sử chỉ thị tương tác giữa Chủ tịch và Minh Quân/Victor theo từng ngày mới."""
    if not date_str:
        date_str = get_ict_now().strftime("%Y-%m-%d")

    file_path = get_daily_directives_file(date_str)
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    return data
        except Exception:
            pass
    else:
        try:
            from scripts.apex_cloud_db_sync import ApexCloudDBSync
            cloud_dirs = ApexCloudDBSync.restore_directives_if_missing(date_str)
            if cloud_dirs:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(cloud_dirs, f, ensure_ascii=False, indent=2)
                return cloud_dirs
        except Exception:
            pass

    if portfolio_live is None or regime is None:
        snap = _get_live_snapshot()
        portfolio_live = portfolio_live or snap.get("portfolio_live", {})
        regime = regime or snap.get("intraday_regime", {})

    cash_vnd = float(portfolio_live.get("cash_vnd", 0.0))
    stocks_val = float(portfolio_live.get("stocks_val_vnd", 0.0))
    total_nav = float(portfolio_live.get("total_nav_vnd", cash_vnd + stocks_val))
    cash_pct = float(portfolio_live.get("cash_pct", 100.0))
    total_shares = int(portfolio_live.get("total_shares", 0))
    holdings_desc = portfolio_live.get("holdings_desc", "0 CP")
    realized = float(portfolio_live.get("realized_pnl_vnd", 0.0))
    regime_label = regime.get("label", "GIẰNG CO PHÂN HÓA")

    default_history = [
        {
            "id": f"dir_{date_str}_001",
            "timestamp": "08:30:15",
            "sender": "Minh Quân (Ban 7 VN)",
            "role": "specialist",
            "type": "morning_brief",
            "content": (
                f"Kính trình Chủ tịch Trần Quốc Thiên Phước! Minh Quân đã kích hoạt Living War-Room V4.0 cho ngày {date_str}. "
                f"Chế độ thị trường hiện tại: {regime_label}. Kỷ luật bất biến: KHÔNG ĐUA LỆNH ATO, kiên nhẫn chờ Khung Giờ Vàng 14h00 - 14h25!"
            )
        },
        {
            "id": f"dir_{date_str}_002",
            "timestamp": "08:32:40",
            "sender": "Victor (Ban 9 Live Sentinel)",
            "role": "sentinel",
            "type": "sentinel_brief",
            "content": (
                f"Báo cáo Chủ tịch! Victor túc trực 24/7 bảo vệ danh mục SSOT ngày {date_str}. "
                f"Tổng NAV live: {total_nav:,.0f} đ | Tiền mặt thật: {cash_vnd:,.0f} đ ({cash_pct:.1f}% Cash) | "
                f"Đang nắm giữ: {total_shares} CP ({holdings_desc} ≈ {stocks_val:,.0f} đ) | Lãi đã chốt lũy kế: +{realized:,.0f} đ. "
                f"Bảng giá & Orderbook 3 bước giá đang được quét liên tục!"
            )
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
        trimmed = history[-60:] if len(history) > 60 else history
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(trimmed, f, ensure_ascii=False, indent=2)
        try:
            from scripts.apex_cloud_db_sync import ApexCloudDBSync
            if trimmed:
                ApexCloudDBSync.sync_directive(trimmed[-1], date_str)
        except Exception:
            pass
    except Exception as e:
        print(f"Error saving directives: {e}", file=sys.stderr)


def push_external_war_room_alert(
    sender: str,
    alert_type: str,
    content: str,
    role: str = "sentinel",
    alert_key: Optional[str] = None,
    date_str: Optional[str] = None,
) -> bool:
    """
    Hook liên phòng ban: Cho phép Ban 9 Sentinel, Ban 10 CBTT Radar, hoặc Sync TCInvest
    bơm trực tiếp cảnh báo khẩn / sự kiện trọng yếu vào Bảng Chỉ Thị Live của War-Room (có chống trùng lặp theo ngày).
    """
    now = get_ict_now()
    if not date_str:
        date_str = now.strftime("%Y-%m-%d")

    directives = load_directives_history(date_str)
    dedup_id = alert_key or f"ext_{date_str}_{alert_type}_{abs(hash(content)) % 1000000}"
    if any(d.get("id") == dedup_id or (alert_key and d.get("key") == alert_key) for d in directives):
        return False

    entry = {
        "id": dedup_id,
        "key": dedup_id,
        "timestamp": now.strftime("%H:%M:%S"),
        "sender": sender,
        "role": role,
        "type": alert_type,
        "content": content,
    }
    directives.append(entry)
    save_directives_history(directives, date_str)
    return True


def evaluate_and_trigger_tactical_alerts(
    live_stocks: List[Dict[str, Any]],
    phase_info: Dict[str, Any],
    directives: List[Dict[str, Any]],
    date_str: str,
    snapshot: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    CƠ CHẾ CẢNH BÁO TÁC CHIẾN ĐỘNG THEO THỜI GIAN THỰC (CHỐNG TRÙNG LẶP):
    - Tự động kích hoạt cảnh báo Stop Loss 2xATR, Cận Stop, Đạt TP1/TP2 cho MỌI mã đang nắm giữ trong SSOT.
    - Kích hoạt cảnh báo Chế độ Thị trường Phòng Thủ (DEFENSIVE_SELLOFF) nếu VN-Index bán tháo.
    - Kích hoạt đề xuất bấm cò Nhịp 1 trong Khung Giờ Vàng (14h00-14h25) khi cổ phiếu standby vào vùng mua + cạn cung.
    """
    now = get_ict_now()
    hm = now.hour * 60 + now.minute
    is_weekend = bool(phase_info.get("is_weekend", now.weekday() >= 5))
    in_market_hours = (not is_weekend) and (9 * 60 <= hm <= 14 * 60 + 45)
    in_golden_window = (not is_weekend) and (13 * 60 + 45 <= hm <= 14 * 60 + 25)

    snap = snapshot or {}
    port = snap.get("portfolio_live", {})
    regime = snap.get("intraday_regime", {})
    regime_id = regime.get("regime_id", "SIDEWAY_CHOPPY")

    cash_vnd = float(port.get("cash_vnd", 0.0))
    cash_pct = float(port.get("cash_pct", 100.0))
    total_nav = float(port.get("total_nav_vnd", cash_vnd))
    holdings = port.get("holdings", [])

    existing_ids = {d.get("id") for d in directives}
    changed = False
    t_now_str = now.strftime("%H:%M:%S")

    # 1. Cảnh báo Chế độ Thị trường Phòng thủ (khi phiên đang mở)
    def_id = f"dir_{date_str}_regime_defensive"
    if in_market_hours and regime_id == "DEFENSIVE_SELLOFF" and def_id not in existing_ids:
        directives.append({
            "id": def_id,
            "timestamp": t_now_str,
            "sender": "Victor (Ban 9 Live Sentinel) & Minh Quân (Ban 7 VN)",
            "role": "sentinel",
            "type": "sentinel_alert",
            "content": (
                f"🚨 [CẢNH BÁO CHẾ ĐỘ PHÒNG THỦ] {regime.get('label')}: {regime.get('guidance')} "
                f"Khóa 100% lệnh mua mới (Hạn mức 0%), bảo vệ két tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV)!"
            )
        })
        existing_ids.add(def_id)
        changed = True

    # 2. Cảnh báo realtime trên từng vị thế đang nắm giữ trong SSOT
    for s in live_stocks:
        if not s.get("is_holding"):
            continue
        code = s["code"]
        act = s.get("action_code", "SAFE_HOLD")
        price = float(s.get("price", 0.0))
        stop_p = float(s.get("stop_loss", 0.0))
        tp1_p = float(s.get("tp1", 0.0))
        tp2_p = float(s.get("tp2", 0.0))

        if act == "STOP_TRIGGERED":
            aid = f"dir_{date_str}_stop_breached_{code}"
            if aid not in existing_ids:
                directives.append({
                    "id": aid,
                    "timestamp": t_now_str,
                    "sender": "Victor (Ban 9 Live Sentinel)",
                    "role": "sentinel",
                    "type": "sentinel_alert",
                    "content": (
                        f"🚨 [BÁO ĐỘNG ĐỎ CẮT LỖ 2xATR — {code}] Giá live {price:,.0f} đ đã chạm/thủng ngưỡng Stop Loss {stop_p:,.0f} đ! "
                        f"Kính trình Chủ tịch kiểm tra khớp cắt lỗ kỷ luật để khóa rủi ro <= 0.35% NAV!"
                    )
                })
                existing_ids.add(aid)
                changed = True
        elif act == "NEAR_STOP_WARNING" and in_market_hours:
            aid = f"dir_{date_str}_near_stop_{code}"
            if aid not in existing_ids:
                directives.append({
                    "id": aid,
                    "timestamp": t_now_str,
                    "sender": "Victor (Ban 9 Live Sentinel)",
                    "role": "sentinel",
                    "type": "sentinel_alert",
                    "content": (
                        f"⚠️ [CẬN NGƯỠNG BẢO VỆ — {code}] Giá live {price:,.0f} đ chỉ còn cách Stop 2xATR ({stop_p:,.0f} đ) "
                        f"{s.get('dist_to_stop_pct', 0):.2f}%. Tuyệt đối KHÔNG bình quân giá xuống!"
                    )
                })
                existing_ids.add(aid)
                changed = True
        elif act in ("TP1_REACHED", "TP2_REACHED"):
            aid = f"dir_{date_str}_{act.lower()}_{code}"
            if aid not in existing_ids:
                target_label = f"TP2 ({tp2_p:,.0f} đ)" if act == "TP2_REACHED" else f"TP1 ({tp1_p:,.0f} đ)"
                directives.append({
                    "id": aid,
                    "timestamp": t_now_str,
                    "sender": "Minh Quân (Ban 7 VN) & Victor",
                    "role": "specialist",
                    "type": "specialist_directive",
                    "content": (
                        f"🎯 [ĐẠT MỤC TIÊU CHỐT LỜI — {code}] Giá live {price:,.0f} đ đã chạm {target_label}! "
                        f"Đề xuất Scaling Out chốt lời 50% vị thế và nâng Stop Loss phần còn lại lên giá hòa vốn!"
                    )
                })
                existing_ids.add(aid)
                changed = True

    # 3. Tóm tắt giám sát vị thế buổi chiều (khi có holdings và đang trong phiên chiều)
    hold_id = f"dir_{date_str}_holding_sentinel"
    if holdings and in_market_hours and (13 * 60 <= hm <= 14 * 60 + 45) and hold_id not in existing_ids:
        summary_parts = []
        for h in holdings:
            summary_parts.append(
                f"{h.get('shares', 0)} {h.get('symbol')} @ Live {float(h.get('current_price', 0)):,.0f} đ ({float(h.get('pnl_pct', 0)):+.2f}%, Stop {float(h.get('stop_loss', 0)):,.0f} đ)"
            )
        directives.append({
            "id": hold_id,
            "timestamp": t_now_str,
            "sender": "Victor (Ban 9 Live Sentinel) & Minh Quân (Ban 7 VN)",
            "role": "sentinel",
            "type": "sentinel_alert",
            "content": (
                f"🛡️ [GIÁM SÁT PHIÊN CHIỀU LIVE] Danh mục hiện hữu: {' | '.join(summary_parts)}. "
                f"Két tiền mặt bảo toàn: {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV • Tổng NAV {total_nav:,.0f} đ). "
                f"Chế độ thị trường: {regime.get('label', 'N/A')}."
            )
        })
        existing_ids.add(hold_id)
        changed = True

    # 4. Tín hiệu mua mới trong Khung Giờ Vàng (chỉ bắn khi chưa cầm mã đó và Regime không DEFENSIVE)
    if in_golden_window and regime_id != "DEFENSIVE_SELLOFF":
        for s in live_stocks:
            if s.get("is_holding"):
                continue
            if s.get("action_code") == "BUY_ZONE" and float(s.get("active_buy_pct", 0.0)) >= 50.0:
                bid = f"dir_{date_str}_golden_buy_{s['code']}"
                if bid not in existing_ids:
                    directives.append({
                        "id": bid,
                        "timestamp": t_now_str,
                        "sender": "Minh Quân (Ban 7 VN)",
                        "role": "specialist",
                        "type": "specialist_directive",
                        "content": (
                            f"🎯 [TÍN HIỆU KHUNG GIỜ VÀNG — {s['code']}] Giá live {s['price']:,.0f} đ vào vùng gom "
                            f"(Mục tiêu <= {s['probe_target']:,.0f} đ), Mua chủ động {s['active_buy_pct']:.1f}%, "
                            f"Stop {s['stop_loss']:,.0f} đ, TP1 {s['tp1']:,.0f} đ. Xin Chủ tịch xem xét giải ngân LO!"
                        )
                    })
                    existing_ids.add(bid)
                    changed = True

    if changed:
        save_directives_history(directives, date_str)
    return directives


def get_weekly_reference_roadmap(snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    BẢNG KẾ HOẠCH TÁC CHIẾN TUẦN (ĐỊNH HƯỚNG THAM KHẢO CHO CHỦ TỊCH):
    - Nạp từ SSOT: data/weekly_tactical_plan_active.json
    - Đồng thời đồng bộ trạng thái khớp lệnh / giá hiện tại từ Snapshot thực tế để tránh lệch số liệu.
    """
    plan_file = DATA_DIR / "weekly_tactical_plan_active.json"
    plan_data: Optional[Dict[str, Any]] = None
    if plan_file.exists():
        try:
            with open(plan_file, "r", encoding="utf-8") as f:
                plan_data = json.load(f)
        except Exception:
            plan_data = None

    snap = snapshot or _get_live_snapshot()
    port = snap.get("portfolio_live", {})
    live_map = {s["code"]: s for s in snap.get("live_stocks", [])}
    holdings_map = {h.get("symbol"): h for h in port.get("holdings", [])}

    if plan_data:
        # Enrich approved_watchlist dynamically without mutating user policy rules
        enriched_wl = []
        for item in plan_data.get("approved_watchlist", []):
            sym = str(item.get("symbol", "")).upper()
            copied = dict(item)
            if sym in holdings_map:
                h = holdings_map[sym]
                copied["executed_shares"] = int(h.get("shares", 0))
                copied["current_status"] = (
                    f"ĐANG NẮM GIỮ {h.get('shares', 0)} CP @ Vốn {float(h.get('avg_cost', 0)):,.0f} đ "
                    f"(Live {float(h.get('current_price', 0)):,.0f} đ • {float(h.get('pnl_pct', 0)):+.2f}%)"
                )
            elif sym in live_map:
                ls = live_map[sym]
                copied["executed_shares"] = 0
                copied["current_status"] = f"STANDBY — Live {ls['price']:,.0f} đ ({ls['change_pct']:+.2f}%)"
            enriched_wl.append(copied)
        if enriched_wl:
            plan_data["approved_watchlist"] = enriched_wl
        return plan_data

    cash_vnd = float(port.get("cash_vnd", 0.0))
    cash_pct = float(port.get("cash_pct", 100.0))
    stocks_val = float(port.get("stocks_val_vnd", 0.0))
    holdings_desc = port.get("holdings_desc", "0 CP")
    now = get_ict_now()
    week_num = now.isocalendar()[1]

    dynamic_wl = []
    for s in snap.get("live_stocks", [])[:6]:
        sym = s["code"]
        h = holdings_map.get(sym)
        dynamic_wl.append({
            "symbol": sym,
            "name": s.get("name", sym),
            "tier": s.get("tier", "Watchlist"),
            "weekly_limit": "Theo ATR Risk-Parity <= 0.35% NAV/lệnh",
            "executed_shares": int(h.get("shares", 0)) if h else 0,
            "current_status": (
                f"ĐANG GIỮ {h.get('shares', 0)} CP @ Live {s['price']:,.0f} đ ({float(h.get('pnl_pct', 0)):+.2f}%)"
                if h else f"STANDBY — Live {s['price']:,.0f} đ ({s['change_pct']:+.2f}%)"
            ),
            "entry_zone": f"{s['probe_target']:,.0f} đ",
            "stop_loss_2xatr": f"{s['stop_loss']:,.0f} đ",
            "tp1": f"{s['tp1']:,.0f} đ" if s.get("tp1") else "N/A",
            "tp2": f"{s['tp2']:,.0f} đ" if s.get("tp2") else "N/A",
            "catalyst": s.get("catalyst", ""),
        })

    return {
        "title": "BẢNG KẾ HOẠCH TÁC CHIẾN TUẦN (ĐỊNH HƯỚNG THAM KHẢO CHO CHỦ TỊCH)",
        "week_label": f"Tuần {week_num} ({now.strftime('%d/%m/%Y')})",
        "basis": "Hồ sơ SSOT Living War-Room V4.0 & Master Execution Blotter",
        "approved_by": "Chủ tịch Trần Quốc Thiên Phước",
        "legal_stamp": "🛡️ BAN 12 TRỌNG NIÊM PHONG PHÁP LÝ THỂ CHẾ",
        "is_reference_only": True,
        "constitution_mandate": (
            "⚠️ THỂ CHẾ BẤT BIẾN THEO CHỈ THỊ CỦA CHỦ TỊCH: Bảng kế hoạch tuần CHỈ MANG TÍNH CHẤT THAM KHẢO ĐỊNH HƯỚNG, "
            "TUYỆT ĐỐI KHÔNG PHẢI KẾ HOẠCH CỨNG. Mọi quyết định giải ngân/phòng thủ PHẢI THAY ĐỔI TỪNG NGÀY theo biến động thực tế."
        ),
        "days": [
            {
                "day_id": "current",
                "day_name": f"Trạng Thái SSOT Hiện Tại ({now.strftime('%d/%m/%Y')})",
                "theme": f"Đang giữ {holdings_desc} ({stocks_val:,.0f} đ) • Két Tiền Mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}%)",
                "status": "ACTIVE",
                "status_badge": "🟢 ĐỒNG BỘ LIVE",
                "guideline": "Tuân thủ kỷ luật 3 Không, bảo vệ vị thế bằng Stop Loss 2xATR và chờ điểm cạn cung Khung Giờ Vàng.",
                "cash_reserve_target": f"{cash_pct:.1f}% NAV ({cash_vnd/1e6:.2f}M)"
            }
        ],
        "approved_watchlist": dynamic_wl,
    }


def _compute_threat_from_snapshot(snap: Dict[str, Any]) -> Dict[str, Any]:
    port = snap.get("portfolio_live", {})
    threat = snap.get("threat", {})
    cash_vnd = float(port.get("cash_vnd", 0.0))
    cash_pct = float(port.get("cash_pct", 100.0))
    stocks_pct = float(port.get("stocks_pct", 0.0))
    total_shares = int(port.get("total_shares", 0))
    level_num = int(threat.get("level_num", 1))
    threat_level = threat.get("threat_level", "LEVEL_1_SAFE_POSITION_ACTIVE")
    threat_label = threat.get(
        "threat_label",
        f"🟢 CẤP {level_num} — AN TOÀN ({cash_vnd:,.0f} đ Tiền Mặt {cash_pct:.1f}% • {total_shares} CP Đang Giữ {stocks_pct:.1f}%)"
    )
    return {
        "level_num": level_num,
        "threat_level": threat_level,
        "threat_label": threat_label,
    }


def get_tactical_war_room_state(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Tập hợp toàn bộ trạng thái thời gian thực của Phòng Tác Chiến (Minh Quân, Victor, Alex)
    trực tiếp từ Living Intraday Brain + SSOT thực tế 100%.
    """
    now = get_ict_now()
    snap = _get_live_snapshot(force_refresh=force_refresh)

    phase_info = get_current_market_phase(now)
    action_plan = get_tactical_action_steps(now, snapshot=snap)
    market_overview = snap.get("market_overview", {})
    live_stocks = snap.get("live_stocks", [])
    dynamic_picks = snap.get("dynamic_picks", [])
    regime = snap.get("intraday_regime", {})
    port = snap.get("portfolio_live", {})
    ledger_meta = snap.get("ledger_meta", {})

    cash_vnd = float(port.get("cash_vnd", 0.0))
    stocks_val_vnd = float(port.get("stocks_val_vnd", 0.0))
    total_nav_vnd = float(port.get("total_nav_vnd", cash_vnd + stocks_val_vnd))
    realized_pnl_vnd = float(port.get("realized_pnl_vnd", 0.0))
    unrealized_pnl_vnd = float(port.get("unrealized_pnl_vnd", 0.0))
    unrealized_pnl_pct = float(port.get("unrealized_pnl_pct", 0.0))
    holdings = port.get("holdings", [])
    holdings_count = int(port.get("holdings_count", len(holdings)))
    total_shares = int(port.get("total_shares", 0))
    cash_pct = float(port.get("cash_pct", 100.0))
    stocks_pct = float(port.get("stocks_pct", 0.0))
    holdings_desc = port.get("holdings_desc", "0 CP")

    threat_info = _compute_threat_from_snapshot(snap)
    regime_label = regime.get("label", "GIẰNG CO PHÂN HÓA")

    if phase_info["active_phase_id"] == "PRE_ATO":
        tactical_message = (
            f"Minh Quân báo cáo: Két tiền mặt thực tế {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV) "
            f"| Danh mục {total_shares} CP ({holdings_desc}). Chế độ: {regime_label}. TUYỆT ĐỐI KHÔNG ĐUA LỆNH ATO!"
        )
    elif phase_info["active_phase_id"] == "ATO_OPEN":
        tactical_message = "Minh Quân báo cáo: Phiên ATO đang diễn ra. Giữ vững kỷ luật 3 KHÔNG, không đua lệnh giá xanh mở gap."
    elif phase_info["active_phase_id"] in ("MORNING_CONTINUOUS", "NOON_INTERMISSION"):
        tactical_message = (
            f"Minh Quân & Victor báo cáo: Danh mục {holdings_desc} ({stocks_val_vnd:,.0f} đ • PnL {unrealized_pnl_vnd:+,.0f} đ) đang được quét 24/7. "
            f"Két tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV) | Chế độ: {regime_label}."
        )
    elif phase_info["active_phase_id"] in ("T2_ABSORPTION", "GOLDEN_WINDOW"):
        tactical_message = (
            f"🎯 MINH QUÂN TÁC CHIẾN CHIỀU ({regime_label}): Đang nắm giữ {total_shares} CP ({holdings_desc} • {stocks_val_vnd:,.0f} đ). "
            f"Két tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV). Victor canh giữ Stop Loss 2xATR & Buy Up từng giây!"
        )
    else:
        tactical_message = (
            f"Minh Quân báo cáo: Thị trường VN tạm nghỉ/đóng cửa. Két tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV) "
            f"và {total_shares} CP ({holdings_desc} ≈ {stocks_val_vnd:,.0f} đ) — Tổng NAV Live {total_nav_vnd:,.0f} đ."
        )

    date_str = phase_info["current_date_str"]
    directives = load_directives_history(date_str, portfolio_live=port, regime=regime)
    directives = evaluate_and_trigger_tactical_alerts(
        live_stocks, phase_info, directives, date_str, snapshot=snap
    )

    # Tự động đồng bộ báo cáo sống Live Intraday Report vào thư mục & Vault (throttled 60s)
    try:
        from scripts.apex_live_intraday_brain import sync_live_intraday_report
        sync_live_intraday_report(snap, force_write=False)
    except Exception:
        pass

    # Tính EV / P(W) / R:R động từ dynamic_picks + ledger_meta
    ev_vals = [float(p.get("ev_pct", 0.0)) for p in dynamic_picks if p.get("ev_pct")]
    pw_vals = [float(p.get("win_prob_pct", 0.0)) for p in dynamic_picks if p.get("win_prob_pct")]
    rr_vals = [float(p.get("rr_ratio", 0.0)) for p in dynamic_picks if p.get("rr_ratio")]

    avg_ev = round(sum(ev_vals) / len(ev_vals), 2) if ev_vals else float(ledger_meta.get("expected_value_pct", 0.0))
    avg_pw = round(sum(pw_vals) / len(pw_vals), 1) if pw_vals else float(ledger_meta.get("win_rate_pct", 0.0))
    avg_rr_num = round(sum(rr_vals) / len(rr_vals), 2) if rr_vals else 0.0
    avg_rr_str = f"1:{avg_rr_num:.2f}" if avg_rr_num > 0 else str(ledger_meta.get("average_rr", "1:2.50"))

    deep_brain_summary: Dict[str, Any] = {
        "top_vn_alpha_picks": [],
        "holdings_optimizer": [],
        "correlation_summary": {},
        "system_maturity_iq": {},
        "multi_horizon_walk_forward": {},
        "legends_top_picks": [],
        "omni_crawler_stats": {},
        "catalyst_alerts": {},
    }
    try:
        brain_path = BASE_DIR / "data" / "deep_financial_brain_analysis.json"
        if brain_path.exists():
            bd = json.loads(brain_path.read_text(encoding="utf-8"))
            for p in bd.get("top_vn_alpha_picks", [])[:6]:
                opt = p.get("optimizer", {})
                val = p.get("valuation", {})
                deep_brain_summary["top_vn_alpha_picks"].append({
                    "symbol": p.get("symbol"),
                    "sector_name": p.get("sector_name"),
                    "live_price": p.get("live_price"),
                    "alpha_score": p.get("alpha_score"),
                    "ocf_ratio": p.get("ocf_ratio"),
                    "ev_pct": opt.get("ev_pct"),
                    "rr_ratio": opt.get("rr_ratio"),
                    "half_kelly_pct": opt.get("half_kelly_pct"),
                    "margin_of_safety_pct": val.get("margin_of_safety_pct"),
                    "intrinsic_fair_value": val.get("intrinsic_fair_value"),
                    "suggested_shares_lot100": opt.get("suggested_shares_lot100"),
                    "action_signal": opt.get("action_signal"),
                    "max_corr_with_holdings": p.get("max_corr_with_holdings"),
                    "most_correlated_holding": p.get("most_correlated_holding"),
                    "corr_guard_status": p.get("corr_guard_status"),
                    "corr_penalty_075x": opt.get("corr_penalty_075x", False),
                })
            deep_brain_summary["holdings_optimizer"] = bd.get("holdings_optimizer", [])
            cm = bd.get("correlation_matrix", {})
            if isinstance(cm, dict) and cm:
                deep_brain_summary["correlation_summary"] = {
                    "session_window": cm.get("session_window", 60),
                    "held_symbols": cm.get("held_symbols", []),
                    "live_60d_series_fetched": cm.get("live_60d_series_fetched", 0),
                    "total_symbols_evaluated": cm.get("total_symbols_evaluated", 0),
                }
    except Exception:
        pass
    try:
        lg_path = BASE_DIR / "data" / "system_evolution_and_legends_state.json"
        if not lg_path.exists():
            lg_path = BASE_DIR / "data" / "legend_investor_wisdom_vault.json"
        if lg_path.exists():
            ld = json.loads(lg_path.read_text(encoding="utf-8"))
            sr = ld.get("self_reflection", {})
            iq_raw = dict(sr.get("system_maturity_iq", {}))
            iq_raw["classification_counts"] = sr.get("classification_counts", {})
            deep_brain_summary["system_maturity_iq"] = iq_raw
            deep_brain_summary["multi_horizon_walk_forward"] = ld.get("multi_horizon_walk_forward", {}) or sr.get("multi_horizon_walk_forward", {})
            for ev in ld.get("ticker_evaluations", [])[:6]:
                top_adv = (ev.get("top_3_advocates") or [{}])[0]
                deep_brain_summary["legends_top_picks"].append({
                    "symbol": ev.get("symbol"),
                    "market": ev.get("market"),
                    "consensus_legends_score": ev.get("consensus_legends_score"),
                    "supporting_legends_count": ev.get("supporting_legends_count"),
                    "legends_verdict": ev.get("legends_verdict"),
                    "top_advocate": f"{top_adv.get('name', '')} ({top_adv.get('score', 0)})",
                    "key_dissent": f"{ev.get('key_dissent', {}).get('name', '')} ({ev.get('key_dissent', {}).get('score', 0)})",
                })
    except Exception:
        pass
    try:
        omni_path = BASE_DIR / "data" / "omni_market_intelligence.json"
        bctc_upd_path = BASE_DIR / "data" / "live_bctc_quarterly_updates.json"
        alerts_path = BASE_DIR / "data" / "live_catalyst_alerts.json"
        bctc_cnt = 0
        if bctc_upd_path.exists():
            bctc_cnt = int(json.loads(bctc_upd_path.read_text(encoding="utf-8")).get("total_tickers_updated", 0) or 0)
        if omni_path.exists():
            od = json.loads(omni_path.read_text(encoding="utf-8"))
            sh = od.get("source_health", [])
            deep_brain_summary["omni_crawler_stats"] = {
                "crawled_at": od.get("crawled_at", ""),
                "total_universe": (od.get("universe_counts") or {}).get("total", 180),
                "total_items": od.get("total_items", 0),
                "live_bctc_updates_count": bctc_cnt,
                "sources_online": f"{sum(1 for s in sh if s.get('ok'))}/{len(sh)}" if sh else "0/0",
            }
        if alerts_path.exists():
            ad = json.loads(alerts_path.read_text(encoding="utf-8"))
            deep_brain_summary["catalyst_alerts"] = {
                "updated_at": ad.get("updated_at", ""),
                "total_alerts": ad.get("total_alerts", 0),
                "holding_alerts_count": ad.get("holding_alerts_count", 0),
                "risk_alerts_count": ad.get("risk_alerts_count", 0),
                "alerts": (ad.get("alerts") or [])[:6],
            }
    except Exception:
        pass

    return {
        "status": "ok",
        "chairman_name": "Trần Quốc Thiên Phước",
        "account_id": "105C307855",
        "trading_date": phase_info["current_date_str"],
        "server_time": phase_info["current_time_str"],
        "phase_info": phase_info,
        "intraday_regime": regime,
        "tactical_message": tactical_message,
        "action_plan": action_plan,
        "market_overview": market_overview,
        "live_stocks": live_stocks,
        "dynamic_picks": dynamic_picks,
        "minh_quan_blueprint": {
            "specialist_name": "Minh Quân",
            "title": "Chuyên Viên Đầu Tư Trưởng TTCK Việt Nam (Ban 7 VN)",
            "mastery_score": float(ledger_meta.get("mastery_score", 98.5)),
            "expected_value_pct": avg_ev,
            "win_rate_pct": avg_pw,
            "average_rr": avg_rr_str,
            "golden_window": "14h00 – 14h25 Chiều",
            "rules": [
                "❌ KHÔNG MUA ATO: Tránh 100% bẫy giá giả (Bull-Trap/Bear-Trap) đầu phiên sáng.",
                "❌ KHÔNG MUA GIÁ XANH: Tuyệt đối không fomo khi RSI > 60 hoặc chưa có nền tích lũy cạn cung.",
                "❌ KHÔNG BÌNH QUÂN GIÁ XUỐNG: Cắt lỗ cứng Stop 2xATR (<= 7.5%) nếu vị thế đi ngược kỳ vọng.",
                f"⭐ CHẾ ĐỘ LIVE HIỆN TẠI: {regime_label} (Hạn mức giải ngân mới tối đa {regime.get('max_new_allocation_pct', 30)}% Cash)."
            ]
        },
        "victor_sentinel": {
            "officer_name": "Victor",
            "title": "Chỉ Huy Giám Sát Realtime & Phòng Hộ Khẩn Cấp (Ban 9 Live Sentinel)",
            "cash_vnd": cash_vnd,
            "total_nav_vnd": total_nav_vnd,
            "stocks_val_vnd": stocks_val_vnd,
            "cash_pct": cash_pct,
            "stocks_pct": stocks_pct,
            "total_shares": total_shares,
            "unrealized_pnl_vnd": unrealized_pnl_vnd,
            "unrealized_pnl_pct": unrealized_pnl_pct,
            "holdings_count": holdings_count,
            "holdings": holdings,
            "realized_round1_profit_vnd": realized_pnl_vnd,
            "threat_level_num": threat_info["level_num"],
            "threat_level": threat_info["threat_level"],
            "threat_label": threat_info["threat_label"],
            "risk_arsenal": [
                "Ngưỡng cắt lỗ cứng Stop 2xATR (khóa mức lỗ tối đa <= 0.35% NAV)",
                "Kỹ thuật T+0 Scalping hạ giá vốn linh hoạt",
                "Phòng vệ danh mục bằng Synthetic Short Hedge HĐTL VN30F khi thị trường gãy MA200"
            ]
        },
        "alex_wall_street": {
            "officer_name": "Alex",
            "title": "Chuyên Viên Đầu Tư Quốc Tế & Phố Wall (Ban 7 US)",
            "status": snap.get("global_spillover", {}).get("overnight_bias", "NEUTRAL_SELECTIVE"),
            "status_label": snap.get("global_spillover", {}).get("bias_label", "⚖️ TRUNG TÍNH"),
            "ny_open_time": "21:30 Tối Giờ VN",
            "countdown_str": phase_info["countdown_to_wall_street"],
            "risk_multiplier": snap.get("global_spillover", {}).get("risk_multiplier", 1.0),
            "max_allocation_pct": snap.get("global_spillover", {}).get("max_allocation_pct", 45),
            "handoff_directive": snap.get("global_spillover", {}).get("handoff_directive", ""),
            "watchlist": [
                {"ticker": "NVDA", "name": "NVIDIA Corporation", "thesis": "Thống trị GPU AI Blackwell, FCF biên độ 55%"},
                {"ticker": "AVGO", "name": "Broadcom Inc.", "thesis": "Custom ASIC AI & Networking, hợp đồng hyperscalers khủng"},
                {"ticker": "MSFT", "name": "Microsoft Corp", "thesis": "Azure Cloud AI tăng tốc, tích hợp Copilot toàn diện"},
                {"ticker": "PLTR", "name": "Palantir Technologies", "thesis": "Nền tảng AIP bùng nổ nhu cầu doanh nghiệp & quốc phòng"}
            ],
            "note": snap.get("global_spillover", {}).get("handoff_directive") or "Sẵn sàng điều phối dòng tiền liên thị trường US <-> VN."
        },
        "global_spillover": snap.get("global_spillover", {}),
        "execution_tracker": snap.get("execution_tracker", {}),
        "deep_brain_summary": deep_brain_summary,
        "directives_history": directives,
        "weekly_reference_plan": get_weekly_reference_roadmap(snapshot=snap)
    }


def _format_stock_live_reply(s: Dict[str, Any], holdings_map: Dict[str, Dict[str, Any]]) -> str:
    code = s["code"]
    hold_note = ""
    if code in holdings_map:
        h = holdings_map[code]
        hold_note = (
            f" [ĐANG NẮM GIỮ {h.get('shares', 0)} CP @ Giá vốn {float(h.get('avg_cost', 0)):,.0f} đ | "
            f"PnL tạm tính: {float(h.get('pnl_vnd', 0)):+,.0f} đ ({float(h.get('pnl_pct', 0)):+.2f}%)]"
        )
    else:
        hold_note = " [Chưa nắm giữ — Trạng thái Radar / Standby]"

    fn = float(s.get("foreign_net_ty", 0.0))
    fn_str = f"{fn:+.2f} Tỷ" if abs(fn) > 0 else "0.00 Tỷ"
    return (
        f"Báo cáo Chủ tịch dữ liệu LIVE của {code} ({s.get('name', code)}){hold_note}:\n"
        f"• Giá Live: {s['price']:,.0f} đ ({s['change_pct']:+.2f}%) | Khớp: {int(s.get('volume', 0)):,} CP (Pace {s.get('vol_ratio_20d', 1):.2f}x MA20)\n"
        f"• Dòng tiền: Mua chủ động {s.get('active_buy_pct', 50):.1f}% | RSI(14): {s.get('rsi14', 50):.1f} | Khối ngoại: {fn_str}\n"
        f"• Vùng mục tiêu gom: <= {s.get('probe_target', 0):,.0f} đ | Stop 2xATR: {s.get('stop_loss', 0):,.0f} đ (cách {s.get('dist_to_stop_pct', 0):+.2f}%) | "
        f"TP1: {s.get('tp1', 0):,.0f} đ | TP2: {s.get('tp2', 0):,.0f} đ\n"
        f"• Đánh giá tác chiến: {s.get('security_label', '')} | Catalyst: {s.get('catalyst', '')}"
    )


def handle_tactical_command(command_text: str, user_name: str = "Chủ tịch Trần Quốc Thiên Phước") -> Dict[str, Any]:
    """
    Xử lý chỉ thị hoặc câu hỏi của Chủ tịch gửi cho Minh Quân và Victor thời gian thực.
    100% sử dụng số liệu live SSOT, Bảng điện VPS, Regime và Holdings thực tế.
    """
    command_text = command_text.strip()
    if not command_text:
        return {"ok": False, "error": "Chỉ thị không được để trống."}

    now = get_ict_now()
    time_str = now.strftime("%H:%M:%S")
    cmd_lower = command_text.lower()

    state = get_tactical_war_room_state(force_refresh=True)
    phase = state["phase_info"]
    regime = state.get("intraday_regime", {})
    market_ov = state.get("market_overview", {})
    vni = market_ov.get("vn_index", {})
    vn30 = market_ov.get("vn30_index", {})
    breadth = market_ov.get("market_breadth", {})
    victor = state["victor_sentinel"]
    cash_vnd = float(victor["cash_vnd"])
    stocks_val_vnd = float(victor["stocks_val_vnd"])
    total_nav_vnd = float(victor["total_nav_vnd"])
    cash_pct = float(victor["cash_pct"])
    stocks_pct = float(victor["stocks_pct"])
    total_shares = int(victor["total_shares"])
    holdings = victor.get("holdings", [])
    holdings_map = {str(h.get("symbol", "")).upper(): h for h in holdings}
    live_stocks = state.get("live_stocks", [])
    dynamic_picks = state.get("dynamic_picks", [])

    response_content = ""
    specialist_sign = "Minh Quân (Ban 7 VN) & Victor (Ban 9 Sentinel)"

    # 1. Kiểm tra xem Chủ tịch có hỏi trực tiếp mã cổ phiếu nào trong Watchlist không
    matched_stock = None
    for s in live_stocks:
        sym_low = s["code"].lower()
        if f" {sym_low} " in f" {cmd_lower} " or sym_low in cmd_lower.replace(",", " ").replace(".", " ").split():
            matched_stock = s
            break
    if not matched_stock:
        for s in live_stocks:
            if s["code"].lower() in cmd_lower:
                matched_stock = s
                break

    if any(k in cmd_lower for k in ["kế hoạch tuần", "tuần", "roadmap", "tuần này", "kế hoạch mỗi tuần", "tham khảo tuần"]):
        w_plan = state["weekly_reference_plan"]
        days_lines = "\n".join(
            f"• {d.get('day_name', '')} [{d.get('status_badge', '')}]: {d.get('theme', '')} — {d.get('guideline', '')}"
            for d in w_plan.get("days", [])[:5]
        )
        wl_lines = "\n".join(
            f"• {w.get('symbol')}: {w.get('current_status')} | Stop {w.get('stop_loss_2xatr')} | TP1 {w.get('tp1')}"
            for w in w_plan.get("approved_watchlist", [])[:5]
        )
        response_content = (
            f"📋 [{w_plan.get('title', 'KẾ HOẠCH TUẦN')} — {w_plan.get('week_label', '')}]\n"
            f"⚖️ NGUYÊN TẮC BẤT BIẾN: {w_plan.get('constitution_mandate', '')}\n\n"
            f"📅 LỘ TRÌNH THAM KHẢO:\n{days_lines}\n\n"
            f"🎯 TRẠNG THÁI RỔ THEO DÕI LIVE:\n{wl_lines}"
        )
    elif matched_stock is not None:
        response_content = _format_stock_live_reply(matched_stock, holdings_map)
    elif any(k in cmd_lower for k in ["sập", "giảm mạnh", "rung lắc", "bán tháo", "rủi ro", "thị trường sập"]):
        hold_stops = "; ".join(
            f"{h.get('symbol')}: Stop {float(h.get('stop_loss', 0)):,.0f} đ (hiện {float(h.get('current_price', 0)):,.0f} đ)"
            for h in holdings
        ) or "Chưa có vị thế cổ phiếu (0 CP rủi ro)"
        response_content = (
            f"Victor Sentinel kính báo kịch bản ứng phó biến động dựa trên SSOT LIVE:\n"
            f"1. Tỷ lệ phòng thủ hiện tại: Tiền mặt {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV) | Cổ phiếu {stocks_val_vnd:,.0f} đ ({stocks_pct:.1f}% NAV).\n"
            f"2. Chế độ thị trường Live: {regime.get('label', 'N/A')} — VN-Index {float(vni.get('value', 0)):,.2f} ({float(vni.get('change_pct', 0)):+.2f}%), Basis VN30F {vn30.get('basis_vn30f', 'N/A')}.\n"
            f"3. Hàng rào Stop Loss 2xATR đang gác 24/7: {hold_stops}.\n"
            f"4. Nếu VN-Index bán tháo (DEFENSIVE_SELLOFF), hệ thống khóa 100% mua mới và kích hoạt Synthetic Short Hedge VN30F khi gãy hỗ trợ lớn."
        )
    elif any(k in cmd_lower for k in ["tiền", "tiền mặt", "két", "sức mua", "số dư", "cash", "nav", "danh mục"]):
        hold_detail = " | ".join(
            f"{h.get('shares', 0)} CP {h.get('symbol')} (Vốn {float(h.get('avg_cost', 0)):,.0f} đ -> Live {float(h.get('current_price', 0)):,.0f} đ, PnL {float(h.get('pnl_vnd', 0)):+,.0f} đ)"
            for h in holdings
        ) or "0 CP (100% Cash)"
        response_content = (
            f"Victor Sentinel báo cáo số liệu tiền thật SSOT LIVE (TCBS 105C307855):\n"
            f"• Tổng NAV Live: {total_nav_vnd:,.0f} đ (Lãi đã chốt lũy kế: +{float(victor.get('realized_round1_profit_vnd', 0)):,.0f} đ | PnL tạm tính danh mục: {float(victor.get('unrealized_pnl_vnd', 0)):+,.0f} đ)\n"
            f"• Tiền mặt khả dụng: {cash_vnd:,.0f} đ ({cash_pct:.1f}% NAV)\n"
            f"• Cổ phiếu đang nắm giữ ({total_shares} CP — {stocks_pct:.1f}% NAV): {hold_detail}."
        )
    elif any(k in cmd_lower for k in ["tiến độ", "báo cáo", "tình hình", "hiện tại", "thế nào", "ra sao", "thị trường"]):
        step_info = state["action_plan"]["current_step"]
        response_content = (
            f"Minh Quân & Victor báo cáo tình hình LIVE lúc {time_str}:\n"
            f"• Pha tác chiến: {step_info['title']} ({step_info['time_range']})\n"
            f"• VN-Index: {float(vni.get('value', 0)):,.2f} ({float(vni.get('change_pct', 0)):+.2f}%) | GTGD: {vni.get('turnover_ty_vnd', 'N/A')} | "
            f"Khối ngoại: {vni.get('foreign_net_ty_vnd', 'N/A')} | Độ rộng: {breadth.get('advancers', 0)}T / {breadth.get('decliners', 0)}G\n"
            f"• Chế độ thị trường: {regime.get('label', '')} — {regime.get('guidance', '')}\n"
            f"• Tài sản Live: NAV {total_nav_vnd:,.0f} đ (Cash {cash_vnd:,.0f} đ • CP {stocks_val_vnd:,.0f} đ).\n"
            f"• Việc cần làm ngay: {step_info['what_to_do']}"
        )
    elif any(k in cmd_lower for k in ["khung giờ vàng", "mấy giờ", "khi nào", "thời gian"]):
        response_content = (
            f"Minh Quân giải trình về Khung Giờ Vàng (14h00 – 14h25): "
            f"Vào buổi sáng thường xuất hiện bẫy kéo giá ảo (Bull-Trap) hoặc đạp ảo ATO. "
            f"Sau 13h45 khi hàng T+2.5 về tài khoản được hấp thụ xong, 90% hình thái nến ngày lộ rõ. "
            f"Chế độ thị trường hôm nay ({regime.get('label', '')}) cho phép giải ngân mới tối đa {regime.get('max_new_allocation_pct', 30)}% két tiền mặt {cash_vnd:,.0f} đ khi thỏa Test Cung!"
        )
    elif any(k in cmd_lower for k in ["lệnh", "mua", "bấm cò", "giải ngân", "vào hàng"]):
        picks_str = "\n".join(
            f"• {p['code']} ({p.get('tier', '')}): Giá Live {p['price']:,.0f} đ | Vùng gom <= {p['probe_target']:,.0f} đ | Stop {p['stop_loss']:,.0f} đ | TP1 {p['tp1']:,.0f} đ | {p['security_label']}"
            for p in dynamic_picks[:4]
        ) or "Chưa có mã mới đạt chuẩn gom."
        response_content = (
            f"Minh Quân kính trình bảng lệnh động theo chế độ {regime.get('label', '')} "
            f"(Két tiền mặt khả dụng {cash_vnd:,.0f} đ • Hạn mức tối đa {regime.get('max_new_allocation_pct', 30)}% Cash):\n"
            f"{picks_str}\n"
            f"• Điều kiện bấm cò: Đặt lệnh LO trong Khung Giờ Vàng 14h00 - 14h25 khi Buy Up >= 50% và không vi phạm Stop!"
        )
    elif any(k in cmd_lower for k in ["alex", "mỹ", "phố wall", "us", "wall street", "nasdaq", "nvda"]):
        response_content = (
            f"Alex (Ban 7 US) xin kính chào Chủ tịch! Phiên New York mở cửa lúc 21h30 tối giờ VN (còn {phase['countdown_to_wall_street']}). "
            f"Watchlist NVDA, AVGO, MSFT, PLTR luôn sẵn sàng phối hợp cùng James và Minh Quân khi Chủ tịch phê duyệt."
        )
    else:
        response_content = (
            f"Minh Quân & Victor đã tiếp nhận chỉ thị lúc {time_str}: \"{command_text}\".\n"
            f"• Trạng thái SSOT Live: NAV {total_nav_vnd:,.0f} đ | Cash {cash_vnd:,.0f} đ ({cash_pct:.1f}%) | "
            f"Đang nắm giữ {total_shares} CP ({stocks_val_vnd:,.0f} đ • PnL {float(victor.get('unrealized_pnl_vnd', 0)):+,.0f} đ).\n"
            f"• VN-Index Live: {float(vni.get('value', 0)):,.2f} ({float(vni.get('change_pct', 0)):+.2f}%) | Chế độ: {regime.get('label', 'N/A')}."
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
    print("Market Regime:", st["intraday_regime"]["label"])
    print("Market Overview VN-Index:", st["market_overview"]["vn_index"]["value"])
    print("Live Stocks count:", len(st["live_stocks"]))
    print("Victor Live NAV:", st["victor_sentinel"]["total_nav_vnd"])
    print("TEST OK!")
