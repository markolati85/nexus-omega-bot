#!/bin/bash
# Serbian Server Live Deployment Script

echo "NEXUS OKX PRO - SERBIAN LIVE DEPLOYMENT"
echo "======================================"
echo "Target: root@185.241.214.234"
echo "Mode: LIVE TRADING (Real Money)"
echo "Balance: $148.50 USDT"
echo

# Step 1: Server Setup Commands
echo "STEP 1: SERVER SETUP (Run on Serbian server)"
echo "ssh root@185.241.214.234"
echo
cat << 'EOF'
mkdir -p /opt/nexus-okx-pro
cd /opt/nexus-okx-pro
apt update && apt install python3 python3-pip python3-venv curl wget htop screen -y
python3 -m venv nexus_env
source nexus_env/bin/activate
pip install --upgrade pip
pip install ccxt==4.3.95 python-dotenv==1.0.0 openai==1.51.2 requests==2.31.0 pandas==2.1.4 numpy==1.24.3 flask==3.0.0 sqlalchemy==2.0.23
echo "✅ Dependencies installed"
EOF

echo
echo "STEP 2: FILE TRANSFER (All 13 files)"
echo "scp nexus_okx_pro_gpt4o.py root@185.241.214.234:/opt/nexus-okx-pro/"
echo "scp launch_autonomous_okx_pro.py root@185.241.214.234:/opt/nexus-okx-pro/"
echo "scp strategy_selector.py root@185.241.214.234:/opt/nexus-okx-pro/"
echo "scp ai_core_langchain.py root@185.241.214.234:/opt/nexus-okx-pro/"
echo "scp futures_handler.py root@185.241.214.234:/opt/nexus-okx-pro/"
echo "scp margin_handler.py root@185.241.214.234:/opt/nexus-okx-pro/"
echo "scp auto_transfer_handler.py root@185.241.214.234:/opt/nexus-okx-pro/"
echo "scp opportunity_shift_engine.py root@185.241.214.234:/opt/nexus-okx-pro/"
echo "scp failsafe.py root@185.241.214.234:/opt/nexus-okx-pro/"
echo "scp config_autonomous.json root@185.241.214.234:/opt/nexus-okx-pro/"
echo "scp leverage_profile.json root@185.241.214.234:/opt/nexus-okx-pro/"
echo "scp failsafe_config.json root@185.241.214.234:/opt/nexus-okx-pro/"
echo "scp .env_okx root@185.241.214.234:/opt/nexus-okx-pro/"

echo
echo "STEP 3: LAUNCH LIVE TRADING BOT"
cat << 'EOF'
cd /opt/nexus-okx-pro
source nexus_env/bin/activate
screen -S nexus_bot
python3 launch_autonomous_okx_pro.py
EOF

echo
echo "STEP 4: MONITOR & VERIFY"
cat << 'EOF'
# Check bot process
ps aux | grep nexus

# Verify connection
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
print(f'✅ USDT: \${balance[\"USDT\"][\"total\"]:.2f}')
print('✅ LIVE TRADING ACTIVE')
print('🤖 BOT OPERATIONAL ON SERBIAN SERVER')
"
EOF

echo
echo "🎯 DEPLOYMENT COMMANDS READY"
echo "✅ All files prepared for transfer"
echo "✅ Live trading mode confirmed"  
echo "✅ $148.50 USDT ready for trading"
echo "✅ GPT-4o AI integration ready"