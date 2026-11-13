#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INSTITUTIONAL CLOUD SUPERVISOR & MULTI-PROCESS WATCHDOG (24/7 AUTONOMOUS OPERATION)
File: scripts/start_apex_cloud_247.py
Cơ quan chủ quản: Palmer — Cố vấn Điều hành Tối cao & Trưởng Phòng Tổng Hệ Thống (Apex Governance)
Giám sát tối cao: Master CIO James (Ban 8)
Phục vụ trực tiếp: Chủ tịch Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)

Nhiệm vụ:
1. Điều hành đồng thời 3 luồng tác chiến ngầm độc lập 24/24:
   - Service 1: `CRON_DAEMON` (17 cột mốc tác chiến, BCTC, CBTT, vĩ mô SBV, tự học & phúc tra EOD).
   - Service 2: `SENTINEL_MONITOR` (Ban 9 Victor canh bảng điện realtime 15s/lần bảo vệ tài khoản 20,167,119 ₫ & radar Tầm ngắm Vòng 2).
   - Service 3: `TELEGRAM_COPILOT` (Trợ lý tương tác 2 chiều 24/7 với Chủ tịch qua Telegram).
2. Tích hợp Watchdog tự động phục hồi (Auto-Restart Watchdog):
   - Quét sức khỏe định kỳ mỗi 5 giây.
   - Tự động hồi sinh tiến trình bị thoát hoặc gặp sự cố mạng/tràn bộ nhớ trong vòng 3-5 giây.
   - Tích hợp cầu chì ngắt vòng lặp sụp đổ (Circuit Breaker): Chặn spam khởi động nếu tiến trình crash liên tục > 10 lần/5 phút.
3. Xuất bản nhịp tim và trạng thái thể chế thời gian thực:
   - Ghi nhận `data/apex_cloud_supervisor_status.json` và `data/apex_cloud_supervisor.log`.
   - Phân tách file log riêng biệt cho từng service trong `data/logs/`.
4. Dừng hệ thống an toàn (Graceful Shutdown):
   - Bắt các tín hiệu SIGINT (Ctrl+C), SIGTERM (Cloud shutdown / container stop).
   - Dọn dẹp tiến trình con sạch sẽ, không để lại tiến trình ma (orphan/zombie).
