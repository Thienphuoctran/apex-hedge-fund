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
ROOM_CONTROLS_FILE = BASE_DIR / "data" / "telegram_room_controls.json"
_ICT_TZ = datetime.timezone(datetime.timedelta(hours=7))

DEFAULT_ROOM_CONTROLS: Dict[str, Dict[str, Any]] = {
    "team_hien": {
        "label": "Khối 1 — Đội Hiền (Dữ liệu & BCTC)",
        "topic_keys": ["hien_desk", "radar_filings"],
        "muted": False,
        "updated_at": "",
    },
    "team_quan_alex": {
        "label": "Khối 2 — Đội Minh Quân & Alex",
        "topic_keys": ["daily_warroom", "morning_blotter"],
        "muted": False,
        "updated_at": "",
    },
    "team_james_palmer": {
        "label": "Khối 3 — James & Palmer (Điều hành)",
        "topic_keys": ["james_hq", "assistant_nam"],
        "muted": False,
        "updated_at": "",
    },
    "team_victor": {
        "label": "Khối 4 — Victor (Cảnh giới Live)",
        "topic_keys": ["alerts"],
        "muted": False,
        "updated_at": "",
    },
    "team_trong_palmer": {
        "label": "Khối 5 — Trọng & Palmer (Kiểm sát)",
        "topic_keys": ["reports_vault", "quant_risk"],
        "muted": False,
        "updated_at": "",
    },
}


def get_room_telegram_controls() -> Dict[str, Dict[str, Any]]:
    """Đọc trạng thái Bật/Tắt thông báo Telegram từng Khối (5 Khối)."""
    out = {k: dict(v) for k, v in DEFAULT_ROOM_CONTROLS.items()}
    if ROOM_CONTROLS_FILE.exists():
        try:
            saved = json.loads(ROOM_CONTROLS_FILE.read_text(encoding="utf-8-sig"))
            rooms = saved.get("rooms") if isinstance(saved.get("rooms"), dict) else saved
            if isinstance(rooms, dict):
                for rid, cfg in rooms.items():
                    if rid in out and isinstance(cfg, dict):
                        out[rid]["muted"] = bool(cfg.get("muted", False))
                        out[rid]["updated_at"] = str(cfg.get("updated_at") or "")
        except Exception:
            pass
    return out


def set_room_telegram_mute(room_id: str, muted: bool) -> Dict[str, Dict[str, Any]]:
    """Lưu trạng thái Tắt/Bật Telegram cho 1 Khối (hoặc 'all') xuống data/telegram_room_controls.json."""
    controls = get_room_telegram_controls()
    now_str = _get_ict_now().strftime("%Y-%m-%d %H:%M:%S ICT")
    targets = list(controls.keys()) if room_id == "all" else ([room_id] if room_id in controls else [])
    for rid in targets:
        controls[rid]["muted"] = bool(muted)
        controls[rid]["updated_at"] = now_str
    ROOM_CONTROLS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = ROOM_CONTROLS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"updated_at": now_str, "rooms": controls}, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(ROOM_CONTROLS_FILE)
    return controls


def _resolve_room_id_for_topic(topic_key: Optional[str]) -> Optional[str]:
    if not topic_key:
        return None
    tk = str(topic_key).strip().lower()
    controls = get_room_telegram_controls()
    for rid, cfg in controls.items():
        if tk in [str(x).lower() for x in (cfg.get("topic_keys") or [])]:
            return rid
    return None


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
        "daily_warroom": ("⚡ PHÒNG TÁC CHIẾN MỖI NGÀY", "#TAC_CHIEN_NGAY #V3_WARROOM"),
        "james_hq": ("🎖️ PHÒNG CỦA JAMES", "#MASTER_CIO #KE_HOACH_HOAN_CHINH"),
        "assistant_nam": ("💼 PHÒNG TRỢ LÝ CÁ NHÂN", "#TRO_LY"),
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


