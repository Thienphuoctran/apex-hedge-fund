#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INSTITUTIONAL REPORT SCANNER & METADATA EXTRACTOR (V2.0 TIMELINE & ARCHIVE VAULT)
File: scripts/apex_report_scanner.py
Cơ quan chủ quản: Palmer — Apex Central System Governance
Phục vụ: Chủ tịch Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)

Nâng cấp Thể chế V2.0:
1. Loại bỏ triệt để các tệp hướng dẫn README.md, agent.md, template.md khỏi danh sách báo cáo.
2. Trích xuất CHÍNH XÁC Giờ Gửi Báo Cáo (Timestamp) và phân loại theo 4 Ca Tác Chiến trong ngày:
   - 🌅 Ca Sáng (06:00 - 11:30)
   - ☀️ Ca Trưa (11:30 - 13:30)
   - 🎯 Ca Chiều (13:30 - 17:00)
   - 🌙 Ca Tối & Đêm (18:00 - 23:30)
3. Cơ chế Phân Tách "Báo Cáo Hôm Nay (Today's Live Desk)" vs "Kho Lưu Trữ Lịch Sử (Historical Archive Vault)".
   - Sang ngày mới, báo cáo hôm trước tự động được chuyển vào Kho Lưu Trữ theo Ngày, không bao giờ bị đè hay rối trang web!
