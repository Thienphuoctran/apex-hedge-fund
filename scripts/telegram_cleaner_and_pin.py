#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TELEGRAM CLEANER & PIN MANAGEMENT ENGINE (V1.0)
File: scripts/telegram_cleaner_and_pin.py
Cơ quan chủ quản: Palmer — Apex Central System Governance
Dành riêng cho: Chủ tịch Phước Trần (Tài khoản TCBS: 105C307855)

Nhiệm vụ:
1. Tự động theo dõi ID mọi tin nhắn do Bot gửi vào Supergroup.
2. Thực thi Đề xuất 3: Tự động xóa dọn sạch sẽ tin nhắn cũ của phiên trước trong các Topic tác chiến (Topic 3 Alerts & Topic 4 Sổ Lệnh).
3. Hỗ trợ Ghim (Pin) tin nhắn Bản Tin Tạp Chí Buổi Sáng lên đầu Topic để dễ đọc trên điện thoại.
"""

import os
import sys
import json
import time
import datetime
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

TRACKER_FILE = BASE_DIR / "data" / "telegram_sent_messages_tracker.json"
CONFIG_FILE = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "telegram_topics_config.json"
TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "bot_token": "9113394586:AAEV3JfSShG3Sl6YEIeqwIky7cTT0XYYccw",
        "group_chat_id": "-1004465270817"
    }


def load_tracker() -> List[Dict[str, Any]]:
    if TRACKER_FILE.exists():
        try:
            with open(TRACKER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_tracker(records: List[Dict[str, Any]]) -> None:
    try:
        with open(TRACKER_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Lỗi ghi tracker tin nhắn: {e}")


def record_message(message_id: int, chat_id: str, thread_id: Optional[int], topic_key: str) -> None:
    """Ghi nhận tin nhắn mới gửi để phục vụ dọn dẹp sau này"""
    records = load_tracker()
    records.append({
        "message_id": message_id,
        "chat_id": str(chat_id),
        "thread_id": thread_id,
        "topic_key": topic_key,
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_tracker(records)


def delete_telegram_message(bot_token: str, chat_id: str, message_id: int) -> bool:
    """Xóa một tin nhắn cụ thể qua API deleteMessage"""
    url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
    payload = json.dumps({"chat_id": str(chat_id), "message_id": message_id}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("ok", False)
    except Exception as e:
        # Có thể tin nhắn đã bị xóa trước đó
        return False


def pin_telegram_message(bot_token: str, chat_id: str, message_id: int, disable_notification: bool = True) -> bool:
    """Ghim tin nhắn lên thanh điều hướng của Supergroup/Topic"""
    url = f"https://api.telegram.org/bot{bot_token}/pinChatMessage"
    payload = json.dumps({
        "chat_id": str(chat_id),
        "message_id": message_id,
        "disable_notification": disable_notification
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("ok", False)
    except Exception as e:
        print(f"[!] Lỗi ghim tin nhắn {message_id}: {e}")
        return False


def auto_clean_old_operational_messages(
    topic_keys: Optional[List[str]] = None,
    keep_today_only: bool = True
) -> int:
    """
    TỰ ĐỘNG THU GỌN / XÓA TIN NHẮN CŨ CỦA PHIÊN HÔM TRƯỚC (ĐỀ XUẤT 3)
    Mặc định: Dọn dẹp sạch sẽ Topic 3 (Alerts) và Topic 4 (Sổ lệnh) để bàn làm việc luôn tinh tươm.
    """
    if topic_keys is None:
        topic_keys = ["alerts", "morning_blotter"]

    cfg = load_config()
    bot_token = cfg.get("bot_token")
    if not bot_token:
        return 0

    records = load_tracker()
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    deleted_count = 0
    remaining_records = []

    print(f"[*] BẮT ĐẦU CHẾ ĐỘ AUTO-CLEAN TIN NHẮN CŨ (Ngày hiện tại: {today_str})...")

    for r in records:
        msg_date = r.get("date")
        t_key = r.get("topic_key")
        msg_id = r.get("message_id")
        c_id = r.get("chat_id")

        # Nếu tin nhắn thuộc topic tác chiến và là của ngày cũ
        if t_key in topic_keys and msg_date < today_str:
            ok = delete_telegram_message(bot_token, c_id, msg_id)
            if ok:
                deleted_count += 1
                print(f"[+] Đã xóa tin nhắn cũ ID {msg_id} (Topic: {t_key}, Ngày: {msg_date})")
            time.sleep(0.05)  # Tránh spam rate limit
        else:
            remaining_records.append(r)

    save_tracker(remaining_records)
    print(f"🎉 [AUTO-CLEAN HOÀN TẤT] Đã xóa dọn dẹp thành công {deleted_count} tin nhắn cũ!")
    return deleted_count


if __name__ == "__main__":
    count = auto_clean_old_operational_messages()
    print(f"Cleaned {count} messages.")
