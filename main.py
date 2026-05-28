import requests
import time
import os
from datetime import datetime
import threading

# ====================== CONFIG ======================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

BASED_TELEGRAM = "https://t.me/based_eth_bot?start=r_aliglshn1"
# ===================================================

seen_tokens = set()
top_tokens_24h = []   # ذخیره توکن‌های ترند ۲۴ ساعته

def send_message(chat_id, text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
        return True
    except:
        return False

def scan():
    global top_tokens_24h
    url = "https://api.geckoterminal.com/api/v2/networks/base/new_pools"
    
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        pools = data.get('data', [])
        
        current_top = []
        
        for pool in pools[:300]:
            attr = pool.get('attributes', {})
            name = attr.get('name', 'Unknown')
            contract = attr.get('address', 'N/A')
            vol = float(attr.get('volume_usd', {}).get('h24', 0) or 0)
            liq = float(attr.get('reserve_in_usd', 0) or 0)
            
            if vol < 30000 or liq < 8000:   # فیلتر مناسب برای ترند
                continue
                
            if contract in seen_tokens:
                continue
                
            seen_tokens.add(contract)
            
            link = f"https://www.geckoterminal.com/base/pools/{contract}"
            
            token_info = {
                'name': name,
                'contract': contract,
                'vol': vol,
                'liq': liq,
                'link': link
            }
            current_top.append(token_info)
            
            # آلرت خودکار برای توکن‌های خیلی قوی
            if vol >= 60000:
                msg = f"""<b>🔥 Trending Token on Base!</b>

🪙 {name}
📍 <code>{contract}</code>
📊 Vol 24h: ${vol:,.0f} | Liq: ${liq:,.0f}

🔗 <a href="{link}">GeckoTerminal</a>
💸 <a href="{BASED_TELEGRAM}">Trade with Based Bot</a>"""
                send_message(TELEGRAM_CHAT_ID, msg)
        
        # به‌روزرسانی لیست ترند
        top_tokens_24h = sorted(current_top, key=lambda x: x['vol'], reverse=True)[:10]
        
    except Exception as e:
        print(f"Scan Error: {e}")

def check_commands():
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
                
                if text in ['/trending', '/top', '/best', 'trending', 'top', 'best']:
                    if not top_tokens_24h:
                        send_message(chat_id, "⏳ هنوز توکن ترندی ثبت نشده. کمی صبر کن...")
                        continue
                    
                    msg = "<b>🏆 Trending Tokens on Base (Last 24h)</b>\n\n"
                    for i, t in enumerate(top_tokens_24h[:8], 1):
                        msg += f"{i}. <b>{t['name']}</b>\n"
                        msg += f"   Vol: ${t['vol']:,.0f} | Liq: ${t['liq']:,.0f}\n"
                        msg += f"   <a href='{t['link']}'>View</a>\n\n"
                    msg += f"💸 <a href='{BASED_TELEGRAM}'>Trade with Based Bot</a>"
                    send_message(chat_id, msg)
        except:
            time.sleep(5)

if __name__ == "__main__":
    print("🚀 Base Radar Bot Started with /trending Command")
    
    threading.Thread(target=check_commands, daemon=True).start()
    
    while True:
        scan()
        time.sleep(40)
