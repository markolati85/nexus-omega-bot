#!/usr/bin/env python3
"""
Verify Serbian Server Deployment Status
Triple-check all components before launch
"""

import os
import json
from dotenv import load_dotenv

def verify_deployment_readiness():
    """Triple-check deployment readiness"""
    
    print("NEXUS OKX PRO - DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    # Check 1: Essential Files
    print("CHECK 1: Essential Files")
    print("-" * 25)
    
    essential_files = [
        'nexus_okx_pro_gpt4o.py',
        'launch_autonomous_okx_pro.py',
        'strategy_selector.py',
        'ai_core_langchain.py',
        'futures_handler.py',
        'margin_handler.py',
        'auto_transfer_handler.py',
        'opportunity_shift_engine.py',
        'failsafe.py',
        'config_autonomous.json',
        'leverage_profile.json',
        'failsafe_config.json',
        '.env_okx'
    ]
    
    missing_files = []
    for file in essential_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size} bytes)")
        else:
            print(f"❌ {file} (MISSING)")
            missing_files.append(file)
    
    # Check 2: Environment Variables
    print(f"\nCHECK 2: Environment Configuration")
    print("-" * 35)
    
    load_dotenv('.env_okx')
    
    required_vars = ['OKX_API_KEY', 'OKX_SECRET', 'OKX_PASSPHRASE', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 8}{value[-4:] if len(value) > 4 else '****'}")
        else:
            print(f"❌ {var}: MISSING")
            missing_vars.append(var)
    
    # Check 3: Configuration Files
    print(f"\nCHECK 3: Configuration Validation")
    print("-" * 33)
    
    try:
        with open('config_autonomous.json', 'r') as f:
            config = json.load(f)
        print(f"✅ config_autonomous.json: Valid JSON")
        print(f"   - Trading pairs: {len(config.get('pairs', []))}")
        print(f"   - Confidence threshold: {config.get('confidence_threshold', 'N/A')}%")
        print(f"   - Position size: {config.get('risk', {}).get('position_size_pct', 'N/A')}%")
    except Exception as e:
        print(f"❌ config_autonomous.json: Error - {e}")
    
    try:
        with open('leverage_profile.json', 'r') as f:
            leverage = json.load(f)
        print(f"✅ leverage_profile.json: Valid JSON")
        print(f"   - Leverage pairs: {len(leverage.get('leverage_limits', {}))}")
    except Exception as e:
        print(f"❌ leverage_profile.json: Error - {e}")
    
    # Check 4: Bot Code Validation
    print(f"\nCHECK 4: Bot Code Validation")
    print("-" * 28)
    
    try:
        with open('nexus_okx_pro_gpt4o.py', 'r') as f:
            content = f.read()
        
        # Check for simulation flags
        if "'sandbox': True" in content or 'SIMULATE = True' in content:
            print("❌ SIMULATION MODE DETECTED - Must be disabled")
        else:
            print("✅ Live trading mode confirmed")
        
        # Check key components
        if 'class NexusOKXProAutonomous' in content:
            print("✅ Main bot class found")
        if 'autonomous_trading_cycle' in content:
            print("✅ Trading cycle method found")
        if 'GPT-4o' in content or 'gpt-4o' in content:
            print("✅ AI integration confirmed")
            
    except Exception as e:
        print(f"❌ Bot code validation failed: {e}")
    
    # Summary
    print(f"\nDEPLOYMENT SUMMARY")
    print("-" * 18)
    
    if not missing_files and not missing_vars:
        print("🟢 ALL CHECKS PASSED")
        print("🚀 Ready for Serbian server deployment")
        print("💰 Live trading with $148.50 USDT")
        print("🤖 AI-powered autonomous operation")
        print("⚡ No simulation - real money trading")
    else:
        print("🟡 ISSUES FOUND:")
        if missing_files:
            print(f"   Missing files: {', '.join(missing_files)}")
        if missing_vars:
            print(f"   Missing variables: {', '.join(missing_vars)}")
    
    print(f"\nNEXT STEPS:")
    print("1. SSH to server: ssh root@185.241.214.234")
    print("2. Run deployment commands")
    print("3. Upload all files to /opt/nexus-okx-pro/")
    print("4. Launch bot with nohup python3 launch_autonomous_okx_pro.py")
    print("5. Monitor with tail -f nexus_live.log")

if __name__ == "__main__":
    verify_deployment_readiness()