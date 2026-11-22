#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX VIRTUAL OFFICE 2.5D LIVE ENGINE (BACKEND REAL-TIME DATA & ACTION HUB)
File: scripts/apex_virtual_office_engine.py
Cơ quan chủ quản: Palmer — Apex Central System Governance
Phục vụ: Chủ tịch Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)

Nguyên tắc kiến trúc:
1. Thuần Python chuẩn (KHÔNG import pandas / numpy / yfinance) để bảo vệ RAM < 220 MB trên Render Free 512 MB.
2. Đọc 100% dữ liệu sống thực tế (SSOT 105C307855, Enterprise Mesh 14 thực thể, Kanban, Daemon Supervisor,
   Living War-Room 145 mã, Omni Internet Crawler, Deep Brain BCTC, Global Spillover, 15 Huyền thoại, Kiểm toán Trọng).
3. Cung cấp API cho Bản đồ Văn phòng 2.5D Sáng Hiện Đại: trạng thái từng phòng, luồng gói tin nối phòng,
   Side Drawer chi tiết chuyên môn + báo cáo thật của riêng Ban, và bộ điều phối tác vụ nền không nghẽn HTTP.
"""

from __future__ import annotations

import datetime
import json
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
AUDIT_LEDGER_FILE = BASE_DIR / "12_Institutional_Ombudsman_And_Inspectorate" / "system_audit_ledger.json"

_CACHE_LOCK = threading.Lock()
_LIVE_CACHE: Dict[str, Any] = {"ts": 0.0, "payload": None}
_REPORTS_CACHE: Dict[str, Any] = {"ts": 0.0, "items": []}

_JOBS_LOCK = threading.Lock()
_OFFICE_JOBS: List[Dict[str, Any]] = []
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


def _get_cached_reports(force_refresh: bool = False) -> List[Dict[str, Any]]:
    now_ts = time.time()
    with _CACHE_LOCK:
        if not force_refresh and _REPORTS_CACHE["items"] and (now_ts - _REPORTS_CACHE["ts"]) < 10.0:
            return list(_REPORTS_CACHE["items"])
    try:
        from scripts.apex_report_scanner import scan_all_institutional_reports
        items = scan_all_institutional_reports(limit=300)
        if not isinstance(items, list):
            items = []
    except Exception:
        items = []
    with _CACHE_LOCK:
        _REPORTS_CACHE["ts"] = now_ts
        _REPORTS_CACHE["items"] = items
    return list(items)


# Quy hoạch 12 Phòng Vật Lý trên Bản đồ 2.5D Isometric (Sắp xếp 3 dãy hành lang mạch lạc)
ROOMS_BLUEPRINT: List[Dict[str, Any]] = [
    {
        "room_id": "room_ban_10",
        "ban_code": "Ban 10",
        "name": "Phòng Băng Tin IR & BCTC",
        "short_name": "Băng tin IR (Hiền)",
        "wing": "Tình Báo & Dữ Liệu",
        "icon": "🌸",
        "accent": "#ec4899",
        "floor_tint": "#fdf2f8",
        "officers": ["Hiền (IR Scout)"],
        "avatars": [{"name": "Hiền", "color": "#ec4899", "role": "IR & Filings"}],
        "gx": 0.2,
        "gy": 0.1,
        "gw": 2.1,
        "gd": 1.65,
        "dept_ids": ["ban_10_hien", "ban_10_cbtt"],
        "roster_ids": ["BAN_10_IR"],
        "kanban_depts": ["Ban 10"],
        "schedule": "18:00 & 21:00 hàng ngày (Cào RSS, Vietcap, 11 cổng IR, EDGAR)",
        "milestone_hours": [(18, 0), (21, 0)],
        "always_on_247": True,
        "veto_power": False,
        "furniture": "news_ticker",
        "primary_action": {"action": "crawl_intel", "label": "📡 Cào Tin & CBTT Sống Ngay"},
    },
    {
        "room_id": "room_ban_1",
        "ban_code": "Ban 1 VN/US",
        "name": "Phòng Vĩ Mô SBV & Toàn Cầu",
        "short_name": "Vĩ mô (Minh & Elena)",
        "wing": "Tình Báo & Dữ Liệu",
        "icon": "🌐",
        "accent": "#0ea5e9",
        "floor_tint": "#f0f9ff",
        "officers": ["Vũ Minh (VN)", "Dr. Elena Vance (US)"],
        "avatars": [
            {"name": "Vũ Minh", "color": "#0284c7", "role": "Vĩ mô SBV"},
            {"name": "Elena", "color": "#38bdf8", "role": "Global Macro"},
        ],
        "gx": 2.75,
        "gy": 0.1,
        "gw": 2.1,
        "gd": 1.65,
        "dept_ids": ["ban_1_macro", "ban_1_vn_macro"],
        "roster_ids": ["BAN_1_VN", "BAN_1_US"],
        "kanban_depts": ["Ban 1", "Ban 1 & 3"],
        "schedule": "07:00 hàng ngày & Phiên đêm Phố Wall (DXY, VIX, US10Y, SBV)",
        "milestone_hours": [(7, 0)],
        "always_on_247": False,
        "veto_power": False,
        "furniture": "macro_map",
        "primary_action": {"action": "convene_dept", "label": "🌐 Cập Nhật Luận Điểm Vĩ Mô"},
    },
    {
        "room_id": "room_ban_2",
        "ban_code": "Ban 2",
        "name": "Phòng Pháp Y BCTC & Định Giá",
        "short_name": "Pháp Y BCTC",
        "wing": "Tình Báo & Dữ Liệu",
        "icon": "🔍",
        "accent": "#10b981",
        "floor_tint": "#ecfdf5",
        "officers": ["Chuyên Gia Pháp Y BCTC"],
        "avatars": [{"name": "Pháp Y B2", "color": "#059669", "role": "OCF & MOS"}],
        "gx": 5.3,
        "gy": 0.1,
        "gw": 2.1,
        "gd": 1.65,
        "dept_ids": ["ban_2_equity", "ban_2_vn_equity"],
        "roster_ids": ["BAN_2_BCTC"],
        "kanban_depts": ["Ban 2", "Ban 2 & 3"],
        "schedule": "08:00 hàng ngày & Soi rổ Q3/2026 (OCF/LNST, Beneish M, MOS)",
        "milestone_hours": [(8, 0)],
        "always_on_247": False,
        "veto_power": True,
        "furniture": "forensic_desk",
        "primary_action": {"action": "convene_dept", "label": "🔬 Thẩm Định Pháp Y Rổ Q3/2026"},
    },
    {
        "room_id": "room_ban_3",
        "ban_code": "Ban 3",
        "name": "Phòng Tổng Hợp CANSLIM & VSA",
        "short_name": "Tổng Hợp (Ban 3)",
        "wing": "Chiến Lược & Hội Đồng",
        "icon": "🎯",
        "accent": "#8b5cf6",
        "floor_tint": "#f5f3ff",
        "officers": ["Trưởng Phòng Tổng Hợp"],
        "avatars": [{"name": "Sàng Lọc B3", "color": "#7c3aed", "role": "CANSLIM/VSA"}],
        "gx": 0.2,
        "gy": 2.2,
        "gw": 2.0,
        "gd": 1.65,
        "dept_ids": ["ban_3_synthesis", "ban_3_debates", "ban_3_vn_synthesis"],
        "roster_ids": ["BAN_3_SYNTHESIS"],
        "kanban_depts": ["Ban 3", "Ban 1 & 3", "Ban 2 & 3", "Ban 3 & Victor"],
        "schedule": "08:00, 11:45 & Tranh biện phản biện Bull vs Bear",
        "milestone_hours": [(8, 0), (11, 45)],
        "always_on_247": False,
        "veto_power": True,
        "furniture": "screener_desk",
        "primary_action": {"action": "convene_dept", "label": "⚔️ Phản Biện & Sàng Lọc Alpha"},
    },
    {
        "room_id": "room_ban_8",
        "ban_code": "Ban 8",
        "name": "Phòng Tổng Tư Lệnh Master CIO",
        "short_name": "Master CIO James",
        "wing": "Bộ Chỉ Huy Tối Cao",
        "icon": "🎖️",
        "accent": "#4f46e5",
        "floor_tint": "#eef2ff",
        "officers": ["Master CIO James"],
        "avatars": [{"name": "James CIO", "color": "#4338ca", "role": "Tổng Tư Lệnh"}],
        "gx": 2.65,
        "gy": 2.2,
        "gw": 2.3,
        "gd": 1.7,
        "dept_ids": ["ban_8_cio", "ban_8_council", "ban_8_enterprise"],
        "roster_ids": ["BAN_8_CIO"],
        "kanban_depts": ["Ban 8", "Ban 7 & 8"],
        "schedule": "08:45 Sổ Lệnh, 14:25 Duyệt Khớp, 23:00 Thượng Đỉnh & Trực 24/7",
        "milestone_hours": [(8, 45), (14, 25), (23, 0)],
        "always_on_247": True,
        "veto_power": True,
        "furniture": "cio_roundtable",
        "primary_action": {"action": "convene_dept", "label": "🏛️ Triệu Tập Họp 14 Ban Ngay"},
    },
    {
        "room_id": "room_ban_12",
        "ban_code": "Ban 12",
        "name": "Phòng Kiểm Sát Viên Trọng",
        "short_name": "Kiểm Sát Trọng",
        "wing": "Bộ Chỉ Huy Tối Cao",
        "icon": "⚖️",
        "accent": "#ef4444",
        "floor_tint": "#fef2f2",
        "officers": ["Kiểm Sát Viên Trọng"],
        "avatars": [{"name": "Trọng B12", "color": "#dc2626", "role": "Thanh Tra SHA-256"}],
        "gx": 5.35,
        "gy": 2.2,
        "gw": 2.05,
        "gd": 1.65,
        "dept_ids": ["ban_12_ombudsman"],
        "roster_ids": ["BAN_12_OMBUDSMAN"],
        "kanban_depts": ["Ban 12"],
        "schedule": "Giám sát 10 Điều Hiến Chương 24/7 & Thanh tra 23:30",
        "milestone_hours": [(23, 30)],
        "always_on_247": True,
        "veto_power": True,
        "furniture": "audit_vault",
        "primary_action": {"action": "run_trong_audit", "label": "🛡️ Chạy Kiểm Toán Tuân Thủ Ngay"},
    },
    {
        "room_id": "room_ban_4",
        "ban_code": "Ban 4",
        "name": "Phòng Quản Trị Rủi Ro Định Lượng",
        "short_name": "Rủi Ro ATR (Ban 4)",
        "wing": "Chiến Lược & Hội Đồng",
        "icon": "🛡️",
        "accent": "#f43f5e",
        "floor_tint": "#fff1f2",
        "officers": ["Hội Đồng Quản Trị Rủi Ro"],
        "avatars": [{"name": "Quant Rủi Ro", "color": "#e11d48", "role": "ATR & Trần 33%"}],
        "gx": 7.8,
        "gy": 2.2,
        "gw": 1.95,
        "gd": 1.65,
        "dept_ids": ["ban_4_risk", "ban_4_vn_risk"],
        "roster_ids": ["BAN_4_RISK"],
        "kanban_depts": ["Ban 4", "Ban 4 & Victor", "Ban 4 & 9"],
        "schedule": "13:00 T+2, 14:25 Guard-03 & Khóa Stop 2xATR <= 7.5%",
        "milestone_hours": [(13, 0), (14, 25)],
        "always_on_247": False,
        "veto_power": True,
        "furniture": "risk_shield",
        "primary_action": {"action": "convene_dept", "label": "⚖️ Kiểm Tra Trần Rủi Ro & Stop 2xATR"},
    },
    {
        "room_id": "room_ban_5_6",
        "ban_code": "Ban 5 & 6",
        "name": "Học Viện 15 Huyền Thoại & Tự Tiến Hóa",
        "short_name": "Học Viện & Tự Học",
        "wing": "Tri Thức & Tự Tiến Hóa",
        "icon": "🎓",
        "accent": "#2563eb",
        "floor_tint": "#eff6ff",
        "officers": ["Giám Đốc Học Viện (Ban 6)", "Chuyên Gia Tự Học (Ban 5)"],
        "avatars": [
            {"name": "Ban 5 AI", "color": "#d97706", "role": "Walk-Forward"},
            {"name": "Coach B6", "color": "#2563eb", "role": "15 Huyền Thoại"},
        ],
        "gx": 0.2,
        "gy": 4.3,
        "gw": 2.1,
        "gd": 1.65,
        "dept_ids": ["ban_5_learning", "ban_6_mentorship", "ban_6_vn_coach"],
        "roster_ids": ["BAN_5_EVOLUTION", "BAN_6_ACADEMY"],
        "kanban_depts": ["Ban 5", "Ban 5 VN", "Ban 6"],
        "schedule": "07:30 Khai Sáng, 15:15 Walk-Forward, 22:00 Tự Học Thích Nghi",
        "milestone_hours": [(7, 30), (15, 15), (22, 0)],
        "always_on_247": False,
        "veto_power": False,
        "furniture": "academy_library",
        "primary_action": {"action": "convene_dept", "label": "🧠 Hội Đồng 15 Huyền Thoại Chấm Điểm"},
    },
    {
        "room_id": "room_ban_7",
        "ban_code": "Ban 7 VN/US",
        "name": "Phòng Thực Thi Sổ Lệnh & Giờ Vàng",
        "short_name": "Minh Quân & Alex",
        "wing": "Sàn Giao Dịch & Thực Thi",
        "icon": "⚡",
        "accent": "#c026d3",
        "floor_tint": "#fdf4ff",
        "officers": ["Minh Quân (VN)", "Alex (US)"],
        "avatars": [
            {"name": "Minh Quân", "color": "#a21caf", "role": "Giờ Vàng 14h00"},
            {"name": "Alex", "color": "#db2777", "role": "US Markets"},
        ],
        "gx": 2.75,
        "gy": 4.3,
        "gw": 2.15,
        "gd": 1.65,
        "dept_ids": ["ban_7_specialist", "ban_7_vn_specialist"],
        "roster_ids": ["BAN_7_VN", "BAN_7_US"],
        "kanban_depts": ["Ban 7 VN", "Ban 7 & 8"],
        "schedule": "08:30 Pre-ATO, Khung Giờ Vàng 14:00–14:25 (Ma trận S1–S4)",
        "milestone_hours": [(8, 30), (14, 0), (14, 25)],
        "always_on_247": False,
        "veto_power": True,
        "furniture": "trading_desk",
        "primary_action": {"action": "publish_warroom", "label": "⚡ Xuất Bản Sổ Lệnh & Ma Trận S1–S4"},
    },
    {
        "room_id": "room_ban_9",
        "ban_code": "Ban 9",
        "name": "Phòng Trực Chiến Bảng Điện 145 Mã",
        "short_name": "Victor (145 Mã Live)",
        "wing": "Sàn Giao Dịch & Thực Thi",
        "icon": "🚨",
        "accent": "#d97706",
        "floor_tint": "#fffbeb",
        "officers": ["Victor Sentinel"],
        "avatars": [{"name": "Victor B9", "color": "#d97706", "role": "Radar 145 Mã"}],
        "gx": 5.3,
        "gy": 4.3,
        "gw": 2.15,
        "gd": 1.65,
        "dept_ids": ["ban_9_sentinel"],
        "roster_ids": ["BAN_9_SENTINEL"],
        "kanban_depts": ["Ban 9", "Ban 9 & System", "Ban 3 & Victor", "Ban 4 & Victor", "Ban 4 & 9"],
        "schedule": "Quét Live 145 mã (09:00–15:00) & Bảo vệ tường lửa 24/7",
        "milestone_hours": [(9, 0), (13, 0), (14, 25)],
        "always_on_247": True,
        "veto_power": True,
        "furniture": "radar_wall",
        "primary_action": {"action": "publish_warroom", "label": "📡 Quét Nhanh 145 Mã & Bảo Vệ Vốn"},
    },
    {
        "room_id": "room_ban_11",
        "ban_code": "Ban 11",
        "name": "Studio Truyền Thông & Video AI",
        "short_name": "Studio Khánh & Bảo",
        "wing": "Tri Thức & Tự Tiến Hóa",
        "icon": "🎬",
        "accent": "#ea580c",
        "floor_tint": "#fff7ed",
        "officers": ["Khánh (Content)", "Bảo (AI Render)"],
        "avatars": [
            {"name": "Khánh", "color": "#ea580c", "role": "Kịch bản 60s"},
            {"name": "Bảo", "color": "#fb923c", "role": "Render Video"},
        ],
        "gx": 7.8,
        "gy": 4.3,
        "gw": 1.95,
        "gd": 1.65,
        "dept_ids": ["ban_11_khanh"],
        "roster_ids": ["BAN_11_MEDIA"],
        "kanban_depts": ["Ban 11"],
        "schedule": "21:15 hàng ngày (Kịch bản & Render Video 9:16 từ BCTC Hiền)",
        "milestone_hours": [(21, 15)],
        "always_on_247": False,
        "veto_power": False,
        "furniture": "video_studio",
        "primary_action": {"action": "convene_dept", "label": "🎬 Lên Ý Tưởng Kịch Bản Từ BCTC"},
    },
    {
        "room_id": "room_lounge",
        "ban_code": "Khu Tiện Ích",
        "name": "Công Viên Apex, Bàn Bi-a & Mô Phỏng",
        "short_name": "Giải Trí & Mô Phỏng",
        "wing": "Tiện Ích Chủ Tịch",
        "icon": "🎱",
        "accent": "#16a34a",
        "floor_tint": "#f0fdf4",
        "officers": ["Trợ Lý Sảnh Apex"],
        "avatars": [{"name": "Palmer", "color": "#16a34a", "role": "Thư ký Chủ tịch"}],
        "gx": 7.8,
        "gy": 0.1,
        "gw": 1.95,
        "gd": 1.65,
        "dept_ids": [],
        "roster_ids": [],
        "kanban_depts": [],
        "schedule": "Mở cửa 24/7 — Bàn Bi-a thư giãn & Giả lập chia vốn 20.05M ₫",
        "milestone_hours": [],
        "always_on_247": True,
        "veto_power": False,
        "furniture": "billiard_lounge",
        "primary_action": {"action": "open_lounge_modal", "label": "🎱 Mở Bàn Bi-a & Mô Phỏng Vốn"},
    },
]

ROOMS_BY_ID: Dict[str, Dict[str, Any]] = {r["room_id"]: r for r in ROOMS_BLUEPRINT}


DATA_FLOW_PIPES: List[Dict[str, str]] = [
    {"id": "flow_10_2", "from": "room_ban_10", "to": "room_ban_2", "label": "Tin IR/BCTC", "tone": "emerald"},
    {"id": "flow_1_3", "from": "room_ban_1", "to": "room_ban_3", "label": "Xung Vĩ Mô", "tone": "sky"},
    {"id": "flow_2_3", "from": "room_ban_2", "to": "room_ban_3", "label": "Pháp Y OCF/MOS", "tone": "emerald"},
    {"id": "flow_3_8", "from": "room_ban_3", "to": "room_ban_8", "label": "Sàng Lọc Alpha", "tone": "violet"},
    {"id": "flow_4_8", "from": "room_ban_4", "to": "room_ban_8", "label": "Cỡ Lô ATR", "tone": "rose"},
    {"id": "flow_7_8", "from": "room_ban_7", "to": "room_ban_8", "label": "Sổ Lệnh S1–S4", "tone": "purple"},
    {"id": "flow_9_8", "from": "room_ban_9", "to": "room_ban_8", "label": "Nhịp 145 Mã", "tone": "amber"},
    {"id": "flow_8_12", "from": "room_ban_8", "to": "room_ban_12", "label": "Kiểm Toán SHA-256", "tone": "red"},
    {"id": "flow_10_11", "from": "room_ban_10", "to": "room_ban_11", "label": "Chất Liệu Video", "tone": "orange"},
    {"id": "flow_56_8", "from": "room_ban_5_6", "to": "room_ban_8", "label": "15 Huyền Thoại", "tone": "blue"},
]


def _get_active_jobs_snapshot() -> List[Dict[str, Any]]:
    with _JOBS_LOCK:
        return [dict(j) for j in _OFFICE_JOBS]


def _record_job_start(room_id: str, action: str, title: str) -> str:
    job_id = f"JOB-{get_ict_now().strftime('%H%M%S')}-{uuid.uuid4().hex[:5].upper()}"
    entry = {
        "job_id": job_id,
        "room_id": room_id,
        "action": action,
        "title": title,
        "status": "RUNNING",
        "started_at": get_ict_now().strftime("%Y-%m-%d %H:%M:%S"),
        "finished_at": None,
        "summary": "Đang thực thi trực tiếp trên hệ thống...",
        "error": None,
    }
    with _JOBS_LOCK:
        _OFFICE_JOBS.insert(0, entry)
        if len(_OFFICE_JOBS) > _MAX_JOBS:
            del _OFFICE_JOBS[_MAX_JOBS:]
    return job_id


def _finish_job(job_id: str, ok: bool, summary: str, error: Optional[str] = None) -> None:
    with _JOBS_LOCK:
        for j in _OFFICE_JOBS:
            if j["job_id"] == job_id:
                j["status"] = "DONE" if ok else "ERROR"
                j["finished_at"] = get_ict_now().strftime("%Y-%m-%d %H:%M:%S")
                j["summary"] = summary
                j["error"] = error
                break
    # Làm mới cache ngay để giao diện nhận diện kết quả mới nhất
    with _CACHE_LOCK:
        _LIVE_CACHE["ts"] = 0.0
        _REPORTS_CACHE["ts"] = 0.0


def get_jobs_list() -> List[Dict[str, Any]]:
    return _get_active_jobs_snapshot()


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
        "holdings_count": len(active_pos),
        "active_positions": active_pos,
        "cash_verified_note": str(st.get("cash_verified_note", "")),
        "next_round_watchlist": st.get("next_round_watchlist", []),
        "last_updated": str(st.get("last_updated", "")),
    }


def get_kanban_board_state() -> Dict[str, Any]:
    with _KANBAN_LOCK:
        data = _load_json(KANBAN_FILE, {})
        if not isinstance(data, dict) or "tasks" not in data or "columns" not in data:
            try:
                from scripts.apex_kanban_manager import init_daily_board
                data = init_daily_board(get_ict_now().strftime("%Y-%m-%d"))
            except Exception:
                data = {
                    "date": get_ict_now().strftime("%Y-%m-%d"),
                    "last_updated": get_ict_now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_tasks": 0,
                    "columns": {"BACKLOG": [], "IN_PROGRESS": [], "AUDIT_REVIEW": [], "DONE": []},
                    "tasks": {},
                }
        cols = data.get("columns", {})
        for col_name in ("BACKLOG", "IN_PROGRESS", "AUDIT_REVIEW", "DONE"):
            cols.setdefault(col_name, [])
        data["columns"] = cols
        return data


def create_kanban_task(
    title: str,
    dept: str,
    assignee: str = "Trưởng Ban",
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
            "dept": (dept or "Ban 8").strip(),
            "assignee": (assignee or "Trưởng Ban").strip(),
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


def _compute_room_status_and_payload(
    bp: Dict[str, Any],
    now_ict: datetime.datetime,
    ssot: Dict[str, Any],
    supervisor_data: Dict[str, Any],
    cron_data: Dict[str, Any],
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

    # Lọc báo cáo thật thuộc phòng này
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
    ][:8]

    # Bổ sung báo cáo thật cho Ban 9 (09_Realtime_Portfolio_Sentinel/*.md) nếu scanner chính chưa quét thư mục này
    if room_id == "room_ban_9" and len(room_reports) < 8:
        sentinel_dir = BASE_DIR / "09_Realtime_Portfolio_Sentinel"
        if sentinel_dir.exists():
            md_files = sorted(
                [p for p in sentinel_dir.glob("*.md") if p.name.lower() != "readme.md"],
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            seen_rel = {r["rel_path"] for r in room_reports}
            for md_p in md_files:
                rel = f"09_Realtime_Portfolio_Sentinel/{md_p.name}"
                if rel in seen_rel:
                    continue
                mtime_dt = datetime.datetime.fromtimestamp(md_p.stat().st_mtime)
                date_part = md_p.name[:10] if len(md_p.name) >= 10 and md_p.name[4] == "-" else mtime_dt.strftime("%Y-%m-%d")
                room_reports.append({
                    "rel_path": rel,
                    "title": md_p.stem.replace("_", " "),
                    "date": date_part,
                    "time_str": mtime_dt.strftime("%H:%M"),
                    "shift_label": "🚨 Trực Chiến Phiên",
                    "dept_name": "Ban 9: Victor Sentinel",
                    "icon": "🚨",
                })
                if len(room_reports) >= 8:
                    break

    # Lọc Kanban tasks của phòng này
    all_tasks = kanban_data.get("tasks", {}) if isinstance(kanban_data, dict) else {}
    k_depts = set(bp["kanban_depts"])
    room_tasks = [t for t in all_tasks.values() if isinstance(t, dict) and t.get("dept") in k_depts]
    in_progress_tasks = [t for t in room_tasks if t.get("status") == "IN_PROGRESS"]
    review_tasks = [t for t in room_tasks if t.get("status") == "AUDIT_REVIEW"]
    done_tasks = [t for t in room_tasks if t.get("status") == "DONE"]

    # Job đang chạy tại phòng này
    running_job = next((j for j in active_jobs if j.get("room_id") == room_id and j.get("status") == "RUNNING"), None)

    # Xác định trạng thái phòng dựa trên dữ liệu sống
    is_weekday = now_ict.weekday() < 5
    hm = now_ict.hour * 60 + now_ict.minute
    is_market_hours = is_weekday and (9 * 60 <= hm <= 15 * 60)
    is_golden_hour = is_weekday and (14 * 60 <= hm <= 14 * 60 + 25)
    near_milestone = any(abs((h * 60 + m) - hm) <= 20 for h, m in bp.get("milestone_hours", []))

    veto_triggered = bool(latest_session.get("veto_triggered", False))
    dissent_notes = [
        note for note in (latest_session.get("dissent_notes") or [])
        if (room_id == "room_ban_3" and "ĐIỀU 3" in note.upper())
        or (room_id == "room_ban_2" and "BAN 2" in note.upper())
        or (room_id == "room_ban_4" and "BAN 4" in note.upper())
    ]

    decision_brain = warroom_data.get("decision_brain", {}) if isinstance(warroom_data, dict) else {}
    proposed_orders = decision_brain.get("proposed_lo_orders", []) or []
    has_upcoming_week = any(d.get("status") == "UPCOMING" for d in (weekly_plan.get("days") or []) if isinstance(d, dict))
    latest_aud = audit_ledger[-1] if audit_ledger else {}

    status_code = "standby"
    status_label_vi = "Trực nhẹ"

    if running_job:
        status_code = "working"
        status_label_vi = "Đang chạy tác vụ"
    elif (veto_triggered and bp.get("veto_power") and room_id in ("room_ban_3", "room_ban_4", "room_ban_12", "room_ban_8")) or (
        room_id == "room_ban_12" and int(latest_aud.get("issues_count", 0) or 0) > 0
    ):
        status_code = "alert_veto"
        status_label_vi = "Cờ đỏ / VETO"
    elif review_tasks or (room_id in ("room_ban_7", "room_ban_8") and (len(proposed_orders) > 0 or is_golden_hour or (room_id == "room_ban_7" and has_upcoming_week))):
        status_code = "waiting_approval"
        status_label_vi = "Chờ duyệt S1–S4" if (has_upcoming_week and not is_market_hours) else "Chờ duyệt"
    elif in_progress_tasks or (is_market_hours and room_id in ("room_ban_9", "room_ban_7", "room_ban_4", "room_ban_8")):
        status_code = "working"
        status_label_vi = "Đang làm"
    elif near_milestone and is_weekday:
        status_code = "working"
        status_label_vi = "Đang chạy cột mốc"
    elif room_id == "room_ban_10" and (intel_feed.get("freshness") or {}).get("is_fresh_under_24h"):
        status_code = "working"
        status_label_vi = "Băng tin sống"
    elif room_id == "room_ban_9" and services.get("sentinel_monitor", {}).get("status") in ("RUNNING", "IN_PROCESS_COMPACT"):
        status_code = "working" if is_market_hours else "standby"
        status_label_vi = "Quét 145 mã" if is_market_hours else "Canh ngoài giờ"
    elif room_id == "room_ban_12" and services.get("inspector_trong", {}).get("status") in ("RUNNING", "IN_PROCESS_COMPACT"):
        status_code = "working" if near_milestone else "standby"
        status_label_vi = "Đang kiểm toán" if near_milestone else "Giám sát 24/7"
    elif room_id == "room_ban_8":
        status_code = "waiting_approval" if (ssot["holdings_count"] == 0 and is_golden_hour) else "standby"
        status_label_vi = "Chờ duyệt S1–S4" if status_code == "waiting_approval" else "Trực chỉ huy 24/7"
    elif room_id == "room_lounge":
        status_code = "standby"
        status_label_vi = "Mở 24/7"

    # Tạo KPI tóm tắt & Bong bóng suy nghĩ (live_thought) sát chuyên môn từng Ban
    recon = warroom_data.get("recon_summary", {}) if isinstance(warroom_data, dict) else {}
    kpi_summary = ""
    live_thought = ""
    specialized_data: Dict[str, Any] = {}

    if room_id == "room_ban_10":
        sc = intel_feed["summary_counts"]
        kpi_summary = f"{sc['total_news_articles']} tin • {sc['verified_ir_portals']} IR • {sc['sec_edgar_filings']} EDGAR"
        live_thought = f"Đã cào {sc['total_news_articles']} bài ({sc['tickers_with_live_news']} mã có tin)"
        specialized_data = {
            "crawled_at": intel_feed["crawled_at"],
            "summary_counts": sc,
            "freshness": intel_feed["freshness"],
            "latest_news": intel_feed["feed_items"][:12],
            "ir_portals": intel_feed["ir_portals"][:8],
            "sec_edgar_filings": intel_feed["sec_edgar_filings"],
        }
    elif room_id == "room_ban_1":
        rm = spillover_data.get("risk_multiplier", 1.0)
        vix_val = (spillover_data.get("metrics", {}).get("VIX") or {}).get("last_price", "--")
        sp_chg = (spillover_data.get("metrics", {}).get("SP500") or {}).get("change_1d_pct", "--")
        kpi_summary = f"Mult {rm}x • VIX {vix_val} • S&P {sp_chg}%"
        live_thought = f"Spillover {rm}x | Trần NAV {spillover_data.get('max_allocation_pct', 30)}%"
        specialized_data = {
            "spillover": spillover_data,
            "vn_index": recon.get("vn_index"),
            "vn_index_chg_pct": recon.get("vn_index_chg_pct"),
            "foreign_net_ty": recon.get("foreign_net_ty"),
        }
    elif room_id == "room_ban_2":
        top_vn = brain_data.get("top_vn_alpha_picks", [])[:8]
        top_us = brain_data.get("top_us_alpha_picks", [])[:5]
        kpi_summary = f"{len(top_vn)} Alpha VN • {len(top_us)} Alpha US (Q3/2026)"
        top_sym = top_vn[0].get("symbol") if top_vn else "TPB"
        top_sc = top_vn[0].get("alpha_score") if top_vn else "--"
        live_thought = f"Top BCTC: {top_sym} ({top_sc}đ) • Rổ Q3 sạch"
        specialized_data = {
            "generated_at": brain_data.get("generated_at", ""),
            "top_vn_alpha": [
                {
                    "symbol": p.get("symbol"),
                    "company_name": p.get("company_name"),
                    "live_price": p.get("live_price"),
                    "alpha_score": p.get("alpha_score"),
                    "piotroski_f_score": p.get("piotroski_f_score"),
                    "roe_pct": p.get("roe_pct"),
                    "pe": p.get("pe"),
                    "ocf_ratio": p.get("ocf_ratio"),
                    "margin_of_safety_pct": (p.get("valuation") or {}).get("margin_of_safety_pct"),
                }
                for p in top_vn
            ],
            "top_us_alpha": [
                {
                    "symbol": p.get("symbol"),
                    "company_name": p.get("company_name"),
                    "live_price": p.get("live_price"),
                    "alpha_score": p.get("alpha_score"),
                    "roe_pct": p.get("roe_pct"),
                    "pe": p.get("pe"),
                }
                for p in top_us
            ],
            "approved_watchlist": weekly_plan.get("approved_watchlist", []),
        }
    elif room_id == "room_ban_3":
        kpi_summary = f"Tranh biện {latest_session.get('dissent_count', 0)} ý kiến • Điều 3 MA20"
        live_thought = dissent_notes[0][:56] + "..." if dissent_notes else "Đang lọc CANSLIM & VSA"
        specialized_data = {
            "dissent_notes": latest_session.get("dissent_notes", []),
            "debate_points": (latest_session.get("debate_points") or [])[:8],
            "target_metrics": latest_session.get("target_metrics", {}),
        }
    elif room_id == "room_ban_4":
        kpi_summary = "Trần lô ≤ 33% NAV • Stop 2xATR ≤ 7.5% • R:R ≥ 1:2"
        live_thought = f"Khống chế rủi ro NAV {ssot['nav_str']}"
        specialized_data = {
            "risk_rules": [
                "Điều 5: Trần giá trị 1 lô 100 CP ≤ 33% NAV",
                "Rủi ro cắt lỗ tối đa 1 lệnh ≤ 1.5% NAV (~300,000 ₫)",
                "Stop Loss 2xATR(14) khóa cứng ≤ 7.5%",
                "Tỷ lệ Risk/Reward tối thiểu ≥ 1:2.0",
            ],
            "watchlist_risk": weekly_plan.get("approved_watchlist", []),
            "correlation_matrix": (brain_data.get("correlation_matrix") or {}).get("held_symbols", []),
        }
    elif room_id == "room_ban_5_6":
        wf = (legends_data.get("self_reflection") or {}).get("multi_horizon_walk_forward") or {}
        t5_hit = (wf.get("T+5") or {}).get("hit_rate_pct", "--")
        t10_hit = (wf.get("T+10") or {}).get("hit_rate_pct", "--")
        kpi_summary = f"15 Huyền thoại • Hit Rate T+5: {t5_hit}% | T+10: {t10_hit}%"
        live_thought = f"15 Danh thủ • Walk-Forward T+10: {t10_hit}%"
        specialized_data = {
            "total_legends": legends_data.get("total_legends", 15),
            "walk_forward": wf,
            "reflection_events": ((legends_data.get("self_reflection") or {}).get("events") or [])[:6],
            "school_summary": legends_data.get("school_summary", {}),
        }
    elif room_id == "room_ban_7":
        kpi_summary = f"5 mã Q3/2026 • Khung Giờ Vàng 14h00–14h25"
        live_thought = f"Tuần 48: S1–S4 | {decision_brain.get('live_regime', 'STANDBY')}"
        specialized_data = {
            "week_label": weekly_plan.get("week_label", ""),
            "constitution_mandate": weekly_plan.get("constitution_mandate", ""),
            "approved_watchlist": weekly_plan.get("approved_watchlist", []),
            "weekly_days": weekly_plan.get("days", []),
            "proposed_lo_orders": proposed_orders,
        }
    elif room_id == "room_ban_8":
        kpi_summary = f"Két {ssot['cash_str']} ({ssot['cash_pct']:.0f}% Cash) • {ssot['holdings_count']} CP"
        live_thought = f"Tuần 48: S1–S4 | Két {ssot['cash_str']}"
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
            "services": services,
        }
    elif room_id == "room_ban_9":
        vni = recon.get("vn_index", "--")
        br = recon.get("live_breadth_ma20_pct", "--")
        scanned = recon.get("scanned_live_count", 0)
        total_u = recon.get("universe_total", 145)
        kpi_summary = f"VNI {vni} • Br20 {br}% • {scanned}/{total_u} mã"
        live_thought = f"Quét {scanned}/{total_u} mã | {decision_brain.get('live_regime', 'STANDBY')}"
        specialized_data = {
            "recon_summary": recon,
            "decision_brain": decision_brain,
            "top_5_sectors": warroom_data.get("top_5_sectors", []),
        }
    elif room_id == "room_ban_11":
        kpi_summary = f"{len(room_reports)} kịch bản & gói tin • Render 9:16"
        live_thought = "Sẵn sàng đóng gói BCTC thành Video 60s"
        specialized_data = {
            "source_intel_at": intel_feed["crawled_at"],
            "featured_tickers": [w.get("symbol") for w in weekly_plan.get("approved_watchlist", [])],
        }
    elif room_id == "room_ban_12":
        latest_aud = audit_ledger[-1] if audit_ledger else {}
        seal = str(latest_session.get("constitutional_seal_sha256", ""))[:16]
        score = latest_session.get("ombudsman_audit_score", "10/10")
        kpi_summary = f"Audit {score} • SHA {seal or '--'}..."
        live_thought = f"Điểm kỷ luật {latest_aud.get('overall_discipline_score', 100)} • 10 Điều Luật"
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
        }
    else:
        kpi_summary = f"Vốn giả lập {ssot['nav_str']} • Bàn Bi-a 6 lỗ"
        live_thought = "Thư giãn & Thử phân bổ 20.05M ₫"
        specialized_data = {
            "cash_vnd": ssot["cash_vnd"],
            "watchlist": weekly_plan.get("approved_watchlist", []),
            "next_round_watchlist": ssot.get("next_round_watchlist", []),
        }

    room_summary = {
        "room_id": room_id,
        "ban_code": bp["ban_code"],
        "name": bp["name"],
        "short_name": bp["short_name"],
        "wing": bp["wing"],
        "icon": bp["icon"],
        "accent": bp["accent"],
        "floor_tint": bp["floor_tint"],
        "officers": bp["officers"],
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
        "tasks_total": len(room_tasks),
        "tasks_active": len(in_progress_tasks) + len(review_tasks),
        "tasks_done": len(done_tasks),
        "active_job": running_job,
        "primary_action": bp["primary_action"],
    }

    room_detail = {
        **room_summary,
        "roster_entities": room_roster,
        "latest_packets": room_packets,
        "latest_votes": room_votes,
        "kanban_tasks": room_tasks,
        "recent_reports": room_reports,
        "specialized_data": specialized_data,
    }
    return room_summary, room_detail


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
    all_reports = _get_cached_reports(force_refresh=False)
    active_jobs = _get_active_jobs_snapshot()

    intel_feed = _collect_intel_feed(intel_data, alerts_data)

    rooms_summary: List[Dict[str, Any]] = []
    rooms_detail: Dict[str, Dict[str, Any]] = {}
    status_counts = {"working": 0, "waiting_approval": 0, "alert_veto": 0, "standby": 0}

    for bp in ROOMS_BLUEPRINT:
        summary, detail = _compute_room_status_and_payload(
            bp=bp,
            now_ict=now_ict,
            ssot=ssot,
            supervisor_data=supervisor_data,
            cron_data=cron_data,
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
        rooms_summary.append(summary)
        rooms_detail[bp["room_id"]] = detail
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

    return {
        "ok": True,
        "generated_at": now_ict.strftime("%Y-%m-%d %H:%M:%S"),
        "weekday_vn": ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"][now_ict.weekday()],
        "is_market_hours": (now_ict.weekday() < 5) and (9 * 60 <= (now_ict.hour * 60 + now_ict.minute) <= 15 * 60),
        "ssot": ssot,
        "market_live": {
            "phase": warroom_data.get("phase", "WEEKEND_STANDBY"),
            "live_regime": decision_brain.get("live_regime", "S4_BEAR_CASH_SHIELD"),
            "target_allocation_pct": decision_brain.get("target_allocation_pct", "0.0% NAV (100% CASH)"),
            "verdict_vi": decision_brain.get("verdict_vi", ""),
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
        "kanban_counts": kanban_counts,
        "status_counts": status_counts,
        "data_flows": DATA_FLOW_PIPES,
        "jobs": active_jobs[:10],
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

    # Bản trả ra gọn nhẹ không kèm toàn bộ _rooms_detail nặng
    light = {k: v for k, v in snap.items() if k != "_rooms_detail"}
    return light


def get_virtual_office_room_detail(room_id: str, force_refresh: bool = False) -> Dict[str, Any]:
    if room_id not in ROOMS_BY_ID:
        return {"ok": False, "error": f"Không tồn tại phòng ban: {room_id}"}
    # Đảm bảo cache được nạp
    get_virtual_office_live_state(force_refresh=force_refresh)
    with _CACHE_LOCK:
        snap = _LIVE_CACHE["payload"]
    detail = (snap or {}).get("_rooms_detail", {}).get(room_id)
    if not detail:
        return {"ok": False, "error": f"Không lấy được chi tiết phòng: {room_id}"}
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
    if room_id not in ROOMS_BY_ID:
        return {"ok": False, "error": f"Không tồn tại phòng: {room_id}"}

    bp = ROOMS_BY_ID[room_id]
    req = payload or {}
    act = (action or "").strip() or bp["primary_action"]["action"]

    if act == "sync_office":
        state = get_virtual_office_live_state(force_refresh=True)
        return {"ok": True, "immediate": True, "action": act, "generated_at": state["generated_at"]}

    if act == "open_lounge_modal":
        return {"ok": True, "immediate": True, "action": act, "message": "Mở Khu Tiện Ích & Mô Phỏng Chủ Tịch."}

    ticker = str(req.get("ticker") or "").strip().upper() or None
    custom_directive = str(req.get("directive") or "").strip()

    job_title_map = {
        "crawl_intel": f"{bp['icon']} {bp['ban_code']}: Cào tin RSS, Vietcap, 11 cổng IR & EDGAR",
        "convene_dept": f"{bp['icon']} {bp['ban_code']}: Họp 14 Ban & Phân tích chuyên sâu" + (f" ({ticker})" if ticker else ""),
        "run_dept_audit": f"{bp['icon']} {bp['ban_code']}: Thẩm định chuyên môn" + (f" ({ticker})" if ticker else ""),
        "publish_warroom": f"{bp['icon']} {bp['ban_code']}: Quét 145 mã & Xuất bản Sổ Lệnh War-Room",
        "run_trong_audit": f"{bp['icon']} {bp['ban_code']}: Kiểm toán Hiến chương & SSOT",
    }
    job_title = job_title_map.get(act, f"{bp['icon']} {bp['ban_code']}: Thực thi {act}")
    job_id = _record_job_start(room_id, act, job_title)

    def _worker():
        try:
            if act == "crawl_intel":
                from scripts.apex_omni_intelligence_crawler import crawl_realtime_market_intelligence
                res = crawl_realtime_market_intelligence(force_refresh=True)
                total = res.get("total_items", 0)
                _finish_job(job_id, True, f"Hoàn tất cào sống: {total} bản tin / hồ sơ mới nhất lúc {res.get('crawled_at', '')}.")
            elif act in ("convene_dept", "run_dept_audit"):
                from scripts.apex_enterprise_collaboration_mesh import run_enterprise_work_session
                directive = custom_directive or f"[{bp['ban_code']}] Rà soát chiến lược Tuần 48 & danh mục rổ BCTC Q3/2026"
                sess = run_enterprise_work_session(
                    directive=directive,
                    ticker=ticker,
                    trigger_source=f"OFFICE_{room_id.upper()}",
                    sync_cloud=False,
                )
                verdict = sess.get("final_verdict", "DONE")
                sid = sess.get("session_id", "")
                _finish_job(job_id, True, f"Hoàn tất phiên {sid}: {verdict} ({sess.get('quorum_count', 14)}/{sess.get('roster_total', 14)} Ban tham dự).")
            elif act == "publish_warroom":
                from scripts.apex_tactical_war_room_engine import publish_war_room_tactical_report
                res = publish_war_room_tactical_report(
                    trigger_reason=f"OFFICE_{room_id.upper()}",
                    target_ticker=ticker,
                )
                ok_flag = bool(res.get("ok", True))
                msg = res.get("message") or res.get("rel_path") or "Đã cập nhật dữ liệu War-Room 145 mã."
                _finish_job(job_id, ok_flag, str(msg))
            elif act == "run_trong_audit":
                from scripts.apex_semantic_consistency_auditor import run_full_institutional_semantic_audit
                res = run_full_institutional_semantic_audit()
                issues = len(res.get("issues", [])) if isinstance(res, dict) else 0
                score = res.get("score", 100) if isinstance(res, dict) else 100
                _finish_job(job_id, True, f"Kiểm toán Trọng hoàn tất: Điểm {score}/100 | Lỗi phát hiện: {issues}.")
            else:
                _finish_job(job_id, False, f"Hành động chưa được hỗ trợ: {act}", error=f"Unsupported action: {act}")
        except Exception as exc:
            _finish_job(job_id, False, f"Lỗi khi chạy tác vụ {act}: {exc}", error=str(exc))

    t = threading.Thread(target=_worker, name=f"ApexOffice-{job_id}", daemon=True)
    t.start()

    return {
        "ok": True,
        "immediate": False,
        "job_id": job_id,
        "room_id": room_id,
        "action": act,
        "title": job_title,
        "message": f"Đã kích hoạt tác vụ nền ({job_id}). Văn phòng sẽ tự động cập nhật khi hoàn tất.",
    }
