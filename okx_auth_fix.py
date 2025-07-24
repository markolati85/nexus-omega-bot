#!/usr/bin/env python3
"""
OKX Authentication Fix and Portfolio Retrieval
"""

import requests
import time
import base64
import hmac
import hashlib
import json

# OKX Credentials
API_KEY = 'bfee3fff-cdf1-4b71-9ef9-8760de8732f4'
SECRET_KEY = 'E7C2058E8DC095D3F45F5C37D6A28DC8'
PASSPHRASE = 'Okx123#'

def test_okx_authentication():
    """Test different authentication methods"""
    
    print("Testing OKX API authentication methods...")
    
    # Method 1: Server time sync
    try:
        print("\n1. Getting OKX server time...")
        time_response = requests.get('https://www.okx.com/api/v5/public/time', timeout=10)
        if time_response.status_code == 200:
            server_time = time_response.json()['data'][0]['ts']
            print(f"Server time: {server_time}")
        else:
            server_time = str(int(time.time() * 1000))
            print(f"Using local time: {server_time}")
    except:
        server_time = str(int(time.time() * 1000))
        print(f"Fallback to local time: {server_time}")
    
    # Method 2: Test with account balance endpoint
    try:
        print("\n2. Testing account balance API...")
        
        method = 'GET'
        request_path = '/api/v5/account/balance'
        body = ''
        
        # Create signature
        message = server_time + method + request_path + body
        mac = hmac.new(
            bytes(SECRET_KEY, encoding='utf8'),
            bytes(message, encoding='utf-8'),
            digestmod='sha256'
        )
        signature = base64.b64encode(mac.digest()).decode()
        
        headers = {
            'OK-ACCESS-KEY': API_KEY,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': server_time,
            'OK-ACCESS-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        print("Headers created:")
        for key, value in headers.items():
            if key != 'OK-ACCESS-SIGN':
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value[:10]}...")
        
        response = requests.get(
            'https://www.okx.com/api/v5/account/balance',
            headers=headers,
            timeout=15
        )
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0':
                print("✅ Authentication successful!")
                
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
                            # Estimate value for non-USDT assets
                            estimated_prices = {
                                'BTC': 118000, 'ETH': 3200, 'SOL': 198,
                                'BNB': 710, 'XRP': 2.65, 'DOGE': 0.38
                            }
                            price = estimated_prices.get(currency, 1)
                            total_value += amount * price
                
                print(f"\n💰 Portfolio Value: ${total_value:.2f}")
                print("📊 Assets:")
                for currency, amount in assets.items():
                    if currency == 'USDT':
                        print(f"  • {currency}: ${amount:.2f}")
                    else:
                        print(f"  • {currency}: {amount:.6f}")
                
                return total_value, assets
            else:
                print(f"❌ API Error: {data}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Method 3: Try with different timestamp
    try:
        print("\n3. Testing with current timestamp...")
        current_time = str(int(time.time() * 1000))
        
        message = current_time + method + request_path + body
        mac = hmac.new(
            bytes(SECRET_KEY, encoding='utf8'),
            bytes(message, encoding='utf-8'),
            digestmod='sha256'
        )
        signature = base64.b64encode(mac.digest()).decode()
        
        headers = {
            'OK-ACCESS-KEY': API_KEY,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': current_time,
            'OK-ACCESS-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://www.okx.com/api/v5/account/balance',
            headers=headers,
            timeout=15
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0':
                print("✅ Current timestamp method works!")
                return True
            else:
                print(f"API Error: {data}")
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")
    
    return False, {}

if __name__ == "__main__":
    test_okx_authentication()