#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX PORTAL SECURITY & SESSION AUTH ENGINE (PHASE 2.4)
File: scripts/apex_portal_auth.py
Cơ quan chủ quản: An Ninh Thể Chế & Bảo Mật Quỹ Apex (TCBS 105C307855)

Tính năng:
1. Kích hoạt bảo mật PIN / Bearer Token thông qua:
   - Biến môi trường `APEX_PORTAL_PIN` / `APEX_API_TOKEN` (khuyên dùng trên Render Cloud), HOẶC
   - Tệp cấu hình nội bộ `config/portal_security.json` (`--set-pin` lưu PBKDF2-HMAC-SHA256 hash).
2. Sinh và kiểm chứng Cookie `HttpOnly; SameSite=Lax` ký bằng HMAC-SHA256 (7 ngày).
3. Giữ nguyên `/api/health`, `/healthz`, `/health` ở chế độ công khai cho Render & Keep-Alive Ping.
"""

import sys
import os
import json
import hmac
import time
import hashlib
import secrets
import argparse
import http.cookies
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
SECURITY_CONFIG_FILE = CONFIG_DIR / "portal_security.json"
SESSION_COOKIE_NAME = "apex_session"
SESSION_TTL_SECONDS = 7 * 24 * 3600


def _read_dotenv_vars(keys: Tuple[str, ...]) -> Dict[str, str]:
    found: Dict[str, str] = {}
    for fname in (".env", ".env.tcbs"):
        fpath = BASE_DIR / fname
        if not fpath.exists():
            continue
        try:
            for line in fpath.read_text(encoding="utf-8", errors="ignore").splitlines():
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k in keys and v and k not in found:
                    found[k] = v
        except Exception:
            pass
    return found


def _get_runtime_secrets() -> Dict[str, Any]:
    keys = ("APEX_PORTAL_PIN", "APEX_API_TOKEN", "APEX_SESSION_SECRET")
    env_map = {k: os.environ.get(k, "").strip() for k in keys if os.environ.get(k, "").strip()}
    if len(env_map) < len(keys):
        dot_map = _read_dotenv_vars(keys)
        for k, v in dot_map.items():
            env_map.setdefault(k, v)

    file_cfg: Dict[str, Any] = {}
    if SECURITY_CONFIG_FILE.exists():
        try:
            file_cfg = json.loads(SECURITY_CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            file_cfg = {}

    env_pin = env_map.get("APEX_PORTAL_PIN", "")
    api_token = env_map.get("APEX_API_TOKEN", "")
    pin_hash = str(file_cfg.get("pin_hash", "")).strip() if file_cfg.get("enabled") else ""
    enabled = bool(env_pin or api_token or (file_cfg.get("enabled") and pin_hash))
    session_secret = (
        env_map.get("APEX_SESSION_SECRET")
        or str(file_cfg.get("session_secret", "")).strip()
        or hashlib.sha256(f"{env_pin}:{api_token}:{pin_hash}:105C307855".encode("utf-8")).hexdigest()
    )
    return {
        "enabled": enabled,
        "env_pin": env_pin,
        "api_token": api_token,
        "pin_hash": pin_hash,
        "session_secret": session_secret,
    }


def is_auth_enabled() -> bool:
    return bool(_get_runtime_secrets()["enabled"])


def hash_pin(pin: str, salt: Optional[str] = None) -> str:
    salt_hex = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt_hex.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256${salt_hex}${dk.hex()}"


def verify_pin_hash(pin: str, encoded_hash: str) -> bool:
    try:
        algo, salt_hex, expected_hex = encoded_hash.split("$", 2)
        if algo != "pbkdf2_sha256":
            return False
        actual = hash_pin(pin, salt_hex).split("$", 2)[2]
        return hmac.compare_digest(actual, expected_hex)
    except Exception:
        return False


def verify_pin_or_token(candidate: str) -> bool:
    cand = (candidate or "").strip()
    if not cand:
        return False
    sec = _get_runtime_secrets()
    if not sec["enabled"]:
        return True
    if sec["env_pin"] and hmac.compare_digest(cand, sec["env_pin"]):
        return True
    if sec["api_token"] and hmac.compare_digest(cand, sec["api_token"]):
        return True
    if sec["pin_hash"] and verify_pin_hash(cand, sec["pin_hash"]):
        return True
    return False


def create_session_token(ttl_seconds: int = SESSION_TTL_SECONDS) -> str:
    sec = _get_runtime_secrets()
    exp = int(time.time()) + ttl_seconds
    payload = f"chairman_105C307855.{exp}"
    sig = hmac.new(sec["session_secret"].encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def verify_session_token(token: str) -> bool:
    if not token or token.count(".") != 2:
        return False
    try:
        sub, exp_str, sig = token.split(".", 2)
        if sub != "chairman_105C307855":
            return False
        exp = int(exp_str)
        if exp < int(time.time()):
            return False
        sec = _get_runtime_secrets()
        payload = f"{sub}.{exp_str}"
        expected = hmac.new(sec["session_secret"].encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected)
    except Exception:
        return False


def is_request_authenticated(headers: Any) -> bool:
    sec = _get_runtime_secrets()
    if not sec["enabled"]:
        return True

    # 1. Check Authorization: Bearer <token>
    auth_hdr = ""
    try:
        auth_hdr = headers.get("Authorization", "") or ""
    except Exception:
        auth_hdr = ""
    if auth_hdr.lower().startswith("bearer "):
        bearer = auth_hdr[7:].strip()
        if verify_session_token(bearer) or verify_pin_or_token(bearer):
            return True

    # 2. Check HttpOnly Cookie: apex_session=...
    cookie_hdr = ""
    try:
        cookie_hdr = headers.get("Cookie", "") or ""
    except Exception:
        cookie_hdr = ""
    if cookie_hdr:
        try:
            c = http.cookies.SimpleCookie()
            c.load(cookie_hdr)
            if SESSION_COOKIE_NAME in c and verify_session_token(c[SESSION_COOKIE_NAME].value):
                return True
        except Exception:
            pass
    return False


def build_session_cookie_header(token: str, is_https: bool = False) -> str:
    parts = [
        f"{SESSION_COOKIE_NAME}={token}",
        "Path=/",
        "HttpOnly",
        "SameSite=Lax",
        f"Max-Age={SESSION_TTL_SECONDS}",
    ]
    if is_https:
        parts.append("Secure")
    return "; ".join(parts)


def build_logout_cookie_header() -> str:
    return f"{SESSION_COOKIE_NAME}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"


def render_pin_login_html(error_msg: str = "") -> str:
    err_html = (
        f'<div style="background:rgba(239,68,68,0.16);border:1px solid #ef4444;color:#fca5a5;padding:10px 12px;border-radius:8px;font-size:12px;margin-bottom:14px;">{error_msg}</div>'
        if error_msg
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Apex Institutional Portal V4.0 — Xác Thực Chủ Tịch</title>
<style>
  body {{
    margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center;
    background: radial-gradient(circle at top, #0f172a, #020617); color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }}
  .card {{
    width: 100%; max-width: 400px; background: rgba(15, 23, 42, 0.92);
    border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 16px;
    padding: 28px; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.65);
  }}
  .badge {{
    display: inline-block; font-size: 11px; font-weight: 800; letter-spacing: 0.5px;
    padding: 4px 10px; border-radius: 999px; background: rgba(56, 189, 248, 0.14);
    color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.35); margin-bottom: 12px;
  }}
  h1 {{ font-size: 20px; margin: 0 0 6px 0; }}
  p {{ font-size: 12.5px; color: #94a3b8; margin: 0 0 18px 0; line-height: 1.5; }}
  input {{
    width: 100%; box-sizing: border-box; padding: 12px 14px; font-size: 15px;
    border-radius: 10px; border: 1px solid rgba(148, 163, 184, 0.35);
    background: #020617; color: #f8fafc; outline: none; margin-bottom: 12px; letter-spacing: 2px;
  }}
  input:focus {{ border-color: #38bdf8; box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25); }}
  button {{
    width: 100%; padding: 12px; border: none; border-radius: 10px; cursor: pointer;
    background: linear-gradient(135deg, #0284c7, #2563eb); color: #fff;
    font-weight: 800; font-size: 14px;
  }}
  button:hover {{ filter: brightness(1.08); }}
</style>
</head>
<body>
  <div class="card">
    <div class="badge">🛡️ APEX INSTITUTIONAL WAR-ROOM V4.0</div>
    <h1>Cổng Bảo Mật Chủ Tịch</h1>
    <p>Tài khoản SSOT: <strong>TCBS 105C307855</strong><br>Vui lòng nhập mã PIN điều hành để mở khóa phiên làm việc bảo mật (HttpOnly Cookie 7 ngày).</p>
    {err_html}
    <div id="login-err" style="display:none;background:rgba(239,68,68,0.16);border:1px solid #ef4444;color:#fca5a5;padding:10px 12px;border-radius:8px;font-size:12px;margin-bottom:14px;"></div>
    <form id="pinForm" onsubmit="return submitPinLogin(event);">
      <input id="pinInput" type="password" autocomplete="current-password" placeholder="Nhập PIN Chủ tịch..." required autofocus>
      <button id="pinBtn" type="submit">🔓 MỞ KHÓA PORTAL</button>
    </form>
  </div>
  <script>
    async function submitPinLogin(e) {{
      e.preventDefault();
      const pin = document.getElementById('pinInput').value;
      const errBox = document.getElementById('login-err');
      const btn = document.getElementById('pinBtn');
      btn.disabled = true; btn.innerText = '⏳ Đang xác thực...';
      errBox.style.display = 'none';
      try {{
        const res = await fetch('/api/auth/login', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ pin }})
        }});
        const data = await res.json();
        if (res.ok && data.ok) {{
          window.location.reload();
        }} else {{
          errBox.innerText = data.error || 'Mã PIN không hợp lệ.';
          errBox.style.display = 'block';
        }}
      }} catch (err) {{
        errBox.innerText = 'Lỗi kết nối: ' + err.message;
        errBox.style.display = 'block';
      }} finally {{
        btn.disabled = false; btn.innerText = '🔓 MỞ KHÓA PORTAL';
      }}
      return false;
    }}
  </script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Apex Portal Security Manager")
    parser.add_argument("--set-pin", type=str, help="Đặt PIN bảo vệ cục bộ (lưu PBKDF2 hash vào config/portal_security.json)")
    parser.add_argument("--disable", action="store_true", help="Tắt PIN cục bộ (chỉ dùng biến môi trường nếu có)")
    parser.add_argument("--status", action="store_true", help="Xem trạng thái bảo mật Portal")
    args = parser.parse_args()

    if args.set_pin:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        cfg = {
            "enabled": True,
            "pin_hash": hash_pin(args.set_pin.strip()),
            "session_secret": secrets.token_hex(32),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        SECURITY_CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[+] Đã kích hoạt Portal PIN Security tại {SECURITY_CONFIG_FILE}")
    elif args.disable:
        if SECURITY_CONFIG_FILE.exists():
            cfg = json.loads(SECURITY_CONFIG_FILE.read_text(encoding="utf-8"))
            cfg["enabled"] = False
            SECURITY_CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
        print("[+] Đã tắt cấu hình PIN cục bộ.")
    else:
        sec = _get_runtime_secrets()
        print(json.dumps({
            "auth_enabled": sec["enabled"],
            "env_pin_configured": bool(sec["env_pin"]),
            "api_token_configured": bool(sec["api_token"]),
            "local_pin_hash_configured": bool(sec["pin_hash"]),
        }, indent=2))


if __name__ == "__main__":
    main()
