#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TELEGRAM MULTI-TOPIC ROUTER & INSTITUTIONAL MESSAGE DISPATCHER
File: scripts/telegram_dispatcher.py
Cơ quan chủ quản: Palmer — Cố vấn Điều hành Tối cao & Trưởng Phòng Tổng Hệ Thống (Apex Central System Governance)
Dành cho: Chủ tịch Phước Trần (Tài khoản TCBS: 105C307855)

Chức năng:
1. Định tuyến thông minh tin nhắn vào 4 Phân Luồng Chủ Đề (Telegram Forum Topics):
   - 'alerts': 🚨 Báo Động Khẩn & Canh 2 Đầu (Victor Sentinel)
   - 'morning_blotter': ☀️ Bản Tin Sáng & Sổ Lệnh Master (Palmer & Minh Quân)
   - 'radar_filings': 📡 Radar Săn Sóng & Công Bố BCTC (Ban 2 & Ban 3)
   - 'copilot_chat': 💬 Phòng Điều Hành Chat Với Palmer (AI Co-Pilot 2 chiều)
2. Hỗ trợ tự động tạo Topics trên Telegram Supergroup qua API `createForumTopic`.
3. Cơ chế Fallback an toàn kép: Nếu Group chưa được thiết lập, tự động gửi sang Private Chat kèm Header chuẩn màu, đảm bảo 0% mất mát tin nhắn.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "telegram_topics_config.json"


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Warning reading telegram_topics_config.json: {e}")
    return {
        "bot_token": "9113394586:AAEV3JfSShG3Sl6YEIeqwIky7cTT0XYYccw",
        "chairman_user_id": "8332675283",
        "private_chat_id": "8332675283",
        "group_chat_id": None,
        "topics_enabled": True,
        "fallback_to_private_if_unconfigured": True,
        "topics": {}
    }


def save_config(cfg: Dict[str, Any]) -> None:
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Error saving telegram_topics_config.json: {e}")


def send_raw_telegram(
    bot_token: str,
    chat_id: str,
    text: str,
    message_thread_id: Optional[int] = None,
    reply_markup: Optional[Dict[str, Any]] = None,
    parse_mode: Optional[str] = "Markdown"
) -> bool:
    """Gửi tin nhắn Telegram thô, tự động xử lý chia nhỏ nếu > 4000 ký tự."""
    if not bot_token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Xử lý tin nhắn quá dài
    chunks = [text]
    if len(text) > 4000:
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]

    success = True
    for chunk in chunks:
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": True
        }
        if message_thread_id is not None:
            payload["message_thread_id"] = message_thread_id
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_markup:
            payload["reply_markup"] = reply_markup

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        sent = False
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                if res.get("ok"):
                    sent = True
        except Exception:
            # Fallback gửi không dùng parse_mode nếu có lỗi format markdown
            if parse_mode:
                try:
                    payload.pop("parse_mode", None)
                    data = json.dumps(payload).encode("utf-8")
                    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        res = json.loads(resp.read().decode("utf-8"))
                        if res.get("ok"):
                            sent = True
                except Exception as e2:
                    print(f"[!] Lỗi kết nối Telegram (plain text fallback): {e2}")
            
        if not sent:
            success = False
            
    return success


