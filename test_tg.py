import requests
import json

with open('config_settings.json', 'r') as f:
    config = json.load(f)

token = config['telegram_token']
chat_id = config['telegram_chat_id']
url = f"https://api.telegram.org/bot{token}/sendMessage"

payload = {
    "chat_id": chat_id,
    "text": "🚀 這是來自 Dynabook NAS 的連線測試！"
}

print("正在嘗試發送測試訊息...")
r = requests.post(url, json=payload)

print("狀態碼:", r.status_code)

try:
    print("JSON回傳:", r.json())
except:
    print("原始回傳:", r.text)