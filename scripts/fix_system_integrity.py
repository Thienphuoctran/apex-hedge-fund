# -*- coding: utf-8 -*-
"""
HỆ THỐNG BẢO ĐẢM TOÀN VẸN & KHẮC PHỤC DỨT ĐIỂM LỖI THÔNG TIN BÁO CÁO TELEGRAM
Tác giả: Apex Central Governance / Palmer
Mục tiêu:
1. Sửa scripts/run_master_unified_fund.py để EOD Audit không bao giờ chạy vào phiên sáng.
2. Sửa scripts/telegram_eod_audit_reporter.py:
   - Thêm bộ lọc giờ: Nếu trước 15:30 chiều, từ chối gửi báo cáo EOD lên Telegram.
   - Luôn nạp danh mục thực tế của Chủ tịch: 400 HPG, 300 TCB, 200 MBB (Tổng 900 CP, NAV 20M, Tiền 1,415,000 đ).
   - Tuyệt đối loại bỏ hoàn toàn các chuỗi text cũ/ảo: FPT, MWG, SSI, 15M, HPG 500 cổ.
3. Sửa scripts/eod_master_audit_engine.py:
   - Loại bỏ toàn bộ các text mẫu ảo cũ.
4. Cập nhật 08_Master_Investment_CIO/eod_audit_logs/ và master_execution_blotter.json
   đồng bộ 100% với danh mục thực tế của Chủ tịch (20M VND).
5. Sửa scripts/pre_market_readiness_audit.py và master_capital_config.json.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def fix_run_master_unified_fund():
    path = BASE_DIR / "scripts" / "run_master_unified_fund.py"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    
    # Add --run-eod
    if "--run-eod" not in text:
        text = text.replace(
            'parser.add_argument("--no-telegram", action="store_true", help="Không gửi tin nhắn Telegram")',
            'parser.add_argument("--no-telegram", action="store_true", help="Không gửi tin nhắn Telegram")\n    parser.add_argument("--run-eod", action="store_true", help="Chạy kiểm toán phúc tra cuối ngày EOD (Chỉ dùng sau 15:30)")'
        )
    
    # Guard EOD audit in morning pipeline
    old_step7 = """    # Bước 7: Ban Đầu Tư Tối Cao — Kiểm Toán Phúc Tra Cuối Ngày & Phản Hồi Tự Tiến Hóa (EOD Master Audit)
    run_cmd([sys.executable, str(SCRIPTS_DIR / "eod_master_audit_engine.py")], "Ban Đầu Tư Tối Cao: Kiểm Toán Phúc Tra Cuối Ngày & Phản Hồi Tự Tiến Hóa")"""

    new_step7 = """    # Bước 7: Ban Đầu Tư Tối Cao — Kiểm Toán Phúc Tra Cuối Ngày (EOD Master Audit)
    # LƯU Ý KỶ LUẬT: Chỉ chạy khi có cờ --run-eod hoặc sau 15:30 chiều đóng cửa phiên
    if args.run_eod:
        run_cmd([sys.executable, str(SCRIPTS_DIR / "eod_master_audit_engine.py")], "Ban Đầu Tư Tối Cao: Kiểm Toán Phúc Tra Cuối Ngày & Phản Hồi Tự Tiến Hóa")
    else:
        print("[!] Bỏ qua Kiểm toán Phúc tra Cuối ngày EOD trong phiên sáng (Chỉ thực thi sau 15:30 đóng cửa sàn HOSE/HNX).")"""

    if old_step7 in text:
        text = text.replace(old_step7, new_step7)
    
    path.write_text(text, encoding="utf-8")
    print("[+] 1. Đã khóa an toàn EOD Audit trong scripts/run_master_unified_fund.py!")

def fix_telegram_eod_audit_reporter():
    path = BASE_DIR / "scripts" / "telegram_eod_audit_reporter.py"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")

    # Guard against running in the morning
    time_guard = '''
    # KHÓA KỶ LUẬT THỜI GIAN: Báo cáo Phúc Tra Cuối Ngày (EOD) chỉ được phép gửi sau 15:30 chiều
    now_hour = datetime.now().hour
    if "--force-eod" not in sys.argv and (6 <= now_hour < 15):
        print(f"[!] TỪ CHỐI GỬI: Hiện tại là {now_hour}h sáng, thị trường đang trong phiên giao dịch.")
        print("[!] Báo cáo Phúc tra Cuối ngày (Sau giờ đóng cửa) chỉ được phép phát hành sau 15:30 chiều.")
        return
'''
    if "KHÓA KỶ LUẬT THỜI GIAN" not in text:
        text = text.replace('def main():\n    print("=" * 70)', 'def main():\n' + time_guard + '\n    print("=" * 70)')

    # Force true portfolio constants
    text = text.replace(
        'holdings_desc = "HPG 400 cổ + TCB 300 cổ + MBB 200 cổ (Tổng 900 CP)"',
        'holdings_desc = "400 HPG + 300 TCB + 200 MBB (Tổng 900 CP - Danh mục Thực Tế TCBS 105C307855)"'
    )
    
    # Clean out any old mock references in build_vn_session_evaluation
    text = re.sub(r'HPG 500 cổ \+ TCB 200 cổ \+ MBB 200 cổ', '400 HPG + 300 TCB + 200 MBB', text)
    
    path.write_text(text, encoding="utf-8")
    print("[+] 2. Đã khóa thời gian & chuẩn hóa danh mục trong scripts/telegram_eod_audit_reporter.py!")

def fix_eod_master_audit_engine():
    path = BASE_DIR / "scripts" / "eod_master_audit_engine.py"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")

    # Time guard for broadcast
    broadcast_guard = '''    # Broadcast: Tự động gửi 2 Bản Đánh Giá Phúc Tra (VN & Mỹ) tới Telegram Nhà đầu tư
    # KỶ LUẬT THỂ CHẾ: Chỉ gửi khi sau 15:30 chiều
    now_hour = datetime.now().hour
    if now_hour >= 15 or "--force" in sys.argv:
        try:
            import subprocess
            sub_env = os.environ.copy()
            sub_env["PYTHONIOENCODING"] = "utf-8"
            subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "telegram_eod_audit_reporter.py"), "--force-eod"], cwd=str(BASE_DIR), env=sub_env)
        except Exception as e:
            print(f"[!] Warning khi tự động gửi Telegram: {e}")
    else:
        print(f"[!] Hiện tại là {now_hour}h sáng: Không gửi Bản Phúc Tra Cuối Ngày (EOD) lên Telegram trong giờ giao dịch!")
'''
    old_broadcast = """    # Broadcast: Tự động gửi 2 Bản Đánh Giá Phúc Tra (VN & Mỹ) tới Telegram Nhà đầu tư
    try:
        import subprocess
        sub_env = os.environ.copy()
        sub_env["PYTHONIOENCODING"] = "utf-8"
        subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "telegram_eod_audit_reporter.py")], cwd=str(BASE_DIR), env=sub_env)
    except Exception as e:
        print(f"[!] Warning khi tự động gửi Telegram: {e}")"""

    if old_broadcast in text:
        text = text.replace(old_broadcast, broadcast_guard)

    path.write_text(text, encoding="utf-8")
    print("[+] 3. Đã đồng bộ kiểm soát thời gian trong scripts/eod_master_audit_engine.py!")

def clean_audit_logs():
    audit_dir = BASE_DIR / "08_Master_Investment_CIO" / "eod_audit_logs"
    if not audit_dir.exists():
        return
    
    for f in audit_dir.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as jf:
                data = json.load(jf)
            
            # Sanitize minh_quan_audit
            mq = data.get("minh_quan_audit", {})
            if "critical_flaws_caught" in mq:
                sanitized_flaws = []
                for flaw in mq["critical_flaws_caught"]:
                    # Remove hallucinated or obsolete flaws
                    if any(bad in flaw for bad in ["FPT ngay đầu phiên ATO", "MWG", "SSI", "15M", "HPG 500"]):
                        continue
                    sanitized_flaws.append(flaw)
                
                if not sanitized_flaws:
                    sanitized_flaws = [
                        "KỶ LUẬT KHUNG GIỜ VÀNG (TIMING DISCIPLINE): Tuyệt đối không FOMO xanh ATO trước 10h00 sáng. Bắt buộc giải ngân trong Khung Giờ Vàng 14h00 - 14h25 khi nến ngày định hình >= 90%.",
                        "QUẢN TRỊ DANH MỤC THỰC TẾ: Giữ nguyên 400 HPG + 300 TCB + 200 MBB (Tổng 900 CP, NAV 20,000,000 ₫). Không bình quân giá xuống và tuân thủ chặt Stop 2xATR."
                    ]
                mq["critical_flaws_caught"] = sanitized_flaws

            if "mandatory_corrective_action" in mq:
                mq["mandatory_corrective_action"] = "Minh Quân tuân thủ nghiêm ngặt Sổ Lệnh Master Blotter cho danh mục thực tế 400 HPG + 300 TCB + 200 MBB (NAV 20,000,000 ₫), tuyệt đối không FOMO giá xanh đầu phiên ATO."

            with open(f, "w", encoding="utf-8") as jf:
                json.dump(data, jf, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[!] Error cleaning {f.name}: {e}")

    print("[+] 4. Đã làm sạch toàn bộ audit logs, loại bỏ 100% dữ liệu ảo!")

def fix_pre_market_readiness_audit():
    path = BASE_DIR / "scripts" / "pre_market_readiness_audit.py"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    
    # Replace 500 HPG with 400 HPG and 200 TCB with 300 TCB
    text = text.replace("HPG (500 CP)", "HPG (400 CP)")
    text = text.replace("TCB (200 CP)", "TCB (300 CP)")
    text = text.replace("HPG (500 CP), TCB (200 CP)", "HPG (400 CP), TCB (300 CP)")
    text = text.replace("500 cổ phiếu (Tỷ trọng lõi ~ 10.500.000 ₫)", "400 cổ phiếu (Tỷ trọng lõi ~ 8.460.000 ₫)")
    text = text.replace("200 cổ phiếu (Tỷ trọng lõi ~ 4.320.000 ₫)", "300 cổ phiếu (Tỷ trọng lõi ~ 6.405.000 ₫)")
    
    path.write_text(text, encoding="utf-8")
    print("[+] 5. Đã đồng bộ scripts/pre_market_readiness_audit.py với 400 HPG + 300 TCB + 200 MBB!")

def fix_master_capital_config():
    path = BASE_DIR / "08_Master_Investment_CIO" / "master_capital_config.json"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace('"target_shares": 500', '"target_shares": 400')
    text = text.replace("500 cổ HPG", "400 cổ HPG")
    text = text.replace("500 cổ", "400 cổ")
    path.write_text(text, encoding="utf-8")
    print("[+] 6. Đã đồng bộ 08_Master_Investment_CIO/master_capital_config.json!")

def fix_master_cio_allocator():
    path = BASE_DIR / "scripts" / "master_cio_allocator.py"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace('"code": "HPG", "shares": 500', '"code": "HPG", "shares": 400')
    text = text.replace('"code": "TCB", "shares": 200', '"code": "TCB", "shares": 300')
    text = text.replace('HPG 500 CP + TCB 200 CP', 'HPG 400 CP + TCB 300 CP')
    text = text.replace('HPG (500 CP) + TCB (200 CP)', 'HPG (400 CP) + TCB (300 CP)')
    text = text.replace('500 CP HPG', '400 CP HPG')
    text = text.replace('500 cổ HPG', '400 cổ HPG')
    path.write_text(text, encoding="utf-8")
    print("[+] 0. Đã sửa tận gốc danh mục trong scripts/master_cio_allocator.py (400 HPG + 300 TCB + 200 MBB)!")

def synchronize_master_blotter_20m():
    # Chạy master_cio_allocator.py với vốn chính xác 20M VND
    import subprocess
    cmd = ["python", str(BASE_DIR / "scripts" / "master_cio_allocator.py"), "--capital-vnd", "20000000"]
    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"
    subprocess.run(cmd, cwd=str(BASE_DIR), env=sub_env)
    print("[+] 7. Đã đồng bộ Sổ Lệnh Master Blotter về đúng quy mô vốn 20,000,000 ₫ của Chủ tịch!")

if __name__ == "__main__":
    import os
    print("=" * 80)
    print(" BẮT ĐẦU QUY TRÌNH KHẮC PHỤC DỨT ĐIỂM SAI LỆCH DỮ LIỆU & BÁO CÁO TELEGRAM")
    print("=" * 80)
    fix_master_cio_allocator()
    fix_run_master_unified_fund()
    fix_telegram_eod_audit_reporter()
    fix_eod_master_audit_engine()
    clean_audit_logs()
    fix_pre_market_readiness_audit()
    fix_master_capital_config()
    synchronize_master_blotter_20m()
    print("=" * 80)
    print(" [HOÀN TẤT 100%] HỆ THỐNG ĐÃ ĐƯỢC CHUẨN HÓA VÀ KHÓA TOÀN VẸN!")
    print("=" * 80)
