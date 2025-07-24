#!/usr/bin/env python3
"""
OKX Timing Fix - Solve timestamp synchronization issues
"""

import requests
import time
import base64
import hmac
import hashlib
import ntplib
from datetime import datetime

# OKX Credentials
API_KEY = 'bfee3fff-cdf1-4b71-9ef9-8760de8732f4'
SECRET_KEY = 'E7C2058E8DC095D3F45F5C37D6A28DC8'
PASSPHRASE = 'Okx123#'

def get_precise_timestamp():
    """Get precise timestamp using multiple methods"""
    methods = []
    
    # Method 1: NTP time
    try:
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org', version=3)
        ntp_time = int(response.tx_time * 1000)
        methods.append(('NTP', ntp_time))
    except:
        pass
    
    # Method 2: OKX server time
    try:
        response = requests.get('https://www.okx.com/api/v5/public/time', timeout=5)
        if response.status_code == 200:
            server_time = int(response.json()['data'][0]['ts'])
            methods.append(('OKX_SERVER', server_time))
    except:
        pass
    
    # Method 3: Local time
    local_time = int(time.time() * 1000)
    methods.append(('LOCAL', local_time))
    
    # Method 4: Adjusted local time (account for network delay)
    adjusted_time = int((time.time() + 0.5) * 1000)  # Add 500ms for network delay
    methods.append(('ADJUSTED', adjusted_time))
    
    return methods

def test_portfolio_with_timing():
    """Test portfolio retrieval with different timing methods"""
    timestamp_methods = get_precise_timestamp()
    
    print(f"Testing {len(timestamp_methods)} timestamp methods...")
    
    for method_name, timestamp in timestamp_methods:
        print(f"\n📅 Testing {method_name} timestamp: {timestamp}")
        print(f"   Time: {datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            method = 'GET'
            request_path = '/api/v5/account/balance'
            body = ''
            
            # Create signature
            message = str(timestamp) + method + request_path + body
            mac = hmac.new(
                bytes(SECRET_KEY, encoding='utf8'),
                bytes(message, encoding='utf-8'),
                digestmod='sha256'
            )
            signature = base64.b64encode(mac.digest()).decode()
            
            headers = {
                'OK-ACCESS-KEY': API_KEY,
                'OK-ACCESS-SIGN': signature,
                'OK-ACCESS-TIMESTAMP': str(timestamp),
                'OK-ACCESS-PASSPHRASE': PASSPHRASE,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://www.okx.com/api/v5/account/balance',
                headers=headers,
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0':
                    print(f"   ✅ SUCCESS with {method_name}!")
                    
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
                                # Estimate value
                                price_map = {
                                    'BTC': 118000, 'ETH': 3200, 'SOL': 198,
                                    'BNB': 710, 'XRP': 2.65, 'DOGE': 0.38
                                }
                                price = price_map.get(currency, 1)
                                total_value += amount * price
                    
                    print(f"   💰 Portfolio: ${total_value:.2f}")
                    print(f"   📊 Assets: {len(assets)} currencies")
                    
                    # Send success to Telegram
                    TOKEN = "8429171890:AAEaYGGQb8L-pir22rt128g5hbh6GTuWDqk"
                    CHAT_ID = "1762317382"
                    
                    success_msg = f"""🎯 OKX CONNECTION SUCCESS!

✅ Authentication Fixed:
• Method: {method_name} timestamp
• Status: Connected and authenticated
• Portfolio: ${total_value:.2f} USDT

📊 Live Portfolio Data:"""
                    
                    for currency, amount in list(assets.items())[:5]:
                        if currency == 'USDT':
                            success_msg += f"\n• {currency}: ${amount:.2f}"
                        else:
                            success_msg += f"\n• {currency}: {amount:.6f}"
                    
                    success_msg += f"""

🔧 Technical Details:
• Timestamp sync: {method_name}
• API response: Success (200)
• Data retrieval: Complete

Try /status now - should show real portfolio!"""
                    
                    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(telegram_url, json={'chat_id': CHAT_ID, 'text': success_msg}, timeout=10)
                    
                    return True, method_name, total_value, assets
                else:
                    print(f"   ❌ API Error: {data}")
            else:
                error_data = response.text
                print(f"   ❌ HTTP Error: {error_data}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return False, None, 0, {}

if __name__ == "__main__":
    print("🔧 OKX Timing Fix - Solving timestamp synchronization...")
    success, method, portfolio, assets = test_portfolio_with_timing()
    
    if success:
        print(f"\n🎉 SUCCESS! Working method: {method}")
        print(f"💰 Portfolio Value: ${portfolio:.2f}")
    else:
        print("\n❌ All timestamp methods failed")
        print("Need to investigate API credentials or permissions")