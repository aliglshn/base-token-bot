import requests
import time
import os
from datetime import datetime
import threading

# ====================== CONFIG ======================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

BASED_X = "https://x.com/basedbot"
BASED_TELEGRAM = "https://t.me/based_eth_bot?start=r_aliglshn1"

CHECK_INTERVAL = 45   # سریع‌تر
# ===================================================

seen_tokens = set()
top_tokens_24h = []

def send_telegram_message(chat_id, text):
    if not TELEGRAM_BOT_TOKEN:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
        return True
    except:
        return False

def get_new_pairs_on_base():
    global top_tokens_24h
    # استفاده از GeckoTerminal API (بهتر از DexScreener)
    url = "https://api.geckoterminal.com/api/v2/networks/base/new_pools"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        pools = data.get('data', [])
        
        print(f"\n[{datetime.now()}] 🔍 GeckoTerminal Scanner Running...")
        
        current_top = []
        found_new = False
        
        for pool in pools[:150]:
            attributes = pool.get('attributes', {})
            name = attributes.get('name', 'Unknown')
            symbol = name.split('/')[0] if '/' in name else '???'
            contract = attributes.get('address', 'N/A')  # pool address
            vol = attributes.get('volume_usd', {}).get('h24', 0)
            liq = attributes.get('reserve_in_usd', 0)
            age_ms = attributes.get('pool_created_at')
            
            if not age_ms:
                continue
                
            age_min = int((time.time() * 1000 - age_ms) / 60000)
            
            token_info = {
                'name': name,
                'symbol': symbol,
                'contract': contract,
                'vol': vol,
                'liq': liq,
                'age': age_min,
                'link': f"https://www.geckoterminal.com/base/pools/{contract}"
            }
            
            current_top.append(token_info)
            
            # آلرت
            if (age_min <= 60 and liq >= 3000) or vol >= 40000:
                if contract not in seen_tokens:
                    seen_tokens.add(contract)
                    status = "🚀 NEW" if age_min <= 60 else "🔥 HIGH VOL"
                    msg = f"""<b>{status} on Base!</b>

🪙 {name}
📍 <code>{contract}</code>
📊 Vol 24h: ${vol:,} | Liq: ${liq:,}
⏱️ {age_min} min

🔗 <a href="{token_info['link']}">GeckoTerminal</a>

💸 <a href="{BASED_TELEGRAM}">Trade with Based Bot</a>"""
                    send_telegram_message(TELEGRAM_CHAT_ID, msg)
                    found_new = True
        
        top_tokens_24h = sorted(current_top, key=lambda x: x['vol'], reverse=True)[:10]
        
        if not found_new:
            print("⏳ No good tokens right now...")
            
    except Exception as e:
        print(f"Error: {e}")

# ==================== /top Command ====================
def check_telegram_commands():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={offset}&timeout=10"
            resp = requests.get(url, timeout=15)
            updates = resp.json().get('result', [])
            
            for update in updates:
                offset = update['update_id'] + 1
                if 'message' not in update:
                    continue
                    
                chat_id = update['message']['chat']['id']
                text = update['message'].get('text', '').strip().lower()
                
                if text in ['/top', '/best', 'top', 'best']:
                    if not top_tokens_24h:
                        send_telegram_message(chat_id, "⏳ هنوز اطلاعات کافی جمع نشده...")
                        continue
                    
                    msg = "<b>🏆 بهترین توکن‌های ۲۴ ساعت (GeckoTerminal)</b>\n\n"
                    for i, t in enumerate(top_tokens_24h[:8], 1):
                        msg += f"{i}. <b>{t['name']}</b>\n   Vol: ${t['vol']:,} | Liq: ${t['liq']:,}\n   <a href='{t['link']}'>Link</a>\n\n"
                    msg += f"💸 <a href='{BASED_TELEGRAM}'>Trade Now</a>"
                    send_telegram_message(chat_id, msg)
        except:
            time.sleep(5)

if __name__ == "__main__":
    print("🚀 Base Meme Radar Bot - GeckoTerminal + /top Command")
    
    threading.Thread(target=check_telegram_commands, daemon=True).start()
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