"""

import os
import re
import sys
import json
import time
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent

# Các tệp tĩnh cần loại trừ tuyệt đối
EXCLUDED_FILENAMES = {
    "readme.md", "agent.md", "prompt.md", "instructions.md",
    "template.md", "guidelines.md", "agents.md", "skill.md"
}

# Bản đồ 12 Phòng Ban & Thư mục báo cáo tương ứng
DEPARTMENTS_CONFIG = [
    {
        "dept_id": "ban_1_macro",
        "name": "Ban 1: Vĩ Mô & Địa Chính Trị Toàn Cầu",
        "short_name": "Vĩ Mô Toàn Cầu",
        "icon": "🌐",
        "color": "#38bdf8",
        "pattern": "01_Macro_Geopolitics/*.md"
    },
    {
        "dept_id": "ban_1_vn_macro",
        "name": "Ban 1 VN: Vĩ Mô, SBV & Tỷ Giá",
        "short_name": "Vĩ Mô SBV",
        "icon": "🇻🇳",
        "color": "#38bdf8",
        "pattern": "VN_Market/01_Macro_Monetary_Vietnam/*.md"
    },
    {
        "dept_id": "ban_2_equity",
        "name": "Ban 2: Thẩm Định Doanh Nghiệp Toàn Cầu",
        "short_name": "Doanh Nghiệp US",
        "icon": "📊",
        "color": "#34d399",
        "pattern": "02_Equity_Research/*.md"
    },
    {
        "dept_id": "ban_2_vn_equity",
        "name": "Ban 2 VN: BCTC & Pháp Y Kế Toán (OCF/FCF)",
        "short_name": "Pháp Y BCTC VN",
        "icon": "🔍",
        "color": "#34d399",
        "pattern": "VN_Market/02_BCTC_Equity_Research/*.md"
    },
    {
        "dept_id": "ban_3_synthesis",
        "name": "Ban 3: Tổng Hợp & Sàng Lọc Phố Wall",
        "short_name": "Sàng Lọc US",
        "icon": "⚖️",
        "color": "#a78bfa",
        "pattern": "03_Synthesis_Memos/*.md"
    },
    {
        "dept_id": "ban_3_debates",
        "name": "Ban 3: Biên Bản Tranh Biện Hội Đồng Đa Chiều",
        "short_name": "Tranh Biện 10 Ban",
        "icon": "⚔️",
        "color": "#c084fc",
        "pattern": "03_Synthesis_Memos/adversarial_debates/*.md"
    },
    {
        "dept_id": "ban_3_vn_synthesis",
        "name": "Ban 3 VN: Phân Hạng Cơ Hội & Bẫy BCTC",
        "short_name": "Phân Hạng VN",
        "icon": "🎯",
        "color": "#a78bfa",
        "pattern": "VN_Market/03_Synthesis_Memos/*.md"
    },
    {
        "dept_id": "ban_4_risk",
        "name": "Ban 4: Hội Đồng Đầu Tư & Rủi Ro Định Lượng",
        "short_name": "Quản Trị Rủi Ro",
        "icon": "🛡️",
        "color": "#f87171",
        "pattern": "04_Investment_Committee/*.md"
    },
    {
        "dept_id": "ban_4_vn_risk",
        "name": "Ban 4 VN: Quản Trị Rủi Ro T+2.5 & Khóa Lệnh ATC",
        "short_name": "Rủi Ro VN T+2.5",
        "icon": "🛡️",
        "color": "#f87171",
        "pattern": "VN_Market/04_Investment_Committee/*.md"
    },
    {
        "dept_id": "ban_5_learning",
        "name": "Ban 5: Thẩm Định Hiệu Suất, Walk-Forward & Tự Học",
        "short_name": "Tự Học & Tiến Hóa",
        "icon": "🧠",
        "color": "#fbbf24",
        "pattern": "05_Learning_And_Evolution/*.md"
    },
    {
        "dept_id": "ban_6_mentorship",
        "name": "Ban 6: Học Viện Đào Tạo Thực Chiến 07h30",
        "short_name": "Bản Tin Khai Sáng",
        "icon": "🎓",
        "color": "#60a5fa",
        "pattern": "06_Investor_Academy_And_Mentorship/daily_mentorship/*.md"
    },
    {
        "dept_id": "ban_6_vn_coach",
        "name": "Ban 6 VN: Huấn Luyện Thực Chiến NĐT Việt Nam",
        "short_name": "Kèm Cặp NĐT VN",
        "icon": "🎓",
        "color": "#60a5fa",
        "pattern": "VN_Market/06_Investor_Academy/daily_mentorship/*.md"
    },
    {
        "dept_id": "ban_7_specialist",
        "name": "Ban 7: Chuyên Viên Đầu Tư Alex (US Markets)",
        "short_name": "Chuyên Viên Alex",
        "icon": "⚡",
        "color": "#f472b6",
        "pattern": "07_Daily_Investment_Specialist/*.md"
    },
    {
        "dept_id": "ban_7_vn_specialist",
        "name": "Ban 7 VN: Chuyên Viên Trưởng Minh Quân (Khung Giờ Vàng)",
        "short_name": "Minh Quân Pre-ATO",
        "icon": "⚡",
        "color": "#f472b6",
        "pattern": "VN_Market/07_Daily_Specialist/*.md"
    },
    {
        "dept_id": "ban_8_cio",
        "name": "Ban 8: Master CIO James (Sổ Lệnh Master Blotter)",
        "short_name": "Tổng Tư Lệnh James",
        "icon": "🎖️",
        "color": "#e879f9",
        "pattern": "08_Master_Investment_CIO/*.md"
    },
    {
        "dept_id": "ban_12_ombudsman",
        "name": "Ban 12: Tổng Kiểm Sát Viên Trọng (Thanh Tra 23h30)",
        "short_name": "Kiểm Sát Viên Trọng",
        "icon": "⚖️",
        "color": "#ef4444",
        "pattern": "12_Institutional_Ombudsman_And_Inspectorate/daily_audits/*.md"
    }
]

# Ánh xạ Cột Mốc Thời Gian Tác Chiến
MILESTONE_TIME_MAP = [
    ("23:30", ["23:30", "23h30", "task-2330", "trong_audit"], "23:30 PM", "🌙 Ca Đêm (23h30)"),
    ("23:00", ["23:00", "23h00", "task-2300", "council", "eod_executive"], "23:00 PM", "🌙 Ca Đêm (23h00)"),
    ("22:00", ["22:00", "22h00", "task-2200", "evolution", "vn_learning_report"], "22:00 PM", "🌙 Ca Đêm (22h00)"),
    ("21:15", ["21:15", "21h15", "task-2115", "khanhvideo", "viral_script"], "21:15 PM", "🌙 Ca Tối (21h15)"),
    ("21:00", ["21:00", "21h00", "task-2100", "hienbctc", "hien_daily_review", "chọn lọc bctc"], "21:00 PM", "🌙 Ca Tối (21h00)"),
    ("18:00", ["18:00", "18h00", "task-1800", "bctclibrary", "vn_cbtt_radar", "rà soát bctc"], "18:00 PM", "🌙 Ca Tối (18h00)"),
    ("15:15", ["15:15", "15h15", "task-1515", "walkforward", "post_mortem", "learning_report"], "15:15 PM", "🎯 Ca Chiều (15h15)"),
    ("14:25", ["14:25", "14h25", "task-1425", "guard03", "pre_atc", "vn_ic_decision", "ic decision", "nghị quyết hội đồng"], "14:25 PM", "🎯 Ca Chiều (14h25)"),
    ("14:00", ["14:00", "14h00", "task-1400", "goldenhour", "khung_gio_vang"], "14:00 PM", "🎯 Ca Chiều (14h00)"),
    ("13:00", ["13:00", "13h00", "task-1300", "t2radar", "t2_pressure"], "13:00 PM", "☀️ Ca Trưa (13h00)"),
    ("11:45", ["11:45", "11h45", "task-1145", "flash", "vn_investment_memo", "investment memo", "sàng lọc cơ hội"], "11:45 AM", "☀️ Ca Trưa (11h45)"),
    ("09:00", ["09:00", "09h00", "task-0900", "opening", "ato"], "09:00 AM", "🌅 Ca Sáng (09h00)"),
    ("08:45", ["08:45", "08h45", "task-0845", "blotter", "master_cio", "quant_risk"], "08:45 AM", "🌅 Ca Sáng (08h45)"),
    ("08:30", ["08:30", "08h30", "task-0830", "magazine", "specialist", "vn_specialist"], "08:30 AM", "🌅 Ca Sáng (08h30)"),
    ("08:00", ["08:00", "08h00", "task-0800", "alpha", "equity", "vn_equity_analysis"], "08:00 AM", "🌅 Ca Sáng (08h00)"),
    ("07:30", ["07:30", "07h30", "task-0730", "coach", "mentor", "mentor_briefing"], "07:30 AM", "🌅 Ca Sáng (07h30)"),
    ("07:00", ["07:00", "07h00", "task-0700", "macro", "vn_macro"], "07:00 AM", "🌅 Ca Sáng (07h00)"),
    ("06:00", ["06:00", "06h00", "task-0600", "autoclean", "cbtt", "cbtt_radar"], "06:00 AM", "🌅 Ca Sáng (06h00)"),
]


def extract_accurate_time(file_name: str, content: str, mtime: float) -> Tuple[str, str, str]:
    """
    Xác định chính xác giờ gửi báo cáo dựa trên cột mốc tác chiến hoặc văn bản bên trong.
    Trả về: (sortable_time, display_time, shift_label)
    """
    fn_lower = file_name.lower()
    content_head = content[:1000].lower()

    # 1. So khớp theo cột mốc tác chiến chuẩn hoá
    for hm, keywords, disp, shift in MILESTONE_TIME_MAP:
        if any(kw in fn_lower for kw in keywords):
            return hm + ":00", disp, shift
        if any(kw in content_head for kw in keywords):
            return hm + ":00", disp, shift

    # 2. Tìm regex giờ cụ thể trong 1000 ký tự đầu: e.g. "08:45:00" hoặc "08h45"
    m = re.search(r"(\d{1,2})[h:](\d{2})(?::(\d{2}))?\s*(am|pm|sáng|chiều|tối)?", content_head)
    if m:
        h = int(m.group(1))
        minute = int(m.group(2))
        ampm = (m.group(4) or "").lower()
        if ampm in ("pm", "chiều", "tối") and h < 12:
            h += 12
        elif ampm in ("am", "sáng") and h == 12:
            h = 0
        sort_t = f"{h:02d}:{minute:02d}:00"
        disp_t = f"{h:02d}:{minute:02d}"
        if h < 11 or (h == 11 and minute < 30):
            shift = f"🌅 Ca Sáng ({disp_t})"
        elif h < 13 or (h == 13 and minute < 30):
            shift = f"☀️ Ca Trưa ({disp_t})"
        elif h < 18:
            shift = f"🎯 Ca Chiều ({disp_t})"
        else:
            shift = f"🌙 Ca Tối ({disp_t})"
        return sort_t, disp_t, shift

    # 3. Fallback: Sử dụng mtime nếu có
    dt = datetime.datetime.fromtimestamp(mtime)
    sort_t = dt.strftime("%H:%M:%S")
    disp_t = dt.strftime("%H:%M")
    h = dt.hour
    if h < 12:
        shift = f"🌅 Ca Sáng ({disp_t})"
    elif h < 18:
        shift = f"🎯 Ca Chiều ({disp_t})"
    else:
        shift = f"🌙 Ca Tối ({disp_t})"
    return sort_t, disp_t, shift


def extract_report_metadata(file_path: Path, dept_cfg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Trích xuất siêu dữ liệu thông minh, loại trừ tệp tĩnh rác và chuẩn hóa ngày giờ."""
    try:
        fn_lower = file_path.name.lower()
        if fn_lower in EXCLUDED_FILENAMES or fn_lower.endswith("_template.md") or fn_lower.startswith("."):
            return None

        stat = file_path.stat()
        mtime = stat.st_mtime
        size_bytes = stat.st_size

        if size_bytes < 50:
            return None

        content = file_path.read_text(encoding="utf-8", errors="ignore")

        # 1. Trích xuất Tiêu đề chính
        title = file_path.stem.replace("_", " ")
        m_title = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if m_title:
            title = m_title.group(1).strip()

        # Loại bỏ nếu tiêu đề trùng với README mô tả thư mục
        if "thư mục này lưu trữ" in content[:300].lower() or title.lower().startswith("ban "):
            if len(content.splitlines()) < 15:
                return None

        # 2. Trích xuất Ngày báo cáo từ tên tệp hoặc nội dung
        m_date = re.search(r"(\d{4}-\d{2}-\d{2})", file_path.name)
        if m_date:
            date_str = m_date.group(1)
        else:
            m_date_content = re.search(r"(\d{4}-\d{2}-\d{2})", content[:500])
            if m_date_content:
                date_str = m_date_content.group(1)
            else:
                date_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

        # 3. Trích xuất Giờ báo cáo chính xác
        sort_time, display_time, shift_label = extract_accurate_time(file_path.name, content, mtime)

        # 4. Trích xuất Tóm tắt ngắn (Preview)
        preview_lines = []
        for line in content.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#") or line_str.startswith("```") or line_str.startswith("|"):
                continue
            cleaned = re.sub(r"[\*\_`]", "", line_str)
            if len(cleaned) > 20:
                preview_lines.append(cleaned)
                if len(preview_lines) >= 3:
                    break
        preview = " ".join(preview_lines)[:250] + ("..." if preview_lines else "")

        rel_path = str(file_path.relative_to(BASE_DIR).as_posix())

        now_date = datetime.datetime.now().strftime("%Y-%m-%d")
        is_today = (date_str == now_date)

        return {
            "file_name": file_path.name,
            "rel_path": rel_path,
            "title": title,
            "date": date_str,
            "time": display_time,
            "sort_time": sort_time,
            "shift_label": shift_label,
            "is_today": is_today,
            "mtime": mtime,
            "size_bytes": size_bytes,
            "size_kb": round(size_bytes / 1024, 1),
            "preview": preview,
            "dept_id": dept_cfg["dept_id"],
            "dept_name": dept_cfg["name"],
            "dept_short": dept_cfg["short_name"],
            "icon": dept_cfg["icon"],
            "color": dept_cfg["color"]
        }
    except Exception:
        return None


