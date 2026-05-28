import requests
import time
from datetime import datetime

CHECK_INTERVAL = 180  # every 3 minutes

def get_new_pairs_on_base():
    url = "https://api.dexscreener.com/latest/dex/search?q=base"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n[{datetime.now()}] Scanning for new pairs on Base...")
        
        pairs = data.get('pairs', [])
        new_found = False
        
        for pair in pairs[:40]:  
            base_token = pair.get('baseToken', {})
            token_name = base_token.get('name', 'Unknown')
            token_symbol = base_token.get('symbol', '')
            price = pair.get('priceUsd', 'N/A')
            volume_24h = pair.get('volume', {}).get('h24', 0)
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            pair_created_at = pair.get('pairCreatedAt')
            
            if not pair_created_at:
                continue
                
            age_minutes = int((time.time() * 1000 - pair_created_at) / 60000)
            
            # فقط توکن‌های نسبتاً جدید یا با لیکوییدیتی خوب
            if age_minutes > 120 and liquidity < 10000:
                continue
                
            new_found = True
            print(f"🆕 {token_name} ({token_symbol}) | Price: ${price} | Vol: ${volume_24h:,} | Liq: ${liquidity:,} | Age: {age_minutes} min")
        
        if not new_found:
            print("No recent interesting pairs found at the moment.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Base Token Radar Bot Started - Improved Version")
    print("Filtering new and active pairs...")
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
