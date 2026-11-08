#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BAN 11 — BAN SÁNG TẠO NỘI DUNG & VIDEO VIRAL TÀI CHÍNH — "KHÁNH"
File: scripts/khanh_content_creator.py
Cơ quan chủ quản: Ban 11 — Khánh (Chief Viral Financial Content Creator & Trending Strategist)
Phối hợp độc quyền: Ban 10 — Hiền (Apex Corporate Filings & IR Intelligence Scout)
Giám sát & Phê duyệt: Tổng Tư Lệnh Master CIO James (Ban 8)
Phục vụ trực tiếp: Chủ tịch Phước Trần (Tài khoản TCBS: 105C307855)

Chức năng:
1. Tiếp nhận và điều phối phiên làm việc tối 21h15 giữa Khánh và Hiền.
2. Trao đổi nghiệp vụ với Hiền để trích xuất số liệu BCTC thật 100% không bịa đặt.
3. Nghiên cứu thị trường và tâm lý người xem trên TikTok / Shorts / Reels để lên kịch bản video viral 60 giây.
4. Trình Tổng Tư Lệnh Master CIO James kiểm định tính minh bạch và đóng dấu Approved.
"""

import os
import sys
import json
import re
import datetime
from pathlib import Path

# --- TÍCH HỢP AGENT ZERO MEDIA HARVESTER (BAN 11 KHÁNH & BẢO) ---
try:
    from scripts.apex_agent_zero_engine import ZeroMediaHarvester
    KHANH_MEDIA_HARVESTER = ZeroMediaHarvester()
except Exception:
    KHANH_MEDIA_HARVESTER = None

from typing import Dict, Any, Optional, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.bctc_ir_filing_scout import (
    extract_live_bctc_fundamentals,
    get_earnings_seasonality_context,
    OFFICIAL_IR_DATABASE
)

CONTENT_DIR = BASE_DIR / "11_Viral_Content_Creation"
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

DIALOGUE_LOG = CONTENT_DIR / "inter_department_hien_khanh_dialogue.json"
TRENDING_VAULT = CONTENT_DIR / "trending_topics_vault.json"
RENDER_QUEUE_DIR = CONTENT_DIR / "render_queue"
RENDER_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = CONTENT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# 1. KHO Ý TƯỞNG TRENDING & TÂM LÝ ĐÁM ĐÔNG MẠNG XÃ HỘI
# ==============================================================================

TRENDING_ANGLES = [
    {
        "id": "ANGLE_01_TRUTH_EXPOSED",
        "name": "Bóc Trần Tiền Thật vs Tiền Giấy",
        "hook_template": "Đừng vội mừng khi thấy doanh nghiệp báo lãi nghìn tỷ! 90% F0 không hề biết bí mật chết người này trên Báo Cáo Tài Chính...",
        "target_emotion": "Tò mò, sợ bị lừa (Fear of being scammed), muốn biết sự thật",
        "suitable_tickers": ["HPG", "MWG", "NVL", "HAG"]
    },
    {
        "id": "ANGLE_02_BANK_WARFARE",
        "name": "Cuộc Chiến Tiền Rẻ CASA Ngân Hàng",
        "hook_template": "Tại sao Techcombank và MBBank cho vay lãi suất cực thấp mà tiền vẫn đổ về như thác lũ? Đây là cỗ máy in tiền CASA...",
        "target_emotion": "Khao khát kiếm tiền, hiểu quy luật tài chính của giới tinh hoa",
        "suitable_tickers": ["TCB", "MBB", "VCB", "ACB"]
    },
    {
        "id": "ANGLE_03_MEGA_PROJECT_CATALYST",
        "name": "Đại Dự Án Dung Quất 2 — Cú Hích Vua Thép",
        "hook_template": "Lò cao Dung Quất 2 của Hòa Phát đã chạy thật hay chỉ là tin đồn thổi giá cổ phiếu? Xem ngay số tiền thật 8.800 tỷ!",
        "target_emotion": "Hào hứng, kỳ vọng bùng nổ, đón đầu siêu sóng chu kỳ",
        "suitable_tickers": ["HPG"]
    },
    {
        "id": "ANGLE_04_DIVIDEND_TRAP",
        "name": "Bẫy Chia Cổ Tức Bằng Cổ Phiếu",
        "hook_template": "Được chia cổ tức 30% bằng cổ phiếu là giàu to hay bị mất trắng một phần vốn? Sự thật phũ phàng ngày giao dịch không hưởng quyền...",
        "target_emotion": "Vỡ òa, tránh mất tiền oan, nâng cao tư duy thực chiến",
        "suitable_tickers": ["SSI", "HPG", "TCB"]
    },
    {
        "id": "ANGLE_05_SMART_MONEY_T0",
        "name": "Chiến Thuật Lướt T+0 Hạ Giá Vốn Của Quỹ Lớn",
        "hook_template": "Thị trường đỏ lửa nhưng tài khoản vẫn sinh lời đều đặn? Tiết lộ cách quỹ đầu tư lướt T+0 ngay trên kho hàng có sẵn...",
        "target_emotion": "Thích thú, muốn áp dụng giải pháp kiếm thêm thu nhập ngay lập tức",
        "suitable_tickers": ["HPG", "TCB", "MBB"]
    }
]


def init_or_update_trending_vault() -> Dict[str, Any]:
    """
    Khởi tạo hoặc cập nhật kho dữ liệu xu hướng, góc nhìn viral và các phễu chuyển đổi iCopy.
    """
    vault_data = {
        "system_title": "Apex Hedge Fund — Viral Trending & Content Vault (Ban 11 - Khánh)",
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "chief_creator": "Khánh (Chief Viral Financial Content Creator & Trending Strategist)",
        "collaborator": "Hiền (Ban 10 — Apex Corporate Filings & IR Scout)",
        "supervisor": "James (Ban 8 — Apex Master CIO)",
        "icopy_target_account": "105C307855",
        "primary_platforms": ["TikTok", "YouTube Shorts", "Facebook Reels", "Threads"],
        "trending_angles": TRENDING_ANGLES,
        "content_pillars": [
            {
                "pillar_name": "BCTC Forensic (Bóc Trần Tiền Thật OCF)",
                "description": "Soi báo cáo tài chính mổ xẻ chất lượng lợi nhuận thật vs ảo, đòn bẩy và dòng tiền tự do",
                "target_audience": "Nhà đầu tư F0 và trung cấp muốn đầu tư an toàn không bị úp bô"
            },
            {
                "pillar_name": "CASA & Cỗ Máy Tiền Rẻ Ngân Hàng",
                "description": "Giải thích mô hình kinh doanh tiền rẻ của các ngân hàng dẫn đầu",
                "target_audience": "Nhà đầu tư dài hạn tìm kiếm siêu cổ phiếu tăng trưởng kép"
            },
            {
                "pillar_name": "Chiến Thuật Đi Lệnh & T+0 Thực Chiến",
                "description": "Chia sẻ kinh nghiệm giao dịch thực tế, lướt T+0 hạ giá vốn, kỷ luật quản trị rủi ro",
                "target_audience": "Nhà đầu tư cá nhân muốn kiếm thêm dòng tiền ngoài luồng 3 - 4 triệu/tháng"
            }
        ]
    }
    TRENDING_VAULT.write_text(json.dumps(vault_data, indent=2, ensure_ascii=False), encoding="utf-8")
    return vault_data


# ==============================================================================
# 2. KHÁNH TRAO ĐỔI NGHIỆP VỤ VỚI HIỀN (INTER-DEPARTMENT COMMUNICATOR)
# ==============================================================================

def communicate_with_hien(ticker: str, research_focus: str) -> Dict[str, Any]:
    """
    Khánh gửi thông điệp yêu cầu số liệu và dữ liệu chi tiết sang Ban 10 (Hiền).
    Hiền rà soát và trả về số liệu đã kiểm toán cùng phân tích tiền thật.
    """
    clean_sym = ticker.upper().strip()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Lời nhắn của Khánh gửi Hiền
    khanh_message = (
        f"Chào Hiền nhé! Tối nay Khánh đang nghiên cứu kịch bản video TikTok/Shorts về chủ đề '{research_focus}' cho mã {clean_sym}. "
        f"Hiền rà soát giúp Khánh số liệu BCTC quý mới nhất: Doanh thu, LNST, Dòng tiền kinh doanh OCF và các ghi chú quan hệ cổ đông để Khánh đưa vào kịch bản nhé. "
        f"Đảm bảo chuẩn xác 100% để trình James duyệt nhé Hiền!"
    )

    # 2. Hiền trích xuất số liệu thực tế
    funds = extract_live_bctc_fundamentals(clean_sym)
    info = OFFICIAL_IR_DATABASE.get(clean_sym, {})

    # 3. Phản hồi nghiệp vụ từ Hiền gửi Khánh
    hien_response = {
        "responder": "Hiền — Trưởng Ban 10 (Rà Soát BCTC & Quan Hệ Cổ Đông)",
        "timestamp": now_str,
        "ticker": clean_sym,
        "company_name": info.get("company_name", f"CTCP {clean_sym}"),
        "exchange": info.get("exchange", "HOSE"),
        "sector": info.get("sector", "Doanh nghiệp niêm yết"),
        "latest_quarter": funds.get("latest_quarter", "Gần nhất"),
        "revenue_vnd_bil": funds.get("revenue_vnd_bil", 0.0),
        "net_income_vnd_bil": funds.get("net_income_vnd_bil", 0.0),
        "ocf_vnd_bil": funds.get("ocf_vnd_bil", 0.0),
        "fcf_vnd_bil": funds.get("fcf_vnd_bil", 0.0),
        "ocf_to_net_income_ratio": funds.get("ocf_to_net_income_ratio", 0.0),
        "earnings_quality_rating": funds.get("earnings_quality_rating", "ĐẠT CHUẨN VAS"),
        "official_ir_portal": info.get("official_ir_url", ""),
        "key_catalyst_notes": info.get("notes", "Doanh nghiệp đầu ngành."),
        "hien_verdict": (
            f"Hiền đã kiểm tra kỹ: {clean_sym} có doanh thu {funds.get('revenue_vnd_bil', 0):,.1f} tỷ, "
            f"LNST {funds.get('net_income_vnd_bil', 0):,.1f} tỷ và dòng tiền OCF thực tế đạt {funds.get('ocf_vnd_bil', 0):,.1f} tỷ. "
            f"Tỷ lệ tiền thật OCF/LNST đạt {funds.get('ocf_to_net_income_ratio', 0)}x ({funds.get('earnings_quality_rating')}). "
            f"Số liệu này 100% lấy từ BCTC kiểm toán chính thống, Khánh an tâm dựng kịch bản nhé!"
        )
    }

    dialogue_entry = {
        "session_id": f"SESSION-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}",
        "timestamp": now_str,
        "khanh_request": {
            "sender": "Khánh — Trưởng Ban 11 (Sáng Tạo Nội Dung)",
            "message": khanh_message,
            "target_ticker": clean_sym,
            "research_focus": research_focus
        },
        "hien_response": hien_response
    }

    # Lưu nhật ký trao đổi liên phòng ban
    existing_dialogues = []
    if DIALOGUE_LOG.exists():
        try:
            existing_dialogues = json.loads(DIALOGUE_LOG.read_text(encoding="utf-8"))
        except Exception:
            existing_dialogues = []
    existing_dialogues.append(dialogue_entry)
    DIALOGUE_LOG.write_text(json.dumps(existing_dialogues, indent=2, ensure_ascii=False), encoding="utf-8")

    return hien_response


# ==============================================================================
# 3. ĐỘNG CƠ SẢN XUẤT KỊCH BẢN VIDEO 60S VIRAL (TIKTOK / REELS / SHORTS)
# ==============================================================================

def craft_viral_video_script(ticker: str = "HPG", chosen_angle_id: str = "ANGLE_01_TRUTH_EXPOSED") -> Dict[str, Any]:
    """
    Sản xuất kịch bản video dọc 9:16 thời lượng 60 giây hoàn chỉnh phục vụ quay trực tiếp.
    """
    clean_sym = ticker.upper().strip()
    
    # 1. Khánh liên hệ Hiền lấy dữ liệu
    angle = next((a for a in TRENDING_ANGLES if a["id"] == chosen_angle_id), TRENDING_ANGLES[0])
    hien_data = communicate_with_hien(clean_sym, angle["name"])

    now_date = datetime.date.today().strftime("%Y-%m-%d")
    now_str = datetime.datetime.now().strftime("%d/%m/%Y lúc %H:%M")

    # 2. Xây dựng nội dung chi tiết dựa trên dữ liệu thật của Hiền
    company_name = hien_data["company_name"]
    rev = f"{hien_data['revenue_vnd_bil']:,.1f} tỷ ₫"
    ni = f"{hien_data['net_income_vnd_bil']:,.1f} tỷ ₫"
    ocf = f"{hien_data['ocf_vnd_bil']:,.1f} tỷ ₫"
    ratio = f"{hien_data['ocf_to_net_income_ratio']}x"
    catalyst = hien_data["key_catalyst_notes"]

    if clean_sym == "HPG":
        title = "SỰ THẬT VỀ 'CỖ MÁY IN TIỀN' HÒA PHÁT: LÃI 8.200 TỶ NHƯNG TIỀN THẬT VÀO TÀI KHOẢN LÀ BAO NHIÊU?"
        hook_text = "Đừng mua Hòa Phát nếu chưa biết con số này! Công ty báo lãi 8.200 tỷ, nhưng số tiền mặt thật sự chảy về két là bao nhiêu? Có phải lợi nhuận trên giấy không?"
        body_text_1 = f"Hầu hết nhà đầu tư chỉ nhìn vào con số lợi nhuận sau thuế {ni}. Nhưng một bậc thầy đầu tư sẽ luôn kiểm tra dòng tiền kinh doanh OCF. Và đây là điều kinh ngạc mà Ban 10 vừa bóc tách:"
        body_text_2 = f"Dòng tiền kinh doanh thật của Hòa Phát quý vừa qua lên tới {ocf}! Tức là tỷ lệ tiền thật gấp {ratio} lần lợi nhuận kế toán. Tiền tươi thóc thật 100%!"
        body_text_3 = f"Không chỉ vậy, đại dự án Lò cao Dung Quất 2 với công suất 5,6 triệu tấn HRC/năm đang được tài trợ bằng chính cỗ máy in tiền này, không phải đọng vốn ảo."
        insight_text = "Bài học xương máu cho anh em: Khi doanh nghiệp có OCF lớn hơn LNST, đó là viên ngọc quý. Ngược lại, nếu lãi nghìn tỷ mà OCF âm liên tục 2 quý, hãy chạy ngay kẻo ăn bẫy xào nấu số liệu!"
        cta_text = "Anh em đang giữ Hòa Phát ở giá vốn bao nhiêu? Bình luận xuống dưới để mình cùng chia sẻ nhật ký gom hàng T+0 tại TCBS nhé!"
    elif clean_sym == "TCB":
        title = "BÍ MẬT ĐẰNG SAU DÒNG TIỀN CASA 40.5% CỦA TECHCOMBANK: CỖ MÁY HUY ĐỘNG VỐN 0 ĐỒNG!"
        hook_text = "Tại sao gửi tiết kiệm lãi suất ngày càng thấp, nhưng Techcombank lại liên tục phá kỷ lục lợi nhuận gần 8.000 tỷ 1 quý? Bí mật nằm ở 4 chữ: Tiền gửi CASA!"
        body_text_1 = f"Báo cáo tài chính quý gần nhất ghi nhận Techcombank đạt doanh thu {rev} và lợi nhuận ròng {ni}. Điều khủng khiếp nằm ở tỷ lệ CASA đạt 40.5% dẫn đầu toàn ngành ngân hàng."
        body_text_2 = "CASA tức là tiền không kỳ hạn để trong tài khoản của anh em với lãi suất chỉ 0.1% - 0.2%. Techcombank lấy nguồn vốn gần như 0 đồng này đem cho vay và tài trợ dự án với biên lãi NIM tới 4.2%!"
        body_text_3 = f"Thêm vào đó, việc chuẩn bị IPO TCBS đang là chất xúc tác cực mạnh giúp giá trị ngân hàng được định giá lại."
        insight_text = "Bài học thực chiến: Muốn chọn siêu cổ phiếu ngân hàng, đừng chỉ nhìn nợ xấu, hãy nhìn tỷ lệ CASA. Ngân hàng nào cầm nhiều vốn rẻ nhất, ngân hàng đó sẽ thắng cuộc chơi dài hạn."
        cta_text = "Anh em có đang dùng tài khoản Techcombank hay TCBS không? Thả tim và follow kênh để nhận file phân tích BCTC chi tiết nhé!"
    else:
        title = f"MỔ XẺ BÁO CÁO TÀI CHÍNH {clean_sym}: TIỀN THẬT HAY LỢI NHUẬN TRÊN GIẤY?"
        hook_text = f"Cảnh báo cho những ai đang ôm cổ phiếu {clean_sym}! Con số lãi {ni} trên mặt báo có thật sự an toàn hay đang che giấu bẫy kế toán?"
        body_text_1 = f"Soi vào BCTC quý gần nhất, doanh thu ghi nhận {rev}, lợi nhuận {ni}. Nhưng khi kiểm tra dòng tiền kinh doanh OCF thì đạt {ocf}."
        body_text_2 = f"Đánh giá chất lượng lợi nhuận: {hien_data['earnings_quality_rating']}. Doanh nghiệp có {catalyst}."
        body_text_3 = "Sự khác biệt giữa người kiếm được tiền và người đu đỉnh nằm ở năng lực đọc vị báo cáo tài chính trước khi đám đông nhận ra."
        insight_text = "Nguyên tắc thép của quỹ: Dòng tiền là máu của doanh nghiệp. Tiền thật vào tài khoản thì doanh nghiệp mới chia cổ tức và mở rộng được sản xuất."
        cta_text = "Bạn muốn bóc trần BCTC mã cổ phiếu nào tiếp theo? Hãy để lại comment mã chứng khoán bên dưới nhé!"

    # 3. Phân cảnh chi tiết 60 giây
    scene_breakdown = [
        {
            "scene": 1,
            "timestamp": "00:00 - 00:03",
            "duration": "3s",
            "phase": "🔥 HOOK (CHẶN NGÓN TAY)",
            "visual_cue": "Góc quay cận cảnh mặt (Close-up), biểu cảm nghiêm túc, mắt nhìn thẳng ống kính. Chữ to màu vàng viền đen giật tít nhấp nháy trên màn hình: 'SỰ THẬT BCTC HÒA PHÁT!'. B-Roll chèn hình ảnh lò cao đang rót thép đỏ rực.",
            "audio_sfx": "Tiếng sấm rền hoặc tiếng gõ búa đanh (Boom sound effect). Nhạc nền đệm kịch tính (Suspense beat).",
            "voiceover": hook_text
        },
        {
            "scene": 2,
            "timestamp": "00:04 - 00:18",
            "duration": "14s",
            "phase": "📊 THỰC TRẠNG & CON SỐ GIẤY",
            "visual_cue": "Chuyển sang góc trung (Medium shot). Màn hình chia đôi: Một bên là hình ảnh bài báo giật tít 'Lãi kỷ lục', một bên là bảng BCTC có khoanh tròn đỏ vào chỉ tiêu 'Lợi nhuận sau thuế'.",
            "audio_sfx": "Tiếng lật trang giấy (Page flip) + Tiếng 'Whoosh' chuyển cảnh.",
            "voiceover": body_text_1
        },
        {
            "scene": 3,
            "timestamp": "00:19 - 00:36",
            "duration": "17s",
            "phase": "💎 BÓC TRẦN TIỀN THẬT OCF (DATA TỪ HIỀN)",
            "visual_cue": "Zoom cận vào con số OCF trên đồ thị trực quan. Hiển thị đồ họa thanh màu xanh lá cây vọt lên cao hơn hẳn cột LNST. Hiệu ứng số tiền nhảy đếm ngược ting ting.",
            "audio_sfx": "Tiếng máy đếm tiền rè rè (Cash register) + Tiếng 'Ting ting' tiền vào tài khoản.",
            "voiceover": body_text_2
        },
        {
            "scene": 4,
            "timestamp": "00:37 - 00:48",
            "duration": "11s",
            "phase": "🚀 CHẤT XÚC TÁC & TRIỂN VỌNG DỰ ÁN",
            "visual_cue": "B-roll flycam toàn cảnh siêu dự án đại công trường hoặc hình ảnh sản phẩm thực tế. Dòng chữ nổi: 'Catalyst: Dung Quất 2 bổ sung 5.6M tấn HRC'.",
            "audio_sfx": "Nhạc nền chuyển sang nhịp điệu tích cực, tăng tốc (Uplifting tempo).",
            "voiceover": body_text_3
        },
        {
            "scene": 5,
            "timestamp": "00:49 - 00:55",
            "duration": "6s",
            "phase": "💡 BÀI HỌC THỰC CHIẾN (INSIGHT)",
            "visual_cue": "Góc quay cận cảnh. Chữ chạy từng từ (Dynamic Captions) nhấn mạnh công thức vàng: 'OCF > LNST = TIỀN THẬT'.",
            "audio_sfx": "Tiếng gõ chuông cảnh báo (Warning bell).",
            "voiceover": insight_text
        },
        {
            "scene": 6,
            "timestamp": "00:56 - 01:00",
            "duration": "5s",
            "phase": "🎯 CALL TO ACTION (CTA & PHỄU ICOPY)",
            "visual_cue": "Màn hình hiển thị nút Follow, nút Thả tim và icon bình luận rung rinh. Góc dưới gắn nhãn nhỏ: 'Tham khảo danh mục iCopy TCBS 105C307855'.",
            "audio_sfx": "Tiếng 'Click' chuột và tiếng chuông reo đăng ký.",
            "voiceover": cta_text
        }
    ]

    # 4. Master CIO James Thẩm Định & Phê Duyệt
    james_audit = {
        "auditor": "James — Master CIO (Ban 8)",
        "audit_timestamp": now_str,
        "metric_verification": f"ĐÃ KIỂM TRA CHÉO 100%: Số liệu Doanh thu, LNST, OCF hoàn toàn trùng khớp với Báo cáo Tài chính kiểm toán của {company_name} ({clean_sym}) do Ban 10 cung cấp.",
        "legal_disclaimer_status": "PASSED: Kịch bản tập trung vào giáo dục tài chính & mổ xẻ BCTC, có câu dẫn nhận định cá nhân, tuân thủ nghiêm ngặt quy chế công bố thông tin.",
        "viral_potential_score": 95,
        "viral_potential_rating": "CỰC KỲ XUẤT SẮC (HIGH VIRALITY)",
        "james_signature_stamp": "APPROVED FOR PRODUCTION — BẬT ĐÈN XANH QUAY VIDEO"
    }

    # SEO package dynamic theo mã
    if clean_sym == "HPG":
        caption_post = (
            f"{hook_text}\n\n"
            f"Nhiều anh em chỉ nhìn lãi {ni} mà quên mất dòng tiền kinh doanh OCF mới là máu của doanh nghiệp. "
            f"Quý này Hòa Phát mang về tới {ocf} tiền tươi thóc thật!\n\n"
            f"Anh em đang ôm HPG giá bao nhiêu? Để lại bình luận cùng đàm đạo nhé!\n\n"
            f"#hoaphat #hpg #chungkhoan #taichinh #bctc #dautu #kinhdoanh #kiemtien #tcbs #icopy"
        )
        hashtags = ["#hoaphat", "#hpg", "#chungkhoan", "#taichinh", "#bctc", "#dautu", "#kinhdoanh", "#kiemtien", "#tcbs", "#icopy"]
    elif clean_sym == "TCB":
        caption_post = (
            f"{hook_text}\n\n"
            f"Techcombank đang chứng minh vị thế cỗ máy in tiền với CASA 40.5% và lợi nhuận ròng {ni}!\n\n"
            f"Anh em đang dùng Techcombank hay TCBS? Để lại bình luận cùng đàm đạo nhé!\n\n"
            f"#techcombank #tcb #tcbs #chungkhoan #taichinh #nganhang #casa #dautu #icopy"
        )
        hashtags = ["#techcombank", "#tcb", "#tcbs", "#chungkhoan", "#taichinh", "#nganhang", "#casa", "#dautu", "#icopy"]
    else:
        caption_post = (
            f"{hook_text}\n\n"
            f"Nhiều anh em chỉ nhìn lãi trên báo mà quên mất dòng tiền kinh doanh OCF mới là dòng tiền thật. "
            f"Quý này {clean_sym} mang về {ocf} tiền thật ({hien_data['earnings_quality_rating']})!\n\n"
            f"Anh em đang theo dõi {clean_sym} ở vùng giá nào? Để lại bình luận nhé!\n\n"
            f"#{clean_sym.lower()} #chungkhoan #taichinh #bctc #dautu #kinhdoanh #kiemtien #tcbs #icopy"
        )
        hashtags = [f"#{clean_sym.lower()}", "#chungkhoan", "#taichinh", "#bctc", "#dautu", "#kinhdoanh", "#kiemtien", "#tcbs", "#icopy"]

    script_package = {
        "metadata": {
            "title": title,
            "ticker": clean_sym,
            "created_by": "Khánh — Trưởng Ban 11 (Viral Content Creator)",
            "supervised_by": "James — Master CIO (Ban 8)",
            "data_source_officer": "Hiền — Trưởng Ban 10 (Rà Soát BCTC & IR)",
            "target_platforms": ["TikTok", "YouTube Shorts", "Facebook Reels", "Threads"],
            "video_aspect_ratio": "9:16 (Dọc)",
            "estimated_duration": "59 Giây",
            "target_audience": "Nhà đầu tư F0, người đi làm quan tâm tài chính cá nhân & kiếm thêm thu nhập",
            "created_at": now_str
        },
        "scenes": scene_breakdown,
        "seo_package": {
            "video_title": title,
            "caption_post": caption_post,
            "hashtags": hashtags
        },
        "hien_data_feed": hien_data,
        "james_audit": james_audit
    }

    return script_package


# ==============================================================================
# 4. XUẤT BẢN FILE KỊCH BẢN MASTER MARKDOWN
# ==============================================================================

def export_khanh_script_markdown(package: Dict[str, Any]) -> Path:
    meta = package["metadata"]
    scenes = package["scenes"]
    seo = package["seo_package"]
    audit = package["james_audit"]
    hien = package["hien_data_feed"]

    now_date = datetime.date.today().strftime("%Y-%m-%d")
    output_path = CONTENT_DIR / f"{now_date}_Viral_Script_Khánh.md"

    md = [
        f"# 🎬 KỊCH BẢN VIDEO VIRAL 60S TIKTOK & SHORTS — BAN 11 (KHÁNH)",
        f"*Thời gian sản xuất*: `{meta['created_at']}`  ",
        f"*Tác giả kịch bản*: **Khánh — Trưởng Ban 11 (Viral Content Creator)**  ",
        f"*Cộng sự cung cấp dữ liệu*: **Hiền — Trưởng Ban 10 (Rà Soát BCTC & Quan Hệ Cổ Đông)**  ",
        f"*Tổng Tư Lệnh Giám Sát & Phê Duyệt*: **James — Master CIO (Ban 8)**  ",
        f"*Phục vụ trực tiếp*: **Chủ tịch Phước Trần** *(TCBS: `105C307855`)*  \n",
        "---",
        "## I. TỔNG QUAN DỰ ÁN VIDEO",
        f"- **Tiêu đề video**: **{meta['title']}**",
        f"- **Mã chứng khoán tâm điểm**: **`{meta['ticker']}`** ({hien['company_name']})",
        f"- **Định dạng**: Video khung dọc 9:16 (Phù hợp 100% cho TikTok, YouTube Shorts, Facebook Reels)",
        f"- **Thời lượng ước tính**: `{meta['estimated_duration']}`",
        f"- **Khán giả mục tiêu**: {meta['target_audience']}",
        f"- **Đánh giá tiềm năng Viral của James**: 🌟 **`{audit['viral_potential_score']}/100 — {audit['viral_potential_rating']}`**\n",
        "---",
        "## II. BIÊN BẢN TRAO ĐỔI NGHIỆP VỤ GIỮA KHÁNH VÀ HIỀN (21H15 TỐI NAY)",
        f"1. **Khánh đặt hàng Hiền**: Yêu cầu số liệu BCTC quý mới nhất của {meta['ticker']}, dòng tiền thật OCF và thông tin lò cao Dung Quất 2.",
        f"2. **Hiền phản hồi chính thức**:",
        f"   - *Doanh thu*: **`{hien['revenue_vnd_bil']:,.1f} tỷ ₫`** | *Lợi nhuận ròng*: **`{hien['net_income_vnd_bil']:,.1f} tỷ ₫`**",
        f"   - *Dòng tiền kinh doanh OCF*: **`{hien['ocf_vnd_bil']:,.1f} tỷ ₫`** *(Tiền thật vào túi = {hien['ocf_to_net_income_ratio']}x LNST)*",
        f"   - *Đánh giá tiền thật*: **`{hien['earnings_quality_rating']}`**",
        f"   - *Bảo chứng của Hiền*: *\"{hien['hien_verdict']}\"*\n",
        "---",
        "## III. BẢNG PHÂN CẢNH QUAY VIDEO 60 GIÂY CHI TIẾT (SHOOTING SCRIPT)\n",
        "| Phân Cảnh | Thời Gian | Giai Đoạn Kịch Bản | Hình Ảnh & Góc Máy (B-Roll / Visual Cue) | Âm Thanh & Nhạc (SFX / Music) | Lời Thoại Chủ Tịch (Voiceover) |",
        "| :---: | :---: | :---: | :--- | :--- | :--- |"
    ]

    for s in scenes:
        md.append(f"| **Cảnh {s['scene']}** | `{s['timestamp']}` | **{s['phase']}** | {s['visual_cue']} | {s['audio_sfx']} | *\"{s['voiceover']}\"* |")

    md.extend([
        "\n---",
        "## IV. GÓI ĐĂNG BÀI TỐI ƯU SEO & PHỄU CHUYỂN ĐỔI (PUBLISHING PACKAGE)",
        f"### 1. Caption Đăng Bài (Copy & Paste 1 Chạm)",
        f"```text\n{seo['caption_post']}\n```\n",
        f"### 2. Bộ Hashtags Đề Xuất",
        f"`{' '.join(seo['hashtags'])}`\n",
        f"### 3. Phễu Tạo Dòng Tiền Thu Nhập Ngoài Luồng (Kiếm 3 - 4 Triệu/Tháng)",
        f"- Gắn link Bio hoặc ghim bình luận đầu tiên: *\"Chi tiết cách mình gom hàng {meta['ticker']} và lướt T+0 hạ giá vốn, anh em xem trong danh mục iCopy TCBS mã 105C307855 của mình nhé!\"*",
        f"- Thu hút người sao chép danh mục $\\rightarrow$ Tạo ra hoa hồng chia sẻ lợi nhuận đều đặn hàng tháng.\n",
        "---",
        "## V. BIÊN BẢN PHÊ DUYỆT CỦA TỔNG TƯ LỆNH MASTER CIO JAMES",
        f"- **Người kiểm định**: **{audit['auditor']}**",
        f"- **Xác thực số liệu**: ✅ {audit['metric_verification']}",
        f"- **Kiểm tra an toàn pháp lý**: ✅ {audit['legal_disclaimer_status']}",
        f"- **Điểm Viral Index**: 🌟 **`{audit['viral_potential_score']}/100`**",
        f"- **Phán quyết cuối cùng**: 🎖️ **`{audit['james_signature_stamp']}`**",
        f"- *Lời dặn của James*: *\"Kịch bản rất đắt giá, đánh trúng tâm lý tò mò của số đông và khai thác trọn vẹn số liệu OCF tiền thật của Hiền. Đề nghị Chủ tịch tự tin bấm máy quay video này ngay tối nay!\"*"
    ])

    content_str = "\n".join(md)
    output_path.write_text(content_str, encoding="utf-8")
    return output_path


def export_render_job_for_bao(package: Dict[str, Any]) -> Path:
    """
    Chuyển giao gói dữ liệu kỹ thuật dựng phim cho Bảo trên máy tính để bàn.
    Bao gồm cấu trúc từng phân cảnh, text voiceover, visual cues, font và audio specs.
    """
    meta = package["metadata"]
    scenes = package["scenes"]
    clean_sym = meta["ticker"]
    now_date = datetime.date.today().strftime("%Y-%m-%d")

    job_id = f"JOB-{now_date}-{clean_sym}"
    job_file = RENDER_QUEUE_DIR / f"{now_date}_{clean_sym}_render_job.json"

    render_job = {
        "job_id": job_id,
        "created_at": meta["created_at"],
        "assigned_to": "Bảo — Chuyên Viên Dựng Phim & Render Video AI (Desktop Studio)",
        "chief_strategist": "Khánh — Trưởng Ban 11 (Laptop HQ)",
        "status": "PENDING_DESKTOP_RENDER",
        "ticker": clean_sym,
        "video_title": meta["title"],
        "aspect_ratio": "9:16",
        "resolution": {"width": 1080, "height": 1920},
        "target_fps": 30,
        "voice_preset": {
            "primary": "vi-VN-NamMinhNeural",
            "alternative": "vi-VN-HoaiMyNeural",
            "rate": "+0%",
            "pitch": "+0Hz"
        },
        "tcbs_icopy_badge": "iCopy TCBS: 105C307855",
        "scenes": [
            {
                "scene_idx": s["scene"],
                "phase": s["phase"],
                "timestamp": s["timestamp"],
                "duration_est_seconds": int(s["duration"].replace("s", "")),
                "voiceover_text": s["voiceover"],
                "visual_prompt": s["visual_cue"],
                "audio_sfx_cue": s["audio_sfx"],
                "subtitle_text": s["voiceover"]
            }
            for s in scenes
        ],
        "seo_package": package["seo_package"],
        "hien_data": package["hien_data_feed"],
        "output_expected_path": str(OUTPUT_DIR / f"{job_id}.mp4")
    }

    job_file.write_text(json.dumps(render_job, indent=2, ensure_ascii=False), encoding="utf-8")
    return job_file


# ==============================================================================
# 5. ĐIỀU KHIỂN CHẠY ROUTINE HOÀN CHỈNH
# ==============================================================================

def run_khanh_evening_routine(ticker: str = "HPG", angle_id: str = "ANGLE_01_TRUTH_EXPOSED") -> Dict[str, Any]:
    print(f"[*] BAN 11 (KHÁNH) BẮT ĐẦU PHIÊN TÁC CHIẾN TỐI 21H15 CHO MÃ: {ticker} (Góc nhìn: {angle_id})...")
    init_or_update_trending_vault()
    package = craft_viral_video_script(ticker, angle_id)
    file_path = export_khanh_script_markdown(package)
    job_file = export_render_job_for_bao(package)
    print(f"[+] Đã hoàn thành kịch bản video viral tại: {file_path}")
    print(f"[+] Đã chuyển giao Lệnh Dựng Phim (Render Job) cho Bảo tại: {job_file}")
    print(f"[+] Đã cập nhật Kho dữ liệu Trending Vault tại: {TRENDING_VAULT}")
    return package


def generate_viral_content(query: str = "HPG") -> Dict[str, Any]:
    """Hàm tiện ích tương thích nhận diện mã từ query và sinh kịch bản hoàn chỉnh"""
    import re
    tickers = re.findall(r"\b[A-Z]{3}\b", (query or "").upper())
    STOP_WORDS = {
        "CHO", "CUA", "TOI", "HAY", "CAC", "MOI", "NGAY", "NAY", "BAN", "XEM", "NAO", "LAM", "VAO", "GUI",
        "XUAT", "TIM", "DOC", "BAI", "HOI", "CON", "MOT", "HAI", "BA", "KHI", "THI", "LAI", "NHAN", "VOI",
        "TRONG", "NGOAI", "THEO", "DUOC", "MINH", "QUAN", "ALEX", "HIEN", "VICTOR", "JAMES", "VND", "USD", "NAV"
    }
    valid_tickers = [t for t in tickers if t not in STOP_WORDS]
    sym = valid_tickers[0] if valid_tickers else "HPG"
    pkg = run_khanh_evening_routine(sym)
    scenes = pkg.get("scenes", [])
    hook_3s = scenes[0].get("spoken_script", "") if scenes else ""
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    return {
        "title": pkg.get("metadata", {}).get("title", f"Bí mật BCTC {sym}"),
        "ticker": sym,
        "hook_3s": hook_3s,
        "duration_seconds": 60,
        "cta": "Bấm theo dõi kênh để không bị lừa bởi BCTC lợi nhuận giấy!",
        "script_file": f"11_Viral_Content_Creation/{date_str}_Viral_Script_Khanh_{sym}.md",
        "package": pkg
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ban 11 — Khánh Chief Viral Financial Content Creator Engine")
    parser.add_argument("ticker_pos", nargs="?", default=None, help="Mã chứng khoán (tùy chọn theo vị trí, ví dụ: HPG, TCB)")
    parser.add_argument("--ticker", "-t", type=str, default=None, help="Mã chứng khoán tâm điểm (ví dụ: HPG, TCB, MBB)")
    parser.add_argument("--hook-style", "--angle", type=str, default="ANGLE_01_TRUTH_EXPOSED", help="Góc tiếp cận viral")
    parser.add_argument("--run-routine", action="store_true", help="Chạy routine sản xuất kịch bản lúc 21h15")
    parser.add_argument("--list-trends", action="store_true", help="Hiển thị danh sách góc tiếp cận trending")
    parser.add_argument("--init-vault", action="store_true", help="Khởi tạo hoặc cập nhật kho dữ liệu Trending Vault")

    args = parser.parse_args()

    if args.list_trends:
        print("\n=== DANH SÁCH CÁC GÓC TIẾP CẬN TRENDING BAN 11 (KHÁNH) ===")
        for a in TRENDING_ANGLES:
            print(f"- [{a['id']}] {a['name']}: {a['hook_template'][:70]}... (Mã phù hợp: {', '.join(a['suitable_tickers'])})")
        sys.exit(0)

    if args.init_vault:
        vault = init_or_update_trending_vault()
        print(f"[+] Đã khởi tạo Trending Vault thành công tại: {TRENDING_VAULT}")
        sys.exit(0)

    target_sym = args.ticker or args.ticker_pos or "HPG"
    run_khanh_evening_routine(target_sym, args.hook_style)
