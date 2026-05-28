import os
from datetime import datetime

print("=== RAILWAY VARIABLES DEBUG ===")
vars_to_check = ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_SECRET']

for v in vars_to_check:
    value = os.getenv(v)
    status = "✅ Exists (length: " + str(len(value)) + ")" if value else "❌ MISSING"
    print(f"{v}: {status}")

print("==================================\n")
print(f"Bot started at: {datetime.now()}")
