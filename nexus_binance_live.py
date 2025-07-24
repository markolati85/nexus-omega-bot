#!/usr/bin/env python3
"""
Nexus Binance Complete - Advanced Trading Bot with Proxy Support
Full autonomous trading system for Binance
"""

import os
import time
import requests
import logging
import sqlite3
import json
from datetime import datetime
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_binance.log'),
        logging.StreamHandler()
    ]
)

class NexusBinanceComplete:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.binance_client = None
        self.working_proxy = None
        self.trading_active = False
        
        # Initialize database
        self.init_database()
        
        # European proxy servers
        self.proxy_list = [
            {'http': 'http://51.15.25.233:8080', 'https': 'http://51.15.25.233:8080'},
            {'http': 'http://193.138.218.74:3128', 'https': 'http://193.138.218.74:3128'},
            {'http': 'http://185.232.23.186:8080', 'https': 'http://185.232.23.186:8080'},
            {'http': 'http://95.216.12.141:3128', 'https': 'http://95.216.12.141:3128'},
        ]
        
        # Trading configuration
        self.config = {
            'position_size_pct': 5.0,  # 5% per trade
            'min_trade_usdt': 10.0,
            'max_trade_usdt': 100.0,
            'stop_loss_pct': 2.0,
            'take_profit_pct': 3.0,
            'trading_pairs': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT', 'BNBUSDT']
        }
    
    def init_database(self):
        """Initialize SQLite database for trade tracking"""
        try:
            conn = sqlite3.connect('nexus_binance.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    symbol TEXT,
                    side TEXT,
                    quantity REAL,
                    price REAL,
                    value_usdt REAL,
                    order_id TEXT,
                    status TEXT,
                    profit_loss REAL DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    total_value_usdt REAL,
                    usdt_balance REAL,
                    crypto_value REAL,
                    active_assets INTEGER
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Database initialized")
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
    
    def test_proxy_and_binance(self, proxy_config):
        """Test proxy and Binance access"""
        try:
            # Test proxy connectivity
            response = requests.get(
                'https://ipinfo.io/json',
                proxies=proxy_config,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                ip = data.get('ip')
                country = data.get('country')
                
                # Test Binance API
                binance_response = requests.get(
                    'https://api.binance.com/api/v3/ping',
                    proxies=proxy_config,
                    timeout=15
                )
                
                if binance_response.status_code == 200:
                    self.logger.info(f"SUCCESS: Proxy {ip} ({country}) works for Binance")
                    return True
                    
        except Exception as e:
            self.logger.warning(f"Proxy test failed: {e}")
        
        return False
    
    def setup_binance_connection(self):
        """Setup Binance connection with proxy"""
        self.logger.info("Setting up Binance connection...")
        
        # First try direct connection
        try:
            temp_client = Client(
                os.getenv('BINANCE_API_KEY'),
                os.getenv('BINANCE_API_SECRET')
            )
            
            # Test direct connection
            response = requests.get('https://api.binance.com/api/v3/ping', timeout=10)
            if response.status_code == 200:
                account = temp_client.get_account()
                if account.get('canTrade', False):
                    self.logger.info("Direct Binance connection successful")
                    self.binance_client = temp_client
                    return True
                    
        except Exception as e:
            if '-2015' in str(e):
                self.logger.info("Geographic restriction detected - trying proxies")
            else:
                self.logger.warning(f"Direct connection failed: {e}")
        
        # Try proxy connections
        for proxy_config in self.proxy_list:
            if self.test_proxy_and_binance(proxy_config):
                try:
                    # Set proxy environment variables
                    os.environ['HTTP_PROXY'] = proxy_config['http']
                    os.environ['HTTPS_PROXY'] = proxy_config['https']
                    
                    self.binance_client = Client(
                        os.getenv('BINANCE_API_KEY'),
                        os.getenv('BINANCE_API_SECRET')
                    )
                    
                    # Test authenticated connection
                    account = self.binance_client.get_account()
                    if account.get('canTrade', False):
                        self.logger.info(f"Binance connected via proxy: {proxy_config['http']}")
                        self.working_proxy = proxy_config
                        return True
                        
                except Exception as e:
                    self.logger.warning(f"Proxy connection failed: {e}")
                    continue
        
        self.logger.error("All connection attempts failed")
        return False
    
    def get_portfolio_data(self):
        """Get comprehensive portfolio data"""
        try:
            account = self.binance_client.get_account()
            balances = account.get('balances', [])
            
            usdt_balance = 0
            crypto_value = 0
            active_assets = []
            
            for balance in balances:
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0.00001:
                    asset = balance['asset']
                    
                    if asset == 'USDT':
                        usdt_balance = total
                    else:
                        try:
                            ticker = self.binance_client.get_symbol_ticker(symbol=f"{asset}USDT")
                            price = float(ticker['price'])
                            value_usdt = total * price
                            
                            if value_usdt > 1:
                                active_assets.append({
                                    'asset': asset,
                                    'amount': total,
                                    'free': free,
                                    'locked': locked,
                                    'price_usdt': price,
                                    'value_usdt': value_usdt
                                })
                                crypto_value += value_usdt
                                
                        except:
                            continue
            
            total_value = usdt_balance + crypto_value
            
            return {
                'usdt_balance': usdt_balance,
                'crypto_value': crypto_value,
                'total_value': total_value,
                'active_assets': active_assets,
                'asset_count': len(active_assets)
            }
            
        except Exception as e:
            self.logger.error(f"Portfolio data error: {e}")
            return None
    
    def save_portfolio_snapshot(self, portfolio_data):
        """Save portfolio snapshot to database"""
        try:
            conn = sqlite3.connect('nexus_binance.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO portfolio_snapshots 
                (timestamp, total_value_usdt, usdt_balance, crypto_value, active_assets)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                portfolio_data['total_value'],
                portfolio_data['usdt_balance'],
                portfolio_data['crypto_value'],
                portfolio_data['asset_count']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Portfolio snapshot error: {e}")
    
    def analyze_market_signals(self, symbol):
        """Analyze market signals for trading decisions"""
        try:
            # Get 24hr ticker statistics
            stats = self.binance_client.get_ticker(symbol=symbol)
            
            price_change_pct = float(stats['priceChangePercent'])
            volume = float(stats['volume'])
            high_price = float(stats['highPrice'])
            low_price = float(stats['lowPrice'])
            current_price = float(stats['lastPrice'])
            
            # Simple momentum analysis
            signals = {
                'symbol': symbol,
                'current_price': current_price,
                'price_change_pct': price_change_pct,
                'volume': volume,
                'price_position': (current_price - low_price) / (high_price - low_price) if high_price > low_price else 0.5
            }
            
            # Generate buy/sell signals
            signals['signal'] = 'HOLD'
            
            if price_change_pct > 2 and signals['price_position'] < 0.7 and volume > 1000:
                signals['signal'] = 'BUY'
                signals['confidence'] = min(85, 50 + abs(price_change_pct) * 2)
            elif price_change_pct < -2 and signals['price_position'] > 0.3:
                signals['signal'] = 'SELL'
                signals['confidence'] = min(85, 50 + abs(price_change_pct) * 2)
            else:
                signals['confidence'] = 30
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Market analysis error for {symbol}: {e}")
            return None
    
    def execute_trade(self, symbol, side, quantity, price=None):
        """Execute trade on Binance"""
        try:
            if price:
                # Limit order
                order = self.binance_client.order_limit(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    price=str(price)
                )
            else:
                # Market order
                if side == 'BUY':
                    order = self.binance_client.order_market_buy(
                        symbol=symbol,
                        quantity=quantity
                    )
                else:
                    order = self.binance_client.order_market_sell(
                        symbol=symbol,
                        quantity=quantity
                    )
            
            if order.get('status') == 'FILLED':
                self.logger.info(f"Trade executed: {side} {quantity} {symbol}")
                
                # Save to database
                executed_qty = float(order.get('executedQty', 0))
                avg_price = float(order.get('fills', [{}])[0].get('price', 0))
                value_usdt = executed_qty * avg_price
                
                conn = sqlite3.connect('nexus_binance.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO trades 
                    (timestamp, symbol, side, quantity, price, value_usdt, order_id, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    symbol,
                    side,
                    executed_qty,
                    avg_price,
                    value_usdt,
                    order.get('orderId'),
                    'FILLED'
                ))
                
                conn.commit()
                conn.close()
                
                return True
            else:
                self.logger.warning(f"Trade not filled: {order.get('status')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Trade execution failed: {e}")
            return False
    
    def trading_cycle(self):
        """Main trading cycle"""
        try:
            # Get portfolio data
            portfolio = self.get_portfolio_data()
            if not portfolio:
                return False
            
            self.logger.info(f"Portfolio: ${portfolio['total_value']:.2f} | USDT: ${portfolio['usdt_balance']:.2f} | Crypto: ${portfolio['crypto_value']:.2f}")
            
            # Save snapshot
            self.save_portfolio_snapshot(portfolio)
            
            # Show active assets
            for asset in portfolio['active_assets'][:5]:
                self.logger.info(f"  {asset['asset']}: {asset['amount']:.6f} (${asset['value_usdt']:.2f})")
            
            # Analyze trading opportunities
            if portfolio['usdt_balance'] > self.config['min_trade_usdt']:
                for symbol in self.config['trading_pairs']:
                    signals = self.analyze_market_signals(symbol)
                    
                    if signals and signals['signal'] == 'BUY' and signals['confidence'] > 70:
                        # Calculate position size
                        trade_amount = min(
                            portfolio['usdt_balance'] * (self.config['position_size_pct'] / 100),
                            self.config['max_trade_usdt']
                        )
                        
                        if trade_amount >= self.config['min_trade_usdt']:
                            quantity = trade_amount / signals['current_price']
                            
                            # Round to appropriate precision
                            if symbol in ['BTCUSDT']:
                                quantity = round(quantity, 6)
                            elif symbol in ['ETHUSDT']:
                                quantity = round(quantity, 5)
                            else:
                                quantity = round(quantity, 4)
                            
                            self.logger.info(f"🚀 LIVE BUY signal: {symbol} | Confidence: {signals['confidence']}% | Amount: ${trade_amount:.2f}")
                            
                            # Execute live trade - ENABLED
                            if self.execute_trade(symbol, 'BUY', quantity):
                                self.logger.info(f"✅ Successfully bought {quantity} {symbol} for ${trade_amount:.2f}")
                                time.sleep(5)  # Cool down
                            else:
                                self.logger.error(f"❌ Failed to execute {symbol} buy order")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Trading cycle error: {e}")
            return False
    
    def run_complete_system(self):
        """Run the complete trading system"""
        self.logger.info("NEXUS BINANCE COMPLETE SYSTEM STARTING")
        
        # Setup connection
        if not self.setup_binance_connection():
            self.logger.error("Cannot establish Binance connection")
            return False
        
        self.logger.info("System operational - starting autonomous trading")
        self.trading_active = True
        
        cycle = 1
        
        while self.trading_active:
            try:
                self.logger.info(f"Trading Cycle #{cycle}")
                
                if self.trading_cycle():
                    self.logger.info("Cycle completed successfully")
                else:
                    self.logger.warning("Cycle had issues")
                
                cycle += 1
                time.sleep(180)  # 3-minute cycles
                
            except KeyboardInterrupt:
                self.logger.info("Trading stopped by user")
                self.trading_active = False
                break
            except Exception as e:
                self.logger.error(f"System error: {e}")
                time.sleep(60)
        
        return True

if __name__ == "__main__":
    nexus = NexusBinanceComplete()
    nexus.run_complete_system()