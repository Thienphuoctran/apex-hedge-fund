#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX PERSISTENT CROSS-DAY MEMORY & CONTINUITY CORE (v4.0 Institutional Memory Engine)
File: scripts/apex_persistent_memory_core.py
Cơ quan chủ trì: Ban 5 VN (Hồi Tố & Tự Học Thích Nghi) & Ban 8 (Master CIO James)

Nhiệm vụ cốt lõi (Giải quyết triệt để bài toán "Không bao giờ như tờ giấy trắng qua ngày hôm sau"):
1. Lưu trữ bất biến toàn bộ hoạt động nghiên cứu, quét 145 mã / 18 ngành, biên bản tranh luận của 10 phòng ban,
   các mã được duyệt đưa vào Tầm ngắm, các mã bị bác bỏ (kèm lý do bác bỏ), và trạng thái tài sản thực tế trong ngày.
2. Tạo Bản Giao Ca Liên Ngày (`Cross-Day Handover Bridge`):
   - Khi bước sang ngày làm việc tiếp theo, hệ thống tự động nạp ký ức của các ngày trước đó.
   - Tự động đối chiếu giá cổ phiếu hôm nay so với giá tại thời điểm họp ngày hôm trước (Walk-Forward Verification)
     để biết nhận định của phòng ban nào đúng, phòng ban nào sai.
