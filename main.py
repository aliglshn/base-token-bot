import requests
import time
import os
from datetime import datetime

# Settings
CHECK_INTERVAL = 300  # Check every 5 minutes (in seconds)

def get_new_pairs_on_base():
    url = "https://api.dexscreener.com/latest/dex/pairs/base"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        print(f"\n[{datetime.now()}] New pairs on Base:")
        
        for pair in data.get('pairs', [])[:10]:  # First 10 pairs
            token_name = pair.get('baseToken', {}).get('name', 'Unknown')
            token_symbol = pair.get('baseToken', {}).get('symbol', '')
            price = pair.get('priceUsd', 'N/A')
            volume_24h = pair.get('volume', {}).get('h24', 0)
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            pair_age = pair.get('pairCreatedAt')
            
            print(f"🪙 {token_name} ({token_symbol}) | Price: ${price} | 24h Vol: ${volume_24h:,} | Liquidity: ${liquidity:,}")
    
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    print("🚀 Base Token Radar Bot Started...")
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
