"""
APEX INSTITUTIONAL MEMORY BRIDGE
--------------------------------
Module cầu nối đồng bộ trí nhớ thể chế tự động:
Kết nối giữa Hệ thống 11 Phòng Ban Apex Fund, SQLite Lakehouse Vault và Bộ nhớ dài hạn Claude-Mem (FTS5).

Đảm bảo:
1. Mọi phiên làm việc mới (phiên sau) tự động đọc được toàn bộ quyết định, lệnh đã khớp và chỉ đạo của Chủ tịch phiên trước.
2. Trị dứt điểm chứng Session Amnesia (quên danh mục, quên tiền mặt, nhắc mua lại cổ phiếu đã sở hữu).
3. Cho phép truy vấn Full-Text Search nhanh về lịch sử lệnh và bài học thể chế.
"""

import os
import json
import sqlite3
import datetime
from pathlib import Path

WORKSPACE_DIR = Path(r"C:\Users\phuoc\Downloads\antigravity\Chứng khoán")
CLAUDE_MEM_DB = Path(r"C:\Users\phuoc\.claude-mem\claude-mem.db")
APEX_VAULT_DB = WORKSPACE_DIR / "data" / "apex_institutional_vault.db"
STATE_FILE = WORKSPACE_DIR / "00_LIVE_INTER_CHAT_STATE.md"
PORTFOLIO_FILE = WORKSPACE_DIR / "data" / "current_portfolio_state.json"
BRAIN_V3_FILE = WORKSPACE_DIR / "data" / "apex_autonomous_brain_v3_output.json"
INTEL_FILE = WORKSPACE_DIR / "data" / "apex_daily_internet_intel.json"
WEEKLY_PLAN_FILE = WORKSPACE_DIR / "data" / "weekly_tactical_plan_active.json"


def get_current_state_snapshot():
    """Đọc snapshot dữ liệu chuẩn SSOT V2.0 hiện tại."""
    state_text = ""
    if STATE_FILE.exists():
        state_text = STATE_FILE.read_text(encoding="utf-8")
    
    portfolio_data = {}
    if PORTFOLIO_FILE.exists():
        try:
            portfolio_data = json.loads(PORTFOLIO_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
            
    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "state_summary": state_text[:2000],
        "portfolio": portfolio_data
    }


