import os
from datetime import datetime

print("=== FULL ENVIRONMENT DEBUG ===")
print("All Environment Variables:\n")

# Print all variables that start with TWITTER
for key, value in os.environ.items():
    if 'TWITTER' in key:
        length = len(value) if value else 0
        print(f"{key}: {'✅ Exists (len: ' + str(length) + ')' if value else '❌ MISSING'}")

print("\n=== SUMMARY ===")
print(f"Total TWITTER variables found: {sum(1 for k in os.environ if 'TWITTER' in k)}")
print(f"Time: {datetime.now()}")
print("================================")
