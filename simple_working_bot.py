#!/usr/bin/env python3
import requests
import time
import ccxt
import os
from datetime import datetime

# Direct configuration - no environment dependencies
TOKEN = "8429171890:AAEaYGGQb8L-pir22rt128g5hbh6GTuWDqk"
CHAT_ID = "1762317382"

OKX_API_KEY = "bfee3fff-cdf1-4b71-9ef9-8760de8732f4"
OKX_SECRET = "E7C2058E8DC095D3F45F5C37D6A28DC8"
OKX_PASSPHRASE = "Okx123#"

PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "DOGE/USDT"]

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        response = requests.post(url, json={"chat_id": CHAT_ID, "text": message}, timeout=10)
        success = response.status_code == 200
        print(f"Telegram: {success} (Status: {response.status_code})")
        return success
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def get_portfolio():
    try:
        exchange = ccxt.okx({
            'apiKey': OKX_API_KEY,
            'secret': OKX_SECRET,
            'password': OKX_PASSPHRASE,
            'sandbox': False
        })
        
        response = exchange.private_get_account_balance()
        total = 0
        
        if response.get('code') == '0':
            details = response.get('data', [{}])[0].get('details', [])
            for detail in details:
                amount = float(detail.get('cashBal', 0))
                symbol = detail.get('ccy', '')
                if amount > 0.001:
                    if symbol == 'USDT':
                        total += amount
                    else:
                        try:
                            ticker = exchange.fetch_ticker(f'{symbol}/USDT')
                            total += amount * ticker['last']
                        except:
                            pass
        return total
    except Exception as e:
        print(f"Portfolio error: {e}")
        return 0

def analyze_pairs():
    try:
        exchange = ccxt.okx({
            'apiKey': OKX_API_KEY,
            'secret': OKX_SECRET,
            'password': OKX_PASSPHRASE,
            'sandbox': False
        })
        
        results = []
        for pair in PAIRS:
            try:
                ticker = exchange.fetch_ticker(pair)
                change = ticker.get('percentage', 0)
                confidence = 50 + abs(change) * 8
                results.append({
                    'pair': pair,
                    'change': change,
                    'confidence': int(min(90, confidence))
                })
            except Exception as e:
                print(f"Error with {pair}: {e}")
        
        results.sort(key=lambda x: x['confidence'], reverse=True)
        return results
    except Exception as e:
        print(f"Analysis error: {e}")
        return []

def main():
    print("Starting simple working bot...")
    
    # Send startup message
    startup_msg = f"""🟢 SIMPLE BOT RESTARTED

✅ Status: Online and operational
📊 Monitoring: 6 major pairs
🔄 Frequency: Every 60 seconds
💰 Portfolio tracking: Active

⏰ Started: {datetime.now().strftime('%H:%M:%S UTC')}

Testing messaging and analysis..."""
    
    if not send_telegram(startup_msg):
        print("Failed to send startup message")
        return
    
    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"\n=== CYCLE {cycle} ===")
            
            # Get data
            portfolio = get_portfolio()
            opportunities = analyze_pairs()
            
            print(f"Portfolio: ${portfolio:.2f}")
            print(f"Opportunities: {len(opportunities)}")
            
            if opportunities:
                best = opportunities[0]
                
                msg = f"""📊 MARKET SCAN #{cycle}

🔍 Analysis Complete:
• Portfolio: ${portfolio:.2f} USDT
• Pairs Scanned: {len(PAIRS)}

📈 Top 3 Opportunities:"""

                for i, opp in enumerate(opportunities[:3], 1):
                    emoji = "🟢" if opp['change'] > 0 else "🔴"
                    msg += f"""
{i}. {emoji} {opp['pair']}: {opp['confidence']}% ({opp['change']:+.1f}%)"""
                
                msg += f"""

🎯 Best: {best['pair']} ({best['confidence']}%)
⏰ {datetime.now().strftime('%H:%M:%S UTC')}

Next scan in 60 seconds..."""
                
                success = send_telegram(msg)
                print(f"Sent scan results: {success}")
            else:
                error_msg = f"❌ SCAN #{cycle} FAILED\n\nNo market data available\n\n⏰ {datetime.now().strftime('%H:%M:%S UTC')}"
                send_telegram(error_msg)
                print("No opportunities found")
            
            # Sleep 60 seconds
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("Bot stopped by user")
        send_telegram("🔴 SIMPLE BOT STOPPED\n\nManual intervention")
    except Exception as e:
        print(f"Bot error: {e}")
        send_telegram(f"⚠️ BOT ERROR\n\n{str(e)[:100]}...")

if __name__ == "__main__":
    main()