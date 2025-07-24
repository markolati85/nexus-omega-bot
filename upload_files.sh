#!/bin/bash

# Upload essential files to Serbian server
echo "Uploading files to Serbian server..."

# Core bot files
scp -o StrictHostKeyChecking=no nexus_okx_pro_gpt4o.py root@185.241.214.234:/opt/nexus-trading/
scp -o StrictHostKeyChecking=no serbian_deployment/start_live_bot.py root@185.241.214.234:/opt/nexus-trading/
scp -o StrictHostKeyChecking=no serbian_deployment/.env_okx root@185.241.214.234:/opt/nexus-trading/

# AI modules  
scp -o StrictHostKeyChecking=no ai_core_langchain.py root@185.241.214.234:/opt/nexus-trading/
scp -o StrictHostKeyChecking=no strategy_selector.py root@185.241.214.234:/opt/nexus-trading/
scp -o StrictHostKeyChecking=no futures_handler.py root@185.241.214.234:/opt/nexus-trading/
scp -o StrictHostKeyChecking=no margin_handler.py root@185.241.214.234:/opt/nexus-trading/
scp -o StrictHostKeyChecking=no failsafe.py root@185.241.214.234:/opt/nexus-trading/

# Config files
scp -o StrictHostKeyChecking=no config_autonomous.json root@185.241.214.234:/opt/nexus-trading/
scp -o StrictHostKeyChecking=no leverage_profile.json root@185.241.214.234:/opt/nexus-trading/

# Monitoring tools
scp -o StrictHostKeyChecking=no check_balance.py root@185.241.214.234:/opt/nexus-trading/
scp -o StrictHostKeyChecking=no serbian_deployment/check_openai_models.py root@185.241.214.234:/opt/nexus-trading/

echo "Files uploaded successfully!"