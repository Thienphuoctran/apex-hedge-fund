#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INSTITUTIONAL CLOUD PORTAL ENGINE (BLOOMBERG-GRADE WEB INTERFACE V2.0)
File: scripts/apex_web_portal_engine.py
Cơ quan chủ quản: Palmer — Apex Central System Governance
Phục vụ: Chủ tịch Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)

Nâng cấp Thể chế V2.0:
1. Tách biệt rạch ròi "Báo Cáo Hôm Nay (Today's Live Desk)" vs "Kho Lưu Trữ Lịch Sử (Archive Vault)".
   - Không bao giờ bị đè báo cáo hay ngập tràn trang web khi bước sang ngày mới!
2. Phân loại theo 4 Ca Tác Chiến: Ca Sáng (06h-11h30), Ca Trưa (11h30-13h30), Ca Chiều (13h30-17h), Ca Tối & Đêm (18h-23h30).
3. Ghi rõ ràng GIỜ GỬI BÁO CÁO CHÍNH XÁC (Timestamp) trên từng thẻ.
4. Tích hợp nút In / Xuất PDF và Sao Chép Toàn Văn trong trình đọc Markdown.
"""

import sys
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
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
    uptime_sec = supervisor_data.get("uptime_seconds", 0)
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
            <td style="padding: 12px; font-weight: 600; color: #f8fafc;">{sinfo.get('name', k)}</td>
            <td style="padding: 12px; font-family: monospace; color: #94a3b8;">{sinfo.get('pid', '-')}</td>
            <td style="padding: 12px;">
                <span style="background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}; padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700;">
                    ● {st}
                </span>
            </td>
            <td style="padding: 12px; color: #94a3b8;">{sinfo.get('restart_count', 0)}</td>
            <td style="padding: 12px; color: #94a3b8;">{sinfo.get('uptime_seconds', 0):.0f}s</td>
        </tr>
        """

    # Render danh sách 18 cột mốc
    milestone_rows = ""
    for m in milestones:
        st_color = m["color"]
        milestone_rows += f"""
        <tr>
            <td style="padding: 10px 14px; font-family: monospace; font-weight: bold; color: #38bdf8; font-size: 14px;">{m['time']}</td>
            <td style="padding: 10px 14px; font-size: 18px; text-align: center;">{m['icon']}</td>
            <td style="padding: 10px 14px; font-weight: 600; color: #f1f5f9;">{m['name']}</td>
            <td style="padding: 10px 14px; font-size: 12px; color: #94a3b8;">{m.get('shift', '')}</td>
            <td style="padding: 10px 14px;">
                <span style="background: {st_color}22; color: {st_color}; border: 1px solid {st_color}; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: 700;">
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

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Institutional Cloud Portal — Định Chế Quỹ Đầu Tư 24/7</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {{
            --bg-base: #090d16;
            --bg-surface: #111827;
            --bg-card: #172033;
            --bg-card-hover: #1e293b;
            --border-color: #27354f;
            --primary: #38bdf8;
            --primary-glow: rgba(56, 189, 248, 0.15);
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
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
            padding: 20px;
        }}
        .container {{ max-width: 1320px; margin: 0 auto; }}
        
        /* HEADER */
        .portal-header {{
            background: linear-gradient(135deg, #111827 0%, #172033 100%);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 22px 26px;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
        }}
        .brand-title {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 22px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.02em;
        }}
        .brand-sub {{
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 4px;
        }}
        .header-meta {{
            display: flex;
            align-items: center;
            gap: 14px;
            flex-wrap: wrap;
        }}
        .live-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.05em;
        }}
        .pulse-dot {{
            width: 8px; height: 8px; border-radius: 50%; background: #10b981;
            box-shadow: 0 0 10px #10b981;
            animation: pulse 1.8s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(0.95); opacity: 0.8; }}
            50% {{ transform: scale(1.25); opacity: 1; }}
            100% {{ transform: scale(0.95); opacity: 0.8; }}
        }}

        /* KPI STATS ROW */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }}
        .kpi-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 18px 20px;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, border-color 0.2s;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: #3b82f6;
        }}
        .kpi-card::before {{
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
        }}
        .kpi-lbl {{ font-size: 11px; text-transform: uppercase; color: var(--text-dim); font-weight: 700; letter-spacing: 0.08em; }}
        .kpi-val {{ font-size: 24px; font-weight: 800; margin-top: 6px; }}
        .kpi-sub {{ font-size: 12px; color: var(--text-muted); margin-top: 4px; }}

        /* TABS NAVIGATION */
        .tab-nav {{
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 20px;
            overflow-x: auto;
            padding-bottom: 8px;
        }}
        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 10px 18px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
            transition: all 0.2s;
        }}
        .tab-btn:hover {{
            background: var(--bg-card);
            color: var(--text-main);
        }}
        .tab-btn.active {{
            background: var(--bg-card);
            color: var(--primary);
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}

        .tab-pane {{ display: none; }}
        .tab-pane.active {{ display: block; }}

        /* TIMELINE & ARCHIVE VAULT SWITCHER BAR */
        .archive-vault-bar {{
            background: linear-gradient(135deg, #172033 0%, #1e293b 100%);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 14px 20px;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .date-tabs {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .date-tab-btn {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 7px 14px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .date-tab-btn:hover {{
            color: #fff;
            border-color: var(--primary);
        }}
        .date-tab-btn.active {{
            background: var(--primary);
            color: #090d16;
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(56, 189, 248, 0.3);
        }}
        .archive-select {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 7px 12px;
            border-radius: 8px;
            font-size: 12px;
            outline: none;
            cursor: pointer;
        }}

        /* 4 CA TÁC CHIẾN FILTER */
        .shift-filter-bar {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 10px 16px;
            margin-bottom: 16px;
        }}
        .shift-btn {{
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-muted);
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .shift-btn:hover {{
            background: var(--bg-card);
            color: #fff;
        }}
        .shift-btn.active {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--primary);
            border-color: rgba(56, 189, 248, 0.3);
            font-weight: 700;
        }}

        /* DEPT FILTER & SEARCH BAR */
        .filter-bar {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 12px 18px;
            margin-bottom: 20px;
        }}
        .filter-tags {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}
        .tag-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 5px 12px;
            border-radius: 9999px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .tag-btn:hover, .tag-btn.active {{
            background: var(--primary);
            color: #090d16;
            font-weight: 700;
            border-color: var(--primary);
        }}
        .search-input {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 13px;
            outline: none;
            min-width: 240px;
        }}
        .search-input:focus {{ border-color: var(--primary); }}

        /* REPORT CARDS GRID */
        .reports-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 18px;
        }}
        .report-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 20px;
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
            box-shadow: 0 8px 24px rgba(56, 189, 248, 0.12);
        }}
        .card-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
            gap: 8px;
        }}
        .dept-tag {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 9999px;
            text-transform: uppercase;
        }}
        .report-time-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            padding: 3px 8px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            color: #cbd5e1;
            white-space: nowrap;
        }}
        .report-title {{
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.4;
            margin-bottom: 10px;
        }}
        .report-preview {{
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.5;
            margin-bottom: 16px;
            flex-grow: 1;
        }}
        .card-bottom {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(255,255,255,0.06);
            padding-top: 12px;
            font-size: 12px;
        }}
        .btn-read {{
            background: var(--primary-glow);
            color: var(--primary);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 6px 14px;
            border-radius: 6px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-read:hover {{
            background: var(--primary);
            color: #090d16;
        }}

        /* MODAL REPORT VIEWER */
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(9, 13, 22, 0.88);
            backdrop-filter: blur(8px);
            z-index: 1000;
            padding: 20px;
            overflow-y: auto;
        }}
        .modal-container {{
            max-width: 980px;
            margin: 30px auto;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
            overflow: hidden;
            animation: modalFadeIn 0.2s ease-out;
        }}
        @keyframes modalFadeIn {{
            from {{ opacity: 0; transform: translateY(15px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .modal-header {{
            background: var(--bg-card);
            border-bottom: 1px solid var(--border-color);
            padding: 20px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
        }}
        .modal-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .modal-btn {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .modal-btn:hover {{ background: rgba(255, 255, 255, 0.15); }}
        .modal-close {{
            background: rgba(255, 255, 255, 0.08);
            border: none;
            color: #fff;
            width: 36px; height: 36px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }}
        .modal-close:hover {{ background: rgba(239, 68, 68, 0.3); }}
        .modal-body {{
            padding: 32px 36px;
            line-height: 1.7;
            font-size: 15px;
            color: #e2e8f0;
            max-height: 80vh;
            overflow-y: auto;
        }}

        /* MARKDOWN RENDER STYLING */
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {{
            color: #ffffff;
            margin: 24px 0 12px;
            font-weight: 800;
            letter-spacing: -0.01em;
        }}
        .markdown-body h1 {{ font-size: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; }}
        .markdown-body h2 {{ font-size: 20px; }}
        .markdown-body h3 {{ font-size: 17px; }}
        .markdown-body p {{ margin-bottom: 14px; }}
        .markdown-body ul, .markdown-body ol {{ margin: 0 0 16px 24px; }}
        .markdown-body li {{ margin-bottom: 6px; }}
        .markdown-body table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}
        .markdown-body th {{
            background: #172554;
            color: #38bdf8;
            padding: 12px 14px;
            text-align: left;
            font-weight: 700;
            border: 1px solid var(--border-color);
        }}
        .markdown-body td {{
            padding: 10px 14px;
            border: 1px solid var(--border-color);
        }}
        .markdown-body tr:nth-child(even) {{ background: rgba(255, 255, 255, 0.02); }}
        .markdown-body pre {{
            background: #090d16;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 16px;
            overflow-x: auto;
            margin: 18px 0;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
        }}
        .markdown-body code {{
            font-family: 'JetBrains Mono', monospace;
            background: rgba(56, 189, 248, 0.1);
            color: #38bdf8;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 13px;
        }}
        .markdown-body blockquote {{
            border-left: 4px solid var(--primary);
            background: rgba(56, 189, 248, 0.05);
            padding: 12px 18px;
            border-radius: 0 8px 8px 0;
            margin: 16px 0;
            color: #94a3b8;
        }}

        /* TABLE BASE STYLES FOR STATIC TABS */
        table.standard-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        table.standard-table th {{
            background: var(--bg-base);
            padding: 12px 14px;
            color: var(--text-dim);
            font-weight: 700;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.05em;
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
                    <span>🏛️</span>
                    <span>APEX INSTITUTIONAL CLOUD PORTAL</span>
                </div>
                <div class="brand-sub">
                    Chủ tọa: <strong style="color: #fff;">Chủ tịch Trần Quốc Thiên Phước</strong> | Tài khoản TCBS: <strong style="color: #38bdf8;">105C307855</strong> | Master CIO: <strong style="color: #fff;">James</strong>
                </div>
            </div>
            <div class="header-meta">
                <div class="live-badge">
                    <span class="pulse-dot"></span>
                    <span>CLOUD 24/7 LIVE</span>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #cbd5e1; background: var(--bg-base); padding: 6px 14px; border-radius: 8px; border: 1px solid var(--border-color);" id="live-clock">
                    --:--:--
                </div>
                <button onclick="refreshData()" class="btn-read" style="display: flex; align-items: center; gap: 6px;">
                    <span>🔄</span> <span>Làm Mới</span>
                </button>
            </div>
        </header>

        <!-- KPI STATS -->
        <section class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-lbl">Tài Sản Khả Dụng (Két TCBS)</div>
                <div class="kpi-val" style="color: #34d399;">20,167,119 ₫</div>
                <div class="kpi-sub">100% Tiền Mặt (0 CP Rủi Ro)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-lbl">Lãi Ròng Thực Nhận Vòng 1</div>
                <div class="kpi-val" style="color: #38bdf8;">+167,119 ₫</div>
                <div class="kpi-sub">Đã tất toán 100% HPG, TCB, MBB</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-lbl">Báo Cáo Hôm Nay ({today_str})</div>
                <div class="kpi-val" style="color: #c084fc;" id="stat-today-count">{today_reports_count} Báo Cáo</div>
                <div class="kpi-sub">Tự động chuyển Kho Lưu Trữ qua ngày mới</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-lbl">Tiến Trình Nền Trực Chiến</div>
                <div class="kpi-val" style="color: #f472b6;">{len(services)}/4 Daemons</div>
                <div class="kpi-sub">Watchdog Tự Hồi Phục Bất Tử</div>
            </div>
        </section>

        <!-- TABS NAV -->
        <nav class="tab-nav">
            <button class="tab-btn active" onclick="switchTab('reports')">📑 Thư Viện Báo Cáo Thể Chế</button>
            <button class="tab-btn" onclick="switchTab('timeline')">⏰ 18 Cột Mốc Tác Chiến Ngày</button>
            <button class="tab-btn" onclick="switchTab('portfolio')">📈 Bản Đồ Vốn & Tầm Ngắm Vòng 2</button>
            <button class="tab-btn" onclick="switchTab('supervisor')">🛡️ Giám Sát 4 Daemons 24/7</button>
        </nav>

        <!-- TAB 1: REPORTS FEED -->
        <main id="tab-reports" class="tab-pane active">
            <!-- ARCHIVE VAULT & DATE SELECTOR BAR -->
            <div class="archive-vault-bar">
                <div class="date-tabs">
                    <span style="font-size: 11px; font-weight: 800; color: var(--text-dim); text-transform: uppercase;">Bộ Lọc Ngày:</span>
                    <button class="date-tab-btn active" id="btn-date-today" onclick="selectDateFilter('today')">🌟 Hôm Nay ({today_str})</button>
                    <button class="date-tab-btn" id="btn-date-yesterday" onclick="selectDateFilter('yesterday')">⏮️ Hôm Qua</button>
                    <button class="date-tab-btn" id="btn-date-all" onclick="selectDateFilter('all')">🏛️ Toàn Bộ Lịch Sử</button>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 12px; color: var(--text-muted);">📅 Chọn Ngày Cụ Thể:</span>
                    <select id="archive-date-select" class="archive-select" onchange="selectDateFromDropdown(this.value)">
                        {date_options_html}
                    </select>
                </div>
            </div>

            <!-- 4 CA TÁC CHIẾN FILTER -->
            <div class="shift-filter-bar">
                <span style="font-size: 11px; font-weight: 800; color: var(--text-dim); text-transform: uppercase;">Ca Tác Chiến:</span>
                <button class="shift-btn active" onclick="filterShift('all')">Tất Cả Ca (24h)</button>
                <button class="shift-btn" onclick="filterShift('Ca Sáng')">🌅 Ca Sáng (06h - 11h30)</button>
                <button class="shift-btn" onclick="filterShift('Ca Trưa')">☀️ Ca Trưa (11h30 - 13h30)</button>
                <button class="shift-btn" onclick="filterShift('Ca Chiều')">🎯 Ca Chiều (13h30 - 17h00)</button>
                <button class="shift-btn" onclick="filterShift('Ca Tối')">🌙 Ca Tối & Đêm (18h00 - 23h30)</button>
            </div>

            <!-- DEPT FILTER & SEARCH -->
            <div class="filter-bar">
                <div class="filter-tags" id="dept-filter-tags">
                    <button class="tag-btn active" onclick="filterReports('all')">Tất Cả Phòng Ban</button>
                    <button class="tag-btn" onclick="filterReports('ban_1_macro')">Ban 1: Vĩ Mô</button>
                    <button class="tag-btn" onclick="filterReports('ban_2_vn_equity')">Ban 2: BCTC</button>
                    <button class="tag-btn" onclick="filterReports('ban_3_debates')">Ban 3: Tranh Biện</button>
                    <button class="tag-btn" onclick="filterReports('ban_4_risk')">Ban 4: Rủi Ro</button>
                    <button class="tag-btn" onclick="filterReports('ban_7_vn_specialist')">Ban 7: Minh Quân</button>
                    <button class="tag-btn" onclick="filterReports('ban_8_cio')">Ban 8: James</button>
                    <button class="tag-btn" onclick="filterReports('ban_12_ombudsman')">Ban 12: Trọng</button>
                </div>
                <input type="text" id="report-search" class="search-input" placeholder="🔍 Tìm kiếm mã (FPT, DGC, HPG...)..." oninput="searchReports()">
            </div>

            <div class="reports-grid" id="reports-container">
                <!-- Sẽ được điền bằng JavaScript -->
            </div>
        </main>

        <!-- TAB 2: 18 MILESTONES TIMELINE -->
        <section id="tab-timeline" class="tab-pane">
            <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 14px; overflow: hidden; padding: 20px;">
                <h3 style="font-size: 16px; margin-bottom: 16px; color: #fff;">⏰ BẢNG TIẾN ĐỘ 18 CỘT MỐC TÁC CHIẾN 24H (TỰ ĐỘNG CHẠY ENGINE THẬT)</h3>
                <div style="overflow-x: auto;">
                    <table class="standard-table">
                        <thead>
                            <tr>
                                <th style="width: 100px;">Thời Gian</th>
                                <th style="width: 50px;">Icon</th>
                                <th>Nhiệm Vụ & Phòng Ban Phụ Trách</th>
                                <th style="width: 140px;">Khung Giờ</th>
                                <th style="width: 150px;">Trạng Thái Thực Thi</th>
                            </tr>
                        </thead>
                        <tbody>
                            {milestone_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 3: PORTFOLIO & WATCHLIST -->
        <section id="tab-portfolio" class="tab-pane">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-bottom: 20px;">
                <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 14px; padding: 20px;">
                    <h3 style="font-size: 16px; margin-bottom: 14px; color: #fff;">📊 PHÂN BỔ TÀI SẢN THỰC TẾ (SSOT V2.0)</h3>
                    <div style="margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">
                            <span>Tiền Mặt Khả Dụng (TCInvest)</span>
                            <strong style="color: #34d399;">100% (20,167,119 ₫)</strong>
                        </div>
                        <div style="background: var(--bg-base); height: 12px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border-color);">
                            <div style="background: linear-gradient(90deg, #10b981, #34d399); width: 100%; height: 100%;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">
                            <span>Cổ Phiếu Đang Nắm Giữ</span>
                            <strong style="color: #94a3b8;">0% (0 CP Rủi Ro)</strong>
                        </div>
                        <div style="background: var(--bg-base); height: 12px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border-color);">
                            <div style="background: #ef4444; width: 0%; height: 100%;"></div>
                        </div>
                    </div>
                    <p style="margin-top: 16px; font-size: 12px; color: #94a3b8; line-height: 1.5;">
                        🛡️ <strong>Chế độ Bảo Toàn Vốn:</strong> Quỹ đã thu hồi toàn bộ vốn và lợi nhuận Vòng 1 (+167,119 ₫) về két TCBS. Sẵn sàng 100% sức mua để kích hoạt Vòng 2 trong Khung Giờ Vàng!
                    </p>
                </div>

                <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 14px; padding: 20px;">
                    <h3 style="font-size: 16px; margin-bottom: 14px; color: #fff;">🎯 QUY TẮC ĐI VỐN KIM TỰ THÁP (30% - 40% - 30%)</h3>
                    <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
                        <div>• <strong>Nhịp 1 (30% Thăm dò):</strong> Mua tại nền hỗ trợ khi có nến Test Cung (Vol cạn kiệt).</div>
                        <div>• <strong>Nhịp 2 (40% Gia tăng):</strong> Giải ngân khi giá vượt đỉnh Pivot kèm Vol >= 150% MA20.</div>
                        <div>• <strong>Nhịp 3 (30% Hoàn tất):</strong> Gia tăng khi cổ phiếu Retest đỉnh thành công.</div>
                        <div style="color: #ef4444; margin-top: 8px;">• <strong>Ngưỡng cắt lỗ cứng:</strong> Khóa cứng Stop Loss 2xATR &le; 7.5% NAV.</div>
                    </div>
                </div>
            </div>

            <!-- BẢNG TẦM NGẮM VÒNG 2 -->
            <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 14px; overflow: hidden; padding: 20px;">
                <h3 style="font-size: 16px; margin-bottom: 16px; color: #fff;">⭐ BẢNG PHÂN TÍCH PHÁP Y 5 SIÊU CỔ PHIẾU TẦM NGẮM VÒNG 2</h3>
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
                                <td style="padding: 12px; font-weight: bold; color: #38bdf8;">FPT</td>
                                <td>Công Nghệ FPT</td>
                                <td>15,200 Tỷ</td>
                                <td>2,850 Tỷ</td>
                                <td><span style="color: #34d399; font-weight: bold;">1.35x 🟩</span></td>
                                <td><span style="color: #34d399;">-2.85 (Sạch)</span></td>
                                <td>22.4x</td>
                                <td>134 - 136 (Thăm dò 30%)</td>
                                <td style="color: #f87171;">128 (-5.5%)</td>
                                <td style="color: #34d399;">152 / 165</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; font-weight: bold; color: #38bdf8;">DGC</td>
                                <td>Hóa Chất Đức Giang</td>
                                <td>2,950 Tỷ</td>
                                <td>860 Tỷ</td>
                                <td><span style="color: #34d399; font-weight: bold;">1.18x 🟩</span></td>
                                <td><span style="color: #34d399;">-2.61 (Sạch)</span></td>
                                <td>14.2x</td>
                                <td>112 - 114 (Thăm dò 30%)</td>
                                <td style="color: #f87171;">106 (-6.2%)</td>
                                <td style="color: #34d399;">128 / 138</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; font-weight: bold; color: #38bdf8;">HPG</td>
                                <td>Tập Đoàn Hòa Phát</td>
                                <td>35,800 Tỷ</td>
                                <td>3,200 Tỷ</td>
                                <td><span style="color: #34d399; font-weight: bold;">1.42x 🟩</span></td>
                                <td><span style="color: #34d399;">-2.90 (Sạch)</span></td>
                                <td>12.8x</td>
                                <td>26.5 - 27.0 (Chờ điểm gom)</td>
                                <td style="color: #f87171;">25.2 (-5.8%)</td>
                                <td style="color: #34d399;">31.0 / 34.0</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; font-weight: bold; color: #38bdf8;">TCB</td>
                                <td>Ngân Hàng Techcombank</td>
                                <td>12,400 Tỷ</td>
                                <td>7,100 Tỷ</td>
                                <td><span style="color: #34d399; font-weight: bold;">1.10x 🟩</span></td>
                                <td><span style="color: #34d399;">-2.45 (Sạch)</span></td>
                                <td>6.8x</td>
                                <td>23.0 - 23.5 (Định giá rẻ)</td>
                                <td style="color: #f87171;">21.8 (-6.0%)</td>
                                <td style="color: #34d399;">28.0 / 30.5</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; font-weight: bold; color: #38bdf8;">MBB</td>
                                <td>Ngân Hàng Quân Đội</td>
                                <td>14,100 Tỷ</td>
                                <td>6,500 Tỷ</td>
                                <td><span style="color: #34d399; font-weight: bold;">1.15x 🟩</span></td>
                                <td><span style="color: #34d399;">-2.52 (Sạch)</span></td>
                                <td>5.9x</td>
                                <td>24.5 - 25.0 (Tích lũy)</td>
                                <td style="color: #f87171;">23.2 (-5.5%)</td>
                                <td style="color: #34d399;">28.5 / 31.0</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 4: SUPERVISOR & DAEMONS -->
        <section id="tab-supervisor" class="tab-pane">
            <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 14px; overflow: hidden; padding: 20px;">
                <h3 style="font-size: 16px; margin-bottom: 16px; color: #fff;">🛡️ TRẠNG THÁI 4 TIẾN TRÌNH TỰ HÀNH 24/24 (WATCHDOG AUTO-RECOVERY)</h3>
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
                <div style="margin-top: 20px; font-size: 12px; color: var(--text-dim); display: flex; justify-content: space-between;">
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
                    <h2 id="modal-report-title" style="font-size: 18px; color: #fff; margin-top: 4px;">Tiêu đề báo cáo</h2>
                    <div id="modal-report-meta" style="font-size: 12px; color: var(--text-muted); margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                        Ngày: 2026-11-07 | Dung lượng: 12 KB
                    </div>
                </div>
                <div class="modal-actions">
                    <button class="modal-btn" onclick="printReport()">🖨️ In / PDF</button>
                    <button class="modal-btn" onclick="copyReportLink()">📋 Sao Chép Link</button>
                    <button class="modal-close" onclick="closeReportModal()">✕</button>
                </div>
            </div>
            <div class="modal-body markdown-body" id="modal-content-area">
                <div style="text-align: center; padding: 40px; color: var(--text-muted);">Đang tải toàn văn báo cáo...</div>
            </div>
        </div>
    </div>

    <script>
        // Dữ liệu ban đầu
        let allReports = {initial_reports_json};
        let availableDates = {available_dates_json};
        const todayDateStr = "{today_str}";

        // Trạng thái bộ lọc
        let currentDateFilter = 'today'; // 'today', 'yesterday', 'all', hoặc cụ thể 'YYYY-MM-DD'
        let currentShiftFilter = 'all';  // 'all', 'Ca Sáng', 'Ca Trưa', 'Ca Chiều', 'Ca Tối'
        let currentDeptFilter = 'all';   // 'all', 'ban_1_macro', ...
        let currentSearchQuery = '';

        // Đồng hồ thời gian thực (Giờ Việt Nam)
        function updateLiveClock() {{
            const now = new Date();
            const timeStr = now.toLocaleTimeString('vi-VN', {{ hour12: false }});
            const dateStr = now.toLocaleDateString('vi-VN');
            const el = document.getElementById('live-clock');
            if (el) el.innerText = `${{dateStr}} ${{timeStr}} (ICT)`;
        }}
        setInterval(updateLiveClock, 1000);
        updateLiveClock();

        // Chuyển Tab
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

            const targetBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
            if (targetBtn) targetBtn.classList.add('active');

            const targetPane = document.getElementById('tab-' + tabId);
            if (targetPane) targetPane.classList.add('active');
        }}

        // BỘ LỌC NGÀY & KHO LƯU TRỮ
        function selectDateFilter(mode) {{
            currentDateFilter = mode;
            document.querySelectorAll('.date-tab-btn').forEach(b => b.classList.remove('active'));

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
            document.querySelectorAll('.date-tab-btn').forEach(b => b.classList.remove('active'));
            if (selectedDate === todayDateStr) {{
                document.getElementById('btn-date-today').classList.add('active');
            }}
            applyAllFilters();
        }}

        // BỘ LỌC CA TÁC CHIẾN
        function filterShift(shiftName) {{
            currentShiftFilter = shiftName;
            document.querySelectorAll('.shift-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = Array.from(document.querySelectorAll('.shift-btn')).find(b => b.getAttribute('onclick').includes(shiftName));
            if (activeBtn) activeBtn.classList.add('active');
            applyAllFilters();
        }}

        // BỘ LỌC PHÒNG BAN
        function filterReports(deptId) {{
            currentDeptFilter = deptId;
            document.querySelectorAll('#dept-filter-tags .tag-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = Array.from(document.querySelectorAll('#dept-filter-tags .tag-btn')).find(b => b.getAttribute('onclick').includes(deptId));
            if (activeBtn) activeBtn.classList.add('active');
            applyAllFilters();
        }}

        // TÌM KIẾM
        function searchReports() {{
            currentSearchQuery = (document.getElementById('report-search').value || '').toLowerCase().trim();
            applyAllFilters();
        }}

        // ÁP DỤNG ĐỒNG THỜI CÁC BỘ LỌC
        function applyAllFilters() {{
            let filtered = allReports;

            // 1. Lọc theo Ngày (Tránh đè báo cáo của hôm trước)
            if (currentDateFilter === 'today') {{
                filtered = filtered.filter(r => r.date === todayDateStr);
            }} else if (currentDateFilter === 'yesterday') {{
                // Tìm ngày gần nhất trước hôm nay
                const olderDates = availableDates.map(d => d.date).filter(d => d < todayDateStr);
                const yesterdayDate = olderDates[0] || '';
                if (yesterdayDate) {{
                    filtered = filtered.filter(r => r.date === yesterdayDate);
                }}
            }} else if (currentDateFilter !== 'all') {{
                filtered = filtered.filter(r => r.date === currentDateFilter);
            }}

            // 2. Lọc theo Ca Tác Chiến
            if (currentShiftFilter !== 'all') {{
                filtered = filtered.filter(r => r.shift_label && r.shift_label.includes(currentShiftFilter));
            }}

            // 3. Lọc theo Phòng Ban
            if (currentDeptFilter !== 'all') {{
                filtered = filtered.filter(r => r.dept_id === currentDeptFilter);
            }}

            // 4. Lọc theo Từ Khóa
            if (currentSearchQuery) {{
                filtered = filtered.filter(r => 
                    (r.title && r.title.toLowerCase().includes(currentSearchQuery)) ||
                    (r.preview && r.preview.toLowerCase().includes(currentSearchQuery)) ||
                    (r.file_name && r.file_name.toLowerCase().includes(currentSearchQuery))
                );
            }}

            renderReports(filtered);
        }}

        // Render danh sách báo cáo
        function renderReports(reports) {{
            const container = document.getElementById('reports-container');
            if (!container) return;

            if (!reports || reports.length === 0) {{
                container.innerHTML = `
                    <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 14px; color: var(--text-muted);">
                        <div style="font-size: 32px; margin-bottom: 12px;">📂</div>
                        <div style="font-size: 16px; font-weight: 700; color: #fff;">Không có báo cáo nào trong khung thời gian này</div>
                        <div style="font-size: 13px; margin-top: 6px; color: var(--text-dim);">Chủ tịch có thể chọn "Toàn Bộ Lịch Sử" hoặc chọn ngày khác trong Kho Lưu Trữ ở trên.</div>
                    </div>
                `;
                return;
            }}

            let html = '';
            reports.forEach(r => {{
                const deptColor = r.color || '#38bdf8';
                const timeText = r.time || '--:--';
                const shiftText = r.shift_label || 'Tác Chiến';

                html += `
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
                            <div class="report-preview">${{r.preview || 'Báo cáo chi tiết thể chế đã lưu trữ.'}}</div>
                        </div>
                        <div class="card-bottom">
                            <span style="color: var(--text-dim); font-family: 'JetBrains Mono', monospace; font-size: 11px;">
                                📅 ${{r.date}} | 📦 ${{r.size_kb}} KB
                            </span>
                            <button class="btn-read" onclick="event.stopPropagation(); openReportModal('${{r.rel_path}}')">
                                📖 Đọc Toàn Văn
                            </button>
                        </div>
                    </div>
                `;
            }});
            container.innerHTML = html;
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

                // Render Markdown sang HTML
                if (window.marked) {{
                    contentArea.innerHTML = marked.parse(data.content);
                }} else {{
                    contentArea.innerHTML = `<pre style="white-space: pre-wrap;">${{data.content}}</pre>`;
                }}

                // Cập nhật URL để Chủ tịch có thể chia sẻ hoặc F5
                history.replaceState(null, '', '?view=' + encodeURIComponent(relPath));
            }} catch (err) {{
                contentArea.innerHTML = `<div style="color: #ef4444; padding: 20px;">Lỗi kết nối máy chủ: ${{err.message}}</div>`;
            }}
        }}

        function closeReportModal() {{
            document.getElementById('report-modal').style.display = 'none';
            document.body.style.overflow = 'auto';
            history.replaceState(null, '', window.location.pathname);
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
            const url = window.location.origin + '?view=' + encodeURIComponent(currentOpenPath);
            navigator.clipboard.writeText(url).then(() => {{
                alert('Đã sao chép link báo cáo: ' + url);
            }}).catch(() => {{
                prompt('Link báo cáo:', url);
            }});
        }}

        // Làm mới dữ liệu từ server (Auto polling mỗi 10 giây)
        async function refreshData() {{
            try {{
                const res = await fetch('/api/reports?limit=150');
                if (res.ok) {{
                    allReports = await res.json();
                    const todayCount = allReports.filter(r => r.date === todayDateStr).length;
                    document.getElementById('stat-today-count').innerText = todayCount + ' Báo Cáo';
                    applyAllFilters();
                }}
            }} catch (e) {{
                console.log('Polling reports error:', e);
            }}
        }}

        // Tự động quét cập nhật mỗi 10 giây
        setInterval(refreshData, 10000);

        // Khởi động render danh sách ban đầu (mặc định mở Báo Cáo Hôm Nay)
        applyAllFilters();

        // Kiểm tra xem trên URL có tham số ?view= không để tự động mở báo cáo
        const urlParams = new URLSearchParams(window.location.search);
        const viewParam = urlParams.get('view');
        if (viewParam) {{
            openReportModal(viewParam);
        }}
    </script>
</body>
</html>
"""
    return html
