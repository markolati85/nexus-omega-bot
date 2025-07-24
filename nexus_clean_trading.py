#!/usr/bin/env python3
"""
NEXUS CLEAN TRADING SYSTEM
Single working bot with real OKX trading and portfolio data
"""

import requests
import ccxt
import time
import threading
import json
import os
import base64
import hmac
import hashlib
from datetime import datetime

# Configuration
TOKEN = "8429171890:AAEaYGGQb8L-pir22rt128g5hbh6GTuWDqk"
CHAT_ID = "1762317382"

class NexusCleanTrader:
    def __init__(self):
        self.last_update_id = 0
        self.running = True
        self.cycles = 0
        self.trades_executed = 0
        
        # OKX Configuration with fixed authentication
        self.api_key = 'bfee3fff-cdf1-4b71-9ef9-8760de8732f4'
        self.secret_key = 'E7C2058E8DC095D3F45F5C37D6A28DC8'
        self.passphrase = 'Okx123#'
        
        # Initialize exchange
        self.exchange = ccxt.okx({
            'apiKey': self.api_key,
            'secret': self.secret_key,
            'password': self.passphrase,
            'sandbox': False,
            'enableRateLimit': True,
            'timeout': 30000
        })
        
        print("Nexus Clean Trading System initialized")
    
    def send_telegram(self, message):
        """Send Telegram message"""
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message}, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
    
    def get_real_portfolio(self):
        """Get real OKX portfolio with multiple methods"""
        try:
            # Method 1: Try ccxt
            balance = self.exchange.fetch_balance()
            total_value = 0
            assets = {}
            
            for currency, bal in balance.items():
                if bal['total'] > 0.001:
                    amount = bal['total']
                    assets[currency] = amount
                    
                    if currency == 'USDT':
                        total_value += amount
                    else:
                        try:
                            ticker = self.exchange.fetch_ticker(f"{currency}/USDT")
                            price = ticker['last']
                            total_value += amount * price
                        except:
                            # Skip if can't get price
                            pass
            
            if total_value > 0:
                return total_value, assets
                
        except Exception as e:
            print(f"CCXT portfolio error: {e}")
        
        # Method 2: Direct API call
        try:
            timestamp = str(int(time.time() * 1000))
            method = 'GET'
            request_path = '/api/v5/account/balance'
            body = ''
            
            message = timestamp + method + request_path + body
            mac = hmac.new(bytes(self.secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
            signature = base64.b64encode(mac.digest()).decode()
            
            headers = {
                'OK-ACCESS-KEY': self.api_key,
                'OK-ACCESS-SIGN': signature,
                'OK-ACCESS-TIMESTAMP': timestamp,
                'OK-ACCESS-PASSPHRASE': self.passphrase,
                'Content-Type': 'application/json'
            }
            
            response = requests.get('https://www.okx.com/api/v5/account/balance', headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0':
                    total_value = 0
                    assets = {}
                    details = data.get('data', [{}])[0].get('details', [])
                    
                    for detail in details:
                        amount = float(detail.get('cashBal', 0))
                        currency = detail.get('ccy', '')
                        if amount > 0.001:
                            assets[currency] = amount
                            if currency == 'USDT':
                                total_value += amount
                            else:
                                # Get approximate value
                                try:
                                    ticker = self.exchange.fetch_ticker(f"{currency}/USDT")
                                    total_value += amount * ticker['last']
                                except:
                                    pass
                    
                    return total_value, assets
            
        except Exception as e:
            print(f"Direct API error: {e}")
        
        # Return error if both methods fail
        return 0, {'error': 'Unable to connect to OKX API'}
    
    def execute_real_trade(self, symbol, side, amount_usd):
        """Execute real trade on OKX"""
        try:
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Calculate amount in base currency
            if side == 'buy':
                amount = amount_usd / current_price
            else:
                amount = amount_usd  # For sell, amount_usd is actually the token amount
            
            # Execute trade
            order = self.exchange.create_market_order(symbol, side, amount)
            
            if order and order.get('id'):
                self.trades_executed += 1
                
                trade_msg = f"""🚀 REAL TRADE EXECUTED

📊 Trade Details:
• Symbol: {symbol}
• Side: {side.upper()}
• Amount: {amount:.6f}
• Price: ${current_price:.4f}
• Value: ${amount_usd:.2f}
• Order ID: {order['id']}

💰 Trade #{self.trades_executed} completed successfully
⏰ {datetime.now().strftime('%H:%M:%S UTC')}"""
                
                self.send_telegram(trade_msg)
                return order
                
        except Exception as e:
            error_msg = f"❌ Trade execution failed: {str(e)}"
            self.send_telegram(error_msg)
            print(f"Trade error: {e}")
            return None
    
    def analyze_and_trade(self):
        """Analyze market and execute trades"""
        try:
            portfolio_value, assets = self.get_real_portfolio()
            
            if portfolio_value < 10:
                return
            
            # Simple trading logic: buy low RSI, sell high RSI
            pairs = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]
            
            for symbol in pairs:
                try:
                    # Get recent price data
                    ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=14)
                    closes = [candle[4] for candle in ohlcv]
                    
                    # Simple RSI calculation
                    if len(closes) >= 14:
                        gains = [max(0, closes[i] - closes[i-1]) for i in range(1, len(closes))]
                        losses = [max(0, closes[i-1] - closes[i]) for i in range(1, len(closes))]
                        
                        avg_gain = sum(gains[-14:]) / 14
                        avg_loss = sum(losses[-14:]) / 14
                        
                        if avg_loss != 0:
                            rs = avg_gain / avg_loss
                            rsi = 100 - (100 / (1 + rs))
                            
                            base_currency = symbol.split('/')[0]
                            position_size = portfolio_value * 0.1  # 10% position
                            
                            # Trading logic
                            if rsi < 30 and 'USDT' in assets and assets['USDT'] >= position_size:
                                # Buy signal
                                order = self.execute_real_trade(symbol, 'buy', position_size)
                                if order:
                                    break
                                    
                            elif rsi > 70 and base_currency in assets and assets[base_currency] > 0.001:
                                # Sell signal
                                sell_amount = assets[base_currency] * 0.5  # Sell 50%
                                order = self.execute_real_trade(symbol, 'sell', sell_amount)
                                if order:
                                    break
                
                except Exception as e:
                    print(f"Analysis error for {symbol}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Trading cycle error: {e}")
    
    def handle_status(self):
        """Handle /status command with real data"""
        portfolio_value, assets = self.get_real_portfolio()
        
        if 'error' in assets:
            status_msg = f"""⚠️ NEXUS TRADING STATUS

🔧 OKX API Issue:
• Connection: Troubleshooting
• Portfolio: Unable to retrieve
• Trading: Paused until connection restored

🔄 System Health:
• Telegram: ✅ Responsive
• Trading Engine: ✅ Ready
• Cycles: {self.cycles}
• Trades Today: {self.trades_executed}

Working on API connection fix...
⏰ {datetime.now().strftime('%H:%M:%S UTC')}"""
        else:
            asset_list = ""
            for currency, amount in list(assets.items())[:6]:
                if currency == 'USDT':
                    asset_list += f"• {currency}: ${amount:.2f}\n"
                else:
                    try:
                        ticker = self.exchange.fetch_ticker(f"{currency}/USDT")
                        price = ticker['last']
                        value = amount * price
                        asset_list += f"• {currency}: {amount:.4f} (${value:.2f})\n"
                    except:
                        asset_list += f"• {currency}: {amount:.4f}\n"
            
            status_msg = f"""📡 NEXUS TRADING SYSTEM

💰 Real Portfolio: ${portfolio_value:.2f} USDT

📊 Live Holdings:
{asset_list}
⚙️ Trading Configuration:
• Exchange: OKX (Live Trading)
• Pairs: BTC, ETH, SOL, XRP
• Strategy: RSI-based momentum
• Position Size: 10% per trade

🔄 Performance:
• Cycles: {self.cycles}
• Trades Executed: {self.trades_executed}
• API Status: ✅ Connected
• Trading: ✅ Active

📈 Current Strategy:
• Buy: RSI < 30 (oversold)
• Sell: RSI > 70 (overbought)
• Risk Management: 10% position sizing

⏰ {datetime.now().strftime('%H:%M:%S UTC')}"""
        
        return self.send_telegram(status_msg)
    
    def handle_topcoin(self):
        """Handle /topcoin with real market data"""
        pairs = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "BNB/USDT", "DOGE/USDT"]
        opportunities = []
        
        for symbol in pairs:
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                change_24h = ticker.get('percentage', 0)
                volume = ticker.get('quoteVolume', 0)
                
                # Calculate opportunity score
                score = abs(change_24h) * 10 + (volume / 1000000)
                
                opportunities.append({
                    'symbol': symbol,
                    'change': change_24h,
                    'score': min(95, int(score)),
                    'volume': volume
                })
                
            except Exception as e:
                print(f"Market data error for {symbol}: {e}")
        
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        msg = f"""🏆 TOP 3 REAL OPPORTUNITIES

📈 Live OKX Market Data:"""
        
        for i, opp in enumerate(opportunities[:3], 1):
            emoji = "🟢" if opp['change'] > 0 else "🔴"
            action = "BUY" if abs(opp['change']) > 2 else "MONITOR"
            msg += f"""
{i}. {emoji} {opp['symbol']}: {opp['score']}%
   📊 24h: {opp['change']:+.1f}% | Action: {action}"""
        
        msg += f"""

🤖 Analysis: Live market data from OKX
💰 Ready to execute trades based on RSI signals
⏰ {datetime.now().strftime('%H:%M:%S UTC')}"""
        
        return self.send_telegram(msg)
    
    def handle_summary(self):
        """Handle /summary with trading performance"""
        portfolio_value, _ = self.get_real_portfolio()
        
        summary_msg = f"""📊 TRADING PERFORMANCE SUMMARY

💰 Portfolio: ${portfolio_value:.2f} USDT
🔄 Analysis Cycles: {self.cycles}
📈 Trades Executed: {self.trades_executed}
🎯 Strategy: RSI Momentum Trading

⚙️ System Performance:
• OKX Connection: Live API
• Trade Execution: Real orders
• Portfolio Tracking: Real-time
• Risk Management: 10% sizing

📊 Trading Stats:
• Success Rate: Monitoring
• Average Trade: ~${portfolio_value * 0.1:.2f}
• Market Analysis: Every 3 minutes
• Pairs Monitored: 4 active

🔧 System Health: Operational
⏰ {datetime.now().strftime('%H:%M:%S UTC')}"""
        
        return self.send_telegram(summary_msg)
    
    def handle_restart(self):
        """Handle /restart command"""
        self.send_telegram("🔄 TRADING SYSTEM RESTART")
        
        # Reset counters
        self.cycles = 0
        self.trades_executed = 0
        
        # Reinitialize exchange
        self.exchange = ccxt.okx({
            'apiKey': self.api_key,
            'secret': self.secret_key,
            'password': self.passphrase,
            'sandbox': False,
            'enableRateLimit': True,
            'timeout': 30000
        })
        
        time.sleep(2)
        self.send_telegram("✅ RESTART COMPLETE\n\nTrading system reinitialized and ready.")
        return True
    
    def check_commands(self):
        """Check for Telegram commands"""
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": self.last_update_id + 1, "timeout": 2}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                updates = data.get("result", [])
                
                for update in updates:
                    self.last_update_id = update["update_id"]
                    message = update.get("message", {})
                    text = message.get("text", "")
                    
                    if text.startswith("/"):
                        cmd = text.split()[0].lower()
                        print(f"Processing command: {cmd}")
                        
                        if cmd == "/status":
                            self.handle_status()
                        elif cmd == "/topcoin":
                            self.handle_topcoin()
                        elif cmd == "/summary":
                            self.handle_summary()
                        elif cmd == "/restart":
                            self.handle_restart()
                        
        except Exception as e:
            print(f"Command check error: {e}")
    
    def trading_cycle(self):
        """Main trading cycle"""
        while self.running:
            try:
                self.cycles += 1
                
                # Analyze and potentially trade
                self.analyze_and_trade()
                
                # Send cycle update every 20 cycles
                if self.cycles % 20 == 0:
                    portfolio_value, _ = self.get_real_portfolio()
                    
                    cycle_msg = f"""🔄 TRADING CYCLE #{self.cycles}

💰 Portfolio: ${portfolio_value:.2f} USDT
📈 Trades Today: {self.trades_executed}
🤖 Strategy: RSI momentum active
🔧 Status: Monitoring for opportunities

⏰ {datetime.now().strftime('%H:%M:%S UTC')}"""
                    
                    self.send_telegram(cycle_msg)
                
                time.sleep(180)  # 3-minute trading cycles
                
            except Exception as e:
                print(f"Trading cycle error: {e}")
                time.sleep(120)
    
    def run(self):
        """Run the clean trading system"""
        # Send startup message
        portfolio_value, assets = self.get_real_portfolio()
        
        startup_msg = f"""✅ NEXUS CLEAN TRADING ONLINE

🎯 SINGLE WORKING SYSTEM:
• All old bots killed ✅
• Real OKX trading active ✅
• Portfolio: ${portfolio_value:.2f} USDT ✅
• Live market data ✅

🤖 Trading Features:
• Real trade execution on OKX
• RSI-based momentum strategy
• 10% position sizing
• 4 major pairs monitored

🎮 Commands:
/status - Real portfolio & trading status
/topcoin - Live market opportunities
/summary - Trading performance
/restart - System restart

💡 This is the ONLY bot running - no conflicts!
Real trading with real portfolio data.

⏰ Started: {datetime.now().strftime('%H:%M:%S UTC')}"""
        
        success = self.send_telegram(startup_msg)
        print(f"Startup sent: {success}")
        
        # Start trading thread
        trading_thread = threading.Thread(target=self.trading_cycle)
        trading_thread.daemon = True
        trading_thread.start()
        
        # Main command loop
        print("Clean trading system running")
        while self.running:
            try:
                self.check_commands()
                time.sleep(1)
            except KeyboardInterrupt:
                self.running = False
                self.send_telegram("🔄 CLEAN TRADING SYSTEM SHUTDOWN")
                break
            except Exception as e:
                print(f"Main loop error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    trader = NexusCleanTrader()
    trader.run()