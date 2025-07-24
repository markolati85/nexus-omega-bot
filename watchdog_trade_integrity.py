#!/usr/bin/env python3
"""
Nexus AI Trading Watchdog - Trade Integrity Module
Eliminates silent failures and ensures maximum leverage profitability
by validating all systems before every trade execution.
"""

import os
import ccxt
import time
import json
import logging
import requests
from datetime import datetime, timedelta
from openai import OpenAI

class TradeIntegrityWatchdog:
    def __init__(self):
        self.exchange = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'), 
            'password': os.getenv('OKX_PASSPHRASE'),
            'sandbox': False,
            'enableRateLimit': True
        })
        
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Validation thresholds
        self.min_futures_balance = 10.0
        self.min_margin_balance = 10.0
        self.min_confidence = 70.0
        self.api_timeout = 2.0
        self.trade_cooldown = 300  # 5 minutes between same symbol
        
        # Tracking
        self.last_trades = {}
        self.failed_trades = {}
        self.watchdog_log = '/opt/nexus-trading/watchdog_integrity.log'
        
        logging.info("🐕 Trade Integrity Watchdog initialized")
    
    def validate_api_endpoints(self):
        """Checkpoint 1: Validate all API endpoints are responding"""
        try:
            start_time = time.time()
            
            # Test OKX Spot API
            self.exchange.options['defaultType'] = 'spot'
            spot_balance = self.exchange.fetch_balance()
            spot_time = time.time() - start_time
            
            # Test OKX Margin API  
            self.exchange.options['defaultType'] = 'margin'
            margin_balance = self.exchange.fetch_balance()
            margin_time = time.time() - start_time
            
            # Test OKX Futures API
            self.exchange.options['defaultType'] = 'swap'
            futures_balance = self.exchange.fetch_balance()
            futures_time = time.time() - start_time
            
            # Test OpenAI API
            ai_start = time.time()
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "API test"}],
                max_tokens=10
            )
            ai_time = time.time() - ai_start
            
            # Validate response times
            if spot_time > self.api_timeout or margin_time > self.api_timeout or futures_time > self.api_timeout:
                self.log_failure("API_TIMEOUT", f"OKX API slow: Spot:{spot_time:.2f}s Margin:{margin_time:.2f}s Futures:{futures_time:.2f}s")
                return False
                
            if ai_time > self.api_timeout:
                self.log_failure("AI_TIMEOUT", f"OpenAI API slow: {ai_time:.2f}s")
                return False
            
            logging.info(f"✅ API Status: OKX({spot_time:.2f}s) AI({ai_time:.2f}s)")
            return True
            
        except Exception as e:
            self.log_failure("API_ERROR", f"API validation failed: {e}")
            return False
    
    def validate_wallet_state(self, trade_type, required_amount):
        """Checkpoint 2: Validate sufficient balance in appropriate account"""
        try:
            if trade_type == 'futures_long' or trade_type == 'futures_short':
                self.exchange.options['defaultType'] = 'swap'
                balance = self.exchange.fetch_balance()
                available = balance.get('USDT', {}).get('free', 0)
                
                if available < self.min_futures_balance:
                    self.log_failure("INSUFFICIENT_FUTURES", f"Futures balance ${available:.2f} < ${self.min_futures_balance}")
                    
                    # Attempt auto-transfer
                    if self.attempt_balance_fix('futures', required_amount):
                        # Re-check after transfer
                        balance = self.exchange.fetch_balance()
                        available = balance.get('USDT', {}).get('free', 0)
                        if available >= self.min_futures_balance:
                            logging.info(f"✅ Auto-transfer successful: Futures ${available:.2f}")
                            return True
                    
                    return False
                    
            elif trade_type == 'margin_long' or trade_type == 'margin_short':
                self.exchange.options['defaultType'] = 'margin'
                balance = self.exchange.fetch_balance()
                available = balance.get('USDT', {}).get('free', 0)
                
                if available < self.min_margin_balance:
                    self.log_failure("INSUFFICIENT_MARGIN", f"Margin balance ${available:.2f} < ${self.min_margin_balance}")
                    
                    # Attempt auto-transfer
                    if self.attempt_balance_fix('margin', required_amount):
                        # Re-check after transfer
                        balance = self.exchange.fetch_balance()
                        available = balance.get('USDT', {}).get('free', 0)
                        if available >= self.min_margin_balance:
                            logging.info(f"✅ Auto-transfer successful: Margin ${available:.2f}")
                            return True
                    
                    return False
            
            logging.info(f"✅ Wallet State: {trade_type} balance sufficient")
            return True
            
        except Exception as e:
            self.log_failure("WALLET_ERROR", f"Wallet validation failed: {e}")
            return False
    
    def validate_ai_decision(self, decision):
        """Checkpoint 3: Validate AI decision structure and quality"""
        try:
            # Check required keys
            required_keys = ['action', 'confidence', 'leverage', 'reason']
            for key in required_keys:
                if key not in decision:
                    self.log_failure("AI_MISSING_KEY", f"AI decision missing '{key}' field")
                    return False
            
            # Validate confidence
            confidence = decision.get('confidence', 0)
            if confidence < self.min_confidence:
                self.log_failure("AI_LOW_CONFIDENCE", f"AI confidence {confidence}% < {self.min_confidence}%")
                return False
            
            # Validate leverage
            leverage = decision.get('leverage', 1)
            if leverage < 1 or leverage > 125:
                self.log_failure("AI_INVALID_LEVERAGE", f"AI leverage {leverage}x outside 1-125x range")
                return False
            
            # Validate action
            valid_actions = ['spot_buy', 'margin_long', 'margin_short', 'futures_long', 'futures_short']
            if decision.get('action') not in valid_actions:
                self.log_failure("AI_INVALID_ACTION", f"AI action '{decision.get('action')}' not in valid list")
                return False
            
            logging.info(f"✅ AI Decision: {decision['action']} {leverage}x @ {confidence}% confidence")
            return True
            
        except Exception as e:
            self.log_failure("AI_VALIDATION_ERROR", f"AI decision validation failed: {e}")
            return False
    
    def validate_strategy_indicators(self, market_data):
        """Checkpoint 4: Validate technical indicators are valid"""
        try:
            required_indicators = ['rsi', 'price', 'change_24h']
            
            for indicator in required_indicators:
                if indicator not in market_data or market_data[indicator] is None:
                    self.log_failure("INDICATOR_MISSING", f"Missing or invalid indicator: {indicator}")
                    return False
            
            # Validate RSI range
            rsi = market_data['rsi']
            if rsi < 0 or rsi > 100:
                self.log_failure("INVALID_RSI", f"RSI {rsi} outside 0-100 range")
                return False
            
            logging.info(f"✅ Indicators: RSI:{rsi:.1f} Price:${market_data['price']:.2f}")
            return True
            
        except Exception as e:
            self.log_failure("INDICATOR_ERROR", f"Indicator validation failed: {e}")
            return False
    
    def validate_trade_cooldown(self, symbol):
        """Checkpoint 5: Prevent rapid repeat trades on same symbol"""
        try:
            current_time = datetime.now()
            
            if symbol in self.last_trades:
                last_trade_time = self.last_trades[symbol]
                time_diff = (current_time - last_trade_time).total_seconds()
                
                if time_diff < self.trade_cooldown:
                    remaining = self.trade_cooldown - time_diff
                    self.log_failure("TRADE_COOLDOWN", f"{symbol} on cooldown: {remaining:.0f}s remaining")
                    return False
            
            logging.info(f"✅ Cooldown: {symbol} ready for trading")
            return True
            
        except Exception as e:
            self.log_failure("COOLDOWN_ERROR", f"Cooldown validation failed: {e}")
            return False
    
    def attempt_balance_fix(self, account_type, required_amount):
        """Attempt to fix insufficient balance through auto-transfer"""
        try:
            logging.info(f"🔧 Attempting balance fix for {account_type}")
            
            # Check spot balance for transfer
            self.exchange.options['defaultType'] = 'spot'
            spot_balance = self.exchange.fetch_balance()
            spot_usdt = spot_balance.get('USDT', {}).get('free', 0)
            
            if spot_usdt < (required_amount + 10):  # Need extra buffer
                logging.warning(f"⚠️ Insufficient spot balance for transfer: ${spot_usdt:.2f}")
                return False
            
            # Execute transfer
            transfer_amount = min(50, max(20, required_amount * 1.2))
            
            if account_type == 'futures':
                to_account = '18'  # Futures
            elif account_type == 'margin':
                to_account = '5'   # Margin
            else:
                return False
            
            transfer_response = self.exchange.private_post_asset_transfer({
                'ccy': 'USDT',
                'amt': str(transfer_amount),
                'from': '6',        # Spot
                'to': to_account
            })
            
            if transfer_response.get('code') == '0':
                logging.info(f"✅ Emergency transfer: ${transfer_amount:.2f} to {account_type}")
                time.sleep(3)  # Wait for settlement
                return True
            else:
                logging.error(f"❌ Transfer failed: {transfer_response}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Balance fix error: {e}")
            return False
    
    def log_failure(self, failure_type, message):
        """Log validation failures for analysis"""
        timestamp = datetime.now().isoformat()
        failure_record = {
            'timestamp': timestamp,
            'type': failure_type,
            'message': message
        }
        
        # Track failed trades
        if failure_type not in self.failed_trades:
            self.failed_trades[failure_type] = 0
        self.failed_trades[failure_type] += 1
        
        # Log to file
        try:
            with open(self.watchdog_log, 'a') as f:
                f.write(f"{json.dumps(failure_record)}\n")
        except:
            pass
        
        logging.warning(f"🚨 WATCHDOG BLOCK: {failure_type} - {message}")
    
    def pre_trade_validation(self, symbol, trade_type, decision, market_data, required_amount):
        """Complete pre-trade validation - ALL checkpoints must pass"""
        logging.info(f"🐕 WATCHDOG: Validating {trade_type} {symbol}")
        
        validation_start = time.time()
        
        # Checkpoint 1: API Status
        if not self.validate_api_endpoints():
            return False, "API endpoints failed validation"
        
        # Checkpoint 2: Wallet State
        if not self.validate_wallet_state(trade_type, required_amount):
            return False, "Insufficient wallet balance"
        
        # Checkpoint 3: AI Decision Quality
        if not self.validate_ai_decision(decision):
            return False, "AI decision failed validation"
        
        # Checkpoint 4: Technical Indicators
        if not self.validate_strategy_indicators(market_data):
            return False, "Technical indicators invalid"
        
        # Checkpoint 5: Trade Cooldown
        if not self.validate_trade_cooldown(symbol):
            return False, "Symbol on trading cooldown"
        
        validation_time = time.time() - validation_start
        
        # Record successful validation
        self.last_trades[symbol] = datetime.now()
        
        logging.info(f"✅ WATCHDOG APPROVED: {trade_type} {symbol} ({validation_time:.2f}s)")
        return True, "All validations passed"
    
    def get_watchdog_stats(self):
        """Return watchdog performance statistics"""
        return {
            'total_failures': sum(self.failed_trades.values()),
            'failure_breakdown': self.failed_trades,
            'symbols_tracked': len(self.last_trades),
            'watchdog_uptime': datetime.now().isoformat()
        }

# Global watchdog instance
trade_watchdog = TradeIntegrityWatchdog()