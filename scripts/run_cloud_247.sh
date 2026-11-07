#!/usr/bin/env bash
# ==============================================================================
# APEX INSTITUTIONAL HEDGE FUND — GOOGLE CLOUD 24/7 LAUNCHER
# Khởi động Bộ Giám Sát Đa Tiến Trình Thể Chế (Supervisor & Watchdog)
# Quản lý 3 tiến trình con: Cron Daemon (17 cột mốc), Victor Sentinel, Telegram Co-Pilot
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "================================================================================"
echo " 🚀 KHỞI ĐỘNG APEX INSTITUTIONAL CLOUD SUPERVISOR 24/7 TRÊN GOOGLE CLOUD"
echo " Danh mục: 400 HPG + 300 TCB + 200 MBB (TCBS: 105C307855)"
echo "================================================================================"

# Tạo thư mục log nếu chưa có
mkdir -p data/logs

# Khởi chạy Supervisor bằng Python trong chế độ unbuffered
export PYTHONUNBUFFERED=1
export PYTHONIOENCODING=utf-8

python3 scripts/start_apex_cloud_247.py "$@"
