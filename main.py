import requests
import time
import os
from datetime import datetime
import threading

# ====================== CONFIG ======================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

BASED_X = "https://x.com/basedbot"
BASED_TELEGRAM = "https://t.me/based_eth_bot?start=r_aliglshn1"

CHECK_INTERVAL = 45
# ===================================================

seen_tokens = set()
top_tokens_24h = []

def send_telegram_message(chat_id, text):
    if not TELEGRAM_BOT_TOKEN:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
        return True
    except:
        return False

def get_new_pairs_on_base():
    global top_tokens_24h
    url = "https://api.geckoterminal.com/api/v2/networks/base/new_pools"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        pools = data.get('data', [])
        
        print(f"\n[{datetime.now()}] 🔍 GeckoTerminal Scanner Running...")
        
        current_top = []
        
        for pool in pools[:200]:
            attributes = pool.get('attributes', {})
            name = attributes.get('name', 'Unknown')
            symbol = name.split('/')[0] if '/' in name else '???'
            contract = attributes.get('address', 'N/A')
            vol = float(attributes.get('volume_usd', {}).get('h24', 0) or 0)
            liq = float(attributes.get('reserve_in_usd', 0) or 0)
            created_str = attributes.get('pool_created_at')
            
            if not created_str:
                continue
                
            # تبدیل
