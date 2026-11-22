#!/usr/bin/env python3
"""
Trình sinh Văn phòng 2.5D Tương tác (Chat Artifact Generator) cho Apex Hedge Fund.
Đồng bộ toàn bộ dữ liệu sống 5 Khối Chuyên Trách + 1 Khu Tiện Ích từ
apex_virtual_office_engine.py vào Artifact HTML để Chủ tịch tương tác ngay cạnh khung chat Palmer.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.apex_virtual_office_engine import get_virtual_office_full_bundle

OFFICE_DIR = BASE_DIR / "dashboard" / "office"
DEFAULT_CHAT_ARTIFACT = Path(
    os.environ.get(
        "APEX_CHAT_ARTIFACT_PATH",
        r"C:\Users\phuoc\.gemini\antigravity\brain\b83f9dc0-2be4-4ab6-888c-baad89e655a4\apex_virtual_office_hq.html",
    )
)


def _safe_inline_json(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False)
    return raw.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def _safe_inline_js(code: str) -> str:
    return code.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")


def build_chat_office_html(force_refresh: bool = True) -> str:
    bundle: Dict[str, Any] = get_virtual_office_full_bundle(force_refresh=force_refresh)
    css_text = (OFFICE_DIR / "office.css").read_text(encoding="utf-8")
    js_text = (OFFICE_DIR / "office.js").read_text(encoding="utf-8")

    ssot = bundle.get("ssot", {})
    mkt = bundle.get("market_live", {})
    gen_at = html.escape(str(bundle.get("generated_at", "")))
    cash_str = html.escape(str(ssot.get("cash_str", "--")))
    cash_pct = float(ssot.get("cash_pct", 100.0))
    vni = html.escape(str(mkt.get("vn_index", "--")))
    regime = html.escape(str(mkt.get("live_regime", "STANDBY")))
    intel_cnt = int(((bundle.get("intel_feed") or {}).get("summary_counts") or {}).get("total_news_articles", 0))

    bundle_json = _safe_inline_json(bundle)
    js_safe = _safe_inline_js(js_text)

    quick_prompt = (
        "Palmer hãy điều phối cuộc họp 5 Khối theo đúng quy trình: "
        "① Hiền (Khối 1) cập nhật BCTC & tin mới ➔ ② Minh Quân & Alex (Khối 2) phân tích thị trường ➔ "
        "③ James & Palmer (Khối 3) hoàn thiện kế hoạch giải ngân trình Chủ tịch ◀── ④ Victor (Khối 4) báo mã chạm ngưỡng "
        "và ⑤ Trọng & Palmer (Khối 5) kiểm toán kỷ luật Hiến Chương."
    )
    quick_prompt_json = _safe_inline_json(quick_prompt)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Apex Hedge Fund — Văn Phòng Điều Hành 2.5D (5 Khối Chuyên Trách)</title>
    <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            background: #f1f5f9;
            color: #0f172a;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}
        .artifact-page {{
            max-width: 1460px;
            margin: 0 auto;
            padding: 12px 14px 18px;
        }}
        .apex-office-shell.artifact-mode {{
            height: 720px;
            min-height: 660px;
            max-height: none;
        }}
        @media (max-width: 768px) {{
            .apex-office-shell.artifact-mode {{
                height: 600px;
                min-height: 560px;
            }}
        }}
        {css_text}
    </style>
</head>
<body>
    <div class="artifact-page">
        <div class="bg-white border border-slate-200 rounded-2xl shadow-sm p-3 mb-3 flex flex-wrap items-center justify-between gap-3">
            <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                    <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        5 KHỐI CHUYÊN TRÁCH LIVE
                    </span>
                    <h1 class="text-sm sm:text-base font-extrabold text-slate-900 m-0">
                        Văn Phòng Điều Hành Apex Hedge Fund 2.5D — Trợ Lý Chat Palmer
                    </h1>
                </div>
                <div class="text-xs text-slate-600 mt-1 flex flex-wrap items-center gap-x-2 gap-y-1">
                    <span><strong>① Hiền</strong> (Dữ liệu &amp; BCTC)</span>
                    <span class="text-indigo-500 font-bold">➔</span>
                    <span><strong>② Minh Quân &amp; Alex</strong> (Thị trường)</span>
                    <span class="text-indigo-500 font-bold">➔</span>
                    <span><strong>③ James &amp; Palmer</strong> (Kế hoạch Đầu tư)</span>
                    <span class="text-amber-600 font-bold">◀──</span>
                    <span><strong>④ Victor</strong> (Canh 145 mã)</span>
                    <span class="text-slate-300">|</span>
                    <span><strong>⑤ Trọng &amp; Palmer</strong> (Giám sát HT)</span>
                </div>
            </div>
            <div class="flex flex-wrap items-center gap-2 text-xs">
                <span class="px-2.5 py-1.5 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-700">
                    🏦 TCBS 105C307855 • 💰 {cash_str} ({cash_pct:.0f}%) • 📊 VNI {vni} ({regime}) • 📰 {intel_cnt} tin • ⏱️ {gen_at}
                </span>
                <button id="artifact-copy-meeting-btn" type="button"
                    class="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold shadow-sm cursor-pointer transition">
                    💬 Copy Lệnh Họp 5 Khối Sang Chat
                </button>
                <a href="http://127.0.0.1:8000" target="_blank" rel="noopener noreferrer"
                    class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold no-underline transition">
                    🌐 Mở Portal Fullscreen
                </a>
            </div>
        </div>

        <div id="apex-virtual-office-root" class="apex-office-shell artifact-mode"></div>
    </div>

    <script>
        window.APEX_OFFICE_API_BASE = "http://127.0.0.1:8000";
        window.APEX_OFFICE_BOOTSTRAP_BUNDLE = {bundle_json};
    </script>
    <script>
{js_safe}
    </script>
    <script>
        (function () {{
            const promptText = {quick_prompt_json};
            function bootArtifactOffice() {{
                if (window.ApexVirtualOffice && typeof window.ApexVirtualOffice.init === "function") {{
                    window.ApexVirtualOffice.init();
                    setTimeout(function () {{
                        if (window.ApexVirtualOffice._state && typeof window.ApexVirtualOffice._state._resizeFn === "function") {{
                            window.ApexVirtualOffice._state._resizeFn();
                        }}
                    }}, 120);
                }}
                const btn = document.getElementById("artifact-copy-meeting-btn");
                if (btn) {{
                    btn.addEventListener("click", function () {{
                        if (navigator.clipboard && navigator.clipboard.writeText) {{
                            navigator.clipboard.writeText(promptText).then(function () {{
                                btn.innerText = "✅ Đã Copy — Dán Vào Chat Palmer!";
                                setTimeout(function () {{ btn.innerText = "💬 Copy Lệnh Họp 5 Khối Sang Chat"; }}, 2600);
                            }}).catch(function () {{
                                window.prompt("Chủ tịch copy chỉ thị giao họp cho Palmer:", promptText);
                            }});
                        }} else {{
                            window.prompt("Chủ tịch copy chỉ thị giao họp cho Palmer:", promptText);
                        }}
                    }});
                }}
            }}
            if (document.readyState === "loading") {{
                document.addEventListener("DOMContentLoaded", bootArtifactOffice);
            }} else {{
                bootArtifactOffice();
            }}
        }})();
    </script>
</body>
</html>
"""


def sync_chat_office_artifact(target_paths: List[Path] | None = None, force_refresh: bool = True) -> Dict[str, Any]:
    html_content = build_chat_office_html(force_refresh=force_refresh)
    targets = target_paths or [DEFAULT_CHAT_ARTIFACT]
    written: List[str] = []
    for path in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".html.tmp")
        tmp.write_text(html_content, encoding="utf-8")
        tmp.replace(path)
        written.append(str(path))
    bundle = get_virtual_office_full_bundle(force_refresh=False)
    return {
        "ok": True,
        "written_paths": written,
        "bytes": len(html_content.encode("utf-8")),
        "rooms_count": len(bundle.get("rooms", [])),
        "generated_at": bundle.get("generated_at", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sinh Artifact Văn phòng 2.5D 5 Khối cho khung chat Palmer")
    parser.add_argument("--output", action="append", help="Đường dẫn tệp HTML đích (có thể truyền nhiều lần)")
    parser.add_argument("--no-refresh", action="store_true", help="Không ép quét lại cache báo cáo")
    args = parser.parse_args()

    targets = [Path(p) for p in args.output] if args.output else None
    result = sync_chat_office_artifact(target_paths=targets, force_refresh=not args.no_refresh)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
