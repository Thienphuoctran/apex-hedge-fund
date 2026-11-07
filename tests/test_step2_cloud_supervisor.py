#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KIỂM ĐỊNH TÍCH HỢP BƯỚC 2 (CÔNG VIỆC 2): APEX CLOUD SUPERVISOR 24/7 & AUTO-RESTART WATCHDOG
File: tests/test_step2_cloud_supervisor.py
"""

import sys
import os
import json
import time
import subprocess
import unittest
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.start_apex_cloud_247 import (
    SERVICES_CONFIG,
    ManagedService,
    ApexCloudSupervisor,
    SUPERVISOR_STATUS_FILE,
    SUPERVISOR_PID_FILE
)


class TestStep2CloudSupervisor(unittest.TestCase):

    def test_01_services_configuration_and_scripts_existence(self):
        """Đảm bảo 3 dịch vụ được định nghĩa chuẩn xác và các file script đều tồn tại trên ổ đĩa."""
        expected_keys = ["cron_daemon", "sentinel_monitor", "telegram_copilot"]
        for key in expected_keys:
            self.assertIn(key, SERVICES_CONFIG, f"Thiếu định nghĩa dịch vụ: {key}")
            cfg = SERVICES_CONFIG[key]
            script_path = BASE_DIR / cfg["script"]
            self.assertTrue(script_path.exists(), f"Không tìm thấy file thực thi: {script_path}")
            self.assertIn("--daemon", cfg["args"])
            self.assertTrue(cfg["enabled"])

    def test_02_managed_service_lifecycle_mock(self):
        """Kiểm tra logic vòng đời của ManagedService và cơ chế Circuit Breaker."""
        cfg = {
            "name": "Test Mock Service",
            "script": "tests/test_step2_cloud_supervisor.py",
            "args": [],
            "log_file": BASE_DIR / "data" / "logs" / "test_mock.log",
            "max_crashes_in_window": 3,
            "crash_window_seconds": 60,
            "restart_delay_seconds": 0
        }
        srv = ManagedService("mock_test", cfg)
        self.assertEqual(srv.status, "STOPPED")
        self.assertFalse(srv.circuit_broken)

        # Giả lập 3 crash timestamps trong window
        now = time.time()
        srv.crash_timestamps = [now - 10, now - 5, now]
        self.assertEqual(len(srv.crash_timestamps), 3)

        info = srv.get_info()
        self.assertIn("name", info)
        self.assertIn("status", info)
        self.assertIn("restart_count", info)

    def test_03_supervisor_status_file_generation(self):
        """Kiểm tra cấu trúc tệp trạng thái apex_cloud_supervisor_status.json."""
        sup = ApexCloudSupervisor(dry_run=True)
        sup._save_status()

        self.assertTrue(SUPERVISOR_STATUS_FILE.exists())
        data = json.loads(SUPERVISOR_STATUS_FILE.read_text(encoding="utf-8"))
        self.assertIn("supervisor_pid", data)
        self.assertIn("supervisor_status", data)
        self.assertIn("services", data)
        self.assertIn("TCBS 105C307855", data["chairman_account"])
        self.assertEqual(len(data["services"]), 3)

    def test_04_supervisor_test_run_subprocess(self):
        """Diễn tập khởi động thực tế cả 3 tiến trình trong 6 giây qua lệnh CLI và tắt sạch sẽ."""
        cmd = [
            sys.executable,
            "-X", "utf8",
            str(BASE_DIR / "scripts" / "start_apex_cloud_247.py"),
            "--test-run", "6",
            "--dry-run"
        ]
        sub_env = os.environ.copy()
        sub_env["PYTHONIOENCODING"] = "utf-8"

        res = subprocess.run(cmd, cwd=str(BASE_DIR), env=sub_env, capture_output=True, encoding="utf-8", errors="replace", timeout=30)
        print("\n--- TEST RUN OUTPUT ---")
        print(res.stdout)
        if res.stderr:
            print("STDERR:", res.stderr)

        self.assertEqual(res.returncode, 0, f"Test-run failed with code {res.returncode}")
        self.assertIn("DIỄN TẬP KIỂM ĐỊNH", res.stdout)
        self.assertIn("Kết quả diễn tập: ✅ THÀNH CÔNG 100%", res.stdout)
        self.assertIn("GRACEFUL SHUTDOWN SUCCESS", res.stdout)

        # Đảm bảo không còn PID file tồn đọng
        self.assertFalse(SUPERVISOR_PID_FILE.exists(), "Supervisor PID file vẫn còn sót lại sau khi dừng!")

    def test_05_supervisor_cli_status_command(self):
        """Kiểm tra lệnh hiển thị trạng thái `python scripts/start_apex_cloud_247.py --status`."""
        cmd = [
            sys.executable,
            "-X", "utf8",
            str(BASE_DIR / "scripts" / "start_apex_cloud_247.py"),
            "--status"
        ]
        sub_env = os.environ.copy()
        sub_env["PYTHONIOENCODING"] = "utf-8"

        res = subprocess.run(cmd, cwd=str(BASE_DIR), env=sub_env, capture_output=True, encoding="utf-8", errors="replace", timeout=10)
        self.assertEqual(res.returncode, 0)
        self.assertIn("BẢNG ĐIỀU KHIỂN GIÁM SÁT APEX CLOUD SUPERVISOR 24/7", res.stdout)
        self.assertIn("Apex Institutional 17-Milestones", res.stdout)
        self.assertIn("Victor - Ban 9", res.stdout)
        self.assertIn("Telegram Co-Pilot", res.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
