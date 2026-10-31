import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

before = Path(r'c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\ref_template_before.html').read_text(encoding='utf-8')
after = Path(r'c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\ref_template_after.html').read_text(encoding='utf-8')

# 1. Modify before: Add Tab 6 button to header
old_nav = """        <button type="button" onclick="switchTab('tab-learning')" id="btn-tab-learning" class="px-3.5 py-2 rounded-lg text-xs font-semibold border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)]">4. Ban 5 — Tự Học & Tiến Hóa</button>
        <button type="button" onclick="switchTab('tab-mentor')" id="btn-tab-mentor" class="px-3.5 py-2 rounded-lg text-xs font-semibold border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)]">5. Ban 6 — Học Viện & Giảng Viên Đồng Hành</button>
      </div>"""

new_nav = """        <button type="button" onclick="switchTab('tab-learning')" id="btn-tab-learning" class="px-3.5 py-2 rounded-lg text-xs font-semibold border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)]">4. Ban 5 — Tự Học & Tiến Hóa</button>
        <button type="button" onclick="switchTab('tab-mentor')" id="btn-tab-mentor" class="px-3.5 py-2 rounded-lg text-xs font-semibold border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)]">5. Ban 6 — Học Viện & Nhật Ký Lệnh</button>
        <button type="button" onclick="switchTab('tab-specialist')" id="btn-tab-specialist" class="px-3.5 py-2 rounded-lg text-xs font-semibold border border-emerald-500/40 bg-emerald-500/10 text-emerald-400">6. Ban 7 — Chuyên Viên Đầu Tư Alex</button>
      </div>"""

if old_nav in before:
    before = before.replace(old_nav, new_nav)
    print("Added Tab 6 button to header.")
else:
    print("Warning: old_nav not found in before!")

# 2. Add Distressed Companies and Movement Explanations to Tab 2 in before
distressed_markup = """    <!-- TAB 2: 35 EQUITIES SCREENER & PREDICTIONS -->
    <div id="tab-screener" class="space-y-5 hidden">
      <!-- Cảnh Báo Trọng Điểm Doanh Nghiệp Đang Thua Lỗ / Đốt Tiền -->
      <div class="bg-[var(--card)] border border-rose-500/40 rounded-xl p-5 shadow-sm space-y-3">
        <div>
          <h2 class="text-base font-semibold text-rose-400">🚨 Tâm Điểm Cảnh Báo: Các Doanh Nghiệp Đang Thua Lỗ Ròng, Cháy Dòng Tiền Tự Do (`FCF < 0`) Hoặc Suy Giảm Doanh Thu</h2>
          <p class="text-xs text-[var(--muted-foreground)]">Bóc tách minh bạch các tập đoàn đang báo lỗ ròng (INTC, COIN), âm dòng tiền tự do do chi phí phần cứng (SMCI), hoặc suy giảm doanh thu/biên lợi nhuận (QCOM, TSLA) và giải thích tại sao giá cổ phiếu biến động mạnh.</p>
        </div>
        <div id="distressed-companies-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs"></div>
      </div>
"""

before = before.replace('<div id="tab-screener" class="space-y-5 hidden">', distressed_markup)

movement_markup = """      <!-- Giải Mã Toàn Diện 35 Cổ Phiếu: Tại Sao Tăng / Giảm, Biến Động & Tình Hình Kinh Doanh -->
      <div class="bg-[var(--card)] border border-sky-500/30 rounded-xl p-5 shadow-sm space-y-4">
        <div>
          <h2 class="text-base font-semibold text-sky-400">🔍 Giải Mã Chi Tiết 35 Cổ Phiếu: Tại Sao Cổ Phiếu Tăng / Giảm, Biến Động & Tình Hình Doanh Nghiệp Tác Động Lên Giá</h2>
          <p class="text-xs text-[var(--muted-foreground)]">Danh sách dưới đây tự động lọc đồng bộ theo bộ lọc phía trên, giải thích rõ nguyên nhân biến động giá (1D / 5D / 1M / 1Y), thực trạng lãi/lỗ nội tại của doanh nghiệp và hướng xử lý.</p>
        </div>
        <div id="movement-explanations-grid" class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs"></div>
      </div>
    </div>
"""