def inject_memory_to_claude_mem(title: str, text: str, category: str = "decision"):
    """
    Ghi nhận một observation trực tiếp vào Claude-Mem SQLite Database (FTS5).
    """
    if not CLAUDE_MEM_DB.exists():
        print(f"[MEMORY BRIDGE] Không tìm thấy DB claude-mem tại {CLAUDE_MEM_DB}")
        return False

    now_iso = datetime.datetime.now().isoformat()
    project = "ApexHedgeFund"

    try:
        conn = sqlite3.connect(CLAUDE_MEM_DB)
        cur = conn.cursor()

        # Tạo bảng apex_memory_store nếu cần mở rộng thêm
        cur.execute("""
            CREATE TABLE IF NOT EXISTS apex_institutional_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT,
                category TEXT,
                title TEXT,
                content TEXT,
                created_at TEXT
            )
        """)

        cur.execute("""
            INSERT INTO apex_institutional_memory (project, category, title, content, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (project, category, title, text, now_iso))

        conn.commit()
        conn.close()
        print(f"[MEMORY BRIDGE] Đã ghi nhận ký ức vào claude-mem.db: [{category.upper()}] {title}")
        return True
    except Exception as e:
        print(f"[MEMORY BRIDGE] Lỗi khi ghi ký ức vào claude-mem: {e}")
        return False


def query_institutional_memory(keyword: str = "", limit: int = 5):
    """
    Truy vấn trí nhớ thể chế cho các phòng ban AI (Minh Quân, James, Victor, Trọng).
    """
    memories = []
    if CLAUDE_MEM_DB.exists():
        try:
            conn = sqlite3.connect(CLAUDE_MEM_DB)
            cur = conn.cursor()
            
            # Kiểm tra xem bảng có tồn tại chưa
            check = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='apex_institutional_memory'").fetchone()
            if check:
                if keyword:
                    rows = cur.execute("""
                        SELECT title, content, created_at, category FROM apex_institutional_memory
                        WHERE content LIKE ? OR title LIKE ?
                        ORDER BY id DESC LIMIT ?
                    """, (f"%{keyword}%", f"%{keyword}%", limit)).fetchall()
                else:
                    rows = cur.execute("""
                        SELECT title, content, created_at, category FROM apex_institutional_memory
                        ORDER BY id DESC LIMIT ?
                    """, (limit,)).fetchall()

                for r in rows:
                    memories.append({
                        "title": r[0],
                        "content": r[1],
                        "created_at": r[2],
                        "category": r[3]
                    })
            conn.close()
        except Exception as e:
            print(f"[MEMORY BRIDGE] Lỗi query claude-mem: {e}")

    return memories


def _load_json_safe(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _purge_stale_hardcoded_memories():
    """Xóa các bản ghi ký ức giả tĩnh cũ (09/11 - 11/11) nếu còn sót trong claude-mem.db."""
    if not CLAUDE_MEM_DB.exists():
        return
    try:
        conn = sqlite3.connect(CLAUDE_MEM_DB)
        cur = conn.cursor()
        exists = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='apex_institutional_memory'"
        ).fetchone()
        if exists:
            cur.execute(
                """
                DELETE FROM apex_institutional_memory
                WHERE title LIKE '%100 HDB & 100 MSH%'
                   OR content LIKE '%14,510,422%'
                   OR content LIKE '%14.51M%'
                   OR content LIKE '%72.0% Cash%'
                """
            )
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"[MEMORY BRIDGE] Cảnh báo khi dọn ký ức cũ: {e}")


def sync_core_apex_memory():
    """
    Đồng bộ hóa tức thì trạng thái danh mục thực tế (SSOT động), Brain V3.0 và crawler Internet vào kho ký ức.
    """
    snap = get_current_state_snapshot()
    portfolio = snap.get("portfolio") or _load_json_safe(PORTFOLIO_FILE)
    v3_out = _load_json_safe(BRAIN_V3_FILE)
    intel_out = _load_json_safe(INTEL_FILE)
    weekly_plan = _load_json_safe(WEEKLY_PLAN_FILE)

    account_id = str(portfolio.get("account_id") or "105C307855")
    status_str = str(portfolio.get("status") or "ALL_CASH_STANDDOWN")
    cash_vnd = float(portfolio.get("cash_balance_vnd") or 0.0)
    nav_vnd = float(portfolio.get("total_nav_vnd") or cash_vnd)
    positions = portfolio.get("active_positions") or {}
    cash_pct = (cash_vnd / nav_vnd * 100.0) if nav_vnd > 0 else 100.0

    if not positions:
        pos_summary = "0 cổ phiếu đang nắm giữ (Đã bán khớp hết 100 BAF @ 30,350đ lúc 13:08 & 100 MSH @ 34,300đ lúc 13:12 ngày 20/11/2026)"
        pos_md_block = "- Cổ phiếu đang giữ: **0 CP (`ALL_CASH_STANDDOWN`)** — Đã tất toán sạch 100% BAF & MSH trưa `20/11/2026`."
    else:
        pos_items = [
            f"{sym} ({int(p.get('shares', 0))} CP @ {float(p.get('entry_price') or p.get('avg_cost') or 0):,.0f} đ)"
            for sym, p in positions.items()
        ]
        pos_summary = "; ".join(pos_items)
        pos_md_block = "\n".join(f"  * **{item}**" for item in pos_items)

    mr = v3_out.get("market_regime") or {}
    regime_id = str(mr.get("regime_id") or "BEAR_WITH_SPRING_WATCH")
    vni_close = float(mr.get("vnindex_close") or 0.0)
    as_of = str(mr.get("as_of_date") or "")
    br20 = float(mr.get("breadth_above_ma20_pct") or 0.0)
    strikes = v3_out.get("asymmetric_conviction_strikes") or []
    strike_names = ", ".join(
        f"{s.get('symbol')} ({int(s.get('shares_lot100') or 0)} CP @ {float(s.get('limit_entry_vnd') or 0):,.0f}đ)"
        for s in strikes[:3]
    ) or "TPB, HDB, CTG"

    sc = intel_out.get("summary_counts") or {}
    crawled_at = str(intel_out.get("crawled_at") or snap["timestamp"])
    mandate = str(weekly_plan.get("constitution_mandate") or "")[:320]

    _purge_stale_hardcoded_memories()

    mem_title_1 = f"TRẠNG THÁI SSOT THỰC TẾ: {cash_pct:.1f}% TIỀN MẶT ({cash_vnd:,.0f} đ) | {len(positions)} CP"
    mem_body_1 = (
        f"Chủ tịch Trần Quốc Thiên Phước (TCBS {account_id}): Trạng thái `{status_str}`. "
        f"Tổng NAV: {nav_vnd:,.0f} đ | Tiền mặt thực tế: {cash_vnd:,.0f} đ ({cash_pct:.1f}% Cash). "
        f"Vị thế cổ phiếu: {pos_summary}. "
        f"TUYỆT ĐỐI KHÔNG BÁO CÒN NẮM GIỮ 100 HDB HOẶC 100 MSH HOẶC 100 BAF."
    )
    inject_memory_to_claude_mem(mem_title_1, mem_body_1, category="portfolio_ssot")

    mem_title_2 = f"CHẾ ĐỘ BRAIN V3.0 ({regime_id}) & KHUNG GIỜ VÀNG 14H05-14H25"
    mem_body_2 = (
        f"1. Thị trường EOD {as_of}: VN-Index {vni_close:,.2f}, Breadth>MA20={br20:.1f}%, Regime={regime_id}. "
        f"2. Không FOMO ATO sáng hay trước 14h00; chỉ kích hoạt lệnh LO khung 14h05–14h25 theo 4 nhánh S1–S4. "
        f"3. Rổ Đánh cược Bất đối xứng V3.0 Tuần 48: {strike_names} (khóa Stop -5.5%). "
        f"4. Intel Crawler ({crawled_at}): {sc.get('total_news_articles', 0)} tin, {sc.get('rss_sources_online', 0)} RSS, "
        f"{sc.get('verified_ir_portals', 0)} IR HTTP-200, {sc.get('tavily_live_hits', 0)} Tavily, {sc.get('sec_edgar_filings', 0)} SEC."
    )
    inject_memory_to_claude_mem(mem_title_2, mem_body_2, category="institutional_policy")

    rule_file = Path(r"C:\Users\phuoc\.agents\rules\claude-mem-context.md")
    if rule_file.parent.exists():
        rule_content = f"""<claude-mem-context>
# APEX INSTITUTIONAL ACTIVE MEMORY (SSOT V3.0 LIVE)
**Thời gian đồng bộ:** {snap['timestamp']}
**Chủ tịch:** Trần Quốc Thiên Phước | Tài khoản TCBS: `{account_id}` | Tổng NAV: **`{nav_vnd:,.0f} ₫`**

## 1. Trạng Thái Danh Mục Thực Tế (SSOT):
- Trạng thái: **`{status_str}`**
- Tiền mặt thực tế trong két: **`{cash_vnd:,.0f} ₫`** (`{cash_pct:.1f}% Cash`)
{pos_md_block}

## 2. Đầu Não Tự Chủ Brain V3.0 & Dữ Liệu Sống:
- Thị trường EOD `{as_of}`: VN-Index **`{vni_close:,.2f}`** | Breadth>MA20: **`{br20:.1f}%`** | Regime: **`{regime_id}`**
- Internet Intel (`{crawled_at}`): `{sc.get('total_news_articles', 0)}` tin (`{sc.get('tickers_with_live_news', 0)}` mã), `{sc.get('rss_sources_online', 0)}` RSS, `{sc.get('verified_ir_portals', 0)}` cổng IR HTTP-200, `{sc.get('tavily_live_hits', 0)}` Tavily, `{sc.get('sec_edgar_filings', 0)}` SEC EDGAR.
- Kèo S3 Spring V3.0 dự kiến chiều Thứ Hai (`14h05–14h25`): `{strike_names}` (chỉ kích hoạt nếu đạt điều kiện; thủng đáy giữ `100%` Tiền mặt S4).
- Chỉ thị Tuần 48: {mandate}
</claude-mem-context>
"""
        rule_file.write_text(rule_content, encoding="utf-8")
        print("[MEMORY BRIDGE] Đã cập nhật claude-mem-context.md động theo SSOT V3.0!")

    return True


if __name__ == "__main__":
    print("=== ĐỒNG BỘ TRÍ NHỚ THỂ CHẾ APEX FUND ===")
    sync_core_apex_memory()
    mems = query_institutional_memory(limit=3)
    print(f"\n[QUERY TEST] Tìm thấy {len(mems)} mẩu ký ức hoạt động:")
    for m in mems:
        print(f" - [{m['category']}] {m['title']} ({m['created_at']})")
