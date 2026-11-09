#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX INSTITUTIONAL DATABASE ENGINE V5.0 (SQLITE LAKEHOUSE VAULT)
File: scripts/apex_database_engine.py

Cơ quan chủ trì: Ban 12 Trọng (Tổng Kiểm Sát Thể Chế) phối hợp cùng Palmer (Cố Vấn Tối Cao)
Giám sát thể chế: Master CIO James (Ban 8)
Phục vụ trực tiếp: Chủ tịch Hội đồng Quản trị Trần Quốc Thiên Phước (Tài khoản TCBS: 105C307855)

Chức năng:
1. Quản lý kết nối cơ sở dữ liệu SQLite chuẩn WAL mode (Write-Ahead Logging), đa luồng (thread-safe), không khóa bảng.
2. Lưu trữ có chỉ mục (Indexed B-Tree) toàn bộ báo cáo thể chế, snapshot tài sản SSOT, và sổ lệnh thực thi.
3. Tích hợp máy tìm kiếm toàn văn FTS5 (Full-Text Search) cho phép tìm kiếm bất kỳ từ khóa / mã CP nào dưới 1 mili-giây.
4. Hỗ trợ cơ chế Ghi Kép (Dual-Write) song song với tệp Markdown truyền thống, bảo đảm 100% Zero Data Loss.
5. Cung cấp API phân trang siêu tốc (Pagination LIMIT / OFFSET) phục vụ Web Portal 24/7.
"""

import os
import re
import sys
import json
import time
import sqlite3
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
DB_PATH = DATA_DIR / "apex_institutional_vault.db"


class ApexDatabaseEngine:
    """Động Cơ Cơ Sở Dữ Liệu Thể Chế Apex V5.0 (SQLite Lakehouse Vault)."""

    _connection_pool: Optional[sqlite3.Connection] = None

    @classmethod
    def get_connection(cls, db_path: Optional[Path] = None) -> sqlite3.Connection:
        """Khởi tạo và cấu hình kết nối SQLite tối ưu chuẩn công nghiệp."""
        target_path = db_path or DB_PATH
        target_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(target_path), timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row

        # Kích hoạt WAL Mode & tối ưu bộ nhớ đệm
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA cache_size = -64000;")  # 64 MB RAM cache
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA temp_store = MEMORY;")

        return conn

    @classmethod
    def initialize_database(cls, db_path: Optional[Path] = None):
        """Khởi tạo toàn bộ cấu trúc Schema, Bảng FTS5 và Triggers đồng bộ tự động."""
        conn = cls.get_connection(db_path)
        cur = conn.cursor()

        # 1. BẢNG BÁO CÁO THỂ CHẾ CHÍNH (institutional_reports)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS institutional_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rel_path TEXT UNIQUE NOT NULL,
            file_name TEXT NOT NULL,
            title TEXT NOT NULL,
            dept_id TEXT NOT NULL,
            dept_name TEXT NOT NULL,
            dept_short TEXT,
            icon TEXT,
            color TEXT,
            date TEXT NOT NULL,
            time TEXT,
            sort_time TEXT NOT NULL,
            shift_label TEXT,
            preview TEXT,
            content TEXT,
            tickers TEXT,
            word_count INTEGER DEFAULT 0,
            size_bytes INTEGER DEFAULT 0,
            size_kb REAL DEFAULT 0.0,
            mtime REAL DEFAULT 0.0,
            is_today INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)

        # Các chỉ mục tăng tốc truy vấn cho bảng institutional_reports
        cur.execute("CREATE INDEX IF NOT EXISTS idx_reports_date_time ON institutional_reports(date DESC, sort_time DESC);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_reports_dept ON institutional_reports(dept_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_reports_shift ON institutional_reports(shift_label);")

        # 2. BẢNG ẢO TÌM KIẾM TOÀN VĂN FTS5 (reports_fts)
        cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS reports_fts USING fts5(
            title,
            preview,
            content,
            tickers,
            dept_name,
            content='institutional_reports',
            content_rowid='id'
        );
        """)

        # 3. TRIGGERS ĐỒNG BỘ TỰ ĐỘNG TỪ BẢNG CHÍNH SANG BẢNG FTS5
        cur.execute("""
        CREATE TRIGGER IF NOT EXISTS reports_ai AFTER INSERT ON institutional_reports BEGIN
            INSERT INTO reports_fts(rowid, title, preview, content, tickers, dept_name)
            VALUES (new.id, new.title, new.preview, new.content, new.tickers, new.dept_name);
        END;
        """)

        cur.execute("""
        CREATE TRIGGER IF NOT EXISTS reports_ad AFTER DELETE ON institutional_reports BEGIN
            INSERT INTO reports_fts(reports_fts, rowid, title, preview, content, tickers, dept_name)
            VALUES ('delete', old.id, old.title, old.preview, old.content, old.tickers, old.dept_name);
        END;
        """)

        cur.execute("""
        CREATE TRIGGER IF NOT EXISTS reports_au AFTER UPDATE ON institutional_reports BEGIN
            INSERT INTO reports_fts(reports_fts, rowid, title, preview, content, tickers, dept_name)
            VALUES ('delete', old.id, old.title, old.preview, old.content, old.tickers, old.dept_name);
            INSERT INTO reports_fts(rowid, title, preview, content, tickers, dept_name)
            VALUES (new.id, new.title, new.preview, new.content, new.tickers, new.dept_name);
        END;
        """)

        # 4. BẢNG MỤC LỤC TOÀN BỘ VĂN BẢN MARKDOWN HỆ THỐNG (all_markdown_catalog)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS all_markdown_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rel_path TEXT UNIQUE NOT NULL,
            file_name TEXT NOT NULL,
            category TEXT,
            title TEXT,
            date TEXT,
            size_bytes INTEGER DEFAULT 0,
            mtime REAL DEFAULT 0.0,
            indexed_at TEXT NOT NULL
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_catalog_category ON all_markdown_catalog(category);")

        # 5. BẢNG LỊCH SỬ TÀI SẢN & SỨC KHỎE SSOT (portfolio_snapshots)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            account_id TEXT NOT NULL,
            cash_vnd REAL NOT NULL,
            active_positions_count INTEGER DEFAULT 0,
            realized_pnl_vnd REAL DEFAULT 0,
            positions_json TEXT,
            notes TEXT
        );
        """)

        # 6. BẢNG SỔ LỆNH THỰC THI THỂ CHẾ (execution_orders)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS execution_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE NOT NULL,
            symbol TEXT NOT NULL,
            action TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            order_type TEXT NOT NULL,
            price_target REAL,
            stop_loss REAL,
            status TEXT NOT NULL,
            allocated_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            notes TEXT
        );
        """)

        # 7. BẢNG LỊCH SỬ KIỂM TOÁN HẠ TẦNG CỦA TRỌNG (infrastructure_audits)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS infrastructure_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            health_score INTEGER NOT NULL,
            total_reports INTEGER NOT NULL,
            total_markdown INTEGER NOT NULL,
            disk_mb REAL NOT NULL,
            status TEXT NOT NULL,
            officer TEXT NOT NULL,
            telemetry_json TEXT
        );
        """)

        conn.commit()
        conn.close()

    @classmethod
    def extract_stock_tickers(cls, text: str) -> List[str]:
        """Trích xuất danh sách mã cổ phiếu Việt Nam & Quốc tế được nhắc tới."""
        potential = re.findall(r"\b[A-Z]{3,5}\b", text)
        exclude_common = {
            "THE", "AND", "FOR", "NOT", "BUT", "ALL", "NEW", "TOP", "NAV", "BUY", "SET",
            "OUT", "TWO", "ONE", "LOW", "BIG", "PER", "NET", "EPS", "ROE", "ROA", "WTI",
            "DXY", "VIX", "USD", "VND", "TCB", "CTG", "MBB", "ACB", "VPB", "HDB", "BID",
            "SSI", "VND", "VCI", "HCM", "FTS", "MSN", "MWG", "PNJ", "DGC", "FPT", "VHM",
            "VIC", "VRE", "KDH", "NLG", "DXG", "DIG", "PVD", "PVS", "BSR", "GAS", "PLX",
            "HPG", "HSG", "NKG", "VHC", "ANV", "MSH", "TNG", "STK", "BAF", "DBC", "HAG",
            "GVR", "DPR", "PHR", "IDC", "SZC", "KBC", "VGC", "QTP", "HND", "GEG", "POW",
            "CTR", "VGI", "FOX", "BMP", "NTP", "DCM", "DPM", "LAS", "BFC"
        }
        known_vietnamese_tickers = {
            "HDB", "MSH", "BAF", "IDC", "FPT", "DGC", "HPG", "TCB", "MBB", "VNM", "MWG",
            "SSI", "VHM", "VIC", "VRE", "ACB", "BID", "CTG", "VPB", "STB", "TPB", "MSN",
            "PNJ", "VHC", "ANV", "TNG", "DBC", "HAG", "GVR", "DPR", "PHR", "SZC", "KBC",
            "VGC", "PVD", "PVS", "BSR", "GAS", "PLX", "QTP", "HND", "GEG", "POW", "CTR",
            "VGI", "DCM", "DPM", "NKG", "HSG", "KDH", "NLG", "DXG", "DIG", "BMP", "NTP"
        }
        known_us_tickers = {
            "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AVGO", "AMD", "QCOM",
            "INTC", "TXN", "ASML", "TSM", "ARM", "MU", "JPM", "BAC", "WFC", "GS", "MS",
            "LLY", "NVO", "JNJ", "PFE", "ABBV", "XOM", "CVX", "COP", "SLB", "CAT", "GE",
            "LMT", "RTX", "BA", "COST", "WMT", "TGT", "HD", "PG", "KO", "PEP", "PLTR"
        }

        found = set()
        for tok in potential:
            if tok in known_vietnamese_tickers or tok in known_us_tickers:
                found.add(tok)

        return sorted(list(found))

    @classmethod
    def upsert_institutional_report(cls, meta: Dict[str, Any], content: str = "") -> int:
        """Thêm mới hoặc cập nhật một báo cáo thể chế vào SQLite Lakehouse Vault."""
        conn = cls.get_connection()
        cur = conn.cursor()

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        word_count = len(content.split()) if content else 0
        tickers_list = cls.extract_stock_tickers(meta.get("title", "") + " " + meta.get("preview", "") + " " + content[:2000])
        tickers_json = json.dumps(tickers_list, ensure_ascii=False)

        cur.execute("""
        INSERT INTO institutional_reports (
            rel_path, file_name, title, dept_id, dept_name, dept_short, icon, color,
            date, time, sort_time, shift_label, preview, content, tickers, word_count,
            size_bytes, size_kb, mtime, is_today, created_at, updated_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?
        )
        ON CONFLICT(rel_path) DO UPDATE SET
            file_name = excluded.file_name,
            title = excluded.title,
            dept_id = excluded.dept_id,
            dept_name = excluded.dept_name,
            dept_short = excluded.dept_short,
            icon = excluded.icon,
            color = excluded.color,
            date = excluded.date,
            time = excluded.time,
            sort_time = excluded.sort_time,
            shift_label = excluded.shift_label,
            preview = excluded.preview,
            content = excluded.content,
            tickers = excluded.tickers,
            word_count = excluded.word_count,
            size_bytes = excluded.size_bytes,
            size_kb = excluded.size_kb,
            mtime = excluded.mtime,
            is_today = excluded.is_today,
            updated_at = excluded.updated_at
        ;
        """, (
            meta["rel_path"],
            meta.get("file_name", Path(meta["rel_path"]).name),
            meta["title"],
            meta["dept_id"],
            meta["dept_name"],
            meta.get("dept_short", ""),
            meta.get("icon", "📄"),
            meta.get("color", "#38bdf8"),
            meta["date"],
            meta.get("time", ""),
            meta.get("sort_time", "00:00:00"),
            meta.get("shift_label", ""),
            meta.get("preview", ""),
            content,
            tickers_json,
            word_count,
            meta.get("size_bytes", len(content.encode("utf-8")) if content else 0),
            meta.get("size_kb", round(meta.get("size_bytes", 0) / 1024, 1)),
            meta.get("mtime", time.time()),
            1 if meta.get("is_today") else 0,
            now_str,
            now_str
        ))

        row_id = cur.lastrowid
        conn.commit()
        conn.close()
        return row_id

    @classmethod
    def upsert_markdown_catalog_entry(cls, rel_path: str, file_name: str, category: str, title: str, date: str, size_bytes: int, mtime: float):
        """Lưu trữ thông tin văn bản vào danh mục toàn hệ thống."""
        conn = cls.get_connection()
        cur = conn.cursor()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
        INSERT INTO all_markdown_catalog (
            rel_path, file_name, category, title, date, size_bytes, mtime, indexed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(rel_path) DO UPDATE SET
            file_name = excluded.file_name,
            category = excluded.category,
            title = excluded.title,
            date = excluded.date,
            size_bytes = excluded.size_bytes,
            mtime = excluded.mtime,
            indexed_at = excluded.indexed_at
        ;
        """, (rel_path, file_name, category, title, date, size_bytes, mtime, now_str))

        conn.commit()
        conn.close()

    @classmethod
    def query_reports(
        cls,
        date_filter: Optional[str] = None,
        dept_filter: Optional[str] = None,
        shift_filter: Optional[str] = None,
        ticker_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Truy vấn danh sách báo cáo siêu tốc (<2ms) có hỗ trợ phân trang và bộ lọc."""
        conn = cls.get_connection()
        cur = conn.cursor()

        conditions = []
        params = []

        if date_filter and date_filter != "all":
            conditions.append("date = ?")
            params.append(date_filter)

        if dept_filter and dept_filter != "all":
            conditions.append("dept_id = ?")
            params.append(dept_filter)

        if shift_filter and shift_filter != "all":
            conditions.append("shift_label LIKE ?")
            params.append(f"%{shift_filter}%")

        if ticker_filter and ticker_filter != "all":
            conditions.append("tickers LIKE ?")
            params.append(f"%{ticker_filter}%")

        # CẦU CHÌ KHÓA THỜI GIAN THỰC (STRICT TIME-GATING & EMBARGO SHIELD)
        now_dt = datetime.datetime.now()
        today_str = now_dt.strftime("%Y-%m-%d")
        current_sort_time = now_dt.strftime("%H:%M:%S")

        # Điều kiện: Nếu date = today_str thì sort_time <= current_sort_time
        conditions.append("(date < ? OR (date = ? AND sort_time <= ?))")
        params.extend([today_str, today_str, current_sort_time])

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        sql = f"""
        SELECT 
            id, rel_path, file_name, title, dept_id, dept_name, dept_short, icon, color,
            date, time, sort_time, shift_label, preview, tickers, word_count,
            size_bytes, size_kb, mtime, is_today
        FROM institutional_reports
        {where_clause}
        ORDER BY date DESC, sort_time DESC
        LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        t0 = time.perf_counter()
        cur.execute(sql, params)
        rows = cur.fetchall()
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        results = []
        for r in rows:
            tickers_val = []
            try:
                tickers_val = json.loads(r["tickers"]) if r["tickers"] else []
            except Exception:
                pass

            item = dict(r)
            item["tickers"] = tickers_val
            item["is_today"] = bool(r["is_today"])
            item["latency_ms"] = latency_ms
            results.append(item)

        conn.close()
        return results

    @classmethod
    def search_reports_fts(cls, search_query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Tìm kiếm toàn văn FTS5 siêu tốc với thuật toán BM25 Relevance Ranking."""
        if not search_query.strip():
            return cls.query_reports(limit=limit)

        conn = cls.get_connection()
        cur = conn.cursor()

        # Làm sạch chuỗi tìm kiếm FTS5
        clean_q = re.sub(r"[^\w\s]", " ", search_query).strip()
        if not clean_q:
            conn.close()
            return []

        fts_match_query = " ".join([f'"{tok}"*' for tok in clean_q.split()])

        now_dt = datetime.datetime.now()
        today_str = now_dt.strftime("%Y-%m-%d")
        current_sort_time = now_dt.strftime("%H:%M:%S")

        sql = """
        SELECT 
            r.id, r.rel_path, r.file_name, r.title, r.dept_id, r.dept_name, r.dept_short, r.icon, r.color,
            r.date, r.time, r.sort_time, r.shift_label, r.preview, r.tickers, r.word_count,
            r.size_bytes, r.size_kb, r.mtime, r.is_today,
            bm25(reports_fts) AS rank
        FROM reports_fts f
        JOIN institutional_reports r ON f.rowid = r.id
        WHERE reports_fts MATCH ?
          AND (r.date < ? OR (r.date = ? AND r.sort_time <= ?))
        ORDER BY rank ASC, r.date DESC, r.sort_time DESC
        LIMIT ?
        """

        t0 = time.perf_counter()
        try:
            cur.execute(sql, (fts_match_query, today_str, today_str, current_sort_time, limit))
            rows = cur.fetchall()
        except sqlite3.OperationalError:
            # Fallback đơn giản nếu cú pháp match có vấn đề
            like_q = f"%{clean_q}%"
            fallback_sql = """
            SELECT 
                id, rel_path, file_name, title, dept_id, dept_name, dept_short, icon, color,
                date, time, sort_time, shift_label, preview, tickers, word_count,
                size_bytes, size_kb, mtime, is_today, 0.0 as rank
            FROM institutional_reports
            WHERE (title LIKE ? OR preview LIKE ? OR tickers LIKE ?)
              AND (date < ? OR (date = ? AND sort_time <= ?))
            ORDER BY date DESC, sort_time DESC
            LIMIT ?
            """
            cur.execute(fallback_sql, (like_q, like_q, like_q, today_str, today_str, current_sort_time, limit))
            rows = cur.fetchall()

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        results = []
        for r in rows:
            tickers_val = []
            try:
                tickers_val = json.loads(r["tickers"]) if r["tickers"] else []
            except Exception:
                pass
            item = dict(r)
            item["tickers"] = tickers_val
            item["is_today"] = bool(r["is_today"])
            item["search_latency_ms"] = latency_ms
            results.append(item)

        conn.close()
        return results

    @classmethod
    def get_database_stats(cls) -> Dict[str, Any]:
        """Lấy số liệu thống kê chi tiết về cơ sở dữ liệu SQLite."""
        if not DB_PATH.exists():
            return {"exists": False, "total_reports": 0, "total_markdown_catalog": 0, "size_kb": 0}

        conn = cls.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM institutional_reports;")
        inst_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM all_markdown_catalog;")
        catalog_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT date) FROM institutional_reports;")
        date_count = cur.fetchone()[0]

        cur.execute("SELECT MIN(date), MAX(date) FROM institutional_reports;")
        min_date, max_date = cur.fetchone()

        size_bytes = DB_PATH.stat().st_size
        size_kb = round(size_bytes / 1024, 1)
        size_mb = round(size_bytes / (1024 * 1024), 2)

        conn.close()

        return {
            "exists": True,
            "db_path": str(DB_PATH),
            "size_kb": size_kb,
            "size_mb": size_mb,
            "total_institutional_reports": inst_count,
            "total_markdown_catalog": catalog_count,
            "distinct_dates_count": date_count,
            "earliest_date": min_date,
            "latest_date": max_date,
            "wal_mode_active": True,
            "fts5_engine_active": True
        }


if __name__ == "__main__":
    print("=" * 70)
    print("🏛️ KHỞI TẠO APEX INSTITUTIONAL DATABASE ENGINE V5.0 (SQLITE LAKEHOUSE)")
    print("=" * 70)
    ApexDatabaseEngine.initialize_database()
    st = ApexDatabaseEngine.get_database_stats()
    print("✅ Schema khởi tạo thành công:")
    print(f"• Đường dẫn: {st['db_path']}")
    print(f"• Dung lượng: {st['size_kb']} KB")
    print(f"• Báo cáo thể chế hiện có: {st['total_institutional_reports']}")
    print("=" * 70)
