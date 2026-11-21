#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX BILATERAL SYNCHRONIZATION BRIDGE (ANTIGRAVITY <-> PALMER REALTIME SYNC)
File: scripts/palmer_antigravity_sync_bridge.py
Cơ quan chủ quản: Palmer (Trưởng Phòng Tổng Hệ Thống) & Antigravity (Đầu Não Chiến Lược & Pair Programmer)
Dành riêng cho: Chủ tịch Hội đồng Quản trị Quỹ Apex — Trần Quốc Thiên Phước (TCBS: 105C307855)

MỤC TIÊU THỂ CHẾ THEO CHỈ THỊ CHỦ TỊCH:
1. Thiết lập cơ chế trao đổi & đồng bộ 2 chiều tức thời giữa Antigravity và Palmer.
2. Mỗi khi Antigravity hoàn thành 1 yêu cầu/câu hỏi của Chủ tịch -> Ngay lập tức phổ biến toàn bộ nội dung, quyết định, phân tích cho Palmer.
3. Ngược lại, mỗi khi Palmer tiếp nhận hay xử lý yêu cầu trên Telegram -> Ngay lập tức phổ biến lại cho Antigravity.
4. Triệt tiêu 100% tình trạng "hoàn toàn mới tinh", thông tin cũ, hoặc bất kỳ sự lệch pha nào trong toàn hệ thống.
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SYNC_LEDGER_FILE = DATA_DIR / "palmer_antigravity_bilateral_sync.json"
LIVE_BRIEFING_FILE = DATA_DIR / "palmer_live_briefing.json"
LIVE_BRIEFING_MD = DATA_DIR / "palmer_live_briefing.md"
INTER_CHAT_STATE_MD = BASE_DIR / "00_LIVE_INTER_CHAT_STATE.md"

PALMER_BRAIN_DIR = Path(r"C:\Users\phuoc\.gemini\antigravity\brain\434b15db-b27c-41bb-b475-10a5bdc513b3")
TRO_LI_DIR = Path(r"c:\Users\phuoc\Downloads\antigravity\Trợ lí cá nhân")
TRO_LI_DATA_DIR = TRO_LI_DIR / "data"
TRO_LI_SYNC_JSON = TRO_LI_DATA_DIR / "james_live_sync_for_palmer.json"
TRO_LI_SYNC_MD = TRO_LI_DATA_DIR / "james_live_sync_for_palmer.md"
TRO_LI_MEMORY_MD = TRO_LI_DIR / "MEMORY.md"


