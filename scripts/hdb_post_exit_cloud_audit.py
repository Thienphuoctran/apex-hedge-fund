#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BAN 5 VN & VICTOR BAN 9 — HDB POST-EXIT CLOUD AUDIT WATCH (19–20/11/2026)
File: scripts/hdb_post_exit_cloud_audit.py
Chạy tự động trên GitHub Actions Cloud lúc 14h50 ICT Thứ Năm (19/11) & Thứ Sáu (20/11)
không cần bật máy cá nhân của Chủ tịch.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

ICT_TZ = datetime.timezone(datetime.timedelta(hours=7))
WATCH_FILE = BASE_DIR / "data" / "hdb_post_exit_audit_watch.json"
LEARNING_DIR = BASE_DIR / "VN_Market" / "05_Learning_And_Evolution"
JOURNAL_FILE = LEARNING_DIR / "vn_system_evolution_journal.md"


def _fetch_hdb_live_close() -> Tuple[Optional[float], Optional[float], Optional[float], str]:
    """Lấy giá chốt mới nhất của HDB & VN-Index từ VPS Direct API, fallback yfinance."""
    try:
        url = "https://bgapidatafeed.vps.com.vn/getliststockdata/HDB"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=12).read().decode("utf-8", errors="ignore")
        arr = json.loads(raw)
        if isinstance(arr, list) and arr:
            row = arr[0]
            last_p = float(row.get("lastPrice") or row.get("c") or 0) * 1000.0
            ref_p = float(row.get("r") or 0) * 1000.0
            high_p = float(row.get("highPrice") or 0) * 1000.0
            if last_p > 0:
                return round(last_p, 0), round(ref_p, 0), round(high_p, 0), "VPS_DIRECT"
    except Exception:
        pass

    try:
        import warnings
        warnings.simplefilter("ignore")
        import yfinance as yf
        t = yf.Ticker("HDB.VN")
        hist = t.history(period="5d", interval="1d")
        if not hist.empty:
            last_p = float(hist["Close"].iloc[-1])
            ref_p = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else last_p
            high_p = float(hist["High"].iloc[-1])
            if last_p < 1000:
                last_p *= 1000.0
                ref_p *= 1000.0
                high_p *= 1000.0
            return round(last_p, 0), round(ref_p, 0), round(high_p, 0), "YFINANCE_HDB_VN"
    except Exception:
        pass

    return None, None, None, "UNAVAILABLE"


def _evaluate_outcome(close_p: float, exit_p: float, rebound_trigger: float) -> Tuple[str, str, str]:
    diff_vnd = close_p - exit_p
    diff_pct = (diff_vnd / exit_p * 100.0) if exit_p > 0 else 0.0
    if close_p >= rebound_trigger:
        verdict = "REBOUND_ALERT_POST_MORTEM_REQUIRED"
        headline = f"⚠️ HDB BẬT TĂNG MẠNH +{diff_pct:.2f}% ({close_p:,.0f} đ vs giá thoát {exit_p:,.0f} đ) — RÚT KINH NGHIỆM BAN 5!"
        lesson = (
            f"HDB đã tăng vượt ngưỡng cảnh báo {rebound_trigger:,.0f} đ (+{diff_pct:.2f}% so với điểm bán 22,050 đ ngày 18/11). "
            "Cần rà soát lại: (1) Áp lực T-1 trước đáo hạn phái sinh (18/11) tạo nhịp quét cầu giả ép mất hàng sát hòa vốn; "
            "(2) Khi VN30 Bank có nền đỡ >100k quanh 22.0k và vẫn nằm trên Stop cứng 2xATR (21,486–21,700 đ), nên nới đệm biến động T-1 thay vì cắt khít ở giá vốn 22,050 đ."
        )
    elif close_p > exit_p * 1.003:
        verdict = "MILD_BOUNCE_MONITOR"
        headline = f"🟡 HDB hồi nhẹ +{diff_pct:.2f}% ({close_p:,.0f} đ vs giá thoát {exit_p:,.0f} đ)"
        lesson = (
            f"HDB đóng cửa nhích nhẹ lên {close_p:,.0f} đ (+{diff_pct:.2f}%). Sau trừ ~0.13% phí/thuế bán, mức hồi chưa vượt ngưỡng cảnh báo {rebound_trigger:,.0f} đ; "
            "vẫn tiếp tục giữ kỷ luật bảo toàn vốn và chờ xác nhận lực cầu bền vững hậu đáo hạn."
        )
    else:
        verdict = "EXIT_VALIDATED_CAPITAL_SAVED"
        headline = f"✅ XÁC NHẬN THOÁT CHUẨN: HDB ở {close_p:,.0f} đ ({diff_pct:+.2f}% vs giá thoát {exit_p:,.0f} đ)"
        lesson = (
            f"HDB đóng cửa tại {close_p:,.0f} đ ({diff_pct:+.2f}% so với giá bán 22,050 đ). Quyết định thoát hòa vốn ngày 18/11 "
            "lúc VN-Index giảm về 1,710 (Breadth 16.5%) đã bảo vệ trọn vẹn ~2.20 triệu tiền mặt sạch qua vùng nhiễu đáo hạn."
        )
    return verdict, headline, lesson


