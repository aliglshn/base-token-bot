import requests
import time
import os
from datetime import datetime, timedelta
import threading

# ====================== CONFIG ======================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')  # چت آیدی اصلی شما

BASED_X = "https://x.com/basedbot"
BASED_TELEGRAM = "https://t.me/based_eth_bot?start=r_aliglshn1"
# ===================================================

seen_tokens = set()
top_tokens_24h = []  # ذخیره توکن‌های برتر ۲۴ ساعت

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
        return True
    except:
        return False

def get_new_pairs_on_base():
    global top_tokens_24h
    url = "https://api.dexscreener.com/latest/dex/search?q=base"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        pairs = data.get('pairs', [])
        
        current_time = datetime.now()
        new_top = []
        
        for pair in pairs[:300]:
            base_token = pair.get('baseToken', {})
            name = base_token.get('name', 'Unknown')
            symbol = base_token.get('symbol', '???')
            contract = base_token.get('address', 'N/A')
            vol = pair.get('volume', {}).get('h24', 0)
            liq = pair.get('liquidity', {}).get('usd', 0)
            created = pair.get('pairCreatedAt')
            pair_address = pair.get('pairAddress')
            
            if not pair_address or vol < 10000:
                continue
                
            age_min = int((time.time() * 1000 - created) / 60000) if created else 9999
            
            token_info = {
                'name': name,
                'symbol': symbol,
                'contract': contract,
                'vol': vol,
                'liq': liq,
                'age': age_min,
                'link': f"https://dexscreener.com/base/{pair_address}"
            }
            
            new_top.append(token_info)
            
            # ارسال آلرت معمولی برای توکن‌های خوب
            if (age_min <= 90 and liq >= 5000) or vol >= 80000:
                if pair_address not in seen_tokens:
                    seen_tokens.add(pair_address)
                    status = "🚀 NEW" if age_min <= 90 else "🔥 HIGH VOL"
                    message = f"""<b>{status} on Base!</b>

🪙 {name} (${symbol})
📍 <code>{contract}</code>
📊 Vol: ${vol:,} | Liq: ${liq:,}
⏱️ {age_min} min

🔗 <a href="{token_info['link']}">DexScreener</a>

💸 <a href="{BASED_TELEGRAM}">Trade with Based Bot</a>"""
                    send_telegram_message(TELEGRAM_CHAT_ID, message)
        
        # مرتب‌سازی ۱۰ توکن برتر ۲۴ ساعت
        top_tokens_24h = sorted(new_top, key=lambda x: x['vol'], reverse=True)[:10]
        
    except Exception as e:
        print(f"Error: {e}")

# ==================== هندل دستورات تلگرام ====================
def handle_telegram_commands():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            resp = requests.get(url, timeout=40)
            updates = resp.json().get('result', [])
            
            for update in updates:
                offset = update['update_id'] + 1
                if 'message' not in update:
                    continue
                    
                chat_id = update['message']['chat']['id']
                text = update['message'].get('text', '').strip().lower()
                
                if text in ['/top', '/best', 'top', 'best']:
                    if not top_tokens_24h:
                        send_telegram_message(chat_id, "⏳ هنوز توکنی ثبت نشده. کمی صبر کنید...")
                        continue
                    
                    msg = "<b>🏆 بهترین توکن‌های ۲۴ ساعت گذشته (بر اساس Volume)</b>\n\n"
                    for i, t in enumerate(top_tokens_24h[:8], 1):
                        msg += f"{i}. <b>{t['name']}</b> (${t['symbol']})\n"
                        msg += f"   Vol: ${t['vol']:,} | Liq: ${t['liq']:,}\n"
                        msg += f"   <a href='{t['link']}'>DexScreener</a>\n\n"
                    
                    msg += f"\n💸 <a href='{BASED_TELEGRAM}'>Trade with Based Bot</a>"
                    send_telegram_message(chat_id, msg)
                    
        except:
            time.sleep(5)

if __name__ == "__main__":
    print("🚀 Base Meme Radar Bot Started with /top Command")
    
    # شروع Thread برای دریافت دستورات تلگرام
    threading.Thread(target=handle_telegram_commands, daemon=True).start()
    
    while True:
        get_new_pairs_on_base()
        time.sleep(CHECK_INTERVAL)
