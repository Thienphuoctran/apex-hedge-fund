# ==============================================================================
# APEX HEDGE FUND — IMMORTAL 24/7 DOCKER CONTAINER CLUSTER
# ĐỊNH CHẾ TÀI CHÍNH ĐỊNH LƯỢNG TOÀN DIỆN (12 PHÒNG BAN CHUYÊN TRÁCH)
# Phục vụ: Chủ tịch Trần Quốc Thiên Phước (TCBS: 105C307855)
# Kiến trúc: Linux Cloud Container / Render Web Service / VPS Docker
# ==============================================================================

FROM python:3.11-slim

WORKDIR /app

# Biến môi trường hệ thống
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    PORT=8000

# Cài đặt curl và CA certificates để hỗ trợ healthcheck và HTTPS
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập múi giờ Việt Nam (Asia/Ho_Chi_Minh)
ENV TZ=Asia/Ho_Chi_Minh
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ dự án vào container
COPY . .

# Mở cổng Web Dashboard & API Healthcheck
EXPOSE 8000 10000 7860

# Healthcheck định kỳ 30 giây để đảm bảo container luôn sống
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

# Khởi chạy Apex Cloud Supervisor 24/7 (Quản trị 4 tiến trình nền bao phủ 12 phòng ban)
CMD ["python", "scripts/start_apex_cloud_247.py"]
