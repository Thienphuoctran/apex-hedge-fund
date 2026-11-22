#!/usr/bin/env python3
"""
Bộ khởi động Idempotent (Chống Trùng Lặp) Toàn Bộ Hệ Thống Apex Trên Local Windows:
- Bật đồng thời Web Portal Văn Phòng 2.5D trên http://127.0.0.1:8000
- Bật trọn vẹn 5 Phòng Ban Tự Động Chạy Nền 24/7 (`ApexCloudSupervisor`: cron_daemon 18 cột mốc,
  sentinel_monitor Victor 145 mã, telegram_copilot, inspector_trong Ban 12, live_intraday_brain).
- Tự đồng bộ Chat Artifact Văn phòng 2.5D lúc khởi động.
"""

from __future__ import annotations

import os
import socket
import sys
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.singleton_dedup_manager import is_pid_running
from scripts.start_apex_cloud_247 import ApexCloudSupervisor, SUPERVISOR_PID_FILE

HOST = os.environ.get("APEX_LOCAL_PORTAL_HOST", "127.0.0.1")
PORT = int(os.environ.get("APEX_LOCAL_PORTAL_PORT", "8000"))
PID_FILE = BASE_DIR / "data" / "apex_local_portal.pid"


def _is_port_listening(host: str, port: int, timeout: float = 0.6) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _read_pid_file(path: Path) -> int | None:
    try:
        if path.exists():
            raw = path.read_text(encoding="utf-8").strip()
            if raw.isdigit():
                return int(raw)
    except Exception:
        pass
    return None


def main() -> int:
    existing_local_pid = _read_pid_file(PID_FILE)
    existing_sup_pid = _read_pid_file(SUPERVISOR_PID_FILE)
    for pid in (existing_local_pid, existing_sup_pid):
        if pid and pid != os.getpid() and is_pid_running(pid) and _is_port_listening(HOST, PORT):
            print(f"LOCAL_PORTAL_ALREADY_RUNNING pid={pid} url=http://{HOST}:{PORT}/", flush=True)
            return 0

    if _is_port_listening(HOST, PORT):
        print(f"LOCAL_PORTAL_PORT_BUSY url=http://{HOST}:{PORT}/", flush=True)
        return 0

    os.environ.setdefault("APEX_BIND_HOST", HOST)
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")

    def _bg_sync_artifact():
        try:
            from scripts.sync_chat_office_artifact import sync_chat_office_artifact
            sync_chat_office_artifact(force_refresh=True)
        except Exception as exc:
            print(f"[WARN] Không đồng bộ được Artifact lúc khởi động: {exc}", flush=True)

    threading.Thread(target=_bg_sync_artifact, daemon=True, name="ApexInitArtifactSync").start()

    print(f"LOCAL_PORTAL_8000_READY pid={os.getpid()} url=http://{HOST}:{PORT}/ mode=SUPERVISOR_5_DAEMONS", flush=True)
    try:
        supervisor = ApexCloudSupervisor(dry_run=False, port=PORT, enable_web=True)
        return int(supervisor.run_loop(poll_interval=5) or 0)
    finally:
        try:
            if PID_FILE.exists() and PID_FILE.read_text(encoding="utf-8").strip() == str(os.getpid()):
                PID_FILE.unlink()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
