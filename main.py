import requests
import time
import os
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

BASED_TELEGRAM = "https://t.me/based_eth_bot?start=r_aliglshn1"

seen_tokens = set()

def send_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
        print("✅ Telegram Sent")
    except:
        print("Send failed")

def scan():
    url = "https://api.geckoterminal.com/api/v2/networks/base/new_pools"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        pools = data.get('data', [])
        
        print(f"\n[{datetime.now()}] Strong Filter Running (Min 60k Vol + 15k Liq)...")
        
        for pool in pools[:250]:
            attr = pool.get('attributes', {})
            name = attr.get('name', 'Unknown')
            contract = attr.get('address', 'N/A')
            vol = float(attr.get('volume_usd', {}).get('h24', 0) or 0)
            liq = float(attr.get('reserve_in_usd', 0) or 0)
            
            # فیلتر خیلی قوی‌تر
            if vol < 60000 or liq < 15000:
                continue
                
            if contract in seen_tokens:
                continue
                
            seen_tokens.add(contract)
            
            link = f"https://www.geckoterminal.com/base/pools/{contract}"
            
            msg = f"""<b>🔥 Strong Token Detected!</b>

🪙 {name}
📍 <code>{contract}</code>
📊 Vol 24h: ${vol:,.0f}
📈 Liq: ${liq:,.0f}

🔗 <a href="{link}">GeckoTerminal</a>
💸 <a href="{BASED_TELEGRAM}">Trade with Based Bot</a>"""

            send_message(msg)
            print(f"Alert sent for {name} (Vol: ${vol:,.0f})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Base Radar Bot - Strong Filter (60k Vol + 15k Liq)")
    
    while True:
        scan()
        time.sleep(40)
