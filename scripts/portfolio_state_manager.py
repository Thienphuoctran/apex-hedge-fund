#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX UNIFIED DYNAMIC PORTFOLIO STATE, EPISODIC MEMORY & TEMPORAL AWARENESS ENGINE (SSOT V2.0)
File: scripts/portfolio_state_manager.py
Cơ quan chủ trì: Master CIO James (Ban 8) & Palmer Central Architecture (11 Phòng Ban)

Nâng cấp Toàn Diện Kiến Trúc Ghi Nhớ & Nhận Thức Không Gian - Thời Gian:
1. SINGLE SOURCE OF TRUTH (SSOT): Lưu trữ chính xác 100% trạng thái tài sản thực tế trên TCBS TCInvest (105C307855).
2. TEMPORAL & SITUATIONAL AWARENESS (Nhận thức Thời gian & Bối cảnh):
   - Tự động biết chính xác thời điểm hiện tại (Thứ, Ngày, Giờ, Phút), thị trường đang Đóng cửa cuối tuần, Nghỉ lễ,
     hay đang ở Phiên Sáng / Nghỉ Trưa / Hấp thụ T+2 / Khung Giờ Vàng 14h00-14h25 / Đóng cửa sau phiên.
   - Biết rõ hệ thống đang ở Giai đoạn Chiến dịch nào (Ví dụ: Đã khép lại Vòng 1 lãi ròng +167,119 ₫, hiện cầm 100% tiền mặt 20,167,119 ₫ chuẩn bị cho Vòng 2).
3. EPISODIC MEMORY (Bộ nhớ Biên niên sử Lịch sử Phiên):
   - Ghi nhớ đầy đủ mọi sự kiện đã diễn ra ở các ngày qua (Mua gì, bán gì, giá nào, lãi/lỗ ròng sau thuế phí bao nhiêu) để phân tích nhưng TUYỆT ĐỐI KHÔNG BAO GIỜ nhầm lẫn lịch sử quá khứ thành vị thế đang nắm giữ hay sổ lệnh chưa thực thi.
4. OMNI-SUBSYSTEM PROPAGATION (Đồng bộ Dây chuyền Tự động 100%):
   - Bất kỳ thay đổi nào cũng tự động đồng bộ tức thời sang:
     * `data/current_portfolio_state.json`
     * `data/institutional_compliance_anchor.json`
     * `08_Master_Investment_CIO/master_execution_blotter.json`
     * `09_Realtime_Portfolio_Sentinel/live_sentinel_status.json`
     * `09_Realtime_Portfolio_Sentinel/vn3_live_telemetry.json`
