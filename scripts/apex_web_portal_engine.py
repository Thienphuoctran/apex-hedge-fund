#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INSTITUTIONAL CLOUD PORTAL ENGINE (BLOOMBERG-GRADE WEB INTERFACE V4.0)
File: scripts/apex_web_portal_engine.py
Cơ quan chủ quản: Palmer — Apex Central System Governance
Phục vụ: Chủ tịch Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)
Tổng Tư Lệnh Điều Hành: Master CIO James

TỔNG NÂNG CẤP GIAO DIỆN TOÀN DIỆN V4.0:
1. Trải nghiệm thị giác công thái học chuẩn Bloomberg Terminal Dark-Mode:
   - Gam màu Obsidian & Slate Navy chống mỏi mắt.
   - Typography chuẩn Plus Jakarta Sans & JetBrains Mono.
2. Phân loại báo cáo đa chiều khoa học:
   - 2 Tầng lọc: Theo Khung Thời Gian (Hôm Nay / Kho Lưu Trữ / 4 Ca) và Theo 5 Khối Chuyên Môn Thể Chế.
   - Hiển thị số lượng báo cáo (N) trực tiếp trên từng nút phân loại.
   - Chuyển đổi 2 chế độ xem: Dạng Thẻ Grid (Trực quan) vs Dạng Bảng Nhanh (Compact Table).
3. Bàn Chỉ Huy Master CIO James 2 Cột (Split-Screen):
   - Cột trái: Luồng chat tương tác 2 chiều thông minh.
   - Cột phải: Live Sticky Sidebar ghim cố định tài khoản TCBS, đồng hồ đếm ngược phiên ATO Thứ Hai, và Radar 4 siêu cổ phiếu Vòng 2.
4. Bộ tiền xử lý thông minh cho tin nhắn James (Smart Visual Formatter):
   - Tự động bóc tách thành 4 Khối KPI Neon (Tiền mặt, Kho hàng, Lãi V1, Chế độ phiên).
   - Tự động render 4 Thẻ Cổ Phiếu Tầm Ngắm (Stock Cards) riêng biệt với vạch màu giá mua rõ nét.
   - Thu gọn Lịch sử Vòng 1 vào thanh Accordion tránh rối mắt.
   - Bật marked breaks: true giữ nguyên ngắt dòng, xóa bỏ triệt để tình trạng dồn chữ (Wall of Text).
