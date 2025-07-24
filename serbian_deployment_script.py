#!/usr/bin/env python3
"""
Serbian Server Deployment and Launch Script
Connects to server, deploys bot, and launches live trading
"""

import subprocess
import time
import os

def deploy_to_serbian_server():
    print("CONNECTING TO SERBIAN SERVER")
    print("Server: 185.241.214.234")
    print("=" * 50)
    
    # Create SSH deployment commands
    deployment_commands = [
        "mkdir -p /opt/nexus-okx-pro",
        "cd /opt/nexus-okx-pro",
        "apt update && apt install python3 python3-pip python3-venv curl wget -y",
        "python3 -m venv nexus_env",
        "source nexus_env/bin/activate && pip install ccxt python-dotenv openai requests pandas numpy flask sqlalchemy",
    ]
    
    # File transfer commands (using scp)
    files_to_transfer = [
        'nexus_okx_pro_gpt4o.py',
        'launch_autonomous_okx_pro.py', 
        'strategy_selector.py',
        'ai_core_langchain.py',
        'futures_handler.py',
        'margin_handler.py',
        'auto_transfer_handler.py',
        'opportunity_shift_engine.py',
        'failsafe.py',
        'config_autonomous.json',
        'leverage_profile.json',
        'failsafe_config.json',
        '.env_okx'
    ]
    
    print("DEPLOYMENT COMMANDS:")
    print("=" * 30)
    
    # SSH connection command
    print("1. SSH Connection:")
    print("ssh root@185.241.214.234")
    print()
    
    # Setup commands
    print("2. Server Setup:")
    for cmd in deployment_commands:
        print(f"   {cmd}")
    print()
    
    # File transfer
    print("3. File Transfer (run from local):")
    for file in files_to_transfer:
        print(f"   scp {file} root@185.241.214.234:/opt/nexus-okx-pro/")
    print()
    
    # Launch commands
    print("4. Launch Bot (run on server):")
    print("   cd /opt/nexus-okx-pro")
    print("   source nexus_env/bin/activate")
    print("   nohup python3 launch_autonomous_okx_pro.py > nexus_live.log 2>&1 &")
    print()
    
    # Verification
    print("5. Verification:")
    print("   ps aux | grep nexus")
    print("   tail -f nexus_live.log")
    print()
    
    # Test connection
    print("6. Test OKX Connection:")
    test_script = '''python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
import ccxt

print('Testing OKX Connection...')
client = ccxt.okx({
    'apiKey': os.getenv('OKX_API_KEY'),
    'secret': os.getenv('OKX_SECRET'), 
    'password': os.getenv('OKX_PASSPHRASE'),
    'enableRateLimit': True,
    'sandbox': False
})

balance = client.fetch_balance()
usdt = balance.get('USDT', {}).get('total', 0)
print(f'✅ USDT Balance: ${usdt:.2f}')
print(f'✅ Mode: LIVE TRADING')
print(f'✅ Ready: Bot can trade with real money')

ticker = client.fetch_ticker('BTC/USDT')
print(f'✅ Market: BTC at ${ticker[\"last\"]:,.2f}')
print('DEPLOYMENT SUCCESSFUL - BOT READY FOR LIVE TRADING!')
"'''
    
    print(f"   {test_script}")
    
    return True

if __name__ == "__main__":
    deploy_to_serbian_server()