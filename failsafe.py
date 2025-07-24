#!/usr/bin/env python3
"""
Failsafe System - Risk management and emergency protection
Auto-disables trading during excessive losses or dangerous conditions
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

class FailsafeSystem:
    def __init__(self, config_file: str = 'failsafe_config.json'):
        """Initialize failsafe system with risk parameters"""
        
        self.config_file = config_file
        self.is_active = True
        self.trading_disabled = False
        self.emergency_mode = False
        
        # Default risk parameters
        self.default_config = {
            'max_daily_loss_pct': 4.5,
            'max_trade_loss_pct': 1.2,
            'max_consecutive_losses': 5,
            'cooldown_hours': 12,
            'emergency_stop_loss_pct': 8.0,
            'max_drawdown_pct': 10.0,
            'min_account_balance': 10.0
        }
        
        # Load or create config
        self.config = self._load_config()
        
        # Tracking variables
        self.daily_pnl = 0.0
        self.trade_history = []
        self.daily_start_balance = 0.0
        self.last_reset_date = datetime.now().date()
        self.disable_timestamp = None
        self.consecutive_losses = 0
        
        logging.info("🛡️ Failsafe System initialized")
        logging.info(f"📊 Max daily loss: {self.config['max_daily_loss_pct']}%")
        logging.info(f"🔴 Max trade loss: {self.config['max_trade_loss_pct']}%")
    
    def check_trade_approval(self, trade_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Check if trade is approved by failsafe system
        
        Args:
            trade_data (dict): Proposed trade information
            
        Returns:
            dict: Approval status with reasons
        """
        
        if not self.is_active:
            return {"approved": True, "reason": "Failsafe system disabled"}
        
        # Check if trading is currently disabled
        if self.trading_disabled:
            remaining_cooldown = self._get_remaining_cooldown()
            if remaining_cooldown > 0:
                return {
                    "approved": False,
                    "reason": f"Trading disabled - {remaining_cooldown:.1f} hours remaining in cooldown"
                }
            else:
                # Cooldown expired, re-enable trading
                self._reset_failsafe()
        
        # Check emergency mode
        if self.emergency_mode:
            return {
                "approved": False,
                "reason": "Emergency mode active - manual reset required"
            }
        
        # Daily reset check
        self._check_daily_reset()
        
        # Risk checks
        risk_checks = [
            self._check_daily_loss_limit(),
            self._check_consecutive_losses(),
            self._check_position_size(trade_data),
            self._check_account_balance(trade_data)
        ]
        
        for check in risk_checks:
            if not check["passed"]:
                return {
                    "approved": False,
                    "reason": check["reason"]
                }
        
        return {"approved": True, "reason": "All risk checks passed"}
    
    def record_trade_result(self, trade_result: Dict[str, Any]) -> None:
        """
        Record trade result for failsafe monitoring
        
        Args:
            trade_result (dict): Trade execution result with PnL
        """
        
        try:
            pnl = trade_result.get('pnl', 0)
            trade_value = trade_result.get('trade_value', 0)
            
            # Calculate trade performance
            pnl_pct = (pnl / trade_value * 100) if trade_value > 0 else 0
            
            # Record trade
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'pair': trade_result.get('pair', 'Unknown'),
                'side': trade_result.get('side', 'Unknown'),
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'trade_value': trade_value
            }
            
            self.trade_history.append(trade_record)
            self.daily_pnl += pnl
            
            # Check for consecutive losses
            if pnl < 0:
                self.consecutive_losses += 1
                logging.warning(f"⚠️ Consecutive loss #{self.consecutive_losses}: {pnl_pct:.2f}%")
            else:
                self.consecutive_losses = 0
            
            # Check if trade triggered any limits
            self._check_trade_limits(trade_record)
            
            # Log trade
            logging.info(f"📊 Trade recorded: {pnl:+.2f} USDT ({pnl_pct:+.2f}%)")
            logging.info(f"📈 Daily PnL: {self.daily_pnl:+.2f} USDT")
            
        except Exception as e:
            logging.error(f"Error recording trade result: {e}")
    
    def get_risk_status(self) -> Dict[str, Any]:
        """Get comprehensive risk status"""
        
        daily_loss_pct = self._calculate_daily_loss_percentage()
        remaining_cooldown = self._get_remaining_cooldown()
        
        return {
            'failsafe_active': self.is_active,
            'trading_enabled': not self.trading_disabled,
            'emergency_mode': self.emergency_mode,
            'daily_pnl': self.daily_pnl,
            'daily_loss_pct': daily_loss_pct,
            'consecutive_losses': self.consecutive_losses,
            'remaining_cooldown_hours': remaining_cooldown,
            'risk_limits': {
                'max_daily_loss': self.config['max_daily_loss_pct'],
                'max_trade_loss': self.config['max_trade_loss_pct'],
                'max_consecutive_losses': self.config['max_consecutive_losses']
            },
            'last_reset': self.last_reset_date.isoformat()
        }
    
    def manual_reset(self) -> Dict[str, Any]:
        """Manual reset of failsafe system"""
        
        logging.info("🔄 Manual failsafe reset initiated")
        
        self.trading_disabled = False
        self.emergency_mode = False
        self.disable_timestamp = None
        self.consecutive_losses = 0
        
        # Reset daily tracking
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
        
        logging.info("✅ Failsafe system reset - trading re-enabled")
        
        return {
            "success": True,
            "message": "Failsafe system reset successfully",
            "trading_enabled": True
        }
    
    def emergency_stop(self, reason: str = "Manual emergency stop") -> Dict[str, Any]:
        """Emergency stop all trading"""
        
        logging.critical(f"🚨 EMERGENCY STOP ACTIVATED: {reason}")
        
        self.emergency_mode = True
        self.trading_disabled = True
        self.disable_timestamp = datetime.now()
        
        return {
            "success": True,
            "message": f"Emergency stop activated: {reason}",
            "requires_manual_reset": True
        }
    
    def _check_daily_loss_limit(self) -> Dict[str, Any]:
        """Check if daily loss limit is exceeded"""
        
        daily_loss_pct = self._calculate_daily_loss_percentage()
        max_allowed = self.config['max_daily_loss_pct']
        
        if daily_loss_pct >= max_allowed:
            self._trigger_failsafe(f"Daily loss limit exceeded: {daily_loss_pct:.2f}% >= {max_allowed}%")
            return {
                "passed": False,
                "reason": f"Daily loss limit exceeded: {daily_loss_pct:.2f}%"
            }
        
        return {"passed": True, "reason": "Daily loss within limits"}
    
    def _check_consecutive_losses(self) -> Dict[str, Any]:
        """Check consecutive losses limit"""
        
        max_allowed = self.config['max_consecutive_losses']
        
        if self.consecutive_losses >= max_allowed:
            self._trigger_failsafe(f"Consecutive losses limit exceeded: {self.consecutive_losses} >= {max_allowed}")
            return {
                "passed": False,
                "reason": f"Too many consecutive losses: {self.consecutive_losses}"
            }
        
        return {"passed": True, "reason": "Consecutive losses within limits"}
    
    def _check_position_size(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if position size is within risk limits"""
        
        position_value = trade_data.get('position_value', 0)
        account_balance = trade_data.get('account_balance', 0)
        
        if account_balance > 0:
            position_pct = (position_value / account_balance) * 100
            max_position_pct = 25.0  # Max 25% of account per trade
            
            if position_pct > max_position_pct:
                return {
                    "passed": False,
                    "reason": f"Position too large: {position_pct:.1f}% > {max_position_pct}%"
                }
        
        return {"passed": True, "reason": "Position size acceptable"}
    
    def _check_account_balance(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if account balance is above minimum"""
        
        account_balance = trade_data.get('account_balance', 0)
        min_balance = self.config['min_account_balance']
        
        if account_balance < min_balance:
            return {
                "passed": False,
                "reason": f"Account balance too low: ${account_balance:.2f} < ${min_balance:.2f}"
            }
        
        return {"passed": True, "reason": "Account balance sufficient"}
    
    def _check_trade_limits(self, trade_record: Dict[str, Any]) -> None:
        """Check if individual trade exceeded limits"""
        
        pnl_pct = abs(trade_record.get('pnl_pct', 0))
        max_trade_loss = self.config['max_trade_loss_pct']
        
        if pnl_pct >= max_trade_loss and trade_record.get('pnl', 0) < 0:
            self._trigger_failsafe(f"Single trade loss exceeded limit: {pnl_pct:.2f}% >= {max_trade_loss}%")
    
    def _calculate_daily_loss_percentage(self) -> float:
        """Calculate daily loss percentage"""
        
        if self.daily_start_balance <= 0:
            return 0.0
        
        daily_loss_pct = abs(min(0, self.daily_pnl) / self.daily_start_balance) * 100
        return daily_loss_pct
    
    def _check_daily_reset(self) -> None:
        """Check if daily reset is needed"""
        
        current_date = datetime.now().date()
        
        if current_date > self.last_reset_date:
            logging.info("📅 Daily reset - resetting counters")
            self.daily_pnl = 0.0
            self.consecutive_losses = 0
            self.last_reset_date = current_date
            # Note: daily_start_balance should be updated by main bot
    
    def _trigger_failsafe(self, reason: str) -> None:
        """Trigger failsafe protection"""
        
        if self.trading_disabled:
            return  # Already disabled
        
        logging.critical(f"🚨 FAILSAFE TRIGGERED: {reason}")
        
        self.trading_disabled = True
        self.disable_timestamp = datetime.now()
        
        # Save state
        self._save_state()
    
    def _get_remaining_cooldown(self) -> float:
        """Get remaining cooldown hours"""
        
        if not self.disable_timestamp:
            return 0.0
        
        elapsed = datetime.now() - self.disable_timestamp
        cooldown_hours = self.config['cooldown_hours']
        remaining = cooldown_hours - (elapsed.total_seconds() / 3600)
        
        return max(0.0, remaining)
    
    def _reset_failsafe(self) -> None:
        """Reset failsafe after cooldown"""
        
        logging.info("✅ Failsafe cooldown expired - re-enabling trading")
        
        self.trading_disabled = False
        self.disable_timestamp = None
        self.consecutive_losses = 0
    
    def _load_config(self) -> Dict[str, Any]:
        """Load failsafe configuration"""
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            logging.info(f"Loaded failsafe config from {self.config_file}")
            return {**self.default_config, **config}
        except FileNotFoundError:
            logging.info("Creating default failsafe config")
            self._save_config(self.default_config)
            return self.default_config.copy()
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return self.default_config.copy()
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save failsafe configuration"""
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    def _save_state(self) -> None:
        """Save current failsafe state"""
        
        state = {
            'trading_disabled': self.trading_disabled,
            'emergency_mode': self.emergency_mode,
            'daily_pnl': self.daily_pnl,
            'consecutive_losses': self.consecutive_losses,
            'disable_timestamp': self.disable_timestamp.isoformat() if self.disable_timestamp else None,
            'last_reset_date': self.last_reset_date.isoformat()
        }
        
        try:
            with open('failsafe_state.json', 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving failsafe state: {e}")
    
    def set_daily_start_balance(self, balance: float) -> None:
        """Set daily starting balance for loss percentage calculations"""
        self.daily_start_balance = balance
        logging.info(f"Daily start balance set: ${balance:.2f}")
    
    def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update failsafe configuration"""
        
        self.config.update(new_config)
        self._save_config(self.config)
        
        logging.info("Failsafe configuration updated")
        
        return {"success": True, "config": self.config}