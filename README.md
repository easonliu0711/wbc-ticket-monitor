# ⚾ WBC Ticket Monitor

A resilient multi-event ticket monitoring system with Telegram bot control.

Built to monitor resale listings on Tixplus and send real-time alerts when new tickets become available.

---

## 🚀 Features

### 🔎 Multi-Event Monitoring
Monitor multiple listing URLs simultaneously.

Each listing maintains its own state file:
state_1520.json
state_1517.json
state_1526.json

Prevents duplicate alerts.

---

### 🛡 Anti-Blocking Strategy

- Randomized polling interval (jitter)
- Session-based requests
- Automatic slow-down on anomalies
- No unnecessary scraping from Telegram commands

---

### 📦 Stateful Architecture

Each monitored listing tracks:

- Last known availability
- Last biddable count
- Last update timestamp

This ensures accurate change detection.

---

### 📱 Telegram Bot Control

Supported commands:
/status
/status 1520


Reads local state without triggering new scraping.

Future-ready for:
/force
/add
/remove

---

## 🧠 Architecture
main.py
├── run_once()
│ └── scraper.py
│ └── requests.Session()
│
├── telegram_listener.py
│ └── getUpdates (offset-controlled)
│
└── notifier.py

Design principles:

- Polling-based bot (no webhook needed)
- Offset control to prevent duplicate replies
- Decoupled scraper and notifier
- Per-listing state isolation

---

## ⚙️ Configuration

Create a `.env` file (not committed):
TELEGRAM_TOKEN=your_token
CHAT_ID=your_chat_id

Create `config_settings.json`:

```json
{
  "target_urls": [
    "https://tradead.tixplus.jp/.../1520",
    "https://tradead.tixplus.jp/.../1517"
  ],
  "check_interval_seconds": 300
}

Development
source .venv/bin/activate
python main.py
Background Mode
nohup python -u main.py > log.txt 2>&1 &

🔐 Security

Secrets stored in .env

.gitignore excludes runtime state

Token rotation supported

📈 Roadmap

Dynamic event management via Telegram

Docker deployment

Multi-platform ticket monitoring

Web dashboard

👨‍💻 Author

Built as a system design & automation exercise focused on:

Monitoring architecture

Telegram bot control

Defensive scraping strategy

Stateful change detection


---
