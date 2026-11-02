import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.telegram_dispatcher import dispatch_message
from scripts.telegram_interactive_copilot import get_interactive_keyboard

welcome_msg = """👋 *[KÍNH CHÀO CHỦ TỊCH PHƯỚC TRẦN — PHÒNG ĐIỀU HÀNH 2 CHIỀU]*

Palmer tôi đã thiết lập thành công toàn bộ 4 phân luồng phòng ban cho Group Tác Chiến!

Tại Topic này, Chủ tịch có thể:
• Bấm các nút chức năng 1-chạm bên dưới để tra cứu tức thì
• Nhắn tin yêu cầu tóm tắt/tổng hợp bất kỳ lúc nào:
  - *"Tổng hợp thị trường hôm nay"*
  - *"Tóm tắt danh mục hiện tại"*
  - *"Kiểm tra mã HPG / TCB / MBB"*
  - *"Sổ lệnh hôm nay mua giá nào"*

Toàn bộ thông tin báo động khẩn cấp sẽ bay vào Topic 1, Bản tin sáng vào Topic 2, Tin tức BCTC vào Topic 3.
Chấm dứt hoàn toàn hiện tượng dính chùm tin nhắn!"""

ok = dispatch_message('copilot_chat', welcome_msg, reply_markup=get_interactive_keyboard())
print("Copilot welcome sent to Topic 4:", ok)
