import requests
import time
from datetime import datetime

CHECK_INTERVAL = 180  # چک هر ۳ دقیقه

def get_new_pairs_on_base():
    url = "https://api.dexscreener.com/latest/dex/search?q=base"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n[{datetime.now()}] Scanning Base pairs...")
        
        pairs = data.get('pairs', [])
        new_pairs_found = False
        
        # Filter and sort by age (newest first)
        for pair in pairs[:30]:  # Check more to find new ones
            base_token = pair.get('baseToken', {})
            token_name = base_token.get('name', 'Unknown')
            token_symbol = base_token.get('symbol', '')
            price = pair.get('priceUsd', 'N/A')
            volume_24h = pair.get('volume', {}).get('h24', 0)
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            pair_created_at = pair.get('pairCreatedAt')
            
            if not pair_created_at:
                continue
                
            # Calculate age in minutes
            age_minutes = int((time.time() * 1000 - pair_created_at) / 60000)
            
            # Only show pairs younger than 60 minutes (or low liquidity new ones)
            if age_minutes > 60 and liquidity < 50000:
                continue
                
            new_pairs_found = True
            print(f"🆕 {token_name} ({token_symbol}) | Price: ${price} | Vol: ${volume_24h:,} | Liq: ${liquidity:,} | Age: {age_minutes} min")
        
        if not new_pairs_found:
            print("No new pairs under 60 minutes found right now.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Base Token Radar Bot Started (Improved Filter)...")
    print("Looking for new pairs on Base...")
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
