#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX AUTONOMOUS KANBAN BOARD & JIRA-LIKE AGENT DISPATCHER (Inspired by Mesa #05 & Paperclip #01)
File: scripts/apex_kanban_manager.py
Cơ quan chủ quản: Phòng Quản Trị Hệ Thống (Palmer) & Master CIO James

Chức năng:
1. Quản lý trạng thái công việc của 11 phòng ban theo mô hình Kanban 4 cột:
   - BACKLOG (Nhiệm vụ chờ đến giờ G)
   - IN_PROGRESS (Phòng ban đang thực thi)
   - AUDIT_REVIEW (Ban 4 / Ban 5 / Master CIO kiểm định)
   - DONE (Đã hoàn thành và nộp lên Telegram + Ổ đĩa)
2. Cung cấp API trực quan cho Apex FounderOS Dashboard.
3. Cho phép AI tự nhận việc, tự chuyển trạng thái và tự báo cáo kết quả.
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
DATA_DIR = BASE_DIR / "data"
KANBAN_FILE = DATA_DIR / "apex_kanban_board.json"

DEFAULT_DAILY_TASKS = [
    {
        "id": "TASK-0600-AUTOCLEAN",
        "title": "Auto-Clean Telegram (Xóa tin rác hôm trước ở Topic 3 & 4)",
        "dept": "Ban 9 & System",
        "assignee": "Palmer & Cleaner",
        "scheduled_time": "06:00",
        "status": "BACKLOG",
        "priority": "HIGH",
        "output": "data/telegram_sent_messages_tracker.json"
    },
    {
        "id": "TASK-0700-MACRO",
        "title": "Báo cáo Vĩ mô SBV, Tỷ giá USD/VND & Phố Wall đêm qua",
        "dept": "Ban 1",
        "assignee": "Macro Lead",
        "scheduled_time": "07:00",
        "status": "BACKLOG",
        "priority": "HIGH",
        "output": "VN_Market/01_Macro_Monetary_Vietnam/{date}_VN_Macro_Report.md"
    },
    {
        "id": "TASK-0730-COACH",
        "title": "Bản Tin Khai Sáng Buổi Sáng gửi Chủ tịch Phước Trần",
        "dept": "Ban 6",
        "assignee": "Coach Huấn Luyện",
        "scheduled_time": "07:30",
        "status": "BACKLOG",
        "priority": "HIGH",
        "output": "VN_Market/06_Investor_Academy/daily_mentorship/{date}_VN_Mentor_Briefing.md"
    },
    {
        "id": "TASK-0800-ALPHA",
        "title": "Rà soát BCTC Forensic & Bảng Alpha Ranking (Top Leader vs Traps)",
        "dept": "Ban 2 & 3",
        "assignee": "Forensic & Screener Lead",
        "scheduled_time": "08:00",
        "status": "BACKLOG",
        "priority": "CRITICAL",
        "output": "VN_Market/03_Synthesis_Memos/{date}_VN_Investment_Memo.md"
    },
    {
        "id": "TASK-0830-MAGAZINE",
        "title": "Xuất bản BẢN TIN TẠP CHÍ BUỔI SÁNG (Ghim Topic 4 kèm 6 nút)",
        "dept": "Ban 7 & 8",
        "assignee": "Minh Quân & James",
        "scheduled_time": "08:30",
        "status": "BACKLOG",
        "priority": "CRITICAL",
        "output": "08_Master_Investment_CIO/master_execution_blotter.json"
    },
    {
        "id": "TASK-0900-OPENING",
        "title": "Khai hỏa phiên ATO sàn HOSE & Cảnh báo bẫy giá giả",
        "dept": "Ban 3 & Victor",
        "assignee": "Victor Sentinel",
        "scheduled_time": "09:00",
        "status": "BACKLOG",
        "priority": "HIGH",
        "output": "Telegram Topic 3 (alerts)"
    },
    {
        "id": "TASK-0900-STREAMING",
        "title": "Trực chiến Sentinel quét giá streaming 60s bảo vệ 900 CP",
        "dept": "Ban 9",
        "assignee": "Victor Sentinel",
        "scheduled_time": "09:00-15:00",
        "status": "BACKLOG",
        "priority": "CRITICAL",
        "output": "09_Realtime_Portfolio_Sentinel/portfolio_tracker.md"
    },
    {
        "id": "TASK-1145-FLASH",
        "title": "Báo cáo Flash khớp lệnh tạm đóng phiên sáng HOSE",
        "dept": "Ban 1 & 3",
        "assignee": "Synthesis Hub",
        "scheduled_time": "11:45",
        "status": "BACKLOG",
        "priority": "MEDIUM",
        "output": "VN_Market/03_Synthesis_Memos/{date}_Morning_Flash_Report.md"
    },
    {
        "id": "TASK-1300-T2RADAR",
        "title": "Radar đo lực xả hàng T+2 về tài khoản phiên chiều",
        "dept": "Ban 4 & Victor",
        "assignee": "Victor & Quant Risk",
        "scheduled_time": "13:00",
        "status": "BACKLOG",
        "priority": "HIGH",
        "output": "09_Realtime_Portfolio_Sentinel/{date}_T2_Pressure_Radar.md"
    },
    {
        "id": "TASK-1400-GOLDENHOUR",
        "title": "KHUNG GIỜ VÀNG TÁC CHIẾN (14h00 - 14h25): Soi nến & Lướt T+0",
        "dept": "Ban 7 VN",
        "assignee": "Minh Quân",
        "scheduled_time": "14:00",
        "status": "BACKLOG",
        "priority": "CRITICAL",
        "output": "08_Master_Investment_CIO/{date}_Golden_Hour_Tactical_Memo.md"
    },
    {
        "id": "TASK-1425-GUARD03",
        "title": "Kích hoạt chốt chặn GUARD-03 đóng vị thế T+0 trước ATC",
        "dept": "Ban 4 & 9",
        "assignee": "Victor Sentinel",
        "scheduled_time": "14:25",
        "status": "BACKLOG",
        "priority": "CRITICAL",
        "output": "Telegram Topic 3 (alerts)"
    },
    {
        "id": "TASK-1515-WALKFORWARD",
        "title": "Hồi tố Walk-Forward Hit Rate % & Kiểm toán tài khoản TCBS",
        "dept": "Ban 5 VN",
        "assignee": "Learning Lead",
        "scheduled_time": "15:15",
        "status": "BACKLOG",
        "priority": "HIGH",
        "output": "VN_Market/05_Learning_And_Evolution/{date}_VN_Learning_Report.md"
    },
    {
        "id": "TASK-1800-BCTCLIBRARY",
        "title": "Đồng bộ giá đóng cửa & Cập nhật Thư viện BCTC Master",
        "dept": "Ban 10",
        "assignee": "Hiền BCTC & IR",
        "scheduled_time": "18:00",
        "status": "BACKLOG",
        "priority": "MEDIUM",
        "output": "VN_Market/02_BCTC_Equity_Research/{date}_BCTC_Master_Library.md"
    },
    {
        "id": "TASK-2100-HIENBCTC",
        "title": "Báo cáo Độc quyền 2-3 BCTC chọn lọc (OCF/LNST ≥ 1.0x) Topic 189",
        "dept": "Ban 10",
        "assignee": "Hiền (Trưởng Ban 10)",
        "scheduled_time": "21:00",
        "status": "BACKLOG",
        "priority": "CRITICAL",
        "output": "VN_Market/02_BCTC_Equity_Research/{date}_Hien_Daily_Review.md"
    },
    {
        "id": "TASK-2115-KHANHVIDEO",
        "title": "Xuất bản kịch bản Video Viral 60s BCTC Hòa Phát vào Topic 190",
        "dept": "Ban 11",
        "assignee": "Khánh & Bảo",
        "scheduled_time": "21:15",
        "status": "BACKLOG",
        "priority": "HIGH",
        "output": "11_Viral_Content_Creation/{date}_Viral_Script_Khanh_HPG.md"
    },
    {
        "id": "TASK-2200-EVOLUTION",
        "title": "Giờ Tự Học Thích Nghi Quỹ Apex & Tinh chỉnh trọng số AI",
        "dept": "Ban 5",
        "assignee": "Performance Agent",
        "scheduled_time": "22:00",
        "status": "BACKLOG",
        "priority": "HIGH",
        "output": "05_Learning_And_Evolution/system_evolution_journal.md"
    },
    {
        "id": "TASK-2300-COUNCIL",
        "title": "Triệu tập Hội Đồng Điều Hành 23h00 & Đóng dấu biên bản EOD",
        "dept": "Ban 8",
        "assignee": "Master CIO James",
        "scheduled_time": "23:00",
        "status": "BACKLOG",
        "priority": "SUPREME",
        "output": "08_Master_Investment_CIO/{date}_23h00_EOD_Executive_Council_Meeting.md"
    }
]


