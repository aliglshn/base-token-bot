import requests
import time
import os
from datetime import datetime

# ====================== TELEGRAM CONFIG ======================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# ===========================================================

CHECK_INTERVAL = 60

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
        
        print(f"\n[{datetime.now()}] 🔍 Smart Scanner - New + High Volume Tokens...")
        
        pairs = data.get('pairs', [])
        found = False
        
        for pair in pairs[:200]:
            base_token = pair.get('baseToken', {})
            name = base_token.get('name', 'Unknown')
            symbol = base_token.get('symbol', '???')
            price = pair.get('priceUsd', 'N/A')
            vol_24h = pair.get('volume', {}).get('h24', 0)
            liq = pair.get('liquidity', {}).get('usd', 0)
            created = pair.get('pairCreatedAt')
            address = pair.get('pairAddress')
            
            if not created or not address:
                continue
                
            age_min = int((time.time() * 1000 - created) / 60000)
            
            # ==================== SMART FILTER ====================
            is_new = age_min <= 60 and liq >= 3000
            is_high_volume = vol_24h >= 50000   # توکن‌هایی که حجم خیلی خوبی می‌خورن
            
            if not (is_new or is_high_volume):
                continue
            # ====================================================
            
            found = True
            link = f"https://dexscreener.com/base/{address}"
            
            if is_new:
                status = "🚀 NEW LAUNCH"
            else:
                status = "🔥 HIGH VOLUME"
            
            print(f"\n{status} DETECTED!")
            print(f"   🪙 {name} (${symbol}) | Age: {age_min} min")
            print(f"   💰 Price: ${price} | Liq: ${liq:,} | 24h Vol: ${vol_24h:,}")
            print(f"   🔗 {link}")
            
            message = f"""<b>{status} on Base!</b>

🪙 <b>{name}</b> (${symbol})
💰 Price: ${price}
📊 Liquidity: ${liq:,}
📈 24h Volume: ${vol_24h:,}
⏱️ {age_min} minutes old

🔗 <a href="{link}">DexScreener</a>

#Base #Memecoin"""
            
            send_telegram_message(message)
            print("-" * 80)
        
        if not found:
            print("⏳ No new or high-volume tokens right now...")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Base Meme Radar Bot - SMART MODE")
    print("Detecting New Launches + High Volume Tokens")
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
