@echo off
chcp 65001 >nul
echo ======================================================================
echo  🚀 KẾT NỐI HỆ THỐNG APEX MULTI-AGENT VỚI GITHUB ĐỂ CHẠY TỰ ĐỘNG 24/7
echo ======================================================================
echo.
echo Bước 1: Vào trang web: https://github.com/new
echo Bước 2: Tạo một repository mới (Khuyên đặt tên: apex-hedge-fund, chọn PRIVATE).
echo Bước 3: Copy đường link repository (Ví dụ: https://github.com/phuoct998/apex-hedge-fund.git).
echo.
set /p REPO_URL="Dán đường link GitHub của bạn vào đây và nhấn Enter: "

if "%REPO_URL%"=="" (
    echo [!] Bạn chưa nhập đường link. Hủy thao tác.
    pause
    exit /b
)

echo.
echo [*] Đang thiết lập remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo [*] Đang đẩy toàn bộ hệ thống lên GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo  🎉 CHÚC MỪNG! HỆ THỐNG ĐÃ ĐƯỢC ĐẨY LÊN GITHUB THÀNH CÔNG!
    echo ======================================================================
    echo Kể từ giờ:
    echo 1. Mỗi sáng lúc 07:30 (VN), GitHub sẽ tự động nghiên cứu đêm và gửi báo cáo Telegram.
    echo 2. Bạn có thể tắt máy tính cá nhân 100%%.
    echo ======================================================================
) else (
    echo.
    echo [!] Có lỗi khi push lên GitHub. Vui lòng kiểm tra lại quyền truy cập hoặc đường link.
)

pause
