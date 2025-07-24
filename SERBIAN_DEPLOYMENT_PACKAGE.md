# NEXUS BOT SERBIAN SERVER DEPLOYMENT PACKAGE

## UPDATED WITH NEW OPENAI API KEY ✅

Your OpenAI API key has been successfully updated and verified. The bot is ready for deployment to your Serbian server.

## QUICK DEPLOYMENT COMMANDS

### 1. Connect to your server
```bash
ssh root@185.241.214.234
```

### 2. Setup environment (run once)
```bash
mkdir -p /opt/nexus-trading
cd /opt/nexus-trading

# Install dependencies
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv git screen htop -y

# Create Python environment
python3 -m venv nexus_env
source nexus_env/bin/activate

# Install required packages
pip install ccxt pandas numpy requests openai python-dotenv flask sqlalchemy
```

### 3. Upload files to server (from your local machine)
Download these files from Replit and upload to your server:

**Core Files (Must Have):**
- `nexus_okx_pro_gpt4o.py`
- `serbian_deployment/.env_okx` ← (Contains your new OpenAI key)
- `serbian_deployment/start_live_bot.py`
- `serbian_deployment/check_openai_models.py`

**AI Modules:**
- `ai_core_langchain.py`
- `strategy_selector.py`
- `futures_handler.py`
- `margin_handler.py`
- `failsafe.py`

**Config Files:**
- `config_autonomous.json`
- `leverage_profile.json`
- `failsafe_config.json`

**Monitoring:**
- `check_balance.py`
- `monitor_bot_performance.py`

### 4. Upload using SCP (alternative)
```bash
# From your local machine where files are downloaded
scp nexus_okx_pro_gpt4o.py root@185.241.214.234:/opt/nexus-trading/
scp serbian_deployment/.env_okx root@185.241.214.234:/opt/nexus-trading/.env_okx
scp serbian_deployment/start_live_bot.py root@185.241.214.234:/opt/nexus-trading/
scp ai_core_langchain.py root@185.241.214.234:/opt/nexus-trading/
scp strategy_selector.py root@185.241.214.234:/opt/nexus-trading/
scp futures_handler.py root@185.241.214.234:/opt/nexus-trading/
scp margin_handler.py root@185.241.214.234:/opt/nexus-trading/
scp failsafe.py root@185.241.214.234:/opt/nexus-trading/
scp config_autonomous.json root@185.241.214.234:/opt/nexus-trading/
scp leverage_profile.json root@185.241.214.234:/opt/nexus-trading/
scp check_balance.py root@185.241.214.234:/opt/nexus-trading/
scp serbian_deployment/check_openai_models.py root@185.241.214.234:/opt/nexus-trading/
```

### 5. Test connections on server
```bash
ssh root@185.241.214.234
cd /opt/nexus-trading
source nexus_env/bin/activate

# Test OKX connection
python3 check_balance.py

# Test OpenAI API
python3 check_openai_models.py
```

### 6. Start the bot
```bash
# Start in background
nohup python3 start_live_bot.py > bot.log 2>&1 &

# Or use screen session
screen -S nexus_bot
python3 start_live_bot.py
# Press Ctrl+A, D to detach
```

### 7. Monitor the bot
```bash
# View logs
tail -f bot.log

# Check bot status
python3 monitor_bot_performance.py

# Check balance
python3 check_balance.py
```

## IMPORTANT NOTES

✅ **OpenAI API Key**: Updated and verified working
✅ **OKX API Keys**: Already configured for live trading
✅ **Trading Balance**: $148.50 USDT ready
✅ **Bot Configuration**: 3-minute cycles, 6% position sizing

The bot will trade autonomously with GPT-4o analysis once started on your Serbian server.

## TROUBLESHOOTING

If you encounter any issues:
1. Check API connections with the test scripts
2. Verify file permissions: `chmod +x *.py`
3. Ensure virtual environment is activated
4. Check logs for detailed error messages

The deployment package is ready - all files contain the updated OpenAI API key and are configured for immediate live trading.