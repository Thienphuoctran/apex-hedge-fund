#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INSTITUTIONAL HARD BUDGET CAPS & TOKEN GOVERNANCE (Inspired by Paperclip #01)
File: scripts/paperclip_token_governor.py
Cơ quan chủ trì: Phòng Quản Trị Hệ Thống (Palmer) & Master CIO James

Mục tiêu cốt lõi:
1. Kiểm soát 100% chi phí token của 11 phòng ban, ngăn chặn triệt để tình trạng tiêu thụ quá đà.
2. Thiết lập Mạch Ngắt Cứng (Hard Circuit Breaker) khi một phòng ban chạm 100% trần ngân sách ngày.
3. Kích hoạt Chế độ Sinh thái (Eco-Mode Fallback) sử dụng cache/digest sẵn có thay vì gọi API mới.
4. Cung cấp dữ liệu trực quan cho Apex FounderOS Dashboard.
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "department_token_budgets.json"
DATA_DIR = BASE_DIR / "data"
LEDGER_FILE = DATA_DIR / "token_usage_ledger.json"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_ledger() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not LEDGER_FILE.exists():
        initial = {
            "date": datetime.date.today().isoformat(),
            "last_reset": datetime.datetime.now().isoformat(),
            "total_tokens": 0,
            "total_usd": 0.0,
            "departments": {}
        }
        save_ledger(initial)
        return initial

    try:
        with open(LEDGER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}

    today_str = datetime.date.today().isoformat()
    if data.get("date") != today_str:
        # Tự động reset sang ngày mới lúc 00:00 VN
        data = {
            "date": today_str,
            "last_reset": datetime.datetime.now().isoformat(),
            "total_tokens": 0,
            "total_usd": 0.0,
            "departments": {}
        }
        save_ledger(data)
    return data


