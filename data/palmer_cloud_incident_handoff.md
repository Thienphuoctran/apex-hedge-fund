# HỒ SƠ CHẨN ĐOÁN KHẨN CẤP & PHƯƠNG ÁN FIX TRIỆT ĐỂ CLOUD RENDER + GITHUB ACTIONS

**Thời điểm lập hồ sơ:** 2026-11-16 10:53 (UTC+7)  
**Đơn vị phối hợp:** Long (Đầu não Trợ lý Cá nhân) & Palmer (Apex Central System Governance)  
**Tài khoản phục vụ:** Chủ tịch Trần Quốc Thiên Phước (TCBS: `105C307855` | Gmail: `phuoct998@gmail.com`)  
**Trạng thái:** Đã hoàn tất chẩn đoán thực chứng 100% — Chờ lệnh phê duyệt triển khai của Chủ tịch

---

## 1. DỮ LIỆU SỰ CỐ TỪ GMAIL (`phuoct998@gmail.com`)
- **Render Web Service (`apex-hedge-fund`, ID `srv-dbng41u7bikc73cf93eg`, Free Plan 512 MB RAM):**
  - `16/11/2026 09:43:03 VN (02:43:03 UTC)`: `Web Service apex-hedge-fund exceeded its memory limit` → tự động restart, gián đoạn dịch vụ.
  - `16/11/2026 09:25:03 VN (02:25:03 UTC)`: `Server failure detected on apex-hedge-fund` — Reason: `dial tcp 10.28.251.18:10000: i/o timeout`.
- **GitHub Actions (`Thienphuoctran/apex-hedge-fund`):**
  - **14 email liên tiếp (`13/11` → `16/11/2026`)**: `Run failed: .github/workflows/apex_cloud_sentinel_247.yml - main` (từ commit `f752357` đến `1675a25`), toàn bộ đều `Duration: 0.0 seconds`, `jobs: []`, `event: push`.

---

## 2. KẾT QUẢ CHẨN ĐOÁN TẬN GỐC (VERIFIED ROOT CAUSES)

### A. Lỗi GitHub Actions (`0.0s`, `jobs: []`) & Rủi ro tiềm ẩn 4 Workflows
1. **Nguyên nhân trực tiếp (`apex_cloud_sentinel_247.yml` dòng 82):**
   - `- name: 5. Ban 12 Trong: 24/7 Technical Integrity & 23h30 Institutional Audit` chứa dấu `: ` không bọc nháy, gây lỗi YAML parser `ScannerError: mapping values are not allowed here` mỗi khi push lên `main` kể từ commit `f752357` (13/11/2026).
2. **Lỗi tiềm ẩn đồng thời:**
   - `apex_cloud_sentinel_247.yml:86` gọi `apex_inspector_trong.py --run-23h30-audit` trên cả cron `*/30` ban ngày → dễ spam báo cáo 23h30 mỗi 30 phút.
   - `apex_cloud_sentinel_247.yml:42` thiếu `google-genai`, `pillow`, `beautifulsoup4` so với `requirements.txt`.
   - `victor_sentinel_cron.yml` (`*/15 2-8`), `apex_cloud_sentinel_247.yml` (`*/30 1-8`), `apex_nightly_autonomous_fund.yml` (`15 8`) trùng giờ nhau, không có `concurrency:` group, không `git pull --rebase`, và đều commit file nhị phân `data/apex_institutional_vault.db` (22.86 MB) lên Git → xung đột push & có thể kích hoạt Render Auto-Deploy liên tục nếu bật auto-deploy.

### B. Lỗi Render Vượt RAM 512 MB & Timeout Cổng `10000`
1. **Chạy 6 Python processes song song trong 1 container 512 MB (`Dockerfile:44` → `scripts/start_apex_cloud_247.py:61-112`):**
   - Supervisor + `cron_daemon` + `sentinel_monitor` + `telegram_copilot` + `inspector_trong` + `live_intraday_brain` (cộng thêm subprocess con của `cron_daemon`).
