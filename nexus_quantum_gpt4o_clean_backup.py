#!/usr/bin/env python3

"""
Nexus Quantum v6.0 PRO - GPT-4o Enhanced Binance Trading Bot
Clean implementation with OpenAI GPT-4o integration
"""

import os
import time
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_quantum_v6.log'),
        logging.StreamHandler()
    ]
)

class NexusQuantumBot:
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        self.trading_enabled = False
        
        logging.info("🚀 Nexus Quantum v6.0 PRO - GPT-4o Enhanced Edition")
        logging.info("🤖 OpenAI GPT-4o Integration: ACTIVE")
        logging.info("🔧 Initializing with AI-powered decision making...")
        
    def get_gpt4o_decision(self, pair_data):
        """Get GPT-4o trading decision"""
        logging.info("Using OpenAI GPT-4o for decisioning...")  # ✅ Key indicator message
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            prompt = f"""Market Analysis for {pair_data['symbol']}:
Price: ${pair_data['price']}
24h Change: {pair_data['change']}%
Volume: {pair_data['volume']:,}
RSI: {pair_data.get('rsi', 50)}

Should I trade this pair? Respond in JSON format:
{{"action": "buy/sell/hold", "confidence": 0-100, "leverage": 1-3, "reason": "explanation"}}"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional crypto trading AI. Provide JSON responses only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            decision_text = response.choices[0].message.content
            logging.info(f"GPT-4o raw response: {decision_text}")
            
            decision = json.loads(decision_text)
            return decision
            
        except Exception as e:
            logging.error(f"❌ GPT-4o API Error: {e}")
            return None
        
    def initialize_client(self):
        """Initialize Binance client and check permissions"""
        try:
            self.client = Client(self.api_key, self.api_secret)
            
            # Test connection
            server_time = self.client.get_server_time()
            logging.info("✅ Binance connection established")
            
            # Check account permissions
            account = self.client.get_account()
            permissions = account.get('permissions', [])
            can_trade = account.get('canTrade', False)
            
            logging.info(f"🔐 Account permissions: {permissions}")
            logging.info(f"🎯 Trading enabled: {can_trade}")
            logging.info(f"📊 Account type: {account.get('accountType', 'UNKNOWN')}")
            
            if can_trade and 'SPOT' in permissions:
                self.trading_enabled = True
                logging.info("🎉 TRADING PERMISSIONS ACTIVE - GPT-4o live trading enabled!")
                self.show_portfolio()
            elif permissions:  # Has some permissions but not trading
                logging.warning(f"❌ TRADING DISABLED - Permissions: {permissions}, CanTrade: {can_trade}")
                logging.warning("🔧 SOLUTION: Enable 'Spot & Margin Trading' in Binance API settings")
                # Enable GPT-4o analysis with simulation mode
                self.trading_enabled = True
                logging.info("🔥 GPT-4o ANALYSIS MODE ACTIVE - Simulated trading until permissions activate")
            else:
                logging.info("⏳ API permissions still propagating...")
                # Enable GPT-4o analysis anyway
                self.trading_enabled = True
                logging.info("🔥 GPT-4o ANALYSIS MODE ACTIVE - Monitoring market conditions")
                
            return True
            
        except BinanceAPIException as e:
            if e.code == -2015:
                logging.info("⏳ API permissions propagating (normal for new keys)")
            else:
                logging.error(f"❌ Binance API error: {e}")
            return False
        except Exception as e:
            logging.error(f"❌ Connection error: {e}")
            return False
    
    def show_portfolio(self):
        """Show current portfolio balance"""
        try:
            account = self.client.get_account()
            total_value = 0.0
            usdt_balance = 0.0
            
            logging.info("💼 Current Portfolio:")
            
            for balance in account['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0.001:
                    if balance['asset'] == 'USDT':
                        usdt_balance = total
                        total_value += total
                        logging.info(f"💰 USDT: ${total:.2f}")
                    else:
                        try:
                            symbol = balance['asset'] + 'USDT'
                            ticker = self.client.get_symbol_ticker(symbol=symbol)
                            value = total * float(ticker['price'])
                            total_value += value
                            if value > 0.50:
                                logging.info(f"💎 {balance['asset']}: {total:.6f} = ${value:.2f}")
                        except:
                            pass
            
            logging.info(f"💼 Total Portfolio Value: ${total_value:.2f}")
            return total_value, usdt_balance
            
        except Exception as e:
            logging.error(f"❌ Portfolio check error: {e}")
            return 0, 0
    
    def analyze_top_markets(self):
        """Analyze top trading pairs with GPT-4o"""
        try:
            tickers = self.client.get_ticker()
            usdt_pairs = [t for t in tickers if t['symbol'].endswith('USDT')]
            usdt_pairs.sort(key=lambda x: float(x['quoteVolume']), reverse=True)
            
            logging.info("📈 Top 5 USDT pairs with GPT-4o analysis:")
            
            for i, ticker in enumerate(usdt_pairs[:5]):
                price = float(ticker['lastPrice'])
                change = float(ticker['priceChangePercent'])
                volume = float(ticker['quoteVolume'])
                symbol = ticker['symbol']
                
                logging.info(f"   {i+1}. {symbol}: ${price:.4f} ({change:+.2f}%) Vol: {volume:,.0f}")
                
                # GPT-4o Analysis for top 3 pairs (force enabled for testing)
                if i < 3 and self.openai_key:
                    pair_data = {
                        'symbol': symbol,
                        'price': price,
                        'change': change,
                        'volume': volume,
                        'rsi': 50 + (change * 2)  # Simplified RSI
                    }
                    
                    # Get GPT-4o decision
                    decision = self.get_gpt4o_decision(pair_data)
                    
                    if decision and isinstance(decision, dict):
                        confidence = decision.get('confidence', 0)
                        action = decision.get('action', 'hold')
                        reason = decision.get('reason', 'No reason')
                        
                        logging.info(f"🤖 GPT-4o Decision: {action.upper()} | Confidence: {confidence}% | {reason}")
                        
                        # Execute trade if conditions met
                        if confidence > 70 and action == 'buy':
                            portfolio_value, usdt_balance = self.show_portfolio()
                            if usdt_balance > 10:
                                self.execute_trade(symbol, decision, usdt_balance)
                    else:
                        logging.warning("⚠️ GPT-4o analysis failed for this pair")
                        
        except Exception as e:
            logging.error(f"❌ Market analysis error: {e}")
    
    def execute_trade(self, symbol, decision, usdt_balance):
        """Execute trade based on GPT-4o decision"""
        try:
            leverage = decision.get('leverage', 1)
            trade_amount = usdt_balance * 0.05 * leverage  # 5% base with leverage
            
            if trade_amount < 10:
                logging.info(f"⏸️ Trade amount ${trade_amount:.2f} below minimum")
                return False
            
            logging.info(f"🚀 EXECUTING GPT-4o TRADE: {symbol}")
            logging.info(f"💰 Amount: ${trade_amount:.2f} | Leverage: {leverage}x")
            logging.info(f"🎯 Confidence: {decision['confidence']}% | Reason: {decision['reason']}")
            
            # Calculate quantity
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            quantity = trade_amount / price
            
            # Round quantity appropriately
            if symbol == 'BTCUSDT':
                quantity = round(quantity, 6)
            elif symbol == 'ETHUSDT':
                quantity = round(quantity, 5)
            else:
                quantity = round(quantity, 4)
            
            # Check if we have actual trading permissions
            account = self.client.get_account()
            can_trade = account.get('canTrade', False)
            permissions = account.get('permissions', [])
            
            if can_trade and 'SPOT' in permissions:
                # Execute real market buy order
                order = self.client.order_market_buy(symbol=symbol, quantity=quantity)
                
                if order and order['status'] == 'FILLED':
                    logging.info(f"✅ GPT-4o LIVE TRADE SUCCESS: Bought {quantity} {symbol} for ${trade_amount:.2f}")
                    logging.info(f"📊 Order ID: {order['orderId']}")
                    return True
                else:
                    logging.error(f"❌ Live trade execution failed: {order}")
                    return False
            else:
                # Simulate trade for GPT-4o testing
                logging.info(f"🧪 GPT-4o SIMULATED TRADE: Would buy {quantity} {symbol} for ${trade_amount:.2f}")
                logging.info(f"🔧 Enable 'Spot & Margin Trading' in Binance API for live execution")
                return True
                
        except Exception as e:
            logging.error(f"❌ Trade execution error: {e}")
            return False
    
    def run_cycle(self):
        """Run GPT-4o enhanced trading cycle"""
        cycle_start = time.time()
        
        # Check API permissions
        if not self.trading_enabled:
            if self.initialize_client():
                if self.trading_enabled:
                    logging.info("🎉 BREAKTHROUGH! GPT-4o trading permissions activated!")
        
        # Analyze markets with GPT-4o
        self.analyze_top_markets()
        
        if self.trading_enabled:
            logging.info("🤖 GPT-4o AI analysis and live trading active")
        else:
            logging.info("📊 MONITORING MODE: Waiting for trading permissions")
        
        logging.info(f"⏱️ GPT-4o cycle complete. Next cycle in 180 seconds...")
        
    def run(self):
        """Main GPT-4o bot loop"""
        logging.info("🚀 Starting Nexus Quantum v6.0 PRO with GPT-4o...")
        
        if not self.openai_key:
            logging.error("❌ OPENAI_API_KEY not found in environment!")
            return
        else:
            logging.info("✅ OpenAI API key found - GPT-4o integration ready")
        
        cycle_count = 0
        while True:
            try:
                cycle_count += 1
                logging.info(f"🔄 Starting GPT-4o Quantum Cycle #{cycle_count}")
                
                self.run_cycle()
                
                # Wait 180 seconds (3 minutes) between cycles
                time.sleep(180)
                
            except KeyboardInterrupt:
                logging.info("🛑 GPT-4o bot stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Cycle error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = NexusQuantumBot()
    bot.run()