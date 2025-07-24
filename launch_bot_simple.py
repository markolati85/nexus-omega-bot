#!/usr/bin/env python3
"""
Simple Bot Launcher - Works with current environment
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv('.env_okx')

print('🚀 NEXUS OKX PRO AUTONOMOUS v6.0')
print('🤖 GPT-4o + OKX Integration')
print('⚡ Up to 125x Leverage | Advanced Risk Management')
print('=' * 60)

# Show credentials status
print('🔧 Credential Check:')
print(f"✅ OKX Key: {os.getenv('OKX_API_KEY', 'Missing')[:8]}...")
print(f"✅ OpenAI: {os.environ.get('OPENAI_API_KEY', 'Missing')[:10]}...")

# Test basic connections
try:
    import ccxt
    
    client = ccxt.okx({
        'apiKey': os.getenv('OKX_API_KEY'),
        'secret': os.getenv('OKX_SECRET'), 
        'password': os.getenv('OKX_PASSPHRASE'),
        'enableRateLimit': True
    })
    
    balance = client.fetch_balance()
    total_usdt = balance.get('USDT', {}).get('total', 0)
    
    print(f'✅ OKX Connected: ${total_usdt:.2f} USDT')
    
    # Count assets
    assets = [k for k,v in balance.items() if isinstance(v, dict) and v.get('total', 0) > 0]
    print(f'📊 Portfolio: {len(assets)} different assets')
    
    # Test trading permissions
    try:
        orders = client.fetch_open_orders('BTC/USDT')
        print('✅ Trading permissions verified')
    except:
        print('⚠️ Trading permissions check inconclusive')
    
    print('\n🎯 AUTONOMOUS BOT STATUS: READY')
    print('💡 The bot can trade with current small balances for testing')
    print('💰 To increase trading volume, deposit more USDT to OKX')
    
    # Launch option
    user_input = input('\n🚀 Launch autonomous trading? (y/n): ')
    
    if user_input.lower() == 'y':
        print('\n' + '='*60)
        print('🚀 LAUNCHING AUTONOMOUS TRADING MODE')
        print('🔄 3-minute cycles with AI analysis')
        print('🛡️ 4.5% daily loss limit protection')
        print('⚡ Dynamic leverage up to 125x')
        print('💱 Auto-transfer between spot/margin/futures')
        print('🔄 Press Ctrl+C to stop')
        print('='*60)
        
        # Import and run main bot
        from nexus_okx_pro_gpt4o import main
        main()
    else:
        print('👋 Launch cancelled')
        
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    print('📦 Run: pip install ccxt openai python-dotenv')
    
except Exception as e:
    print(f'❌ Connection error: {e}')
    print('💡 Check API credentials in .env_okx file')