def save_ledger(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calculate_cost(input_tokens: int, output_tokens: int, model: str = "gemini_flash_argon", config: dict = None) -> float:
    if config is None:
        config = load_config()
    pricing = config.get("pricing_per_1m_tokens", {}).get(model, {
        "input": 0.075,
        "output": 0.30
    })
    cost_in = (input_tokens / 1_000_000.0) * pricing["input"]
    cost_out = (output_tokens / 1_000_000.0) * pricing["output"]
    return round(cost_in + cost_out, 6)


def check_budget_allowance(dept_key: str) -> dict:
    """
    Kiểm tra xem phòng ban có được phép gọi API mô hình tiếp hay không.
    Trả về dict: {
        "allowed": bool,
        "status": "NORMAL" | "WARNING" | "HARD_CUTOFF",
        "used_tokens": int,
        "cap_tokens": int,
        "used_usd": float,
        "cap_usd": float,
        "usage_pct": float,
        "eco_mode": bool
    }
    """
    config = load_config()
    ledger = load_ledger()
    dept_cfg = config.get("departments", {}).get(dept_key)

    if not dept_cfg:
        # Nếu phòng ban chưa đăng ký trần, cho phép chạy với cảnh báo
        return {
            "allowed": True,
            "status": "NORMAL",
            "used_tokens": 0,
            "cap_tokens": 50000,
            "used_usd": 0.0,
            "cap_usd": 0.10,
            "usage_pct": 0.0,
            "eco_mode": False
        }

    dept_usage = ledger.get("departments", {}).get(dept_key, {
        "tokens": 0,
        "usd": 0.0,
        "call_count": 0
    })

    cap_usd = dept_cfg.get("daily_usd_cap", 0.10)
    cap_tokens = dept_cfg.get("daily_token_cap", 50000)
    used_usd = dept_usage.get("usd", 0.0)
    used_tokens = dept_usage.get("tokens", 0)

    pct_by_usd = (used_usd / cap_usd * 100) if cap_usd > 0 else 0
    pct_by_token = (used_tokens / cap_tokens * 100) if cap_tokens > 0 else 0
    usage_pct = max(pct_by_usd, pct_by_token)

    warn_threshold = config.get("global_settings", {}).get("warning_threshold_pct", 80)
    hard_cutoff = config.get("global_settings", {}).get("hard_cutoff_threshold_pct", 100)

    if usage_pct >= hard_cutoff:
        return {
            "allowed": False,
            "status": "HARD_CUTOFF",
            "reason": f"Phòng ban '{dept_cfg.get('name')}' đã đạt {usage_pct:.1f}% trần ngân sách ngày (${used_usd:.4f}/${cap_usd:.2f} USD). Mạch ngắt cứng kích hoạt!",
            "used_tokens": used_tokens,
            "cap_tokens": cap_tokens,
            "used_usd": used_usd,
            "cap_usd": cap_usd,
            "usage_pct": round(usage_pct, 1),
            "eco_mode": True
        }
    elif usage_pct >= warn_threshold:
        return {
            "allowed": True,
            "status": "WARNING",
            "reason": f"Cảnh báo vàng: Phòng ban '{dept_cfg.get('name')}' đã dùng {usage_pct:.1f}% ngân sách.",
            "used_tokens": used_tokens,
            "cap_tokens": cap_tokens,
            "used_usd": used_usd,
            "cap_usd": cap_usd,
            "usage_pct": round(usage_pct, 1),
            "eco_mode": False
        }
    else:
        return {
            "allowed": True,
            "status": "NORMAL",
            "reason": "Ngân sách an toàn trong định mức.",
            "used_tokens": used_tokens,
            "cap_tokens": cap_tokens,
            "used_usd": used_usd,
            "cap_usd": cap_usd,
            "usage_pct": round(usage_pct, 1),
            "eco_mode": False
        }


def record_usage(dept_key: str, input_tokens: int, output_tokens: int, model: str = "gemini_flash_argon", task_name: str = "routine_task") -> dict:
    """
    Ghi nhận chi phí token thực tế sau mỗi cuộc gọi API của phòng ban.
    """
    config = load_config()
    ledger = load_ledger()

    cost = calculate_cost(input_tokens, output_tokens, model, config)
    total_new_tokens = input_tokens + output_tokens

    dept_entry = ledger.setdefault("departments", {}).setdefault(dept_key, {
        "name": config.get("departments", {}).get(dept_key, {}).get("name", dept_key),
        "tokens": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "usd": 0.0,
        "call_count": 0,
        "history": []
    })

    dept_entry["tokens"] += total_new_tokens
    dept_entry["input_tokens"] += input_tokens
    dept_entry["output_tokens"] += output_tokens
    dept_entry["usd"] = round(dept_entry["usd"] + cost, 6)
    dept_entry["call_count"] += 1

    # Lưu 15 sự kiện gần nhất
    event = {
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "task": task_name,
        "tokens": total_new_tokens,
        "usd": cost,
        "model": model
    }
    dept_entry.setdefault("history", []).append(event)
    if len(dept_entry["history"]) > 15:
        dept_entry["history"] = dept_entry["history"][-15:]

    ledger["total_tokens"] += total_new_tokens
    ledger["total_usd"] = round(ledger["total_usd"] + cost, 6)

    save_ledger(ledger)
    return {
        "dept_key": dept_key,
        "task_cost_usd": cost,
        "dept_total_usd": dept_entry["usd"],
        "dept_total_tokens": dept_entry["tokens"]
    }


def generate_governance_report() -> str:
    config = load_config()
    ledger = load_ledger()

    lines = []
    lines.append("=" * 80)
    lines.append(f"🛡️ BÁO CÁO QUẢN TRỊ NGÂN SÁCH TOKEN QUỸ APEX (PAPERCLIP PROTOCOL)")
    lines.append(f"Ngày kiểm toán: {ledger.get('date')} | Cập nhật: {datetime.datetime.now().strftime('%H:%M:%S')}")
    lines.append(f"Tổng chi phí toàn quỹ hôm nay: ${ledger.get('total_usd', 0.0):.4f} USD / Trần: ${config.get('global_settings', {}).get('daily_total_cap_usd', 1.20):.2f} USD")
    lines.append(f"Tổng Tokens tiêu thụ: {ledger.get('total_tokens', 0):,} tokens")
    lines.append("-" * 80)
    lines.append(f"{'Phòng Ban':<36} | {'Đã Dùng':<10} | {'Định Mức':<10} | {'Tỷ Lệ %':<8} | {'Trạng Thái':<12}")
    lines.append("-" * 80)

    for dept_key, dept_cfg in config.get("departments", {}).items():
        st = check_budget_allowance(dept_key)
        name = dept_cfg.get("name", dept_key)[:34]
        used_usd_str = f"${st['used_usd']:.4f}"
        cap_usd_str = f"${st['cap_usd']:.2f}"
        pct_str = f"{st['usage_pct']:.1f}%"

        status_icon = "🟢 AN TOÀN"
        if st["status"] == "WARNING":
            status_icon = "🟡 CẢNH BÁO"
        elif st["status"] == "HARD_CUTOFF":
            status_icon = "🔴 NGẮT CỨNG"

        lines.append(f"{name:<36} | {used_usd_str:<10} | {cap_usd_str:<10} | {pct_str:<8} | {status_icon:<12}")

    lines.append("=" * 80)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Apex Token Governor (Paperclip Mode)")
    parser.add_argument("--summary", action="store_true", help="Hiển thị bảng tổng hợp ngân sách token")
    parser.add_argument("--check", type=str, help="Kiểm tra ngân sách phòng ban cụ thể")
    parser.add_argument("--test-circuit-breaker", action="store_true", help="Kiểm thử giả lập kích hoạt ngắt cứng khi vượt trần")
    args = parser.parse_args()

    if args.summary:
        print(generate_governance_report())
        return

    if args.check:
        res = check_budget_allowance(args.check)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    if args.test_circuit_breaker:
        print("🧪 BẮT ĐẦU KIỂM THỬ MẠCH NGẮT CỨNG (HARD CIRCUIT BREAKER)...")
        test_dept = "ban_10_hien"
        initial_check = check_budget_allowance(test_dept)
        print(f"Trạng thái ban đầu ({test_dept}): {initial_check['status']} (Đã dùng {initial_check['usage_pct']}%)")

        print("Simulating 60,000 tokens consumption (vượt trần 50,000 tokens của Hiền)...")
        record_usage(test_dept, 50000, 15000, model="gemini_flash_argon", task_name="test_heavy_bctc_crawling")

        after_check = check_budget_allowance(test_dept)
        print(f"Trạng thái sau khi vượt trần: {after_check['status']}")
        print(f"Allowed to proceed: {after_check['allowed']}")
        print(f"Lý do phản hồi: {after_check.get('reason')}")
        assert after_check["allowed"] is False, "LỖI: Mạch ngắt cứng không kích hoạt đúng!"
        print("✅ KIỂM THỬ THÀNH CÔNG: Mạch ngắt cứng Paperclip hoạt động 100% chuẩn xác!")
        return

    # Mặc định in summary
    print(generate_governance_report())


if __name__ == "__main__":
    main()
