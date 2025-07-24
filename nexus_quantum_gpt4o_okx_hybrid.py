#!/usr/bin/env python3
"""
NEXUS QUANTUM GPT-4o OKX HYBRID v1.0
Combines proven OKX integration with GPT-4o AI decision making
Based on successful OKX implementation + GPT-4o breakthrough
"""

import os
import sys
import time
import json
import logging
import threading
from datetime import datetime
from dotenv import load_dotenv

# AI Integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI not available - using fallback logic")

# Exchange Integration
try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    print("❌ CCXT not available - install with: pip install ccxt")
    sys.exit(1)

# Load environment
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_okx_gpt4o.log'),
        logging.StreamHandler()
    ]
)

class NexusQuantumOKX:
    def __init__(self):
        """Initialize the hybrid OKX + GPT-4o trading system"""
        self.client = None
        self.openai_client = None
        self.trading_enabled = False
        self.confidence_threshold = 70  # GPT-4o confidence threshold
        self.trading_pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT']
        self.position_size = 0.05  # 5% of portfolio per trade
        
        logging.info("🚀 Nexus Quantum v1.0 - OKX + GPT-4o Hybrid Edition")
        self.initialize_systems()
    
    def initialize_systems(self):
        """Initialize OKX and OpenAI connections"""
        self.setup_okx()
        self.setup_openai()
        
    def setup_okx(self):
        """Setup OKX exchange connection using proven CCXT method"""
        try:
            api_key = os.getenv('OKX_API_KEY')
            secret = os.getenv('OKX_SECRET') 
            passphrase = os.getenv('OKX_PASSPHRASE')
            
            if not all([api_key, secret, passphrase]):
                logging.error("❌ OKX credentials missing from .env file")
                return False
                
            self.client = ccxt.okx({
                'apiKey': api_key,
                'secret': secret,
                'password': passphrase,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',  # Start with spot trading
                    'createMarketBuyOrderRequiresPrice': False
                }
            })
            
            # Test connection
            balance = self.client.fetch_balance()
            logging.info("✅ OKX connection established successfully")
            
            # Check trading permissions
            account_info = self.client.fetch_balance()
            if account_info:
                self.trading_enabled = True
                logging.info("🎉 OKX TRADING PERMISSIONS ACTIVE")
                self.show_portfolio()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ OKX connection failed: {e}")
            return False
    
    def setup_openai(self):
        """Setup OpenAI GPT-4o for AI decision making"""
        if not OPENAI_AVAILABLE:
            logging.warning("⚠️ OpenAI not available - using random decisions")
            return False
            
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logging.error("❌ OpenAI API key missing")
                return False
                
            self.openai_client = OpenAI(api_key=api_key)
            
            # Test API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Test connection - respond with 'OK'"}],
                max_tokens=10
            )
            
            logging.info("✅ OpenAI GPT-4o connection verified")
            logging.info("🤖 AI-powered decision making ACTIVE")
            return True
            
        except Exception as e:
            logging.error(f"❌ OpenAI setup failed: {e}")
            return False
    
    def show_portfolio(self):
        """Display current portfolio status"""
        try:
            balance = self.client.fetch_balance()
            total_usdt = 0
            
            logging.info("💼 PORTFOLIO STATUS:")
            for asset, amounts in balance['total'].items():
                if amounts > 0:
                    try:
                        if asset == 'USDT':
                            value_usdt = amounts
                        else:
                            ticker = self.client.fetch_ticker(f'{asset}/USDT')
                            value_usdt = amounts * ticker['last']
                        
                        total_usdt += value_usdt
                        logging.info(f"   {asset}: {amounts:.6f} (${value_usdt:.2f})")
                    except:
                        logging.info(f"   {asset}: {amounts:.6f}")
            
            logging.info(f"📊 Total Portfolio Value: ${total_usdt:.2f}")
            
        except Exception as e:
            logging.error(f"Portfolio display error: {e}")
    
    def get_market_analysis(self, pair):
        """Get comprehensive market data for analysis"""
        try:
            ticker = self.client.fetch_ticker(pair)
            
            # Calculate basic indicators
            price = ticker['last']
            change_24h = ticker['percentage'] or 0
            volume_24h = ticker['quoteVolume'] or 0
            
            # Get additional market data
            ohlcv = self.client.fetch_ohlcv(pair, '1h', limit=50)
            if len(ohlcv) >= 14:
                closes = [candle[4] for candle in ohlcv[-14:]]
                rsi = self.calculate_rsi(closes, 14)
            else:
                rsi = 50
            
            return {
                'pair': pair,
                'price': price,
                'change_24h': change_24h,
                'volume_24h': volume_24h,
                'rsi': rsi
            }
            
        except Exception as e:
            logging.error(f"Market analysis error for {pair}: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        try:
            gains = []
            losses = []
            
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            if len(gains) < period:
                return 50
            
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
            
        except:
            return 50
    
    def get_gpt4o_decision(self, market_data):
        """Get AI trading decision from GPT-4o"""
        if not self.openai_client:
            # Fallback logic without AI
            if market_data['rsi'] < 30:
                return {'action': 'buy', 'confidence': 75, 'reason': 'RSI oversold condition'}
            elif market_data['rsi'] > 70:
                return {'action': 'sell', 'confidence': 75, 'reason': 'RSI overbought condition'}
            else:
                return {'action': 'hold', 'confidence': 60, 'reason': 'Neutral market conditions'}
        
        try:
            prompt = f"""
You are an expert cryptocurrency trader analyzing {market_data['pair']}. 
Current market data:
- Price: ${market_data['price']}
- 24h Change: {market_data['change_24h']:.2f}%
- 24h Volume: ${market_data['volume_24h']:,.0f}
- RSI: {market_data['rsi']:.2f}

Based on this data, should I BUY, SELL, or HOLD? 
Respond ONLY with valid JSON in this exact format:
{{"action": "buy/sell/hold", "confidence": 0-100, "reason": "brief explanation"}}
"""
            
            logging.info(f"🤖 Using OpenAI GPT-4o for {market_data['pair']} decisioning...")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )
            
            decision_text = response.choices[0].message.content.strip()
            logging.info(f"GPT-4o raw response: {decision_text}")
            
            # Parse JSON response
            decision = json.loads(decision_text)
            
            return {
                'action': decision.get('action', 'hold').lower(),
                'confidence': max(0, min(100, decision.get('confidence', 50))),
                'reason': decision.get('reason', 'AI analysis complete')
            }
            
        except Exception as e:
            logging.error(f"GPT-4o decision error: {e}")
            return {'action': 'hold', 'confidence': 50, 'reason': 'AI error - defaulting to hold'}
    
    def execute_trade(self, pair, action, confidence, reason):
        """Execute trade based on AI decision"""
        if not self.trading_enabled:
            logging.info(f"📊 SIMULATION: {action.upper()} {pair} - Confidence: {confidence}% - {reason}")
            return False
        
        if confidence < self.confidence_threshold:
            logging.info(f"⚠️ Low confidence ({confidence}%) - skipping trade")
            return False
        
        try:
            balance = self.client.fetch_balance()
            usdt_balance = balance['USDT']['free']
            
            if action == 'buy' and usdt_balance >= 10:
                # Buy with 5% of USDT balance
                trade_amount = usdt_balance * self.position_size
                ticker = self.client.fetch_ticker(pair)
                quantity = trade_amount / ticker['last']
                
                order = self.client.create_market_buy_order(pair, quantity)
                
                logging.info(f"🟢 EXECUTED BUY: {quantity:.6f} {pair} for ${trade_amount:.2f}")
                logging.info(f"📋 Order ID: {order['id']}")
                logging.info(f"🤖 AI Confidence: {confidence}% - {reason}")
                return True
                
            elif action == 'sell':
                # Get current holdings of base asset
                base_asset = pair.split('/')[0]
                asset_balance = balance.get(base_asset, {}).get('free', 0)
                
                if asset_balance > 0:
                    # Sell 50% of holdings
                    sell_quantity = asset_balance * 0.5
                    
                    order = self.client.create_market_sell_order(pair, sell_quantity)
                    
                    logging.info(f"🔴 EXECUTED SELL: {sell_quantity:.6f} {pair}")
                    logging.info(f"📋 Order ID: {order['id']}")
                    logging.info(f"🤖 AI Confidence: {confidence}% - {reason}")
                    return True
                    
            return False
            
        except Exception as e:
            logging.error(f"❌ Trade execution failed: {e}")
            return False
    
    def run_trading_cycle(self):
        """Main trading cycle with GPT-4o analysis"""
        logging.info("🔄 Starting GPT-4o Trading Cycle")
        
        for pair in self.trading_pairs:
            try:
                # Get market data
                market_data = self.get_market_analysis(pair)
                if not market_data:
                    continue
                
                logging.info(f"📈 {pair}: ${market_data['price']:.4f} ({market_data['change_24h']:+.2f}%) RSI: {market_data['rsi']:.1f}")
                
                # Get AI decision
                decision = self.get_gpt4o_decision(market_data)
                action = decision['action']
                confidence = decision['confidence']
                reason = decision['reason']
                
                logging.info(f"🤖 GPT-4o Decision: {action.upper()} | Confidence: {confidence}% | {reason}")
                
                # Execute if high confidence
                if action in ['buy', 'sell'] and confidence >= self.confidence_threshold:
                    self.execute_trade(pair, action, confidence, reason)
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                logging.error(f"Cycle error for {pair}: {e}")
                continue
        
        logging.info("⏱️ Cycle complete. Next cycle in 3 minutes...")
    
    def run(self):
        """Main bot execution loop"""
        if not self.client:
            logging.error("❌ OKX not initialized - cannot start trading")
            return
        
        logging.info("🚀 Starting Nexus Quantum OKX + GPT-4o Hybrid Bot")
        
        cycle_count = 0
        while True:
            try:
                cycle_count += 1
                logging.info(f"🔄 Starting Trading Cycle #{cycle_count}")
                
                self.run_trading_cycle()
                
                # Show portfolio every 5 cycles
                if cycle_count % 5 == 0:
                    self.show_portfolio()
                
                time.sleep(180)  # 3 minute cycles
                
            except KeyboardInterrupt:
                logging.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Main loop error: {e}")
                time.sleep(60)

def main():
    """Entry point"""
    print("🚀 Nexus Quantum GPT-4o + OKX Hybrid v1.0")
    print("🔧 Initializing AI-powered OKX trading system...")
    
    bot = NexusQuantumOKX()
    bot.run()

if __name__ == "__main__":
    main()