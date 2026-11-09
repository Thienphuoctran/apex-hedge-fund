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

BASE_DIR = Path(__file__).resolve().parent.parent

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
    try:
        from scripts.apex_tactical_war_room_engine import get_tactical_war_room_state
        wr_state = get_tactical_war_room_state()
    except Exception:
        wr_state = {
            "server_time": datetime.datetime.now().strftime("%H:%M:%S"),
            "phase_info": {"active_phase_id": "NOON_INTERMISSION", "countdown_to_wall_street": "--:--:--"},
            "action_plan": {"current_step": {
                "step_number": 5, "title": "BƯỚC 5: NGHỈ TRƯA, TỔNG KẾT PHIÊN SÁNG & ĐỐI SOÁT KHỐI NGOẠI",
                "time_range": "11:30 - 13:00 (Nghỉ Trưa)",
                "actions": ["1. Giữ nguyên 100% tiền mặt.", "2. Bóc tách dữ liệu giao dịch khớp lệnh phiên sáng."],
                "doctrine_rule": "Khóa cứng kỷ luật bảo toàn vốn."
            }},
            "market_overview": {"vnindex": "1,258.62", "vnindex_change": "+4.25 (+0.34%)", "vn30": "1,324.95", "vn30_change": "+3.80 (+0.29%)", "status": "UPTREND TÍCH LŨY", "foreign_flow": "+52.6 Tỷ (Mua ròng)", "breadth": "242 Tăng / 145 Giảm"},
            "live_stocks": [
                {"symbol": "HDB", "price": "22,450", "change": "+0.45%", "volume": "16.2M", "buy_up_ratio": "54.2%", "status": "AN TOÀN"},
                {"symbol": "MSH", "price": "34,800", "change": "0.00%", "volume": "512k", "buy_up_ratio": "58.6%", "status": "AN TOÀN"}
            ],
            "tactical_message": {"speaker": "Minh Quân (Ban 7 VN)", "content": "Phiên sáng đã khép lại an toàn..."}
        }
    wr_phase_id = wr_state['phase_info']['active_phase_id']
    wr_server_time = wr_state['server_time']
    wr_ny_countdown = wr_state['phase_info']['countdown_to_wall_street']
    wr_step = wr_state['action_plan']['current_step']
    wr_market = wr_state['market_overview']
    wr_stocks = wr_state['live_stocks']
    wr_message = wr_state['tactical_message']

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

    db_milestone_banner = ""
    sqlite_db_file = BASE_DIR / "data" / "apex_institutional_vault.db"
    if sqlite_db_file.exists():
        db_milestone_banner = f'''
        <div style="background: linear-gradient(135deg, #064e3b 0%, #022c22 100%); border: 1px solid #10b981; border-radius: 14px; padding: 14px 22px; margin-bottom: 22px; display: flex; align-items: center; justify-content: space-between; gap: 14px; box-shadow: 0 4px 20px rgba(16, 185, 129, 0.25);">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 26px;">⚡</span>
                <div>
                    <strong style="color: #34d399; font-size: 14.5px;">HẠ TẦNG V5.0: ĐÃ NÂNG CẤP LÊN SQLITE LAKEHOUSE VAULT (SỨC CHỨA 100.000 BÁO CÁO)</strong>
                    <div style="font-size: 12.5px; color: #a7f3d0; margin-top: 3px;">Truy vấn chỉ mục B-Tree &lt; 2ms | Kích hoạt FTS5 Search toàn văn | Bảo tồn 100% tài liệu tiền thật theo lệnh Chủ tịch Phước Trần!</div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; border-radius: 9999px; padding: 6px 14px; font-size: 12px; font-weight: 700;">
                    🟢 SQLITE VAULT ACTIVE
                </span>
            </div>
        </div>
        '''
    elif total_reports_count >= 300:
        db_milestone_banner = f'''
        <div style="background: linear-gradient(135deg, #78350f 0%, #451a03 100%); border: 1px solid #f59e0b; border-radius: 14px; padding: 14px 22px; margin-bottom: 22px; display: flex; align-items: center; justify-content: space-between; gap: 14px; box-shadow: 0 4px 20px rgba(245, 158, 11, 0.25);">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 26px;">⚠️</span>
                <div>
                    <strong style="color: #fbbf24; font-size: 14.5px;">CẢNH BÁO THỂ CHẾ: KHO DỮ LIỆU ĐÃ ĐẠT {total_reports_count} BÁO CÁO (NGƯỠNG 300 - 500)</strong>
                    <div style="font-size: 12.5px; color: #fde68a; margin-top: 3px;">Hệ thống đang tự động kích hoạt Kế hoạch Nâng cấp Cơ sở dữ liệu V5.0 (SQLite / PostgreSQL) theo đúng Chỉ thị của Chủ tịch Phước Trần!</div>
                </div>
            </div>
            <button onclick="switchTab(\'james-command\'); sendQuickCommand(\'Đệ trình kế hoạch nâng cấp Database V5.0\')" class="btn-read" style="background: #f59e0b; color: #070a12; font-weight: 800; white-space: nowrap; padding: 8px 18px;">
                ⚡ Xem Đệ Trình
            </button>
        </div>
        '''

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

        /* INTERACTIVE CHAT REPORT CARD (CLICK TO OPEN REPORT MODAL) */
        .chat-open-report-card {{
            display: flex;
            align-items: center;
            gap: 14px;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.85));
            border: 1.5px solid rgba(56, 189, 248, 0.4);
            box-shadow: 0 4px 20px rgba(56, 189, 248, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 14px 18px;
            margin: 14px 0;
            cursor: pointer;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        .chat-open-report-card:hover {{
            border-color: #38bdf8;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.98), rgba(15, 23, 42, 0.9));
            box-shadow: 0 8px 30px rgba(56, 189, 248, 0.35), 0 0 15px rgba(56, 189, 248, 0.2);
            transform: translateY(-2px);
        }}
        .chat-open-report-icon-box {{
            width: 44px;
            height: 44px;
            border-radius: 10px;
            background: rgba(56, 189, 248, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            flex-shrink: 0;
        }}
        .chat-open-report-body {{
            flex: 1;
            min-width: 0;
        }}
        .chat-open-report-label {{
            font-size: 10.5px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: #38bdf8;
            margin-bottom: 2px;
        }}
        .chat-open-report-name {{
            font-size: 13.5px;
            font-weight: 700;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .chat-open-report-path {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #94a3b8;
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .chat-open-report-btn {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, #0284c7, #0369a1);
            color: #ffffff;
            border: 1px solid #38bdf8;
            padding: 9px 16px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            box-shadow: 0 2px 10px rgba(2, 132, 199, 0.4);
            transition: all 0.2s;
            flex-shrink: 0;
        }}
        .chat-open-report-btn:hover {{
            background: linear-gradient(135deg, #0ea5e9, #0284c7);
            box-shadow: 0 4px 16px rgba(14, 165, 233, 0.6);
            transform: scale(1.02);
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

        /* ========================================================
           TAB 4: PHÒNG HỌP THƯỢNG ĐỈNH TRỰC TUYẾN (APEX WAR ROOM)
           ======================================================== */
        .summit-container {{
            display: flex;
            flex-direction: column;
            gap: 18px;
        }}
        .summit-header-card {{
            background: linear-gradient(135deg, #0b1329 0%, #171d36 50%, #1e1b4b 100%);
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 16px;
            padding: 22px 28px;
            box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
            position: relative;
            overflow: hidden;
        }}
        .summit-header-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #ec4899);
        }}
        .summit-title-box {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .summit-tag-row {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .summit-tag {{
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 3px 10px;
            border-radius: 9999px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}
        .summit-tag-gold {{
            background: rgba(234, 179, 8, 0.15);
            color: #facc15;
            border: 1px solid rgba(234, 179, 8, 0.35);
        }}
        .summit-tag-blue {{
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.35);
        }}
        .summit-tag-inspector {{
            background: rgba(245, 158, 11, 0.18);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.45);
            font-weight: 800;
        }}
        .summit-title {{
            font-size: 20px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .summit-sub {{
            font-size: 12.5px;
            color: var(--text-muted);
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .summit-timer-card {{
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            padding: 14px 20px;
            text-align: center;
            min-width: 220px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }}
        .summit-timer-label {{
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 800;
            color: var(--text-dim);
            letter-spacing: 0.08em;
            margin-bottom: 4px;
        }}
        .summit-timer-val {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 24px;
            font-weight: 800;
            color: #38bdf8;
            letter-spacing: 0.04em;
        }}
        .summit-timer-sub {{
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 3px;
        }}

        /* PHASES TIMELINE STEPPER */
        .summit-phases-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 18px 22px;
        }}
        .summit-phases-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--text-dim);
        }}
        .summit-steps-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 8px;
        }}
        .summit-step-item {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 10px 12px;
            transition: all 0.2s;
            position: relative;
        }}
        .summit-step-item.active {{
            border-color: #38bdf8;
            background: rgba(56, 189, 248, 0.08);
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.25);
        }}
        .summit-step-item.completed {{
            border-color: #10b981;
            background: rgba(16, 185, 129, 0.06);
        }}
        .summit-step-min {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10.5px;
            font-weight: 700;
            color: var(--text-muted);
            margin-bottom: 3px;
        }}
        .summit-step-item.active .summit-step-min {{ color: #38bdf8; }}
        .summit-step-item.completed .summit-step-min {{ color: #34d399; }}
        .summit-step-lbl {{
            font-size: 11.5px;
            font-weight: 700;
            color: #f1f5f9;
            line-height: 1.3;
        }}

        /* SPLIT-VIEW WAR ROOM (70% - 30%) */
        .summit-war-split {{
            display: grid;
            grid-template-columns: 1fr 360px;
            gap: 18px;
            align-items: start;
        }}
        @media (max-width: 1080px) {{
            .summit-war-split {{ grid-template-columns: 1fr; }}
        }}

        /* CỘT TRÁI: LIVE DIALOGUE STREAM */
        .summit-feed-panel {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            min-height: 680px;
        }}
        .summit-feed-header {{
            background: linear-gradient(135deg, #131b2e 0%, #1e293b 100%);
            border-bottom: 1px solid var(--border-color);
            padding: 16px 22px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .summit-feed-body {{
            flex: 1;
            padding: 20px 22px;
            overflow-y: auto;
            max-height: 620px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            background: #090e1a;
            scrollbar-width: thin;
        }}
        .summit-msg-card {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 12px;
            padding: 16px 18px;
            transition: all 0.2s;
            animation: fadeInMsg 0.3s ease;
        }}
        .summit-msg-card:hover {{
            background: rgba(255, 255, 255, 0.04);
            border-color: rgba(255, 255, 255, 0.15);
        }}
        .summit-msg-card.msg-chairman {{
            background: rgba(234, 179, 8, 0.06);
            border-color: rgba(234, 179, 8, 0.35);
            box-shadow: 0 4px 18px rgba(234, 179, 8, 0.1);
        }}
        .summit-msg-card.msg-inspector {{
            background: rgba(245, 158, 11, 0.06);
            border-color: rgba(245, 158, 11, 0.35);
        }}
        .summit-msg-card.msg-debate {{
            background: rgba(239, 68, 68, 0.06);
            border-color: rgba(239, 68, 68, 0.45);
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.08);
        }}
        .summit-msg-card.msg-forensic {{
            background: rgba(236, 72, 153, 0.06);
            border-color: rgba(236, 72, 153, 0.35);
        }}
        .summit-msg-card.msg-quant {{
            background: rgba(16, 185, 129, 0.06);
            border-color: rgba(16, 185, 129, 0.35);
        }}
        .summit-msg-card.msg-tactical {{
            background: rgba(249, 115, 22, 0.06);
            border-color: rgba(249, 115, 22, 0.4);
            box-shadow: 0 2px 14px rgba(249, 115, 22, 0.12);
        }}
        @keyframes fadeInMsg {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .summit-msg-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .summit-msg-author {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .summit-msg-avatar {{
            font-size: 20px;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.06);
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .summit-msg-name {{
            font-weight: 800;
            color: #f8fafc;
            font-size: 13.5px;
        }}
        .summit-msg-dept {{
            font-size: 11px;
            color: var(--text-muted);
        }}
        .summit-msg-time {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--text-dim);
        }}
        .summit-msg-content {{
            font-size: 13.5px;
            line-height: 1.6;
            color: #e2e8f0;
            white-space: pre-wrap;
        }}
        .summit-msg-highlight {{
            margin-top: 10px;
            padding: 8px 12px;
            background: rgba(56, 189, 248, 0.08);
            border-left: 3px solid #38bdf8;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            color: #7dd3fc;
        }}

        /* LIVE EVIDENCE DATA CARDS (BƯỚC 2) */
        .summit-evidence-box {{
            margin-top: 12px;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 8px;
            overflow: hidden;
            font-size: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            transition: all 0.2s ease;
        }}
        .summit-evidence-box:hover {{
            border-color: rgba(56, 189, 248, 0.55);
            box-shadow: 0 6px 24px rgba(56, 189, 248, 0.12);
        }}
        .summit-evidence-toggle-btn {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(90deg, rgba(56, 189, 248, 0.12) 0%, rgba(30, 58, 138, 0.15) 100%);
            padding: 9px 14px;
            cursor: pointer;
            border-bottom: 1px solid rgba(56, 189, 248, 0.2);
            user-select: none;
        }}
        .summit-evidence-title {{
            font-weight: 800;
            color: #38bdf8;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 11.5px;
            letter-spacing: 0.5px;
        }}
        .summit-evidence-content {{
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .evidence-peer-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
            margin-top: 4px;
        }}
        .evidence-peer-table th {{
            background: rgba(255, 255, 255, 0.05);
            color: #94a3b8;
            font-weight: 700;
            padding: 6px 8px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            font-family: 'JetBrains Mono', monospace;
            font-size: 10.5px;
            text-transform: uppercase;
        }}
        .evidence-peer-table td {{
            padding: 7px 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            color: #cbd5e1;
        }}
        .evidence-check-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 8px;
            margin-top: 4px;
        }}
        .evidence-check-item {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 6px;
            padding: 7px 10px;
        }}
        .evidence-check-k {{
            font-size: 10px;
            color: #94a3b8;
            text-transform: uppercase;
            font-weight: 700;
        }}
        .evidence-check-v {{
            font-size: 11px;
            color: #34d399;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 2px;
        }}

        /* CHAIRMAN DIRECT INPUT BAR */
        .summit-input-panel {{
            background: var(--bg-surface);
            border-top: 1px solid var(--border-color);
            padding: 16px 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .summit-input-label {{
            font-size: 11px;
            font-weight: 800;
            color: #facc15;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .summit-input-row {{
            display: flex;
            gap: 10px;
        }}
        .summit-input-field {{
            flex: 1;
            background: var(--bg-base);
            border: 1px solid rgba(234, 179, 8, 0.35);
            border-radius: 10px;
            color: #fff;
            padding: 12px 16px;
            font-size: 13.5px;
            font-family: inherit;
            outline: none;
            transition: border-color 0.2s;
        }}
        .summit-input-field:focus {{
            border-color: #facc15;
            box-shadow: 0 0 12px rgba(234, 179, 8, 0.25);
        }}
        .summit-btn-send {{
            background: linear-gradient(135deg, #eab308 0%, #ca8a04 100%);
            color: #070a12;
            font-weight: 800;
            font-size: 13px;
            padding: 12px 22px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }}
        .summit-btn-send:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(234, 179, 8, 0.35);
        }}

        /* CỘT PHẢI: BÀN KIỂM SÁT TRỌNG & BIỂU QUYẾT */
        .summit-side-col {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .summit-side-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 18px 20px;
            position: relative;
        }}
        .summit-side-title {{
            font-size: 13px;
            font-weight: 800;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 14px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .inspector-rule-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 12px;
        }}
        .inspector-rule-item:last-child {{ border-bottom: none; }}
        .inspector-rule-text {{ color: var(--text-muted); }}
        .inspector-rule-badge {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 10.5px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
        }}
        .summit-stock-vote-card {{
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 10px;
        }}
        .summit-stock-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }}
        .summit-stock-sym {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 15px;
            font-weight: 800;
            color: #38bdf8;
        }}
        .summit-vote-tally {{
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 800;
        }}
        .summit-stock-meta {{
            font-size: 11.5px;
            color: var(--text-muted);
            line-height: 1.4;
        }}
        .summit-action-btn-large {{
            width: 100%;
            background: linear-gradient(135deg, #1e1b4b 0%, #1e293b 100%);
            border: 1px solid #38bdf8;
            color: #38bdf8;
            padding: 12px 16px;
            border-radius: 10px;
            font-size: 12.5px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        .summit-action-btn-large:hover {{
            background: #38bdf8;
            color: #070a12;
            box-shadow: 0 4px 18px rgba(56, 189, 248, 0.35);
        }}
        .summit-action-btn-gold {{
            width: 100%;
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: #0f172a;
            font-weight: 800;
            font-size: 11.5px;
            padding: 11px 14px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            box-shadow: 0 4px 18px rgba(245, 158, 11, 0.35);
            transition: all 0.2s;
            text-transform: uppercase;
        }}
        .summit-action-btn-gold:hover {{
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(245, 158, 11, 0.5);
        }}
        .summit-action-btn-gold:disabled {{
            opacity: 0.65;
            cursor: not-allowed;
            transform: none;
        }}

    
        /* ========================================================
           TAB 3: PHÒNG TÁC CHIẾN ĐẦU TƯ TRONG NGÀY (WAR-ROOM) CSS
           ======================================================== */
        .war-room-wrap {{
            display: flex;
            flex-direction: column;
            gap: 18px;
            padding-bottom: 40px;
        }}

        /* Header Ribbon */
        .war-room-ribbon {{
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9));
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}
        .war-room-ribbon-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .war-room-title-box {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .war-room-live-pulse {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.5);
            border-radius: 999px;
            font-size: 11px;
            font-weight: 800;
            color: #f87171;
            letter-spacing: 0.5px;
        }}
        .war-room-live-dot {{
            width: 8px;
            height: 8px;
            background: #ef4444;
            border-radius: 50%;
            animation: pulse-dot 1.5s infinite;
        }}
        @keyframes pulse-dot {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.4); opacity: 0.4; }}
        }}
        .war-room-title {{
            font-size: 17px;
            font-weight: 800;
            color: #f8fafc;
            letter-spacing: 0.3px;
        }}
        .war-room-subtitle {{
            font-size: 12px;
            color: #94a3b8;
            margin-top: 2px;
        }}
        .war-room-meta-group {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .meta-pill {{
            display: flex;
            align-items: center;
            gap: 6px;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(148, 163, 184, 0.2);
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 11.5px;
            color: #e2e8f0;
        }}
        .meta-pill strong {{
            color: #38bdf8;
        }}

        /* 8-Phase Market Progress Bar */
        .phase-stepper-wrap {{
            display: flex;
            align-items: stretch;
            gap: 6px;
            overflow-x: auto;
            padding: 4px 0;
        }}
        .phase-step-card {{
            flex: 1;
            min-width: 125px;
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 8px;
            padding: 8px 10px;
            display: flex;
            flex-direction: column;
            gap: 3px;
            transition: all 0.25s ease;
        }}
        .phase-step-card.active {{
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.25), rgba(30, 41, 59, 0.95));
            border-color: #38bdf8;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.35);
            transform: translateY(-2px);
        }}
        .phase-step-card.completed {{
            border-color: rgba(16, 185, 129, 0.35);
            background: rgba(16, 185, 129, 0.08);
        }}
        .phase-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 10px;
            font-weight: 700;
            color: #94a3b8;
        }}
        .phase-step-card.active .phase-card-header {{
            color: #38bdf8;
        }}
        .phase-card-name {{
            font-size: 11.5px;
            font-weight: 800;
            color: #f1f5f9;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .phase-card-time {{
            font-size: 10.5px;
            color: #64748b;
        }}
        .phase-step-card.active .phase-card-time {{
            color: #7dd3fc;
            font-weight: 700;
        }}

        /* 3-Column Tactical Layout */
        .war-room-columns {{
            display: grid;
            grid-template-columns: 32% 40% 28%;
            gap: 18px;
        }}
        @media (max-width: 1250px) {{
            .war-room-columns {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Common Card Style */
        .tactical-panel {{
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        }}
        .panel-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(148, 163, 184, 0.15);
            padding-bottom: 10px;
        }}
        .panel-title-box {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .panel-icon {{
            font-size: 18px;
        }}
        .panel-title {{
            font-size: 14.5px;
            font-weight: 800;
            color: #f8fafc;
        }}
        .panel-badge {{
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
        }}

        /* Stock Cards */
        .stock-pick-card {{
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 9px;
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            gap: 9px;
            transition: all 0.2s ease;
        }}
        .stock-pick-card:hover {{
            border-color: #38bdf8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
        }}
        .stock-pick-card.leader {{
            border-left: 4px solid #10b981;
        }}
        .stock-pick-card.alpha {{
            border-left: 4px solid #38bdf8;
        }}
        .stock-pick-card.standby {{
            border-left: 4px solid #64748b;
            opacity: 0.85;
        }}
        .stock-card-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .stock-ticker {{
            font-size: 15px;
            font-weight: 900;
            color: #f8fafc;
            letter-spacing: 0.5px;
        }}
        .stock-name {{
            font-size: 11px;
            color: #94a3b8;
            margin-left: 6px;
        }}
        .stock-stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
            background: rgba(15, 23, 42, 0.6);
            padding: 7px;
            border-radius: 6px;
            border: 1px solid rgba(148, 163, 184, 0.1);
        }}
        .stock-stat-item {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .stat-label {{
            font-size: 9.5px;
            color: #64748b;
            text-transform: uppercase;
        }}
        .stat-val {{
            font-size: 12px;
            font-weight: 800;
            color: #f1f5f9;
        }}
        .stat-val.gain {{
            color: #34d399;
        }}
        .stat-val.loss {{
            color: #f87171;
        }}
        .stat-val.gold {{
            color: #fbbf24;
        }}
        .stock-catalyst {{
            font-size: 11px;
            color: #cbd5e1;
            line-height: 1.4;
            background: rgba(30, 41, 59, 0.4);
            padding: 6px 9px;
            border-radius: 6px;
        }}

        /* Directive Stream & Chat Box */
        .directive-hero-box {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(15, 23, 42, 0.9));
            border: 1px solid rgba(52, 211, 153, 0.4);
            border-radius: 9px;
            padding: 12px 14px;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }}
        .directive-hero-text {{
            font-size: 12px;
            color: #e2e8f0;
            line-height: 1.5;
        }}

        /* Timeline in Column 2 */
        .tactical-milestones-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-height: 320px;
            overflow-y: auto;
            padding-right: 4px;
        }}
        .milestone-card {{
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 8px;
            padding: 9px 12px;
            display: flex;
            flex-direction: column;
            gap: 3px;
            transition: all 0.2s ease;
        }}
        .milestone-card.active {{
            border-color: #38bdf8;
            background: rgba(56, 189, 248, 0.1);
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
        }}
        .milestone-card.completed {{
            border-color: rgba(16, 185, 129, 0.3);
            background: rgba(16, 185, 129, 0.05);
        }}
        .milestone-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .milestone-time {{
            font-size: 11px;
            font-weight: 800;
            color: #38bdf8;
        }}
        .milestone-badge {{
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .milestone-title {{
            font-size: 12px;
            font-weight: 700;
            color: #f8fafc;
        }}
        .milestone-desc {{
            font-size: 11px;
            color: #94a3b8;
            line-height: 1.35;
        }}

        /* Interactive Directive Box */
        .tactical-interactive-card {{
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 10px;
            padding: 13px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .directive-history-box {{
            max-height: 240px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 9px;
            padding-right: 4px;
        }}
        .directive-msg {{
            padding: 9px 11px;
            border-radius: 7px;
            font-size: 11.5px;
            line-height: 1.45;
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}
        .directive-msg.chairman {{
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.4);
            border-left: 3px solid #f59e0b;
        }}
        .directive-msg.specialist {{
            background: rgba(14, 165, 233, 0.12);
            border: 1px solid rgba(14, 165, 233, 0.4);
            border-left: 3px solid #38bdf8;
        }}
        .directive-msg.sentinel {{
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-left: 3px solid #10b981;
        }}
        .directive-msg-head {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 10.5px;
            font-weight: 800;
        }}
        .directive-msg.chairman .directive-msg-head {{ color: #fbbf24; }}
        .directive-msg.specialist .directive-msg-head {{ color: #38bdf8; }}
        .directive-msg.sentinel .directive-msg-head {{ color: #34d399; }}
        .directive-msg-body {{
            color: #e2e8f0;
        }}
        .quick-prompts-row {{
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }}
        .btn-quick-prompt {{
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.25);
            color: #cbd5e1;
            padding: 4px 9px;
            border-radius: 5px;
            font-size: 10.5px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .btn-quick-prompt:hover {{
            background: rgba(56, 189, 248, 0.2);
            border-color: #38bdf8;
            color: #f8fafc;
        }}
        .directive-input-row {{
            display: flex;
            gap: 8px;
        }}
        .directive-input {{
            flex: 1;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 6px;
            padding: 8px 12px;
            color: #f8fafc;
            font-size: 11.5px;
            outline: none;
        }}
        .directive-input:focus {{
            border-color: #38bdf8;
            box-shadow: 0 0 8px rgba(56, 189, 248, 0.3);
        }}
        .btn-send-directive {{
            background: linear-gradient(135deg, #0284c7, #0369a1);
            border: none;
            color: #ffffff;
            font-weight: 800;
            font-size: 11.5px;
            padding: 8px 14px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }}
        .btn-send-directive:hover {{
            background: linear-gradient(135deg, #0ea5e9, #0284c7);
            box-shadow: 0 0 12px rgba(14, 165, 233, 0.4);
        }}

    
        /* Action Plan Card & Live Stock Sentinel Table */
        .action-plan-hero-card {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 10px;
            padding: 14px 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        }}
        .action-plan-tag {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.4);
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 800;
        }}
        .action-plan-step-title {{
            font-size: 13.5px;
            font-weight: 800;
            color: #38bdf8;
            letter-spacing: 0.2px;
        }}
        .action-plan-content {{
            font-size: 12px;
            color: #f1f5f9;
            line-height: 1.5;
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 8px;
            padding: 10px 12px;
        }}
        .action-plan-rule {{
            font-size: 11px;
            color: #cbd5e1;
            font-style: italic;
            border-left: 3px solid #f59e0b;
            padding-left: 8px;
        }}

        /* Market Radar Overview Card */
        .market-radar-card {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 10px;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .index-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }}
        .index-item {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 7px;
            padding: 8px 10px;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}

        /* Live Stock Ticker Sentinel Table */
        .stock-sentinel-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 11px;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.2);
        }}
        .stock-sentinel-table th {{
            background: rgba(30, 41, 59, 0.9);
            color: #94a3b8;
            font-weight: 700;
            padding: 7px 8px;
            text-align: left;
            border-bottom: 1px solid rgba(148, 163, 184, 0.2);
            font-size: 10px;
            text-transform: uppercase;
        }}
        .stock-sentinel-table td {{
            background: rgba(15, 23, 42, 0.6);
            color: #f1f5f9;
            padding: 7px 8px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }}
        .stock-sentinel-table tr:hover td {{
            background: rgba(56, 189, 248, 0.1);
        }}
        .price-badge {{
            font-weight: 800;
            font-size: 11.5px;
        }}
        .price-badge.up {{ color: #34d399; }}
        .price-badge.down {{ color: #f87171; }}
        .price-badge.ref {{ color: #fbbf24; }}

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
                <div class="kpi-val" id="top-kpi-cash-val" style="color: #34d399;">14,510,422 ₫</div>
                <div class="kpi-sub" id="top-kpi-cash-sub"><span style="color: #34d399; font-weight: 700;">72.0% Cash</span> • 200 CP (5,650,000 ₫ • 28.0% NAV)</div>
            </div>
            <div class="kpi-card" style="--card-accent: #38bdf8;">
                <div class="kpi-lbl">📈 Lãi Ròng Thu Về Vòng 1</div>
                <div class="kpi-val" style="color: #38bdf8;">+167,119 ₫</div>
                <div class="kpi-sub">Đã tất toán 100% (HPG, TCB, MBB)</div>
            </div>
            <div class="kpi-card" style="--card-accent: #c084fc;">
                <div class="kpi-lbl">📑 Báo Cáo Hôm Nay ({today_str})</div>
                <div class="kpi-val" style="color: #c084fc;" id="stat-today-count">{today_reports_count} Báo Cáo</div>
                <div class="kpi-sub">Kho Vault: <strong style="color: #10b981;">{total_reports_count} Báo Cáo</strong> (SQLite V5.0: Sức chứa 100.000)</div>
            </div>
            <div class="kpi-card" style="--card-accent: #f472b6;">
                <div class="kpi-lbl">🛡️ Hệ Thống Tự Hành 24/7</div>
                <div class="kpi-val" style="color: #f472b6;">{len(services)}/4 Daemons</div>
                <div class="kpi-sub">Watchdog Tự Hồi Phục Bất Tử</div>
            </div>
        </section>

        {db_milestone_banner}
        <!-- TABS NAV -->
        <nav class="tab-nav">
            <button class="tab-btn active" onclick="switchTab('reports')">
                <span>📑</span> <span>1. Thư Viện Báo Cáo 18 Cột Mốc</span>
                <span class="tab-badge" id="nav-total-count">{total_reports_count}</span>
            </button>
            <button class="tab-btn" onclick="switchTab('portfolio')">
                <span>🎯</span> <span>2. Tầm Ngắm Vòng 2 & TradingView</span>
            </button>
            <button class="tab-btn" id="btn-tab-war-room" onclick="switchTab('war-room')">
                <span>⚡</span> <span>3. Phòng Tác Chiến Trong Ngày (Minh Quân & Victor)</span>
                <span class="live-badge" style="background: rgba(239, 68, 68, 0.25); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.5); padding: 2px 8px; font-size: 10.5px; margin-left: 4px; border-radius: 9999px; animation: pulse 2s infinite;">● TRỰC CHIẾN LIVE</span>
            </button>
            <button class="tab-btn" onclick="switchTab('james-command')">
                <span>🎖️</span> <span>4. Bàn Chỉ Huy Master CIO James</span>
            </button>
            <button class="tab-btn" id="btn-tab-summit" onclick="switchTab('summit-room')">
                <span>🏛️</span> <span>5. Phòng Họp Thượng Đỉnh Trực Tuyến</span>
                <span class="live-badge" id="summit-nav-badge" style="padding: 2px 8px; font-size: 10.5px; margin-left: 4px; border-radius: 9999px;">● LIVE 21H00</span>
            </button>
            <button class="tab-btn" onclick="switchTab('timeline')">
                <span>⏰</span> <span>6. Tiến Độ 18 Cột Mốc Ngày</span>
            </button>
            <button class="tab-btn" onclick="switchTab('supervisor')">
                <span>🛡️</span> <span>7. Giám Sát Cụm Container 24/7</span>
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
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:HDB', this)">🏦 HDB (Mũi Nhọn 1)</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:MSH', this)">🧵 MSH (Mũi Nhọn 2)</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:BAF', this)">🐷 BAF (Dự phòng)</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HNX:IDC', this)">🏗️ IDC (Dự phòng)</button>
                        <button class="tv-btn" onclick="switchTVSymbol('HOSE:PVT', this)">🚢 PVT (Radar Tuần)</button>
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
                            <strong style="color: #34d399; font-family: 'JetBrains Mono', monospace;">72.0% (14,510,422 ₫)</strong>
                        </div>
                        <div style="background: var(--bg-base); height: 12px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border-color);">
                            <div style="background: linear-gradient(90deg, #10b981, #34d399); width: 72%; height: 100%;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 13.5px; margin-bottom: 8px;">
                            <span>Cổ Phiếu Đang Nắm Giữ</span>
                            <strong style="color: #38bdf8; font-family: 'JetBrains Mono', monospace;">28.0% (5,650,000 ₫ • 200 CP)</strong>
                        </div>
                        <div style="background: var(--bg-base); height: 12px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border-color);">
                            <div style="background: linear-gradient(90deg, #0ea5e9, #38bdf8); width: 28%; height: 100%;"></div>
                        </div>
                    </div>
                    <p style="margin-top: 18px; font-size: 12.5px; color: #94a3b8; line-height: 1.6;">
                        🛡️ <strong>Chế độ Bảo Vệ Vị Thế:</strong> Quỹ đã giải ngân Nhịp 1 thành công (100 CP HDB & 100 CP MSH). Tiền mặt khả dụng 14,510,422 ₫ (72.0% NAV) bảo toàn an toàn trong két. Victor đã kích hoạt ngay hàng rào phòng thủ Stop 2xATR!
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

            <!-- SỔ LỆNH THỰC THI & KẾ HOẠCH TÁC CHIẾN CHUẨN CHỈ (NGÀY 09/11/2026) -->
            <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; padding: 24px; margin-bottom: 22px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 14px;">
                    <div>
                        <h3 style="font-size: 17px; color: #fff; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                            <span>🎯</span> <span>BẢNG KẾ HOẠCH ĐẦU TƯ CHUẨN CHỈ: PHÂN TÁCH 3 NHỊP KIM TỰ THÁP (30% - 40% - 30%)</span>
                        </h3>
                        <p style="font-size: 12.5px; color: #94a3b8; margin-top: 4px;">
                            Tài khoản TCBS <strong style="color: #38bdf8;">105C307855</strong> (Chủ tịch: <strong>Trần Quốc Thiên Phước</strong>) • Tài sản ròng NAV: <strong style="color: #34d399;">20,160,386 ₫</strong> (Tiền mặt: 14,510,422 ₫ • Cổ phiếu: 5,650,000 ₫)
                        </p>
                    </div>
                    <div>
                        <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); padding: 5px 12px; border-radius: 9999px; font-size: 11.5px; font-weight: 800;">
                            ● DUY NHẤT NHỊP 1 HÔM NAY (14h00 – 14h25)
                        </span>
                    </div>
                </div>

                <!-- PHẦN 1: TOP 2 MÃ GIẢI NGÂN NHỊP 1 HÔM NAY -->
                <div style="margin-bottom: 20px;">
                    <div style="font-size: 12px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
                        <span>🔥</span> <span>PHẦN 1: LỆNH THỰC THI NHỊP 1 THĂM DÒ HÔM NAY (KHUNG GIỜ VÀNG 14h00 – 14h25)</span>
                    </div>
                    <div style="overflow-x: auto;">
                        <table class="standard-table">
                            <thead>
                                <tr>
                                    <th>Mã</th>
                                    <th>Sàn / Ngành</th>
                                    <th>Thị Giá Phiên Sáng</th>
                                    <th>Lệnh Khung Giờ Vàng (14h00 - 14h25)</th>
                                    <th>Vốn Giải Ngân Hôm Nay</th>
                                    <th>Nhịp 2 (Breakout)</th>
                                    <th>Nhịp 3 (Retest)</th>
                                    <th>Tổng Target Cap</th>
                                    <th>Cắt Lỗ Stop 2xATR</th>
                                    <th>Chốt Lời TP1 / TP2</th>
                                    <th>EV% & R:R</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="background: rgba(56, 189, 248, 0.04);">
                                    <td style="padding: 12px 14px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono', monospace; font-size: 15px;">HDB</td>
                                    <td style="padding: 12px 14px; font-weight: 600;">HOSE • Ngân Hàng TMCP</td>
                                    <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace;">22,300 – 22,450 đ</td>
                                    <td style="padding: 12px 14px; color: #34d399; font-weight: 700;">
                                        <strong>100 CP (Lô chẵn 100)</strong><br/>
                                        <span style="font-size: 11px; color: #94a3b8;">Đặt LO: 22,300 – 22,450 đ</span>
                                    </td>
                                    <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace; font-weight: 800; color: #34d399;">
                                        ~2,230,000 – 2,245,000 ₫<br/>
                                        <span style="font-size: 11px; color: #94a3b8;">(~11.1% NAV)</span>
                                    </td>
                                    <td style="padding: 12px 14px; font-size: 12px; color: #cbd5e1;">+100 CP (Vượt 22,820 đ Vol +50%)</td>
                                    <td style="padding: 12px 14px; font-size: 12px; color: #cbd5e1;">+100 CP (Retest nền 22,500 đ)</td>
                                    <td style="padding: 12px 14px; font-weight: 700; color: #fbbf24;">300 CP (6.75M - 33.5% NAV)</td>
                                    <td style="padding: 12px 14px; color: #f87171; font-weight: 700;">21,220 đ (-5.69%)</td>
                                    <td style="padding: 12px 14px; color: #34d399; font-weight: 700;">24,290 / 25,820 đ</td>
                                    <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace; font-size: 12px;">+8.8% (1:2.59)</td>
                                </tr>
                                <tr style="background: rgba(56, 189, 248, 0.04);">
                                    <td style="padding: 12px 14px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono', monospace; font-size: 15px;">MSH</td>
                                    <td style="padding: 12px 14px; font-weight: 600;">HOSE • Dệt May Xuất Khẩu</td>
                                    <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace;">34,600 – 35,000 đ</td>
                                    <td style="padding: 12px 14px; color: #34d399; font-weight: 700;">
                                        <strong>100 CP (Lô chẵn 100)</strong><br/>
                                        <span style="font-size: 11px; color: #94a3b8;">Đặt LO: 34,600 – 35,000 đ</span>
                                    </td>
                                    <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace; font-weight: 800; color: #34d399;">
                                        ~3,460,000 – 3,500,000 ₫<br/>
                                        <span style="font-size: 11px; color: #94a3b8;">(~17.2% NAV)</span>
                                    </td>
                                    <td style="padding: 12px 14px; font-size: 12px; color: #cbd5e1;">+100 CP (Vượt 36,220 đ Vol lớn)</td>
                                    <td style="padding: 12px 14px; font-size: 12px; color: #cbd5e1;">0 CP (Đã đủ 200 CP)</td>
                                    <td style="padding: 12px 14px; font-weight: 700; color: #fbbf24;">200 CP (7.10M - 35.2% NAV)</td>
                                    <td style="padding: 12px 14px; color: #f87171; font-weight: 700;">33,090 đ (-6.79%)</td>
                                    <td style="padding: 12px 14px; color: #34d399; font-weight: 700;">39,560 / 43,040 đ</td>
                                    <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace; font-size: 12px;">+13.1% (1:3.13)</td>
                                </tr>
                                <tr style="background: rgba(16, 185, 129, 0.08); font-weight: 800;">
                                    <td colspan="4" style="padding: 12px 14px; color: #34d399; text-align: right;">TỔNG GIẢI NGÂN NHỊP 1 HÔM NAY (2 LÔ 100 CP):</td>
                                    <td colspan="2" style="padding: 12px 14px; color: #34d399; font-family: 'JetBrains Mono', monospace; font-size: 14px;">~5,690,000 ₫ (~28.2% NAV)</td>
                                    <td colspan="5" style="padding: 12px 14px; color: #38bdf8;">KÉT TIỀN MẶT GIỮ LẠI: 14,477,119 ₫ (71.8% NAV BẢO VỆ AN TOÀN)</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- PHẦN 2: DANH MỤC DỰ PHÒNG & THEO DÕI VĨ MÔ -->
                <div style="margin-bottom: 20px;">
                    <div style="font-size: 12px; font-weight: 800; color: #fbbf24; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
                        <span>🛡️</span> <span>PHẦN 2: DANH MỤC DỰ PHÒNG & THEO DÕI CHIẾN LƯỢC (STANDBY WATCHLIST — CHƯA KÍCH HOẠT HÔM NAY)</span>
                    </div>
                    <div style="overflow-x: auto;">
                        <table class="standard-table">
                            <thead>
                                <tr>
                                    <th>Mã</th>
                                    <th>Sàn / Ngành</th>
                                    <th>Thị Giá</th>
                                    <th>Trạng Thái Chiến Lược Hôm Nay</th>
                                    <th>Lý Do Tạm Giữ Ở Trạng Thái Chờ</th>
                                    <th>Cột Mốc Kích Hoạt Dự Kiến</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td style="padding: 10px 14px; font-weight: 800; color: #fbbf24; font-family: 'JetBrains Mono', monospace;">BAF</td>
                                    <td style="padding: 10px 14px;">HOSE • Nông nghiệp 3F</td>
                                    <td style="padding: 10px 14px; font-family: 'JetBrains Mono', monospace;">30,800 đ</td>
                                    <td style="padding: 10px 14px;"><span style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">STANDBY (0 CP)</span></td>
                                    <td style="padding: 10px 14px; font-size: 12px; color: #94a3b8;">Nội tại cực khỏe (RS 96) nhưng ưu tiên tối đa vốn cho Top 2 (HDB & MSH) để không loãng danh mục.</td>
                                    <td style="padding: 10px 14px; font-size: 12px; color: #cbd5e1;">Kích hoạt khi HDB/MSH chốt lời TP1 thu hồi vốn.</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 14px; font-weight: 800; color: #fbbf24; font-family: 'JetBrains Mono', monospace;">IDC</td>
                                    <td style="padding: 10px 14px;">HNX • BĐS Khu Công Nghiệp</td>
                                    <td style="padding: 10px 14px; font-family: 'JetBrains Mono', monospace;">34,900 đ</td>
                                    <td style="padding: 10px 14px;"><span style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">STANDBY (0 CP)</span></td>
                                    <td style="padding: 10px 14px; font-size: 12px; color: #94a3b8;">Sàn HNX biên độ 10%, cổ tức tiền 40%, chờ dòng tiền FDI và khu công nghiệp bứt phá.</td>
                                    <td style="padding: 10px 14px; font-size: 12px; color: #cbd5e1;">Kích hoạt tại Nhịp 2 khi vượt cản 35,570 đ.</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 14px; font-weight: 800; color: #fbbf24; font-family: 'JetBrains Mono', monospace;">PVT</td>
                                    <td style="padding: 10px 14px;">HOSE • Vận tải Dầu khí</td>
                                    <td style="padding: 10px 14px; font-family: 'JetBrains Mono', monospace;">20,650 đ</td>
                                    <td style="padding: 10px 14px;"><span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">RADAR TUẦN (0 CP)</span></td>
                                    <td style="padding: 10px 14px; font-size: 12px; color: #94a3b8;">Đội tàu 58 chiếc chạy quốc tế thu USD, OCF gấp đôi LNST, theo dõi sóng vận tải cả tuần.</td>
                                    <td style="padding: 10px 14px; font-size: 12px; color: #cbd5e1;">Chờ điểm Pivot cạn cung No-Supply.</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 14px; font-weight: 800; color: #fbbf24; font-family: 'JetBrains Mono', monospace;">BSR</td>
                                    <td style="padding: 10px 14px;">UPCoM • Lọc hóa dầu</td>
                                    <td style="padding: 10px 14px; font-family: 'JetBrains Mono', monospace;">26,500 đ</td>
                                    <td style="padding: 10px 14px;"><span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">RADAR TUẦN (0 CP)</span></td>
                                    <td style="padding: 10px 14px; font-size: 12px; color: #94a3b8;">Tiền mặt 28,300 tỷ đồng, chờ thông tin chính thức chuyển sàn niêm yết sang HOSE.</td>
                                    <td style="padding: 10px 14px; font-size: 12px; color: #cbd5e1;">Chờ tin tức chuyển sàn HOSE.</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- PHẦN 3: TIMELINE TÁC CHIẾN 4 PHA -->
                <div style="background: var(--bg-base); border: 1px solid var(--border-color); border-radius: 12px; padding: 18px 20px;">
                    <div style="font-size: 12px; font-weight: 800; color: #fff; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 12px;">
                        ⏱️ KẾ HOẠCH TÁC CHIẾN 4 PHA NGÀY HÔM NAY (THỨ HAI 09/11/2026)
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px;">
                        <div style="background: var(--bg-surface); padding: 12px 14px; border-radius: 8px; border-left: 3px solid #64748b;">
                            <div style="font-size: 11px; color: #94a3b8; font-weight: 700;">PHA 1: 09h00 - 11h30</div>
                            <div style="font-size: 13px; font-weight: 700; color: #fff; margin-top: 2px;">Phiên Sáng: ĐỨNG NGOÀI 100%</div>
                            <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 4px;">Tuyệt đối không mua đuổi giá xanh ATO; quan sát phe bán kiệt sức.</div>
                        </div>
                        <div style="background: var(--bg-surface); padding: 12px 14px; border-radius: 8px; border-left: 3px solid #f59e0b;">
                            <div style="font-size: 11px; color: #fbbf24; font-weight: 700;">PHA 2: 11h30 - 13h00</div>
                            <div style="font-size: 13px; font-weight: 700; color: #fff; margin-top: 2px;">Nghỉ Trưa: Rà Soát Sổ Lệnh</div>
                            <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 4px;">Kiểm tra độ cạn cung No-Supply, mở app TCBS sẵn sàng tiểu khoản 105C307855.</div>
                        </div>
                        <div style="background: var(--bg-surface); padding: 12px 14px; border-radius: 8px; border-left: 3px solid #38bdf8;">
                            <div style="font-size: 11px; color: #38bdf8; font-weight: 700;">PHA 3: 13h00 - 13h55</div>
                            <div style="font-size: 13px; font-weight: 700; color: #fff; margin-top: 2px;">Đầu Chiều: Radar Hàng T+2.5</div>
                            <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 4px;">Đánh giá lực hấp thụ hàng bán cắt lỗ của thị trường, xác nhận dòng tiền tạo lập.</div>
                        </div>
                        <div style="background: var(--bg-surface); padding: 12px 14px; border-radius: 8px; border-left: 3px solid #10b981;">
                            <div style="font-size: 11px; color: #34d399; font-weight: 700;">PHA 4: 14h00 - 14h25</div>
                            <div style="font-size: 13px; font-weight: 700; color: #fff; margin-top: 2px;">KHUNG GIỜ VÀNG: Bấm Cò Nhịp 1</div>
                            <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 4px;">Đặt lệnh LO: 100 CP HDB (22.30 - 22.45) & 100 CP MSH (34.60 - 35.00).</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>


        <!-- ========================================================
             TAB 3: PHÒNG TÁC CHIẾN ĐẦU TƯ TRONG NGÀY (MINH QUÂN & VICTOR)
             ======================================================== -->
        <!-- ========================================================
             TAB 3: PHÒNG TÁC CHIẾN ĐẦU TƯ TRONG NGÀY (MINH QUÂN & VICTOR)
             ======================================================== -->
        <!-- ========================================================
             TAB 3: PHÒNG TÁC CHIẾN ĐẦU TƯ TRONG NGÀY (MINH QUÂN & VICTOR)
             ======================================================== -->
        <section id="tab-war-room" class="tab-pane">
            <div class="war-room-wrap">
                <!-- TOP RIBBON: MARKET PHASE & REALTIME CLOCKS -->
                <div class="war-room-ribbon">
                    <div class="war-room-ribbon-top">
                        <div class="war-room-title-box">
                            <span class="war-room-live-pulse"><span class="war-room-live-dot"></span> TRỰC CHIẾN LIVE</span>
                            <div>
                                <div class="war-room-title">⚡ PHÒNG TÁC CHIẾN ĐẦU TƯ TRONG NGÀY (APEX DAILY TACTICAL WAR-ROOM)</div>
                                <div class="war-room-subtitle">Chủ tịch: <strong>Trần Quốc Thiên Phước</strong> (TCBS: <code>105C307855</code>) | Trực chiến: <strong>Minh Quân</strong> (Ban 7 VN) &amp; <strong>Victor</strong> (Ban 9 Live Sentinel) | Standby: <strong>Alex</strong> (Ban 7 US)</div>
                            </div>
                        </div>
                        <div class="war-room-meta-group">
                            <div class="meta-pill">📅 Ngày: <strong>2026-11-09</strong></div>
                            <div class="meta-pill">⏰ Giờ VN: <strong id="war-room-clock" style="color: #38bdf8; font-family: monospace;">{wr_server_time}</strong></div>
                            <div class="meta-pill" id="wr-header-cash-pill" style="border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.1);">💰 Két Tiền Thật: <strong style="color: #34d399;">14,510,422 ₫</strong> (72.0% Cash) | 📈 Cổ Phiếu: <strong style="color: #38bdf8;">5,650,000 ₫</strong> (200 CP)</div>
                            <div class="meta-pill" style="border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.1);">🗽 Phiên New York (21h30): <strong id="war-room-ny-countdown" style="color: #fbbf24;">{wr_ny_countdown}</strong></div>
                            <button onclick="loadTacticalWarRoomData()" class="btn-quick-prompt" style="background: rgba(14, 165, 233, 0.25); border-color: #38bdf8; color: #f8fafc; font-weight: 800; padding: 6px 12px;">🔄 Làm Mới Live</button>
                        </div>
                    </div>

                    <!-- 8-PHASE STEPPER (DYNAMIC ACTIVE STATE) -->
                    <div class="phase-stepper-wrap" id="war-room-phase-stepper">
                        <div class="phase-step-card {'active' if wr_phase_id == 'PRE_ATO' else ''}" id="step-PRE_ATO">
                            <div class="phase-card-header"><span>PHASE 1</span><span>08:30-09:00</span></div>
                            <div class="phase-card-name">📋 Pre-ATO Giao Ban</div>
                            <div class="phase-card-time">Sổ Lệnh Master</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'ATO_OPEN' else ''}" id="step-ATO_OPEN">
                            <div class="phase-card-header"><span>PHASE 2</span><span>09:00-09:15</span></div>
                            <div class="phase-card-name">🛑 Mở Cửa ATO</div>
                            <div class="phase-card-time">Không Đua Lệnh</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'MORNING_CONTINUOUS' else ''}" id="step-MORNING_CONTINUOUS">
                            <div class="phase-card-header"><span style="color:#38bdf8;">PHASE 3</span><span>09:15-11:30</span></div>
                            <div class="phase-card-name">📈 Phiên Sáng</div>
                            <div class="phase-card-time">Đo Lực Mua Chủ Động</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'NOON_INTERMISSION' else ''}" id="step-NOON_INTERMISSION">
                            <div class="phase-card-header"><span style="color:#fbbf24;">PHASE 4 ●</span><span>11:30-13:00</span></div>
                            <div class="phase-card-name" style="color:#fbbf24;">☕ Nghỉ Trưa &amp; Hội Ý</div>
                            <div class="phase-card-time">Đối Soát Khối Ngoại</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'T2_ABSORPTION' else ''}" id="step-T2_ABSORPTION">
                            <div class="phase-card-header"><span>PHASE 5</span><span>13:00-14:00</span></div>
                            <div class="phase-card-name">⏳ Hấp Thụ T+2</div>
                            <div class="phase-card-time">Quan Sát Rũ Cung</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'GOLDEN_WINDOW' else ''}" id="step-GOLDEN_WINDOW" style="border-color: rgba(245, 158, 11, 0.5);">
                            <div class="phase-card-header"><span style="color:#fbbf24;">⭐ PHASE 6</span><span>14:00-14:25</span></div>
                            <div class="phase-card-name" style="color:#fbbf24;">🎯 Khung Giờ Vàng</div>
                            <div class="phase-card-time">Bấm Cò Nhịp 1</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'ATC_CLOSING' else ''}" id="step-ATC_CLOSING">
                            <div class="phase-card-header"><span>PHASE 7</span><span>14:30-14:45</span></div>
                            <div class="phase-card-name">🏁 Đóng Cửa ATC</div>
                            <div class="phase-card-time">Đối Soát Nến Ngày</div>
                        </div>
                        <div class="phase-step-card {'active' if wr_phase_id == 'POST_MARKET_WALL_STREET' else ''}" id="step-POST_MARKET_WALL_STREET">
                            <div class="phase-card-header"><span>PHASE 8</span><span>14:45-24:00</span></div>
                            <div class="phase-card-name">🗽 Phố Wall Ca Tối</div>
                            <div class="phase-card-time">Chuyển Giao Alex</div>
                        </div>
                    </div>
                </div>

                <!-- ========================================================
                     BẢNG KẾ HOẠCH TÁC CHIẾN TUẦN (ĐỊNH HƯỚNG THAM KHẢO CHO CHỦ TỊCH)
                     CĂN CỨ: NGHỊ QUYẾT ĐẠI HỘI NGHỊ THƯỢNG ĐỈNH (APEX-SUMMIT-20261108-2100)
                     ======================================================== -->
                <div class="weekly-roadmap-box" id="weekly-roadmap-box" style="margin-bottom: 20px; background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.85)); border: 1.5px solid rgba(245, 158, 11, 0.45); border-radius: 14px; padding: 18px 20px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 22px;">📅</span>
                            <div>
                                <div style="font-size: 15px; font-weight: 800; color: #fbbf24; display: flex; align-items: center; gap: 8px;">
                                    <span>BẢNG KẾ HOẠCH TÁC CHIẾN TUẦN (ĐỊNH HƯỚNG THAM KHẢO CHO CHỦ TỊCH)</span>
                                    <span style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); padding: 2px 8px; border-radius: 9999px; font-size: 10.5px; font-weight: 800;">TUẦN 46: 09/11 – 13/11</span>
                                </div>
                                <div style="font-size: 11.5px; color: #94a3b8; margin-top: 2px;">
                                    Căn cứ: <strong>Nghị Quyết Đại Hội Nghị Thượng Đỉnh Toàn Doanh Nghiệp</strong> (Mã: <code>APEX-SUMMIT-20261108-2100</code>) • Ký duyệt lúc <strong>23:08:16 Ngày 08/11/2026</strong> • 🛡️ Ban 12 Niêm Phong
                                </div>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="background: rgba(14, 165, 233, 0.15); color: #38bdf8; border: 1px solid rgba(14, 165, 233, 0.3); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">
                                💡 Dành Riêng Cho Chủ Tịch Tham Khảo
                            </span>
                            <button id="btn-toggle-weekly-roadmap" onclick="toggleWeeklyRoadmap()" style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); color: #cbd5e1; font-size: 11.5px; font-weight: 700; padding: 5px 12px; border-radius: 6px; cursor: pointer;">
                                ▾ Thu Gọn
                            </button>
                        </div>
                    </div>

                    <!-- KHUNG CẢNH BÁO THỂ CHẾ BẮT BUỘC (DISCLAIMER ĐANH THÉP) -->
                    <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; font-size: 11.5px; color: #fde68a; line-height: 1.55;">
                        ⚖️ <strong>QUY TẮC HIẾN CHƯƠNG TỐI QUAN TRỌNG THEO CHỈ THỊ CỦA CHỦ TỊCH:</strong><br>
                        Bảng kế hoạch tuần này <strong>CHỈ MANG TÍNH CHẤT THAM KHẢO ĐỊNH HƯỚNG DÀNH RIÊNG CHO CHỦ TỊCH</strong>, <strong>TUYỆT ĐỐI KHÔNG PHẢI KẾ HOẠCH CỨNG CỦA CẢ TUẦN</strong> vì thị trường chứng khoán liên tục biến động và đầy biến số.<br>
                        <strong>TOÀN BỘ 12 PHÒNG BAN NGHIÊM CẤM TỰ Ý XEM ĐÂY LÀ KẾ HOẠCH CHÍNH THỨC ĐỂ TỰ ĐỘNG THỰC THI</strong>. Mọi quyết định giải ngân, gia tăng hay phòng thủ <strong>BẮT BUỘC PHẢI ĐƯỢC THAY ĐỔI TỪNG NGÀY</strong> dựa trên Báo cáo KQKD, Báo cáo Vĩ mô và Sổ Lệnh Đầu Ngày (08h30) của từng phiên giao dịch!
                    </div>

                    <!-- NỘI DUNG CHI TIẾT 5 NGÀY VÀ WATCHLIST TUẦN (CÓ THỂ COLLAPSE) -->
                    <div id="weekly-roadmap-details">
                        <!-- 5 NGÀY TÁC CHIẾN TRONG TUẦN -->
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; margin-bottom: 14px;">
                            <!-- Thứ Hai -->
                            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong style="color: #34d399; font-size: 12px;">THỨ HAI (09/11)</strong>
                                    <span style="background: rgba(16, 185, 129, 0.25); color: #34d399; font-size: 9.5px; font-weight: 800; padding: 2px 6px; border-radius: 4px;">✅ ĐÃ HOÀN TẤT</span>
                                </div>
                                <div style="font-size: 11.5px; font-weight: 800; color: #f8fafc;">Khảo Sát Hàng T+2 &amp; Thăm Dò Nhịp 1</div>
                                <div style="font-size: 10.5px; color: #cbd5e1; line-height: 1.45;">
                                    🎉 <strong>Đã thực thi thành công</strong>: Khớp 100 CP HDB (22,050 ₫) &amp; 100 CP MSH (34,517 ₫) lúc 14:02. Vốn giải ngân 5.65M (28.0% NAV). Két tiền 14.51M (72.0% NAV). Stop 2xATR đã khóa chặt!
                                </div>
                            </div>

                            <!-- Thứ Ba -->
                            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 10px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong style="color: #38bdf8; font-size: 12px;">THỨ BA (10/11)</strong>
                                    <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; font-size: 9.5px; font-weight: 800; padding: 2px 6px; border-radius: 4px;">⏳ DỰ KIẾN THAM KHẢO</span>
                                </div>
                                <div style="font-size: 11.5px; font-weight: 800; color: #f8fafc;">Thẩm Định Giữ Nền &amp; Soi BAF / IDC</div>
                                <div style="font-size: 10.5px; color: #cbd5e1; line-height: 1.45;">
                                    • Quan sát lực đỡ của HDB (22k) và MSH (34.5k).<br>
                                    • Soi nến Test Cung của BAF (30.5 – 30.8k) và IDC (34.2 – 34.6k).<br>
                                    • <strong>Hành động</strong>: Tiếp tục bảo toàn 72% tiền mặt. Tuyệt đối không FOMO đuổi giá xanh!
                                </div>
                            </div>

                            <!-- Thứ Tư -->
                            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 10px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong style="color: #94a3b8; font-size: 12px;">THỨ TƯ (11/11)</strong>
                                    <span style="background: rgba(148, 163, 184, 0.15); color: #94a3b8; font-size: 9.5px; font-weight: 800; padding: 2px 6px; border-radius: 4px;">⏳ DỰ KIẾN THAM KHẢO</span>
                                </div>
                                <div style="font-size: 11.5px; font-weight: 800; color: #f8fafc;">Hấp Thụ Hàng T+2 &amp; Điểm Breakout</div>
                                <div style="font-size: 10.5px; color: #cbd5e1; line-height: 1.45;">
                                    • Đo lường phân hóa dòng tiền 3 khối.<br>
                                    • <strong>Điều kiện Nhịp 2 (40%)</strong>: Chỉ xem xét gia tăng nếu HDB vượt 22.8k hoặc MSH vượt 36k kèm Vol &ge; 150% MA20.<br>
                                    • Nếu vol yếu, kiên quyết không giải ngân thêm.
                                </div>
                            </div>

                            <!-- Thứ Năm -->
                            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 10px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong style="color: #94a3b8; font-size: 12px;">THỨ NĂM (12/11)</strong>
                                    <span style="background: rgba(148, 163, 184, 0.15); color: #94a3b8; font-size: 9.5px; font-weight: 800; padding: 2px 6px; border-radius: 4px;">⏳ DỰ KIẾN THAM KHẢO</span>
                                </div>
                                <div style="font-size: 11.5px; font-weight: 800; color: #f8fafc;">Hàng Về Tài Khoản &amp; Trailing Stop</div>
                                <div style="font-size: 10.5px; color: #cbd5e1; line-height: 1.45;">
                                    • 13:15 chiều: 200 CP (HDB, MSH) về kho khả dụng.<br>
                                    • Nếu lãi &ge; +5%: Nâng Stop Loss lên giá vốn (Trailing Stop 0% rủi ro).<br>
                                    • Nếu chạm TP1 (HDB: 24.29k, MSH: 39.56k): Chủ động chốt lời 50% đút tiền vào két.
                                </div>
                            </div>

                            <!-- Thứ Sáu -->
                            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 10px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong style="color: #94a3b8; font-size: 12px;">THỨ SÁU (13/11)</strong>
                                    <span style="background: rgba(148, 163, 184, 0.15); color: #94a3b8; font-size: 9.5px; font-weight: 800; padding: 2px 6px; border-radius: 4px;">⏳ DỰ KIẾN THAM KHẢO</span>
                                </div>
                                <div style="font-size: 11.5px; font-weight: 800; color: #f8fafc;">Đóng Nến Tuần &amp; Đối Soát Hiệu Suất</div>
                                <div style="font-size: 10.5px; color: #cbd5e1; line-height: 1.45;">
                                    • CẤM MỞ LỆNH MỚI chiều Thứ Sáu.<br>
                                    • Khóa bảo toàn két tiền mặt &ge; 50% - 60% NAV.<br>
                                    • Ban 5 VN hồi tố Hit Rate %; Bàn giao toàn bộ số liệu kiểm toán cho Master CIO James chuẩn bị Hội Nghị Thượng Đỉnh 21h00 Chủ Nhật.
                                </div>
                            </div>
                        </div>

                        <!-- BẢNG TOP 4 SIÊU CỔ PHIẾU ĐỊNH HƯỚNG TUẦN (PHÊ DUYỆT BỞI HỘI NGHỊ THƯỢNG ĐỈNH) -->
                        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 8px; padding: 10px 14px;">
                            <div style="font-size: 11px; font-weight: 800; color: #38bdf8; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                                <span>🎯 TOP 4 SIÊU CỔ PHIẾU ĐỊNH HƯỚNG TUẦN (NGHỊ QUYẾT APEX-SUMMIT-20261108-2100)</span>
                                <span style="font-size: 10.5px; color: #94a3b8;">Biên độ gom LO • Stop 2xATR • Kế hoạch chia nhịp Kim Tự Tháp</span>
                            </div>
                            <table class="stock-sentinel-table" style="font-size: 11px;">
                                <thead>
                                    <tr>
                                        <th>Mã CP</th>
                                        <th>Phân Tầng</th>
                                        <th>Vùng Gom LO</th>
                                        <th>Stop 2xATR</th>
                                        <th>Mục Tiêu TP1 / TP2</th>
                                        <th>Kế Hoạch Cả Tuần</th>
                                        <th>Trạng Thái Thực Tế</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><strong style="color: #38bdf8;">HDB</strong></td>
                                        <td><span style="color: #34d399;">Core Compounder</span></td>
                                        <td>22,200 – 22,400 ₫</td>
                                        <td style="color: #ef4444; font-weight: 700;">21,220 ₫ (-5.7%)</td>
                                        <td>24.29k / 25.82k</td>
                                        <td>Tối đa 300 CP (3 nhịp)</td>
                                        <td><span style="background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 2px 6px; border-radius: 4px; font-weight: 700;">✅ ĐÃ KHỚP 100 CP</span></td>
                                    </tr>
                                    <tr>
                                        <td><strong style="color: #38bdf8;">MSH</strong></td>
                                        <td><span style="color: #38bdf8;">Tactical Alpha</span></td>
                                        <td>34,500 – 35,000 ₫</td>
                                        <td style="color: #ef4444; font-weight: 700;">33,090 ₫ (-6.8%)</td>
                                        <td>39.56k / 43.04k</td>
                                        <td>Tối đa 200 CP (2 nhịp)</td>
                                        <td><span style="background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 2px 6px; border-radius: 4px; font-weight: 700;">✅ ĐÃ KHỚP 100 CP</span></td>
                                    </tr>
                                    <tr>
                                        <td><strong style="color: #38bdf8;">BAF</strong></td>
                                        <td><span style="color: #fbbf24;">Standby Alpha 1</span></td>
                                        <td>30,500 – 30,800 ₫</td>
                                        <td style="color: #ef4444; font-weight: 700;">29,650 ₫ (-4.0%)</td>
                                        <td>32.65k / 35.50k</td>
                                        <td>Tối đa đúng 100 CP (Rào nợ)</td>
                                        <td><span style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; padding: 2px 6px; border-radius: 4px; font-weight: 700;">⏳ CHỜ TÍN HIỆU (0 CP)</span></td>
                                    </tr>
                                    <tr>
                                        <td><strong style="color: #38bdf8;">IDC</strong></td>
                                        <td><span style="color: #fbbf24;">Standby Alpha 2</span></td>
                                        <td>34,200 – 34,600 ₫</td>
                                        <td style="color: #ef4444; font-weight: 700;">32,530 ₫ (-6.0%)</td>
                                        <td>38.66k / 41.88k</td>
                                        <td>Tối đa 200 CP (2 nhịp)</td>
                                        <td><span style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; padding: 2px 6px; border-radius: 4px; font-weight: 700;">⏳ CHỜ TÍN HIỆU (0 CP)</span></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- 3 COLUMNS TACTICAL COMMAND -->
                <div class="war-room-columns">
                    <!-- ================= CỘT 1: MINH QUÂN BLUEPRINT ================= -->
                    <div class="tactical-panel">
                        <div class="panel-header">
                            <div class="panel-title-box">
                                <span class="panel-icon">👨‍💼</span>
                                <div>
                                    <div class="panel-title">Kế Hoạch Đầu Ngày Chuẩn Chỉ</div>
                                    <div style="font-size: 11px; color: #94a3b8;">Minh Quân (Ban 7 VN) công bố lúc 08h30</div>
                                </div>
                            </div>
                            <div class="panel-badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4);">Mastery: 98.5/100</div>
                        </div>

                        <!-- Stats Bar Minh Quân -->
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; background: rgba(30, 41, 59, 0.5); padding: 8px 10px; border-radius: 8px; border: 1px solid rgba(148, 163, 184, 0.15);">
                            <div style="display: flex; flex-direction: column; align-items: center;">
                                <span style="font-size: 10px; color: #94a3b8;">Kỳ Vọng Toán Học</span>
                                <strong style="font-size: 13px; color: #34d399;">EV% +10.95%</strong>
                            </div>
                            <div style="display: flex; flex-direction: column; align-items: center; border-left: 1px solid rgba(148, 163, 184, 0.15); border-right: 1px solid rgba(148, 163, 184, 0.15);">
                                <span style="font-size: 10px; color: #94a3b8;">Tỷ Lệ Thắng TB</span>
                                <strong style="font-size: 13px; color: #38bdf8;">P(W) 85.5%</strong>
                            </div>
                            <div style="display: flex; flex-direction: column; align-items: center;">
                                <span style="font-size: 10px; color: #94a3b8;">Risk / Reward</span>
                                <strong style="font-size: 13px; color: #fbbf24;">R:R 1:2.86</strong>
                            </div>
                        </div>

                        <!-- Top 4 Picks Cards -->
                        <div style="display: flex; flex-direction: column; gap: 10px;" id="war-room-picks-container">
                            <!-- HDB -->
                            <div class="stock-pick-card leader">
                                <div class="stock-card-top">
                                    <div>
                                        <span class="stock-ticker">HDB</span>
                                        <span class="stock-name">HDBank (HOSE)</span>
                                    </div>
                                    <span style="font-size: 10.5px; font-weight: 800; color: #10b981; background: rgba(16, 185, 129, 0.15); padding: 2px 6px; border-radius: 4px;">TIÊU ĐIỂM SỐ 1</span>
                                </div>
                                <div class="stock-stats-grid">
                                    <div class="stock-stat-item">
                                        <span class="stat-label">Giá Gom N1 (100 CP)</span>
                                        <span class="stat-val">22,100 – 22,450 ₫</span>
                                    </div>
                                    <div class="stock-stat-item">
                                        <span class="stat-label">Stop 2xATR</span>
                                        <span class="stat-val loss">21,220 ₫ (-5.7%)</span>
                                    </div>
                                    <div class="stock-stat-item">
                                        <span class="stat-label">Mục Tiêu TP1 / TP2</span>
                                        <span class="stat-val gain">24.29k / 25.82k</span>
                                    </div>
                                    <div class="stock-stat-item">
                                        <span class="stat-label">Tỷ Lệ R:R</span>
                                        <span class="stat-val gold">1 : 2.59</span>
                                    </div>
                                    <div class="stock-stat-item">
                                        <span class="stat-label">Kỳ Vọng EV%</span>
                                        <span class="stat-val gain">+8.8%</span>
                                    </div>
                                    <div class="stock-stat-item">
                                        <span class="stat-label">Vốn Nhịp 1</span>
                                        <span class="stat-val">2,235,000 ₫</span>
                                    </div>
                                </div>
                                <div class="stock-catalyst">⚡ <strong>Catalyst</strong>: Tín dụng +22% (Top 1 ngành), NIM 5.1%, CASA 18.2%, ROE 24.5%. Lãi Q3 tăng 42% YoY.</div>
                            </div>

                            <!-- MSH -->
                            <div class="stock-pick-card alpha">
                                <div class="stock-card-top">
                                    <div>
                                        <span class="stock-ticker">MSH</span>
                                        <span class="stock-name">May Sông Hồng (HOSE)</span>
                                    </div>
                                    <span style="font-size: 10.5px; font-weight: 800; color: #38bdf8; background: rgba(56, 189, 248, 0.15); padding: 2px 6px; border-radius: 4px;">TACTICAL ALPHA</span>
                                </div>
                                <div class="stock-stats-grid">
                                    <div class="stock-stat-item">
                                        <span class="stat-label">Giá Gom N1 (100 CP)</span>
                                        <span class="stat-val">34,500 – 35,000 ₫</span>
                                    </div>
                                    <div class="stock-stat-item">
                                        <span class="stat-label">Stop 2xATR</span>
                                        <span class="stat-val loss">33,090 ₫ (-6.8%)</span>
                                    </div>
                                    <div class="stock-stat-item">
                                        <span class="stat-label">Mục Tiêu TP1 / TP2</span>
                                        <span class="stat-val gain">39.56k / 43.04k</span>
                                    </div>
                                    <div class="stock-stat-item">
                                        <span class="stat-label">Tỷ Lệ R:R</span>
                                        <span class="stat-val gold">1 : 3.13</span>
                                    </div>
                                    <div class="stock-stat-item">
                                        <span class="stat-label">Kỳ Vọng EV%</span>
                                        <span class="stat-val gain">+13.1%</span>
                                    </div>
                                    <div class="stock-stat-item">
                                        <span class="stat-label">Vốn Nhịp 1</span>
                                        <span class="stat-val">3,480,000 ₫</span>
                                    </div>
                                </div>
                                <div class="stock-catalyst">⚡ <strong>Catalyst</strong>: Nhà máy Sông Hồng 10 chạy 100% công suất, đơn hàng dệt may Mỹ hồi phục cực mạnh, cổ tức tiền mặt 30-40%.</div>
                            </div>

                            <!-- BAF & IDC STANDBY -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                                <div class="stock-pick-card standby">
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <span class="stock-ticker">BAF</span>
                                        <span style="font-size:10px; color:#94a3b8;">STANDBY</span>
                                    </div>
                                    <div style="font-size:11px; color:#cbd5e1;">Giá 30.85k | Stop 28.6k</div>
                                    <div style="font-size:10px; color:#94a3b8;">Chờ test cạn Vol, heo >65k</div>
                                </div>
                                <div class="stock-pick-card standby">
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <span class="stock-ticker">IDC</span>
                                        <span style="font-size:10px; color:#94a3b8;">STANDBY</span>
                                    </div>
                                    <div style="font-size:11px; color:#cbd5e1;">Giá 34.6k | Stop 32.5k</div>
                                    <div style="font-size:10px; color:#94a3b8;">KCN Hựu Thạnh FCF khủng</div>
                                </div>
                            </div>
                        </div>

                        <!-- 3 KHÔNG & 1 KHUNG GIỜ VÀNG -->
                        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 8px; padding: 10px 12px; display: flex; flex-direction: column; gap: 4px;">
                            <div style="font-size: 11px; font-weight: 800; color: #f87171;">🛡️ QUY TẮC KỶ LUẬT SẮT MINH QUÂN:</div>
                            <div style="font-size: 11px; color: #cbd5e1;">• ❌ <strong>Không mua ATO</strong>: Tránh bẫy kéo giá ảo đầu ngày.</div>
                            <div style="font-size: 11px; color: #cbd5e1;">• ❌ <strong>Không mua giá xanh</strong>: Cấm FOMO khi chưa có nền cạn cung.</div>
                            <div style="font-size: 11px; color: #cbd5e1;">• ❌ <strong>Không bình quân giá xuống</strong>: Cắt lỗ cứng Stop 2xATR.</div>
                            <div style="font-size: 11px; color: #fbbf24;">• ⭐ <strong>Khung Giờ Vàng 14h00-14h25</strong>: Chỉ bấm cò khi nhìn rõ 90% nến ngày!</div>
                        </div>

                        <!-- Button Full Report -->
                        <button onclick="openReportModal('VN_Market/07_Daily_Specialist/2026-11-09_VN_Specialist_Decision.md')" class="btn-read" style="background: rgba(14, 165, 233, 0.2); border: 1px solid #38bdf8; color: #38bdf8; font-weight: 800; padding: 8px; text-align: center; border-radius: 6px; cursor: pointer; transition: all 0.2s;">
                            📖 Xem Toàn Văn Quyết Định Minh Quân Hôm Nay
                        </button>
                    </div>

                    <!-- ================= CỘT 2: BÁO CÁO TÁC CHIẾN TRONG NGÀY (3 GIAI ĐOẠN QUYẾT ĐỊNH) ================= -->
                    <div class="tactical-panel">
                        <div class="panel-header">
                            <div class="panel-title-box">
                                <span class="panel-icon">📋</span>
                                <div>
                                    <div class="panel-title">Báo Cáo Tác Chiến Trong Ngày</div>
                                    <div style="font-size: 11px; color: #94a3b8;">Lộ trình 3 Giai Đoạn Phiên Chiều &amp; Sổ Lệnh Khung Giờ Vàng</div>
                                </div>
                            </div>
                            <span class="war-room-live-pulse" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border-color: rgba(56, 189, 248, 0.4);"><span class="war-room-live-dot" style="background: #38bdf8;"></span> REALTIME</span>
                        </div>

                        <!-- 3 GIAI ĐOẠN PHIÊN CHIỀU (CHỦ TỊCH YÊU CẦU ĐẶC BIỆT) -->
                        <div style="display: flex; flex-direction: column; gap: 10px;" id="afternoon-tactical-stages">
                            
                            <!-- GIAI ĐOẠN 1: 13:00 - 13:45 (ACTIVE) -->
                            <div id="stage-1-card" class="action-plan-hero-card" style="border: 1.5px solid rgba(56, 189, 248, 0.5); background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(15, 23, 42, 0.88)); border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                                <div style="display: flex; align-items: center; justify-content: space-between;">
                                    <span id="stage-1-badge" class="action-plan-tag" style="background: rgba(56, 189, 248, 0.25); color: #38bdf8; border-color: rgba(56, 189, 248, 0.5); font-weight: 800;">
                                        <span class="war-room-live-dot" style="background:#38bdf8;"></span> ĐANG DIỄN RA
                                    </span>
                                    <span style="font-size: 11.5px; font-weight: 800; color: #38bdf8; font-family: monospace;">13:00 – 13:45</span>
                                </div>
                                <div style="font-size: 13px; font-weight: 800; color: #f8fafc;">
                                    1. Giai Đoạn 1 (13:00 – 13:45): Quan Sát Nhịp Hấp Thụ Hàng T+2 Về Tài Khoản
                                </div>
                                <div style="font-size: 11px; color: #cbd5e1; line-height: 1.55;">
                                    • <strong>Bản chất nhịp thị trường</strong>: Khung giờ từ <code style="color:#38bdf8;">13:15 – 13:35</code> là thời điểm lượng hàng bắt đáy T+2.5 từ tuần trước chính thức về tài khoản các nhà đầu tư cá nhân. Đây thường là nhịp rung lắc biến động mạnh nhất phiên chiều khi nhóm lướt sóng ngắn hạn mang hàng ra chốt lời hoặc cắt lỗ.
                                </div>
                                <div style="background: rgba(239, 68, 68, 0.12); border-left: 3px solid #ef4444; padding: 6px 10px; border-radius: 4px; font-size: 10.5px; color: #fca5a5; line-height: 1.5;">
                                    ⚖️ <strong>Kỷ luật Hiến chương</strong>: <strong>TUYỆT ĐỐI KHÔNG NÔN NÓNG GIẢI NGÂN SỚM</strong>. Chúng ta kiên nhẫn để phe bán cá nhân xả hết hàng tự nhiên, quan sát xem có áp lực bán tháo hoảng loạn hay không.
                                </div>
                            </div>

                            <!-- GIAI ĐOẠN 2: 13:45 - 13:55 (UPCOMING / NO-SUPPLY CHECK) -->
                            <div id="stage-2-card" style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                                <div style="display: flex; align-items: center; justify-content: space-between;">
                                    <span id="stage-2-badge" style="font-size: 10px; font-weight: 800; color: #94a3b8; background: rgba(148, 163, 184, 0.15); padding: 2px 8px; border-radius: 4px;">CHUẨN BỊ ĐẾN</span>
                                    <span style="font-size: 11px; font-weight: 800; color: #94a3b8; font-family: monospace;">13:45 – 13:55</span>
                                </div>
                                <div style="font-size: 13px; font-weight: 800; color: #f1f5f9;">
                                    2. Giai Đoạn 2 (13:45 – 13:55): Thẩm Định Lực Đỡ &amp; Độ Cạn Cung (No-Supply Check)
                                </div>
                                <div style="font-size: 11px; color: #cbd5e1; line-height: 1.55;">
                                    • Victor và Minh Quân sẽ đo lường trực tiếp tỷ lệ Mua chủ động (Buy Up Ratio) và khối lượng khớp lệnh:
                                    <div style="margin-left: 8px; margin-top: 4px; display: flex; flex-direction: column; gap: 3px;">
                                        <div>• <strong style="color: #38bdf8;">HDB</strong>: Xác nhận lực đỡ quanh vùng giá <code style="color:#fbbf24;">22,100 – 22,450 đ</code>. Nếu khối lượng bán teo tóp và bên mua chủ động chiếm ưu thế <strong>&ge; 50%</strong>, tín hiệu gom hàng hoàn tất.</div>
                                        <div>• <strong style="color: #38bdf8;">MSH</strong>: Xác nhận lực giữ nền quanh vùng <code style="color:#fbbf24;">34,500 – 35,000 đ</code>. Biên độ dao động siết chặt là điều kiện tiên quyết.</div>
                                    </div>
                                </div>
                            </div>

                            <!-- GIAI ĐOẠN 3: 14:00 - 14:25 (GOLDEN WINDOW - MASTER EXECUTION) -->
                            <div id="stage-3-card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.16), rgba(15, 23, 42, 0.95)); border: 1.5px solid rgba(52, 211, 153, 0.6); border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 7px;">
                                <div style="display: flex; align-items: center; justify-content: space-between;">
                                    <span id="stage-3-badge" style="font-size: 10px; font-weight: 800; color: #34d399; background: rgba(16, 185, 129, 0.2); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.35);">
                                        ✅ ĐÃ BẤM CÒ & KHỚP LỆNH THÀNH CÔNG
                                    </span>
                                    <span style="font-size: 11px; font-weight: 800; color: #34d399; font-family: monospace;">14:00 – 14:25 (ĐÃ KHỚP)</span>
                                </div>
                                <div style="font-size: 13px; font-weight: 800; color: #34d399;">
                                    3. Giai Đoạn 3 (14:00 – 14:25): ✅ ĐÃ KHỚP LỆNH MUA NHỊP 1 THÀNH CÔNG (100 HDB + 100 MSH)
                                </div>
                                <div style="font-size: 11px; color: #e2e8f0; line-height: 1.5;">
                                    • Chủ tịch đã thực thi đặt lệnh Limit (LO) và khớp thành công 100% trên app TCInvest lúc 14:02:
                                </div>
                                <div style="font-size: 11px; color: #cbd5e1; line-height: 1.5;">
                                    <div style="margin-left: 6px; margin-top: 5px; display: flex; flex-direction: column; gap: 5px;">
                                        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(52, 211, 153, 0.35); padding: 6px 10px; border-radius: 6px; font-size: 11px;">
                                            <strong style="color: #38bdf8;">1. Lệnh 1 (HDB)</strong>: Đã Mua khớp đúng <strong style="color: #34d399;">100 CP</strong> • Giá khớp: <strong style="color: #f8fafc;">22,050 đ</strong> (Giá trị: <code>2,200,000 đ</code> — Stop 2xATR: <code>21,220 đ</code>).
                                        </div>
                                        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(52, 211, 153, 0.35); padding: 6px 10px; border-radius: 6px; font-size: 11px;">
                                            <strong style="color: #38bdf8;">2. Lệnh 2 (MSH)</strong>: Đã Mua khớp đúng <strong style="color: #34d399;">100 CP</strong> • Giá khớp: <strong style="color: #f8fafc;">34,517 đ</strong> (Giá trị: <code>3,450,000 đ</code> — Stop 2xATR: <code>33,090 đ</code>).
                                        </div>
                                    </div>
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 3px; padding-top: 6px; border-top: 1px solid rgba(52, 211, 153, 0.2);">
                                    <div style="background: rgba(14, 165, 233, 0.1); padding: 5px 8px; border-radius: 6px; font-size: 10.5px;">
                                        <span style="color: #94a3b8;">Cổ phiếu đã khớp:</span><br>
                                        <strong style="color: #38bdf8; font-size: 12px;">5,650,000 đ (28.0% NAV)</strong>
                                    </div>
                                    <div style="background: rgba(16, 185, 129, 0.1); padding: 5px 8px; border-radius: 6px; font-size: 10.5px;">
                                        <span style="color: #94a3b8;">Tiền mặt TCBS còn lại:</span><br>
                                        <strong style="color: #34d399; font-size: 12px;">14,510,422 đ (72.0% NAV)</strong>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Current Directive Hero Box -->
                        <div class="directive-hero-box" style="margin-top: 8px;">
                            <span style="font-size: 20px;">📢</span>
                            <div>
                                <div style="font-size: 11px; font-weight: 800; color: #34d399; margin-bottom: 2px;">THÔNG ĐIỆP CHỈ ĐẠO CỦA MINH QUÂN HIỆN TẠI:</div>
                                <div class="directive-hero-text" id="war-room-live-directive-box">
                                    {wr_message}
                                </div>
                            </div>
                        </div>

                        <!-- INTERACTIVE DIRECTIVE DESK FOR CHAIRMAN -->
                        <div class="tactical-interactive-card">
                            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(148, 163, 184, 0.15); padding-bottom: 6px;">
                                <div style="font-size: 12px; font-weight: 800; color: #fbbf24; display: flex; align-items: center; gap: 6px;">
                                    <span>👑</span> BÀN RA CHỈ LỆNH TRỰC TIẾP CỦA CHỦ TỊCH
                                </div>
                                <span style="font-size: 10.5px; color: #94a3b8;">Minh Quân &amp; Victor phản hồi tức thì</span>
                            </div>

                            <!-- History Box -->
                            <div class="directive-history-box" id="directive-history-box">
                                <div class="directive-msg specialist">
                                    <div class="directive-msg-head">
                                        <span>Minh Quân (Ban 7 VN)</span>
                                        <span style="font-weight:400; color:#94a3b8;">08:30:15</span>
                                    </div>
                                    <div class="directive-msg-body">
                                        Kính trình Chủ tịch Trần Quốc Thiên Phước! Minh Quân đã hoàn tất Bản Kế Hoạch Đầu Ngày 08h30. Hôm nay ưu tiên quan sát HDB (gom 22,350 ₫) và MSH (gom 34,800 ₫). Két tiền mặt 20,167,119 ₫ sẵn sàng. Toàn đội tuân thủ tuyệt đối: KHÔNG ĐUA LỆNH ATO, chờ Khung Giờ Vàng 14h00 - 14h25!
                                    </div>
                                </div>
                                <div class="directive-msg sentinel">
                                    <div class="directive-msg-head">
                                        <span>Victor (Ban 9 Live Sentinel)</span>
                                        <span style="font-weight:400; color:#94a3b8;">08:32:40</span>
                                    </div>
                                    <div class="directive-msg-body">
                                        Báo cáo Chủ tịch! Victor túc trực 24/7 bảo vệ danh mục. Két tiền mặt thật 20,167,119 ₫ (100% Cash, 0 CP rủi ro). Toàn bộ lãi Vòng 1 (+167,119 ₫) đã khóa an toàn. Radar rủi ro ở CẤP 1 (AN TOÀN TUYỆT ĐỐI). Các kịch bản phòng thủ Stop 2xATR và Synthetic Short Hedge VN30F sẵn sàng trong nòng súng.
                                    </div>
                                </div>
                            </div>

                            <!-- Quick Prompts -->
                            <div class="quick-prompts-row">
                                <button class="btn-quick-prompt" onclick="sendQuickTactical('Minh Quân báo cáo tiến độ hiện tại')">💬 Báo cáo tiến độ</button>
                                <button class="btn-quick-prompt" onclick="sendQuickTactical('Cho tôi xem kế hoạch tuần')" style="border-color: #fbbf24; color: #fbbf24; font-weight: 700;">📅 Soi Kế Hoạch Tuần</button>
                                <button class="btn-quick-prompt" onclick="sendQuickTactical('Đánh giá điều kiện Test Cung của HDB và MSH')">🎯 Soi HDB &amp; MSH</button>
                                <button class="btn-quick-prompt" onclick="sendQuickTactical('Kịch bản ứng phó nếu thị trường bất ngờ sập 15 điểm')">🛡️ Kịch bản thị trường sập</button>
                                <button class="btn-quick-prompt" onclick="sendQuickTactical('Victor kiểm tra két tiền mặt SSOT và sức mua')">💰 Két tiền &amp; Sức mua</button>
                            </div>

                            <!-- Input Row -->
                            <div class="directive-input-row">
                                <input type="text" id="tactical-cmd-input" class="directive-input" placeholder="Kính gửi Chủ tịch, gõ câu hỏi hoặc chỉ thị cho Minh Quân &amp; Victor tại đây..." onkeydown="if(event.key==='Enter') sendTacticalCommand()">
                                <button id="btn-send-tactical" class="btn-send-directive" onclick="sendTacticalCommand()">⚡ Gửi Chỉ Lệnh</button>
                            </div>
                        </div>
                    </div>

                    <!-- ================= CỘT 3: VICTOR SENTINEL & LIVE STOCKS ================= -->
                    <div class="tactical-panel">
                        <!-- VICTOR SENTINEL -->
                        <div class="panel-header">
                            <div class="panel-title-box">
                                <span class="panel-icon">🛡️</span>
                                <div>
                                    <div class="panel-title">Victor Live Portfolio Sentinel</div>
                                    <div style="font-size: 11px; color: #94a3b8;">Ban 9 — Giám Sát Realtime &amp; Ứng Phó Khẩn Cấp</div>
                                </div>
                            </div>
                            <span class="panel-badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4);">24/7 ACTIVE</span>
                        </div>

                        <!-- SSOT Cash & Portfolio Status -->
                        <div id="victor-ssot-cash-card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(15, 23, 42, 0.9)); border: 1px solid rgba(52, 211, 153, 0.35); border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 6px;">
                            <div style="font-size: 11px; color: #94a3b8; display: flex; justify-content: space-between;">
                                <span>TÀI KHOẢN TCBS: <strong>105C307855</strong></span>
                                <span style="color: #34d399; font-weight: 800;">SSOT V2.0</span>
                            </div>
                            <div style="display: flex; align-items: baseline; justify-content: space-between;">
                                <span style="font-size: 11px; color: #cbd5e1;">Két Tiền Mặt Thật:</span>
                                <strong id="victor-cash-val" style="font-size: 19px; color: #34d399; font-family: monospace;">14,510,422 ₫</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; font-size: 11px; border-top: 1px solid rgba(148, 163, 184, 0.15); padding-top: 5px;">
                                <span id="victor-holdings-val" style="color: #94a3b8;">Cổ phiếu rủi ro: <strong style="color: #38bdf8;">200 CP (5,650,000 ₫ • 28.0%)</strong></span>
                                <span id="victor-pnl-val" style="color: #94a3b8;">PnL Tạm: <strong style="color: #f87171;">-6,700 ₫ (-0.1%)</strong> | Lãi V1: <strong style="color: #34d399;">+167,119 ₫</strong></span>
                            </div>
                        </div>

                        <!-- LIVE HOLDINGS CARD (2 MÃ ĐÃ GIẢI NGÂN) -->
                        <div id="victor-live-holdings-box" style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 9px; padding: 10px; display: flex; flex-direction: column; gap: 6px;">
                            <div style="font-size: 11px; font-weight: 800; color: #38bdf8; display: flex; justify-content: space-between;">
                                <span>📦 DANH MỤC ĐÃ GIẢI NGÂN (2 MÃ • 200 CP)</span>
                                <span style="color: #34d399;">🛡️ STOP 2xATR BẢO VỆ</span>
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 5px;">
                                <div style="background: rgba(30, 41, 59, 0.7); padding: 6px 8px; border-radius: 6px; font-size: 11px; display: flex; justify-content: space-between; align-items: center;">
                                    <div><strong style="color: #38bdf8;">HDB</strong> <span style="color: #94a3b8;">(100 CP)</span></div>
                                    <div>Vốn: <span style="color: #cbd5e1;">22,050 ₫</span> ➔ Live: <span style="color: #f87171;">22,000 ₫</span></div>
                                    <div>PnL: <strong style="color: #f87171;">-5,000 ₫ (-0.2%)</strong></div>
                                    <div style="color: #fbbf24; font-size: 10px;">Stop: 21,220 ₫</div>
                                </div>
                                <div style="background: rgba(30, 41, 59, 0.7); padding: 6px 8px; border-radius: 6px; font-size: 11px; display: flex; justify-content: space-between; align-items: center;">
                                    <div><strong style="color: #38bdf8;">MSH</strong> <span style="color: #94a3b8;">(100 CP)</span></div>
                                    <div>Vốn: <span style="color: #cbd5e1;">34,517 ₫</span> ➔ Live: <span style="color: #f87171;">34,500 ₫</span></div>
                                    <div>PnL: <strong style="color: #f87171;">-1,700 ₫ (-0.05%)</strong></div>
                                    <div style="color: #fbbf24; font-size: 10px;">Stop: 33,090 ₫</div>
                                </div>
                            </div>
                        </div>

                        <!-- LIVE MARKET OVERVIEW (VN-INDEX & VN30) -->
                        <div class="market-radar-card" id="market-radar-card">
                            <div style="font-size: 11px; font-weight: 800; color: #38bdf8; display: flex; justify-content: space-between;">
                                <span>📊 GIÁM SÁT THỊ TRƯỜNG REALTIME</span>
                                <span style="color: #34d399;" id="market-status-badge">● UPTREND TÍCH LŨY</span>
                            </div>
                            <div class="index-grid">
                                <div class="index-item">
                                    <div style="display:flex; justify-content:space-between; font-size:10px; color:#94a3b8;">
                                        <span>VN-INDEX</span>
                                        <span class="price-badge up" id="vnindex-pts">+{wr_market['vn_index']['change_pts']} (+{wr_market['vn_index']['change_pct']}%)</span>
                                    </div>
                                    <div style="font-size:15px; font-weight:900; color:#34d399;" id="vnindex-val">{wr_market['vn_index']['value']}</div>
                                    <div style="font-size:10px; color:#94a3b8;">GTGD: <strong>{wr_market['vn_index']['turnover_ty_vnd']}</strong></div>
                                </div>
                                <div class="index-item">
                                    <div style="display:flex; justify-content:space-between; font-size:10px; color:#94a3b8;">
                                        <span>VN30-INDEX</span>
                                        <span class="price-badge up" id="vn30-pts">+{wr_market['vn30_index']['change_pts']} (+{wr_market['vn30_index']['change_pct']}%)</span>
                                    </div>
                                    <div style="font-size:15px; font-weight:900; color:#34d399;" id="vn30-val">{wr_market['vn30_index']['value']}</div>
                                    <div style="font-size:10px; color:#94a3b8;">Basis F1M: <strong>{wr_market['vn30_index']['basis_vn30f']}</strong></div>
                                </div>
                            </div>
                            <div style="font-size:10.5px; color:#cbd5e1; display:flex; justify-content:space-between; border-top:1px solid rgba(148,163,184,0.15); padding-top:4px;">
                                <span>Khối ngoại: <strong style="color:#34d399;" id="foreign-net">{wr_market['vn_index']['foreign_net_ty_vnd']}</strong></span>
                                <span>Độ rộng: <strong style="color:#e2e8f0;">242 Tăng / 145 Giảm</strong></span>
                            </div>
                        </div>

                        <!-- LIVE STOCK TICKER SENTINEL TABLE -->
                        <div style="display: flex; flex-direction: column; gap: 6px;">
                            <div style="font-size: 11.5px; font-weight: 800; color: #f8fafc; display: flex; justify-content: space-between; align-items: center;">
                                <span>🎯 BẢNG GIÁ GIÁM SÁT 4 MÃ VÒNG 2</span>
                                <span style="font-size: 10px; color: #38bdf8;">Tự động cập nhật 24/24</span>
                            </div>
                            <table class="stock-sentinel-table">
                                <thead>
                                    <tr>
                                        <th>Mã CP</th>
                                        <th>Giá Live</th>
                                        <th>+/- %</th>
                                        <th>Volume</th>
                                        <th>Buy Up</th>
                                        <th>Trạng Thái</th>
                                    </tr>
                                </thead>
                                <tbody id="live-stocks-table-body">
                                    <tr>
                                        <td><strong style="color:#38bdf8;">HDB</strong></td>
                                        <td class="price-badge down">22,100</td>
                                        <td class="price-badge down">-1.78%</td>
                                        <td>6.1M</td>
                                        <td style="color:#34d399;">52.4%</td>
                                        <td><span style="color:#10b981; font-weight:700;">🟢 AN TOÀN</span></td>
                                    </tr>
                                    <tr>
                                        <td><strong style="color:#38bdf8;">MSH</strong></td>
                                        <td class="price-badge down">34,500</td>
                                        <td class="price-badge down">-2.82%</td>
                                        <td>53.2k</td>
                                        <td style="color:#34d399;">56.8%</td>
                                        <td><span style="color:#10b981; font-weight:700;">🟢 AN TOÀN</span></td>
                                    </tr>
                                    <tr>
                                        <td><strong style="color:#38bdf8;">BAF</strong></td>
                                        <td class="price-badge down">30,850</td>
                                        <td class="price-badge down">-0.16%</td>
                                        <td>593k</td>
                                        <td style="color:#34d399;">50.5%</td>
                                        <td><span style="color:#fbbf24; font-weight:700;">🟡 STANDBY</span></td>
                                    </tr>
                                    <tr>
                                        <td><strong style="color:#38bdf8;">IDC</strong></td>
                                        <td class="price-badge down">34,600</td>
                                        <td class="price-badge down">-0.86%</td>
                                        <td>232.7k</td>
                                        <td style="color:#34d399;">48.5%</td>
                                        <td><span style="color:#fbbf24; font-weight:700;">🟡 STANDBY</span></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <!-- Radar 5 Cấp Độ An Ninh -->
                        <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 9px; display: flex; flex-direction: column; gap: 5px;">
                            <div style="font-size: 11px; font-weight: 800; color: #f8fafc; display: flex; justify-content: space-between;">
                                <span>RADAR 5 CẤP ĐỘ NGUY HIỂM</span>
                                <span style="color: #34d399;">● CẤP 1 (AN TOÀN)</span>
                            </div>
                            <div style="display: flex; gap: 4px;">
                                <div style="flex: 1; height: 6px; border-radius: 3px; background: #10b981; box-shadow: 0 0 6px #10b981;"></div>
                                <div style="flex: 1; height: 6px; border-radius: 3px; background: rgba(148, 163, 184, 0.2);"></div>
                                <div style="flex: 1; height: 6px; border-radius: 3px; background: rgba(148, 163, 184, 0.2);"></div>
                                <div style="flex: 1; height: 6px; border-radius: 3px; background: rgba(148, 163, 184, 0.2);"></div>
                                <div style="flex: 1; height: 6px; border-radius: 3px; background: rgba(148, 163, 184, 0.2);"></div>
                            </div>
                            <div style="font-size: 10.5px; color: #94a3b8; line-height: 1.35;">
                                🟢 <strong>Cấp 1 — An toàn tuyệt đối</strong>: 100% tiền mặt, miễn nhiễm hoàn toàn với mọi biến động tiêu cực của thị trường.
                            </div>
                        </div>

                        <!-- ALEX WALL STREET DESK (STANDBY SLOT) -->
                        <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(15, 23, 42, 0.9)); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 9px; padding: 11px; display: flex; flex-direction: column; gap: 6px;">
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <span style="font-size: 15px;">🗽</span>
                                    <span style="font-size: 11.5px; font-weight: 800; color: #fbbf24;">Alex — Phố Wall &amp; Global Desk</span>
                                </div>
                                <span style="font-size: 10px; font-weight: 800; color: #fbbf24; background: rgba(245, 158, 11, 0.2); padding: 2px 6px; border-radius: 4px;">STANDBY</span>
                            </div>
                            <div style="font-size: 10.5px; color: #cbd5e1;">
                                Phiên New York mở lúc <strong>21:30 Tối</strong> (Còn: <strong id="alex-ny-countdown" style="color: #fbbf24;">{wr_ny_countdown}</strong>).
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px;">
                                <div style="background: rgba(15, 23, 42, 0.7); padding: 4px 6px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.15);">
                                    <div style="font-size: 10.5px; font-weight: 800; color: #38bdf8;">NVDA (Blackwell)</div>
                                </div>
                                <div style="background: rgba(15, 23, 42, 0.7); padding: 4px 6px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.15);">
                                    <div style="font-size: 10.5px; font-weight: 800; color: #38bdf8;">AVGO (ASIC AI)</div>
                                </div>
                                <div style="background: rgba(15, 23, 42, 0.7); padding: 4px 6px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.15);">
                                    <div style="font-size: 10.5px; font-weight: 800; color: #38bdf8;">MSFT (Azure AI)</div>
                                </div>
                                <div style="background: rgba(15, 23, 42, 0.7); padding: 4px 6px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.15);">
                                    <div style="font-size: 10.5px; font-weight: 800; color: #38bdf8;">PLTR (AIP Def)</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- ========================================================
             TAB 4: BÀN CHỈ HUY MASTER CIO JAMES (SPLIT-VIEW 2 CỘT)
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
                        <button class="cmd-chip" onclick="sendQuickCommand('/tcbs')">🏦 /tcbs (Két 20.16M)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/danhmuc')">📊 /danhmuc (100% Cash)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/solenh')">⚡ /solenh (Nhịp 1 HDB & MSH)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/hop HDB')">🏦 /hop HDB (Soi BCTC HDB)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/hop MSH')">🧵 /hop MSH (Soi BCTC MSH)</button>
                        <button class="cmd-chip" onclick="sendQuickCommand('/hop BAF')">🐷 /hop BAF (Soi BCTC BAF)</button>
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
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 20px; font-weight: 800; color: #34d399; margin-top: 2px;">14,510,422 ₫</div>
                            <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Tỷ trọng: 72% Cash • 28% CP (200 CP: HDB, MSH)</div>
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
             TAB 4: PHÒNG HỌP THƯỢNG ĐỈNH TRỰC TUYẾN (APEX WAR ROOM)
             ======================================================== -->
        <section id="tab-summit-room" class="tab-pane">
            <div class="summit-container">
                <!-- 1. HEADER CARD & REAL-TIME TIMER -->
                <div class="summit-header-card">
                    <div class="summit-title-box">
                        <div class="summit-tag-row">
                            <span class="summit-tag summit-tag-gold">👑 CHỦ TỌA: CHỦ TỊCH TRẦN QUỐC THIÊN PHƯỚC</span>
                            <span class="summit-tag summit-tag-blue">🎖️ CHỦ TRÌ: MASTER CIO JAMES & PALMER</span>
                            <span class="summit-tag summit-tag-inspector">🛡️ GIÁM SÁT VIÊN THƯỜNG TRỰC: TỔNG KIỂM SÁT VIÊN TRỌNG (BAN 12)</span>
                        </div>
                        <h2 class="summit-title" id="summit-main-title">
                            <span>🏛️</span> <span>ĐẠI HỘI NGHỊ THƯỢNG ĐỈNH TOÀN DOANH NGHIỆP APEX</span>
                        </h2>
                        <div class="summit-sub">
                            <span>⏱️ Khung giờ: <strong>21h00 – 21h30 (30 Phút)</strong></span>
                            <span>🏦 Tài khoản: <strong>TCBS 105C307855</strong> (14,510,422 ₫ Tiền Mặt • 5,650,000 ₫ Cổ Phiếu)</span>
                            <span>⚖️ Thể chế: <strong>100% Tuân thủ Hiến Chương V1.0</strong></span>
                        </div>
                    </div>
                    <div class="summit-timer-card">
                        <div class="summit-timer-label" id="summit-timer-lbl">⏱️ ĐỒNG HỒ ĐẾM NGƯỢC GIỜ G</div>
                        <div class="summit-timer-val" id="summit-timer-val">21:00:00</div>
                        <div class="summit-timer-sub" id="summit-timer-sub">Đồng bộ nguyên tử theo máy chủ</div>
                    </div>
                </div>

                <!-- 2. PHASES & STEPS TIMELINE TRACKER -->
                <div class="summit-phases-card">
                    <div class="summit-phases-header">
                        <span>📋 NGHỊ TRÌNH 2 GIAI ĐOẠN / 8 BƯỚC ĐỊNH CHẾ (30 PHÚT)</span>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <button onclick="toggleSummitPreview()" id="btn-toggle-preview" style="background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); color: #38bdf8; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px; cursor: pointer;">
                                👁️ Xem Trước Toàn Bộ (Preview)
                            </button>
                            <span id="summit-phase-indicator" style="color: #38bdf8; font-weight: 800;">Giai Đoạn 1: Báo Cáo Chuẩn Bị</span>
                        </div>
                    </div>
                    <div class="summit-steps-grid" id="summit-steps-container">
                        <div class="summit-step-item active" id="step-node-1">
                            <div class="summit-step-min">00 - 03m</div>
                            <div class="summit-step-lbl">1. Khai mạc & Đối soát Tiền Mặt 20M</div>
                        </div>
                        <div class="summit-step-item" id="step-node-2">
                            <div class="summit-step-min">03 - 07m</div>
                            <div class="summit-step-lbl">2. Vĩ mô Phố Wall sập & SBV</div>
                        </div>
                        <div class="summit-step-item" id="step-node-3">
                            <div class="summit-step-min">08 - 12m</div>
                            <div class="summit-step-lbl">3. Hiệp 1: Đại chiến MSH (Dệt may vs Lạm phát)</div>
                        </div>
                        <div class="summit-step-item" id="step-node-4">
                            <div class="summit-step-min">13 - 17m</div>
                            <div class="summit-step-lbl">4. Hiệp 2: Đại chiến BAF (Biên lãi vs Nợ 2.4k tỷ)</div>
                        </div>
                        <div class="summit-step-item" id="step-node-5">
                            <div class="summit-step-min">18 - 22m</div>
                            <div class="summit-step-lbl">5. Hiệp 3: Đại chiến HDB (NIM 5.2% vs Nợ nhóm 2)</div>
                        </div>
                        <div class="summit-step-item" id="step-node-6">
                            <div class="summit-step-min">23 - 27m</div>
                            <div class="summit-step-lbl">6. Hiệp 4: Đại chiến IDC (Tiền trả trước 5.2k tỷ)</div>
                        </div>
                        <div class="summit-step-item" id="step-node-7">
                            <div class="summit-step-min">28 - 29m</div>
                            <div class="summit-step-lbl">7. Bảo lưu thể chế & Bỏ phiếu độc lập</div>
                        </div>
                        <div class="summit-step-item" id="step-node-8">
                            <div class="summit-step-min">29 - 30m</div>
                            <div class="summit-step-lbl">8. Trọng chứng thực 100% Làm thật & Bế mạc</div>
                        </div>
                    </div>
                </div>

                <!-- 3. SPLIT-VIEW WAR ROOM (70% - 30%) -->
                <div class="summit-war-split">
                    <!-- CỘT TRÁI: LIVE DIALOGUE STREAM -->
                    <div class="summit-feed-panel">
                        <div class="summit-feed-header">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span class="pulse-dot" style="background: #ef4444; box-shadow: 0 0 10px #ef4444;"></span>
                                <h3 style="font-size: 14.5px; font-weight: 800; color: #fff;">LUỒNG PHÁT BIỂU & TRANH BIỆN THỜI GIAN THỰC</h3>
                            </div>
                            <span id="summit-feed-counter" style="font-size: 11.5px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">
                                Đang tải luồng...
                            </span>
                        </div>
                        <div class="summit-feed-body" id="summit-feed-container">
                            <!-- Messages will be rendered here dynamically -->
                        </div>
                        <div class="summit-input-panel">
                            <div class="summit-input-label">
                                <span>👑</span> <span>Chủ Tịch Trần Quốc Thiên Phước Can Thiệp / Chỉ Thị Trực Tiếp Vào Phòng Họp:</span>
                            </div>
                            <div class="summit-input-row">
                                <input type="text" id="summit-chairman-input" class="summit-input-field" 
                                       placeholder="Gõ câu hỏi, chất vấn hoặc chỉ thị trực tiếp cho Hội đồng..." 
                                       onkeydown="if(event.key === 'Enter') sendChairmanSummitDirective();" />
                                <button id="summit-btn-send-directive" class="summit-btn-send" onclick="sendChairmanSummitDirective()">
                                    <span>🚀</span> <span>Gửi Chỉ Thị</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- CỘT PHẢI: BÀN KIỂM SÁT TRỌNG & BIỂU QUYẾT -->
                    <div class="summit-side-col">
                        <!-- Card 1: Bàn Kiểm Sát Trọng -->
                        <div class="summit-side-card" style="border-color: rgba(245, 158, 11, 0.4);">
                            <div class="summit-side-title" style="color: #fbbf24;">
                                <span>🛡️</span> <span>Bàn Kiểm Sát Viên Trọng (Ban 12)</span>
                            </div>
                            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 8px; padding: 10px 12px; margin-bottom: 12px;">
                                <div style="font-size: 11px; font-weight: 800; color: #f59e0b; text-transform: uppercase;">
                                    TỔNG KIỂM SÁT VIÊN THƯỜNG TRỰC BẤT BIẾN
                                </div>
                                <div style="font-size: 12px; color: #fef3c7; margin-top: 4px;">
                                    Đảm bảo 100% "Làm thật việc thật", không vi phạm bất kỳ điều cấm nào trong Hiến Chương Doanh Nghiệp.
                                </div>
                            </div>
                            <div id="summit-inspector-rules">
                                <div class="inspector-rule-item">
                                    <span class="inspector-rule-text">1. Tuyệt đối bảo vệ vốn (Stop &le; 6.8%)</span>
                                    <span class="inspector-rule-badge">ĐẠT CHUẨN</span>
                                </div>
                                <div class="inspector-rule-item">
                                    <span class="inspector-rule-text">2. Tiền thật OCF/LNST &gt; 1.15x</span>
                                    <span class="inspector-rule-badge">ĐẠT CHUẨN</span>
                                </div>
                                <div class="inspector-rule-item">
                                    <span class="inspector-rule-text">3. 1 lô 100 CP &le; 33% NAV (Giá &le; 36k)</span>
                                    <span class="inspector-rule-badge">ĐẠT CHUẨN</span>
                                </div>
                                <div class="inspector-rule-item">
                                    <span class="inspector-rule-text">4. Khung Giờ Vàng 14h00-14h25</span>
                                    <span class="inspector-rule-badge">ĐẠT CHUẨN</span>
                                </div>
                                <div class="inspector-rule-item">
                                    <span class="inspector-rule-text">5. Quyền quyết định tối cao của Chủ tịch</span>
                                    <span class="inspector-rule-badge">ĐẠT CHUẨN</span>
                                </div>
                            </div>
                        </div>

                        <!-- Card 2: Bảng Biểu Quyết Điện Tử & Sổ Lệnh Bắn Tỉa Vòng 2 -->
                        <div class="summit-side-card">
                            <div class="summit-side-title">
                                <span>📊</span> <span>Sổ Lệnh Bắn Tỉa Vòng 2 & Biểu Quyết</span>
                            </div>
                            <div id="summit-voting-container">
                                <!-- Stock voting cards rendered here -->
                            </div>
                        </div>

                        <!-- Card 2.5: Phê Chuẩn Nghị Quyết Của Chủ Tịch (BƯỚC 3) -->
                        <div class="summit-side-card" style="border: 1px solid rgba(234, 179, 8, 0.45); background: linear-gradient(180deg, rgba(234, 179, 8, 0.08) 0%, rgba(15, 23, 42, 0.6) 100%);">
                            <div class="summit-side-title" style="color: #fbbf24;">
                                <span>👑</span> <span>Phê Chuẩn Sổ Lệnh — Chủ Tịch Phước Trần</span>
                            </div>
                            <div id="summit-approval-box">
                                <div id="summit-approval-status" style="font-size: 11.5px; color: #fef3c7; margin-bottom: 12px; line-height: 1.5;">
                                    Trạng thái: <strong style="color: #f59e0b;">⏳ Chờ Chủ Tịch Ký Phê Duyệt</strong>
                                </div>
                                <button id="btn-approve-summit" class="summit-action-btn-gold" onclick="approveSummitResolution()">
                                    <span>✍️</span> <span>KÝ PHÊ DUYỆT SỔ LỆNH SÁNG THỨ HAI</span>
                                </button>
                            </div>
                        </div>

                        <!-- Card 3: Nút Xem Nghị Quyết Thượng Đỉnh -->
                        <div class="summit-side-card" style="text-align: center;">
                            <button class="summit-action-btn-large" onclick="openReportModal('08_Master_Investment_CIO/2026-11-08_Ke_Hoach_Nghi_Trinh_Thuong_Dinh_21h00_James.md')">
                                <span>📖</span> <span>XEM TOÀN VĂN NGHỊ QUYẾT 21H30</span>
                            </button>
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
            if (tabId === 'war-room') {{
                initTacticalWarRoom();
            }}
            if (tabId === 'summit-room') {{
                initSummitRoom();
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

            // 4. Biến đổi tất cả các đường dẫn báo cáo / kịch bản thành Thẻ Tương Tác Bấm Để Xem Báo Cáo Toàn Văn
            const seenReportPaths = new Set();
            function createReportCardHtml(rawPath) {{
                const cleanPath = rawPath.replace(/[`*]/g, '').trim();
                if (!cleanPath || !cleanPath.endsWith('.md')) return '';

                let icon = '📑';
                let label = 'BÁO CÁO CHI TIẾT THEO YÊU CẦU CỦA CHỦ TỊCH';
                let title = '';

                if (cleanPath.includes('Viral_Script') || cleanPath.includes('11_Viral_Content_Creation')) {{
                    icon = '🎬';
                    label = 'KỊCH BẢN VIDEO VIRAL TIKTOK / REELS — BAN 11 (KHÁNH & BẢO)';
                    title = 'Kịch Bản Video Viral 60s TikTok & Shorts';
                }} else if (cleanPath.includes('Hien_Daily_Review') || cleanPath.includes('02_BCTC_Equity_Research')) {{
                    icon = '🌸';
                    label = 'RÀ SOÁT BCTC & DÒNG TIỀN THẬT OCF — BAN 10 (HIỀN)';
                    title = 'Báo Cáo Kiểm Toán BCTC Chuyên Sâu & Tiền Thật';
                }} else if (cleanPath.includes('CBTT_Radar')) {{
                    icon = '🔍';
                    label = 'RADAR CÔNG BỐ THÔNG TIN & BCTC ĐÊM QUA — BAN 10';
                    title = 'Báo Cáo Radar CBT & Quan Hệ Cổ Đông';
                }} else if (cleanPath.includes('Macro_Report') || cleanPath.includes('01_Macro') || cleanPath.includes('Weekend_Market_Intel')) {{
                    icon = '🌐';
                    label = 'PHÂN TÍCH VĨ MÔ & CHÍNH SÁCH TIỀN TỆ SBV — BAN 1';
                    title = 'Báo Cáo Vĩ Mô, Tỷ Giá & Luân Chuyển Ngành';
                }} else if (cleanPath.includes('Master_CIO') || cleanPath.includes('Final_Decision') || cleanPath.includes('08_Master') || cleanPath.includes('Blotter')) {{
                    icon = '🎖️';
                    label = 'QUYẾT ĐỊNH ĐẦU TƯ TỐI CAO & SỔ LỆNH MASTER — MASTER CIO JAMES';
                    title = 'Sổ Lệnh Master Blotter & Phân Bổ Vốn Thống Nhất';
                }} else if (cleanPath.includes('Specialist_Decision') || cleanPath.includes('07_Daily_Specialist')) {{
                    icon = '⚡';
                    label = 'KẾ HOẠCH TÁC CHIẾN KHUNG GIỜ VÀNG — MINH QUÂN BAN 7 VN';
                    title = 'Chiến Lược Ra Lệnh & Tối Ưu Lợi Nhuận Trước ATO';
                }} else if (cleanPath.includes('IC_Decision') || cleanPath.includes('Quant_Risk') || cleanPath.includes('04_Investment')) {{
                    icon = '⚖️';
                    label = 'QUẢN TRỊ RỦI RO ĐỊNH LƯỢNG & HỘI ĐỒNG ĐẦU TƯ — BAN 4';
                    title = 'Nghị Quyết Hội Đồng & Định Cỡ Vị Thế ATR Risk-Parity';
                }} else if (cleanPath.includes('Trong') || cleanPath.includes('12_Institutional_Ombudsman')) {{
                    icon = '🏛️';
                    label = 'TỔNG KIỂM SÁT THỂ CHẾ & HẠ TẦNG — BAN 12 TRỌNG';
                    title = 'Biên Bản Giám Sát Sức Chứa Dữ Liệu & Toàn Vẹn Hệ Thống';
                }} else if (cleanPath.includes('Mentor_Briefing') || cleanPath.includes('06_Investor_Academy')) {{
                    icon = '💡';
                    label = 'HỌC VIỆN ĐÀO TẠO & KÈM CẶP THỰC CHIẾN — BAN 6';
                    title = 'Bản Tin Khai Sáng Buổi Sáng Cho Nhà Đầu Tư';
                }} else if (cleanPath.includes('Learning') || cleanPath.includes('Evolution') || cleanPath.includes('HEURISTICS')) {{
                    icon = '🧠';
                    label = 'BÁCH KHOA TOÀN THƯ & TIẾN HÓA THÍCH NGHI — BAN 5';
                    title = 'Bách Khoa Toàn Thư Tri Thức & 105 Mẹo Bất Hủ';
                }}

                if (!title) {{
                    const fileName = cleanPath.split('/').pop().replace('.md', '');
                    title = fileName.replace(/^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}_/, '').replace(/_/g, ' ');
                }}

                const dateMatch = cleanPath.match(/([0-9]{{4}})-([0-9]{{2}})-([0-9]{{2}})/);
                let dateBadge = '';
                if (dateMatch) {{
                    dateBadge = `<span style="font-size: 11px; color: #fbbf24; background: rgba(251, 191, 36, 0.12); padding: 2px 7px; border-radius: 4px; font-weight: 600;">📅 Ngày ${{dateMatch[3]}}/${{dateMatch[2]}}/${{dateMatch[1]}}</span>`;
                }}

                return `
<div class="chat-open-report-card" onclick="openReportModal('${{cleanPath}}')">
    <div class="chat-open-report-icon-box">
        <span>${{icon}}</span>
    </div>
    <div class="chat-open-report-body">
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <div class="chat-open-report-label">${{label}}</div>
            ${{dateBadge}}
        </div>
        <div class="chat-open-report-name">${{title}}</div>
        <div class="chat-open-report-path">📂 ${{cleanPath}}</div>
    </div>
    <button class="chat-open-report-btn" onclick="event.stopPropagation(); openReportModal('${{cleanPath}}')">
        <span>📖</span> BẤM ĐỂ XEM TOÀN VĂN NGAY ➔
    </button>
</div>
                `;
            }}

            // Regex 1: Thay thế các dòng mang định dạng "Kịch bản chi tiết:", "Báo cáo chi tiết:", "Nhấn vào đây để xem toàn văn:"
            const reportLineRegex = /^[ \\t]*(?:[•\\-*👉]|\\d+\\.)?[ \\t]*(?:\\*{{0,2}}(?:Kịch bản chi tiết|Báo cáo chi tiết|Tệp báo cáo|Tệp tin|Đường dẫn lưu trữ|Đường dẫn|Nhấn vào đây để xem toàn văn báo cáo|Nhấn vào đây để xem toàn văn kịch bản|Nhấn vào đây để xem toàn văn|Nhấn vào đây để xem|Bấm để xem toàn văn|Bấm để xem|Xem toàn văn|File)[:\\s*]*(?:\\*{{0,2}}))?[ \\t]*`?((?:11_Viral_Content_Creation|VN_Market\\/[a-zA-Z0-9_\\-]+|[0-9]{{2}}_[a-zA-Z0-9_\\-]+)[^\\s`*()\\[\\]"':<>|]+\\.md)`?[ \\t]*$/gmi;

            textToParse = textToParse.replace(reportLineRegex, (match, path) => {{
                const clean = path.replace(/[`*]/g, '').trim();
                if (seenReportPaths.has(clean)) return '';
                seenReportPaths.add(clean);
                return `\n\n${{createReportCardHtml(clean)}}\n\n`;
            }});

            // Regex 2: Kiểm tra các đường dẫn báo cáo thể chế còn sót lại trong toàn văn
            const generalPathRegex = /(`?((?:11_Viral_Content_Creation|VN_Market\\/[a-zA-Z0-9_\\-]+|[0-9]{{2}}_[a-zA-Z0-9_\\-]+)[^\\s`*()\\[\\]"':<>|]+\\.md)`?)/g;
            let mReport;
            let extraReportCards = '';
            while ((mReport = generalPathRegex.exec(rawText)) !== null) {{
                const clean = mReport[2].replace(/[`*]/g, '').trim();
                if (!seenReportPaths.has(clean)) {{
                    seenReportPaths.add(clean);
                    extraReportCards += `\n${{createReportCardHtml(clean)}}`;
                }}
            }}

            // Render Markdown cho phần còn lại
            const parsedMd = window.marked ? marked.parse(textToParse) : `<pre style="white-space: pre-wrap;">${{textToParse}}</pre>`;
            htmlOutput += parsedMd + extraReportCards;
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

            // 4. Lọc theo Từ Khóa (Bao gồm cả Tiêu đề, Tóm tắt, Tên tệp và Mã Cổ Phiếu Tickers)
            if (currentSearchQuery) {{
                finalFiltered = finalFiltered.filter(r => 
                    (r.title && r.title.toLowerCase().includes(currentSearchQuery)) ||
                    (r.preview && r.preview.toLowerCase().includes(currentSearchQuery)) ||
                    (r.file_name && r.file_name.toLowerCase().includes(currentSearchQuery)) ||
                    (r.tickers && Array.isArray(r.tickers) && r.tickers.some(t => t.toLowerCase().includes(currentSearchQuery)))
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


        // ========================================================
        // TAB 4: SUMMIT MEETING REAL-TIME CLIENT ENGINE
        // ========================================================
        let summitPreviewMode = false;
        let lastSummitMsgCount = 0;
        let summitPollTimer = null;

        function toggleEvidenceCard(cardId) {{
            const el = document.getElementById(cardId);
            const btn = document.getElementById('btn-' + cardId);
            if (!el) return;
            if (el.style.display === 'none') {{
                el.style.display = 'block';
                if (btn) btn.innerText = '▲ THU GỌN BẰNG CHỨNG';
            }} else {{
                el.style.display = 'none';
                if (btn) btn.innerText = '▼ MỞ RỘNG BẰNG CHỨNG';
            }}
        }}

        function toggleSummitPreview() {{
            summitPreviewMode = !summitPreviewMode;
            const btn = document.getElementById('btn-toggle-preview');
            if (btn) {{
                btn.innerText = summitPreviewMode ? '🔴 Trở Về Thời Gian Thực' : '👁️ Xem Trước Toàn Bộ (Preview)';
                btn.style.background = summitPreviewMode ? 'rgba(239, 68, 68, 0.2)' : 'rgba(56, 189, 248, 0.12)';
                btn.style.color = summitPreviewMode ? '#ef4444' : '#38bdf8';
                btn.style.borderColor = summitPreviewMode ? '#ef4444' : 'rgba(56, 189, 248, 0.3)';
            }}
            pollSummitMeeting();
        }}

        async function pollSummitMeeting() {{
            try {{
                const url = '/api/summit_meeting' + (summitPreviewMode ? '?preview=1' : '');
                const res = await fetch(url);
                if (!res.ok) return;
                const data = await res.json();
                renderSummitMeetingState(data);
            }} catch (e) {{
                console.error('Lỗi poll summit meeting:', e);
            }}
        }}

        function renderSummitMeetingState(data) {{
            if (!data) return;

            // 1. Cập nhật Timer & Badge
            const timerVal = document.getElementById('summit-timer-val');
            const timerLbl = document.getElementById('summit-timer-lbl');
            const timerSub = document.getElementById('summit-timer-sub');
            const phaseInd = document.getElementById('summit-phase-indicator');
            const navBadge = document.getElementById('summit-nav-badge');

            if (data.meeting_status === 'WAITING_COUNTDOWN') {{
                const totalSec = data.countdown_seconds || 0;
                const m = Math.floor(totalSec / 60);
                const s = totalSec % 60;
                if (timerVal) timerVal.innerText = `${{String(m).padStart(2,'0')}}m : ${{String(s).padStart(2,'0')}}s`;
                if (timerLbl) timerLbl.innerText = '⏱️ ĐỒNG HỒ ĐẾM NGƯỢC GIỜ G';
                if (timerSub) timerSub.innerText = 'Khai mạc chính xác lúc 21h00:00';
                if (phaseInd) phaseInd.innerText = 'Phòng chờ sẵn sàng 100%';
                if (navBadge) {{
                    navBadge.innerText = '⏳ CHỜ 21H00';
                    navBadge.style.color = '#f59e0b';
                }}
            }} else if (data.meeting_status === 'LIVE_IN_PROGRESS') {{
                const curMin = data.current_minute || 0;
                if (timerVal) timerVal.innerText = `PHÚT ${{curMin}} / 30`;
                if (timerLbl) timerLbl.innerText = '🔴 ĐANG HỌP TRỰC TIẾP';
                if (timerSub) timerSub.innerText = 'Đồng bộ nguyên tử theo máy chủ';
                if (phaseInd) phaseInd.innerText = data.current_phase === 1 ? 'Giai Đoạn 1: Báo Cáo Chuẩn Bị' : 'Giai Đoạn 2: Tranh Biện & Biểu Quyết';
                if (navBadge) {{
                    navBadge.innerText = `● LIVE (P.${{curMin}})`;
                    navBadge.style.color = '#ef4444';
                }}
            }} else {{
                if (timerVal) timerVal.innerText = '30m : 00s (BẾ MẠC)';
                if (timerLbl) timerLbl.innerText = '🏁 HỘI NGHỊ ĐÃ KẾT THÚC';
                if (timerSub) timerSub.innerText = 'Nghị quyết sẵn sàng ký duyệt';
                if (phaseInd) phaseInd.innerText = 'Đã hoàn tất 100% nghị trình';
                if (navBadge) {{
                    navBadge.innerText = '✅ HOÀN TẤT';
                    navBadge.style.color = '#10b981';
                }}
            }}

            // 2. Cập nhật Step Tracker (1 đến 8)
            const curStep = data.current_step || 1;
            for (let i = 1; i <= 8; i++) {{
                const el = document.getElementById('step-node-' + i);
                if (el) {{
                    el.classList.remove('active', 'completed');
                    if (i < curStep) el.classList.add('completed');
                    else if (i === curStep) el.classList.add('active');
                }}
            }}

            // 3. Render Luồng Tin Nhắn
            const container = document.getElementById('summit-feed-container');
            const counter = document.getElementById('summit-feed-counter');
            const msgs = data.timeline_stream || [];

            if (counter) counter.innerText = `${{msgs.length}} phát biểu ghi nhận`;

            if (container) {{
                // Chỉ render lại nếu số lượng tin nhắn thay đổi hoặc lần đầu
                if (msgs.length !== lastSummitMsgCount) {{
                    container.innerHTML = msgs.map(m => {{
                        let cardClass = 'summit-msg-card';
                        if (m.sender_name && m.sender_name.includes('Chủ tịch')) cardClass += ' msg-chairman';
                        else if (m.sender_name && m.sender_name.includes('Trọng')) cardClass += ' msg-inspector';
                        else if (m.badge && (m.badge.includes('TRANH BIỆN') || m.badge.includes('KẺ THÙ') || m.badge.includes('BẢO LƯU') || m.badge.includes('PHẢN ĐỐI'))) cardClass += ' msg-debate';
                        else if (m.badge && (m.badge.includes('PHÁP Y') || m.badge.includes('DỮ LIỆU') || m.badge.includes('BCTC'))) cardClass += ' msg-forensic';
                        else if (m.sender_name && m.sender_name.includes('Minh Quân')) cardClass += ' msg-tactical';
                        else if (m.badge && (m.badge.includes('ĐỊNH LƯỢNG') || m.badge.includes('PHÁN QUYẾT') || m.badge.includes('ĐỐI SOÁT') || m.badge.includes('ĐỀ XUẤT') || m.badge.includes('RỦI RO'))) cardClass += ' msg-quant';

                        let badgeHtml = '';
                        if (m.badge) {{
                            badgeHtml = `<span style="background: ${{m.badge_color || '#38bdf8'}}22; color: ${{m.badge_color || '#38bdf8'}}; border: 1px solid ${{m.badge_color || '#38bdf8'}}55; padding: 2px 8px; border-radius: 9999px; font-size: 10px; font-weight: 800;">${{m.badge}}</span>`;
                        }}

                        let highlightHtml = '';
                        if (m.highlight) {{
                            highlightHtml = `<div class="summit-msg-highlight">📌 <strong>Điểm Nhấn:</strong> ${{m.highlight}}</div>`;
                        }}

                        let metricsHtml = '';
                        if (m.metrics && typeof m.metrics === 'object') {{
                            const chips = Object.entries(m.metrics).map(([k, v]) => 
                                `<span style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 4px; padding: 2px 7px; font-size: 11px; font-family: 'JetBrains Mono', monospace; color: #cbd5e1;"><strong style="color: #38bdf8;">${{k}}:</strong> ${{v}}</span>`
                            ).join(' ');
                            metricsHtml = `<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; padding-top: 8px; border-top: 1px dashed rgba(255,255,255,0.1);">${{chips}}</div>`;
                        }}

                        let formattedContent = (m.content || '')
                            .replace(/\\*\\*(.*?)\\*\\*/g, '<strong style="color: #f8fafc;">$1</strong>')
                            .split(String.fromCharCode(10) + '- ').join('<br/>• ')
                            .split(String.fromCharCode(10)).join('<br/>');

                        let evidenceHtml = '';
                        if (m.evidence_card) {{
                            const ev = m.evidence_card;
                            const cardId = 'ev-card-' + (m.id || Math.random().toString(36).substr(2, 9));

                            const bs = ev.balance_sheet || {{}};
                            const bsChips = Object.entries(bs).map(([k, v]) => 
                                `<span style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.2); padding: 3px 8px; border-radius: 4px; font-size: 11px; font-family: 'JetBrains Mono', monospace;"><strong style="color: #7dd3fc;">${{k}}:</strong> <span style="color: #f8fafc;">${{v}}</span></span>`
                            ).join(' ');

                            const peer = ev.peer_comparison || {{}};
                            const peerRows = (peer.comparison_rows || []).map(r => `
                                <tr>
                                    <td style="font-weight: 600; color: #f8fafc;">${{r.criteria}}</td>
                                    <td style="color: #34d399; font-weight: 700; font-family: 'JetBrains Mono', monospace;">${{r.stock}}</td>
                                    <td style="color: #94a3b8; font-family: 'JetBrains Mono', monospace;">${{r.peer}}</td>
                                    <td style="color: #fbbf24; font-weight: 700;">${{r.verdict}}</td>
                                </tr>
                            `).join('');

                            const checks = ev.forensic_checks || {{}};
                            const checkBoxes = Object.entries(checks).map(([k, v]) => `
                                <div class="evidence-check-item">
                                    <div class="evidence-check-k">${{k.replace(/_/g, ' ')}}</div>
                                    <div class="evidence-check-v">${{v}}</div>
                                </div>
                            `).join('');

                            evidenceHtml = `
                                <div class="summit-evidence-box">
                                    <div class="summit-evidence-toggle-btn" onclick="toggleEvidenceCard('${{cardId}}')">
                                        <span class="summit-evidence-title">📑 THẺ BẰNG CHỨNG PHÁP Y BCTC SỐNG — ${{ev.ticker}} (KIỂM TOÁN BIG 4)</span>
                                        <span id="btn-${{cardId}}" style="color: #38bdf8; font-weight: 700; font-size: 11px;">▲ THU GỌN BẰNG CHỨNG</span>
                                    </div>
                                    <div id="${{cardId}}" class="summit-evidence-content" style="display: block;">
                                        <div>
                                            <div style="font-size: 10.5px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px;">1. BẢNG CÂN ĐỐI & DÒNG TIỀN KIỂM TOÁN THẬT Q3/2026:</div>
                                            <div style="display: flex; flex-wrap: wrap; gap: 6px;">${{bsChips}}</div>
                                        </div>

                                        <div style="margin-top: 6px;">
                                            <div style="font-size: 10.5px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px;">2. ĐỐI ĐẦU TRỰC DIỆN ĐỐI THỦ CÙNG NGÀNH (${{peer.peer_name || ''}}):</div>
                                            <div style="overflow-x: auto; background: rgba(0,0,0,0.2); border-radius: 6px; padding: 6px;">
                                                <table class="evidence-peer-table">
                                                    <thead>
                                                        <tr>
                                                            <th>Tiêu Chí Pháp Y</th>
                                                            <th>${{ev.ticker}} (Đề Xuất)</th>
                                                            <th>Đối Thủ Cùng Ngành</th>
                                                            <th>Phán Quyết Ban 2</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        ${{peerRows}}
                                                    </tbody>
                                                </table>
                                            </div>
                                            <div style="margin-top: 6px; font-size: 11px; color: #7dd3fc; font-style: italic;">
                                                💡 <strong>Kết luận:</strong> ${{peer.conclusion || ''}}
                                            </div>
                                        </div>

                                        <div style="margin-top: 6px;">
                                            <div style="font-size: 10.5px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px;">3. BỘ RADAR KIỂM ĐỊNH GIAN LẬN KẾ TOÁN (BENEISH M & ALTMAN Z):</div>
                                            <div class="evidence-check-grid">${{checkBoxes}}</div>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }}

                        return `
                            <div class="${{cardClass}}">
                                <div class="summit-msg-header">
                                    <div class="summit-msg-author">
                                        <div class="summit-msg-avatar">${{m.avatar || '👤'}}</div>
                                        <div>
                                            <div class="summit-msg-name">${{m.sender_name}}</div>
                                            <div class="summit-msg-dept">${{m.department || ''}} • ${{m.role || ''}}</div>
                                        </div>
                                    </div>
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        ${{badgeHtml}}
                                        <span class="summit-msg-time">${{m.time_str}}</span>
                                    </div>
                                </div>
                                <div class="summit-msg-content">${{formattedContent}}</div>
                                ${{metricsHtml}}
                                ${{evidenceHtml}}
                                ${{highlightHtml}}
                            </div>
                        `;
                    }}).join('');

                    // Tự động cuộn xuống dưới cùng nếu có tin mới
                    container.scrollTop = container.scrollHeight;
                    lastSummitMsgCount = msgs.length;
                }}
            }}

            // 4. Render Bảng Biểu Quyết & Sổ Lệnh Bắn Tỉa Vòng 2 (BƯỚC 3)
            const voteContainer = document.getElementById('summit-voting-container');
            const votes = data.voting_board || [];
            if (voteContainer) {{
                voteContainer.innerHTML = votes.map(v => {{
                    let tallyHtml = `<span class="summit-vote-tally" style="color: #34d399;">${{v.votes_for}}/12 Nhất Trí</span>`;
                    if (v.votes_against > 0 || (v.status && v.status.includes('CONDITION'))) {{
                        tallyHtml = `<span class="summit-vote-tally" style="color: #f59e0b; background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.3); padding: 2px 6px; border-radius: 4px;">${{v.votes_for}}/12 (${{v.votes_against}} Phiếu Bảo Lưu)</span>`;
                    }}
                    let orderZoneHtml = v.order_zone ? `<div style="color: #38bdf8; font-weight: 700; font-size: 11px; margin-top: 3px;">📍 Vùng Kê LO: ${{v.order_zone}}</div>` : '';
                    let tpRrHtml = (v.take_profit_1 && v.rr_ratio) ? `<div style="color: #a78bfa; font-size: 10.5px; margin-top: 2px;">🎯 TP1: ${{v.take_profit_1}} • TP2: ${{v.take_profit_2 || 'MA20'}} (R:R = ${{v.rr_ratio}})</div>` : '';
                    let actionHtml = v.action ? `<div style="margin-top: 6px; font-size: 11px; color: #7dd3fc; border-top: 1px dashed rgba(255,255,255,0.08); padding-top: 4px;">⚡ ${{v.action}}</div>` : '';
                    let disciplineHtml = v.discipline_note ? `<div style="margin-top: 5px; font-size: 10.5px; color: #fbbf24; background: rgba(245,158,11,0.08); border-left: 2px solid #f59e0b; padding: 4px 6px; border-radius: 4px;">${{v.discipline_note}}</div>` : '';

                    return `
                        <div class="summit-stock-vote-card">
                            <div class="summit-stock-header">
                                <span class="summit-stock-sym">${{v.ticker}}</span>
                                ${{tallyHtml}}
                            </div>
                            <div class="summit-stock-meta">
                                <div><strong>${{v.name}}</strong> (${{v.sector}})</div>
                                ${{orderZoneHtml}}
                                <div style="margin-top: 3px; color: #34d399;">Giá: ${{v.price}} • 1 Lô 100 CP: ${{v.lot_cost}}</div>
                                <div style="color: #94a3b8;">OCF/LNST: ${{v.ocf_lnst}} • Stop: <strong style="color: #f87171;">${{v.stop_loss}}</strong></div>
                                ${{tpRrHtml}}
                                ${{actionHtml}}
                                ${{disciplineHtml}}
                            </div>
                        </div>
                    `;
                }}).join('');
            }}

            // 5. Cập nhật Trạng Thái Phê Chuẩn của Chủ Tịch (BƯỚC 5: XUẤT VĂN KIỆN & CHUYỂN GIAO)
            const appBox = document.getElementById('summit-approval-status');
            const appBtn = document.getElementById('btn-approve-summit');
            if (data.executive_approval && data.executive_approval.status === 'APPROVED') {{
                if (appBox) {{
                    appBox.innerHTML = `
                        <div style="background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3); border-radius: 8px; padding: 12px 14px; margin-bottom: 12px;">
                            <div style="color: #34d399; font-weight: 800; font-size: 12px; display: flex; align-items: center; gap: 6px;">
                                <span>👑</span> <span>NGHỊ QUYẾT ĐÃ ĐƯỢC CHỦ TỊCH KÝ PHÊ DUYỆT CHÍNH THỨC</span>
                            </div>
                            <div style="color: #cbd5e1; font-size: 11px; margin-top: 4px;">Thời gian ký duyệt: <strong>${{data.executive_approval.approval_time}}</strong></div>
                            <div style="color: #fbbf24; font-size: 11px; margin-top: 2px;">🛡️ BAN 12 TRỌNG ĐÃ NIÊM PHONG PHÁP LÝ THỂ CHẾ</div>
                            <div style="color: #38bdf8; font-size: 11px; margin-top: 5px; line-height: 1.4;">🚀 <strong>ĐÃ CHUYỂN GIAO SỔ LỆNH:</strong> 4 mã (HDB, MSH, BAF, IDC) đã khóa sẵn trong hàng đợi tác chiến Khung Giờ Vàng 14h00 cho Minh Quân & James!</div>
                        </div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            <button onclick="openReportModal('08_Master_Investment_CIO/council_resolutions/2026-11-08_Nghi_Quyet_Thuong_Dinh_Da_Ky_Duyet.md')" 
                                    style="flex: 1; min-width: 170px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #ffffff; border: none; border-radius: 6px; padding: 10px 12px; font-size: 11px; font-weight: 800; cursor: pointer; text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; justify-content: center; gap: 6px; box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);">
                                <span>📄</span> <span>Xem Toàn Văn Nghị Quyết</span>
                            </button>
                            <a href="/api/report?path=08_Master_Investment_CIO/council_resolutions/2026-11-08_Nghi_Quyet_Thuong_Dinh_Da_Ky_Duyet.md" target="_blank"
                               style="background: rgba(255, 255, 255, 0.08); color: #cbd5e1; border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 6px; padding: 10px 12px; font-size: 11px; font-weight: 700; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 6px;">
                                <span>📥</span> <span>Tải Markdown</span>
                            </a>
                        </div>
                    `;
                }}
                if (appBtn) {{
                    appBtn.style.display = 'none';
                }}
            }}
        }}

        async function approveSummitResolution() {{
            const btn = document.getElementById('btn-approve-summit');
            if (btn) {{
                btn.disabled = true;
                btn.innerHTML = '<span>⏳</span> <span>Đang Niêm Phong Nghị Quyết & Đóng Dấu Mộc...</span>';
            }}
            try {{
                const res = await fetch('/api/approve_summit_resolution', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ approved_by: 'Chủ tịch Trần Quốc Thiên Phước', timestamp: new Date().toISOString() }})
                }});
                const data = await res.json();
                if (data.ok) {{
                    alert(`🎉 CHÚC MỪNG CHỦ TỊCH!\n\nToàn văn Nghị Quyết Thượng Đỉnh và Sổ Lệnh Bắn Tỉa Vòng 2 đã được Chủ tịch Trần Quốc Thiên Phước chính thức KÝ DUYỆT BAN HÀNH!\n\nBan 12 Tổng Kiểm Sát Viên Trọng đã niêm phong pháp lý thể chế.`);
                    await pollSummitMeeting();
                }} else {{
                    alert('Lỗi phê duyệt: ' + (data.error || 'Không xác định'));
                }}
            }} catch (err) {{
                alert('Lỗi kết nối máy chủ khi phê duyệt: ' + err.message);
            }} finally {{
                if (btn) btn.disabled = false;
            }}
        }}

        async function sendChairmanSummitDirective() {{
            const input = document.getElementById('summit-chairman-input');
            const btn = document.getElementById('summit-btn-send-directive') || document.querySelector('.summit-btn-send');
            if (!input) return;
            const msg = input.value.trim();
            if (!msg) return;

            input.value = '';
            input.disabled = true;
            if (btn) {{
                btn.disabled = true;
                btn.innerHTML = '<span>⏳</span> <span>Đang Phân Tích & Điều Phối...</span>';
            }}

            try {{
                const res = await fetch('/api/summit_message', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ message: msg }})
                }});
                const data = await res.json();
                if (data.ok) {{
                    await pollSummitMeeting();
                    // Cuộn mượt xuống cuối phòng họp để xem ngay lập tức các phản hồi rẽ nhánh
                    const container = document.getElementById('summit-timeline-container');
                    if (container) {{
                        setTimeout(() => {{ container.scrollTop = container.scrollHeight; }}, 80);
                    }}
                    // Đồng bộ sang phòng chat Bàn Chỉ Huy James (Tab 3)
                    if (typeof appendUserMessage === 'function') {{
                        appendUserMessage(msg);
                    }}
                    if (data.james_resp && typeof appendJamesMessage === 'function') {{
                        appendJamesMessage(data.james_resp.content, data.james_resp.time_str);
                    }}
                }} else {{
                    alert('Lỗi gửi chỉ thị: ' + (data.error || 'Không xác định'));
                }}
            }} catch (err) {{
                alert('Lỗi kết nối máy chủ khi gửi chỉ thị: ' + err.message);
            }} finally {{
                input.disabled = false;
                if (btn) {{
                    btn.disabled = false;
                    btn.innerHTML = '<span>🚀</span> <span>Gửi Chỉ Thị</span>';
                }}
                input.focus();
            }}
        }}

        function initSummitRoom() {{
            pollSummitMeeting();
            if (!summitPollTimer) {{
                summitPollTimer = setInterval(pollSummitMeeting, 2500);
            }}
        }}

        // Tự động kiểm tra URL tham số để mở báo cáo nếu có ?open=

        /* ========================================================
           TAB 3: WAR ROOM JAVASCRIPT ENGINE (REALTIME 24/24)
           ======================================================== */
        let warRoomPollingInterval = null;

        function startLiveClockTicker() {{
            function tick() {{
                const now = new Date();
                const pad = n => n < 10 ? '0' + n : n;
                const timeStr = `${{pad(now.getHours())}}:${{pad(now.getMinutes())}}:${{pad(now.getSeconds())}}`;
                const clockEl = document.getElementById('war-room-clock');
                if (clockEl) clockEl.innerText = timeStr;

                // NY Countdown (21:30)
                const nyMinutes = 21 * 60 + 30;
                const currentMin = now.getHours() * 60 + now.getMinutes();
                let diff = nyMinutes - currentMin;
                if (diff < 0) diff += 24 * 60;
                const countStr = `${{Math.floor(diff / 60)}}h ${{pad(diff % 60)}}m`;
                const nyEl = document.getElementById('war-room-ny-countdown');
                if (nyEl) nyEl.innerText = countStr;
                const alexNyEl = document.getElementById('alex-ny-countdown');
                if (alexNyEl) alexNyEl.innerText = countStr;

                // Live dynamic switcher for 3 afternoon stages
                const curMinutes = now.getHours() * 60 + now.getMinutes();
                const s1Card = document.getElementById('stage-1-card');
                const s2Card = document.getElementById('stage-2-card');
                const s3Card = document.getElementById('stage-3-card');
                const s1Badge = document.getElementById('stage-1-badge');
                const s2Badge = document.getElementById('stage-2-badge');
                const s3Badge = document.getElementById('stage-3-badge');

                if (s1Card && s2Card && s3Card) {{
                    if (curMinutes >= 13 * 60 && curMinutes < 13 * 60 + 45) {{
                        // Stage 1 ACTIVE
                        s1Card.style.border = '1.5px solid rgba(56, 189, 248, 0.6)';
                        s1Card.style.background = 'linear-gradient(135deg, rgba(14, 165, 233, 0.18), rgba(15, 23, 42, 0.9))';
                        if (s1Badge) {{ s1Badge.style.background = 'rgba(56, 189, 248, 0.25)'; s1Badge.style.color = '#38bdf8'; s1Badge.innerHTML = '<span class="war-room-live-dot" style="background:#38bdf8;"></span> ĐANG DIỄN RA'; }}

                        s2Card.style.border = '1px solid rgba(148, 163, 184, 0.2)';
                        s2Card.style.background = 'rgba(30, 41, 59, 0.5)';
                        if (s2Badge) {{ s2Badge.style.background = 'rgba(148, 163, 184, 0.15)'; s2Badge.style.color = '#94a3b8'; s2Badge.innerText = 'CHUẨN BỊ ĐẾN'; }}

                        s3Card.style.border = '1.5px solid rgba(245, 158, 11, 0.4)';
                        if (s3Badge) {{ s3Badge.style.background = 'rgba(245, 158, 11, 0.2)'; s3Badge.style.color = '#fbbf24'; s3Badge.innerText = '⭐ THỜI KHẮC QUYẾT ĐỊNH'; }}
                    }} else if (curMinutes >= 13 * 60 + 45 && curMinutes < 14 * 60) {{
                        // Stage 2 ACTIVE (13:45 - 13:55 No-Supply Check)
                        s1Card.style.border = '1px solid rgba(16, 185, 129, 0.3)';
                        s1Card.style.background = 'rgba(16, 185, 129, 0.05)';
                        if (s1Badge) {{ s1Badge.style.background = 'rgba(16, 185, 129, 0.2)'; s1Badge.style.color = '#34d399'; s1Badge.innerText = '✓ ĐÃ HOÀN TẤT HẤP THỤ'; }}

                        s2Card.style.border = '1.8px solid #38bdf8';
                        s2Card.style.background = 'linear-gradient(135deg, rgba(14, 165, 233, 0.2), rgba(15, 23, 42, 0.95))';
                        if (s2Badge) {{ s2Badge.style.background = 'rgba(56, 189, 248, 0.3)'; s2Badge.style.color = '#38bdf8'; s2Badge.innerHTML = '<span class="war-room-live-dot" style="background:#38bdf8;"></span> ĐANG DIỄN RA (NO-SUPPLY CHECK)'; }}

                        s3Card.style.border = '1.5px solid rgba(245, 158, 11, 0.5)';
                        if (s3Badge) {{ s3Badge.style.background = 'rgba(245, 158, 11, 0.2)'; s3Badge.style.color = '#fbbf24'; s3Badge.innerText = '⭐ SẴN SÀNG BẤM CÒ (14h00)'; }}
                    }} else if (curMinutes >= 14 * 60 && curMinutes <= 14 * 60 + 25) {{
                        // Stage 3 ACTIVE (14:00 - 14:25 GOLDEN HOUR)
                        s1Card.style.border = '1px solid rgba(148, 163, 184, 0.15)';
                        s1Card.style.background = 'rgba(15, 23, 42, 0.5)';
                        if (s1Badge) {{ s1Badge.style.background = 'rgba(148, 163, 184, 0.15)'; s1Badge.style.color = '#94a3b8'; s1Badge.innerText = '✓ ĐÃ QUA'; }}

                        s2Card.style.border = '1px solid rgba(16, 185, 129, 0.3)';
                        s2Card.style.background = 'rgba(16, 185, 129, 0.05)';
                        if (s2Badge) {{ s2Badge.style.background = 'rgba(16, 185, 129, 0.2)'; s2Badge.style.color = '#34d399'; s2Badge.innerText = '✓ ĐẠT CHUẨN CẠN VOL'; }}

                        s3Card.style.border = '2.5px solid #fbbf24';
                        s3Card.style.background = 'linear-gradient(135deg, rgba(245, 158, 11, 0.25), rgba(15, 23, 42, 0.98))';
                        s3Card.style.boxShadow = '0 0 20px rgba(245, 158, 11, 0.35)';
                        if (s3Badge) {{ s3Badge.style.background = '#fbbf24'; s3Badge.style.color = '#0f172a'; s3Badge.style.fontWeight = '900'; s3Badge.innerHTML = '⚡ ⭐ KHUNG GIỜ VÀNG — BẤM CÒ NGAY! ⭐ ⚡'; }}
                    }}
                }}
            }}
            tick();
            setInterval(tick, 1000);
        }}

        function initTacticalWarRoom() {{
            loadTacticalWarRoomData();
            if (warRoomPollingInterval) clearInterval(warRoomPollingInterval);
            warRoomPollingInterval = setInterval(() => {{
                loadTacticalWarRoomData();
            }}, 4000);
        }}

        async function loadTacticalWarRoomData() {{
            try {{
                const res = await fetch('/api/tactical_war_room');
                if (!res.ok) return;
                const data = await res.json();
                renderTacticalWarRoom(data);
            }} catch (err) {{
                console.warn('Error loading tactical war room data:', err);
            }}
        }}

        function renderTacticalWarRoom(data) {{
            if (!data) return;

            // 1. Clocks
            if (data.server_time) {{
                const clockEl = document.getElementById('war-room-clock');
                if (clockEl) clockEl.innerText = data.server_time;
            }}

            // 2. Active Phase Highlight
            if (data.phase_info && data.phase_info.active_phase_id) {{
                const activeId = data.phase_info.active_phase_id;
                document.querySelectorAll('.phase-step-card').forEach(card => {{
                    card.classList.remove('active');
                }});
                const targetCard = document.getElementById('step-' + activeId);
                if (targetCard) targetCard.classList.add('active');
            }}

            // 3. Action Plan Hero: Ta nên làm gì vào thời điểm này?
            if (data.action_plan && data.action_plan.current_step) {{
                const cur = data.action_plan.current_step;
                const timeEl = document.getElementById('action-plan-time');
                const titleEl = document.getElementById('action-plan-title');
                const whatEl = document.getElementById('action-plan-what-to-do');
                const ruleEl = document.getElementById('action-plan-rule');

                if (timeEl) timeEl.innerText = cur.time_range;
                if (titleEl) titleEl.innerText = `📍 ${{cur.title.toUpperCase()}}`;
                if (whatEl) whatEl.innerHTML = `<strong>🎯 HÀNH ĐỘNG CỦA DOANH NGHIỆP TA:</strong><br>${{cur.what_to_do}}`;
                if (ruleEl) ruleEl.innerHTML = `⚖️ <strong>Kỷ Luật Hiến Chương Bắt Buộc</strong>: ${{cur.constitution_rule}}`;
            }}

            // 4. Current Directive Hero Text
            const dirBox = document.getElementById('war-room-live-directive-box');
            if (dirBox && data.tactical_message) {{
                dirBox.innerHTML = data.tactical_message;
            }}

            // 5. Milestones Timeline
            const msContainer = document.getElementById('tactical-milestones-list');
            if (msContainer && data.action_plan && data.action_plan.all_steps) {{
                let msHtml = '';
                data.action_plan.all_steps.forEach(m => {{
                    const isAct = m.status === 'ACTIVE';
                    const isComp = m.status === 'COMPLETED';
                    const borderCls = isAct ? 'active' : (isComp ? 'completed' : '');
                    const badgeBg = isAct ? 'rgba(56, 189, 248, 0.25)' : (isComp ? 'rgba(16, 185, 129, 0.2)' : 'rgba(148, 163, 184, 0.2)');
                    const badgeClr = isAct ? '#38bdf8' : (isComp ? '#34d399' : '#94a3b8');
                    const badgeText = isAct ? 'ĐANG DIỄN RA' : (isComp ? 'ĐÃ HOÀN TẤT' : 'CHỜ ĐẾN GIỜ');

                    msHtml += `
                        <div class="milestone-card ${{borderCls}}">
                            <div class="milestone-header">
                                <span class="milestone-time">⏰ ${{m.time_range}}</span>
                                <span class="milestone-badge" style="background:${{badgeBg}}; color:${{badgeClr}};">${{badgeText}}</span>
                            </div>
                            <div class="milestone-title">${{m.title}}</div>
                            <div class="milestone-desc">${{m.what_to_do}}</div>
                        </div>
                    `;
                }});
                msContainer.innerHTML = msHtml;
            }}

            // 6. Market Radar Overview (Victor)
            if (data.market_overview) {{
                const mo = data.market_overview;
                const vnPts = document.getElementById('vnindex-pts');
                const vnVal = document.getElementById('vnindex-val');
                const vn30Pts = document.getElementById('vn30-pts');
                const vn30Val = document.getElementById('vn30-val');
                const fnEl = document.getElementById('foreign-net');

                if (mo.vn_index) {{
                    if (vnVal) vnVal.innerText = Number(mo.vn_index.value).toLocaleString('en-US', {{ minimumFractionDigits: 2 }});
                    if (vnPts) vnPts.innerText = `${{mo.vn_index.change_pts >= 0 ? '+' : ''}}${{mo.vn_index.change_pts}} (${{mo.vn_index.change_pct >= 0 ? '+' : ''}}${{mo.vn_index.change_pct}}%)`;
                }}
                if (mo.vn30_index) {{
                    if (vn30Val) vn30Val.innerText = Number(mo.vn30_index.value).toLocaleString('en-US', {{ minimumFractionDigits: 2 }});
                    if (vn30Pts) vn30Pts.innerText = `${{mo.vn30_index.change_pts >= 0 ? '+' : ''}}${{mo.vn30_index.change_pts}} (${{mo.vn30_index.change_pct >= 0 ? '+' : ''}}${{mo.vn30_index.change_pct}}%)`;
                }}
                if (fnEl && mo.vn_index.foreign_net_ty_vnd) {{
                    fnEl.innerText = mo.vn_index.foreign_net_ty_vnd;
                }}
            }}

            // 7. Live Stock Sentinel Table (Victor)
            if (data.live_stocks && data.live_stocks.length > 0) {{
                const tbody = document.getElementById('live-stocks-table-body');
                if (tbody) {{
                    let tbHtml = '';
                    data.live_stocks.forEach(s => {{
                        const isUp = s.change_pct > 0;
                        const isDown = s.change_pct < 0;
                        const pCls = isUp ? 'up' : (isDown ? 'down' : 'ref');
                        const sign = isUp ? '+' : '';
                        const volStr = s.volume > 1000000 ? (s.volume / 1000000).toFixed(1) + 'M' : (s.volume / 1000).toFixed(0) + 'k';
                        const secColor = s.security_status === 'SAFE' ? '#10b981' : '#fbbf24';

                        tbHtml += `
                            <tr>
                                <td><strong style="color:#38bdf8;">${{s.code}}</strong></td>
                                <td class="price-badge ${{pCls}}">${{Number(s.price).toLocaleString('en-US')}}</td>
                                <td class="price-badge ${{pCls}}">${{sign}}${{s.change_pct}}%</td>
                                <td>${{volStr}}</td>
                                <td style="color:#34d399;">${{s.active_buy_pct}}%</td>
                                <td><span style="color:${{secColor}}; font-weight:700;">${{s.security_status === 'SAFE' ? '🟢 AN TOÀN' : '🟡 STANDBY'}}</span></td>
                            </tr>
                        `;
                    }});
                    tbody.innerHTML = tbHtml;
                }}
            }}

            // 8. Directive Chat Stream
            const chatBox = document.getElementById('directive-history-box');
            if (chatBox && data.directives_history) {{
                let chatHtml = '';
                data.directives_history.forEach(d => {{
                    const roleClass = d.role === 'chairman' ? 'chairman' : (d.role === 'sentinel' ? 'sentinel' : 'specialist');
                    chatHtml += `
                        <div class="directive-msg ${{roleClass}}">
                            <div class="directive-msg-head">
                                <span>${{d.sender}}</span>
                                <span style="font-weight:400; color:#94a3b8;">${{d.timestamp}}</span>
                            </div>
                            <div class="directive-msg-body">${{d.content}}</div>
                        </div>
                    `;
                }});
                chatBox.innerHTML = chatHtml;
                chatBox.scrollTop = chatBox.scrollHeight;
            }}

            // 9. Dynamic Victor Sentinel & SSOT Cash Update
            if (data.victor_sentinel) {{
                const vs = data.victor_sentinel;
                const vCash = document.getElementById('victor-cash-val');
                const vHold = document.getElementById('victor-holdings-val');
                const vPnl = document.getElementById('victor-pnl-val');
                const headPill = document.getElementById('wr-header-cash-pill');
                const topKpiCash = document.getElementById('top-kpi-cash-val');
                const topKpiSub = document.getElementById('top-kpi-cash-sub');

                const cashFmt = Number(vs.cash_vnd || 14510422).toLocaleString('en-US') + ' ₫';
                const stockFmt = Number(vs.stocks_val_vnd || 5650000).toLocaleString('en-US') + ' ₫';
                const pnlFmt = (vs.unrealized_pnl_vnd ? (vs.unrealized_pnl_vnd > 0 ? '+' : '') + Number(vs.unrealized_pnl_vnd).toLocaleString('en-US') : '-6,700') + ' ₫';
                const pnlPct = vs.unrealized_pnl_pct !== undefined ? vs.unrealized_pnl_pct : -0.1;
                const holdCount = vs.holdings_count || 2;

                if (vCash) vCash.innerText = cashFmt;
                if (vHold) vHold.innerHTML = `Cổ phiếu rủi ro: <strong style="color: #38bdf8;">${{holdCount * 100}} CP (${{stockFmt}} • 28.0%)</strong>`;
                if (vPnl) vPnl.innerHTML = `PnL Tạm: <strong style="color: #f87171;">${{pnlFmt}} (${{pnlPct}}%)</strong> | Lãi V1: <strong style="color: #34d399;">+167,119 ₫</strong>`;
                if (headPill) headPill.innerHTML = `💰 Két Tiền Thật: <strong style="color: #34d399;">${{cashFmt}}</strong> (72.0% Cash) | 📈 Cổ Phiếu: <strong style="color: #38bdf8;">${{stockFmt}}</strong> (${{holdCount * 100}} CP)`;
                if (topKpiCash) topKpiCash.innerText = cashFmt;
                if (topKpiSub) topKpiSub.innerHTML = `<span style="color: #34d399; font-weight: 700;">72.0% Cash</span> • ${{holdCount * 100}} CP (${{stockFmt}} • 28.0% NAV)`;

                // Update live holdings box if holdings present
                const holdBox = document.getElementById('victor-live-holdings-box');
                if (holdBox && vs.holdings && vs.holdings.length > 0) {{
                    let hHtml = `
                    <div style="font-size: 11px; font-weight: 800; color: #38bdf8; display: flex; justify-content: space-between;">
                        <span>📦 DANH MỤC ĐÃ GIẢI NGÂN (${{vs.holdings.length}} MÃ • ${{vs.holdings.length * 100}} CP)</span>
                        <span style="color: #34d399;">🛡️ STOP 2xATR BẢO VỆ</span>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 5px;">`;
                    vs.holdings.forEach(h => {{
                        const sym = h.symbol;
                        const sh = h.shares || 100;
                        const ep = Number(h.entry_price || 0).toLocaleString('en-US');
                        const cp = Number(h.current_price || h.entry_price || 0).toLocaleString('en-US');
                        const pnl = Number(h.unrealized_pnl_vnd || 0).toLocaleString('en-US');
                        const pnlP = h.unrealized_pnl_pct || 0;
                        const pnlColor = (h.unrealized_pnl_vnd || 0) >= 0 ? '#34d399' : '#f87171';
                        const sl = Number(h.stop_loss || 0).toLocaleString('en-US');
                        hHtml += `
                        <div style="background: rgba(30, 41, 59, 0.7); padding: 6px 8px; border-radius: 6px; font-size: 11px; display: flex; justify-content: space-between; align-items: center;">
                            <div><strong style="color: #38bdf8;">${{sym}}</strong> <span style="color: #94a3b8;">(${{sh}} CP)</span></div>
                            <div>Vốn: <span style="color: #cbd5e1;">${{ep}} ₫</span> ➔ Live: <span style="color: ${{pnlColor}};">${{cp}} ₫</span></div>
                            <div>PnL: <strong style="color: ${{pnlColor}};">${{pnl}} ₫ (${{pnlP}}%)</strong></div>
                            <div style="color: #fbbf24; font-size: 10px;">Stop: ${{sl}} ₫</div>
                        </div>`;
                    }});
                    hHtml += `</div>`;
                    holdBox.innerHTML = hHtml;
                    holdBox.style.display = 'flex';
                }}
            }}
        }}

        function toggleWeeklyRoadmap() {{
            const det = document.getElementById('weekly-roadmap-details');
            const btn = document.getElementById('btn-toggle-weekly-roadmap');
            if (!det || !btn) return;
            if (det.style.display === 'none') {{
                det.style.display = 'block';
                btn.innerText = '▾ Thu Gọn';
            }} else {{
                det.style.display = 'none';
                btn.innerText = '▸ Mở Rộng';
            }}
        }}

        async function sendTacticalCommand(customPrompt) {{
            const inputEl = document.getElementById('tactical-cmd-input');
            const btnEl = document.getElementById('btn-send-tactical');
            const prompt = customPrompt || (inputEl ? inputEl.value.trim() : '');
            if (!prompt) return;

            if (inputEl) inputEl.value = '';
            if (btnEl) {{
                btnEl.disabled = true;
                btnEl.innerText = '⏳ Đang gửi...';
            }}

            try {{
                const res = await fetch('/api/tactical_command', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ command: prompt }})
                }});
                if (res.ok) {{
                    await loadTacticalWarRoomData();
                }}
            }} catch (err) {{
                console.error('Error sending tactical command:', err);
            }} finally {{
                if (btnEl) {{
                    btnEl.disabled = false;
                    btnEl.innerText = '⚡ Gửi Chỉ Lệnh';
                }}
                if (inputEl) inputEl.focus();
            }}
        }}

        function sendQuickTactical(promptText) {{
            const inputEl = document.getElementById('tactical-cmd-input');
            if (inputEl) inputEl.value = promptText;
            sendTacticalCommand(promptText);
        }}


        window.addEventListener('DOMContentLoaded', () => {{
            applyAllFilters();
            const urlParams = new URLSearchParams(window.location.search);
            const openPath = urlParams.get('open');
            if (openPath) {{
                openReportModal(openPath);
            }}
            initSummitRoom();
            startLiveClockTicker();
            initTacticalWarRoom();
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