5. Trình đọc báo cáo Reader Modal tối ưu đọc tập trung (880px max-width, hỗ trợ In/PDF).
"""

import sys
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def generate_portal_html(
    supervisor_data: Dict[str, Any],
    initial_reports: List[Dict[str, Any]],
    milestones: List[Dict[str, Any]],
    available_dates: Optional[List[Dict[str, Any]]] = None
) -> str:
    sup_status = supervisor_data.get("supervisor_status", "HEALTHY_ALL_RUNNING")
    services = supervisor_data.get("services", {})
    total_reports_count = len(initial_reports)

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_reports_count = sum(1 for r in initial_reports if r.get("date") == today_str)

    # Render bảng tiến trình daemons
    services_rows = ""
    for k, sinfo in services.items():
        st = sinfo.get("status", "UNKNOWN")
        badge_color = "#10b981" if st == "RUNNING" else ("#ef4444" if st == "STOPPED" else "#f59e0b")
        services_rows += f"""
        <tr>
            <td style="padding: 12px 16px; font-weight: 600; color: #f8fafc;">{sinfo.get('name', k)}</td>
            <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace; color: #38bdf8;">{sinfo.get('pid', '-')}</td>
            <td style="padding: 12px 16px;">
                <span style="background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}55; padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700;">
                    ● {st}
                </span>
            </td>
            <td style="padding: 12px 16px; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">{sinfo.get('restart_count', 0)}</td>
            <td style="padding: 12px 16px; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">{sinfo.get('uptime_seconds', 0):.0f}s</td>
        </tr>
        """

    # Render danh sách 18 cột mốc
    milestone_rows = ""
    for m in milestones:
        st_color = m.get("color", "#38bdf8")
        milestone_rows += f"""
        <tr>
            <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #38bdf8; font-size: 13px;">{m['time']}</td>
            <td style="padding: 12px 16px; font-size: 18px; text-align: center;">{m['icon']}</td>
            <td style="padding: 12px 16px; font-weight: 600; color: #f1f5f9;">{m['name']}</td>
            <td style="padding: 12px 16px; font-size: 12px; color: #94a3b8;">{m.get('shift', '')}</td>
            <td style="padding: 12px 16px;">
                <span style="background: {st_color}22; color: {st_color}; border: 1px solid {st_color}55; padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700;">
                    ● {m['status_label']}
                </span>
            </td>
        </tr>
        """

    if not available_dates:
        available_dates = [{"date": today_str, "display": f"🌟 Hôm Nay ({today_str})", "count": today_reports_count, "is_today": True}]

    # Dropdown options
    date_options_html = ""
    for d in available_dates:
        selected = "selected" if d["is_today"] else ""
        date_options_html += f'<option value="{d["date"]}" {selected}>{d["display"]}</option>'

    # Serialized JSON dữ liệu ban đầu cho JavaScript clientside
    initial_reports_json = json.dumps(initial_reports, ensure_ascii=False)
    available_dates_json = json.dumps(available_dates, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Institutional Cloud Portal — Định Chế Quỹ Đầu Tư 24/7</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <style>
        :root {{
            --bg-base: #070a12;
            --bg-surface: #0e1524;
            --bg-card: #141d30;
            --bg-card-hover: #1c2740;
            --border-color: #23304a;
            --border-glow: rgba(56, 189, 248, 0.35);
            --primary: #38bdf8;
            --primary-glow: rgba(56, 189, 248, 0.15);
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.15);
            --warning: #fbbf24;
            --danger: #ef4444;
            --purple: #c084fc;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            padding: 20px 24px;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.03) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(192, 132, 252, 0.03) 0%, transparent 40%);
            background-attachment: fixed;
        }}
        .container {{ max-width: 1420px; margin: 0 auto; }}
        
        /* HEADER */
        .portal-header {{
            background: linear-gradient(135deg, #0e1524 0%, #141d30 100%);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 22px 28px;
            margin-bottom: 22px;
            box-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.6);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 18px;
        }}
        .brand-title {{
            display: flex;
            align-items: center;
            gap: 14px;
            font-size: 22px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.02em;
        }}
        .brand-sub {{
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 6px;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
        }}
        .header-meta {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .live-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.35);
            padding: 7px 16px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.04em;
        }}
        .pulse-dot {{
            width: 8px; height: 8px; border-radius: 50%; background: #10b981;
            box-shadow: 0 0 10px #10b981;
            animation: pulse 1.8s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(0.95); opacity: 0.8; }}
            50% {{ transform: scale(1.3); opacity: 1; }}
            100% {{ transform: scale(0.95); opacity: 0.8; }}
        }}

        /* KPI STATS ROW */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
            margin-bottom: 22px;
        }}
        .kpi-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 20px 22px;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: var(--primary);
            box-shadow: 0 8px 24px rgba(56, 189, 248, 0.1);
        }}
        .kpi-card::before {{
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, var(--card-accent, #38bdf8), #818cf8);
        }}
        .kpi-lbl {{
            font-size: 11px;
            text-transform: uppercase;
            color: var(--text-dim);
            font-weight: 800;
            letter-spacing: 0.08em;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .kpi-val {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 24px;
            font-weight: 800;
            margin-top: 8px;
            letter-spacing: -0.02em;
        }}
        .kpi-sub {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 5px;
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        /* TABS NAVIGATION */
        .tab-nav {{
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 22px;
            overflow-x: auto;
            padding-bottom: 10px;
            scrollbar-width: thin;
        }}
        .tab-btn {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 11px 20px;
            font-size: 13.5px;
            font-weight: 700;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 9px;
            white-space: nowrap;
            transition: all 0.2s;
        }}
        .tab-btn:hover {{
            background: var(--bg-card);
            color: var(--text-main);
            border-color: #3b82f6;
        }}
        .tab-btn.active {{
            background: linear-gradient(135deg, #1e293b 0%, #1e1b4b 100%);
            color: #38bdf8;
            border-color: #38bdf8;
            box-shadow: 0 4px 16px rgba(56, 189, 248, 0.2);
        }}
        .tab-badge {{
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            padding: 2px 7px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
        }}

        .tab-pane {{ display: none; }}
        .tab-pane.active {{ display: block; }}

        /* ========================================================
           TAB 1: THƯ VIỆN BÁO CÁO (PHÂN LOẠI 2 TẦNG CHUYÊN NGHIỆP)
           ======================================================== */
        .library-controller {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px 24px;
            margin-bottom: 22px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        /* TẦNG 1: THỜI GIAN & CA TÁC CHIẾN */
        .filter-row-header {{
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            color: var(--text-dim);
            letter-spacing: 0.08em;
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 8px;
        }}
        .time-filter-section {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
            padding-bottom: 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .date-pills {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .date-pill-btn {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 12.5px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .date-pill-btn:hover {{ color: #fff; border-color: var(--primary); }}
        .date-pill-btn.active {{
            background: var(--primary);
            color: #070a12;
            border-color: var(--primary);
            box-shadow: 0 2px 10px rgba(56, 189, 248, 0.35);
        }}
        .archive-select {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 12.5px;
            outline: none;
            cursor: pointer;
        }}

        /* 4 CA TÁC CHIẾN */
        .shifts-group {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .shift-pill {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .shift-pill:hover {{ background: var(--bg-card); color: #fff; }}
        .shift-pill.active {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--primary);
            border-color: rgba(56, 189, 248, 0.4);
            font-weight: 700;
        }}

        /* TẦNG 2: 5 KHỐI PHÂN LOẠI THỂ CHẾ */
        .category-filter-section {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .cat-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 9999px;
            font-size: 12.5px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .cat-btn:hover {{
            background: var(--bg-card-hover);
            color: #fff;
            border-color: #3b82f6;
        }}
        .cat-btn.active {{
            background: linear-gradient(135deg, #1e293b 0%, #1e1b4b 100%);
            color: var(--primary);
            font-weight: 800;
            border-color: var(--primary);
            box-shadow: 0 2px 10px rgba(56, 189, 248, 0.2);
        }}
        .cat-count {{
            background: rgba(255, 255, 255, 0.08);
            padding: 1px 7px;
            border-radius: 9999px;
            font-size: 11px;
            font-family: 'JetBrains Mono', monospace;
        }}
        .cat-btn.active .cat-count {{
            background: rgba(56, 189, 248, 0.25);
            color: #38bdf8;
            font-weight: 700;
        }}

        /* TẦNG 3: TOOLBAR TÌM KIẾM & CHẾ ĐỘ XEM */
        .library-toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .search-box-wrap {{
            position: relative;
            flex-grow: 1;
            max-width: 480px;
        }}
        .search-box {{
            width: 100%;
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 10px 16px 10px 40px;
            border-radius: 10px;
            font-size: 13.5px;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-box:focus {{ border-color: var(--primary); }}
        .search-icon {{
            position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
            color: var(--text-dim); font-size: 15px;
        }}
        .view-mode-toggle {{
            display: flex;
            gap: 6px;
            background: var(--bg-base);
            padding: 4px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}
        .view-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .view-btn.active {{
            background: var(--bg-card);
            color: var(--primary);
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
        }}

        /* GRID VIEW: CARDS */
        .reports-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }}
        .report-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 22px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
            cursor: pointer;
            position: relative;
        }}
        .report-card:hover {{
            transform: translateY(-3px);
            border-color: var(--primary);
            box-shadow: 0 10px 28px rgba(56, 189, 248, 0.12);
        }}
        .card-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
            gap: 10px;
        }}
        .dept-tag {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 800;
            padding: 4px 11px;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .report-time-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            padding: 4px 10px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: #cbd5e1;
            white-space: nowrap;
        }}
        .report-title {{
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.45;
            margin-bottom: 12px;
        }}
        .report-snippet {{
            font-size: 13px;
            color: #94a3b8;
            line-height: 1.6;
            margin-bottom: 18px;
            background: rgba(255, 255, 255, 0.02);
            border-left: 3px solid #38bdf8;
            padding: 10px 14px;
            border-radius: 0 8px 8px 0;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .card-bottom {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 14px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .btn-read {{
            background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
            color: #ffffff;
            border: none;
            padding: 7px 16px;
            border-radius: 8px;
            font-size: 12.5px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
        }}
        .btn-read:hover {{
            background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%);
            box-shadow: 0 4px 14px rgba(56, 189, 248, 0.4);
            transform: translateY(-1px);
        }}

        /* TABLE VIEW: COMPACT LIST */
        .reports-table-wrap {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            overflow: hidden;
        }}
        .reports-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
        }}
        .reports-table th {{
            background: var(--bg-card);
            padding: 12px 16px;
            color: var(--text-dim);
            font-weight: 800;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        .reports-table td {{
            padding: 12px 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            color: #cbd5e1;
        }}
        .reports-table tr:hover td {{
            background: rgba(56, 189, 248, 0.04);
        }}

        /* ========================================================
           TAB 3: BÀN CHỈ HUY MASTER CIO JAMES (SPLIT-VIEW 2 CỘT)
           ======================================================== */
        .james-split-container {{
            display: grid;
            grid-template-columns: 1fr 360px;
            gap: 20px;
            align-items: start;
        }}
        @media (max-width: 1100px) {{
            .james-split-container {{ grid-template-columns: 1fr; }}
        }}
        .james-main-panel {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            min-height: 680px;
        }}
        .james-sidebar-panel {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .sidebar-widget {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 18px 20px;
            position: relative;
            overflow: hidden;
        }}
        .sidebar-widget::before {{
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, #c084fc, #38bdf8);
        }}
        .sidebar-widget-title {{
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            color: var(--text-dim);
            letter-spacing: 0.06em;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* JAMES COMMAND CHIPS */
        .cmd-chip {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 13px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .cmd-chip:hover {{
            background: var(--primary);
            color: #070a12;
            font-weight: 800;
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(56, 189, 248, 0.3);
        }}

        /* CHAT BUBBLES */
        .msg-user {{
            align-self: flex-end;
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
            color: #ffffff;
            padding: 14px 18px;
            border-radius: 14px 14px 2px 14px;
            max-width: 820px;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
        }}
        .msg-james {{
            align-self: flex-start;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: #e2e8f0;
            padding: 20px 22px;
            border-radius: 14px 14px 14px 2px;
            max-width: 900px;
            width: 100%;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3);
        }}
        .msg-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }}

        /* SMART VISUAL WIDGETS FOR JAMES MESSAGES */
        .exec-kpi-banner {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            margin: 14px 0 18px;
        }}
        .exec-kpi-box {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px 14px;
        }}
        .exec-kpi-box-lbl {{ font-size: 10.5px; text-transform: uppercase; color: var(--text-dim); font-weight: 800; }}
        .exec-kpi-box-val {{ font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 800; margin-top: 4px; }}

        .stock-target-card {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 12px;
            transition: border-color 0.15s;
        }}
        .stock-target-card:hover {{ border-color: #38bdf8; }}
        .stock-target-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .stock-target-badge {{
            font-size: 13px;
            font-weight: 800;
            color: #38bdf8;
            font-family: 'JetBrains Mono', monospace;
            background: rgba(56, 189, 248, 0.12);
            padding: 2px 8px;
            border-radius: 6px;
        }}
        .price-badge-buy {{
            background: rgba(56, 189, 248, 0.1);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }}
        .price-badge-breakout {{
            background: rgba(16, 185, 129, 0.1);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }}

        details.round1-accordion {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px 16px;
            margin: 14px 0;
            cursor: pointer;
        }}
        details.round1-accordion summary {{
            font-size: 12.5px;
            font-weight: 700;
            color: #34d399;
            outline: none;
        }}
        details.round1-accordion .round1-body {{
            margin-top: 12px;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            font-size: 13px;
            color: #94a3b8;
            line-height: 1.6;
        }}

        /* TRADINGVIEW STYLES */
        .tv-btn {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .tv-btn:hover {{ color: #fff; border-color: var(--primary); }}
        .tv-btn.active {{
            background: var(--primary);
            color: #070a12;
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(56, 189, 248, 0.35);
        }}

        /* MODAL ĐỌC BÁO CÁO */
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(3, 7, 18, 0.88);
            backdrop-filter: blur(8px);
            z-index: 9999;
            padding: 30px 20px;
            overflow-y: auto;
        }}
        .modal-container {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            max-width: 960px;
            margin: 0 auto;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.85);
            overflow: hidden;
        }}
        .modal-header {{
            background: var(--bg-card);
            border-bottom: 1px solid var(--border-color);
            padding: 22px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .modal-body {{
            padding: 36px 42px;
            line-height: 1.8;
            font-size: 15.5px;
            color: #e2e8f0;
            max-height: 80vh;
            overflow-y: auto;
        }}

        /* MARKDOWN STYLING */
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {{
            color: #ffffff;
            margin: 26px 0 14px;
            font-weight: 800;
            letter-spacing: -0.01em;
        }}
        .markdown-body h1 {{ font-size: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }}
        .markdown-body h2 {{ font-size: 19px; }}
        .markdown-body h3 {{ font-size: 16px; color: #38bdf8; }}
        .markdown-body p {{ margin-bottom: 16px; }}
        .markdown-body ul, .markdown-body ol {{ margin: 0 0 18px 24px; }}
        .markdown-body li {{ margin-bottom: 8px; }}
        .markdown-body table {{
            width: 100%;
            border-collapse: collapse;
            margin: 22px 0;
            font-size: 13.5px;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}
        .markdown-body th {{
            background: #172554;
            color: #38bdf8;
            padding: 12px 16px;
            text-align: left;
            font-weight: 800;
            border: 1px solid var(--border-color);
        }}
        .markdown-body td {{
            padding: 11px 16px;
            border: 1px solid var(--border-color);
        }}
        .markdown-body tr:nth-child(even) {{ background: rgba(255, 255, 255, 0.02); }}
        .markdown-body code {{
            font-family: 'JetBrains Mono', monospace;
            background: rgba(56, 189, 248, 0.1);
            color: #38bdf8;
            padding: 2px 7px;
            border-radius: 5px;
            font-size: 13px;
        }}

        /* TABLE BASE STYLES */
        table.standard-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
        }}
        table.standard-table th {{
            background: var(--bg-base);
            padding: 12px 16px;
            color: var(--text-dim);
            font-weight: 800;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.06em;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        table.standard-table td {{
            border-bottom: 1px solid var(--border-color);
        }}
        table.standard-table tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}

        @media print {{
            body * {{ visibility: hidden; }}
            #report-modal, #report-modal * {{ visibility: visible; }}
            #report-modal {{ position: absolute; left: 0; top: 0; width: 100%; background: #fff; color: #000; padding: 0; }}
            .modal-header {{ border-bottom: 2px solid #000; }}
            .modal-close, .modal-actions {{ display: none; }}
            .modal-container {{ box-shadow: none; border: none; width: 100%; max-width: 100%; margin: 0; }}
            .markdown-body {{ color: #000; }}
            .markdown-body th {{ background: #f1f5f9; color: #000; }}
            .markdown-body code {{ color: #000; background: #eee; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <header class="portal-header">
            <div>
                <div class="brand-title">
                    <span style="font-size: 26px;">🏛️</span>
                    <span>APEX INSTITUTIONAL CLOUD PORTAL</span>
                    <span style="background: rgba(192, 132, 252, 0.15); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3); font-size: 11px; padding: 3px 9px; border-radius: 9999px; font-weight: 800;">V4.0</span>
                </div>
                <div class="brand-sub">
                    <span>👤 Chủ tọa: <strong style="color: #fff;">Chủ tịch Trần Quốc Thiên Phước</strong></span>
                    <span>•</span>
                    <span>🏦 TCBS: <strong style="color: #38bdf8; font-family: 'JetBrains Mono', monospace;">105C307855</strong></span>
                    <span>•</span>
                    <span>🎖️ Tổng Tư Lệnh: <strong style="color: #c084fc;">Master CIO James</strong></span>
                </div>
            </div>
            <div class="header-meta">
                <div class="live-badge">
                    <span class="pulse-dot"></span>
                    <span>CLOUD 24/7 ACTIVE</span>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #cbd5e1; background: var(--bg-base); padding: 7px 16px; border-radius: 8px; border: 1px solid var(--border-color);" id="live-clock">
                    --:--:--
                </div>
                <button onclick="refreshData()" class="btn-read" style="display: flex; align-items: center; gap: 6px; padding: 8px 16px;">
                    <span>🔄</span> <span>Làm Mới</span>
                </button>
            </div>
        </header>

        <!-- KPI STATS (4 HỘP CHỈ SỐ ĐIỀU HÀNH) -->
        <section class="kpi-grid">
            <div class="kpi-card" style="--card-accent: #10b981;">
                <div class="kpi-lbl">💰 Tiền Mặt TCInvest (SSOT V2.0)</div>
                <div class="kpi-val" style="color: #34d399;">20,167,119 ₫</div>
                <div class="kpi-sub"><span style="color: #34d399; font-weight: 700;">100.0% Cash</span> • 0 CP Rủi Ro (An Toàn)</div>
            </div>
            <div class="kpi-card" style="--card-accent: #38bdf8;">
                <div class="kpi-lbl">📈 Lãi Ròng Thu Về Vòng 1</div>
                <div class="kpi-val" style="color: #38bdf8;">+167,119 ₫</div>
                <div class="kpi-sub">Đã tất toán 100% (HPG, TCB, MBB)</div>
            </div>
            <div class="kpi-card" style="--card-accent: #c084fc;">
                <div class="kpi-lbl">📑 Báo Cáo Hôm Nay ({today_str})</div>
                <div class="kpi-val" style="color: #c084fc;" id="stat-today-count">{today_reports_count} Báo Cáo</div>
                <div class="kpi-sub">Tự động chuyển Kho Vault qua ngày mới</div>
            </div>
            <div class="kpi-card" style="--card-accent: #f472b6;">
                <div class="kpi-lbl">🛡️ Hệ Thống Tự Hành 24/7</div>
                <div class="kpi-val" style="color: #f472b6;">{len(services)}/4 Daemons</div>
                <div class="kpi-sub">Watchdog Tự Hồi Phục Bất Tử</div>
            </div>
        </section>

        <!-- TABS NAV -->
        <nav class="tab-nav">
            <button class="tab-btn active" onclick="switchTab('reports')">
                <span>📑</span> <span>1. Thư Viện Báo Cáo 18 Cột Mốc</span>
                <span class="tab-badge" id="nav-total-count">{total_reports_count}</span>
            </button>
            <button class="tab-btn" onclick="switchTab('portfolio')">
                <span>🎯</span> <span>2. Tầm Ngắm Vòng 2 & TradingView</span>
            </button>
            <button class="tab-btn" onclick="switchTab('james-command')">
                <span>🎖️</span> <span>3. Bàn Chỉ Huy Master CIO James</span>
            </button>
            <button class="tab-btn" onclick="switchTab('timeline')">
                <span>⏰</span> <span>4. Tiến Độ 18 Cột Mốc Ngày</span>
            </button>
            <button class="tab-btn" onclick="switchTab('supervisor')">
                <span>🛡️</span> <span>5. Giám Sát Cụm Container 24/7</span>
            </button>
        </nav>

        <!-- ========================================================
             TAB 1: THƯ VIỆN BÁO CÁO (PHÂN LOẠI 2 TẦNG CHUYÊN NGHIỆP)
             ======================================================== -->
        <main id="tab-reports" class="tab-pane active">
            <div class="library-controller">
                <!-- TẦNG 1: THỜI GIAN & CA TÁC CHIẾN -->
                <div class="time-filter-section">
                    <div>
                        <div class="filter-row-header">📅 Kho Lưu Trữ Thời Gian</div>
                        <div class="date-pills">
                            <button class="date-pill-btn active" id="btn-date-today" onclick="selectDateFilter('today')">
                                <span>🌟</span> <span>Hôm Nay ({today_str})</span>
                            </button>
                            <button class="date-pill-btn" id="btn-date-yesterday" onclick="selectDateFilter('yesterday')">
                                <span>⏮️</span> <span>Hôm Qua</span>
                            </button>
                            <button class="date-pill-btn" id="btn-date-all" onclick="selectDateFilter('all')">
                                <span>🏛️</span> <span>Toàn Bộ Lịch Sử</span>
                            </button>
                            <select id="archive-date-select" class="archive-select" onchange="selectDateFromDropdown(this.value)">
                                {date_options_html}
                            </select>
                        </div>
                    </div>

                    <div>
                        <div class="filter-row-header">⏱️ 4 Ca Tác Chiến</div>
                        <div class="shifts-group">
                            <button class="shift-pill active" onclick="filterShift('all')">Tất Cả Ca</button>
                            <button class="shift-pill" onclick="filterShift('Ca Sáng')">🌅 Ca Sáng</button>
                            <button class="shift-pill" onclick="filterShift('Ca Trưa')">☀️ Ca Trưa</button>
                            <button class="shift-pill" onclick="filterShift('Ca Chiều')">🎯 Ca Chiều</button>
                            <button class="shift-pill" onclick="filterShift('Ca Tối')">🌙 Ca Tối & Đêm</button>
                        </div>
                    </div>
                </div>

                <!-- TẦNG 2: 5 KHỐI PHÂN LOẠI CHUYÊN MÔN THỂ CHẾ -->
                <div>
                    <div class="filter-row-header">🏛️ Phân Loại Khối Chức Năng (12 Phòng Ban)</div>
                    <div class="category-filter-section" id="cat-filter-buttons">
                        <button class="cat-btn active" onclick="filterCategory('all')">
                            <span>🌟</span> <span>Tất Cả</span>
                            <span class="cat-count" id="count-cat-all">0</span>
                        </button>
                        <button class="cat-btn" onclick="filterCategory('macro')">
                            <span>🌐</span> <span>Vĩ Mô & SBV</span>
                            <span class="cat-count" id="count-cat-macro">0</span>
                        </button>
                        <button class="cat-btn" onclick="filterCategory('equity_bctc')">
                            <span>📑</span> <span>BCTC & Pháp Y</span>
                            <span class="cat-count" id="count-cat-equity">0</span>
                        </button>
                        <button class="cat-btn" onclick="filterCategory('cio_execution')">
                            <span>🎖️</span> <span>Sổ Lệnh & Thực Thi</span>
                            <span class="cat-count" id="count-cat-cio">0</span>
                        </button>
                        <button class="cat-btn" onclick="filterCategory('risk_learning')">
                            <span>⚖️</span> <span>Rủi Ro & Tự Học</span>
                            <span class="cat-count" id="count-cat-risk">0</span>
                        </button>
                        <button class="cat-btn" onclick="filterCategory('mentorship')">
                            <span>🎓</span> <span>Học Viện Huấn Luyện</span>
                            <span class="cat-count" id="count-cat-mentor">0</span>
                        </button>
                    </div>
                </div>

                <!-- TẦNG 3: TOOLBAR TÌM KIẾM & CHẾ ĐỘ XEM -->
                <div class="library-toolbar">
                    <div class="search-box-wrap">
                        <span class="search-icon">🔍</span>
                        <input type="text" id="report-search" class="search-box" placeholder="Tìm theo mã CP (FPT, DGC, HPG...) hoặc tiêu đề báo cáo..." oninput="searchReports()">
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 12px; color: var(--text-muted); font-weight: 600;">Chế độ xem:</span>
                        <div class="view-mode-toggle">
                            <button class="view-btn active" id="btn-view-grid" onclick="switchViewMode('grid')">🖼️ Dạng Thẻ Grid</button>
                            <button class="view-btn" id="btn-view-table" onclick="switchViewMode('table')">📋 Dạng Bảng Nhanh</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- CONTAINER HIỂN THỊ BÁO CÁO -->
            <div id="reports-container">
                <!-- Sẽ được render bởi JavaScript -->
            </div>
        </main>

        <!-- ========================================================
             TAB 2: TẦM NGẮM VÒNG 2 & TRADINGVIEW (LIVE HOSE)
             ======================================================== -->
        <section id="tab-portfolio" class="tab-pane">
            <!-- TRADINGVIEW LIVE HOSE CHART WIDGET -->
            <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; padding: 22px; margin-bottom: 22px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; margin-bottom: 16px;">
                    <div>
                        <h3 style="font-size: 17px; color: #fff; display: flex; align-items: center; gap: 10px; font-weight: 800;">
                            <span>📈</span> <span>BIỂU ĐỒ NẾN KỸ THUẬT REALTIME TRADINGVIEW (LIVE SÀN HOSE)</span>
                        </h3>
                        <p style="font-size: 12.5px; color: var(--text-muted); margin-top: 5px;">
                            Soi trực tiếp Candlestick, Khối lượng Volume, MA20/MA50, RSI & MACD trên sàn HOSE • Cập nhật trực tiếp từng giây
                        </p>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;" id="tv-symbol-buttons">
                        <button class="tv-btn active" onclick="switchTVSymbol('HOSE:VNINDEX', this)">📈 VN-INDEX</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:FPT', this)">💎 FPT</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:DGC', this)">🧪 DGC</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:HPG', this)">🏗️ HPG</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:TCB', this)">🏦 TCB</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:MBB', this)">🛡️ MBB</button>
                    </div>
                </div>
                <div id="tv_chart_container" style="height: 540px; border-radius: 12px; overflow: hidden; border: 1px solid var(--border-color);"></div>
            </div>

            <!-- PHÂN BỔ VỐN & NGUYÊN TẮC -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 20px; margin-bottom: 22px;">
                <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; padding: 22px;">
                    <h3 style="font-size: 16px; margin-bottom: 16px; color: #fff; font-weight: 800;">📊 PHÂN BỔ TÀI SẢN THỰC TẾ (SSOT V2.0)</h3>
                    <div style="margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; font-size: 13.5px; margin-bottom: 8px;">
                            <span>Tiền Mặt Khả Dụng (Két TCInvest)</span>
                            <strong style="color: #34d399; font-family: 'JetBrains Mono', monospace;">100% (20,167,119 ₫)</strong>
                        </div>
                        <div style="background: var(--bg-base); height: 12px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border-color);">
                            <div style="background: linear-gradient(90deg, #10b981, #34d399); width: 100%; height: 100%;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 13.5px; margin-bottom: 8px;">
                            <span>Cổ Phiếu Đang Nắm Giữ</span>
                            <strong style="color: #94a3b8; font-family: 'JetBrains Mono', monospace;">0% (0 CP Rủi Ro)</strong>
                        </div>
                        <div style="background: var(--bg-base); height: 12px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border-color);">
                            <div style="background: #ef4444; width: 0%; height: 100%;"></div>
                        </div>
                    </div>
                    <p style="margin-top: 18px; font-size: 12.5px; color: #94a3b8; line-height: 1.6;">
                        🛡️ <strong>Chế độ Bảo Toàn Vốn:</strong> Quỹ đã thu hồi toàn bộ vốn và lợi nhuận Vòng 1 (+167,119 ₫) về két TCBS. Sẵn sàng 100% sức mua để kích hoạt Vòng 2 trong Khung Giờ Vàng!
                    </p>
                </div>

                <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; padding: 22px;">
                    <h3 style="font-size: 16px; margin-bottom: 16px; color: #fff; font-weight: 800;">🎯 QUY TẮC ĐI VỐN KIM TỰ THÁP (30% - 40% - 30%)</h3>
                    <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
                        <div>• <strong>Nhịp 1 (30% Thăm dò):</strong> Mua tại nền hỗ trợ khi có nến Test Cung (Vol cạn kiệt 30%-50% MA20).</div>
                        <div>• <strong>Nhịp 2 (40% Gia tăng):</strong> Giải ngân khi giá vượt đỉnh Pivot kèm Vol &ge; 150% MA20.</div>
                        <div>• <strong>Nhịp 3 (30% Hoàn tất):</strong> Gia tăng khi cổ phiếu Retest đỉnh thành công.</div>
                        <div style="color: #ef4444; margin-top: 10px; font-weight: 700;">• Ngưỡng cắt lỗ cứng: Khóa cứng Stop Loss 2xATR &le; 7.5% NAV.</div>
                    </div>
                </div>
            </div>

            <!-- BẢNG TẦM NGẮM VÒNG 2 -->
            <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; padding: 22px;">
                <h3 style="font-size: 16px; margin-bottom: 18px; color: #fff; font-weight: 800;">⭐ BẢNG PHÂN TÍCH PHÁP Y 5 SIÊU CỔ PHIẾU TẦM NGẮM VÒNG 2</h3>
                <div style="overflow-x: auto;">
                    <table class="standard-table">
                        <thead>
                            <tr>
                                <th>Mã</th>
                                <th>Tên Doanh Nghiệp</th>
                                <th>Doanh Thu Q</th>
                                <th>LNST Q</th>
                                <th>OCF/LNST</th>
                                <th>Beneish M</th>
                                <th>P/E</th>
                                <th>Vùng Gom Kim Tự Tháp</th>
                                <th>Cắt Lỗ Stop</th>
                                <th>Target TP1/TP2</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="padding: 12px 16px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono', monospace;">FPT</td>
                                <td style="padding: 12px 16px; font-weight: 600;">Công Nghệ FPT</td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">15,200 Tỷ</td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">2,850 Tỷ</td>
                                <td style="padding: 12px 16px;"><span style="color: #34d399; font-weight: bold;">1.35x 🟩</span></td>
                                <td style="padding: 12px 16px;"><span style="color: #34d399;">-2.85 (Sạch)</span></td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">22.4x</td>
                                <td style="padding: 12px 16px; color: #38bdf8; font-weight: 600;">134 - 136 (Thăm dò 30%)</td>
                                <td style="padding: 12px 16px; color: #f87171; font-weight: 600;">128 (-5.5%)</td>
                                <td style="padding: 12px 16px; color: #34d399; font-weight: 600;">152 / 165</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px 16px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono', monospace;">DGC</td>
                                <td style="padding: 12px 16px; font-weight: 600;">Hóa Chất Đức Giang</td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">2,950 Tỷ</td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">860 Tỷ</td>
                                <td style="padding: 12px 16px;"><span style="color: #34d399; font-weight: bold;">1.18x 🟩</span></td>
                                <td style="padding: 12px 16px;"><span style="color: #34d399;">-2.61 (Sạch)</span></td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">14.2x</td>
                                <td style="padding: 12px 16px; color: #38bdf8; font-weight: 600;">112 - 114 (Thăm dò 30%)</td>
                                <td style="padding: 12px 16px; color: #f87171; font-weight: 600;">106 (-6.2%)</td>
                                <td style="padding: 12px 16px; color: #34d399; font-weight: 600;">128 / 138</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px 16px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono', monospace;">HPG</td>
                                <td style="padding: 12px 16px; font-weight: 600;">Tập Đoàn Hòa Phát</td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">35,800 Tỷ</td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">3,200 Tỷ</td>
                                <td style="padding: 12px 16px;"><span style="color: #34d399; font-weight: bold;">1.42x 🟩</span></td>
                                <td style="padding: 12px 16px;"><span style="color: #34d399;">-2.90 (Sạch)</span></td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">12.8x</td>
                                <td style="padding: 12px 16px; color: #38bdf8; font-weight: 600;">26.5 - 27.0 (Chờ điểm gom)</td>
                                <td style="padding: 12px 16px; color: #f87171; font-weight: 600;">25.2 (-5.8%)</td>
                                <td style="padding: 12px 16px; color: #34d399; font-weight: 600;">31.0 / 34.0</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px 16px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono', monospace;">TCB</td>
                                <td style="padding: 12px 16px; font-weight: 600;">Ngân Hàng Techcombank</td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">12,400 Tỷ</td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">7,100 Tỷ</td>
                                <td style="padding: 12px 16px;"><span style="color: #34d399; font-weight: bold;">1.10x 🟩</span></td>
                                <td style="padding: 12px 16px;"><span style="color: #34d399;">-2.45 (Sạch)</span></td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">6.8x</td>
                                <td style="padding: 12px 16px; color: #38bdf8; font-weight: 600;">23.0 - 23.5 (Định giá rẻ)</td>
                                <td style="padding: 12px 16px; color: #f87171; font-weight: 600;">21.8 (-6.0%)</td>
                                <td style="padding: 12px 16px; color: #34d399; font-weight: 600;">28.0 / 30.5</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px 16px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono', monospace;">MBB</td>
                                <td style="padding: 12px 16px; font-weight: 600;">Ngân Hàng Quân Đội</td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">14,100 Tỷ</td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">6,500 Tỷ</td>
                                <td style="padding: 12px 16px;"><span style="color: #34d399; font-weight: bold;">1.15x 🟩</span></td>
                                <td style="padding: 12px 16px;"><span style="color: #34d399;">-2.52 (Sạch)</span></td>
                                <td style="padding: 12px 16px; font-family: 'JetBrains Mono', monospace;">5.9x</td>
                                <td style="padding: 12px 16px; color: #38bdf8; font-weight: 600;">24.5 - 25.0 (Tích lũy)</td>
                                <td style="padding: 12px 16px; color: #f87171; font-weight: 600;">23.2 (-5.5%)</td>
                                <td style="padding: 12px 16px; color: #34d399; font-weight: 600;">28.5 / 31.0</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ========================================================
             TAB 3: BÀN CHỈ HUY MASTER CIO JAMES (SPLIT-VIEW 2 CỘT)
             ======================================================== -->
        <section id="tab-james-command" class="tab-pane">
            <div class="james-split-container">
                <!-- CỘT TRÁI (68%): LUỒNG TƯƠNG TÁC ĐIỀU HÀNH -->
                <div class="james-main-panel">
                    <!-- Header Panel -->
                    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #172033 100%); border-bottom: 1px solid var(--border-color); padding: 18px 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                        <div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 22px;">🎖️</span>
                                <h3 style="font-size: 17px; font-weight: 800; color: #fff;">TRUNG TÂM CHỈ HUY TÁC CHIẾN — MASTER CIO JAMES</h3>
                            </div>
                            <p style="font-size: 12.5px; color: var(--text-muted); margin-top: 4px;">
                                Kênh giao việc trực tiếp từ Chủ tịch Phước Trần • Tiếp nhận & đóng lặp thực thi qua 10 phòng ban thời gian thực
                            </p>
                        </div>
                        <div>
                            <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); padding: 5px 12px; border-radius: 9999px; font-size: 11px; font-weight: 700;">
                                ● ĐANG TRỰC CHIẾN 24/7
                            </span>
                        </div>
                    </div>

                    <!-- Quick Command Chips -->
                    <div style="background: var(--bg-card); border-bottom: 1px solid var(--border-color); padding: 12px 20px; display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
                        <span style="font-size: 11px; font-weight: 800; color: var(--text-dim); text-transform: uppercase;">Lệnh Nhanh:</span>
                        <button class="cmd-chip" onclick="sendQuickCommand('/tcbs')">🏦 /tcbs (Két Tiền)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/danhmuc')">📊 /danhmuc (100% Cash)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/solenh')">⚡ /solenh (Sổ Lệnh Vòng 2)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/hop FPT')">⚔️ /hop FPT (Họp Soi FPT)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/hop DGC')">🎯 /hop DGC (Họp Soi DGC)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/hop HPG')">🏗️ /hop HPG (Họp Soi HPG)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/baomat')">🛡️ /baomat (Khiên Bảo Mật)</button>
                    </div>

                    <!-- Chat Messages Stream -->
                    <div id="james-chat-stream" style="flex-grow: 1; padding: 24px; overflow-y: auto; max-height: 520px; display: flex; flex-direction: column; gap: 16px;">
                        <!-- Lời chào đầu tiên -->
                        <div class="msg-james">
                            <div class="msg-header">
                                <span style="font-weight: 800; color: #c084fc;">🎖️ Master CIO James (Ban 8)</span>
                                <span style="font-size: 11px; color: var(--text-dim); font-family: 'JetBrains Mono', monospace;">TRỰC CHIẾN 24/7</span>
                            </div>
                            <div class="msg-body markdown-body">
                                <p>Kính chào <strong>Chủ tịch Trần Quốc Thiên Phước</strong>!</p>
                                <p>Tôi là <strong>James</strong> — Tổng Tư Lệnh Master CIO trực tiếp chỉ huy toàn bộ Quỹ Apex. Tôi túc trực 24/7 để tiếp nhận chỉ thị điều hành trực tiếp từ Chủ tịch ngay tại Web Portal này.</p>
                                <p>Chủ tịch có thể bấm các <strong>Lệnh Nhanh</strong> phía trên hoặc gõ bất kỳ chỉ thị nào bên dưới (ví dụ: <code>/hop FPT</code>, <code>Rà soát BCTC DGC</code>, <code>/danhmuc</code>, <code>/tcbs</code>, <code>/solenh</code>). Tôi sẽ lập tức điều phối các phòng ban thực thi và phản hồi số liệu ngay lập tức!</p>
                            </div>
                        </div>
                    </div>

                    <!-- Input Box -->
                    <div style="background: var(--bg-card); border-top: 1px solid var(--border-color); padding: 16px 20px;">
                        <form id="james-cmd-form" onsubmit="submitJamesCommand(event)" style="display: flex; gap: 12px; align-items: center;">
                            <input type="text" id="james-cmd-input" class="search-box" style="flex-grow: 1; padding: 12px 18px; font-size: 14px;" placeholder="💬 Gõ chỉ thị điều hành cho James (Ví dụ: /hop FPT, /danhmuc, Soi BCTC DGC...)..." autocomplete="off">
                            <button type="submit" id="james-submit-btn" class="btn-read" style="padding: 12px 24px; font-size: 14px; display: flex; align-items: center; gap: 8px;">
                                <span>🚀</span> <span>Gửi Chỉ Thị</span>
                            </button>
                        </form>
                    </div>
                </div>

                <!-- CỘT PHẢI (32%): LIVE STICKY SIDEBAR -->
                <div class="james-sidebar-panel">
                    <!-- Widget 1: Live TCBS Account -->
                    <div class="sidebar-widget">
                        <div class="sidebar-widget-title">🏦 Trạng Thái Tài Khoản TCBS</div>
                        <div style="font-size: 13px; color: #94a3b8;">Số tài khoản: <strong style="color: #38bdf8; font-family: 'JetBrains Mono', monospace;">105C307855</strong></div>
                        <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">Chủ tài khoản: <strong style="color: #fff;">Trần Quốc Thiên Phước</strong></div>
                        <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.06);">
                            <div style="font-size: 11px; text-transform: uppercase; color: var(--text-dim); font-weight: 800;">Tiền mặt khả dụng:</div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 20px; font-weight: 800; color: #34d399; margin-top: 2px;">20,167,119 ₫</div>
                            <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Tỷ trọng: 100% Cash • 0 CP kẹp hàng</div>
                        </div>
                    </div>

                    <!-- Widget 2: Countdown to Next Session -->
                    <div class="sidebar-widget">
                        <div class="sidebar-widget-title">⏳ Đếm Ngược Phiên Giao Dịch</div>
                        <div style="font-size: 12.5px; color: #cbd5e1;">Phiên tiếp theo: <strong style="color: #fbbf24;">09:00 Thứ Hai (09/11)</strong></div>
                        <div id="countdown-timer" style="font-family: 'JetBrains Mono', monospace; font-size: 22px; font-weight: 800; color: #38bdf8; margin: 10px 0; letter-spacing: 0.04em;">
                            --:--:--
                        </div>
                        <div style="font-size: 11.5px; color: var(--text-muted); line-height: 1.5;">
                            Chiến dịch: Chuẩn bị kích hoạt giải ngân Vòng 2 trong Khung Giờ Vàng (14h00 - 14h25).
                        </div>
                    </div>

                    <!-- Widget 3: Quick Watchlist Jump -->
                    <div class="sidebar-widget">
                        <div class="sidebar-widget-title">🎯 Tầm Ngắm Vòng 2 (Top 4)</div>
                        <div style="display: flex; flex-direction: column; gap: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-base); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color);">
                                <div><strong style="color: #38bdf8; font-family: 'JetBrains Mono', monospace;">HDB</strong> <span style="font-size: 12px; color: var(--text-muted);">22,310 - 22,500</span></div>
                                <button onclick="switchTab('portfolio'); switchTVSymbol('HOSE:VNINDEX')" style="background: rgba(56, 189, 248, 0.15); border: none; color: #38bdf8; padding: 4px 8px; border-radius: 4px; font-size: 11px; cursor: pointer; font-weight: 700;">Chart</button>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-base); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color);">
                                <div><strong style="color: #38bdf8; font-family: 'JetBrains Mono', monospace;">MSH</strong> <span style="font-size: 12px; color: var(--text-muted);">35,060 - 35,500</span></div>
                                <button onclick="switchTab('portfolio'); switchTVSymbol('HOSE:VNINDEX')" style="background: rgba(56, 189, 248, 0.15); border: none; color: #38bdf8; padding: 4px 8px; border-radius: 4px; font-size: 11px; cursor: pointer; font-weight: 700;">Chart</button>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-base); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color);">
                                <div><strong style="color: #38bdf8; font-family: 'JetBrains Mono', monospace;">BAF</strong> <span style="font-size: 12px; color: var(--text-muted);">30,710 - 30,900</span></div>
                                <button onclick="switchTab('portfolio'); switchTVSymbol('HOSE:VNINDEX')" style="background: rgba(56, 189, 248, 0.15); border: none; color: #38bdf8; padding: 4px 8px; border-radius: 4px; font-size: 11px; cursor: pointer; font-weight: 700;">Chart</button>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-base); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color);">
                                <div><strong style="color: #38bdf8; font-family: 'JetBrains Mono', monospace;">IDC</strong> <span style="font-size: 12px; color: var(--text-muted);">34,500 - 34,900</span></div>
                                <button onclick="switchTab('portfolio'); switchTVSymbol('HOSE:VNINDEX')" style="background: rgba(56, 189, 248, 0.15); border: none; color: #38bdf8; padding: 4px 8px; border-radius: 4px; font-size: 11px; cursor: pointer; font-weight: 700;">Chart</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- ========================================================
             TAB 4: 18 CỘT MỐC TÁC CHIẾN 24H
             ======================================================== -->
        <section id="tab-timeline" class="tab-pane">
            <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; padding: 22px;">
                <h3 style="font-size: 16px; margin-bottom: 18px; color: #fff; font-weight: 800;">⏰ BẢNG TIẾN ĐỘ 18 CỘT MỐC TÁC CHIẾN 24H (TỰ ĐỘNG CHẠY ENGINE THẬT)</h3>
                <div style="overflow-x: auto;">
                    <table class="standard-table">
                        <thead>
                            <tr>
                                <th style="width: 110px;">Thời Gian</th>
                                <th style="width: 50px;">Icon</th>
                                <th>Nhiệm Vụ & Phòng Ban Phụ Trách</th>
                                <th style="width: 150px;">Khung Giờ</th>
                                <th style="width: 160px;">Trạng Thái Thực Thi</th>
                            </tr>
                        </thead>
                        <tbody>
                            {milestone_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ========================================================
             TAB 5: SUPERVISOR & 4 DAEMONS 24/7
             ======================================================== -->
        <section id="tab-supervisor" class="tab-pane">
            <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; padding: 22px;">
                <h3 style="font-size: 16px; margin-bottom: 18px; color: #fff; font-weight: 800;">🛡️ TRẠNG THÁI 4 TIẾN TRÌNH TỰ HÀNH 24/24 (WATCHDOG AUTO-RECOVERY)</h3>
                <div style="overflow-x: auto;">
                    <table class="standard-table">
                        <thead>
                            <tr>
                                <th>Tên Dịch Vụ</th>
                                <th>PID</th>
                                <th>Trạng Thái</th>
                                <th>Số Lần Tự Hồi Phục</th>
                                <th>Thời Gian Chạy Liên Tục</th>
                            </tr>
                        </thead>
                        <tbody>
                            {services_rows}
                        </tbody>
                    </table>
                </div>
                <div style="margin-top: 22px; font-size: 12px; color: var(--text-dim); display: flex; justify-content: space-between;">
                    <div>Hạ tầng: Linux Cloud Container / Render Web Service (Port 10000)</div>
                    <div>Được bảo vệ bởi: Watchdog Circuit Breaker (Cầu chì ngắt lỗi tự động)</div>
                </div>
            </div>
        </section>
    </div>

    <!-- MODAL ĐỌC BÁO CÁO TOÀN VĂN -->
    <div id="report-modal" class="modal-overlay" onclick="closeModalOnOverlay(event)">
        <div class="modal-container">
            <div class="modal-header">
                <div>
                    <span id="modal-dept-badge" class="dept-tag" style="margin-bottom: 6px; display: inline-block;">BAN 8</span>
                    <h2 id="modal-report-title" style="font-size: 18px; color: #fff; margin-top: 4px; font-weight: 800;">Tiêu đề báo cáo</h2>
                    <div id="modal-report-meta" style="font-size: 12px; color: var(--text-muted); margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                        Ngày: 2026-11-07 | Dung lượng: 12 KB
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <button class="date-pill-btn" onclick="printReport()" style="padding: 6px 12px; font-size: 12px;">🖨️ In / PDF</button>
                    <button class="date-pill-btn" onclick="copyReportLink()" style="padding: 6px 12px; font-size: 12px;">📋 Sao Chép Link</button>
                    <button onclick="closeReportModal()" style="background: rgba(255,255,255,0.08); border: none; color: #fff; width: 34px; height: 34px; border-radius: 50%; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center;">✕</button>
                </div>
            </div>
            <div class="modal-body markdown-body" id="modal-content-area">
                <div style="text-align: center; padding: 40px; color: var(--text-muted);">Đang tải toàn văn báo cáo...</div>
            </div>
        </div>
    </div>

    <script>
        // Cấu hình marked.js giữ nguyên ngắt dòng
        if (window.marked) {{
            marked.setOptions({{
                breaks: true,
                gfm: true
            }});
        }}

        // Dữ liệu ban đầu
        let allReports = {initial_reports_json};
        let availableDates = {available_dates_json};
        const todayDateStr = "{today_str}";

        // Trạng thái bộ lọc
        let currentDateFilter = 'today'; // 'today', 'yesterday', 'all', hoặc 'YYYY-MM-DD'
        let currentShiftFilter = 'all';  // 'all', 'Ca Sáng', 'Ca Trưa', 'Ca Chiều', 'Ca Tối'
        let currentCategoryFilter = 'all'; // 'all', 'macro', 'equity_bctc', 'cio_execution', 'risk_learning', 'mentorship'
        let currentSearchQuery = '';
        let currentViewMode = 'grid'; // 'grid' hoặc 'table'

        // Ánh xạ 5 Khối Chuyên Môn Thể Chế
        const CATEGORY_MAP = {{
            'macro': ['ban_1_macro', 'ban_1_vn_macro'],
            'equity_bctc': ['ban_2_equity', 'ban_2_vn_equity', 'ban_3_synthesis', 'ban_3_vn_synthesis', 'ban_10_ir_filings'],
            'cio_execution': ['ban_8_cio', 'ban_7_specialist', 'ban_7_vn_specialist', 'ban_9_sentinel'],
            'risk_learning': ['ban_4_risk', 'ban_4_vn_risk', 'ban_5_learning', 'ban_3_debates', 'ban_12_ombudsman'],
            'mentorship': ['ban_6_mentorship', 'ban_6_vn_coach', 'ban_11_video']
        }};

        // Đồng hồ thời gian thực (Giờ Việt Nam)
        function updateLiveClock() {{
            const now = new Date();
            const timeStr = now.toLocaleTimeString('vi-VN', {{ hour12: false }});
            const dateStr = now.toLocaleDateString('vi-VN');
            const el = document.getElementById('live-clock');
            if (el) el.innerText = `${{dateStr}} ${{timeStr}} (ICT)`;

            // Cập nhật đồng hồ đếm ngược phiên Thứ Hai (09:00 AM)
            updateCountdown();
        }}
        setInterval(updateLiveClock, 1000);
        updateLiveClock();

        function updateCountdown() {{
            const el = document.getElementById('countdown-timer');
            if (!el) return;

            const now = new Date();
            // Tính toán thời điểm Thứ Hai 09:00 gần nhất
            let target = new Date();
            let day = target.getDay(); // 0: Chủ Nhật, 6: Thứ Bảy
            let daysUntilMonday = (1 + 7 - day) % 7;
            if (daysUntilMonday === 0 && (target.getHours() >= 9)) {{
                daysUntilMonday = 7;
            }}
            target.setDate(target.getDate() + daysUntilMonday);
            target.setHours(9, 0, 0, 0);

            let diff = target - now;
            if (diff <= 0) {{
                el.innerText = 'ĐANG TRONG PHIÊN GIAO DỊCH!';
                el.style.color = '#34d399';
                return;
            }}

            let hours = Math.floor(diff / (1000 * 60 * 60));
            let mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            let secs = Math.floor((diff % (1000 * 60)) / 1000);

            const pad = (n) => String(n).padStart(2, '0');
            el.innerText = `${{pad(hours)}}h : ${{pad(mins)}}m : ${{pad(secs)}}s`;
        }}

        // Chuyển Tab
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

            const targetBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
            if (targetBtn) targetBtn.classList.add('active');

            const targetPane = document.getElementById('tab-' + tabId);
            if (targetPane) targetPane.classList.add('active');

            if (tabId === 'portfolio') {{
                setTimeout(() => initTradingViewWidget(currentTVSymbol), 100);
            }}
        }}

        // TRADINGVIEW REALTIME WIDGET (ĐỀ XUẤT 3)
        let currentTVSymbol = 'HOSE:VNINDEX';
        function initTradingViewWidget(symbol) {{
            const container = document.getElementById('tv_chart_container');
            if (!container || typeof TradingView === 'undefined') return;
            container.innerHTML = '';
            new TradingView.widget({{
                "autosize": true,
                "symbol": symbol || currentTVSymbol,
                "interval": "D",
                "timezone": "Asia/Ho_Chi_Minh",
                "theme": "dark",
                "style": "1",
                "locale": "vi_VN",
                "toolbar_bg": "#0e1524",
                "enable_publishing": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "container_id": "tv_chart_container"
            }});
        }}

        function switchTVSymbol(symbol, btn) {{
            currentTVSymbol = symbol;
            document.querySelectorAll('.tv-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            initTradingViewWidget(symbol);
        }}

        // MASTER CIO JAMES COMMAND CENTER
        let isJamesProcessing = false;
        async function submitJamesCommand(e) {{
            if (e) e.preventDefault();
            if (isJamesProcessing) return;

            const input = document.getElementById('james-cmd-input');
            const cmd = input.value.trim();
            if (!cmd) return;

            input.value = '';
            appendUserMessage(cmd);

            // Bật trạng thái loading
            isJamesProcessing = true;
            const submitBtn = document.getElementById('james-submit-btn');
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.6';
            const tempLoadingId = appendJamesLoading();

            try {{
                const res = await fetch('/api/command', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ command: cmd }})
                }});
                const data = await res.json();
                removeJamesLoading(tempLoadingId);

                if (data.ok) {{
                    appendJamesMessage(data.response, data.timestamp);
                }} else {{
                    appendJamesMessage('❌ **Lỗi điều hành:** ' + (data.error || 'Không thể phản hồi.'));
                }}
            }} catch (err) {{
                removeJamesLoading(tempLoadingId);
                appendJamesMessage('❌ **Lỗi kết nối:** Không thể gửi chỉ thị tới Master CIO James trên máy chủ đám mây (' + err.message + ').');
            }} finally {{
                isJamesProcessing = false;
                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
            }}
        }}

        function sendQuickCommand(cmd) {{
            document.getElementById('james-cmd-input').value = cmd;
            submitJamesCommand();
        }}

        function appendUserMessage(text) {{
            const stream = document.getElementById('james-chat-stream');
            const nowTime = new Date().toLocaleTimeString('vi-VN', {{ hour12: false }});
            const div = document.createElement('div');
            div.className = 'msg-user';
            div.innerHTML = `
                <div class="msg-header" style="border-bottom-color: rgba(255,255,255,0.2);">
                    <span style="font-weight: 800; color: #fff;">👤 Chủ tịch Trần Quốc Thiên Phước</span>
                    <span style="font-size: 11px; opacity: 0.8; font-family: 'JetBrains Mono', monospace;">${{nowTime}}</span>
                </div>
                <div style="font-size: 14px; line-height: 1.6;">${{text}}</div>
            `;
            stream.appendChild(div);
            stream.scrollTop = stream.scrollHeight;
        }}

        function appendJamesLoading() {{
            const stream = document.getElementById('james-chat-stream');
            const loadingId = 'loading-' + Date.now();
            const div = document.createElement('div');
            div.className = 'msg-james';
            div.id = loadingId;
            div.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px; color: #c084fc; font-size: 13.5px;">
                    <span class="pulse-dot" style="background: #c084fc; box-shadow: 0 0 10px #c084fc;"></span>
                    <span>Master CIO James đang triệu tập các phòng ban và xử lý chỉ thị...</span>
                </div>
            `;
            stream.appendChild(div);
            stream.scrollTop = stream.scrollHeight;
            return loadingId;
        }}

        function removeJamesLoading(id) {{
            const el = document.getElementById(id);
            if (el) el.remove();
        }}

        // BỘ TIỀN XỬ LÝ THÔNG MINH CHO CÂU TRẢ LỜI CỦA JAMES (SMART VISUAL FORMATTER)
        function formatJamesResponseHtml(rawText) {{
            if (!rawText) return '';

            // Nếu câu trả lời có chứa thông tin tài khoản / két tiền / danh mục
            let htmlOutput = '';
            let textToParse = rawText;

            // 1. Trích xuất 4 KPI nếu có dữ liệu tiền mặt
            if (rawText.includes('20,167,119') || rawText.includes('105C307855')) {{
                htmlOutput += `
                <div class="exec-kpi-banner">
                    <div class="exec-kpi-box" style="border-left: 3px solid #10b981;">
                        <div class="exec-kpi-box-lbl">💰 Két Tiền Mặt TCBS</div>
                        <div class="exec-kpi-box-val" style="color: #34d399;">20,167,119 ₫</div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">100% Cash Bảo Toàn</div>
                    </div>
                    <div class="exec-kpi-box" style="border-left: 3px solid #38bdf8;">
                        <div class="exec-kpi-box-lbl">🛡️ Kho Hàng Hiện Tại</div>
                        <div class="exec-kpi-box-val" style="color: #38bdf8;">0 CP</div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">0% Rủi Ro Biến Động</div>
                    </div>
                    <div class="exec-kpi-box" style="border-left: 3px solid #c084fc;">
                        <div class="exec-kpi-box-lbl">📈 Lãi Vòng 1 Thực Thu</div>
                        <div class="exec-kpi-box-val" style="color: #c084fc;">+167,119 ₫</div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">Đã Tất Toán 100%</div>
                    </div>
                    <div class="exec-kpi-box" style="border-left: 3px solid #fbbf24;">
                        <div class="exec-kpi-box-lbl">⏱️ Chế Độ Thị Trường</div>
                        <div class="exec-kpi-box-val" style="color: #fbbf24; font-size: 13.5px;">Chờ ATO Thứ Hai</div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">Mở Cửa 09:00 AM</div>
                    </div>
                </div>
                `;
            }}

            // 2. Chuyển đổi các mục cổ phiếu dạng 1. HDB(...), 2. MSH(...) thành Stock Target Cards
            const stockRegex = /(\\d+)\\.\\s*([A-Z]{3})\\s*\\((.*?)\\):\\s*Gom thăm dò Limit LO quanh\\s*(.*?);\\s*Gia tăng khi vượt\\s*(.*?)\\s*trong Khung Giờ Vàng.*?\\|\\s*Hạng\\s*(.*?)\\s*\\((.*?)\\)\\s*•\\s*(.*?)\\s*•\\s*(.*)/g;
            let hasStockCards = false;
            let stockCardsHtml = '<div style="margin: 16px 0;">';

            let match;
            while ((match = stockRegex.exec(rawText)) !== null) {{
                hasStockCards = true;
                const ticker = match[2];
                const compName = match[3];
                const buyRange = match[4];
                const breakout = match[5];
                const rank = match[6];
                const rankDetail = match[7];
                const faMetrics = match[8];
                const alloc = match[9];

                stockCardsHtml += `
                <div class="stock-target-card">
                    <div class="stock-target-top">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="stock-target-badge">${{ticker}}</span>
                            <strong style="color: #fff; font-size: 13.5px;">${{compName}}</strong>
                            <span style="font-size: 11px; color: #c084fc; background: rgba(192, 132, 252, 0.1); padding: 2px 6px; border-radius: 4px;">${{rank}} (${{rankDetail}})</span>
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11.5px; color: #94a3b8;">
                            ${{alloc}}
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0;">
                        <span class="price-badge-buy">🎯 Gom LO: <strong>${{buyRange}}</strong></span>
                        <span class="price-badge-breakout">⚡ Bứt phá: <strong>> ${{breakout}}</strong></span>
                    </div>
                    <div style="font-size: 12px; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">
                        📊 ${{faMetrics}}
                    </div>
                </div>
                `;
            }}
            stockCardsHtml += '</div>';

            if (hasStockCards) {{
                // Xóa phần list text thô để thay bằng card đẹp
                textToParse = textToParse.replace(/\\d+\\.\\s*[A-Z]{3}\\s*\\(.*\\):\\s*Gom thăm dò.*?NAV\\)/g, '');
                htmlOutput += stockCardsHtml;
            }}

            // 3. Thu gọn phần Lịch sử Vòng 1 vào Accordion nếu có
            if (textToParse.includes('LỊCH SỬ CHIẾN DỊCH VÒNG 1')) {{
                const round1Match = textToParse.match(/✅\\s*1\\.\\s*LỊCH SỬ CHIẾN DỊCH VÒNG 1[\\s\\S]*?(?=🎯\\s*2\\.\\s*SỔ LỆNH|\\n\\n\\n|$)/);
                if (round1Match) {{
                    const round1Content = round1Match[0];
                    textToParse = textToParse.replace(round1Content, `
<details class="round1-accordion">
    <summary>📁 CHI TIẾT CHIẾN DỊCH VÒNG 1 (ĐÃ TẤT TOÁN 100% — BẤM ĐỂ MỞ/ĐÓNG)</summary>
    <div class="round1-body">
        ${{round1Content.replace(/•/g, '<br>• ')}}
    </div>
</details>
                    `);
                }}
            }}

            // Render Markdown cho phần còn lại
            const parsedMd = window.marked ? marked.parse(textToParse) : `<pre style="white-space: pre-wrap;">${{textToParse}}</pre>`;
            htmlOutput += parsedMd;
            return htmlOutput;
        }}

        function appendJamesMessage(rawText, timestamp) {{
            const stream = document.getElementById('james-chat-stream');
            const nowTime = timestamp || new Date().toLocaleTimeString('vi-VN', {{ hour12: false }});
            const div = document.createElement('div');
            div.className = 'msg-james';
            
            const formattedContent = formatJamesResponseHtml(rawText);

            div.innerHTML = `
                <div class="msg-header">
                    <span style="font-weight: 800; color: #c084fc;">🎖️ Master CIO James (Ban 8)</span>
                    <span style="font-size: 11px; color: var(--text-dim); font-family: 'JetBrains Mono', monospace;">${{nowTime}}</span>
                </div>
                <div class="msg-body markdown-body">${{formattedContent}}</div>
            `;
            stream.appendChild(div);
            stream.scrollTop = stream.scrollHeight;
        }}

        // BỘ LỌC NGÀY & KHO LƯU TRỮ
        function selectDateFilter(mode) {{
            currentDateFilter = mode;
            document.querySelectorAll('.date-pill-btn').forEach(b => b.classList.remove('active'));

            if (mode === 'today') {{
                document.getElementById('btn-date-today').classList.add('active');
                document.getElementById('archive-date-select').value = todayDateStr;
            }} else if (mode === 'yesterday') {{
                document.getElementById('btn-date-yesterday').classList.add('active');
            }} else if (mode === 'all') {{
                document.getElementById('btn-date-all').classList.add('active');
            }}
            applyAllFilters();
        }}

        function selectDateFromDropdown(selectedDate) {{
            currentDateFilter = selectedDate;
            document.querySelectorAll('.date-pill-btn').forEach(b => b.classList.remove('active'));
            if (selectedDate === todayDateStr) {{
                document.getElementById('btn-date-today').classList.add('active');
            }}
            applyAllFilters();
        }}

        // BỘ LỌC CA TÁC CHIẾN
        function filterShift(shiftName) {{
            currentShiftFilter = shiftName;
            document.querySelectorAll('.shift-pill').forEach(b => b.classList.remove('active'));
            const activeBtn = Array.from(document.querySelectorAll('.shift-pill')).find(b => b.getAttribute('onclick').includes(shiftName));
            if (activeBtn) activeBtn.classList.add('active');
            applyAllFilters();
        }}

        // BỘ LỌC 5 KHỐI PHÂN LOẠI THỂ CHẾ
        function filterCategory(catKey) {{
            currentCategoryFilter = catKey;
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = Array.from(document.querySelectorAll('.cat-btn')).find(b => b.getAttribute('onclick').includes(catKey));
            if (activeBtn) activeBtn.classList.add('active');
            applyAllFilters();
        }}

        // TÌM KIẾM
        function searchReports() {{
            currentSearchQuery = (document.getElementById('report-search').value || '').toLowerCase().trim();
            applyAllFilters();
        }}

        // CHUYỂN ĐỔI CHẾ ĐỘ XEM (GRID VS TABLE)
        function switchViewMode(mode) {{
            currentViewMode = mode;
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            if (mode === 'grid') {{
                document.getElementById('btn-view-grid').classList.add('active');
            }} else {{
                document.getElementById('btn-view-table').classList.add('active');
            }}
            applyAllFilters();
        }}

        // ÁP DỤNG ĐỒNG THỜI CÁC BỘ LỌC VÀ CẬP NHẬT BADGE ĐẾM
        function applyAllFilters() {{
            let dateFiltered = allReports;

            // 1. Lọc theo Ngày
            if (currentDateFilter === 'today') {{
                dateFiltered = dateFiltered.filter(r => r.date === todayDateStr);
            }} else if (currentDateFilter === 'yesterday') {{
                const olderDates = availableDates.map(d => d.date).filter(d => d < todayDateStr);
                const yesterdayDate = olderDates[0] || '';
                if (yesterdayDate) {{
                    dateFiltered = dateFiltered.filter(r => r.date === yesterdayDate);
                }}
            }} else if (currentDateFilter !== 'all') {{
                dateFiltered = dateFiltered.filter(r => r.date === currentDateFilter);
            }}

            // 2. Lọc theo Ca Tác Chiến
            if (currentShiftFilter !== 'all') {{
                dateFiltered = dateFiltered.filter(r => r.shift_label && r.shift_label.includes(currentShiftFilter));
            }}

            // Cập nhật số đếm trên 5 nút khối chuyên môn (Category Badges)
            updateCategoryCounts(dateFiltered);

            let finalFiltered = dateFiltered;

            // 3. Lọc theo Khối Chuyên Môn Thể Chế
            if (currentCategoryFilter !== 'all') {{
                const allowedDepts = CATEGORY_MAP[currentCategoryFilter] || [];
                finalFiltered = finalFiltered.filter(r => allowedDepts.includes(r.dept_id));
            }}

            // 4. Lọc theo Từ Khóa
            if (currentSearchQuery) {{
                finalFiltered = finalFiltered.filter(r => 
                    (r.title && r.title.toLowerCase().includes(currentSearchQuery)) ||
                    (r.preview && r.preview.toLowerCase().includes(currentSearchQuery)) ||
                    (r.file_name && r.file_name.toLowerCase().includes(currentSearchQuery))
                );
            }}

            renderReports(finalFiltered);
        }}

        function updateCategoryCounts(reportsList) {{
            const total = reportsList.length;
            const elTotal = document.getElementById('count-cat-all');
            if (elTotal) elTotal.innerText = total;

            for (const [catKey, depts] of Object.entries(CATEGORY_MAP)) {{
                const count = reportsList.filter(r => depts.includes(r.dept_id)).length;
                let badgeId = '';
                if (catKey === 'macro') badgeId = 'count-cat-macro';
                else if (catKey === 'equity_bctc') badgeId = 'count-cat-equity';
                else if (catKey === 'cio_execution') badgeId = 'count-cat-cio';
                else if (catKey === 'risk_learning') badgeId = 'count-cat-risk';
                else if (catKey === 'mentorship') badgeId = 'count-cat-mentor';

                const el = document.getElementById(badgeId);
                if (el) el.innerText = count;
            }}
        }}

        // RENDER DANH SÁCH BÁO CÁO (HỖ TRỢ CẢ GRID VÀ TABLE)
        function renderReports(reports) {{
            const container = document.getElementById('reports-container');
            if (!container) return;

            if (!reports || reports.length === 0) {{
                container.innerHTML = `
                    <div style="text-align: center; padding: 70px 20px; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; color: var(--text-muted);">
                        <div style="font-size: 38px; margin-bottom: 14px;">📂</div>
                        <div style="font-size: 17px; font-weight: 800; color: #fff;">Không tìm thấy báo cáo nào phù hợp với bộ lọc</div>
                        <div style="font-size: 13.5px; margin-top: 8px; color: var(--text-dim);">Chủ tịch có thể bấm nút "Tất Cả" ở trên hoặc chọn ngày khác trong Kho Lưu Trữ.</div>
                    </div>
                `;
                return;
            }}

            if (currentViewMode === 'table') {{
                // RENDER DẠNG BẢNG NHANH (COMPACT TABLE)
                let tableHtml = `
                <div class="reports-table-wrap">
                    <table class="reports-table">
                        <thead>
                            <tr>
                                <th style="width: 100px;">Giờ Gửi</th>
                                <th style="width: 140px;">Phòng Ban</th>
                                <th>Tiêu Đề Báo Cáo Thể Chế</th>
                                <th>Tóm Tắt Nhanh (Key Takeaway)</th>
                                <th style="width: 110px;">Ngày</th>
                                <th style="width: 90px;">Dung Lượng</th>
                                <th style="width: 120px; text-align: center;">Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                reports.forEach(r => {{
                    const deptColor = r.color || '#38bdf8';
                    const timeText = r.time || '--:--';
                    tableHtml += `
                        <tr onclick="openReportModal('${{r.rel_path}}')" style="cursor: pointer;">
                            <td style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #fbbf24;">${{timeText}}</td>
                            <td>
                                <span class="dept-tag" style="background: ${{deptColor}}22; color: ${{deptColor}}; border: 1px solid ${{deptColor}}44;">
                                    ${{r.icon}} ${{r.dept_short}}
                                </span>
                            </td>
                            <td style="font-weight: 700; color: #ffffff;">${{r.title}}</td>
                            <td style="color: #94a3b8; font-size: 12.5px; max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                ${{r.preview || 'Xem toàn văn chi tiết.'}}
                            </td>
                            <td style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-dim);">${{r.date}}</td>
                            <td style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-dim);">${{r.size_kb}} KB</td>
                            <td style="text-align: center;">
                                <button class="btn-read" onclick="event.stopPropagation(); openReportModal('${{r.rel_path}}')" style="padding: 5px 12px; font-size: 11.5px;">
                                    📖 Đọc
                                </button>
                            </td>
                        </tr>
                    `;
                }});
                tableHtml += `
                        </tbody>
                    </table>
                </div>
                `;
                container.innerHTML = tableHtml;
            }} else {{
                // RENDER DẠNG THẺ GRID (VISUAL CARDS)
                let gridHtml = '<div class="reports-grid">';
                reports.forEach(r => {{
                    const deptColor = r.color || '#38bdf8';
                    const timeText = r.time || '--:--';
                    const shiftText = r.shift_label || 'Tác Chiến';

                    gridHtml += `
                        <div class="report-card" onclick="openReportModal('${{r.rel_path}}')">
                            <div>
                                <div class="card-top">
                                    <span class="dept-tag" style="background: ${{deptColor}}22; color: ${{deptColor}}; border: 1px solid ${{deptColor}}44;">
                                        ${{r.icon}} ${{r.dept_short}}
                                    </span>
                                    <div class="report-time-badge">
                                        <strong style="color: #fbbf24;">⏰ ${{timeText}}</strong>
                                        <span style="color: var(--text-dim);">• ${{shiftText}}</span>
                                    </div>
                                </div>
                                <div class="report-title">${{r.title}}</div>
                                <div class="report-snippet">
                                    📌 ${{r.preview || 'Báo cáo chi tiết thể chế đã lưu trữ trong kho dữ liệu Apex.'}}
                                </div>
                            </div>
                            <div class="card-bottom">
                                <span style="color: var(--text-dim); font-family: 'JetBrains Mono', monospace; font-size: 11.5px;">
                                    📅 ${{r.date}} | 📦 ${{r.size_kb}} KB
                                </span>
                                <button class="btn-read" onclick="event.stopPropagation(); openReportModal('${{r.rel_path}}')">
                                    📖 Đọc Toàn Văn
                                </button>
                            </div>
                        </div>
                    `;
                }});
                gridHtml += '</div>';
                container.innerHTML = gridHtml;
            }}
        }}

        // Mở Modal đọc báo cáo toàn văn
        let currentOpenPath = '';
        async function openReportModal(relPath) {{
            currentOpenPath = relPath;
            const modal = document.getElementById('report-modal');
            const contentArea = document.getElementById('modal-content-area');
            const titleEl = document.getElementById('modal-report-title');
            const metaEl = document.getElementById('modal-report-meta');
            const badgeEl = document.getElementById('modal-dept-badge');

            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
            contentArea.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-muted);">⏳ Đang tải toàn văn từ máy chủ đám mây...</div>';

            try {{
                const res = await fetch('/api/report?path=' + encodeURIComponent(relPath));
                const data = await res.json();

                if (!data.ok) {{
                    contentArea.innerHTML = `<div style="color: #ef4444; padding: 20px;">Lỗi tải báo cáo: ${{data.error || 'Không tìm thấy tệp.'}}</div>`;
                    return;
                }}

                titleEl.innerText = data.title || 'Báo cáo chi tiết';
                metaEl.innerText = `Đường dẫn: ${{data.path}} | Kích thước: ${{data.size_kb}} KB | Thời gian cập nhật: ${{data.last_modified}}`;
                
                const meta = allReports.find(r => r.rel_path === relPath);
                if (meta) {{
                    badgeEl.innerText = `${{meta.icon}} ${{meta.dept_name}} [${{meta.shift_label}}]`;
                    badgeEl.style.background = `${{meta.color}}22`;
                    badgeEl.style.color = meta.color;
                    badgeEl.style.borderColor = `${{meta.color}}55`;
                }}

                if (window.marked) {{
                    contentArea.innerHTML = marked.parse(data.content);
                }} else {{
                    contentArea.innerHTML = `<pre style="white-space: pre-wrap;">${{data.content}}</pre>`;
                }}
            }} catch (err) {{
                contentArea.innerHTML = `<div style="color: #ef4444; padding: 20px;">Không thể tải báo cáo từ máy chủ: ${{err.message}}</div>`;
            }}
        }}

        function closeReportModal() {{
            document.getElementById('report-modal').style.display = 'none';
            document.body.style.overflow = 'auto';
        }}

        function closeModalOnOverlay(e) {{
            if (e.target.id === 'report-modal') {{
                closeReportModal();
            }}
        }}

        function printReport() {{
            window.print();
        }}

        function copyReportLink() {{
            const url = window.location.origin + '/?open=' + encodeURIComponent(currentOpenPath);
            navigator.clipboard.writeText(url).then(() => {{
                alert('Đã sao chép liên kết báo cáo: ' + url);
            }}).catch(() => {{
                prompt('Sao chép liên kết báo cáo:', url);
            }});
        }}

        // Tự động kiểm tra URL tham số để mở báo cáo nếu có ?open=
        window.addEventListener('DOMContentLoaded', () => {{
            applyAllFilters();
            const urlParams = new URLSearchParams(window.location.search);
            const openPath = urlParams.get('open');
            if (openPath) {{
                openReportModal(openPath);
            }}
        }});

        // LÀM MỚI DỮ LIỆU
        async function refreshData() {{
            try {{
                const res = await fetch('/api/reports');
                const data = await res.json();
                if (data.ok && data.reports) {{
                    allReports = data.reports;
                    applyAllFilters();
                    alert('Đã làm mới dữ liệu toàn hệ thống thành công (' + allReports.length + ' báo cáo)!');
                }} else {{
                    location.reload();
                }}
            }} catch (err) {{
                location.reload();
            }}
        }}
    </script>
</body>
</html>
"""