def dispatch_message(
    topic_key: str,
    text: str,
    header_badge: Optional[str] = None,
    reply_markup: Optional[Dict[str, Any]] = None,
    force_private: bool = False,
    parse_mode: Optional[str] = "Markdown"
) -> bool:
    """
    Định tuyến tin nhắn vào đúng Forum Topic trên Supergroup.
    Nếu Supergroup chưa được cấu hình, tự động fallback gửi vào Private Chat của Chủ tịch kèm thẻ màu sắc nét.
    """
    cfg = load_config()
    bot_token = cfg.get("bot_token", "")
    group_chat_id = cfg.get("group_chat_id")
    private_chat_id = cfg.get("private_chat_id", "")
    topics = cfg.get("topics", {})

    target_topic = topics.get(topic_key, {})
    thread_id = target_topic.get("thread_id")
    topic_name = target_topic.get("name", topic_key.upper())

    # Thêm Header Badge nếu có
    formatted_text = text
    if header_badge:
        formatted_text = f"{header_badge}\n{text}"

    # Nếu có Group và có thread_id và không ép gửi private
    if group_chat_id and thread_id and not force_private:
        ok = send_raw_telegram(
            bot_token=bot_token,
            chat_id=str(group_chat_id),
            text=formatted_text,
            message_thread_id=int(thread_id),
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        if ok:
            return True
        print(f"[!] Không thể gửi vào Group Topic {topic_key} (thread {thread_id}), chuyển hướng sang Private Chat...")

    # Fallback sang Private Chat của Chủ tịch
    fallback_badge = f"🔖 *[{topic_name}]*\n"
    if fallback_badge not in formatted_text:
        formatted_text = f"{fallback_badge}{formatted_text}"
        
    return send_raw_telegram(
        bot_token=bot_token,
        chat_id=str(private_chat_id),
        text=formatted_text,
        reply_markup=reply_markup,
        parse_mode=parse_mode
    )


def create_forum_topic(bot_token: str, chat_id: str, name: str, icon_color: int = 16478046) -> Optional[int]:
    """Tạo 1 Forum Topic mới trong Telegram Supergroup."""
    url = f"https://api.telegram.org/bot{bot_token}/createForumTopic"
    payload = {
        "chat_id": chat_id,
        "name": name,
        "icon_color": icon_color
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if res.get("ok"):
                thread_id = res.get("result", {}).get("message_thread_id")
                return thread_id
            else:
                print(f"[!] createForumTopic error: {res}")
    except Exception as e:
        print(f"[!] Lỗi khi gọi createForumTopic: {e}")
    return None


def provision_all_topics_for_group(group_chat_id: str) -> Dict[str, Any]:
    """Tự động khởi tạo đầy đủ 4 Forum Topics cho Group của Apex Fund."""
    cfg = load_config()
    bot_token = cfg.get("bot_token", "")
    cfg["group_chat_id"] = str(group_chat_id)
    
    results = {}
    for key, topic_info in cfg.get("topics", {}).items():
        name = topic_info.get("name", key)
        color = topic_info.get("icon_color", 16478046)
        
        print(f"[*] Đang tạo Topic: {name} (color={color})...")
        th_id = create_forum_topic(bot_token, str(group_chat_id), name, color)
        if th_id:
            cfg["topics"][key]["thread_id"] = th_id
            results[key] = th_id
            print(f"  [+] Thành công! Thread ID: {th_id}")
        else:
            print(f"  [!] Thất bại khi tạo topic {name}")
            
    save_config(cfg)
    return results


def check_recent_group_id() -> Optional[str]:
    """Quét getUpdates để tự động tìm group_chat_id nếu Chủ tịch vừa thêm bot vào Group."""
    cfg = load_config()
    bot_token = cfg.get("bot_token", "")
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates?limit=20"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            for item in reversed(res.get("result", [])):
                msg = item.get("message", {}) or item.get("my_chat_member", {})
                chat = msg.get("chat", {})
                chat_type = chat.get("type", "")
                if chat_type in ["group", "supergroup"]:
                    return str(chat.get("id"))
    except Exception as e:
        print(f"[!] Lỗi quét group id: {e}")
    return None


if __name__ == "__main__":
    print("[*] Kiểm thử module Telegram Dispatcher...")
    cfg = load_config()
    print(f"  - Bot Token: {cfg['bot_token'][:10]}... (Ẩn)")
    print(f"  - Private Chat ID: {cfg['private_chat_id']}")
    print(f"  - Group Chat ID: {cfg.get('group_chat_id') or 'Chưa cấu hình (Đang dùng Fallback)'}")
    print(f"  - Số topics đã quy hoạch: {len(cfg.get('topics', {}))}")
