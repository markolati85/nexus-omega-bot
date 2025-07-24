#!/usr/bin/env python3
"""
Direct Nexus Launch - Clean restart with working components
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
        logging.FileHandler('/opt/nexus-trading/nexus_direct.log'),
        logging.StreamHandler()
    ]
)

class SimpleNexusBot:
    def __init__(self):
        self.balance = 305.57
        self.start_time = time.time()
        self.cycle_count = 0
        self.setup_apis()
        
    def setup_apis(self):
        """Setup OKX and OpenAI APIs"""
        try:
            # OKX setup
            self.exchange = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'sandbox': False,
                'enableRateLimit': True
            })
            
            # OpenAI setup
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            logging.info("✅ APIs initialized successfully")
            
        except Exception as e:
            logging.error(f"❌ API setup error: {e}")
            self.exchange = None
            self.openai_client = None
    
    def get_balance(self):
        """Get current balance"""
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
    
    def get_market_data(self, symbol):
        """Get market data for symbol"""
        try:
            if self.exchange:
                ticker = self.exchange.fetch_ticker(symbol)
                return {
                    'price': ticker['last'],
                    'change': ticker['percentage'],
                    'volume': ticker['quoteVolume']
                }
        except Exception as e:
            logging.error(f"Market data error for {symbol}: {e}")
            return None
    
    def make_ai_decision(self, market_data):
        """Make AI trading decision with working implementation"""
        try:
            if not self.openai_client:
                return self.fallback_decision()
            
            prompt = f"""
            Analyze this crypto market data and decide: BUY, SELL, or HOLD
            
            Data: {json.dumps(market_data, indent=2)}
            
            Respond with ONLY this JSON format:
            {{"action": "hold", "confidence": 65, "reason": "market analysis"}}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            decision = json.loads(content)
            
            logging.info(f"AI Decision: {decision}")
            return decision
            
        except Exception as e:
            logging.error(f"AI decision error: {e}")
            return self.fallback_decision()
    
    def fallback_decision(self):
        """Fallback when AI fails"""
        return {
            "action": "hold",
            "confidence": 50,
            "reason": "AI fallback - monitoring market"
        }
    
    def update_dashboard_log(self):
        """Update dashboard log file"""
        try:
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'cycle': self.cycle_count,
                'balance': self.balance,
                'bot_status': 'RUNNING',
                'uptime': time.time() - self.start_time,
                'system_health': 'OPERATIONAL',
                'last_update': datetime.now().strftime('%H:%M:%S')
            }
            
            with open('/opt/nexus-trading/latest_log.json', 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Dashboard log error: {e}")
    
    def run_cycle(self):
        """Run one trading cycle"""
        self.cycle_count += 1
        
        # Get balance
        balance = self.get_balance()
        logging.info(f"💰 Balance: ${balance:.2f}")
        
        # Get market data
        market_data = {}
        pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        
        for pair in pairs:
            data = self.get_market_data(pair)
            if data:
                market_data[pair] = data
                logging.info(f"📊 {pair}: ${data['price']:.4f} ({data['change']:+.2f}%)")
        
        # Make AI decision
        if market_data:
            decision = self.make_ai_decision(market_data)
            logging.info(f"🤖 AI: {decision['action'].upper()} (confidence: {decision['confidence']}%)")
        
        # Update dashboard
        self.update_dashboard_log()
        
        logging.info(f"✅ Cycle {self.cycle_count} complete")
    
    def run(self):
        """Main bot loop"""
        logging.info("🚀 NEXUS BOT STARTING - DIRECT LAUNCH")
        logging.info(f"💰 Initial Balance: ${self.balance:.2f}")
        
        while True:
            try:
                self.run_cycle()
                time.sleep(60)  # 60-second cycles
                
            except KeyboardInterrupt:
                logging.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Cycle error: {e}")
                time.sleep(30)  # Wait before retry

if __name__ == "__main__":
    bot = SimpleNexusBot()
    bot.run()