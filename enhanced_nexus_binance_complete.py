#!/usr/bin/env python3
"""
Enhanced Nexus AI Binance Bot with Telegram Notifications
Complete autonomous trading system with monitoring
"""
import os
import time
import logging
import sqlite3
import json
import threading
from datetime import datetime, timedelta
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv
import requests
from telegram_notifier import TelegramNotifier, load_telegram_config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/bot_output.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedNexusBinanceBot:
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = None
        self.telegram = load_telegram_config()
        self.db_file = '/root/nexus_bot.db'
        self.running = True
        self.last_balance = 0
        
        # Trading parameters
        self.position_size_percent = float(os.getenv('POSITION_SIZE_PERCENT', '5.0'))
        self.max_trade_usdt = float(os.getenv('MAX_TRADE_USDT', '100.0'))
        self.stop_loss_percent = float(os.getenv('STOP_LOSS_PERCENT', '2.0'))
        self.take_profit_percent = float(os.getenv('TAKE_PROFIT_PERCENT', '3.0'))
        
        # Trading pairs to monitor
        self.trading_pairs = [
            'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT',
            'XRPUSDT', 'BNBUSDT', 'DOTUSDT', 'LINKUSDT'
        ]
        
        self.setup_database()
        self.setup_binance_client()
        
    def setup_database(self):
        """Initialize SQLite database for trade logging"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    symbol TEXT,
                    side TEXT,
                    quantity REAL,
                    price REAL,
                    order_id TEXT,
                    status TEXT,
                    reason TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS balance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    usdt_balance REAL,
                    total_value REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database setup error: {e}")
    
    def setup_binance_client(self):
        """Initialize Binance client with API credentials"""
        try:
            if not self.api_key or not self.api_secret:
                raise ValueError("Binance API credentials not found")
            
            self.client = Client(self.api_key, self.api_secret)
            
            # Test connection
            account = self.client.get_account()
            logger.info(f"Binance connection successful - Trading: {account.get('canTrade', False)}")
            
            # Send startup notification
            if self.telegram:
                external_ip = self.get_external_ip()
                self.telegram.send_bot_startup(external_ip)
            
            return True
            
        except Exception as e:
            logger.error(f"Binance client setup failed: {e}")
            if self.telegram:
                self.telegram.send_error_alert("Connection Error", str(e))
            return False
    
    def get_external_ip(self):
        """Get current external IP address"""
        try:
            response = requests.get('https://ifconfig.me', timeout=10)
            return response.text.strip()
        except:
            return "Unknown"
    
    def get_account_balance(self):
        """Get USDT balance from Binance account"""
        try:
            if not self.client:
                return 0.0
            account = self.client.get_account()
            for balance in account['balances']:
                if balance['asset'] == 'USDT':
                    return float(balance['free'])
            return 0.0
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0.0
    
    def get_symbol_price(self, symbol):
        """Get current price for trading symbol"""
        try:
            if not self.client:
                return 0.0
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return 0.0
    
    def calculate_rsi(self, symbol, interval='1h', period=14):
        """Calculate RSI indicator"""
        try:
            if not self.client:
                return 50
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=period+1)
            closes = [float(kline[4]) for kline in klines]
            
            if len(closes) < period + 1:
                return 50  # Neutral RSI if insufficient data
            
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [delta if delta > 0 else 0 for delta in deltas]
            losses = [-delta if delta < 0 else 0 for delta in deltas]
            
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"RSI calculation error for {symbol}: {e}")
            return 50
    
    def generate_trading_signal(self, symbol):
        """Generate trading signal based on technical analysis"""
        try:
            # Get current price and RSI
            current_price = self.get_symbol_price(symbol)
            rsi = self.calculate_rsi(symbol)
            
            if current_price == 0:
                return None
            
            # Simple RSI-based strategy
            if rsi < 30:  # Oversold - potential buy signal
                return {
                    'action': 'BUY',
                    'symbol': symbol,
                    'price': current_price,
                    'rsi': rsi,
                    'reason': f'RSI oversold ({rsi:.1f})'
                }
            elif rsi > 70:  # Overbought - potential sell signal
                return {
                    'action': 'SELL',
                    'symbol': symbol,
                    'price': current_price,
                    'rsi': rsi,
                    'reason': f'RSI overbought ({rsi:.1f})'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Signal generation error for {symbol}: {e}")
            return None
    
    def execute_trade(self, signal):
        """Execute trade based on signal"""
        try:
            balance = self.get_account_balance()
            
            if balance < 10:  # Minimum balance check
                logger.warning(f"Insufficient balance: ${balance:.2f}")
                return False
            
            # Calculate position size
            trade_amount = min(
                balance * (self.position_size_percent / 100),
                self.max_trade_usdt
            )
            
            symbol = signal['symbol']
            action = signal['action']
            price = signal['price']
            
            if action == 'BUY':
                # Calculate quantity to buy
                quantity = trade_amount / price
                
                # Round to symbol precision (simplified)
                if 'BTC' in symbol:
                    quantity = round(quantity, 6)
                else:
                    quantity = round(quantity, 3)
                
                # Place buy order
                if not self.client:
                    return False
                order = self.client.order_market_buy(
                    symbol=symbol,
                    quantity=quantity
                )
                
                # Log trade
                self.log_trade(
                    symbol=symbol,
                    side='BUY',
                    quantity=quantity,
                    price=price,
                    order_id=order['orderId'],
                    status='FILLED',
                    reason=signal['reason']
                )
                
                # Send Telegram notification
                if self.telegram:
                    self.telegram.send_trade_signal('BUY', symbol, price, quantity, signal['reason'])
                
                logger.info(f"BUY executed: {quantity} {symbol} at ${price:.4f}")
                return True
                
            elif action == 'SELL':
                # Check if we have this asset to sell
                if not self.client:
                    return False
                account = self.client.get_account()
                asset = symbol.replace('USDT', '')
                
                asset_balance = 0
                for balance_info in account['balances']:
                    if balance_info['asset'] == asset:
                        asset_balance = float(balance_info['free'])
                        break
                
                if asset_balance > 0:
                    # Place sell order
                    order = self.client.order_market_sell(
                        symbol=symbol,
                        quantity=asset_balance
                    )
                    
                    # Log trade
                    self.log_trade(
                        symbol=symbol,
                        side='SELL',
                        quantity=asset_balance,
                        price=price,
                        order_id=order['orderId'],
                        status='FILLED',
                        reason=signal['reason']
                    )
                    
                    # Send Telegram notification
                    if self.telegram:
                        self.telegram.send_trade_signal('SELL', symbol, price, asset_balance, signal['reason'])
                    
                    logger.info(f"SELL executed: {asset_balance} {symbol} at ${price:.4f}")
                    return True
                else:
                    logger.info(f"No {asset} balance to sell")
                    return False
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            if self.telegram:
                self.telegram.send_error_alert("Trading Error", str(e))
            return False
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            if self.telegram:
                self.telegram.send_error_alert("System Error", str(e))
            return False
    
    def log_trade(self, symbol, side, quantity, price, order_id, status, reason):
        """Log trade to database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades (timestamp, symbol, side, quantity, price, order_id, status, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.utcnow().isoformat(),
                symbol, side, quantity, price, order_id, status, reason
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Trade logging error: {e}")
    
    def log_balance(self):
        """Log current balance to database"""
        try:
            balance = self.get_account_balance()
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO balance_history (timestamp, usdt_balance, total_value)
                VALUES (?, ?, ?)
            ''', (
                datetime.utcnow().isoformat(),
                balance,
                balance  # Simplified - could calculate total portfolio value
            ))
            
            conn.commit()
            conn.close()
            
            # Check for significant balance changes
            if self.last_balance > 0:
                change_percent = ((balance - self.last_balance) / self.last_balance) * 100
                if abs(change_percent) > 5:  # 5% change threshold
                    if self.telegram:
                        status = "📈 Increased" if change_percent > 0 else "📉 Decreased"
                        message = f"Balance {status} by {change_percent:.1f}%: ${balance:.2f}"
                        self.telegram.send_message(f"💰 {message}")
            
            self.last_balance = balance
            
        except Exception as e:
            logger.error(f"Balance logging error: {e}")
    
    def trading_cycle(self):
        """Main trading cycle"""
        logger.info("Starting trading cycle")
        
        try:
            # Log current balance
            self.log_balance()
            
            # Monitor each trading pair
            for symbol in self.trading_pairs:
                if not self.running:
                    break
                
                # Generate signal
                signal = self.generate_trading_signal(symbol)
                
                if signal:
                    logger.info(f"Signal generated: {signal['action']} {symbol} - {signal['reason']}")
                    
                    # Execute trade
                    success = self.execute_trade(signal)
                    if success:
                        logger.info(f"Trade executed successfully for {symbol}")
                    else:
                        logger.warning(f"Trade failed for {symbol}")
                
                # Small delay between symbol checks
                time.sleep(2)
        
        except Exception as e:
            logger.error(f"Trading cycle error: {e}")
            if self.telegram:
                self.telegram.send_error_alert("Cycle Error", str(e))
    
    def send_daily_summary(self):
        """Send daily trading summary"""
        try:
            if not self.telegram:
                return
            
            # Get today's trades
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            today = datetime.utcnow().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(*), symbol, side, price, quantity
                FROM trades 
                WHERE timestamp LIKE ?
                ORDER BY timestamp DESC
            ''', (f'{today}%',))
            
            trades = cursor.fetchall()
            trade_count = len(trades)
            
            # Get current balance
            current_balance = self.get_account_balance()
            
            # Calculate rough P&L (simplified)
            cursor.execute('''
                SELECT usdt_balance FROM balance_history 
                WHERE timestamp LIKE ? 
                ORDER BY timestamp ASC 
                LIMIT 1
            ''', (f'{today}%',))
            
            start_balance_row = cursor.fetchone()
            start_balance = start_balance_row[0] if start_balance_row else current_balance
            
            daily_pnl = current_balance - start_balance
            
            conn.close()
            
            # Send summary
            self.telegram.send_daily_summary(trade_count, daily_pnl, current_balance)
            
        except Exception as e:
            logger.error(f"Daily summary error: {e}")
    
    def run(self):
        """Main bot execution loop"""
        logger.info("🤖 NEXUS AI BINANCE BOT STARTED")
        logger.info(f"Trading pairs: {', '.join(self.trading_pairs)}")
        logger.info(f"Position size: {self.position_size_percent}%")
        logger.info(f"Max trade amount: ${self.max_trade_usdt}")
        
        cycle_count = 0
        last_daily_summary = datetime.utcnow().date()
        
        while self.running:
            try:
                cycle_count += 1
                logger.info(f"🔄 Starting cycle #{cycle_count}")
                
                # Run trading cycle
                self.trading_cycle()
                
                # Send daily summary (once per day)
                current_date = datetime.utcnow().date()
                if current_date > last_daily_summary:
                    self.send_daily_summary()
                    last_daily_summary = current_date
                
                # Wait before next cycle (3 minutes)
                logger.info("⏱️ Waiting 3 minutes for next cycle...")
                time.sleep(180)
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                if self.telegram:
                    self.telegram.send_error_alert("System Error", str(e))
                time.sleep(60)  # Wait 1 minute on error

def main():
    """Main function"""
    bot = EnhancedNexusBinanceBot()
    
    try:
        bot.run()
    except Exception as e:
        logger.error(f"Bot startup error: {e}")
        
        # Send error notification
        telegram = load_telegram_config()
        if telegram:
            telegram.send_error_alert("Startup Error", str(e))

if __name__ == "__main__":
    main()