def scan_all_institutional_reports(
    date_filter: Optional[str] = None,
    dept_filter: Optional[str] = None,
    shift_filter: Optional[str] = None,
    limit: int = 200
) -> List[Dict[str, Any]]:
    """Quét và gom toàn bộ báo cáo từ 12 phòng ban, sắp xếp ngày và giờ tác chiến mới nhất lên đầu."""
    reports: List[Dict[str, Any]] = []

    for dept_cfg in DEPARTMENTS_CONFIG:
        if dept_filter and dept_filter != "all" and dept_cfg["dept_id"] != dept_filter:
            continue

        pattern = dept_cfg["pattern"]
        matched_files = list(BASE_DIR.glob(pattern))

        for file_path in matched_files:
            if not file_path.is_file() or file_path.name.startswith("."):
                continue

            meta = extract_report_metadata(file_path, dept_cfg)
            if not meta:
                continue

            if date_filter and date_filter != "all" and meta["date"] != date_filter:
                continue

            if shift_filter and shift_filter != "all" and shift_filter not in meta["shift_label"]:
                continue

            # CẦU CHÌ KHÓA THỜI GIAN THỰC (STRICT TIME-GATING & EMBARGO SHIELD):
            # Nếu báo cáo mang ngày hôm nay, CHỈ ĐƯỢC PHÉP CÔNG BỐ khi giờ thực tế >= giờ tác chiến của báo cáo.
            now_dt = datetime.datetime.now()
            today_str = now_dt.strftime("%Y-%m-%d")
            current_sort_time = now_dt.strftime("%H:%M:%S")

            if meta["date"] == today_str and meta["sort_time"] > current_sort_time:
                # CHƯA ĐẾN GIỜ TÁC CHIẾN THỰC TẾ! Embargoed - Khóa lại cho đến khi đến đúng giờ!
                continue

            reports.append(meta)

    # Sắp xếp theo Ngày giảm dần, sau đó theo Giờ tác chiến giảm dần
    reports.sort(key=lambda r: (r["date"], r["sort_time"]), reverse=True)
    return reports[:limit]


