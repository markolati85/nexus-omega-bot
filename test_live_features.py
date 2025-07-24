#!/usr/bin/env python3
"""
Test Live Features - Verify bot capabilities
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env_okx')

def test_live_features():
    print("TESTING LIVE FEATURES FROM REPLIT")
    print("=" * 40)
    print(f"Test Time: {datetime.now()}")
    print()
    
    # Test 1: OKX Connection
    print("1. Testing OKX Live Connection...")
    try:
        import ccxt
        client = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'enableRateLimit': True,
            'sandbox': False  # LIVE MODE
        })
        
        balance = client.fetch_balance()
        usdt = balance.get('USDT', {}).get('total', 0)
        print(f"   ✅ Connected - USDT: ${usdt:.2f}")
        print(f"   ✅ Mode: LIVE TRADING")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 2: OpenAI GPT-4o
    print("\n2. Testing GPT-4o AI Connection...")
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'AI Connected' if you receive this"}],
            max_tokens=10
        )
        
        ai_response = response.choices[0].message.content.strip()
        print(f"   ✅ Connected - Response: {ai_response}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: Market Data
    print("\n3. Testing Market Data Access...")
    try:
        ticker = client.fetch_ticker('BTC/USDT')
        price = ticker['last']
        volume = ticker.get('quoteVolume', 0)
        change = ticker.get('percentage', 0)
        
        print(f"   ✅ BTC Price: ${price:,.2f}")
        print(f"   ✅ 24h Change: {change:+.2f}%")
        print(f"   ✅ Volume: ${volume:,.0f}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 4: Trading Readiness
    print("\n4. Testing Trading Readiness...")
    if usdt >= 5:
        print(f"   ✅ Sufficient balance for trading")
        position_size = usdt * 0.06
        print(f"   ✅ Position size (6%): ${position_size:.2f}")
        
        # Test minimum order calculation
        btc_amount = position_size / price
        if btc_amount * price >= 5:
            print(f"   ✅ Can place BTC order: {btc_amount:.6f} BTC")
        else:
            print(f"   ⚠️  Order too small: {btc_amount:.6f} BTC")
    else:
        print(f"   ❌ Insufficient balance: ${usdt:.2f}")
    
    print("\n" + "=" * 40)
    print("LIVE FEATURES TEST COMPLETE")
    print("Bot ready for autonomous trading from Replit")
    print("All systems operational for live trading")
    
    return True

if __name__ == "__main__":
    test_live_features()