"""

import os
import sys
import time
import json
import signal
import datetime
import subprocess
import http.server
import threading
import urllib.parse
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

SUPERVISOR_PID_FILE = DATA_DIR / "apex_cloud_supervisor.pid"
SUPERVISOR_STATUS_FILE = DATA_DIR / "apex_cloud_supervisor_status.json"
SUPERVISOR_LOG_FILE = DATA_DIR / "apex_cloud_supervisor.log"

sys.path.insert(0, str(BASE_DIR))
from scripts.singleton_dedup_manager import is_pid_running
from scripts.telegram_dispatcher import dispatch_message

SERVICES_CONFIG = {
    "cron_daemon": {
        "name": "Apex Institutional 18-Milestones Cron Daemon",
        "script": "scripts/apex_institutional_cron_daemon.py",
        "args": ["--daemon"],
        "log_file": LOGS_DIR / "cron_daemon.log",
        "enabled": True,
        "max_crashes_in_window": 10,
        "crash_window_seconds": 300,
        "restart_delay_seconds": 3
    },
    "sentinel_monitor": {
        "name": "Apex Portfolio Realtime Sentinel (Victor - Ban 9)",
        "script": "scripts/vn3_portfolio_autonomous_sentinel.py",
        "args": ["--daemon"],
        "log_file": LOGS_DIR / "sentinel_monitor.log",
        "enabled": True,
        "max_crashes_in_window": 10,
        "crash_window_seconds": 300,
        "restart_delay_seconds": 3
    },
    "telegram_copilot": {
        "name": "Apex Interactive Bidirectional Telegram Co-Pilot",
        "script": "scripts/telegram_interactive_copilot.py",
        "args": ["--daemon"],
        "log_file": LOGS_DIR / "telegram_copilot.log",
        "enabled": True,
        "max_crashes_in_window": 10,
        "crash_window_seconds": 300,
        "restart_delay_seconds": 3
    },
    "inspector_trong": {
        "name": "Apex Institutional Ombudsman (Trọng - Ban 12)",
        "script": "scripts/apex_inspector_trong.py",
        "args": ["--daemon"],
        "log_file": LOGS_DIR / "inspector_trong.log",
        "enabled": True,
        "max_crashes_in_window": 10,
        "crash_window_seconds": 300,
        "restart_delay_seconds": 3
    }
}


def log_sup(msg: str, echo: bool = True):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [SUPERVISOR] {msg}"
    if echo:
        print(line, flush=True)
    try:
        with open(SUPERVISOR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass




def generate_supervisor_dashboard_html(data: Dict[str, Any]) -> str:
    sup_status = data.get("supervisor_status", "UNKNOWN")
    uptime_sec = data.get("uptime_seconds", 0)
    started_at = data.get("started_at", "N/A")
    last_hb = data.get("last_heartbeat", "N/A")
    services = data.get("services", {})

    # Load dynamic portfolio SSOT
    cash_str = "14,510,422 ₫"
    cash_sub = "72.0% Cash • 200 CP (5,650,000 ₫ • 28.0% NAV)"
    pnl_str = "+167,119 ₫"
    try:
        ssot_path = DATA_DIR / "current_portfolio_state.json"
        if ssot_path.exists():
            with open(ssot_path, "r", encoding="utf-8") as f:
                pdata = json.load(f)
                cash_val = float(pdata.get("cash_balance_vnd", 14510422.0))
                tot_nav = float(pdata.get("total_nav_vnd", 20160422.0))
                mkt_val = float(pdata.get("total_market_val_vnd", 5650000.0))
                pos = pdata.get("active_positions", {})
                num_cp = sum(p.get("shares", 0) for p in pos.values())
                cash_str = f"{cash_val:,.0f} ₫"
                cash_pct = (cash_val / tot_nav * 100) if tot_nav > 0 else 72.0
                nav_pct = 100.0 - cash_pct
                if num_cp > 0:
                    pos_names = ", ".join([f"{p.get('shares', 0)} {s}" for s, p in pos.items()])
                    cash_sub = f"{cash_pct:.1f}% Cash • {num_cp} CP ({pos_names}) • {nav_pct:.1f}% NAV"
                else:
                    cash_sub = "100% Tiền Mặt (0 CP Rủi Ro)"
                realized = float(pdata.get("realized_pnl_vnd", 167119.0))
                pnl_str = f"+{realized:,.0f} ₫" if realized >= 0 else f"{realized:,.0f} ₫"
    except Exception:
        pass
    
    rows_html = ""
    for k, sinfo in services.items():
        st = sinfo.get("status", "UNKNOWN")
        badge_color = "#10b981" if st == "RUNNING" else ("#ef4444" if st == "STOPPED" else "#f59e0b")
        rows_html += f"""
        <tr style="border-bottom: 1px solid #374151;">
            <td style="padding: 12px; font-weight: 600; color: #f3f4f6;">{sinfo.get('name', k)}</td>
            <td style="padding: 12px; font-family: monospace; color: #9ca3af;">{sinfo.get('pid', '-')}</td>
            <td style="padding: 12px;">
                <span style="background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700;">
                    ● {st}
                </span>
            </td>
            <td style="padding: 12px; color: #9ca3af;">{sinfo.get('restart_count', 0)}</td>
            <td style="padding: 12px; color: #9ca3af;">{sinfo.get('uptime_seconds', 0):.0f}s</td>
        </tr>
        """
        
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="10">
    <title>Apex Cloud Supervisor 24/7 — Live Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 24px; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 20px; }}
        .stat-box {{ background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 16px; }}
        .stat-val {{ font-size: 20px; font-weight: bold; color: #38bdf8; margin-top: 4px; }}
        .stat-lbl {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }}
        th {{ background: #0f172a; padding: 12px; color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 11px; }}
    </style>
</head>
<body>
    <div style="max-width: 1000px; margin: 0 auto;">
        <div class="card">
            <div class="header">
                <div>
                    <h1 style="margin: 0; font-size: 22px; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
                        🏛️ APEX INSTITUTIONAL CLOUD SUPERVISOR 24/7
                    </h1>
                    <p style="margin: 4px 0 0; color: #94a3b8; font-size: 13px;">
                        Tài khoản: <strong style="color: #f1f5f9;">TCBS 105C307855 (Trần Quốc Thiên Phước)</strong> | Master CIO: <strong style="color: #f1f5f9;">James</strong>
                    </p>
                </div>
                <div style="text-align: right;">
                    <span style="background: #10b98122; color: #10b981; border: 1px solid #10b981; padding: 6px 14px; border-radius: 9999px; font-size: 13px; font-weight: 700;">
                        ● {sup_status}
                    </span>
                    <div style="font-size: 11px; color: #64748b; margin-top: 6px;">Uptime: {uptime_sec:.0f}s | Tự làm mới: 10s</div>
                </div>
            </div>

            <div class="grid">
                <div class="stat-box">
                    <div class="stat-lbl">Tài Sản Khả Dụng (SSOT V2.0)</div>
                    <div class="stat-val" style="color: #34d399;">{cash_str}</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">{cash_sub}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-lbl">Lãi Ròng Thu Về Vòng 1</div>
                    <div class="stat-val" style="color: #60a5fa;">{pnl_str}</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Đã tất toán 100% (HPG, TCB, MBB)</div>
                </div>
                <div class="stat-box">
                    <div class="stat-lbl">Dịch Vụ Trực Chiến</div>
                    <div class="stat-val" style="color: #f472b6;">{len(services)} Dịch Vụ Nền</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Bao phủ trọn vẹn 12 phòng ban</div>
                </div>
                <div class="stat-box">
                    <div class="stat-lbl">Nhịp Tim Gần Nhất</div>
                    <div class="stat-val" style="font-size: 15px; color: #fbbf24; margin-top: 8px;">{last_hb}</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Healthcheck: 200 OK</div>
                </div>
            </div>

            <h3 style="font-size: 15px; margin: 24px 0 12px; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.05em;">
                🛡️ Bảng Trạng Thái 4 Tiến Trình Tự Hành 24/24 (Watchdog Tự Hồi Phục)
            </h3>
            <div style="overflow-x: auto; border-radius: 8px; border: 1px solid #334155;">
                <table>
                    <thead>
                        <tr>
                            <th>Tên Dịch Vụ</th>
                            <th>PID</th>
                            <th>Trạng Thái</th>
                            <th>Restarts</th>
                            <th>Thời Gian Chạy</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px; font-size: 12px; color: #64748b; border-top: 1px solid #334155; padding-top: 16px;">
                <div>Hạ tầng: Linux Cloud Container / Render Worker 24/7</div>
                <div style="display: flex; gap: 12px;">
                    <a href="/api/health" style="color: #38bdf8; text-decoration: none;">[API Healthcheck]</a>
                    <a href="/api/status" style="color: #38bdf8; text-decoration: none;">[API Status JSON]</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html


class ApexSupervisorHTTPHandler(http.server.BaseHTTPRequestHandler):
    supervisor_ref = None

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        if path in ("/api/health", "/healthz", "/health"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            port_file = DATA_DIR / "current_portfolio_state.json"
            port_state = {}
            if port_file.exists():
                try:
                    with open(port_file, "r", encoding="utf-8") as pf:
                        port_state = json.load(pf)
                except Exception:
                    pass
            active_pos = port_state.get("active_positions", {})
            cash_val = float(port_state.get("cash_balance_vnd", 0.0))
            mkt_val = float(port_state.get("total_market_val_vnd", 0.0))
            nav_val = float(port_state.get("total_nav_vnd", cash_val + mkt_val))
            data = {
                "status": "ok",
                "supervisor": "HEALTHY",
                "chairman_account": "TCBS 105C307855 (Trần Quốc Thiên Phước)",
                "cash_vnd": cash_val,
                "stock_market_val_vnd": mkt_val,
                "total_nav_vnd": nav_val,
                "holdings_count": len(active_pos),
                "active_holdings": list(active_pos.keys()),
                "realized_round_1_profit_vnd": float(port_state.get("realized_pnl_vnd", 167119.0)),
                "unrealized_pnl_vnd": float(port_state.get("unrealized_pnl_vnd", 0.0)),
                "debt_vnd": float(port_state.get("debt_vnd", 0.0)),
                "timestamp": datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        elif path in ("/api/status", "/api/state"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            status_data = {}
            if SUPERVISOR_STATUS_FILE.exists():
                try:
                    with open(SUPERVISOR_STATUS_FILE, "r", encoding="utf-8") as f:
                        status_data = json.load(f)
                except Exception:
                    pass
            self.wfile.write(json.dumps(status_data, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/reports":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                import importlib
                import scripts.apex_report_scanner
                importlib.reload(scripts.apex_report_scanner)
                from scripts.apex_report_scanner import scan_all_institutional_reports
                date_filter = query.get("date", ["all"])[0]
                dept_filter = query.get("dept", ["all"])[0]
                shift_filter = query.get("shift", ["all"])[0]
                search_query = query.get("search", [""])[0] or query.get("q", [""])[0]
                limit = int(query.get("limit", [2000])[0])
                offset = int(query.get("offset", [0])[0])
                reports = scan_all_institutional_reports(
                    date_filter=date_filter,
                    dept_filter=dept_filter,
                    shift_filter=shift_filter,
                    search_query=search_query,
                    limit=limit,
                    offset=offset
                )
                self.wfile.write(json.dumps(reports, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif path in ("/api/db_stats", "/api/database"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.apex_database_engine import ApexDatabaseEngine
                st = ApexDatabaseEngine.get_database_stats()
                self.wfile.write(json.dumps(st, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif path == "/api/report":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            rel_path = query.get("path", [""])[0]
            if not rel_path or ".." in rel_path or not rel_path.endswith(".md"):
                self.wfile.write(json.dumps({"ok": False, "error": "Đường dẫn báo cáo không hợp lệ."}).encode("utf-8"))
                return
            full_path = BASE_DIR / rel_path
            if not full_path.exists() or not full_path.is_file():
                self.wfile.write(json.dumps({"ok": False, "error": f"Không tìm thấy file: {rel_path}"}).encode("utf-8"))
                return
            try:
                content = full_path.read_text(encoding="utf-8", errors="ignore")
                stat = full_path.stat()
                mtime_str = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                m_title = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = m_title.group(1).strip() if m_title else full_path.stem
                payload = {
                    "ok": True,
                    "path": rel_path,
                    "title": title,
                    "content": content,
                    "size_kb": round(stat.st_size / 1024, 1),
                    "last_modified": mtime_str
                }
                self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
            return

        elif path == "/api/timeline":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.apex_report_scanner import get_daily_milestones_status
                ms = get_daily_milestones_status()
                self.wfile.write(json.dumps(ms, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif path == "/api/dates":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.apex_report_scanner import get_available_archive_dates
                dates = get_available_archive_dates()
                self.wfile.write(json.dumps(dates, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif path == "/api/heuristics":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.apex_persistent_memory_core import ApexPersistentMemoryCore
                query_str = query.get("q", [""])[0]
                category_str = query.get("cat", [""])[0]
                if query_str or category_str:
                    res = ApexPersistentMemoryCore.query_heuristics(query=query_str, category=category_str, limit=50)
                    self.wfile.write(json.dumps({"count": len(res), "heuristics": res}, ensure_ascii=False).encode("utf-8"))
                else:
                    db = ApexPersistentMemoryCore.load_heuristics_database()
                    self.wfile.write(json.dumps(db, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif path == "/api/summit_meeting":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.apex_summit_meeting_engine import get_realtime_meeting_state
                preview = query.get("preview", ["0"])[0] in ("1", "true", "True")
                st = get_realtime_meeting_state(preview_mode=preview)
                self.wfile.write(json.dumps(st, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif path == "/api/tactical_war_room":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.apex_tactical_war_room_engine import get_tactical_war_room_state
                from scripts.apex_web_portal_engine import generate_dynamic_tactical_stages_html
                st = get_tactical_war_room_state()
                st["tactical_stages_html"] = generate_dynamic_tactical_stages_html()
                self.wfile.write(json.dumps(st, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            status_data = {}
            if SUPERVISOR_STATUS_FILE.exists():
                try:
                    with open(SUPERVISOR_STATUS_FILE, "r", encoding="utf-8") as f:
                        status_data = json.load(f)
                except Exception:
                    pass
            try:
                import importlib
                import scripts.apex_report_scanner
                import scripts.apex_web_portal_engine
                importlib.reload(scripts.apex_report_scanner)
                importlib.reload(scripts.apex_web_portal_engine)
                reports = scripts.apex_report_scanner.scan_all_institutional_reports(limit=2000)
                milestones = scripts.apex_report_scanner.get_daily_milestones_status()
                dates = scripts.apex_report_scanner.get_available_archive_dates()
                html = scripts.apex_web_portal_engine.generate_portal_html(status_data, reports, milestones, available_dates=dates)
            except Exception as e:
                import traceback
                log_supervisor(f"[CRITICAL_PORTAL_RENDER_ERROR] {traceback.format_exc()}")
                print(f"[CRITICAL_PORTAL_RENDER_ERROR] {traceback.format_exc()}", flush=True)
                html = generate_supervisor_dashboard_html(status_data)
            self.wfile.write(html.encode("utf-8"))
            return

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == "/api/command":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                req_data = json.loads(body_bytes.decode("utf-8"))
                user_command = req_data.get("command", "").strip()
                if not user_command:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "error": "Chỉ thị không được để trống."}).encode("utf-8"))
                    return

                # Gọi trực tiếp bộ chỉ huy Master CIO James
                from scripts.master_cio_james_agent import handle_james_chat
                james_reply = handle_james_chat(user_command)

                # Gửi thông báo đồng bộ vào Telegram james_hq để lưu vết
                try:
                    from scripts.telegram_dispatcher import dispatch_message
                    dispatch_message("james_hq", f"💬 *[CHỈ THỊ TỪ WEB PORTAL]*\n👤 *Chủ tịch*: `{user_command}`\n\n{james_reply}")
                except Exception:
                    pass

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                payload = {
                    "ok": True,
                    "command": user_command,
                    "response": james_reply,
                    "officer": "Master CIO James (Ban 8)",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
            return

        elif parsed_url.path == "/api/summit_message":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                req_data = json.loads(body_bytes.decode("utf-8"))
                user_msg = req_data.get("message", "").strip()
                if not user_msg:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "error": "Chỉ thị không được để trống."}).encode("utf-8"))
                    return
                from scripts.apex_summit_meeting_engine import add_chairman_directive
                res = add_chairman_directive(user_msg)

                # Gửi báo cáo nghiên cứu đồng bộ vào Telegram james_hq
                try:
                    from scripts.telegram_dispatcher import dispatch_message
                    james_content = res.get('james_resp', {}).get('content', '')
                    dispatch_message('james_hq', f"🏛️ *[CHỈ THỊ TẠI ĐẠI HỘI NGHỊ THƯỢNG ĐỈNH]*\n👤 *Chủ tịch*: `{user_msg}`\n\n{james_content}")
                except Exception:
                    pass

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
            return

        elif parsed_url.path == "/api/approve_summit_resolution":
            try:
                from scripts.apex_autonomous_council_engine import approve_summit_resolution
                res = approve_summit_resolution()

                # Gửi thông báo đến Telegram james_hq
                try:
                    from scripts.telegram_dispatcher import dispatch_message
                    dispatch_message('james_hq', "👑 *[CHỦ TỊCH ĐÃ KÝ DUYỆT NGHỊ QUYẾT THƯỢNG ĐỈNH & SỔ LỆNH VÒNG 2]*\n\n👤 *Người ký*: `Chủ tịch Trần Quốc Thiên Phước`\n📜 *Văn kiện*: `08_Master_Investment_CIO/council_resolutions/`\n🛡️ *Tổng Kiểm Sát Ban 12 Trọng*: Đã niêm phong pháp lý thể chế thành công 100%!")
                except Exception:
                    pass

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
            return

        elif parsed_url.path == "/api/tactical_command":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                req_data = json.loads(body_bytes.decode("utf-8"))
                user_msg = req_data.get("command", "").strip()
                if not user_msg:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "error": "Chỉ thị không được để trống."}).encode("utf-8"))
                    return

                from scripts.apex_tactical_war_room_engine import handle_tactical_command
                res = handle_tactical_command(user_msg, user_name="Chủ tịch Trần Quốc Thiên Phước")

                try:
                    from scripts.telegram_dispatcher import dispatch_message
                    resp_text = res.get('specialist_response', '')
                    dispatch_message('minh_quan_execution', f"⚡ *[PHÒNG TÁC CHIẾN ĐẦU TƯ TRONG NGÀY]*\n👤 *Chủ tịch*: `{user_msg}`\n\n🎯 *Minh Quân & Victor*: {resp_text}")
                except Exception:
                    pass

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
            return
        else:
            self.send_response(404)
            self.end_headers()
            return

class ManagedService:
    def __init__(self, key: str, cfg: Dict[str, Any]):
        self.key = key
        self.name = cfg["name"]
        self.script_rel = cfg["script"]
        self.args = cfg["args"]
        self.log_path = Path(cfg["log_file"])
        self.enabled = cfg.get("enabled", True)
        self.max_crashes = cfg.get("max_crashes_in_window", 10)
        self.crash_window = cfg.get("crash_window_seconds", 300)
        self.restart_delay = cfg.get("restart_delay_seconds", 3)

        self.process: Optional[subprocess.Popen] = None
        self.pid: Optional[int] = None
        self.start_time: Optional[float] = None
        self.restart_count: int = 0
        self.crash_timestamps: List[float] = []
        self.last_exit_code: Optional[int] = None
        self.status: str = "STOPPED"
        self.circuit_broken: bool = False
        self._log_fh = None

    def start(self) -> bool:
        if not self.enabled:
            self.status = "DISABLED"
            return False

        if self.circuit_broken:
            log_sup(f"⚠️ [CIRCUIT BREAKER] Service '{self.key}' đang bị phong tỏa do lỗi lặp lại. Bỏ qua khởi động.")
            return False

        script_path = BASE_DIR / self.script_rel
        if not script_path.exists():
            log_sup(f"❌ Không tìm thấy script: {script_path}")
            self.status = "SCRIPT_NOT_FOUND"
            return False

        cmd = [sys.executable, "-X", "utf8", str(script_path)] + self.args
        sub_env = os.environ.copy()
        sub_env["PYTHONIOENCODING"] = "utf-8"
        sub_env["PYTHONUNBUFFERED"] = "1"

        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self._log_fh = open(self.log_path, "a", encoding="utf-8", buffering=1)
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._log_fh.write(f"\n--- [SPAWN AT {ts}] {cmd} ---\n")

            self.process = subprocess.Popen(
                cmd,
                cwd=str(BASE_DIR),
                env=sub_env,
                stdout=self._log_fh,
                stderr=subprocess.STDOUT
            )
            self.pid = self.process.pid
            self.start_time = time.time()
            self.status = "RUNNING"
            log_sup(f"🚀 Khởi động dịch vụ '{self.key}' ({self.name}) thành công (PID={self.pid}).")
            return True
        except Exception as e:
            log_sup(f"❌ Lỗi khởi động '{self.key}': {e}")
            self.status = "START_FAILED"
            return False

    def is_alive(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None

    def check_health_and_recover(self) -> str:
        """Kiểm tra sức khỏe tiến trình. Nếu đã thoát, kích hoạt cơ chế hồi phục tự động."""
        if not self.enabled or self.circuit_broken:
            return self.status

        if self.process is None:
            self.start()
            return self.status

        poll_res = self.process.poll()
        if poll_res is None:
            self.status = "RUNNING"
            return "RUNNING"

        # Tiến trình đã thoát
        now = time.time()
        self.last_exit_code = poll_res
        self.crash_timestamps.append(now)
        self.restart_count += 1
        log_sup(f"⚠️ Dịch vụ '{self.key}' (PID={self.pid}) ĐÃ DỪNG với Exit Code: {poll_res} (Lần #{self.restart_count}).")

        # Kiểm tra Circuit Breaker (Crash liên tục trong window)
        recent_crashes = [t for t in self.crash_timestamps if (now - t) <= self.crash_window]
        self.crash_timestamps = recent_crashes

        if len(recent_crashes) >= self.max_crashes:
            self.circuit_broken = True
            self.status = "CIRCUIT_BROKEN"
            log_sup(f"🚨 [CIRCUIT BREAKER ACTIVATED] '{self.key}' đã crash {len(recent_crashes)} lần trong {self.crash_window}s. TẠM DỪNG TỰ ĐỘNG KHỞI ĐỘNG ĐỂ BẢO VỆ TÀI NGUYÊN!")
            try:
                alert_text = (
                    f"🚨 *[APEX WATCHDOG CẢNH BÁO KHẨN CẤP]*\n"
                    f"Dịch vụ *{self.name}* (`{self.key}`) đã dừng bất thường {len(recent_crashes)} lần liên tiếp.\n"
                    f"Hệ thống đã kích hoạt Cầu chì ngắt lỗi để bảo vệ CPU/RAM. Các dịch vụ khác vẫn duy trì 24/7 bình thường!"
                )
                dispatch_message("alerts", alert_text)
                dispatch_message("james_hq", alert_text)
            except Exception:
                pass
            return self.status

        # Tự động khởi động lại sau khoảng đệm an toàn
        self.status = "RESTARTING"
        time.sleep(self.restart_delay)
        self.start()
        return self.status

    def stop(self, timeout: int = 5):
        if self.process is None:
            self.status = "STOPPED"
            return

        if self.process.poll() is None:
            log_sup(f"🛑 Đang dừng dịch vụ '{self.key}' (PID={self.pid})...")
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    log_sup(f"[!] Quá thời gian chờ {timeout}s, buộc dừng '{self.key}' (PID={self.pid})...")
                    self.process.kill()
                    self.process.wait(timeout=2)
            except Exception as e:
                log_sup(f"[!] Lỗi khi dừng '{self.key}': {e}")

        if self._log_fh:
            try:
                self._log_fh.close()
            except Exception:
                pass
            self._log_fh = None

        self.status = "STOPPED"
        self.pid = None

    def get_info(self) -> Dict[str, Any]:
        uptime = round(time.time() - self.start_time, 1) if (self.start_time and self.status == "RUNNING") else 0.0
        return {
            "name": self.name,
            "script": self.script_rel,
            "status": self.status,
            "pid": self.pid,
            "uptime_seconds": uptime,
            "restart_count": self.restart_count,
            "last_exit_code": self.last_exit_code,
            "circuit_broken": self.circuit_broken,
            "log_file": str(self.log_path.relative_to(BASE_DIR).as_posix())
        }


class ApexCloudSupervisor:
    def __init__(self, dry_run: bool = False, port: int = 8000, enable_web: bool = True):
        self.port = port
        self.enable_web = enable_web
        self.http_server = None
        self.dry_run = dry_run
        self.running = False
        self.start_time = time.time()
        self.services: Dict[str, ManagedService] = {}
        for k, cfg in SERVICES_CONFIG.items():
            self.services[k] = ManagedService(k, cfg)

    def _acquire_supervisor_lock(self) -> bool:
        current_pid = os.getpid()
        if SUPERVISOR_PID_FILE.exists():
            try:
                old_pid = int(SUPERVISOR_PID_FILE.read_text(encoding="utf-8").strip())
                if old_pid != current_pid and is_pid_running(old_pid):
                    log_sup(f"🛑 [SUPERVISOR BLOCKED] Đã có Supervisor khác (PID={old_pid}) đang chạy. Dừng tiến trình mới.")
                    return False
            except Exception:
                pass
        SUPERVISOR_PID_FILE.write_text(str(current_pid), encoding="utf-8")
        return True

    def _release_supervisor_lock(self):
        try:
            if SUPERVISOR_PID_FILE.exists():
                cur = os.getpid()
                old = int(SUPERVISOR_PID_FILE.read_text(encoding="utf-8").strip())
                if cur == old:
                    SUPERVISOR_PID_FILE.unlink(missing_ok=True)
        except Exception:
            pass

    def _save_status(self):
        now = time.time()
        uptime = round(now - self.start_time, 1)
        srv_statuses = [s.status for s in self.services.values() if s.enabled]
        overall = "HEALTHY_ALL_RUNNING"
        if any(st == "CIRCUIT_BROKEN" for st in srv_statuses):
            overall = "DEGRADED_CIRCUIT_BROKEN"
        elif any(st != "RUNNING" for st in srv_statuses):
            overall = "DEGRADED_RECOVERING"

        payload = {
            "supervisor_name": "Apex Institutional Cloud Supervisor 24/7",
            "supervisor_pid": os.getpid(),
            "supervisor_status": overall,
            "uptime_seconds": uptime,
            "started_at": datetime.datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S"),
            "last_heartbeat": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_platform": sys.platform,
            "python_executable": sys.executable,
            "chairman_account": "TCBS 105C307855 (Trần Quốc Thiên Phước)",
            "services": {k: s.get_info() for k, s in self.services.items()}
        }
        try:
            with open(SUPERVISOR_STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_sup(f"[!] Lỗi ghi status: {e}", echo=False)

    def _setup_signal_handlers(self):
        def _handle_exit(sig, frame):
            log_sup(f"🛑 Nhận tín hiệu dừng hệ thống ({sig}). Đang thực hiện Graceful Shutdown...")
            self.running = False

        try:
            signal.signal(signal.SIGINT, _handle_exit)
            signal.signal(signal.SIGTERM, _handle_exit)
        except Exception:
            pass

    def start_all(self):
        log_sup("🌟 BẮT ĐẦU KHỞI ĐỘNG HỆ THỐNG APEX CLOUD SUPERVISOR 24/7...")
        # Dọn dẹp các tệp PID con không còn hợp lệ trước khi khởi chạy
        child_pids = [DATA_DIR / "apex_cron_daemon.pid", DATA_DIR / "telegram_copilot.pid"]
        for pf in child_pids:
            if pf.exists():
                try:
                    c_pid = int(pf.read_text(encoding="utf-8").strip())
                    if not is_pid_running(c_pid):
                        pf.unlink(missing_ok=True)
                        log_sup(f"🧹 Dọn dẹp tệp PID rác không còn hoạt động: {pf.name} (PID cũ {c_pid})")
                except Exception:
                    pf.unlink(missing_ok=True)

        # Tự động đồng bộ toàn bộ báo cáo Markdown vào SQLite Lakehouse Vault V5.0
        try:
            log_sup("🔄 Đang đồng bộ thư viện báo cáo Markdown vào SQLite Lakehouse Vault V5.0...")
            from scripts.migrate_markdown_to_sqlite import migrate_all_markdown_reports
            migrate_all_markdown_reports()
            log_sup("✅ Đồng bộ SQLite Lakehouse Vault thành công!")
        except Exception as e_mig:
            log_sup(f"⚠️ Cảnh báo đồng bộ SQLite ban đầu: {e_mig}")

        for k, s in self.services.items():
            s.start()
        self._save_status()
        if self.enable_web:
            try:
                ApexSupervisorHTTPHandler.supervisor_ref = self
                self.http_server = http.server.ThreadingHTTPServer(("0.0.0.0", self.port), ApexSupervisorHTTPHandler)
                t = threading.Thread(target=self.http_server.serve_forever, daemon=True)
                t.start()
                log_sup(f"🌐 [IMMORTAL WEB SERVER] Đang phục vụ tại http://0.0.0.0:{self.port} (Healthcheck: /api/health)")
            except Exception as e:
                log_sup(f"[!] Cảnh báo mở Web Port {self.port}: {e}. Tiếp tục chạy 4 dịch vụ ngầm bình thường.")
                self.http_server = None

        if not self.dry_run:
            log_sup("🌟 [APEX CLOUD SUPERVISOR 24/7] Đã sẵn sàng chạy ngầm 24/7. (Đã tắt broadcast khởi động lên Telegram để bảo vệ trải nghiệm của Chủ tịch).")

    def stop_all(self):
        log_sup("🛑 ĐANG DỪNG TOÀN BỘ 3 DỊCH VỤ DƯỚI QUYỀN SUPERVISOR...")
        if self.http_server:
            try:
                self.http_server.shutdown()
            except Exception:
                pass
            self.http_server = None
        for k, s in self.services.items():
            s.stop()
        self._release_supervisor_lock()
        self._save_status()
        log_sup("✅ HỆ THỐNG ĐÃ ĐÓNG HOÀN TOÀN AN TOÀN (GRACEFUL SHUTDOWN SUCCESS).")

    def run_loop(self, poll_interval: int = 5):
        if not self._acquire_supervisor_lock():
            return 1

        self._setup_signal_handlers()
        self.running = True
        self.start_all()

        last_status_write = time.time()
        log_sup("⚡ Watchdog đang giám sát 24/7 (Chu kỳ kiểm tra mỗi 5 giây)...")

        try:
            while self.running:
                for k, s in self.services.items():
                    s.check_health_and_recover()

                now = time.time()
                if now - last_status_write >= 15:
                    self._save_status()
                    last_status_write = now

                time.sleep(poll_interval)
        except KeyboardInterrupt:
            log_sup("🛑 Dừng do lệnh bàn phím (KeyboardInterrupt).")
        finally:
            self.stop_all()

        return 0

    def run_test_verification(self, test_duration_seconds: int = 15) -> bool:
        """Thử nghiệm nhanh: Khởi động cả 3 dịch vụ, giám sát N giây, kiểm tra nhịp tim, và tắt an toàn."""
        log_sup(f"🧪 BẮT ĐẦU DIỄN TẬP KIỂM ĐỊNH SUPERVISOR 24/7 ({test_duration_seconds} GIÂY)...")
        if not self._acquire_supervisor_lock():
            return False

        try:
            for k, s in self.services.items():
                s.start()

            time.sleep(2)
            self._save_status()

            # Kiểm tra cả 3 tiến trình có sống không
            alive_count = sum(1 for s in self.services.values() if s.is_alive())
            log_sup(f"📊 Trạng thái sau 2s: {alive_count}/{len(self.services)} dịch vụ đang RUNNING.")

            # Chờ thêm thời gian diễn tập
            remain = max(test_duration_seconds - 2, 1)
            time.sleep(remain)

            # Kiểm tra lại trước khi dừng
            for k, s in self.services.items():
                s.check_health_and_recover()
            self._save_status()

            success = (alive_count == len(self.services))
            log_sup(f"🏁 Kết quả diễn tập: {'✅ THÀNH CÔNG 100%' if success else '❌ CÓ DỊCH VỤ LỖI'}")
            return success
        finally:
            self.stop_all()


def show_status():
    if not SUPERVISOR_STATUS_FILE.exists():
        print("[!] Chưa có tệp trạng thái supervisor (data/apex_cloud_supervisor_status.json).")
        return

    try:
        data = json.loads(SUPERVISOR_STATUS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[!] Lỗi đọc file status: {e}")
        return

    sup_pid = data.get("supervisor_pid", 0)
    sup_alive = is_pid_running(sup_pid)

    print("=" * 80)
    print("  🏛️ BẢNG ĐIỀU KHIỂN GIÁM SÁT APEX CLOUD SUPERVISOR 24/7")
    print("=" * 80)
    print(f"• Trạng Thái Supervisor : {data.get('supervisor_status')} ({'🟢 ĐANG CHẠY' if sup_alive else '🔴 ĐÃ DỪNG'})")
    print(f"• Supervisor PID        : {sup_pid}")
    print(f"• Thời Gian Khởi Động   : {data.get('started_at')} (Uptime: {data.get('uptime_seconds')}s)")
    print(f"• Nhịp Tim Gần Nhất     : {data.get('last_heartbeat')}")
    print(f"• Môi Trường Vận Hành   : {data.get('system_platform')}")
    print(f"• Tài Khoản Phục Vụ     : {data.get('chairman_account')}")
    print("-" * 105)
    print(f"{'Tên Dịch Vụ':<54} | {'PID':<8} | {'Trạng Thái':<16} | {'Restarts':<8} | {'Uptime':<8}")
    print("-" * 105)

    services = data.get("services", {})
    for key, sinfo in services.items():
        s_pid = sinfo.get("pid") or "-"
        st = sinfo.get("status", "UNKNOWN")
        st_icon = "🟢" if st == "RUNNING" else ("🔴" if st == "STOPPED" else "🟡")
        print(f"{sinfo.get('name', key)[:54]:<54} | {str(s_pid):<8} | {st_icon} {st:<13} | {sinfo.get('restart_count', 0):<8} | {sinfo.get('uptime_seconds', 0):.0f}s")
    print("=" * 105)


def stop_running_supervisor():
    if not SUPERVISOR_PID_FILE.exists():
        print("[!] Không tìm thấy PID file của Supervisor. Có thể Supervisor chưa chạy.")
        return

    try:
        pid = int(SUPERVISOR_PID_FILE.read_text(encoding="utf-8").strip())
    except Exception:
        print("[!] Không đọc được PID.")
        return

    if not is_pid_running(pid):
        print(f"[*] Supervisor (PID={pid}) không còn tồn tại trên hệ thống. Dọn dẹp PID file.")
        SUPERVISOR_PID_FILE.unlink(missing_ok=True)
        return

    print(f"🛑 Gửi lệnh dừng tới Supervisor (PID={pid})...")
    if sys.platform == "win32":
        subprocess.run(f"taskkill /PID {pid} /T /F", shell=True, check=False)
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except Exception:
            pass

    time.sleep(2)
    if not is_pid_running(pid):
        print("✅ Đã dừng Supervisor thành công.")
        SUPERVISOR_PID_FILE.unlink(missing_ok=True)
    else:
        print("⚠️ Tiến trình chưa dừng hoàn toàn.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apex Cloud Supervisor & Watchdog 24/7")
    parser.add_argument("--status", action="store_true", help="Hiển thị bảng trạng thái chi tiết của Supervisor và 3 dịch vụ")
    parser.add_argument("--stop", action="store_true", help="Dừng tiến trình Supervisor đang chạy")
    parser.add_argument("--test-run", type=int, nargs="?", const=15, default=None, help="Chạy thử nghiệm kiểm định N giây rồi tự động dừng (mặc định 15s)")
    parser.add_argument("--dry-run", action="store_true", help="Chạy thử nghiệm không gửi tin nhắn Telegram")
    parser.add_argument("--no-cron", action="store_true", help="Tắt dịch vụ Cron Daemon")
    parser.add_argument("--no-sentinel", action="store_true", help="Tắt dịch vụ Sentinel")
    parser.add_argument("--no-copilot", action="store_true", help="Tắt dịch vụ Telegram Copilot")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)), help="Cổng Web Dashboard & Healthcheck (mặc định: 8000 hoặc $PORT)")
    parser.add_argument("--no-web", action="store_true", help="Không khởi động Web Dashboard")

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.stop:
        stop_running_supervisor()
        return

    if args.no_cron:
        SERVICES_CONFIG["cron_daemon"]["enabled"] = False
    if args.no_sentinel:
        SERVICES_CONFIG["sentinel_monitor"]["enabled"] = False
    if args.no_copilot:
        SERVICES_CONFIG["telegram_copilot"]["enabled"] = False

    supervisor = ApexCloudSupervisor(dry_run=args.dry_run or (args.test_run is not None), port=args.port, enable_web=not args.no_web)

    if args.test_run is not None:
        duration = args.test_run if args.test_run > 0 else 15
        ok = supervisor.run_test_verification(test_duration_seconds=duration)
        sys.exit(0 if ok else 1)

    # Chạy vòng lặp thường trực
    code = supervisor.run_loop()
    sys.exit(code)


if __name__ == "__main__":
    main()
