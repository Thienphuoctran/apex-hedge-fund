#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restart apex_institutional_cron_daemon.py cleanly.
"""

import subprocess
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Kill any existing instances of apex_institutional_cron_daemon.py
kill_cmd = [
    "powershell",
    "-Command",
    "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*apex_institutional_cron_daemon.py*' -and $_.ProcessId -ne $PID } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host 'Stopped old PID:' $_.ProcessId }"
]
res = subprocess.run(kill_cmd, capture_output=True, text=True)
print(res.stdout)

# 2. Launch new daemon in background
daemon_script = str(BASE_DIR / "scripts" / "apex_institutional_cron_daemon.py")
p = subprocess.Popen([sys.executable, daemon_script, "--daemon"], cwd=str(BASE_DIR))
print(f"[+] Launched new apex_institutional_cron_daemon.py with PID: {p.pid}")
