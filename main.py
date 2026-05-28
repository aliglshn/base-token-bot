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

CHECK_INTERVAL = 45
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
    url = "https://api.geckoterminal.com/api/v2/networks/base/new_pools"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        pools = data.get('data', [])
        
        print(f"\n[{datetime.now()}] 🔍 High Volume + High Liq Scanner (Min 50k Vol | 10k Liq)")
        
        current_top = []
        
        for pool in pools[:250]:
            attributes = pool.get('attributes', {})
            name = attributes.get('name', 'Unknown')
            symbol = name.split('/')[0] if '/' in name else '???'
            contract = attributes.get('address', 'N/A')
            vol = float(attributes.get('volume_usd', {}).get('h24', 0) or 0)
            liq = float(attributes.get('reserve_in_usd', 0) or 0)
            
            # محاسبه سن
            created_str = attributes.get('pool_created_at')
            age_min = 9999
            if created_str:
                try:
                    created_str = created_str.replace('Z', '')
                    if '.' in created_str:
                        created_str = created_str.split('.')[0]
                    created_time = datetime.fromisoformat(created_str)
                    age_min = int((datetime.utcnow() - created_time).total_seconds() / 60)
                except:
                    pass
            
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
            
            # فیلتر نهایی: ولوم بالای ۵۰k + لیکوییدیتی بالای ۱۰k
            if vol >= 50000 and liq >= 10000:
                if contract not in seen_tokens:
                    seen_tokens.add(contract)
                    status = "🚀 NEW + STRONG" if age_min <= 90 else "🔥 HIGH VOLUME"
                    msg = f"""<b>{status} on Base!</b>

🪙 {name}
📍 <code>{contract}</code>
📊 Vol 24h: ${vol:,.0f} | Liq: ${liq:,.0f}
⏱️ {age_min} min

🔗 <a href="{token_info['link']}">GeckoTerminal</a>

💸 <a href="{BASED_TELEGRAM}">Trade with Based Bot</a>"""
                    send_telegram_message(TELEGRAM_CHAT_ID, msg)
        
        top_tokens_24h = sorted(current_top, key=lambda x: x['vol'], reverse=True)[:10]
        
    except Exception as e:
        print(f"Error: {e}")

# /top Command
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
                    
                    msg = "<b>🏆 بهترین توکن‌های ۲۴ ساعت گذشته</b>\n\n"
                    for i, t in enumerate(top_tokens_24h[:8], 1):
                        msg += f"{i}. <b>{t['name']}</b>\n   Vol: ${t['vol']:,.0f} | Liq: ${t['liq']:,.0f} | Age: {t['age']} min\n   <a href='{t['link']}'>Link</a>\n\n"
                    msg += f"💸 <a href='{BASED_TELEGRAM}'>Trade with Based Bot</a>"
                    send_telegram_message(chat_id, msg)
        except:
            time.sleep(5)

if __name__ == "__main__":
    print("🚀 Base Meme Radar Bot - High Volume + High Liquidity (50k Vol | 10k Liq)")
    
    threading.Thread(target=check_telegram_commands, daemon=True).start()
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
