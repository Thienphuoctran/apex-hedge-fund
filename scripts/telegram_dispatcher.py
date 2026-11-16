#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TELEGRAM MULTI-TOPIC ROUTER & DEDICATED REPORT VAULT DISPATCHER (V2.0)
File: scripts/telegram_dispatcher.py
Cơ quan chủ quản: Palmer — Cố vấn Điều hành Tối cao & Trưởng Phòng Tổng Hệ Thống (Apex Central System Governance)
Dành cho: Chủ tịch Phước Trần (Tài khoản TCBS: 105C307855)

Chức năng V2.0 (Tối ưu Xem, Tìm kiếm & Chống loãng thông báo):
1. Phòng Báo Cáo Độc Quyền (`reports_vault`): Tách riêng 100% khỏi tin chat/rác, hỗ trợ Topic riêng hoặc Group/Channel độc lập (`dedicated_reports_chat_id`).
2. Chuẩn hóa Search-Optimized Card: Gắn #hashtag chuẩn (`#BC_YYYYMMDD`, mã CP, phòng ban) + Nút/Link mở thẳng Web Portal (`?open=<rel_path>`).
3. Tích hợp Phương án A ($0/tháng): Tóm tắt thông minh 3 ý chốt bằng `gemini-3.8-flash` (fallback rule-based tức thì).
4. Cơ chế Chống Loãng & Dedup Shield: Chặn gửi trùng 5 phút, chặn đổ rác vào Private Chat.
"""

import datetime
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "telegram_topics_config.json"
DEDUP_CACHE_FILE = BASE_DIR / "data" / "telegram_dedup_cache.json"
_ICT_TZ = datetime.timezone(datetime.timedelta(hours=7))


def _get_ict_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).astimezone(_ICT_TZ)


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
        "dedicated_reports_chat_id": None,
        "topics_enabled": True,
        "fallback_to_private_if_unconfigured": True,
        "anti_noise_routing": {
            "block_private_fallback_for_reports": True,
            "mirror_reports_to_vault_room": True,
            "auto_pin_daily_index": True,
            "portal_base_url": "https://apex-hedge-fund.onrender.com"
        },
        "topics": {}
    }


def save_config(cfg: Dict[str, Any]) -> None:
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Error saving telegram_topics_config.json: {e}")


def _extract_stock_hashtags(text: str) -> List[str]:
    known = [
        "HDB", "MSH", "BSR", "BAF", "HPG", "TCB", "MBB", "FPT", "DGC", "MWG",
        "PVT", "IDC", "DBC", "SSI", "VND", "HCM", "VCB", "BID", "CTG", "ACB",
        "STB", "VPB", "GAS", "MSN", "ACV", "BVH", "GMD", "HAH", "SZC", "KBC",
        "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "TSM", "SPY"
    ]
    found = []
    upper = text.upper()
    for tk in known:
        if re.search(rf"\b{tk}\b", upper):
            found.append(f"#{tk}")
        if len(found) >= 6:
            break
    return found


def summarize_with_gemini_38_flash(title: str, raw_text: str) -> Optional[str]:
    """[Phương Án A - $0/tháng] Tóm tắt nhanh 3 ý chốt bằng gemini-3.8-flash Free Tier nếu có API Key."""
    try:
        from scripts.assistant_nam_agent import get_gemini_api_key
        api_key = get_gemini_api_key()
        if not api_key:
            return None
        from google import genai
        from google.genai import types
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=6000,
                retry_options=types.HttpRetryOptions(attempts=1)
            )
        )
        prompt = (
            "Bạn là bộ lọc thông tin tinh gọn của Quỹ Apex (Chủ tịch Phước Trần, TCBS 105C307855).\n"
            "Hãy tóm tắt báo cáo/cảnh báo sau thành ĐÚNG 3 gạch đầu dòng ngắn gọn (tiếng Việt, mỗi dòng <= 18 từ), "
            "và 1 dòng cuối '👉 Hành động:' nêu rõ giữ nguyên hay cần mở Antigravity họp James ngay.\n\n"
            f"Tiêu đề: {title}\nNội dung:\n{raw_text[:2800]}"
        )
        for m in ("gemini-3.8-flash", "gemini-2.5-flash"):
            try:
                resp = client.models.generate_content(model=m, contents=prompt)
                if resp and resp.text:
                    return resp.text.strip()[:900]
            except Exception:
                continue
    except Exception:
        pass
    return None


def _rule_based_3_bullets(raw_text: str) -> str:
    """Trích xuất nhanh 3 dòng cốt lõi khi không gọi LLM (luôn hoạt động offline 0ms)."""
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    picked = []
    skip_tokens = ("━━━", "---", "🔖 *[")
    for ln in lines:
        if any(st in ln for st in skip_tokens) or len(ln) < 12:
            continue
        clean = re.sub(r"[*_`]", "", ln).strip()
        if clean.startswith("#"):
            clean = clean.lstrip("# ").strip()
        if clean and clean not in picked:
            picked.append(f"• {clean[:140]}")
        if len(picked) >= 3:
            break
    return "\n".join(picked) if picked else f"• {raw_text[:240].strip()}"


def build_search_optimized_card(
    topic_key: str,
    title: str,
    raw_text: str,
    report_rel_path: Optional[str] = None,
    use_ai_summary: bool = False
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Chuẩn hóa tin nhắn thành Thẻ Tìm Kiếm Telegram gọn nhẹ, có #hashtag & link mở thẳng Web Portal."""
    cfg = load_config()
    anti_noise = cfg.get("anti_noise_routing", {}) or {}
    portal_base = str(anti_noise.get("portal_base_url") or "https://apex-hedge-fund.onrender.com").rstrip("/")
    now_ict = _get_ict_now()
    date_tag = now_ict.strftime("%Y%m%d")
    time_str = now_ict.strftime("%H:%M")

    topic_map = {
        "alerts": ("🚨 BÁO ĐỘNG ĐỎ", "#KHAN_CAP #BAN_9_VICTOR"),
        "morning_blotter": ("☀️ SỔ LỆNH & TÁC CHIẾN", "#SOLENH #BAN_7_VN #TACTICAL"),
        "radar_filings": ("📡 RADAR VĨ MÔ & ALPHA", "#RADAR #BAN_1_2_3"),
        "hien_desk": ("🌸 BCTC & IR (HIỀN)", "#BCTC #IR #BAN_10"),
        "quant_risk": ("⚖️ QUẢN TRỊ RỦI RO", "#RISK #BAN_4"),
        "academy_learning": ("🏛️ HỌC VIỆN & TIẾN HÓA", "#DAOTAO #BAN_5_6"),
        "james_hq": ("🎖️ CHỈ HUY MASTER CIO", "#MASTER_CIO #BAN_8"),
        "reports_vault": ("📑 BÁO CÁO CHUẨN HÓA", "#BAOCAO_CHINH_THUC"),
    }
    badge, base_tags = topic_map.get(topic_key, ("📑 BÁO CÁO HỆ THỐNG", f"#{topic_key.upper()}"))
    summary = summarize_with_gemini_38_flash(title, raw_text) if use_ai_summary else None
    if not summary:
        summary = _rule_based_3_bullets(raw_text)

    tickers = _extract_stock_hashtags(f"{title}\n{raw_text}")
    all_tags = f"#BC_{date_tag} {base_tags} " + (" ".join(tickers) if tickers else "#VNINDEX")

    portal_url = f"{portal_base}/?open={urllib.parse.quote(report_rel_path)}" if report_rel_path else portal_base
    card_lines = [
        f"{badge} | `{time_str} ICT`",
        f"*{title[:120]}*",
        "━━━━━━━━━━━━━━━━━━━",
        summary,
        "━━━━━━━━━━━━━━━━━━━",
        f"🔗 *Mở Web Portal:* {portal_url}",
        f"🔍 *Tìm nhanh:* {all_tags.strip()}"
    ]
    markup = {
        "inline_keyboard": [[
            {"text": "📖 Đọc Đầy Đủ Trên Web Portal", "url": portal_url}
        ]]
    }
    return "\n".join(card_lines), markup


