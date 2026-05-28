import requests
import time
import os
from datetime import datetime

# ====================== CONFIG ======================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

BASED_X = "https://x.com/basedbot"
BASED_TELEGRAM = "https://t.me/based_eth_bot?start=r_aliglshn1"
# ===================================================

CHECK_INTERVAL = 60
seen_tokens = set()

def is_honeypot(contract_address):
    """چک کردن honeypot با RugCheck API"""
    try:
        url = f"https://api.rugcheck.xyz/v1/tokens/{contract_address}/report"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            score = data.get('score', 0)
            is_honeypot_risk = data.get('isHoneypot', False) or score < 50
            return is_honeypot_risk, score
        return True, 0  # اگر خطا داد، احتیاطاً honeypot فرض کن
    except:
        return True, 0

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
        
        print(f"\n[{datetime.now()}] 🔍 Smart Scanner + Honeypot Check Running...")
        
        pairs = data.get('pairs', [])
        found_new = False
        
        for pair in pairs[:200]:
            base_token = pair.get('baseToken', {})
            name = base_token.get('name', 'Unknown')
            symbol = base_token.get('symbol', '???')
            contract_address = base_token.get('address', 'N/A')
            price = pair.get('priceUsd', 'N/A')
            vol_24h = pair.get('volume', {}).get('h24', 0)
            liq = pair.get('liquidity', {}).get('usd', 0)
            created = pair.get('pairCreatedAt')
            pair_address = pair.get('pairAddress')
            
            if not created or not pair_address or not contract_address:
                continue
                
            token_key = pair_address
            if token_key in seen_tokens:
                continue
                
            age_min = int((time.time() * 1000 - created) / 60000)
            
            is_new = age_min <= 90 and liq >= 3000
            is_high_volume = vol_24h >= 50000 and age_min <= 300
            
            if not (is_new or is_high_volume):
                continue
            
            # ==================== Honeypot Check ====================
            print(f"   Checking Honeypot for {symbol}...")
            honeypot_risk, score = is_honeypot(contract_address)
            if honeypot_risk:
                print(f"   ❌ Honeypot Risk Detected
