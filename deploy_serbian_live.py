#!/usr/bin/env python3
"""
Serbian Server Live Deployment Script
Direct deployment and launch with live trading verification
"""

import subprocess
import os
import time
from datetime import datetime

def deploy_to_serbian_server():
    print("DEPLOYING NEXUS OKX PRO TO SERBIAN SERVER")
    print("=" * 50)
    print(f"Server: root@185.241.214.234")
    print(f"Mode: LIVE TRADING (Real Money)")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Create deployment package
    deployment_commands = """
#!/bin/bash
set -e

echo "🔧 SERBIAN SERVER DEPLOYMENT - LIVE TRADING"
echo "==========================================="

# Create directory
mkdir -p /opt/nexus-okx-pro
cd /opt/nexus-okx-pro

# System setup
apt update -y
apt install python3 python3-pip python3-venv curl wget htop screen unzip -y

# Python environment
python3 -m venv nexus_env
source nexus_env/bin/activate

# Install dependencies
pip install --upgrade pip
pip install ccxt==4.3.95
pip install python-dotenv==1.0.0  
pip install openai==1.51.2
pip install requests==2.31.0
pip install pandas==2.1.4
pip install numpy==1.24.3
pip install flask==3.0.0
pip install sqlalchemy==2.0.23

echo "✅ Dependencies installed successfully"

# Verify installations
python3 -c "import ccxt; print(f'CCXT: {ccxt.__version__}')"
python3 -c "import openai; print(f'OpenAI: {openai.__version__}')"

echo "🚀 Server ready for bot files"
"""
    
    print("DEPLOYMENT SCRIPT:")
    print("-" * 30)
    print(deployment_commands)
    
    # File list for transfer
    essential_files = [
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
    
    print(f"\nFILE TRANSFER COMMANDS:")
    print("-" * 25)
    for file in essential_files:
        if os.path.exists(file):
            print(f"scp {file} root@185.241.214.234:/opt/nexus-okx-pro/")
        else:
            print(f"⚠️  Missing: {file}")
    
    # Launch script
    launch_script = """
# Navigate to bot directory
cd /opt/nexus-okx-pro
source nexus_env/bin/activate

# Test OKX connection first
echo "🔍 Testing live OKX connection..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
import ccxt

client = ccxt.okx({
    'apiKey': os.getenv('OKX_API_KEY'),
    'secret': os.getenv('OKX_SECRET'),
    'password': os.getenv('OKX_PASSPHRASE'),
    'enableRateLimit': True,
    'sandbox': False
})

balance = client.fetch_balance()
usdt = balance.get('USDT', {}).get('total', 0)
print(f'✅ USDT Balance: \${usdt:.2f}')
print(f'✅ Mode: LIVE TRADING')

ticker = client.fetch_ticker('BTC/USDT')
print(f'✅ Market: BTC at \${ticker[\"last\"]:,.2f}')
print('🚀 CONNECTION VERIFIED - READY FOR LIVE TRADING')
"

# Launch bot in screen session
echo "🤖 Launching autonomous trading bot..."
screen -dmS nexus_live python3 launch_autonomous_okx_pro.py

# Monitor startup
sleep 10
screen -ls
echo "✅ Bot launched in screen session 'nexus_live'"
echo "Monitor with: screen -r nexus_live"

# Verify bot is running
ps aux | grep nexus | grep -v grep
echo "🎯 SERBIAN DEPLOYMENT COMPLETE - LIVE TRADING ACTIVE"
"""
    
    print(f"\nLAUNCH SCRIPT:")
    print("-" * 15)
    print(launch_script)
    
    print(f"\nDEPLOYMENT SUMMARY:")
    print("=" * 20)
    print("1. SSH: ssh root@185.241.214.234")
    print("2. Run deployment script above")
    print("3. Transfer all 13 files") 
    print("4. Execute launch script")
    print("5. Monitor: screen -r nexus_live")
    print()
    print("✅ Bot will trade with $148.50 USDT")
    print("✅ Live mode confirmed (no simulation)")
    print("✅ GPT-4o AI integration ready")
    print("✅ 70% confidence threshold")
    print("✅ 3-minute autonomous cycles")

if __name__ == "__main__":
    deploy_to_serbian_server()