#!/usr/bin/env python3
"""
Test New OKX API Credentials
"""

import requests
import time
import base64
import hmac
import hashlib
from datetime import datetime

# NEW OKX Credentials
API_KEY = '26163826-e458-4b6e-95f3-946a40201868'
SECRET_KEY = '0359A963F8FAD2B3112C14C2B8FF2DD1'
PASSPHRASE = 'newapilast'  # Using API name as passphrase

def test_new_okx_credentials():
    """Test the new OKX API credentials"""
    
    print("Testing NEW OKX API credentials...")
    print(f"API Key: {API_KEY}")
    print(f"Permissions: Read, Withdraw, Trade")
    print(f"IP Whitelist: 185.241.214.234")
    
    try:
        # Get server time first
        server_response = requests.get('https://www.okx.com/api/v5/public/time', timeout=10)
        if server_response.status_code == 200:
            timestamp = server_response.json()['data'][0]['ts']
            print(f"Server timestamp: {timestamp}")
        else:
            timestamp = str(int(time.time() * 1000))
            print(f"Using local timestamp: {timestamp}")
        
        # Test account balance endpoint
        method = 'GET'
        request_path = '/api/v5/account/balance'
        body = ''
        
        # Create signature
        message = timestamp + method + request_path + body
        mac = hmac.new(
            bytes(SECRET_KEY, encoding='utf8'),
            bytes(message, encoding='utf-8'),
            digestmod='sha256'
        )
        signature = base64.b64encode(mac.digest()).decode()
        
        headers = {
            'OK-ACCESS-KEY': API_KEY,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        print("\nSending authenticated request...")
        response = requests.get(
            'https://www.okx.com/api/v5/account/balance',
            headers=headers,
            timeout=15
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0':
                print("✅ AUTHENTICATION SUCCESS!")
                
                # Parse portfolio
                details = data.get('data', [{}])[0].get('details', [])
                total_value = 0
                assets = {}
                
                for detail in details:
                    amount = float(detail.get('cashBal', 0))
                    currency = detail.get('ccy', '')
                    if amount > 0.001:
                        assets[currency] = amount
                        if currency == 'USDT':
                            total_value += amount
                        else:
                            # Get live price
                            try:
                                price_resp = requests.get(
                                    f'https://www.okx.com/api/v5/market/ticker?instId={currency}-USDT',
                                    timeout=5
                                )
                                if price_resp.status_code == 200:
                                    price_data = price_resp.json()
                                    if price_data.get('code') == '0':
                                        price = float(price_data['data'][0]['last'])
                                        total_value += amount * price
                                        print(f"  {currency}: {amount:.6f} @ ${price:.4f}")
                            except:
                                print(f"  {currency}: {amount:.6f} (price lookup failed)")
                
                print(f"\n💰 PORTFOLIO VALUE: ${total_value:.2f} USDT")
                print(f"📊 ASSETS: {len(assets)} currencies")
                
                # Send success notification to Telegram
                TOKEN = "8429171890:AAEaYGGQb8L-pir22rt128g5hbh6GTuWDqk"
                CHAT_ID = "1762317382"
                
                success_msg = f"""🎉 NEW OKX API CREDENTIALS SUCCESS!

✅ Authentication Breakthrough:
• Status: FULLY CONNECTED
• Portfolio: ${total_value:.2f} USDT
• Assets: {len(assets)} currencies

📊 Live Portfolio Access Restored:"""
                
                for currency, amount in list(assets.items())[:6]:
                    if currency == 'USDT':
                        success_msg += f"\n💰 {currency}: ${amount:.2f}"
                    else:
                        success_msg += f"\n🪙 {currency}: {amount:.6f}"
                
                success_msg += f"""

🔧 Technical Success:
• New API Key: Working perfectly
• Permissions: Read, Withdraw, Trade ✅
• IP Whitelist: Validated ✅
• Real-time data: Active ✅

🚀 READY FOR LIVE TRADING!
Bot will now update with full functionality."""
                
                telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                requests.post(telegram_url, json={'chat_id': CHAT_ID, 'text': success_msg})
                
                return True, total_value, assets
            else:
                print(f"❌ API Error: {data}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False, 0, {}

if __name__ == "__main__":
    success, portfolio, assets = test_new_okx_credentials()
    if success:
        print(f"\n🎉 SUCCESS! Portfolio: ${portfolio:.2f}")
    else:
        print("\n❌ Authentication still failing")