#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_vn_dashboard.py - Bộ Tạo Giao Diện Interactive Dashboard Thị Trường Chứng Khoán Việt Nam
Tách biệt hoàn toàn, độc lập 100% với hệ thống quốc tế.
Xuất bản tại: VN_Market/dashboard/index.html
"""

import os
import sys
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
import json
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "vn_market_data.json")
BCTC_PATH = os.path.join(BASE_DIR, "data", "vn_bctc_analysis.json")
SPECIALIST_LEDGER = os.path.join(BASE_DIR, "07_Daily_Specialist", "vn_daily_ledger.json")
DASHBOARD_HTML = os.path.join(BASE_DIR, "dashboard", "index.html")

def run():
    print("=== [VN DASHBOARD GENERATOR] ĐANG TẠO GIAO DIỆN INTERACTIVE HTML CHO TTCK VN ===")
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        mkt = json.load(f)
    with open(BCTC_PATH, "r", encoding="utf-8") as f:
        bctc = json.load(f)
        
    orders = []
    if os.path.exists(SPECIALIST_LEDGER):
        with open(SPECIALIST_LEDGER, "r", encoding="utf-8") as f:
            ledger = json.load(f)
            orders = ledger.get("orders", [])
            
    macro = mkt.get("macro_vietnam", {})
    stocks = mkt.get("stocks", {})

    # Tạo bảng HTML rows cho 46 mã cổ phiếu
    table_rows = ""
    for code, stk in stocks.items():
        tech = stk.get("technical", {})
        price = tech.get("price", 0)
        chg = tech.get("day_change_pct", 0)
        chg_class = "text-green" if chg > 0 else ("text-red" if chg < 0 else "text-yellow")
        chg_sign = "+" if chg > 0 else ""
        
        b_info = bctc.get(code, {})
        rating = b_info.get("rating", "A")
        badge_class = "badge-aaa" if rating in ["AAA", "AA"] else ("badge-a" if rating == "A" else "badge-warn")
        
        dir_val = b_info.get("price_direction", "NEUTRAL")
        dir_badge = "badge-bull" if "BULLISH" in dir_val else ("badge-warn" if "OVERBOUGHT" in dir_val else "badge-neut")
        
        pe = stk.get("pe") or "-"
        pb = stk.get("pb") or "-"
        ocf_ratio = b_info.get("ocf_to_profit_ratio", 1.0)
        de = b_info.get("debt_to_equity", 0.5)

        table_rows += f"""
        <tr>
            <td><strong>{code}</strong></td>
            <td><span class="exchange-tag">{stk.get('exchange')}</span></td>
            <td>{stk.get('sector_name')}</td>
            <td><strong>{price:,.0f} đ</strong></td>
            <td class="{chg_class}"><strong>{chg_sign}{chg:.2f}%</strong></td>
            <td>{pe}</td>
            <td>{pb}</td>
            <td>{ocf_ratio}x</td>
            <td>{de}x</td>
            <td><span class="badge {badge_class}">{rating}</span></td>
            <td><span class="badge {dir_badge}">{dir_val}</span></td>
        </tr>
        """

    # Tạo cards cho Sổ lệnh chuyên viên Minh Quân
    order_cards = ""
    for o in orders:
        order_cards += f"""
        <div class="card order-card">
            <div class="card-header">
                <div>
                    <span class="stock-title">{o['code']}</span>
                    <span class="stock-sub">{o['name']} ({o['exchange']})</span>
                </div>
                <span class="badge badge-aaa">EV: +{o['ev_pct']}%</span>
            </div>
            <div class="order-grid">
                <div class="order-metric">
                    <span class="metric-label">Thị giá hiện tại</span>
                    <span class="metric-val">{o['current_price']:,.0f} đ</span>
                </div>
                <div class="order-metric">
                    <span class="metric-label">Vùng mua thăm dò (60%)</span>
                    <span class="metric-val text-blue">{o['probe_price_60']:,.0f} đ</span>
                </div>
                <div class="order-metric">
                    <span class="metric-label">Vùng mua gia tăng (40%)</span>
                    <span class="metric-val text-green">{o['breakout_price_40']:,.0f} đ</span>
                </div>
                <div class="order-metric">
                    <span class="metric-label">Cắt lỗ (Stop 2xATR)</span>
                    <span class="metric-val text-red">{o['stop_loss']:,.0f} đ (-{o['loss_pct']}%)</span>
                </div>
                <div class="order-metric">
                    <span class="metric-label">Mục tiêu chốt lời TP1</span>
                    <span class="metric-val text-green">{o['tp1']:,.0f} đ (+{o['gain_pct']}%)</span>
                </div>
                <div class="order-metric">
                    <span class="metric-label">Tỷ lệ Risk / Reward</span>
                    <span class="metric-val">1:{o['rr_ratio']}</span>
                </div>
            </div>
            <div class="order-footer">
                <small><strong>Chất xúc tác BCTC:</strong> {o['catalysts']}</small>
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hệ Thống AI Multi-Agent Đầu Tư Chứng Khoán Việt Nam</title>
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #182234;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-green: #22c55e;
            --accent-red: #ef4444;
            --accent-yellow: #eab308;
            --border-color: #334155;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background: var(--bg-primary); color: var(--text-primary); padding: 24px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border-color); }}
        .header h1 {{ font-size: 24px; color: var(--accent-blue); }}
        .header p {{ color: var(--text-secondary); font-size: 14px; margin-top: 4px; }}
        
        .macro-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .card {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; }}
        .card h4 {{ color: var(--text-secondary); font-size: 13px; font-weight: normal; margin-bottom: 6px; }}
        .card .value {{ font-size: 20px; font-weight: bold; color: var(--text-primary); }}
        .card .sub {{ font-size: 12px; color: var(--accent-blue); margin-top: 4px; }}

        .section-title {{ font-size: 18px; margin: 24px 0 16px 0; color: var(--accent-blue); display: flex; align-items: center; gap: 8px; }}
        
        .orders-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 16px; margin-bottom: 32px; }}
        .order-card {{ border-left: 4px solid var(--accent-green); }}
        .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }}
        .stock-title {{ font-size: 18px; font-weight: bold; margin-right: 8px; color: #fff; }}
        .stock-sub {{ font-size: 13px; color: var(--text-secondary); }}
        .order-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 12px; }}
        .order-metric {{ background: var(--bg-secondary); padding: 8px 12px; border-radius: 6px; }}
        .metric-label {{ display: block; font-size: 11px; color: var(--text-secondary); }}
        .metric-val {{ display: block; font-size: 14px; font-weight: bold; margin-top: 2px; }}
        .order-footer {{ font-size: 12px; color: var(--text-secondary); line-height: 1.4; border-top: 1px solid var(--border-color); padding-top: 8px; }}

        table {{ width: 100%; border-collapse: collapse; background: var(--bg-card); border-radius: 8px; overflow: hidden; border: 1px solid var(--border-color); }}
        th, td {{ padding: 12px 14px; text-align: left; font-size: 13px; border-bottom: 1px solid var(--border-color); }}
        th {{ background: var(--bg-secondary); color: var(--text-secondary); font-weight: 600; text-transform: uppercase; font-size: 11px; }}
        tr:hover {{ background: rgba(56, 189, 248, 0.05); }}
        
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        .badge-aaa {{ background: rgba(34, 197, 94, 0.2); color: var(--accent-green); border: 1px solid var(--accent-green); }}
        .badge-a {{ background: rgba(56, 189, 248, 0.2); color: var(--accent-blue); }}
        .badge-warn {{ background: rgba(234, 179, 8, 0.2); color: var(--accent-yellow); }}
        .badge-bull {{ background: rgba(34, 197, 94, 0.2); color: var(--accent-green); }}
        .badge-neut {{ background: rgba(148, 163, 184, 0.2); color: var(--text-secondary); }}
        .exchange-tag {{ background: #334155; padding: 2px 6px; border-radius: 4px; font-size: 10px; }}

        .text-green {{ color: var(--accent-green); }}
        .text-red {{ color: var(--accent-red); }}
        .text-yellow {{ color: var(--accent-yellow); }}
        .text-blue {{ color: var(--accent-blue); }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <h1>🏛️ HỆ THỐNG AI ĐẦU TƯ ĐỊNH LƯỢNG & MỔ XẺ BCTC CHỨNG KHOÁN VIỆT NAM</h1>
            <p>Phiên giao dịch: {today_str} | Chu kỳ thanh toán: T+2.5 | Quản trị biên độ: HOSE 7% - HNX 10% | Độc lập 100%</p>
        </div>
        <div>
            <span class="badge badge-aaa">Trạng thái: Hoạt động đồng bộ 7 Ban</span>
        </div>
    </div>

    <div class="macro-grid">
        <div class="card">
            <h4>Lãi Suất Tái Cấp Vốn SBV</h4>
            <div class="value">{macro.get('SBV_Refinancing_Rate', {}).get('value')}%</div>
            <div class="sub">{macro.get('SBV_Refinancing_Rate', {}).get('status')}</div>
        </div>
        <div class="card">
            <h4>Tỷ Giá USD / VND</h4>
            <div class="value">{macro.get('USD_VND_Exchange_Rate', {}).get('value'):,} đ</div>
            <div class="sub">{macro.get('USD_VND_Exchange_Rate', {}).get('trend')}</div>
        </div>
        <div class="card">
            <h4>Tăng Trưởng Tín Dụng YTD</h4>
            <div class="value">{macro.get('Credit_Growth_YTD', {}).get('value')}%</div>
            <div class="sub">Mục tiêu: {macro.get('Credit_Growth_YTD', {}).get('target')}</div>
        </div>
        <div class="card">
            <h4>Giải Ngân Đầu Tư Công</h4>
            <div class="value">{macro.get('Public_Investment_Disbursed_Pct', {}).get('value')}%</div>
            <div class="sub">Thúc đẩy hạ tầng giao thông</div>
        </div>
        <div class="card">
            <h4>Chỉ Số DXY Quốc Tế</h4>
            <div class="value">{macro.get('DXY', {}).get('value')}</div>
            <div class="sub">Lợi suất US10Y: {macro.get('US10Y', {}).get('value')}%</div>
        </div>
    </div>

    <div class="section-title">
        <span>⚡ SỔ LỆNH THỰC THI TRONG NGÀY CỦA CHUYÊN VIÊN MINH QUÂN (BAN 7 — 8H30 AM)</span>
    </div>

    <div class="orders-container">
        {order_cards}
    </div>

    <div class="section-title">
        <span>📊 BẢNG THEO DÕI TOÀN DIỆN 46 SIÊU CỔ PHIẾU ĐẦU NGÀNH (BCTC & DÒNG TIỀN)</span>
    </div>

    <table>
        <thead>
            <tr>
                <th>Mã</th>
                <th>Sàn</th>
                <th>Nhóm Ngành</th>
                <th>Thị Giá</th>
                <th>Biến Động 1D</th>
                <th>P/E</th>
                <th>P/B</th>
                <th>Tiền Thật (OCF/LNST)</th>
                <th>Đòn Bẩy (D/E)</th>
                <th>Xếp Hạng BCTC</th>
                <th>Dự Báo Xu Hướng</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>

</body>
</html>
"""

    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"=== Đã tạo thành công Interactive Dashboard tại: {DASHBOARD_HTML} ===")

if __name__ == "__main__":
    run()