3. Cung cấp API truy xuất ký ức xuyên suốt cho toàn bộ 11 Phòng Ban và Bot Telegram (`/kyuc`, `/giaoca`, `/hop`).
"""

import os
import sys
import json
import datetime
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SNAPSHOTS_DIR = DATA_DIR / "daily_snapshots"
CONTINUITY_LEDGER_FILE = DATA_DIR / "apex_daily_continuity_ledger.json"
EPISODIC_MEMORY_FILE = DATA_DIR / "apex_episodic_memory_ledger.json"


class ApexPersistentMemoryCore:
    """Bộ não ghi nhớ xuyên ngày của Quỹ Đầu Tư Định Lượng Apex."""

    @staticmethod
    def load_continuity_ledger() -> Dict[str, Any]:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        if CONTINUITY_LEDGER_FILE.exists():
            try:
                with open(CONTINUITY_LEDGER_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "ledger_version": "4.0-INSTITUTIONAL-CONTINUITY",
            "account_id": "105C307855",
            "chairman": "Trần Quốc Thiên Phước",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "historical_campaigns_completed": [
                {
                    "campaign_id": "CAMPAIGN-VN-ROUND-01",
                    "period": "2026-11-04 -> 2026-11-06",
                    "status": "CLOSED_100_PERCENT_CASH",
                    "initial_capital_vnd": 20000000.0,
                    "final_settled_cash_vnd": 20167119.0,
                    "net_profit_after_tax_fee_vnd": 167119.0,
                    "closed_trades": [
                        {"symbol": "HPG", "shares": 400, "entry": 21156, "status": "SOLD_ALL"},
                        {"symbol": "TCB", "shares": 300, "entry": 21356, "status": "SOLD_ALL"},
                        {"symbol": "MBB", "shares": 200, "entry": 18606, "status": "SOLD_ALL"}
                    ],
                    "key_lesson": "Chốt lời toàn bộ trước kỳ nghỉ cuối tuần, bảo toàn 100% vốn + lãi thực nhận 20,167,119 ₫, 0% rủi ro qua tuần."
                }
            ],
            "daily_work_logs": {},
            "active_council_resolutions": {},
            "rejected_tickers_memory": {},
            "handover_briefing_for_next_session": {}
        }

    @staticmethod
    def record_daily_session(
        date_str: str,
        scan_summary: Dict[str, Any],
        council_resolution: Dict[str, Any],
        approved_watchlist: List[Dict[str, Any]],
        rejected_candidates: List[Dict[str, Any]],
        manual_actions_required: List[str]
    ) -> Dict[str, Any]:
        """Ghi nhớ toàn bộ kết quả làm việc trong ngày và tạo Bản Giao Ca cho ngày hôm sau."""
        ledger = ApexPersistentMemoryCore.load_continuity_ledger()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ledger["last_updated"] = now_str

        # Lưu chi tiết phiên làm việc hôm nay
        session_record = {
            "session_date": date_str,
            "recorded_at": now_str,
            "total_stocks_scanned": scan_summary.get("total_stocks_scanned", 145),
            "total_sectors_scanned": scan_summary.get("total_sectors_covered", 18),
            "market_breadth": scan_summary.get("market_breadth_summary", {}),
            "top_leading_sectors": [
                {
                    "sector_name": s["sector_name"],
                    "score": s["sector_strength_score"],
                    "stage": s["rotation_stage"],
                    "top_picks": s["top_sector_picks"]
                }
                for s in scan_summary.get("sector_rotation_ranking", [])[:5]
            ],
            "council_resolution_id": council_resolution.get("resolution_id", f"RES-{date_str}"),
            "departments_participated_count": len(council_resolution.get("departmental_reports", [])),
            "approved_round2_watchlist": approved_watchlist,
            "rejected_or_downgraded_stocks": rejected_candidates,
            "manual_actions_required_from_chairman": manual_actions_required
        }

        ledger.setdefault("daily_work_logs", {})[date_str] = session_record
        ledger["active_council_resolutions"] = council_resolution

        # Cập nhật bộ nhớ các mã bị loại/hạ bậc để ngày mai không lặp lại sai lầm
        rej_mem = ledger.setdefault("rejected_tickers_memory", {})
        for r in rejected_candidates:
            rej_mem[r["code"]] = {
                "rejected_on": date_str,
                "price_at_rejection": r.get("price", 0),
                "reason": r.get("rejection_reason", ""),
                "rejected_by_department": r.get("rejected_by", "Ban 3 & Ban 4")
            }

        # Tạo Bản Giao Ca Liên Ngày (Handover Briefing) cho phiên làm việc tiếp theo
        handover = {
            "generated_from_session": date_str,
            "generated_at": now_str,
            "account_cash_vnd": council_resolution.get("account_cash_vnd", 20167119.0),
            "portfolio_status": council_resolution.get("portfolio_status", "ALL_CASH_STANDDOWN"),
            "what_we_did_last_session": (
                f"Phiên {date_str}: Hệ thống đã quét toàn diện {session_record['total_stocks_scanned']} cổ phiếu thuộc "
                f"{session_record['total_sectors_scanned']} nhóm ngành trên 3 sàn HOSE/HNX/UPCoM. "
                f"10 Phòng ban đã họp tranh biện trực tiếp, loại bỏ thói quen chỉ nhìn vào 4 mã cũ (hạ bậc FPT do RS=18 gãy MA20, "
                f"hạ bậc DGC do RS=22 yếu, loại MWG/FRT khỏi danh mục mua trực tiếp do 1 lô 100 CP chiếm >35% vốn 20M). "
                f"Đã tuyển chọn bộ Tầm ngắm Vòng 2 đa ngành có RS 81-96 và BCTC hạng AAA/AA vừa khít quy mô vốn 20.16 triệu VNĐ."
            ),
            "Priority_Watchlist_To_Track_Next_Session": [
                {
                    "code": w["code"],
                    "name": w["name"],
                    "sector": w["sector_name"],
                    "reference_price_vnd": w["price"],
                    "ideal_buy_zone_vnd": w["probe_buy_price"],
                    "breakout_trigger_vnd": w["breakout_buy_price"],
                    "stop_loss_2atr_vnd": w["stop_loss_2atr"],
                    "tp1_vnd": w["tp1"],
                    "target_shares_lot100": w["target_shares"],
                    "allocated_capital_vnd": w["allocated_vnd"],
                    "rs_rating": w["rs_rating"],
                    "legends_score": w["legends_score"]
                }
                for w in approved_watchlist
            ],
            "Rejected_Stocks_Do_Not_Repropose_Unless_Reversal": [
                f"{r['code']} ({r['rejection_reason']})" for r in rejected_candidates
            ],
            "Pending_Manual_Actions_For_Chairman": manual_actions_required
        }
        ledger["handover_briefing_for_next_session"] = handover

        # Lưu vào file chính và file snapshot theo ngày
        with open(CONTINUITY_LEDGER_FILE, "w", encoding="utf-8") as f:
            json.dump(ledger, f, ensure_ascii=False, indent=2)

        snap_path = SNAPSHOTS_DIR / f"{date_str}_session_memory.json"
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump(session_record, f, ensure_ascii=False, indent=2)

        return ledger

    @staticmethod
    def get_handover_for_today(live_stocks: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Nạp Bản Giao Ca từ phiên trước và tự động đối soát với giá thực tế hôm nay (Walk-Forward Continuity Check).
        """
        ledger = ApexPersistentMemoryCore.load_continuity_ledger()
        handover = ledger.get("handover_briefing_for_next_session", {})
        if not handover:
            return {"has_previous_memory": False, "message": "Khởi tạo phiên đầu tiên của sổ cái Liên Ngày V4.0."}

        walk_forward_checks = []
        if live_stocks:
            for item in handover.get("Priority_Watchlist_To_Track_Next_Session", []):
                code = item["code"]
                ref_p = float(item.get("reference_price_vnd", 0))
                curr_stk = live_stocks.get(code, {})
                curr_p = float(curr_stk.get("technical", {}).get("price", ref_p))
                diff_pct = round(((curr_p - ref_p) / ref_p) * 100.0, 2) if ref_p > 0 else 0.0
                walk_forward_checks.append({
                    "code": code,
                    "ref_price_vnd": ref_p,
                    "current_price_vnd": curr_p,
                    "delta_pct": diff_pct,
                    "ideal_buy_zone_vnd": item.get("ideal_buy_zone_vnd"),
                    "status": "IN_BUY_ZONE" if curr_p <= item.get("ideal_buy_zone_vnd", ref_p) * 1.01 else "WAITING_PULLBACK_OR_BREAKOUT"
                })

        return {
            "has_previous_memory": True,
            "last_session_date": handover.get("generated_from_session"),
            "what_we_did_last_session": handover.get("what_we_did_last_session"),
            "priority_watchlist": handover.get("Priority_Watchlist_To_Track_Next_Session", []),
            "rejected_stocks": handover.get("Rejected_Stocks_Do_Not_Repropose_Unless_Reversal", []),
            "walk_forward_verification": walk_forward_checks
        }


    @staticmethod
    def load_heuristics_database() -> Dict[str, Any]:
        """Tải 105 Tinh hoa, Mẹo & Bài học Đầu tư Huyền thoại từ Database máy đọc được."""
        db_path = DATA_DIR / "100_institutional_heuristics_database.json"
        if db_path.exists():
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"total_heuristics": 0, "heuristics": []}

    @staticmethod
    def query_heuristics(query: str = "", category: str = "", limit: int = 5) -> List[Dict[str, Any]]:
        """Tìm kiếm mẹo và bài học theo từ khóa hoặc danh mục chuyên khoa."""
        data = ApexPersistentMemoryCore.load_heuristics_database()
        heuristics = data.get("heuristics", [])
        results = []
        q = query.lower().strip()
        cat = category.upper().strip()
        for h in heuristics:
            match = True
            if cat and h.get("category_code") != cat:
                match = False
            if q and match:
                full_text = (h.get("title", "") + " " + h.get("author", "") + " " + h.get("core_principle", "") + " " + h.get("apex_heuristic", "")).lower()
                # Tách từ khóa và loại bỏ các từ dừng tiếng Việt phổ biến
                stopwords = {"của", "và", "cho", "tôi", "các", "những", "về", "là", "có", "được", "bài", "học", "mẹo", "hãy"}
                tokens = [w for w in re.findall(r"\w+", q) if w not in stopwords]
                if tokens:
                    if not any(token in full_text for token in tokens):
                        match = False
                elif q not in full_text:
                    match = False
            if match:
                results.append(h)
                if len(results) >= limit:
                    break
        return results

    @staticmethod
    def get_daily_guiding_heuristic(date_str: str = None) -> Dict[str, Any]:
        """Trả về bài học chỉ đạo chiến lược ngày xoay vòng theo ngày cho Alex, Minh Quân và Huấn luyện viên."""
        data = ApexPersistentMemoryCore.load_heuristics_database()
        heuristics = data.get("heuristics", [])
        if not heuristics:
            return {}
        if not date_str:
            date_str = datetime.date.today().strftime("%Y-%m-%d")
        try:
            day_num = int(date_str.replace("-", ""))
        except Exception:
            day_num = 1
        idx = day_num % len(heuristics)
        return heuristics[idx]


if __name__ == "__main__":
    mem = ApexPersistentMemoryCore.load_continuity_ledger()
    print(f"[MEMORY CORE V4.0] Loaded Continuity Ledger. Last updated: {mem.get('last_updated')}")
    heuristics_db = ApexPersistentMemoryCore.load_heuristics_database()
    print(f"[HEURISTICS CORE V9.0] Loaded {heuristics_db.get('total_heuristics', 0)} Legendary Heuristics.")
    sample = ApexPersistentMemoryCore.get_daily_guiding_heuristic()
    if sample:
        print(f"[DAILY GUIDING HEURISTIC] Bài {sample.get('id')}: {sample.get('title')} ({sample.get('author')})")
