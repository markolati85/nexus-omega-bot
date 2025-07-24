#!/usr/bin/env python3
"""
Nexus Live Trading Verified - REAL MONEY TRADING ONLY
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
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/nexus-trading/nexus_live_verified.log'),
        logging.StreamHandler()
    ]
)

class NexusLiveTradingBot:
    def __init__(self):
        self.balance = 0
        self.start_time = time.time()
        self.cycle_count = 0
        self.trades_executed = 0
        self.setup_apis()
        
        # CRITICAL: DISABLE ALL SIMULATION MODES
        self.SIMULATE = False
        self.DEMO_MODE = False
        self.TEST_MODE = False
        
        logging.info("🚨 LIVE TRADING MODE ACTIVATED - NO SIMULATION")
        
    def setup_apis(self):
        """Setup OKX API with LIVE trading"""
        try:
            self.exchange = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'sandbox': False,  # CRITICAL: Live trading
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'
                }
            })
            
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Test API connection immediately
            test_balance = self.exchange.fetch_balance()
            logging.info(f"✅ LIVE API CONNECTED - Balance: ${test_balance.get('USDT', {}).get('free', 0):.2f}")
            
            # Load markets to verify trading capability
            markets = self.exchange.load_markets()
            logging.info(f"✅ {len(markets)} markets loaded for LIVE trading")
            
        except Exception as e:
            logging.error(f"❌ LIVE API setup error: {e}")
            sys.exit(1)  # Exit if API fails
    
    def get_live_balance(self):
        """Get real balance from OKX"""
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            self.balance = usdt_balance
            
            logging.info(f"💰 LIVE Balance: ${usdt_balance:.2f} USDT")
            return usdt_balance
            
        except Exception as e:
            logging.error(f"❌ Balance fetch error: {e}")
            return 0
    
    def get_market_data(self, symbol):
        """Get real market data"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=24)
            
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
                'bid': ticker['bid'],
                'ask': ticker['ask']
            }
            
        except Exception as e:
            logging.error(f"Market data error for {symbol}: {e}")
            return None
    
    def make_ai_decision(self, symbol, market_data):
        """AI decision for LIVE trading"""
        try:
            prompt = f"""
            LIVE TRADING DECISION REQUIRED - REAL MONEY AT RISK
            
            Symbol: {symbol}
            Price: ${market_data['price']:.2f}
            24h Change: {market_data['change']:+.2f}%
            RSI: {market_data['rsi']:.1f}
            Volume: ${market_data['volume']:,.0f}
            
            Available Balance: ${self.balance:.2f} USDT
            Position Size: 8% = ${self.balance * 0.08:.2f} per trade
            
            TRADING RULES:
            - RSI < 45: Strong BUY signal (oversold opportunity)
            - RSI > 55: Strong SELL signal (overbought opportunity)  
            - Only trade if confidence >= 70%
            - Use market orders for immediate execution
            - Current market shows good volatility for trading
            
            Respond with ONLY this JSON:
            {{
                "action": "buy/sell/hold",
                "confidence": 75-95,
                "reason": "detailed analysis for real money decision"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are making REAL MONEY trading decisions. Be precise and confident."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            decision = json.loads(content)
            logging.info(f"🤖 AI Decision: {decision}")
            return decision
            
        except Exception as e:
            logging.error(f"AI error: {e}")
            return {"action": "hold", "confidence": 50, "reason": "AI error - holding position"}
    
    def execute_live_trade(self, symbol, decision):
        """Execute REAL MONEY trade on OKX"""
        try:
            if decision['action'] == 'hold' or decision['confidence'] < 70:
                return False
            
            action = decision['action']
            trade_amount_usd = self.balance * 0.08  # 8% position size
            
            if trade_amount_usd < 5:  # OKX minimum
                logging.warning(f"⚠️ Trade amount ${trade_amount_usd:.2f} below $5 minimum")
                return False
            
            # Execute REAL trade
            if action == 'buy':
                # Calculate quantity to buy
                market_price = self.get_market_data(symbol)['price']
                quantity = trade_amount_usd / market_price
                
                logging.info(f"🟢 EXECUTING LIVE BUY: {symbol}")
                logging.info(f"   Amount: ${trade_amount_usd:.2f}")
                logging.info(f"   Quantity: {quantity:.6f}")
                logging.info(f"   Price: ${market_price:.2f}")
                
                # REAL ORDER EXECUTION
                order = self.exchange.create_market_buy_order(symbol, quantity)
                
                logging.info(f"✅ LIVE BUY ORDER EXECUTED")
                logging.info(f"   Order ID: {order['id']}")
                logging.info(f"   Status: {order['status']}")
                
            elif action == 'sell':
                # Get current holdings
                balance = self.exchange.fetch_balance()
                base_currency = symbol.split('/')[0]
                holdings = balance.get(base_currency, {}).get('free', 0)
                
                if holdings > 0:
                    logging.info(f"🔴 EXECUTING LIVE SELL: {symbol}")
                    logging.info(f"   Quantity: {holdings:.6f}")
                    
                    # REAL ORDER EXECUTION
                    order = self.exchange.create_market_sell_order(symbol, holdings)
                    
                    logging.info(f"✅ LIVE SELL ORDER EXECUTED")
                    logging.info(f"   Order ID: {order['id']}")
                    logging.info(f"   Status: {order['status']}")
                else:
                    logging.warning(f"⚠️ No {base_currency} holdings to sell")
                    return False
            
            # Log trade to file
            trade_log = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'action': action,
                'amount_usd': trade_amount_usd,
                'confidence': decision['confidence'],
                'reason': decision['reason'],
                'order_id': order['id'],
                'status': 'EXECUTED_LIVE'
            }
            
            with open('/opt/nexus-trading/live_trades.log', 'a') as f:
                f.write(json.dumps(trade_log) + '\n')
            
            self.trades_executed += 1
            logging.info(f"🎯 LIVE TRADE #{self.trades_executed} EXECUTED SUCCESSFULLY")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ LIVE TRADE EXECUTION ERROR: {e}")
            return False
    
    def update_dashboard_log(self, decisions):
        """Update dashboard with live data"""
        try:
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'cycle': self.cycle_count,
                'balance': self.balance,
                'bot_status': 'LIVE_TRADING_ACTIVE',
                'uptime': time.time() - self.start_time,
                'trades_executed': self.trades_executed,
                'trading_mode': 'LIVE_REAL_MONEY',
                'decisions': decisions,
                'last_update': datetime.now().strftime('%H:%M:%S')
            }
            
            with open('/opt/nexus-trading/latest_log.json', 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Dashboard log error: {e}")
    
    def run_live_cycle(self):
        """Run live trading cycle"""
        self.cycle_count += 1
        
        # Get live balance
        balance = self.get_live_balance()
        if balance <= 0:
            logging.error("❌ No USDT balance available for trading")
            return
        
        # Analyze trading pairs
        pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        decisions = {}
        
        for pair in pairs:
            market_data = self.get_market_data(pair)
            if market_data:
                logging.info(f"📊 {pair}: ${market_data['price']:.4f} ({market_data['change']:+.2f}%) RSI:{market_data['rsi']:.1f}")
                
                # Make AI decision
                decision = self.make_ai_decision(pair, market_data)
                decisions[pair] = decision
                
                logging.info(f"🤖 {pair} AI: {decision['action'].upper()} (confidence: {decision['confidence']}%)")
                logging.info(f"   Reason: {decision['reason']}")
                
                # Execute live trade if conditions met
                if decision['confidence'] >= 70 and decision['action'] != 'hold':
                    trade_executed = self.execute_live_trade(pair, decision)
                    if trade_executed:
                        logging.info(f"🎯 LIVE TRADE COMPLETED: {pair} - {decision['action'].upper()}")
                        # Wait before next trade
                        time.sleep(10)
        
        # Update dashboard
        self.update_dashboard_log(decisions)
        
        logging.info(f"✅ Live Cycle {self.cycle_count} complete (Live Trades: {self.trades_executed})")
    
    def run(self):
        """Main live trading loop"""
        logging.info("🚀 NEXUS LIVE TRADING BOT STARTING")
        logging.info("💰 REAL MONEY TRADING ACTIVATED")
        logging.info("⚠️  NO SIMULATION - ALL TRADES ARE REAL")
        
        while True:
            try:
                self.run_live_cycle()
                time.sleep(90)  # 90-second cycles
                
            except KeyboardInterrupt:
                logging.info("🛑 Live trading stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Cycle error: {e}")
                time.sleep(30)

if __name__ == "__main__":
    # Final verification
    if os.getenv('OKX_API_KEY') and os.getenv('OKX_SECRET') and os.getenv('OKX_PASSPHRASE'):
        bot = NexusLiveTradingBot()
        bot.run()
    else:
        logging.error("❌ Missing OKX API credentials")
        sys.exit(1)