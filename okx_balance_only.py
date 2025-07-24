#!/usr/bin/env python3
"""
OKX Balance Only - Single Exchange Report
"""

import os
from dotenv import load_dotenv
load_dotenv('.env_okx')

try:
    import ccxt
    
    client = ccxt.okx({
        'apiKey': os.getenv('OKX_API_KEY'),
        'secret': os.getenv('OKX_SECRET'), 
        'password': os.getenv('OKX_PASSPHRASE'),
        'enableRateLimit': True
    })
    
    print('OKX ACCOUNT BALANCE REPORT')
    print('=' * 40)
    
    # Get spot balance only (main funded account)
    client.options['defaultType'] = 'spot'
    balance = client.fetch_balance()
    
    total_usdt = 0
    active_assets = 0
    
    # Show only assets with meaningful balances
    for asset, data in balance.items():
        if isinstance(data, dict):
            amount = data.get('total', 0)
            if amount > 0.001:  # Filter out dust
                active_assets += 1
                if asset == 'USDT':
                    total_usdt = amount
                    print(f'{asset}: ${amount:.2f}')
                else:
                    print(f'{asset}: {amount:.6f}')
    
    print('=' * 40)
    print(f'USDT Available: ${total_usdt:.2f}')
    print(f'Active Assets: {active_assets}')
    print(f'Trading Ready: {"Yes" if total_usdt >= 5 else "Need more USDT"}')
    
except Exception as e:
    print(f'Error: {e}')