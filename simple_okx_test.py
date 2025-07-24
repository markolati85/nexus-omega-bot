#!/usr/bin/env python3
"""
Simple OKX Authentication Test - No external dependencies
"""

import requests
import time
import base64
import hmac
import hashlib
from datetime import datetime

# OKX Credentials
API_KEY = 'bfee3fff-cdf1-4b71-9ef9-8760de8732f4'
SECRET_KEY = 'E7C2058E8DC095D3F45F5C37D6A28DC8'
PASSPHRASE = 'Okx123#'

def test_simple_auth():
    """Test OKX authentication with timing adjustments"""
    
    print("Testing OKX authentication with time adjustments...")
    
    # Test multiple timing strategies
    timing_strategies = [
        ("Current time", int(time.time() * 1000)),
        ("Current + 1s", int((time.time() + 1) * 1000)),
        ("Current - 1s", int((time.time() - 1) * 1000)),
        ("Current + 2s", int((time.time() + 2) * 1000)),
    ]
    
    # First get OKX server time
    try:
        print("\n1. Getting OKX server time...")
        server_response = requests.get('https://www.okx.com/api/v5/public/time', timeout=10)
        if server_response.status_code == 200:
            server_time = int(server_response.json()['data'][0]['ts'])
            local_time = int(time.time() * 1000)
            time_diff = server_time - local_time
            print(f"   Server time: {server_time}")
            print(f"   Local time:  {local_time}")
            print(f"   Difference:  {time_diff}ms")
            
            # Add server-adjusted time to strategies
            timing_strategies.insert(0, ("Server time", server_time))
            timing_strategies.insert(1, ("Server +1s", server_time + 1000))
            timing_strategies.insert(2, ("Server -1s", server_time - 1000))
    except Exception as e:
        print(f"   Could not get server time: {e}")
    
    for strategy_name, timestamp in timing_strategies:
        print(f"\n2. Testing {strategy_name}: {timestamp}")
        
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
                timeout=15
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0':
                    print(f"   ✅ SUCCESS!")
                    
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
                                except:
                                    # Fallback prices
                                    prices = {
                                        'BTC': 118000, 'ETH': 3200, 'SOL': 198,
                                        'BNB': 710, 'XRP': 2.65, 'DOGE': 0.38
                                    }
                                    price = prices.get(currency, 1)
                                    total_value += amount * price
                    
                    print(f"   💰 Portfolio: ${total_value:.2f} USDT")
                    print(f"   📊 Assets: {list(assets.keys())}")
                    
                    # Send Telegram notification
                    TOKEN = "8429171890:AAEaYGGQb8L-pir22rt128g5hbh6GTuWDqk"
                    CHAT_ID = "1762317382"
                    
                    success_msg = f"""🎉 OKX API AUTHENTICATION SUCCESS!

✅ Connection Established:
• Method: {strategy_name}
• Portfolio: ${total_value:.2f} USDT
• Assets: {len(assets)} currencies

📊 Live Portfolio:"""
                    
                    for currency, amount in list(assets.items())[:5]:
                        if currency == 'USDT':
                            success_msg += f"\n💰 {currency}: ${amount:.2f}"
                        else:
                            success_msg += f"\n🪙 {currency}: {amount:.6f}"
                    
                    success_msg += f"""

🔧 Technical Fix:
• Timestamp sync: Working
• Authentication: Successful
• Real-time data: Active

Your bot can now access real portfolio data!
Try /status for live updates."""
                    
                    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(telegram_url, json={'chat_id': CHAT_ID, 'text': success_msg})
                    
                    return True, strategy_name, total_value, assets
                else:
                    print(f"   ❌ API Error: {data}")
            else:
                print(f"   ❌ Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n❌ All authentication methods failed")
    
    # Send failure notification
    TOKEN = "8429171890:AAEaYGGQb8L-pir22rt128g5hbh6GTuWDqk"
    CHAT_ID = "1762317382"
    
    fail_msg = """⚠️ OKX API Authentication Status

❌ Issue: All timestamp methods failed
🔍 Possible causes:
• API key permissions insufficient
• Passphrase encoding issue
• Network connectivity problem
• Account restrictions

🔧 Next Steps:
1. Verify API key has trading permissions
2. Check passphrase is exactly correct
3. Ensure IP whitelist includes current IP

Bot remains responsive for all commands, working on alternative solutions..."""
    
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(telegram_url, json={'chat_id': CHAT_ID, 'text': fail_msg})
    
    return False, None, 0, {}

if __name__ == "__main__":
    test_simple_auth()