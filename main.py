import os
from datetime import datetime

print("🚀 Base Meme Radar Bot - Debug Mode")
print(f"Time: {datetime.now()}\n")

keys = ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_SECRET']

for key in keys:
    value = os.getenv(key)
    if value:
        print(f"✅ {key} = Loaded (length: {len(value)})")
    else:
        print(f"❌ {key} = MISSING")

print("\n" + "="*50)
print("اگر همه ✅ شد، توییتر باید کار کنه")
print("="*50)
