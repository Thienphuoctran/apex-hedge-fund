#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX CLOUD DB PERSISTENCE & SUPABASE POSTGRES BRIDGE (PHASE 2.3)
File: scripts/apex_cloud_db_sync.py
Cơ quan chủ quản: Master CIO James (Ban 8) & Palmer Architecture

Nhiệm vụ:
1. Đồng bộ bền vững SSOT (current_portfolio_state.json), nhật ký chỉ thị War-Room,
   báo cáo Live Intraday, lịch sử tín hiệu Slippage Tracker và Global Spillover
   lên Supabase PostgreSQL (qua PostgREST HTTPS API - 0 phụ thuộc driver ngoài).
2. Tự động khôi phục (hydrate) trạng thái mới nhất từ Cloud DB khi Render container
   khởi động lại (chống mất dữ liệu trên ephemeral disk).
3. Luôn sao lưu song song vào SQLite Vault cục bộ (data/apex_institutional_vault.db)
   để hệ thống vận hành 100% bền vững ngay cả khi chưa cấu hình Supabase hoặc offline.
"""

import sys
import os
import json
import sqlite3
import datetime
import threading
import urllib.request
import urllib.error
import urllib.parse
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
VAULT_DB_PATH = DATA_DIR / "apex_institutional_vault.db"
CLOUD_SYNC_STATE_FILE = DATA_DIR / "apex_cloud_db_status.json"

_SYNC_LOCK = threading.Lock()
_SQLITE_INIT_DONE = False


def _read_dotenv_fallback(keys: List[str]) -> Dict[str, str]:
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


def _get_supabase_credentials() -> Dict[str, str]:
    target_keys = [
        "SUPABASE_URL",
        "APEX_SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "APEX_SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_SECRET_KEY",
    ]
    env_vals = {k: os.environ.get(k, "").strip() for k in target_keys if os.environ.get(k, "").strip()}
    if not env_vals:
        env_vals = _read_dotenv_fallback(target_keys)
    url = (env_vals.get("SUPABASE_URL") or env_vals.get("APEX_SUPABASE_URL") or "").rstrip("/")
    key = (
        env_vals.get("SUPABASE_SERVICE_ROLE_KEY")
        or env_vals.get("APEX_SUPABASE_SERVICE_ROLE_KEY")
        or env_vals.get("SUPABASE_SECRET_KEY")
        or ""
    )
    return {"url": url, "key": key}


def _ensure_local_tables() -> None:
    global _SQLITE_INIT_DONE
    if _SQLITE_INIT_DONE:
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(VAULT_DB_PATH, timeout=10) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS cloud_ssot_snapshots (
                account_id TEXT PRIMARY KEY,
                cash_balance_vnd REAL,
                total_nav_vnd REAL,
                state_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cloud_war_room_directives (
                id TEXT PRIMARY KEY,
                trading_date TEXT NOT NULL,
                timestamp_str TEXT,
                sender TEXT,
                role TEXT,
                type TEXT,
                content TEXT,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_cloud_wr_dir_date
                ON cloud_war_room_directives(trading_date);
            CREATE TABLE IF NOT EXISTS cloud_live_intraday_reports (
                report_key TEXT PRIMARY KEY,
                trading_date TEXT NOT NULL,
                regime_id TEXT,
                vn_index REAL,
                total_nav_vnd REAL,
                cash_vnd REAL,
                markdown_content TEXT,
                snapshot_json TEXT,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cloud_signal_tracker (
                signal_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                signal_date TEXT NOT NULL,
                signal_type TEXT,
                signal_price REAL,
                executed_price REAL,
                slippage_bps REAL,
                t3_return_pct REAL,
                t5_return_pct REAL,
                outcome TEXT,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cloud_spillover_snapshots (
                snapshot_date TEXT PRIMARY KEY,
                risk_multiplier REAL,
                max_allocation_pct INTEGER,
                overnight_bias TEXT,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS apex_v6_intelligence_snapshots (
                snapshot_key TEXT PRIMARY KEY,
                pillar_type TEXT NOT NULL,
                trading_date TEXT NOT NULL,
                total_tickers INTEGER DEFAULT 0,
                maturity_score REAL DEFAULT 0.0,
                collective_iq REAL DEFAULT 0.0,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS apex_live_catalyst_alerts (
                alert_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                market TEXT DEFAULT 'VN',
                is_holding INTEGER DEFAULT 0,
                priority TEXT DEFAULT 'ALPHA_CATALYST',
                category TEXT DEFAULT 'MARKET_GENERAL',
                estimated_fair_value_impact_pct REAL DEFAULT 0.0,
                recommended_action TEXT DEFAULT 'HOLD_AND_MONITOR',
                title TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                detected_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS apex_enterprise_work_sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                trigger_source TEXT NOT NULL DEFAULT 'CHAIRMAN_DIRECTIVE',
                target_ticker TEXT,
                directive TEXT NOT NULL,
                final_verdict TEXT NOT NULL,
                quorum_count INTEGER NOT NULL DEFAULT 14,
                packet_count INTEGER NOT NULL DEFAULT 0,
                dissent_count INTEGER NOT NULL DEFAULT 0,
                veto_triggered INTEGER NOT NULL DEFAULT 0,
                ombudsman_audit_score TEXT NOT NULL DEFAULT '10/10',
                constitutional_seal_sha256 TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
    _SQLITE_INIT_DONE = True


def _postgrest_request(
    method: str,
    table: str,
    payload: Optional[Any] = None,
    query_params: str = "",
    timeout: int = 5,
) -> Optional[Any]:
    creds = _get_supabase_credentials()
    if not creds["url"] or not creds["key"]:
        return None
    endpoint = f"{creds['url']}/rest/v1/{table}"
    if query_params:
        endpoint = f"{endpoint}?{query_params}"

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    headers = {
        "apikey": creds["key"],
        "Authorization": f"Bearer {creds['key']}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if method in ("POST", "PATCH"):
        headers["Prefer"] = "resolution=merge-duplicates,return=minimal"

    req = urllib.request.Request(endpoint, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace").strip()
        if not raw:
            return {"ok": True}
        return json.loads(raw)


def _record_sync_telemetry(target: str, cloud_ok: bool, detail: str = "") -> None:
    now_str = datetime.datetime.now(datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=7))
    ).strftime("%Y-%m-%d %H:%M:%S")
    creds = _get_supabase_credentials()
    status_obj = {
        "supabase_configured": bool(creds["url"] and creds["key"]),
        "local_sqlite_mirror": True,
        "last_target": target,
        "last_cloud_sync_ok": cloud_ok,
        "last_sync_at": now_str,
        "detail": detail[:240],
    }
    try:
        CLOUD_SYNC_STATE_FILE.write_text(
            json.dumps(status_obj, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


class ApexCloudDBSync:
    """Bộ điều phối đồng bộ Cloud DB (Supabase PostgREST) + Local SQLite Mirror."""

    @classmethod
    def get_cloud_status(cls, lightweight: bool = False) -> Dict[str, Any]:
        if not lightweight:
            _ensure_local_tables()
        creds = _get_supabase_credentials()
        configured = bool(creds["url"] and creds["key"])
        telemetry = {}
        if CLOUD_SYNC_STATE_FILE.exists():
            try:
                telemetry = json.loads(CLOUD_SYNC_STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "mode": "SUPABASE_POSTGRES_PLUS_SQLITE" if configured else "LOCAL_SQLITE_VAULT_MIRROR",
            "supabase_configured": configured,
            "local_sqlite_mirror": True,
            "vault_db_exists": VAULT_DB_PATH.exists(),
            "last_sync_at": telemetry.get("last_sync_at", ""),
            "last_cloud_sync_ok": telemetry.get("last_cloud_sync_ok", None),
            "last_target": telemetry.get("last_target", ""),
        }

    @classmethod
    def sync_ssot(cls, state: Dict[str, Any]) -> bool:
        if not isinstance(state, dict) or not state.get("account_id"):
            return False
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        account_id = str(state.get("account_id", "105C307855"))
        cash_val = float(state.get("cash_balance_vnd", 0.0))
        nav_val = float(state.get("total_nav_vnd", cash_val))
        mkt_val = float(state.get("total_market_val_vnd", 0.0))
        real_pnl = float(state.get("realized_pnl_vnd", 0.0))
        unreal_pnl = float(state.get("unrealized_pnl_vnd", 0.0))
        state_str = json.dumps(state, ensure_ascii=False)

        with _SYNC_LOCK:
            _ensure_local_tables()
            try:
                with sqlite3.connect(VAULT_DB_PATH, timeout=10) as conn:
                    conn.execute(
                        """
                        INSERT INTO cloud_ssot_snapshots (account_id, cash_balance_vnd, total_nav_vnd, state_json, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(account_id) DO UPDATE SET
                            cash_balance_vnd = excluded.cash_balance_vnd,
                            total_nav_vnd = excluded.total_nav_vnd,
                            state_json = excluded.state_json,
                            updated_at = excluded.updated_at
                        """,
                        (account_id, cash_val, nav_val, state_str, now_iso),
                    )
            except Exception as e:
                print(f"[!] CloudDB Local SQLite SSOT sync error: {e}")

            cloud_ok = False
            detail = "local-sqlite-only"
            try:
                res = _postgrest_request(
                    "POST",
                    "apex_portfolio_ssot",
                    payload={
                        "account_id": account_id,
                        "chairman": str(state.get("chairman", "Trần Quốc Thiên Phước")),
                        "status": str(state.get("status", "ACTIVE_HOLDING")),
                        "cash_balance_vnd": cash_val,
                        "total_nav_vnd": nav_val,
                        "total_market_val_vnd": mkt_val,
                        "realized_pnl_vnd": real_pnl,
                        "unrealized_pnl_vnd": unreal_pnl,
                        "state_json": state,
                        "updated_at": now_iso,
                    },
                    query_params="on_conflict=account_id",
                )
                if res is not None:
                    cloud_ok = True
                    detail = "supabase-synced"
            except Exception as e:
                detail = f"supabase-err: {e}"
            _record_sync_telemetry("apex_portfolio_ssot", cloud_ok, detail)
            return True

    @classmethod
    def restore_ssot_if_newer(cls, local_state: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Nếu Supabase Postgres có bản SSOT mới hơn bản trên đĩa Render (ephemeral), tự động khôi phục."""
        creds = _get_supabase_credentials()
        if not creds["url"] or not creds["key"]:
            return None
        try:
            acct = (local_state or {}).get("account_id", "105C307855")
            rows = _postgrest_request(
                "GET",
                "apex_portfolio_ssot",
                query_params=f"account_id=eq.{urllib.parse.quote(acct)}&select=state_json,updated_at&limit=1",
            )
            if not isinstance(rows, list) or not rows:
                return None
            remote_state = rows[0].get("state_json")
            if not isinstance(remote_state, dict):
                return None
            local_ts = str((local_state or {}).get("last_updated", ""))
            remote_ts = str(remote_state.get("last_updated", ""))
            if not local_state or (remote_ts and remote_ts > local_ts):
                _record_sync_telemetry("apex_portfolio_ssot_restore", True, f"restored {remote_ts}")
                return remote_state
        except Exception:
            pass
        return None

    @classmethod
    def sync_directive(cls, entry: Dict[str, Any], trading_date: str) -> bool:
        if not isinstance(entry, dict) or not entry.get("id"):
            return False
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with _SYNC_LOCK:
            _ensure_local_tables()
            try:
                with sqlite3.connect(VAULT_DB_PATH, timeout=10) as conn:
                    conn.execute(
                        """
                        INSERT INTO cloud_war_room_directives (id, trading_date, timestamp_str, sender, role, type, content, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET content = excluded.content
                        """,
                        (
                            str(entry.get("id")),
                            trading_date,
                            str(entry.get("timestamp", "")),
                            str(entry.get("sender", "")),
                            str(entry.get("role", "specialist")),
                            str(entry.get("type", "directive")),
                            str(entry.get("content", "")),
                            now_iso,
                        ),
                    )
            except Exception:
                pass

            cloud_ok = False
            detail = "local-sqlite-only"
            try:
                res = _postgrest_request(
                    "POST",
                    "apex_war_room_directives",
                    payload={
                        "id": str(entry.get("id")),
                        "trading_date": trading_date,
                        "timestamp_str": str(entry.get("timestamp", "")),
                        "sender": str(entry.get("sender", "")),
                        "role": str(entry.get("role", "specialist")),
                        "type": str(entry.get("type", "directive")),
                        "content": str(entry.get("content", "")),
                        "created_at": now_iso,
                    },
                    query_params="on_conflict=id",
                )
                if res is not None:
                    cloud_ok = True
                    detail = "supabase-synced"
            except Exception as e:
                detail = f"supabase-err: {e}"
            _record_sync_telemetry("apex_war_room_directives", cloud_ok, detail)
            return True

    @classmethod
    def restore_directives_if_missing(cls, trading_date: str) -> Optional[List[Dict[str, Any]]]:
        creds = _get_supabase_credentials()
        if not creds["url"] or not creds["key"]:
            return None
        try:
            rows = _postgrest_request(
                "GET",
                "apex_war_room_directives",
                query_params=f"trading_date=eq.{urllib.parse.quote(trading_date)}&order=created_at.asc",
            )
            if isinstance(rows, list) and rows:
                return [
                    {
                        "id": r.get("id", ""),
                        "timestamp": r.get("timestamp_str", ""),
                        "sender": r.get("sender", ""),
                        "role": r.get("role", "specialist"),
                        "type": r.get("type", "directive"),
                        "content": r.get("content", ""),
                    }
                    for r in rows
                ]
        except Exception:
            pass
        return None

    @classmethod
    def sync_live_report(cls, snapshot: Dict[str, Any], markdown_content: str) -> bool:
        trading_date = str(snapshot.get("trading_date", ""))
        if not trading_date:
            return False
        report_key = f"{trading_date}_Live_Intraday_Report"
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        regime_id = str(snapshot.get("regime", {}).get("regime_id", "SIDEWAY_CHOPPY"))
        vni_val = float(snapshot.get("market_overview", {}).get("vn_index", {}).get("value", 0.0))
        vs = snapshot.get("victor_sentinel", {})
        nav_val = float(vs.get("total_nav_vnd", 0.0))
        cash_val = float(vs.get("cash_vnd", 0.0))

        with _SYNC_LOCK:
            _ensure_local_tables()
            try:
                with sqlite3.connect(VAULT_DB_PATH, timeout=10) as conn:
                    conn.execute(
                        """
                        INSERT INTO cloud_live_intraday_reports (
                            report_key, trading_date, regime_id, vn_index, total_nav_vnd,
                            cash_vnd, markdown_content, snapshot_json, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(report_key) DO UPDATE SET
                            regime_id = excluded.regime_id,
                            vn_index = excluded.vn_index,
                            total_nav_vnd = excluded.total_nav_vnd,
                            cash_vnd = excluded.cash_vnd,
                            markdown_content = excluded.markdown_content,
                            snapshot_json = excluded.snapshot_json,
                            updated_at = excluded.updated_at
                        """,
                        (
                            report_key,
                            trading_date,
                            regime_id,
                            vni_val,
                            nav_val,
                            cash_val,
                            markdown_content,
                            json.dumps(snapshot, ensure_ascii=False),
                            now_iso,
                        ),
                    )
            except Exception:
                pass

            cloud_ok = False
            detail = "local-sqlite-only"
            try:
                res = _postgrest_request(
                    "POST",
                    "apex_live_intraday_reports",
                    payload={
                        "report_key": report_key,
                        "trading_date": trading_date,
                        "regime_id": regime_id,
                        "vn_index": vni_val,
                        "total_nav_vnd": nav_val,
                        "cash_vnd": cash_val,
                        "markdown_content": markdown_content,
                        "snapshot_json": snapshot,
                        "updated_at": now_iso,
                    },
                    query_params="on_conflict=report_key",
                )
                if res is not None:
                    cloud_ok = True
                    detail = "supabase-synced"
            except Exception as e:
                detail = f"supabase-err: {e}"
            _record_sync_telemetry("apex_live_intraday_reports", cloud_ok, detail)
            return True

    @classmethod
    def sync_signal(cls, signal_record: Dict[str, Any]) -> bool:
        if not isinstance(signal_record, dict) or not signal_record.get("signal_id"):
            return False
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sig_id = str(signal_record["signal_id"])
        with _SYNC_LOCK:
            _ensure_local_tables()
            try:
                with sqlite3.connect(VAULT_DB_PATH, timeout=10) as conn:
                    conn.execute(
                        """
                        INSERT INTO cloud_signal_tracker (
                            signal_id, symbol, signal_date, signal_type, signal_price,
                            executed_price, slippage_bps, t3_return_pct, t5_return_pct,
                            outcome, payload_json, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(signal_id) DO UPDATE SET
                            executed_price = excluded.executed_price,
                            slippage_bps = excluded.slippage_bps,
                            t3_return_pct = excluded.t3_return_pct,
                            t5_return_pct = excluded.t5_return_pct,
                            outcome = excluded.outcome,
                            payload_json = excluded.payload_json,
                            updated_at = excluded.updated_at
                        """,
                        (
                            sig_id,
                            str(signal_record.get("symbol", "")),
                            str(signal_record.get("signal_date", "")),
                            str(signal_record.get("signal_type", "")),
                            float(signal_record.get("signal_price", 0.0)),
                            signal_record.get("executed_price"),
                            signal_record.get("slippage_bps"),
                            signal_record.get("t3_return_pct"),
                            signal_record.get("t5_return_pct"),
                            str(signal_record.get("outcome", "PENDING")),
                            json.dumps(signal_record, ensure_ascii=False),
                            now_iso,
                        ),
                    )
            except Exception:
                pass

            cloud_ok = False
            detail = "local-sqlite-only"
            try:
                res = _postgrest_request(
                    "POST",
                    "apex_signal_slippage_tracker",
                    payload={
                        "signal_id": sig_id,
                        "symbol": str(signal_record.get("symbol", "")),
                        "signal_date": str(signal_record.get("signal_date", "")),
                        "signal_time": str(signal_record.get("signal_time", "")),
                        "signal_type": str(signal_record.get("signal_type", "")),
                        "signal_price": float(signal_record.get("signal_price", 0.0)),
                        "buy_up_pct": float(signal_record.get("buy_up_pct", 50.0)),
                        "rsi14": float(signal_record.get("rsi14", 50.0)),
                        "breadth_pct": float(signal_record.get("breadth_pct", 50.0)),
                        "regime_id": str(signal_record.get("regime_id", "SIDEWAY_CHOPPY")),
                        "executed_price": signal_record.get("executed_price"),
                        "slippage_bps": signal_record.get("slippage_bps"),
                        "t3_price": signal_record.get("t3_price"),
                        "t3_return_pct": signal_record.get("t3_return_pct"),
                        "t5_price": signal_record.get("t5_price"),
                        "t5_return_pct": signal_record.get("t5_return_pct"),
                        "outcome": str(signal_record.get("outcome", "PENDING")),
                        "meta_json": signal_record,
                        "updated_at": now_iso,
                    },
                    query_params="on_conflict=signal_id",
                )
                if res is not None:
                    cloud_ok = True
                    detail = "supabase-synced"
            except Exception as e:
                detail = f"supabase-err: {e}"
            _record_sync_telemetry("apex_signal_slippage_tracker", cloud_ok, detail)
            return True

    @classmethod
    def sync_spillover(cls, spillover_data: Dict[str, Any]) -> bool:
        snap_date = str(spillover_data.get("snapshot_date", ""))
        if not snap_date:
            return False
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with _SYNC_LOCK:
            _ensure_local_tables()
            try:
                with sqlite3.connect(VAULT_DB_PATH, timeout=10) as conn:
                    conn.execute(
                        """
                        INSERT INTO cloud_spillover_snapshots (
                            snapshot_date, risk_multiplier, max_allocation_pct, overnight_bias, payload_json, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(snapshot_date) DO UPDATE SET
                            risk_multiplier = excluded.risk_multiplier,
                            max_allocation_pct = excluded.max_allocation_pct,
                            overnight_bias = excluded.overnight_bias,
                            payload_json = excluded.payload_json,
                            updated_at = excluded.updated_at
                        """,
                        (
                            snap_date,
                            float(spillover_data.get("risk_multiplier", 1.0)),
                            int(spillover_data.get("max_allocation_pct", 40)),
                            str(spillover_data.get("overnight_bias", "NEUTRAL_SELECTIVE")),
                            json.dumps(spillover_data, ensure_ascii=False),
                            now_iso,
                        ),
                    )
            except Exception:
                pass

            cloud_ok = False
            detail = "local-sqlite-only"
            try:
                res = _postgrest_request(
                    "POST",
                    "apex_global_spillover_snapshots",
                    payload={
                        "snapshot_date": snap_date,
                        "risk_multiplier": float(spillover_data.get("risk_multiplier", 1.0)),
                        "max_allocation_pct": int(spillover_data.get("max_allocation_pct", 40)),
                        "overnight_bias": str(spillover_data.get("overnight_bias", "NEUTRAL_SELECTIVE")),
                        "payload_json": spillover_data,
                        "updated_at": now_iso,
                    },
                    query_params="on_conflict=snapshot_date",
                )
                if res is not None:
                    cloud_ok = True
                    detail = "supabase-synced"
            except Exception as e:
                detail = f"supabase-err: {e}"
            _record_sync_telemetry("apex_global_spillover_snapshots", cloud_ok, detail)
            return True

    @classmethod
    def sync_v6_intelligence_to_vault(cls) -> Dict[str, Any]:
        """V6.0 Nâng cấp 4: Đồng bộ Deep Financial Brain, Evolution/Legends, BCTC Updates & Catalyst Alerts vào Vault."""
        now_ict = datetime.datetime.now(datetime.timezone.utc).astimezone(
            datetime.timezone(datetime.timedelta(hours=7))
        )
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        today_str = now_ict.strftime("%Y-%m-%d")

        def _read_j(p: Path) -> Dict[str, Any]:
            if not p.exists():
                return {}
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return {}

        deep_brain = _read_j(DATA_DIR / "deep_financial_brain_analysis.json")
        evo_state = _read_j(DATA_DIR / "system_evolution_and_legends_state.json") or _read_j(DATA_DIR / "legend_investor_wisdom_vault.json")
        bctc_upd = _read_j(DATA_DIR / "live_bctc_quarterly_updates.json")
        alerts_data = _read_j(DATA_DIR / "live_catalyst_alerts.json")

        iq_block = (evo_state.get("self_reflection") or {}).get("system_maturity_iq", {})
        mat_score = float(iq_block.get("maturity_score", 0.0) or 0.0)
        col_iq = float(iq_block.get("collective_iq", 0.0) or 0.0)

        snapshots = [
            (
                f"{today_str}_DEEP_FINANCIAL_BRAIN",
                "DEEP_FINANCIAL_BRAIN",
                int(deep_brain.get("total_analyzed", 0) or 0),
                mat_score,
                col_iq,
                deep_brain,
            ),
            (
                f"{today_str}_EVOLUTION_AND_LEGENDS",
                "EVOLUTION_AND_LEGENDS",
                int(evo_state.get("total_legends", 15) or 15),
                mat_score,
                col_iq,
                evo_state,
            ),
            (
                f"{today_str}_LIVE_BCTC_UPDATES",
                "LIVE_BCTC_UPDATES",
                int(bctc_upd.get("total_tickers_updated", 0) or 0),
                mat_score,
                col_iq,
                bctc_upd,
            ),
        ]

        alerts_list = alerts_data.get("alerts", []) if isinstance(alerts_data.get("alerts"), list) else []
        snapshots_saved = 0
        alerts_saved = 0

        with _SYNC_LOCK:
            _ensure_local_tables()
            try:
                with sqlite3.connect(VAULT_DB_PATH, timeout=10) as conn:
                    for snap_key, pillar, cnt, ms, ciq, payload in snapshots:
                        if not payload:
                            continue
                        conn.execute(
                            """
                            INSERT INTO apex_v6_intelligence_snapshots (
                                snapshot_key, pillar_type, trading_date, total_tickers,
                                maturity_score, collective_iq, payload_json, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(snapshot_key) DO UPDATE SET
                                total_tickers = excluded.total_tickers,
                                maturity_score = excluded.maturity_score,
                                collective_iq = excluded.collective_iq,
                                payload_json = excluded.payload_json,
                                updated_at = excluded.updated_at
                            """,
                            (snap_key, pillar, today_str, cnt, ms, ciq, json.dumps(payload, ensure_ascii=False), now_iso),
                        )
                        snapshots_saved += 1

                    for al in alerts_list[:40]:
                        aid = str(al.get("alert_id", ""))
                        if not aid:
                            continue
                        conn.execute(
                            """
                            INSERT INTO apex_live_catalyst_alerts (
                                alert_id, symbol, market, is_holding, priority, category,
                                estimated_fair_value_impact_pct, recommended_action, title, payload_json, detected_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(alert_id) DO UPDATE SET
                                priority = excluded.priority,
                                estimated_fair_value_impact_pct = excluded.estimated_fair_value_impact_pct,
                                recommended_action = excluded.recommended_action,
                                payload_json = excluded.payload_json,
                                detected_at = excluded.detected_at
                            """,
                            (
                                aid,
                                str(al.get("symbol", "")),
                                str(al.get("market", "VN")),
                                1 if al.get("is_holding") else 0,
                                str(al.get("priority", "ALPHA_CATALYST")),
                                str(al.get("category", "MARKET_GENERAL")),
                                float(al.get("estimated_fair_value_impact_pct", 0.0) or 0.0),
                                str(al.get("recommended_action", "HOLD_AND_MONITOR")),
                                str(al.get("title", "")),
                                json.dumps(al, ensure_ascii=False),
                                now_iso,
                            ),
                        )
                        alerts_saved += 1
            except Exception as e:
                print(f"[!] CloudDB V6 SQLite sync error: {e}")

            cloud_ok = False
            detail = "local-sqlite-only"
            try:
                for snap_key, pillar, cnt, ms, ciq, payload in snapshots:
                    if not payload:
                        continue
                    res = _postgrest_request(
                        "POST",
                        "apex_v6_intelligence_snapshots",
                        payload={
                            "snapshot_key": snap_key,
                            "pillar_type": pillar,
                            "trading_date": today_str,
                            "total_tickers": cnt,
                            "maturity_score": ms,
                            "collective_iq": ciq,
                            "payload_json": payload,
                            "updated_at": now_iso,
                        },
                        query_params="on_conflict=snapshot_key",
                    )
                    if res is not None:
                        cloud_ok = True
                        detail = "supabase-synced"
                if alerts_list:
                    alert_rows = [
                        {
                            "alert_id": str(al.get("alert_id", "")),
                            "symbol": str(al.get("symbol", "")),
                            "market": str(al.get("market", "VN")),
                            "is_holding": bool(al.get("is_holding")),
                            "priority": str(al.get("priority", "ALPHA_CATALYST")),
                            "category": str(al.get("category", "MARKET_GENERAL")),
                            "estimated_fair_value_impact_pct": float(al.get("estimated_fair_value_impact_pct", 0.0) or 0.0),
                            "recommended_action": str(al.get("recommended_action", "HOLD_AND_MONITOR")),
                            "title": str(al.get("title", "")),
                            "payload_json": al,
                            "detected_at": now_iso,
                        }
                        for al in alerts_list[:40]
                        if al.get("alert_id")
                    ]
                    if alert_rows:
                        _postgrest_request(
                            "POST",
                            "apex_live_catalyst_alerts",
                            payload=alert_rows,
                            query_params="on_conflict=alert_id",
                        )
            except Exception as e:
                detail = f"supabase-err: {e}"
            _record_sync_telemetry("apex_v6_intelligence_snapshots", cloud_ok, detail)
            return {
                "ok": True,
                "snapshots_saved": snapshots_saved,
                "alerts_saved": alerts_saved,
                "cloud_synced": cloud_ok,
                "detail": detail,
            }

    @classmethod
    def sync_enterprise_session(cls, session_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Đồng bộ phiên làm việc Doanh Nghiệp Sống V7.0 lên SQLite Vault Mirror & Supabase Cloud DB."""
        if not isinstance(session_payload, dict) or not session_payload.get("session_id"):
            return {"ok": False, "detail": "invalid-enterprise-session-payload"}
        with _SYNC_LOCK:
            _ensure_local_tables()
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            sid = str(session_payload["session_id"])
            created_at = str(session_payload.get("created_at") or now_iso)
            trigger_src = str(session_payload.get("trigger_source") or "CHAIRMAN_DIRECTIVE")
            ticker = str(session_payload.get("target_ticker") or "")
            directive = str(session_payload.get("directive") or "")
            verdict = str(session_payload.get("final_verdict") or "")
            quorum = int(session_payload.get("quorum_count") or 14)
            pkt_cnt = int(session_payload.get("packet_count") or 0)
            dis_cnt = int(session_payload.get("dissent_count") or 0)
            veto_flag = bool(session_payload.get("veto_triggered"))
            audit_score = str(session_payload.get("ombudsman_audit_score") or "10/10")
            seal_sha = str(session_payload.get("constitutional_seal_sha256") or "")

            local_saved = False
            try:
                with sqlite3.connect(VAULT_DB_PATH, timeout=15) as conn:
                    conn.execute(
                        """
                        INSERT INTO apex_enterprise_work_sessions (
                            session_id, created_at, trigger_source, target_ticker, directive,
                            final_verdict, quorum_count, packet_count, dissent_count, veto_triggered,
                            ombudsman_audit_score, constitutional_seal_sha256, payload_json, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(session_id) DO UPDATE SET
                            final_verdict=excluded.final_verdict,
                            quorum_count=excluded.quorum_count,
                            packet_count=excluded.packet_count,
                            dissent_count=excluded.dissent_count,
                            veto_triggered=excluded.veto_triggered,
                            ombudsman_audit_score=excluded.ombudsman_audit_score,
                            constitutional_seal_sha256=excluded.constitutional_seal_sha256,
                            payload_json=excluded.payload_json,
                            updated_at=excluded.updated_at
                        """,
                        (
                            sid, created_at, trigger_src, ticker or None, directive,
                            verdict, quorum, pkt_cnt, dis_cnt, 1 if veto_flag else 0,
                            audit_score, seal_sha, json.dumps(session_payload, ensure_ascii=False), now_iso,
                        ),
                    )
                    local_saved = True
            except Exception as e:
                print(f"[!] CloudDB V7 SQLite sync error: {e}")

            cloud_ok = False
            detail = "local-sqlite-only"
            try:
                res = _postgrest_request(
                    "POST",
                    "apex_enterprise_work_sessions",
                    payload={
                        "session_id": sid,
                        "created_at": created_at,
                        "trigger_source": trigger_src,
                        "target_ticker": ticker or None,
                        "directive": directive,
                        "final_verdict": verdict,
                        "quorum_count": quorum,
                        "packet_count": pkt_cnt,
                        "dissent_count": dis_cnt,
                        "veto_triggered": veto_flag,
                        "ombudsman_audit_score": audit_score,
                        "constitutional_seal_sha256": seal_sha,
                        "payload_json": session_payload,
                        "updated_at": now_iso,
                    },
                    query_params="on_conflict=session_id",
                )
                if res is not None:
                    cloud_ok = True
                    detail = "supabase-synced"
            except Exception as e:
                detail = f"supabase-err: {e}"

            _record_sync_telemetry("apex_enterprise_work_sessions", cloud_ok, detail)
            return {
                "ok": local_saved,
                "session_id": sid,
                "local_saved": local_saved,
                "cloud_synced": cloud_ok,
                "detail": detail,
            }


if __name__ == "__main__":
    v6_res = ApexCloudDBSync.sync_v6_intelligence_to_vault()
    print("=== APEX CLOUD DB SYNC STATUS ===")
    print(json.dumps({"v6_sync": v6_res, "status": ApexCloudDBSync.get_cloud_status()}, ensure_ascii=False, indent=2))
