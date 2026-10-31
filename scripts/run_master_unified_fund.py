#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER UNIFIED FUND ORCHESTRATOR: Toàn Bộ Hệ Thống Quỹ Đầu Tư Định Lượng 14 Phòng Ban & Ban Đầu Tư Tối Cao (Master CIO Desk)
File: scripts/run_master_unified_fund.py

Kích hoạt 1-Click:
1. Chạy Chu Trình 7 Phòng Ban Toàn Cầu (Mỹ / US Markets) & Alex (Ban 7 Global).
2. Chạy Chu Trình 7 Phòng Ban Việt Nam (HOSE / HNX) & Minh Quân (Ban 7 VN).
3. Kích hoạt Ban Đầu Tư Tối Cao (Ban 8 Master CIO):
   - Tổng hợp BCTC 2 thị trường.
   - Chủ trì hội nghị thượng đỉnh Alex vs Minh Quân.
   - Phân bổ vốn ban đầu khoa học (USD & VNĐ) theo ATR Risk-Parity & Kelly Criterion.
   - Khóa rủi ro Stop 2xATR và xuất Sổ Lệnh Master Blotter.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
VN_SCRIPTS_DIR = BASE_DIR / "VN_Market" / "scripts"


def run_cmd(cmd_list: list[str], desc: str) -> None:
    print(f"\n>>> [TIẾN TRÌNH] {desc}...")
    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run(cmd_list, cwd=str(BASE_DIR), env=sub_env)
    if res.returncode != 0:
        print(f"[CẢNH BÁO] Bước {desc} trả về exit code {res.returncode}")
    else:
        print(f"[HOÀN TẤT] {desc}")


def main():
    parser = argparse.ArgumentParser(description="Hệ Thống Quỹ Đầu Tư Thống Nhất Global & VN (Apex Master CIO Suite)")
    parser.add_argument("--capital-usd", type=float, default=100000.0, help="Tổng vốn ban đầu bằng USD (Mặc định: $100,000)")
    parser.add_argument("--capital-vnd", type=float, default=None, help="Tổng vốn ban đầu bằng VNĐ (vd: 2540000000)")
    parser.add_argument("--fast", action="store_true", help="Chạy chế độ nhanh với dữ liệu đã lưu")
    parser.add_argument("--cio-only", action="store_true", help="Chỉ chạy bước phân bổ vốn Master CIO")
    parser.add_argument("--telegram", action="store_true", default=True, help="Tự động gửi bản tin sáng tới Telegram Bot")
    parser.add_argument("--no-telegram", action="store_true", help="Không gửi tin nhắn Telegram")
    args = parser.parse_args()

    start_time = time.time()
    print("=" * 80)
    print(" ⭐ HỆ THỐNG QUỸ ĐẦU TƯ ĐỊNH LƯỢNG ĐA TẦNG — TOÀN CẦU & VIỆT NAM (APEX MASTER CIO)")
    print("   VĂN PHÒNG TỔNG TƯ LỆNH ĐẦU TƯ: 'KHẨU SÚNG BẤM CÒ THỰC THI DANH MỤC TỐI THƯỢNG'")
    print("=" * 80)

    if not args.cio_only:
        # Bước 1: Chạy Hệ Thống Toàn Cầu (US Market)
        global_args = ["--fast"] if args.fast else []
        run_cmd([sys.executable, str(SCRIPTS_DIR / "run_daily_pipeline.py")] + global_args, "Chạy Hệ Thống 7 Phòng Ban Toàn Cầu & Alex")

        # Bước 2: Chạy Hệ Thống Việt Nam (VN Market)
        run_cmd([sys.executable, str(VN_SCRIPTS_DIR / "run_vn_pipeline.py")], "Chạy Hệ Thống 7 Phòng Ban Việt Nam & Minh Quân")

    # Bước 3: Kích Hoạt Ban Đầu Tư Tối Cao Master CIO
    cio_cmd = [sys.executable, str(SCRIPTS_DIR / "master_cio_allocator.py")]
    if args.capital_vnd is not None and args.capital_vnd > 0:
        cio_cmd.extend(["--capital-vnd", str(args.capital_vnd)])
    else:
        cio_cmd.extend(["--capital-usd", str(args.capital_usd)])

    run_cmd(cio_cmd, "Ban Đầu Tư Tối Cao (Ban 8) Tính Toán Phân Bổ Vốn & Lập Sổ Lệnh Master Blotter")

    # Bước 4: Kích Hoạt Ban 9 Live Portfolio Sentinel Audit ("Victor")
    run_cmd([sys.executable, str(SCRIPTS_DIR / "intraday_portfolio_sentinel.py"), "--scan-once"], "Ban 9 ('Victor') Rà Soát Giám Sát Danh Mục Thời Gian Thực")

    # Bước 5: Gửi Bản Tin Khai Sáng & Sổ Lệnh Sáng Sớm Qua Telegram
    if not args.no_telegram:
        run_cmd([sys.executable, str(SCRIPTS_DIR / "telegram_morning_reporter.py")], "Gửi Bản Tin Khai Sáng & Sổ Lệnh Master Blotter qua Telegram Bot")

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f" [THỰC THI HOÀN TẤT TRONG {elapsed:.1f} GIÂY] KHẨU SÚNG ĐÃ SẴN SÀNG NẠP ĐẠN & BẤM CÒ!")
    print(" - Báo cáo Quyết định: 08_Master_Investment_CIO/YYYY-MM-DD_Master_CIO_Final_Decision.md")
    print(" - Sổ Lệnh JSON: 08_Master_Investment_CIO/master_execution_blotter.json")
    print(" - Giám Sát Thời Gian Thực (Ban 9): 09_Realtime_Portfolio_Sentinel/live_sentinel_status.md")
    print("=" * 80)


if __name__ == "__main__":
    main()
