#!/bin/bash

# Nexus Bot Serbian Server Deployment Commands
# Server: 185.241.214.234
# Complete deployment script

echo "NEXUS BOT SERBIAN SERVER DEPLOYMENT"
echo "===================================="
echo "Server: 185.241.214.234"
echo "Directory: /opt/nexus-trading"
echo ""

# 1. Connect to server and setup environment
echo "Step 1: Setting up server environment..."
ssh root@185.241.214.234 << 'EOF'
    # Create directories
    mkdir -p /opt/nexus-trading
    cd /opt/nexus-trading
    
    # Update system
    apt update && apt upgrade -y
    
    # Install required packages
    apt install python3 python3-pip python3-venv git screen htop -y
    
    # Create virtual environment
    python3 -m venv nexus_env
    source nexus_env/bin/activate
    
    # Install Python dependencies
    pip install --upgrade pip
    pip install ccxt pandas numpy requests openai python-dotenv
    pip install flask sqlalchemy websocket-client
    pip install datetime sqlite3
    
    echo "Server environment setup complete"
EOF

echo "Step 1 complete ✅"

# 2. Upload all required files
echo ""
echo "Step 2: Uploading bot files..."

# Core bot files
scp nexus_okx_pro_gpt4o.py root@185.241.214.234:/opt/nexus-trading/
scp start_live_bot.py root@185.241.214.234:/opt/nexus-trading/
scp launch_autonomous_okx_pro.py root@185.241.214.234:/opt/nexus-trading/

# Environment and config (with updated OpenAI key)
scp serbian_deployment/.env_okx root@185.241.214.234:/opt/nexus-trading/.env_okx
scp config_autonomous.json root@185.241.214.234:/opt/nexus-trading/
scp leverage_profile.json root@185.241.214.234:/opt/nexus-trading/
scp failsafe_config.json root@185.241.214.234:/opt/nexus-trading/

# AI and strategy modules
scp ai_core_langchain.py root@185.241.214.234:/opt/nexus-trading/
scp strategy_selector.py root@185.241.214.234:/opt/nexus-trading/
scp futures_handler.py root@185.241.214.234:/opt/nexus-trading/
scp margin_handler.py root@185.241.214.234:/opt/nexus-trading/
scp auto_transfer_handler.py root@185.241.214.234:/opt/nexus-trading/
scp opportunity_shift_engine.py root@185.241.214.234:/opt/nexus-trading/
scp failsafe.py root@185.241.214.234:/opt/nexus-trading/

# Monitoring tools
scp monitor_bot_performance.py root@185.241.214.234:/opt/nexus-trading/
scp check_live_status.py root@185.241.214.234:/opt/nexus-trading/
scp check_balance.py root@185.241.214.234:/opt/nexus-trading/
scp bot_assessment.py root@185.241.214.234:/opt/nexus-trading/
scp serbian_deployment/check_openai_models.py root@185.241.214.234:/opt/nexus-trading/
scp serbian_deployment/start_live_bot.py root@185.241.214.234:/opt/nexus-trading/

echo "Step 2 complete ✅"

# 3. Set permissions and test
echo ""
echo "Step 3: Setting permissions and testing..."
ssh root@185.241.214.234 << 'EOF'
    cd /opt/nexus-trading
    
    # Set permissions
    chmod +x *.py
    chown -R root:root /opt/nexus-trading
    
    # Test connections
    source nexus_env/bin/activate
    echo "Testing OKX connection..."
    python3 check_balance.py
    echo ""
    echo "Testing OpenAI API..."
    python3 check_openai_models.py
    
    echo "Files deployed:"
    ls -la
EOF

echo "Step 3 complete ✅"

# 4. Create systemd service
echo ""
echo "Step 4: Creating systemd service..."

# Create service file locally
cat > nexus-bot.service << 'EOF'
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

# Upload and configure service
scp nexus-bot.service root@185.241.214.234:/etc/systemd/system/
rm nexus-bot.service

ssh root@185.241.214.234 << 'EOF'
    # Configure service
    systemctl daemon-reload
    systemctl enable nexus-bot
    
    echo "Systemd service created and enabled"
EOF

echo "Step 4 complete ✅"

# 5. Start the bot
echo ""
echo "Step 5: Starting the bot..."
ssh root@185.241.214.234 << 'EOF'
    cd /opt/nexus-trading
    
    # Start service
    systemctl start nexus-bot
    
    # Wait a moment
    sleep 5
    
    # Check status
    echo "Bot service status:"
    systemctl status nexus-bot --no-pager
    
    echo ""
    echo "Live trading status:"
    source nexus_env/bin/activate
    python3 check_live_status.py
EOF

echo "Step 5 complete ✅"

echo ""
echo "===================================="
echo "DEPLOYMENT COMPLETE! ✅"
echo "===================================="
echo ""
echo "Your Nexus bot is now running on the Serbian server!"
echo ""
echo "Monitoring commands:"
echo "ssh root@185.241.214.234 'journalctl -u nexus-bot -f'"
echo "ssh root@185.241.214.234 'cd /opt/nexus-trading && source nexus_env/bin/activate && python3 monitor_bot_performance.py'"
echo ""
echo "Control commands:"
echo "ssh root@185.241.214.234 'systemctl stop nexus-bot'    # Stop bot"
echo "ssh root@185.241.214.234 'systemctl start nexus-bot'   # Start bot"
echo "ssh root@185.241.214.234 'systemctl restart nexus-bot' # Restart bot"
echo ""
echo "The bot will run 24/7 and auto-restart if it crashes."
echo "Trading with $148.50 USDT using GPT-4o analysis every 3 minutes."