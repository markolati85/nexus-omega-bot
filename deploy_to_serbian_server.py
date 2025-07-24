#!/usr/bin/env python3
"""
Deploy Nexus Bot to Serbian Server
Automated deployment script
"""

import os
import subprocess
import sys

SERVER_IP = "185.241.214.234"
SERVER_USER = "root"
BOT_DIR = "/opt/nexus-trading"

# Files to upload
REQUIRED_FILES = [
    "nexus_okx_pro_gpt4o.py",
    "start_live_bot.py", 
    "launch_autonomous_okx_pro.py",
    ".env_okx",
    "ai_core_langchain.py",
    "strategy_selector.py",
    "futures_handler.py",
    "margin_handler.py",
    "auto_transfer_handler.py",
    "opportunity_shift_engine.py",
    "failsafe.py",
    "config_autonomous.json",
    "leverage_profile.json",
    "failsafe_config.json",
    "monitor_bot_performance.py",
    "check_live_status.py",
    "check_balance.py",
    "bot_assessment.py"
]

def run_command(command, description):
    """Execute command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def check_files():
    """Check if all required files exist"""
    print("Checking required files...")
    missing_files = []
    
    for file in REQUIRED_FILES:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"\n❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    return True

def setup_server():
    """Setup server environment"""
    commands = [
        (f"ssh {SERVER_USER}@{SERVER_IP} 'mkdir -p {BOT_DIR}'", "Create bot directory"),
        (f"ssh {SERVER_USER}@{SERVER_IP} 'apt update && apt upgrade -y'", "Update system"),
        (f"ssh {SERVER_USER}@{SERVER_IP} 'apt install python3 python3-pip python3-venv git -y'", "Install Python"),
        (f"ssh {SERVER_USER}@{SERVER_IP} 'cd {BOT_DIR} && python3 -m venv nexus_env'", "Create virtual environment"),
        (f"ssh {SERVER_USER}@{SERVER_IP} 'cd {BOT_DIR} && source nexus_env/bin/activate && pip install ccxt pandas numpy requests openai python-dotenv flask sqlalchemy websocket-client'", "Install dependencies")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def upload_files():
    """Upload all bot files to server"""
    print("Uploading files to server...")
    
    for file in REQUIRED_FILES:
        command = f"scp {file} {SERVER_USER}@{SERVER_IP}:{BOT_DIR}/"
        if not run_command(command, f"Upload {file}"):
            return False
    
    # Set permissions
    command = f"ssh {SERVER_USER}@{SERVER_IP} 'cd {BOT_DIR} && chmod +x *.py && chown -R root:root {BOT_DIR}'"
    return run_command(command, "Set file permissions")

def test_deployment():
    """Test bot deployment"""
    print("Testing deployment...")
    
    commands = [
        (f"ssh {SERVER_USER}@{SERVER_IP} 'cd {BOT_DIR} && source nexus_env/bin/activate && python3 check_balance.py'", "Test OKX connection"),
        (f"ssh {SERVER_USER}@{SERVER_IP} 'cd {BOT_DIR} && ls -la'", "List deployed files")
    ]
    
    for command, description in commands:
        run_command(command, description)

def create_systemd_service():
    """Create systemd service for auto-start"""
    service_content = f"""[Unit]
Description=Nexus Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={BOT_DIR}
Environment=PATH={BOT_DIR}/nexus_env/bin
ExecStart={BOT_DIR}/nexus_env/bin/python start_live_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"""
    
    # Write service file
    with open('nexus-bot.service', 'w') as f:
        f.write(service_content)
    
    commands = [
        (f"scp nexus-bot.service {SERVER_USER}@{SERVER_IP}:/etc/systemd/system/", "Upload service file"),
        (f"ssh {SERVER_USER}@{SERVER_IP} 'systemctl daemon-reload'", "Reload systemd"),
        (f"ssh {SERVER_USER}@{SERVER_IP} 'systemctl enable nexus-bot'", "Enable service"),
    ]
    
    for command, description in commands:
        run_command(command, description)
    
    # Clean up local service file
    os.remove('nexus-bot.service')

def start_bot():
    """Start the trading bot"""
    print("Starting trading bot...")
    
    command = f"ssh {SERVER_USER}@{SERVER_IP} 'cd {BOT_DIR} && systemctl start nexus-bot'"
    run_command(command, "Start bot service")
    
    # Check status
    command = f"ssh {SERVER_USER}@{SERVER_IP} 'systemctl status nexus-bot'"
    run_command(command, "Check bot status")

def main():
    """Main deployment function"""
    print("NEXUS BOT SERBIAN SERVER DEPLOYMENT")
    print("=" * 50)
    print(f"Target Server: {SERVER_IP}")
    print(f"Deployment Directory: {BOT_DIR}")
    print()
    
    # Step 1: Check files
    if not check_files():
        print("❌ File check failed. Please ensure all required files are present.")
        return False
    
    # Step 2: Setup server
    print("\nStep 2: Setting up server environment...")
    if not setup_server():
        print("❌ Server setup failed.")
        return False
    
    # Step 3: Upload files
    print("\nStep 3: Uploading bot files...")
    if not upload_files():
        print("❌ File upload failed.")
        return False
    
    # Step 4: Test deployment
    print("\nStep 4: Testing deployment...")
    test_deployment()
    
    # Step 5: Create service
    print("\nStep 5: Creating systemd service...")
    create_systemd_service()
    
    # Step 6: Start bot
    print("\nStep 6: Starting trading bot...")
    start_bot()
    
    print("\n" + "=" * 50)
    print("✅ DEPLOYMENT COMPLETE")
    print(f"Bot is now running on {SERVER_IP}")
    print(f"Monitor with: ssh {SERVER_USER}@{SERVER_IP} 'journalctl -u nexus-bot -f'")
    print(f"Check status: ssh {SERVER_USER}@{SERVER_IP} 'cd {BOT_DIR} && source nexus_env/bin/activate && python3 check_live_status.py'")
    
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)