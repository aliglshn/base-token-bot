import os
from datetime import datetime

print("=== ENVIRONMENT VARIABLES CHECK ===")
print("TWITTER_API_KEY:", "✅ Exists" if os.getenv('TWITTER_API_KEY') else "❌ MISSING")
print("TWITTER_API_SECRET:", "✅ Exists" if os.getenv('TWITTER_API_SECRET') else "❌ MISSING")
print("TWITTER_ACCESS_TOKEN:", "✅ Exists" if os.getenv('TWITTER_ACCESS_TOKEN') else "❌ MISSING")
print("TWITTER_ACCESS_SECRET:", "✅ Exists" if os.getenv('TWITTER_ACCESS_SECRET') else "❌ MISSING")
print("==================================\n")

print(f"Bot started at: {datetime.now()}")
print("If all are ✅, Twitter should work.")