2. **Tính toán trùng lặp 3 tầng (Triple Duplication):**
   - `live_intraday_brain` (20s), `sentinel_monitor` (15s), và SSE stream `/api/tactical_war_room/stream` (4s) đều gọi trùng `compute_live_war_room_snapshot` / `get_tactical_war_room_state` kèm `ThreadPoolExecutor(8)` và import `yfinance` + `pandas` + `numpy`.
3. **Memory Leak từ `importlib.reload()` (`start_apex_cloud_247.py:416, 539-540, 563-564, 776-777, 923-924, 968-969, 1006`):**
   - Mỗi request mở Portal `/` thực hiện `importlib.reload(scripts.apex_web_portal_engine)` và `scripts.apex_report_scanner`, giữ tham chiếu cũ gây phình RSS liên tục.
4. **SQLite Cache 64 MB/connection (`scripts/apex_database_engine.py:64`):**
   - `PRAGMA cache_size = -64000;` trên nhiều connection đa tiến trình/đa luồng + chạy `migrate_all_markdown_reports()` đồng bộ + `_flat_file_scan_all_institutional_reports()` quét 21 glob patterns trên disk.
5. **Bind Port `10000` bị chặn cuối cùng (`start_apex_cloud_247.py:1515-1531`) & `/api/health` nặng (`:345-346`):**
   - Supervisor chạy xong `migrate_all_markdown_reports()` và spawn cả 5 subprocesses rồi mới mở port `10000`.
   - `/api/health` gọi `ApexCloudDBSync.get_cloud_status()` mở kết nối SQLite (`PRAGMA journal_mode=WAL` + `CREATE TABLE`), có nguy cơ nghẽn khi DB đang bị write lock.
6. **Xung đột Telegram Bot (`HTTP 409 Conflict`) giữa Cloud & PC:**
   - `telegram_interactive_copilot.py` trên Windows ủy quyền sang `Trợ lí cá nhân\scripts\telegram_ai_copilot.py` (Omni-Copilot V4.0), nhưng trên Linux Render đường dẫn Windows không tồn tại nên container tự chạy vòng polling `getUpdates` riêng trên cùng Bot Token `@Chuyenvienvictor_bot`.

---

## 3. PHƯƠNG ÁN TRIỂN KHAI FIX TRIỆT ĐỂ 4 GIAI ĐOẠN
- **Giai đoạn 1 (Cứu hỏa khẩn cấp ~15 phút):** Fix dòng 82 YAML `apex_cloud_sentinel_247.yml` + phân tách trigger `23h30`; thêm cờ `APEX_DISABLE_TELEGRAM_COPILOT=1` tắt polling bot trên Render; đưa lệnh mở HTTP port `10000` lên trước `migrate` và bỏ chạm SQLite khỏi `/api/health`.
- **Giai đoạn 2 (Tái kiến trúc Render < 220 MB RAM):** Hợp nhất 6 tiến trình → 1–2 tiến trình nhẹ; gộp quét War-Room & Victor vào 1 vòng duy nhất; xóa `importlib.reload()`; hạ `PRAGMA cache_size = -4000`; thay `yfinance/pandas/numpy` trên web runtime bằng Yahoo JSON API nhẹ qua `urllib`; cho `apex_report_scanner` đọc SQLite trực tiếp.
- **Giai đoạn 3 (Chuẩn hóa GitHub Actions & GitOps):** Đưa `apex_institutional_vault.db*` vào `.gitignore` (tái tạo từ Markdown/Supabase); thêm `concurrency:` + `git pull --rebase`; giãn pha cron giữa các workflow; cấu hình Render Build Filters/Auto-Deploy hợp lý.
- **Giai đoạn 4 (Chốt chặn vĩnh viễn):** Bắt buộc YAML preflight check; kiểm thử container RAM < 250 MB & `/api/health < 2s` trước deploy; khóa Single-Owner Telegram Lock và chuyển `bot_token` sang biến môi trường bảo mật.
