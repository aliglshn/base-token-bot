import requests
import time
from datetime import datetime

# Settings
CHECK_INTERVAL = 300  # 5 minutes

def get_new_pairs_on_base():
    # New working method: Search for recent activity on Base
    url = "https://api.dexscreener.com/latest/dex/search?q=base"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        
        print(f"\n[{datetime.now()}] New / Active pairs on Base:")
        
        # Sort by newest or volume if possible
        pairs = data.get('pairs', [])[:15]  # Take more to have options
        
        for pair in pairs:
            base_token = pair.get('baseToken', {})
            token_name = base_token.get('name', 'Unknown')
            token_symbol = base_token.get('symbol', '')
            price = pair.get('priceUsd', 'N/A')
            volume_24h = pair.get('volume', {}).get('h24', 0)
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            created_at = pair.get('pairCreatedAt')
            
            age_text = ""
            if created_at:
                age_minutes = int((time.time() * 1000 - created_at) / 60000)
                age_text = f" | Age: {age_minutes} min"
            
            print(f"🪙 {token_name} ({token_symbol}) | Price: ${price} | Vol: ${volume_24h:,} | Liq: ${liquidity:,}{age_text}")
    
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    print("🚀 Base Token Radar Bot Started...")
    print("Using DexScreener search for Base chain...")
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