def search_vault_reports(query: str, limit: int = 5) -> str:
    """Tìm kiếm nhanh báo cáo từ SQLite FTS5 Vault trả về danh sách kèm link mở thẳng Portal."""
    cfg = load_config()
    portal_base = str((cfg.get("anti_noise_routing") or {}).get("portal_base_url") or "https://apex-hedge-fund.onrender.com").rstrip("/")
    db_path = BASE_DIR / "data" / "apex_institutional_vault.db"
    q_clean = re.sub(r"[^\w\sÀ-ỹ]", " ", (query or "").strip())
    if not db_path.exists() or not q_clean:
        return "⚠️ Vui lòng nhập từ khóa (VD: `/tim HDB`, `/tim BCTC`, `/tim chiến lược`)."

    rows = []
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT r.rel_path, r.title, r.dept_name, r.date "
                "FROM reports_fts f JOIN institutional_reports r ON f.rowid = r.id "
                "WHERE reports_fts MATCH ? ORDER BY r.date DESC, r.sort_time DESC LIMIT ?",
                (q_clean, limit)
            )
            rows = cur.fetchall()
        except Exception:
            like_q = f"%{q_clean}%"
            cur.execute(
                "SELECT rel_path, title, dept_name, date FROM institutional_reports "
                "WHERE title LIKE ? OR content LIKE ? OR tickers LIKE ? OR rel_path LIKE ? "
                "ORDER BY date DESC, sort_time DESC LIMIT ?",
                (like_q, like_q, like_q, like_q, limit)
            )
            rows = cur.fetchall()
        conn.close()
    except Exception as e:
        return f"⚠️ Lỗi truy vấn Vault: {e}"

    if not rows:
        return f"🔍 Không tìm thấy báo cáo nào khớp với `{query}` trong SQLite Vault."

    lines = [f"🔍 *KẾT QUẢ TÌM BÁO CÁO CHO `{query.upper()}` ({len(rows)} bản mới nhất):*", "━━━━━━━━━━━━━━━━━━━"]
    for idx, (rel_p, title, dept, r_date) in enumerate(rows, 1):
        url = f"{portal_base}/?open={urllib.parse.quote(str(rel_p))}"
        lines.append(f"*{idx}. [{r_date}]* {str(title)[:85]}\n   🏢 {dept}\n   🔗 {url}")
    return "\n".join(lines)