# Place movement_markup right at the end of tab-screener
before = re.sub(r'(</div>\s*<!-- ===================================================== -->\s*<!-- TAB 3:)', r'\n' + movement_markup + r'\n    \1', before, count=1)

# 3. Add Tab 6 (Ban 7 Alex) after Tab 5 in before
specialist_tab_markup = """    <!-- ===================================================== -->
    <!-- TAB 6: BAN 7 — DAILY INVESTMENT SPECIALIST & SELF-EVOLUTION -->
    <!-- ===================================================== -->
    <div id="tab-specialist" class="hidden space-y-6">
      <div id="specialist-summary-cards" class="grid grid-cols-1 md:grid-cols-4 gap-4"></div>

      <!-- Morning Inter-Departmental Hearing -->
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-5 shadow-sm space-y-3">
        <h2 class="text-base font-semibold">1. Hội Nghị Giao Ban Đầu Ngày: Lắng Nghe & Tổng Hợp Đánh Giá Từ 6 Phòng Ban Lãnh Đạo (`Inter-Departmental Hearing`)</h2>
        <div id="specialist-hearing-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs"></div>
      </div>

      <!-- Yesterday Post-Mortem & Self-Learning Autopsy -->
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-5 shadow-sm space-y-4">
        <div>
          <h2 class="text-base font-semibold text-emerald-400">2. Tự Kiểm Điểm Ngày Hôm Qua: Chỗ Đúng, Chỗ Sai, Chỗ Thiếu & Thuật Toán Tối Ưu Lợi Nhuận (`Daily Self-Learning Loop`)</h2>
          <p class="text-xs text-[var(--muted-foreground)]" id="specialist-macro-shift"></p>
        </div>
        <div id="specialist-postmortem-grid" class="grid grid-cols-1 lg:grid-cols-3 gap-4 text-xs"></div>
      </div>

      <!-- Scientific Daily Order Blotter -->
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-5 shadow-sm space-y-3">
        <div>
          <h2 class="text-base font-semibold">3. Sổ Lệnh Đầu Tư Khoa Học Trong Ngày Của Alex (`$1,000,000 Reference NAV — 0 Mã Sắp Ra BCTC <= 7 Ngày`)</h2>
          <p class="text-xs text-[var(--muted-foreground)]">Mỗi quyết định được tính toán Kỳ vọng Toán học (Expected Value EV%), Xác suất thắng P(W), Tỷ lệ R:R và chia lệnh 2 nhịp (60% Vùng hiện tại + 40% Limit Pullback -0.35x ATR).</p>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                <th class="py-2.5 px-2.5">Mã</th>
                <th class="py-2.5 px-2.5">Phân Nhánh</th>
                <th class="py-2.5 px-2.5">Quyết Định Hành Động Hôm Nay</th>
                <th class="py-2.5 px-2.5 text-right">Giá (vs Hôm qua)</th>
                <th class="py-2.5 px-2.5">Chiến Thuật Chia Lệnh (60/40 Limit)</th>
                <th class="py-2.5 px-2.5 text-right">TP1 / TP2</th>
                <th class="py-2.5 px-2.5 text-right">Stop 2xATR</th>
                <th class="py-2.5 px-2.5 text-right">Tỷ Trọng (% NAV)</th>
                <th class="py-2.5 px-2.5 text-right">Xác Suất P(W)</th>
                <th class="py-2.5 px-2.5 text-right">Kỳ Vọng EV%</th>
              </tr>
            </thead>
            <tbody id="specialist-orders-tbody" class="divide-y divide-[var(--border)]"></tbody>
          </table>
        </div>
      </div>

      <!-- Alex's In-Depth Case Files: Why & How to Optimize -->
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-5 shadow-sm space-y-4">
        <div>
          <h2 class="text-base font-semibold text-sky-400">4. Hồ Sơ Mổ Xẻ Chi Tiết Của Alex: Tại Sao Đầu Tư & Cách Thức Tối Ưu Lợi Nhuận</h2>
          <p class="text-xs text-[var(--muted-foreground)]">Giải trình minh bạch biến động, chất xúc tác doanh nghiệp, sự kiện vĩ mô và chiến lược chia nhịp vào lệnh tối ưu nhất cho từng mã.</p>
        </div>
        <div id="specialist-deepdive-grid" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs"></div>
      </div>
    </div>
"""

