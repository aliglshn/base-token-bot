import os
import tweepy
from datetime import datetime

print("🚀 Base Meme Radar Bot Started")

# Debug
print("API_KEY loaded:", bool(os.getenv('TWITTER_API_KEY')))
print("ACCESS_TOKEN loaded:", bool(os.getenv('TWITTER_ACCESS_TOKEN')))

client = tweepy.Client(
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
)

print("✅ Twitter Client Created")

test_tweet = f"""🧪 Test Tweet from Base Meme Radar Bot
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Bot is live! 🚀 #Base"""

try:
    response = client.create_tweet(text=test_tweet)
    print(f"✅ Tweet Posted Successfully! ID: {response.data['id']}")
except Exception as e:
    print(f"❌ Tweet Error: {e}")
