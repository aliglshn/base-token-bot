import requests
import time
import os
import json
import html

from datetime import datetime, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# =========================================================
# CONFIG
# =========================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CHECK_INTERVAL = 45

# ================= FILTERS =================

MIN_VOLUME = 50000
MIN_LIQUIDITY = 10000
MIN_AGE_MINUTES = 3
MAX_VOL_LIQ_RATIO = 20

# ===========================================

BASED_TELEGRAM = "https://t.me/based_eth_bot?start=r_aliglshn1"

# BETTER ENDPOINT
GECKO_API = (
    "https://api.geckoterminal.com/api/v2/"
    "networks/base/trending_pools"
)

SEEN_FILE = "seen_tokens.json"

# =========================================================
# GLOBALS
# =========================================================

top_tokens_24h = []
telegram_offset = 0

# =========================================================
# HTTP SESSION + RETRY
# =========================================================

session = requests.Session()

retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)

session.mount("https://", adapter)
session.mount("http://", adapter)

# =========================================================
# STORAGE
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

# Load persistent cache
seen_tokens = load_seen_tokens()

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

        age = int(
            (now - created_time).total_seconds() / 60
        )

        return age

    except Exception as e:

        print(f"[AGE ERROR] {e}")

        return 9999

# =========================================================
# TELEGRAM
# =========================================================

def send_telegram_message(chat_id, text):

    if not TELEGRAM_BOT_TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN missing")
        return False

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:

        response = session.post(
            url,
            json=payload,
            timeout=15
        )

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
# SCANNER
# =========================================================

def get_trending_pairs():

    global top_tokens_24h
    global seen_tokens

    try:

        response = session.get(
            GECKO_API,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        pools = data.get("data", [])

        print(
            f"\n[{datetime.now()}] "
            f"🔍 Scanning Trending Base Pools..."
        )

        current_top = []

        for pool in pools:

            try:

                attributes = pool.get("attributes", {})

                name = html.escape(
                    attributes.get("name", "Unknown")
                )

                contract = attributes.get(
                    "address",
                    "N/A"
                )

                volume = safe_float(
                    attributes.get("volume_usd", 0)
                )

                liquidity = safe_float(
                    attributes.get("reserve_in_usd", 0)
                )

                created_str = attributes.get(
                    "pool_created_at"
                )

                age_min = calculate_age_minutes(
                    created_str
                )

                if contract == "N/A":
                    continue

                if liquidity <= 0:
                    continue

                if volume <= 0:
                    continue

                token_info = {
                    "name": name,
                    "contract": contract,
                    "vol": volume,
                    "liq": liquidity,
                    "age": age_min,
                    "link": (
                        f"https://www.geckoterminal.com/"
                        f"base/pools/{contract}"
                    )
                }

                current_top.append(token_info)

                print(
                    f"{name[:28]:28} | "
                    f"VOL ${volume:,.0f} | "
                    f"LIQ ${liquidity:,.0f} | "
                    f"AGE {age_min}m"
                )

                # =================================================
                # FILTERS
                # =================================================

                if liquidity < MIN_LIQUIDITY:
                    continue

                if volume < MIN_VOLUME:
                    continue

                if age_min < MIN_AGE_MINUTES:
                    continue

                ratio = volume / liquidity

                if ratio > MAX_VOL_LIQ_RATIO:
                    continue

                # =================================================
                # DUPLICATE CHECK
                # =================================================

                if contract in seen_tokens:
                    continue

                seen_tokens.add(contract)

                save_seen_tokens(seen_tokens)

                status = (
                    "🚀 NEW STRONG TOKEN"
                    if age_min <= 90
                    else "🔥 TRENDING TOKEN"
                )

                message = f"""
<b>{status}</b>

🪙 <b>{name}</b>

📍 <code>{contract}</code>

📊 Volume 24h: ${volume:,.0f}

💧 Liquidity: ${liquidity:,.0f}

⚖️ Vol/Liq Ratio: {ratio:.1f}

⏱️ Age: {age_min} min

🔗 <a href="{token_info['link']}">GeckoTerminal</a>

💸 <a href="{BASED_TELEGRAM}">
Trade with Based Bot
</a>
"""

                print(
                    f"\n🚨 ALERT:"
                    f"\n{name}"
                    f"\nVOL ${volume:,.0f}"
                    f"\nLIQ ${liquidity:,.0f}"
                    f"\nRATIO {ratio:.1f}\n"
                )

                send_telegram_message(
                    TELEGRAM_CHAT_ID,
                    message
                )

            except Exception as pool_error:

                print(f"[POOL ERROR] {pool_error}")

                continue

        current_top = sorted(
            current_top,
            key=lambda x: x["vol"],
            reverse=True
        )[:10]

        top_tokens_24h = current_top

    except Exception as e:

        print(f"[SCAN ERROR] {e}")

# =========================================================
# TELEGRAM COMMANDS
# =========================================================

def check_telegram_commands():

    global telegram_offset

    try:

        url = (
            f"https://api.telegram.org/"
            f"bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        )

        params = {
            "offset": telegram_offset,
            "timeout": 1
        }

        response = session.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        updates = data.get("result", [])

        for update in updates:

            telegram_offset = update["update_id"] + 1

            if "message" not in update:
                continue

            message = update["message"]

            chat_id = message["chat"]["id"]

            text = (
                message.get("text", "")
                .strip()
                .lower()
            )

            if text in [
                "/top",
                "/best",
                "top",
                "best"
            ]:

                if not top_tokens_24h:

                    send_telegram_message(
                        chat_id,
                        "⏳ هنوز دیتا جمع نشده..."
                    )

                    continue

                msg = "<b>🏆 Top Base Tokens</b>\n\n"

                for i, token in enumerate(top_tokens_24h[:8], 1):

                    msg += (
                        f"{i}. <b>{token['name']}</b>\n"
                        f"📊 Vol: ${token['vol']:,.0f}\n"
                        f"💧 Liq: ${token['liq']:,.0f}\n"
                        f"⏱️ Age: {token['age']} min\n"
                        f"🔗 <a href='{token['link']}'>Chart</a>\n\n"
                    )

                send_telegram_message(chat_id, msg)

    except Exception as e:

        print(f"[TG ERROR] {e}")

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("\n🚀 BASE MEME RADAR STARTED\n")

    print(f"MIN VOLUME: ${MIN_VOLUME:,}")
    print(f"MIN LIQUIDITY: ${MIN_LIQUIDITY:,}")
    print(f"MIN AGE: {MIN_AGE_MINUTES} min")
    print(f"MAX VOL/LIQ RATIO: {MAX_VOL_LIQ_RATIO}")
    print(f"CHECK INTERVAL: {CHECK_INTERVAL}s\n")

    while True:

        try:

            get_trending_pairs()

            for _ in range(CHECK_INTERVAL):

                check_telegram_commands()

                time.sleep(1)

        except Exception as e:

            print(f"[MAIN LOOP ERROR] {e}")

            time.sleep(5)