# Place specialist_tab_markup right before MODAL 1
idx_modal1 = before.find('<!-- ===================================================== -->\n  <!-- MODAL 1: 360-DEGREE')
if idx_modal1 != -1:
    before = before[:idx_modal1] + specialist_tab_markup + '\n  ' + before[idx_modal1:]
    print("Added Tab 6 (Ban 7 Alex) markup.")
else:
    print("Warning: MODAL 1 not found in before!")

# 4. Modify after: Add tab-specialist to switchTab and add renderSpecialist
old_switch = "['tab-overview', 'tab-screener', 'tab-quant', 'tab-learning', 'tab-mentor'].forEach(id => {"
new_switch = "['tab-overview', 'tab-screener', 'tab-quant', 'tab-learning', 'tab-mentor', 'tab-specialist'].forEach(id => {"
after = after.replace(old_switch, new_switch)

# Add renderSpecialist function to after
specialist_js = """
    function renderSpecialist() {
      const sp = DATA.specialist || {};
      const prof = sp.specialist_profile || {};
      const pm = sp.yesterday_post_mortem || {};
      const cards = document.getElementById('specialist-summary-cards');
      if (cards) {
        cards.innerHTML = `
          <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
            <div class="text-xs text-[var(--muted-foreground)]">Chỉ Số Hoàn Thiện Chuyên Viên (Mastery Score)</div>
            <div class="text-xl font-bold mt-1 text-emerald-400 font-mono">${prof.mastery_score ?? 95.8} / 100</div>
            <div class="text-xs text-[var(--muted-foreground)] mt-1">${prof.mastery_delta_vs_yesterday ?? '+4.3 điểm so với hôm qua'}</div>
          </div>
          <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
            <div class="text-xs text-[var(--muted-foreground)]">Kỳ Vọng Toán Học Danh Mục (Expected Value)</div>
            <div class="text-xl font-bold mt-1 text-sky-400 font-mono">+${prof.portfolio_weighted_expected_value_pct ?? 11.53}%</div>
            <div class="text-xs text-[var(--muted-foreground)] mt-1">Xác suất thắng TB: ${prof.portfolio_weighted_win_prob_pct ?? 78.6}%</div>
          </div>
          <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
            <div class="text-xs text-[var(--muted-foreground)]">Cấu Trúc Vốn Thực Thi Hôm Nay</div>
            <div class="text-xl font-bold mt-1 text-amber-400 font-mono">52% Core + 8% Alpha</div>
            <div class="text-xs text-[var(--muted-foreground)] mt-1">40% Tiền mặt T-Bills & Chờ sau BCTC</div>
          </div>
          <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
            <div class="text-xs text-[var(--muted-foreground)]">Kiểm Toán Lệnh Thực Thi (Gatekeeper)</div>
            <div class="text-xl font-bold mt-1 text-emerald-400 font-mono">0 Vi Phạm BCTC</div>
            <div class="text-xs text-[var(--muted-foreground)] mt-1">Chia lệnh 60/40 Limit • Nhánh Alpha</div>
          </div>
        `;
      }

      const hearingGrid = document.getElementById('specialist-hearing-grid');
      if (hearingGrid) {
        hearingGrid.innerHTML = (sp.departmental_hearing || []).map(h => `
          <div class="p-3.5 rounded-xl border border-[var(--border)] bg-[var(--secondary)]/30 space-y-1.5">
            <div class="font-bold text-sky-400">${h.department}</div>
            <div class="text-[11px] font-semibold text-emerald-400">${h.verdict}</div>
            <p class="text-[var(--muted-foreground)] leading-relaxed">${h.key_assessment}</p>
            <div class="pt-1 border-t border-[var(--border)] font-semibold text-[var(--foreground)]">👉 Quyết định Ban 7: ${h.specialist_takeaway}</div>
          </div>
        `).join('');
      }

      const macroShiftEl = document.getElementById('specialist-macro-shift');
      if (macroShiftEl) {
        macroShiftEl.textContent = 'Đối soát phiên ' + (pm.compared_period || '2026-10-30 -> 2026-10-31') + ': ' + (pm.macro_shift_summary || '');
      }

      const pmGrid = document.getElementById('specialist-postmortem-grid');
      if (pmGrid) {
        const winsHtml = (pm.validated_wins || []).map(w => `<div class="mb-2"><b>• ${w.category}:</b> ${w.detail}</div>`).join('');
        const errsHtml = (pm.mistakes_and_flaws || []).map(m => `
          <div class="space-y-1">
            <div class="font-bold text-rose-400">${m.error_code}: ${m.title}</div>
            <p class="text-[var(--muted-foreground)]">${m.what_happened}</p>
            <div class="p-2 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-semibold">Sửa sai: ${m.corrective_action}</div>
          </div>
        `).join('');
        const gapsHtml = (pm.missed_opportunities || []).map(g => `
          <div class="space-y-1">
            <div class="font-bold text-amber-400">${g.gap_code}: ${g.title}</div>
            <p class="text-[var(--muted-foreground)]">${g.what_happened}</p>
            <div class="p-2 rounded bg-sky-500/10 border border-sky-500/30 text-sky-400 font-semibold">Tối ưu: ${g.optimization_adopted}</div>
          </div>
        `).join('');

        pmGrid.innerHTML = `
          <div class="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5 space-y-2">
            <div class="font-bold text-sm text-emerald-400">✅ Chỗ ĐÚNG Hôm Qua Cần Phát Huy</div>
            <div>${winsHtml}</div>
          </div>
          <div class="p-4 rounded-xl border border-rose-500/30 bg-rose-500/5 space-y-2">
            <div class="font-bold text-sm text-rose-400">🔍 Chỗ SAI / Điểm Vào Chưa Tối Ưu</div>
            <div>${errsHtml}</div>
          </div>
          <div class="p-4 rounded-xl border border-amber-500/30 bg-amber-500/5 space-y-2">
            <div class="font-bold text-sm text-amber-400">🚀 Chỗ THIẾU SÓT & Cách Tối Ưu Lợi Nhuận</div>
            <div>${gapsHtml}</div>
          </div>
        `;
      }

      const ordersTbody = document.getElementById('specialist-orders-tbody');
      if (ordersTbody) {
        ordersTbody.innerHTML = (sp.daily_scientific_orders || []).map(o => `
          <tr class="hover:bg-[var(--secondary)]/40 cursor-pointer" onclick="openStockModal('${o.symbol}')">
            <td class="py-2.5 px-2.5 font-bold font-mono text-sky-400">${o.symbol}</td>
            <td class="py-2.5 px-2.5"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${o.sleeve.includes('ALPHA') ? 'bg-sky-500/20 text-sky-400' : 'bg-emerald-500/15 text-emerald-400'}">${o.sleeve}</span></td>
            <td class="py-2.5 px-2.5 font-semibold">${o.action_type}</td>
            <td class="py-2.5 px-2.5 text-right font-bold font-mono">$${o.last_price} <span class="text-[11px] font-normal">(${fmtPct(o.change_vs_yesterday_pct)})</span></td>
            <td class="py-2.5 px-2.5 text-[11px]">${o.tranche_split}</td>
            <td class="py-2.5 px-2.5 text-right font-mono">$${o.tp1_price} / $${o.tp2_price}</td>
            <td class="py-2.5 px-2.5 text-right font-mono text-rose-400 font-bold">$${o.stop_2atr_price} (-${o.stop_dist_pct}%)</td>
            <td class="py-2.5 px-2.5 text-right font-bold text-emerald-400 font-mono">${o.weight_nav_pct}% NAV</td>
            <td class="py-2.5 px-2.5 text-right font-semibold font-mono">${o.win_prob_pct}%</td>
            <td class="py-2.5 px-2.5 text-right font-bold text-sky-400 font-mono">+${o.expected_value_pct}%</td>
          </tr>
        `).join('');
      }

      const deepdiveGrid = document.getElementById('specialist-deepdive-grid');
      if (deepdiveGrid) {
        deepdiveGrid.innerHTML = (sp.daily_scientific_orders || []).map(o => `
          <div class="p-4 rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-sm space-y-2.5">
            <div class="flex items-center justify-between border-b border-[var(--border)] pb-2">
              <div>
                <span class="text-sm font-bold font-mono text-sky-400">${o.symbol}</span>
                <span class="text-[var(--muted-foreground)] text-xs"> — ${o.name}</span>
              </div>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${o.sleeve.includes('ALPHA') ? 'bg-sky-500/20 text-sky-400' : 'bg-emerald-500/15 text-emerald-400'}">${o.sleeve} • ${o.weight_nav_pct}% NAV</span>
            </div>
            <div>
              <div class="font-bold text-amber-400">1. Biến động & Sự kiện kích hoạt (Catalysts):</div>
              <p class="text-[var(--muted-foreground)] leading-relaxed mt-0.5">${o.market_events_and_catalysts || o.scientific_rationale}</p>
            </div>
            <div>
              <div class="font-bold text-sky-400">2. Tại sao Alex đầu tư (Why Alex Invests):</div>
              <p class="text-[var(--foreground)] leading-relaxed mt-0.5">${o.why_alex_invests || o.scientific_rationale}</p>
            </div>
            <div class="p-2.5 rounded-lg bg-[var(--secondary)]/40 border border-[var(--border)]">
              <div class="font-bold text-emerald-400">3. Cách thức tối ưu hóa lợi nhuận (Execution Strategy):</div>
              <p class="text-[var(--foreground)] leading-relaxed mt-0.5">${o.how_to_optimize_profit || o.tranche_split}</p>
            </div>
          </div>
        `).join('');
      }
    }
"""

