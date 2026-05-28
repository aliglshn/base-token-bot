```python
import requests
import time
import os
import json
import html
import threading

from datetime import datetime, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# =========================================================
# CONFIG
# =========================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASED_X = "https://x.com/basedbot"
BASED_TELEGRAM = "https://t.me/based_eth_bot?start=r_aliglshn1"

CHECK_INTERVAL = 45

MIN_VOLUME = 50000
MIN_LIQUIDITY = 10000

SEEN_FILE = "seen_tokens.json"

GECKO_API = "https://api.geckoterminal.com/api/v2/networks/base/new_pools"

# =========================================================
# GLOBALS
# =========================================================

top_tokens_24h = []
top_lock = threading.Lock()

# =========================================================
# HTTP SESSION WITH RETRY
# =========================================================

session = requests.Session()

retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)

adapter = HTTPAdapter(max_retries=retries)

session.mount("https://", adapter)
session.mount("http://", adapter)

# =========================================================
# PERSISTENT STORAGE
# =========================================================

def load_seen_tokens():
    if not os.path.exists(SEEN_FILE):
        return set()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return set(data)

    except Exception as e:
        print(f"[LOAD ERROR] {e}")
        return set()


def save_seen_tokens(tokens):
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(tokens), f)

    except Exception as e:
        print(f"[SAVE ERROR] {e}")


seen_tokens = load_seen_tokens()

# =========================================================
# TELEGRAM
# =========================================================

def send_telegram_message(chat_id, text):
    if not TELEGRAM_BOT_TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN not found")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        response = session.post(url, json=payload, timeout=15)

        response.raise_for_status()

        result = response.json()

        if not result.get("ok"):
            print("[TELEGRAM ERROR]", result)
            return False

        return True

    except Exception as e:
        print(f"[TELEGRAM SEND ERROR] {e}")
        return False

# =========================================================
# HELPERS
# =========================================================

def safe_float(value, default=0):
    try:
        return float(value)
    except:
        return default


def calculate_age_minutes(created_str):
    if not created_str:
        return 9999

    try:
        created_str = created_str.replace("Z", "+00:00")

        created_time = datetime.fromisoformat(created_str)

        now = datetime.now(timezone.utc)

        age_minutes = int(
            (now - created_time).total_seconds() / 60
        )

        return age_minutes

    except Exception as e:
        print(f"[AGE ERROR] {e}")
        return 9999

# =========================================================
# GECKO TERMINAL SCANNER
# =========================================================

def get_new_pairs_on_base():
    global top_tokens_24h
    global seen_tokens

    try:
        response = session.get(GECKO_API, timeout=20)

        response.raise_for_status()

        data = response.json()

        pools = data.get("data", [])

        print(
            f"\n[{datetime.now()}] "
            f"🔍 Scanning Base New Pools..."
        )

        current_top = []

        for pool in pools:

            attributes = pool.get("attributes", {})

            name = attributes.get("name", "Unknown")

            name = html.escape(name)

            contract = attributes.get("address", "N/A")

            volume = safe_float(
                attributes.get("volume_usd", 0)
            )

            liquidity = safe_float(
                attributes.get("reserve_in_usd", 0)
            )

            created_str = attributes.get("pool_created_at")

            age_min = calculate_age_minutes(created_str)

            token_info = {
                "name": name,
                "contract": contract,
                "vol": volume,
                "liq": liquidity,
                "age": age_min,
                "link": f"https://www.geckoterminal.com/base/pools/{contract}"
            }

            current_top.append(token_info)

            print(
                f"{name[:30]:30} | "
                f"VOL ${volume:,.0f} | "
                f"LIQ ${liquidity:,.0f} | "
                f"{age_min}m"
            )

            # =================================================
            # FILTER
            # =================================================

            if (
                volume >= MIN_VOLUME
                and liquidity >= MIN_LIQUIDITY
            ):

                if contract not in seen_tokens:

                    seen_tokens.add(contract)

                    save_seen_tokens(seen_tokens)

                    status = (
                        "🚀 NEW + STRONG"
                        if age_min <= 90
                        else "🔥 HIGH VOLUME"
                    )

                    message = f"""
<b>{status} on Base!</b>

🪙 {name}

📍 <code>{contract}</code>

📊 Vol 24h: ${volume:,.0f}
💧 Liquidity: ${liquidity:,.0f}

⏱️ Age: {age_min} min

🔗 <a href="{token_info['link']}">GeckoTerminal</a>

💸 <a href="{BASED_TELEGRAM}">
Trade with Based Bot
</a>
"""

                    print(f"[ALERT] {name}")

                    send_telegram_message(
                        TELEGRAM_CHAT_ID,
                        message
                    )

        # =====================================================
        # UPDATE TOP TOKENS THREAD-SAFE
        # =====================================================

        current_top = sorted(
            current_top,
            key=lambda x: x["vol"],
            reverse=True
        )[:10]

        with top_lock:
            top_tokens_24h = current_top

    except Exception as e:
        print(f"[SCAN ERROR] {e}")

# =========================================================
# TELEGRAM COMMANDS
# =========================================================

def check_telegram_commands():

    offset = 0

    while True:

        try:

            url = (
                f"https://api.telegram.org/"
                f"bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            )

            params = {
                "offset": offset,
                "timeout": 30
            }

            response = session.get(
                url,
                params=params,
                timeout=35
            )

            response.raise_for_status()

            data = response.json()

            updates = data.get("result", [])

            for update in updates:

                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                message = update["message"]

                chat_id = message["chat"]["id"]

                text = (
                    message.get("text", "")
                    .strip()
                    .lower()
                )

                # =============================================
                # /TOP
                # =============================================

                if text in ["/top", "/best", "top", "best"]:

                    with top_lock:
                        current_top = top_tokens_24h.copy()

                    if not current_top:

                        send_telegram_message(
                            chat_id,
                            "⏳ هنوز اطلاعات کافی جمع نشده..."
                        )

                        continue

                    msg = (
                        "<b>🏆 Top Base Tokens</b>\n\n"
                    )

                    for i, token in enumerate(current_top[:8], 1):

                        msg += (
                            f"{i}. <b>{token['name']}</b>\n"
                            f"📊 Vol: ${token['vol']:,.0f}\n"
                            f"💧 Liq: ${token['liq']:,.0f}\n"
                            f"⏱️ Age: {token['age']} min\n"
                            f"🔗 <a href='{token['link']}'>Chart</a>\n\n"
                        )

                    msg += (
                        f"💸 <a href='{BASED_TELEGRAM}'>"
                        f"Trade with Based Bot"
                        f"</a>"
                    )

                    send_telegram_message(chat_id, msg)

        except Exception as e:

            print(f"[TELEGRAM LOOP ERROR] {e}")

            time.sleep(5)

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print(
        "🚀 Base Meme Radar Bot Started\n"
        f"Min Volume: ${MIN_VOLUME:,}\n"
        f"Min Liquidity: ${MIN_LIQUIDITY:,}\n"
    )

    telegram_thread = threading.Thread(
        target=check_telegram_commands,
        daemon=True
    )

    telegram_thread.start()

    while True:

        try:

            get_new_pairs_on_base()

        except Exception as e:

            print(f"[MAIN LOOP ERROR] {e}")

        time.sleep(CHECK_INTERVAL)
```
