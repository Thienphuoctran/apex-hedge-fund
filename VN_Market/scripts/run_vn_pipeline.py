#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_vn_pipeline.py - Trình Kích Hoạt 1-Click Chu Trình 7 Phòng Ban AI Đầu Tư Chứng Khoán Việt Nam
Tách biệt hoàn toàn, vận hành độc lập, không xung đột dữ liệu.
"""

import os
import sys
import subprocess
import time

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

PIPELINE_STEPS = [
    ("Bước 1: Thu thập Dữ liệu Giá & Chỉ số Vĩ mô VN", "vn_market_data_fetcher.py"),
    ("Bước 2: Mổ xẻ Chuyên sâu Báo cáo Tài chính & KQKD (VAS/TT200)", "vn_bctc_analyzer.py"),
    ("Bước 3: Kiểm toán & Đối soát Số liệu Minh bạch (Audited Briefing)", "vn_audit_and_verify.py"),
    ("Bước 4: Định lượng Rủi ro T+2.5 & Nghị quyết Hội đồng Đầu tư Ban 4", "vn_quant_portfolio.py"),
    ("Bước 5: Thẩm định Hiệu suất, Hồi tố Hit Rate % & Tự học Ban 5", "vn_performance_learning.py"),
    ("Bước 6: Biên soạn Bản tin Khai sáng 7h30 sáng Ban 6", "vn_mentor_engine.py"),
    ("Bước 7: Chuyên viên Minh Quân kích hoạt Giao ban 8h30 & Lập Sổ Lệnh ATO", "vn_daily_specialist.py"),
    ("Bước 8: Xuất bản Interactive HTML Dashboard TTCK Việt Nam", "generate_vn_dashboard.py")
]

def run_pipeline():
    print("=" * 70)
    print("  🚀 KHỞI ĐỘNG HỆ THỐNG AI MULTI-AGENT ĐẦU TƯ CHỨNG KHOÁN VIỆT NAM (VN-1.0)")
    print("=" * 70)
    start_time = time.time()

    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"

    # [BƯỚC 0 THỂ CHẾ] Đồng bộ Trí nhớ dài hạn Claude-Mem FTS5 & SQLite SSOT
    memory_bridge_path = os.path.join(os.path.dirname(os.path.dirname(SCRIPTS_DIR)), "scripts", "apex_institutional_memory_bridge.py")
    if os.path.exists(memory_bridge_path):
        print("\n[BƯỚC 0/8] >>> Đồng bộ Trí Nhớ Dài Hạn Claude-Mem (FTS5 Long-term Memory)...")
        subprocess.run([sys.executable, memory_bridge_path], env=sub_env, capture_output=False)

    for idx, (desc, script_name) in enumerate(PIPELINE_STEPS, 1):
        script_path = os.path.join(SCRIPTS_DIR, script_name)
        print(f"\n[{idx}/8] >>> {desc}...")
        res = subprocess.run([sys.executable, script_path], env=sub_env, capture_output=False)
        if res.returncode != 0:
            print(f"❌ CẢNH BÁO: Lỗi tại bước {script_name} (Exit code: {res.returncode})")
        else:
            print(f"✅ Hoàn thành: {script_name}")

    optimizer_path = os.path.join(os.path.dirname(os.path.dirname(SCRIPTS_DIR)), "scripts", "titan_token_optimizer.py")
    if os.path.exists(optimizer_path):
        subprocess.run([sys.executable, optimizer_path, "--quiet"], env=sub_env, capture_output=False)
    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 70)
    print(f"🎉 TOÀN BỘ CHU TRÌNH 7 PHÒNG BAN VIỆT NAM ĐÃ VẬN HÀNH THÀNH CÔNG! ({elapsed} giây)")
    print("  - Bản tin Khai sáng 7h30: VN_Market/06_Investor_Academy/daily_mentorship/")
    print("  - Sổ lệnh Chuyên viên Minh Quân 8h30: VN_Market/07_Daily_Specialist/")
    print("  - Dashboard tương tác: VN_Market/dashboard/index.html")
    print("=" * 70)

if __name__ == "__main__":
    run_pipeline()
