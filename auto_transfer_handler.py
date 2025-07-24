#!/usr/bin/env python3
"""
Smart Auto-Transfer Module for Nexus AI Bot
Automatically manages wallet transfers between Spot, Margin, and Futures accounts
with built-in safeguards and cooldown protection.
"""

import os
import ccxt
import time
import json
import logging
from datetime import datetime, timedelta

class AutoTransferHandler:
    def __init__(self):
        self.exchange = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'), 
            'password': os.getenv('OKX_PASSPHRASE'),
            'sandbox': False,
            'enableRateLimit': True
        })
        
        # Transfer limits and safeguards
        self.min_futures_balance = 10.0  # Minimum USDT in futures account
        self.min_margin_balance = 10.0   # Minimum USDT in margin account
        self.transfer_amount = 50.0      # Default transfer amount
        self.max_transfer_per_hour = 1   # Maximum transfers per hour
        self.min_spot_reserve = 20.0     # Always keep this much in spot
        
        # Transfer tracking
        self.last_transfer_time = {}
        self.transfer_log_file = '/opt/nexus-trading/transfer_log.json'
        
        logging.info("🔄 Auto-Transfer Handler initialized with safeguards")
    
    def load_transfer_history(self):
        """Load recent transfer history for cooldown tracking"""
        try:
            if os.path.exists(self.transfer_log_file):
                with open(self.transfer_log_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_transfer_record(self, transfer_type, amount, from_account, to_account):
        """Save transfer record for tracking"""
        try:
            history = self.load_transfer_history()
            record = {
                'timestamp': datetime.now().isoformat(),
                'type': transfer_type,
                'amount': amount,
                'from': from_account,
                'to': to_account,
                'status': 'completed'
            }
            history.append(record)
            
            # Keep only last 50 transfers
            if len(history) > 50:
                history = history[-50:]
            
            with open(self.transfer_log_file, 'w') as f:
                json.dump(history, f)
            
            logging.info(f"📝 Transfer recorded: ${amount:.2f} {from_account} → {to_account}")
        except Exception as e:
            logging.error(f"Transfer record save error: {e}")
    
    def can_transfer(self, account_type):
        """Check if transfer is allowed based on cooldown"""
        current_time = datetime.now()
        last_transfer = self.last_transfer_time.get(account_type)
        
        if not last_transfer:
            return True
            
        time_diff = current_time - last_transfer
        if time_diff.total_seconds() >= 3600:  # 1 hour cooldown
            return True
            
        remaining = 3600 - time_diff.total_seconds()
        logging.warning(f"⏰ Transfer cooldown: {remaining/60:.1f} minutes remaining for {account_type}")
        return False
    
    def get_wallet_balances(self):
        """Get balances from all wallet types"""
        try:
            balance = self.exchange.fetch_balance()
            
            # Extract balances by account type
            spot_usdt = 0
            margin_usdt = 0  
            futures_usdt = 0
            
            # Parse OKX balance structure
            for account_info in balance.get('info', {}).get('data', []):
                account_type = account_info.get('details', [{}])[0].get('ccy')
                if account_type == 'USDT':
                    cash_bal = float(account_info.get('details', [{}])[0].get('cashBal', 0))
                    if account_info.get('instType') == 'SPOT':
                        spot_usdt = cash_bal
                    elif account_info.get('instType') == 'MARGIN':
                        margin_usdt = cash_bal
                    elif account_info.get('instType') == 'SWAP':
                        futures_usdt = cash_bal
            
            return {
                'spot': spot_usdt,
                'margin': margin_usdt,
                'futures': futures_usdt,
                'total': spot_usdt + margin_usdt + futures_usdt
            }
            
        except Exception as e:
            logging.error(f"Balance check error: {e}")
            return {'spot': 0, 'margin': 0, 'futures': 0, 'total': 0}
    
    def execute_transfer(self, amount, from_account, to_account, currency='USDT'):
        """Execute wallet transfer with OKX API"""
        try:
            # OKX transfer API parameters
            transfer_params = {
                'ccy': currency,
                'amt': str(amount),
                'from': self._get_account_id(from_account),
                'to': self._get_account_id(to_account)
            }
            
            # Execute transfer
            result = self.exchange.transfer(currency, amount, from_account, to_account, transfer_params)
            
            if result and result.get('info', {}).get('code') == '0':
                logging.info(f"✅ Transfer completed: ${amount:.2f} {from_account} → {to_account}")
                self.last_transfer_time[to_account] = datetime.now()
                self.save_transfer_record('auto', amount, from_account, to_account)
                return True
            else:
                logging.error(f"❌ Transfer failed: {result}")
                return False
                
        except Exception as e:
            logging.error(f"Transfer execution error: {e}")
            return False
    
    def _get_account_id(self, account_name):
        """Convert account name to OKX account ID"""
        account_map = {
            'spot': '6',      # Trading account
            'margin': '5',    # Margin account  
            'futures': '18',  # Futures account
            'funding': '6'    # Funding account
        }
        return account_map.get(account_name.lower(), '6')
    
    def ensure_futures_balance(self, required_amount=None):
        """Ensure sufficient futures balance for trading"""
        if not self.can_transfer('futures'):
            return False
            
        balances = self.get_wallet_balances()
        futures_balance = balances['futures']
        needed_amount = required_amount or self.min_futures_balance
        
        if futures_balance >= needed_amount:
            logging.info(f"✅ Sufficient futures balance: ${futures_balance:.2f}")
            return True
        
        # Determine transfer amount
        transfer_needed = max(self.transfer_amount, needed_amount - futures_balance + 10)
        
        # Check if spot has enough (with reserve)
        spot_balance = balances['spot']
        if spot_balance < (transfer_needed + self.min_spot_reserve):
            logging.warning(f"⚠️ Insufficient spot balance for transfer: ${spot_balance:.2f}")
            return False
        
        # Execute transfer
        logging.info(f"🔄 Transferring ${transfer_needed:.2f} spot → futures")
        return self.execute_transfer(transfer_needed, 'spot', 'futures')
    
    def ensure_margin_balance(self, required_amount=None):
        """Ensure sufficient margin balance for trading"""
        if not self.can_transfer('margin'):
            return False
            
        balances = self.get_wallet_balances()
        margin_balance = balances['margin']
        needed_amount = required_amount or self.min_margin_balance
        
        if margin_balance >= needed_amount:
            logging.info(f"✅ Sufficient margin balance: ${margin_balance:.2f}")
            return True
        
        # Determine transfer amount
        transfer_needed = max(self.transfer_amount, needed_amount - margin_balance + 10)
        
        # Check if spot has enough (with reserve)
        spot_balance = balances['spot']
        if spot_balance < (transfer_needed + self.min_spot_reserve):
            logging.warning(f"⚠️ Insufficient spot balance for transfer: ${spot_balance:.2f}")
            return False
        
        # Execute transfer
        logging.info(f"🔄 Transferring ${transfer_needed:.2f} spot → margin")
        return self.execute_transfer(transfer_needed, 'spot', 'margin')
    
    def consolidate_to_spot(self, emergency=False):
        """Emergency consolidation: move all funds to spot for trading"""
        if not emergency and not self.can_transfer('consolidation'):
            return False
            
        balances = self.get_wallet_balances()
        total_transferred = 0
        
        # Transfer from futures to spot
        if balances['futures'] > 1:
            if self.execute_transfer(balances['futures'] - 0.5, 'futures', 'spot'):
                total_transferred += balances['futures'] - 0.5
        
        # Transfer from margin to spot  
        if balances['margin'] > 1:
            if self.execute_transfer(balances['margin'] - 0.5, 'margin', 'spot'):
                total_transferred += balances['margin'] - 0.5
        
        if total_transferred > 0:
            logging.info(f"🎯 Emergency consolidation: ${total_transferred:.2f} moved to spot")
            return True
        
        return False
    
    def smart_balance_optimization(self):
        """Intelligent balance distribution based on trading needs"""
        balances = self.get_wallet_balances()
        total_balance = balances['total']
        
        if total_balance < 50:
            logging.info("💰 Low balance - keeping all in spot")
            return
        
        # Optimal distribution percentages
        optimal_spot = total_balance * 0.60     # 60% in spot
        optimal_margin = total_balance * 0.25   # 25% in margin
        optimal_futures = total_balance * 0.15  # 15% in futures
        
        # Execute optimization transfers if needed
        current_time = datetime.now()
        if not hasattr(self, '_last_optimization') or \
           (current_time - self._last_optimization).total_seconds() > 7200:  # 2 hours
            
            logging.info("⚖️ Optimizing wallet distribution...")
            
            # Only transfer if significantly off-balance
            if abs(balances['futures'] - optimal_futures) > 20:
                if balances['futures'] < optimal_futures and balances['spot'] > optimal_spot:
                    transfer_amount = min(30, optimal_futures - balances['futures'])
                    self.execute_transfer(transfer_amount, 'spot', 'futures')
            
            self._last_optimization = current_time
    
    def get_transfer_status(self):
        """Get current transfer status and recommendations"""
        balances = self.get_wallet_balances()
        
        status = {
            'balances': balances,
            'futures_ready': balances['futures'] >= self.min_futures_balance,
            'margin_ready': balances['margin'] >= self.min_margin_balance,
            'transfer_cooldowns': {},
            'recommendations': []
        }
        
        # Check cooldowns
        current_time = datetime.now()
        for account in ['futures', 'margin']:
            last_transfer = self.last_transfer_time.get(account)
            if last_transfer:
                remaining = 3600 - (current_time - last_transfer).total_seconds()
                if remaining > 0:
                    status['transfer_cooldowns'][account] = remaining / 60  # minutes
        
        # Generate recommendations
        if not status['futures_ready'] and balances['spot'] > 50:
            status['recommendations'].append('Transfer funds to futures for leverage trading')
        
        if not status['margin_ready'] and balances['spot'] > 50:
            status['recommendations'].append('Transfer funds to margin for leveraged positions')
        
        return status

if __name__ == "__main__":
    # Test the auto-transfer functionality
    logging.basicConfig(level=logging.INFO)
    
    handler = AutoTransferHandler()
    status = handler.get_transfer_status()
    
    print("🔄 Auto-Transfer System Status:")
    print(f"💰 Balances: Spot ${status['balances']['spot']:.2f} | Margin ${status['balances']['margin']:.2f} | Futures ${status['balances']['futures']:.2f}")
    print(f"✅ Futures Ready: {status['futures_ready']}")
    print(f"✅ Margin Ready: {status['margin_ready']}")
    
    if status['recommendations']:
        print("💡 Recommendations:")
        for rec in status['recommendations']:
            print(f"   • {rec}")