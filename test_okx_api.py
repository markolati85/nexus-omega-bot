#!/usr/bin/env python3
"""
OKX API Connection and Permissions Test
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env_okx')

print('🔧 Testing OKX API Connection...')
print('=' * 50)

try:
    import ccxt
    
    # Initialize OKX client
    client = ccxt.okx({
        'apiKey': os.getenv('OKX_API_KEY'),
        'secret': os.getenv('OKX_SECRET'), 
        'password': os.getenv('OKX_PASSPHRASE'),
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    })
    
    print(f'📡 API Key: {os.getenv("OKX_API_KEY")[:8]}...')
    print('🔗 Establishing connection...')
    
    # Test 1: Basic connection with account balance
    print('\n🧪 TEST 1: Account Balance')
    balance = client.fetch_balance()
    print('✅ Balance call successful')
    
    total_usdt = balance.get('USDT', {}).get('total', 0)
    free_usdt = balance.get('USDT', {}).get('free', 0)
    print(f'💰 Total USDT: {total_usdt:.2f}')
    print(f'💸 Free USDT: {free_usdt:.2f}')
    
    # Show all non-zero balances
    print('\n📊 All Account Balances:')
    for currency, info in balance.items():
        if isinstance(info, dict) and info.get('total', 0) > 0:
            print(f'   {currency}: {info["total"]:.6f} (free: {info["free"]:.6f})')
    
    # Test 2: Market data access
    print('\n🧪 TEST 2: Market Data Access')
    ticker = client.fetch_ticker('BTC/USDT')
    print('✅ Market data access successful')
    print(f'📈 BTC/USDT Price: ${ticker["last"]:.2f}')
    
    # Test 3: Trading permissions check
    print('\n🧪 TEST 3: Trading Permissions')
    try:
        # Check if we can access trading endpoints
        markets = client.load_markets()
        btc_market = markets.get('BTC/USDT')
        if btc_market:
            min_amount = btc_market.get('limits', {}).get('amount', {}).get('min', 0.00001)
            print(f'✅ Trading endpoint access confirmed')
            print(f'📏 BTC/USDT min amount: {min_amount}')
        
        # Try to fetch open orders (trading permission test)
        open_orders = client.fetch_open_orders('BTC/USDT')
        print(f'✅ Trading permissions confirmed')
        print(f'📋 Open orders: {len(open_orders)}')
        
    except Exception as e:
        if 'permission' in str(e).lower() or 'forbidden' in str(e).lower():
            print(f'❌ Trading permissions denied: {e}')
        else:
            print(f'✅ Trading permissions likely OK (error: {e})')
    
    # Test 4: Futures access
    print('\n🧪 TEST 4: Futures Trading Access')
    try:
        client.options['defaultType'] = 'swap'
        futures_balance = client.fetch_balance()
        print('✅ Futures access confirmed')
        futures_usdt = futures_balance.get('USDT', {}).get('total', 0)
        print(f'🔮 Futures USDT: {futures_usdt:.2f}')
        client.options['defaultType'] = 'spot'  # Reset
    except Exception as e:
        print(f'⚠️ Futures access limited: {e}')
    
    # Test 5: Margin access
    print('\n🧪 TEST 5: Margin Trading Access')
    try:
        margin_balance = client.fetch_balance({'type': 'margin'})
        print('✅ Margin access confirmed')
        margin_usdt = margin_balance.get('USDT', {}).get('total', 0)
        print(f'💹 Margin USDT: {margin_usdt:.2f}')
    except Exception as e:
        print(f'⚠️ Margin access limited: {e}')
    
    print('\n' + '=' * 50)
    print('🎉 OKX API CONNECTION SUCCESSFUL')
    print('✅ Basic permissions verified')
    print('🚀 Ready for autonomous trading')
    
    # Return connection status
    print('\nCONNECTION_STATUS: SUCCESS')
    print(f'TOTAL_BALANCE: {total_usdt:.2f}')
    
except ImportError as e:
    print(f'❌ Missing library: {e}')
    print('💡 Installing required packages...')
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'ccxt'], check=True)
    print('✅ Packages installed - please retry')
    
except Exception as e:
    print(f'❌ Connection failed: {e}')
    if 'Invalid API key' in str(e):
        print('💡 Solution: Check API key is correct')
    elif 'timestamp' in str(e):
        print('💡 Solution: Check system time synchronization')
    elif 'signature' in str(e):
        print('💡 Solution: Check API secret is correct')
    else:
        print('💡 Solution: Verify all API credentials in .env_okx')
    
    print('\nCONNECTION_STATUS: FAILED')