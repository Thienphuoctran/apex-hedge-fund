import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from scripts.vietnam_realtime_feed import fetch_vps_quotes

sys.stdout.reconfigure(encoding='utf-8')

bctc = json.load(open('VN_Market/data/vn_bctc_analysis.json', 'r', encoding='utf-8'))
symbols = list(bctc.keys())
print(f"Total symbols in BCTC: {len(symbols)}")

quotes = fetch_vps_quotes(symbols, timeout=6)
print(f"Fetched quotes for {len(quotes)} symbols")

results = []
for sym, q in quotes.items():
    b = bctc.get(sym, {})
    price = q.get('price', 0)
    ref = q.get('ref_price', 0)
    chg = ((price - ref) / ref * 100) if ref > 0 else 0
    vol = q.get('volume', 0)
    rs = b.get('oneil_rs_rating', 0)
    canslim = b.get('oneil_canslim_score', 0)
    ocf_ratio = b.get('ocf_to_profit_ratio', 0)
    f_score = b.get('piotroski_f_score', 0)
    z_score = b.get('altman_z_score', 0)
    m_score = b.get('beneish_m_score', 0)
    comp_score = b.get('master_composite_score', 0)
    catalyst = b.get('key_catalyst', '')
    
    results.append({
        'symbol': sym,
        'name': b.get('name', sym),
        'sector': b.get('sector_name', ''),
        'price': price,
        'ref': ref,
        'chg_pct': round(chg, 2),
        'vol': vol,
        'rs': rs,
        'canslim': canslim,
        'ocf_ratio': ocf_ratio,
        'f_score': f_score,
        'z_score': z_score,
        'm_score': m_score,
        'comp_score': comp_score,
        'agm_completion': b.get('agm_completion_est_pct', 0),
        'catalyst': catalyst
    })

results.sort(key=lambda x: (x['chg_pct'], x['rs']), reverse=True)

print("\n=== BẢNG THỐNG KÊ TOÀN BỘ 46+ CỔ PHIẾU THEO BIẾN ĐỘNG HÔM NAY (06/11/2026 ~10:00 AM) ===")
green_count = sum(1 for r in results if r['chg_pct'] > 0)
ref_count = sum(1 for r in results if r['chg_pct'] == 0)
red_count = sum(1 for r in results if r['chg_pct'] < 0)
print(f"Tổng quan thị trường trong danh mục theo dõi: Xanh: {green_count} | Tham chiếu: {ref_count} | Đỏ: {red_count}")

print("\n--- TOP XANH / KHÁNG LẠI THỊ TRƯỜNG (RELATIVE STRENGTH CAO NHẤT) ---")
for r in results[:15]:
    print(f"[{r['symbol']}] {r['name']} ({r['sector']}): Giá {r['price']:,.0f} ({r['chg_pct']:+.2f}%) | Vol: {r['vol']:,} | RS: {r['rs']} | OCF/LNST: {r['ocf_ratio']:.2f}x | F-Score: {r['f_score']}/9 | CompScore: {r['comp_score']}/100")
    print(f"    Catalyst: {r['catalyst']}")

print("\n--- CÁC MÃ ĐẦU NGÀNH ĐANG CHIẾT KHẤU / ĐỎ CẦN QUAN SÁT TẠO ĐÁY ---")
reds = [r for r in results if r['chg_pct'] < -1.0 and r['rs'] >= 75]
reds.sort(key=lambda x: x['rs'], reverse=True)
for r in reds[:10]:
    print(f"[{r['symbol']}] {r['name']}: Giá {r['price']:,.0f} ({r['chg_pct']:+.2f}%) | Vol: {r['vol']:,} | RS: {r['rs']} | OCF/LNST: {r['ocf_ratio']:.2f}x | F-Score: {r['f_score']}/9")
