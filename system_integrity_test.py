#!/usr/bin/env python3
"""
NEXUS SYSTEM INTEGRITY VERIFICATION SCRIPT
Complete verification of all trading bot components
"""

import os
import json
import time
import traceback
from datetime import datetime

def log_test(test_name, status, details=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_icon = "✅" if status else "❌"
    print(f"{timestamp} {status_icon} {test_name}: {details}")
    return status

def test_api_connections():
    """Test all API connections"""
    try:
        import ccxt
        from openai import OpenAI
        
        # Test OKX API
        exchange = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'), 
            'password': os.getenv('OKX_PASSPHRASE'),
            'sandbox': False
        })
        
        balance = exchange.fetch_balance()
        log_test("OKX API Connection", True, f"Balance: ${balance.get('USDT', {}).get('total', 0):.2f}")
        
        # Test different account types
        results = {}
        for account_type in ['spot', 'margin', 'swap']:
            try:
                exchange.options['defaultType'] = account_type
                acc_balance = exchange.fetch_balance()
                usdt_bal = acc_balance.get('USDT', {}).get('free', 0)
                results[account_type] = usdt_bal
                log_test(f"OKX {account_type.title()} API", True, f"${usdt_bal:.2f}")
            except Exception as e:
                log_test(f"OKX {account_type.title()} API", False, str(e))
                results[account_type] = 0
        
        # Test OpenAI API
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Test connection. Respond with JSON: {\"status\": \"ok\", \"confidence\": 75}"}],
            max_tokens=50
        )
        content = response.choices[0].message.content.strip()
        test_data = json.loads(content)
        log_test("OpenAI API Connection", True, f"Response: {test_data}")
        
        return True, results
        
    except Exception as e:
        log_test("API Connection Test", False, str(e))
        return False, {}

def test_portfolio_calculation():
    """Test portfolio value calculation"""
    try:
        import ccxt
        
        exchange = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'sandbox': False
        })
        
        balance = exchange.fetch_balance()
        total_value = 0
        positions = []
        
        for currency, info in balance.items():
            if isinstance(info, dict) and info.get('total', 0) > 0:
                total = info['total']
                if currency == 'USDT':
                    total_value += total
                    positions.append(f'USDT: ${total:.2f}')
                else:
                    try:
                        ticker = exchange.fetch_ticker(f'{currency}/USDT')
                        value = total * ticker['last']
                        total_value += value
                        positions.append(f'{currency}: {total:.6f} = ${value:.2f}')
                    except:
                        positions.append(f'{currency}: {total:.6f} (price unavailable)')
        
        log_test("Portfolio Calculation", True, f"Total: ${total_value:.2f}")
        for pos in positions:
            print(f"   📊 {pos}")
        
        return True, total_value, positions
        
    except Exception as e:
        log_test("Portfolio Calculation", False, str(e))
        return False, 0, []

def test_auto_transfer_system():
    """Test auto-transfer functionality"""
    try:
        from auto_transfer_handler import AutoTransferHandler
        
        handler = AutoTransferHandler()
        status = handler.get_transfer_status()
        
        log_test("Auto-Transfer System", True, "Module loaded successfully")
        print(f"   💰 Spot: ${status['balances']['spot']:.2f}")
        print(f"   💰 Margin: ${status['balances']['margin']:.2f}")
        print(f"   💰 Futures: ${status['balances']['futures']:.2f}")
        print(f"   ✅ Futures Ready: {status['futures_ready']}")
        print(f"   ✅ Margin Ready: {status['margin_ready']}")
        
        return True, status
        
    except Exception as e:
        log_test("Auto-Transfer System", False, str(e))
        return False, {}

def test_ai_decision_parsing():
    """Test AI decision parsing with various scenarios"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Test AI decision making
        prompt = """
        Analyze BTC/USDT with RSI 35.0, price $118,000, 24h change -0.5%, volatility 0.8%.
        
        Respond with ONLY JSON:
        {
            "action": "spot_buy" | "margin_long" | "futures_long" | "margin_short" | "futures_short" | "hold",
            "leverage": 1-125,
            "confidence": 0-100,
            "reason": "brief explanation"
        }
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
            
        decision = json.loads(content)
        
        # Test parsing logic
        confidence = float(decision.get("confidence", 0))
        action = decision.get("action", "hold")
        leverage = int(decision.get("leverage", 1))
        reason = decision.get("reason", "AI decision")
        
        log_test("AI Decision Parsing", True, f"Action: {action}, Confidence: {confidence}%, Leverage: {leverage}x")
        print(f"   🤖 Reason: {reason}")
        
        return True, decision
        
    except Exception as e:
        log_test("AI Decision Parsing", False, str(e))
        return False, {}

def main():
    """Run complete system integrity verification"""
    print("🔍 NEXUS SYSTEM INTEGRITY VERIFICATION")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: API Connections
    print("\n📡 TESTING API CONNECTIONS...")
    api_status, api_data = test_api_connections()
    test_results['api_connections'] = api_status
    
    # Test 2: Portfolio Calculation
    print("\n💰 TESTING PORTFOLIO CALCULATION...")
    portfolio_status, total_value, positions = test_portfolio_calculation()
    test_results['portfolio_calculation'] = portfolio_status
    
    # Test 3: Auto-Transfer System
    print("\n🔄 TESTING AUTO-TRANSFER SYSTEM...")
    transfer_status, transfer_data = test_auto_transfer_system()
    test_results['auto_transfer'] = transfer_status
    
    # Test 4: AI Decision Parsing
    print("\n🤖 TESTING AI DECISION PARSING...")
    ai_status, ai_decision = test_ai_decision_parsing()
    test_results['ai_decision_parsing'] = ai_status
    
    # Final Report
    print("\n" + "=" * 60)
    print("📋 FINAL VERIFICATION REPORT")
    print("=" * 60)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, status in test_results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 OVERALL SCORE: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🏆 SYSTEM STATUS: ALL SYSTEMS OPERATIONAL")
        print("✅ Ready for live trading with full confidence")
    else:
        print("⚠️ SYSTEM STATUS: ISSUES DETECTED")
        print("❌ System requires fixes before full operation")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()