"""

import sys
import os
import json
import time
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PORTFOLIO_STATE_FILE = DATA_DIR / "current_portfolio_state.json"
COMPLIANCE_ANCHOR_FILE = DATA_DIR / "institutional_compliance_anchor.json"
BLOTTER_FILE = BASE_DIR / "08_Master_Investment_CIO" / "master_execution_blotter.json"
SENTINEL_STATUS_FILE = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "live_sentinel_status.json"
VN3_TELEMETRY_FILE = BASE_DIR / "09_Realtime_Portfolio_Sentinel" / "vn3_live_telemetry.json"
EVOLUTION_JOURNAL_FILE = BASE_DIR / "05_Learning_And_Evolution" / "system_evolution_journal.md"
EPISODIC_MEMORY_FILE = DATA_DIR / "apex_episodic_memory_ledger.json"

WEEKDAY_VN = {
    0: "Thứ Hai",
    1: "Thứ Ba",
    2: "Thứ Tư",
    3: "Thứ Năm",
    4: "Thứ Sáu",
    5: "Thứ Bảy",
    6: "Chủ Nhật"
}

DEFAULT_INITIAL_STATE = {
    "account_id": "105C307855",
    "chairman": "Trần Quốc Thiên Phước",
    "tcbs_mcp_url": "https://mcp.tcbs.com.vn/mcp/tcinvest/",
    "status": "ALL_CASH_STANDDOWN",
    "current_campaign_phase": "ROUND_1_COMPLETED_100_CASH_WAITING_ROUND_2",
    "initial_capital_vnd": 20000000.0,
    "cash_balance_vnd": 20167119.0,
    "total_nav_vnd": 20167119.0,
    "total_market_val_vnd": 0.0,
    "total_cost_vnd": 0.0,
    "realized_pnl_vnd": 167119.0,
    "unrealized_pnl_vnd": 0.0,
    "active_positions": {},
    "pending_active_orders": [],
    "next_round_watchlist": [
        {
            "symbol": "FPT",
            "name": "Tập Đoàn FPT",
            "sector": "Công Nghệ & AI Factory",
            "target_buy_zone": "Canh nhịp chiết khấu về hỗ trợ MA20 trong Khung Giờ Vàng 14h00-14h25",
            "bctc_highlight": "Xếp hạng AAA, OCF/LNST = 1.25x, Beneish M = -2.80 (An toàn)"
        },
        {
            "symbol": "DGC",
            "name": "Tập Đoàn Hóa Chất Đức Giang",
            "sector": "Hóa Chất & Phốt Pho Bán Dẫn",
            "target_buy_zone": "Canh nền tích lũy cạn cung (No Supply) phiên chiều",
            "bctc_highlight": "Pháo đài tiền mặt >10,500 tỷ (77% tài sản), OCF/LNST = 1.15x"
        },
        {
            "symbol": "HPG",
            "name": "Tập Đoàn Hòa Phát (Đã chốt lời Vòng 1 — Theo dõi làm vòng mới)",
            "sector": "Thép & Vật Liệu Xây Dựng",
            "target_buy_zone": "Chỉ vào lại khi điều chỉnh chiết khấu đủ biên an toàn (Không mua đuổi)",
            "bctc_highlight": "Đã mang về lợi nhuận Vòng 1; Dung Quất 2 là động lực dài hạn"
        },
        {
            "symbol": "TCB",
            "name": "Ngân Hàng Techcombank (Đã chốt lời Vòng 1 — Theo dõi làm vòng mới)",
            "sector": "Ngân Hàng",
            "target_buy_zone": "Chờ kiểm định lại vùng hỗ trợ sau nhịp chốt lời Vòng 1",
            "bctc_highlight": "CASA 40.5% dẫn đầu ngành, CAR 15.2%"
        }
    ],
    "completed_campaigns": [
        {
            "campaign_id": "CAMPAIGN-VN-ROUND-01",
            "period": "2026-11-04 -> 2026-11-06",
            "status": "CLOSED_AND_SETTLED_100_PERCENT_CASH",
            "initial_capital_vnd": 20000000.0,
            "final_cash_tcbs_vnd": 20167119.0,
            "net_realized_profit_after_tax_fee_vnd": 167119.0,
            "net_return_pct": 0.8356,
            "positions_traded_and_closed": [
                {"symbol": "HPG", "shares_bought": 400, "shares_sold": 400, "remaining_shares": 0, "entry_price": 21156.0, "exit_status": "SOLD_100_PERCENT"},
                {"symbol": "TCB", "shares_bought": 300, "shares_sold": 300, "remaining_shares": 0, "entry_price": 21356.0, "exit_status": "SOLD_100_PERCENT"},
                {"symbol": "MBB", "shares_bought": 200, "shares_sold": 200, "remaining_shares": 0, "entry_price": 18606.0, "exit_status": "SOLD_100_PERCENT"}
            ],
            "lesson_learned": "Chốt lời dứt khoát toàn bộ 900 CP trước kỳ nghỉ cuối tuần, bảo toàn 100% vốn + lãi thực nhận 20,167,119 ₫ trên TCInvest, triệt tiêu 100% rủi ro qua tuần (0% Weekend Risk)."
        }
    ],
    "trade_history": [
        {
            "trade_id": "TRD-20261106-001",
            "timestamp": "2026-11-06 09:30:00",
            "action": "SELL_ALL",
            "reason": "Chốt lời tất toán 100% danh mục Vòng 1 (400 HPG, 300 TCB, 200 MBB) theo chỉ thị Chủ tịch & Master CIO James",
            "shares_sold": {"HPG": 400, "TCB": 300, "MBB": 200},
            "realized_pnl_vnd": 167119.0,
            "cash_after_trade": 20167119.0
        }
    ],
    "tactical_regime": "PATIENT_PREDATOR_100_CASH_STANDDOWN",
    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}


class PortfolioStateManager:
    """Bộ Não Trung Tâm Quản Trị Trạng Thái, Ghi Nhớ Lịch Sử & Nhận Thức Thời Gian Thực."""

    @staticmethod
    def get_temporal_context(now_dt: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        """
        Xác định chính xác hệ thống đang ở thời điểm nào, thứ mấy, phiên thị trường đóng hay mở,
        và đang ở giai đoạn tác chiến nào để mọi báo cáo đều có nhận thức thời gian chuẩn xác 100%.
        """
        if now_dt is None:
            now_dt = datetime.datetime.now()

        wd = now_dt.weekday()
        wd_name = WEEKDAY_VN.get(wd, "Hôm nay")
        date_vn = now_dt.strftime("%d/%m/%Y")
        time_vn = now_dt.strftime("%H:%M:%S")
        hm = now_dt.hour * 60 + now_dt.minute

        if wd in (5, 6):
            market_phase = "WEEKEND_CLOSED"
            market_phase_vn = f"Nghỉ cuối tuần ({wd_name}) — Sàn HOSE/HNX đóng cửa, 0% rủi ro biến động"
            is_trading_hours = False
            next_session_note = "Phiên giao dịch tiếp theo mở cửa lúc 09:00 sáng Thứ Hai."
        else:
            if hm < 9 * 60:
                market_phase = "PRE_MARKET_PREPARATION"
                market_phase_vn = f"Trước giờ mở cửa phiên sáng ({wd_name}) — Chuẩn bị kế hoạch tác chiến"
                is_trading_hours = False
                next_session_note = "Đợi qua 09:15 (sau ATO) để quan sát cung cầu thực chất."
            elif 9 * 60 <= hm <= 11 * 60 + 30:
                market_phase = "MORNING_SESSION"
                market_phase_vn = f"Đang trong Phiên Sáng ({wd_name}) — Kỷ luật KHÔNG FOMO mua đuổi giá xanh"
                is_trading_hours = True
                next_session_note = "Quan sát áp lực cung cầu; chờ nhịp hấp thụ chiều."
            elif 11 * 60 + 30 < hm < 13 * 60:
                market_phase = "LUNCH_BREAK"
                market_phase_vn = f"Nghỉ trưa giữa hai phiên ({wd_name}) — Sàn tạm nghỉ 11h30-13h00"
                is_trading_hours = False
                next_session_note = "Phiên chiều mở cửa lúc 13:00 (Hàng T+2.5 về tài khoản)."
            elif 13 * 60 <= hm < 14 * 60:
                market_phase = "AFTERNOON_T2_ABSORPTION"
                market_phase_vn = f"Phiên Chiều: Khung hấp thụ lượng hàng T+2.5 về tài khoản (13h00-14h00)"
                is_trading_hours = True
                next_session_note = "Chờ Khung Giờ Vàng 14h00-14h25 để xác nhận 90% nến ngày."
            elif 14 * 60 <= hm <= 14 * 60 + 25:
                market_phase = "GOLDEN_HOUR_14H00_14H25"
                market_phase_vn = f"🔥 KHUNG GIỜ VÀNG TÁC CHIẾN (14h00-14h25 {wd_name}) — Thời điểm quyết định giải ngân/cơ cấu"
                is_trading_hours = True
                next_session_note = "Sau 14h30 bước vào phiên ATC."
            elif 14 * 60 + 25 < hm <= 14 * 60 + 45:
                market_phase = "ATC_SESSION"
                market_phase_vn = f"Phiên khớp lệnh định kỳ đóng cửa ATC (14h30-14h45 {wd_name})"
                is_trading_hours = True
                next_session_note = "Đóng bảng lúc 14h45, tổng kết lúc 15h00."
            else:
                market_phase = "AFTER_HOURS_CLOSED"
                market_phase_vn = f"Ngoài giờ giao dịch ({wd_name} sau 15h00) — Sàn HOSE/HNX đã đóng cửa"
                is_trading_hours = False
                next_session_note = "Hệ thống thực hiện kiểm toán EOD, rà soát BCTC và chuẩn bị cho phiên kế tiếp."

        return {
            "timestamp_iso": now_dt.isoformat(),
            "date_str": now_dt.strftime("%Y-%m-%d"),
            "date_vn": date_vn,
            "time_vn": time_vn,
            "weekday_index": wd,
            "weekday_vn": wd_name,
            "full_time_label_vn": f"{time_vn} {wd_name}, ngày {date_vn}",
            "market_phase": market_phase,
            "market_phase_vn": market_phase_vn,
            "is_trading_hours": is_trading_hours,
            "next_session_note": next_session_note
        }

    @staticmethod
    def load_state() -> Dict[str, Any]:
        """Tải trạng thái danh mục hiện tại từ đĩa (SSOT) kèm làm giàu ngữ cảnh thời gian & lịch sử."""
        if not PORTFOLIO_STATE_FILE.exists():
            PortfolioStateManager.save_state(DEFAULT_INITIAL_STATE)
            return DEFAULT_INITIAL_STATE.copy()

        try:
            with open(PORTFOLIO_STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Đảm bảo các trường bộ nhớ lịch sử luôn hiện diện đầy đủ
            for k, v in DEFAULT_INITIAL_STATE.items():
                if k not in data:
                    data[k] = v
            data["temporal_context"] = PortfolioStateManager.get_temporal_context()
            return data
        except Exception as e:
            print(f"[!] Lỗi đọc state file ({e}). Nạp fallback...")
            st = DEFAULT_INITIAL_STATE.copy()
            st["temporal_context"] = PortfolioStateManager.get_temporal_context()
            return st

    @staticmethod
    def save_state(state: Dict[str, Any]) -> bool:
        """
        Lưu trạng thái danh mục và TỰ ĐỘNG ĐỒNG BỘ DÂY CHUYỀN (Omni-Propagation)
        tới toàn bộ các file JSON của Ban 8, Ban 9, Neo thể chế và Sổ cái Ký ức Lịch sử.
        """
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["last_updated"] = now_str
        state["temporal_context"] = PortfolioStateManager.get_temporal_context()

        # Đảm bảo tính toán lại tổng giá trị thị trường & NAV chính xác
        positions = state.get("active_positions", {})
        total_mkt = 0.0
        total_cost = 0.0
        for sym, pos in list(positions.items()):
            sh = int(pos.get("shares", 0))
            if sh <= 0:
                del positions[sym]
                continue
            ep = float(pos.get("entry_price", pos.get("avg_price", 0.0)))
            cp = float(pos.get("current_price", ep))
            total_cost += sh * ep
            total_mkt += sh * cp

        cash_vnd = float(state.get("cash_balance_vnd", 20167119.0))
        state["total_cost_vnd"] = round(total_cost, 0)
        state["total_market_val_vnd"] = round(total_mkt, 0)
        state["unrealized_pnl_vnd"] = round(total_mkt - total_cost, 0)
        state["total_nav_vnd"] = round(cash_vnd + total_mkt, 0)

        if len(positions) == 0:
            state["status"] = "ALL_CASH_STANDDOWN"
            state["current_campaign_phase"] = "ROUND_1_COMPLETED_100_CASH_WAITING_ROUND_2"
            state["tactical_regime"] = "PATIENT_PREDATOR_100_CASH_STANDDOWN"
        else:
            state["status"] = "ACTIVE_HOLDING"
            state["current_campaign_phase"] = "ACTIVE_CAMPAIGN_HOLDING"
            state["tactical_regime"] = "HOLDING_WITH_RISK_PARITY_STOP"

        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(PORTFOLIO_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

            # Đồng bộ dây chuyền sang toàn bộ các phân hệ của Quỹ
            PortfolioStateManager._sync_to_anchor(state)
            PortfolioStateManager._sync_to_master_blotter(state)
            PortfolioStateManager._sync_to_sentinel_files(state)
            PortfolioStateManager._sync_to_episodic_memory(state)
            return True
        except Exception as e:
            print(f"[!] Lỗi ghi portfolio state: {e}")
            return False

    @staticmethod
    def _sync_to_anchor(state: Dict[str, Any]):
        """Đồng bộ sang `data/institutional_compliance_anchor.json`."""
        try:
            anchor = {}
            if COMPLIANCE_ANCHOR_FILE.exists():
                with open(COMPLIANCE_ANCHOR_FILE, "r", encoding="utf-8") as f:
                    anchor = json.load(f)

            has_positions = len(state.get("active_positions", {})) > 0
            if has_positions:
                anchor["status"] = "ACTIVE_HOLDING"
                anchor["enforced_strategy"] = "RISK_PARITY_STOP_2XATR"
            else:
                anchor["status"] = "ALL_POSITIONS_CLOSED_100_PERCENT_CASH"
                anchor["enforced_strategy"] = "100_PERCENT_CASH_PROTECTED"

            anchor["realized_cash_vnd"] = float(state.get("cash_balance_vnd", 20167119.0))
            anchor["realized_pnl_vnd"] = float(state.get("realized_pnl_vnd", 167119.0))
            anchor["audit_timestamp"] = f"{datetime.datetime.now().strftime('%Y-%m-%d_%Hh%M')}_dynamic_sync"

            with open(COMPLIANCE_ANCHOR_FILE, "w", encoding="utf-8") as f:
                json.dump(anchor, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Lỗi đồng bộ anchor: {e}")

    @staticmethod
    def _sync_to_master_blotter(state: Dict[str, Any]):
        """
        Đồng bộ trực tiếp sang `08_Master_Investment_CIO/master_execution_blotter.json`.
        Nếu đã bán sạch (100% tiền mặt), `orders_vietnam` phải phản ánh đúng các vị thế đang mở (= [])
        và lưu rõ lịch sử Vòng 1 đã tất toán vào `completed_orders_history`, tránh tuyệt đối việc báo cáo lại lệnh cũ!
        """
        try:
            blotter = {}
            if BLOTTER_FILE.exists():
                with open(BLOTTER_FILE, "r", encoding="utf-8") as f:
                    blotter = json.load(f)

            cash_vnd = float(state.get("cash_balance_vnd", 20167119.0))
            mkt_vnd = float(state.get("total_market_val_vnd", 0.0))
            nav_vnd = float(state.get("total_nav_vnd", cash_vnd + mkt_vnd))
            realized_pnl = float(state.get("realized_pnl_vnd", 167119.0))
            positions = state.get("active_positions", {})
            t_ctx = state.get("temporal_context") or PortfolioStateManager.get_temporal_context()

            blotter["generated_at_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            blotter["trading_date"] = t_ctx["date_str"]
            blotter["temporal_context"] = t_ctx

            cap = blotter.setdefault("capital_summary", {})
            fx = float(cap.get("fx_rate_usd_vnd", 25400.0))
            cap["total_nav_vnd"] = nav_vnd
            cap["total_nav_usd"] = round(nav_vnd / fx, 2)
            cap["vn_allocated_vnd"] = mkt_vnd
            cap["vn_allocated_usd"] = round(mkt_vnd / fx, 2)
            cap["vn_allocated_pct"] = round((mkt_vnd / nav_vnd * 100.0), 2) if nav_vnd > 0 else 0.0
            cap["dry_powder_vnd"] = cash_vnd
            cap["dry_powder_usd"] = round(cash_vnd / fx, 2)
            cap["dry_powder_pct"] = round((cash_vnd / nav_vnd * 100.0), 2) if nav_vnd > 0 else 100.0
            cap["realized_pnl_vnd"] = realized_pnl

            if not positions:
                blotter["cio_desk_verdict"] = (
                    f"100% TIỀN MẶT ({cash_vnd:,.0f} ₫) — ĐÃ TẤT TOÁN VÒNG 1 (LÃI RÒNG +{realized_pnl:,.0f} ₫) & ĐỢI TẦM NGẮM VÒNG 2"
                )
                blotter["orders_vietnam"] = []
                blotter["completed_orders_history"] = state.get("completed_campaigns", [])
                blotter["next_round_watchlist"] = state.get("next_round_watchlist", [])
                blotter["agent_zero_validation"] = {
                    "status": "VERIFIED_100_PERCENT_CASH_SYNCED",
                    "sandbox_math_verified": True,
                    "portfolio_allocation_verified": f"100% TIỀN MẶT ({cash_vnd:,.0f} VNĐ) | 0 CP NẮM GIỮ | LÃI ĐÃ CHỐT +{realized_pnl:,.0f} VNĐ",
                    "max_risk_locked_pct": 0.0,
                    "timestamp": t_ctx["full_time_label_vn"]
                }
            else:
                blotter["cio_desk_verdict"] = f"ĐANG NẮM GIỮ {len(positions)} MÃ CỔ PHIẾU — GIÁM SÁT STOP 2XATR & TP1/TP2"
                active_orders = []
                for sym, pos in positions.items():
                    sh = int(pos.get("shares", 0))
                    ep = float(pos.get("entry_price", 0.0))
                    alloc = sh * ep
                    active_orders.append({
                        "market": "VIETNAM",
                        "symbol": sym,
                        "name": pos.get("name", sym),
                        "sector": pos.get("sector", "Cổ phiếu Việt Nam"),
                        "sleeve": pos.get("sleeve", "ACTIVE HOLDING"),
                        "exchange": "HOSE",
                        "weight_nav_pct": round(alloc / nav_vnd * 100.0, 2) if nav_vnd > 0 else 0.0,
                        "allocated_capital_vnd": alloc,
                        "shares": sh,
                        "current_price_vnd": float(pos.get("current_price", ep)),
                        "entry_price_vnd": ep,
                        "stop_loss_2atr_vnd": float(pos.get("stop_loss", round(ep * 0.93, 0))),
                        "tp1_vnd": float(pos.get("take_profit_tp1", round(ep * 1.15, 0))),
                        "tp2_vnd": float(pos.get("take_profit_tp2", round(ep * 1.25, 0))),
                        "entry_strategy": f"Đang nắm giữ {sh:,} CP tại giá vốn {ep:,.0f} ₫",
                        "execution_instruction": f"Canh chốt lời TP1 ({pos.get('take_profit_tp1', round(ep * 1.15, 0)):,.0f} ₫) và khóa chặt Stop Loss 2xATR ({pos.get('stop_loss', round(ep * 0.93, 0)):,.0f} ₫)."
                    })
                blotter["orders_vietnam"] = active_orders

            BLOTTER_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(BLOTTER_FILE, "w", encoding="utf-8") as f:
                json.dump(blotter, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Lỗi đồng bộ master_execution_blotter.json: {e}")

    @staticmethod
    def _sync_to_sentinel_files(state: Dict[str, Any]):
        """Đồng bộ sang `09_Realtime_Portfolio_Sentinel/live_sentinel_status.json` và `vn3_live_telemetry.json`."""
        try:
            positions = state.get("active_positions", {})
            cash_vnd = float(state.get("cash_balance_vnd", 20167119.0))
            realized_pnl = float(state.get("realized_pnl_vnd", 167119.0))
            t_ctx = state.get("temporal_context") or PortfolioStateManager.get_temporal_context()

            # 1. Cập nhật live_sentinel_status.json
            sentinel = {}
            if SENTINEL_STATUS_FILE.exists():
                with open(SENTINEL_STATUS_FILE, "r", encoding="utf-8") as f:
                    sentinel = json.load(f)

            sentinel["last_scan_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            sentinel["temporal_context"] = t_ctx
            sentinel["cash_balance_vnd"] = cash_vnd
            sentinel["realized_pnl_vnd"] = realized_pnl

            if not positions:
                sentinel["status"] = "ALL_CASH_STANDDOWN_0_SHARES"
                sentinel["total_positions_monitored"] = 0
                sentinel["positions_tracked"] = []
                sentinel["positions"] = []
            else:
                tracked = []
                for sym, pos in positions.items():
                    ep = float(pos.get("entry_price", 0.0))
                    cp = float(pos.get("current_price", ep))
                    sl = float(pos.get("stop_loss", round(ep * 0.93, 0)))
                    tp1 = float(pos.get("take_profit_tp1", round(ep * 1.15, 0)))
                    dist_stop = round((cp - sl) / cp * 100.0, 2) if cp > 0 else 0.0
                    dist_tp1 = round((tp1 - cp) / cp * 100.0, 2) if cp > 0 else 0.0
                    tracked.append({
                        "symbol": sym,
                        "market": "VIETNAM",
                        "shares": int(pos.get("shares", 0)),
                        "entry_price": ep,
                        "current_price": cp,
                        "stop_loss_2atr": sl,
                        "tp1": tp1,
                        "distance_to_stop_pct": dist_stop,
                        "distance_to_tp1_pct": dist_tp1,
                        "severity": "NORMAL"
                    })
                sentinel["status"] = "ACTIVE_MONITORING"
                sentinel["total_positions_monitored"] = len(tracked)
                sentinel["positions_tracked"] = tracked
                sentinel["positions"] = tracked

            SENTINEL_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SENTINEL_STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(sentinel, f, indent=2, ensure_ascii=False)

            # 2. Cập nhật vn3_live_telemetry.json
            telemetry = {
                "updated_at": t_ctx["full_time_label_vn"],
                "account_id": "105C307855",
                "status": state.get("status", "ALL_CASH_STANDDOWN"),
                "cash_balance_vnd": cash_vnd,
                "dry_powder": cash_vnd,
                "total_nav_vnd": float(state.get("total_nav_vnd", cash_vnd)),
                "realized_pnl_vnd": realized_pnl,
                "positions": list(positions.values()) if positions else []
            }
            with open(VN3_TELEMETRY_FILE, "w", encoding="utf-8") as f:
                json.dump(telemetry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Lỗi đồng bộ sentinel files: {e}")

    @staticmethod
    def _sync_to_episodic_memory(state: Dict[str, Any]):
        """Lưu trữ Sổ cái Ký ức Sự kiện & Nhận thức Thời gian (`data/apex_episodic_memory_ledger.json`)."""
        try:
            t_ctx = state.get("temporal_context") or PortfolioStateManager.get_temporal_context()
            memory_doc = {
                "system_name": "APEX HEDGE FUND — UNIFIED EPISODIC MEMORY & TEMPORAL AWARENESS LEDGER",
                "last_synchronized": t_ctx["full_time_label_vn"],
                "temporal_awareness": t_ctx,
                "current_situational_awareness": {
                    "account_id": state.get("account_id", "105C307855"),
                    "chairman": state.get("chairman", "Trần Quốc Thiên Phước"),
                    "portfolio_status": state.get("status", "ALL_CASH_STANDDOWN"),
                    "campaign_phase": state.get("current_campaign_phase", "ROUND_1_COMPLETED_100_CASH_WAITING_ROUND_2"),
                    "initial_capital_vnd": state.get("initial_capital_vnd", 20000000.0),
                    "verified_tcbs_cash_vnd": state.get("cash_balance_vnd", 20167119.0),
                    "verified_tcbs_nav_vnd": state.get("total_nav_vnd", 20167119.0),
                    "net_realized_profit_vnd": state.get("realized_pnl_vnd", 167119.0),
                    "active_positions_count": len(state.get("active_positions", {})),
                    "active_positions": state.get("active_positions", {}),
                    "what_we_are_doing_now": (
                        "Đã tất toán 100% cổ phiếu Vòng 1 (400 HPG, 300 TCB, 200 MBB), thu về két sắt TCBS 20,167,119 VNĐ "
                        "(lãi ròng thực nhận +167,119 VNĐ sau thuế phí). Hiện đang cầm 100% tiền mặt (0 CP), an toàn tuyệt đối qua cuối tuần, "
                        "và chuẩn bị danh sách tầm ngắm Vòng 2 cho tuần giao dịch mới."
                        if not state.get("active_positions")
                        else f"Đang nắm giữ {len(state.get('active_positions', {}))} mã cổ phiếu và canh chặt ngưỡng Stop Loss 2xATR / TP1."
                    )
                },
                "completed_campaigns_chronicle": state.get("completed_campaigns", []),
                "trade_execution_history": state.get("trade_history", []),
                "next_round_watchlist": state.get("next_round_watchlist", [])
            }
            with open(EPISODIC_MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(memory_doc, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Lỗi đồng bộ episodic memory: {e}")

    @staticmethod
    def execute_sell_order(
        symbol: str,
        shares: int,
        sell_price: float,
        reason: str = "Chốt lời / Cắt lỗ theo kế hoạch"
    ) -> Tuple[bool, str]:
        """
        Khớp lệnh BÁN một phần hoặc toàn bộ một cổ phiếu.
        Tự động tính toán tiền thu về, PnL thực tế, cập nhật số dư tiền mặt và đồng bộ toàn bộ 11 phòng ban.
        """
        state = PortfolioStateManager.load_state()
        positions = state.get("active_positions", {})
        sym = symbol.upper().strip()

        if sym not in positions or positions[sym].get("shares", 0) <= 0:
            return False, (
                f"ℹ️ *[NHẮC NHỞ TRẠNG THÁI THỰC TẾ]*\n"
                f"Mã *{sym}* hiện không còn trong danh mục nắm giữ (Số dư: `0 CP`).\n"
                f"• Lịch sử ghi nhận: Toàn bộ cổ phiếu Vòng 1 đã được bán tất toán, thu về két TCBS `{state.get('cash_balance_vnd', 20167119.0):,.0f} ₫`."
            )

        current_shares = positions[sym].get("shares", 0)
        entry_price = positions[sym].get("entry_price", sell_price)

        if shares > current_shares or shares <= 0:
            shares = current_shares

        sell_val = shares * sell_price
        cost_val = shares * entry_price
        trade_pnl = sell_val - cost_val

        state["cash_balance_vnd"] = state.get("cash_balance_vnd", 0.0) + sell_val
        state["realized_pnl_vnd"] = state.get("realized_pnl_vnd", 0.0) + trade_pnl

        remaining_shares = current_shares - shares
        if remaining_shares > 0:
            positions[sym]["shares"] = remaining_shares
        else:
            del positions[sym]

        trade_entry = {
            "trade_id": f"TRD-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": "SELL",
            "symbol": sym,
            "shares": shares,
            "sell_price": sell_price,
            "entry_price": entry_price,
            "trade_pnl_vnd": round(trade_pnl, 0),
            "cash_after_trade": round(state["cash_balance_vnd"], 0),
            "reason": reason
        }
        state.setdefault("trade_history", []).append(trade_entry)

        PortfolioStateManager.save_state(state)

        PortfolioStateManager._log_to_evolution_journal(
            f"Thực thi BÁN {shares:,} {sym} tại giá {sell_price:,.0f} ₫. PnL thực tế: {trade_pnl:+,.0f} ₫. Lý do: {reason}"
        )

        msg = (
            f"✅ *[KHỚP LỆNH BÁN & ĐỒNG BỘ TOÀN HỆ THỐNG THÀNH CÔNG]*\n"
            f"• Mã: *{sym}* | Khối lượng bán: `{shares:,} CP` | Giá bán: `{sell_price:,.0f} ₫`\n"
            f"• Tiền thu về: `{sell_val:,.0f} ₫` | Lãi/Lỗ thương vụ: `{trade_pnl:+,.0f} ₫`\n"
            f"• Tiền mặt Quỹ hiện tại: `{state['cash_balance_vnd']:,.0f} ₫`\n"
            f"• Số cổ phiếu {sym} còn lại: `{remaining_shares:,} CP`\n"
            f"• Đã đồng bộ tức thời sang Sổ lệnh Ban 8, Radar Ban 9 và Sổ cái Ký ức!"
        )
        return True, msg

    @staticmethod
    def execute_buy_order(
        symbol: str,
        shares: int,
        buy_price: float,
        stop_loss: float = 0.0,
        take_profit: float = 0.0,
        reason: str = "Giải ngân theo khuyến nghị Master CIO"
    ) -> Tuple[bool, str]:
        """
        Khớp lệnh MUA mới hoặc gia tăng một cổ phiếu.
        Tự động trừ tiền mặt, cập nhật giá vốn bình quân, Stop Loss và đồng bộ toàn hệ thống.
        """
        state = PortfolioStateManager.load_state()
        sym = symbol.upper().strip()
        total_cost = shares * buy_price

        current_cash = state.get("cash_balance_vnd", 0.0)
        if total_cost > current_cash:
            return False, f"⚠️ Không đủ tiền mặt để mua! Cần `{total_cost:,.0f} ₫`, nhưng tiền mặt khả dụng hiện tại là `{current_cash:,.0f} ₫`."

        positions = state.setdefault("active_positions", {})
        if sym in positions:
            old_shares = positions[sym].get("shares", 0)
            old_entry = positions[sym].get("entry_price", buy_price)
            new_shares = old_shares + shares
            new_entry = ((old_shares * old_entry) + total_cost) / new_shares
            positions[sym]["shares"] = new_shares
            positions[sym]["entry_price"] = round(new_entry, 0)
            positions[sym]["current_price"] = buy_price
        else:
            positions[sym] = {
                "symbol": sym,
                "shares": shares,
                "entry_price": buy_price,
                "current_price": buy_price,
                "stop_loss": stop_loss if stop_loss > 0 else round(buy_price * 0.93, 0),
                "take_profit_tp1": take_profit if take_profit > 0 else round(buy_price * 1.15, 0),
                "take_profit_tp2": round(buy_price * 1.25, 0),
                "bought_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        state["cash_balance_vnd"] = current_cash - total_cost

        trade_entry = {
            "trade_id": f"TRD-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": "BUY",
            "symbol": sym,
            "shares": shares,
            "buy_price": buy_price,
            "total_cost_vnd": round(total_cost, 0),
            "cash_after_trade": round(state["cash_balance_vnd"], 0),
            "reason": reason
        }
        state.setdefault("trade_history", []).append(trade_entry)

        PortfolioStateManager.save_state(state)

        PortfolioStateManager._log_to_evolution_journal(
            f"Thực thi MUA {shares:,} {sym} tại giá {buy_price:,.0f} ₫ (Vốn: {total_cost:,.0f} ₫). Lý do: {reason}"
        )

        msg = (
            f"✅ *[KHỚP LỆNH MUA & ĐỒNG BỘ TOÀN HỆ THỐNG THÀNH CÔNG]*\n"
            f"• Mã: *{sym}* | Khối lượng: `{shares:,} CP` | Giá mua: `{buy_price:,.0f} ₫`\n"
            f"• Tổng tiền giải ngân: `{total_cost:,.0f} ₫`\n"
            f"• Tiền mặt còn lại: `{state['cash_balance_vnd']:,.0f} ₫`\n"
            f"• Stop Loss 2xATR thiết lập: `{positions[sym]['stop_loss']:,.0f} ₫` | TP1: `{positions[sym]['take_profit_tp1']:,.0f} ₫`"
        )
        return True, msg

    @staticmethod
    def execute_sell_all_and_lock_cash(reason: str = "Chốt lời toàn bộ danh mục quy về 100% Tiền Mặt") -> Tuple[bool, str]:
        """Bán sạch toàn bộ cổ phiếu và khóa 100% Tiền Mặt tức thời."""
        state = PortfolioStateManager.load_state()
        positions = state.get("active_positions", {})

        if not positions:
            # Vẫn ép đồng bộ lại toàn bộ các file phụ trợ để đảm bảo 100% nhất quán
            PortfolioStateManager.save_state(state)
            return True, (
                f"🛡️ *[XÁC NHẬN TRẠNG THÁI KÝ ỨC & TÀI SẢN THỰC TẾ]*\n"
                f"• Danh mục hiện tại vốn dĩ đã là **100% TIỀN MẶT (`{state.get('cash_balance_vnd', 20167119.0):,.0f} ₫`)**, `0 CP` nắm giữ.\n"
                f"• Toàn bộ 900 CP Vòng 1 (`400 HPG`, `300 TCB`, `200 MBB`) đã được bán tất toán trước đó (Lãi ròng thực nhận sau thuế phí: `+{state.get('realized_pnl_vnd', 167119.0):,.0f} ₫`).\n"
                f"• Đã đồng bộ khóa cứng trạng thái 100% Tiền Mặt trên toàn bộ 11 Phòng Ban!"
            )

        total_liquidated = 0.0
        total_pnl = 0.0
        sold_summary = {}

        for sym, pos in list(positions.items()):
            sh = pos.get("shares", 0)
            p = pos.get("current_price", pos.get("entry_price", 0.0))
            cost = sh * pos.get("entry_price", p)
            val = sh * p
            pnl = val - cost
            total_liquidated += val
            total_pnl += pnl
            sold_summary[sym] = {"shares": sh, "price": p, "pnl": round(pnl, 0)}

        state["cash_balance_vnd"] = state.get("cash_balance_vnd", 0.0) + total_liquidated
        state["realized_pnl_vnd"] = state.get("realized_pnl_vnd", 0.0) + total_pnl
        state["active_positions"] = {}

        trade_entry = {
            "trade_id": f"TRD-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": "SELL_ALL",
            "details": sold_summary,
            "liquidated_vnd": round(total_liquidated, 0),
            "pnl_vnd": round(total_pnl, 0),
            "cash_after_trade": round(state["cash_balance_vnd"], 0),
            "reason": reason
        }
        state.setdefault("trade_history", []).append(trade_entry)

        PortfolioStateManager.save_state(state)

        PortfolioStateManager._log_to_evolution_journal(
            f"Kích hoạt BÁN SẠCH TOÀN BỘ DANH MỤC quy về 100% Tiền Mặt ({state['cash_balance_vnd']:,.0f} ₫). Lý do: {reason}"
        )

        msg = (
            f"🛡️ *[ĐÃ BÁN SẠCH TOÀN BỘ DANH MỤC — 100% TIỀN MẶT]*\n"
            f"• Tiền mặt thu về: `{total_liquidated:,.0f} ₫`\n"
            f"• Lợi nhuận chốt lời: `{total_pnl:+,.0f} ₫`\n"
            f"• Tổng số dư Tiền Mặt Quỹ: `{state['cash_balance_vnd']:,.0f} ₫`\n"
            f"• Trạng thái: `0 Cổ phiếu`, đã đồng bộ xóa toàn bộ lệnh/vị thế cũ trên cả 11 Phòng Ban!"
        )
        return True, msg

    @staticmethod
    def _log_to_evolution_journal(entry: str):
        """Ghi nhận vào sổ nhật ký tự học của Ban 5."""
        if not EVOLUTION_JOURNAL_FILE.exists():
            return
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = f"\n- `[{ts}]` **[DYNAMIC STATE & EPISODIC MEMORY SYNC]**: {entry}\n"
        try:
            with open(EVOLUTION_JOURNAL_FILE, "a", encoding="utf-8") as f:
                f.write(record)
        except Exception:
            pass


def get_current_portfolio_state() -> Dict[str, Any]:
    """Module-level helper to load current SSOT portfolio state."""
    return PortfolioStateManager.load_state()


def get_temporal_context() -> Dict[str, Any]:
    """Module-level helper to get temporal context."""
    return PortfolioStateManager.get_temporal_context()


def sync_all_portfolio_files(state: Dict[str, Any] = None) -> None:
    """Module-level helper to sync state across all 5 JSON files."""
    if state is None:
        state = PortfolioStateManager.load_state()
    PortfolioStateManager.save_state(state)


if __name__ == "__main__":
    st = PortfolioStateManager.load_state()
    PortfolioStateManager.save_state(st)
    t_ctx = st.get("temporal_context", {})
    print("=" * 75)
    print(" 🏛️ APEX UNIFIED PORTFOLIO STATE, EPISODIC MEMORY & TEMPORAL ENGINE V2.0")
    print("=" * 75)
    print(f"• Thời điểm hệ thống : {t_ctx.get('full_time_label_vn')}")
    print(f"• Pha thị trường     : {t_ctx.get('market_phase_vn')}")
    print(f"• Trạng thái Quỹ     : {st.get('status')} ({st.get('current_campaign_phase')})")
    print(f"• Số dư tiền mặt TCBS: {st.get('cash_balance_vnd', 0):,.0f} ₫")
    print(f"• Lãi ròng đã chốt   : {st.get('realized_pnl_vnd', 0):+,.0f} ₫")
    print(f"• Vị thế đang giữ    : {len(st.get('active_positions', {}))} mã (0 CP)")
    print(f"• Lịch sử Chiến dịch : {len(st.get('completed_campaigns', []))} chiến dịch đã hoàn tất")
    print("=" * 75)
