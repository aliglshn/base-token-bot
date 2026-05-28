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
trending_tokens = []  # برای دستور /trending

def send_message(chat_id, text):
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
        return True
    except:
        return False

def scan():
    global trending_tokens
    url = "https://api.geckoterminal.com/api/v2/networks/base/new_pools"
    
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        pools = data.get('data', [])
        
        print(f"\n[{datetime.now()}] Scanning for strong tokens...")
        
        current_trending = []
        
        for pool in pools[:300]:
            attr = pool.get('attributes', {})
            name = attr.get('name', 'Unknown')
            contract = attr.get('address', 'N/A')
            vol = float(attr.get('volume_usd', {}).get('h24', 0) or 0)
            liq = float(attr.get('reserve_in_usd', 0) or 0)
            
            if not contract:
                continue
                
            # محاسبه سن
            age_min = 9999
            created_str = attr.get('pool_created_at')
            if created_str:
                try:
                    created_str = created_str.replace('Z', '').split('.')[0]
                    created_time = datetime.fromisoformat(created_str)
                    age_min = int((datetime.utcnow() - created_time).total_seconds() / 60)
                except:
                    pass
            
            token_info = {
                'name': name,
                'contract': contract,
                'vol': vol,
                'liq': liq,
                'age': age_min,
                'link': f"https://www.geckoterminal.com/base/pools/{contract}"
            }
            
            current_trending.append(token_info)
            
            # آلرت خودکار برای توکن‌های قوی
            if vol >= 45000 and liq >= 10000 and contract not in seen_tokens:
                seen_tokens.add(contract)
                msg = f"""<b>🔥 Strong Token on Base!</b>

🪙 {name}
📍 <code>{contract}</code>
📊 Vol 24h: ${vol:,.0f} | Liq: ${liq:,.0f}
⏱️ {age_min} min

🔗 <a href="{token_info['link']}">GeckoTerminal</a>
💸 <a href="{BASED_TELEGRAM}">Trade with Based Bot</a>"""
                send_message(TELEGRAM_CHAT_ID, msg)
        
        # به‌روزرسانی لیست ترند
        trending_tokens = sorted(current_trending, key=lambda x: x['vol'], reverse=True)[:12]
        
    except Exception as e:
        print(f"Scan Error: {e}")

def handle_commands():
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
                
                if text in ['/trending', '/top', '/best']:
                    if not trending_tokens:
                        send_message(chat_id, "⏳ هنوز توکن ترندی ثبت نشده. کمی صبر کن...")
                        continue
                    
                    msg = "<b>🏆 Trending Tokens on Base (Last 24h)</b>\n\n"
                    for i, t in enumerate(trending_tokens[:8], 1):
                        msg += f"{i}. <b>{t['name']}</b>\n"
                        msg += f"   Vol: ${t['vol']:,.0f} | Liq: ${t['liq']:,.0f} | Age: {t['age']} min\n"
                        msg += f"   <a href='{t['link']}'>View Chart</a>\n\n"
                    msg += f"💸 <a href='{BASED_TELEGRAM}'>Trade with Based Bot</a>"
                    send_message(chat_id, msg)
                
                elif text == '/help':
                    send_message(chat_id, """<b>🤖 Base Radar Bot Commands</b>

• /trending - Top trending tokens
• /top - Same as trending
• /best - Same as trending
• /help - Show this menu""")
        except:
            time.sleep(5)

if __name__ == "__main__":
    print("🚀 Professional Base Radar Bot Started")
    print("Commands: /trending | /top | /best | /help")
    
    threading.Thread(target=handle_commands, daemon=True).start()
    
    while True:
        scan()
        time.sleep(40)
