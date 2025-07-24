# SERBIAN SERVER DEPLOYMENT BACKUP

## DEPLOYMENT SUMMARY
- **Server**: root@185.241.214.234
- **Path**: /opt/nexus-okx-pro
- **Mode**: Live Trading (NO SIMULATION)
- **Balance**: $148.50 USDT
- **AI**: GPT-4o powered autonomous trading

## ESSENTIAL FILES (13 total)
```
nexus_okx_pro_gpt4o.py - Main bot (38KB)
launch_autonomous_okx_pro.py - Launcher (7KB)
strategy_selector.py - AI strategy selection
ai_core_langchain.py - GPT-4o integration
futures_handler.py - Futures trading
margin_handler.py - Margin trading
auto_transfer_handler.py - Wallet management
opportunity_shift_engine.py - Capital reallocation
failsafe.py - Risk management
config_autonomous.json - Configuration
leverage_profile.json - Leverage settings
failsafe_config.json - Safety limits
.env_okx - API credentials
```

## DEPLOYMENT COMMANDS

### 1. Server Setup
```bash
ssh root@185.241.214.234
mkdir -p /opt/nexus-okx-pro
cd /opt/nexus-okx-pro
apt update && apt install python3 python3-pip python3-venv curl wget htop screen -y
python3 -m venv nexus_env
source nexus_env/bin/activate
pip install ccxt==4.3.95 python-dotenv==1.0.0 openai==1.51.2 requests==2.31.0 pandas==2.1.4 numpy==1.24.3 flask==3.0.0 sqlalchemy==2.0.23
```

### 2. File Transfer
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

### 3. Launch Live Trading
```bash
cd /opt/nexus-okx-pro
source nexus_env/bin/activate
screen -dmS nexus_live python3 launch_autonomous_okx_pro.py
screen -r nexus_live
```

### 4. Verification
```bash
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
print(f'USDT: \${balance[\"USDT\"][\"total\"]:.2f}')
print('LIVE TRADING ACTIVE')
"
```

## MONITORING
- **Process**: `ps aux | grep nexus`
- **Screen**: `screen -r nexus_live`
- **Status**: Bot runs 3-minute cycles autonomously
- **Trades**: Execute when AI confidence >70%

## CONFIGURATION
- Position Size: 6% per trade ($8.91)
- AI Threshold: 70% confidence
- Cycle Time: 3 minutes
- Risk Limit: 4.5% daily loss
- Leverage: Up to 125x futures

**STATUS: READY FOR IMMEDIATE DEPLOYMENT**