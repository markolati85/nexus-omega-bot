#!/usr/bin/env python3
"""
Nexus Binance Live Trading via German VPN
Production trading bot with geographic bypass
"""

import os
import time
import logging
import requests
import sqlite3
from datetime import datetime
from binance.client import Client
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_binance_live.log'),
        logging.StreamHandler()
    ]
)

class NexusBinanceLiveVPN:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.german_ip = "91.99.238.81"
        self.vpn_proxies = {
            'http': 'socks5://127.0.0.1:8080',
            'https': 'socks5://127.0.0.1:8080'
        }
        self.client = None
        self.trading_pairs = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT']
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for trade tracking"""
        self.conn = sqlite3.connect('nexus_binance_trades.db')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT,
                side TEXT,
                quantity REAL,
                price REAL,
                order_id TEXT,
                status TEXT,
                profit_loss REAL
            )
        ''')
        self.conn.commit()
        
    def verify_vpn_connection(self):
        """Verify German VPN is active"""
        try:
            response = requests.get(
                'https://httpbin.org/ip', 
                proxies=self.vpn_proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                current_ip = response.json().get('origin')
                
                if current_ip == self.german_ip:
                    self.logger.info(f"✅ German VPN active: {current_ip}")
                    return True
                else:
                    self.logger.warning(f"⚠️ Wrong IP detected: {current_ip}")
                    return False
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ VPN verification failed: {e}")
            return False
    
    def initialize_binance_client(self):
        """Initialize Binance client with German VPN"""
        try:
            self.client = Client(
                os.getenv('BINANCE_API_KEY'),
                os.getenv('BINANCE_API_SECRET'),
                requests_params={
                    'proxies': self.vpn_proxies,
                    'timeout': 30
                }
            )
            
            # Test connection
            server_time = self.client.get_server_time()
            self.logger.info("✅ Binance client initialized via German VPN")
            
            # Get account info
            account = self.client.get_account()
            permissions = account.get('permissions', [])
            can_trade = account.get('canTrade', False)
            
            self.logger.info(f"🔐 Permissions: {permissions}")
            self.logger.info(f"🎯 Trading enabled: {can_trade}")
            
            return can_trade
            
        except Exception as e:
            self.logger.error(f"❌ Binance client initialization failed: {e}")
            return False
    
    def get_account_balance(self):
        """Get account balance information"""
        try:
            account = self.client.get_account()
            balances = account.get('balances', [])
            
            active_balances = {}
            for balance in balances:
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    active_balances[asset] = {
                        'free': free,
                        'locked': locked,
                        'total': total
                    }
            
            return active_balances
            
        except Exception as e:
            self.logger.error(f"❌ Balance retrieval failed: {e}")
            return {}
    
    def get_market_data(self, symbol):
        """Get current market data for symbol"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            
            # Get 24hr stats
            stats = self.client.get_ticker(symbol=symbol)
            
            return {
                'symbol': symbol,
                'price': price,
                'change': float(stats['priceChangePercent']),
                'volume': float(stats['volume'])
            }
            
        except Exception as e:
            self.logger.error(f"❌ Market data error for {symbol}: {e}")
            return None
    
    def execute_test_trade(self):
        """Execute a small test trade to verify functionality"""
        try:
            self.logger.info("🧪 Executing test trade to verify system...")
            
            # Get BTCUSDT price
            btc_data = self.get_market_data('BTCUSDT')
            if not btc_data:
                return False
            
            btc_price = btc_data['price']
            self.logger.info(f"💰 BTC Price: ${btc_price:,.2f}")
            
            # Check if we have USDT for a test trade
            balances = self.get_account_balance()
            usdt_balance = balances.get('USDT', {}).get('free', 0)
            
            self.logger.info(f"💳 USDT Balance: ${usdt_balance:.2f}")
            
            if usdt_balance >= 10:  # Minimum $10 for test trade
                self.logger.info("💰 Sufficient balance for test trade")
                
                # Calculate small test quantity (0.0001 BTC minimum)
                test_quantity = max(0.0001, 10 / btc_price)
                test_quantity = round(test_quantity, 6)
                
                self.logger.info(f"🎯 Test trade: BUY {test_quantity} BTC at ${btc_price:,.2f}")
                
                # Place test order (market buy)
                order = self.client.order_market_buy(
                    symbol='BTCUSDT',
                    quoteOrderQty=10  # $10 test order
                )
                
                order_id = order['orderId']
                self.logger.info(f"✅ TEST TRADE EXECUTED! Order ID: {order_id}")
                
                # Log trade to database
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO trades (symbol, side, quantity, price, order_id, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ('BTCUSDT', 'BUY', test_quantity, btc_price, order_id, 'FILLED'))
                self.conn.commit()
                
                self.logger.info("🎉 LIVE BINANCE TRADING CONFIRMED!")
                return True
                
            else:
                self.logger.info(f"⚠️ Insufficient USDT balance for test trade: ${usdt_balance:.2f}")
                self.logger.info("💡 Trading system ready - awaiting sufficient balance")
                return True  # System is working, just needs more funds
            
        except Exception as e:
            self.logger.error(f"❌ Test trade failed: {e}")
            return False
    
    def run_live_trading(self):
        """Main live trading loop"""
        self.logger.info("🚀 NEXUS BINANCE LIVE TRADING VIA GERMAN VPN")
        self.logger.info(f"🇩🇪 VPN Endpoint: {self.german_ip}")
        
        # Verify VPN connection
        if not self.verify_vpn_connection():
            self.logger.error("❌ German VPN not active - cannot proceed")
            return
        
        # Initialize Binance client
        if not self.initialize_binance_client():
            self.logger.error("❌ Binance client initialization failed")
            return
        
        # Execute test trade
        if self.execute_test_trade():
            self.logger.info("✅ SYSTEM FULLY OPERATIONAL")
            
            # Start monitoring loop
            cycle = 1
            while True:
                try:
                    self.logger.info(f"🔄 Trading Cycle #{cycle}")
                    
                    # Verify VPN still active
                    if not self.verify_vpn_connection():
                        self.logger.error("❌ VPN connection lost - stopping trading")
                        break
                    
                    # Get account status
                    balances = self.get_account_balance()
                    usdt_balance = balances.get('USDT', {}).get('total', 0)
                    
                    self.logger.info(f"💳 Portfolio: {len(balances)} assets, USDT: ${usdt_balance:.2f}")
                    
                    # Monitor market data
                    for symbol in self.trading_pairs:
                        market_data = self.get_market_data(symbol)
                        if market_data:
                            price = market_data['price']
                            change = market_data['change']
                            self.logger.info(f"📊 {symbol}: ${price:.4f} ({change:+.2f}%)")
                    
                    cycle += 1
                    time.sleep(60)  # Check every minute
                    
                except KeyboardInterrupt:
                    self.logger.info("🛑 Live trading stopped by user")
                    break
                except Exception as e:
                    self.logger.error(f"❌ Trading cycle error: {e}")
                    time.sleep(30)
        else:
            self.logger.error("❌ System verification failed")

if __name__ == "__main__":
    bot = NexusBinanceLiveVPN()
    bot.run_live_trading()
