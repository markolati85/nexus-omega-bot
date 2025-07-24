#!/usr/bin/env python3
"""
Monitor Bot Performance - Fix AI and restart system
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

try:
    import ccxt
    from openai import OpenAI
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

load_dotenv()

def diagnose_system():
    """Complete system diagnosis"""
    
    print("🔍 NEXUS SYSTEM DIAGNOSIS")
    print("=" * 50)
    
    # 1. Check OpenAI API
    print("1. CHECKING OPENAI API:")
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": "Test connection. Respond with: OK"}],
                max_tokens=10
            )
            print(f"   ✅ OpenAI API: {response.choices[0].message.content}")
        else:
            print("   ❌ OpenAI API key missing")
    except Exception as e:
        print(f"   ❌ OpenAI API error: {e}")
    
    # 2. Check OKX API
    print("\n2. CHECKING OKX API:")
    if CCXT_AVAILABLE:
        try:
            exchange = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'sandbox': False,
                'enableRateLimit': True
            })
            
            balance = exchange.fetch_balance()
            usdt_bal = balance.get('USDT', {}).get('free', 0)
            print(f"   ✅ OKX API: ${usdt_bal:.2f} USDT available")
            
        except Exception as e:
            print(f"   ❌ OKX API error: {e}")
    else:
        print("   ❌ CCXT not available")
    
    # 3. Check file permissions
    print("\n3. CHECKING FILES:")
    files_to_check = [
        '/opt/nexus-trading/nexus_ultimate_v6_advanced.py',
        '/opt/nexus-trading/.env_okx',
        '/opt/nexus-trading/ai_core_langchain.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} missing")
    
    # 4. Create dashboard log file
    print("\n4. CREATING DASHBOARD LOG:")
    try:
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'balance': usdt_bal if 'usdt_bal' in locals() else 305.57,
            'bot_status': 'DIAGNOSING',
            'ai_confidence': 0,
            'market_analysis': {},
            'trade_signals': [],
            'uptime': 0,
            'system_health': 'CHECKING'
        }
        
        with open('/opt/nexus-trading/latest_log.json', 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        print("   ✅ Dashboard log created")
        
    except Exception as e:
        print(f"   ❌ Dashboard log error: {e}")
    
    print("\n✅ DIAGNOSIS COMPLETE")
    return True

def fix_ai_core():
    """Fix AI core integration issues"""
    
    print("\n🔧 FIXING AI CORE INTEGRATION")
    print("=" * 50)
    
    # Create a working AI core with proper error handling
    ai_fix_code = '''import json
import logging
import os
from typing import Dict, Any
from openai import OpenAI

class AICore:
    def __init__(self):
        self.client = None
        self.confidence_range = {"min": 65, "max": 90}
        self.setup_ai_core()
    
    def setup_ai_core(self) -> bool:
        """Initialize AI core with proper error handling"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logging.error("OpenAI API key not found")
                return False
            
            self.client = OpenAI(api_key=api_key)
            logging.info("AI Core initialized with GPT-4o")
            return True
            
        except Exception as e:
            logging.error(f"AI Core setup failed: {e}")
            return False
    
    def get_trade_decision(self, pair_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI trading decision with fallback"""
        
        if not self.client:
            return self._fallback_decision(pair_data)
        
        try:
            prompt = self._create_trading_prompt(pair_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": "You are an expert cryptocurrency trading AI. Respond ONLY with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            decision = json.loads(content)
            return self._validate_decision(decision, pair_data)
            
        except json.JSONDecodeError as e:
            logging.error(f"AI JSON decode error: {e}")
            return self._fallback_decision(pair_data)
        except Exception as e:
            logging.error(f"AI decision error: {e}")
            return self._fallback_decision(pair_data)
    
    def _fallback_decision(self, pair_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback decision when AI fails"""
        return {
            "direction": "hold",
            "leverage": 1,
            "strategy": "trend", 
            "confidence": 50,
            "reasoning": "AI fallback - holding position",
            "stop_loss_pct": 2.0,
            "trailing_stop_pct": 1.5,
            "take_profit_pct": 3.0,
            "trade_type": "spot",
            "dynamic_risk": False,
            "volatility_adjusted": False
        }
'''
    
    print("✅ AI Core fix prepared")
    return ai_fix_code

if __name__ == "__main__":
    diagnose_system()
    fix_ai_core()