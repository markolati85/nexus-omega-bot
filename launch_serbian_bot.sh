#!/bin/bash
# Serbian Server Bot Launch Script

echo "NEXUS OKX PRO - SERBIAN SERVER LAUNCHER"
echo "========================================"

# Server details
SERVER_IP="185.241.214.234"
SERVER_PATH="/opt/nexus-okx-pro"

echo "Target Server: $SERVER_IP"
echo "Deploy Path: $SERVER_PATH"
echo

# Create SSH command for easy copy-paste
echo "📋 SSH CONNECTION COMMAND:"
echo "ssh root@$SERVER_IP"
echo

# Create deployment commands
echo "🚀 DEPLOYMENT COMMANDS (run on server):"
echo
echo "# 1. Create directory"
echo "mkdir -p $SERVER_PATH"
echo "cd $SERVER_PATH"
echo
echo "# 2. Install dependencies"
echo "apt update && apt install python3 python3-pip python3-venv -y"
echo "python3 -m venv nexus_env"
echo "source nexus_env/bin/activate"
echo "pip install ccxt python-dotenv openai requests pandas numpy flask sqlalchemy"
echo
echo "# 3. Launch bot"
echo "nohup python3 launch_autonomous_okx_pro.py > nexus_trading.log 2>&1 &"
echo
echo "# 4. Monitor"
echo "tail -f nexus_trading.log"
echo "ps aux | grep nexus"
echo

# Quick verification script
echo "💡 VERIFICATION SCRIPT (run on server):"
echo "python3 -c \""
echo "import os"
echo "from dotenv import load_dotenv"
echo "load_dotenv()"
echo "import ccxt"
echo "client = ccxt.okx({"
echo "    'apiKey': os.getenv('OKX_API_KEY'),"
echo "    'secret': os.getenv('OKX_SECRET')," 
echo "    'password': os.getenv('OKX_PASSPHRASE'),"
echo "    'enableRateLimit': True"
echo "})"
echo "balance = client.fetch_balance()"
echo "print(f'USDT Balance: \${balance[\"USDT\"][\"total\"]:.2f}')"
echo "print('Bot ready for live trading!')"
echo "\""
echo

echo "✅ Ready for Serbian server deployment!"
echo "📁 Files prepared in: serbian_deployment/"
echo "📖 Full guide: SERBIAN_SERVER_DEPLOYMENT.md"