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
import gc
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

_SSE_LOCK = threading.Lock()
_ACTIVE_SSE_CLIENTS = 0
_MAX_SSE_CLIENTS = 4


def _get_process_rss_mb() -> float:
    """Đọc RSS thực tế (MB) của tiến trình hiện tại (Linux /proc hoặc fallback 0)."""
    try:
        status_p = Path("/proc/self/status")
        if status_p.exists():
            for line in status_p.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("VmRSS:"):
                    kb = float(line.split()[1])
                    return round(kb / 1024.0, 1)
    except Exception:
        pass
    try:
        import resource  # type: ignore
        ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return round(ru / 1024.0, 1) if sys.platform.startswith("linux") else round(ru / (1024.0 * 1024.0), 1)
    except Exception:
        return 0.0

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
    },
    "live_intraday_brain": {
        "name": "Apex Living Intraday Decision Brain (V4.0 Realtime)",
        "script": "scripts/apex_live_intraday_brain.py",
        "args": ["--daemon"],
        "log_file": LOGS_DIR / "live_intraday_brain.log",
        "enabled": True,
        "max_crashes_in_window": 10,
        "crash_window_seconds": 300,
        "restart_delay_seconds": 5
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

    def _is_https_request(self) -> bool:
        proto = (self.headers.get("X-Forwarded-Proto", "") or "").lower()
        return proto == "https"

    def _enforce_auth_or_deny(self, path: str) -> bool:
        """Trả True nếu được phép đi tiếp; trả False và gửi 401 nếu chưa xác thực."""
        try:
            from scripts.apex_portal_auth import (
                is_auth_enabled,
                is_request_authenticated,
                render_pin_login_html,
            )
        except Exception:
            return True

        if not is_auth_enabled() or is_request_authenticated(self.headers):
            return True

        if path.startswith("/api/"):
            self.send_response(401)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(json.dumps({
                "ok": False,
                "auth_required": True,
                "error": "Yêu cầu xác thực PIN Chủ tịch hoặc Bearer Token."
            }, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(401)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(render_pin_login_html().encode("utf-8"))
        return False

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "3600")
        self.end_headers()

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
            cloud_status = {}
            auth_on = False
            try:
                from scripts.apex_cloud_db_sync import ApexCloudDBSync
                cloud_status = ApexCloudDBSync.get_cloud_status(lightweight=True)
            except Exception:
                pass
            try:
                from scripts.apex_portal_auth import is_auth_enabled
                auth_on = is_auth_enabled()
            except Exception:
                pass
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
                "auth_enabled": auth_on,
                "cloud_db": cloud_status,
                "process_rss_mb": _get_process_rss_mb(),
                "timestamp": datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/auth/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            try:
                from scripts.apex_portal_auth import is_auth_enabled, is_request_authenticated
                auth_res = {
                    "ok": True,
                    "auth_enabled": is_auth_enabled(),
                    "authenticated": is_request_authenticated(self.headers),
                }
            except Exception as e:
                auth_res = {"ok": False, "error": str(e)}
            self.wfile.write(json.dumps(auth_res, ensure_ascii=False).encode("utf-8"))
            return

        if not self._enforce_auth_or_deny(path):
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
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            try:
                import scripts.apex_autonomous_council_engine
                import scripts.apex_summit_meeting_engine
                preview = query.get("preview", ["0"])[0] in ("1", "true", "True")
                archive_id = query.get("archive_id", [""])[0].strip() or None
                st = scripts.apex_summit_meeting_engine.get_realtime_meeting_state(
                    preview_mode=preview,
                    archive_id=archive_id
                )
                self.wfile.write(json.dumps(st, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/summit/archive":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            try:
                import scripts.apex_autonomous_council_engine
                import scripts.apex_summit_meeting_engine
                meeting_id = query.get("meeting_id", [""])[0].strip()
                if meeting_id:
                    sess = scripts.apex_autonomous_council_engine.get_archived_summit_by_id(meeting_id)
                    if sess is None:
                        self.wfile.write(json.dumps({"ok": False, "error": f"Không tìm thấy phiên họp lưu trữ '{meeting_id}'"}, ensure_ascii=False).encode("utf-8"))
                    else:
                        self.wfile.write(json.dumps({"ok": True, "session": sess}, ensure_ascii=False).encode("utf-8"))
                else:
                    ledger = scripts.apex_autonomous_council_engine.load_summit_archive_ledger()
                    state = scripts.apex_summit_meeting_engine.load_meeting_state()
                    retention = scripts.apex_autonomous_council_engine.compute_retention_status(state)
                    self.wfile.write(json.dumps({
                        "ok": True,
                        "ledger": ledger,
                        "retention_status": retention,
                    }, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/daily_live_warroom":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                def _load_j(rel_p, default_val):
                    fp = BASE_DIR / rel_p
                    if not fp.exists():
                        return default_val
                    try:
                        return json.loads(fp.read_text(encoding="utf-8"))
                    except Exception:
                        return default_val

                wr_file = BASE_DIR / "data/live_warroom_state.json"
                wr_live = _load_j("data/live_warroom_state.json", {})
                now_ict_api = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
                in_win = (now_ict_api.weekday() < 5) and ("09:00" <= now_ict_api.strftime("%H:%M") <= "16:00")
                is_stale = (not wr_file.exists()) or (in_win and (time.time() - wr_file.stat().st_mtime > 120))
                if (not wr_live) or is_stale:
                    try:
                        from scripts.apex_daily_live_warroom_engine import run_live_recon_and_decision
                        wr_live = run_live_recon_and_decision(refresh_intel=False, send_telegram=False, tag="API_ON_DEMAND")
                    except Exception:
                        pass
                hist_all = _load_j("data/live_warroom_intraday_history.json", {})
                today_key = str(wr_live.get("date") or datetime.datetime.now().strftime("%Y-%m-%d"))
                payload = {
                    "ok": True,
                    "live_warroom": wr_live,
                    "history_today": (hist_all.get(today_key) or [])[-30:] if isinstance(hist_all, dict) else [],
                    "brain_v3": _load_j("data/apex_autonomous_brain_v3_output.json", {}),
                    "weekly_plan": _load_j("data/weekly_tactical_plan_active.json", {}),
                }
                self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
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
                st["tactical_stages_html"] = generate_dynamic_tactical_stages_html(wr_state=st)
                self.wfile.write(json.dumps(st, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif path == "/api/tactical_war_room/stream":
            global _ACTIVE_SSE_CLIENTS
            try:
                max_frames = int(query.get("max_frames", ["0"])[0] or 0)
            except Exception:
                max_frames = 0
            effective_max_frames = max_frames if max_frames > 0 else 150
            with _SSE_LOCK:
                if _ACTIVE_SSE_CLIENTS >= _MAX_SSE_CLIENTS:
                    self.send_response(503)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "error": "SSE stream limit reached"}).encode("utf-8"))
                    return
                _ACTIVE_SSE_CLIENTS += 1
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.close_connection = True
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            try:
                from scripts.apex_tactical_war_room_engine import get_tactical_war_room_state
                from scripts.apex_web_portal_engine import generate_dynamic_tactical_stages_html
                frame_idx = 0
                while True:
                    st = get_tactical_war_room_state(force_refresh=False)
                    st["tactical_stages_html"] = generate_dynamic_tactical_stages_html(wr_state=st)
                    payload = f"event: war_room_tick\ndata: {json.dumps(st, ensure_ascii=False)}\n\n"
                    self.wfile.write(payload.encode("utf-8"))
                    self.wfile.flush()
                    frame_idx += 1
                    if frame_idx >= effective_max_frames:
                        break
                    time.sleep(5)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                return
            except Exception as e:
                try:
                    err_payload = f"event: error\ndata: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
                    self.wfile.write(err_payload.encode("utf-8"))
                    self.wfile.flush()
                except Exception:
                    pass
            finally:
                with _SSE_LOCK:
                    _ACTIVE_SSE_CLIENTS = max(0, _ACTIVE_SSE_CLIENTS - 1)
            return

        elif path == "/api/spillover_and_slippage":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.global_to_vn_spillover_engine import compute_global_to_vn_spillover
                from scripts.execution_slippage_tracker import get_tracker_summary
                from scripts.apex_cloud_db_sync import ApexCloudDBSync
                payload = {
                    "ok": True,
                    "global_spillover": compute_global_to_vn_spillover(force_refresh=False),
                    "execution_tracker": get_tracker_summary(),
                    "cloud_db": ApexCloudDBSync.get_cloud_status(),
                }
            except Exception as e:
                payload = {"ok": False, "error": str(e)}
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/intelligence/search":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.apex_omni_intelligence_crawler import search_market_intelligence
                q_str = query.get("q", [""])[0]
                cat_str = query.get("category", [None])[0] or None
                try:
                    lim = int(query.get("limit", ["25"])[0] or 25)
                except Exception:
                    lim = 25
                res = search_market_intelligence(query=q_str, category=cat_str, limit=max(1, min(100, lim)))
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/intelligence/alerts":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                alerts_p = DATA_DIR / "live_catalyst_alerts.json"
                bctc_p = DATA_DIR / "live_bctc_quarterly_updates.json"
                alerts_d = json.loads(alerts_p.read_text(encoding="utf-8")) if alerts_p.exists() else {"total_alerts": 0, "alerts": []}
                bctc_d = json.loads(bctc_p.read_text(encoding="utf-8")) if bctc_p.exists() else {"total_tickers_updated": 0, "ticker_updates": {}}
                self.wfile.write(json.dumps({
                    "ok": True,
                    "catalyst_alerts": alerts_d,
                    "bctc_quarterly_updates": bctc_d,
                }, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/deep_brain":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                ticker_q = query.get("ticker", [""])[0].strip().upper()
                refresh_q = query.get("refresh", ["0"])[0] in ("1", "true", "True")
                if ticker_q:
                    from scripts.apex_deep_financial_brain import analyze_deep_bctc_and_valuation
                    analysis = analyze_deep_bctc_and_valuation(ticker_q)
                    payload = {"ok": True, "mode": "single_ticker", "ticker": ticker_q, "analysis": analysis}
                else:
                    brain_file = DATA_DIR / "deep_financial_brain_analysis.json"
                    legends_file = DATA_DIR / "legend_investor_wisdom_vault.json"
                    if refresh_q or not brain_file.exists():
                        from scripts.apex_deep_financial_brain import run_full_market_alpha_optimization
                        brain_data = run_full_market_alpha_optimization(force_live=refresh_q)
                    else:
                        brain_data = json.loads(brain_file.read_text(encoding="utf-8"))
                    if not legends_file.exists():
                        from scripts.apex_evolution_and_legends_engine import run_full_evolution_cycle
                        legends_data = run_full_evolution_cycle(dry_run=False)
                    else:
                        legends_data = json.loads(legends_file.read_text(encoding="utf-8"))
                    payload = {
                        "ok": True,
                        "mode": "full_brain",
                        "generated_at": brain_data.get("generated_at", ""),
                        "account_ssot": brain_data.get("account_ssot", {}),
                        "holdings_optimizer": brain_data.get("holdings_optimizer", []),
                        "correlation_matrix": brain_data.get("correlation_matrix", {}),
                        "top_vn_alpha_picks": brain_data.get("top_vn_alpha_picks", [])[:15],
                        "top_us_alpha_picks": brain_data.get("top_us_alpha_picks", [])[:10],
                        "system_maturity_iq": legends_data.get("self_reflection", {}).get("system_maturity_iq", {}),
                        "multi_horizon_walk_forward": legends_data.get("multi_horizon_walk_forward", {}),
                        "school_attribution_matrix": legends_data.get("school_attribution_matrix", {}),
                        "legends_evaluations": legends_data.get("ticker_evaluations", []),
                        "school_summary": legends_data.get("school_summary", {}),
                    }
                self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/enterprise/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.apex_enterprise_collaboration_mesh import get_enterprise_mesh_summary
                summary = get_enterprise_mesh_summary()
                self.wfile.write(json.dumps({"ok": True, **summary}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/office/live_status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.apex_virtual_office_engine import get_virtual_office_live_state
                force_flag = query.get("force", ["0"])[0] in ("1", "true", "yes")
                payload = get_virtual_office_live_state(force_refresh=force_flag)
                self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/office/room":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.apex_virtual_office_engine import get_virtual_office_room_detail
                room_id = query.get("id", [""])[0].strip()
                force_flag = query.get("force", ["0"])[0] in ("1", "true", "yes")
                payload = get_virtual_office_room_detail(room_id=room_id, force_refresh=force_flag)
                self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/office/kanban":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.apex_virtual_office_engine import get_kanban_board_state
                board = get_kanban_board_state()
                self.wfile.write(json.dumps({"ok": True, **board}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/office/jobs":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                from scripts.apex_virtual_office_engine import get_jobs_list
                self.wfile.write(json.dumps({"ok": True, "jobs": get_jobs_list()}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif path in ("/api/office/assets/office.css", "/api/office/assets/office.js"):
            fname = "office.css" if path.endswith(".css") else "office.js"
            ctype = "text/css; charset=utf-8" if fname.endswith(".css") else "application/javascript; charset=utf-8"
            asset_path = BASE_DIR / "dashboard" / "office" / fname
            if not asset_path.exists():
                self.send_response(404)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(f"Asset not found: {fname}".encode("utf-8"))
                return
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(asset_path.read_bytes())
            return

        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            status_data = {}
            if SUPERVISOR_STATUS_FILE.exists():
                try:
                    with open(SUPERVISOR_STATUS_FILE, "r", encoding="utf-8") as f:
                        status_data = json.load(f)
                except Exception:
                    pass
            try:
                import scripts.apex_report_scanner
                import scripts.apex_web_portal_engine
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
        if parsed_url.path == "/api/auth/login":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                req_data = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
                pin_val = str(req_data.get("pin", req_data.get("token", ""))).strip()
                from scripts.apex_portal_auth import (
                    verify_pin_or_token,
                    create_session_token,
                    build_session_cookie_header,
                )
                if not verify_pin_or_token(pin_val):
                    self.send_response(401)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "error": "Mã PIN hoặc Token không đúng."}, ensure_ascii=False).encode("utf-8"))
                    return
                tok = create_session_token()
                cookie_hdr = build_session_cookie_header(tok, is_https=self._is_https_request())
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Set-Cookie", cookie_hdr)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "token": tok}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif parsed_url.path == "/api/auth/logout":
            from scripts.apex_portal_auth import build_logout_cookie_header
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Set-Cookie", build_logout_cookie_header())
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}, ensure_ascii=False).encode("utf-8"))
            return

        if not self._enforce_auth_or_deny(parsed_url.path):
            return

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

                # Gửi báo cáo nghiên cứu đồng bộ vào Telegram james_hq ở nền (không chặn HTTP response)
                def _bg_dispatch_summit_msg(_msg=user_msg, _jc=res.get('james_resp', {}).get('content', '')):
                    try:
                        from scripts.telegram_dispatcher import dispatch_message
                        dispatch_message('james_hq', f"🏛️ *[CHỈ THỊ TẠI ĐẠI HỘI NGHỊ THƯỢNG ĐỈNH]*\n👤 *Chủ tịch*: `{_msg}`\n\n{_jc}")
                    except Exception:
                        pass

                threading.Thread(target=_bg_dispatch_summit_msg, daemon=True).start()

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
                content_length = int(self.headers.get("Content-Length", 0))
                body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
                req_data = json.loads(body_bytes.decode("utf-8") or "{}")
            except Exception:
                req_data = {}
            try:
                import scripts.apex_autonomous_council_engine
                import scripts.apex_summit_meeting_engine
                approved_by = str(req_data.get("approved_by") or "Chủ tịch Trần Quốc Thiên Phước").strip()
                res = scripts.apex_autonomous_council_engine.approve_summit_resolution(approved_by=approved_by)

                # Gửi thông báo đến Telegram james_hq ở nền (không chặn HTTP response)
                def _bg_dispatch_approve(_res=res, _by=approved_by):
                    try:
                        from scripts.telegram_dispatcher import dispatch_message
                        mid = _res.get("meeting_id", "APEX-SUMMIT")
                        unlock_disp = (_res.get("retention_status") or {}).get("min_cleanup_display", "+2H")
                        dispatch_message(
                            "james_hq",
                            f"👑 *[CHỦ TỊCH ĐÃ KÝ DUYỆT NGHỊ QUYẾT THƯỢNG ĐỈNH ({mid})]*\n\n"
                            f"👤 *Người ký*: `{_by}`\n"
                            f"📜 *Văn kiện*: `{_res.get('resolution_report_path', '08_Master_Investment_CIO/council_resolutions/')}`\n"
                            f"⏳ *Quy chế dọn phòng (Điều 5)*: Được lưu trữ & dọn sạch sau tối thiểu 2 tiếng (`{unlock_disp}`)\n"
                            f"🛡️ *Tổng Kiểm Sát Ban 12 Trọng*: Đã niêm phong pháp lý thể chế & đồng bộ Kho Lưu Trữ 100%!"
                        )
                    except Exception:
                        pass

                threading.Thread(target=_bg_dispatch_approve, daemon=True).start()

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif parsed_url.path == "/api/summit/schedule":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
                req_data = json.loads(body_bytes.decode("utf-8") or "{}")
            except Exception:
                req_data = {}
            try:
                import scripts.apex_autonomous_council_engine
                import scripts.apex_summit_meeting_engine
                start_time_str = str(req_data.get("start_time") or "").strip() or None
                duration_minutes = int(req_data.get("duration_minutes") or 30)
                prep_minutes = int(req_data.get("prep_minutes") or 20)
                topic_str = str(req_data.get("topic") or "").strip() or None
                trigger_prep_now = bool(req_data.get("trigger_prep_now", True))
                res = scripts.apex_summit_meeting_engine.schedule_custom_summit_meeting(
                    start_time_str=start_time_str,
                    duration_minutes=duration_minutes,
                    topic=topic_str,
                    trigger_prep_now=trigger_prep_now,
                    prep_minutes=prep_minutes,
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return

        elif parsed_url.path == "/api/summit/archive_and_clean":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
                req_data = json.loads(body_bytes.decode("utf-8") or "{}")
            except Exception:
                req_data = {}
            try:
                import scripts.apex_autonomous_council_engine
                force_flag = bool(req_data.get("force", False))
                requested_by = str(req_data.get("requested_by") or "Chủ tịch Trần Quốc Thiên Phước").strip()
                res = scripts.apex_autonomous_council_engine.clean_and_reset_summit_room(
                    force=force_flag,
                    requested_by=requested_by,
                )
                status_code = 200 if res.get("ok") else 409
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
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

        elif parsed_url.path == "/api/sync_tcinvest":
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                body_str = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                req_data = json.loads(body_str)

                action = str(req_data.get("action", "")).strip().upper()
                symbol = str(req_data.get("symbol", "")).strip().upper()
                shares = int(req_data.get("shares", 0) or 0)
                price = float(req_data.get("price", 0) or 0)
                stop_loss = float(req_data.get("stop_loss", 0) or 0)
                take_profit = float(req_data.get("take_profit", 0) or 0)
                cash_override = req_data.get("cash_balance_vnd", None)
                reason = str(req_data.get("reason", "")).strip()

                from scripts.portfolio_state_manager import PortfolioStateManager
                from scripts.apex_live_intraday_brain import invalidate_live_cache, compute_live_war_room_snapshot, sync_live_intraday_report
                from scripts.apex_tactical_war_room_engine import push_external_war_room_alert, get_tactical_war_room_state

                ok = False
                msg = ""
                if action == "BUY":
                    if not symbol or shares <= 0 or price <= 0:
                        raise ValueError("Lệnh BUY yêu cầu symbol, shares > 0 và price > 0.")
                    ok, msg = PortfolioStateManager.execute_buy_order(
                        symbol=symbol,
                        shares=shares,
                        buy_price=price,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        reason=reason or "Chủ tịch đồng bộ 1-Click từ TCInvest War-Room V4.0",
                    )
                    if ok:
                        try:
                            from scripts.execution_slippage_tracker import record_execution_fill
                            record_execution_fill(symbol=symbol, executed_price=price, shares=shares)
                        except Exception:
                            pass
                elif action == "SELL":
                    if not symbol or shares <= 0 or price <= 0:
                        raise ValueError("Lệnh SELL yêu cầu symbol, shares > 0 và price > 0.")
                    ok, msg = PortfolioStateManager.execute_sell_order(
                        symbol=symbol,
                        shares=shares,
                        sell_price=price,
                        reason=reason or "Chủ tịch đồng bộ 1-Click từ TCInvest War-Room V4.0",
                    )
                elif action == "RECONCILE":
                    st_curr = PortfolioStateManager.load_state()
                    updates = []
                    if cash_override is not None and str(cash_override).strip() != "":
                        new_cash = float(cash_override)
                        st_curr["cash_balance_vnd"] = round(new_cash, 2)
                        updates.append(f"Tiền mặt -> {new_cash:,.0f} đ")
                    if symbol and symbol in st_curr.get("active_positions", {}):
                        pos = st_curr["active_positions"][symbol]
                        if stop_loss > 0:
                            pos["stop_loss"] = round(stop_loss, 2)
                            updates.append(f"{symbol} Stop -> {stop_loss:,.0f} đ")
                        if take_profit > 0:
                            pos["tp1"] = round(take_profit, 2)
                            updates.append(f"{symbol} TP1 -> {take_profit:,.0f} đ")
                    if not updates:
                        raise ValueError("RECONCILE yêu cầu cash_balance_vnd hoặc symbol/stop_loss/take_profit hợp lệ.")
                    ok = PortfolioStateManager.save_state(st_curr)
                    msg = "Đã đối soát SSOT trực tiếp: " + ", ".join(updates) if ok else "Lỗi lưu state SSOT."
                else:
                    raise ValueError("action phải là BUY, SELL hoặc RECONCILE.")

                if not ok:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "error": msg}, ensure_ascii=False).encode("utf-8"))
                    return

                invalidate_live_cache()
                snap = compute_live_war_room_snapshot(force_refresh=True)
                sync_live_intraday_report(snap, force_write=True)
                push_external_war_room_alert(
                    sender="TCInvest 1-Click Sync (SSOT Engine)",
                    alert_type="tcinvest_sync",
                    content=f"⚡ [ĐỒNG BỘ LỆNH TCINVEST] {msg}",
                    role="specialist",
                    alert_key=f"sync_{int(time.time()*1000)}",
                )
                wr_state = get_tactical_war_room_state(force_refresh=True)

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": True,
                    "message": msg,
                    "war_room_state": wr_state,
                }, ensure_ascii=False).encode("utf-8"))
            except ValueError as ve:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(ve)}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return
        elif parsed_url.path == "/api/intelligence/crawl":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b""
            try:
                req_data = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
                force_flag = bool(req_data.get("force", True))
                from scripts.apex_omni_intelligence_crawler import crawl_realtime_market_intelligence
                res = crawl_realtime_market_intelligence(force_refresh=force_flag)
                sh = res.get("source_health", [])
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": True,
                    "crawled_at": res.get("crawled_at", ""),
                    "universe_counts": res.get("universe_counts", {}),
                    "total_items": res.get("total_items", 0),
                    "category_counts": res.get("category_counts", {}),
                    "sources_online": f"{sum(1 for s in sh if s.get('ok'))}/{len(sh)}" if sh else "0/0",
                    "latest_items": res.get("items", [])[:15],
                }, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return
        elif parsed_url.path == "/api/enterprise/convene":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b""
            try:
                req_data = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
                directive = str(req_data.get("directive") or "Họp giao ban toàn doanh nghiệp đánh giá danh mục và tầm ngắm").strip()
                ticker = str(req_data.get("ticker") or "").strip().upper() or None
                trigger_src = str(req_data.get("trigger_source") or "WEB_PORTAL_CONVENE").strip()
                sync_flag = bool(req_data.get("sync_cloud", True))
                from scripts.apex_enterprise_collaboration_mesh import (
                    get_enterprise_mesh_summary,
                    run_enterprise_work_session,
                )
                sess = run_enterprise_work_session(
                    directive=directive,
                    ticker=ticker,
                    trigger_source=trigger_src,
                    sync_cloud=sync_flag,
                )
                summary = get_enterprise_mesh_summary()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": True,
                    "session": sess,
                    "summary": summary,
                }, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return
        elif parsed_url.path == "/api/war_room/publish_report":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                req_data = json.loads(raw_body) if raw_body.strip() else {}
            except Exception:
                req_data = {}
            try:
                from scripts.apex_tactical_war_room_engine import publish_war_room_tactical_report
                trigger_reason = str(req_data.get("trigger_reason") or "MANUAL_WAR_ROOM_PUBLISH")
                target_ticker = req_data.get("ticker") or None
                res = publish_war_room_tactical_report(
                    trigger_reason=trigger_reason,
                    target_ticker=target_ticker,
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return
        elif parsed_url.path == "/api/office/room_action":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                req_data = json.loads(raw_body) if raw_body.strip() else {}
            except Exception:
                req_data = {}
            try:
                from scripts.apex_virtual_office_engine import trigger_room_action
                room_id = str(req_data.get("room_id") or "").strip()
                action = str(req_data.get("action") or "").strip()
                res = trigger_room_action(room_id=room_id, action=action, payload=req_data)
                status_code = 200 if res.get("ok") else 400
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
            return
        elif parsed_url.path == "/api/office/kanban":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                req_data = json.loads(raw_body) if raw_body.strip() else {}
            except Exception:
                req_data = {}
            try:
                from scripts.apex_virtual_office_engine import (
                    create_kanban_task,
                    move_kanban_task,
                    delete_kanban_task,
                )
                op = str(req_data.get("op") or "").strip().lower()
                if op == "create":
                    res = create_kanban_task(
                        title=str(req_data.get("title") or ""),
                        dept=str(req_data.get("dept") or "Khối 3 (James & Palmer)"),
                        assignee=str(req_data.get("assignee") or "Trưởng Khối"),
                        priority=str(req_data.get("priority") or "HIGH"),
                        scheduled_time=str(req_data.get("scheduled_time") or ""),
                        output_note=str(req_data.get("output") or ""),
                        status=str(req_data.get("status") or "BACKLOG"),
                    )
                elif op == "move":
                    res = move_kanban_task(
                        task_id=str(req_data.get("task_id") or "").strip(),
                        new_status=str(req_data.get("status") or "").strip(),
                    )
                elif op == "delete":
                    res = delete_kanban_task(task_id=str(req_data.get("task_id") or "").strip())
                else:
                    raise ValueError(f"Thao tác Kanban không hợp lệ: {op}")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            except ValueError as ve:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(ve)}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8"))
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

        self.is_render_cloud = bool(
            os.environ.get("RENDER")
            or os.environ.get("RENDER_SERVICE_ID")
            or os.environ.get("APEX_CLOUD_COMPACT_MODE", "").strip().lower() in ("1", "true", "yes")
        )
        self.compact_cloud_mode = self.is_render_cloud and (not dry_run)
        tg_owner = os.environ.get("TELEGRAM_POLLING_OWNER", "pc").strip().lower()
        disable_tg = (
            os.environ.get("APEX_DISABLE_TELEGRAM_COPILOT", "").strip().lower() in ("1", "true", "yes")
            or (self.is_render_cloud and tg_owner != "cloud")
        )
        if not dry_run and disable_tg and "telegram_copilot" in self.services:
            self.services["telegram_copilot"].enabled = False
            self.services["telegram_copilot"].status = "DISABLED_PC_OWNER"

        if self.compact_cloud_mode:
            for consolidated_key in ("sentinel_monitor", "inspector_trong", "live_intraday_brain"):
                if consolidated_key in self.services:
                    self.services[consolidated_key].enabled = False
                    self.services[consolidated_key].status = "IN_PROCESS_COMPACT"

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
            "compact_cloud_mode": self.compact_cloud_mode,
            "process_rss_mb": _get_process_rss_mb(),
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

    def _start_compact_inprocess_sentinel(self):
        """Vòng lặp gộp Sentinel + War-Room + Trong Technical Sweep trong 1 thread gọn nhẹ (< 150MB RAM)."""
        def _compact_worker():
            log_sup("🛡️ [COMPACT CLOUD LOOP] Khởi chạy luồng hợp nhất Victor + War-Room + Quét 145 Mã + Ban 12 Trọng (Tiết kiệm ~300MB RAM).")
            last_trong_ts = 0.0
            last_warroom_145_ts = 0.0
            while self.running:
                try:
                    from scripts.apex_live_intraday_brain import is_vn_trading_hours, compute_live_war_room_snapshot, sync_live_intraday_report
                    from scripts.vn3_portfolio_autonomous_sentinel import fetch_live_quotes, check_triggers_and_alert, update_telemetry
                    in_vn = is_vn_trading_hours()
                    quotes = fetch_live_quotes()
                    check_triggers_and_alert(quotes, notify_telegram=in_vn)
                    update_telemetry(quotes)
                    snap = compute_live_war_room_snapshot(force_refresh=in_vn)
                    sync_live_intraday_report(snap, force_write=False)

                    now_ts = time.time()
                    if now_ts - last_warroom_145_ts >= (120 if in_vn else 300):
                        try:
                            from scripts.apex_daily_live_warroom_engine import run_live_recon_and_decision
                            run_live_recon_and_decision(refresh_intel=False, send_telegram=in_vn, tag="CLOUD_247_SYNC")
                        except Exception as _we:
                            log_sup(f"⚠️ [CLOUD 145-STOCK SYNC WARNING] {_we}", echo=False)
                        last_warroom_145_ts = now_ts

                    if now_ts - last_trong_ts >= 900:
                        try:
                            from scripts.apex_inspector_trong import ApexInspectorTrong
                            ApexInspectorTrong.audit_system_technical_integrity_247()
                        except Exception:
                            pass
                        last_trong_ts = now_ts
                    gc.collect()
                    sleep_sec = 30 if in_vn else 90
                except Exception as _ce:
                    log_sup(f"⚠️ [COMPACT LOOP WARNING] {_ce}", echo=False)
                    sleep_sec = 60
                for _ in range(sleep_sec):
                    if not self.running:
                        break
                    time.sleep(1)

        threading.Thread(target=_compact_worker, daemon=True, name="ApexCompactCloudSentinel").start()

    def start_all(self):
        log_sup(f"🌟 BẮT ĐẦU KHỞI ĐỘNG HỆ THỐNG APEX CLOUD SUPERVISOR 24/7 (Compact={self.compact_cloud_mode})...")
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

        # BƯỚC 1 (QUAN TRỌNG NHẤT CHO RENDER): Mở Web Port NGAY TỨC THÌ để triệt tiêu lỗi i/o timeout khi khởi động
        if self.enable_web:
            try:
                class _DaemonThreadingHTTPServer(http.server.ThreadingHTTPServer):
                    daemon_threads = True
                    allow_reuse_address = True
                    request_queue_size = 32

                ApexSupervisorHTTPHandler.supervisor_ref = self
                self.http_server = _DaemonThreadingHTTPServer(("0.0.0.0", self.port), ApexSupervisorHTTPHandler)
                t = threading.Thread(target=self.http_server.serve_forever, daemon=True)
                t.start()
                log_sup(f"🌐 [IMMORTAL WEB SERVER] Đã mở cổng http://0.0.0.0:{self.port} TỨC THÌ (Healthcheck: /api/health)")
            except Exception as e:
                log_sup(f"[!] Cảnh báo mở Web Port {self.port}: {e}. Tiếp tục chạy các dịch vụ ngầm bình thường.")
                self.http_server = None

        # BƯỚC 2: Khởi động các dịch vụ con được bật (Trong Compact Cloud Mode chỉ bật cron_daemon + tắt Telegram Cloud để chống 409)
        for k, s in self.services.items():
            if s.enabled:
                s.start()
            else:
                log_sup(f"ℹ️ Dịch vụ '{k}' ở trạng thái {s.status} (tối ưu tài nguyên & chống xung đột).")
        self._save_status()

        # BƯỚC 3: Đồng bộ SQLite Lakehouse Vault V5.0 & pre-warm ở nền (không chặn cổng 10000)
        def _bg_sqlite_sync_and_warmup():
            try:
                log_sup("🔄 [BG-SYNC] Đang đồng bộ thư viện báo cáo Markdown vào SQLite Lakehouse Vault V5.0...")
                from scripts.migrate_markdown_to_sqlite import migrate_all_markdown_reports
                migrate_all_markdown_reports()
                gc.collect()
                log_sup("✅ [BG-SYNC] Đồng bộ SQLite Lakehouse Vault thành công!")
            except Exception as e_mig:
                log_sup(f"⚠️ [BG-SYNC] Cảnh báo đồng bộ SQLite ban đầu: {e_mig}")
            if self.enable_web:
                try:
                    from scripts.apex_tactical_war_room_engine import get_tactical_war_room_state
                    get_tactical_war_room_state(force_refresh=False)
                    gc.collect()
                    log_sup("⚡ [WARMUP] Đã nạp sẵn cache Living War-Room Snapshot thành công.")
                except Exception as _we:
                    log_sup(f"⚠️ [WARMUP] Bỏ qua warmup ban đầu: {_we}")

        threading.Thread(target=_bg_sqlite_sync_and_warmup, daemon=True, name="ApexBgSqliteSync").start()

        if self.compact_cloud_mode:
            self._start_compact_inprocess_sentinel()

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
                    rss_mb = _get_process_rss_mb()
                    if rss_mb > 240.0:
                        gc.collect()
                    if rss_mb > 360.0:
                        log_sup(f"⚠️ [MEMORY GUARD] RSS Supervisor hiện đạt {rss_mb:.1f} MB (ngưỡng 512MB Render) -> Đã chạy gc.collect().")
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
