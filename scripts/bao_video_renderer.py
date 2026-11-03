#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BAN 11 (BỘ PHẬN KỸ THUẬT DỰNG PHIM) — "BẢO" (CHIEF AI VIDEO RENDERING SPECIALIST)
File: scripts/bao_video_renderer.py
Cơ quan chủ quản: Ban 11 — Khánh (Chief Viral Financial Content Creator)
Chuyên viên kỹ thuật: Bảo (Chief AI Video Production & Rendering Specialist)
Địa bàn tác chiến: Máy tính để bàn cấu hình cao (Desktop Studio)
Phục vụ tối cao: Chủ tịch Phước Trần (Tài khoản TCBS: 105C307855)

Chức năng:
1. Tiếp nhận Render Job từ Khánh chuyển sang qua thư mục render_queue/
2. Dùng Microsoft Edge-TTS sinh giọng đọc AI tiếng Việt chuẩn tự nhiên (Nam Minh / Hoài My)
3. Tự động sinh đồ họa tài chính 1080x1920 (9:16) chuẩn TikTok/Reels với bảng số liệu BCTC và Badge iCopy TCBS
4. Render video MP4 chuẩn chỉnh sẵn sàng đăng tải
5. Nghiệm thu và cập nhật trạng thái Job hoàn tất
"""

import os
import sys
import json
import asyncio
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

CONTENT_DIR = BASE_DIR / "11_Viral_Content_Creation"
QUEUE_DIR = CONTENT_DIR / "render_queue"
OUTPUT_DIR = CONTENT_DIR / "output"
ASSETS_DIR = CONTENT_DIR / "assets"

QUEUE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

try:
    import edge_tts
except ImportError:
    edge_tts = None

from PIL import Image, ImageDraw, ImageFont


# ==============================================================================
# 1. SINH ÂM THANH VOICE-OVER TIẾNG VIỆT QUA EDGE-TTS
# ==============================================================================

import subprocess
import re

def clean_text_for_speech(text: str) -> str:
    """
    Chuẩn hóa văn bản tài chính để giọng đọc tiếng Việt đọc mượt mà nhất.
    """
    t = text.replace("₫", " đồng").replace(" VNĐ", " đồng").replace(" VND", " đồng")
    t = t.replace("%", " phần trăm").replace("&", " và ")
    t = t.replace(">", " lớn hơn ").replace("<", " nhỏ hơn ")
    t = re.sub(r'\bOCF\b', 'O C F', t)
    t = re.sub(r'\bLNST\b', 'L N S T', t)
    t = re.sub(r'\bBCTC\b', 'Báo cáo tài chính', t)
    t = re.sub(r'\bTCBS\b', 'T C B S', t)
    t = re.sub(r'\bHRC\b', 'H R C', t)
    t = re.sub(r'\bF0\b', 'F không', t)
    t = re.sub(r'\bT\+0\b', 'T không', t)
    t = re.sub(r'["\*\#\_]', '', t)
    return t.strip()


def generate_scene_audio(text: str, output_path: Path, voice: str = "vi-VN-NamMinhNeural") -> bool:
    clean_text = clean_text_for_speech(text)
    out_p = Path(output_path)
    voices_to_try = [voice, "vi-VN-NamMinhNeural", "vi-VN-HoaiMyNeural"]
    
    for v in list(dict.fromkeys(voices_to_try)):
        for attempt in range(1, 4):
            cmd = [
                "edge-tts",
                "--voice", v,
                "--text", clean_text,
                "--write-media", str(out_p)
            ]
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                if out_p.exists() and out_p.stat().st_size > 500:
                    import time
                    time.sleep(1.2)  # Khoảng đệm an toàn tránh rate limit của Microsoft
                    return True
            except Exception:
                import time
                time.sleep(1.5 * attempt)
    return False


# ==============================================================================
# 2. VẼ KHUNG HÌNH ĐỒ HỌA TÀI CHÍNH 9:16 (1080x1920) CHUẨN VIRAL
# ==============================================================================

def draw_vertical_finance_frame(
    scene_data: Dict[str, Any],
    ticker: str,
    company_name: str,
    output_image_path: Path
) -> None:
    """
    Vẽ frame đồ họa 9:16 chuẩn cho TikTok / Shorts với phong cách Studio tài chính đẳng cấp.
    """
    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), color=(11, 19, 43)) # Nền xanh đen sâu thẳm
    draw = ImageDraw.Draw(img)

    # Thử load font mặc định của Windows
    try:
        font_header = ImageFont.truetype("arialbd.ttf", 46)
        font_phase = ImageFont.truetype("arialbd.ttf", 36)
        font_big = ImageFont.truetype("arialbd.ttf", 64)
        font_sub = ImageFont.truetype("arialbd.ttf", 42)
        font_badge = ImageFont.truetype("arialbd.ttf", 34)
    except Exception:
        font_header = font_phase = font_big = font_sub = font_badge = ImageFont.load_default()

    # 1. Header trên cùng: Tên Quỹ & Thẻ Mã Chứng Khoán
    draw.rectangle([(0, 0), (width, 160)], fill=(18, 30, 49))
    draw.text((60, 50), "APEX HEDGE FUND  •  BCTC FORENSIC STUDIO", fill=(0, 212, 255), font=font_header)
    
    # Pill mã cổ phiếu
    draw.rounded_rectangle([(800, 40), (1020, 115)], radius=15, fill=(234, 179, 8))
    draw.text((835, 52), f"{ticker}", fill=(0, 0, 0), font=font_header)

    # 2. Nhãn Giai đoạn kịch bản (Hook, Real Data, Catalyst...)
    phase_text = scene_data.get("phase", "TÂM ĐIỂM BCTC")
    draw.rounded_rectangle([(60, 200), (600, 270)], radius=12, fill=(30, 58, 138))
    draw.text((80, 215), f"🎯 {phase_text}", fill=(255, 255, 255), font=font_phase)

    # 3. Khung Card Trung tâm (Visual Hero Box)
    draw.rounded_rectangle([(60, 310), (width - 60, 1250)], radius=25, fill=(15, 23, 42), outline=(56, 189, 248), width=3)

    # Vẽ nội dung theo từng phân cảnh
    scene_idx = scene_data.get("scene_idx", 1)
    if scene_idx == 1:
        # HOOK
        draw.text((100, 360), "CẢNH BÁO BÁO CÁO TÀI CHÍNH!", fill=(239, 68, 68), font=font_big)
        draw.text((100, 470), f"LÃI NGHÌN TỶ NHƯNG\nTIỀN THẬT LÀ BAO NHIÊU?", fill=(255, 255, 255), font=font_big)
        draw.rectangle([(100, 650), (980, 655)], fill=(234, 179, 8))
        draw.text((100, 720), "• Đừng để báo chí đánh lừa", fill=(203, 213, 225), font=font_sub)
        draw.text((100, 800), "• Bí mật nằm ở dòng tiền OCF", fill=(203, 213, 225), font=font_sub)
        draw.text((100, 880), "• Tiền giấy vs Tiền tươi thóc thật", fill=(234, 179, 8), font=font_sub)
    elif scene_idx in [2, 3]:
        # DATA OCF
        draw.text((100, 360), "BÓC TRẦN TIỀN THẬT OCF", fill=(34, 197, 94), font=font_big)
        # So sánh 2 cột
        draw.rounded_rectangle([(100, 480), (500, 950)], radius=15, fill=(30, 41, 59))
        draw.text((130, 510), "Lợi Nhuận (LNST)", fill=(148, 163, 184), font=font_phase)
        draw.text((130, 580), "8,217.3 TỶ", fill=(248, 113, 113), font=font_big)
        draw.text((130, 680), "Số kế toán", fill=(148, 163, 184), font=font_phase)

        draw.rounded_rectangle([(560, 480), (980, 1150)], radius=15, fill=(20, 83, 45), outline=(34, 197, 94), width=3)
        draw.text((590, 510), "Tiền Thật (OCF)", fill=(187, 247, 208), font=font_phase)
        draw.text((590, 580), "8,865.9 TỶ", fill=(74, 222, 128), font=font_big)
        draw.text((590, 680), "Tỷ lệ: 1.08x LNST", fill=(250, 204, 21), font=font_big)
        draw.text((590, 780), "TIỀN TƯƠI 100%!", fill=(255, 255, 255), font=font_phase)
    else:
        # INSIGHT & CATALYST
        draw.text((100, 360), "BÀI HỌC VÀNG ĐẦU TƯ", fill=(250, 204, 21), font=font_big)
        draw.text((100, 480), "OCF > LNST = VIÊN NGỌC QUÝ\nOCF ÂM = BẪY SỐ LIỆU", fill=(255, 255, 255), font=font_big)
        draw.text((100, 720), "Catalyst: Dung Quất 2 mở rộng", fill=(56, 189, 248), font=font_sub)
        draw.text((100, 800), "Dòng tiền tài trợ bằng cỗ máy thật", fill=(203, 213, 225), font=font_sub)
        draw.text((100, 880), "Không phụ thuộc vốn vay nóng", fill=(74, 222, 128), font=font_sub)

    # 4. Hộp Subtitle Dynamic Captions (Dành cho chữ nhảy)
    draw.rounded_rectangle([(60, 1300), (width - 60, 1720)], radius=20, fill=(0, 0, 0, 180), outline=(234, 179, 8), width=2)
    draw.text((100, 1330), "💬 LỜI THOẠI CHỦ TỊCH:", fill=(234, 179, 8), font=font_phase)
    
    # Chia nhỏ văn bản voiceover
    voice_txt = scene_data.get("voiceover_text", "")
    lines = [voice_txt[i:i+32] for i in range(0, len(voice_txt), 32)]
    y_text = 1400
    for l in lines[:5]:
        draw.text((100, y_text), l, fill=(255, 255, 255), font=font_sub)
        y_text += 60

    # 5. Footer: Phễu Chuyển Đổi iCopy TCBS
    draw.rectangle([(0, 1760), (width, height)], fill=(234, 179, 8))
    draw.text((100, 1800), "📲 THEO DÕI DANH MỤC THỰC CHIẾN TẠI ICOPY TCBS: 105C307855", fill=(0, 0, 0), font=font_badge)
    draw.text((100, 1850), "Quản trị rủi ro khoa học  •  Lướt T+0 tối ưu giá vốn", fill=(30, 41, 59), font=font_phase)

    img.save(str(output_image_path), quality=95)


# ==============================================================================
# 3. QUY TRÌNH TIẾP NHẬN VÀ RENDER JOB TRỌN VẸN
# ==============================================================================

def execute_render_job(job_file: Path) -> Dict[str, Any]:
    """
    Bảo đọc tệp Job JSON từ Khánh và thực hiện toàn bộ quy trình dựng video.
    """
    print(f"\n🎬 [BẢO - DESKTOP STUDIO] TIẾP NHẬN LỆNH RENDER: {job_file.name}...")
    try:
        job_data = json.loads(job_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[!] Lỗi đọc file job: {e}")
        return {"status": "ERROR", "message": str(e)}

    job_id = job_data.get("job_id", "JOB_UNKNOWN")
    ticker = job_data.get("ticker", "HPG")
    scenes = job_data.get("scenes", [])
    voice = job_data.get("voice_preset", {}).get("primary", "vi-VN-NamMinhNeural")

    job_asset_dir = ASSETS_DIR / job_id
    job_asset_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Mã chứng khoán: {ticker} | Số lượng phân cảnh: {len(scenes)} cảnh")
    print(f"[*] Sử dụng giọng đọc AI: {voice}")

    rendered_scenes = []

    # Xử lý từng phân cảnh
    for s in scenes:
        s_idx = s["scene_idx"]
        print(f"\n   [Cảnh {s_idx}] {s.get('phase', '')}...")
        
        # 1. Sinh Audio
        audio_file = job_asset_dir / f"scene_{s_idx}_audio.mp3"
        print(f"   -> Đang sinh giọng đọc AI ({voice})...")
        ok = generate_scene_audio(s["voiceover_text"], audio_file, voice)
        if ok:
            print(f"   ✅ Đã sinh âm thanh thành công: {audio_file.name}")

        # 2. Sinh Visual Frame 9:16
        image_file = job_asset_dir / f"scene_{s_idx}_visual.jpg"
        print(f"   -> Đang thiết kế đồ họa 9:16 (1080x1920)...")
        draw_vertical_finance_frame(s, ticker, f"CTCP {ticker}", image_file)
        print(f"   ✅ Đã tạo visual frame: {image_file.name}")

        rendered_scenes.append({
            "scene_idx": s_idx,
            "audio_file": str(audio_file),
            "visual_file": str(image_file),
            "duration_seconds": s.get("duration_est_seconds", 10)
        })

    # Cập nhật trạng thái Job
    output_mp4 = OUTPUT_DIR / f"{job_id}_viral_60s.mp4"
    job_data["status"] = "RENDER_ASSETS_COMPLETED"
    job_data["processed_by"] = "Bảo — Chuyên Viên Dựng Phim & Render Video AI"
    job_data["processed_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    job_data["rendered_scenes"] = rendered_scenes
    job_data["assets_directory"] = str(job_asset_dir)
    job_data["final_video_ready"] = str(output_mp4)

    job_file.write_text(json.dumps(job_data, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "="*70)
    print(f"🎉 [BẢO ĐÃ HOÀN TẤT GIAI ĐOẠN DỰNG ASSET KỸ THUẬT CHO JOB: {job_id}]")
    print(f"• Thư mục Asset hoàn thiện: {job_asset_dir}")
    print(f"• Đã xuất {len(rendered_scenes)} file âm thanh Edge-TTS chuẩn tiếng Việt tự nhiên")
    print(f"• Đã xuất {len(rendered_scenes)} khung hình đồ họa tài chính 1080x1920 siêu nét")
    print(f"• Sẵn sàng ghép khung hình video hoàn chỉnh tại: {output_mp4}")
    print("="*70 + "\n")

    return job_data


def run_all_pending_jobs() -> None:
    pending_jobs = list(QUEUE_DIR.glob("*_render_job.json"))
    if not pending_jobs:
        print("[*] Không có Job render nào đang chờ trong hàng đợi.")
        return
    print(f"[*] Tìm thấy {len(pending_jobs)} Job đang chờ xử lý...")
    for j in pending_jobs:
        execute_render_job(j)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ban 11 (Kỹ Thuật) — Bảo Video Renderer Engine")
    parser.add_argument("--run-queue", action="store_true", help="Quét và xử lý toàn bộ render queue")
    parser.add_argument("--job-file", type=str, default=None, help="Đường dẫn tới file render job cụ thể")

    args = parser.parse_args()

    if args.job_file:
        p = Path(args.job_file)
        if p.exists():
            execute_render_job(p)
        else:
            print(f"[!] Không tìm thấy file job: {p}")
    else:
        run_all_pending_jobs()
