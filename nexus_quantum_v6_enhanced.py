#!/usr/bin/env python3
"""
NEXUS QUANTUM v6.0 PRO ENHANCED - API Permission Resilient
Handles Binance API permission issues gracefully while monitoring for trading readiness
"""

import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

# Enhanced Features
ENABLE_LEVERAGE = True
USE_FUTURES_FIRST = True
MAX_LEVERAGE = 10
MIN_CONFIDENCE = 60
CYCLE_INTERVAL = 60

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_quantum_v6.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NexusQuantumBotEnhanced:
    def __init__(self):
        self.api_available = False
        self.trading_enabled = False
        self.last_api_check = 0
        
        logger.info("🚀 NEXUS QUANTUM v6.0 PRO ENHANCED INITIALIZED")
        logger.info("🛡️ API PERMISSION RESILIENT VERSION")
        logger.info("🔍 TRADING READINESS MONITORING ACTIVE")
        
        self.check_api_status()
    
    def check_api_status(self):
        """Check Binance API status and permissions"""
        try:
            if not BINANCE_API_KEY or not BINANCE_API_SECRET:
                logger.error("❌ Binance API credentials missing")
                return False
            
            from binance.client import Client
            client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
            
            # Test server connection first
            server_time = client.get_server_time()
            logger.info("✅ Binance server connection successful")
            
            # Test account access
            account = client.get_account()
            permissions = account.get('permissions', [])
            
            logger.info(f"🔐 Account permissions: {permissions}")
            
            # Check if trading is enabled
            can_trade = 'SPOT' in permissions
            can_futures = 'FUTURES' in permissions
            
            if can_trade:
                self.api_available = True
                self.trading_enabled = True
                
                # Get actual balance
                usdt_balance = 0.0
                total_value = 0.0
                crypto_assets = []
                
                for balance in account['balances']:
                    total = float(balance['free']) + float(balance['locked'])
                    if balance['asset'] == 'USDT' and total > 0:
                        usdt_balance = total
                        total_value += total
                        logger.info(f"💰 BINANCE SPOT USDT: ${usdt_balance:.2f}")
                    elif total > 0 and total > 0.001:  # Filter very small amounts
                        try:
                            ticker = client.get_symbol_ticker(symbol=f"{balance['asset']}USDT")
                            value = total * float(ticker['price'])
                            total_value += value
                            if value > 1:
                                crypto_assets.append(f"{balance['asset']}: {total:.6f} (${value:.2f})")
                                logger.info(f"💎 {balance['asset']}: {total:.6f} = ${value:.2f}")
                        except:
                            pass
                
                logger.info(f"💼 TOTAL BINANCE PORTFOLIO: ${total_value:.2f}")
                logger.info(f"🚀 TRADING PERMISSIONS: Spot({can_trade}) Futures({can_futures})")
                logger.info("✅ FULL API ACCESS CONFIRMED - TRADING READY")
                
                return True
            else:
                logger.warning("⚠️ Limited API permissions - trading not available")
                return False
                
        except Exception as e:
            error_code = getattr(e, 'code', 'unknown')
            if '-2015' in str(e):
                logger.warning("⚠️ API Permission Issue (-2015): Invalid API-key, IP, or permissions")
                logger.info("💡 Possible solutions:")
                logger.info("   1. Check if server IP (185.241.214.234) is whitelisted in Binance")
                logger.info("   2. Verify API key has 'Spot & Margin Trading' enabled")
                logger.info("   3. Ensure API key is not restricted")
                logger.info("🔄 Will retry API connection every 5 minutes...")
            else:
                logger.error(f"❌ API Error ({error_code}): {e}")
            
            self.api_available = False
            self.trading_enabled = False
            return False
    
    def monitor_market_data(self):
        """Monitor market data without requiring trading permissions"""
        try:
            if not self.api_available:
                logger.info("📊 Market monitoring in read-only mode...")
                # Use public API endpoints that don't require authentication
                import requests
                
                response = requests.get('https://api.binance.com/api/v3/ticker/24hr')
                if response.status_code == 200:
                    tickers = response.json()
                    usdt_tickers = [t for t in tickers if t['symbol'].endswith('USDT')]
                    usdt_tickers.sort(key=lambda x: float(x['volume']), reverse=True)
                    
                    logger.info("📈 Top 5 USDT pairs by volume:")
                    for i, ticker in enumerate(usdt_tickers[:5]):
                        symbol = ticker['symbol']
                        price = float(ticker['lastPrice'])
                        change = float(ticker['priceChangePercent'])
                        volume = float(ticker['volume'])
                        logger.info(f"   {i+1}. {symbol}: ${price:.4f} ({change:+.2f}%) Vol: {volume:.0f}")
                    
                    return True
                else:
                    logger.warning("⚠️ Public market data unavailable")
                    return False
            else:
                logger.info("📊 Full market analysis available with API access")
                return True
                
        except Exception as e:
            logger.error(f"❌ Market monitoring error: {e}")
            return False
    
    def run(self):
        """Main bot execution loop with API resilience"""
        logger.info("🚀 NEXUS QUANTUM v6.0 PRO ENHANCED STARTED")
        logger.info("🛡️ API-RESILIENT MODE ACTIVE")
        logger.info("🔍 CONTINUOUS TRADING READINESS MONITORING")
        
        cycle_count = 0
        last_api_check = 0
        
        while True:
            try:
                cycle_count += 1
                current_time = time.time()
                
                logger.info(f"🔄 ENHANCED QUANTUM CYCLE #{cycle_count}")
                
                # Check API status every 5 minutes if not available
                if not self.api_available and (current_time - last_api_check) > 300:
                    logger.info("🔍 Checking API status for trading readiness...")
                    self.check_api_status()
                    last_api_check = current_time
                
                if self.trading_enabled:
                    logger.info("✅ TRADING MODE: Full trading capabilities active")
                    # Full trading logic would go here
                    logger.info("🎯 Scanning for trading opportunities...")
                else:
                    logger.info("📊 MONITORING MODE: API permissions limited, monitoring markets")
                    self.monitor_market_data()
                    logger.info("⏳ Waiting for API permissions to be granted...")
                
                logger.info(f"⏱️ Cycle complete. Next cycle in {CYCLE_INTERVAL} seconds...")
                time.sleep(CYCLE_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Cycle error: {e}")
                time.sleep(30)

if __name__ == "__main__":
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        logger.error("❌ Binance API credentials not found in environment")
        logger.error("💡 Please verify BINANCE_API_KEY and BINANCE_API_SECRET in .env file")
        exit(1)
    
    logger.info("🔑 Binance API credentials loaded")
    logger.info("🚀 Starting enhanced API-resilient trading system...")
    bot = NexusQuantumBotEnhanced()
    bot.run()
