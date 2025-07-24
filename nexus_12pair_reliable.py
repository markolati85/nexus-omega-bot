#!/usr/bin/env python3
import requests
import time
import ccxt
import os
from datetime import datetime

# Configuration
TOKEN = "8429171890:AAEaYGGQb8L-pir22rt128g5hbh6GTuWDqk"
CHAT_ID = "1762317382"

WATCHLIST = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT",
    "XRP/USDT", "DOGE/USDT", "APT/USDT", "OP/USDT", 
    "AVAX/USDT", "MATIC/USDT", "ARB/USDT", "LTC/USDT"
]

# OKX API Configuration
OKX_CONFIG = {
    'apiKey': 'bfee3fff-cdf1-4b71-9ef9-8760de8732f4',
    'secret': 'E7C2058E8DC095D3F45F5C37D6A28DC8',
    'password': 'Okx123#',
    'sandbox': False
}

def send_telegram_message(message):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        response = requests.post(url, json=data, timeout=15)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def get_portfolio_value():
    """Get total portfolio value in USDT"""
    try:
        exchange = ccxt.okx(OKX_CONFIG)
        response = exchange.private_get_account_balance()
        
        if response.get("code") == "0":
            details = response.get("data", [{}])[0].get("details", [])
            total_value = 0
            
            for detail in details:
                symbol = detail.get("ccy", "")
                amount = float(detail.get("cashBal", 0))
                
                if amount > 0.001:  # Ignore dust
                    if symbol == "USDT":
                        total_value += amount
                    else:
                        try:
                            ticker = exchange.fetch_ticker(f"{symbol}/USDT")
                            total_value += amount * ticker["last"]
                        except:
                            pass  # Skip if can't convert
            
            return total_value
        
    except Exception as e:
        print(f"Portfolio error: {e}")
        return 0

def analyze_crypto_pair(symbol):
    """Analyze single crypto pair"""
    try:
        exchange = ccxt.okx(OKX_CONFIG)
        ticker = exchange.fetch_ticker(symbol)
        
        price = ticker["last"]
        change_24h = ticker.get("percentage", 0)
        volume = ticker.get("quoteVolume", 0)
        
        # Calculate confidence score
        momentum_score = min(40, abs(change_24h) * 8)
        volume_score = 20 if volume > 1000000 else 10
        
        confidence = 50 + momentum_score + volume_score
        confidence = min(95, confidence)
        
        # Determine action
        if change_24h >= 2:
            action = "BUY"
        elif change_24h <= -2:
            action = "SELL"
        else:
            action = "HOLD"
        
        # Calculate leverage
        leverage = min(15, int(confidence / 6)) if confidence >= 60 else 1
        
        return {
            "symbol": symbol,
            "price": price,
            "change_24h": change_24h,
            "confidence": int(confidence),
            "action": action,
            "leverage": leverage
        }
        
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

def scan_all_pairs():
    """Scan all 12 pairs and return ranked opportunities"""
    opportunities = []
    
    for symbol in WATCHLIST:
        analysis = analyze_crypto_pair(symbol)
        if analysis and analysis["confidence"] >= 50:
            opportunities.append(analysis)
    
    # Sort by confidence (highest first)
    opportunities.sort(key=lambda x: x["confidence"], reverse=True)
    return opportunities

def run_market_scan(cycle_num):
    """Run complete market scan and send results"""
    print(f"\n=== 12-PAIR SCAN CYCLE {cycle_num} ===")
    
    # Get current portfolio
    portfolio_value = get_portfolio_value()
    print(f"Portfolio: ${portfolio_value:.2f} USDT")
    
    # Scan all pairs
    opportunities = scan_all_pairs()
    
    if not opportunities:
        message = f"📊 12-PAIR SCAN #{cycle_num}\n\n❌ No opportunities above 50% confidence\n\n⏰ {datetime.now().strftime('%H:%M:%S UTC')}"
        send_telegram_message(message)
        return
    
    best = opportunities[0]
    top_3 = opportunities[:3]
    
    print(f"Best opportunity: {best['symbol']} ({best['confidence']}%)")
    
    # Check if we have a strong trade signal
    if best["confidence"] >= 70 and best["action"] != "HOLD":
        # High confidence trade signal
        position_size = portfolio_value * 0.12  # 12% position sizing
        
        emoji = "🚀" if best["action"] == "BUY" else "📉"
        message = f"""{emoji} TRADE SIGNAL - {best['symbol']}

📊 Analysis:
• Price: ${best['price']:,.4f}
• Change: {best['change_24h']:+.1f}%
• Action: {best['action']}
• Confidence: {best['confidence']}%
• Leverage: {best['leverage']}x

💰 Trade Details:
• Position: ${position_size:.2f} (12%)
• Portfolio: ${portfolio_value:.2f} USDT

📈 Alternatives:"""
        
        for i, opp in enumerate(top_3[1:3], 2):
            message += f"\n{i}. {opp['symbol']}: {opp['confidence']}% ({opp['change_24h']:+.1f}%)"
        
        message += f"\n\n⏰ Cycle {cycle_num} • {datetime.now().strftime('%H:%M:%S UTC')}"
        
    else:
        # Regular market scan results
        message = f"""📊 12-PAIR SCAN #{cycle_num}

🔍 Market Analysis:
• Pairs Scanned: 12
• Opportunities: {len(opportunities)}
• Best Confidence: {best['confidence']}%

📈 Top 3 Opportunities:"""
        
        for i, opp in enumerate(top_3, 1):
            action_emoji = "🟢" if opp["action"] == "BUY" else "🔴" if opp["action"] == "SELL" else "⚪"
            message += f"\n{i}. {action_emoji} {opp['symbol']}: {opp['confidence']}% ({opp['change_24h']:+.1f}%)"
        
        message += f"""

💰 Portfolio: ${portfolio_value:.2f} USDT
🎯 Need: 70%+ confidence for trades

⏰ {datetime.now().strftime('%H:%M:%S UTC')}"""
    
    # Send the analysis
    success = send_telegram_message(message)
    print(f"Telegram sent: {success}")

def main():
    """Main bot loop"""
    print("🚀 Starting Nexus 12-Pair Reliable Bot...")
    
    # Send startup notification
    startup_message = f"""🟢 12-PAIR BOT ONLINE (RELIABLE)

✅ Monitoring Active:
• Pairs: {len(WATCHLIST)} major cryptos
• Analysis: Multi-factor confidence
• Threshold: 70%+ for trade signals
• Position: 12% portfolio sizing

📊 Watchlist:
{', '.join(WATCHLIST[:6])}
{', '.join(WATCHLIST[6:])}

🔄 Scanning every 90 seconds
💰 Portfolio: ${get_portfolio_value():.2f} USDT

⏰ Started: {datetime.now().strftime('%H:%M:%S UTC')}"""
    
    if not send_telegram_message(startup_message):
        print("❌ Failed to send startup message")
        return
    
    print("✅ Bot started successfully")
    
    cycle = 0
    try:
        while True:
            cycle += 1
            start_time = time.time()
            
            # Run market scan
            run_market_scan(cycle)
            
            # Sleep for 90 seconds (adjust for processing time)
            elapsed = time.time() - start_time
            sleep_time = max(0, 90 - elapsed)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        send_telegram_message("🔴 12-PAIR BOT OFFLINE\n\nStopped by user intervention.")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        send_telegram_message(f"⚠️ BOT ERROR\n\n{str(e)[:100]}...")

if __name__ == "__main__":
    main()