def build_daily_reports_index(date_str: Optional[str] = None) -> str:
    """Tổng hợp Mục lục Báo cáo trong ngày để gửi hoặc ghim trong Phòng Báo Cáo."""
    cfg = load_config()
    portal_base = str((cfg.get("anti_noise_routing") or {}).get("portal_base_url") or "https://apex-hedge-fund.onrender.com").rstrip("/")
    target_date = date_str or _get_ict_now().strftime("%Y-%m-%d")
    db_path = BASE_DIR / "data" / "apex_institutional_vault.db"
    rows = []
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute(
                "SELECT rel_path, title, dept_name, time FROM institutional_reports "
                "WHERE date = ? ORDER BY sort_time DESC, id DESC LIMIT 12",
                (target_date,)
            )
            rows = cur.fetchall()
            conn.close()
        except Exception:
            rows = []

    if not rows:
        return f"📑 *[MỤC LỤC BÁO CÁO NGÀY {target_date}]*\nChưa có báo cáo nào được lập mục lục hôm nay. Xem Portal: {portal_base}"

    lines = [
        f"📑 *[MỤC LỤC BÁO CÁO HỆ THỐNG — NGÀY {target_date}]*",
        f"🔍 _Tìm theo ngày:_ `#BC_{target_date.replace('-', '')}` | _Lệnh tra cứu:_ `/tim <mã/từ khóa>`",
        "━━━━━━━━━━━━━━━━━━━"
    ]
    for idx, (rel_p, title, dept, r_time) in enumerate(rows[:8], 1):
        url = f"{portal_base}/?open={urllib.parse.quote(str(rel_p))}"
        lines.append(f"*{idx}. `{r_time or '--:--'}`* {str(title)[:75]}\n   🔗 {url}")
    lines.append("━━━━━━━━━━━━━━━━━━━")
    lines.append(f"🌐 *Kho Báo Cáo Đầy Đủ:* {portal_base}")
    return "\n".join(lines)


def set_dedicated_reports_room(chat_id: str, title: Optional[str] = None) -> Dict[str, Any]:
    """Gán Group/Channel độc lập làm phòng riêng biệt CHỈ nhận báo cáo chuẩn hóa."""
    cfg = load_config()
    cfg["dedicated_reports_chat_id"] = str(chat_id)
    if title:
        cfg["dedicated_reports_chat_title"] = title
    save_config(cfg)
    return cfg


