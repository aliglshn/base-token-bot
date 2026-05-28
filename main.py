import requests
import time
import os
from datetime import datetime
import tweepy

# ====================== TWITTER SETUP ======================
client = None
try:
    client = tweepy.Client(
        consumer_key=os.getenv('TWITTER_API_KEY'),
        consumer_secret=os.getenv('TWITTER_API_SECRET'),
        access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
    )
    print("✅ Twitter Connected Successfully!")
except Exception as e:
    print(f"⚠️ Twitter connection failed: {e}")

CHECK_INTERVAL = 120  # 2 minutes

def post_to_twitter(message):
    if not client:
        print("❌ Twitter client not ready")
        return False
    try:
        response = client.create_tweet(text=message)
        print(f"✅ Tweet Posted! ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"❌ Failed to post tweet: {e}")
        return False

def get_new_pairs_on_base():
    url = "https://api.dexscreener.com/latest/dex/search?q=base"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n[{datetime.now()}] 🔍 Scanning for new Base memes...")
        
        pairs = data.get('pairs', [])
        found_new = False
        
        for pair in pairs[:80]:
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
            
            # Strict filter for good new memes
            if age_minutes > 45 or liquidity < 10000 or volume_24h < 800:
                continue
                
            found_new = True
            link = f"https://dexscreener.com/base/{pair_address}"
            
            print(f"🚀 NEW MEME FOUND: {token_name} ({token_symbol})")
            
            tweet_text = f"""🚀 New Meme Coin on Base!

🪙 {token_name} (${token_symbol})
💰 Price: ${price}
📊 Liquidity: ${liquidity:,}
📈 24h Vol: ${volume_24h:,}
⏱️ Age: {age_minutes} min

🔗 {link}

#Base #Memecoin #Crypto"""

            post_to_twitter(tweet_text)
            print("-" * 70)
        
        if not found_new:
            print("⏳ No new high-quality memes right now.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Base Meme Radar Bot Started with Twitter Posting")
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
