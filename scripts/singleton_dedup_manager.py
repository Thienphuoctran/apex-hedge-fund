import atexit
import json
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PID_FILE = DATA_DIR / "apex_cron_daemon.pid"
DEDUP_AUDIT_FILE = DATA_DIR / "dispatched_milestones_audit.json"


def is_pid_running_windows(pid: int) -> bool:
    """Kiểm tra xem PID có đang thực sự chạy trên Windows hay không"""
    if pid <= 0:
        return False
    try:
        output = subprocess.check_output(f'tasklist /FI "PID eq {pid}" /NH', shell=True, text=True, errors="replace")
        return str(pid) in output and "python" in output.lower()
    except Exception:
        return False


def acquire_singleton_lock() -> bool:
    """
    [SINGLETON LOCK] Đảm bảo trên toàn bộ hệ điều hành Windows CHỈ CÓ DUY NHẤT 1 DAEMON ĐƯỢC PHÉP CHẠY.
    Nếu có daemon khác đang chạy, tiến trình mới tự động dừng để triệt tiêu 100% việc gửi trùng tin nhắn.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    current_pid = os.getpid()

    if PID_FILE.exists():
        try:
            old_pid = int(PID_FILE.read_text(encoding="utf-8").strip())
            if old_pid != current_pid and is_pid_running_windows(old_pid):
                print(f"[!] [SINGLETON BLOCKED] Đã có một tiến trình Apex Cron Daemon (PID={old_pid}) đang chạy ngầm!")
                print(f"[!] Tiến trình mới (PID={current_pid}) TỰ ĐỘNG THOÁT để bảo vệ Chủ tịch không bị trùng lặp tin nhắn.")
                return False
        except Exception:
            pass

    # Ghi nhận PID mới
    PID_FILE.write_text(str(current_pid), encoding="utf-8")
    atexit.register(release_singleton_lock)
    print(f"[+] [SINGLETON LOCK ACQUIRED] Đã xác lập quyền kiểm soát độc quyền cho PID={current_pid}")
    return True


def release_singleton_lock():
    try:
        current_pid = os.getpid()
        if PID_FILE.exists():
            recorded_pid = int(PID_FILE.read_text(encoding="utf-8").strip())
            if recorded_pid == current_pid:
                PID_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def is_milestone_already_dispatched(date_str: str, milestone_id: str) -> bool:
    """
    [ATOMIC MILESTONE DEDUPLICATION]
    Kiểm tra xem một mốc tác chiến trong ngày (ví dụ 08:30 Magazine Card hoặc 18:00 BCTC) đã được phát sóng chưa.
    Nếu đã phát sóng rồi, từ chối phát lại lần thứ hai.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache = {}
    if DEDUP_AUDIT_FILE.exists():
        try:
            with open(DEDUP_AUDIT_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    milestone_key = f"{date_str}_{milestone_id}"
    return milestone_key in cache


def mark_milestone_dispatched(date_str: str, milestone_id: str, details: str = ""):
    """Ghi nhận mốc tác chiến đã được xuất bản thành công vào sổ cái chống trùng lặp"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache = {}
    if DEDUP_AUDIT_FILE.exists():
        try:
            with open(DEDUP_AUDIT_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    milestone_key = f"{date_str}_{milestone_id}"
    cache[milestone_key] = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "details": details
    }
    with open(DEDUP_AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
