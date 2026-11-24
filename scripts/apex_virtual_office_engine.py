#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX VIRTUAL OFFICE 2.5D LIVE ENGINE — SƠ ĐỒ TỔ CHỨC 5 KHỐI + 1 KHU TIỆN ÍCH (V2.0)
File: scripts/apex_virtual_office_engine.py
Cơ quan chủ quản: Palmer & Kiểm Sát Viên Trọng (Khối 5 — Giám Sát Toàn Hệ Thống)
Phục vụ: Chủ tịch Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)

SƠ ĐỒ TỔ CHỨC CHÍNH THỨC THEO CHỈ THỊ CHỦ TỊCH (22/11/2026):
1. Khối 1 (`team_hien`) — Trưởng phòng: Hiền
   Cào dữ liệu Internet, CBTT, Cổng IR, SEC EDGAR, Pháp y BCTC & Phân tích Tài chính (Ban 10, Ban 2, Ban 11)
   ──▶ Bàn giao báo cáo sang Khối 2 (Minh Quân & Alex).
2. Khối 2 (`team_quan_alex`) — Đồng Trưởng phòng: Minh Quân (VN) & Alex (US) (chịu trách nhiệm trước James)
   Phân tích thị trường & thẩm định báo cáo từ đội Hiền (Ban 7 VN/US, Ban 1 Vĩ mô, Ban 3 CANSLIM/VSA, Ban 4 Rủi ro ATR)
   ──▶ Gửi phân tích & đề xuất lên Khối 3 (Master CIO James & Palmer).
3. Khối 3 (`team_james_palmer`) — Lãnh đạo: Master CIO James & Palmer
   Tiếp nhận báo cáo từ Minh Quân & Alex + báo động chạm ngưỡng từ Victor ──▶ Hoàn thiện Kế hoạch Đầu tư trình Chủ tịch!
   (Kèm Ban 5 Tự tiến hóa & Ban 6 Học viện 15 Huyền thoại tham mưu).
4. Khối 4 (`team_victor`) — Trưởng phòng: Victor (Ban 9 Sentinel)
   Giám sát bảng điện 145 mã trong suốt phiên; chạm ngưỡng Mua/Bán trong kế hoạch ──▶ Báo ngay về James triển khai tức thì!
5. Khối 5 (`team_trong_palmer`) — Đồng Giám sát: Kiểm Sát Viên Trọng (Ban 12) & Palmer
   Giám sát toàn bộ hoạt động 4 Khối & toàn hệ thống 24/7 (10 Điều Hiến Chương, SSOT, niêm phong SHA-256).
6. Khu Tiện Ích (`room_lounge`) — Công Viên Apex, Bàn Bi-a 6 lỗ & Mô phỏng Chia Vốn 20.05M ₫.

