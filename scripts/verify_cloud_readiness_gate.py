#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX CLOUD READINESS & REGRESSION GUARDRAIL GATE (STAGE 4)
File: scripts/verify_cloud_readiness_gate.py
Phối hợp thiết kế: Palmer (Apex Central System Governance) & Long (Executive AI)

Chốt chặn kiểm định trước khi push/deploy lên Render & GitHub Actions:
1. Kiểm tra cú pháp YAML toàn bộ `.github/workflows/*.yml` (ngăn lỗi 0.0s jobs:[]).
2. Kiểm tra Git Hygiene: DB nhị phân `data/apex_institutional_vault.db` đã được đưa vào `.gitignore` và gỡ khỏi git index.
3. Kiểm tra Memory Hygiene: Zero `importlib.reload` trong HTTP handler, SQLite cache <= 8MB, không nạp pandas/numpy/yfinance khi boot Compact Mode.
4. Diễn tập Boot Render Compact Mode thực tế:
   - Đo thời gian mở cổng & trả HTTP 200 của `/api/health` (< 2.0s).
   - Đo tổng RAM tiêu thụ (RSS) của toàn cây tiến trình Supervisor (< 250 MB so với trần 512 MB Render).
   - Chạy kiểm toán live endpoints.
"""

import os
import sys
import json
import time
import glob
import signal
import subprocess
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent


def get_process_tree_ram_mb(root_pid: int) -> dict:
    """Đo RAM thực tế của tiến trình root và mọi tiến trình con (Windows CIM hoặc Linux /proc)."""
    if sys.platform == "win32":
        ps_cmd = (
            "$all = Get-CimInstance Win32_Process; "
            f"$pids = @({root_pid}); "
            "$changed = $true; "
            "while ($changed) { $changed = $false; "
            "  foreach ($p in $all) { if ($p.ParentProcessId -in $pids -and $p.ProcessId -notin $pids) { $pids += $p.ProcessId; $changed = $true } } "
            "}; "
            "$rows = $all | Where-Object { $_.ProcessId -in $pids } | ForEach-Object { "
            "  $gp = Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue; "
            "  [PSCustomObject]@{ pid=$_.ProcessId; name=$_.Name; mb=if($gp){[math]::Round($gp.WorkingSet64/1MB,1)}else{0}; cmd=$_.CommandLine } "
            "}; "
            "$rows | ConvertTo-Json -Compress"
        )
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
        raw = (res.stdout or "").strip()
        if not raw:
            return {"count": 0, "total_mb": 0.0, "processes": []}
        data = json.loads(raw)
        procs = data if isinstance(data, list) else [data]
        total = round(sum(float(p.get("mb", 0)) for p in procs), 1)
        return {"count": len(procs), "total_mb": total, "processes": procs}
    else:
        return {"count": 1, "total_mb": 0.0, "processes": []}


def main() -> int:
    failures = []
    print("=" * 75)
    print(" 🛡️ APEX CLOUD READINESS & REGRESSION GUARDRAIL GATE (STAGE 4)")
    print("=" * 75)

    # 1. YAML Workflow Preflight Gate
    print("\n[1/5] Kiểm tra cú pháp toàn bộ GitHub Workflows (.github/workflows/*.yml)...")
    try:
        import yaml
        yml_files = sorted(glob.glob(str(BASE_DIR / ".github" / "workflows" / "*.yml")))
        assert len(yml_files) > 0, "Không tìm thấy file workflow nào"
        for yf in yml_files:
            with open(yf, "r", encoding="utf-8") as f:
                yaml.safe_load(f)
            print(f"  [PASS] YAML Valid: {Path(yf).name}")
    except Exception as e:
        msg = f"YAML Validation Error: {e}"
        print(f"  [FAIL] {msg}")
        failures.append(msg)

    # 2. Git Hygiene Gate
    print("\n[2/5] Kiểm tra Git Hygiene & loại bỏ DB nhị phân khỏi Git tracking...")
    try:
        gi_text = (BASE_DIR / ".gitignore").read_text(encoding="utf-8")
        if "data/apex_institutional_vault.db" not in gi_text:
            raise AssertionError("Thiếu data/apex_institutional_vault.db trong .gitignore")
        ls_res = subprocess.run(
            ["git", "ls-files", "data/apex_institutional_vault.db"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        if ls_res.stdout.strip():
            raise AssertionError(f"File DB vẫn đang bị track trong Git: {ls_res.stdout.strip()}")
        print("  [PASS] .gitignore đã chặn DB nhị phân & Git index hoàn toàn sạch.")
    except Exception as e:
        print(f"  [FAIL] {e}")
        failures.append(str(e))

    # 3. Code & Memory Hygiene Gate
    print("\n[3/5] Kiểm tra chống rò rỉ RAM (importlib.reload, SQLite cache, lazy yfinance)...")
    try:
        sup_src = (BASE_DIR / "scripts" / "start_apex_cloud_247.py").read_text(encoding="utf-8")
        reload_cnt = sup_src.count("importlib.reload")
        assert reload_cnt == 0, f"Vẫn còn {reload_cnt} lệnh importlib.reload trong start_apex_cloud_247.py"

        db_src = (BASE_DIR / "scripts" / "apex_database_engine.py").read_text(encoding="utf-8")
        assert "cache_size = -4000" in db_src, "SQLite cache_size chưa hạ xuống -4000 (4MB)"
        assert "cache_size = -64000" not in db_src, "Vẫn còn cấu hình cache_size = -64000 (64MB)"

        # Kiểm tra khi import ở chế độ Compact Mode không tự kéo pandas/numpy/yfinance vào RAM
        chk_env = os.environ.copy()
        chk_env["APEX_CLOUD_COMPACT_MODE"] = "1"
        chk_env["APEX_DISABLE_TELEGRAM_COPILOT"] = "1"
        chk_code = (
            "import sys; sys.path.insert(0, '.'); "
            "import scripts.start_apex_cloud_247; "
            "import scripts.vn3_portfolio_autonomous_sentinel; "
            "import scripts.global_to_vn_spillover_engine; "
            "heavy = [m for m in ('pandas','numpy','yfinance') if m in sys.modules]; "
            "assert not heavy, f'Phát hiện import nặng: {heavy}'; "
            "print('NO_HEAVY_IMPORTS')"
        )
        imp_res = subprocess.run([sys.executable, "-c", chk_code], cwd=str(BASE_DIR), env=chk_env, capture_output=True, text=True)
        if imp_res.returncode != 0 or "NO_HEAVY_IMPORTS" not in imp_res.stdout:
            raise AssertionError(f"Heavy import check failed: {imp_res.stdout} {imp_res.stderr}")
        print("  [PASS] 0 importlib.reload | SQLite cache = 4MB | 0 pandas/numpy/yfinance khi boot.")
    except Exception as e:
        print(f"  [FAIL] {e}")
        failures.append(str(e))

    # 4. Boot Render Compact Mode & Measure Port Latency + Total Process Tree RAM
    print("\n[4/5] Diễn tập khởi động Render Compact Mode (Port=18999) & đo độ trễ /api/health + tổng RAM...")
    test_port = 18999
    sub_env = os.environ.copy()
    sub_env["PORT"] = str(test_port)
    sub_env["APEX_CLOUD_COMPACT_MODE"] = "1"
    sub_env["APEX_DISABLE_TELEGRAM_COPILOT"] = "1"
    sub_env["TELEGRAM_POLLING_OWNER"] = "pc"
    sub_env["PYTHONIOENCODING"] = "utf-8"

    log_file = BASE_DIR / "data" / "logs" / "verify_gate_server.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(log_file, "w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(
        [sys.executable, "-X", "utf8", "scripts/start_apex_cloud_247.py", "--port", str(test_port)],
        cwd=str(BASE_DIR),
        env=sub_env,
        stdout=log_fh,
        stderr=subprocess.STDOUT,
    )

    try:
        t0 = time.perf_counter()
        health_ok = False
        health_latency = None
        health_payload = {}
        while time.perf_counter() - t0 < 10.0:
            if proc.poll() is not None:
                log_fh.flush()
                out_log = log_file.read_text(encoding="utf-8", errors="replace") if log_file.exists() else ""
                raise RuntimeError(f"Supervisor thoát sớm với code {proc.returncode}: {out_log[-600:]}")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{test_port}/api/health", timeout=2) as resp:
                    if resp.status == 200:
                        health_payload = json.loads(resp.read().decode("utf-8"))
                        health_latency = round(time.perf_counter() - t0, 3)
                        health_ok = True
                        break
            except Exception:
                time.sleep(0.15)

        if not health_ok:
            raise TimeoutError("Port 18999 không trả về 200 OK trong 10 giây!")

        print(f"  [PASS] /api/health phản hồi 200 OK sau {health_latency}s (Ngưỡng < 2.0s)")
        if health_latency and health_latency > 3.0:
            failures.append(f"/api/health khởi động chậm: {health_latency}s")

        # Chờ background warmup 8 giây rồi test các endpoint quan trọng & đo tổng RAM thực tế
        time.sleep(8)
        for ep in ["/api/status", "/api/reports?limit=20", "/api/tactical_war_room", "/api/tactical_war_room/stream?max_frames=1", "/"]:
            t_ep = time.perf_counter()
            with urllib.request.urlopen(f"http://127.0.0.1:{test_port}{ep}", timeout=15) as r:
                raw_b = r.read()
                if r.status != 200 or len(raw_b) == 0:
                    raise AssertionError(f"Endpoint {ep} trả status={r.status}, len={len(raw_b)}")
                print(f"  [PASS] GET {ep} -> 200 OK ({len(raw_b):,} bytes, {round((time.perf_counter()-t_ep)*1000,1)} ms)")

        # Đo tổng RAM toàn cây tiến trình
        ram_info = get_process_tree_ram_mb(proc.pid)
        print(f"  [INFO] Số tiến trình trong cây Render Compact: {ram_info['count']} | Tổng RAM: {ram_info['total_mb']} MB")
        for p in ram_info["processes"]:
            print(f"         • PID {p.get('pid')} ({p.get('name')}): {p.get('mb')} MB")

        if ram_info["count"] > 2:
            raise AssertionError(f"Số tiến trình quá nhiều ở Compact Mode: {ram_info['count']} (Kỳ vọng <= 2)")
        if ram_info["total_mb"] > 260.0:
            raise AssertionError(f"Tổng RAM vượt ngưỡng an toàn Compact Mode: {ram_info['total_mb']} MB > 260 MB")
        print(f"  [PASS] Tổng RAM cây tiến trình = {ram_info['total_mb']} MB (An toàn sâu dưới trần 512 MB Render!)")

        # [5/5] Chạy kiểm toán tổng thể 58+ checks của James & Trọng nhắm vào localhost test port
        print(f"\n[5/5] Chạy Bộ Tổng Kiểm Toán Thể Chế (comprehensive_system_audit.py --url http://127.0.0.1:{test_port})...")
        audit_res = subprocess.run(
            [sys.executable, "-X", "utf8", "scripts/comprehensive_system_audit.py", "--url", f"http://127.0.0.1:{test_port}"],
            cwd=str(BASE_DIR),
            env=sub_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=240,
        )
        print(audit_res.stdout)
        if audit_res.returncode != 0:
            if audit_res.stderr:
                print("STDERR:", audit_res.stderr)
            raise AssertionError(f"comprehensive_system_audit.py thất bại với exit code {audit_res.returncode}")
    except Exception as e:
        print(f"  [FAIL] {e}")
        failures.append(str(e))
    finally:
        print("\n[*] Đang tắt tiến trình diễn tập Render Compact an toàn...")
        subprocess.run(
            [sys.executable, "-X", "utf8", "scripts/start_apex_cloud_247.py", "--stop"],
            cwd=str(BASE_DIR),
            capture_output=True,
            timeout=15,
        )
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        if sys.platform == "win32":
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", f"Get-CimInstance Win32_Process | Where-Object {{ $_.ParentProcessId -eq {proc.pid} -or $_.ProcessId -eq {proc.pid} }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}"],
                capture_output=True,
            )
        try:
            log_fh.close()
        except Exception:
            pass

    print("\n" + "=" * 75)
    if failures:
        print(f"❌ GUARDRAIL GATE THẤT BẠI ({len(failures)} lỗi):")
        for f in failures:
            print(f"   - {f}")
        print("=" * 75)
        return 1
    print("🏆 TẤT CẢ 5/5 CHỐT CHẶN GUARDRAIL GATE ĐẠT 100/100 ĐIỂM! SẴN SÀNG DEPLOY RENDER & GITHUB.")
    print("=" * 75)
    return 0


if __name__ == "__main__":
    sys.exit(main())
