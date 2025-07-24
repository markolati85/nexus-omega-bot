#!/usr/bin/env python3
"""
Live OKX Pro Deployment - Serbian Server Launch
"""

import subprocess
import os
import time
from datetime import datetime

def deploy_live_bot():
    print("DEPLOYING NEXUS OKX PRO TO SERBIAN SERVER")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print("Server: 185.241.214.234")
    print("Mode: LIVE TRADING (NO SIMULATION)")
    print()
    
    # SSH deployment script
    deployment_script = """
#!/bin/bash
set -e

echo "🔧 PREPARING SERBIAN SERVER FOR LIVE TRADING"
echo "============================================="

# Create directory
mkdir -p /opt/nexus-okx-pro
cd /opt/nexus-okx-pro

# Update system and install dependencies
echo "📦 Installing system dependencies..."
apt update && apt install python3 python3-pip python3-venv curl wget htop -y

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv nexus_env
source nexus_env/bin/activate

# Install OKX trading dependencies
echo "💹 Installing OKX trading dependencies..."
pip install --upgrade pip
pip install ccxt==4.3.95
pip install python-dotenv==1.0.0
pip install openai==1.51.2
pip install requests==2.31.0
pip install pandas==2.1.4
pip install numpy==1.24.3
pip install flask==3.0.0
pip install sqlalchemy==2.0.23

# Verify installations
echo "✅ Verifying installations..."
python3 -c "import ccxt; print(f'CCXT: {ccxt.__version__}')"
python3 -c "import openai; print(f'OpenAI: {openai.__version__}')"
python3 -c "import pandas; print(f'Pandas: {pandas.__version__}')"

echo "🚀 SERVER READY FOR BOT DEPLOYMENT"
echo "Dependencies installed successfully"
"""
    
    print("DEPLOYMENT SCRIPT GENERATED")
    print("Save this script and run on Serbian server:")
    print("-" * 40)
    print(deployment_script)
    
    # Generate file transfer commands
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
    
    print("\nFILE TRANSFER COMMANDS:")
    print("-" * 30)
    for file in files_to_transfer:
        print(f"scp {file} root@185.241.214.234:/opt/nexus-okx-pro/")
    
    # Launch commands
    launch_commands = """
# Launch live trading bot
cd /opt/nexus-okx-pro
source nexus_env/bin/activate

# Start bot in live mode
echo "🚀 LAUNCHING LIVE TRADING BOT..."
nohup python3 launch_autonomous_okx_pro.py > nexus_live_trading.log 2>&1 &

# Get process ID
BOT_PID=$!
echo "Bot started with PID: $BOT_PID"

# Monitor startup
sleep 5
tail -20 nexus_live_trading.log

# Check process
ps aux | grep nexus | grep -v grep
echo "✅ LIVE TRADING BOT DEPLOYED SUCCESSFULLY"
"""
    
    print(f"\nLAUNCH COMMANDS:")
    print("-" * 20)
    print(launch_commands)
    
    # Verification script
    verification_script = """
# Test live OKX connection
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
import ccxt

print('🔍 TESTING LIVE OKX CONNECTION...')
client = ccxt.okx({
    'apiKey': os.getenv('OKX_API_KEY'),
    'secret': os.getenv('OKX_SECRET'),
    'password': os.getenv('OKX_PASSPHRASE'),
    'enableRateLimit': True,
    'sandbox': False
})

# Test connection
balance = client.fetch_balance()
usdt = balance.get('USDT', {}).get('total', 0)
print(f'✅ USDT Balance: \${usdt:.2f}')
print(f'✅ Mode: LIVE TRADING')
print(f'✅ Trading Ready: {\"Yes\" if usdt >= 5 else \"No - Insufficient\"}')

# Market test
ticker = client.fetch_ticker('BTC/USDT')
print(f'✅ Market Data: BTC at \${ticker[\"last\"]:,.2f}')

print('🚀 SERBIAN SERVER DEPLOYMENT SUCCESSFUL!')
print('🤖 BOT READY FOR LIVE PROFIT GENERATION!')
"
"""
    
    print(f"\nVERIFICATION SCRIPT:")
    print("-" * 25)
    print(verification_script)
    
    print(f"\nCOMPLETE DEPLOYMENT READY")
    print("=" * 30)
    print("1. SSH to server: ssh root@185.241.214.234")
    print("2. Run deployment script above")
    print("3. Transfer all 13 files")
    print("4. Execute launch commands")
    print("5. Run verification script")
    print("6. Monitor: tail -f nexus_live_trading.log")

if __name__ == "__main__":
    deploy_live_bot()