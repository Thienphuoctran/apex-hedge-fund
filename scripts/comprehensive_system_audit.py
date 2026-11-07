#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HỆ THỐNG TỔNG KIỂM TRA TOÀN VẸN THỂ CHẾ VÀ RÀ SOÁT CÁC NÂNG CẤP (APEX FULL AUDIT SUITE)
Chủ trì: Master CIO James (Ban 8) & Tổng Kiểm Sát Viên Trọng (Ban 12)
Phục vụ: Chủ tịch Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)
"""

import sys
import os

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
import time
import datetime
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

audit_results = {
    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "officers": ["Master CIO James (Ban 8)", "Tổng Kiểm Sát Viên Trọng (Ban 12)"],
    "account": "TCBS 105C307855 (Chủ tịch Trần Quốc Thiên Phước)",
    "modules_tested": [],
    "total_checks": 0,
    "passed_checks": 0,
    "warnings": [],
    "errors": []
}

def record_check(module_name, check_name, passed, details=""):
    audit_results["total_checks"] += 1
    if passed:
        audit_results["passed_checks"] += 1
    else:
        audit_results["errors"].append({
            "module": module_name,
            "check": check_name,
            "details": details
        })
    audit_results["modules_tested"].append({
        "module": module_name,
        "check": check_name,
        "status": "PASSED" if passed else "FAILED",
        "details": details
    })

print("=" * 70)
print("BẮT ĐẦU TỔNG RÀ SOÁT & KIỂM TRA THỰC TẾ HỆ THỐNG APEX")
print("=" * 70)

# 1. KIỂM TRA TÍNH TOÀN VẸN SSOT V2.0
try:
    from scripts.portfolio_state_manager import PortfolioStateManager
    st = PortfolioStateManager.load_state()
    cash = float(st.get("cash_balance_vnd", 0))
    acc_id = st.get("account_id")
    pos = st.get("active_positions", {})
    
    check_acc = (acc_id == "105C307855")
    record_check("SSOT_Integrity", "Mã tài khoản TCBS chính chủ", check_acc, f"Account: {acc_id}")
    
    check_cash = (abs(cash - 20167119.0) < 1.0)
    record_check("SSOT_Integrity", "Số dư tiền mặt chuẩn 20,167,119 ₫", check_cash, f"Cash: {cash:,.0f} ₫")
    
    check_pos = (len(pos) == 0)
    record_check("SSOT_Integrity", "Kho hàng 0 CP rủi ro (100% Cash)", check_pos, f"Holdings: {len(pos)} CP")
except Exception as e:
    record_check("SSOT_Integrity", "Nạp PortfolioStateManager", False, str(e))

# 2. KIỂM TRA LIVE ENDPOINTS TRÊN RENDER CLOUD
live_url = "https://apex-hedge-fund.onrender.com"

# Check 2.1: /api/health
try:
    req = urllib.request.Request(f"{live_url}/api/health", headers={"User-Agent": "ApexAudit/1.0"})
    res = urllib.request.urlopen(req, timeout=15)
    body = json.loads(res.read().decode("utf-8"))
    check_health = (res.status == 200 and body.get("status") == "ok" and body.get("cash_vnd") == 20167119.0)
    record_check("Cloud_Endpoint", "GET /api/health", check_health, f"Response: {body.get('status')}, Cash: {body.get('cash_vnd')}")
except Exception as e:
    record_check("Cloud_Endpoint", "GET /api/health", False, str(e))

# Check 2.2: /api/reports
try:
    req = urllib.request.Request(f"{live_url}/api/reports", headers={"User-Agent": "ApexAudit/1.0"})
    res = urllib.request.urlopen(req, timeout=15)
    data = json.loads(res.read().decode("utf-8"))
    reps = data.get("reports", []) if isinstance(data, dict) else data
    check_reps = (res.status == 200 and len(reps) > 0)
    record_check("Cloud_Endpoint", "GET /api/reports", check_reps, f"Tổng số báo cáo: {len(reps)}")
except Exception as e:
    record_check("Cloud_Endpoint", "GET /api/reports", False, str(e))

# Check 2.3: POST /api/command (/tcbs)
try:
    cmd_data = json.dumps({"command": "/tcbs"}).encode("utf-8")
    req = urllib.request.Request(f"{live_url}/api/command", data=cmd_data, headers={"Content-Type": "application/json", "User-Agent": "ApexAudit/1.0"})
    res = urllib.request.urlopen(req, timeout=20)
    cmd_res = json.loads(res.read().decode("utf-8"))
    check_cmd = (res.status == 200 and cmd_res.get("ok") is True and "105C307855" in cmd_res.get("response", ""))
    record_check("Cloud_Endpoint", "POST /api/command (/tcbs)", check_cmd, f"Officer: {cmd_res.get('officer')}, Ok: {cmd_res.get('ok')}")
except Exception as e:
    record_check("Cloud_Endpoint", "POST /api/command (/tcbs)", False, str(e))

# Check 2.4: POST /api/command (/solenh)
try:
    cmd_data = json.dumps({"command": "/solenh"}).encode("utf-8")
    req = urllib.request.Request(f"{live_url}/api/command", data=cmd_data, headers={"Content-Type": "application/json", "User-Agent": "ApexAudit/1.0"})
    res = urllib.request.urlopen(req, timeout=20)
    cmd_res = json.loads(res.read().decode("utf-8"))
    check_solenh = (res.status == 200 and cmd_res.get("ok") is True and ("HDB" in cmd_res.get("response", "") or "20,167,119" in cmd_res.get("response", "")))
    record_check("Cloud_Endpoint", "POST /api/command (/solenh)", check_solenh, f"Response length: {len(cmd_res.get('response', ''))}")
except Exception as e:
    record_check("Cloud_Endpoint", "POST /api/command (/solenh)", False, str(e))

# Check 2.5: POST /api/command (/hop FPT)
try:
    cmd_data = json.dumps({"command": "/hop FPT"}).encode("utf-8")
    req = urllib.request.Request(f"{live_url}/api/command", data=cmd_data, headers={"Content-Type": "application/json", "User-Agent": "ApexAudit/1.0"})
    res = urllib.request.urlopen(req, timeout=20)
    cmd_res = json.loads(res.read().decode("utf-8"))
    check_hop = (res.status == 200 and cmd_res.get("ok") is True and "FPT" in cmd_res.get("response", ""))
    record_check("Cloud_Endpoint", "POST /api/command (/hop FPT)", check_hop, f"Debate length: {len(cmd_res.get('response', ''))}")
except Exception as e:
    record_check("Cloud_Endpoint", "POST /api/command (/hop FPT)", False, str(e))

# 3. KIỂM TRA CẦU CHÌ KHÓA THỜI GIAN THỰC (TIME-GATING EMBARGO)
try:
    from scripts.apex_report_scanner import scan_all_institutional_reports
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time_str = datetime.datetime.now().strftime("%H:%M:%S")
    scanned = scan_all_institutional_reports(date_filter=today_str)
    
    future_leaks = [r for r in scanned if r["date"] == today_str and r["sort_time"] > current_time_str]
    check_embargo = (len(future_leaks) == 0)
    record_check("TimeGating_Embargo", "Cầu chì khóa thời gian thực (0 rò rỉ báo cáo tương lai)", check_embargo, f"Báo cáo tương lai rò rỉ: {len(future_leaks)}")
except Exception as e:
    record_check("TimeGating_Embargo", "Cầu chì khóa thời gian thực", False, str(e))

# 4. KIỂM TRA BỘ GIÁM SÁT NGƯỠNG NÂNG CẤP DATABASE (300 - 500 BÁO CÁO)
try:
    cfg_file = BASE_DIR / "config" / "database_scaling_sentinel.json"
    check_cfg_exists = cfg_file.exists()
    record_check("Database_Sentinel", "Tệp quy chuẩn database_scaling_sentinel.json", check_cfg_exists, str(cfg_file))
    
    if check_cfg_exists:
        with open(cfg_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        check_thresholds = (cfg.get("threshold_warning_min") == 300 and cfg.get("threshold_warning_max") == 500)
        record_check("Database_Sentinel", "Ngưỡng giám sát 300 - 500", check_thresholds, f"Min: {cfg.get('threshold_warning_min')}, Max: {cfg.get('threshold_warning_max')}")
        
    from scripts.apex_inspector_trong import ApexInspectorTrong
    audit_res = ApexInspectorTrong.audit_system_technical_integrity_247()
    check_trong_check6 = (audit_res.get("checks_performed", 0) >= 6)
    record_check("Database_Sentinel", "Check 6 trong Bộ Não Thanh Tra Của Trọng", check_trong_check6, f"Checks performed: {audit_res.get('checks_performed')}")
except Exception as e:
    record_check("Database_Sentinel", "Kiểm tra Sentinel Nâng Cấp DB", False, str(e))

# 5. KIỂM TRA MÃ NGUỒN PYTHON (SYNTAX COMPILATION TOÀN BỘ SCRIPTS)
py_files = list((BASE_DIR / "scripts").glob("*.py"))
syntax_errors = []
for pf in py_files:
    try:
        import py_compile
        py_compile.compile(str(pf), doraise=True)
    except Exception as e:
        syntax_errors.append(f"{pf.name}: {e}")

check_syntax = (len(syntax_errors) == 0)
record_check("Python_Code_Integrity", f"Biên dịch sạch {len(py_files)} scripts trong scripts/", check_syntax, f"Lỗi: {len(syntax_errors)}")

# 6. KIỂM TRA JAVASCRIPT FRONTEND TRÊN WEB PORTAL
try:
    req = urllib.request.Request(f"{live_url}/", headers={"User-Agent": "ApexAudit/1.0"})
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8")
    
    has_v4 = ("V4.0" in html)
    record_check("Web_Portal_UI", "Giao diện V4.0 Bloomberg-Grade đã kích hoạt", has_v4, "V4.0 badge on live HTML")
    
    has_tv = ("tv_chart_container" in html and "tradingview" in html.lower())
    record_check("Web_Portal_UI", "TradingView HOSE Live Widget tích hợp", has_tv, "Found tv_chart_container")
    
    has_split = ("james-split-container" in html and "james-sidebar-panel" in html)
    record_check("Web_Portal_UI", "Bàn Chỉ Huy James 2 Cột (Split-View)", has_split, "Found split layout classes")
    
    has_5cat = ("count-cat-macro" in html and "count-cat-equity" in html and "count-cat-cio" in html)
    record_check("Web_Portal_UI", "5 Khối phân loại báo cáo có badge đếm", has_5cat, "Found category count elements")
    
    has_view_mode = ("btn-view-grid" in html and "btn-view-table" in html)
    record_check("Web_Portal_UI", "Công tắc chuyển đổi Chế độ xem (Grid vs Table)", has_view_mode, "Found view mode buttons")
    
    has_smart_formatter = ("formatJamesResponseHtml" in html and "exec-kpi-banner" in html)
    record_check("Web_Portal_UI", "Smart Formatter bóc tách KPI & Stock Cards cho James", has_smart_formatter, "Found formatJamesResponseHtml")
except Exception as e:
    record_check("Web_Portal_UI", "Kiểm tra Web Portal Frontend", False, str(e))

print("=" * 70)
print(f"KẾT QUẢ TỔNG KIỂM TOÁN: {audit_results['passed_checks']}/{audit_results['total_checks']} HẠNG MỤC ĐẠT CHUẨN!")
if audit_results["errors"]:
    print(f"CÁC LỖI PHÁT HIỆN: {len(audit_results['errors'])}")
    for err in audit_results["errors"]:
        print(f"  - [{err['module']}] {err['check']}: {err['details']}")
else:
    print("HOÀN TOÀN KHÔNG CÓ LỖI! 100% CÁC NÂNG CẤP HOẠT ĐỘNG TRƠN TRU & HOÀN THIỆN!")
print("=" * 70)

# Lưu kết quả kiểm toán vào ledger
audit_log_path = BASE_DIR / "12_Institutional_Ombudsman_And_Inspectorate" / "daily_audits" / f"{datetime.datetime.now().strftime('%Y-%m-%d')}_Comprehensive_Audit_Report.json"
with open(audit_log_path, "w", encoding="utf-8") as f:
    json.dump(audit_results, f, ensure_ascii=False, indent=2)
print(f"Đã lưu hồ sơ kiểm toán: {audit_log_path}")
