#!/usr/bin/env python3
"""
API Monitor - Continuously test Binance API until it's working
"""
import os
import time
from dotenv import load_dotenv
from binance.client import Client

def test_api():
    load_dotenv()
    client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
    
    attempt = 1
    while True:
        try:
            print(f"\n=== API Test Attempt #{attempt} ===")
            print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Test authenticated call
            account = client.get_account()
            
            print("🎉 API WORKING! Authentication successful!")
            print(f"CanTrade: {account.get('canTrade', False)}")
            print(f"Permissions: {account.get('permissions', [])}")
            
            # Show balances
            balances = [b for b in account['balances'] if float(b['free']) > 0]
            print(f"Active balances: {len(balances)}")
            for b in balances[:5]:
                print(f"  {b['asset']}: {b['free']}")
            
            print("\n✅ READY FOR LIVE TRADING!")
            return True
            
        except Exception as e:
            print(f"❌ API not ready yet: {e}")
            print(f"Waiting 60 seconds before retry...")
            time.sleep(60)
            attempt += 1
            
            if attempt > 30:  # Max 30 minutes
                print("❌ API still not working after 30 minutes")
                return False

if __name__ == "__main__":
    test_api()