def should_block_outbound_telegram(
    is_intraday_alert: bool = False,
    priority: str = "NORMAL",
    topic_key: Optional[str] = None,
    room_id: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    [OUTBOUND GUARD] Chống gửi trùng giữa Cloud & PC, chặn tin ngày nghỉ lễ và tôn trọng nút Tắt Telegram từng phòng.
    """
    prio = str(priority or "NORMAL").upper()
    if prio == "CRITICAL_STOP":
        return False, "CRITICAL_OVERRIDE"

    target_room = room_id or _resolve_room_id_for_topic(topic_key)
    if target_room:
        controls = get_room_telegram_controls()
        if controls.get(target_room, {}).get("muted", False):
            return True, f"ROOM_MUTED:{target_room}"

    is_cloud_env = (
        os.environ.get("RENDER", "").strip().lower() == "true"
        or os.environ.get("APEX_CLOUD_COMPACT_MODE", "").strip() == "1"
    )
    polling_owner = os.environ.get("TELEGRAM_POLLING_OWNER", "").strip().lower()
    allow_cloud_push = os.environ.get("APEX_ALLOW_CLOUD_TELEGRAM_PUSH", "0").strip() == "1"
    if is_cloud_env and polling_owner == "pc" and not allow_cloud_push:
        return True, "CLOUD_SINGLE_OWNER_PC"

    if is_intraday_alert:
        try:
            from scripts.vn_market_calendar import get_vn_market_session_state
            msess = get_vn_market_session_state(now_ict=_get_ict_now())
            if (not msess.get("is_trading_day", True)) or bool(msess.get("stale_feed_detected", False)):
                return True, f"HOLIDAY_OR_CLOSED_MARKET:{msess.get('status_code', 'CLOSED')}"
        except Exception:
            pass

    return False, "ALLOWED"


def _clean_plain_fallback_text(text: str) -> str:
    """Loại bỏ ký tự Markdown thô (*, `, _ biên) nếu phải fallback sang plain text."""
    cleaned = re.sub(r"[*`]", "", text or "")
    cleaned = re.sub(r"(?<!\w)_|_(?!\w)", "", cleaned)
    return cleaned


def is_duplicate_message(
    chat_id: str,
    thread_id: Optional[int],
    text: str,
    window_seconds: int = 1800,
    event_key: Optional[str] = None,
    priority: str = "NORMAL",
) -> bool:
    """
    [4-LAYER DEDUP SHIELD + QUOTA BREAKER]
    1) Event Key Cooldown (VD: 2026-11-24_HPG_STOP).
    2) Semantic Hash bỏ qua con số dao động nhỏ (BuyUp 39.3% -> 39.4% không gửi lại).
    3) Exact Hash chống bắn đúp đồng thời.
    4) Quota Circuit Breaker: Tối đa 6 tin/giờ & 25 tin/ngày mỗi phòng (trừ CRITICAL_STOP).
    """
    try:
        now_ict = _get_ict_now()
        today_str = now_ict.strftime("%Y-%m-%d")
        now_ts = time.time()
        prio = str(priority or "NORMAL").upper()
        win_sec = max(60, int(window_seconds or 1800))

        raw_cache: Dict[str, Any] = {}
        if DEDUP_CACHE_FILE.exists():
            try:
                with open(DEDUP_CACHE_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        raw_cache = loaded
            except Exception:
                raw_cache = {}

        if "events" in raw_cache and isinstance(raw_cache.get("events"), dict):
            events: Dict[str, Any] = dict(raw_cache.get("events") or {})
            quotas: Dict[str, Any] = dict(raw_cache.get("quotas") or {})
        else:
            # Tương thích ngược từ cấu trúc dict phẳng cũ
            events = {
                k: v for k, v in raw_cache.items()
                if isinstance(v, dict) and "ts" in v
            }
            quotas = {}

        # Dọn cache quá 24h & quota ngoài ngày hôm nay
        events = {
            k: v for k, v in events.items()
            if isinstance(v, dict) and (now_ts - float(v.get("ts", 0))) < 86400
        }
        cleaned_quotas: Dict[str, Any] = {}
        for qk, qv in quotas.items():
            if isinstance(qv, dict) and qv.get("date") == today_str:
                ts_list = [float(x) for x in (qv.get("timestamps") or []) if (now_ts - float(x)) < 86400]
                cleaned_quotas[qk] = {"date": today_str, "timestamps": ts_list}
        quotas = cleaned_quotas

        q_key = f"{chat_id}_{thread_id}"
        q_rec = quotas.get(q_key, {"date": today_str, "timestamps": []})
        day_ts = list(q_rec.get("timestamps") or [])
        hour_ts = [t for t in day_ts if (now_ts - float(t)) < 3600]

        if prio != "CRITICAL_STOP":
            if len(hour_ts) >= 6:
                print(f"[!] [QUOTA BREAKER] Topic {q_key} đã đạt trần 6 tin/giờ ({len(hour_ts)}). Tự động chặn chống spam!")
                return True
            if len(day_ts) >= 25:
                print(f"[!] [QUOTA BREAKER] Topic {q_key} đã đạt trần 25 tin/ngày ({len(day_ts)}). Tự động chặn chống spam!")
                return True

        ev_id: Optional[str] = None
        if event_key:
            ev_digest = hashlib.sha256(str(event_key).encode("utf-8")).hexdigest()[:24]
            ev_id = f"{chat_id}_{thread_id}_EV_{ev_digest}"
            if ev_id in events:
                elapsed = now_ts - float(events[ev_id].get("ts", 0))
                if elapsed < win_sec:
                    print(f"[!] [EVENT COOLDOWN] Event '{event_key}' đã gửi cách đây {elapsed:.0f}s (< {win_sec}s). Chặn trùng!")
                    return True

        # Semantic hash: loại bỏ mọi số liệu/thời gian dao động nhỏ (39.3% -> #, 11:08 -> #)
        semantic_norm = re.sub(r"\d[\d.,:%+-]*", "#", str(text or ""))
        semantic_norm = re.sub(r"\s+", " ", semantic_norm).strip()
        sem_digest = hashlib.sha256(semantic_norm.encode("utf-8")).hexdigest()[:24]
        sem_id = f"{chat_id}_{thread_id}_SEM_{sem_digest}"
        if prio != "CRITICAL_STOP" and sem_id in events:
            elapsed = now_ts - float(events[sem_id].get("ts", 0))
            if elapsed < win_sec:
                print(f"[!] [SEMANTIC DEDUP] Tin cùng mẫu biến động đã gửi cách đây {elapsed:.0f}s (< {win_sec}s). Chặn spam!")
                return True

        exact_norm = "".join(str(text or "").split())
        exact_digest = hashlib.sha256(f"{chat_id}_{thread_id}_{exact_norm}".encode("utf-8")).hexdigest()[:24]
        exact_id = f"{chat_id}_{thread_id}_EX_{exact_digest}"
        if exact_id in events:
            elapsed = now_ts - float(events[exact_id].get("ts", 0))
            if elapsed < win_sec:
                print(f"[!] [EXACT DEDUP] Tin trùng khớp tuyệt đối cách đây {elapsed:.0f}s. Chặn ngay!")
                return True

        entry_meta = {"ts": now_ts, "thread_id": thread_id, "preview": str(text or "")[:64]}
        if ev_id:
            events[ev_id] = dict(entry_meta, event_key=str(event_key))
        events[sem_id] = dict(entry_meta)
        events[exact_id] = dict(entry_meta)

        day_ts.append(now_ts)
        quotas[q_key] = {"date": today_str, "timestamps": day_ts[-40:]}

        DEDUP_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = DEDUP_CACHE_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"events": events, "quotas": quotas}, f, indent=2, ensure_ascii=False)
        tmp.replace(DEDUP_CACHE_FILE)

        return False
    except Exception:
        return False


