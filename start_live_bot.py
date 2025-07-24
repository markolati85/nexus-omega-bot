#!/usr/bin/env python3
"""
Nexus Live Bot Launcher for Serbian Server
Starts the live trading bot with updated API keys
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env_okx')

def main():
    print("NEXUS OKX PRO - SERBIAN SERVER LAUNCHER")
    print("=" * 50)
    print(f"Launch Time: {datetime.now()}")
    print("Mode: LIVE TRADING (Real Money)")
    print()
    
    # Check API keys
    okx_key = os.getenv('OKX_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not okx_key or not openai_key:
        print("❌ Missing API keys in .env_okx file")
        print("Required: OKX_API_KEY, OPENAI_API_KEY")
        return False
    
    print("✅ API Keys loaded")
    print(f"OKX: {okx_key[:8]}...")
    print(f"OpenAI: {openai_key[:20]}...")
    print()
    
    # Start the main trading bot
    try:
        print("🚀 Starting Nexus trading bot...")
        subprocess.run([sys.executable, "nexus_okx_pro_gpt4o.py"], check=True)
    except KeyboardInterrupt:
        print("\n⚠️  Bot stopped by user")
        return True
    except Exception as e:
        print(f"❌ Bot failed: {e}")
        return False

if __name__ == "__main__":
    main()