import os
import tweepy
from datetime import datetime

# Twitter Setup
client = tweepy.Client(
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
)

print("✅ Twitter Connected!")

# تست توییت
test_tweet = f"""🧪 Test Tweet from Base Meme Radar Bot

This is a test.
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Bot is working correctly! 🚀"""

try:
    response = client.create_tweet(text=test_tweet)
    print(f"✅ Test Tweet Posted Successfully!")
    print(f"Tweet ID: {response.data['id']}")
except Exception as e:
    print(f"❌ Error posting test tweet: {e}")
