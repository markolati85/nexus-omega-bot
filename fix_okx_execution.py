#!/usr/bin/env python3
"""
EMERGENCY OKX EXECUTION FIX
Fix the API parameter issues and enable direct crypto trading without USDT conversion
"""

def fix_futures_execution():
    """Generate fixed futures execution code"""
    
    fixed_code = '''
    # FIXED OKX FUTURES EXECUTION 
    elif action == 'futures_long':
        try:
            futures_symbol = symbol.replace('/USDT', '-USDT-SWAP')
            quantity = trade_amount_usd / market_data['price']
            
            # Try OKX futures with simpler approach
            try:
                # Set leverage first
                self.futures_exchange.set_leverage(leverage, futures_symbol)
                
                # Simple market buy order without complex params
                order = self.futures_exchange.create_market_buy_order(futures_symbol, quantity)
                
                if order and order.get('id'):
                    logging.info(f"🔥 FUTURES LONG executed - {leverage}x leverage, Order: {order['id']}")
                    return self.log_ultimate_trade(symbol, action, leverage, trade_amount_usd, effective_position, decision['confidence'], decision['reason'], order['id'], "EXECUTED_ULTIMATE")
                else:
                    raise Exception("No order ID returned")
                    
            except Exception as futures_error:
                logging.error(f"Futures execution failed: {futures_error}")
                
                # Emergency fallback: Sell crypto directly for the trade
                spot_balance = self.spot_exchange.fetch_balance()
                
                # Find crypto to sell for this trade value
                for currency, info in spot_balance.items():
                    if currency not in ['USDT'] and isinstance(info, dict):
                        amount = info.get('total', 0)
                        if amount > 0:
                            try:
                                sell_symbol = f'{currency}/USDT'
                                ticker = self.spot_exchange.fetch_ticker(sell_symbol)
                                crypto_value = amount * ticker['last']
                                
                                if crypto_value >= trade_amount_usd * 0.8:  # 80% of needed amount
                                    # Sell crypto for USDT
                                    sell_order = self.spot_exchange.create_market_sell_order(sell_symbol, amount * 0.9)  # Sell 90%
                                    logging.info(f"💱 Emergency conversion: Sold {amount * 0.9:.6f} {currency} for USDT")
                                    
                                    # Wait and then buy target crypto
                                    time.sleep(2)
                                    updated_balance = self.spot_exchange.fetch_balance()
                                    new_usdt = updated_balance.get('USDT', {}).get('free', 0)
                                    
                                    if new_usdt >= 5:  # Minimum for trade
                                        buy_quantity = (new_usdt * 0.9) / market_data['price']
                                        buy_order = self.spot_exchange.create_market_buy_order(symbol, buy_quantity)
                                        logging.info(f"✅ Emergency SPOT BUY executed: ${new_usdt * 0.9:.2f}")
                                        return self.log_ultimate_trade(symbol, "spot_buy", 1, new_usdt * 0.9, new_usdt * 0.9, decision['confidence'], f"Emergency conversion from {currency}", buy_order['id'], "EXECUTED_ULTIMATE")
                                    break
                                    
                            except Exception as conversion_error:
                                logging.error(f"Conversion error for {currency}: {conversion_error}")
                                continue
                
                logging.warning("⚠️ No suitable crypto found for emergency conversion")
                return False
                
        except Exception as e:
            logging.error(f"❌ Ultimate futures execution error: {e}")
            return False
    '''
    
    return fixed_code

def main():
    print("🔧 OKX EXECUTION FIX GENERATED")
    print("=" * 50)
    print("Generated emergency execution code that:")
    print("1. Tries simplified OKX futures parameters")
    print("2. Sets leverage separately before order")
    print("3. Uses emergency crypto conversion if futures fail")
    print("4. Executes spot trades with available crypto")
    print("5. Provides comprehensive fallback logic")
    print("\nThis will enable trading with existing crypto holdings")
    print("without requiring USDT balance transfers")
    
    # Show the code
    fixed_code = fix_futures_execution()
    print("\n📝 FIXED EXECUTION CODE:")
    print(fixed_code[:500] + "..." if len(fixed_code) > 500 else fixed_code)

if __name__ == "__main__":
    main()