def get_available_archive_dates() -> List[Dict[str, Any]]:
    """Lấy danh sách tất cả các ngày có báo cáo trong kho dữ liệu kèm số lượng báo cáo chuẩn unembargoed."""
    all_reps = scan_all_institutional_reports(limit=1000)
    date_counts: Dict[str, int] = {}
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    for r in all_reps:
        d = r["date"]
        date_counts[d] = date_counts.get(d, 0) + 1

    sorted_dates = sorted(date_counts.keys(), reverse=True)
    result = []
    for d in sorted_dates:
        is_today = (d == today_str)
        try:
            dt = datetime.datetime.strptime(d, "%Y-%m-%d")
            label = dt.strftime("%d/%m/%Y")
        except Exception:
            label = d

        if is_today:
            display = f"🌟 Hôm Nay ({label}) — {date_counts[d]} Báo Cáo"
        else:
            display = f"🏛️ Ngày {label} — {date_counts[d]} Báo Cáo"

        result.append({
            "date": d,
            "display": display,
            "count": date_counts[d],
            "is_today": is_today
        })

    return result


def get_daily_milestones_status() -> List[Dict[str, Any]]:
    """Tính toán tiến độ 18 Cột Mốc Tác Chiến trong ngày so khớp với giờ Việt Nam."""
    now_vn = datetime.datetime.now()
    now_hm = now_vn.strftime("%H:%M")

    milestones_def = [
        ("06:00", "TASK-0600-AUTOCLEAN", "Ban 10: Rà Soát CBTT Đêm Qua & Dọn Dẹp Cache", "ban_10_hien", "🌸", "🌅 Ca Sáng"),
        ("07:00", "TASK-0700-MACRO", "Ban 1: Cào Dữ Liệu Vĩ Mô SBV, Tỷ Giá & Phố Wall", "ban_1_macro", "🌐", "🌅 Ca Sáng"),
        ("07:30", "TASK-0730-COACH", "Ban 6: Bản Tin Khai Sáng Buổi Sáng Cho NĐT", "ban_6_coach", "🎓", "🌅 Ca Sáng"),
        ("08:00", "TASK-0800-ALPHA", "Ban 2: Thẩm Định Pháp Y BCTC & Dòng Tiền Thật", "ban_2_equity", "🔍", "🌅 Ca Sáng"),
        ("08:30", "TASK-0830-MAGAZINE", "Ban 7: Alex & Minh Quân Lập Chiến Lược Ngày", "ban_7_specialist", "⚡", "🌅 Ca Sáng"),
        ("08:45", "TASK-0845-BLOTTER", "Ban 8: Master CIO James Phê Duyệt Master Blotter", "ban_8_cio", "🎖️", "🌅 Ca Sáng"),
        ("09:00", "TASK-0900-OPENING", "Ban 9: Victor Trực Chiến Bảng Điện Mở Phiên ATO", "ban_9_sentinel", "🚨", "🌅 Ca Sáng"),
        ("11:45", "TASK-1145-FLASH", "Ban 3: Tổng Kết Phiên Sáng & Flash Note Trưa", "ban_3_synthesis", "⚖️", "☀️ Ca Trưa"),
        ("13:00", "TASK-1300-T2RADAR", "Ban 4: Radar Hấp Thụ Hàng T+2.5 Đầu Giờ Chiều", "ban_4_risk", "🛡️", "☀️ Ca Trưa"),
        ("14:00", "TASK-1400-GOLDENHOUR", "Ban 7: Tác Chiến KHUNG GIỜ VÀNG (14h00-14h25)", "ban_7_specialist", "⭐", "🎯 Ca Chiều"),
        ("14:25", "TASK-1425-GUARD03", "Ban 4: Khóa Sổ Lệnh Mua, Kích Hoạt Phòng Thủ ATC", "ban_4_risk", "🛡️", "🎯 Ca Chiều"),
        ("15:15", "TASK-1515-WALKFORWARD", "Ban 5: Hồi Tố Walk-Forward & Hit Rate % EOD", "ban_5_learning", "📊", "🎯 Ca Chiều"),
        ("18:00", "TASK-1800-BCTCLIBRARY", "Ban 10: Tổng Rà Soát Thư Viện BCTC & Báo Cáo Soát Xét", "ban_10_hien", "📚", "🌙 Ca Tối"),
        ("21:00", "TASK-2100-HIENBCTC", "Ban 10: Mổ Xẻ Chuyên Sâu 1 Siêu Cổ Phiếu", "ban_10_hien", "🔬", "🌙 Ca Tối"),
        ("21:15", "TASK-2115-KHANHVIDEO", "Ban 11: Sáng Tạo Kịch Bản & Render Video AI 60s", "ban_11_khanh", "🎬", "🌙 Ca Tối"),
        ("22:00", "TASK-2200-EVOLUTION", "Ban 5: Tự Tiến Hóa & Tinh Chỉnh Trọng Số", "ban_5_learning", "🧠", "🌙 Ca Đêm"),
        ("23:00", "TASK-2300-COUNCIL", "Ban 8: Đại Hội Đồng 10 Phòng Ban Phúc Tra EOD", "ban_8_cio", "🏛️", "🌙 Ca Đêm"),
        ("23:30", "TASK-2330-TRONG-AUDIT", "Ban 12: Tổng Kiểm Sát Trọng Thanh Tra 10 Điều", "ban_12_ombudsman", "⚖️", "🌙 Ca Đêm")
    ]

    status_list = []
    for time_milestone, tid, name, dept_code, icon, shift in milestones_def:
        if now_hm > time_milestone:
            status = "COMPLETED"
            status_label = "ĐÃ HOÀN TẤT"
            color = "#10b981"
        elif abs(int(now_hm[:2])*60 + int(now_hm[3:]) - (int(time_milestone[:2])*60 + int(time_milestone[3:]))) <= 15:
            status = "ACTIVE"
            status_label = "ĐANG TRỰC CHIẾN"
            color = "#f59e0b"
        else:
            status = "PENDING"
            status_label = "CHỜ ĐẾN GIỜ"
            color = "#64748b"

        status_list.append({
            "time": time_milestone,
            "task_id": tid,
            "name": name,
            "dept_code": dept_code,
            "icon": icon,
            "shift": shift,
            "status": status,
            "status_label": status_label,
            "color": color
        })

    return status_list


if __name__ == "__main__":
    print("[*] Kiểm thử Module Apex Report Scanner V2.0...")
    dates = get_available_archive_dates()
    print(f"[+] Tìm thấy {len(dates)} ngày lưu trữ lịch sử:")
    for d in dates[:5]:
        print(f"  - {d['display']}")

    today_reps = scan_all_institutional_reports(date_filter="2026-11-07", limit=10)
    print(f"\n[+] Báo cáo Hôm Nay (2026-11-07): {len(today_reps)} báo cáo:")
    for r in today_reps:
        print(f"  {r['icon']} [{r['shift_label']}] {r['title']} ({r['size_kb']} KB)")
