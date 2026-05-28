import requests
import time
import os
from datetime import datetime

# ====================== TELEGRAM CONFIG ======================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# ===========================================================

CHECK_INTERVAL = 75   # چک هر ۷۵ ثانیه

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
        
        print(f"\n[{datetime.now()}] 🔍 Light Filter Scan - Looking for potential launches...")
        
        pairs = data.get('pairs', [])
        found = False
        
        for pair in pairs[:150]:
            base_token = pair.get('baseToken', {})
            name = base_token.get('name', 'Unknown')
            symbol = base_token.get('symbol', '???')
            price = pair.get('priceUsd', 'N/A')
            vol = pair.get('volume', {}).get('h24', 0)
            liq = pair.get('liquidity', {}).get('usd', 0)
            created = pair.get('pairCreatedAt')
            address = pair.get('pairAddress')
            
            if not created or not address:
                continue
                
            age_min = int((time.time() * 1000 - created) / 60000)
            
            # ==================== LIGHT FILTER ====================
            if age_min > 75:           # حداکثر ۷۵ دقیقه
                continue
            if liq < 5000:             # حداقل لیکوییدیتی
                continue
            if vol < 1000:             # حداقل ولوم
                continue
            # ====================================================
            
            found = True
            link = f"https://dexscreener.com/base/{address}"
            
            print(f"\n🚀 POTENTIAL NEW MEME!")
            print(f"   🪙 {name} (${symbol}) | Age: {age_min} min")
            print(f"   💰 Price: ${price} | Liq: ${liq:,} | Vol: ${vol:,}")
            print(f"   🔗 {link}")
            
            message = f"""🚀 <b>Potential New Meme on Base</b>

🪙 <b>{name}</b> (${symbol})
💰 Price: ${price}
📊 Liq: ${liq:,} | Vol: ${vol:,}
⏱️ {age_min} minutes old

🔗 <a href="{link}">View on DexScreener</a>

#Base #Memecoin"""
            
            send_telegram_message(message)
            print("-" * 80)
        
        if not found:
            print("⏳ No potential memes right now...")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Base Meme Radar Bot - LIGHT FILTER Mode")
    print("Age < 75min | Liq > 5k | Vol > 1k")
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