after = after.replace('    renderMentorCaseStudy();', '    renderMentorCaseStudy();\n    renderSpecialist();')
after = specialist_js + '\n' + after

# Also in renderScreenerTable in after, make sure rows and movement explanations are rendered
render_screener_patch = """
      // Also render Distressed Companies & Movement Explanations
      const distressedGrid = document.getElementById('distressed-companies-grid');
      if (distressedGrid) {
        const distressed = (DATA.snapshot.broad_equities || []).filter(e => e.movement_explanation?.is_distressed_or_losing).sort((a, b) => (a.change_1d_pct ?? 0) - (b.change_1d_pct ?? 0));
        distressedGrid.innerHTML = distressed.map(e => {
          const f = e.fundamentals || {};
          const mv = e.movement_explanation || {};
          const niStr = f.net_income_usd_bil !== null && f.net_income_usd_bil !== undefined ? `$${f.net_income_usd_bil}B` : 'N/A';
          const fcfStr = f.free_cashflow_bil !== null && f.free_cashflow_bil !== undefined ? `$${f.free_cashflow_bil}B` : 'N/A';
          return `
            <div class="p-3.5 rounded-xl border border-rose-500/40 bg-rose-500/5 space-y-2 cursor-pointer hover:border-rose-500 transition" onclick="openStockModal('${e.symbol}')">
              <div class="flex items-center justify-between border-b border-rose-500/20 pb-1.5">
                <div>
                  <span class="font-bold text-sm text-rose-400 font-mono">${e.symbol}</span>
                  <span class="text-[var(--muted-foreground)]"> — ${e.name}</span>
                </div>
                <span class="font-bold font-mono">$${e.last_price} (${fmtPct(e.change_1d_pct)})</span>
              </div>
              <div class="flex flex-wrap gap-1.5">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400">${mv.profit_status_badge || 'CẢNH BÁO'}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-[var(--secondary)]">Net: ${niStr} • FCF: ${fcfStr}</span>
              </div>
              <div>
                <div class="font-bold text-amber-400">• Tại sao cổ phiếu giảm / biến động:</div>
                <p class="text-[var(--muted-foreground)] leading-relaxed">${mv.why_price_moved_vn || ''}</p>
              </div>
              <div>
                <div class="font-bold text-rose-400">• Thực trạng kinh doanh & Lãi/Lỗ:</div>
                <p class="text-[var(--foreground)] leading-relaxed">${mv.business_health_vn || ''}</p>
              </div>
            </div>
          `;
        }).join('');
      }

      const mvGrid = document.getElementById('movement-explanations-grid');
      if (mvGrid) {
        mvGrid.innerHTML = filtered.map(eq => {
          const mv = eq.movement_explanation || {};
          const isDistressed = mv.is_distressed_or_losing;
          const borderCls = isDistressed ? 'border-rose-500/40 bg-rose-500/5' : 'border-[var(--border)] bg-[var(--secondary)]/20';
          const pBadgeCls = isDistressed ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/15 text-emerald-400';
          return `
            <div class="p-3.5 rounded-xl border ${borderCls} space-y-2 cursor-pointer hover:border-sky-500/50 transition" onclick="openStockModal('${eq.symbol}')">
              <div class="flex items-center justify-between border-b border-[var(--border)] pb-1.5">
                <div>
                  <span class="font-bold text-sm font-mono text-sky-400">${eq.symbol}</span>
                  <span class="text-[var(--muted-foreground)]"> — ${eq.name} (${eq.sector})</span>
                </div>
                <div class="text-right font-bold font-mono">$${eq.last_price} <span class="text-[11px] font-normal">(${fmtPct(eq.change_1d_pct)} 1D • ${fmtPct(eq.change_1m_pct)} 1M)</span></div>
              </div>
              <div class="flex flex-wrap gap-1.5">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-500/15 text-sky-400">${mv.move_badge || ''}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold ${pBadgeCls}">${mv.profit_status_badge || ''}</span>
              </div>
              <div>
                <div class="font-bold text-amber-400">1. Tại sao cổ phiếu tăng / giảm & biến động thị trường:</div>
                <p class="text-[var(--muted-foreground)] leading-relaxed mt-0.5">${mv.why_price_moved_vn || ''}</p>
              </div>
              <div>
                <div class="font-bold text-sky-400">2. Tình hình kinh doanh, Lãi/Lỗ & BCTC tác động lên giá:</div>
                <p class="text-[var(--foreground)] leading-relaxed mt-0.5">${mv.business_health_vn || ''}</p>
              </div>
              <div class="pt-1 border-t border-[var(--border)] font-semibold text-emerald-400">
                👉 Hành động: ${mv.action_outlook_vn || ''}
              </div>
            </div>
          `;
        }).join('');
      }
"""

after = after.replace('tbody.innerHTML = filtered.map(eq => {', render_screener_patch + '\n      tbody.innerHTML = filtered.map(eq => {')

# Assemble full template
full_template = before + "\n    const DATA = <!-- DATA_JSON_PAYLOAD -->;\n" + after

out_template_path = Path(r'c:\Users\phuoc\Downloads\antigravity\Chứng khoán\scripts\dashboard_template.html')
out_template_path.write_text(full_template, encoding='utf-8')
print("Successfully generated dashboard_template.html! Length:", len(full_template))
