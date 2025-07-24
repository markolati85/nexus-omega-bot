# NEXUS BOT SERBIAN SERVER DEPLOYMENT GUIDE

## SERVER DETAILS
- **IP**: 185.241.214.234
- **Access**: SSH root access
- **OS**: Ubuntu/Debian recommended
- **Purpose**: 24/7 autonomous trading bot operation

## REQUIRED FILES TO UPLOAD

### Core Trading Bot Files
1. **nexus_okx_pro_gpt4o.py** - Main trading bot engine
2. **start_live_bot.py** - Bot launcher script
3. **launch_autonomous_okx_pro.py** - Alternative launcher
4. **.env_okx** - Environment variables (API keys)

### AI and Strategy Modules
5. **ai_core_langchain.py** - GPT-4o decision engine
6. **strategy_selector.py** - Trading strategy selection
7. **futures_handler.py** - Futures trading module
8. **margin_handler.py** - Margin trading module
9. **auto_transfer_handler.py** - Wallet management
10. **opportunity_shift_engine.py** - Capital reallocation
11. **failsafe.py** - Risk management system

### Configuration Files
12. **config_autonomous.json** - Bot configuration
13. **leverage_profile.json** - Leverage settings
14. **failsafe_config.json** - Safety parameters

### Monitoring and Control
15. **monitor_bot_performance.py** - Performance monitoring
16. **check_live_status.py** - Status checker
17. **check_balance.py** - Balance verification
18. **bot_assessment.py** - Performance assessment

## DEPLOYMENT COMMANDS

### 1. Connect to Server
```bash
ssh root@185.241.214.234
```

### 2. Create Bot Directory
```bash
mkdir -p /opt/nexus-trading
cd /opt/nexus-trading
```

### 3. Install Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Python and pip
apt install python3 python3-pip python3-venv git -y

# Create virtual environment
python3 -m venv nexus_env
source nexus_env/bin/activate

# Install required packages
pip install ccxt pandas numpy requests openai python-dotenv sqlite3
pip install flask sqlalchemy websocket-client
```

### 4. Upload Files (from your local machine)
```bash
# Upload all files to server
scp nexus_okx_pro_gpt4o.py root@185.241.214.234:/opt/nexus-trading/
scp start_live_bot.py root@185.241.214.234:/opt/nexus-trading/
scp .env_okx root@185.241.214.234:/opt/nexus-trading/
scp ai_core_langchain.py root@185.241.214.234:/opt/nexus-trading/
scp strategy_selector.py root@185.241.214.234:/opt/nexus-trading/
scp futures_handler.py root@185.241.214.234:/opt/nexus-trading/
scp margin_handler.py root@185.241.214.234:/opt/nexus-trading/
scp auto_transfer_handler.py root@185.241.214.234:/opt/nexus-trading/
scp opportunity_shift_engine.py root@185.241.214.234:/opt/nexus-trading/
scp failsafe.py root@185.241.214.234:/opt/nexus-trading/
scp config_autonomous.json root@185.241.214.234:/opt/nexus-trading/
scp leverage_profile.json root@185.241.214.234:/opt/nexus-trading/
scp failsafe_config.json root@185.241.214.234:/opt/nexus-trading/
scp monitor_bot_performance.py root@185.241.214.234:/opt/nexus-trading/
scp check_live_status.py root@185.241.214.234:/opt/nexus-trading/
scp check_balance.py root@185.241.214.234:/opt/nexus-trading/
scp bot_assessment.py root@185.241.214.234:/opt/nexus-trading/
```

### 5. Set Permissions
```bash
cd /opt/nexus-trading
chmod +x *.py
chown -R root:root /opt/nexus-trading
```

### 6. Test Connection
```bash
source nexus_env/bin/activate
python3 check_balance.py
```

### 7. Start Bot
```bash
# Background execution
nohup python3 start_live_bot.py > bot.log 2>&1 &

# Or screen session
screen -S nexus_bot
python3 start_live_bot.py
# Ctrl+A, D to detach
```

### 8. Create Systemd Service (Optional)
```bash
# Create service file
cat > /etc/systemd/system/nexus-bot.service << EOF
[Unit]
Description=Nexus Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/nexus-trading
Environment=PATH=/opt/nexus-trading/nexus_env/bin
ExecStart=/opt/nexus-trading/nexus_env/bin/python start_live_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable nexus-bot
systemctl start nexus-bot
```

## MONITORING COMMANDS

### Check Bot Status
```bash
cd /opt/nexus-trading
source nexus_env/bin/activate
python3 check_live_status.py
python3 monitor_bot_performance.py
```

### View Logs
```bash
tail -f bot.log
# Or for systemd service
journalctl -u nexus-bot -f
```

### Check Process
```bash
ps aux | grep start_live_bot
```

### Stop Bot
```bash
# Kill process
pkill -f start_live_bot
# Or stop service
systemctl stop nexus-bot
```

## IMPORTANT NOTES

1. **Environment Variables**: Ensure .env_okx contains valid OKX API credentials
2. **Firewall**: Server should allow outbound HTTPS connections to OKX and OpenAI
3. **Monitoring**: Check logs regularly for trading activity and errors
4. **Balance**: Confirm $148.50 USDT is available before starting
5. **Backup**: Keep backups of configuration files and trading database

## TROUBLESHOOTING

### Connection Issues
- Verify API keys in .env_okx
- Check internet connectivity
- Confirm OKX API permissions

### Bot Not Trading
- Check balance with check_balance.py
- Verify market conditions
- Review AI confidence thresholds

### Performance Issues
- Monitor CPU and memory usage
- Check log file sizes
- Restart bot if needed

The bot will run continuously on your Serbian server, trading autonomously with GPT-4o analysis every 3 minutes.