#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INSTITUTIONAL REPORT SCANNER & METADATA EXTRACTOR
File: scripts/apex_report_scanner.py
Cơ quan chủ quản: Palmer — Apex Central System Governance
Phục vụ: Chủ tịch Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)

Chức năng:
1. Tự động quét toàn bộ kho báo cáo Markdown (.md) trên hệ thống đám mây.
2. Phân loại theo 12 phòng ban chuyên trách kèm Icon & Mã màu thể chế.
3. Trích xuất Tiêu đề, Ngày tạo, Tóm tắt preview, Kích thước tệp.
4. Cung cấp API cho Web Portal và Telegram Dispatcher cập nhật theo thời gian thực.
"""

import os
import re
import sys
import json
import time
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent

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


def extract_report_metadata(file_path: Path, dept_cfg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Trích xuất siêu dữ liệu thông minh từ file Markdown."""
    try:
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

        # 2. Trích xuất Ngày báo cáo từ tên tệp hoặc nội dung
        date_str = ""
        m_date = re.search(r"(\d{4}-\d{2}-\d{2})", file_path.name)
        if m_date:
            date_str = m_date.group(1)
        else:
            date_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

        # 3. Trích xuất thời gian tạo
        time_str = datetime.datetime.fromtimestamp(mtime).strftime("%H:%M:%S")

        # 4. Trích xuất Tóm tắt ngắn (Preview)
        preview_lines = []
        for line in content.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#") or line_str.startswith("```"):
                continue
            cleaned = re.sub(r"[\*\_`]", "", line_str)
            if len(cleaned) > 20:
                preview_lines.append(cleaned)
                if len(preview_lines) >= 3:
                    break
        preview = " ".join(preview_lines)[:250] + ("..." if preview_lines else "")

        rel_path = str(file_path.relative_to(BASE_DIR).as_posix())

        return {
            "file_name": file_path.name,
            "rel_path": rel_path,
            "title": title,
            "date": date_str,
            "time": time_str,
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
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Quét và gom toàn bộ báo cáo từ 12 phòng ban, sắp xếp thời gian mới nhất lên đầu."""
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

            reports.append(meta)

    # Sắp xếp thời gian mới nhất lên trên
    reports.sort(key=lambda r: (r["date"], r["mtime"]), reverse=True)
    return reports[:limit]


def get_daily_milestones_status() -> List[Dict[str, Any]]:
    """Tính toán tiến độ 18 Cột Mốc Tác Chiến trong ngày so khớp với giờ Việt Nam."""
    now_vn = datetime.datetime.now()
    now_hm = now_vn.strftime("%H:%M")
    today_date = now_vn.strftime("%Y-%m-%d")

    milestones_def = [
        ("06:00", "TASK-0600-AUTOCLEAN", "Ban 10: Rà Soát CBTT Đêm Qua & Dọn Dẹp Cache", "ban_10_hien", "🌸"),
        ("07:00", "TASK-0700-MACRO", "Ban 1: Cào Dữ Liệu Vĩ Mô SBV, Tỷ Giá & Phố Wall", "ban_1_macro", "🌐"),
        ("07:30", "TASK-0730-COACH", "Ban 6: Bản Tin Khai Sáng Buổi Sáng Cho NĐT", "ban_6_coach", "🎓"),
        ("08:00", "TASK-0800-ALPHA", "Ban 2: Thẩm Định Pháp Y BCTC & Dòng Tiền Thật", "ban_2_equity", "🔍"),
        ("08:30", "TASK-0830-MAGAZINE", "Ban 7: Alex & Minh Quân Lập Chiến Lược Ngày", "ban_7_specialist", "⚡"),
        ("08:45", "TASK-0845-BLOTTER", "Ban 8: Master CIO James Phê Duyệt Master Blotter", "ban_8_cio", "🎖️"),
        ("09:00", "TASK-0900-OPENING", "Ban 9: Victor Trực Chiến Bảng Điện Mở Phiên ATO", "ban_9_sentinel", "🚨"),
        ("11:45", "TASK-1145-FLASH", "Ban 3: Tổng Kết Phiên Sáng & Flash Note Trưa", "ban_3_synthesis", "⚖️"),
        ("13:00", "TASK-1300-T2RADAR", "Ban 4: Radar Hấp Thụ Hàng T+2.5 Đầu Giờ Chiều", "ban_4_risk", "🛡️"),
        ("14:00", "TASK-1400-GOLDENHOUR", "Ban 7: Tác Chiến KHUNG GIỜ VÀNG (14h00-14h25)", "ban_7_specialist", "⭐"),
        ("14:25", "TASK-1425-GUARD03", "Ban 4: Khóa Sổ Lệnh Mua, Kích Hoạt Phòng Thủ ATC", "ban_4_risk", "🛡️"),
        ("15:15", "TASK-1515-WALKFORWARD", "Ban 5: Hồi Tố Walk-Forward & Hit Rate % EOD", "ban_5_learning", "📊"),
        ("18:00", "TASK-1800-BCTCLIBRARY", "Ban 10: Tổng Rà Soát Thư Viện BCTC & Báo Cáo Soát Xét", "ban_10_hien", "📚"),
        ("21:00", "TASK-2100-HIENBCTC", "Ban 10: Mổ Xẻ Chuyên Sâu 1 Siêu Cổ Phiếu", "ban_10_hien", "🔬"),
        ("21:15", "TASK-2115-KHANHVIDEO", "Ban 11: Sáng Tạo Kịch Bản & Render Video AI 60s", "ban_11_khanh", "🎬"),
        ("22:00", "TASK-2200-EVOLUTION", "Ban 5: Tự Tiến Hóa & Tinh Chỉnh Trọng Số", "ban_5_learning", "🧠"),
        ("23:00", "TASK-2300-COUNCIL", "Ban 8: Đại Hội Đồng 10 Phòng Ban Phúc Tra EOD", "ban_8_cio", "🏛️"),
        ("23:30", "TASK-2330-TRONG-AUDIT", "Ban 12: Tổng Kiểm Sát Trọng Thanh Tra 10 Điều", "ban_12_ombudsman", "⚖️")
    ]

    status_list = []
    for time_milestone, tid, name, dept_code, icon in milestones_def:
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
            "status": status,
            "status_label": status_label,
            "color": color
        })

    return status_list


if __name__ == "__main__":
    print("[*] Kiểm thử Module Apex Report Scanner...")
    all_reports = scan_all_institutional_reports(limit=5)
    print(f"[+] Tìm thấy tổng cộng: {len(all_reports)} báo cáo gần nhất.")
    for r in all_reports:
        print(f"  {r['icon']} [{r['dept_short']}] {r['date']} {r['time']}: {r['title']} ({r['rel_path']})")
    
    print("\n[*] Kiểm thử 18 Cột Mốc Tác Chiến:")
    ms = get_daily_milestones_status()
    for m in ms[:5]:
        print(f"  {m['time']} {m['icon']} {m['name']} -> {m['status_label']}")
