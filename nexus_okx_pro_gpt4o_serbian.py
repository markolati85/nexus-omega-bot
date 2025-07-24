#!/usr/bin/env python3
"""
NEXUS OKX PRO GPT-4o SERBIAN SERVER VERSION
Complementary strategy to work with Omega trader
Focus on larger positions and strategic trading
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

# Trading configuration - Complementary to Omega
CYCLE_INTERVAL = 180  # 3 minutes (complementary to Omega's 45 seconds)
MIN_TRADE_USDT = 1.0  # Lowered for test purchases
CONFIDENCE_THRESHOLD = 0.70  # Lowered to 70% for more aggressive trading
POSITION_SIZE = 0.15  # 15% of balance per trade

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_pro_serbian.log'),
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

class NexusProSerbian:
    def __init__(self):
        self.base_url = "https://www.okx.com"
        self.cycle_count = 0
        
        # Initialize database
        self.init_database()
        logger.info("🚀 NEXUS OKX PRO SERBIAN - STRATEGIC TRADER")
        logger.info("📈 Complementary to Omega with strategic focus")
        logger.info("🎯 Large positions with high confidence trades")
        
    def init_database(self):
        """Initialize SQLite database for trade tracking"""
        self.conn = sqlite3.connect('nexus_pro_serbian.db', check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pro_trades (
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
        logger.info("📊 Pro Serbian database initialized")

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
                        balance = float(detail.get('availBal', 0))
                        if balance > 0:
                            balances[currency] = balance
                
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

    def gpt4o_strategic_analysis(self, usdt_balance, market_conditions):
        """Get GPT-4o strategic trading analysis"""
        if not openai_client:
            return {"action": "HOLD", "symbol": "BTC", "confidence": 0.5, "reasoning": "No AI available"}
        
        try:
            prompt = f"""
            NEXUS PRO STRATEGIC TRADING ANALYSIS:
            
            Available USDT: ${usdt_balance:.2f}
            Position Size: 15% (${usdt_balance * 0.15:.2f})
            
            Current Market Conditions:
            - BTC Price: ${market_conditions.get('BTC', 0):.2f}
            - ETH Price: ${market_conditions.get('ETH', 0):.2f}
            - SOL Price: ${market_conditions.get('SOL', 0):.2f}
            
            STRATEGIC MISSION:
            - Execute test purchases for system validation (70%+ confidence)
            - Complement Omega trader which handles quick exits
            - Build strategic positions for medium-term holds
            - Target assets with strong fundamentals
            - ENABLE TEST PURCHASES for immediate trading activation
            
            AVAILABLE PAIRS: BTC-USDT, ETH-USDT, SOL-USDT
            
            Should we execute a strategic BUY order?
            Only recommend BUY if extremely confident about direction.
            
            Respond with JSON: {{"action": "BUY" or "HOLD", "symbol": "BTC/ETH/SOL", "confidence": 0.90, "reasoning": "detailed analysis"}}
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=300
            )
            
            analysis = json.loads(response.choices[0].message.content)
            logger.info(f"🧠 GPT-4o Strategic: {analysis['action']} {analysis.get('symbol', 'N/A')} ({analysis['confidence']:.0%})")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ GPT-4o analysis failed: {e}")
            return {"action": "HOLD", "symbol": "BTC", "confidence": 0.5, "reasoning": "AI analysis failed"}

    def execute_buy_order(self, symbol, usdt_amount):
        """Execute market buy order"""
        try:
            order_data = {
                "instId": f"{symbol}-USDT",
                "tdMode": "cash",
                "side": "buy",
                "ordType": "market",
                "sz": str(usdt_amount)
            }
            
            response = self.okx_request('POST', '/trade/order', order_data)
            
            if response and response.get('code') == '0':
                order_id = response['data'][0]['ordId']
                logger.info(f"✅ BUY order executed: ${usdt_amount} {symbol}-USDT | Order ID: {order_id}")
                return True, order_id
            else:
                logger.error(f"❌ BUY order failed: {response}")
                return False, None
                
        except Exception as e:
            logger.error(f"❌ Buy execution error: {e}")
            return False, None

    def pro_cycle(self):
        """Execute one strategic trading cycle"""
        self.cycle_count += 1
        logger.info(f"🔄 PRO CYCLE #{self.cycle_count}")
        
        # Get account balance
        balances = self.get_account_balance()
        if not balances:
            logger.warning("⚠️ No balance data - skipping cycle")
            return
        
        usdt_balance = balances.get('USDT', 0)
        logger.info(f"💵 Available USDT: ${usdt_balance:.2f}")
        
        if usdt_balance < MIN_TRADE_USDT:
            logger.info(f"💤 Insufficient USDT for strategic trading (need ${MIN_TRADE_USDT})")
            return
        
        # Get market conditions
        market_conditions = {
            'BTC': self.get_ticker_price('BTC-USDT'),
            'ETH': self.get_ticker_price('ETH-USDT'),
            'SOL': self.get_ticker_price('SOL-USDT')
        }
        
        # Get strategic analysis
        analysis = self.gpt4o_strategic_analysis(usdt_balance, market_conditions)
        
        # Execute trade if confidence is high enough
        if analysis['action'] == 'BUY' and analysis['confidence'] >= CONFIDENCE_THRESHOLD:
            symbol = analysis.get('symbol', 'BTC')
            trade_amount = usdt_balance * POSITION_SIZE
            
            success, order_id = self.execute_buy_order(symbol, trade_amount)
            
            if success:
                # Log trade to database
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO pro_trades (timestamp, cycle, symbol, action, amount, price, value, confidence, reasoning, success)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    self.cycle_count,
                    symbol,
                    'BUY',
                    trade_amount,
                    market_conditions.get(symbol, 0),
                    trade_amount,
                    analysis['confidence'],
                    analysis['reasoning'],
                    True
                ))
                self.conn.commit()
                
                logger.info(f"📈 STRATEGIC TRADE: ${trade_amount:.2f} {symbol} executed")
        else:
            logger.info(f"💤 HOLDING: {analysis['reasoning']}")

    def run(self):
        """Main trading loop"""
        logger.info("🚀 Starting Nexus Pro Serbian Strategic Trading")
        
        while True:
            try:
                start_time = time.time()
                
                # Execute trading cycle
                self.pro_cycle()
                
                # Calculate timing
                cycle_time = time.time() - start_time
                sleep_time = max(0, CYCLE_INTERVAL - cycle_time)
                
                logger.info(f"⏰ Pro cycle {self.cycle_count} completed in {cycle_time:.1f}s | Next in {sleep_time:.0f}s")
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except KeyboardInterrupt:
                logger.info("🛑 Pro Serbian trader stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Cycle error: {e}")
                time.sleep(60)  # Wait 60 seconds before retry

if __name__ == "__main__":
    trader = NexusProSerbian()
    trader.run()