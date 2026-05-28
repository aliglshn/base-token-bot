import requests
import time
from datetime import datetime

# ====================== CONFIG ======================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')   # بعداً تو Railway اضافه می‌کنیم
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')       # Chat ID خودت

CHECK_INTERVAL = 90
# ===================================================

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("📝 [LOG] Telegram not configured:", text[:100])
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Telegram Alert Sent!")
            return True
        else:
            print(f"❌ Telegram Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Telegram Failed: {e}")
        return False

def get_new_pairs_on_base():
    url = "https://api.dexscreener.com/latest/dex/search?q=base"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        print(f"\n[{datetime.now()}] 🔍 Scanning for new memes on Base...")
        
        pairs = data.get('pairs', [])
        found = False
        
        for pair in pairs[:100]:
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
            
            if age_min > 90 or liq < 6000 or vol < 600:
                continue
                
            found = True
            link = f"https://dexscreener.com/base/{address}"
            
            print(f"\n🚀 NEW MEME DETECTED!")
            print(f"   🪙 {name} (${symbol}) | Age: {age_min} min")
            print(f"   🔗 {link}")
            
            # ارسال به تلگرام
            message = f"""🚀 <b>New Meme on Base!</b>

🪙 <b>{name}</b> (${symbol})
💰 Price: ${price}
📊 Liq: ${liq:,} | Vol: ${vol:,}
⏱️ {age_min} minutes old

🔗 {link}

#Base #Memecoin"""
            
            send_telegram_message(message)
            print("-" * 70)
        
        if not found:
            print("⏳ No new interesting memes right now.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Base Meme Radar Bot Started with Telegram Alerts")
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
