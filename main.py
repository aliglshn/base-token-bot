import requests
import time
import os
from datetime import datetime

# ====================== TELEGRAM CONFIG ======================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# ===========================================================

CHECK_INTERVAL = 60

# ذخیره توکن‌های دیده شده برای جلوگیری از تکرار
seen_tokens = set()

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
        print("✅ Telegram Alert Sent!")
        return True
    except:
        return False

def get_new_pairs_on_base():
    url = "https://api.dexscreener.com/latest/dex/search?q=base"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        print(f"\n[{datetime.now()}] 🔍 Smart Scanner Running...")
        
        pairs = data.get('pairs', [])
        found_new = False
        
        for pair in pairs[:200]:
            base_token = pair.get('baseToken', {})
            name = base_token.get('name', 'Unknown')
            symbol = base_token.get('symbol', '???')
            contract_address = base_token.get('address', 'N/A')   # ← آدرس قرارداد
            price = pair.get('priceUsd', 'N/A')
            vol_24h = pair.get('volume', {}).get('h24', 0)
            liq = pair.get('liquidity', {}).get('usd', 0)
            created = pair.get('pairCreatedAt')
            pair_address = pair.get('pairAddress')
            
            if not created or not pair_address:
                continue
                
            token_key = pair_address
            if token_key in seen_tokens:
                continue
                
            age_min = int((time.time() * 1000 - created) / 60000)
            
            # ==================== SMART FILTER ====================
            is_new = age_min <= 60 and liq >= 4000
            is_high_volume = vol_24h >= 80000 and age_min <= 180
            
            if not (is_new or is_high_volume):
                continue
            
            seen_tokens.add(token_key)
            found_new = True
            dexscreener_link = f"https://dexscreener.com/base/{pair_address}"
            
            if is_new:
                status = "🚀 NEW LAUNCH"
            else:
                status = "🔥 HIGH VOLUME"
            
            print(f"\n{status} DETECTED!")
            print(f"   🪙 {name} (${symbol})")
            print(f"   📍 Contract: {