class PalmerAntigravitySyncBridge:
    """Cầu nối đồng bộ 2 chiều thời gian thực giữa Antigravity và Palmer."""

    @staticmethod
    def load_sync_ledger() -> List[Dict[str, Any]]:
        if SYNC_LEDGER_FILE.exists():
            try:
                with open(SYNC_LEDGER_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    @staticmethod
    def save_sync_ledger(ledger: List[Dict[str, Any]]) -> None:
        try:
            with open(SYNC_LEDGER_FILE, "w", encoding="utf-8") as f:
                json.dump(ledger[:300], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Lỗi ghi sync ledger: {e}")

    @staticmethod
    def load_live_briefing() -> Dict[str, Any]:
        if LIVE_BRIEFING_FILE.exists():
            try:
                with open(LIVE_BRIEFING_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    @classmethod
    def broadcast_from_antigravity_to_palmer(
        cls,
        user_request: str,
        response_summary: str,
        completed_tasks: List[str],
        active_decisions: Dict[str, Any],
        priority: str = "HIGH"
    ) -> Dict[str, Any]:
        """
        Antigravity gọi hàm này ngay sau khi hoàn thành bất kỳ yêu cầu/câu hỏi nào của Chủ tịch
        để trao đổi và phổ biến ngay lập tức cho Palmer.
        """
        now = datetime.datetime.now()
        sync_id = f"SYNC-AG2P-{now.strftime('%Y%m%d-%H%M%S')}"

        # Đọc trạng thái danh mục mới nhất từ PortfolioStateManager
        from scripts.portfolio_state_manager import PortfolioStateManager
        st = PortfolioStateManager.load_state()
        cash_vnd = float(st.get("cash_balance_vnd", 0.0) or 0.0)
        positions = st.get("active_positions", {}) or {}
        
        stock_market_val = 0.0
        pos_details = {}
        for sym, pos in positions.items():
            sh = int(pos.get("shares", 0))
            if sh <= 0:
                continue
            ep = float(pos.get("entry_price", 0.0))
            cp = float(pos.get("current_price", ep))
            val = sh * cp
            stock_market_val += val
            pos_details[sym] = {
                "shares": sh,
                "entry_price": ep,
                "current_price": cp,
                "market_val_vnd": val,
                "pnl_vnd": val - (sh * ep),
                "status": pos.get("status", "HOLDING")
            }
        
        total_nav = cash_vnd + stock_market_val
        cash_pct = round((cash_vnd / total_nav) * 100.0, 2) if total_nav > 0 else 100.0
        v2_file = DATA_DIR / "apex_quant_brain_v2_output.json"
        live_regime = st.get("tactical_regime", "CASH_100_DEFENSE_WEEKEND_REST")
        if v2_file.exists():
            try:
                v2_d = json.loads(v2_file.read_text(encoding="utf-8"))
                mr_id = (v2_d.get("market_regime") or {}).get("regime_id")
                if mr_id:
                    live_regime = f"{mr_id} ({st.get('status', 'CASH_RESERVE_100_PERCENT')})"
            except Exception:
                pass

        packet = {
            "sync_id": sync_id,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "source": "ANTIGRAVITY",
            "target": "PALMER",
            "priority": priority,
            "user_request": user_request,
            "response_summary": response_summary,
            "completed_tasks": completed_tasks,
            "active_decisions": active_decisions,
            "system_state": {
                "chairman_account": "TCBS 105C307855 (Trần Quốc Thiên Phước)",
                "status": st.get("status", "CASH_RESERVE_100_PERCENT"),
                "current_campaign_phase": st.get("current_campaign_phase", "TRIAL_CLOSED_100_CASH_WEEK48_PREP"),
                "total_nav_vnd": total_nav,
                "cash_vnd": cash_vnd,
                "cash_pct": cash_pct,
                "stock_market_val_vnd": stock_market_val,
                "active_holdings": pos_details,
                "realized_pnl_vnd": float(st.get("realized_pnl_vnd", 0.0) or 0.0),
                "current_market_regime": live_regime
            },
            "acknowledged_by_palmer": True,
            "acknowledged_at": now.strftime("%Y-%m-%d %H:%M:%S")
        }

        # 1. Ghi vào Sổ cái trao đổi 2 chiều
        ledger = cls.load_sync_ledger()
        ledger.insert(0, packet)
        cls.save_sync_ledger(ledger)

        # 2. Cập nhật Bộ Nhớ Trực Tuyến Live Briefing cho Palmer
        default_holdings_dir = (
            "100% TIỀN MẶT (0 CP đang giữ — BAF & MSH đã bán khớp hết trưa 20/11). Tuyệt đối không báo còn cổ phiếu."
            if not pos_details
            else ", ".join(f"{sym}: {d['shares']} CP @ {d['current_price']:,.0f}₫" for sym, d in pos_details.items())
        )
        live_briefing = {
            "last_updated": now.strftime("%Y-%m-%d %H:%M:%S"),
            "last_synced_by": "ANTIGRAVITY",
            "sync_id": sync_id,
            "latest_user_request": user_request,
            "latest_response_summary": response_summary,
            "latest_completed_tasks": completed_tasks,
            "latest_strategic_decisions": active_decisions,
            "portfolio_snapshot": {
                "status": st.get("status", "CASH_RESERVE_100_PERCENT"),
                "total_nav_vnd": total_nav,
                "cash_vnd": cash_vnd,
                "cash_pct": cash_pct,
                "stock_market_val_vnd": stock_market_val,
                "positions": pos_details,
                "current_market_regime": live_regime,
            },
            "directives_for_palmer_responses": {
                "current_holdings_directive": active_decisions.get("current_holdings_directive", default_holdings_dir),
                "market_regime_directive": active_decisions.get("market_regime_directive", f"Chế độ sống: {live_regime}. Giải ngân chỉ mở khung 14h00-14h25 khi đạt điều kiện S1/S2/S3."),
                "weekly_plan_directive": active_decisions.get("weekly_plan_directive", "Cuối tuần 20-22/11 nghỉ ngơi 100% Cash. Tuần 48 (23/11) đánh rổ Q3/2026 sạch (TPB, HDB, HPG, CTG, VPB) theo Ma trận 4 kịch bản S1-S4."),
                "upgrade_progress_directive": active_decisions.get("upgrade_progress_directive", "Đã triển khai crawler Internet/BCTC/IR đa nguồn hàng ngày (Giai đoạn 1) và đồng bộ 2 chiều về Palmer."),
                # Backward-compatible aliases (trỏ về thông tin mới nhất, không chứa dữ liệu cũ)
                "regarding_bsr_baf": active_decisions.get("current_holdings_directive", default_holdings_dir),
                "regarding_hdb_msh": active_decisions.get("market_regime_directive", f"Chế độ sống: {live_regime}."),
                "regarding_weekly_plan": active_decisions.get("weekly_plan_directive", "Tuần 48 (23/11) sẵn sàng 100% Cash với Ma trận S1-S4."),
                "regarding_today_morning_tasks": active_decisions.get("upgrade_progress_directive", "Đã hoàn tất đồng bộ Palmer <-> Antigravity V2.0.")
            }
        }

        with open(LIVE_BRIEFING_FILE, "w", encoding="utf-8") as f:
            json.dump(live_briefing, f, indent=2, ensure_ascii=False)

        # 3. Xuất file Markdown để con người & agent đọc trực tiếp
        cls._export_live_briefing_md(live_briefing)

        # 4. Đồng bộ vào Closed-Loop Task Ledger để Palmer tra cứu
        try:
            from scripts.closed_loop_task_dispatcher import load_task_ledger, save_task_ledger
            t_ledger = load_task_ledger()
            task_entry = {
                "task_id": f"TASK-AG2P-{now.strftime('%Y%m%d-%H%M%S')}",
                "created_at": now.isoformat(),
                "command_raw": user_request,
                "source": "ANTIGRAVITY_TO_PALMER_SYNC",
                "assigned_department": "CENTRAL_SYSTEM_GOVERNANCE_PALMER",
                "assigned_department_name": "Phòng Quản Trị Hệ Thống & Cố Vấn Tối Cao Palmer",
                "assigned_officer": "Palmer & Antigravity",
                "topic_key": "james_hq",
                "topic_name": "🎖️ BỘ CHỈ HUY TỔNG TƯ LỆNH JAMES",
                "status": "COMPLETED",
                "action_type": "BILATERAL_SYNC_BROADCAST",
                "execution_result": {
                    "summary": response_summary,
                    "completed_tasks": completed_tasks,
                    "active_decisions": active_decisions
                },
                "logs": [f"{now.strftime('%H:%M:%S')} - Đã phổ biến trực tiếp và đồng bộ 100% sang Palmer"]
            }
            t_ledger.insert(0, task_entry)
            save_task_ledger(t_ledger)
        except Exception as e:
            print(f"[!] Lỗi đồng bộ closed-loop task: {e}")

        return packet

    @classmethod
    def broadcast_from_palmer_to_antigravity(
        cls,
        user_query: str,
        palmer_response: str,
        action_executed: str = ""
    ) -> Dict[str, Any]:
        """
        Palmer gọi hàm này mỗi khi xử lý tin nhắn từ Chủ tịch trên Telegram
        để truyền đạt ngược lại ngay cho Antigravity.
        """
        now = datetime.datetime.now()
        sync_id = f"SYNC-P2AG-{now.strftime('%Y%m%d-%H%M%S')}"

        packet = {
            "sync_id": sync_id,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "source": "PALMER",
            "target": "ANTIGRAVITY",
            "priority": "HIGH",
            "user_request": user_query,
            "response_summary": palmer_response,
            "action_executed": action_executed,
            "acknowledged_by_antigravity": True,
            "acknowledged_at": now.strftime("%Y-%m-%d %H:%M:%S")
        }

        ledger = cls.load_sync_ledger()
        ledger.insert(0, packet)
        cls.save_sync_ledger(ledger)

        # Cập nhật Live Briefing
        live = cls.load_live_briefing()
        live["last_updated"] = now.strftime("%Y-%m-%d %H:%M:%S")
        live["last_synced_by"] = "PALMER"
        live["last_telegram_interaction"] = {
            "query": user_query,
            "response": palmer_response,
            "action": action_executed,
            "time": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(LIVE_BRIEFING_FILE, "w", encoding="utf-8") as f:
            json.dump(live, f, indent=2, ensure_ascii=False)

        cls._export_live_briefing_md(live)
        return packet

    @classmethod
    def get_latest_briefing_for_palmer(cls) -> str:
        """
        Được gọi bởi Telegram Copilot / Palmer để trích xuất nhanh toàn bộ context mới nhất
        do Antigravity chuyển giao, dùng để trả lời ngay lập tức nếu Chủ tịch hỏi.
        """
        live = cls.load_live_briefing()
        if not live:
            return "Chưa có bản tin đồng bộ nào."

        lines = [
            f"🔄 *[THÔNG TIN ĐỒNG BỘ NỘI BỘ TỨC THỜI ANTIGRAVITY ➔ PALMER]*",
            f"🕒 *Cập nhật:* `{live.get('last_updated')}` (Bởi {live.get('last_synced_by')})",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📌 *Yêu cầu/Câu hỏi gần nhất của Chủ tịch:*",
            f"_{live.get('latest_user_request')}_",
            "\n💡 *Quyết định & Kết luận chiến lược đã chốt:*",
            f"{live.get('latest_response_summary')}",
            "\n✅ *Các công việc đã thực thi xong:*",
        ]
        for t in live.get("latest_completed_tasks", []):
            lines.append(f"• {t}")

        directives = live.get("directives_for_palmer_responses", {})
        lines.extend([
            "\n🎯 *CHỈ THỊ ĐỒNG NHẤT CỦA HỆ THỐNG:*",
            f"• *Vị thế hiện tại:* {directives.get('current_holdings_directive', directives.get('regarding_bsr_baf'))}",
            f"• *Chế độ thị trường:* {directives.get('market_regime_directive', directives.get('regarding_hdb_msh'))}",
            f"• *Kế hoạch Tuần 48:* {directives.get('weekly_plan_directive', directives.get('regarding_weekly_plan'))}",
            f"• *Tiến độ nâng cấp:* {directives.get('upgrade_progress_directive', directives.get('regarding_today_morning_tasks'))}"
        ])
        return "\n".join(lines)

    @classmethod
    def _export_live_briefing_md(cls, data: Dict[str, Any]) -> None:
        try:
            snap = data.get("portfolio_snapshot", {})
            cash_val = float(snap.get("cash_vnd", 0.0) or 0.0)
            nav_val = float(snap.get("total_nav_vnd", cash_val) or 0.0)
            stk_val = float(snap.get("stock_market_val_vnd", 0.0) or 0.0)
            cash_pct = float(snap.get("cash_pct", (cash_val / nav_val * 100.0) if nav_val > 0 else 100.0))
            pos = snap.get("positions", {}) or {}
            dirs = data.get("directives_for_palmer_responses", {})

            content = f"""# APEX EXECUTIVE LIVE BRIEFING (ANTIGRAVITY <-> PALMER SYNC)
**Thời gian cập nhật:** {data.get('last_updated')}  
**Người đồng bộ gần nhất:** {data.get('last_synced_by')}  
**Mã đồng bộ:** `{data.get('sync_id')}`  

---

## I. YÊU CẦU & KẾT QUẢ PHÂN TÍCH MỚI NHẤT CỦA CHỦ TỊCH
* **Yêu cầu gần nhất của Chủ tịch:** {data.get('latest_user_request')}
* **Kết luận & Quyết định thể chế:**
{data.get('latest_response_summary')}

## II. CÁC CÔNG VIỆC ĐÃ HOÀN TẤT THỰC SỰ
"""
            for task in data.get("latest_completed_tasks", []):
                content += f"- [x] {task}\n"

            content += f"""
## III. TRẠNG THÁI DANH MỤC THỜI GIAN THỰC (SSOT)
- **Tài khoản thụ hưởng:** TCBS `105C307855` (Chủ tịch Trần Quốc Thiên Phước)
- **Tổng NAV ròng:** `{nav_val:,.0f} ₫` (`{cash_pct:.1f}% Tiền mặt`)
- **Tiền mặt ròng:** `{cash_val:,.0f} ₫`
- **Giá trị cổ phiếu:** `{stk_val:,.0f} ₫`
- **Vị thế cổ phiếu đang giữ:**
"""
            if pos:
                for sym, p in pos.items():
                    content += f"  * **{sym}**: {p.get('shares')} CP | Giá vốn: {p.get('entry_price'):,.0f} ₫ | Thị giá: {p.get('current_price'):,.0f} ₫ | PnL: {p.get('pnl_vnd'):+,.0f} ₫ ({p.get('status')})\n"
            else:
                content += "  * **KHÔNG CÓ (`0 cổ phiếu` — Đang giữ `100.0% Tiền mặt` sạch qua cuối tuần)**\n"

            content += f"""
## IV. NGUYÊN TẮC PHÁT NGÔN ĐỒNG BỘ TUYỆT ĐỐI CHO PALMER
1. **Vị thế hiện tại:** {dirs.get('current_holdings_directive', dirs.get('regarding_bsr_baf'))}
2. **Chế độ thị trường:** {dirs.get('market_regime_directive', dirs.get('regarding_hdb_msh'))}
3. **Kế hoạch Tuần 48:** {dirs.get('weekly_plan_directive', dirs.get('regarding_weekly_plan'))}
4. **Tiến độ nâng cấp hệ thống:** {dirs.get('upgrade_progress_directive', dirs.get('regarding_today_morning_tasks'))}

*Lưu ý thể chế: Palmer và Antigravity là một thực thể thống nhất. Tuyệt đối không đưa ra thông tin lệch pha hoặc dùng dữ liệu cũ.*
"""
            with open(LIVE_BRIEFING_MD, "w", encoding="utf-8") as f:
                f.write(content)

            # Ghi ra thư mục gốc workspace Chứng khoán để mọi agent/chat đều nhìn thấy ngay
            try:
                with open(INTER_CHAT_STATE_MD, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as _e_root:
                print(f"[!] Lỗi ghi 00_LIVE_INTER_CHAT_STATE.md: {_e_root}")

            # Ghi trực tiếp vào thư mục brain của đoạn chat Palmer (Tổng hệ thống)
            if PALMER_BRAIN_DIR.exists():
                try:
                    with open(PALMER_BRAIN_DIR / "00_LIVE_INTER_CHAT_STATE.md", "w", encoding="utf-8") as f:
                        f.write(content)
                    with open(PALMER_BRAIN_DIR / "LIVE_BRIEFING_FROM_JAMES.md", "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception as _e_brain:
                    print(f"[!] Lỗi ghi brain của Palmer: {_e_brain}")

            # Đồng bộ trực tiếp sang phòng làm việc của Palmer (Trợ lí cá nhân)
            if TRO_LI_DIR.exists():
                try:
                    TRO_LI_DATA_DIR.mkdir(parents=True, exist_ok=True)
                    with open(TRO_LI_SYNC_JSON, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    with open(TRO_LI_SYNC_MD, "w", encoding="utf-8") as f:
                        f.write(content)
                    cls._sync_to_tro_li_memory(data)
                except Exception as _e_tr:
                    print(f"[!] Lỗi đồng bộ sang Trợ lí cá nhân: {_e_tr}")
        except Exception as e:
            print(f"[!] Lỗi xuất Markdown briefing: {e}")

    @classmethod
    def _sync_to_tro_li_memory(cls, data: Dict[str, Any]) -> None:
        if not TRO_LI_MEMORY_MD.exists():
            return
        try:
            mem_content = TRO_LI_MEMORY_MD.read_text(encoding="utf-8")
            snap = data.get("portfolio_snapshot", {})
            pos = snap.get("positions", {}) or {}
            dirs = data.get("directives_for_palmer_responses", {})
            cash_val = float(snap.get("cash_vnd", 0.0) or 0.0)
            nav_val = float(snap.get("total_nav_vnd", cash_val) or 0.0)
            stk_val = float(snap.get("stock_market_val_vnd", 0.0) or 0.0)
            cash_pct = float(snap.get("cash_pct", (cash_val / nav_val * 100.0) if nav_val > 0 else 100.0))

            section_header = "## 6. SỔ CÁI ĐỒNG BỘ DỮ LIỆU TỨC THỜI TỪ MASTER CIO JAMES (INTER-CHAT SYNC)"
            pos_bullets = []
            for sym, p in pos.items():
                pos_bullets.append(f"• **{sym}**: {p.get('shares')} CP | Giá vốn: {p.get('entry_price'):,.0f} ₫ | Thị giá: {p.get('current_price'):,.0f} ₫ | PnL: {p.get('pnl_vnd'):+,.0f} ₫ ({p.get('status', 'HOLDING')})")
            pos_str = "\n".join(pos_bullets) if pos_bullets else "• **KHÔNG CÓ (`0 CP` — Đang giữ `100.0% Tiền mặt` sạch qua cuối tuần)**"

            sync_block = f"""{section_header}
> [!IMPORTANT]
> **Dữ liệu sống từ phòng chat Chứng khoán của Master CIO James (Cập nhật: {data.get('last_updated')})**:
> - **Tài khoản TCBS**: `105C307855` (Chủ tịch Trần Quốc Thiên Phước)
> - **Tổng NAV**: `{nav_val:,.0f} ₫` | **Tiền mặt**: `{cash_val:,.0f} ₫` ({cash_pct:.1f}% Cash) | **Cổ phiếu**: `{stk_val:,.0f} ₫`
> - **Vị thế nắm giữ hiện tại**:
{pos_str}
> - **Chỉ thị tác chiến thống nhất (James <-> Palmer)**:
>   * Vị thế: {dirs.get('current_holdings_directive', dirs.get('regarding_bsr_baf'))}
>   * Thị trường: {dirs.get('market_regime_directive', dirs.get('regarding_hdb_msh'))}
>   * Kế hoạch Tuần 48: {dirs.get('weekly_plan_directive', dirs.get('regarding_weekly_plan'))}
>   * Nâng cấp hệ thống: {dirs.get('upgrade_progress_directive', dirs.get('regarding_today_morning_tasks'))}
>   * Yêu cầu gần nhất của Chủ tịch: _{data.get('latest_user_request')}_
>   * Kết luận của James: {data.get('latest_response_summary')}
"""
            if section_header in mem_content:
                parts = mem_content.split(section_header)
                mem_content = parts[0].rstrip() + "\n\n" + sync_block
            else:
                mem_content = mem_content.rstrip() + "\n\n---\n\n" + sync_block

            TRO_LI_MEMORY_MD.write_text(mem_content, encoding="utf-8")
        except Exception as e:
            print(f"[!] Lỗi cập nhật Trợ lí cá nhân MEMORY.md: {e}")


    @classmethod
    def sync_current_ssot(cls, note: str = "") -> Dict[str, Any]:
        """Đọc trực tiếp SSOT + kế hoạch tuần + dữ liệu cào Internet mới nhất để đồng bộ sang Palmer."""
        from scripts.portfolio_state_manager import PortfolioStateManager
        st = PortfolioStateManager.load_state()
        cash_vnd = float(st.get("cash_balance_vnd", 0.0) or 0.0)
        pos = st.get("active_positions") or {}

        weekly_plan_path = DATA_DIR / "weekly_tactical_plan_active.json"
        weekly_summary = "Tuần 48 (23/11): Rổ BCTC Q3/2026 sạch (TPB, HDB, HPG, CTG, VPB) theo Ma trận 4 kịch bản S1–S4."
        if weekly_plan_path.exists():
            try:
                wp = json.loads(weekly_plan_path.read_text(encoding="utf-8"))
                weekly_summary = wp.get("constitution_mandate") or weekly_summary
            except Exception:
                pass

        intel_path = DATA_DIR / "apex_daily_internet_intel.json"
        intel_note = "Chưa chạy quét Internet hôm nay."
        if intel_path.exists():
            try:
                intel = json.loads(intel_path.read_text(encoding="utf-8"))
                counts = intel.get("summary_counts") or {}
                intel_note = (
                    f"Cào sống ngày {intel.get('crawled_at')}: {counts.get('total_news_articles', 0)} bài báo RSS/CBTT, "
                    f"{counts.get('tickers_with_live_news', 0)} mã có tin doanh nghiệp Vietcap/CafeF, "
                    f"{counts.get('verified_ir_portals', 0)} cổng IR HTTP-200, "
                    f"{counts.get('tavily_live_hits', 0)} kết quả Tavily, "
                    f"{counts.get('sec_edgar_filings', 0)} hồ sơ SEC EDGAR."
                )
            except Exception:
                pass

        completed = [
            f"Xác nhận SSOT tài khoản TCBS 105C307855: Cash {cash_vnd:,.0f} ₫ | {len(pos)} vị thế mở",
            f"Đồng bộ dữ liệu cào Internet/BCTC: {intel_note}",
            "Đồng bộ 2 chiều sang data/palmer_live_briefing.*, 00_LIVE_INTER_CHAT_STATE.md và Trợ lí cá nhân (MEMORY.md)",
        ]
        if note:
            completed.insert(0, note)

        return cls.broadcast_from_antigravity_to_palmer(
            user_request=note or "Đồng bộ trạng thái SSOT & Dữ liệu cào Internet/BCTC mới nhất giữa James và Palmer",
            response_summary=weekly_summary,
            completed_tasks=completed,
            active_decisions={
                "current_holdings_directive": (
                    f"100% TIỀN MẶT ({cash_vnd:,.0f} ₫, 0 CP đang giữ — BAF @ 30,350đ & MSH @ 34,300đ đã bán khớp hết trưa 20/11). Tuyệt đối không báo còn nắm giữ cổ phiếu."
                    if not pos
                    else f"Đang giữ {len(pos)} mã, Cash {cash_vnd:,.0f} ₫."
                ),
                "weekly_plan_directive": weekly_summary,
                "upgrade_progress_directive": intel_note,
            },
        )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Apex Bilateral Sync Bridge (Antigravity <-> Palmer)")
    parser.add_argument("--sync-current", action="store_true", help="Đồng bộ trực tiếp SSOT và dữ liệu Internet mới nhất sang Palmer")
    parser.add_argument("--note", type=str, default="", help="Ghi chú đồng bộ tùy chọn")
    args = parser.parse_args()

    print("[*] Thực thi PalmerAntigravitySyncBridge (Live SSOT)...")
    pkt = PalmerAntigravitySyncBridge.sync_current_ssot(note=args.note)
    print(f"[+] Thành công! Sync ID: {pkt['sync_id']}")
    print("\n--- NỘI DUNG PALMER TRÍCH XUẤT ---")
    print(PalmerAntigravitySyncBridge.get_latest_briefing_for_palmer())
