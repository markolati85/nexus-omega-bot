#!/usr/bin/env python3
"""
NEXUS OKX PRO AUTONOMOUS LAUNCHER v6.0
Complete deployment and launch system for autonomous trading bot
"""

import os
import sys
import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def check_dependencies():
    """Check and install required dependencies"""
    
    required_packages = [
        'ccxt',
        'openai', 
        'python-dotenv',
        'requests'
    ]
    
    logging.info("🔧 Checking dependencies...")
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logging.info(f"✅ {package} - installed")
        except ImportError:
            logging.info(f"📦 Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
            logging.info(f"✅ {package} - installed successfully")

def check_files():
    """Check if all required files exist"""
    
    required_files = [
        'nexus_okx_pro_gpt4o.py',
        '.env_okx',
        'config_autonomous.json',
        'leverage_profile.json',
        'strategy_selector.py',
        'ai_core_langchain.py',
        'futures_handler.py',
        'margin_handler.py',
        'opportunity_shift_engine.py',
        'auto_transfer_handler.py',
        'failsafe.py'
    ]
    
    logging.info("📋 Checking required files...")
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            logging.info(f"✅ {file} - found")
        else:
            logging.error(f"❌ {file} - missing")
            missing_files.append(file)
    
    if missing_files:
        logging.error(f"❌ Missing files: {missing_files}")
        return False
    
    logging.info("✅ All required files present")
    return True

def check_api_credentials():
    """Check API credentials are configured"""
    
    from dotenv import load_dotenv
    load_dotenv('.env_okx')
    
    okx_key = os.getenv('OKX_API_KEY')
    okx_secret = os.getenv('OKX_SECRET')
    okx_passphrase = os.getenv('OKX_PASSPHRASE')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not all([okx_key, okx_secret, okx_passphrase]):
        logging.error("❌ OKX API credentials missing")
        return False
    
    if not openai_key:
        logging.warning("⚠️ OpenAI API key missing - AI features will be limited")
    
    # Mask credentials for logging
    masked_okx_key = okx_key[:8] + '...' + okx_key[-4:] if okx_key else 'None'
    masked_openai = openai_key[:10] + '...' if openai_key else 'None'
    
    logging.info(f"🔑 OKX API Key: {masked_okx_key}")
    logging.info(f"🤖 OpenAI Key: {masked_openai}")
    
    return True

def test_okx_connection():
    """Test OKX API connection"""
    
    try:
        logging.info("🔗 Testing OKX connection...")
        
        import ccxt
        from dotenv import load_dotenv
        load_dotenv('.env_okx')
        
        client = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'enableRateLimit': True
        })
        
        # Test with account balance call
        balance = client.fetch_balance()
        total_usdt = balance.get('USDT', {}).get('total', 0)
        
        logging.info(f"✅ OKX connection successful")
        logging.info(f"💰 Account Balance: ${total_usdt:.2f} USDT")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ OKX connection failed: {e}")
        return False

def launch_autonomous_bot():
    """Launch the autonomous trading bot"""
    
    logging.info("🚀 LAUNCHING NEXUS OKX PRO AUTONOMOUS v6.0")
    logging.info("=" * 80)
    logging.info("🤖 GPT-4o Powered Trading Bot")
    logging.info("📊 Spot + Margin + Futures Integration")
    logging.info("⚡ Up to 125x Leverage")
    logging.info("🛡️ Advanced Risk Management")
    logging.info("🔄 Opportunity Detection Engine")
    logging.info("💱 Auto-Transfer System")
    logging.info("=" * 80)
    
    try:
        # Import and run the bot
        sys.path.append('.')
        from nexus_okx_pro_gpt4o import main
        
        logging.info("🎯 Starting autonomous trading mode...")
        main()
        
    except KeyboardInterrupt:
        logging.info("🛑 Bot stopped by user")
    except Exception as e:
        logging.error(f"❌ Bot execution error: {e}")
        raise

def deploy_to_server():
    """Deploy to Serbian server"""
    
    server = "root@185.241.214.234"
    password = "Simanovci1"
    
    logging.info("🌍 Deploying to Serbian server...")
    
    files_to_upload = [
        'nexus_okx_pro_gpt4o.py',
        '.env_okx',
        'config_autonomous.json',
        'leverage_profile.json',
        'strategy_selector.py',
        'ai_core_langchain.py',
        'futures_handler.py',
        'margin_handler.py',
        'opportunity_shift_engine.py',
        'auto_transfer_handler.py',
        'failsafe.py',
        'launch_autonomous_okx_pro.py'
    ]
    
    try:
        # Upload all files
        for file in files_to_upload:
            cmd = f"sshpass -p '{password}' scp {file} {server}:/opt/nexus-trading/"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info(f"✅ Uploaded {file}")
            else:
                logging.error(f"❌ Failed to upload {file}: {result.stderr}")
        
        # Install dependencies on server
        install_cmd = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no {server} 'cd /opt/nexus-trading && pip install ccxt openai python-dotenv requests'"
        subprocess.run(install_cmd, shell=True)
        
        # Set permissions
        chmod_cmd = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no {server} 'chmod +x /opt/nexus-trading/*.py'"
        subprocess.run(chmod_cmd, shell=True)
        
        logging.info("✅ Deployment to server completed")
        logging.info("🚀 To run on server: ssh root@185.241.214.234")
        logging.info("📂 cd /opt/nexus-trading")
        logging.info("▶️  python3 launch_autonomous_okx_pro.py")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Server deployment failed: {e}")
        return False

def main():
    """Main launcher function"""
    
    print("🚀 NEXUS OKX PRO AUTONOMOUS LAUNCHER v6.0")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'deploy':
        # Deploy to server mode
        if check_files():
            deploy_to_server()
        return
    
    # Local launch mode
    logging.info("🔧 Pre-flight checks...")
    
    # Check dependencies
    check_dependencies()
    
    # Check files
    if not check_files():
        logging.error("❌ Missing required files - cannot launch")
        return
    
    # Check credentials
    if not check_api_credentials():
        logging.error("❌ API credentials not configured - cannot launch")
        return
    
    # Test connection
    if not test_okx_connection():
        logging.error("❌ OKX connection failed - cannot launch")
        return
    
    logging.info("✅ All pre-flight checks passed")
    
    # Launch bot
    launch_autonomous_bot()

if __name__ == "__main__":
    main()