def run_audit(dry_run: bool = False) -> int:
    now_ict = datetime.datetime.now(ICT_TZ)
    date_str = now_ict.strftime("%Y-%m-%d")
    ts_str = now_ict.strftime("%Y-%m-%d %H:%M:%S ICT")

    if not WATCH_FILE.exists():
        print("[HDB-Audit] Không tìm thấy file hdb_post_exit_audit_watch.json -> Bỏ qua.")
        return 0

    watch = json.loads(WATCH_FILE.read_text(encoding="utf-8"))
    if watch.get("status") == "COMPLETED" and not dry_run:
        print("[HDB-Audit] Hồ sơ theo dõi HDB tuần 18-20/11 đã COMPLETED -> Thoát sạch.")
        return 0

    close_p, ref_p, high_p, source = _fetch_hdb_live_close()
    if close_p is None:
        print("[HDB-Audit] Không lấy được giá HDB từ VPS/yfinance.")
        return 1

    exit_p = float(watch.get("exit_price_vnd", 22050.0))
    entry_p = float(watch.get("entry_cost_basis_vnd", 22057.0))
    rebound_trigger = float(watch.get("alert_rebound_trigger_vnd", 22600.0))
    diff_vnd = close_p - exit_p
    diff_pct = (diff_vnd / exit_p * 100.0) if exit_p > 0 else 0.0

    verdict, headline, lesson = _evaluate_outcome(close_p, exit_p, rebound_trigger)
    print(f"[{ts_str}] {headline} (Src: {source}, Ref: {ref_p}, High: {high_p})")

    report_path = LEARNING_DIR / f"{date_str}_HDB_Post_Exit_Audit.md"
    report_md = (
        f"# 🔍 BÁO CÁO ĐỐI SOÁT HẬU BÁN `HDB` — {now_ict.strftime('%d/%m/%Y')}\n"
        f"> **Cơ quan thực hiện:** Ban 5 VN (Tự Học & Hồi Tố) + Ban 9 (Victor Sentinel) + Minh Quân (Ban 7)  \n"
        f"> **Thời điểm đối soát (Cloud Auto):** `{ts_str}` (`Nguồn: {source}`)  \n"
        f"> **Điểm thoát thực tế ngày `18/11`:** `100 CP @ {exit_p:,.0f} đ` (Giá vốn `{entry_p:,.0f} đ`)  \n\n"
        f"## 1. KẾT QUẢ GIÁ ĐÓNG CỬA & ĐỐI SOÁT\n"
        f"- **Giá chốt `HDB` ngày {now_ict.strftime('%d/%m')}:** **`{close_p:,.0f} đ`** (Tham chiếu: `{ref_p:,.0f} đ` | Cao nhất phiên: `{high_p:,.0f} đ`)\n"
        f"- **Chênh lệch so với giá đã bán (`22,050 đ`):** **`{diff_vnd:+,.0f} đ/CP` (`{diff_pct:+.2f}%`)**\n"
        f"- **Trạng thái kiểm toán:** `{verdict}`\n\n"
        f"## 2. KẾT LUẬN & BÀI HỌC RÚT KINH NGHIỆM (BAN 5)\n"
        f"{headline}\n\n"
        f"- **Phân tích nguyên nhân:** {lesson}\n"
    )

    if not dry_run:
        LEARNING_DIR.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_md, encoding="utf-8")

        checks = watch.setdefault("daily_checks", [])
        checks.append({
            "date": date_str,
            "timestamp_ict": ts_str,
            "close_price_vnd": close_p,
            "diff_vs_exit_pct": round(diff_pct, 2),
            "verdict": verdict,
            "source": source,
            "report_path": str(report_path.relative_to(BASE_DIR)).replace("\\", "/"),
        })
        if date_str >= "2026-11-20":
            watch["status"] = "COMPLETED"
        WATCH_FILE.write_text(json.dumps(watch, ensure_ascii=False, indent=2), encoding="utf-8")

        if JOURNAL_FILE.exists():
            jtxt = JOURNAL_FILE.read_text(encoding="utf-8", errors="ignore")
            tag = f"HDB Post-Exit Audit {date_str}"
            if tag not in jtxt:
                entry_line = f"\n- **[{tag} | {ts_str}]**: {headline} — {lesson}\n"
                JOURNAL_FILE.write_text(jtxt + entry_line, encoding="utf-8")

        try:
            from scripts.telegram_dispatcher import dispatch_message
            tg_text = (
                f"🔍 *[CLOUD AUTO — ĐỐI SOÁT HDB CUỐI TUẦN]*\n"
                f"• Ngày: `{now_ict.strftime('%d/%m/%Y %H:%M')}` (`{source}`)\n"
                f"• Giá đóng `HDB`: **`{close_p:,.0f} đ`** (Giá bán 18/11: `22,050 đ` | Chênh: **`{diff_pct:+.2f}%`**)\n"
                f"• Đánh giá: {headline}\n"
                f"• Bài học Ban 5: {lesson}"
            )
            dispatch_message(topic_key="alerts", text=tg_text)
        except Exception as e:
            print(f"[HDB-Audit] Warning Telegram dispatch: {e}")

        try:
            from scripts.palmer_antigravity_sync_bridge import PalmerAntigravitySyncBridge
            PalmerAntigravitySyncBridge.broadcast_from_antigravity_to_palmer(
                user_request=f"Cloud Auto Check HDB hậu bán ({date_str})",
                response_summary=f"{headline} — {lesson}",
                completed_tasks=[f"Xuất {report_path.name} & cập nhật hdb_post_exit_audit_watch.json"],
                active_decisions={"hdb_post_exit_verdict": verdict, "hdb_close": close_p, "diff_pct": round(diff_pct, 2)},
            )
        except Exception as e:
            print(f"[HDB-Audit] Warning Palmer bridge: {e}")
    else:
        print("[HDB-Audit DRY-RUN] Verdict:", verdict, "| Report preview OK.")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Cloud HDB Post-Exit Audit Watch (19-20/11/2026)")
    parser.add_argument("--dry-run", action="store_true", help="Chạy thử đọc giá thật nhưng không ghi file/gửi Telegram")
    args = parser.parse_args()
    return run_audit(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
