#!/usr/bin/env python3
"""
Nexus Ultimate Margin & Futures Trading - Full leverage and short selling enabled
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

try:
    import ccxt
    from openai import OpenAI
    from auto_transfer_handler import AutoTransferHandler
    from watchdog_trade_integrity import trade_watchdog
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/nexus-trading/nexus_margin_futures.log'),
        logging.StreamHandler()
    ]
)

class NexusMarginFuturesBot:
    def __init__(self):
        self.balance = 0
        self.start_time = time.time()
        self.cycle_count = 0
        self.trades_executed = 0
        self.active_positions = {}  # Track active positions for advanced exit logic
        self.trade_start_times = {}  # Track trade start times for timeout exits
        self.trailing_stops = {}  # Track trailing stops
        self.setup_apis()
        
        logging.info("🚀 NEXUS ULTIMATE: MARGIN + FUTURES + SHORT SELLING + ADVANCED EXIT LOGIC ACTIVATED")
        
    def get_total_portfolio_value(self):
        """Calculate total portfolio value across all assets and wallets"""
        try:
            balance = self.spot_exchange.fetch_balance()
            total_value = 0
            
            # Get USDT balance
            usdt_total = balance.get('USDT', {}).get('total', 0)
            total_value += usdt_total
            
            # Get crypto holdings value
            for currency, info in balance.items():
                if isinstance(info, dict) and currency != 'USDT':
                    amount = info.get('total', 0)
                    if amount > 0:
                        try:
                            ticker = self.spot_exchange.fetch_ticker(f'{currency}/USDT')
                            crypto_value = amount * ticker['last']
                            total_value += crypto_value
                        except:
                            pass  # Skip if price unavailable
            
            return max(total_value, 1.0)  # Minimum $1 to prevent division by zero
            
        except Exception as e:
            logging.error(f"Portfolio value calculation error: {e}")
            return max(self.balance, 1.0)
    
    def convert_crypto_for_trade(self, required_usdt, symbol):
        """Convert crypto holdings to USDT for trading if needed"""
        try:
            balance = self.spot_exchange.fetch_balance()
            current_usdt = balance.get('USDT', {}).get('total', 0)
            
            if current_usdt >= required_usdt:
                return True  # Already have enough USDT
            
            needed_usdt = required_usdt - current_usdt
            
            # Find crypto to sell (exclude the one we're about to buy)
            target_currency = symbol.split('/')[0]
            
            for currency, info in balance.items():
                if currency in ['USDT', target_currency] or not isinstance(info, dict):
                    continue
                    
                amount = info.get('total', 0)
                if amount > 0:
                    try:
                        # Try to sell this crypto for USDT
                        sell_symbol = f'{currency}/USDT'
                        ticker = self.spot_exchange.fetch_ticker(sell_symbol)
                        crypto_value = amount * ticker['last']
                        
                        if crypto_value >= needed_usdt * 1.1:  # 10% buffer
                            # Sell enough to cover needed USDT
                            sell_amount = (needed_usdt * 1.1) / ticker['last']
                            order = self.spot_exchange.create_market_sell_order(sell_symbol, sell_amount)
                            logging.info(f"💱 Converted {sell_amount:.6f} {currency} to USDT for trade")
                            return True
                            
                    except Exception as e:
                        logging.error(f"Conversion error for {currency}: {e}")
                        continue
            
            return False  # Couldn't convert enough
            
        except Exception as e:
            logging.error(f"Crypto conversion error: {e}")
            return False

    def setup_apis(self):
        """Setup OKX API with spot, margin, and futures trading"""
        try:
            # Spot trading
            self.spot_exchange = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'sandbox': False,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            
            # Margin trading (up to 10x leverage)
            self.margin_exchange = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'sandbox': False,
                'enableRateLimit': True,
                'options': {'defaultType': 'margin'}
            })
            
            # Futures trading (up to 125x leverage)
            self.futures_exchange = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'sandbox': False,
                'enableRateLimit': True,
                'options': {'defaultType': 'swap'}  # Perpetual futures
            })
            
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Initialize Auto-Transfer Handler
            try:
                self.transfer_handler = AutoTransferHandler()
                logging.info("🔄 Smart Auto-Transfer Handler initialized")
            except Exception as e:
                logging.error(f"Auto-Transfer initialization error: {e}")
                self.transfer_handler = None
            
            # Test all connections
            spot_balance = self.spot_exchange.fetch_balance()
            logging.info(f"✅ SPOT API connected - Balance: ${spot_balance.get('USDT', {}).get('free', 0):.2f}")
            
            try:
                margin_balance = self.margin_exchange.fetch_balance()
                logging.info(f"✅ MARGIN API connected - Balance: ${margin_balance.get('USDT', {}).get('free', 0):.2f}")
            except Exception as e:
                logging.warning(f"⚠️ Margin API: {e}")
            
            try:
                futures_balance = self.futures_exchange.fetch_balance()
                logging.info(f"✅ FUTURES API connected - Balance: ${futures_balance.get('USDT', {}).get('free', 0):.2f}")
            except Exception as e:
                logging.warning(f"⚠️ Futures API: {e}")
            
        except Exception as e:
            logging.error(f"❌ API setup error: {e}")
            sys.exit(1)
    
    def transfer_funds_for_trading(self, amount_needed, trade_type='spot'):
        """Transfer funds between accounts if needed"""
        try:
            if trade_type == 'spot':
                target_account = 'spot'
            elif trade_type in ['margin_long', 'margin_short']:
                target_account = 'margin'
            elif trade_type in ['futures_long', 'futures_short']:
                target_account = 'swap'
            else:
                target_account = 'spot'
            
            # Check if we need to transfer funds
            if target_account == 'spot':
                balance = self.spot_exchange.fetch_balance()
                available = balance.get('USDT', {}).get('free', 0)
            elif target_account == 'margin':
                balance = self.margin_exchange.fetch_balance()
                available = balance.get('USDT', {}).get('free', 0)
            elif target_account == 'swap':
                balance = self.futures_exchange.fetch_balance()
                available = balance.get('USDT', {}).get('free', 0)
            
            if available >= amount_needed:
                return True  # Already have enough
            
            needed = amount_needed - available
            
            # Try to transfer from other accounts
            try:
                # Get funding account balance (main wallet)
                funding_balance = self.spot_exchange.private_get_asset_balances()
                for item in funding_balance.get('data', []):
                    if item.get('ccy') == 'USDT':
                        funding_usdt = float(item.get('availBal', 0))
                        if funding_usdt >= needed:
                            # Transfer from funding to target account
                            transfer_result = self.spot_exchange.private_post_asset_transfer({
                                'ccy': 'USDT',
                                'amt': str(needed),
                                'from': '6',  # Funding account
                                'to': '18' if target_account == 'spot' else ('3' if target_account == 'margin' else '12'),  # Target account
                                'type': '0'  # Internal transfer
                            })
                            if transfer_result.get('code') == '0':
                                logging.info(f"💱 Transferred ${needed:.2f} USDT to {target_account} account")
                                return True
                            break
            except Exception as transfer_error:
                logging.warning(f"Transfer attempt failed: {transfer_error}")
            
            return False
            
        except Exception as e:
            logging.error(f"Fund transfer error: {e}")
            return False

    def get_comprehensive_balance(self):
        """Get balance across all trading accounts"""
        try:
            total_balance = 0
            balances = {}
            
            # Spot balance
            spot_balance = self.spot_exchange.fetch_balance()
            spot_usdt = spot_balance.get('USDT', {}).get('free', 0)
            balances['spot'] = spot_usdt
            total_balance += spot_usdt
            
            # Margin balance
            try:
                margin_balance = self.margin_exchange.fetch_balance()
                margin_usdt = margin_balance.get('USDT', {}).get('free', 0)
                balances['margin'] = margin_usdt
                total_balance += margin_usdt
            except:
                balances['margin'] = 0
            
            # Futures balance
            try:
                futures_balance = self.futures_exchange.fetch_balance()
                futures_usdt = futures_balance.get('USDT', {}).get('free', 0)
                balances['futures'] = futures_usdt
                total_balance += futures_usdt
            except:
                balances['futures'] = 0
            
            self.balance = total_balance
            return balances, total_balance
            
        except Exception as e:
            logging.error(f"Balance error: {e}")
            return {'spot': self.balance, 'margin': 0, 'futures': 0}, self.balance
    
    def get_market_data(self, symbol):
        """Get comprehensive market data"""
        try:
            ticker = self.spot_exchange.fetch_ticker(symbol)
            ohlcv = self.spot_exchange.fetch_ohlcv(symbol, '1h', limit=24)
            
            # Calculate RSI
            closes = [candle[4] for candle in ohlcv[-14:]]
            if len(closes) >= 14:
                deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
                gains = [d if d > 0 else 0 for d in deltas]
                losses = [-d if d < 0 else 0 for d in deltas]
                
                avg_gain = sum(gains) / len(gains) if gains else 0
                avg_loss = sum(losses) / len(losses) if losses else 0.1
                
                rsi = 100 - (100 / (1 + (avg_gain / avg_loss))) if avg_loss > 0 else 50
            else:
                rsi = 50
            
            return {
                'price': ticker['last'],
                'change': ticker['percentage'],
                'volume': ticker['quoteVolume'],
                'rsi': rsi,
                'volatility': abs(ticker['percentage'])
            }
            
        except Exception as e:
            logging.error(f"Market data error for {symbol}: {e}")
            return None
    
    def check_advanced_exit_conditions(self, symbol, market_data):
        """Advanced profit-taking and exit logic"""
        try:
            if symbol not in self.active_positions:
                return None
                
            position = self.active_positions[symbol]
            current_rsi = market_data['rsi']
            current_price = market_data['price']
            trade_start_time = self.trade_start_times.get(symbol, time.time())
            trade_duration = (time.time() - trade_start_time) / 60  # minutes
            
            # 1. RSI-Triggered Exit (Enhanced)
            if current_rsi >= 50 and position['confidence'] >= 70:
                return {"action": "exit", "reason": "RSI target reached (>=50)", "priority": "high"}
            
            # 2. Smart Exit on Overbought RSI + Flip to Short
            if current_rsi >= 65:
                return {"action": "flip_short", "reason": "Overbought RSI - flip to short", "priority": "urgent"}
            
            # 3. Timeout Exit (Failsafe) - 2 hours
            if trade_duration >= 120:
                return {"action": "exit", "reason": "Trade timeout (2 hours)", "priority": "medium"}
            
            # 4. Volatility-Based Exit (Trend Weakness)
            if market_data['volatility'] < 1.0 and current_rsi < 45:
                return {"action": "exit", "reason": "Trend weakening (low volatility)", "priority": "medium"}
            
            # 5. Trailing Stop Logic
            if symbol in self.trailing_stops:
                stop_data = self.trailing_stops[symbol]
                if position['action'] in ['margin_long', 'futures_long']:
                    # Long position trailing stop
                    if current_price <= stop_data['stop_price']:
                        return {"action": "exit", "reason": "Trailing stop triggered", "priority": "urgent"}
                    # Update trailing stop if price moved favorably
                    elif current_price > stop_data['highest_price']:
                        self.trailing_stops[symbol]['highest_price'] = current_price
                        self.trailing_stops[symbol]['stop_price'] = current_price * 0.985  # 1.5% trailing
                
            return None
            
        except Exception as e:
            logging.error(f"Exit condition check error: {e}")
            return None

    def activate_trailing_stop(self, symbol, current_price, trigger_pct=100, step_pct=1.5):
        """Activate trailing stop when unrealized PnL reaches trigger"""
        try:
            if symbol not in self.active_positions:
                return
                
            position = self.active_positions[symbol]
            entry_price = position.get('entry_price', current_price)
            
            # Calculate unrealized PnL percentage
            if position['action'] in ['margin_long', 'futures_long']:
                pnl_pct = ((current_price - entry_price) / entry_price) * 100 * position.get('leverage', 1)
            else:
                pnl_pct = ((entry_price - current_price) / entry_price) * 100 * position.get('leverage', 1)
            
            # Activate trailing stop if PnL >= trigger percentage
            if pnl_pct >= trigger_pct:
                self.trailing_stops[symbol] = {
                    'highest_price': current_price,
                    'stop_price': current_price * (1 - step_pct/100),
                    'activated': True
                }
                logging.info(f"🎯 Trailing stop activated for {symbol} at ${current_price:.2f} (PnL: {pnl_pct:.1f}%)")
                
        except Exception as e:
            logging.error(f"Trailing stop activation error: {e}")

    def find_better_opportunity(self, current_symbol, current_confidence):
        """Check if there's a better trading opportunity on other coins"""
        try:
            pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
            best_opportunity = None
            best_score = current_confidence
            
            for pair in pairs:
                if pair == current_symbol:
                    continue
                    
                market_data = self.get_market_data(pair)
                if not market_data:
                    continue
                    
                # Calculate opportunity score based on RSI extremes and volatility
                rsi = market_data['rsi']
                volatility = market_data['volatility']
                
                if rsi <= 20:  # Extremely oversold
                    score = 90 + (20 - rsi) * 2 + volatility  # Bonus for extreme RSI
                elif rsi >= 80:  # Extremely overbought (short opportunity)
                    score = 85 + (rsi - 80) * 2 + volatility
                elif rsi <= 35:  # Oversold
                    score = 75 + (35 - rsi) + volatility
                elif rsi >= 65:  # Overbought
                    score = 70 + (rsi - 65) + volatility
                else:
                    score = 50  # Neutral
                
                if score > best_score:
                    best_score = score
                    best_opportunity = {
                        'symbol': pair,
                        'score': score,
                        'rsi': rsi,
                        'volatility': volatility,
                        'market_data': market_data
                    }
            
            return best_opportunity
            
        except Exception as e:
            logging.error(f"Better opportunity search error: {e}")
            return None

    def make_ultimate_trading_decision(self, symbol, market_data):
        """AI decision for ALL trading types: Spot, Margin, Futures, Long, Short with Advanced Exit Logic"""
        try:
            # First check if we should exit current position
            exit_decision = self.check_advanced_exit_conditions(symbol, market_data)
            if exit_decision:
                return exit_decision
            
            # Check for better opportunities on other coins
            if symbol in self.active_positions:
                current_confidence = self.active_positions[symbol]['confidence']
                better_opportunity = self.find_better_opportunity(symbol, current_confidence)
                if better_opportunity and better_opportunity['score'] > current_confidence + 15:
                    return {
                        "action": "rotate_capital", 
                        "reason": f"Better opportunity: {better_opportunity['symbol']} (score: {better_opportunity['score']:.1f})",
                        "new_target": better_opportunity
                    }
            
            # Activate trailing stops for profitable positions
            self.activate_trailing_stop(symbol, market_data['price'])
            
            prompt = f"""
            ULTIMATE TRADING DECISION - ALL TYPES ENABLED WITH ADVANCED EXIT LOGIC
            
            Symbol: {symbol}
            Price: ${market_data['price']:.2f}
            24h Change: {market_data['change']:+.2f}%
            RSI: {market_data['rsi']:.1f}
            Volatility: {market_data['volatility']:.2f}%
            Available Balance: ${self.balance:.2f} USDT
            Active Position: {symbol in self.active_positions}
            
            AVAILABLE TRADING OPTIONS:
            1. SPOT: Regular buy/sell (1x)
            2. MARGIN_LONG: Leveraged long position (2-10x)
            3. MARGIN_SHORT: Leveraged short position (2-10x)
            4. FUTURES_LONG: Futures long position (5-125x)
            5. FUTURES_SHORT: Futures short position (5-125x)
            6. EXIT: Close current position
            7. FLIP_SHORT: Close long and open short position
            
            ENHANCED TRADING RULES:
            - RSI < 30: ULTRA-STRONG LONG signals (futures_long with max leverage)
            - RSI 30-40: Strong LONG signals (margin_long/futures_long)
            - RSI 40-50: Moderate LONG signals (spot_buy/margin_long)
            - RSI 50-60: Moderate SHORT signals (spot_sell/margin_short)
            - RSI 60-70: Strong SHORT signals (margin_short/futures_short)
            - RSI > 70: ULTRA-STRONG SHORT signals (futures_short with max leverage)
            - High volatility (>2%): Use futures for maximum profit
            - Moderate volatility (1-2%): Use margin trading
            - Low volatility (<1%): Use spot trading
            - Confidence >= 70% to execute
            
            LEVERAGE GUIDELINES:
            - BTC/ETH: Max 25x leverage
            - SOL/DOGE: Max 50x leverage  
            - Other alts: Max 125x leverage
            
            Respond with ONLY this JSON:
            {{
                "action": "spot_buy/spot_sell/margin_long/margin_short/futures_long/futures_short/exit/flip_short/hold",
                "leverage": 1-125,
                "confidence": 70-95,
                "reason": "detailed analysis for trading type selection with exit logic"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in spot, margin, and futures trading. Select the optimal trading type and leverage."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            try:
                decision = json.loads(content)
                # Critical fix: Safely extract confidence with validation
                confidence = float(decision.get("confidence", 0))
                action = decision.get("action", "hold")
                leverage = int(decision.get("leverage", 1))
                reason = decision.get("reason", "AI decision")
                
                # Validate confidence threshold
                if confidence < 70:
                    logging.info(f"⚠️ Low confidence ({confidence}%) - skipping trade")
                    return {"action": "hold", "leverage": 1, "confidence": confidence, "reason": f"Low confidence: {reason}"}
                
                # Return validated decision
                validated_decision = {
                    "action": action,
                    "leverage": leverage, 
                    "confidence": confidence,
                    "reason": reason
                }
                logging.info(f"🤖 Ultimate AI Decision: {validated_decision}")
                return validated_decision
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logging.error(f"AI decision parsing error: {e}")
                return {"action": "hold", "leverage": 1, "confidence": 50, "reason": f"Parsing error: {e}"}
            
        except Exception as e:
            logging.error(f"AI decision error: {e}")
            return {"action": "hold", "leverage": 1, "confidence": 50, "reason": "AI error"}
    
    def execute_ultimate_trade(self, symbol, decision):
        """Execute trade across ALL platforms with leverage and short selling + Advanced Exit Logic"""
        try:
            # Handle advanced exit actions first
            if decision['action'] == 'exit':
                return self.exit_position(symbol, decision['reason'])
            elif decision['action'] == 'flip_short':
                return self.flip_to_short_position(symbol, decision['reason'])
            elif decision['action'] == 'rotate_capital':
                return self.rotate_capital_to_better_opportunity(symbol, decision)
            
            if decision['action'] == 'hold' or decision.get('confidence', 0) < 70:
                return False
            
            action = decision['action']
            # Ultra-aggressive position sizing based on AI confidence and opportunity
            confidence = float(decision.get('confidence', 70))
            leverage = int(decision.get('leverage', 1))
            
            # Calculate position size based on confidence and leverage potential
            if confidence >= 85 and leverage >= 25:  # Ultra-high confidence + high leverage
                position_pct = 0.50  # Use 50% of portfolio
            elif confidence >= 80 and leverage >= 10:  # High confidence + medium leverage  
                position_pct = 0.35  # Use 35% of portfolio
            elif confidence >= 75:  # Good confidence
                position_pct = 0.20  # Use 20% of portfolio
            else:
                position_pct = 0.08  # Conservative 8% default
            
            # Get total available funds across all assets  
            total_portfolio_value = self.get_total_portfolio_value()
            
            # Ensure we can convert crypto if needed
            if action in ['futures_long', 'margin_long'] and confidence >= 85:
                self.convert_crypto_for_trade(total_portfolio_value * position_pct, symbol)
            
            trade_amount_usd = total_portfolio_value * position_pct
            
            logging.info(f"💰 Portfolio Value: ${total_portfolio_value:.2f}")
            logging.info(f"🎯 Confidence: {confidence}% | Leverage: {leverage}x | Position: {position_pct*100:.0f}%")
            logging.info(f"💵 Trade Amount: ${trade_amount_usd:.2f}")
            
            if trade_amount_usd < 5:
                logging.warning(f"⚠️ Trade amount ${trade_amount_usd:.2f} below minimum, skipping")
                return False
            
            # Get current market price
            market_data = self.get_market_data(symbol)
            if not market_data:
                logging.error(f"❌ No market data for {symbol}")
                return False
            
            # Calculate effective position with leverage
            effective_position = trade_amount_usd * leverage
            
            logging.info(f"🎯 EXECUTING: {action.upper().replace('_', ' ')} {symbol}")
            logging.info(f"   Base Amount: ${trade_amount_usd:.2f}")
            logging.info(f"   Leverage: {leverage}x")
            logging.info(f"   Effective Position: ${effective_position:.2f}")
            
            order = None
            
            if action == 'spot_buy':
                # Regular spot buy
                quantity = trade_amount_usd / market_data['price']
                order = self.spot_exchange.create_market_buy_order(symbol, quantity)
                logging.info(f"✅ SPOT BUY executed - Quantity: {quantity:.6f}")
                
            elif action == 'spot_sell':
                # Regular spot sell
                balance = self.spot_exchange.fetch_balance()
                base_currency = symbol.split('/')[0]
                holdings = balance.get(base_currency, {}).get('free', 0)
                if holdings > 0:
                    order = self.spot_exchange.create_market_sell_order(symbol, holdings)
                    logging.info(f"✅ SPOT SELL executed - Quantity: {holdings:.6f}")
                
            elif action == 'margin_long':
                # Margin long position (leveraged buy) - Fixed balance checking
                try:
                    # Check available balance first
                    margin_balance = self.margin_exchange.fetch_balance()
                    available_usdt = margin_balance.get('USDT', {}).get('free', 0)
                    
                    if available_usdt < 5:  # Not enough in margin account
                        # Try spot account as fallback
                        spot_balance = self.spot_exchange.fetch_balance()
                        spot_usdt = spot_balance.get('USDT', {}).get('free', 0)
                        if spot_usdt >= 5:
                            safe_amount = min(spot_usdt * 0.9, trade_amount_usd)
                            quantity = safe_amount / market_data['price']
                            order = self.spot_exchange.create_market_buy_order(symbol, quantity)
                            logging.info(f"✅ SPOT BUY executed (margin fallback) - ${safe_amount:.2f}")
                        else:
                            logging.warning(f"⚠️ Insufficient balance: Margin ${available_usdt:.2f}, Spot ${spot_usdt:.2f}")
                            return False
                    else:
                        # Execute margin trade with available balance
                        safe_amount = min(available_usdt * 0.9, trade_amount_usd)
                        quantity = safe_amount / market_data['price']
                        order = self.margin_exchange.create_market_buy_order(symbol, quantity)
                        logging.info(f"🚀 MARGIN LONG executed - {leverage}x leverage, ${safe_amount:.2f}")
                        
                except Exception as e:
                    logging.error(f"Margin long error: {e}")
                    # Final fallback to spot
                    try:
                        spot_balance = self.spot_exchange.fetch_balance()
                        available_usdt = spot_balance.get('USDT', {}).get('free', 0)
                        if available_usdt >= 5:
                            safe_amount = min(available_usdt * 0.9, trade_amount_usd)
                            quantity = safe_amount / market_data['price']
                            order = self.spot_exchange.create_market_buy_order(symbol, quantity)
                            logging.info(f"✅ Final fallback SPOT BUY executed - ${safe_amount:.2f}")
                        else:
                            return False
                    except:
                        return False
                
            elif action == 'margin_short':
                # Margin short position (leveraged sell) - Fixed parameters
                try:
                    margin_balance = self.margin_exchange.fetch_balance()
                    available_usdt = margin_balance.get('USDT', {}).get('free', 0)
                    
                    if available_usdt >= 5:
                        safe_amount = min(available_usdt * 0.9, trade_amount_usd)
                        quantity = safe_amount / market_data['price']
                        
                        # OKX margin short with proper parameters
                        # OKX margin short parameters
                        params = {
                            'tdMode': 'isolated',  # Trading mode for margin
                            'side': 'sell'  # Explicit side
                        }
                        order = self.margin_exchange.create_market_sell_order(symbol, quantity, None, params)
                        logging.info(f"📉 MARGIN SHORT executed - {leverage}x leverage, ${safe_amount:.2f}")
                    else:
                        logging.warning(f"⚠️ Insufficient margin balance for short: ${available_usdt:.2f}")
                        return False
                        
                except Exception as e:
                    logging.error(f"Margin short error: {e}")
                    logging.info(f"⚠️ Margin short not available, holding position")
                    return False
                
            elif action == 'futures_long':
                # PROPER FUTURES LONG with OKX API - Fixed Implementation + Auto-Transfer
                try:
                    # Try real futures trading first with auto-transfer
                    try:
                        futures_balance = self.futures_exchange.fetch_balance()
                        available_usdt = futures_balance.get('USDT', {}).get('free', 0)
                        
                        # Auto-transfer funds if insufficient balance
                        if available_usdt < 10 and self.transfer_handler:
                            logging.info(f"💰 Insufficient futures balance (${available_usdt:.2f}) - attempting auto-transfer")
                            if self.transfer_handler.ensure_futures_balance(trade_amount_usd):
                                # Re-check balance after transfer
                                time.sleep(2)
                                futures_balance = self.futures_exchange.fetch_balance()
                                available_usdt = futures_balance.get('USDT', {}).get('free', 0)
                                logging.info(f"✅ Auto-transfer completed - New futures balance: ${available_usdt:.2f}")
                        
                        if available_usdt >= 5:
                            # Calculate position size
                            safe_amount = min(available_usdt * 0.8, trade_amount_usd)  # Use 80% of available
                            
                            # OKX Futures API parameters - CORRECT FORMAT
                            base_currency = symbol.split('/')[0]  # SOL from SOL/USDT
                            futures_symbol = f'{base_currency}-USDT-SWAP'  # SOL-USDT-SWAP
                            
                            # Calculate quantity for futures
                            quantity = safe_amount / market_data['price']
                            
                            # OKX Futures parameters - PROPER FORMAT
                            params = {
                                'instType': 'SWAP',  # Perpetual futures
                                'tdMode': 'cross',   # Cross margin mode
                                'side': 'buy',       # Buy side
                                'posSide': 'long',   # Long position
                                'ordType': 'market', # Market order
                                'lever': str(min(leverage, 125))  # Leverage as string
                            }
                            
                            # Fixed OKX futures API call format
                            order = self.futures_exchange.create_market_order(
                                futures_symbol,
                                'buy',
                                quantity,
                                None,
                                params
                            )
                            logging.info(f"🚀 REAL FUTURES LONG executed - {leverage}x leverage, ${safe_amount:.2f}")
                            logging.info(f"📊 Futures Order ID: {order.get('id', 'unknown')}")
                            
                            return self.log_ultimate_trade(symbol, "futures_long", leverage, safe_amount, safe_amount * leverage, decision['confidence'], f"Real futures long: {decision['reason']}", order['id'], "EXECUTED_ULTIMATE_FUTURES")
                            
                        else:
                            logging.warning(f"⚠️ Insufficient futures balance: ${available_usdt:.2f}")
                            
                    except Exception as futures_error:
                        logging.error(f"Futures execution error: {futures_error}")
                        logging.info("🔄 Falling back to emergency conversion system...")
                    
                    # Fallback: Emergency crypto conversion system (existing working code)
                    spot_balance = self.spot_exchange.fetch_balance()
                    available_usdt = spot_balance.get('USDT', {}).get('free', 0)
                    
                    logging.info(f"💰 Available USDT: ${available_usdt:.2f}")
                    
                    # If we have enough USDT, try simple spot buy first
                    if available_usdt >= 5:
                        safe_amount = min(available_usdt * 0.9, trade_amount_usd)
                        quantity = safe_amount / market_data['price']
                        order = self.spot_exchange.create_market_buy_order(symbol, quantity)
                        logging.info(f"✅ DIRECT SPOT BUY executed - ${safe_amount:.2f}")
                        return self.log_ultimate_trade(symbol, "spot_buy", 1, safe_amount, safe_amount, decision['confidence'], f"Direct buy with available USDT: {decision['reason']}", order['id'], "EXECUTED_ULTIMATE")
                    
                    # EMERGENCY: Convert existing crypto to execute the trade
                    target_currency = symbol.split('/')[0]  # e.g., 'SOL' from 'SOL/USDT'
                    
                    # Find crypto assets to convert (exclude the target)
                    for currency, info in spot_balance.items():
                        if currency in ['USDT', target_currency] or not isinstance(info, dict):
                            continue
                            
                        amount = info.get('total', 0)
                        if amount > 0:
                            try:
                                # Get current price to estimate value
                                sell_symbol = f'{currency}/USDT'
                                ticker = self.spot_exchange.fetch_ticker(sell_symbol)
                                crypto_value = amount * ticker['last']
                                
                                logging.info(f"🔍 Found {currency}: {amount:.6f} tokens = ${crypto_value:.2f}")
                                
                                if crypto_value >= 10:  # Worth at least $10
                                    # Sell this crypto for USDT
                                    sell_amount = amount * 0.95  # Sell 95% to avoid precision issues
                                    sell_order = self.spot_exchange.create_market_sell_order(sell_symbol, sell_amount)
                                    logging.info(f"💱 CONVERTED: Sold {sell_amount:.6f} {currency} for USDT")
                                    
                                    # Wait for execution and get new balance
                                    time.sleep(3)
                                    updated_balance = self.spot_exchange.fetch_balance()
                                    new_usdt = updated_balance.get('USDT', {}).get('free', 0)
                                    
                                    if new_usdt >= 5:
                                        # Now buy the target crypto
                                        buy_amount = new_usdt * 0.95  # Use 95% of new USDT
                                        buy_quantity = buy_amount / market_data['price']
                                        buy_order = self.spot_exchange.create_market_buy_order(symbol, buy_quantity)
                                        logging.info(f"✅ EMERGENCY BUY executed: ${buy_amount:.2f} → {buy_quantity:.6f} {target_currency}")
                                        
                                        return self.log_ultimate_trade(symbol, "emergency_buy", 1, buy_amount, buy_amount, decision['confidence'], f"Emergency conversion from {currency}: {decision['reason']}", buy_order['id'], "EXECUTED_ULTIMATE")
                                    else:
                                        logging.warning(f"⚠️ Conversion did not provide enough USDT: ${new_usdt:.2f}")
                                        
                            except Exception as conversion_error:
                                logging.error(f"Conversion error for {currency}: {conversion_error}")
                                continue
                    
                    logging.warning("⚠️ No suitable crypto assets found for conversion")
                    return False
                    
                except Exception as e:
                    logging.error(f"❌ Futures trade execution error: {e}")
                    return False
                
            elif action == 'futures_short':
                # PROPER FUTURES SHORT with OKX API - Fixed Implementation + Auto-Transfer
                try:
                    futures_balance = self.futures_exchange.fetch_balance()
                    available_usdt = futures_balance.get('USDT', {}).get('free', 0)
                    
                    # Auto-transfer funds if insufficient balance
                    if available_usdt < 10 and self.transfer_handler:
                        logging.info(f"💰 Insufficient futures balance (${available_usdt:.2f}) for short - attempting auto-transfer")
                        if self.transfer_handler.ensure_futures_balance(trade_amount_usd):
                            # Re-check balance after transfer
                            time.sleep(2)
                            futures_balance = self.futures_exchange.fetch_balance()
                            available_usdt = futures_balance.get('USDT', {}).get('free', 0)
                            logging.info(f"✅ Auto-transfer completed - New futures balance: ${available_usdt:.2f}")
                    
                    if available_usdt >= 5:
                        # Calculate position size
                        safe_amount = min(available_usdt * 0.8, trade_amount_usd)
                        
                        # OKX Futures API parameters - CORRECT FORMAT
                        base_currency = symbol.split('/')[0]  # SOL from SOL/USDT
                        futures_symbol = f'{base_currency}-USDT-SWAP'  # SOL-USDT-SWAP
                        
                        # Calculate quantity for futures short
                        quantity = safe_amount / market_data['price']
                        
                        # OKX Futures SHORT parameters - PROPER FORMAT
                        params = {
                            'instType': 'SWAP',   # Perpetual futures
                            'tdMode': 'cross',    # Cross margin mode
                            'side': 'sell',       # Sell side for short
                            'posSide': 'short',   # Short position
                            'ordType': 'market',  # Market order
                            'lever': str(min(leverage, 125))  # Leverage as string
                        }
                        
                        # Fixed OKX futures short order
                        order = self.futures_exchange.create_market_order(
                            futures_symbol,
                            'sell',
                            quantity,
                            None,
                            {'positionSide': 'short'}
                        )
                        logging.info(f"⚡ REAL FUTURES SHORT executed - {leverage}x leverage, ${safe_amount:.2f}")
                        logging.info(f"📊 Futures Short Order ID: {order.get('id', 'unknown')}")
                        
                        return self.log_ultimate_trade(symbol, "futures_short", leverage, safe_amount, safe_amount * leverage, decision['confidence'], f"Real futures short: {decision['reason']}", order['id'], "EXECUTED_ULTIMATE_FUTURES_SHORT")
                        
                    else:
                        logging.warning(f"⚠️ Insufficient futures balance for short: ${available_usdt:.2f}")
                        return False
                        
                except Exception as e:
                    logging.error(f"Futures short error: {e}")
                    logging.info(f"⚠️ Futures short execution failed: {e}")
                    return False
            
            if order:
                # Track active position for advanced exit logic
                self.active_positions[symbol] = {
                    'action': action,
                    'leverage': leverage,
                    'entry_price': market_data['price'],
                    'trade_amount': trade_amount_usd,
                    'effective_position': effective_position,
                    'confidence': decision['confidence'],
                    'order_id': order.get('id', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                }
                self.trade_start_times[symbol] = time.time()
                
                # Log comprehensive trade
                trade_log = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'action': action,
                    'leverage': leverage,
                    'trade_amount': trade_amount_usd,
                    'effective_position': effective_position,
                    'confidence': decision['confidence'],
                    'reason': decision['reason'],
                    'order_id': order.get('id', 'unknown'),
                    'status': 'EXECUTED_ULTIMATE_ADVANCED'
                }
                
                with open('/opt/nexus-trading/ultimate_trades.log', 'a') as f:
                    f.write(json.dumps(trade_log) + '\n')
                
                self.trades_executed += 1
                logging.info(f"🎯 ULTIMATE TRADE #{self.trades_executed} - Order ID: {order.get('id', 'unknown')}")
                logging.info(f"📊 Position tracked for advanced exit logic")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"❌ Ultimate trade execution error: {e}")
            return False
    
    def exit_position(self, symbol, reason):
        """Exit current position with advanced logic"""
        try:
            if symbol not in self.active_positions:
                logging.warning(f"⚠️ No active position to exit for {symbol}")
                return False
                
            position = self.active_positions[symbol]
            market_data = self.get_market_data(symbol)
            if not market_data:
                return False
            
            logging.info(f"🚪 EXITING POSITION: {symbol} - Reason: {reason}")
            
            # Determine exit strategy based on original position type
            if position['action'] in ['margin_long', 'futures_long']:
                # Close long position (sell)
                try:
                    if 'futures' in position['action']:
                        futures_symbol = symbol.replace('/USDT', '-USDT-SWAP')
                        balance = self.futures_exchange.fetch_balance()
                        base_currency = symbol.split('/')[0]
                        holdings = balance.get(base_currency, {}).get('free', 0)
                        if holdings > 0:
                            order = self.futures_exchange.create_market_sell_order(futures_symbol, holdings)
                    else:
                        balance = self.spot_exchange.fetch_balance()
                        base_currency = symbol.split('/')[0]
                        holdings = balance.get(base_currency, {}).get('free', 0)
                        if holdings > 0:
                            order = self.spot_exchange.create_market_sell_order(symbol, holdings)
                    
                    logging.info(f"✅ Long position closed for {symbol}")
                    
                except Exception as e:
                    logging.error(f"Exit long error: {e}")
                    
            elif position['action'] in ['margin_short', 'futures_short']:
                # Close short position (buy back)
                try:
                    trade_amount = position['trade_amount']
                    quantity = trade_amount / market_data['price']
                    
                    if 'futures' in position['action']:
                        futures_symbol = symbol.replace('/USDT', '-USDT-SWAP')
                        order = self.futures_exchange.create_market_buy_order(futures_symbol, quantity)
                    else:
                        order = self.margin_exchange.create_market_buy_order(symbol, quantity)
                    
                    logging.info(f"✅ Short position closed for {symbol}")
                    
                except Exception as e:
                    logging.error(f"Exit short error: {e}")
            
            # Clean up position tracking
            if symbol in self.active_positions:
                del self.active_positions[symbol]
            if symbol in self.trade_start_times:
                del self.trade_start_times[symbol]
            if symbol in self.trailing_stops:
                del self.trailing_stops[symbol]
            
            # Log exit
            exit_log = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'action': 'EXIT_POSITION',
                'reason': reason,
                'original_position': position,
                'status': 'POSITION_CLOSED'
            }
            
            with open('/opt/nexus-trading/ultimate_trades.log', 'a') as f:
                f.write(json.dumps(exit_log) + '\n')
            
            logging.info(f"🎯 POSITION EXITED: {symbol} - {reason}")
            return True
            
        except Exception as e:
            logging.error(f"Exit position error: {e}")
            return False
    
    def flip_to_short_position(self, symbol, reason):
        """Close long position and immediately open short position"""
        try:
            logging.info(f"🔄 FLIPPING TO SHORT: {symbol} - {reason}")
            
            # Exit current long position
            exit_success = self.exit_position(symbol, f"Flip to short: {reason}")
            if not exit_success:
                return False
            
            time.sleep(2)  # Brief pause between trades
            
            # Open new short position
            market_data = self.get_market_data(symbol)
            if not market_data:
                return False
            
            # Create short decision
            short_decision = {
                'action': 'futures_short' if market_data['volatility'] > 2 else 'margin_short',
                'leverage': 25 if symbol in ['BTC/USDT', 'ETH/USDT'] else 50,
                'confidence': 85,
                'reason': f'Flip to short after exit: {reason}'
            }
            
            return self.execute_ultimate_trade(symbol, short_decision)
            
        except Exception as e:
            logging.error(f"Flip to short error: {e}")
            return False
    
    def rotate_capital_to_better_opportunity(self, current_symbol, decision):
        """Exit current position and move capital to better opportunity"""
        try:
            new_target = decision['new_target']
            logging.info(f"🔄 ROTATING CAPITAL: {current_symbol} → {new_target['symbol']} (Score: {new_target['score']:.1f})")
            
            # Exit current position
            exit_success = self.exit_position(current_symbol, decision['reason'])
            if not exit_success:
                return False
            
            time.sleep(3)  # Allow time for settlement
            
            # Create new position decision based on new target's market data
            new_market_data = new_target['market_data']
            rsi = new_market_data['rsi']
            volatility = new_market_data['volatility']
            
            if rsi <= 30:
                action = 'futures_long' if volatility > 2 else 'margin_long'
                leverage = 50 if new_target['symbol'] == 'SOL/USDT' else 25
            elif rsi >= 70:
                action = 'futures_short' if volatility > 2 else 'margin_short'
                leverage = 50 if new_target['symbol'] == 'SOL/USDT' else 25
            else:
                action = 'spot_buy' if rsi < 50 else 'spot_sell'
                leverage = 1
            
            rotation_decision = {
                'action': action,
                'leverage': leverage,
                'confidence': min(new_target['score'], 95),
                'reason': f"Capital rotation from {current_symbol} - Better opportunity detected"
            }
            
            return self.execute_ultimate_trade(new_target['symbol'], rotation_decision)
            
        except Exception as e:
            logging.error(f"Capital rotation error: {e}")
            return False
    
    def update_dashboard_log(self, decisions, balances):
        """Update dashboard with ultimate trading data"""
        try:
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'cycle': self.cycle_count,
                'balance': self.balance,
                'account_balances': balances,
                'bot_status': 'ULTIMATE_TRADING_ACTIVE',
                'uptime': time.time() - self.start_time,
                'trades_executed': self.trades_executed,
                'trading_features': 'SPOT_MARGIN_FUTURES_SHORT_LONG_125X',
                'decisions': decisions,
                'last_update': datetime.now().strftime('%H:%M:%S')
            }
            
            with open('/opt/nexus-trading/latest_log.json', 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Dashboard log error: {e}")
    
    def run_ultimate_cycle(self):
        """Run ultimate trading cycle with all features"""
        self.cycle_count += 1
        
        # Get comprehensive balance
        balances, total_balance = self.get_comprehensive_balance()
        logging.info(f"💰 Total Balance: ${total_balance:.2f}")
        logging.info(f"   Spot: ${balances['spot']:.2f} | Margin: ${balances['margin']:.2f} | Futures: ${balances['futures']:.2f}")
        
        # Analyze trading pairs
        pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        decisions = {}
        
        for pair in pairs:
            market_data = self.get_market_data(pair)
            if market_data:
                logging.info(f"📊 {pair}: ${market_data['price']:.4f} ({market_data['change']:+.2f}%) RSI:{market_data['rsi']:.1f} Vol:{market_data['volatility']:.1f}%")
                
                # Make ultimate AI decision
                decision = self.make_ultimate_trading_decision(pair, market_data)
                decisions[pair] = decision
                
                action_display = decision['action'].upper().replace('_', ' ')
                leverage_info = f" {decision.get('leverage', 1)}x" if decision.get('leverage', 1) > 1 else ""
                
                logging.info(f"🤖 {pair} AI: {action_display}{leverage_info} (confidence: {decision['confidence']}%)")
                logging.info(f"   Reason: {decision['reason']}")
                
                # Execute ultimate trade if conditions met
                if decision['confidence'] >= 70 and decision['action'] != 'hold':
                    trade_executed = self.execute_ultimate_trade(pair, decision)
                    if trade_executed:
                        logging.info(f"🎯 ULTIMATE TRADE COMPLETED: {pair} - {action_display}{leverage_info}")
                        time.sleep(10)  # Wait between trades
        
        # Update dashboard
        self.update_dashboard_log(decisions, balances)
        
        logging.info(f"✅ Ultimate Cycle {self.cycle_count} complete (Ultimate Trades: {self.trades_executed})")
    
    def run(self):
        """Main ultimate trading loop"""
        logging.info("🚀 NEXUS ULTIMATE MARGIN & FUTURES BOT STARTING")
        logging.info("💰 FEATURES: Spot, Margin (10x), Futures (125x), Long/Short positions")
        logging.info("⚡ SHORT SELLING ENABLED - Profit from falling markets")
        
        while True:
            try:
                self.run_ultimate_cycle()
                time.sleep(90)  # 90-second cycles
                
            except KeyboardInterrupt:
                logging.info("🛑 Ultimate trading stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Ultimate cycle error: {e}")
                time.sleep(30)

    def log_ultimate_trade(self, symbol, action, leverage, trade_amount, effective_position, confidence, reason, order_id, status):
        """Log ultimate trade with comprehensive details"""
        try:
            trade_data = {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "action": action,
                "leverage": leverage,
                "trade_amount": trade_amount,
                "effective_position": effective_position,
                "confidence": confidence,
                "reason": reason,
                "order_id": order_id,
                "status": status
            }
            
            # Log to ultimate trades file
            with open("/opt/nexus-trading/ultimate_trades.log", "a") as f:
                f.write(json.dumps(trade_data) + "\n")
            
            logging.info(f"📝 Trade logged: {action} {symbol} ${trade_amount:.2f} (Order: {order_id})")
            self.trades_executed += 1
            return True
            
        except Exception as e:
            logging.error(f"Error logging ultimate trade: {e}")
            return False

if __name__ == "__main__":
    bot = NexusMarginFuturesBot()
    bot.run()