def load_kanban() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today_str = datetime.date.today().isoformat()

    if not KANBAN_FILE.exists():
        data = init_daily_board(today_str)
        return data

    try:
        with open(KANBAN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = init_daily_board(today_str)

    if data.get("date") != today_str:
        data = init_daily_board(today_str)
    return data


def save_kanban(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(KANBAN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def init_daily_board(date_str: str) -> dict:
    tasks = []
    now_time = datetime.datetime.now().strftime("%H:%M")

    for t in DEFAULT_DAILY_TASKS:
        item = dict(t)
        item["output"] = item["output"].replace("{date}", date_str)
        item["created_at"] = f"{date_str} {t['scheduled_time']}"
        # Đánh dấu sơ bộ nếu qua giờ
        sched = t["scheduled_time"].split("-")[0]
        if sched <= now_time and sched not in ["09:00", "09:00-15:00"]:
            item["status"] = "DONE"
            item["completed_at"] = f"{date_str} {sched}"
        elif sched in ["09:00", "09:00-15:00"] and "09:00" <= now_time <= "15:00":
            item["status"] = "IN_PROGRESS"
        else:
            item["status"] = "BACKLOG"
        tasks.append(item)

    board = {
        "date": date_str,
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_tasks": len(tasks),
        "columns": {
            "BACKLOG": [t["id"] for t in tasks if t["status"] == "BACKLOG"],
            "IN_PROGRESS": [t["id"] for t in tasks if t["status"] == "IN_PROGRESS"],
            "AUDIT_REVIEW": [t["id"] for t in tasks if t["status"] == "AUDIT_REVIEW"],
            "DONE": [t["id"] for t in tasks if t["status"] == "DONE"]
        },
        "tasks": {t["id"]: t for t in tasks}
    }
    save_kanban(board)
    return board


def update_task_status(task_id: str, new_status: str, note: str = "") -> bool:
    board = load_kanban()
    tasks = board.get("tasks", {})
    if task_id not in tasks:
        return False

    old_status = tasks[task_id].get("status", "BACKLOG")
    tasks[task_id]["status"] = new_status
    tasks[task_id]["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if note:
        tasks[task_id]["note"] = note
    if new_status == "DONE":
        tasks[task_id]["completed_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Cập nhật columns
    for col in board.get("columns", {}):
        if task_id in board["columns"][col]:
            board["columns"][col].remove(task_id)

    board.setdefault("columns", {}).setdefault(new_status, []).append(task_id)
    board["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_kanban(board)
    return True


def print_ascii_board() -> None:
    board = load_kanban()
    tasks = board.get("tasks", {})
    cols = board.get("columns", {})

    print("=" * 95)
    print(f"📋 BẢNG GIAO VIỆC KANBAN TỰ ĐỘNG QUỸ APEX (MESA & PAPERCLIP HYBRID)")
    print(f"Ngày tác chiến: {board.get('date')} | Cập nhật lần cuối: {board.get('last_updated')}")
    print("-" * 95)
    print(f"{'Cột Trạng Thái':<16} | {'Số Việc':<8} | {'Danh Sách Mã Task & Người Phụ Trách'}")
    print("-" * 95)

    col_names = [
        ("BACKLOG", "⏳ Chờ Giờ G"),
        ("IN_PROGRESS", "⚡ Đang Chạy"),
        ("AUDIT_REVIEW", "🔍 Thẩm Định"),
        ("DONE", "✅ Hoàn Thành")
    ]

    for col_key, col_label in col_names:
        task_ids = cols.get(col_key, [])
        count_str = f"{len(task_ids)} việc"
        items_summary = []
        for tid in task_ids:
            t = tasks.get(tid, {})
            items_summary.append(f"[{t.get('scheduled_time')}] {t.get('assignee')}: {t.get('title')[:30]}")
        
        print(f"{col_label:<16} | {count_str:<8} |")
        for item in items_summary:
            print(f"{'':<16} | {'':<8} |   ↳ {item}")
        print("-" * 95)
    print("=" * 95)


def main():
    parser = argparse.ArgumentParser(description="Apex Kanban Manager")
    parser.add_argument("--board", action="store_true", help="Hiển thị bảng Kanban ASCII")
    parser.add_argument("--json", action="store_true", help="Xuất định dạng JSON cho Dashboard")
    parser.add_argument("--update", nargs=2, metavar=("TASK_ID", "STATUS"), help="Cập nhật trạng thái task")
    parser.add_argument("--init", action="store_true", help="Khởi tạo lại bảng Kanban ngày mới")
    args = parser.parse_args()

    if args.init:
        b = init_daily_board(datetime.date.today().isoformat())
        print(f"✅ Đã khởi tạo bảng Kanban với {b['total_tasks']} nhiệm vụ.")
        return

    if args.update:
        tid, st = args.update
        ok = update_task_status(tid, st)
        if ok:
            print(f"✅ Đã cập nhật {tid} -> {st}")
        else:
            print(f"❌ Không tìm thấy task {tid}")
        return

    if args.json:
        print(json.dumps(load_kanban(), indent=2, ensure_ascii=False))
        return

    print_ascii_board()


if __name__ == "__main__":
    main()