def send_raw_telegram(
    bot_token: str,
    chat_id: str,
    text: str,
    message_thread_id: Optional[int] = None,
    reply_markup: Optional[Dict[str, Any]] = None,
    parse_mode: Optional[str] = "Markdown",
    event_key: Optional[str] = None,
    cooldown_seconds: int = 1800,
    is_intraday_alert: bool = False,
    priority: str = "NORMAL",
) -> bool:
    """Gửi tin nhắn Telegram có 4 lớp khiên chống spam + HTML/Markdown an toàn."""
    if not bot_token or not chat_id:
        return False

    blocked, reason = should_block_outbound_telegram(
        is_intraday_alert=is_intraday_alert,
        priority=priority,
        topic_key=getattr(send_raw_telegram, "_current_topic_key", None),
    )
    if blocked:
        print(f"[Telegram Guard] Chặn gửi tin tự động ({reason}).")
        return False

    if is_duplicate_message(
        chat_id,
        message_thread_id,
        text,
        window_seconds=cooldown_seconds,
        event_key=event_key,
        priority=priority,
    ):
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
                    payload["text"] = _clean_plain_fallback_text(chunk) if parse_mode == "Markdown" else re.sub(r"<[^>]+>", "", chunk)
                    data = json.dumps(payload).encode("utf-8")
                    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
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


