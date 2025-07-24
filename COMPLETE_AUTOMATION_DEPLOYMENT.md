# NEXUS OKX PRO - COMPLETE SERBIAN DEPLOYMENT

## 🚀 IMMEDIATE DEPLOYMENT COMMANDS

### STEP 1: Connect to Serbian Server
```bash
ssh root@185.241.214.234
```

### STEP 2: Setup Server Environment
```bash
mkdir -p /opt/nexus-okx-pro
cd /opt/nexus-okx-pro
apt update && apt install python3 python3-pip python3-venv curl wget htop screen -y
python3 -m venv nexus_env
source nexus_env/bin/activate
pip install --upgrade pip
pip install ccxt==4.3.95 python-dotenv==1.0.0 openai==1.51.2 requests==2.31.0 pandas==2.1.4 numpy==1.24.3 flask==3.0.0 sqlalchemy==2.0.23
exit
```

### STEP 3: Transfer All Files (From Local Machine)
```bash
scp nexus_okx_pro_gpt4o.py root@185.241.214.234:/opt/nexus-okx-pro/
scp launch_autonomous_okx_pro.py root@185.241.214.234:/opt/nexus-okx-pro/
scp strategy_selector.py root@185.241.214.234:/opt/nexus-okx-pro/
scp ai_core_langchain.py root@185.241.214.234:/opt/nexus-okx-pro/
scp futures_handler.py root@185.241.214.234:/opt/nexus-okx-pro/
scp margin_handler.py root@185.241.214.234:/opt/nexus-okx-pro/
scp auto_transfer_handler.py root@185.241.214.234:/opt/nexus-okx-pro/
scp opportunity_shift_engine.py root@185.241.214.234:/opt/nexus-okx-pro/
scp failsafe.py root@185.241.214.234:/opt/nexus-okx-pro/
scp config_autonomous.json root@185.241.214.234:/opt/nexus-okx-pro/
scp leverage_profile.json root@185.241.214.234:/opt/nexus-okx-pro/
scp failsafe_config.json root@185.241.214.234:/opt/nexus-okx-pro/
scp .env_okx root@185.241.214.234:/opt/nexus-okx-pro/
```

### STEP 4: Launch Live Trading Bot
```bash
ssh root@185.241.214.234
cd /opt/nexus-okx-pro
source nexus_env/bin/activate

# Test connection first
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
print(f'USDT Balance: \${usdt:.2f}')
print('Mode: LIVE TRADING')
print('READY FOR DEPLOYMENT')
"

# Launch bot
screen -dmS nexus_live python3 launch_autonomous_okx_pro.py
screen -r nexus_live
```

## ✅ DEPLOYMENT VERIFICATION

- **Server**: 185.241.214.234
- **Balance**: $148.50 USDT ready for trading
- **Mode**: Live trading (NO simulation)
- **AI**: GPT-4o powered autonomous decisions
- **Frequency**: 3-minute cycles
- **Threshold**: 70% AI confidence
- **Position Size**: 6% per trade

## 🎯 MONITORING COMMANDS

```bash
# Check bot process
ps aux | grep nexus

# Access bot screen
screen -r nexus_live

# View live logs
tail -f /opt/nexus-okx-pro/*.log
```

**🚀 BOT WILL START LIVE TRADING IMMEDIATELY UPON DEPLOYMENT**