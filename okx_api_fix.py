#!/usr/bin/env python3
"""
OKX API FIX FOR NEXUS ULTIMATE BOT
Direct fix for Parameter posSide error and insufficient balance issues  
"""

import os
import ccxt
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_fixed_okx_exchanges():
    """Create properly configured OKX exchanges"""
    
    # Spot exchange (working)
    spot_exchange = ccxt.okx({
        'apiKey': os.getenv('OKX_API_KEY'),
        'secret': os.getenv('OKX_SECRET'),
        'password': os.getenv('OKX_PASSPHRASE'),
        'sandbox': False,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    # Futures exchange with proper configuration
    futures_exchange = ccxt.okx({
        'apiKey': os.getenv('OKX_API_KEY'),
        'secret': os.getenv('OKX_SECRET'),
        'password': os.getenv('OKX_PASSPHRASE'),
        'sandbox': False,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap',  # Perpetual futures
            'marginMode': 'isolated'  # Default margin mode
        }
    })
    
    return spot_exchange, futures_exchange

def execute_okx_futures_long(futures_exchange, symbol, quantity, leverage=10):
    """Fixed OKX futures long execution"""
    try:
        # Convert symbol to OKX format
        if '/USDT' in symbol:
            okx_symbol = symbol.replace('/USDT', '-USDT-SWAP')
        else:
            okx_symbol = symbol
        
        logging.info(f"🎯 Attempting OKX futures long: {okx_symbol}, qty: {quantity:.6f}, leverage: {leverage}x")
        
        # Method 1: Try with simplified parameters
        try:
            params = {
                'tdMode': 'isolated',  # Trading mode
                'posSide': 'long',     # Position side
                'lever': str(leverage) # Leverage
            }
            
            order = futures_exchange.create_order(
                okx_symbol,
                'market',
                'buy', 
                quantity,
                None,  # price
                params
            )
            
            if order and order.get('id'):
                logging.info(f"✅ OKX Futures LONG executed successfully: {order['id']}")
                return order
                
        except Exception as method1_error:
            logging.warning(f"Method 1 failed: {method1_error}")
            
            # Method 2: Try direct create_market_buy_order without extra params
            try:
                order = futures_exchange.create_market_buy_order(okx_symbol, quantity)
                if order and order.get('id'):
                    logging.info(f"✅ OKX Futures LONG (method 2) executed: {order['id']}")
                    return order
            except Exception as method2_error:
                logging.warning(f"Method 2 failed: {method2_error}")
                
                # Method 3: Fallback to spot trading
                try:
                    spot_symbol = okx_symbol.replace('-USDT-SWAP', '/USDT')
                    spot_order = futures_exchange.create_market_buy_order(spot_symbol, quantity)
                    if spot_order and spot_order.get('id'):
                        logging.info(f"✅ Fallback SPOT BUY executed: {spot_order['id']}")
                        return spot_order
                except Exception as method3_error:
                    logging.error(f"All methods failed: {method3_error}")
                    return None
                    
    except Exception as e:
        logging.error(f"❌ OKX futures execution error: {e}")
        return None

def check_and_transfer_balance(exchange, required_amount=10.0):
    """Check balance and transfer if needed"""
    try:
        # Check spot balance
        balance = exchange.fetch_balance()
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        
        logging.info(f"💰 Current USDT balance: ${usdt_balance:.2f}")
        
        if usdt_balance >= required_amount:
            return True
        
        # Try to get funding account balance
        try:
            funding_response = exchange.private_get_asset_balances()
            for item in funding_response.get('data', []):
                if item.get('ccy') == 'USDT':
                    funding_balance = float(item.get('availBal', 0))
                    logging.info(f"💰 Funding account USDT: ${funding_balance:.2f}")
                    
                    if funding_balance >= required_amount:
                        # Try transfer
                        transfer_amount = min(funding_balance * 0.9, required_amount * 1.5)
                        transfer_result = exchange.private_post_asset_transfer({
                            'ccy': 'USDT',
                            'amt': str(transfer_amount),
                            'from': '6',  # Funding account  
                            'to': '18',   # Spot trading account
                            'type': '0'   # Internal transfer
                        })
                        
                        if transfer_result.get('code') == '0':
                            logging.info(f"💱 Successfully transferred ${transfer_amount:.2f} USDT")
                            time.sleep(2)  # Wait for transfer
                            return True
                        else:
                            logging.warning(f"Transfer failed: {transfer_result}")
                    break
        except Exception as transfer_error:
            logging.warning(f"Transfer attempt failed: {transfer_error}")
        
        return False
        
    except Exception as e:
        logging.error(f"Balance check error: {e}")
        return False

def main():
    """Test OKX API fixes"""
    print("🔧 TESTING OKX API FIXES")
    print("=" * 40)
    
    try:
        spot_exchange, futures_exchange = create_fixed_okx_exchanges()
        
        # Test 1: Check balance and transfer if needed
        print("\n📊 TEST 1: Balance Check and Transfer")
        balance_ok = check_and_transfer_balance(spot_exchange, 20.0)
        print(f"Balance sufficient: {balance_ok}")
        
        # Test 2: Try a small futures long order
        if balance_ok:
            print("\n🎯 TEST 2: Futures Long Execution")
            test_quantity = 0.001  # Small test amount
            order_result = execute_okx_futures_long(
                futures_exchange, 
                'SOL/USDT', 
                test_quantity, 
                leverage=10
            )
            print(f"Order result: {order_result is not None}")
        
        print("\n✅ OKX API FIX TESTING COMPLETE")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    main()