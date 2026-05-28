import requests
import time
from datetime import datetime

CHECK_INTERVAL = 90  # چک هر ۱.۵ دقیقه

def get_new_pairs_on_base():
    url = "https://api.dexscreener.com/latest/dex/search?q=base"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n[{datetime.now()}] 🔍 Scanning for new memes on Base...")
        
        pairs = data.get('pairs', [])
        found_new = False
        
        for pair in pairs[:100]:
            base_token = pair.get('baseToken', {})
            token_name = base_token.get('name', 'Unknown')
            token_symbol = base_token.get('symbol', '???')
            price = pair.get('priceUsd', 'N/A')
            volume_24h = pair.get('volume', {}).get('h24', 0)
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            pair_created_at = pair.get('pairCreatedAt')
            pair_address = pair.get('pairAddress')
            
            if not pair_created_at or not pair_address:
                continue
                
            age_minutes = int((time.time() * 1000 - pair_created_at) / 60000)
            
            # فیلتر خوب برای میم‌کوین جدید
            if age_minutes > 60 or liquidity < 8000 or volume_24h < 1000:
                continue
                
            found_new = True
            link = f"https://dexscreener.com/base/{pair_address}"
            
            print(f"\n🚀 NEW MEME DETECTED!")
            print(f"   🪙 {token_name} (${token_symbol})")
            print(f"   💰 Price: ${price}")
            print(f"   📊 Liquidity: ${liquidity:,} | 24h Vol: ${volume_24h:,}")
            print(f"   ⏱️ Age: {age_minutes} minutes")
            print(f"   🔗 {link}")
            print("-" * 80)
        
        if not found_new:
            print("⏳ No new high-quality memes found right now.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Base Meme Radar Bot Started (Logging Mode)")
    print("Will only log new memes - No tweeting for now")
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
