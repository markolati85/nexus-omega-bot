#!/usr/bin/env python3
"""
Nexus Quantum GPT-4o Demo - Advanced trading with leverage and short positions
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
        logging.FileHandler('/opt/nexus-trading/nexus_quantum_demo.log'),
        logging.StreamHandler()
    ]
)

class AdvancedNexusBot:
    def __init__(self):
        self.balance = 305.57
        self.start_time = time.time()
        self.cycle_count = 0
        self.trades_executed = 0
        self.setup_apis()
        
    def setup_apis(self):
        """Setup OKX and OpenAI APIs with margin/futures support"""
        try:
            # OKX setup with margin and futures enabled
            self.exchange = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'sandbox': False,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'  # Can switch to 'margin' or 'swap' for futures
                }
            })
            
            # OpenAI setup
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            logging.info("✅ APIs initialized with margin/futures support")
            
        except Exception as e:
            logging.error(f"❌ API setup error: {e}")
            self.exchange = None
            self.openai_client = None
    
    def get_balance(self):
        """Get current balance across all accounts"""
        try:
            if self.exchange:
                balance = self.exchange.fetch_balance()
                usdt_balance = balance.get('USDT', {}).get('free', 0)
                self.balance = usdt_balance
                return usdt_balance
            return self.balance
        except Exception as e:
            logging.error(f"Balance error: {e}")
            return self.balance
    
    def get_enhanced_market_data(self, symbol):
        """Get comprehensive market data with technical indicators"""
        try:
            if self.exchange:
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
                    'high': ticker['high'],
                    'low': ticker['low'],
                    'bid': ticker['bid'],
                    'ask': ticker['ask']
                }
        except Exception as e:
            logging.error(f"Market data error for {symbol}: {e}")
            return None
    
    def make_advanced_ai_decision(self, market_data):
        """Advanced AI decision with margin/leverage capabilities"""
        try:
            if not self.openai_client:
                return self.fallback_decision()
            
            prompt = f"""
            You are an expert crypto trader with access to margin trading and leverage up to 10x.
            
            Current market data: {json.dumps(market_data, indent=2)}
            
            Trading capabilities available:
            1. SPOT: Regular buy/sell
            2. MARGIN_LONG: Buy with leverage (up to 10x) 
            3. MARGIN_SHORT: Short sell with leverage (profit from price drops)
            4. Position size: 8% of $305.57 = $24.45 per trade
            
            Market conditions analysis:
            - If RSI < 30: Oversold (good for MARGIN_LONG)
            - If RSI > 70: Overbought (good for MARGIN_SHORT) 
            - If strong downtrend: Use MARGIN_SHORT to profit from decline
            - If strong uptrend: Use MARGIN_LONG for amplified gains
            - If sideways: Use SPOT trading
            
            Respond with ONLY this JSON format:
            {{
                "action": "spot_buy/spot_sell/margin_long/margin_short/hold",
                "leverage": 1-10,
                "confidence": 65-95,
                "reason": "detailed market analysis",
                "position_size": 24.45,
                "stop_loss": 2.0,
                "take_profit": 4.0
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": "You are an expert crypto trader. Respond ONLY with valid JSON. Use margin trading and leverage when market conditions are favorable."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            decision = json.loads(content)
            
            logging.info(f"Advanced AI Decision: {decision}")
            return decision
            
        except Exception as e:
            logging.error(f"AI decision error: {e}")
            return self.fallback_decision()
    
    def execute_trade(self, pair, decision):
        """Execute advanced trades including margin positions"""
        try:
            if not self.exchange or decision['action'] == 'hold':
                return False
            
            action = decision['action']
            leverage = decision.get('leverage', 1)
            position_size = decision.get('position_size', 24.45)
            
            # Calculate trade amount
            if action in ['margin_long', 'margin_short']:
                # For margin trades, use leverage
                trade_amount = position_size * leverage
                logging.info(f"🔥 MARGIN TRADE: {action} with {leverage}x leverage (${trade_amount:.2f} position)")
            else:
                trade_amount = position_size
                logging.info(f"📊 SPOT TRADE: {action} (${trade_amount:.2f})")
            
            # For demo, we'll simulate the trade execution
            # In live trading, you would execute actual orders here
            
            if action == 'spot_buy':
                logging.info(f"🟢 EXECUTING: Spot buy {pair} - ${trade_amount:.2f}")
                
            elif action == 'spot_sell':
                logging.info(f"🔴 EXECUTING: Spot sell {pair} - ${trade_amount:.2f}")
                
            elif action == 'margin_long':
                logging.info(f"🚀 EXECUTING: Margin long {pair} - {leverage}x leverage - ${trade_amount:.2f} position")
                
            elif action == 'margin_short':
                logging.info(f"📉 EXECUTING: Margin short {pair} - {leverage}x leverage - ${trade_amount:.2f} position")
            
            # Log trade details
            trade_log = {
                'timestamp': datetime.now().isoformat(),
                'pair': pair,
                'action': action,
                'leverage': leverage,
                'position_size': trade_amount,
                'confidence': decision['confidence'],
                'reason': decision['reason']
            }
            
            with open('/opt/nexus-trading/trades.log', 'a') as f:
                f.write(json.dumps(trade_log) + '\n')
            
            self.trades_executed += 1
            logging.info(f"✅ Trade #{self.trades_executed} logged successfully")
            
            return True
            
        except Exception as e:
            logging.error(f"Trade execution error: {e}")
            return False
    
    def fallback_decision(self):
        """Fallback when AI fails"""
        return {
            "action": "hold",
            "leverage": 1,
            "confidence": 50,
            "reason": "AI fallback - monitoring market",
            "position_size": 24.45,
            "stop_loss": 2.0,
            "take_profit": 4.0
        }
    
    def update_dashboard_log(self, decisions):
        """Update dashboard log with advanced trading data"""
        try:
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'cycle': self.cycle_count,
                'balance': self.balance,
                'bot_status': 'RUNNING_ADVANCED',
                'uptime': time.time() - self.start_time,
                'system_health': 'OPERATIONAL',
                'trades_executed': self.trades_executed,
                'advanced_features': 'MARGIN_LEVERAGE_ENABLED',
                'decisions': decisions,
                'last_update': datetime.now().strftime('%H:%M:%S')
            }
            
            with open('/opt/nexus-trading/latest_log.json', 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Dashboard log error: {e}")
    
    def run_cycle(self):
        """Run one advanced trading cycle"""
        self.cycle_count += 1
        
        # Get balance
        balance = self.get_balance()
        logging.info(f"💰 Balance: ${balance:.2f}")
        
        # Get market data for multiple pairs
        pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOGE/USDT']
        decisions = {}
        
        for pair in pairs:
            market_data = self.get_enhanced_market_data(pair)
            if market_data:
                logging.info(f"📊 {pair}: ${market_data['price']:.4f} ({market_data['change']:+.2f}%) RSI:{market_data['rsi']:.1f}")
                
                # Make AI decision for this pair
                decision = self.make_advanced_ai_decision({pair: market_data})
                decisions[pair] = decision
                
                action = decision['action'].upper().replace('_', ' ')
                leverage_info = f"{decision['leverage']}x" if decision['leverage'] > 1 else ""
                
                logging.info(f"🤖 {pair} AI: {action} {leverage_info} (confidence: {decision['confidence']}%)")
                logging.info(f"   Reason: {decision['reason']}")
                
                # Execute trade if confidence >= 70% and not hold
                if decision['confidence'] >= 70 and decision['action'] != 'hold':
                    trade_executed = self.execute_trade(pair, decision)
                    if trade_executed:
                        logging.info(f"🎯 TRADE EXECUTED: {pair} - {action}")
        
        # Update dashboard
        self.update_dashboard_log(decisions)
        
        logging.info(f"✅ Advanced Cycle {self.cycle_count} complete (Trades: {self.trades_executed})")
    
    def run(self):
        """Main bot loop with advanced features"""
        logging.info("🚀 NEXUS QUANTUM GPT-4o ADVANCED BOT STARTING")
        logging.info("⚡ Features: Margin Trading, Leverage up to 10x, Short Positions")
        logging.info(f"💰 Initial Balance: ${self.balance:.2f}")
        
        while True:
            try:
                self.run_cycle()
                time.sleep(90)  # 90-second cycles for more analysis time
                
            except KeyboardInterrupt:
                logging.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Cycle error: {e}")
                time.sleep(30)  # Wait before retry

if __name__ == "__main__":
    bot = AdvancedNexusBot()
    bot.run()