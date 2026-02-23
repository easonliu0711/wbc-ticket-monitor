# telegram_listener.py
import requests
import json
from pathlib import Path

STATE_PREFIX = "state_"
STATE_SUFFIX = ".json"


def get_updates(token, offset=None):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {}
    if offset:
        params["offset"] = offset
    r = requests.get(url, params=params)
    return r.json()


def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })


def load_state_by_id(listing_id):
    state_file = Path(f"{STATE_PREFIX}{listing_id}{STATE_SUFFIX}")
    if not state_file.exists():
        return None
    return json.loads(state_file.read_text())


def load_all_states():
    states = []
    for file in Path(".").glob(f"{STATE_PREFIX}*{STATE_SUFFIX}"):
        listing_id = file.stem.replace(STATE_PREFIX, "")
        state = json.loads(file.read_text())
        states.append((listing_id, state))
    return states


def handle_status(token, chat_id, text):
    parts = text.split()

    # 指定場次
    if len(parts) == 2:
        listing_id = parts[1]
        state = load_state_by_id(listing_id)

        if not state:
            send_message(token, chat_id, f"找不到場次 {listing_id}")
            return

        msg = (
            f"⚾ WBC {listing_id}\n"
            f"可投標: {state.get('last_biddable')}\n"
            f"狀態: {state.get('last_status')}\n"
            f"更新時間: {state.get('updated_at')}"
        )
        send_message(token, chat_id, msg)
        return

    # 顯示全部
    states = load_all_states()
    if not states:
        send_message(token, chat_id, "尚無資料")
        return

    msg = "⚾ WBC 多場次狀態\n\n"
    for listing_id, state in states:
        msg += (
            f"{listing_id} | "
            f"{state.get('last_status')} | "
            f"{state.get('last_biddable')}\n"
        )

    send_message(token, chat_id, msg)


def run_listener(token, chat_id, last_update_id=None):
    url = f"https://api.telegram.org/bot{token}/getUpdates"

    params = {}
    if last_update_id:
        params["offset"] = last_update_id

    r = requests.get(url, params=params)
    data = r.json()

    if not data.get("ok"):
        return last_update_id

    for update in data.get("result", []):
        last_update_id = update["update_id"] + 1

        message = update.get("message", {})
        text = message.get("text")

        if text and text.startswith("/status"):
            handle_status(token, chat_id, text)

    return last_update_id