/* ============================================================================
   APEX VIRTUAL OFFICE 2.5D — LIGHT MODERN ISOMETRIC HQ ENGINE
   File: dashboard/office/office.js
   ============================================================================ */
(function () {
    "use strict";

    const ISO_X = 64;
    const ISO_Y = 32;
    const ISO_Z = 28;

    const STATUS_META = {
        working: { label: "Đang làm", color: "#10b981", pillBg: "#dcfce7", pillText: "#166534" },
        waiting_approval: { label: "Chờ duyệt", color: "#f59e0b", pillBg: "#fef3c7", pillText: "#92400e" },
        alert_veto: { label: "Cờ đỏ / VETO", color: "#ef4444", pillBg: "#fee2e2", pillText: "#991b1b" },
        standby: { label: "Trực nhẹ", color: "#64748b", pillBg: "#f1f5f9", pillText: "#475569" },
    };

    const FLOW_TONE_COLORS = {
        pink: "#ec4899",
        emerald: "#10b981",
        sky: "#0ea5e9",
        violet: "#7c3aed",
        rose: "#f43f5e",
        purple: "#c026d3",
        amber: "#d97706",
        red: "#dc2626",
        orange: "#f97316",
        blue: "#3b82f6",
    };

    function getApiBase() {
        if (window.APEX_OFFICE_API_BASE) return window.APEX_OFFICE_API_BASE;
        if (window.location && (window.location.protocol === "http:" || window.location.protocol === "https:") && window.location.host) {
            return "";
        }
        return "http://127.0.0.1:8000";
    }

    function copyTextSafe(txt, successMsg) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(txt).then(() => showToast(successMsg, "success")).catch(() => fallbackCopy(txt, successMsg));
        } else {
            fallbackCopy(txt, successMsg);
        }
    }

    function fallbackCopy(txt, successMsg) {
        try {
            const ta = document.createElement("textarea");
            ta.value = txt;
            ta.style.position = "fixed";
            ta.style.opacity = "0";
            document.body.appendChild(ta);
            ta.select();
            document.execCommand("copy");
            document.body.removeChild(ta);
            showToast(successMsg, "success");
        } catch (_) {
            showToast("Không copy tự động được — Chủ tịch bôi đen copy thủ công nhé.", "warn");
        }
    }

    const state = {
        initialized: false,
        visible: true,
        rootEl: null,
        canvasEl: null,
        ctx: null,
        dpr: 1,
        width: 1100,
        height: 680,
        zoom: 0.92,
        panX: 0,
        panY: 0,
        isDragging: false,
        dragStartX: 0,
        dragStartY: 0,
        dragMoved: false,
        hoveredRoomId: null,
        selectedRoomId: null,
        statusFilter: "all",
        liveData: null,
        roomDetailCache: {},
        kanbanData: null,
        activeModal: null,
        loungeTab: "pool",
        poolGame: null,
        rafId: null,
        pollTimer: null,
        lastTick: 0,
        animTime: 0,
        isFullscreen: false,
    };

    function esc(str) {
        return String(str == null ? "" : str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function fmtVnd(n) {
        const num = Number(n || 0);
        return Math.round(num).toLocaleString("en-US") + " ₫";
    }

    function showToast(msg, type) {
        if (typeof window.showPortalToast === "function") {
            window.showPortalToast(msg, type || "info");
            return;
        }
        const el = document.getElementById("office-local-toast");
        if (!el) return;
        el.innerText = msg;
        el.style.display = "block";
        clearTimeout(el._timer);
        el._timer = setTimeout(() => { el.style.display = "none"; }, 3200);
    }

    function isoToScreen(gx, gy, gz) {
        const cx = state.width * 0.5 + state.panX;
        const cy = state.height * 0.5 + state.panY;
        const centerGx = 4.0;
        const centerGy = 4.05;
        const rx = gx - centerGx;
        const ry = gy - centerGy;
        return {
            x: cx + (rx - ry) * ISO_X * state.zoom,
            y: cy + (rx + ry) * ISO_Y * state.zoom - (gz || 0) * ISO_Z * state.zoom,
        };
    }

    function screenToIso(sx, sy) {
        const cx = state.width * 0.5 + state.panX;
        const cy = state.height * 0.5 + state.panY;
        const dx = (sx - cx) / (ISO_X * state.zoom);
        const dy = (sy - cy) / (ISO_Y * state.zoom);
        return {
            gx: (dx + dy) * 0.5 + 4.0,
            gy: (dy - dx) * 0.5 + 4.05,
        };
    }

    function resetView() {
        const w = state.width || 1100;
        const h = state.height || 680;
        state.zoom = Math.min(1.02, Math.max(0.56, Math.min((w - 110) / 1180, (h - 120) / 620)));
        state.panX = 36;
        state.panY = 18;
    }

    function buildShellDOM(root) {
        root.innerHTML = `
            <canvas class="apex-office-canvas" id="office-iso-canvas"></canvas>
            <div id="office-local-toast" style="display:none;position:absolute;top:68px;left:50%;transform:translateX(-50%);z-index:60;background:#0f172a;color:#f8fafc;padding:8px 16px;border-radius:9999px;font-size:12px;font-weight:700;box-shadow:0 8px 24px rgba(15,23,42,0.28);"></div>

            <!-- TOP LEFT: STATUS LEGEND & FILTER -->
            <div class="office-hud-card office-hud-topleft">
                <div class="office-hud-title">
                    <span>🏢 Sơ Đồ 5 Khối + Tiện Ích</span>
                    <button class="office-btn-sm" id="office-filter-reset" style="font-size:10px;padding:2px 6px;">Tất cả</button>
                </div>
                <div class="office-filter-list" id="office-filter-list">
                    <button class="office-filter-item" data-filter="working">
                        <span class="office-dot-label"><span class="office-status-dot working"></span> Đang tác chiến</span>
                        <span class="office-filter-count" id="cnt-filter-working">0</span>
                    </button>
                    <button class="office-filter-item" data-filter="waiting_approval">
                        <span class="office-dot-label"><span class="office-status-dot waiting_approval"></span> Chờ duyệt / S1–S4</span>
                        <span class="office-filter-count" id="cnt-filter-waiting_approval">0</span>
                    </button>
                    <button class="office-filter-item" data-filter="alert_veto">
                        <span class="office-dot-label"><span class="office-status-dot alert_veto"></span> Cờ đỏ / VETO</span>
                        <span class="office-filter-count" id="cnt-filter-alert_veto">0</span>
                    </button>
                    <button class="office-filter-item" data-filter="standby">
                        <span class="office-dot-label"><span class="office-status-dot standby"></span> Trực 24/7 / Nhẹ</span>
                        <span class="office-filter-count" id="cnt-filter-standby">0</span>
                    </button>
                </div>
            </div>

            <!-- TOP CENTER: LIVE TICKER & WORKFLOW BANNER -->
            <div class="office-hud-topcenter">
                <div class="office-hud-card office-live-pill" id="office-live-pill">
                    <span>🏦 TCBS <strong style="color:#4f46e5;">105C307855</strong></span>
                    <span style="color:#cbd5e1;">|</span>
                    <span>💰 Két: <strong id="office-hud-cash" style="color:#059669;">--</strong></span>
                    <span style="color:#cbd5e1;">|</span>
                    <span>📊 <strong id="office-hud-vni">VNI --</strong></span>
                    <span style="color:#cbd5e1;">|</span>
                    <span id="office-hud-regime" style="color:#b45309;">Đang đồng bộ...</span>
                </div>
                <div class="office-hud-card" style="pointer-events:auto;padding:3px 12px;border-radius:9999px;font-size:10.5px;font-weight:700;color:#334155;">
                    ① Hiền (BCTC) ➔ ② Quân &amp; Alex (Thị trường) ➔ ③ James &amp; Palmer (Kế hoạch) ◀ ④ Victor | ⑤ Trọng &amp; Palmer
                </div>
                <div class="office-job-banner" id="office-job-banner">
                    <span class="office-status-dot working"></span>
                    <span id="office-job-banner-text">Đang chạy tác vụ...</span>
                </div>
            </div>

            <!-- TOP RIGHT: CAMERA & ACTION CONTROLS -->
            <div class="office-hud-card office-hud-topright">
                <button class="office-ctrl-btn" id="office-btn-reset" title="Xem toàn cảnh">🧭 Toàn cảnh</button>
                <button class="office-ctrl-btn" id="office-btn-zoom-in" title="Phóng to">＋</button>
                <button class="office-ctrl-btn" id="office-btn-zoom-out" title="Thu nhỏ">－</button>
                <button class="office-ctrl-btn" id="office-btn-fullscreen" title="Phóng rộng toàn màn hình">⛶</button>
                <button class="office-ctrl-btn primary" id="office-btn-convene">⚡ Họp 5 Khối</button>
                <button class="office-ctrl-btn" id="office-btn-sync" title="Đồng bộ dữ liệu live">🔄</button>
            </div>

            <!-- BOTTOM FLOATING DOCK -->
            <div class="office-hud-card office-hud-dock">
                <button class="office-dock-btn active" data-dock="overview-map">
                    <span>🏛️</span><span>Toàn cảnh HQ</span>
                </button>
                <button class="office-dock-btn" data-dock="kanban">
                    <span>📋</span><span>Công việc</span>
                    <span class="office-dock-badge" id="dock-badge-kanban">0</span>
                </button>
                <button class="office-dock-btn" data-dock="intel">
                    <span>📰</span><span>Băng tin Hiền</span>
                    <span class="office-dock-badge" id="dock-badge-intel">0</span>
                </button>
                <button class="office-dock-btn" data-dock="summary">
                    <span>📊</span><span>Tổng hợp S1–S4</span>
                </button>
                <button class="office-dock-btn" data-dock="lounge">
                    <span>🎱</span><span>Giải trí &amp; Mô phỏng</span>
                </button>
                <span class="office-dock-sep"></span>
                <button class="office-dock-btn" data-dock="tab-reports">
                    <span>📑</span><span>18 Cột Mốc</span>
                </button>
                <button class="office-dock-btn" data-dock="tab-war-room">
                    <span>⚡</span><span>145 Mã Live</span>
                </button>
                <button class="office-dock-btn" data-dock="tab-portfolio">
                    <span>🎖️</span><span>Chỉ huy James</span>
                </button>
            </div>

            <!-- RIGHT SLIDING DRAWER FOR ROOM DETAILS -->
            <aside class="office-drawer" id="office-room-drawer" aria-hidden="true">
                <div class="office-drawer-header">
                    <div>
                        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                            <span id="drawer-room-icon" style="font-size:22px;">🏢</span>
                            <div>
                                <div id="drawer-room-title" style="font-size:15px;font-weight:800;color:#0f172a;">Phòng ban Apex</div>
                                <div id="drawer-room-sub" style="font-size:11.5px;color:#64748b;margin-top:2px;">--</div>
                            </div>
                        </div>
                    </div>
                    <button class="office-drawer-close" id="office-drawer-close" title="Đóng">✕</button>
                </div>
                <div class="office-drawer-body" id="office-drawer-body">
                    <div style="text-align:center;padding:30px;color:#64748b;">Chọn một phòng ban trên bản đồ để xem chi tiết...</div>
                </div>
            </aside>

            <!-- CENTER POPUP MODAL FOR DOCK TOOLS (KANBAN / INTEL / S1-S4 / LOUNGE) -->
            <div class="office-modal-backdrop" id="office-modal-backdrop">
                <div class="office-modal-box">
                    <div class="office-modal-header">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <span id="office-modal-icon" style="font-size:22px;">📋</span>
                            <div>
                                <div id="office-modal-title" style="font-size:15.5px;font-weight:800;">Tiêu đề</div>
                                <div id="office-modal-sub" style="font-size:11.5px;color:#64748b;">Dữ liệu thời gian thực</div>
                            </div>
                        </div>
                        <button class="office-drawer-close" id="office-modal-close">✕</button>
                    </div>
                    <div class="office-modal-body" id="office-modal-body"></div>
                </div>
            </div>
        `;
    }

    function bindEvents() {
        const canvas = state.canvasEl;
        if (!canvas) return;

        // Resize observer
        const doResize = () => {
            if (!state.rootEl || !state.canvasEl) return;
            const rect = state.rootEl.getBoundingClientRect();
            if (rect.width <= 0 || rect.height <= 0) return;
            state.dpr = Math.min(window.devicePixelRatio || 1, 2);
            state.width = rect.width;
            state.height = rect.height;
            state.canvasEl.width = Math.round(rect.width * state.dpr);
            state.canvasEl.height = Math.round(rect.height * state.dpr);
            if (!state._viewInitialized) {
                resetView();
                state._viewInitialized = true;
            }
        };
        window.addEventListener("resize", doResize);
        state._resizeFn = doResize;
        doResize();

        // Pointer drag + click hit-testing
        canvas.addEventListener("mousedown", (e) => {
            state.isDragging = true;
            state.dragMoved = false;
            state.dragStartX = e.clientX;
            state.dragStartY = e.clientY;
        });

        window.addEventListener("mousemove", (e) => {
            if (state.isDragging) {
                const dx = e.clientX - state.dragStartX;
                const dy = e.clientY - state.dragStartY;
                if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
                    state.dragMoved = true;
                }
                state.panX += dx;
                state.panY += dy;
                state.dragStartX = e.clientX;
                state.dragStartY = e.clientY;
                return;
            }
            if (!state.visible) return;
            const rect = canvas.getBoundingClientRect();
            if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) {
                state.hoveredRoomId = null;
                return;
            }
            const hit = hitTestRoom(e.clientX - rect.left, e.clientY - rect.top);
            state.hoveredRoomId = hit ? hit.room_id : null;
            canvas.style.cursor = hit ? "pointer" : "grab";
        });

        window.addEventListener("mouseup", (e) => {
            if (!state.isDragging) return;
            state.isDragging = false;
            if (!state.dragMoved) {
                const rect = canvas.getBoundingClientRect();
                if (e.clientX >= rect.left && e.clientX <= rect.right && e.clientY >= rect.top && e.clientY <= rect.bottom) {
                    const hit = hitTestRoom(e.clientX - rect.left, e.clientY - rect.top);
                    if (hit) {
                        if (hit.room_id === "room_lounge") {
                            openDockModal("lounge");
                        } else {
                            openRoomDrawer(hit.room_id);
                        }
                    } else {
                        closeRoomDrawer();
                    }
                }
            }
        });

        // Touch support for pan & tap
        let touchLast = null;
        let touchMoved = false;
        canvas.addEventListener("touchstart", (e) => {
            if (e.touches.length === 1) {
                touchLast = { x: e.touches[0].clientX, y: e.touches[0].clientY };
                touchMoved = false;
            }
        }, { passive: true });
        canvas.addEventListener("touchmove", (e) => {
            if (e.touches.length === 1 && touchLast) {
                const dx = e.touches[0].clientX - touchLast.x;
                const dy = e.touches[0].clientY - touchLast.y;
                if (Math.abs(dx) > 4 || Math.abs(dy) > 4) touchMoved = true;
                state.panX += dx;
                state.panY += dy;
                touchLast = { x: e.touches[0].clientX, y: e.touches[0].clientY };
            }
        }, { passive: true });
        canvas.addEventListener("touchend", (e) => {
            if (!touchMoved && e.changedTouches.length === 1) {
                const rect = canvas.getBoundingClientRect();
                const hit = hitTestRoom(e.changedTouches[0].clientX - rect.left, e.changedTouches[0].clientY - rect.top);
                if (hit) {
                    if (hit.room_id === "room_lounge") openDockModal("lounge");
                    else openRoomDrawer(hit.room_id);
                }
            }
            touchLast = null;
        });

        canvas.addEventListener("wheel", (e) => {
            e.preventDefault();
            const factor = e.deltaY < 0 ? 1.1 : 0.91;
            const newZoom = Math.min(1.85, Math.max(0.55, state.zoom * factor));
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left - state.width * 0.5;
            const my = e.clientY - rect.top - state.height * 0.5;
            const ratio = newZoom / state.zoom;
            state.panX = mx - (mx - state.panX) * ratio;
            state.panY = my - (my - state.panY) * ratio;
            state.zoom = newZoom;
        }, { passive: false });

        canvas.addEventListener("dblclick", (e) => {
            const rect = canvas.getBoundingClientRect();
            const hit = hitTestRoom(e.clientX - rect.left, e.clientY - rect.top);
            if (hit) focusOnRoom(hit);
            else resetView();
        });

        // HUD buttons
        document.getElementById("office-btn-reset").onclick = () => resetView();
        document.getElementById("office-btn-zoom-in").onclick = () => {
            state.zoom = Math.min(1.85, state.zoom * 1.15);
        };
        document.getElementById("office-btn-zoom-out").onclick = () => {
            state.zoom = Math.max(0.55, state.zoom * 0.87);
        };
        document.getElementById("office-btn-fullscreen").onclick = () => {
            state.isFullscreen = !state.isFullscreen;
            state.rootEl.classList.toggle("is-fullscreen", state.isFullscreen);
            setTimeout(() => state._resizeFn && state._resizeFn(), 40);
        };
        document.getElementById("office-btn-sync").onclick = async () => {
            await fetchLiveState(true);
            showToast("Đã đồng bộ dữ liệu sống toàn văn phòng Apex!", "success");
        };
        document.getElementById("office-btn-convene").onclick = async () => {
            await triggerRoomAction("team_james_palmer", "convene_dept", {
                directive: "Hội nghị giao ban 5 Khối theo quy trình: Hiền -> Minh Quân & Alex -> James & Palmer <- Victor"
            });
        };

        // Status filters
        document.getElementById("office-filter-reset").onclick = () => setStatusFilter("all");
        document.querySelectorAll("#office-filter-list .office-filter-item").forEach((btn) => {
            btn.onclick = () => {
                const f = btn.getAttribute("data-filter");
                setStatusFilter(state.statusFilter === f ? "all" : f);
            };
        });

        // Drawer close
        document.getElementById("office-drawer-close").onclick = closeRoomDrawer;

        // Modal close
        document.getElementById("office-modal-close").onclick = closeDockModal;
        document.getElementById("office-modal-backdrop").addEventListener("click", (e) => {
            if (e.target && e.target.id === "office-modal-backdrop") closeDockModal();
        });

        // Dock navigation
        document.querySelectorAll(".office-dock-btn").forEach((btn) => {
            btn.onclick = () => {
                const target = btn.getAttribute("data-dock");
                if (target === "tab-reports" && typeof window.switchTab === "function") {
                    window.switchTab("reports");
                    return;
                }
                if (target === "tab-war-room" && typeof window.switchTab === "function") {
                    window.switchTab("war-room");
                    return;
                }
                if (target === "tab-portfolio" && typeof window.switchTab === "function") {
                    window.switchTab("portfolio");
                    return;
                }
                if (target === "overview-map") {
                    closeDockModal();
                    closeRoomDrawer();
                    resetView();
                    return;
                }
                if (target === "tab-reports") {
                    openRoomDrawer("team_hien");
                    showToast("Đang mở Khối 1 (Hiền) & danh sách báo cáo thật (mở localhost:8000 để xem Thư viện 18 Cột Mốc).", "info");
                    return;
                }
                if (target === "tab-war-room") {
                    openRoomDrawer("team_victor");
                    showToast("Đang mở Khối 4 (Victor) & Radar 145 Mã Live.", "info");
                    return;
                }
                if (target === "tab-portfolio") {
                    openRoomDrawer("team_james_palmer");
                    showToast("Đang mở Khối 3 (James & Palmer) — Kế hoạch đầu tư.", "info");
                    return;
                }
                openDockModal(target);
            };
        });
    }

    function setStatusFilter(filterVal) {
        state.statusFilter = filterVal;
        document.querySelectorAll("#office-filter-list .office-filter-item").forEach((btn) => {
            btn.classList.toggle("active", btn.getAttribute("data-filter") === filterVal);
        });
    }

    function focusOnRoom(room) {
        const cx = room.gx + room.gw * 0.5;
        const cy = room.gy + room.gd * 0.5;
        state.zoom = 1.15;
        state.panX = -((cx - 4.0) - (cy - 4.05)) * ISO_X * state.zoom;
        state.panY = -((cx - 4.0) + (cy - 4.05)) * ISO_Y * state.zoom;
    }

    function hitTestRoom(sx, sy) {
        const rooms = (state.liveData && state.liveData.rooms) || [];
        const pt = screenToIso(sx, sy);
        // Check from frontmost to backmost
        const sorted = [...rooms].sort((a, b) => (b.gx + b.gw * 0.5 + b.gy + b.gd * 0.5) - (a.gx + a.gw * 0.5 + a.gy + a.gd * 0.5));
        for (const r of sorted) {
            if (pt.gx >= r.gx - 0.08 && pt.gx <= r.gx + r.gw + 0.08 && pt.gy >= r.gy - 0.08 && pt.gy <= r.gy + r.gd + 0.08) {
                return r;
            }
        }
        // Also test slight elevated click on walls / floating label
        const ptWall = screenToIso(sx, sy + 26 * state.zoom);
        for (const r of sorted) {
            if (ptWall.gx >= r.gx && ptWall.gx <= r.gx + r.gw && ptWall.gy >= r.gy && ptWall.gy <= r.gy + r.gd) {
                return r;
            }
        }
        return null;
    }

    // ========================================================================
    // ISOMETRIC DRAWING PRIMITIVES
    // ========================================================================
    function drawPoly(ctx, pts, fill, stroke, lineWidth) {
        ctx.beginPath();
        ctx.moveTo(pts[0].x, pts[0].y);
        for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i].x, pts[i].y);
        ctx.closePath();
        if (fill) {
            ctx.fillStyle = fill;
            ctx.fill();
        }
        if (stroke) {
            ctx.strokeStyle = stroke;
            ctx.lineWidth = lineWidth || 1;
            ctx.stroke();
        }
    }

    function drawIsoBox(ctx, gx, gy, gz, gw, gd, gh, colors) {
        const p00 = isoToScreen(gx, gy, gz);
        const p10 = isoToScreen(gx + gw, gy, gz);
        const p11 = isoToScreen(gx + gw, gy + gd, gz);
        const p01 = isoToScreen(gx, gy + gd, gz);

        const t00 = isoToScreen(gx, gy, gz + gh);
        const t10 = isoToScreen(gx + gw, gy, gz + gh);
        const t11 = isoToScreen(gx + gw, gy + gd, gz + gh);
        const t01 = isoToScreen(gx, gy + gd, gz + gh);

        // Right front face (gx+gw side -> visible on right)
        drawPoly(ctx, [p10, p11, t11, t10], colors.right || "#cbd5e1", colors.stroke || null, 0.8);
        // Left front face (gy+gd side -> visible on left)
        drawPoly(ctx, [p01, p11, t11, t01], colors.left || "#e2e8f0", colors.stroke || null, 0.8);
        // Top face
        drawPoly(ctx, [t00, t10, t11, t01], colors.top || "#ffffff", colors.stroke || null, 0.8);
    }

    function drawRoundRect(ctx, x, y, w, h, r, fill, stroke, lineWidth) {
        const rad = Math.min(r, w * 0.5, h * 0.5);
        ctx.beginPath();
        ctx.moveTo(x + rad, y);
        ctx.arcTo(x + w, y, x + w, y + h, rad);
        ctx.arcTo(x + w, y + h, x, y + h, rad);
        ctx.arcTo(x, y + h, x, y, rad);
        ctx.arcTo(x, y, x + w, y, rad);
        ctx.closePath();
        if (fill) {
            ctx.fillStyle = fill;
            ctx.fill();
        }
        if (stroke) {
            ctx.strokeStyle = stroke;
            ctx.lineWidth = lineWidth || 1;
            ctx.stroke();
        }
    }

    function drawCampusBase(ctx) {
        // Large campus lawn slab for 5 Executive Teams + Lounge + Park
        const c0 = isoToScreen(-1.9, -0.5, 0);
        const c1 = isoToScreen(8.6, -0.5, 0);
        const c2 = isoToScreen(8.6, 8.4, 0);
        const c3 = isoToScreen(-1.9, 8.4, 0);

        const b0 = isoToScreen(-1.9, -0.5, -0.22);
        const b1 = isoToScreen(8.6, -0.5, -0.22);
        const b2 = isoToScreen(8.6, 8.4, -0.22);
        const b3 = isoToScreen(-1.9, 8.4, -0.22);
        drawPoly(ctx, [c3, c2, b2, b3], "#b7dba0");
        drawPoly(ctx, [c1, c2, b2, b1], "#9ecb85");
        drawPoly(ctx, [c0, c1, c2, c3], "#dff4cf", "#b6de9a", 1.5);

        ctx.save();
        ctx.strokeStyle = "rgba(134, 197, 94, 0.22)";
        ctx.lineWidth = 1;
        for (let gx = -1; gx <= 8; gx += 1) {
            const a = isoToScreen(gx, -0.5, 0);
            const b = isoToScreen(gx, 8.4, 0);
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
        }
        for (let gy = 0; gy <= 8; gy += 1) {
            const a = isoToScreen(-1.9, gy, 0);
            const b = isoToScreen(8.6, gy, 0);
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
        }
        ctx.restore();

        // Main wide corridors between the 5 Teams & Lounge
        const walkways = [
            { x1: 0.2, y1: 2.35, x2: 7.9, y2: 3.05 },
            { x1: 0.2, y1: 5.15, x2: 7.9, y2: 5.85 },
            { x1: 3.5, y1: 0.3, x2: 4.25, y2: 7.7 },
            { x1: 3.95, y1: 3.0, x2: 4.65, y2: 7.7 },
        ];
        for (const wk of walkways) {
            const p0 = isoToScreen(wk.x1, wk.y1, 0.01);
            const p1 = isoToScreen(wk.x2, wk.y1, 0.01);
            const p2 = isoToScreen(wk.x2, wk.y2, 0.01);
            const p3 = isoToScreen(wk.x1, wk.y2, 0.01);
            drawPoly(ctx, [p0, p1, p2, p3], "#f1f5f9", "#e2e8f0", 1);
        }

        // Park pond in bottom-left lawn
        const pondCenter = isoToScreen(-1.05, 6.1, 0.02);
        ctx.save();
        ctx.beginPath();
        ctx.ellipse(pondCenter.x, pondCenter.y, 44 * state.zoom, 22 * state.zoom, 0, 0, Math.PI * 2);
        ctx.fillStyle = "#bae6fd";
        ctx.fill();
        ctx.strokeStyle = "#7dd3fc";
        ctx.lineWidth = 2 * state.zoom;
        ctx.stroke();
        ctx.restore();
    }

    function drawTree(ctx, gx, gy, scale) {
        const s = (scale || 1) * state.zoom;
        const base = isoToScreen(gx, gy, 0.02);
        ctx.save();
        // Shadow
        ctx.fillStyle = "rgba(15, 23, 42, 0.10)";
        ctx.beginPath();
        ctx.ellipse(base.x + 4 * s, base.y + 3 * s, 16 * s, 8 * s, 0, 0, Math.PI * 2);
        ctx.fill();
        // Trunk
        ctx.fillStyle = "#92400e";
        ctx.fillRect(base.x - 3 * s, base.y - 16 * s, 6 * s, 16 * s);
        // Canopy layers
        ctx.fillStyle = "#22c55e";
        ctx.beginPath();
        ctx.arc(base.x, base.y - 24 * s, 14 * s, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#4ade80";
        ctx.beginPath();
        ctx.arc(base.x - 5 * s, base.y - 28 * s, 10 * s, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#86efac";
        ctx.beginPath();
        ctx.arc(base.x + 5 * s, base.y - 31 * s, 7 * s, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }

    function drawFerrisWheel(ctx, gx, gy, t) {
        const base = isoToScreen(gx, gy, 0.05);
        const z = state.zoom;
        const r = 42 * z;
        const cx = base.x;
        const cy = base.y - 54 * z;

        ctx.save();
        // Base shadow & legs
        ctx.fillStyle = "rgba(15, 23, 42, 0.12)";
        ctx.beginPath();
        ctx.ellipse(base.x, base.y + 3 * z, 32 * z, 14 * z, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = "#475569";
        ctx.lineWidth = 3.2 * z;
        ctx.beginPath();
        ctx.moveTo(base.x - 18 * z, base.y);
        ctx.lineTo(cx, cy);
        ctx.lineTo(base.x + 18 * z, base.y);
        ctx.stroke();

        // Outer rim
        ctx.strokeStyle = "#f43f5e";
        ctx.lineWidth = 3 * z;
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.stroke();

        ctx.strokeStyle = "#fda4af";
        ctx.lineWidth = 1.4 * z;
        ctx.beginPath();
        ctx.arc(cx, cy, r * 0.72, 0, Math.PI * 2);
        ctx.stroke();

        // Spokes & cabins
        const cabinColors = ["#ef4444", "#f59e0b", "#10b981", "#3b82f6", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316"];
        for (let i = 0; i < 8; i++) {
            const ang = t * 0.45 + (i * Math.PI) / 4;
            const px = cx + Math.cos(ang) * r;
            const py = cy + Math.sin(ang) * r;
            ctx.strokeStyle = "#94a3b8";
            ctx.lineWidth = 1.2 * z;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(px, py);
            ctx.stroke();

            // Cabin
            drawRoundRect(ctx, px - 6 * z, py - 2 * z, 12 * z, 10 * z, 3 * z, cabinColors[i % cabinColors.length], "#ffffff", 1.2 * z);
        }
        // Hub
        ctx.fillStyle = "#1e293b";
        ctx.beginPath();
        ctx.arc(cx, cy, 5 * z, 0, Math.PI * 2);
        ctx.fill();

        // Park sign
        drawRoundRect(ctx, base.x - 42 * z, base.y + 8 * z, 84 * z, 18 * z, 9 * z, "rgba(255,255,255,0.92)", "#86efac", 1);
        ctx.fillStyle = "#166534";
        ctx.font = `700 ${Math.max(9, Math.round(10 * z))}px "Plus Jakarta Sans", sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("🎡 Công Viên Apex", base.x, base.y + 17 * z);
        ctx.restore();
    }

    function drawDataFlows(ctx, t, layer) {
        const flows = (state.liveData && state.liveData.data_flows) || [];
        const rooms = (state.liveData && state.liveData.rooms) || [];
        const roomMap = {};
        for (const r of rooms) roomMap[r.room_id] = r;

        const hasRunningJob = rooms.some((r) => r.active_job && r.active_job.status === "RUNNING");
        const speed = hasRunningJob ? 0.52 : 0.24;
        const drawLines = !layer || layer === "lines";
        const drawBadges = !layer || layer === "badges";

        ctx.save();
        for (let i = 0; i < flows.length; i++) {
            const f = flows[i];
            const src = roomMap[f.from];
            const dst = roomMap[f.to];
            if (!src || !dst) continue;

            const p1 = isoToScreen(src.gx + src.gw * 0.5, src.gy + src.gd * 0.5, 0.06);
            const p2 = isoToScreen(dst.gx + dst.gw * 0.5, dst.gy + dst.gd * 0.5, 0.06);
            const col = FLOW_TONE_COLORS[f.tone] || "#4f46e5";

            if (drawLines) {
                ctx.strokeStyle = col + "66";
                ctx.lineWidth = 2.6 * state.zoom;
                ctx.setLineDash([6 * state.zoom, 5 * state.zoom]);
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
                ctx.setLineDash([]);
            }

            if (drawBadges) {
                // Midpoints sit inside corridors between teams; draw arrow, badge & animated packet cleanly on top
                const mx = (p1.x + p2.x) * 0.5;
                const my = (p1.y + p2.y) * 0.5;
                const ang = Math.atan2(p2.y - p1.y, p2.x - p1.x);
                const aSize = 6.5 * state.zoom;
                ctx.fillStyle = col;
                ctx.beginPath();
                ctx.moveTo(mx + Math.cos(ang) * aSize, my + Math.sin(ang) * aSize);
                ctx.lineTo(mx + Math.cos(ang + 2.4) * aSize, my + Math.sin(ang + 2.4) * aSize);
                ctx.lineTo(mx + Math.cos(ang - 2.4) * aSize, my + Math.sin(ang - 2.4) * aSize);
                ctx.closePath();
                ctx.fill();

                if (f.label && state.zoom >= 0.72) {
                    ctx.font = `700 ${Math.max(8, Math.round(9.5 * state.zoom))}px "Plus Jakarta Sans", sans-serif`;
                    const tw = ctx.measureText(f.label).width + 12 * state.zoom;
                    const th = 16 * state.zoom;
                    drawRoundRect(ctx, mx - tw * 0.5, my - th - 6 * state.zoom, tw, th, 8 * state.zoom, "rgba(255,255,255,0.95)", col + "99", 1);
                    ctx.fillStyle = col;
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillText(f.label, mx, my - th * 0.5 - 6 * state.zoom);
                }

                // Animated moving data packet
                const phase = (t * speed + i * 0.19) % 1;
                const px = p1.x + (p2.x - p1.x) * phase;
                const py = p1.y + (p2.y - p1.y) * phase;
                ctx.fillStyle = col;
                ctx.beginPath();
                ctx.arc(px, py, 4.3 * state.zoom, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#ffffff";
                ctx.beginPath();
                ctx.arc(px, py, 1.7 * state.zoom, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        ctx.restore();
    }

    function drawAvatar(ctx, gx, gy, gz, avatar, statusCode, t, idx) {
        const z = state.zoom;
        const bob = statusCode === "working" ? Math.sin(t * 6 + idx * 1.4) * 2.5 : Math.sin(t * 2 + idx) * 0.9;
        const pos = isoToScreen(gx, gy, gz);
        const ax = pos.x;
        const ay = pos.y - bob * z * 0.4;

        ctx.save();
        // Shadow
        ctx.fillStyle = "rgba(15, 23, 42, 0.15)";
        ctx.beginPath();
        ctx.ellipse(pos.x, pos.y + 2 * z, 9 * z, 4.5 * z, 0, 0, Math.PI * 2);
        ctx.fill();

        // Body
        drawRoundRect(ctx, ax - 7 * z, ay - 22 * z, 14 * z, 16 * z, 5 * z, avatar.color || "#4f46e5", "#ffffff", 1.2 * z);
        // Head
        ctx.fillStyle = "#fde68a";
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1.4 * z;
        ctx.beginPath();
        ctx.arc(ax, ay - 28 * z, 7 * z, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        // Hair cap
        ctx.fillStyle = "#1e293b";
        ctx.beginPath();
        ctx.arc(ax, ay - 30.5 * z, 6.2 * z, Math.PI, Math.PI * 2);
        ctx.fill();

        // Nameplate under avatar
        if (state.zoom >= 0.78) {
            ctx.fillStyle = "rgba(15, 23, 42, 0.78)";
            const lbl = avatar.name || "AI";
            ctx.font = `700 ${Math.max(8, Math.round(9 * z))}px "Plus Jakarta Sans", sans-serif`;
            const tw = ctx.measureText(lbl).width + 8 * z;
            drawRoundRect(ctx, ax - tw * 0.5, ay + 4 * z, tw, 13 * z, 6 * z, "rgba(255,255,255,0.92)", "#cbd5e1", 0.8);
            ctx.fillStyle = "#0f172a";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(lbl, ax, ay + 10.5 * z);
        }
        ctx.restore();
    }

    function drawRoomFurniture(ctx, r, t) {
        const isWorking = r.status_code === "working";
        const screenGlow = isWorking ? "#38bdf8" : (r.status_code === "alert_veto" ? "#f87171" : "#94a3b8");

        if (r.furniture === "billiard_lounge") {
            drawIsoBox(ctx, r.gx + 0.65, r.gy + 0.45, 0.08, 1.35, 0.72, 0.36, {
                top: "#15803d", left: "#78350f", right: "#92400e", stroke: "#451a03"
            });
            const balls = [
                { dx: 0.9, dy: 0.8, c: "#ffffff" },
                { dx: 1.45, dy: 0.72, c: "#ef4444" },
                { dx: 1.55, dy: 0.88, c: "#eab308" },
                { dx: 1.65, dy: 0.8, c: "#2563eb" },
            ];
            for (const b of balls) {
                const p = isoToScreen(r.gx + b.dx, r.gy + b.dy, 0.46);
                ctx.fillStyle = b.c;
                ctx.beginPath();
                ctx.arc(p.x, p.y, 3.2 * state.zoom, 0, Math.PI * 2);
                ctx.fill();
            }
            return;
        }

        if (r.furniture === "cio_command_suite") {
            // Executive command roundtable + triple wall monitor
            drawIsoBox(ctx, r.gx + 0.85, r.gy + 0.55, 0.08, 1.65, 0.85, 0.34, {
                top: "#e0e7ff", left: "#c7d2fe", right: "#a5b4fc", stroke: "#6366f1"
            });
            drawIsoBox(ctx, r.gx + 1.15, r.gy + 0.62, 0.42, 0.95, 0.1, 0.36, {
                top: "#1e293b", left: screenGlow, right: "#0f172a", stroke: "#0f172a"
            });
            return;
        }

        if (r.furniture === "victor_radar_wall") {
            // Live trading radar terminal desk
            drawIsoBox(ctx, r.gx + 0.65, r.gy + 0.42, 0.08, 1.65, 0.58, 0.34, {
                top: "#fef3c7", left: "#fde68a", right: "#fcd34d", stroke: "#d97706"
            });
            drawIsoBox(ctx, r.gx + 0.8, r.gy + 0.46, 0.42, 1.25, 0.09, 0.38, {
                top: "#0f172a", left: "#f59e0b", right: "#1e293b", stroke: "#0f172a"
            });
            return;
        }

        if (r.furniture === "audit_vault") {
            // Ombudsman inspection table + SHA-256 vault
            drawIsoBox(ctx, r.gx + 0.65, r.gy + 0.42, 0.08, 1.45, 0.58, 0.32, {
                top: "#ffffff", left: "#fecaca", right: "#fca5a5", stroke: "#dc2626"
            });
            drawIsoBox(ctx, r.gx + r.gw - 0.65, r.gy + 0.25, 0.08, 0.44, 0.44, 0.64, {
                top: "#94a3b8", left: "#64748b", right: "#475569", stroke: "#1e293b"
            });
            return;
        }

        // Dual workstations for Team Hiền & Team Minh Quân & Alex
        drawIsoBox(ctx, r.gx + 0.45, r.gy + 0.36, 0.08, 1.15, 0.5, 0.32, {
            top: "#ffffff", left: "#e2e8f0", right: "#cbd5e1", stroke: "#94a3b8"
        });
        drawIsoBox(ctx, r.gx + 0.62, r.gy + 0.4, 0.4, 0.52, 0.08, 0.3, {
            top: "#1e293b", left: screenGlow, right: "#0f172a", stroke: "#0f172a"
        });

        drawIsoBox(ctx, r.gx + 1.85, r.gy + 0.36, 0.08, 1.05, 0.5, 0.32, {
            top: "#ffffff", left: "#e2e8f0", right: "#cbd5e1", stroke: "#94a3b8"
        });
        drawIsoBox(ctx, r.gx + 2.02, r.gy + 0.4, 0.4, 0.5, 0.08, 0.3, {
            top: "#1e293b", left: screenGlow, right: "#0f172a", stroke: "#0f172a"
        });

        if (isWorking || r.status_code === "alert_veto") {
            const led = isoToScreen(r.gx + 0.88, r.gy + 0.46, 0.58);
            ctx.fillStyle = r.status_code === "alert_veto" ? "#ef4444" : (Math.sin(t * 7) > 0 ? "#10b981" : "#34d399");
            ctx.beginPath();
            ctx.arc(led.x, led.y, 3.2 * state.zoom, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function drawRoom(ctx, r, t) {
        const z = state.zoom;
        const isHovered = state.hoveredRoomId === r.room_id;
        const isSelected = state.selectedRoomId === r.room_id;
        const dimmed = state.statusFilter !== "all" && r.status_code !== state.statusFilter;

        ctx.save();
        if (dimmed) ctx.globalAlpha = 0.32;

        // Drop shadow under room pad
        const s0 = isoToScreen(r.gx, r.gy, 0.01);
        const s1 = isoToScreen(r.gx + r.gw, r.gy, 0.01);
        const s2 = isoToScreen(r.gx + r.gw, r.gy + r.gd, 0.01);
        const s3 = isoToScreen(r.gx, r.gy + r.gd, 0.01);
        ctx.fillStyle = isHovered || isSelected ? "rgba(79, 70, 229, 0.18)" : "rgba(15, 23, 42, 0.10)";
        drawPoly(ctx, [
            { x: s0.x + 4 * z, y: s0.y + 6 * z },
            { x: s1.x + 4 * z, y: s1.y + 6 * z },
            { x: s2.x + 4 * z, y: s2.y + 6 * z },
            { x: s3.x + 4 * z, y: s3.y + 6 * z },
        ], ctx.fillStyle);

        // Floor slab
        const strokeCol = isSelected ? "#4f46e5" : (isHovered ? r.accent : "#cbd5e1");
        drawIsoBox(ctx, r.gx, r.gy, 0.0, r.gw, r.gd, 0.08, {
            top: r.floor_tint || "#ffffff",
            left: "#e2e8f0",
            right: "#cbd5e1",
            stroke: strokeCol,
        });

        // Highlight border if selected or hovered
        if (isHovered || isSelected) {
            const f0 = isoToScreen(r.gx, r.gy, 0.085);
            const f1 = isoToScreen(r.gx + r.gw, r.gy, 0.085);
            const f2 = isoToScreen(r.gx + r.gw, r.gy + r.gd, 0.085);
            const f3 = isoToScreen(r.gx, r.gy + r.gd, 0.085);
            drawPoly(ctx, [f0, f1, f2, f3], null, isSelected ? "#4f46e5" : r.accent, 2.4 * z);
        }

        // Accent inner rug
        const rg0 = isoToScreen(r.gx + 0.2, r.gy + 0.2, 0.082);
        const rg1 = isoToScreen(r.gx + r.gw - 0.2, r.gy + 0.2, 0.082);
        const rg2 = isoToScreen(r.gx + r.gw - 0.2, r.gy + r.gd - 0.2, 0.082);
        const rg3 = isoToScreen(r.gx + 0.2, r.gy + r.gd - 0.2, 0.082);
        drawPoly(ctx, [rg0, rg1, rg2, rg3], (r.accent || "#6366f1") + "14", (r.accent || "#6366f1") + "40", 1);

        // Low 2.5D back walls (top-left & top-right so interior stays visible!)
        drawIsoBox(ctx, r.gx, r.gy, 0.08, r.gw, 0.09, 0.72, {
            top: "#f8fafc",
            left: "#f1f5f9",
            right: "#e2e8f0",
            stroke: "#cbd5e1",
        });
        drawIsoBox(ctx, r.gx, r.gy, 0.08, 0.09, r.gd, 0.72, {
            top: "#f8fafc",
            left: "#e2e8f0",
            right: "#f1f5f9",
            stroke: "#cbd5e1",
        });
        // Colored accent stripe along top wall
        drawIsoBox(ctx, r.gx + 0.1, r.gy, 0.76, r.gw - 0.1, 0.09, 0.08, {
            top: r.accent,
            left: r.accent,
            right: r.accent,
        });

        // Furniture & AI avatars
        drawRoomFurniture(ctx, r, t);
        const avatars = r.avatars || [];
        const avStep = avatars.length > 1 ? Math.min(0.68, (r.gw - 0.85) / (avatars.length - 1)) : 0;
        const avStart = avatars.length > 1 ? Math.max(0.48, (r.gw - avStep * (avatars.length - 1)) * 0.5) : r.gw * 0.5;
        avatars.forEach((av, i) => {
            const ax = r.gx + avStart + i * avStep;
            const ay = r.gy + r.gd - 0.42;
            drawAvatar(ctx, ax, ay, 0.08, av, r.status_code, t, i);
        });

        // Floating Room Name Pill above top corner
        const tagPos = isoToScreen(r.gx + r.gw * 0.48, r.gy + 0.1, 1.05);
        const stMeta = STATUS_META[r.status_code] || STATUS_META.standby;
        const labelTxt = `${r.icon} ${r.short_name}`;
        ctx.font = `800 ${Math.max(10, Math.round(11.5 * z))}px "Plus Jakarta Sans", sans-serif`;
        const textW = ctx.measureText(labelTxt).width;
        const pillW = textW + 46 * z;
        const pillH = 24 * z;
        const px = tagPos.x - pillW * 0.5;
        const py = tagPos.y - pillH * 0.5;

        drawRoundRect(
            ctx,
            px,
            py,
            pillW,
            pillH,
            12 * z,
            isSelected ? "#eef2ff" : "rgba(255, 255, 255, 0.96)",
            isSelected ? "#4f46e5" : (isHovered ? r.accent : "#cbd5e1"),
            isSelected || isHovered ? 2 : 1.2
        );

        // Status pulse dot
        const dotX = px + 13 * z;
        const dotY = py + pillH * 0.5;
        if (r.status_code === "working" || r.status_code === "alert_veto") {
            const pulseR = (5.5 + Math.sin(t * 5) * 2.5) * z;
            ctx.fillStyle = stMeta.color + "33";
            ctx.beginPath();
            ctx.arc(dotX, dotY, pulseR, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.fillStyle = stMeta.color;
        ctx.beginPath();
        ctx.arc(dotX, dotY, 4.2 * z, 0, Math.PI * 2);
        ctx.fill();

        // Label text
        ctx.fillStyle = "#0f172a";
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";
        ctx.fillText(labelTxt, px + 22 * z, dotY + 0.5);

        // Report count micro-badge
        if (r.reports_count > 0) {
            const bx = px + pillW - 14 * z;
            ctx.fillStyle = r.accent + "22";
            ctx.beginPath();
            ctx.arc(bx, dotY, 8 * z, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = r.accent;
            ctx.font = `800 ${Math.max(8, Math.round(9 * z))}px "JetBrains Mono", monospace`;
            ctx.textAlign = "center";
            ctx.fillText(String(r.reports_count), bx, dotY + 0.5);
        }

        // Live thought bubble when hovered, selected, or actively working
        if ((isHovered || isSelected || r.status_code === "working" || r.status_code === "alert_veto") && r.live_thought && z >= 0.72) {
            const thought = r.live_thought.length > 40 ? r.live_thought.slice(0, 38) + "…" : r.live_thought;
            ctx.font = `600 ${Math.max(9, Math.round(10 * z))}px "Plus Jakarta Sans", sans-serif`;
            const tw = ctx.measureText(thought).width + 16 * z;
            const th = 19 * z;
            const bx = tagPos.x - tw * 0.5;
            const by = py - th - 5 * z;
            drawRoundRect(ctx, bx, by, tw, th, 9 * z, "rgba(15, 23, 42, 0.88)", null);
            ctx.fillStyle = "#f8fafc";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(thought, tagPos.x, by + th * 0.5);
        }

        ctx.restore();
    }

    function renderFrame(ts) {
        if (!state.visible) {
            state.rafId = null;
            return;
        }
        const dt = state.lastTick ? Math.min(0.05, (ts - state.lastTick) / 1000) : 0.016;
        state.lastTick = ts;
        state.animTime += dt;

        const ctx = state.ctx;
        if (ctx) {
            ctx.save();
            ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);
            ctx.clearRect(0, 0, state.width, state.height);

            drawCampusBase(ctx);
            drawDataFlows(ctx, state.animTime, "lines");

            // Trees around 5-Team campus perimeter (clear of rooms & walkways)
            const trees = [
                [-1.3, 0.4, 1.0], [-1.4, 2.5, 0.95], [-1.2, 4.4, 1.05],
                [8.25, 0.7, 0.95], [8.25, 3.8, 1.0], [8.25, 7.2, 0.9],
                [0.8, 8.05, 0.85], [4.2, 8.05, 0.9], [7.2, 8.05, 0.85],
            ];
            for (const tr of trees) {
                if (tr[1] < 3.6) drawTree(ctx, tr[0], tr[1], tr[2]);
            }

            // Sort rooms back-to-front by isometric depth (gx + gy)
            const rooms = (state.liveData && state.liveData.rooms) || [];
            const sortedRooms = [...rooms].sort((a, b) => (a.gx + a.gw * 0.5 + a.gy + a.gd * 0.5) - (b.gx + b.gw * 0.5 + b.gy + b.gd * 0.5));
            for (const r of sortedRooms) {
                drawRoom(ctx, r, state.animTime);
            }

            // Draw workflow midpoint badges & moving packets in walkways cleanly above room edges
            drawDataFlows(ctx, state.animTime, "badges");

            // Foreground trees & Ferris wheel in bottom-left park
            for (const tr of trees) {
                if (tr[1] >= 3.6) drawTree(ctx, tr[0], tr[1], tr[2]);
            }
            drawFerrisWheel(ctx, -1.0, 7.0, state.animTime);

            ctx.restore();
        }
        state.rafId = requestAnimationFrame(renderFrame);
    }

    function startAnimLoop() {
        if (!state.rafId && state.visible) {
            state.lastTick = 0;
            state.rafId = requestAnimationFrame(renderFrame);
        }
    }

    function stopAnimLoop() {
        if (state.rafId) {
            cancelAnimationFrame(state.rafId);
            state.rafId = null;
        }
    }

    // ========================================================================
    // LIVE DATA FETCH & HUD UPDATES
    // ========================================================================
    async function fetchLiveState(forceRefresh) {
        if (!state.liveData && window.APEX_OFFICE_BOOTSTRAP_BUNDLE) {
            state.liveData = window.APEX_OFFICE_BOOTSTRAP_BUNDLE;
            if (!state.kanbanData && window.APEX_OFFICE_BOOTSTRAP_BUNDLE.kanban_board) {
                state.kanbanData = window.APEX_OFFICE_BOOTSTRAP_BUNDLE.kanban_board;
            }
            updateHUD(state.liveData);
        }
        try {
            const url = getApiBase() + "/api/office/live_status" + (forceRefresh ? "?force=1" : "");
            const ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
            const timer = ctrl ? setTimeout(() => ctrl.abort(), 3800) : null;
            const res = await fetch(url, { cache: "no-store", signal: ctrl ? ctrl.signal : undefined });
            if (timer) clearTimeout(timer);
            if (!res.ok) return;
            const data = await res.json();
            if (!data || !data.ok) return;
            state.liveData = data;
            if (data.kanban_board) state.kanbanData = data.kanban_board;
            updateHUD(data);
            if (state.selectedRoomId && document.getElementById("office-room-drawer").classList.contains("open")) {
                loadAndRenderRoomDrawer(state.selectedRoomId, forceRefresh);
            }
            if (state.activeModal) {
                refreshActiveModalIfNeeded();
            }
        } catch (err) {
            if (!state.liveData && window.APEX_OFFICE_BOOTSTRAP_BUNDLE) {
                state.liveData = window.APEX_OFFICE_BOOTSTRAP_BUNDLE;
                updateHUD(state.liveData);
            }
        }
    }

    function updateHUD(data) {
        const sc = data.status_counts || {};
        ["working", "waiting_approval", "alert_veto", "standby"].forEach((k) => {
            const el = document.getElementById("cnt-filter-" + k);
            if (el) el.innerText = String(sc[k] || 0);
        });

        const ssot = data.ssot || {};
        const mkt = data.market_live || {};
        const cashEl = document.getElementById("office-hud-cash");
        if (cashEl) cashEl.innerText = `${ssot.cash_str || "--"} (${Number(ssot.cash_pct || 100).toFixed(0)}%)`;

        const vniEl = document.getElementById("office-hud-vni");
        if (vniEl) {
            const vni = mkt.vn_index ? Number(mkt.vn_index).toFixed(2) : "--";
            const chg = mkt.vn_index_chg_pct != null ? `${Number(mkt.vn_index_chg_pct) >= 0 ? "+" : ""}${Number(mkt.vn_index_chg_pct).toFixed(2)}%` : "";
            vniEl.innerText = `VNI ${vni} ${chg}`.trim();
        }

        const regEl = document.getElementById("office-hud-regime");
        if (regEl) regEl.innerText = `${mkt.live_regime || "STANDBY"} • ${data.generated_at || ""}`;

        const kCounts = data.kanban_counts || {};
        const kbBadge = document.getElementById("dock-badge-kanban");
        if (kbBadge) kbBadge.innerText = String(kCounts.total || 0);

        const intelCnt = ((data.intel_feed || {}).summary_counts || {}).total_news_articles || 0;
        const intelBadge = document.getElementById("dock-badge-intel");
        if (intelBadge) intelBadge.innerText = String(intelCnt);

        // Active running job banner
        const jobs = data.jobs || [];
        const runningJob = jobs.find((j) => j.status === "RUNNING");
        const jobBanner = document.getElementById("office-job-banner");
        const jobText = document.getElementById("office-job-banner-text");
        if (jobBanner && jobText) {
            if (runningJob) {
                jobBanner.classList.add("show");
                jobText.innerText = runningJob.title;
            } else {
                jobBanner.classList.remove("show");
            }
        }
    }

    function scheduleNextPoll() {
        clearTimeout(state.pollTimer);
        if (!state.visible || document.hidden) return;
        const jobs = (state.liveData && state.liveData.jobs) || [];
        const hasRunning = jobs.some((j) => j.status === "RUNNING");
        const delayMs = hasRunning ? 2000 : 6000;
        state.pollTimer = setTimeout(async () => {
            await fetchLiveState(false);
            scheduleNextPoll();
        }, delayMs);
    }

    // ========================================================================
    // ROOM SIDE DRAWER (REAL DETAILS, PACKETS, REPORTS & 1-CLICK ACTIONS)
    // ========================================================================
    async function openRoomDrawer(roomId) {
        state.selectedRoomId = roomId;
        const drawer = document.getElementById("office-room-drawer");
        const body = document.getElementById("office-drawer-body");
        if (!drawer || !body) return;
        drawer.classList.add("open");
        drawer.setAttribute("aria-hidden", "false");
        body.innerHTML = `<div style="text-align:center;padding:30px;color:#64748b;">⏳ Đang tải hồ sơ phòng ban...</div>`;
        await loadAndRenderRoomDrawer(roomId, false);
    }

    function closeRoomDrawer() {
        state.selectedRoomId = null;
        const drawer = document.getElementById("office-room-drawer");
        if (drawer) {
            drawer.classList.remove("open");
            drawer.setAttribute("aria-hidden", "true");
        }
    }

    async function loadAndRenderRoomDrawer(roomId, force) {
        try {
            const url = `${getApiBase()}/api/office/room?id=${encodeURIComponent(roomId)}${force ? "&force=1" : ""}`;
            const ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
            const timer = ctrl ? setTimeout(() => ctrl.abort(), 3500) : null;
            const res = await fetch(url, { cache: "no-store", signal: ctrl ? ctrl.signal : undefined });
            if (timer) clearTimeout(timer);
            const data = await res.json();
            if (data && data.ok && data.room) {
                renderRoomDrawerContent(data.room);
                return;
            }
        } catch (_) {
            // Fallback offline từ bundle nhúng sẵn trong Artifact Chat
        }
        const bndl = window.APEX_OFFICE_BOOTSTRAP_BUNDLE || {};
        const detailMap = bndl.rooms_detail || {};
        const fallbackList = ((state.liveData || {}).rooms) || bndl.rooms || [];
        const localRoom = detailMap[roomId] || fallbackList.find((x) => x.room_id === roomId);
        if (localRoom) {
            renderRoomDrawerContent(localRoom);
        } else {
            document.getElementById("office-drawer-body").innerHTML = `<div style="color:#ef4444;">Không tìm thấy phòng ban: ${esc(roomId)}</div>`;
        }
    }

    function renderSpecializedSection(r) {
        const sp = r.specialized_data || {};
        if (r.room_id === "team_hien") {
            const news = sp.latest_news || [];
            const sc = sp.summary_counts || {};
            const picks = sp.top_vn_alpha || [];
            return `
                <div class="office-section-box">
                    <div class="office-section-title">
                        <span>📰 Băng Tin IR &amp; Pháp Y BCTC (${esc(sc.total_news_articles || 0)} bài • ${picks.length} Alpha)</span>
                        <button class="office-btn-sm" onclick="window.ApexVirtualOffice.openDockModal('intel')">Xem Toàn Bộ</button>
                    </div>
                    <div style="font-size:11px;color:#64748b;margin-bottom:8px;">Cập nhật: ${esc(sp.crawled_at || "--")} • ${esc(sc.verified_ir_portals || 0)} cổng IR • ${esc(sc.sec_edgar_filings || 0)} hồ sơ SEC EDGAR</div>
                    ${picks.slice(0, 4).map((p) => `
                        <div class="office-news-item" style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
                            <div>
                                <strong style="font-size:12px;">${esc(p.symbol)}</strong>
                                <span style="font-size:11px;color:#64748b;">(${esc(p.alpha_score)}đ • F=${esc(p.piotroski_f_score)}/9 • ROE ${esc(p.roe_pct)}%)</span>
                                <div style="font-size:11px;color:#059669;">OCF/LNST: ${esc(p.ocf_ratio)}x • MOS: ${esc(p.margin_of_safety_pct)}%</div>
                            </div>
                            <button class="office-btn-sm" onclick="window.ApexVirtualOffice.triggerRoomAction('team_quan_alex','convene_dept',{ticker:'${esc(p.symbol)}',directive:'Phân tích thị trường & điểm mua mã ${esc(p.symbol)} từ hồ sơ BCTC Hiền'})">➔ Đẩy Quân &amp; Alex</button>
                        </div>
                    `).join("")}
                    ${news.slice(0, 4).map((n) => `
                        <div class="office-news-item">
                            <div style="display:flex;justify-content:space-between;gap:6px;margin-bottom:3px;">
                                <strong style="font-size:11px;color:#db2777;">${esc(n.symbol)}</strong>
                                <span style="font-size:10.5px;color:#64748b;">${esc(n.source_name)}</span>
                            </div>
                            <div style="font-size:12px;font-weight:700;color:#0f172a;margin-bottom:5px;">${esc(n.title)}</div>
                            <div style="display:flex;gap:6px;flex-wrap:wrap;">
                                ${n.source_url ? `<a href="${esc(n.source_url)}" target="_blank" rel="noopener noreferrer" class="office-btn-sm" style="text-decoration:none;">🔗 Nguồn</a>` : ""}
                                <button class="office-btn-sm" onclick="window.ApexVirtualOffice.triggerRoomAction('team_quan_alex','convene_dept',{ticker:'${esc(n.symbol)}',directive:'Thẩm định catalyst & điểm vào mã ${esc(n.symbol)} từ tin Hiền'})">➔ Gửi Quân &amp; Alex</button>
                            </div>
                        </div>
                    `).join("")}
                </div>
            `;
        }
        if (r.room_id === "team_quan_alex") {
            const wl = sp.approved_watchlist || [];
            const rules = sp.risk_rules || [];
            const rm = (sp.spillover || {}).risk_multiplier || 1.0;
            return `
                <div class="office-section-box">
                    <div class="office-section-title">
                        <span>🎯 Phân Tích Thị Trường &amp; Rổ Q3/2026 (Mult ${esc(rm)}x)</span>
                        <button class="office-btn-sm" onclick="window.ApexVirtualOffice.openDockModal('summary')">Ma trận S1–S4</button>
                    </div>
                    <div style="font-size:11.5px;color:#334155;margin-bottom:6px;">${esc(sp.constitution_mandate || "")}</div>
                    ${rules.length ? `<div style="font-size:11px;color:#7c3aed;background:#f5f3ff;border-radius:8px;padding:6px 8px;margin-bottom:8px;">${rules.map((rl) => `• ${esc(rl)}`).join("<br>")}</div>` : ""}
                    ${wl.map((w) => `
                        <div class="office-news-item">
                            <div style="display:flex;justify-content:space-between;font-size:12px;">
                                <strong>${esc(w.symbol)} — ${esc(w.name)}</strong>
                                <span style="color:#7c3aed;font-weight:700;">${esc(w.weekly_limit)}</span>
                            </div>
                            <div style="font-size:11px;color:#475569;margin-top:3px;">${esc(w.entry_zone)} | Stop: ${esc(w.stop_loss_2xatr)}</div>
                            <div style="margin-top:5px;">
                                <button class="office-btn-sm" onclick="window.ApexVirtualOffice.triggerRoomAction('team_james_palmer','convene_dept',{ticker:'${esc(w.symbol)}',directive:'Trình James & Palmer chốt kế hoạch giải ngân ${esc(w.symbol)} (${esc(w.entry_zone)})'})">🎖️ Trình James Chốt Kế Hoạch</button>
                            </div>
                        </div>
                    `).join("")}
                </div>
            `;
        }
        if (r.room_id === "team_james_palmer") {
            const ssot = sp.ssot || {};
            const ls = sp.latest_session || {};
            const t10 = ((sp.walk_forward || {})["T+10"] || {}).hit_rate_pct || "--";
            return `
                <div class="office-section-box">
                    <div class="office-section-title"><span>🎖️ Két Tiền Thật &amp; Kế Hoạch Đầu Tư Trình Chủ Tịch</span></div>
                    <div style="font-size:12px;color:#0f172a;margin-bottom:6px;">
                        💰 Tiền mặt: <strong style="color:#059669;">${esc(ssot.cash_str)}</strong> (${esc(ssot.cash_pct)}%) • Vị thế: <strong>${esc(ssot.holdings_count)} CP</strong> • T+10 Hit Rate: <strong>${esc(t10)}%</strong>
                    </div>
                    <div style="font-size:11.5px;background:#ffffff;border:1px solid #e2e8f0;border-radius:9px;padding:8px;">
                        <div><strong>Phiên:</strong> ${esc(ls.session_id || "--")} (${esc(ls.quorum_count || 0)}/${esc(ls.roster_total || 14)} Ban)</div>
                        <div style="margin-top:3px;"><strong>Phán quyết:</strong> <span style="color:#4f46e5;font-weight:700;">${esc(ls.final_verdict || "--")}</span></div>
                        <div style="margin-top:3px;color:#334155;">${esc(ls.action_plan || "")}</div>
                    </div>
                </div>
            `;
        }
        if (r.room_id === "team_victor") {
            const rec = sp.recon_summary || {};
            const sectors = sp.top_5_sectors || [];
            const tw = sp.trigger_watch || [];
            return `
                <div class="office-section-box">
                    <div class="office-section-title">
                        <span>🚨 Radar Bảng Điện 145 Mã &amp; Ngưỡng Báo James</span>
                        <button class="office-btn-sm" onclick="window.ApexVirtualOffice.triggerRoomAction('team_james_palmer','convene_dept',{directive:'Victor báo cáo mã chạm ngưỡng từ Radar 145 mã sang James xử lý ngay'})">⚡ Báo James Ngay</button>
                    </div>
                    <div style="font-size:12px;margin-bottom:6px;">
                        VN-Index: <strong>${esc(rec.vn_index || "--")}</strong> (${esc(rec.vn_index_chg_pct || 0)}%) • Breadth MA20: <strong>${esc(rec.live_breadth_ma20_pct || 0)}%</strong> • BuyUp: <strong>${esc(rec.avg_buy_up_pct || 0)}%</strong>
                    </div>
                    <div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px;">
                        ${sectors.slice(0, 5).map((s) => `<span class="office-btn-sm">${esc(s.sector)}: ${Number(s.avg_change_pct) >= 0 ? "+" : ""}${esc(s.avg_change_pct)}%</span>`).join("")}
                    </div>
                    ${tw.map((w) => `
                        <div class="office-news-item" style="font-size:11.5px;">
                            <strong>${esc(w.symbol)}</strong> • Mua: <span style="color:#059669;">${esc(w.buy_zone)}</span> • Stop: <span style="color:#dc2626;">${esc(w.stop)}</span> • TP1: <strong>${esc(w.tp1)}</strong>
                        </div>
                    `).join("")}
                </div>
            `;
        }
        if (r.room_id === "team_trong_palmer") {
            const aud = sp.latest_audit_entry || {};
            return `
                <div class="office-section-box">
                    <div class="office-section-title"><span>🛡️ Kiểm Toán 10 Điều Hiến Chương &amp; Toàn Hệ Thống</span></div>
                    <div style="font-size:12px;">
                        <div>Điểm Hội Đồng: <strong>${esc(sp.ombudsman_audit_score || "10/10")}</strong> • Kỷ luật: <strong>${esc(aud.overall_discipline_score || 100)}</strong> • Vấn đề mở: <strong>${esc(aud.issues_count || 0)}</strong></div>
                        <div style="font-size:11px;color:#64748b;margin-top:4px;word-break:break-all;">SHA-256: <code>${esc(sp.constitutional_seal_sha256 || "--")}</code></div>
                    </div>
                </div>
            `;
        }
        return "";
    }

    function renderRoomDrawerContent(r) {
        const iconEl = document.getElementById("drawer-room-icon");
        const titleEl = document.getElementById("drawer-room-title");
        const subEl = document.getElementById("drawer-room-sub");
        const body = document.getElementById("office-drawer-body");
        if (!body) return;

        if (iconEl) iconEl.innerText = r.icon || "🏢";
        if (titleEl) titleEl.innerText = `${r.ban_code}: ${r.name}`;
        if (subEl) subEl.innerText = `${r.lead_title || ""} • Phụ trách: ${(r.officers || []).join(", ")}`;

        const subDeptHtml = (r.sub_departments || []).length
            ? `<div style="display:flex;flex-direction:column;gap:4px;margin-top:8px;">${r.sub_departments.map((sd) => {
                const txt = typeof sd === "string"
                    ? esc(sd)
                    : `<strong>${esc(sd.code || sd.name || "")}</strong>${sd.role ? `: <span style="color:#475569;">${esc(sd.role)}</span>` : ""}`;
                return `<div style="font-size:11px;background:#ffffff;border:1px solid #cbd5e1;border-radius:7px;padding:4px 8px;color:#0f172a;">${txt}</div>`;
            }).join("")}</div>`
            : "";

        const reportsHtml = (r.recent_reports || []).length
            ? r.recent_reports.map((rep) => `
                <button class="office-report-item" data-rel-path="${esc(rep.rel_path)}">
                    <div style="min-width:0;">
                        <div style="font-size:12px;font-weight:700;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${esc(rep.title)}</div>
                        <div style="font-size:10.5px;color:#64748b;">${esc(rep.date)} ${esc(rep.time_str)} • ${esc(rep.shift_label)}</div>
                    </div>
                    <span style="font-size:11px;font-weight:700;color:#4f46e5;flex-shrink:0;">${typeof window.openReportModal === "function" ? "Đọc →" : "Copy lệnh →"}</span>
                </button>
            `).join("")
            : `<div style="font-size:12px;color:#64748b;">Chưa có tệp báo cáo Markdown riêng trong khối này.</div>`;

        const votesHtml = (r.latest_votes || []).map((v) => `
            <div style="font-size:11.5px;background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:7px 9px;margin-bottom:5px;">
                <div><strong>${esc(v.officer)}</strong> • Phiếu: <strong style="color:#4f46e5;">${esc(v.vote)}</strong></div>
                <div style="color:#475569;margin-top:2px;">${esc(v.rationale)}</div>
            </div>
        `).join("");

        const tasksHtml = (r.kanban_tasks || []).map((t) => `
            <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;font-size:11.5px;background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:6px 8px;margin-bottom:4px;">
                <span style="min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${esc(t.scheduled_time)} • ${esc(t.title)}</span>
                <span class="office-btn-sm" style="flex-shrink:0;">${esc(t.status)}</span>
            </div>
        `).join("");

        const pa = r.primary_action || {};
        const isJobRunning = r.active_job && r.active_job.status === "RUNNING";
        const defaultCmd = r.chat_template || `Palmer giao việc cho ${r.ban_code}: rà soát và báo cáo ngay.`;

        body.innerHTML = `
            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;">
                <span class="office-status-pill ${esc(r.status_code)}">● ${esc(r.status_label_vi)}</span>
                <span style="font-size:11px;font-weight:700;color:${r.veto_power ? "#dc2626" : "#64748b"};">${r.veto_power ? "🛡️ Có quyền Phủ quyết VETO" : "📡 Khối Chuyên Môn"}</span>
            </div>

            <div class="office-section-box" style="background:linear-gradient(135deg,#eef2ff 0%,#f8fafc 100%);border-color:#c7d2fe;">
                <div class="office-section-title"><span>💬 Giao Việc Trực Tiếp Sang Khung Chat Palmer</span></div>
                <div style="font-size:11px;color:#475569;margin-bottom:6px;">Luồng bàn giao: <strong>${esc(r.handoff_to || "")}</strong></div>
                <textarea id="drawer-palmer-cmd" class="office-input" rows="2" style="width:100%;resize:vertical;font-size:11.5px;line-height:1.4;">${esc(defaultCmd)}</textarea>
                <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:6px;">
                    <select id="drawer-cmd-ticker" class="office-select" style="font-size:11px;padding:4px 8px;">
                        <option value="">-- Gắn mã CP --</option>
                        <option value="TPB">TPB</option>
                        <option value="HDB">HDB</option>
                        <option value="CTG">CTG</option>
                        <option value="HPG">HPG</option>
                        <option value="VPB">VPB</option>
                        <option value="MSH">MSH</option>
                        <option value="BAF">BAF</option>
                        <option value="NVDA">NVDA</option>
                    </select>
                    <button class="office-btn-sm" id="drawer-copy-palmer-btn" style="background:#4f46e5;color:#fff;border-color:#4f46e5;flex:1;">📋 Copy Lệnh Dán Sang Chat</button>
                </div>
            </div>

            <div class="office-section-box">
                <div class="office-section-title"><span>⏱️ Lịch Chạy &amp; Cơ Cấu Bộ Phận</span></div>
                <div style="font-size:12px;font-weight:700;color:#0f172a;margin-bottom:4px;">${esc(r.kpi_summary)}</div>
                <div style="font-size:11.5px;color:#475569;">${esc(r.schedule)}</div>
                ${subDeptHtml}
                <div style="margin-top:10px;">
                    <button class="office-btn-action" id="drawer-primary-action-btn" ${isJobRunning ? "disabled" : ""}>
                        ${isJobRunning ? "⏳ Đang chạy tác vụ..." : esc(pa.label || "⚡ Chạy Tác Vụ Khối")}
                    </button>
                </div>
            </div>

            ${renderSpecializedSection(r)}

            ${votesHtml ? `<div class="office-section-box"><div class="office-section-title"><span>🗣️ Phát Ngôn Hội Đồng Gần Nhất</span></div>${votesHtml}</div>` : ""}

            <div class="office-section-box">
                <div class="office-section-title">
                    <span>📑 Báo Cáo Thật Của Khối (${(r.recent_reports || []).length})</span>
                </div>
                <div style="display:flex;flex-direction:column;gap:6px;">${reportsHtml}</div>
            </div>

            <div class="office-section-box">
                <div class="office-section-title">
                    <span>📋 Nhiệm Vụ Kanban (${(r.kanban_tasks || []).length})</span>
                    <button class="office-btn-sm" onclick="window.ApexVirtualOffice.openDockModal('kanban')">Mở Bảng Kanban</button>
                </div>
                ${tasksHtml || `<div style="font-size:11.5px;color:#64748b;">Chưa có thẻ việc gán riêng cho khối này.</div>`}
                <div style="display:flex;gap:6px;margin-top:8px;">
                    <input type="text" id="drawer-new-task-input" class="office-input" style="flex:1;" placeholder="Giao nhanh việc mới cho ${esc(r.ban_code)}...">
                    <button class="office-btn-sm" id="drawer-new-task-btn" style="background:#0f172a;color:#fff;border-color:#0f172a;">+ Giao</button>
                </div>
            </div>
        `;

        // Bind report click (Portal modal OR copy-to-chat command in Artifact sandbox)
        body.querySelectorAll(".office-report-item[data-rel-path]").forEach((btn) => {
            btn.onclick = () => {
                const rel = btn.getAttribute("data-rel-path");
                if (typeof window.openReportModal === "function") {
                    window.openReportModal(rel);
                } else {
                    copyTextSafe(`Palmer hãy đọc và tóm tắt chi tiết báo cáo ${rel}`, `Đã copy lệnh đọc báo cáo — Dán sang khung chat Palmer!`);
                }
            };
        });

        const tickerSel = document.getElementById("drawer-cmd-ticker");
        const cmdBox = document.getElementById("drawer-palmer-cmd");
        if (tickerSel && cmdBox) {
            tickerSel.onchange = () => {
                const sym = tickerSel.value;
                if (!sym) return;
                cmdBox.value = defaultCmd.includes("...") ? defaultCmd : `${defaultCmd.replace(/\.$/, "")} Trọng tâm mã ${sym}.`;
            };
        }
        const copyBtn = document.getElementById("drawer-copy-palmer-btn");
        if (copyBtn && cmdBox) {
            copyBtn.onclick = () => copyTextSafe(cmdBox.value.trim(), "Đã copy chỉ thị — Chủ tịch dán sang chat cho Palmer thực thi ngay!");
        }

        const actionBtn = document.getElementById("drawer-primary-action-btn");
        if (actionBtn) {
            actionBtn.onclick = () => {
                if (pa.action === "open_lounge_modal") {
                    openDockModal("lounge");
                } else {
                    const sym = tickerSel ? tickerSel.value : "";
                    triggerRoomAction(r.room_id, pa.action, sym ? { ticker: sym } : {});
                }
            };
        }

        const addTaskBtn = document.getElementById("drawer-new-task-btn");
        if (addTaskBtn) {
            addTaskBtn.onclick = async () => {
                const inp = document.getElementById("drawer-new-task-input");
                const title = (inp && inp.value || "").trim();
                if (!title) return;
                await createKanbanTask({
                    title,
                    dept: r.ban_code,
                    assignee: (r.officers || ["Trưởng Khối"])[0],
                    priority: "HIGH",
                });
                inp.value = "";
                await loadAndRenderRoomDrawer(r.room_id, true);
            };
        }
    }

    // ========================================================================
    // ROOM ACTIONS & KANBAN API CALLS
    // ========================================================================
    async function triggerRoomAction(roomId, action, payload) {
        const rooms = ((state.liveData || {}).rooms) || [];
        const rm = rooms.find((x) => x.room_id === roomId);
        try {
            const res = await fetch(getApiBase() + "/api/office/room_action", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ room_id: roomId, action: action, ...(payload || {}) }),
            });
            const data = await res.json();
            if (!data.ok) {
                showToast("Không thực thi được tác vụ: " + (data.error || "Lỗi"), "error");
                return data;
            }
            showToast(data.message || "Đã kích hoạt tác vụ!", "success");
            await fetchLiveState(true);
            scheduleNextPoll();
            return data;
        } catch (err) {
            const cmd = (payload && payload.directive) || (rm && rm.chat_template) || `Palmer kích hoạt ${roomId} (${action})`;
            copyTextSafe(cmd, "Sandbox Chat đã copy lệnh sang clipboard — Chủ tịch dán sang khung chat Palmer!");
            return { ok: false, error: err.message, copied_cmd: cmd };
        }
    }

    async function createKanbanTask(taskPayload) {
        try {
            const res = await fetch(getApiBase() + "/api/office/kanban", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ op: "create", ...taskPayload }),
            });
            const data = await res.json();
            if (data.ok) {
                state.kanbanData = data.board;
                showToast("Đã giao nhiệm vụ mới vào Kanban!", "success");
                await fetchLiveState(true);
            } else {
                showToast(data.error || "Lỗi giao việc", "error");
            }
            return data;
        } catch (_) {
            const kb = state.kanbanData || { columns: { BACKLOG: [], IN_PROGRESS: [], AUDIT_REVIEW: [], DONE: [] }, tasks: {} };
            const tid = "OFFICE-" + Date.now();
            kb.tasks = kb.tasks || {};
            kb.columns = kb.columns || { BACKLOG: [], IN_PROGRESS: [], AUDIT_REVIEW: [], DONE: [] };
            kb.tasks[tid] = {
                task_id: tid,
                title: taskPayload.title || "Nhiệm vụ mới",
                dept: taskPayload.dept || "Khối 3",
                assignee: taskPayload.assignee || "Palmer & James",
                priority: taskPayload.priority || "HIGH",
                status: "BACKLOG",
                scheduled_time: taskPayload.scheduled_time || "LIVE",
            };
            kb.columns.BACKLOG = [tid].concat(kb.columns.BACKLOG || []);
            state.kanbanData = kb;
            copyTextSafe(`Palmer giao việc cho ${taskPayload.dept || "Khối"}: ${taskPayload.title}`, "Đã thêm trên bản xem trước & copy lệnh giao việc sang chat!");
            return { ok: true, board: kb, offline: true };
        }
    }

    async function moveKanbanTask(taskId, newStatus) {
        try {
            const res = await fetch(getApiBase() + "/api/office/kanban", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ op: "move", task_id: taskId, status: newStatus }),
            });
            const data = await res.json();
            if (data.ok) {
                state.kanbanData = data.board;
                showToast(`Đã chuyển nhiệm vụ sang ${newStatus}`, "success");
                await fetchLiveState(true);
                if (state.activeModal === "kanban") renderKanbanModal();
            } else {
                showToast(data.error || "Lỗi chuyển trạng thái", "error");
            }
            return data;
        } catch (err) {
            showToast("Đang ở chế độ xem trước Artifact — mở localhost:8000 để ghi đĩa Kanban.", "warn");
            return { ok: false, error: err.message };
        }
    }

    async function deleteKanbanTask(taskId) {
        try {
            const res = await fetch(getApiBase() + "/api/office/kanban", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ op: "delete", task_id: taskId }),
            });
            const data = await res.json();
            if (data.ok) {
                state.kanbanData = data.board;
                showToast("Đã xóa thẻ việc bổ sung.", "info");
                await fetchLiveState(true);
                if (state.activeModal === "kanban") renderKanbanModal();
            } else {
                showToast(data.error || "Không thể xóa thẻ này", "warn");
            }
            return data;
        } catch (err) {
            showToast("Đang ở chế độ xem trước Artifact — mở localhost:8000 để xóa thẻ đĩa.", "warn");
            return { ok: false, error: err.message };
        }
    }

    // ========================================================================
    // DOCK MODALS (5-TEAM KANBAN / INTEL / S1-S4 / LOUNGE)
    // ========================================================================
    function openDockModal(mode) {
        state.activeModal = mode;
        document.querySelectorAll(".office-dock-btn").forEach((b) => {
            b.classList.toggle("active", b.getAttribute("data-dock") === mode);
        });
        const backdrop = document.getElementById("office-modal-backdrop");
        if (backdrop) backdrop.classList.add("open");
        if (mode === "kanban") renderKanbanModal();
        else if (mode === "intel") renderIntelModal();
        else if (mode === "summary") renderSummaryModal();
        else if (mode === "lounge") renderLoungeModal();
    }

    function closeDockModal() {
        state.activeModal = null;
        if (state.poolGame && state.poolGame.stop) state.poolGame.stop();
        const backdrop = document.getElementById("office-modal-backdrop");
        if (backdrop) backdrop.classList.remove("open");
        document.querySelectorAll(".office-dock-btn").forEach((b) => {
            b.classList.toggle("active", b.getAttribute("data-dock") === "overview-map");
        });
    }

    function refreshActiveModalIfNeeded() {
        if (state.activeModal === "intel") renderIntelModal();
        else if (state.activeModal === "summary") renderSummaryModal();
    }

    async function renderKanbanModal() {
        document.getElementById("office-modal-icon").innerText = "📋";
        document.getElementById("office-modal-title").innerText = "Bảng Giao Việc Kanban 5 Khối Chuyên Trách";
        document.getElementById("office-modal-sub").innerText = "Chuẩn Mesa Protocol • Đồng bộ trực tiếp data/apex_kanban_board.json";
        const body = document.getElementById("office-modal-body");
        body.innerHTML = `<div style="padding:20px;text-align:center;color:#64748b;">⏳ Đang tải Kanban...</div>`;
        try {
            const ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
            const timer = ctrl ? setTimeout(() => ctrl.abort(), 3000) : null;
            const res = await fetch(getApiBase() + "/api/office/kanban", { cache: "no-store", signal: ctrl ? ctrl.signal : undefined });
            if (timer) clearTimeout(timer);
            const data = await res.json();
            if (data && data.tasks) state.kanbanData = data;
        } catch (e) {
            if (!state.kanbanData && window.APEX_OFFICE_BOOTSTRAP_BUNDLE && window.APEX_OFFICE_BOOTSTRAP_BUNDLE.kanban_board) {
                state.kanbanData = window.APEX_OFFICE_BOOTSTRAP_BUNDLE.kanban_board;
            }
        }
        const kb = state.kanbanData || { columns: {}, tasks: {} };
        const cols = [
            { id: "BACKLOG", title: "⏳ Chuẩn Bị Giao", next: "IN_PROGRESS", nextLbl: "Bắt đầu →" },
            { id: "IN_PROGRESS", title: "⚡ Đang Làm", next: "AUDIT_REVIEW", nextLbl: "Trình duyệt →" },
            { id: "AUDIT_REVIEW", title: "🛡️ Chờ Duyệt", next: "DONE", nextLbl: "Duyệt xong ✓" },
            { id: "DONE", title: "✅ Hoàn Thành", next: null, nextLbl: "" },
        ];
        body.innerHTML = `
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;background:#f8fafc;padding:10px;border-radius:12px;border:1px solid #e2e8f0;">
                <input id="kb-new-title" class="office-input" style="flex:1;min-width:220px;" placeholder="Nội dung công việc giao cho 5 Khối...">
                <select id="kb-new-dept" class="office-select">
                    <option value="Khối 1 (Hiền)">① Khối 1 — Hiền (BCTC &amp; Dữ Liệu)</option>
                    <option value="Khối 2 (Quân & Alex)">② Khối 2 — Minh Quân &amp; Alex (Thị Trường)</option>
                    <option value="Khối 3 (James & Palmer)">③ Khối 3 — James &amp; Palmer (Kế Hoạch Đầu Tư)</option>
                    <option value="Khối 4 (Victor)">④ Khối 4 — Victor (Giám Sát 145 Mã Live)</option>
                    <option value="Khối 5 (Trọng & Palmer)">⑤ Khối 5 — Trọng &amp; Palmer (Giám Sát Toàn HT)</option>
                </select>
                <select id="kb-new-prio" class="office-select">
                    <option value="CRITICAL">CRITICAL</option>
                    <option value="HIGH" selected>HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                </select>
                <button id="kb-create-btn" class="office-ctrl-btn primary">+ Giao Việc</button>
            </div>
            <div class="office-kanban-grid">
                ${cols.map((c) => {
                    const ids = (kb.columns && kb.columns[c.id]) || [];
                    return `
                        <div class="office-kanban-col">
                            <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;font-weight:800;margin-bottom:8px;">
                                <span>${c.title}</span>
                                <span class="office-filter-count">${ids.length}</span>
                            </div>
                            <div class="office-kanban-list">
                                ${ids.map((tid) => {
                                    const t = (kb.tasks && kb.tasks[tid]) || {};
                                    const isCustom = String(tid).startsWith("OFFICE-");
                                    return `
                                        <div class="office-kanban-card prio-${esc(t.priority || "MEDIUM")}">
                                            <div style="display:flex;justify-content:space-between;font-size:10.5px;color:#64748b;margin-bottom:4px;">
                                                <strong>${esc(t.dept || "--")}</strong>
                                                <span>${esc(t.scheduled_time || "")}</span>
                                            </div>
                                            <div style="font-size:12px;font-weight:700;color:#0f172a;margin-bottom:6px;">${esc(t.title || tid)}</div>
                                            <div style="display:flex;justify-content:space-between;align-items:center;gap:4px;">
                                                <span style="font-size:10.5px;color:#475569;">👤 ${esc(t.assignee || "")}</span>
                                                <div style="display:flex;gap:4px;">
                                                    ${c.next ? `<button class="office-btn-sm" onclick="window.ApexVirtualOffice.moveKanbanTask('${esc(tid)}','${c.next}')">${c.nextLbl}</button>` : ""}
                                                    ${isCustom ? `<button class="office-btn-sm" style="color:#dc2626;" onclick="window.ApexVirtualOffice.deleteKanbanTask('${esc(tid)}')">✕</button>` : ""}
                                                </div>
                                            </div>
                                        </div>
                                    `;
                                }).join("")}
                            </div>
                        </div>
                    `;
                }).join("")}
            </div>
        `;
        document.getElementById("kb-create-btn").onclick = async () => {
            const titleEl = document.getElementById("kb-new-title");
            const deptEl = document.getElementById("kb-new-dept");
            const prioEl = document.getElementById("kb-new-prio");
            if (!titleEl || !titleEl.value.trim()) return;
            await createKanbanTask({
                title: titleEl.value.trim(),
                dept: deptEl.value,
                priority: prioEl.value,
            });
            renderKanbanModal();
        };
    }

    function renderIntelModal() {
        const intel = (state.liveData && state.liveData.intel_feed) || {};
        const items = intel.feed_items || [];
        const sc = intel.summary_counts || {};
        document.getElementById("office-modal-icon").innerText = "📰";
        document.getElementById("office-modal-title").innerText = "Băng Tin IR, CBTT & BCTC Sống (Khối 1 — Trưởng phòng Hiền)";
        document.getElementById("office-modal-sub").innerText = `Cào lúc ${intel.crawled_at || "--"} • ${sc.total_news_articles || 0} bài RSS/CBTT • ${sc.verified_ir_portals || 0} cổng IR • ${sc.sec_edgar_filings || 0} SEC EDGAR`;
        const body = document.getElementById("office-modal-body");
        body.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
                <input id="intel-filter-input" class="office-input" style="min-width:240px;flex:1;" placeholder="Lọc theo mã (TPB, HDB, HPG, CTG, NVDA...) hoặc từ khóa...">
                <button class="office-ctrl-btn primary" onclick="window.ApexVirtualOffice.triggerRoomAction('team_hien','crawl_intel',{})">📡 + Cập Nhật Băng Tin Ngay</button>
            </div>
            <div id="intel-feed-list"></div>
        `;
        const renderList = (kw) => {
            const q = (kw || "").trim().toLowerCase();
            const filtered = items.filter((it) => !q || (it.symbol + " " + it.title + " " + it.source_name).toLowerCase().includes(q));
            document.getElementById("intel-feed-list").innerHTML = filtered.slice(0, 30).map((n) => `
                <div class="office-news-item">
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:4px;">
                        <div>
                            <span style="background:#fdf2f8;color:#db2777;border:1px solid #fbcfe8;padding:2px 8px;border-radius:9999px;font-size:11px;font-weight:800;">${esc(n.symbol)}</span>
                            <span style="font-size:11px;color:#64748b;margin-left:6px;">${esc(n.source_name)} • ${esc(n.published_at)}</span>
                        </div>
                        <span style="font-size:11px;font-weight:700;color:${Number(n.sentiment_score) >= 0 ? "#059669" : "#dc2626"};">Sent: ${esc(n.sentiment_score)}</span>
                    </div>
                    <div style="font-size:13.5px;font-weight:800;color:#0f172a;margin-bottom:4px;">${esc(n.title)}</div>
                    <div style="font-size:12px;color:#475569;margin-bottom:8px;">${esc(n.summary)}</div>
                    <div style="display:flex;gap:8px;flex-wrap:wrap;">
                        ${n.source_url ? `<a href="${esc(n.source_url)}" target="_blank" rel="noopener noreferrer" class="office-btn-sm" style="text-decoration:none;">🔗 Mở Bài Gốc</a>` : ""}
                        <button class="office-btn-sm" onclick="window.ApexVirtualOffice.triggerRoomAction('team_quan_alex','convene_dept',{ticker:'${esc(n.symbol)}',directive:'Phân tích BCTC & điểm vào mã ${esc(n.symbol)} từ băng tin Khối 1 Hiền'})">➔ Đẩy Quân &amp; Alex</button>
                        <button class="office-btn-sm" onclick="window.ApexVirtualOffice.triggerRoomAction('team_james_palmer','convene_dept',{ticker:'${esc(n.symbol)}',directive:'Trình James & Palmer xem xét catalyst mã ${esc(n.symbol)}'})">🎖️ Báo Cáo James</button>
                    </div>
                </div>
            `).join("") || `<div style="padding:20px;text-align:center;color:#64748b;">Không có tin khớp từ khóa.</div>`;
        };
        renderList("");
        document.getElementById("intel-filter-input").addEventListener("input", (e) => renderList(e.target.value));
    }

    function renderSummaryModal() {
        const d = state.liveData || {};
        const ssot = d.ssot || {};
        const wp = d.weekly_plan_summary || {};
        const es = d.enterprise_session || {};
        const sup = d.supervisor || {};
        document.getElementById("office-modal-icon").innerText = "📊";
        document.getElementById("office-modal-title").innerText = "Tổng Hợp Doanh Nghiệp & Ma Trận 4 Kịch Bản Tuần 48 (S1–S4)";
        document.getElementById("office-modal-sub").innerText = `Tài khoản TCBS ${ssot.account_id || "105C307855"} • ${wp.week_label || ""}`;

        const scenarios = [
            { code: "S1 — UPTREND XÁC NHẬN", cond: "VNI > MA20/MA50 & Breadth >= 50%", alloc: "75% – 85% NAV", picks: "TPB (500 CP), HDB (200 CP), HPG (300 CP)", color: "#059669", bg: "#ecfdf5" },
            { code: "S2 — TÍCH LŨY CHỌN LỌC", cond: "Breadth MA20 đạt 30% – 50%, Buy-Up >= 55%", alloc: "~34% NAV", picks: "HDB (200 CP) + TPB (200 CP) khung 14h00–14h25", color: "#0284c7", bg: "#f0f9ff" },
            { code: "S3 — SPRING RÚT CHÂN", cond: "Rút chân xác nhận 14h05–14h25 sau rũ bỏ", alloc: "~36% NAV", picks: "TPB (200–300 CP), CTG (100 CP), HPG (100 CP)", color: "#d97706", bg: "#fffbeb" },
            { code: "S4 — BEAR DOWNTREND", cond: "VNI yếu, Breadth MA20 < 28% hoặc Phố Wall sốc", alloc: "0% GIẢI NGÂN (100% CASH)", picks: "Giữ trọn két 20,051,117 ₫ • Không ép lệnh KPI", color: "#dc2626", bg: "#fef2f2" },
        ];

        const body = document.getElementById("office-modal-body");
        body.innerHTML = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin-bottom:14px;">
                <div class="office-section-box"><div class="office-section-title">💰 Tiền Mặt Ròng SSOT</div><strong style="font-size:18px;color:#059669;">${esc(ssot.cash_str)}</strong><div style="font-size:11px;color:#64748b;">${esc(ssot.cash_pct)}% Tiền mặt • ${esc(ssot.holdings_count)} vị thế mở</div></div>
                <div class="office-section-box"><div class="office-section-title">🏛️ Hội Đồng 5 Khối Chuyên Trách</div><strong style="font-size:15px;color:#4f46e5;">${esc(es.final_verdict || "--")}</strong><div style="font-size:11px;color:#64748b;">Điểm danh: ${esc(es.quorum_count || 0)}/${esc(es.roster_total || 14)} Ban • Audit ${esc(es.ombudsman_audit_score || "10/10")}</div></div>
                <div class="office-section-box"><div class="office-section-title">📡 Thị Trường Live</div><strong style="font-size:15px;">VNI ${esc((d.market_live || {}).vn_index || "--")}</strong><div style="font-size:11px;color:#64748b;">Chế độ: ${esc((d.market_live || {}).live_regime || "--")} • Daemons: ${esc(sup.services_count || 5)}</div></div>
            </div>
            <div class="office-section-box" style="margin-bottom:14px;">
                <div class="office-section-title"><span>📜 Chỉ Thị Hiến Chương Tuần 48</span></div>
                <div style="font-size:12.5px;color:#0f172a;line-height:1.5;">${esc(wp.constitution_mandate || "")}</div>
            </div>
            <div class="office-section-box" style="margin-bottom:14px;">
                <div class="office-section-title"><span>🧭 Ma Trận Tự Chủ 4 Kịch Bản Thị Trường (S1–S4)</span></div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;">
                    ${scenarios.map((sc) => `
                        <div style="background:${sc.bg};border:1px solid ${sc.color}44;border-radius:10px;padding:10px;">
                            <div style="font-size:12px;font-weight:800;color:${sc.color};">${esc(sc.code)}</div>
                            <div style="font-size:11px;color:#334155;margin-top:3px;"><strong>Điều kiện:</strong> ${esc(sc.cond)}</div>
                            <div style="font-size:11px;color:#0f172a;margin-top:3px;"><strong>Giải ngân:</strong> ${esc(sc.alloc)}</div>
                            <div style="font-size:11px;color:#475569;margin-top:2px;"><strong>Danh mục:</strong> ${esc(sc.picks)}</div>
                        </div>
                    `).join("")}
                </div>
            </div>
            <div class="office-section-box" style="margin-bottom:14px;">
                <div class="office-section-title"><span>🎯 Rổ BCTC Q3/2026 Sạch (Khung Giờ Vàng 14h00–14h25)</span></div>
                <table class="office-table">
                    <thead><tr><th>Mã</th><th>Trạng thái</th><th>Vùng Mua Limit LO</th><th>Stop 2xATR</th><th>Mục tiêu TP1 / TP2</th></tr></thead>
                    <tbody>
                        ${(wp.approved_watchlist || []).map((w) => `
                            <tr>
                                <td><strong>${esc(w.symbol)}</strong><div style="font-size:10.5px;color:#64748b;">${esc(w.name)}</div></td>
                                <td>${esc(w.weekly_limit)}</td>
                                <td>${esc(w.entry_zone)}</td>
                                <td style="color:#dc2626;font-weight:700;">${esc(w.stop_loss_2xatr)}</td>
                                <td style="color:#059669;font-weight:700;">${esc(w.tp1)} / ${esc(w.tp2)}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
            <div class="office-section-box">
                <div class="office-section-title"><span>🗓️ Lộ Trình Điều Hành Tuần</span></div>
                ${(wp.days || []).map((day) => `
                    <div class="office-news-item">
                        <div style="display:flex;justify-content:space-between;gap:8px;">
                            <strong style="font-size:12px;">${esc(day.day_name)}</strong>
                            <span style="font-size:11px;font-weight:700;color:#4f46e5;">${esc(day.status_badge)}</span>
                        </div>
                        <div style="font-size:11.5px;color:#475569;margin-top:4px;">${esc(day.guideline)}</div>
                    </div>
                `).join("")}
            </div>
        `;
    }

    function initPoolGame(canvas) {
        const W = 720;
        const H = 380;
        const PAD = 28;
        const R = 11;
        const POCKET_R = 19;
        const pockets = [
            { x: PAD, y: PAD },
            { x: W * 0.5, y: PAD - 3 },
            { x: W - PAD, y: PAD },
            { x: PAD, y: H - PAD },
            { x: W * 0.5, y: H - PAD + 3 },
            { x: W - PAD, y: H - PAD },
        ];

        const game = {
            balls: [],
            shots: 0,
            pocketed: 0,
            aiming: false,
            aimX: 0,
            aimY: 0,
            raf: null,
            running: true,
            rack() {
                const startX = 480;
                const startY = H * 0.5;
                const cols = ["#eab308", "#2563eb", "#ef4444", "#7c3aed", "#f97316", "#0f172a"];
                const list = [{ id: 0, x: 185, y: H * 0.5, vx: 0, vy: 0, color: "#ffffff", cue: true, active: true }];
                let idx = 0;
                for (let row = 0; row < 3; row++) {
                    for (let col = 0; col <= row; col++) {
                        list.push({
                            id: idx + 1,
                            x: startX + row * (R * 1.85),
                            y: startY + (col - row * 0.5) * (R * 2.12),
                            vx: 0,
                            vy: 0,
                            color: cols[idx % cols.length],
                            cue: false,
                            active: true,
                        });
                        idx++;
                    }
                }
                this.balls = list;
                this.shots = 0;
                this.pocketed = 0;
                this.updateStats();
            },
            updateStats() {
                const scEl = document.getElementById("pool-score-txt");
                if (scEl) scEl.innerText = `Bi vào lỗ: ${this.pocketed}/6 • Số gậy: ${this.shots}`;
            },
            stop() {
                this.running = false;
                if (this.raf) cancelAnimationFrame(this.raf);
                if (this._onMove) window.removeEventListener("mousemove", this._onMove);
                if (this._onUp) window.removeEventListener("mouseup", this._onUp);
            },
        };
        game.rack();

        function isAnyMoving() {
            return game.balls.some((b) => b.active && (Math.abs(b.vx) > 0.05 || Math.abs(b.vy) > 0.05));
        }

        function getMousePos(e) {
            const rect = canvas.getBoundingClientRect();
            const sx = W / rect.width;
            const sy = H / rect.height;
            const cx = e.touches && e.touches[0] ? e.touches[0].clientX : e.clientX;
            const cy = e.touches && e.touches[0] ? e.touches[0].clientY : e.clientY;
            return { x: (cx - rect.left) * sx, y: (cy - rect.top) * sy };
        }

        const onStart = (e) => {
            if (isAnyMoving()) return;
            const pt = getMousePos(e);
            game.aiming = true;
            game.aimX = pt.x;
            game.aimY = pt.y;
        };
        const onMove = (e) => {
            if (!game.aiming || !game.running) return;
            const pt = getMousePos(e);
            game.aimX = pt.x;
            game.aimY = pt.y;
        };
        const onUp = () => {
            if (!game.aiming || !game.running) return;
            game.aiming = false;
            const cue = game.balls[0];
            if (!cue || !cue.active) return;
            const dx = cue.x - game.aimX;
            const dy = cue.y - game.aimY;
            const dist = Math.hypot(dx, dy);
            if (dist < 6) return;
            const power = Math.min(18, dist * 0.14);
            cue.vx = (dx / dist) * power;
            cue.vy = (dy / dist) * power;
            game.shots += 1;
            game.updateStats();
        };

        game._onMove = onMove;
        game._onUp = onUp;
        canvas.addEventListener("mousedown", onStart);
        canvas.addEventListener("touchstart", onStart, { passive: true });
        canvas.addEventListener("touchmove", onMove, { passive: true });
        canvas.addEventListener("touchend", onUp);
        window.addEventListener("mousemove", onMove);
        window.addEventListener("mouseup", onUp);

        const ctx = canvas.getContext("2d");
        function step() {
            if (!game.running) return;
            // Physics substeps
            for (let sub = 0; sub < 2; sub++) {
                for (const b of game.balls) {
                    if (!b.active) continue;
                    b.x += b.vx * 0.5;
                    b.y += b.vy * 0.5;
                    b.vx *= 0.992;
                    b.vy *= 0.992;
                    if (Math.hypot(b.vx, b.vy) < 0.04) {
                        b.vx = 0;
                        b.vy = 0;
                    }
                    // Cushions
                    if (b.x - R < PAD) { b.x = PAD + R; b.vx = Math.abs(b.vx) * 0.85; }
                    if (b.x + R > W - PAD) { b.x = W - PAD - R; b.vx = -Math.abs(b.vx) * 0.85; }
                    if (b.y - R < PAD) { b.y = PAD + R; b.vy = Math.abs(b.vy) * 0.85; }
                    if (b.y + R > H - PAD) { b.y = H - PAD - R; b.vy = -Math.abs(b.vy) * 0.85; }

                    // Pockets
                    for (const pk of pockets) {
                        if (Math.hypot(b.x - pk.x, b.y - pk.y) < POCKET_R) {
                            if (b.cue) {
                                b.x = 185; b.y = H * 0.5; b.vx = 0; b.vy = 0;
                            } else {
                                b.active = false;
                                b.vx = 0; b.vy = 0;
                                game.pocketed += 1;
                                game.updateStats();
                            }
                            break;
                        }
                    }
                }
                // Ball-ball elastic collisions
                for (let i = 0; i < game.balls.length; i++) {
                    const a = game.balls[i];
                    if (!a.active) continue;
                    for (let j = i + 1; j < game.balls.length; j++) {
                        const b = game.balls[j];
                        if (!b.active) continue;
                        const dx = b.x - a.x;
                        const dy = b.y - a.y;
                        const dist = Math.hypot(dx, dy);
                        if (dist > 0 && dist < R * 2) {
                            const nx = dx / dist;
                            const ny = dy / dist;
                            const overlap = R * 2 - dist;
                            a.x -= nx * overlap * 0.5;
                            a.y -= ny * overlap * 0.5;
                            b.x += nx * overlap * 0.5;
                            b.y += ny * overlap * 0.5;
                            const dvx = a.vx - b.vx;
                            const dvy = a.vy - b.vy;
                            const dot = dvx * nx + dvy * ny;
                            if (dot > 0) {
                                a.vx -= dot * nx;
                                a.vy -= dot * ny;
                                b.vx += dot * nx;
                                b.vy += dot * ny;
                            }
                        }
                    }
                }
            }

            // Draw table
            ctx.fillStyle = "#78350f";
            ctx.fillRect(0, 0, W, H);
            ctx.fillStyle = "#15803d";
            ctx.fillRect(PAD, PAD, W - PAD * 2, H - PAD * 2);
            ctx.strokeStyle = "#166534";
            ctx.lineWidth = 4;
            ctx.strokeRect(PAD, PAD, W - PAD * 2, H - PAD * 2);

            // Pockets
            for (const pk of pockets) {
                ctx.fillStyle = "#0f172a";
                ctx.beginPath();
                ctx.arc(pk.x, pk.y, POCKET_R - 2, 0, Math.PI * 2);
                ctx.fill();
            }

            // Aim line & power cue
            const cue = game.balls[0];
            if (game.aiming && cue && cue.active) {
                const dx = cue.x - game.aimX;
                const dy = cue.y - game.aimY;
                const dist = Math.hypot(dx, dy);
                if (dist > 4) {
                    const nx = dx / dist;
                    const ny = dy / dist;
                    ctx.save();
                    ctx.strokeStyle = "rgba(255,255,255,0.75)";
                    ctx.setLineDash([6, 6]);
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(cue.x, cue.y);
                    ctx.lineTo(cue.x + nx * 210, cue.y + ny * 210);
                    ctx.stroke();
                    ctx.setLineDash([]);
                    // Stick behind cue
                    ctx.strokeStyle = "#fde68a";
                    ctx.lineWidth = 5;
                    ctx.beginPath();
                    ctx.moveTo(cue.x - nx * 16, cue.y - ny * 16);
                    ctx.lineTo(cue.x - nx * (24 + Math.min(120, dist)), cue.y - ny * (24 + Math.min(120, dist)));
                    ctx.stroke();
                    ctx.restore();
                }
            }

            // Draw balls
            for (const b of game.balls) {
                if (!b.active) continue;
                ctx.fillStyle = "rgba(0,0,0,0.25)";
                ctx.beginPath();
                ctx.arc(b.x + 2, b.y + 3, R, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = b.color;
                ctx.beginPath();
                ctx.arc(b.x, b.y, R, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "rgba(255,255,255,0.45)";
                ctx.beginPath();
                ctx.arc(b.x - 3, b.y - 3, 3, 0, Math.PI * 2);
                ctx.fill();
            }

            game.raf = requestAnimationFrame(step);
        }
        game.raf = requestAnimationFrame(step);
        return game;
    }

    function renderCapitalSimulator(container) {
        const d = state.liveData || {};
        const ssot = d.ssot || {};
        const cashTotal = Number(ssot.cash_vnd || 20051117);
        const candidates = [
            { sym: "TPB", name: "TPBank", price: 12250, stop: 11600, tp1: 13350, note: "F=9/9 • Q3/2026 #1" },
            { sym: "HDB", name: "HDBank", price: 21700, stop: 20500, tp1: 23650, note: "ROE 23.7% • RS 90" },
            { sym: "CTG", name: "VietinBank", price: 29950, stop: 28300, tp1: 32650, note: "F=8/9 • Big4 ROE 22.6%" },
            { sym: "HPG", name: "Hòa Phát", price: 20450, stop: 19300, tp1: 22300, note: "F=8/9 • Thanh khoản 402 tỷ" },
            { sym: "VPB", name: "VPBank", price: 20500, stop: 19350, tp1: 23450, note: "Dự phòng S1 Uptrend" },
            { sym: "NAB", name: "Nam A Bank", price: 12920, stop: 12460, tp1: 13760, note: "Watchlist RS 95" },
            { sym: "PVP", name: "PVTrans Pacific", price: 16580, stop: 15630, tp1: 18320, note: "AAA • OCF/LNST 1.4x" },
            { sym: "PVT", name: "PVTrans", price: 18460, stop: 17390, tp1: 20410, note: "AAA • OCF/LNST 2.38x" },
        ];
        const qtyMap = { TPB: 200, HDB: 100, CTG: 0, HPG: 0, VPB: 0, NAB: 0, PVP: 0, PVT: 0 };

        container.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
                <div style="font-size:12.5px;color:#334155;">Két SSOT khả dụng: <strong style="color:#059669;">${fmtVnd(cashTotal)}</strong> • Giới hạn Điều 5: <strong>≤ 33% NAV/mã</strong> • Stop/lệnh: <strong>≤ 1.5% NAV (${fmtVnd(cashTotal * 0.015)})</strong></div>
                <button class="office-ctrl-btn primary" id="sim-save-kanban">📋 Giao Lệnh Dự Kiến Vào Kanban</button>
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;margin-bottom:12px;" id="sim-summary-cards"></div>
            <table class="office-table">
                <thead><tr><th>Mã Cổ Phiếu</th><th>Giá Limit LO</th><th>Stop 2xATR / TP1</th><th>Số Lô (100 CP)</th><th>Giá Trị &amp; % NAV</th><th>Lỗ Max Nếu Cắt</th></tr></thead>
                <tbody id="sim-tbody"></tbody>
            </table>
        `;

        function recalc() {
            let totalAlloc = 0;
            let totalRisk = 0;
            let totalReward = 0;
            let warnings = [];
            const chosen = [];
            const rowsHtml = candidates.map((c) => {
                const qty = qtyMap[c.sym] || 0;
                const val = qty * c.price;
                const pctNav = cashTotal > 0 ? (val / cashTotal) * 100 : 0;
                const risk = qty * Math.max(0, c.price - c.stop);
                const reward = qty * Math.max(0, c.tp1 - c.price);
                totalAlloc += val;
                totalRisk += risk;
                totalReward += reward;
                if (pctNav > 33.0) warnings.push(`${c.sym} vượt trần 33% NAV (${pctNav.toFixed(1)}%)`);
                if (risk > cashTotal * 0.015) warnings.push(`${c.sym} lỗ Stop ${fmtVnd(risk)} > 1.5% NAV`);
                if (qty > 0) chosen.push(`${qty} ${c.sym} @ ${c.price.toLocaleString("en-US")}`);
                return `
                    <tr>
                        <td><strong>${c.sym}</strong> — ${c.name}<div style="font-size:10.5px;color:#64748b;">${c.note}</div></td>
                        <td style="font-family:'JetBrains Mono',monospace;">${c.price.toLocaleString("en-US")} ₫</td>
                        <td style="font-size:11px;"><span style="color:#dc2626;">${c.stop.toLocaleString("en-US")}</span> / <span style="color:#059669;">${c.tp1.toLocaleString("en-US")}</span></td>
                        <td>
                            <div style="display:inline-flex;align-items:center;gap:6px;">
                                <button class="office-btn-sm sim-dec" data-sym="${c.sym}">－</button>
                                <strong style="min-width:44px;text-align:center;font-family:'JetBrains Mono',monospace;">${qty}</strong>
                                <button class="office-btn-sm sim-inc" data-sym="${c.sym}">＋</button>
                            </div>
                        </td>
                        <td style="font-weight:700;color:${pctNav > 33 ? "#dc2626" : "#0f172a"};">${fmtVnd(val)} (${pctNav.toFixed(1)}%)</td>
                        <td style="color:${risk > cashTotal * 0.015 ? "#dc2626" : "#475569"};font-weight:700;">-${fmtVnd(risk)}</td>
                    </tr>
                `;
            }).join("");

            const remCash = cashTotal - totalAlloc;
            const allocPct = cashTotal > 0 ? (totalAlloc / cashTotal) * 100 : 0;
            const rr = totalRisk > 0 ? (totalReward / totalRisk) : 0;

            document.getElementById("sim-tbody").innerHTML = rowsHtml;
            document.getElementById("sim-summary-cards").innerHTML = `
                <div class="office-section-box"><div class="office-section-title">Tổng Giải Ngân Dự Kiến</div><strong style="font-size:16px;color:${remCash < 0 ? "#dc2626" : "#4f46e5"};">${fmtVnd(totalAlloc)} (${allocPct.toFixed(1)}%)</strong><div style="font-size:11px;color:#64748b;">Tiền mặt còn: ${fmtVnd(remCash)}</div></div>
                <div class="office-section-box"><div class="office-section-title">Rủi Ro / Lợi Nhuận (R:R)</div><strong style="font-size:16px;color:#059669;">${rr.toFixed(2)}x</strong><div style="font-size:11px;color:#64748b;">Lỗ tối đa: -${fmtVnd(totalRisk)} • Lãi TP1: +${fmtVnd(totalReward)}</div></div>
                <div class="office-section-box"><div class="office-section-title">Kiểm Định Hiến Chương</div><strong style="font-size:13px;color:${warnings.length || remCash < 0 ? "#dc2626" : "#059669"};">${remCash < 0 ? "❌ Vượt quá tiền mặt trong két!" : (warnings.length ? "⚠️ " + warnings.join("; ") : "✅ Đạt chuẩn Điều 5 & ATR Risk")}</strong></div>
            `;

            container.querySelectorAll(".sim-dec").forEach((b) => {
                b.onclick = () => { const s = b.getAttribute("data-sym"); qtyMap[s] = Math.max(0, (qtyMap[s] || 0) - 100); recalc(); };
            });
            container.querySelectorAll(".sim-inc").forEach((b) => {
                b.onclick = () => { const s = b.getAttribute("data-sym"); qtyMap[s] = (qtyMap[s] || 0) + 100; recalc(); };
            });
            document.getElementById("sim-save-kanban").onclick = async () => {
                if (!chosen.length) { showToast("Chủ tịch vui lòng chọn ít nhất 1 lô 100 CP.", "warn"); return; }
                await createKanbanTask({
                    title: `[Mô phỏng S1–S3] Kịch bản: ${chosen.join(" + ")} (${allocPct.toFixed(1)}% NAV)`,
                    dept: "Khối 2 (Quân & Alex)",
                    assignee: "Minh Quân & Alex",
                    priority: "HIGH",
                    scheduled_time: "14:00",
                });
            };
        }
        recalc();
    }

    function renderLoungeModal() {
        document.getElementById("office-modal-icon").innerText = "🎱";
        document.getElementById("office-modal-title").innerText = "Khu Tiện Ích Chủ Tịch — Bàn Bi-a Giải Trí & Mô Phỏng Vốn";
        document.getElementById("office-modal-sub").innerText = "Chơi Bi-a thư giãn trong lúc chờ phiên hoặc giả lập chia vốn 20.05M ₫ chuẩn Điều 5";
        const body = document.getElementById("office-modal-body");
        if (state.poolGame && state.poolGame.stop) state.poolGame.stop();

        body.innerHTML = `
            <div class="office-lounge-tabs">
                <button class="office-lounge-tab ${state.loungeTab === "pool" ? "active" : ""}" id="ltab-pool">🎱 Bàn Bi-a Giải Trí</button>
                <button class="office-lounge-tab ${state.loungeTab === "sim" ? "active" : ""}" id="ltab-sim">🧮 Mô Phỏng Chia Vốn 20.05M ₫</button>
            </div>
            <div id="lounge-tab-content"></div>
        `;
        document.getElementById("ltab-pool").onclick = () => { state.loungeTab = "pool"; renderLoungeModal(); };
        document.getElementById("ltab-sim").onclick = () => { state.loungeTab = "sim"; renderLoungeModal(); };

        const content = document.getElementById("lounge-tab-content");
        if (state.loungeTab === "pool") {
            content.innerHTML = `
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
                    <span style="font-size:12px;color:#475569;">Kéo chuột ngược từ bi trắng để ngắm đường tia và thả tay để bắn!</span>
                    <div style="display:flex;align-items:center;gap:10px;">
                        <strong id="pool-score-txt" style="font-size:12.5px;color:#059669;">Bi vào lỗ: 0/6 • Số gậy: 0</strong>
                        <button class="office-ctrl-btn" id="pool-rack-btn">🔄 Xếp lại bi</button>
                    </div>
                </div>
                <canvas id="office-pool-canvas" class="office-pool-canvas" width="720" height="380"></canvas>
            `;
            const pCanvas = document.getElementById("office-pool-canvas");
            state.poolGame = initPoolGame(pCanvas);
            document.getElementById("pool-rack-btn").onclick = () => state.poolGame && state.poolGame.rack();
        } else {
            renderCapitalSimulator(content);
        }
    }

    // ========================================================================
    // LIFECYCLE PUBLIC API
    // ========================================================================
    async function init() {
        const root = document.getElementById("apex-virtual-office-root");
        if (!root) return;
        if (state.initialized && state.rootEl === root) return;
        state.rootEl = root;
        buildShellDOM(root);
        state.canvasEl = document.getElementById("office-iso-canvas");
        state.ctx = state.canvasEl ? state.canvasEl.getContext("2d") : null;
        state.initialized = true;
        bindEvents();

        await fetchLiveState(false);
        startAnimLoop();
        scheduleNextPoll();

        document.addEventListener("visibilitychange", () => {
            if (!document.hidden && state.visible) {
                fetchLiveState(false);
                startAnimLoop();
                scheduleNextPoll();
            } else {
                stopAnimLoop();
                clearTimeout(state.pollTimer);
            }
        });
    }

    function onShow() {
        state.visible = true;
        if (!state.initialized) {
            init();
            return;
        }
        setTimeout(() => {
            state._resizeFn && state._resizeFn();
            startAnimLoop();
            fetchLiveState(false);
            scheduleNextPoll();
        }, 60);
    }

    function onHide() {
        state.visible = false;
        stopAnimLoop();
        clearTimeout(state.pollTimer);
    }

    window.ApexVirtualOffice = {
        init,
        onShow,
        onHide,
        openRoomDrawer,
        closeRoomDrawer,
        openDockModal,
        closeDockModal,
        triggerRoomAction,
        createKanbanTask,
        moveKanbanTask,
        deleteKanbanTask,
        _state: state,
    };
})();
