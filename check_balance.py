#!/usr/bin/env python3
"""
Quick Balance Check - Live OKX Account Status
"""

import os
from dotenv import load_dotenv

load_dotenv('.env_okx')

def check_live_balance():
    """Check current live balance and trading readiness"""
    try:
        import ccxt
        
        client = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'enableRateLimit': True,
            'sandbox': False  # LIVE MODE
        })
        
        print("OKX LIVE BALANCE CHECK")
        print("=" * 30)
        
        balance = client.fetch_balance()
        usdt_total = balance.get('USDT', {}).get('total', 0)
        usdt_free = balance.get('USDT', {}).get('free', 0)
        
        print(f"USDT Balance: ${usdt_total:.2f}")
        print(f"Available: ${usdt_free:.2f}")
        print(f"Mode: LIVE TRADING")
        
        # Check crypto holdings
        crypto_value = 0
        for asset, amounts in balance['total'].items():
            if asset != 'USDT' and amounts > 0.001:
                try:
                    ticker = client.fetch_ticker(f'{asset}/USDT')
                    value = amounts * ticker['last']
                    crypto_value += value
                    print(f"{asset}: {amounts:.6f} (${value:.2f})")
                except:
                    pass
        
        total_portfolio = usdt_total + crypto_value
        print(f"Total Portfolio: ${total_portfolio:.2f}")
        
        # Trading readiness
        if usdt_total >= 5:
            print("✅ Ready for trading")
        else:
            print("⚠️  Low balance - limited trading")
        
        return total_portfolio
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

if __name__ == "__main__":
    check_live_balance()