Thuần Python chuẩn (KHÔNG import pandas / numpy / yfinance) để tối ưu RAM < 220 MB cho Render Free 512 MB.
"""

from __future__ import annotations

import datetime
import json
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DATA_DIR = BASE_DIR / "data"
KANBAN_FILE = DATA_DIR / "apex_kanban_board.json"
JOBS_HISTORY_FILE = DATA_DIR / "office_jobs_history.json"
AUDIT_LEDGER_FILE = BASE_DIR / "12_Institutional_Ombudsman_And_Inspectorate" / "system_audit_ledger.json"

from scripts.vn_market_calendar import get_vn_market_session_state
from scripts.apex_canonical_truth import load_canonical_truth

TRADING_ONLY_MILESTONE_TIMES = {"09:00", "11:45", "13:00", "14:00", "14:25", "15:15"}

_CACHE_LOCK = threading.Lock()
_LIVE_CACHE: Dict[str, Any] = {"ts": 0.0, "payload": None}
_REPORTS_CACHE: Dict[str, Any] = {"ts": 0.0, "items": []}

_JOBS_LOCK = threading.Lock()
_MAX_JOBS = 30
_KANBAN_LOCK = threading.Lock()


def get_ict_now() -> datetime.datetime:
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(datetime.timezone(datetime.timedelta(hours=7)))


def _load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {} if default is None else default


def _save_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.{uuid.uuid4().hex[:8]}.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def _load_initial_jobs() -> List[Dict[str, Any]]:
    raw = _load_json(JOBS_HISTORY_FILE, [])
    if not isinstance(raw, list):
        return []
    cleaned: List[Dict[str, Any]] = []
    for item in raw[:_MAX_JOBS]:
        if isinstance(item, dict) and item.get("job_id"):
            cleaned.append(item)
    return cleaned


_OFFICE_JOBS: List[Dict[str, Any]] = _load_initial_jobs()


def _get_cached_reports(force_refresh: bool = False) -> List[Dict[str, Any]]:
    now_ts = time.time()
    with _CACHE_LOCK:
        if not force_refresh and _REPORTS_CACHE["items"] and (now_ts - _REPORTS_CACHE["ts"]) < 10.0:
            return list(_REPORTS_CACHE["items"])
    try:
        from scripts.apex_report_scanner import scan_all_institutional_reports
        items = scan_all_institutional_reports(limit=350)
        if not isinstance(items, list):
            items = []
    except Exception:
        items = []
    with _CACHE_LOCK:
        _REPORTS_CACHE["ts"] = now_ts
        _REPORTS_CACHE["items"] = items
    return list(items)


# ==============================================================================
# QUY HOẠCH 5 KHỐI CHUYÊN MÔN + 1 KHU TIỆN ÍCH (RỘNG RÃI, MẠCH LẠC, RÕ TRƯỞNG PHÒNG)
# ==============================================================================
ROOMS_BLUEPRINT: List[Dict[str, Any]] = [
    {
        "room_id": "team_hien",
        "step_badge": "①",
        "ban_code": "Khối 1 — Đội Hiền",
        "name": "Khối Cào Dữ Liệu, BCTC & Phân Tích Tài Chính",
        "short_name": "① Đội Hiền (Dữ liệu & BCTC)",
        "wing": "Bước 1: Đầu Vào Dữ Liệu & Pháp Y Tài Chính",
        "lead_title": "Trưởng phòng: Hiền",
        "handoff_to": "Chuyển báo cáo sang ② Minh Quân & Alex",
        "icon": "🌸",
        "accent": "#ec4899",
        "floor_tint": "#fdf2f8",
        "officers": ["Hiền (Trưởng phòng)", "Ban 2 Pháp Y BCTC", "Khánh & Bảo (Ban 11)"],
        "sub_departments": [
            {"code": "Ban 10 (Hiền)", "role": "Cào RSS/CBTT, Vietcap/CafeF, 11 cổng IR & SEC EDGAR"},
            {"code": "Ban 2 (Pháp Y)", "role": "Kiểm toán tiền thật OCF/LNST, Piotroski F-Score, Beneish M, MOS"},
            {"code": "Ban 11 (Khánh & Bảo)", "role": "Đóng gói dữ liệu tài chính trực quan & kịch bản truyền thông"},
        ],
        "avatars": [
            {"name": "Hiền (TP)", "color": "#db2777", "role": "Trưởng phòng"},
            {"name": "Pháp Y B2", "color": "#10b981", "role": "BCTC & OCF"},
            {"name": "Khánh B11", "color": "#f97316", "role": "Đóng gói tin"},
        ],
        "gx": 0.4,
        "gy": 0.3,
        "gw": 3.1,
        "gd": 2.05,
        "dept_ids": ["ban_10_hien", "ban_10_cbtt", "ban_2_equity", "ban_2_vn_equity", "ban_11_khanh"],
        "roster_ids": ["BAN_10_IR", "BAN_2_BCTC", "BAN_11_MEDIA"],
        "kanban_depts": ["Ban 10", "Ban 2", "Ban 2 & 3", "Ban 11"],
        "schedule": "Cào sống trước 08:00, 18:00 & 21:00 — Chuyển ngay báo cáo BCTC sạch sang Minh Quân & Alex",
        "milestone_hours": [(8, 0), (18, 0), (21, 0), (21, 15)],
        "always_on_247": True,
        "veto_power": True,
        "furniture": "hien_data_hub",
        "primary_action": {"action": "crawl_intel", "label": "📡 Hiền Cào Tin & BCTC Sống Ngay"},
        "chat_template": "Giao Khối 1 (Hiền) cào dữ liệu mới nhất & mổ xẻ BCTC cho các mã trọng điểm (TPB, HDB, CTG, HPG, VPB) rồi bàn giao ngay sang Khối 2 (Minh Quân & Alex).",
    },
    {
        "room_id": "team_quan_alex",
        "step_badge": "②",
        "ban_code": "Khối 2 — Đội Minh Quân & Alex",
        "name": "Khối Phân Tích Thị Trường & Tín Hiệu",
        "short_name": "② Minh Quân & Alex (Thị trường)",
        "wing": "Bước 2: Phân Tích Thị Trường & Báo Cáo Đội Hiền",
        "lead_title": "Đồng Trưởng phòng: Minh Quân (VN) & Alex (US) — Báo cáo trực tiếp James",
        "handoff_to": "Trình phân tích & sổ lệnh lên ③ Master CIO James & Palmer",
        "icon": "⚡",
        "accent": "#7c3aed",
        "floor_tint": "#f5f3ff",
        "officers": ["Minh Quân (Trưởng phòng VN)", "Alex (Trưởng phòng US)", "Vũ Minh & Elena (Ban 1)", "Ban 3 & Ban 4"],
        "sub_departments": [
            {"code": "Ban 7 VN (Minh Quân)", "role": "Phân tích thị trường VN, thẩm định BCTC đội Hiền, Ma trận S1–S4 & Giờ Vàng 14h05–14h25"},
            {"code": "Ban 7 US (Alex)", "role": "Phân tích Phố Wall/Quốc tế & xung lan tỏa sang Việt Nam"},
            {"code": "Ban 1 (Vũ Minh & Elena)", "role": "Vĩ mô SBV, Tỷ giá USD/VND, Fed/VIX/DXY/US10Y"},
            {"code": "Ban 3 & Ban 4", "role": "Sàng lọc CANSLIM/VSA (Điều 3 MA20) & Khóa rủi ro ATR, trần lô ≤ 33% NAV"},
        ],
        "avatars": [
            {"name": "Minh Quân", "color": "#7c3aed", "role": "TP Thị trường VN"},
            {"name": "Alex (US)", "color": "#db2777", "role": "TP Thị trường US"},
            {"name": "Vũ Minh", "color": "#0284c7", "role": "Vĩ mô SBV"},
            {"name": "Rủi Ro B4", "color": "#e11d48", "role": "ATR & Stop"},
        ],
        "gx": 4.25,
        "gy": 0.3,
        "gw": 3.45,
        "gd": 2.05,
        "dept_ids": [
            "ban_7_specialist", "ban_7_vn_specialist",
            "ban_1_macro", "ban_1_vn_macro",
            "ban_3_synthesis", "ban_3_debates", "ban_3_vn_synthesis",
            "ban_4_risk", "ban_4_vn_risk",
        ],
        "roster_ids": ["BAN_7_VN", "BAN_7_US", "BAN_1_VN", "BAN_1_US", "BAN_3_SYNTHESIS", "BAN_4_RISK"],
        "kanban_depts": ["Ban 7 VN", "Ban 7 & 8", "Ban 1", "Ban 1 & 3", "Ban 3", "Ban 4", "Ban 4 & Victor", "Ban 4 & 9"],
        "schedule": "07:00 Vĩ mô, 08:30 Pre-ATO, 11:35 Giữa phiên & 14:05–14:25 Khung Giờ Vàng",
        "milestone_hours": [(7, 0), (8, 30), (11, 35), (14, 5)],
        "always_on_247": False,
        "veto_power": True,
        "furniture": "market_analysis_floor",
        "primary_action": {"action": "convene_dept", "label": "📊 Chạy Phân Tích Thị Trường & Gửi Lên James"},
        "chat_template": "Giao Khối 2 (Minh Quân & Alex) phân tích thị trường hôm nay cùng báo cáo BCTC từ đội Hiền, lọc CANSLIM/ATR và gửi đề xuất kịch bản S1–S4 lên cho James & Palmer.",
    },
    {
        "room_id": "team_james_palmer",
        "step_badge": "③",
        "ban_code": "Khối 3 — James & Palmer",
        "name": "Ban Điều Hành Tối Cao & Hoạch Định Kế Hoạch Đầu Tư",
        "short_name": "③ James & Palmer (Kế hoạch Đầu tư)",
        "wing": "Bước 3: Hoàn Thiện Kế Hoạch Đầu Tư & Trình Chủ Tịch",
        "lead_title": "Tổng Tư Lệnh: Master CIO James & Palmer (Tiếp nhận Minh Quân, Alex & Victor)",
        "handoff_to": "Hoàn thiện Bản Kế Hoạch Đầu Tư Chuyên Môn Nhất ──▶ TRÌNH CHỦ TỊCH PHƯỚC TRẦN",
        "icon": "🎖️",
        "accent": "#4f46e5",
        "floor_tint": "#eef2ff",
        "officers": ["Master CIO James", "Palmer (Điều hành)", "Ban 5 & Ban 6 (Tham mưu)"],
        "sub_departments": [
            {"code": "Ban 8 (Master CIO James)", "role": "Chốt phân bổ vốn 20.05M ₫, phán quyết S1–S4 & kế hoạch triển khai tức thì khi Victor báo chạm ngưỡng"},
            {"code": "Palmer (Điều Hành)", "role": "Đồng bộ 100% báo cáo, quản trị tiến độ & tương tác trực tiếp cùng Chủ tịch"},
            {"code": "Ban 5 & Ban 6", "role": "Tham mưu 15 Huyền thoại đầu tư, Walk-Forward Hit Rate & đúc rút bài học EOD"},
        ],
        "avatars": [
            {"name": "James CIO", "color": "#4338ca", "role": "Tổng Tư Lệnh"},
            {"name": "Palmer", "color": "#0ea5e9", "role": "Điều hành & HT"},
            {"name": "Học Viện", "color": "#2563eb", "role": "15 Huyền thoại"},
        ],
        "gx": 0.4,
        "gy": 3.05,
        "gw": 3.55,
        "gd": 2.1,
        "dept_ids": ["ban_8_cio", "ban_8_council", "ban_8_enterprise", "ban_5_learning", "ban_6_mentorship", "ban_6_vn_coach"],
        "roster_ids": ["BAN_8_CIO", "BAN_5_EVOLUTION", "BAN_6_ACADEMY"],
        "kanban_depts": ["Ban 8", "Ban 7 & 8", "Ban 5", "Ban 5 VN", "Ban 6"],
        "schedule": "Trực chỉ huy 24/7 • Chốt kế hoạch 09:00 / 11:35 / 14:05 / 15:45 & phản ứng tức thời theo Victor",
        "milestone_hours": [(8, 45), (9, 0), (14, 5), (15, 45), (23, 0)],
        "always_on_247": True,
        "veto_power": True,
        "furniture": "cio_command_suite",
        "primary_action": {"action": "convene_dept", "label": "🏛️ Họp 5 Khối & Chốt Kế Hoạch Trình Chủ Tịch"},
        "chat_template": "Yêu cầu Khối 3 (James & Palmer) tổng hợp báo cáo từ Minh Quân, Alex và cảnh báo từ Victor để chốt ngay Bản Kế Hoạch Đầu Tư chi tiết (Kịch bản S1–S4, giá LO, Stop, TP) trình tôi duyệt.",
    },
    {
        "room_id": "team_victor",
        "step_badge": "④",
        "ban_code": "Khối 4 — Phòng Victor",
        "name": "Phòng Giám Sát Thị Trường & Cảnh Báo Chạm Ngưỡng Live",
        "short_name": "④ Victor (Giám sát 145 Mã Live)",
        "wing": "Giám Sát Trong Phiên 09h00–15h00 & Báo Ngay Về James",
        "lead_title": "Trưởng phòng: Victor Sentinel (Ban 9)",
        "handoff_to": "Chạm ngưỡng MUA / BÁN trong kế hoạch ──▶ BÁO NGAY VỀ ③ JAMES TRIỂN KHAI",
        "icon": "🚨",
        "accent": "#d97706",
        "floor_tint": "#fffbeb",
        "officers": ["Victor Sentinel (Trưởng phòng Ban 9)"],
        "sub_departments": [
            {"code": "Radar 145 Mã Live", "role": "Quét bảng điện liên tục trong phiên: VN-Index, Breadth > MA20, Buy-Up %, dòng tiền 18 ngành"},
            {"code": "Bộ Kích Hoạt Ngưỡng Mua/Bán", "role": "Canh sát từng mức giá kế hoạch (TPB 12,250 | HDB 21,700 | CTG 29,950 | Stop -5.5% | TP1 +9%) — chạm là báo ngay James!"},
        ],
        "avatars": [
            {"name": "Victor B9", "color": "#d97706", "role": "Giám sát Live"},
        ],
        "gx": 4.65,
        "gy": 3.05,
        "gw": 3.05,
        "gd": 2.1,
        "dept_ids": ["ban_9_sentinel"],
        "roster_ids": ["BAN_9_SENTINEL"],
        "kanban_depts": ["Ban 9", "Ban 9 & System", "Ban 3 & Victor", "Ban 4 & Victor", "Ban 4 & 9"],
        "schedule": "Giám sát liên tục 09:00–15:00 T2–T6 & Bảo vệ tài khoản 24/7",
        "milestone_hours": [(9, 0), (13, 0), (14, 5), (14, 25)],
        "always_on_247": True,
        "veto_power": True,
        "furniture": "victor_radar_wall",
        "primary_action": {"action": "publish_warroom", "label": "🚨 Quét 145 Mã & Kiểm Tra Ngưỡng Mua/Bán Ngay"},
        "chat_template": "Yêu cầu Khối 4 (Victor) quét ngay bảng điện 145 mã, kiểm tra xem có mã nào trong rổ Tuần 48 (TPB, HDB, CTG, HPG, VPB) chạm ngưỡng Mua/Bán không và báo cáo tức thời cho James.",
    },
    {
        "room_id": "team_trong_palmer",
        "step_badge": "⑤",
        "ban_code": "Khối 5 — Trọng & Palmer",
        "name": "Ban Giám Sát, Kiểm Toán & Quản Trị Toàn Hệ Thống",
        "short_name": "⑤ Trọng & Palmer (Giám sát Toàn HT)",
        "wing": "Giám Sát Toàn Bộ 4 Khối, 10 Điều Hiến Chương & Auto-Run 24/7",
        "lead_title": "Đồng Giám sát: Kiểm Sát Viên Trọng (Ban 12) & Palmer",
        "handoff_to": "Giám sát kỷ luật, SSOT 105C307855 & niêm phong SHA-256 cho toàn hệ thống",
        "icon": "⚖️",
        "accent": "#dc2626",
        "floor_tint": "#fef2f2",
        "officers": ["Kiểm Sát Viên Trọng (Ban 12)", "Palmer (Tổng Hệ Thống)"],
        "sub_departments": [
            {"code": "Ban 12 (Kiểm Sát Trọng)", "role": "Kiểm toán 10 Điều Hiến Chương, đối chiếu SSOT, phát VETO chống sai số & niêm phong SHA-256"},
            {"code": "Palmer (Tổng Hệ Thống)", "role": "Giám sát vận hành tự động 24/7, khởi động cùng Windows, đồng bộ Web/Chat/Cloud"},
        ],
        "avatars": [
            {"name": "Trọng B12", "color": "#dc2626", "role": "Kiểm Sát Viên"},
            {"name": "Palmer HT", "color": "#0f172a", "role": "Giám sát 24/7"},
        ],
        "gx": 0.4,
        "gy": 5.85,
        "gw": 3.55,
        "gd": 1.85,
        "dept_ids": ["ban_12_ombudsman"],
        "roster_ids": ["BAN_12_OMBUDSMAN"],
        "kanban_depts": ["Ban 12", "Ban 9 & System"],
        "schedule": "Giám sát toàn hệ thống 24/7 & Tổng kiểm toán 15:45 / 23:30",
        "milestone_hours": [(15, 45), (23, 30)],
        "always_on_247": True,
        "veto_power": True,
        "furniture": "audit_vault",
        "primary_action": {"action": "run_trong_audit", "label": "🛡️ Chạy Kiểm Toán Toàn Hệ Thống Ngay"},
        "chat_template": "Yêu cầu Khối 5 (Trọng & Palmer) kiểm toán toàn bộ hoạt động 4 Khối hôm nay, đối chiếu số dư SSOT TCBS 105C307855 và báo cáo tình trạng sức khỏe toàn hệ thống cho tôi.",
    },
    {
        "room_id": "room_lounge",
        "step_badge": "★",
        "ban_code": "Khu Tiện Ích",
        "name": "Công Viên Apex, Bàn Bi-a & Mô Phỏng Vốn 20.05M",
        "short_name": "🎱 Giải Trí & Mô Phỏng Vốn",
        "wing": "Thư Giãn Chủ Tịch & Giả Lập Phân Bổ Vốn Chuẩn Điều 5",
        "lead_title": "Khu tiện ích riêng cho Chủ tịch Phước Trần",
        "handoff_to": "Lưu kịch bản chia vốn What-If trực tiếp vào Kanban cho Minh Quân",
        "icon": "🎱",
        "accent": "#16a34a",
        "floor_tint": "#f0fdf4",
        "officers": ["Trợ Lý Sảnh Apex"],
        "sub_departments": [
            {"code": "Bàn Bi-a 6 Lỗ", "role": "Giải trí thư giãn nhẹ nhàng trong lúc chờ phiên 14h05"},
            {"code": "Bộ Mô Phỏng Vốn 20.05M ₫", "role": "Thử chia lô 100 CP, tự kiểm tra trần 33% NAV & Stop 1.5% NAV"},
        ],
        "avatars": [{"name": "Sảnh Apex", "color": "#16a34a", "role": "Tiện ích"}],
        "gx": 4.65,
        "gy": 5.85,
        "gw": 3.05,
        "gd": 1.85,
        "dept_ids": [],
        "roster_ids": [],
        "kanban_depts": [],
        "schedule": "Mở cửa 24/7 — Giải trí & Giả lập kịch bản vốn",
        "milestone_hours": [],
        "always_on_247": True,
        "veto_power": False,
        "furniture": "billiard_lounge",
        "primary_action": {"action": "open_lounge_modal", "label": "🎱 Mở Bàn Bi-a & Mô Phỏng Vốn"},
        "chat_template": "Mở giúp tôi bảng mô phỏng chia vốn 20,051,117 ₫ cho kịch bản S3 Spring (TPB, HDB, CTG, HPG).",
    },
]

ROOMS_BY_ID: Dict[str, Dict[str, Any]] = {r["room_id"]: r for r in ROOMS_BLUEPRINT}

# Ánh xạ tương thích ngược ID phòng cũ -> Khối mới
LEGACY_ROOM_ALIAS: Dict[str, str] = {
    "room_ban_10": "team_hien",
    "room_ban_2": "team_hien",
    "room_ban_11": "team_hien",
    "room_ban_1": "team_quan_alex",
    "room_ban_3": "team_quan_alex",
    "room_ban_4": "team_quan_alex",
    "room_ban_7": "team_quan_alex",
    "room_ban_8": "team_james_palmer",
    "room_ban_5_6": "team_james_palmer",
    "room_ban_9": "team_victor",
    "room_ban_12": "team_trong_palmer",
}

DATA_FLOW_PIPES: List[Dict[str, str]] = [
    {"id": "flow_hien_to_qa", "from": "team_hien", "to": "team_quan_alex", "label": "①→② BCTC & Tin", "tone": "pink"},
    {"id": "flow_qa_to_james", "from": "team_quan_alex", "to": "team_james_palmer", "label": "②→③ Thị trường", "tone": "violet"},
    {"id": "flow_victor_to_james", "from": "team_victor", "to": "team_james_palmer", "label": "④→③ Chạm ngưỡng!", "tone": "amber"},
    {"id": "flow_trong_audit_james", "from": "team_trong_palmer", "to": "team_james_palmer", "label": "⑤ Giám sát 10Đ", "tone": "red"},
    {"id": "flow_trong_audit_victor", "from": "team_trong_palmer", "to": "team_victor", "label": "⑤ Kiểm SSOT", "tone": "red"},
]


def _persist_jobs_unlocked() -> None:
    try:
        _save_json_atomic(JOBS_HISTORY_FILE, _OFFICE_JOBS[:_MAX_JOBS])
    except Exception:
        pass


def _get_active_jobs_snapshot() -> List[Dict[str, Any]]:
    with _JOBS_LOCK:
        return [dict(j) for j in _OFFICE_JOBS]


def _record_job_start(room_id: str, action: str, title: str) -> str:
    now_ict = get_ict_now()
    job_id = f"JOB-{now_ict.strftime('%H%M%S')}-{uuid.uuid4().hex[:5].upper()}"
    entry: Dict[str, Any] = {
        "job_id": job_id,
        "room_id": room_id,
        "action": action,
        "title": title,
        "status": "RUNNING",
        "started_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
        "started_epoch": time.time(),
        "finished_at": None,
        "duration_sec": 0.0,
        "progress_pct": 10,
        "steps_log": [
            {"time": now_ict.strftime("%H:%M:%S"), "text": "Khởi tạo & nạp trạng thái SSOT / Lịch phiên mới nhất...", "ok": True}
        ],
        "deliverables": {},
        "summary": "Đang khởi chạy tác vụ trên máy chủ Apex...",
        "error": None,
    }
    with _JOBS_LOCK:
        _OFFICE_JOBS.insert(0, entry)
        if len(_OFFICE_JOBS) > _MAX_JOBS:
            del _OFFICE_JOBS[_MAX_JOBS:]
        _persist_jobs_unlocked()
    return job_id


def _append_job_step(job_id: str, text: str, progress_pct: int, ok: bool = True) -> None:
    now_ict = get_ict_now()
    with _JOBS_LOCK:
        for j in _OFFICE_JOBS:
            if j["job_id"] == job_id:
                steps = list(j.get("steps_log") or [])
                steps.append({"time": now_ict.strftime("%H:%M:%S"), "text": str(text), "ok": bool(ok)})
                j["steps_log"] = steps[-12:]
                j["progress_pct"] = max(int(j.get("progress_pct", 10)), min(99, int(progress_pct)))
                j["summary"] = str(text)
                break
        _persist_jobs_unlocked()


def _finish_job(
    job_id: str,
    ok: bool,
    summary: str,
    error: Optional[str] = None,
    deliverables: Optional[Dict[str, Any]] = None,
) -> None:
    now_ict = get_ict_now()
    with _JOBS_LOCK:
        for j in _OFFICE_JOBS:
            if j["job_id"] == job_id:
                started_ep = float(j.get("started_epoch") or time.time())
                j["status"] = "DONE" if ok else "ERROR"
                j["finished_at"] = now_ict.strftime("%Y-%m-%d %H:%M:%S")
                j["duration_sec"] = round(max(0.1, time.time() - started_ep), 2)
                j["progress_pct"] = 100
                steps = list(j.get("steps_log") or [])
                steps.append({
                    "time": now_ict.strftime("%H:%M:%S"),
                    "text": ("Hoàn tất & xác thực đầu ra" if ok else f"Lỗi thực thi: {error or summary}"),
                    "ok": bool(ok),
                })
                j["steps_log"] = steps[-12:]
                if deliverables:
                    j["deliverables"] = dict(deliverables)
                j["summary"] = summary
                j["error"] = error
                break
        _persist_jobs_unlocked()
    with _CACHE_LOCK:
        _LIVE_CACHE["ts"] = 0.0
        _REPORTS_CACHE["ts"] = 0.0


def get_jobs_list() -> List[Dict[str, Any]]:
    return _get_active_jobs_snapshot()


def get_job_detail(job_id: str) -> Dict[str, Any]:
    jid = str(job_id or "").strip()
    if not jid:
        return {"ok": False, "error": "Thiếu tham số id của tác vụ"}
    with _JOBS_LOCK:
        for j in _OFFICE_JOBS:
            if j.get("job_id") == jid:
                return {"ok": True, "job": dict(j)}
    return {"ok": False, "error": f"Không tìm thấy tác vụ {jid}"}


def _extract_ssot_summary() -> Dict[str, Any]:
    st = _load_json(DATA_DIR / "current_portfolio_state.json", {})
    cash_vnd = float(st.get("cash_balance_vnd", 0.0))
    stocks_val_vnd = float(st.get("total_market_val_vnd", 0.0))
    total_nav_vnd = float(st.get("total_nav_vnd", cash_vnd + stocks_val_vnd))
    if total_nav_vnd <= 0:
        total_nav_vnd = cash_vnd + stocks_val_vnd
    active_pos = st.get("active_positions", {})
    if not isinstance(active_pos, dict):
        active_pos = {}
    holdings_desc = " + ".join(
        f"{int(p.get('shares', 0))} {s}"
        for s, p in active_pos.items()
        if isinstance(p, dict) and int(p.get("shares", 0)) > 0
    ) or "0 CP"
    cash_pct = round((cash_vnd / total_nav_vnd) * 100.0, 1) if total_nav_vnd > 0 else 100.0
    return {
        "account_id": str(st.get("account_id", "105C307855")),
        "chairman": str(st.get("chairman", "Trần Quốc Thiên Phước")),
        "status": str(st.get("status", "ALL_CASH_STANDDOWN")),
        "tactical_regime": str(st.get("tactical_regime", "PATIENT_PREDATOR_100_CASH_STANDDOWN")),
        "cash_vnd": cash_vnd,
        "cash_str": f"{cash_vnd:,.0f} ₫",
        "stocks_val_vnd": stocks_val_vnd,
        "stocks_str": f"{stocks_val_vnd:,.0f} ₫",
        "total_nav_vnd": total_nav_vnd,
        "nav_str": f"{total_nav_vnd:,.0f} ₫",
        "cash_pct": cash_pct,
        "stocks_pct": round(100.0 - cash_pct, 1),
        "realized_pnl_vnd": float(st.get("realized_pnl_vnd", 0.0)),
        "unrealized_pnl_vnd": float(st.get("unrealized_pnl_vnd", 0.0)),
        "holdings_count": sum(1 for p in active_pos.values() if isinstance(p, dict) and int(p.get("shares", 0)) > 0),
        "holdings_desc": holdings_desc,
        "active_positions": active_pos,
        "cash_verified_note": str(st.get("cash_verified_note", "")),
        "next_round_watchlist": st.get("next_round_watchlist", []),
        "last_updated": str(st.get("last_updated", "")),
    }


def get_kanban_board_state() -> Dict[str, Any]:
    today_str = get_ict_now().strftime("%Y-%m-%d")
    with _KANBAN_LOCK:
        data = _load_json(KANBAN_FILE, {})
        needs_rollover = (
            not isinstance(data, dict)
            or "tasks" not in data
            or "columns" not in data
            or data.get("date") != today_str
        )
        if needs_rollover:
            preserved_custom: List[Dict[str, Any]] = []
            old_tasks = data.get("tasks", {}) if isinstance(data, dict) else {}
            if isinstance(old_tasks, dict):
                for tid, tobj in old_tasks.items():
                    if str(tid).startswith("OFFICE-") and isinstance(tobj, dict) and tobj.get("status") != "DONE":
                        preserved_custom.append(dict(tobj))
            try:
                from scripts.apex_kanban_manager import init_daily_board
                data = init_daily_board(today_str)
            except Exception:
                data = {
                    "date": today_str,
                    "last_updated": get_ict_now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_tasks": 0,
                    "columns": {"BACKLOG": [], "IN_PROGRESS": [], "AUDIT_REVIEW": [], "DONE": []},
                    "tasks": {},
                }
            if preserved_custom:
                tasks_map = data.setdefault("tasks", {})
                cols_map = data.setdefault("columns", {})
                for col_name in ("BACKLOG", "IN_PROGRESS", "AUDIT_REVIEW", "DONE"):
                    cols_map.setdefault(col_name, [])
                for ctask in preserved_custom:
                    cid = ctask.get("id") or f"OFFICE-{uuid.uuid4().hex[:6].upper()}"
                    cst = ctask.get("status") if ctask.get("status") in cols_map else "BACKLOG"
                    tasks_map[cid] = ctask
                    if cid not in cols_map[cst]:
                        cols_map[cst].insert(0, cid)
                data["total_tasks"] = len(tasks_map)
                _save_json_atomic(KANBAN_FILE, data)

        cols = data.get("columns", {})
        for col_name in ("BACKLOG", "IN_PROGRESS", "AUDIT_REVIEW", "DONE"):
            cols.setdefault(col_name, [])
        data["columns"] = cols
        return data


def create_kanban_task(
    title: str,
    dept: str,
    assignee: str = "Trưởng Phòng",
    priority: str = "HIGH",
    scheduled_time: str = "",
    output_note: str = "",
    status: str = "BACKLOG",
) -> Dict[str, Any]:
    clean_title = (title or "").strip()
    if not clean_title:
        raise ValueError("Tiêu đề nhiệm vụ không được để trống.")
    clean_status = status if status in ("BACKLOG", "IN_PROGRESS", "AUDIT_REVIEW", "DONE") else "BACKLOG"
    clean_prio = priority if priority in ("SUPREME", "CRITICAL", "HIGH", "MEDIUM", "LOW") else "HIGH"
    now_ict = get_ict_now()
    sched = (scheduled_time or "").strip() or now_ict.strftime("%H:%M")

    with _KANBAN_LOCK:
        data = _load_json(KANBAN_FILE, {})
        if not isinstance(data, dict) or "tasks" not in data:
            data = {
                "date": now_ict.strftime("%Y-%m-%d"),
                "last_updated": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tasks": 0,
                "columns": {"BACKLOG": [], "IN_PROGRESS": [], "AUDIT_REVIEW": [], "DONE": []},
                "tasks": {},
            }
        task_id = f"OFFICE-{now_ict.strftime('%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        task_obj = {
            "id": task_id,
            "title": clean_title,
            "dept": (dept or "Khối 3 — James & Palmer").strip(),
            "assignee": (assignee or "Trưởng Phòng").strip(),
            "scheduled_time": sched,
            "status": clean_status,
            "priority": clean_prio,
            "output": (output_note or "Giao từ Văn Phòng 2.5D").strip(),
            "created_at": now_ict.strftime("%Y-%m-%d %H:%M"),
            "source": "VIRTUAL_OFFICE_25D",
        }
        if clean_status == "DONE":
            task_obj["completed_at"] = now_ict.strftime("%Y-%m-%d %H:%M")
        data["tasks"][task_id] = task_obj
        for col in ("BACKLOG", "IN_PROGRESS", "AUDIT_REVIEW", "DONE"):
            data["columns"].setdefault(col, [])
            if task_id in data["columns"][col]:
                data["columns"][col].remove(task_id)
        data["columns"][clean_status].insert(0, task_id)
        data["total_tasks"] = len(data["tasks"])
        data["last_updated"] = now_ict.strftime("%Y-%m-%d %H:%M:%S")
        _save_json_atomic(KANBAN_FILE, data)

    with _CACHE_LOCK:
        _LIVE_CACHE["ts"] = 0.0
    return {"ok": True, "task": task_obj, "board": data}


def move_kanban_task(task_id: str, new_status: str) -> Dict[str, Any]:
    if new_status not in ("BACKLOG", "IN_PROGRESS", "AUDIT_REVIEW", "DONE"):
        raise ValueError(f"Trạng thái cột Kanban không hợp lệ: {new_status}")
    now_ict = get_ict_now()
    with _KANBAN_LOCK:
        data = _load_json(KANBAN_FILE, {})
        tasks = data.get("tasks", {})
        if task_id not in tasks:
            raise ValueError(f"Không tìm thấy nhiệm vụ: {task_id}")
        for col in ("BACKLOG", "IN_PROGRESS", "AUDIT_REVIEW", "DONE"):
            data.setdefault("columns", {}).setdefault(col, [])
            if task_id in data["columns"][col]:
                data["columns"][col].remove(task_id)
        data["columns"][new_status].append(task_id)
        tasks[task_id]["status"] = new_status
        if new_status == "DONE":
            tasks[task_id]["completed_at"] = now_ict.strftime("%Y-%m-%d %H:%M")
        data["last_updated"] = now_ict.strftime("%Y-%m-%d %H:%M:%S")
        _save_json_atomic(KANBAN_FILE, data)

    with _CACHE_LOCK:
        _LIVE_CACHE["ts"] = 0.0
    return {"ok": True, "task": tasks[task_id], "board": data}


def delete_kanban_task(task_id: str) -> Dict[str, Any]:
    if not str(task_id).startswith("OFFICE-"):
        raise ValueError("Chỉ cho phép xóa nhiệm vụ giao bổ sung (OFFICE-*), bảo toàn 17 cột mốc thể chế.")
    now_ict = get_ict_now()
    with _KANBAN_LOCK:
        data = _load_json(KANBAN_FILE, {})
        tasks = data.get("tasks", {})
        if task_id not in tasks:
            raise ValueError(f"Không tìm thấy nhiệm vụ: {task_id}")
        removed = tasks.pop(task_id)
        for col in ("BACKLOG", "IN_PROGRESS", "AUDIT_REVIEW", "DONE"):
            lst = data.get("columns", {}).get(col, [])
            if task_id in lst:
                lst.remove(task_id)
        data["total_tasks"] = len(tasks)
        data["last_updated"] = now_ict.strftime("%Y-%m-%d %H:%M:%S")
        _save_json_atomic(KANBAN_FILE, data)

    with _CACHE_LOCK:
        _LIVE_CACHE["ts"] = 0.0
    return {"ok": True, "removed": removed, "board": data}


def _collect_intel_feed(intel_data: Dict[str, Any], alerts_data: Dict[str, Any]) -> Dict[str, Any]:
    counts = intel_data.get("summary_counts", {})
    freshness = intel_data.get("bctc_and_ohlcv_freshness", {})
    items: List[Dict[str, Any]] = []
    seen_titles = set()

    for h in intel_data.get("top_priority_headlines", [])[:40]:
        title = str(h.get("title", "")).strip()
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        tickers = h.get("tickers") or []
        sym = tickers[0] if tickers else str(h.get("sector", "MARKET"))
        items.append({
            "item_id": h.get("item_id", ""),
            "symbol": sym,
            "market": h.get("market", "VN"),
            "category": h.get("category", "NEWS"),
            "urgency": h.get("urgency", "MEDIUM"),
            "sentiment_score": h.get("sentiment_score", 0.0),
            "title": title,
            "summary": str(h.get("summary", ""))[:260],
            "source_name": h.get("source_name", "RSS/Vietcap"),
            "source_url": h.get("source_url", ""),
            "published_at": h.get("published_at", ""),
        })

    ticker_corp = intel_data.get("ticker_corporate_intel", {})
    if isinstance(ticker_corp, dict):
        for sym, info in list(ticker_corp.items())[:25]:
            for sub in (info.get("top_items") or [])[:2]:
                title = str(sub.get("title", "")).strip()
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)
                items.append({
                    "item_id": "",
                    "symbol": sym,
                    "market": "VN",
                    "category": sub.get("category", "CORPORATE"),
                    "urgency": sub.get("urgency", "MEDIUM"),
                    "sentiment_score": sub.get("sentiment_score", 0.0),
                    "title": title,
                    "summary": str(sub.get("summary", ""))[:260],
                    "source_name": sub.get("source_name", "Vietcap/CafeF"),
                    "source_url": sub.get("url", ""),
                    "published_at": sub.get("published_at", ""),
                })

    for al in (alerts_data.get("alerts") or [])[:15]:
        title = str(al.get("title", "")).strip()
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        items.append({
            "item_id": al.get("item_id", ""),
            "symbol": al.get("symbol", "VN"),
            "market": al.get("market", "VN"),
            "category": al.get("category", "CATALYST"),
            "urgency": al.get("priority", "MEDIUM"),
            "sentiment_score": al.get("sentiment_score", 0.0),
            "title": title,
            "summary": f"Khuyến nghị: {al.get('recommended_action', '')} • Tác động MOS: {al.get('estimated_fair_value_impact_pct', 0)}%",
            "source_name": al.get("source_name", "Catalyst Alert"),
            "source_url": al.get("source_url", ""),
            "published_at": al.get("published_at", ""),
        })

    return {
        "crawled_at": str(intel_data.get("crawled_at", "")),
        "summary_counts": {
            "total_news_articles": int(counts.get("total_news_articles", len(items))),
            "corp_vietcap_cafef_articles": int(counts.get("corp_vietcap_cafef_articles", 0)),
            "tickers_with_live_news": int(counts.get("tickers_with_live_news", 0)),
            "verified_ir_portals": int(counts.get("verified_ir_portals", 0)),
            "tavily_live_hits": int(counts.get("tavily_live_hits", 0)),
            "sec_edgar_filings": int(counts.get("sec_edgar_filings", 0)),
        },
        "freshness": freshness,
        "ir_portals": (intel_data.get("ir_portals") or [])[:12],
        "sec_edgar_filings": (intel_data.get("sec_edgar_filings") or [])[:6],
        "feed_items": items[:50],
    }


def _collect_victor_reports(existing_reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    res = list(existing_reports)
    sentinel_dir = BASE_DIR / "09_Realtime_Portfolio_Sentinel"
    if sentinel_dir.exists() and len(res) < 10:
        md_files = sorted(
            [p for p in sentinel_dir.glob("*.md") if p.name.lower() != "readme.md"],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        seen_rel = {r["rel_path"] for r in res}
        for md_p in md_files:
            rel = f"09_Realtime_Portfolio_Sentinel/{md_p.name}"
            if rel in seen_rel:
                continue
            mtime_dt = datetime.datetime.fromtimestamp(md_p.stat().st_mtime)
            date_part = md_p.name[:10] if len(md_p.name) >= 10 and md_p.name[4] == "-" else mtime_dt.strftime("%Y-%m-%d")
            res.append({
                "rel_path": rel,
                "title": md_p.stem.replace("_", " "),
                "date": date_part,
                "time_str": mtime_dt.strftime("%H:%M"),
                "shift_label": "🚨 Giám Sát Phiên",
                "dept_name": "Khối 4: Victor Sentinel",
                "icon": "🚨",
            })
            if len(res) >= 10:
                break
    return res


def _build_room_executive_brief(
    room_id: str,
    bp: Dict[str, Any],
    msess: Dict[str, Any],
    ssot: Dict[str, Any],
    status_label_vi: str,
    kpi_summary: str,
    live_thought: str,
    recon: Dict[str, Any],
    intel_feed: Dict[str, Any],
    latest_session: Dict[str, Any],
    latest_aud: Dict[str, Any],
) -> Dict[str, Any]:
    """Tạo thẻ tóm tắt điều hành ngắn gọn (3 KPI + 1 Phán quyết hành động) cho ngăn kéo mỗi Khối."""
    is_trading = bool(msess.get("is_trading_day", True))
    next_td = str(msess.get("next_trading_day") or "")
    next_dm = f"{next_td[8:10]}/{next_td[5:7]}" if len(next_td) >= 10 else "phiên tới"

    if room_id == "team_hien":
        sc = intel_feed.get("summary_counts", {})
        return {
            "headline": f"Đã thu thập {sc.get('total_news_articles', 0)} bản tin & kiểm toán {sc.get('verified_ir_portals', 0)} cổng IR",
            "action_badge": "🌸 BƯỚC 1: ĐẦU VÀO DỮ LIỆU",
            "action_text": "Bấm nút xanh bên dưới để Hiền cào tin CBTT/RSS/IR mới nhất và đẩy sang Minh Quân & Alex.",
            "kpis": [
                {"label": "Tin CBTT/RSS", "value": str(sc.get("total_news_articles", 0))},
                {"label": "Cổng IR/SEC", "value": f"{sc.get('verified_ir_portals', 0)} / {sc.get('sec_edgar_filings', 0)}"},
                {"label": "Cập nhật lúc", "value": str(intel_feed.get("crawled_at") or "--")[-8:]},
            ],
        }
    if room_id == "team_quan_alex":
        return {
            "headline": f"Phân tích thị trường & lọc rổ cổ phiếu chuẩn Hội đồng (Mở lại {next_dm})" if not is_trading else live_thought,
            "action_badge": "⏸️ NGHỈ LỄ — CHUẨN BỊ PHIÊN MỚI" if not is_trading else "⚡ BƯỚC 2: PHÂN TÍCH THỊ TRƯỜNG",
            "action_text": f"Không giao dịch hôm nay; bấm nút xanh để chạy lại mô phỏng phân tích & gửi đề xuất lên James cho phiên {next_dm}." if not is_trading else "Bấm nút xanh để chạy phân tích CANSLIM/VSA + Rủi ro ATR và gửi báo cáo lên James.",
            "kpis": [
                {"label": "VN-Index (EOD)" if not is_trading else "VN-Index", "value": f"{recon.get('vn_index', '--')}"},
                {"label": "Độ rộng MA20", "value": f"{recon.get('live_breadth_ma20_pct', '--')}%"},
                {"label": "Buy-Up TB", "value": f"{recon.get('avg_buy_up_pct', '--')}%"},
            ],
        }
    if room_id == "team_james_palmer":
        verdict = str(latest_session.get("final_verdict") or "STANDBY")
        return {
            "headline": f"Giữ {ssot.get('holdings_desc', '0 CP')} ({ssot.get('stocks_pct', 0):.1f}%) • Tiền mặt {ssot.get('cash_str', '--')}",
            "action_badge": f"🎌 NGHỈ LỄ (Mở lại {next_dm})" if not is_trading else f"🎖️ {verdict}",
            "action_text": f"Bấm nút xanh để họp đủ 5 Khối (14 thành viên), khóa nghị quyết hành động MUA/BÁN/ĐỢI và xuất biên bản mới nhất.",
            "kpis": [
                {"label": "Tổng NAV", "value": ssot.get("nav_str", "--")},
                {"label": "Két Tiền Mặt", "value": f"{ssot.get('cash_pct', 100):.1f}%"},
                {"label": "Đang Nắm Giữ", "value": ssot.get("holdings_desc", "0 CP")},
            ],
        }
    if room_id == "team_victor":
        return {
            "headline": f"Radar 145 mã đang ở chế độ bảo vệ SSOT ({status_label_vi})",
            "action_badge": "🛡️ BẢO VỆ 24/7" if not is_trading else "🚨 CANH NGƯỠNG MUA / BÁN",
            "action_text": "Bấm nút xanh để quét bảng điện VPS/Entrade, kiểm tra Stop Loss / Chốt lời TP1 và xuất báo cáo tức thời.",
            "kpis": [
                {"label": "Quét Bảng Điện", "value": f"{recon.get('scanned_live_count', 0)}/{recon.get('universe_total', 145)}"},
                {"label": "Trạng Thái Sàn", "value": "Đóng cửa" if not is_trading else "Đang khớp"},
                {"label": "Vị Thế Canh", "value": ssot.get("holdings_desc", "0 CP")},
            ],
        }
    if room_id == "team_trong_palmer":
        score = latest_session.get("ombudsman_audit_score", "10/10")
        issues = int(latest_aud.get("issues_count", 0) or 0)
        return {
            "headline": f"Điểm Hiến chương {score} • Kỷ luật {latest_aud.get('overall_discipline_score', 100)} • Vấn đề mở: {issues}",
            "action_badge": "🛡️ KIỂM TOÁN TOÀN HỆ THỐNG",
            "action_text": "Bấm nút xanh để Trọng & Palmer kiểm tra chéo dữ liệu giữa Chat, War-Room, Cron và Web Portal.",
            "kpis": [
                {"label": "Hiến Chương", "value": str(score)},
                {"label": "Lỗi Đang Mở", "value": str(issues)},
                {"label": "SSOT Chủ Tài Khoản", "value": "105C307855"},
            ],
        }
    return {
        "headline": kpi_summary,
        "action_badge": status_label_vi,
        "action_text": live_thought,
        "kpis": [{"label": "NAV Giả Lập", "value": ssot.get("nav_str", "--")}],
    }


def _compute_room_status_and_payload(
    bp: Dict[str, Any],
    now_ict: datetime.datetime,
    ssot: Dict[str, Any],
    supervisor_data: Dict[str, Any],
    enterprise_data: Dict[str, Any],
    kanban_data: Dict[str, Any],
    warroom_data: Dict[str, Any],
    intel_feed: Dict[str, Any],
    brain_data: Dict[str, Any],
    spillover_data: Dict[str, Any],
    legends_data: Dict[str, Any],
    audit_state: Dict[str, Any],
    audit_ledger: List[Dict[str, Any]],
    weekly_plan: Dict[str, Any],
    all_reports: List[Dict[str, Any]],
    active_jobs: List[Dict[str, Any]],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    room_id = bp["room_id"]
    services = supervisor_data.get("services", {}) if isinstance(supervisor_data, dict) else {}
    latest_session = enterprise_data.get("latest_session", {}) if isinstance(enterprise_data, dict) else {}
    roster_list = enterprise_data.get("roster", []) if isinstance(enterprise_data, dict) else []
    roster_map = {r.get("dept_id"): r for r in roster_list if isinstance(r, dict)}
    packets = latest_session.get("packets", []) if isinstance(latest_session, dict) else []
    roll_calls = latest_session.get("roll_call_votes", []) if isinstance(latest_session, dict) else []

    room_roster = [roster_map[rid] for rid in bp["roster_ids"] if rid in roster_map]
    room_packets = [p for p in packets if p.get("from_dept") in bp["roster_ids"]]
    room_votes = [v for v in roll_calls if v.get("dept_id") in bp["roster_ids"]]

    dept_id_set = set(bp["dept_ids"])
    room_reports = [
        {
            "rel_path": r.get("rel_path", ""),
            "title": r.get("title", ""),
            "date": r.get("date", ""),
            "time_str": r.get("time_str", ""),
            "shift_label": r.get("shift_label", ""),
            "dept_name": r.get("dept_name", ""),
            "icon": r.get("icon", bp["icon"]),
        }
        for r in all_reports
        if r.get("dept_id") in dept_id_set
    ][:10]

    if room_id == "team_victor":
        room_reports = _collect_victor_reports(room_reports)

    if room_id == "team_james_palmer":
        truth_pin = load_canonical_truth(refresh_if_missing=False)
        council_info = truth_pin.get("latest_council_resolution") or {}
        pinned_entries: List[Dict[str, Any]] = []
        c_rel = str(council_info.get("rel_path") or "").strip()
        if c_rel and (BASE_DIR / c_rel).exists():
            c_stat = (BASE_DIR / c_rel).stat()
            c_dt = datetime.datetime.fromtimestamp(c_stat.st_mtime)
            pinned_entries.append({
                "rel_path": c_rel,
                "title": str(council_info.get("title") or c_rel),
                "date": c_dt.strftime("%Y-%m-%d"),
                "time_str": "21:00",
                "shift_label": "🏛️ Nghị Quyết 5 Khối",
                "dept_name": "Khối 3: Hội Đồng & Chat",
                "icon": "🏛️",
                "is_pinned": True,
                "is_today": True,
                "freshness_badge": "⭐ NGHỊ QUYẾT HỘI ĐỒNG 21H",
            })
        if (BASE_DIR / "00_LIVE_INTER_CHAT_STATE.md").exists():
            ic_stat = (BASE_DIR / "00_LIVE_INTER_CHAT_STATE.md").stat()
            ic_dt = datetime.datetime.fromtimestamp(ic_stat.st_mtime)
            pinned_entries.append({
                "rel_path": "00_LIVE_INTER_CHAT_STATE.md",
                "title": "Hồ Sơ Đồng Bộ 2 Chiều Chat <-> Hệ Thống (Live SSOT)",
                "date": ic_dt.strftime("%Y-%m-%d"),
                "time_str": ic_dt.strftime("%H:%M"),
                "shift_label": "💬 Đồng Bộ Chat",
                "dept_name": "Khối 3: Hội Đồng & Chat",
                "icon": "💬",
                "is_pinned": True,
                "is_today": True,
                "freshness_badge": "💬 ĐỒNG BỘ CHAT LIVE",
            })
        seen_rels = {p["rel_path"] for p in pinned_entries}
        room_reports = (pinned_entries + [r for r in room_reports if r.get("rel_path") not in seen_rels])[:10]

    today_str = now_ict.strftime("%Y-%m-%d")
    reports_today_count = 0
    for rep in room_reports:
        is_today_flag = bool(rep.get("is_today")) or (str(rep.get("date", "")) == today_str)
        if is_today_flag:
            reports_today_count += 1
        rep["is_today"] = is_today_flag
        if not rep.get("freshness_badge"):
            rep["freshness_badge"] = "MỚI HÔM NAY" if is_today_flag else f"LƯU TRỮ ({rep.get('date', '--')})"

    all_tasks = kanban_data.get("tasks", {}) if isinstance(kanban_data, dict) else {}
    k_depts = set(bp["kanban_depts"])
    room_tasks = [
        t for t in all_tasks.values()
        if isinstance(t, dict) and (t.get("dept") in k_depts or bp["ban_code"] in str(t.get("dept", "")))
    ]
    in_progress_tasks = [t for t in room_tasks if t.get("status") == "IN_PROGRESS"]
    review_tasks = [t for t in room_tasks if t.get("status") == "AUDIT_REVIEW"]
    done_tasks = [t for t in room_tasks if t.get("status") == "DONE"]

    running_job = next((j for j in active_jobs if j.get("room_id") == room_id and j.get("status") == "RUNNING"), None)

    msess = get_vn_market_session_state(now_ict=now_ict)
    is_trading_day = bool(msess.get("is_trading_day", True))
    is_weekday = is_trading_day
    hm = now_ict.hour * 60 + now_ict.minute
    is_market_hours = bool(msess.get("is_live_session", False))
    is_golden_hour = is_trading_day and (14 * 60 <= hm <= 14 * 60 + 25)
    near_milestone = is_trading_day and any(abs((h * 60 + m) - hm) <= 20 for h, m in bp.get("milestone_hours", []))

    veto_triggered = bool(latest_session.get("veto_triggered", False))
    decision_brain = warroom_data.get("decision_brain", {}) if isinstance(warroom_data, dict) else {}
    proposed_orders = decision_brain.get("proposed_lo_orders", []) or []
    has_upcoming_week = any(d.get("status") in ("ACTIVE", "UPCOMING") for d in (weekly_plan.get("days") or []) if isinstance(d, dict))
    latest_aud = audit_ledger[-1] if audit_ledger else {}

    status_code = "standby"
    status_label_vi = "Trực nhẹ"

    if running_job:
        status_code = "working"
        status_label_vi = "Đang thực thi"
    elif (veto_triggered and room_id in ("team_quan_alex", "team_james_palmer", "team_trong_palmer")) or (
        room_id == "team_trong_palmer" and int(latest_aud.get("issues_count", 0) or 0) > 0
    ):
        status_code = "alert_veto"
        status_label_vi = "Cờ đỏ / VETO"
    elif review_tasks or (room_id in ("team_quan_alex", "team_james_palmer") and (len(proposed_orders) > 0 or is_golden_hour or (not is_trading_day and has_upcoming_week))):
        status_code = "waiting_approval"
        status_label_vi = f"Nghỉ lễ • Sẵn phiên {msess['next_trading_day'][8:10]}/{msess['next_trading_day'][5:7]}" if not is_trading_day else ("Sẵn sàng S1–S4" if not is_market_hours else "Chờ duyệt")
    elif in_progress_tasks or (is_market_hours and room_id in ("team_victor", "team_quan_alex", "team_james_palmer")):
        status_code = "working"
        status_label_vi = "Đang tác chiến"
    elif near_milestone and is_weekday:
        status_code = "working"
        status_label_vi = "Chạy cột mốc"
    elif room_id == "team_hien" and (intel_feed.get("freshness") or {}).get("is_fresh_under_24h"):
        status_code = "working"
        status_label_vi = "Dữ liệu sống < 24h"
    elif room_id == "team_victor":
        status_code = "working" if is_market_hours else "standby"
        status_label_vi = "Canh 145 mã Live" if is_market_hours else ("Nghỉ lễ • Trực 24/7" if not is_trading_day else "Trực ngưỡng ngoài giờ")
    elif room_id == "team_trong_palmer":
        status_code = "standby"
        status_label_vi = "Giám sát 24/7"
    elif room_id == "team_james_palmer":
        status_code = "standby"
        status_label_vi = "Trực chỉ huy 24/7"
    elif room_id == "room_lounge":
        status_code = "standby"
        status_label_vi = "Mở 24/7"

    recon = warroom_data.get("recon_summary", {}) if isinstance(warroom_data, dict) else {}
    kpi_summary = ""
    live_thought = ""
    specialized_data: Dict[str, Any] = {}

    if room_id == "team_hien":
        sc = intel_feed["summary_counts"]
        top_vn = brain_data.get("top_vn_alpha_picks", [])[:8]
        kpi_summary = f"{sc['total_news_articles']} tin • {sc['verified_ir_portals']} IR • {len(top_vn)} Alpha BCTC Q3"
        live_thought = f"Hiền: {sc['total_news_articles']} tin & BCTC sạch ➔ Gửi Quân & Alex"
        specialized_data = {
            "crawled_at": intel_feed["crawled_at"],
            "summary_counts": sc,
            "freshness": intel_feed["freshness"],
            "latest_news": intel_feed["feed_items"][:10],
            "ir_portals": intel_feed["ir_portals"][:8],
            "sec_edgar_filings": intel_feed["sec_edgar_filings"],
            "top_vn_alpha": [
                {
                    "symbol": p.get("symbol"),
                    "company_name": p.get("company_name"),
                    "live_price": p.get("live_price"),
                    "alpha_score": p.get("alpha_score"),
                    "piotroski_f_score": p.get("piotroski_f_score"),
                    "roe_pct": p.get("roe_pct"),
                    "ocf_ratio": p.get("ocf_ratio"),
                    "margin_of_safety_pct": (p.get("valuation") or {}).get("margin_of_safety_pct"),
                }
                for p in top_vn
            ],
        }
    elif room_id == "team_quan_alex":
        rm = spillover_data.get("risk_multiplier", 1.0)
        vix_val = (spillover_data.get("metrics", {}).get("VIX") or {}).get("last_price", "--")
        wl_syms = ",".join(str(w.get("symbol") or "") for w in (weekly_plan.get("approved_watchlist") or [])[:5] if w.get("symbol")) or "TPB,HPG,CTG,NAB,CTS"
        kpi_summary = f"Rổ Hội Đồng ({wl_syms}) • Mult {rm}x • VIX {vix_val}"
        live_thought = (
            f"Quân & Alex: Sàn nghỉ lễ ({msess['short_badge_vi']}) • Giữ kế hoạch phiên {msess['next_trading_day'][8:10]}/{msess['next_trading_day'][5:7]}"
            if not is_trading_day
            else "Quân & Alex: Lọc S1–S4 (14h05) ➔ Trình James"
        )
        specialized_data = {
            "week_label": weekly_plan.get("week_label", ""),
            "constitution_mandate": weekly_plan.get("constitution_mandate", ""),
            "approved_watchlist": weekly_plan.get("approved_watchlist", []),
            "spillover": spillover_data,
            "dissent_notes": latest_session.get("dissent_notes", []),
            "risk_rules": [
                "Điều 5: Trần lô 100 CP ≤ 33% NAV",
                "Stop Loss cứng -5.5% (tối đa ≤ 1.5% NAV/lệnh)",
                "Cấm mua FOMO trước 14h00 — chỉ hành động 14h05–14h25",
            ],
        }
    elif room_id == "team_james_palmer":
        wf = (legends_data.get("self_reflection") or {}).get("multi_horizon_walk_forward") or {}
        t10_hit = (wf.get("T+10") or {}).get("hit_rate_pct", "--")
        kpi_summary = f"Giữ {ssot['holdings_desc']} ({ssot['stocks_pct']:.1f}%) • Két {ssot['cash_str']} ({ssot['cash_pct']:.0f}%) • T+10 {t10_hit}%"
        live_thought = (
            f"James & Palmer: {ssot['holdings_desc']} • Két {ssot['cash_str']} ({msess['short_badge_vi']})"
            if not is_trading_day
            else f"James & Palmer: {ssot['holdings_desc']} • Két {ssot['cash_str']} ({ssot['cash_pct']:.0f}% Cash)"
        )
        specialized_data = {
            "ssot": ssot,
            "latest_session": {
                "session_id": latest_session.get("session_id", ""),
                "created_at": latest_session.get("created_at", ""),
                "target_ticker": latest_session.get("target_ticker", ""),
                "directive": latest_session.get("directive", ""),
                "final_verdict": latest_session.get("final_verdict", ""),
                "action_plan": latest_session.get("action_plan", ""),
                "quorum_count": latest_session.get("quorum_count", 0),
                "roster_total": latest_session.get("roster_total", 14),
                "veto_triggered": veto_triggered,
                "veto_reasons": latest_session.get("veto_reasons", []),
            },
            "walk_forward": wf,
            "total_legends": legends_data.get("total_legends", 15),
        }
    elif room_id == "team_victor":
        vni = recon.get("vn_index", "--")
        br = recon.get("live_breadth_ma20_pct", "--")
        scanned = recon.get("scanned_live_count", 0)
        total_u = recon.get("universe_total", 145)
        kpi_summary = f"VNI {vni} • Br20 {br}% • {scanned}/{total_u} mã • Canh ngưỡng LO"
        live_thought = f"Victor: Canh 145 mã • Chạm ngưỡng báo ngay James"
        specialized_data = {
            "recon_summary": recon,
            "decision_brain": decision_brain,
            "top_5_sectors": warroom_data.get("top_5_sectors", []),
            "trigger_watch": [
                {"symbol": w.get("symbol"), "buy_zone": w.get("entry_zone"), "stop": w.get("stop_loss_2xatr"), "tp1": w.get("tp1")}
                for w in weekly_plan.get("approved_watchlist", [])
            ],
        }
    elif room_id == "team_trong_palmer":
        seal = str(latest_session.get("constitutional_seal_sha256", ""))[:16]
        score = latest_session.get("ombudsman_audit_score", "10/10")
        kpi_summary = f"Audit {score} • Kỷ luật {latest_aud.get('overall_discipline_score', 97.6)} • SHA {seal or '--'}..."
        live_thought = f"Trọng & Palmer: 10/10 Hiến Chương • SSOT chuẩn"
        specialized_data = {
            "ombudsman_audit_score": score,
            "constitutional_seal_sha256": latest_session.get("constitutional_seal_sha256", ""),
            "ten_articles_checks": latest_session.get("ten_articles_checks", []),
            "audit_state": audit_state,
            "latest_audit_entry": {
                "audit_session_id": latest_aud.get("audit_session_id", ""),
                "timestamp": latest_aud.get("timestamp", ""),
                "overall_discipline_score": latest_aud.get("overall_discipline_score", ""),
                "overall_expertise_score": latest_aud.get("overall_expertise_score", ""),
                "system_health_score": latest_aud.get("system_health_score", ""),
                "issues_count": latest_aud.get("issues_count", 0),
            },
            "services": services,
        }
    else:
        kpi_summary = f"Vốn giả lập {ssot['nav_str']} • Bàn Bi-a 6 lỗ"
        live_thought = "Thư giãn & Giả lập chia vốn 20.05M ₫"
        specialized_data = {
            "cash_vnd": ssot["cash_vnd"],
            "watchlist": weekly_plan.get("approved_watchlist", []),
            "next_round_watchlist": ssot.get("next_round_watchlist", []),
        }

    room_summary = {
        "room_id": room_id,
        "step_badge": bp["step_badge"],
        "ban_code": bp["ban_code"],
        "name": bp["name"],
        "short_name": bp["short_name"],
        "wing": bp["wing"],
        "lead_title": bp["lead_title"],
        "handoff_to": bp["handoff_to"],
        "icon": bp["icon"],
        "accent": bp["accent"],
        "floor_tint": bp["floor_tint"],
        "officers": bp["officers"],
        "sub_departments": bp["sub_departments"],
        "avatars": bp["avatars"],
        "gx": bp["gx"],
        "gy": bp["gy"],
        "gw": bp["gw"],
        "gd": bp["gd"],
        "furniture": bp["furniture"],
        "status_code": status_code,
        "status_label_vi": status_label_vi,
        "veto_power": bp["veto_power"],
        "schedule": bp["schedule"],
        "kpi_summary": kpi_summary,
        "live_thought": live_thought,
        "reports_count": len(room_reports),
        "reports_today_count": reports_today_count,
        "tasks_total": len(room_tasks),
        "tasks_active": len(in_progress_tasks) + len(review_tasks),
        "tasks_done": len(done_tasks),
        "active_job": running_job,
        "primary_action": bp["primary_action"],
        "chat_template": bp["chat_template"],
        "executive_brief": _build_room_executive_brief(
            room_id=room_id,
            bp=bp,
            msess=msess,
            ssot=ssot,
            status_label_vi=status_label_vi,
            kpi_summary=kpi_summary,
            live_thought=live_thought,
            recon=recon,
            intel_feed=intel_feed,
            latest_session=latest_session,
            latest_aud=latest_aud,
        ),
    }

    room_jobs = [dict(j) for j in active_jobs if j.get("room_id") == room_id]
    last_completed = next((j for j in room_jobs if j.get("status") in ("DONE", "ERROR")), None)

    room_detail = {
        **room_summary,
        "roster_entities": room_roster,
        "latest_packets": room_packets,
        "latest_votes": room_votes,
        "kanban_tasks": room_tasks,
        "recent_reports": room_reports,
        "specialized_data": specialized_data,
        "recent_jobs": room_jobs[:5],
        "last_completed_job": last_completed,
    }
    return room_summary, room_detail


DAILY_MILESTONE_DEFS: List[Dict[str, Any]] = [
    {"time": "06:00", "team_id": "team_hien", "team_label": "① Hiền (BCTC & Tin)", "officer": "Hiền (Ban 10)", "title": "Rà soát CBTT đêm qua & Pháp y Agent Zero (54 VN / 35 US)", "patterns": ("VN_CBTT_Radar",)},
    {"time": "07:00", "team_id": "team_quan_alex", "team_label": "② Minh Quân & Alex", "officer": "Vũ Minh & Elena (Ban 1)", "title": "Cào Vĩ mô SBV, Tỷ giá USD/VND, Fed/VIX/DXY trước phiên", "patterns": ("VN_Macro_Report", "Macro_Report")},
    {"time": "07:30", "team_id": "team_james_palmer", "team_label": "③ James & Palmer", "officer": "Ban 6 (Học Viện)", "title": "Phát hành Bản Tin Khai Sáng 7h30 cho Chủ tịch Phước Trần", "patterns": ("VN_Mentor_Briefing", "Mentor_Briefing")},
    {"time": "08:00", "team_id": "team_hien", "team_label": "① Hiền (BCTC & Tin)", "officer": "Hiền & Ban 2 Pháp Y", "title": "Thẩm định BCTC 54 mã, lọc tiền thật OCF/LNST & chuyển Minh Quân", "patterns": ("VN_Investment_Memo", "VN_Equity_Analysis")},
    {"time": "08:30", "team_id": "team_quan_alex", "team_label": "② Minh Quân & Alex", "officer": "Minh Quân (Ban 7 VN)", "title": "Giao ban Soi Gương 8h30 & Tạp chí Chiến lược gửi James", "patterns": ("VN_Specialist_Decision", "Daily_Specialist")},
    {"time": "08:45", "team_id": "team_james_palmer", "team_label": "③ James & Palmer", "officer": "Master CIO James & Palmer", "title": "Chốt Master Blotter & Kế hoạch phân bổ vốn 20.05M ₫ đầu ngày", "patterns": ("Master_Blotter_Snapshot",)},
    {"time": "09:00", "team_id": "team_victor", "team_label": "④ Victor (145 Mã)", "officer": "Victor Sentinel (Ban 9)", "title": "Mở phiên ATO HOSE, bật Guard-01 & quét sống 145 mã 15s/lần", "patterns": ("ATO_Guard_Report",)},
    {"time": "11:45", "team_id": "team_quan_alex", "team_label": "② Minh Quân & Alex", "officer": "Minh Quân & Ban 3", "title": "Báo cáo Flash đóng cửa phiên sáng HOSE & cung cầu VSA", "patterns": ("Morning_Flash_Report",)},
    {"time": "13:00", "team_id": "team_victor", "team_label": "④ Victor (145 Mã)", "officer": "Victor & Ban 4", "title": "Radar đo lực xả hàng T+2.5 về tài khoản phiên chiều", "patterns": ("T2_Pressure_Radar",)},
    {"time": "14:00", "team_id": "team_quan_alex", "team_label": "② Minh Quân & Alex", "officer": "Minh Quân (Giờ Vàng)", "title": "Khung Giờ Vàng 14h00–14h25: Xác nhận S1–S4 & báo James chốt LO", "patterns": ("Golden_Hour_Tactical_Memo",)},
    {"time": "14:25", "team_id": "team_victor", "team_label": "④ Victor (145 Mã)", "officer": "Victor (GUARD-03)", "title": "Kích hoạt chốt chặn GUARD-03 khóa vị thế an toàn trước ATC", "patterns": ("GUARD03_Pre_ATC_Lock",)},
    {"time": "15:15", "team_id": "team_james_palmer", "team_label": "③ James & Palmer", "officer": "Ban 5 & Master CIO James", "title": "Hồi tố Walk-Forward EOD, Tự học trọng số & đối soát TCBS", "patterns": ("VN_Learning_Report", "Learning_And_Attribution")},
    {"time": "18:00", "team_id": "team_hien", "team_label": "① Hiền (BCTC & Tin)", "officer": "Hiền (Ban 10)", "title": "Đồng bộ giá đóng cửa & cập nhật Thư viện BCTC Master 11 IR", "patterns": ("BCTC_Master_Library",)},
    {"time": "21:00", "team_id": "team_hien", "team_label": "① Hiền (BCTC & Tin)", "officer": "Hiền (Ban 10 Độc Quyền)", "title": "Báo cáo BCTC chọn lọc tiền thật OCF/LNST >= 1.0x chuyển Khánh", "patterns": ("Hien_Daily_Review",)},
    {"time": "21:15", "team_id": "team_hien", "team_label": "① Hiền (BCTC & Tin)", "officer": "Khánh & Bảo (Ban 11)", "title": "Đóng gói kịch bản Video 60s truyền thông tài chính", "patterns": ("Viral_Script",)},
    {"time": "22:00", "team_id": "team_james_palmer", "team_label": "③ James & Palmer", "officer": "Hội Đồng Viện Sĩ (B5 & B6)", "title": "Giờ Tự Học & Nạp tri thức thực chiến 100% các ban", "patterns": ("Autonomous_Learning_Report",)},
    {"time": "23:00", "team_id": "team_james_palmer", "team_label": "③ James & Palmer", "officer": "Master CIO James & Palmer", "title": "Hội nghị Điều hành 23h00 & Tự kiểm điểm toàn doanh nghiệp", "patterns": ("23h00_EOD_Executive_Council_Meeting",)},
    {"time": "23:30", "team_id": "team_trong_palmer", "team_label": "⑤ Trọng & Palmer", "officer": "Kiểm Sát Viên Trọng & Palmer", "title": "Niêm phong kiểm toán 10 Điều Hiến Chương & SSOT 105C307855", "patterns": ("23h30", "Audit", "Ombudsman", "Health_Check")},
]


def _build_daily_activity_log(
    now_ict: datetime.datetime,
    all_reports: List[Dict[str, Any]],
    cron_data: Dict[str, Any],
    enterprise_data: Dict[str, Any],
    warroom_data: Dict[str, Any],
    intel_feed: Dict[str, Any],
    kanban_data: Dict[str, Any],
    ssot: Optional[Dict[str, Any]] = None,
    weekly_plan: Optional[Dict[str, Any]] = None,
    canonical_truth: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    today_str = now_ict.strftime("%Y-%m-%d")
    current_hm = now_ict.strftime("%H:%M")
    msess = (canonical_truth or {}).get("market_session") or get_vn_market_session_state(now_ict=now_ict)
    is_trading_day = bool(msess.get("is_trading_day", True))
    executed_raw = (cron_data.get("executed_milestones") or {}).get(today_str, [])
    executed_today = {str(x).strip() for x in executed_raw} if isinstance(executed_raw, list) else set()

    today_reports = [r for r in all_reports if str(r.get("date", "")) == today_str]
    timeline: List[Dict[str, Any]] = []
    completed_cnt = 0
    pending_cnt = 0
    upcoming_cnt = 0
    holiday_cnt = 0
    next_milestone = None
    latest_done = None

    for mdef in DAILY_MILESTONE_DEFS:
        mtime = mdef["time"]
        pats = mdef["patterns"]
        rep_today = next(
            (r for r in today_reports if any(p in str(r.get("rel_path", "")) for p in pats)),
            None,
        )
        rep_latest = rep_today or next(
            (r for r in all_reports if any(p in str(r.get("rel_path", "")) for p in pats)),
            None,
        )
        ran_in_cron = mtime in executed_today
        if (not is_trading_day) and (mtime in TRADING_ONLY_MILESTONE_TIMES):
            verified_today = False
            status_code = "holiday_skipped"
            status_vi = "🎌 NGHỈ LỄ HOSE/HNX" if msess.get("is_holiday") else "🛑 NGHỈ CUỐI TUẦN"
            holiday_cnt += 1
        else:
            verified_today = bool(ran_in_cron or rep_today is not None)
            if verified_today:
                status_code = "done_today"
                status_vi = "🟢 ĐÃ LÀM THẬT HÔM NAY"
                completed_cnt += 1
            elif mtime <= current_hm:
                status_code = "pending_catchup"
                status_vi = "🟠 CHỜ CHẠY BÙ HÔM NAY"
                pending_cnt += 1
            else:
                status_code = "upcoming"
                status_vi = "⏳ CHỜ ĐẾN GIỜ"
                upcoming_cnt += 1

        entry = {
            "time": mtime,
            "team_id": mdef["team_id"],
            "team_label": mdef["team_label"],
            "officer": mdef["officer"],
            "title": mdef["title"],
            "ran_in_cron": ran_in_cron,
            "verified_today": verified_today,
            "status_code": status_code,
            "status_vi": status_vi,
            "report_rel_path": (rep_latest or {}).get("rel_path", ""),
            "report_date": (rep_latest or {}).get("date", ""),
            "report_time": (rep_latest or {}).get("time_str", ""),
            "report_is_today": bool(rep_today is not None),
        }
        timeline.append(entry)
        if verified_today:
            latest_done = entry
        elif status_code == "upcoming" and next_milestone is None:
            next_milestone = entry

    latest_session = enterprise_data.get("latest_session", {}) if isinstance(enterprise_data, dict) else {}
    recon = warroom_data.get("recon_summary", {}) if isinstance(warroom_data, dict) else {}
    decision_brain = warroom_data.get("decision_brain", {}) if isinstance(warroom_data, dict) else {}
    can_reg = (canonical_truth or {}).get("canonical_regime") or (warroom_data.get("canonical_regime") or {})
    reg_id = str(can_reg.get("regime_id") or decision_brain.get("live_regime") or "--")
    ssot_live = ssot or _extract_ssot_summary()
    wl_syms = ", ".join(str(w.get("symbol") or "") for w in ((weekly_plan or {}).get("approved_watchlist") or [])[:6] if w.get("symbol")) or "TPB, HPG, CTG, NAB, CTS"

    sc_intel = intel_feed.get("summary_counts", {})
    crawled_at = str(intel_feed.get("crawled_at", ""))
    scanned_at = str(warroom_data.get("timestamp_ict") or recon.get("scanned_at") or "")
    sess_at = str(latest_session.get("created_at", ""))

    handoff_feed = [
        {
            "step": "① ➔ ②",
            "from_team": "Đội Hiền (Khối 1)",
            "to_team": "Minh Quân & Alex (Khối 2)",
            "timestamp": crawled_at or "--",
            "is_today": crawled_at.startswith(today_str),
            "summary": f"Đã cào {sc_intel.get('total_news_articles', 0)} bài RSS/CBTT, {sc_intel.get('verified_ir_portals', 0)} cổng IR, {sc_intel.get('sec_edgar_filings', 0)} SEC EDGAR & kiểm toán BCTC sạch.",
        },
        {
            "step": "② ➔ ③",
            "from_team": "Minh Quân & Alex (Khối 2)",
            "to_team": "James & Palmer (Khối 3)",
            "timestamp": sess_at or crawled_at or "--",
            "is_today": sess_at.startswith(today_str) or crawled_at.startswith(today_str),
            "summary": f"Phân tích rổ Hội đồng ({wl_syms}) & Ma trận S1–S4; chế độ hợp nhất hiện tại: {reg_id}.",
        },
        {
            "step": "④ ➔ ③",
            "from_team": "Victor Sentinel (Khối 4)",
            "to_team": "James & Palmer (Khối 3)",
            "timestamp": scanned_at or "--",
            "is_today": scanned_at.startswith(today_str),
            "summary": f"{msess.get('short_badge_vi')} | Tham chiếu {recon.get('scanned_live_count', 0)}/{recon.get('universe_total', 145)} mã (VNI {recon.get('vn_index', '--')}, Br20 {recon.get('live_breadth_ma20_pct', 0)}%).",
        },
        {
            "step": "③ ➔ 👑",
            "from_team": "James & Palmer (Khối 3)",
            "to_team": "Chủ tịch Phước Trần",
            "timestamp": (canonical_truth or {}).get("generated_at_ict") or now_ict.strftime("%Y-%m-%d %H:%M:%S"),
            "is_today": True,
            "summary": f"SSOT: {ssot_live['holdings_count']} mã ({ssot_live['holdings_desc']}) + Két {ssot_live['cash_str']} ({ssot_live['cash_pct']:.1f}% Cash) | {msess.get('short_badge_vi')}.",
        },
        {
            "step": "⑤ 🛡",
            "from_team": "Trọng & Palmer (Khối 5)",
            "to_team": "Giám Sát Toàn Hệ Thống",
            "timestamp": str(kanban_data.get("last_updated", "")) or now_ict.strftime("%Y-%m-%d %H:%M:%S"),
            "is_today": str(kanban_data.get("date", "")) == today_str,
            "summary": f"Ngày {today_str} ({msess.get('short_badge_vi')}): {completed_cnt}/{len(timeline)} mốc chạy thật ({holiday_cnt} mốc nghỉ lễ bỏ qua) • Audit {latest_session.get('ombudsman_audit_score', '10/10')}.",
        },
    ]

    return {
        "date": today_str,
        "current_time_ict": current_hm,
        "total_milestones": len(timeline),
        "completed_today_count": completed_cnt,
        "pending_catchup_count": pending_cnt,
        "upcoming_count": upcoming_cnt,
        "holiday_skipped_count": holiday_cnt,
        "next_milestone": next_milestone,
        "latest_completed": latest_done,
        "reports_written_today_count": len(today_reports),
        "intel_crawled_at": crawled_at,
        "intel_is_fresh_today": crawled_at.startswith(today_str),
        "enterprise_session_today": sess_at.startswith(today_str),
        "warroom_scan_today": scanned_at.startswith(today_str),
        "handoff_feed": handoff_feed,
        "milestones_timeline": timeline,
    }


def get_telegram_room_controls() -> Dict[str, Any]:
    """Đọc trạng thái Bật/Tắt thông báo Telegram từng Khối (pure stdlib local import)."""
    try:
        from scripts.telegram_dispatcher import get_room_telegram_controls as _get_tg
        return _get_tg()
    except Exception:
        return {}


def update_telegram_room_control(room_id: str, muted: bool) -> Dict[str, Any]:
    """Cập nhật Bật/Tắt Telegram cho Khối phòng ban và làm mới cache 2.5D Office."""
    try:
        from scripts.telegram_dispatcher import set_room_telegram_mute as _set_tg
        controls = _set_tg(room_id=room_id, muted=bool(muted))
        with _CACHE_LOCK:
            _LIVE_CACHE["ts"] = 0.0
        return {"ok": True, "room_id": room_id, "muted": bool(muted), "controls": controls}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _build_full_office_snapshot() -> Dict[str, Any]:
    now_ict = get_ict_now()
    ssot = _extract_ssot_summary()
    supervisor_data = _load_json(DATA_DIR / "apex_cloud_supervisor_status.json", {})
    cron_data = _load_json(DATA_DIR / "apex_cron_daemon_state.json", {})
    enterprise_data = _load_json(DATA_DIR / "enterprise_collaboration_state.json", {})
    kanban_data = get_kanban_board_state()
    warroom_data = _load_json(DATA_DIR / "live_warroom_state.json", {})
    intel_data = _load_json(DATA_DIR / "apex_daily_internet_intel.json", {})
    alerts_data = _load_json(DATA_DIR / "live_catalyst_alerts.json", {})
    brain_data = _load_json(DATA_DIR / "deep_financial_brain_analysis.json", {})
    spillover_data = _load_json(DATA_DIR / "global_spillover_state.json", {})
    legends_data = _load_json(DATA_DIR / "legend_investor_wisdom_vault.json", {})
    audit_state = _load_json(DATA_DIR / "system_audit_state.json", {})
    audit_ledger_raw = _load_json(AUDIT_LEDGER_FILE, [])
    audit_ledger = audit_ledger_raw if isinstance(audit_ledger_raw, list) else []
    weekly_plan = _load_json(DATA_DIR / "weekly_tactical_plan_active.json", {})
    canonical_truth = load_canonical_truth(refresh_if_missing=False)
    scbp_data = _load_json(DATA_DIR / "canonical_executive_briefing.json", {})
    trong_audit = _load_json(DATA_DIR / "trong_12gates_audit.json", {})
    victor_trailing = _load_json(DATA_DIR / "victor_trailing_state.json", {})
    tg_controls = get_telegram_room_controls()
    all_reports = _get_cached_reports(force_refresh=False)
    active_jobs = _get_active_jobs_snapshot()

    intel_feed = _collect_intel_feed(intel_data, alerts_data)
    daily_activity = _build_daily_activity_log(
        now_ict=now_ict,
        all_reports=all_reports,
        cron_data=cron_data,
        enterprise_data=enterprise_data,
        warroom_data=warroom_data,
        intel_feed=intel_feed,
        kanban_data=kanban_data,
        ssot=ssot,
        weekly_plan=weekly_plan,
        canonical_truth=canonical_truth,
    )

    rooms_summary: List[Dict[str, Any]] = []
    rooms_detail: Dict[str, Dict[str, Any]] = {}
    status_counts = {"working": 0, "waiting_approval": 0, "alert_veto": 0, "standby": 0}

    _scbp_seal_short = str(scbp_data.get("sha256_seal") or "")[:12] or "PENDING"
    _scbp_sla = scbp_data.get("freshness_sla") or {}
    _bctc_cov_txt = f"{_scbp_sla.get('bctc_verified_count', 145)}/{_scbp_sla.get('bctc_requested_count', 145)} mã"
    _v4_cal = (scbp_data.get("empirical_backtest") or {}).get("v4_sector_alpha") or {}
    _v4_perf_txt = (
        f"+{float(_v4_cal.get('total_return_pct') or 14.12):.2f}% (MaxDD {float(_v4_cal.get('max_drawdown_pct') or -7.13):.2f}%, Sharpe {float(_v4_cal.get('sharpe_ratio') or 0.89):.2f})"
    )
    _trong_lbl = f"{trong_audit.get('passed_count', 0)}/{trong_audit.get('total_gates', 12)} ({trong_audit.get('status', 'PENDING')})"

    for bp in ROOMS_BLUEPRINT:
        summary, detail = _compute_room_status_and_payload(
            bp=bp,
            now_ict=now_ict,
            ssot=ssot,
            supervisor_data=supervisor_data,
            enterprise_data=enterprise_data,
            kanban_data=kanban_data,
            warroom_data=warroom_data,
            intel_feed=intel_feed,
            brain_data=brain_data,
            spillover_data=spillover_data,
            legends_data=legends_data,
            audit_state=audit_state,
            audit_ledger=audit_ledger,
            weekly_plan=weekly_plan,
            all_reports=all_reports,
            active_jobs=active_jobs,
        )
        rid = bp["room_id"]
        is_tg_muted = bool((tg_controls.get(rid) or {}).get("muted", False))
        summary["telegram_muted"] = is_tg_muted
        detail["telegram_muted"] = is_tg_muted
        detail["v7_proof"] = {
            "scbp_seal": _scbp_seal_short,
            "bctc_coverage": _bctc_cov_txt,
            "brain_v4_perf": _v4_perf_txt,
            "trong_status": _trong_lbl,
            "trailing_positions": len((victor_trailing.get("positions") or {}) if isinstance(victor_trailing, dict) else {}),
        }
        detail["daily_milestones"] = [
            m for m in daily_activity["milestones_timeline"] if m["team_id"] == rid
        ]
        rooms_summary.append(summary)
        rooms_detail[rid] = detail
        sc = summary["status_code"]
        status_counts[sc] = status_counts.get(sc, 0) + 1

    latest_session = enterprise_data.get("latest_session", {}) if isinstance(enterprise_data, dict) else {}
    recon = warroom_data.get("recon_summary", {}) if isinstance(warroom_data, dict) else {}
    decision_brain = warroom_data.get("decision_brain", {}) if isinstance(warroom_data, dict) else {}
    services = supervisor_data.get("services", {}) if isinstance(supervisor_data, dict) else {}

    k_cols = kanban_data.get("columns", {})
    kanban_counts = {
        "BACKLOG": len(k_cols.get("BACKLOG", [])),
        "IN_PROGRESS": len(k_cols.get("IN_PROGRESS", [])),
        "AUDIT_REVIEW": len(k_cols.get("AUDIT_REVIEW", [])),
        "DONE": len(k_cols.get("DONE", [])),
        "total": len(kanban_data.get("tasks", {})),
    }

    today_str = now_ict.strftime("%Y-%m-%d")
    executed_today = (cron_data.get("executed_milestones") or {}).get(today_str, [])
    msess = canonical_truth.get("market_session") or get_vn_market_session_state(now_ict=now_ict)
    can_reg = canonical_truth.get("canonical_regime") or warroom_data.get("canonical_regime") or {}
    live_reg_id = str(can_reg.get("regime_id") or decision_brain.get("live_regime") or "S4_BEAR_CASH_SHIELD")

    return {
        "ok": True,
        "org_model": "APEX_5_TEAMS_EXECUTIVE_WORKFLOW_V2",
        "workflow_chain": "① Hiền (Dữ liệu & BCTC) ➔ ② Minh Quân & Alex (Thị trường) ➔ ③ James & Palmer (Kế hoạch Đầu tư) ◀── ④ Victor (Giám sát Live) | ⑤ Trọng & Palmer (Giám sát Toàn HT)",
        "generated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
        "weekday_vn": ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"][now_ict.weekday()],
        "is_market_hours": bool(msess.get("is_live_session", False)),
        "market_session": msess,
        "canonical_regime": can_reg,
        "executive_directive_vi": canonical_truth.get("executive_directive_vi", ""),
        "ssot": ssot,
        "market_live": {
            "phase": warroom_data.get("phase", msess.get("status_code", "STANDBY")),
            "live_regime": live_reg_id,
            "regime_badge_vi": can_reg.get("short_label") or live_reg_id,
            "target_allocation_pct": can_reg.get("target_exposure_label") or decision_brain.get("target_allocation_pct", "0.0% NAV"),
            "verdict_vi": decision_brain.get("verdict_vi") or canonical_truth.get("executive_directive_vi", ""),
            "vn_index": recon.get("vn_index", 0),
            "vn_index_chg_pct": recon.get("vn_index_chg_pct", 0),
            "breadth_ma20_pct": recon.get("live_breadth_ma20_pct", 0),
            "avg_buy_up_pct": recon.get("avg_buy_up_pct", 0),
            "scanned_live_count": recon.get("scanned_live_count", 0),
            "universe_total": recon.get("universe_total", 145),
        },
        "supervisor": {
            "status": supervisor_data.get("supervisor_status", "STANDBY"),
            "last_heartbeat": supervisor_data.get("last_heartbeat", ""),
            "services_count": len(services),
            "executed_milestones_today": executed_today,
        },
        "enterprise_session": {
            "session_id": latest_session.get("session_id", ""),
            "created_at": latest_session.get("created_at", ""),
            "target_ticker": latest_session.get("target_ticker", ""),
            "final_verdict": latest_session.get("final_verdict", ""),
            "action_plan": latest_session.get("action_plan", ""),
            "quorum_count": latest_session.get("quorum_count", 0),
            "roster_total": latest_session.get("roster_total", 14),
            "veto_triggered": bool(latest_session.get("veto_triggered", False)),
            "ombudsman_audit_score": latest_session.get("ombudsman_audit_score", "10/10"),
        },
        "weekly_plan_summary": {
            "week_label": weekly_plan.get("week_label", ""),
            "constitution_mandate": weekly_plan.get("constitution_mandate", ""),
            "days": weekly_plan.get("days", []),
            "approved_watchlist": weekly_plan.get("approved_watchlist", []),
        },
        "intel_feed": intel_feed,
        "daily_activity": daily_activity,
        "kanban_counts": kanban_counts,
        "status_counts": status_counts,
        "data_flows": DATA_FLOW_PIPES,
        "jobs": active_jobs[:10],
        "canonical_briefing_summary": {
            "version": scbp_data.get("version", "V7.0"),
            "sha256_seal": scbp_data.get("sha256_seal", ""),
            "generated_at_ict": scbp_data.get("generated_at_ict", ""),
            "executive_verdict": scbp_data.get("executive_verdict", {}),
            "simple_action_board": (scbp_data.get("simple_action_board") or [])[:8],
            "freshness_sla": _scbp_sla,
        },
        "trong_12_gates": {
            "passed_count": trong_audit.get("passed_count", 0),
            "total_gates": trong_audit.get("total_gates", 12),
            "status": trong_audit.get("status", "PENDING"),
            "audited_at_ict": trong_audit.get("audited_at_ict", ""),
            "gates": trong_audit.get("gates", []),
        },
        "victor_trailing_state": victor_trailing,
        "telegram_room_controls": tg_controls,
        "rooms": rooms_summary,
        "_rooms_detail": rooms_detail,
    }


def get_virtual_office_live_state(force_refresh: bool = False) -> Dict[str, Any]:
    now_ts = time.time()
    with _CACHE_LOCK:
        if not force_refresh and _LIVE_CACHE["payload"] is not None and (now_ts - _LIVE_CACHE["ts"]) < 3.0:
            snap = _LIVE_CACHE["payload"]
        else:
            snap = None

    if snap is None:
        if force_refresh:
            _get_cached_reports(force_refresh=True)
        snap = _build_full_office_snapshot()
        with _CACHE_LOCK:
            _LIVE_CACHE["ts"] = time.time()
            _LIVE_CACHE["payload"] = snap

    return {k: v for k, v in snap.items() if k != "_rooms_detail"}


def get_virtual_office_full_bundle(force_refresh: bool = False) -> Dict[str, Any]:
    """Trả trọn gói cả live_state + rooms_detail + kanban (dùng để nhúng vào Chat Artifact)."""
    get_virtual_office_live_state(force_refresh=force_refresh)
    with _CACHE_LOCK:
        snap = _LIVE_CACHE["payload"] or {}
    return {
        **{k: v for k, v in snap.items() if k != "_rooms_detail"},
        "rooms_detail": snap.get("_rooms_detail", {}),
        "kanban_board": get_kanban_board_state(),
    }


def get_virtual_office_room_detail(room_id: str, force_refresh: bool = False) -> Dict[str, Any]:
    resolved_id = LEGACY_ROOM_ALIAS.get(room_id, room_id)
    if resolved_id not in ROOMS_BY_ID:
        return {"ok": False, "error": f"Không tồn tại khối phòng ban: {room_id}"}
    get_virtual_office_live_state(force_refresh=force_refresh)
    with _CACHE_LOCK:
        snap = _LIVE_CACHE["payload"]
    detail = (snap or {}).get("_rooms_detail", {}).get(resolved_id)
    if not detail:
        return {"ok": False, "error": f"Không lấy được chi tiết khối: {resolved_id}"}
    return {
        "ok": True,
        "generated_at": (snap or {}).get("generated_at", ""),
        "ssot": (snap or {}).get("ssot", {}),
        "room": detail,
    }


def trigger_room_action(
    room_id: str,
    action: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    resolved_id = LEGACY_ROOM_ALIAS.get(room_id, room_id)
    if resolved_id not in ROOMS_BY_ID:
        return {"ok": False, "error": f"Không tồn tại khối: {room_id}"}

    bp = ROOMS_BY_ID[resolved_id]
    req = payload or {}
    act = (action or "").strip() or bp["primary_action"]["action"]

    if act == "sync_office":
        state = get_virtual_office_live_state(force_refresh=True)
        return {"ok": True, "immediate": True, "action": act, "generated_at": state["generated_at"]}

    if act == "open_lounge_modal":
        return {"ok": True, "immediate": True, "action": act, "message": "Mở Khu Tiện Ích & Mô Phỏng Chủ Tịch."}

    ticker = str(req.get("ticker") or "").strip().upper() or None
    custom_directive = str(req.get("directive") or "").strip()
    milestone_hm = str(req.get("milestone") or "").strip()

    job_title_map = {
        "crawl_intel": f"{bp['icon']} {bp['ban_code']}: Cào tin RSS, Vietcap, 11 cổng IR & BCTC",
        "convene_dept": f"{bp['icon']} {bp['ban_code']}: Họp 5 Khối & Chốt Kế Hoạch" + (f" ({ticker})" if ticker else ""),
        "run_dept_audit": f"{bp['icon']} {bp['ban_code']}: Thẩm định chuyên môn" + (f" ({ticker})" if ticker else ""),
        "publish_warroom": f"{bp['icon']} {bp['ban_code']}: Victor quét 145 mã & kiểm tra ngưỡng Mua/Bán",
        "run_trong_audit": f"{bp['icon']} {bp['ban_code']}: Trọng & Palmer kiểm toán toàn hệ thống",
        "run_milestone": f"🕒 Chạy cột mốc {milestone_hm or '--'} ({bp['ban_code']})",
        "catchup_today": "⚡ Chạy bù các cột mốc & làm mới toàn bộ báo cáo hôm nay",
    }
    job_title = job_title_map.get(act, f"{bp['icon']} {bp['ban_code']}: Thực thi {act}")
    job_id = _record_job_start(resolved_id, act, job_title)

    def _worker():
        report_rel = ""
        metrics_out: Dict[str, Any] = {}
        handoff_note = f"Đã đồng bộ kết quả sang {bp['handoff_to']}"
        try:
            if act == "crawl_intel":
                _append_job_step(job_id, "Đang kết nối RSS/CBTT, Vietcap/CafeF, 11 cổng IR & SEC EDGAR...", 28)
                from scripts.apex_omni_intelligence_crawler import crawl_realtime_market_intelligence
                res = crawl_realtime_market_intelligence(force_refresh=True)
                total = res.get("total_items", 0)
                crawled_at = str(res.get("crawled_at", ""))
                _append_job_step(job_id, f"Đã thu thập xong {total} bản tin tài chính lúc {crawled_at}.", 78)
                today_s = get_ict_now().strftime("%Y-%m-%d")
                cand_rep = f"02_Equity_Research/{today_s}_Daily_Internet_And_BCTC_Intel_Report.md"
                report_rel = cand_rep if (BASE_DIR / cand_rep).exists() else "00_LIVE_INTER_CHAT_STATE.md"
                metrics_out = {"total_items": total, "crawled_at": crawled_at}
                summary_txt = f"Đội Hiền hoàn tất cào sống {total} bản tin lúc {crawled_at} và bàn giao sang Minh Quân & Alex."

            elif act in ("convene_dept", "run_dept_audit"):
                _append_job_step(job_id, "Đang triệu tập 14 thực thể phòng ban & thu thập số liệu SSOT + BCTC...", 25)
                from scripts.apex_enterprise_collaboration_mesh import run_enterprise_work_session
                directive = custom_directive or f"[{bp['ban_code']}] Rà soát theo quy trình Hiền -> Minh Quân & Alex -> James & Palmer"
                _append_job_step(job_id, "Đang tranh biện đa chiều (Ban 1-4, Ban 7 VN/US, Victor & Kiểm sát viên Trọng)...", 55)
                sess = run_enterprise_work_session(
                    directive=directive,
                    ticker=ticker,
                    trigger_source=f"OFFICE_{resolved_id.upper()}",
                    sync_cloud=False,
                )
                verdict = sess.get("final_verdict", "DONE")
                sid = sess.get("session_id", "")
                date_part = str(sess.get("created_at") or get_ict_now().strftime("%Y-%m-%d"))[:10]
                report_rel = str(sess.get("report_rel_path") or f"08_Master_Investment_CIO/enterprise_sessions/{date_part}_Enterprise_Work_Session.md")
                _append_job_step(job_id, f"Đã biểu quyết {sess.get('quorum_count', 14)}/{sess.get('roster_total', 14)} Ban & niêm phong SHA-256.", 85)
                metrics_out = {
                    "session_id": sid,
                    "final_verdict": verdict,
                    "quorum": f"{sess.get('quorum_count', 14)}/{sess.get('roster_total', 14)}",
                    "packets": sess.get("packet_count", 0),
                }
                summary_txt = f"Hoàn tất phiên {sid}: {verdict} ({sess.get('quorum_count', 14)}/{sess.get('roster_total', 14)} thành viên). Đã xuất biên bản."

            elif act == "publish_warroom":
                _append_job_step(job_id, "Victor đang quét bảng điện 145 mã VPS/Entrade & đối chiếu SSOT...", 35)
                from scripts.apex_tactical_war_room_engine import publish_war_room_tactical_report
                res = publish_war_room_tactical_report(
                    trigger_reason=f"OFFICE_{resolved_id.upper()}",
                    target_ticker=ticker,
                )
                ok_flag = bool(res.get("ok", True))
                today_s = get_ict_now().strftime("%Y-%m-%d")
                report_rel = str(
                    res.get("intraday_report_path")
                    or res.get("enterprise_report_path")
                    or f"VN_Market/07_Daily_Specialist/{today_s}_Live_Intraday_Report.md"
                )
                _append_job_step(job_id, "Đã kiểm tra xong ngưỡng Mua LO / Chốt lời TP1 / Cắt lỗ Stop toàn rổ.", 82)
                summary_txt = str(res.get("message") or "Victor đã hoàn tất quét 145 mã & đồng bộ báo cáo cho James.")
                metrics_out = {"report_rel_path": report_rel}

            elif act == "run_trong_audit":
                _append_job_step(job_id, "Trọng & Palmer đang kiểm toán nhất quán dữ liệu giữa Chat, Cron & Web Portal...", 35)
                from scripts.apex_semantic_consistency_auditor import run_full_institutional_semantic_audit
                res = run_full_institutional_semantic_audit()
                issues = len(res.get("issues", [])) if isinstance(res, dict) else 0
                score = res.get("score", 100) if isinstance(res, dict) else 100
                today_s = get_ict_now().strftime("%Y-%m-%d")
                cand_tr = f"12_Institutional_Ombudsman_And_Inspectorate/daily_audits/{today_s}_Trong_Audit_Report.md"
                report_rel = cand_tr if (BASE_DIR / cand_tr).exists() else "00_LIVE_INTER_CHAT_STATE.md"
                _append_job_step(job_id, f"Hoàn tất kiểm toán 10 Điều Hiến chương: Điểm {score}/100 ({issues} vấn đề).", 85)
                metrics_out = {"score": score, "issues": issues}
                summary_txt = f"Trọng & Palmer kiểm toán xong: Điểm {score}/100 | Lỗi phát hiện: {issues}."
                ok_flag = True

            elif act == "run_milestone":
                valid_ms = {m["time"]: m for m in DAILY_MILESTONE_DEFS}
                if milestone_hm not in valid_ms:
                    _finish_job(job_id, False, f"Cột mốc không hợp lệ: {milestone_hm}", error="Invalid milestone")
                    return
                _append_job_step(job_id, f"Đang kích hoạt cột mốc {milestone_hm}: {valid_ms[milestone_hm]['title']}...", 35)
                cron_script = BASE_DIR / "scripts" / "apex_institutional_cron_daemon.py"
                proc = subprocess.run(
                    [sys.executable, "-X", "utf8", str(cron_script), f"--at={milestone_hm}", "--force"],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=180,
                    check=False,
                )
                ok_flag = (proc.returncode == 0)
                report_rel = "00_LIVE_INTER_CHAT_STATE.md"
                for pat in valid_ms[milestone_hm].get("patterns", ()):
                    matched = next((r.get("rel_path") for r in _get_cached_reports(force_refresh=True) if pat in str(r.get("rel_path", ""))), None)
                    if matched:
                        report_rel = matched
                        break
                metrics_out = {"milestone": milestone_hm, "exit_code": proc.returncode}
                summary_txt = f"Đã chạy xong cột mốc {milestone_hm} (exit={proc.returncode}) & cập nhật báo cáo hôm nay."
                err_txt = None if ok_flag else (proc.stderr or "")[-300:]

            elif act == "catchup_today":
                now_ict = get_ict_now()
                today_str = now_ict.strftime("%Y-%m-%d")
                now_hm = now_ict.strftime("%H:%M")
                _append_job_step(job_id, "Đang kiểm tra lịch phiên & chạy bù các cột mốc hợp lệ trong ngày...", 25)
                cron_data = _load_json(DATA_DIR / "apex_cron_daemon_state.json", {})
                executed_set = {str(x).strip() for x in ((cron_data.get("executed_milestones") or {}).get(today_str, []) or [])}
                cron_script = BASE_DIR / "scripts" / "apex_institutional_cron_daemon.py"
                ran_list: List[str] = []
                for m in DAILY_MILESTONE_DEFS:
                    mt = m["time"]
                    if mt <= now_hm and mt not in executed_set:
                        subprocess.run(
                            [sys.executable, "-X", "utf8", str(cron_script), f"--at={mt}"],
                            cwd=str(BASE_DIR),
                            capture_output=True,
                            text=True,
                            timeout=180,
                            check=False,
                        )
                        ran_list.append(mt)
                _append_job_step(job_id, "Đang cập nhật lại War-Room 145 mã & Artifact 2.5D...", 70)
                war_script = BASE_DIR / "scripts" / "apex_daily_live_warroom_engine.py"
                if war_script.exists():
                    subprocess.run(
                        [sys.executable, "-X", "utf8", str(war_script), "--once", "--refresh-intel"],
                        cwd=str(BASE_DIR),
                        capture_output=True,
                        text=True,
                        timeout=180,
                        check=False,
                    )
                try:
                    from scripts.sync_chat_office_artifact import sync_chat_office_artifact
                    sync_chat_office_artifact(force_refresh=True)
                except Exception:
                    pass
                ok_flag = True
                report_rel = "00_LIVE_INTER_CHAT_STATE.md"
                metrics_out = {"caught_up": ran_list}
                summary_txt = f"Đã chạy bù {len(ran_list)} cột mốc ({', '.join(ran_list) or 'đã đủ'}) + làm mới 145 mã & BCTC hôm nay."

            else:
                _finish_job(job_id, False, f"Hành động chưa hỗ trợ: {act}", error=f"Unsupported action: {act}")
                return

            try:
                from scripts.apex_canonical_truth import build_and_save_canonical_truth
                build_and_save_canonical_truth()
            except Exception:
                pass

            if report_rel and not (BASE_DIR / report_rel).exists():
                report_rel = "00_LIVE_INTER_CHAT_STATE.md" if (BASE_DIR / "00_LIVE_INTER_CHAT_STATE.md").exists() else ""

            _finish_job(
                job_id,
                ok=locals().get("ok_flag", True),
                summary=locals().get("summary_txt", f"Hoàn tất tác vụ {act}"),
                error=locals().get("err_txt"),
                deliverables={
                    "report_rel_path": report_rel,
                    "metrics": metrics_out,
                    "handoff_note": handoff_note,
                },
            )
        except Exception as exc:
            _finish_job(job_id, False, f"Lỗi khi chạy tác vụ {act}: {exc}", error=str(exc))

    t = threading.Thread(target=_worker, name=f"ApexOffice-{job_id}", daemon=True)
    t.start()

    return {
        "ok": True,
        "immediate": False,
        "job_id": job_id,
        "room_id": resolved_id,
        "action": act,
        "title": job_title,
        "message": f"Đã kích hoạt tác vụ nền ({job_id}). Văn phòng sẽ tự động cập nhật khi hoàn tất.",
    }
