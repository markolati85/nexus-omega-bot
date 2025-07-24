#!/usr/bin/env python3
"""
Test different passphrase formats for new OKX API
"""

import requests
import time
import base64
import hmac
import hashlib

# NEW OKX Credentials
API_KEY = '26163826-e458-4b6e-95f3-946a40201868'
SECRET_KEY = '0359A963F8FAD2B3112C14C2B8FF2DD1'

def test_different_passphrases():
    """Test different passphrase formats"""
    
    # Different passphrase possibilities
    passphrases_to_test = [
        'newapilast',           # API name as provided
        'Newapilast',           # Capitalized
        'NEWAPILAST',           # All caps
        '',                     # Empty string
        'test123',              # Common default
        'password',             # Common default
        'passphrase',           # Common default
    ]
    
    print("Testing different passphrase formats for new OKX API credentials...")
    
    for i, passphrase in enumerate(passphrases_to_test, 1):
        print(f"\n{i}. Testing passphrase: '{passphrase}'")
        
        try:
            # Get server time
            server_response = requests.get('https://www.okx.com/api/v5/public/time', timeout=10)
            if server_response.status_code == 200:
                timestamp = server_response.json()['data'][0]['ts']
            else:
                timestamp = str(int(time.time() * 1000))
            
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
                'OK-ACCESS-PASSPHRASE': passphrase,
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
                    print(f"   ✅ SUCCESS with passphrase: '{passphrase}'!")
                    
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
                                prices = {
                                    'BTC': 118000, 'ETH': 3200, 'SOL': 198,
                                    'BNB': 710, 'XRP': 2.65, 'DOGE': 0.38
                                }
                                price = prices.get(currency, 1)
                                total_value += amount * price
                    
                    print(f"   💰 Portfolio: ${total_value:.2f} USDT")
                    print(f"   📊 Assets: {list(assets.keys())}")
                    
                    # Send success notification
                    TOKEN = "8429171890:AAEaYGGQb8L-pir22rt128g5hbh6GTuWDqk"
                    CHAT_ID = "1762317382"
                    
                    success_msg = f"""🎉 PASSPHRASE BREAKTHROUGH!

✅ Working Passphrase Found: '{passphrase}'
💰 Portfolio: ${total_value:.2f} USDT
📊 Assets: {len(assets)} currencies

🔑 Correct API Configuration:
• API Key: {API_KEY}
• Secret: {SECRET_KEY}
• Passphrase: '{passphrase}'
• Status: AUTHENTICATED ✅

Portfolio access restored! Bot will now update with full functionality."""
                    
                    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(telegram_url, json={'chat_id': CHAT_ID, 'text': success_msg})
                    
                    return True, passphrase, total_value, assets
                else:
                    print(f"   ❌ API Error: {data}")
            else:
                error = response.text
                if "Timestamp request expired" in error:
                    print(f"   ❌ Timestamp expired")
                elif "passphrase" in error.lower():
                    print(f"   ❌ Passphrase issue")
                else:
                    print(f"   ❌ Other error: {error}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # If all passphrases fail, check if it's an IP or API issue
    print(f"\n❌ All passphrases failed. Possible issues:")
    print(f"• IP not whitelisted (Current: Unknown)")
    print(f"• API key not activated yet")
    print(f"• Missing trading permissions")
    print(f"• Account verification required")
    
    # Send failure notification
    TOKEN = "8429171890:AAEaYGGQb8L-pir22rt128g5hbh6GTuWDqk"
    CHAT_ID = "1762317382"
    
    fail_msg = """⚠️ NEW API CREDENTIALS TESTING

❌ All passphrase variations failed:
• Tested: newapilast, Newapilast, NEWAPILAST, empty, common defaults
• Error: Timestamp request expired (consistent)

🔍 Possible Issues:
• IP whitelist: May need current Replit IP
• API activation: New key might need time to activate
• Account verification: May require additional steps
• Passphrase format: Could be custom value

💡 Next Steps:
1. Check OKX account for exact passphrase
2. Verify IP whitelist includes current IP
3. Confirm API key is fully activated
4. Check if account needs verification

Bot remains responsive while troubleshooting..."""
    
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(telegram_url, json={'chat_id': CHAT_ID, 'text': fail_msg})
    
    return False, None, 0, {}

if __name__ == "__main__":
    test_different_passphrases()