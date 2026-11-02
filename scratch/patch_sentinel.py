with open('scripts/intraday_portfolio_sentinel.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = "def send_telegram_alert(config: Dict[str, Any], text: str):"
replacement = """def send_telegram_alert(config: Dict[str, Any], text: str):
    try:
        from scripts.telegram_dispatcher import dispatch_message
        if dispatch_message("alerts", text):
            print("  [+] Đã gửi tin nhắn cảnh báo qua Telegram Dispatcher!")
            return
    except Exception:
        pass"""

if target in text:
    text = text.replace(target, replacement, 1)
    with open('scripts/intraday_portfolio_sentinel.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESS: Patched intraday_portfolio_sentinel.py")
else:
    print("TARGET NOT FOUND")