def is_duplicate_message(chat_id: str, thread_id: Optional[int], text: str, window_seconds: int = 300) -> bool:
    """[DEDUP SHIELD] Chặn đứng 100% tin nhắn gửi trùng lặp trong cùng topic trong 5 phút."""
    try:
        norm_text = "".join(text.split())
        key_raw = f"{chat_id}_{thread_id}_{norm_text}"
        msg_hash = hashlib.md5(key_raw.encode("utf-8")).hexdigest()
        now_ts = time.time()

        cache = {}
        if DEDUP_CACHE_FILE.exists():
            try:
                with open(DEDUP_CACHE_FILE, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except Exception:
                cache = {}

        cache = {k: v for k, v in cache.items() if now_ts - v.get("ts", 0) < 3600}

        if msg_hash in cache:
            elapsed = now_ts - cache[msg_hash].get("ts", 0)
            if elapsed < window_seconds:
                print(f"[!] [DEDUP SHIELD] Phát hiện tin nhắn trùng lặp (đã gửi cách đây {elapsed:.1f}s). Tự động chặn ngay!")
                return True

        cache[msg_hash] = {"ts": now_ts, "thread_id": thread_id, "preview": text[:60]}
        DEDUP_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DEDUP_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)

        return False
    except Exception:
        return False


def send_raw_telegram(
    bot_token: str,
    chat_id: str,
    text: str,
    message_thread_id: Optional[int] = None,
    reply_markup: Optional[Dict[str, Any]] = None,
    parse_mode: Optional[str] = "Markdown"
) -> bool:
    """Gửi tin nhắn Telegram thô, tự động chia nhỏ nếu > 4000 ký tự."""
    if not bot_token or not chat_id:
        return False

    if is_duplicate_message(chat_id, message_thread_id, text):
        return True

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    chunks = [text]
    if len(text) > 4000:
        chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]

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
                    msg_id = res.get("result", {}).get("message_id")
                    if msg_id:
                        try:
                            from scripts.telegram_cleaner_and_pin import record_message
                            record_message(msg_id, chat_id, message_thread_id, getattr(send_raw_telegram, "_current_topic_key", "general"))
                        except Exception:
                            pass
        except Exception:
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


def _extract_title_from_text(raw_text: str, fallback: str) -> str:
    for ln in raw_text.splitlines():
        s = re.sub(r"[*_`#\[\]]", "", ln).strip()
        if len(s) >= 8:
            return s[:110]
    return fallback


def dispatch_report_card(
    topic_key: str,
    title: str,
    raw_text: str,
    report_rel_path: Optional[str] = None,
    use_ai_summary: bool = False,
    pin_message: bool = False
) -> bool:
    """Gửi Thẻ Báo Cáo chuẩn hóa tìm kiếm (#hashtag + nút mở Web Portal) vào Phòng Báo Cáo riêng biệt."""
    card_text, card_markup = build_search_optimized_card(
        topic_key=topic_key,
        title=title,
        raw_text=raw_text,
        report_rel_path=report_rel_path,
        use_ai_summary=use_ai_summary
    )
    ok = dispatch_message(
        topic_key="reports_vault",
        text=card_text,
        reply_markup=card_markup,
        force_private=False,
        parse_mode="Markdown",
        mirror_to_reports_vault=False
    )
    if ok and pin_message:
        try:
            from scripts.telegram_cleaner_and_pin import load_tracker, pin_telegram_message
            cfg = load_config()
            recs = load_tracker()
            if recs:
                last = recs[-1]
                pin_telegram_message(cfg.get("bot_token", ""), str(last.get("chat_id")), int(last.get("message_id")))
        except Exception:
            pass
    return ok


