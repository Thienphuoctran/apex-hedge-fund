#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BAN QUẢN TRỊ HẠ TẦNG CLOUD — APEX CODESPACES & CLOUD CONTAINER KEEP-ALIVE DAEMON
File: scripts/apex_codespaces_keepalive.py
Chức năng:
- Tạo nhịp tim I/O liên tục mỗi 45 giây để ngăn chặn cơ chế Idle Sleep của GitHub Codespaces / Cloud Container.
- Tự động ping vào endpoint kiểm tra sức khỏe của Supervisor (http://127.0.0.1:8000/api/health) để giữ container luôn thức.
- Xuất bản telemetry nhịp tim vào data/codespaces_keepalive.json phục vụ Ban 12 Trọng thanh tra.
"""

import os
import sys
import time
import json
import datetime
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
HEARTBEAT_FILE = DATA_DIR / "codespaces_keepalive.json"
LOG_FILE = DATA_DIR / "codespaces_keepalive.log"

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def log_keepalive(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [KEEP-ALIVE] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def ping_local_health(port: int = 8000) -> bool:
    url = f"http://127.0.0.1:{port}/api/health"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ApexKeepAliveDaemon/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def run_keepalive_loop(interval_sec: int = 45, port: int = 8000):
    log_keepalive(f"🚀 Khởi động Apex Cloud Container Keep-Alive Daemon (Chu kỳ: {interval_sec}s, Ping Port: {port})...")
    log_keepalive("🛡️ Giữ cho Container luôn thức 24/24, triệt tiêu nguy cơ Idle Sleep khi đóng tab!")
    
    pulse_count = 0
    start_time = time.time()
    
    while True:
        try:
            pulse_count += 1
            now = datetime.datetime.now()
            ts_str = now.strftime("%Y-%m-%d %H:%M:%S")
            uptime = round(time.time() - start_time, 1)
            
            # Ping supervisor health
            health_ok = ping_local_health(port)
            status_text = "SUPERVISOR_ONLINE_200" if health_ok else "SUPERVISOR_LOCAL_WAITING"
            
            telemetry = {
                "daemon_name": "Apex Codespaces Keep-Alive Daemon",
                "pid": os.getpid(),
                "pulse_count": pulse_count,
                "uptime_seconds": uptime,
                "last_pulse": ts_str,
                "supervisor_health_ping": status_text,
                "status": "IMMORTAL_ACTIVE"
            }
            
            with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
                json.dump(telemetry, f, indent=2, ensure_ascii=False)
                
            log_keepalive(f"💓 [PULSE #{pulse_count}] Nhịp tim hoạt động bình thường | Uptime: {uptime}s | {status_text}")
            
        except KeyboardInterrupt:
            log_keepalive("🛑 Dừng Keep-Alive Daemon theo lệnh bàn phím.")
            break
        except Exception as e:
            log_keepalive(f"[!] Cảnh báo nhịp tim: {e}")
            
        time.sleep(interval_sec)


if __name__ == "__main__":
    port_arg = int(os.environ.get("PORT", 8000))
    interval_arg = 45
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        interval_arg = int(sys.argv[1])
    run_keepalive_loop(interval_sec=interval_arg, port=port_arg)
