import requests
import time
from datetime import datetime

CHECK_INTERVAL = 120  # چک هر ۲ دقیقه

def get_new_pairs_on_base():
    url = "https://api.dexscreener.com/latest/dex/search?q=base"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n[{datetime.now()}] 🔍 Scanning for NEW pairs on Base...")
        
        pairs = data.get('pairs', [])
        found_recent = False
        
        for pair in pairs[:50]:  # چک تعداد بیشتر
            base_token = pair.get('baseToken', {})
            token_name = base_token.get('name', 'Unknown')
            token_symbol = base_token.get('symbol', '???')
            price = pair.get('priceUsd', 'N/A')
            volume_24h = pair.get('volume', {}).get('h24', 0)
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            pair_created_at = pair.get('pairCreatedAt')
            
            if not pair_created_at:
                continue
                
            age_minutes = int((time.time() * 1000 - pair_created_at) / 60000)
            
            # فیلتر خیلی سخت: فقط توکن‌های خیلی جدید
            if age_minutes > 60:  # حداکثر ۱ ساعت
                continue
            if liquidity < 5000:  # حداقل لیکوییدیتی
                continue
                
            found_recent = True
            print(f"🚀 NEW MEME! {token_name} ({token_symbol})")
            print(f"   Price: ${price} | Vol 24h: ${volume_24h:,} | Liq: ${liquidity:,} | Age: {age_minutes} min")
            print(f"   Link: https://dexscreener.com/base/{pair.get('pairAddress')}")
            print("-" * 60)
        
        if not found_recent:
            print("⏳ No new pairs (under 60 min + good liquidity) found right now.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Base Token Radar Bot - Strict New Meme Filter")
    print("Only showing pairs < 60 minutes old with decent liquidity")
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
