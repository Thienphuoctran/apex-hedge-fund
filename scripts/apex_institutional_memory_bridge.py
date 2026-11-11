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
PORTFOLIO_FILE = WORKSPACE_DIR / "VN_Market" / "data" / "current_portfolio_state.json"


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


def sync_core_apex_memory():
    """
    Đồng bộ hóa tức thì trạng thái danh mục then chốt vào kho ký ức.
    """
    snap = get_current_state_snapshot()
    
    # Ký ức then chốt 1: Lệnh đã khớp Vòng 2
    mem_title_1 = "DANH MỤC THỰC TẾ ĐÃ KHỚP LỆNH: 100 HDB & 100 MSH (T+2.5 VỀ KÉT 13H00)"
    mem_body_1 = (
        "Chủ tịch Trần Quốc Thiên Phước (TCBS 105C307855) đã khớp thành công 100 CP HDB (@22,050 ₫) "
        "và 100 CP MSH (@34,517 ₫) trong phiên 09/11/2026. "
        "Tổng giá trị cổ phiếu: 5,650,000 ₫ (28.0% NAV). "
        "Tiền mặt thực tế còn lại: 14,510,422 ₫ (72.0% Cash). "
        "Tổng NAV: 20,160,422 ₫. "
        "Chiều nay 11/11/2026 lúc 13h00, 200 CP này chính thức về tài khoản khả dụng. "
        "TUYỆT ĐỐI CẤM NHẮC MUA LẠI HOẶC GIỤC MUA GOM NHỊP 1 HDB/MSH."
    )
    inject_memory_to_claude_mem(mem_title_1, mem_body_1, category="portfolio_ssot")

    # Ký ức then chốt 2: Quy tắc điều hành và bảo vệ vốn
    mem_title_2 = "QUY TẮC BẢO VỆ VỐN VÀ KHUNG GIỜ VÀNG 14H00-14H25"
    mem_body_2 = (
        "1. Két tiền mặt 14.51M là bất khả xâm phạm. "
        "2. Không FOMO mua đuổi giá xanh trước 10h00 sáng. "
        "3. Phiên chiều 13h00-13h45: Quan sát hấp thụ hàng T+2 về tài khoản. "
        "4. Khung Giờ Vàng 14h00-14h25: Nâng Stop giá vốn cho HDB (22,050) và MSH (34,517) để gồng lãi không rủi ro; "
        "chỉ giải ngân thăm dò tối đa 5.5M nếu BAF/IDC/BSR xuất hiện nến Test Cung bứt phá."
    )
    inject_memory_to_claude_mem(mem_title_2, mem_body_2, category="institutional_policy")

    # Cập nhật placeholder file của Antigravity rules
    rule_file = Path(r"C:\Users\phuoc\.agents\rules\claude-mem-context.md")
    if rule_file.parent.exists():
        rule_content = f"""<claude-mem-context>
# APEX INSTITUTIONAL ACTIVE MEMORY (SSOT V2.0)
**Thời gian đồng bộ:** {snap['timestamp']}
**Chủ tịch:** Trần Quốc Thiên Phước | Tài khoản TCBS: 105C307855 | Tổng NAV: 20,160,422 ₫

## 1. Trạng Thái Danh Mục Thực Tế:
- Tiền mặt két: **14,510,422 ₫** (~72.0% Cash)
- Cổ phiếu nắm giữ (T+2.5 khả dụng chiều nay 13h00):
  * **100 HDB**: Giá vốn 22,050 ₫ | Live: ~22.25k | Stop 2xATR: 21,220 ₫ | LÃI ĐỆM
  * **100 MSH**: Giá vốn 34,517 ₫ | Live: ~34.60k | Stop 2xATR: 33,090 ₫ | LÃI ĐỆM
- Tổng lãi chốt Vòng 1: +167,119 ₫ (Đã tất toán 100% HPG, TCB, MBB)

## 2. Kỷ Luật Tác Chiến Bất Biến:
- CẤM nhắc mua lại HDB hoặc MSH (đã khớp xong từ phiên 09/11).
- Phiên hôm nay 11/11: Chờ 13h00 hàng về, Khung Giờ Vàng 14h00-14h25 nâng Stop giá vốn gồng lãi.
- Kế hoạch giải ngân mới: Chỉ thăm dò tối đa 5.5M nếu BAF/IDC/BSR có setup A+.
</claude-mem-context>
"""
        rule_file.write_text(rule_content, encoding="utf-8")
        print("[MEMORY BRIDGE] Đã cập nhật claude-mem-context.md cho Antigravity Rules!")

    return True


if __name__ == "__main__":
    print("=== ĐỒNG BỘ TRÍ NHỚ THỂ CHẾ APEX FUND ===")
    sync_core_apex_memory()
    mems = query_institutional_memory(limit=3)
    print(f"\n[QUERY TEST] Tìm thấy {len(mems)} mẩu ký ức hoạt động:")
    for m in mems:
        print(f" - [{m['category']}] {m['title']} ({m['created_at']})")
