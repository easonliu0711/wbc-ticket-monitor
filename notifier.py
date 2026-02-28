import requests

def send_notification(message, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        # 增加 timeout 避免網路卡死
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        print("✅ Telegram notification sent successfully.")
    except Exception as e:
        # 僅印出錯誤而不噴出 Exception，確保監控主程式繼續運作
        print(f"⚠️ Telegram notification failed: {e}")