LEGACY_TOPIC_ALIAS_MAP: Dict[str, str] = {
    "morning_blotter": "daily_warroom",
    "alerts": "daily_warroom",
    "radar_filings": "daily_warroom",
    "quant_risk": "daily_warroom",
    "academy_learning": "daily_warroom",
    "hien_desk": "daily_warroom",
    "khanh_studio": "daily_warroom",
    "reports_vault": "daily_warroom",
}


def dispatch_message(
    topic_key: str,
    text: str,
    header_badge: Optional[str] = None,
    reply_markup: Optional[Dict[str, Any]] = None,
    force_private: bool = False,
    parse_mode: Optional[str] = "Markdown",
    report_rel_path: Optional[str] = None,
    mirror_to_reports_vault: bool = True,
    use_ai_summary: bool = False,
    allow_assistant_standby: bool = False,
    event_key: Optional[str] = None,
    cooldown_seconds: int = 1800,
    is_intraday_alert: bool = False,
    priority: str = "NORMAL",
) -> bool:
    """
    Định tuyến tin nhắn chuẩn 3 Phòng Telegram kèm 4 lớp chống spam:
      1. `assistant_nam`: Phòng Trợ lý Cá nhân (mặc định standby, chặn bot tự spam nếu chưa mở).
      2. `daily_warroom`: Phòng Tác chiến Mỗi ngày (hợp nhất toàn bộ báo cáo/biến động kế hoạch trong ngày).
      3. `james_hq`: Phòng của Master CIO James (gửi Kế hoạch Tác chiến Hoàn chỉnh trong ngày).
    """
    blocked, reason = should_block_outbound_telegram(
        is_intraday_alert=is_intraday_alert,
        priority=priority,
        topic_key=topic_key,
    )
    if blocked:
        print(f"[Telegram Guard] Bỏ qua gửi tin topic '{topic_key}' ({reason}).")
        return False

    cfg = load_config()
    bot_token = cfg.get("bot_token", "")
    group_chat_id = cfg.get("group_chat_id")
    dedicated_reports_chat_id = cfg.get("dedicated_reports_chat_id")
    private_chat_id = cfg.get("private_chat_id", "")
    topics = cfg.get("topics", {})
    anti_noise = cfg.get("anti_noise_routing", {}) or {}

    effective_key = LEGACY_TOPIC_ALIAS_MAP.get(topic_key, topic_key)
    if effective_key not in topics and not force_private:
        effective_key = "daily_warroom" if "daily_warroom" in topics else ("james_hq" if "james_hq" in topics else effective_key)

    if effective_key == "assistant_nam" and bool(cfg.get("assistant_room_standby", True)) and not allow_assistant_standby:
        print("[Telegram 3-Room] Phòng Trợ Lý đang ở chế độ Standby theo chỉ thị Chủ tịch (bỏ qua tin tự động).")
        return True

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
            parse_mode=parse_mode,
            event_key=event_key,
            cooldown_seconds=cooldown_seconds,
            is_intraday_alert=is_intraday_alert,
            priority=priority,
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
            parse_mode=parse_mode,
            event_key=event_key,
            cooldown_seconds=cooldown_seconds,
            is_intraday_alert=is_intraday_alert,
            priority=priority,
        )

    if primary_ok:
        if (
            mirror_to_reports_vault
            and anti_noise.get("mirror_reports_to_vault_room", False)
            and "reports_vault" in topics
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
                    mirror_to_reports_vault=False,
                    event_key=(f"MIRROR_{event_key}" if event_key else None),
                    cooldown_seconds=cooldown_seconds,
                    is_intraday_alert=is_intraday_alert,
                    priority=priority,
                )
            except Exception:
                pass
        return True

    block_priv = bool(anti_noise.get("block_private_fallback_for_reports", True))
    if block_priv and not force_private and effective_key != "alerts":
        print(f"[Anti-Noise] Đã chặn fallback rác về Private Chat cho topic '{topic_key}'.")
        return False

    fallback_badge = f"🔖 *[{topic_name}]*\n" if parse_mode == "Markdown" else f"🔖 <b>[{topic_name}]</b>\n"
    if fallback_badge not in formatted_text:
        formatted_text = f"{fallback_badge}{formatted_text}"

    return send_raw_telegram(
        bot_token=bot_token,
        chat_id=str(private_chat_id),
        text=formatted_text,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
        event_key=event_key,
        cooldown_seconds=cooldown_seconds,
        is_intraday_alert=is_intraday_alert,
        priority=priority,
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


def send_single_eod_digest(force: bool = False) -> bool:
    """
    [ANTI-SPAM V7.0] Gửi DUY NHẤT 1 bản Tổng Kết Cuối Ngày (EOD Digest) chuẩn hóa từ SCBP
    thay thế mọi tin nhắn rời rạc cuối phiên.
    """
    import html as _html_mod

    now_ict = _get_ict_now()
    today_str = now_ict.strftime("%Y-%m-%d")
    scbp_path = BASE_DIR / "data" / "canonical_executive_briefing.json"
    scbp: Dict[str, Any] = {}
    if scbp_path.exists():
        try:
            scbp = json.loads(scbp_path.read_text(encoding="utf-8-sig"))
        except Exception:
            scbp = {}
    if not scbp or not scbp.get("sha256_seal"):
        try:
            from scripts.apex_unified_briefing_builder import build_canonical_executive_briefing
            scbp = build_canonical_executive_briefing()
        except Exception as e:
            print(f"[!] Không build được SCBP cho EOD Digest: {e}")
            return False

    ev = scbp.get("executive_verdict") or {}
    sla = scbp.get("freshness_sla") or {}
    trong = scbp.get("trong_audit_seal") or {}
    board = (scbp.get("simple_action_board") or [])[:5]
    seal = str(scbp.get("sha256_seal") or "")[:12]

    lines = [
        f"📊 <b>BẢN TIN TỔNG KẾT EOD DUY NHẤT — APEX V7.0</b> ({_html_mod.escape(today_str)})",
        f"🔐 <b>SCBP Seal:</b> <code>{_html_mod.escape(seal)}</code> | <b>Trọng:</b> {trong.get('passed_count', 0)}/{trong.get('total_gates', 12)} | <b>BCTC:</b> {sla.get('bctc_verified_count', 0)}/{sla.get('bctc_requested_count', 145)}",
        "",
        f"1️⃣ <b>Đang cầm:</b> {_html_mod.escape(str(ev.get('what_holding_vi') or ''))}",
        f"2️⃣ <b>Lãi/Lỗ ròng:</b> {_html_mod.escape(str(ev.get('net_pnl_vi') or ''))}",
        f"3️⃣ <b>Hành động tới:</b> {_html_mod.escape(str(ev.get('next_action_vi') or ''))}",
        "",
        "🎯 <b>BẢNG HÀNH ĐỘNG NHANH:</b>",
    ]
    for row in board:
        lines.append(
            f"• <b>{_html_mod.escape(str(row.get('symbol') or ''))}</b>: {_html_mod.escape(str(row.get('action_label_vi') or ''))} "
            f"(Giá {float(row.get('price_vnd') or 0):,.0f}đ | Stop {float(row.get('stop_loss_vnd') or 0):,.0f}đ | TP1 {float(row.get('tp1_vnd') or 0):,.0f}đ)"
        )

    msg_html = "\n".join(lines)[:3750]
    return dispatch_message(
        topic_key="james_hq",
        text=msg_html,
        parse_mode="HTML",
        mirror_to_reports_vault=False,
        event_key=f"EOD_SINGLE_DIGEST_{today_str}",
        cooldown_seconds=(60 if force else 43200),
        is_intraday_alert=False,
        priority="HIGH_CONVICTION",
    )


if __name__ == "__main__":
    print("[*] Kiểm thử module Telegram Dispatcher V2.0...")
    cfg = load_config()
    print(f"  - Private Chat ID: {cfg['private_chat_id']}")
    print(f"  - Group Chat ID: {cfg.get('group_chat_id') or 'Chưa cấu hình'}")
    print(f"  - Dedicated Reports Chat ID: {cfg.get('dedicated_reports_chat_id') or 'Dùng Topic reports_vault'}")
    print(f"  - Số topics đã quy hoạch: {len(cfg.get('topics', {}))}")
