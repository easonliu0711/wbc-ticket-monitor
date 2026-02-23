# main.py
from __future__ import annotations

from dotenv import load_dotenv
import os
import json
import time
import random
from datetime import datetime
from pathlib import Path

from notifier import send_notification
from scraper import check_ticket
from telegram_listener import run_listener


# -------------------------
# Load environment variables
# -------------------------
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError("❌ Missing TELEGRAM_TOKEN or CHAT_ID in .env")


# -------------------------
# Config & State Helpers
# -------------------------

def load_config():
    with open("config_settings.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_listing_id(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def load_state(state_file: Path) -> dict:
    if state_file.exists():
        try:
            return json.loads(state_file.read_text())
        except Exception:
            pass
    return {"last_biddable": 0, "last_status": "UNKNOWN"}


def save_state(state_file: Path, state: dict):
    state_file.write_text(json.dumps(state, indent=2))


# -------------------------
# Core Monitoring Logic
# -------------------------

def run_once(config):
    urls = config["target_urls"]

    print("\n==============================")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🔍 檢查中...")

    unknown_count = 0

    for url in urls:
        listing_id = get_listing_id(url)
        state_file = Path(f"state_{listing_id}.json")

        print(f"\n📍 {listing_id}")

        result = check_ticket(url)

        if result.status == "UNKNOWN":
            print(f"⚠️ UNKNOWN: {result.reason}")
            unknown_count += 1
            continue

        state = load_state(state_file)
        previous = state.get("last_biddable", 0)
        current = result.biddable or 0

        if result.status == "AVAILABLE":
            print(f"✅ AVAILABLE: {current}")
        else:
            print("❌ SOLD_OUT")

        if current > previous:
            print("🚨 新票釋出！")
            message = (
                f"<b>⚾ WBC 門票釋出</b>\n\n"
                f"場次 ID: {listing_id}\n"
                f"目前可投標: {current}\n"
                f"之前: {previous}\n\n"
                f"<a href='{url}'>點擊前往</a>"
            )
            send_notification(
                message,
                TELEGRAM_TOKEN,
                TELEGRAM_CHAT_ID
            )

        state["last_biddable"] = current
        state["last_status"] = result.status
        state["updated_at"] = datetime.now().isoformat()

        save_state(state_file, state)

    return unknown_count


# -------------------------
# Main Loop
# -------------------------

def main():
    config = load_config()
    base_interval = CHECK_INTERVAL
    last_update_id = None

    print("🚀 雷達啟動（隱蔽模式）")

    while True:
        unknowns = run_once(config)

        last_update_id = run_listener(
            TELEGRAM_TOKEN,
            TELEGRAM_CHAT_ID,
            last_update_id
        )

        # 隨機間隔（anti-detection）
        interval = random.randint(
            int(base_interval * 0.8),
            int(base_interval * 1.2)
        )

        print(f"💤 下次檢查: {interval} 秒後")
        time.sleep(interval)


if __name__ == "__main__":
    main()