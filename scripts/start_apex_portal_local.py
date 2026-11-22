#!/usr/bin/env python3
"""
Bộ khởi động Idempotent (Chống Trùng Lặp) Web Portal Văn Phòng 2.5D Apex trên 127.0.0.1:8000.
Tự động đồng bộ Artifact chat khi khởi động và chịu lỗi sạch sẽ nếu máy vừa khởi động lại.
"""

from __future__ import annotations

import http.server
import os
import socket
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.singleton_dedup_manager import is_pid_running
from scripts.start_apex_cloud_247 import ApexSupervisorHTTPHandler

HOST = os.environ.get("APEX_LOCAL_PORTAL_HOST", "127.0.0.1")
PORT = int(os.environ.get("APEX_LOCAL_PORTAL_PORT", "8000"))
PID_FILE = BASE_DIR / "data" / "apex_local_portal.pid"


class _ReusableThreadingHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def _is_port_listening(host: str, port: int, timeout: float = 0.6) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _read_existing_pid() -> int | None:
    try:
        if PID_FILE.exists():
            raw = PID_FILE.read_text(encoding="utf-8").strip()
            if raw.isdigit():
                return int(raw)
    except Exception:
        pass
    return None


def main() -> int:
    existing_pid = _read_existing_pid()
    if existing_pid and existing_pid != os.getpid() and is_pid_running(existing_pid) and _is_port_listening(HOST, PORT):
        print(f"LOCAL_PORTAL_ALREADY_RUNNING pid={existing_pid} url=http://{HOST}:{PORT}/", flush=True)
        return 0

    if _is_port_listening(HOST, PORT):
        print(f"LOCAL_PORTAL_PORT_BUSY url=http://{HOST}:{PORT}/", flush=True)
        return 0

    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")

    try:
        from scripts.sync_chat_office_artifact import sync_chat_office_artifact
        sync_chat_office_artifact(force_refresh=True)
    except Exception as exc:
        print(f"[WARN] Không đồng bộ được Artifact lúc khởi động: {exc}", flush=True)

    srv = _ReusableThreadingHTTPServer((HOST, PORT), ApexSupervisorHTTPHandler)
    print(f"LOCAL_PORTAL_8000_READY pid={os.getpid()} url=http://{HOST}:{PORT}/", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
        try:
            if PID_FILE.exists() and PID_FILE.read_text(encoding="utf-8").strip() == str(os.getpid()):
                PID_FILE.unlink()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
