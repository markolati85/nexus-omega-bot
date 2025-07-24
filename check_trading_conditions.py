#!/usr/bin/env python3
"""
Check Trading Conditions - Verify if conditions are right for trades
"""

import os
import ccxt
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def check_conditions():
    print("🔍 CHECKING LIVE TRADING CONDITIONS")
    print("=" * 50)
    
    # Setup APIs
    exchange = ccxt.okx({
        'apiKey': os.getenv('OKX_API_KEY'),
        'secret': os.getenv('OKX_SECRET'),
        'password': os.getenv('OKX_PASSPHRASE'),
        'sandbox': False,
        'enableRateLimit': True
    })
    
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Check balance
    balance = exchange.fetch_balance()
    usdt_balance = balance.get('USDT', {}).get('free', 0)
    print(f"💰 USDT Balance: ${usdt_balance:.2f}")
    
    if usdt_balance < 5:
        print("❌ Insufficient balance for trading (minimum $5)")
        return
    
    # Check trading pairs
    pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    
    for pair in pairs:
        ticker = exchange.fetch_ticker(pair)
        ohlcv = exchange.fetch_ohlcv(pair, '1h', limit=24)
        
        # Calculate RSI
        closes = [candle[4] for candle in ohlcv[-14:]]
        if len(closes) >= 14:
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]
            
            avg_gain = sum(gains) / len(gains) if gains else 0
            avg_loss = sum(losses) / len(losses) if losses else 0.1
            
            rsi = 100 - (100 / (1 + (avg_gain / avg_loss))) if avg_loss > 0 else 50
        else:
            rsi = 50
        
        print(f"\n📊 {pair}:")
        print(f"   Price: ${ticker['last']:.2f}")
        print(f"   24h Change: {ticker['percentage']:+.2f}%")
        print(f"   RSI: {rsi:.1f}")
        
        # AI decision with relaxed thresholds
        prompt = f"""
        Trading Decision for {pair}:
        Price: ${ticker['last']:.2f}
        24h Change: {ticker['percentage']:+.2f}%
        RSI: {rsi:.1f}
        Balance: ${usdt_balance:.2f}
        
        RELAXED TRADING RULES:
        - RSI < 45: BUY signal
        - RSI > 55: SELL signal
        - Confidence >= 70% to execute
        
        Respond with JSON: {{"action": "buy/sell/hold", "confidence": 70-95, "reason": "analysis"}}
        """
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )
            
            import json
            decision = json.loads(response.choices[0].message.content.strip())
            
            print(f"   🤖 AI: {decision['action'].upper()} ({decision['confidence']}%)")
            print(f"   Reason: {decision['reason']}")
            
            if decision['confidence'] >= 70 and decision['action'] != 'hold':
                print(f"   ✅ TRADE CONDITIONS MET!")
                
                # Test trade amount
                trade_amount = usdt_balance * 0.08
                print(f"   💵 Trade Amount: ${trade_amount:.2f}")
                
                if trade_amount >= 5:
                    print(f"   🚀 READY FOR LIVE EXECUTION")
                else:
                    print(f"   ⚠️  Trade amount below $5 minimum")
            else:
                print(f"   ⏳ Waiting for better conditions")
                
        except Exception as e:
            print(f"   ❌ AI Error: {e}")
    
    print(f"\n📈 MARKET ANALYSIS COMPLETE")
    print(f"If no trades executed, RSI conditions not optimal yet.")
    print(f"System will execute trades when RSI < 45 or RSI > 55 with 70%+ confidence.")

if __name__ == "__main__":
    check_conditions()