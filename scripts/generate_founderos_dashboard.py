#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX FOUNDEROS COMMAND CENTER GENERATOR (Inspired by FounderOS #04, Mesa #05, Solopreneur #08)
File: scripts/generate_founderos_dashboard.py
Cơ quan chủ quản: Phòng Quản Trị Hệ Thống (Palmer) & Master CIO James

Tạo bảng điều khiển một cửa (Unified Executive Dashboard) cho Chủ tịch Phước Trần:
- Quản trị 11 phòng ban chuyên trách (Sơ đồ tổ chức & Năng lực trực chiến)
- Bảng Kanban giao việc thời gian thực 17 mốc tác chiến 24/7 (Mesa Jira-like Protocol)
- Radar BCTC tiền thật của Hiền (Ban 10) & Studio Video Viral của Khánh (Ban 11)
- Kho tri thức Y Combinator cho Solopreneur (#08)
(KHÔNG giới hạn chi phí - Các Agent hoạt động với 100% Full Power và trí tuệ cao nhất)
"""

import datetime
import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DASHBOARD_DIR = BASE_DIR / "dashboard"
OUTPUT_HTML = DASHBOARD_DIR / "founderos.html"

DEPARTMENTS_INFO = [
    {"id": "ban_1", "name": "Ban 1 — Vĩ Mô SBV & Dòng Tiền", "role": "Macro & Monetary", "lead": "Macro Lead", "topic": "Topic 5 (radar_filings)", "status": "🟢 Trực Chiến 24/7"},
    {"id": "ban_2", "name": "Ban 2 — Thẩm Định BCTC & Định Giá", "role": "BCTC Forensic OCF", "lead": "Equity Lead", "topic": "Topic 5 (radar_filings)", "status": "🟢 Trực Chiến 24/7"},
    {"id": "ban_3", "name": "Ban 3 — Tổng Hợp & Săn Sóng Alpha", "role": "Synthesis & Screener", "lead": "Screener Lead", "topic": "Topic 5 (radar_filings)", "status": "🟢 Trực Chiến 24/7"},
    {"id": "ban_4", "name": "Ban 4 — Quản Trị Rủi Ro Định Lượng", "role": "ATR Risk-Parity Stop", "lead": "Quant Lead", "topic": "Topic 111 (quant_risk)", "status": "🟢 Trực Chiến 24/7"},
    {"id": "ban_5", "name": "Ban 5 — Thẩm Định Hiệu Suất & Tự Học", "role": "Adaptive Learning Loop", "lead": "Learning Lead", "topic": "Topic 112 (academy_learning)", "status": "🟢 Trực Chiến 24/7"},
    {"id": "ban_6", "name": "Ban 6 — Học Viện Huấn Luyện NĐT", "role": "Investor Coach", "lead": "Coach Lead", "topic": "Topic 112 (academy_learning)", "status": "🟢 Trực Chiến 24/7"},
    {"id": "ban_7", "name": "Ban 7 — Chuyên Viên Đầu Tư Pre-ATO", "role": "Daily Specialist Execution", "lead": "Minh Quân & Alex", "topic": "Topic 4 (morning_blotter)", "status": "🟢 Trực Chiến 24/7"},
    {"id": "ban_8", "name": "Ban 8 — Tổng Tư Lệnh Master CIO", "role": "Supreme Execution & Capital", "lead": "James", "topic": "Topic 6 (james_hq)", "status": "⭐ Tổng Tư Lệnh"},
    {"id": "ban_9", "name": "Ban 9 — Giám Sát Thời Gian Thực", "role": "Live Sentinel 60s", "lead": "Victor", "topic": "Topic 3 (alerts)", "status": "🛡️ Trực Chiến Phiên"},
    {"id": "ban_10", "name": "Ban 10 — BCTC, Thường Niên & IR", "role": "Filings & IR Scout", "lead": "Hiền", "topic": "Topic 189 (hien_desk)", "status": "🌸 Trực Chiến 21h00"},
    {"id": "ban_11", "name": "Ban 11 — Studio Video Viral Tài Chính", "role": "Viral Content & AI Render", "lead": "Khánh & Bảo", "topic": "Topic 190 (khanh_studio)", "status": "🎬 Trực Chiến 21h15"}
]


def load_json(p: Path, default=None):
    if not p.exists():
        return default if default is not None else {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def build_dashboard():
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    today_str = datetime.date.today().isoformat()
    now_str = datetime.datetime.now().strftime("%H:%M:%S")

    kanban_data = load_json(DATA_DIR / "apex_kanban_board.json", {})
    tasks = kanban_data.get("tasks", {})
    cols = kanban_data.get("columns", {
        "BACKLOG": [],
        "IN_PROGRESS": [],
        "AUDIT_REVIEW": [],
        "DONE": []
    })

    # Department table rows
    dept_rows_html = ""
    for d in DEPARTMENTS_INFO:
        dept_rows_html += f"""
        <tr class="border-b border-slate-800 hover:bg-slate-800/40 transition">
            <td class="py-3 px-4 font-semibold text-slate-200">{d['name']}</td>
            <td class="py-3 px-4 text-xs text-sky-400 font-mono">{d['role']}</td>
            <td class="py-3 px-4 font-bold text-slate-100">👤 {d['lead']}</td>
            <td class="py-3 px-4 text-xs text-slate-400 font-mono">{d['topic']}</td>
            <td class="py-3 px-4 text-center">
                <span class="px-2.5 py-1 text-xs font-bold rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                    {d['status']}
                </span>
            </td>
        </tr>
        """

    def render_col_cards(col_name):
        task_ids = cols.get(col_name, [])
        cards = ""
        for tid in task_ids:
            t = tasks.get(tid, {})
            prio = t.get("priority", "MEDIUM")
            prio_color = "border-sky-500/30 bg-sky-950/20 text-sky-300"
            if prio == "CRITICAL" or prio == "SUPREME":
                prio_color = "border-rose-500/40 bg-rose-950/30 text-rose-300"
            elif prio == "HIGH":
                prio_color = "border-amber-500/40 bg-amber-950/20 text-amber-300"

            cards += f"""
            <div class="p-3 mb-2.5 rounded-lg border {prio_color} shadow-sm hover:scale-[1.01] transition">
                <div class="flex items-center justify-between text-xs mb-1">
                    <span class="font-mono font-bold text-slate-400">{t.get('scheduled_time', '')}</span>
                    <span class="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-800 text-slate-300">{t.get('dept', '')}</span>
                </div>
                <div class="text-sm font-semibold text-slate-100 mb-1">{t.get('title', '')}</div>
                <div class="text-xs text-slate-400 flex items-center justify-between">
                    <span>👤 {t.get('assignee', '')}</span>
                    <span class="font-mono text-[10px] text-slate-500">{t.get('id', '')}</span>
                </div>
            </div>
            """
        return cards if cards else '<div class="text-xs text-slate-500 italic p-3 text-center">Không có nhiệm vụ</div>'

    html_content = f"""<!DOCTYPE html>
<html lang="vi" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex FounderOS — Bảng Điều Hành Quỹ & Solopreneur Đa Tầng</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #0b0f19; color: #f1f5f9; }}
        .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: #0b0f19; }}
        ::-webkit-scrollbar-thumb {{ background: #1e293b; border-radius: 3px; }}
    </style>
</head>
<body class="p-4 md:p-6 space-y-6">

    <!-- TOP HEADER -->
    <header class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <div class="flex items-center gap-3">
                <span class="text-2xl">🏛️</span>
                <h1 class="text-2xl font-black text-slate-100 tracking-tight">APEX FOUNDEROS COMMAND CENTER</h1>
                <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">Full Power Mode</span>
            </div>
            <p class="text-xs md:text-sm text-slate-400 mt-1">
                Chủ tịch: <strong class="text-amber-400">Phước Trần</strong> • Tài khoản TCBS: <code class="text-sky-300 font-mono">105C307855</code> • Telegram Supergroup: <code class="text-slate-400 font-mono">-1004465270817</code>
            </p>
        </div>
        <div class="flex flex-wrap items-center gap-3 text-xs">
            <div class="bg-slate-800/80 border border-slate-700/60 rounded-xl px-3.5 py-2">
                <span class="text-slate-400">Thời gian hệ thống:</span>
                <span class="font-mono font-bold text-slate-200 ml-1">{today_str} ({now_str})</span>
            </div>
            <div class="bg-emerald-950/30 border border-emerald-500/40 rounded-xl px-3.5 py-2 text-emerald-400 font-mono font-bold">
                ⚡ 11 Phòng Ban Trực Chiến 24/7
            </div>
            <a href="https://t.me/c/4465270817/4" target="_blank" class="bg-sky-600 hover:bg-sky-500 text-white font-bold px-4 py-2 rounded-xl transition flex items-center gap-1.5 shadow-md">
                📱 Mở Telegram Quỹ
            </a>
        </div>
    </header>

    <!-- KPI STATS CARDS -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Vốn Quỹ & TCBS -->
        <div class="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Danh Mục 900 Cổ Phiếu</span>
            <div class="text-xl font-black text-emerald-400 font-mono mt-1">400 HPG • 300 TCB • 200 MBB</div>
            <div class="text-xs text-slate-400 mt-2 flex justify-between">
                <span>Tiền mặt: <strong class="text-slate-200">1,415,000 ₫ (7.1%)</strong></span>
                <span class="text-emerald-400">Margin: 0.0%</span>
            </div>
        </div>

        <!-- Trạng thái Tác Chiến 24/7 -->
        <div class="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Tác Chiến Tự Động (Cron 24/7)</span>
            <div class="text-xl font-black text-sky-400 font-mono mt-1">17 Cột Mốc <span class="text-xs font-normal text-slate-400">Khép kín</span></div>
            <div class="text-xs text-slate-400 mt-2 flex justify-between">
                <span>Tiến trình nền: <strong class="text-emerald-400">RUNNING 24/7</strong></span>
                <span>Tự động bù giờ: Có</span>
            </div>
        </div>

        <!-- Kanban Progress (Mesa Jira) -->
        <div class="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Bảng Giao Việc (Mesa Protocol)</span>
            <div class="text-xl font-black text-amber-400 font-mono mt-1">{len(cols.get('DONE', []))} / 17 <span class="text-xs font-normal text-slate-400">Đã hoàn thành</span></div>
            <div class="text-xs text-slate-400 mt-2 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Đang chạy: <strong class="text-slate-200">{len(cols.get('IN_PROGRESS', []))} nhiệm vụ</strong></span>
            </div>
        </div>

        <!-- Y Combinator Collective IQ -->
        <div class="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Trí Tuệ Quỹ (YC Stanford #08)</span>
            <div class="text-xl font-black text-purple-400 font-mono mt-1">IQ 152.0 <span class="text-xs font-normal text-slate-400">(Peter Thiel Moat)</span></div>
            <div class="text-xs text-slate-400 mt-2">
                <span>100% Tiền Thật <strong class="text-emerald-400">OCF/LNST ≥ 1.0x</strong></span>
            </div>
        </div>
    </div>

    <!-- MAIN TWO-COLUMN WORKSPACE -->
    <div class="grid grid-cols-1 xl:grid-cols-12 gap-6">

        <!-- LEFT: KANBAN BOARD (Mesa Protocol) - 7 COLS -->
        <div class="xl:col-span-7 space-y-4">
            <div class="flex items-center justify-between">
                <h2 class="text-lg font-bold flex items-center gap-2 text-slate-100">
                    <span>📋</span> Bảng Giao Việc Kanban 11 Phòng Ban (Mesa Jira Protocol)
                </h2>
                <span class="text-xs text-slate-400 font-mono">17 Nhiệm vụ tự động hóa 24/7</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <!-- COL 1: BACKLOG -->
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-3 flex flex-col h-[520px]">
                    <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
                        <span class="font-bold text-xs uppercase text-slate-400">⏳ Chờ Giờ G</span>
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300 font-mono">{len(cols.get('BACKLOG', []))}</span>
                    </div>
                    <div class="overflow-y-auto flex-1 pr-1">
                        {render_col_cards('BACKLOG')}
                    </div>
                </div>

                <!-- COL 2: IN_PROGRESS -->
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-3 flex flex-col h-[520px]">
                    <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
                        <span class="font-bold text-xs uppercase text-sky-400">⚡ Đang Chạy</span>
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-sky-950 text-sky-300 border border-sky-500/40 font-mono">{len(cols.get('IN_PROGRESS', []))}</span>
                    </div>
                    <div class="overflow-y-auto flex-1 pr-1">
                        {render_col_cards('IN_PROGRESS')}
                    </div>
                </div>

                <!-- COL 3: DONE -->
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-3 flex flex-col h-[520px]">
                    <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
                        <span class="font-bold text-xs uppercase text-emerald-400">✅ Hoàn Thành</span>
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-500/40 font-mono">{len(cols.get('DONE', []))}</span>
                    </div>
                    <div class="overflow-y-auto flex-1 pr-1">
                        {render_col_cards('DONE')}
                    </div>
                </div>
            </div>
        </div>

        <!-- RIGHT: HIỀN BCTC & KHÁNH STUDIO - 5 COLS -->
        <div class="xl:col-span-5 space-y-6">

            <!-- HIỀN BCTC CARD -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
                <div class="flex items-center justify-between">
                    <h3 class="font-bold text-sm text-slate-100 flex items-center gap-2">
                        <span>🌸</span> Ban 10 — Bàn Làm Việc Của Hiền (BCTC & IR)
                    </h3>
                    <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-pink-500/20 text-pink-300 border border-pink-500/40">Topic 189</span>
                </div>
                <p class="text-xs text-slate-400">Rà soát 2-3 BCTC chọn lọc lúc 21h00 tối. Tích hợp Agent Zero Headless Scout cào web vượt tường lửa.</p>

                <div class="space-y-2 pt-1">
                    <div class="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/60 flex items-center justify-between">
                        <div>
                            <span class="font-bold text-xs text-slate-200">HPG (Hòa Phát)</span>
                            <span class="text-[11px] text-emerald-400 ml-2 font-mono">OCF 1.08x (8,866 tỷ)</span>
                        </div>
                        <a href="https://hoaphat.com.vn/quan-he-co-dong" target="_blank" class="text-xs text-sky-400 hover:underline">Link IR ↗</a>
                    </div>
                    <div class="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/60 flex items-center justify-between">
                        <div>
                            <span class="font-bold text-xs text-slate-200">GMD (Gemadept)</span>
                            <span class="text-[11px] text-emerald-400 ml-2 font-mono">OCF 1.42x (1,441 tỷ)</span>
                        </div>
                        <a href="https://gemadept.com.vn/quan-he-co-dong" target="_blank" class="text-xs text-sky-400 hover:underline">Link IR ↗</a>
                    </div>
                    <div class="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/60 flex items-center justify-between">
                        <div>
                            <span class="font-bold text-xs text-slate-200">DGC (Đức Giang)</span>
                            <span class="text-[11px] text-emerald-400 ml-2 font-mono">OCF 2.79x (2,348 tỷ)</span>
                        </div>
                        <a href="https://ducgiangchem.vn/quan-he-co-dong" target="_blank" class="text-xs text-sky-400 hover:underline">Link IR ↗</a>
                    </div>
                </div>
            </div>

            <!-- KHÁNH STUDIO CARD -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
                <div class="flex items-center justify-between">
                    <h3 class="font-bold text-sm text-slate-100 flex items-center gap-2">
                        <span>🎬</span> Ban 11 — Studio Video Viral (Khánh & Bảo)
                    </h3>
                    <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">Topic 190</span>
                </div>
                <p class="text-xs text-slate-400">Kịch bản video TikTok 60s lúc 21h15 tối và chuyển lệnh Render Job tự động sang máy tính Bảo.</p>

                <div class="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 text-xs space-y-1.5">
                    <div class="font-bold text-amber-400">🔥 Video mới nhất: Sự Thật Tiền Thật Hòa Phát (HPG)</div>
                    <div class="text-slate-300">Hook 3s: 'Đừng vội mừng khi thấy công ty lãi nghìn tỷ! 90% F0 không biết bí mật này...'</div>
                    <div class="text-[11px] text-slate-400 font-mono">Trạng thái: Đã chuyển sang máy tính Bảo render video 9:16 Edge-TTS</div>
                </div>
            </div>

        </div>
    </div>

    <!-- LOWER SECTION: 11 DEPARTMENTS DIRECTORY -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
                <h2 class="text-lg font-bold flex items-center gap-2 text-slate-100">
                    <span>👥</span> Danh Bạ 11 Phòng Ban Chuyên Trách & Phân Quyền Vận Hành
                </h2>
                <p class="text-xs text-slate-400 mt-0.5">Sơ đồ tổ chức phân quyền độc lập, hoạt động với 100% Full Power và trí tuệ cao nhất.</p>
            </div>
            <div class="flex items-center gap-2 font-mono text-xs">
                <span class="px-2.5 py-1 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 font-bold">11/11 Trực Chiến Sẵn Sàng</span>
            </div>
        </div>

        <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-300">
                <thead class="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider font-mono">
                    <tr>
                        <th class="py-3 px-4 rounded-l-lg">Phòng Ban</th>
                        <th class="py-3 px-4">Chuyên Môn Cốt Lõi</th>
                        <th class="py-3 px-4">Người Phụ Trách</th>
                        <th class="py-3 px-4">Telegram Topic</th>
                        <th class="py-3 px-4 text-center rounded-r-lg">Trạng Thái</th>
                    </tr>
                </thead>
                <tbody>
                    {dept_rows_html}
                </tbody>
            </table>
        </div>
    </div>

    <!-- FOOTER -->
    <footer class="text-center text-xs text-slate-500 py-3 font-mono">
        Apex Quantitative & Fundamental Multi-Agent Hedge Fund • Powered by Antigravity AI Engine • Phục vụ trực tiếp Chủ tịch Phước Trần
    </footer>

</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ ĐÃ XUẤT BẢN THÀNH CÔNG APEX FOUNDEROS DASHBOARD TẠI: {OUTPUT_HTML}")
    return OUTPUT_HTML


if __name__ == "__main__":
    build_dashboard()
