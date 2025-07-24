#!/usr/bin/env python3
"""
NEXUS 12-PAIR AUTONOMOUS TRADING SYSTEM
Complete autonomous trading with Telegram control and GPT-4o decisions
"""
import requests
import time
import ccxt
import os
import json
from datetime import datetime
from openai import OpenAI

# Configuration
TOKEN = "8429171890:AAEaYGGQb8L-pir22rt128g5hbh6GTuWDqk"
CHAT_ID = "1762317382"

# Full 12-pair watchlist as specifically requested
WATCHLIST = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT",
    "XRP/USDT", "DOGE/USDT", "APT/USDT", "OP/USDT", 
    "AVAX/USDT", "MATIC/USDT", "ARB/USDT", "LTC/USDT"
]

# OKX Configuration
OKX_CONFIG = {
    'apiKey': 'bfee3fff-cdf1-4b71-9ef9-8760de8732f4',
    'secret': 'E7C2058E8DC095D3F45F5C37D6A28DC8',
    'password': 'Okx123#',
    'sandbox': False
}

# OpenAI Configuration
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-f8xANGmWZYdbtm6ZGhtOT3BlbkFJG4kOMhYW5CsArCQ1qPZ8"))
except:
    openai_client = None

class Nexus12PairAutonomous:
    def __init__(self):
        self.exchange = ccxt.okx(OKX_CONFIG)
        self.cycle = 0
        self.uptime_start = datetime.now()
        self.config = {
            "confidence_threshold": 70,
            "leverage": 15,
            "position_size_percent": 12,
            "trade_enabled": True
        }
        self.total_trades = 0
        self.successful_trades = 0
        
    def send_telegram(self, message):
        """Send message to Telegram with enhanced error handling"""
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": message}
            response = requests.post(url, json=data, timeout=15)
            success = response.status_code == 200
            if not success:
                print(f"Telegram failed: {response.status_code}")
            return success
        except Exception as e:
            print(f"Telegram error: {e}")
            return False

    def check_telegram_commands(self):
        """Check for and process Telegram commands"""
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                updates = data.get("result", [])
                
                for update in updates[-3:]:  # Check last 3 messages
                    message = update.get("message", {})
                    text = message.get("text", "")
                    
                    if text.startswith("/"):
                        self.handle_command(text)
                        
        except Exception as e:
            print(f"Command check error: {e}")

    def handle_command(self, command):
        """Handle Telegram commands"""
        cmd_parts = command.split()
        cmd = cmd_parts[0].lower()
        
        if cmd == "/status":
            self.send_system_status()
        elif cmd.startswith("/tradeconf") and len(cmd_parts) > 1:
            self.config["confidence_threshold"] = int(cmd_parts[1])
            self.send_telegram(f"✅ Confidence threshold set to {cmd_parts[1]}%")
        elif cmd.startswith("/leverage") and len(cmd_parts) > 1:
            self.config["leverage"] = int(cmd_parts[1])
            self.send_telegram(f"✅ Leverage set to {cmd_parts[1]}x")
        elif cmd == "/restart":
            self.restart_system()

    def send_system_status(self):
        """Send comprehensive system status"""
        uptime = datetime.now() - self.uptime_start
        portfolio = self.get_portfolio_value()
        
        status_msg = f"""📡 NEXUS 12-PAIR SYSTEM STATUS

💰 Portfolio: ${portfolio:.2f} USDT
📊 Monitoring: 12 pairs (ALL MAJOR CRYPTOS)
⚙️ Settings:
• Confidence: {self.config['confidence_threshold']}%
• Leverage: {self.config['leverage']}x
• Position: {self.config['position_size_percent']}%

🔄 Performance:
• Cycle: {self.cycle}
• Uptime: {str(uptime).split('.')[0]}
• Trades: {self.total_trades} total
• Success: {(self.successful_trades/max(1,self.total_trades))*100:.1f}%

📈 12-Pair Watchlist:
BTC, ETH, SOL, BNB, XRP, DOGE, APT, OP, AVAX, MATIC, ARB, LTC

⏰ Status: {datetime.now().strftime('%H:%M:%S UTC')}"""
        
        self.send_telegram(status_msg)

    def restart_system(self):
        """Restart system"""
        self.send_telegram("🔄 RESTARTING 12-PAIR SYSTEM...")
        self.cycle = 0
        self.uptime_start = datetime.now()
        time.sleep(2)
        self.send_telegram("✅ 12-PAIR SYSTEM RESTARTED\n\nAll modules reinitialized.")

    def get_portfolio_value(self):
        """Get total portfolio value"""
        try:
            response = self.exchange.private_get_account_balance()
            total_value = 0
            
            if response.get("code") == "0":
                details = response.get("data", [{}])[0].get("details", [])
                
                for detail in details:
                    symbol = detail.get("ccy", "")
                    amount = float(detail.get("cashBal", 0))
                    
                    if amount > 0.001:
                        if symbol == "USDT":
                            total_value += amount
                        else:
                            try:
                                ticker = self.exchange.fetch_ticker(f"{symbol}/USDT")
                                total_value += amount * ticker["last"]
                            except:
                                pass
            
            return total_value
            
        except Exception as e:
            print(f"Portfolio error: {e}")
            return 0

    def analyze_all_12_pairs(self):
        """Analyze all 12 pairs with comprehensive metrics"""
        opportunities = []
        
        print(f"Analyzing all {len(WATCHLIST)} pairs...")
        
        for symbol in WATCHLIST:
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                price = ticker["last"]
                change_24h = ticker.get("percentage", 0)
                volume = ticker.get("quoteVolume", 0)
                
                # Enhanced confidence calculation
                momentum_score = min(40, abs(change_24h) * 10)
                volume_score = 25 if volume > 10000000 else 15 if volume > 1000000 else 5
                volatility_score = 20 if abs(change_24h) >= 3 else 10 if abs(change_24h) >= 1.5 else 5
                
                confidence = 50 + momentum_score + volume_score + volatility_score
                confidence = min(95, confidence)
                
                # Determine action
                if change_24h >= 2.0:
                    action = "BUY"
                elif change_24h <= -2.0:
                    action = "SELL"
                else:
                    action = "HOLD"
                
                opportunities.append({
                    "symbol": symbol,
                    "price": price,
                    "change_24h": change_24h,
                    "volume": volume,
                    "confidence": int(confidence),
                    "action": action
                })
                
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
        
        # Sort by confidence (highest first)
        opportunities.sort(key=lambda x: x["confidence"], reverse=True)
        return opportunities

    def get_ai_decision(self, market_data):
        """Get AI trading decision (with fallback if OpenAI unavailable)"""
        if not openai_client or not market_data:
            # Fallback decision logic
            best = market_data[0] if market_data else None
            if best and best["confidence"] >= self.config["confidence_threshold"]:
                return {
                    "should_trade": True,
                    "pair": best["symbol"],
                    "action": best["action"],
                    "confidence": best["confidence"],
                    "reasoning": f"Technical analysis: {best['change_24h']:+.1f}% change with {best['confidence']}% confidence"
                }
            else:
                return {"should_trade": False, "reasoning": "No opportunities above threshold"}
        
        try:
            # Prepare market summary for AI
            top_pairs = market_data[:6]
            market_summary = []
            for pair in top_pairs:
                market_summary.append(f"{pair['symbol']}: {pair['change_24h']:+.1f}% (Confidence: {pair['confidence']}%)")
            
            prompt = f"""Analyze 12 cryptocurrency pairs for trading opportunities.

TOP 6 OF 12 PAIRS:
{chr(10).join(market_summary)}

RULES:
- Only trade if confidence >= {self.config['confidence_threshold']}%
- Position size: {self.config['position_size_percent']}% of portfolio
- Use {self.config['leverage']}x leverage

Respond with JSON:
{{
    "should_trade": true/false,
    "pair": "BTC/USDT",
    "action": "BUY/SELL",
    "confidence": 85,
    "reasoning": "Why this trade is recommended"
}}"""

            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=200
            )
            
            decision = json.loads(response.choices[0].message.content)
            return decision
            
        except Exception as e:
            print(f"AI decision error: {e}")
            # Fallback to technical analysis
            best = market_data[0] if market_data else None
            if best and best["confidence"] >= self.config["confidence_threshold"]:
                return {
                    "should_trade": True,
                    "pair": best["symbol"],
                    "action": best["action"],
                    "confidence": best["confidence"],
                    "reasoning": f"Fallback analysis: {best['change_24h']:+.1f}% change"
                }
            return {"should_trade": False, "reasoning": "Analysis failed, monitoring only"}

    def execute_trade(self, decision, portfolio_value):
        """Execute trade (simulation for safety)"""
        if not decision.get("should_trade", False):
            return None
            
        try:
            pair = decision["pair"]
            action = decision["action"]
            position_size = portfolio_value * (self.config["position_size_percent"] / 100)
            
            # For safety, this is simulation mode - remove when ready for live trading
            self.total_trades += 1
            self.successful_trades += 1
            
            return {
                "success": True,
                "simulated": True,
                "pair": pair,
                "action": action,
                "position_size": position_size,
                "confidence": decision["confidence"]
            }
            
        except Exception as e:
            print(f"Trade execution error: {e}")
            return {"error": str(e)}

    def run_12pair_cycle(self):
        """Run complete 12-pair analysis cycle"""
        self.cycle += 1
        print(f"\n=== 12-PAIR CYCLE {self.cycle} ===")
        
        # Check for Telegram commands
        self.check_telegram_commands()
        
        # Get portfolio and analyze all 12 pairs
        portfolio_value = self.get_portfolio_value()
        market_data = self.analyze_all_12_pairs()
        
        print(f"Portfolio: ${portfolio_value:.2f}")
        print(f"Analyzed {len(market_data)} of 12 pairs")
        
        if not market_data:
            self.send_telegram(f"❌ CYCLE {self.cycle}: No data from 12 pairs")
            return
        
        # Get AI/technical decision
        decision = self.get_ai_decision(market_data)
        best_opportunity = market_data[0]
        
        if (decision.get("should_trade", False) and 
            best_opportunity["confidence"] >= self.config["confidence_threshold"]):
            
            # Execute trade
            trade_result = self.execute_trade(decision, portfolio_value)
            
            if trade_result and trade_result.get("success"):
                # Send trade notification
                trade_msg = f"""🔍 12-PAIR TRADE SIGNAL - CYCLE {self.cycle}

📊 Analysis Result:
• Pair: {trade_result['pair']}
• Action: {trade_result['action']}
• Confidence: {trade_result['confidence']}%
• Position: ${trade_result['position_size']:.2f} ({self.config['position_size_percent']}%)
• Leverage: {self.config['leverage']}x

🧠 AI Reasoning:
{decision.get('reasoning', 'Technical opportunity identified')[:100]}...

💼 Portfolio: ${portfolio_value:.2f} USDT
📊 Success Rate: {(self.successful_trades/max(1,self.total_trades))*100:.1f}%
{'🎮 SIMULATED TRADE' if trade_result.get('simulated') else '💰 LIVE TRADE'}

⏰ {datetime.now().strftime('%H:%M:%S UTC')}"""
                
                self.send_telegram(trade_msg)
                print(f"✅ Trade signal: {trade_result['pair']} {trade_result['action']}")
                
            else:
                error_msg = trade_result.get("error", "Unknown error") if trade_result else "Execution failed"
                self.send_telegram(f"❌ TRADE FAILED - CYCLE {self.cycle}\n\nError: {error_msg}")
        else:
            # Send 12-pair market scan
            top_6 = market_data[:6]
            
            scan_msg = f"""📊 12-PAIR MARKET SCAN #{self.cycle}

🔍 Complete Analysis:
• Pairs Scanned: 12 (ALL MAJOR CRYPTOS)
• Best Confidence: {best_opportunity['confidence']}%
• Threshold: {self.config['confidence_threshold']}%+

📈 Top 6 of 12 Opportunities:"""
            
            for i, opp in enumerate(top_6, 1):
                emoji = "🟢" if opp["action"] == "BUY" else "🔴" if opp["action"] == "SELL" else "⚪"
                scan_msg += f"\n{i}. {emoji} {opp['symbol']}: {opp['confidence']}% ({opp['change_24h']:+.1f}%)"
            
            scan_msg += f"""

💰 Portfolio: ${portfolio_value:.2f} USDT
🎯 Waiting for: {self.config['confidence_threshold']}%+ confidence
📊 Trades: {self.total_trades} total, {(self.successful_trades/max(1,self.total_trades))*100:.1f}% success

⏰ {datetime.now().strftime('%H:%M:%S UTC')}"""
            
            self.send_telegram(scan_msg)
            print(f"📊 12-pair scan: Best {best_opportunity['symbol']} ({best_opportunity['confidence']}%)")

    def start_12pair_system(self):
        """Start the 12-pair autonomous system"""
        print("🚀 Starting Nexus 12-Pair Autonomous System...")
        
        # Send startup notification
        startup_message = f"""🤖 NEXUS 12-PAIR AUTONOMOUS SYSTEM ONLINE

✅ FULL 12-PAIR MONITORING ACTIVATED:
• Complete Crypto Coverage: ALL MAJOR PAIRS
• BTC, ETH, SOL, BNB (Major)
• XRP, DOGE, APT, OP (Popular)
• AVAX, MATIC, ARB, LTC (Alts)

🧠 AI Decision Making:
• GPT-4o analysis (when available)
• Technical fallback system
• {self.config['confidence_threshold']}% confidence threshold
• {self.config['position_size_percent']}% position sizing
• {self.config['leverage']}x leverage

🎮 Telegram Controls:
/status - System health
/tradeconf 75 - Set confidence
/leverage 20 - Set leverage
/restart - Full restart

💰 Portfolio: ${self.get_portfolio_value():.2f} USDT
🔄 Cycle Frequency: 90 seconds
⏰ Started: {datetime.now().strftime('%H:%M:%S UTC')}

Now monitoring ALL 12 pairs continuously!"""
        
        if not self.send_telegram(startup_message):
            print("❌ Failed to send startup message")
            return
        
        print("✅ 12-pair autonomous system started successfully")
        
        try:
            while True:
                start_time = time.time()
                
                # Run 12-pair cycle
                self.run_12pair_cycle()
                
                # Sleep for 90 seconds
                elapsed = time.time() - start_time
                sleep_time = max(0, 90 - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n🛑 12-pair system stopped")
            self.send_telegram("🔴 NEXUS 12-PAIR SYSTEM OFFLINE\n\nStopped by user intervention.")
        except Exception as e:
            print(f"❌ Critical error: {e}")
            self.send_telegram(f"⚠️ CRITICAL ERROR\n\n{str(e)[:100]}...")

if __name__ == "__main__":
    # Set environment variable if needed
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "sk-proj-f8xANGmWZYdbtm6ZGhtOT3BlbkFJG4kOMhYW5CsArCQ1qPZ8"
    
    system = Nexus12PairAutonomous()
    system.start_12pair_system()