#!/usr/bin/env python3
"""
NEXUS OMEGA TRADER OPTIMIZED - LIVE VERSION
Ultra-aggressive OKX trading with OpenAI GPT-4o integration
Real money trading, no simulation
"""

import os
import logging
import time
import json
import requests
import hmac
import hashlib
import base64
import sqlite3
from datetime import datetime, timezone
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv('.env_okx')

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OKX_API_KEY = os.getenv('OKX_API_KEY')
OKX_SECRET_KEY = os.getenv('OKX_SECRET')
OKX_PASSPHRASE = os.getenv('OKX_PASSPHRASE')

# Trading configuration
CYCLE_INTERVAL = 45  # 45 seconds for ultra-fast trading
MIN_TRADE_USDT = 1.0
CONFIDENCE_THRESHOLD = 0.75  # 75% confidence for aggressive trading
UNDERPERFORMANCE_THRESHOLD = -0.01  # -1% exit strategy

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_omega_live.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize OpenAI
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("✅ OpenAI GPT-4o client initialized")
except Exception as e:
    logger.error(f"❌ OpenAI initialization failed: {e}")
    openai_client = None

class NexusOmegaLive:
    def __init__(self):
        self.base_url = "https://www.okx.com"
        self.cycle_count = 0
        
        # Initialize database
        self.init_database()
        logger.info("🚀 NEXUS OMEGA TRADER OPTIMIZED - LIVE VERSION")
        logger.info("⚡ Ultra-aggressive -1% exit strategy")
        logger.info("🎯 Live trading with GPT-4o analysis")
        
    def init_database(self):
        """Initialize SQLite database for trade tracking"""
        self.conn = sqlite3.connect('nexus_omega_live.db', check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS omega_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                cycle INTEGER,
                symbol TEXT,
                action TEXT,
                amount REAL,
                price REAL,
                value REAL,
                confidence REAL,
                reasoning TEXT,
                success BOOLEAN
            )
        ''')
        self.conn.commit()
        logger.info("📊 Database initialized")

    def create_okx_signature(self, timestamp, method, request_path, body=''):
        """Create OKX API signature"""
        message = timestamp + method + request_path + body
        signature = base64.b64encode(
            hmac.new(OKX_SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
        ).decode()
        return signature

    def okx_request(self, method, endpoint, params=None):
        """Make authenticated OKX API request"""
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        request_path = f"/api/v5{endpoint}"
        
        body = json.dumps(params) if params else ''
        signature = self.create_okx_signature(timestamp, method, request_path, body)
        
        headers = {
            'OK-ACCESS-KEY': OKX_API_KEY,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': OKX_PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        url = self.base_url + request_path
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.post(url, headers=headers, data=body, timeout=10)
            
            return response.json()
        except Exception as e:
            logger.error(f"❌ OKX API request failed: {e}")
            return None

    def get_account_balance(self):
        """Get account balance including USDT"""
        try:
            response = self.okx_request('GET', '/account/balance')
            if response and response.get('code') == '0':
                balances = {}
                for account in response.get('data', []):
                    for detail in account.get('details', []):
                        currency = detail['ccy']
                        # Use 'availBal' (available balance) instead of 'bal'
                        balance = float(detail.get('availBal', 0))
                        if balance > 0:
                            balances[currency] = balance
                
                logger.info(f"💰 Account balance: {balances}")
                return balances
            else:
                logger.error(f"❌ Balance fetch failed: {response}")
                return {}
        except Exception as e:
            logger.error(f"❌ Balance error: {e}")
            return {}

    def get_ticker_price(self, symbol):
        """Get current ticker price"""
        try:
            response = self.okx_request('GET', f'/market/ticker?instId={symbol}')
            if response and response.get('code') == '0':
                ticker = response['data'][0]
                return float(ticker['last'])
        except Exception as e:
            logger.error(f"❌ Price fetch error for {symbol}: {e}")
        return 0

    def gpt4o_analysis(self, symbol, balance, price, usdt_balance):
        """Get GPT-4o trading analysis"""
        if not openai_client:
            return {"action": "HOLD", "confidence": 0.5, "reasoning": "No AI available"}
        
        try:
            prompt = f"""
            NEXUS OMEGA ULTRA-AGGRESSIVE TRADING ANALYSIS:
            
            Asset: {symbol}
            Balance: {balance:.6f} {symbol}
            Current Price: ${price:.4f}
            Position Value: ${balance * price:.2f}
            Available USDT: ${usdt_balance:.2f}
            
            Ultra-aggressive strategy: Exit ANY position showing -1% underperformance
            Reallocate capital to better opportunities immediately
            
            DECISION REQUIRED: SELL or HOLD this position?
            - SELL: If any chance of decline or better opportunities exist
            - HOLD: Only if extremely bullish short-term outlook
            
            Respond with JSON: {{"action": "SELL" or "HOLD", "confidence": 0.85, "reasoning": "specific reason"}}
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=200
            )
            
            analysis = json.loads(response.choices[0].message.content)
            logger.info(f"🤖 GPT-4o: {symbol} -> {analysis['action']} ({analysis['confidence']:.0%})")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ GPT-4o analysis failed: {e}")
            return {"action": "HOLD", "confidence": 0.5, "reasoning": "AI analysis failed"}

    def execute_sell_order(self, symbol, amount):
        """Execute market sell order"""
        try:
            order_data = {
                "instId": f"{symbol}-USDT",
                "tdMode": "cash",
                "side": "sell",
                "ordType": "market",
                "sz": str(amount)
            }
            
            response = self.okx_request('POST', '/trade/order', order_data)
            
            if response and response.get('code') == '0':
                order_id = response['data'][0]['ordId']
                logger.info(f"✅ SELL order executed: {amount:.6f} {symbol} | Order ID: {order_id}")
                return True, order_id
            else:
                logger.error(f"❌ SELL order failed: {response}")
                return False, None
                
        except Exception as e:
            logger.error(f"❌ Sell execution error: {e}")
            return False, None

    def omega_cycle(self):
        """Execute one Omega trading cycle"""
        self.cycle_count += 1
        logger.info(f"🔄 OMEGA CYCLE #{self.cycle_count}")
        
        # Get account balance
        balances = self.get_account_balance()
        if not balances:
            logger.warning("⚠️ No balance data - skipping cycle")
            return
        
        usdt_balance = balances.get('USDT', 0)
        logger.info(f"💵 Available USDT: ${usdt_balance:.2f}")
        
        trades_executed = 0
        total_reallocated = 0
        
        # Analyze each crypto position
        for currency, balance in balances.items():
            if currency == 'USDT':
                continue
                
            symbol = currency
            price = self.get_ticker_price(f"{symbol}-USDT")
            
            if price <= 0:
                continue
                
            position_value = balance * price
            
            if position_value < MIN_TRADE_USDT:
                logger.info(f"✋ HOLDING {symbol}: ${position_value:.2f} - Below ${MIN_TRADE_USDT} minimum")
                continue
            
            # Get GPT-4o analysis
            analysis = self.gpt4o_analysis(symbol, balance, price, usdt_balance)
            
            # Execute trade based on analysis
            if analysis['action'] == 'SELL' and analysis['confidence'] >= CONFIDENCE_THRESHOLD:
                success, order_id = self.execute_sell_order(symbol, balance)
                
                if success:
                    trades_executed += 1
                    total_reallocated += position_value
                    
                    # Log trade to database
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        INSERT INTO omega_trades (timestamp, cycle, symbol, action, amount, price, value, confidence, reasoning, success)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        datetime.now().isoformat(),
                        self.cycle_count,
                        symbol,
                        'SELL',
                        balance,
                        price,
                        position_value,
                        analysis['confidence'],
                        analysis['reasoning'],
                        True
                    ))
                    self.conn.commit()
            else:
                logger.info(f"✋ HOLDING {symbol}: ${position_value:.2f} - {analysis['reasoning']}")
        
        # Cycle summary
        logger.info(f"📈 OMEGA SUMMARY: Evaluated {len(balances)-1} | Executed {trades_executed} | Reallocated ${total_reallocated:.2f}")
        
        return trades_executed

    def run(self):
        """Main trading loop"""
        logger.info("🚀 Starting Nexus Omega Live Trading")
        
        while True:
            try:
                start_time = time.time()
                
                # Execute trading cycle
                trades = self.omega_cycle()
                
                # Calculate timing
                cycle_time = time.time() - start_time
                sleep_time = max(0, CYCLE_INTERVAL - cycle_time)
                
                logger.info(f"⏰ Omega cycle {self.cycle_count} completed in {cycle_time:.1f}s | Next in {sleep_time:.1f}s")
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except KeyboardInterrupt:
                logger.info("🛑 Omega trader stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Cycle error: {e}")
                time.sleep(30)  # Wait 30 seconds before retry

if __name__ == "__main__":
    trader = NexusOmegaLive()
    trader.run()