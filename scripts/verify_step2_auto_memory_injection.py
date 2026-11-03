#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/verify_step2_auto_memory_injection.py
Kiểm thử & Nghiệm thu Độc lập Bước 2: Cơ chế Tự động Nạp Bộ Nhớ Ngữ Cảnh (Auto-Memory Injection)
cho cả Minh Quân (TTCK Việt Nam) và Alex (Phố Wall).
"""

import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent

def test_step2():
    print("=" * 80)
    print(" BẮT ĐẦU KIỂM THỬ ĐỘC LẬP BƯỚC 2: AUTO-MEMORY INJECTION (MINH QUÂN & ALEX)")
    print("=" * 80)

    # 1. Kiểm tra Kho Bộ Nhớ VN (vn_contextual_memory_vault.json)
    vn_vault_path = BASE_DIR / "VN_Market" / "05_Learning_And_Evolution" / "vn_contextual_memory_vault.json"
    assert vn_vault_path.exists(), f"Không tìm thấy {vn_vault_path}"
    with open(vn_vault_path, "r", encoding="utf-8") as f:
        vn_vault = json.load(f)
    vn_mems = [m["memory_id"] for m in vn_vault.get("contextual_memories", [])]
    print(f"[+] 1. VN Memory Vault v{vn_vault.get('vault_version')}: Đã nạp {len(vn_mems)} quy tắc -> {vn_mems}")
    for req_id in ["MEM-VN-001", "MEM-VN-002", "MEM-VN-003", "MEM-VN-004", "MEM-VN-005"]:
        assert req_id in vn_mems, f"Thiếu quy tắc {req_id} trong VN Vault"

    # 2. Kiểm tra Kho Bộ Nhớ Global (contextual_error_memory_vault.json)
    glb_vault_path = BASE_DIR / "05_Learning_And_Evolution" / "contextual_error_memory_vault.json"
    assert glb_vault_path.exists(), f"Không tìm thấy {glb_vault_path}"
    with open(glb_vault_path, "r", encoding="utf-8") as f:
        glb_vault = json.load(f)
    glb_mems = [m["memory_id"] for m in glb_vault.get("contextual_memories", [])]
    print(f"[+] 2. Global Memory Vault v{glb_vault.get('vault_version')}: Đã nạp {len(glb_mems)} quy tắc -> {glb_mems}")
    for req_id in ["MEM-GLB-001", "MEM-GLB-002", "MEM-GLB-003", "MEM-GLB-004", "MEM-GLB-005"]:
        assert req_id in glb_mems, f"Thiếu quy tắc {req_id} trong Global Vault"

    # 3. Kiểm tra Sổ cái Minh Quân (vn_daily_ledger.json)
    vn_ledger_path = BASE_DIR / "VN_Market" / "07_Daily_Specialist" / "vn_daily_ledger.json"
    assert vn_ledger_path.exists(), f"Không tìm thấy {vn_ledger_path}"
    with open(vn_ledger_path, "r", encoding="utf-8") as f:
        vn_ledger = json.load(f)
    injected_vn = vn_ledger.get("injected_contextual_memories", [])
    print(f"[+] 3. Sổ Cái Minh Quân vn_daily_ledger.json: Đã nạp {len(injected_vn)} quy tắc -> {injected_vn}")
    assert len(injected_vn) == 5, f"Số lượng quy tắc VN chưa đủ: {len(injected_vn)}"

    # 4. Kiểm tra Báo cáo Minh Quân (2026-11-03_VN_Specialist_Decision.md)
    vn_md_path = BASE_DIR / "VN_Market" / "07_Daily_Specialist" / "2026-11-03_VN_Specialist_Decision.md"
    assert vn_md_path.exists(), f"Không tìm thấy {vn_md_path}"
    with open(vn_md_path, "r", encoding="utf-8") as f:
        vn_md = f.read()
    assert "## 🧠 1.5. BỘ NHỚ QUẢN TRỊ RỦI RO & BÀI HỌC THỰC CHIẾN TỰ ĐỘNG NẠP" in vn_md, "Thiếu Mục 1.5 trong Báo cáo Minh Quân"
    assert "MEM-VN-004" in vn_md and "MEM-VN-005" in vn_md, "Thiếu quy tắc mới MEM-VN-004/005 trong Báo cáo Minh Quân"
    print(f"[+] 4. Báo Cáo Minh Quân (.md): Mục 1.5 Auto-Injected Contextual Memory hiển thị hoàn hảo ({vn_md_path.stat().st_size:,} bytes)")

    # 5. Kiểm tra Sổ cái Alex (daily_specialist_ledger.json)
    glb_ledger_path = BASE_DIR / "07_Daily_Investment_Specialist" / "daily_specialist_ledger.json"
    assert glb_ledger_path.exists(), f"Không tìm thấy {glb_ledger_path}"
    with open(glb_ledger_path, "r", encoding="utf-8") as f:
        glb_ledger = json.load(f)
    injected_glb = glb_ledger.get("injected_contextual_memories", [])
    print(f"[+] 5. Sổ Cái Alex daily_specialist_ledger.json: Đã nạp {len(injected_glb)} quy tắc -> {injected_glb}")
    assert len(injected_glb) == 5, f"Số lượng quy tắc Global chưa đủ: {len(injected_glb)}"

    # 6. Kiểm tra Báo cáo Alex (2026-11-03_Daily_Specialist_Decision.md)
    glb_md_path = BASE_DIR / "07_Daily_Investment_Specialist" / "2026-11-03_Daily_Specialist_Decision.md"
    assert glb_md_path.exists(), f"Không tìm thấy {glb_md_path}"
    with open(glb_md_path, "r", encoding="utf-8") as f:
        glb_md = f.read()
    assert "## 🧠 1.5. BỘ NHỚ QUẢN TRỊ RỦI RO & BÀI HỌC THỰC CHIẾN TỰ ĐỘNG NẠP" in glb_md, "Thiếu Mục 1.5 trong Báo cáo Alex"
    assert "MEM-GLB-004" in glb_md and "MEM-GLB-005" in glb_md, "Thiếu quy tắc mới MEM-GLB-004/005 trong Báo cáo Alex"
    print(f"[+] 6. Báo Cáo Alex (.md): Mục 1.5 Auto-Injected Contextual Memory hiển thị hoàn hảo ({glb_md_path.stat().st_size:,} bytes)")

    # 7. Kiểm tra Ràng buộc Toán học Danh mục
    # Kiểm tra Trần Rủi Ro Ngành Bán Dẫn <= 28% của Alex
    semi_orders = [o for o in glb_ledger.get("daily_scientific_orders", []) if o.get("symbol") in ["NVDA", "TSM", "AVGO"]]
    semi_total_weight = sum(o.get("weight_nav_pct", 0.0) for o in semi_orders)
    print(f"[+] 7. Alex Semiconductor Allocation: {semi_total_weight:.1f}% NAV (Khống chế <= 28.0% theo MEM-GLB-004)")
    assert semi_total_weight <= 28.0, f"Vi phạm trần rủi ro Bán dẫn: {semi_total_weight}% > 28.0%"

    # Kiểm tra Lô chẵn 100 CP & Tiền mặt dự phòng >= 7% của Minh Quân
    vn_orders = vn_ledger.get("orders", [])
    for o in vn_orders:
        shares = o.get("shares", 0)
        assert shares % 100 == 0, f"Mã {o.get('ticker')} vi phạm quy chuẩn lô 100: {shares}"
    total_vn_weight = sum(o.get("weight_pct", 0.0) for o in vn_orders)
    dry_powder_vn = round(100.0 - total_vn_weight, 1)
    print(f"[+] 8. Minh Quân Portfolio: 100% Lô chẵn 100 CP | Dry Powder: {dry_powder_vn}% NAV (Bảo đảm >= 7% theo MEM-VN-005)")
    assert dry_powder_vn >= 7.0, f"Tiền mặt dự phòng VN quá thấp: {dry_powder_vn}% < 7.0%"

    print("=" * 80)
    print(" 🎉 [NGHIỆM THU 100%] BƯỚC 2: AUTO-MEMORY INJECTION CHO MINH QUÂN & ALEX ĐẠT CHUẨN HOÀN TOÀN!")
    print("=" * 80)
    return 0

if __name__ == "__main__":
    sys.exit(test_step2())