def dispatch_message(
    topic_key: str,
    text: str,
    header_badge: Optional[str] = None,
    reply_markup: Optional[Dict[str, Any]] = None,
    force_private: bool = False,
    parse_mode: Optional[str] = "Markdown",
    report_rel_path: Optional[str] = None,
    mirror_to_reports_vault: bool = True,
    use_ai_summary: bool = False
) -> bool:
    """
    Định tuyến tin nhắn chống loãng thông báo:
    1. Nếu gửi vào 'reports_vault': ưu tiên Group/Channel độc lập (dedicated_reports_chat_id) nếu đã liên kết,
       nếu chưa thì gửi vào Topic riêng biệt 'PHÒNG BÁO CÁO & TÌM KIẾM ĐỘC QUYỀN'.
    2. Chặn rơi rác về Private Chat nếu các script cũ dùng topic_key không hợp lệ ('copilot_chat', 'general'...).
    3. Tự động nhân bản 1 Thẻ Báo Cáo tinh gọn có #hashtag + Link mở Web Portal vào Phòng Báo Cáo riêng biệt.
    """
    cfg = load_config()
    bot_token = cfg.get("bot_token", "")
    group_chat_id = cfg.get("group_chat_id")
    dedicated_reports_chat_id = cfg.get("dedicated_reports_chat_id")
    private_chat_id = cfg.get("private_chat_id", "")
    topics = cfg.get("topics", {})
    anti_noise = cfg.get("anti_noise_routing", {}) or {}

    effective_key = topic_key
    if topic_key not in topics and not force_private:
        effective_key = "reports_vault"

    target_topic = topics.get(effective_key, {})
    thread_id = target_topic.get("thread_id")
    topic_name = target_topic.get("name", effective_key.upper())

    formatted_text = text
    if header_badge:
        formatted_text = f"{header_badge}\n{text}"

    send_raw_telegram._current_topic_key = effective_key

    if effective_key == "reports_vault" and dedicated_reports_chat_id and not force_private:
        ok_ded = send_raw_telegram(
            bot_token=bot_token,
            chat_id=str(dedicated_reports_chat_id),
            text=formatted_text,
            message_thread_id=None,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        if ok_ded:
            return True

    primary_ok = False
    if group_chat_id and thread_id and not force_private:
        primary_ok = send_raw_telegram(
            bot_token=bot_token,
            chat_id=str(group_chat_id),
            text=formatted_text,
            message_thread_id=int(thread_id),
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )

    if primary_ok:
        mirror_sources = {"alerts", "morning_blotter", "radar_filings", "hien_desk", "quant_risk", "academy_learning", "james_hq"}
        if (
            mirror_to_reports_vault
            and anti_noise.get("mirror_reports_to_vault_room", True)
            and effective_key in mirror_sources
            and len(text.strip()) >= 280
            and effective_key != "reports_vault"
        ):
            try:
                title_guess = _extract_title_from_text(text, topic_name)
                use_ai = use_ai_summary or (effective_key == "alerts")
                card_text, card_markup = build_search_optimized_card(
                    topic_key=effective_key,
                    title=title_guess,
                    raw_text=text,
                    report_rel_path=report_rel_path,
                    use_ai_summary=use_ai
                )
                dispatch_message(
                    topic_key="reports_vault",
                    text=card_text,
                    reply_markup=card_markup,
                    force_private=False,
                    parse_mode="Markdown",
                    mirror_to_reports_vault=False
                )
            except Exception:
                pass
        return True

    block_priv = bool(anti_noise.get("block_private_fallback_for_reports", True))
    if block_priv and not force_private and effective_key != "alerts":
        print(f"[Anti-Noise] Đã chặn fallback rác về Private Chat cho topic '{topic_key}'.")
        return False

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
    payload = {"chat_id": chat_id, "name": name, "icon_color": icon_color}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if res.get("ok"):
                return res.get("result", {}).get("message_thread_id")
            print(f"[!] createForumTopic error: {res}")
    except Exception as e:
        print(f"[!] Lỗi khi gọi createForumTopic: {e}")
    return None


def provision_all_topics_for_group(group_chat_id: str) -> Dict[str, Any]:
    """Tự động khởi tạo đầy đủ Forum Topics cho Group của Apex Fund."""
    cfg = load_config()
    bot_token = cfg.get("bot_token", "")
    cfg["group_chat_id"] = str(group_chat_id)
    results = {}
    for key, topic_info in cfg.get("topics", {}).items():
        name = topic_info.get("name", key)
        color = topic_info.get("icon_color", 16478046)
        th_id = create_forum_topic(bot_token, str(group_chat_id), name, color)
        if th_id:
            cfg["topics"][key]["thread_id"] = th_id
            results[key] = th_id
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
                if chat.get("type", "") in ["group", "supergroup"]:
                    return str(chat.get("id"))
    except Exception as e:
        print(f"[!] Lỗi quét group id: {e}")
    return None


if __name__ == "__main__":
    print("[*] Kiểm thử module Telegram Dispatcher V2.0...")
    cfg = load_config()
    print(f"  - Private Chat ID: {cfg['private_chat_id']}")
    print(f"  - Group Chat ID: {cfg.get('group_chat_id') or 'Chưa cấu hình'}")
    print(f"  - Dedicated Reports Chat ID: {cfg.get('dedicated_reports_chat_id') or 'Dùng Topic reports_vault'}")
    print(f"  - Số topics đã quy hoạch: {len(cfg.get('topics', {}))}")
