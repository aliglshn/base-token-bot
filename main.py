import requests
import time
from datetime import datetime

CHECK_INTERVAL = 120  # Check every 2 minutes

def get_new_pairs_on_base():
    url = "https://api.dexscreener.com/latest/dex/search?q=base"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n[{datetime.now()}] 🔍 Scanning for new pairs on Base...")
        
        pairs = data.get('pairs', [])
        recent_found = False
        
        for pair in pairs[:60]:
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
            
            # Strict filter: only very new tokens
            if age_minutes > 30:
                continue
            if liquidity < 8000:
                continue
            if volume_24h < 1000:
                continue
                
            recent_found = True
            print(f"🚀 FOUND NEW MEME COIN!")
            print(f"   🪙 {token_name} ({token_symbol})")
            print(f"   💰 Price: ${price}")
            print(f"   📊 Vol 24h: ${volume_24h:,} | Liq: ${liquidity:,}")
            print(f"   ⏱️ Age: {age_minutes} minutes")
            print(f"   🔗 https://dexscreener.com/base/{pair.get('pairAddress')}")
            print("-" * 70)
        
        if not recent_found:
            print("⏳ No new high-quality pairs found in the last 30 minutes.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Base Meme Radar Bot - STRICT NEW FILTER")
    print("Only showing tokens under 30 minutes old with good liquidity")
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
