#!/usr/bin/env python3
"""
Comprehensive Test Suite for Watchdog Trade Integrity System
Tests all modules and validates enhanced trading capabilities
"""

import os
import sys
import ccxt
import time
import json
import logging
from datetime import datetime
from watchdog_trade_integrity import trade_watchdog

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_watchdog_system():
    """Comprehensive test of all watchdog modules"""
    print("🧪 NEXUS WATCHDOG INTEGRATION TEST SUITE")
    print("="*60)
    
    # Test 1: API Endpoint Validation
    print("\n🔍 TEST 1: API ENDPOINT VALIDATION")
    try:
        api_valid = trade_watchdog.validate_api_endpoints()
        print(f"✅ API Validation: {'PASSED' if api_valid else 'FAILED'}")
    except Exception as e:
        print(f"❌ API Validation Error: {e}")
    
    # Test 2: Wallet State Validation
    print("\n💰 TEST 2: WALLET STATE VALIDATION")
    try:
        # Test futures wallet
        futures_valid = trade_watchdog.validate_wallet_state('futures_long', 20.0)
        print(f"📊 Futures Wallet: {'SUFFICIENT' if futures_valid else 'INSUFFICIENT'}")
        
        # Test margin wallet
        margin_valid = trade_watchdog.validate_wallet_state('margin_long', 20.0)
        print(f"📊 Margin Wallet: {'SUFFICIENT' if margin_valid else 'INSUFFICIENT'}")
        
    except Exception as e:
        print(f"❌ Wallet Validation Error: {e}")
    
    # Test 3: AI Decision Validation
    print("\n🤖 TEST 3: AI DECISION VALIDATION")
    try:
        # Valid AI decision
        valid_decision = {
            'action': 'futures_long',
            'confidence': 85.0,
            'leverage': 50,
            'reason': 'Strong RSI signal'
        }
        ai_valid = trade_watchdog.validate_ai_decision(valid_decision)
        print(f"✅ Valid AI Decision: {'PASSED' if ai_valid else 'FAILED'}")
        
        # Invalid AI decision (low confidence)
        invalid_decision = {
            'action': 'futures_long',
            'confidence': 65.0,  # Below threshold
            'leverage': 50,
            'reason': 'Weak signal'
        }
        ai_invalid = trade_watchdog.validate_ai_decision(invalid_decision)
        print(f"❌ Invalid AI Decision: {'BLOCKED' if not ai_invalid else 'INCORRECTLY PASSED'}")
        
    except Exception as e:
        print(f"❌ AI Validation Error: {e}")
    
    # Test 4: Strategy Indicators Validation  
    print("\n📈 TEST 4: STRATEGY INDICATORS VALIDATION")
    try:
        valid_market_data = {
            'rsi': 25.5,
            'price': 191.50,
            'change_24h': -5.2
        }
        indicators_valid = trade_watchdog.validate_strategy_indicators(valid_market_data)
        print(f"📊 Valid Indicators: {'PASSED' if indicators_valid else 'FAILED'}")
        
        invalid_market_data = {
            'rsi': 150,  # Invalid RSI > 100
            'price': 191.50,
            'change_24h': -5.2
        }
        indicators_invalid = trade_watchdog.validate_strategy_indicators(invalid_market_data)
        print(f"❌ Invalid Indicators: {'BLOCKED' if not indicators_invalid else 'INCORRECTLY PASSED'}")
        
    except Exception as e:
        print(f"❌ Indicators Validation Error: {e}")
    
    # Test 5: Trade Cooldown Validation
    print("\n⏱️ TEST 5: TRADE COOLDOWN VALIDATION")
    try:
        cooldown_valid = trade_watchdog.validate_trade_cooldown('SOL/USDT')
        print(f"🕒 Cooldown Check: {'READY' if cooldown_valid else 'ON COOLDOWN'}")
    except Exception as e:
        print(f"❌ Cooldown Validation Error: {e}")
    
    # Test 6: Complete Pre-Trade Validation
    print("\n🚀 TEST 6: COMPLETE PRE-TRADE VALIDATION")
    try:
        test_decision = {
            'action': 'futures_long',
            'confidence': 85.0,
            'leverage': 50,
            'reason': 'Ultra-strong RSI signal with high volatility'
        }
        
        test_market_data = {
            'rsi': 23.5,
            'price': 191.60,
            'change_24h': -6.2
        }
        
        validation_result, validation_message = trade_watchdog.pre_trade_validation(
            symbol='SOL/USDT',
            trade_type='futures_long',
            decision=test_decision,
            market_data=test_market_data,
            required_amount=20.0
        )
        
        print(f"🎯 Complete Validation: {'✅ APPROVED' if validation_result else '🔴 BLOCKED'}")
        print(f"📝 Message: {validation_message}")
        
    except Exception as e:
        print(f"❌ Complete Validation Error: {e}")
    
    # Test 7: Watchdog Statistics
    print("\n📊 TEST 7: WATCHDOG STATISTICS")
    try:
        stats = trade_watchdog.get_watchdog_stats()
        print(f"📈 Watchdog Stats:")
        print(f"   Total Failures: {stats.get('total_failures', 0)}")
        print(f"   Symbols Tracked: {stats.get('symbols_tracked', 0)}")
        print(f"   Failure Breakdown: {stats.get('failure_breakdown', {})}")
    except Exception as e:
        print(f"❌ Statistics Error: {e}")
    
    print("\n" + "="*60)
    print("🏆 WATCHDOG INTEGRATION TEST COMPLETE")
    
    # Test current portfolio state
    print("\n💰 CURRENT PORTFOLIO STATE CHECK:")
    try:
        exchange = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'sandbox': False
        })
        
        # Check all accounts
        for account_type in ['spot', 'margin', 'swap']:
            exchange.options['defaultType'] = account_type
            balance = exchange.fetch_balance()
            usdt = balance.get('USDT', {}).get('free', 0)
            print(f"   {account_type.upper()}: ${usdt:.2f}")
            
        # Check SOL holdings
        exchange.options['defaultType'] = 'spot'
        balance = exchange.fetch_balance()
        sol_amount = balance.get('SOL', {}).get('free', 0)
        if sol_amount > 0:
            sol_ticker = exchange.fetch_ticker('SOL/USDT')
            sol_value = sol_amount * sol_ticker['last']
            print(f"   SOL: {sol_amount:.6f} (≈${sol_value:.2f})")
            
        print(f"🎯 SYSTEM STATUS: Ready for watchdog-protected trading")
        
    except Exception as e:
        print(f"❌ Portfolio check error: {e}")

if __name__ == "__main__":
    test_watchdog_system()