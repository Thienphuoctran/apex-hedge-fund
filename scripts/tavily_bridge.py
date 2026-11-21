#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAVILY 24/7 REST BRIDGE & DLP SECURITY GUARDRAIL (APEX CLOUD & LOCAL READY)
File: scripts/tavily_bridge.py
Cơ quan sử dụng: Ban 10 (Hiền IR), Ban 1-2 (Vĩ mô & BCTC), Ban 8 (James), Ban 9 (Victor), Ban 12 (Trọng)
"""

import os
import re
import ssl
import json
import html
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent

TAVILY_SEARCH_ENDPOINT = "https://api.tavily.com/search"
TAVILY_EXTRACT_ENDPOINT = "https://api.tavily.com/extract"

_FORBIDDEN_DLP_PATTERNS = [
    r"105C307855",
    r"tvly-[A-Za-z0-9_-]{8,}",
    r"AIza[A-Za-z0-9_-]{12,}",
    r"\b(?:otp|smart\s*otp|mật\s*khẩu|password|passcode|pin\s*code|secret\s*key)\b",
]


def load_tavily_api_key() -> str:
    """Đọc TAVILY_API_KEY từ biến môi trường (Render/GitHub Actions) hoặc file .env nội bộ."""
    env_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if env_key:
        return env_key

    env_path = BASE_DIR / ".env"
    if env_path.exists():
        try:
            for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "TAVILY_API_KEY":
                    val = v.strip().strip("'\"")
                    if val:
                        return val
        except Exception:
            pass
    return ""


def sanitize_query_dlp(text: str) -> Optional[str]:
    """Chốt chặn an ninh DLP: từ chối mọi truy vấn chứa dữ liệu tài khoản/bí mật."""
    if not text or not isinstance(text, str):
        return None
    cleaned = text.strip()[:380]
    for pat in _FORBIDDEN_DLP_PATTERNS:
        if re.search(pat, cleaned, flags=re.IGNORECASE):
            return None
    return cleaned


def _post_tavily_json(endpoint: str, payload: Dict[str, Any], timeout: int = 12) -> Dict[str, Any]:
    api_key = load_tavily_api_key()
    if not api_key:
        return {"ok": False, "error": "MISSING_TAVILY_API_KEY", "results": []}

    body = dict(payload)
    body["api_key"] = api_key
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")

    ssl_ctx = ssl.create_default_context()
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Apex-Institutional-247/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw)
            parsed["ok"] = True
            return parsed
    except urllib.error.HTTPError as he:
        err_body = ""
        try:
            err_body = he.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            pass
        return {"ok": False, "error": f"HTTP_{he.code}: {err_body}", "results": []}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "results": []}


def tavily_search(
    query: str,
    search_depth: str = "advanced",
    max_results: int = 5,
    topic: str = "general",
    time_range: Optional[str] = None,
    include_domains: Optional[List[str]] = None,
    include_answer: bool = False,
    timeout: int = 12,
) -> Dict[str, Any]:
    """Truy vấn Tavily Search API phục vụ Ban 10 Hiền, Ban 1-2 và Watchdog 24/7."""
    safe_q = sanitize_query_dlp(query)
    if not safe_q:
        return {"ok": False, "error": "BLOCKED_BY_DLP_OR_EMPTY_QUERY", "results": []}

    payload: Dict[str, Any] = {
        "query": safe_q,
        "search_depth": search_depth,
        "max_results": max(1, min(int(max_results), 10)),
        "topic": topic,
        "include_answer": include_answer,
    }
    if time_range in ("day", "week", "month", "year"):
        payload["time_range"] = time_range
    if include_domains:
        payload["include_domains"] = list(include_domains)

    return _post_tavily_json(TAVILY_SEARCH_ENDPOINT, payload, timeout=timeout)


def tavily_extract(
    urls: List[str],
    extract_depth: str = "advanced",
    timeout: int = 15,
) -> Dict[str, Any]:
    """Trích xuất nội dung Markdown sạch từ URL BCTC/CBTT/IR."""
    clean_urls = [u.strip() for u in (urls or []) if isinstance(u, str) and u.strip().startswith(("http://", "https://"))][:10]
    if not clean_urls:
        return {"ok": False, "error": "NO_VALID_URLS", "results": []}
    return _post_tavily_json(
        TAVILY_EXTRACT_ENDPOINT,
        {"urls": clean_urls, "extract_depth": extract_depth},
        timeout=timeout,
    )


def format_search_context_for_llm(resp: Dict[str, Any], max_items: int = 4, max_chars_per_item: int = 400) -> str:
    if not resp.get("ok"):
        return ""
    lines = []
    for idx, item in enumerate(resp.get("results", [])[:max_items], 1):
        title = str(item.get("title") or "").strip()
        url = str(item.get("url") or "").strip()
        snippet = re.sub(r"\s+", " ", str(item.get("content") or "")).strip()[:max_chars_per_item]
        lines.append(f"[{idx}] {title}\nNguồn: {url}\nNội dung: {snippet}")
    return "\n\n".join(lines)


def format_telegram_search_html(query: str, resp: Dict[str, Any], limit: int = 4) -> str:
    if not resp.get("ok"):
        return f"⚠️ <b>TAVILY SEARCH KHÔNG KHẢ DỤNG:</b> <code>{html.escape(str(resp.get('error', 'UNKNOWN')))}</code>"
    results = resp.get("results", [])[:limit]
    if not results:
        return f"🔎 Không tìm thấy kết quả phù hợp cho: <i>{html.escape(query)}</i>"
    lines = [f"🌐 <b>KẾT QUẢ TAVILY REAL-TIME:</b> <code>{html.escape(query)}</code>\n"]
    for idx, item in enumerate(results, 1):
        title = html.escape(str(item.get("title") or "Không tiêu đề").strip())
        url = str(item.get("url") or "").strip()
        snippet = html.escape(re.sub(r"\s+", " ", str(item.get("content") or "")).strip()[:220])
        lines.append(f"<b>{idx}. <a href=\"{html.escape(url)}\">{title}</a></b>\n• {snippet}...\n")
    return "\n".join(lines)
