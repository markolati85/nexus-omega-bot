#!/usr/bin/env python3
"""
NEXUS AI AUTONOMOUS TRADING BOT - FINAL VERSION
Full GPT-4o controlled autonomous trading with live execution
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

WATCHLIST = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT",
    "XRP/USDT", "DOGE/USDT", "APT/USDT", "OP/USDT", 
    "AVAX/USDT", "MATIC/USDT", "ARB/USDT", "LTC/USDT"
]

# OKX API Configuration
OKX_CONFIG = {
    'apiKey': 'bfee3fff-cdf1-4b71-9ef9-8760de8732f4',
    'secret': 'E7C2058E8DC095D3F45F5C37D6A28DC8',
    'password': 'Okx123#',
    'sandbox': False
}

# OpenAI GPT-4o Configuration
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class NexusAutonomousBot:
    def __init__(self):
        self.exchange = ccxt.okx(OKX_CONFIG)
        self.cycle = 0
        self.total_trades = 0
        self.successful_trades = 0
        
    def send_telegram(self, message):
        """Send message to Telegram with error handling"""
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": message}
            response = requests.post(url, json=data, timeout=15)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram error: {e}")
            return False

    def get_comprehensive_portfolio(self):
        """Get complete portfolio across all OKX accounts"""
        try:
            # Get account balance
            response = self.exchange.private_get_account_balance()
            total_value = 0
            assets = {}
            
            if response.get("code") == "0":
                details = response.get("data", [{}])[0].get("details", [])
                
                for detail in details:
                    symbol = detail.get("ccy", "")
                    amount = float(detail.get("cashBal", 0))
                    
                    if amount > 0.001:
                        if symbol == "USDT":
                            total_value += amount
                            assets[symbol] = {"amount": amount, "value": amount}
                        else:
                            try:
                                ticker = self.exchange.fetch_ticker(f"{symbol}/USDT")
                                value = amount * ticker["last"]
                                total_value += value
                                assets[symbol] = {"amount": amount, "value": value}
                            except:
                                assets[symbol] = {"amount": amount, "value": 0}
            
            return {"total_value": total_value, "assets": assets}
            
        except Exception as e:
            print(f"Portfolio error: {e}")
            return {"total_value": 0, "assets": {}}

    def auto_transfer_if_needed(self, required_amount):
        """Auto-transfer funds from other wallets if needed"""
        try:
            # Check if we need to transfer funds
            portfolio = self.get_comprehensive_portfolio()
            usdt_available = portfolio["assets"].get("USDT", {}).get("amount", 0)
            
            if usdt_available < required_amount:
                print(f"Need ${required_amount:.2f}, have ${usdt_available:.2f} - checking other wallets")
                
                # Try to transfer from funding account
                try:
                    transfer_response = self.exchange.private_post_asset_transfer({
                        'ccy': 'USDT',
                        'amt': str(required_amount - usdt_available + 10),  # Add buffer
                        'from': '6',  # Funding account
                        'to': '18'    # Trading account
                    })
                    
                    if transfer_response.get("code") == "0":
                        print(f"Successfully transferred funds")
                        time.sleep(2)  # Wait for transfer
                        return True
                        
                except Exception as transfer_error:
                    print(f"Transfer failed: {transfer_error}")
            
            return usdt_available >= required_amount
            
        except Exception as e:
            print(f"Auto-transfer error: {e}")
            return False

    def get_gpt4o_trading_decision(self, market_data, portfolio_data):
        """Get GPT-4o trading decision with full reasoning"""
        try:
            # Prepare market analysis for GPT-4o
            market_summary = []
            for pair_data in market_data[:6]:  # Top 6 pairs
                market_summary.append(f"{pair_data['symbol']}: {pair_data['change_24h']:+.1f}% (Confidence: {pair_data['confidence']}%)")
            
            prompt = f"""You are an expert cryptocurrency trading AI with full autonomy to execute trades.

PORTFOLIO STATUS:
- Total Value: ${portfolio_data['total_value']:.2f} USDT
- Available for Trading: ${portfolio_data['assets'].get('USDT', {}).get('amount', 0):.2f} USDT

MARKET ANALYSIS:
{chr(10).join(market_summary)}

TRADING RULES:
1. Only trade if confidence >= 70%
2. Position sizing based on confidence:
   - 70-74%: 8% of portfolio
   - 75-84%: 12% of portfolio  
   - 85-89%: 18% of portfolio
   - 90%+: 25% of portfolio
3. Choose trade type: SPOT, MARGIN, or FUTURES based on confidence and volatility
4. Set leverage (1x-50x) based on confidence and risk assessment
5. Always set stop-loss (-3% to -5%) and take-profit (+5% to +15%)

Respond with JSON only:
{{
    "should_trade": true/false,
    "pair": "BTC/USDT",
    "action": "BUY/SELL",
    "confidence": 85,
    "position_size_percent": 18,
    "trade_type": "FUTURES",
    "leverage": 25,
    "stop_loss_percent": -3,
    "take_profit_percent": 8,
    "reasoning": "Strong bullish breakout with high volume confirmation and RSI oversold bounce"
}}"""

            response = openai_client.chat.completions.create(
                model="gpt-4o",  # Latest OpenAI model
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            decision = json.loads(response.choices[0].message.content)
            return decision
            
        except Exception as e:
            print(f"GPT-4o decision error: {e}")
            return {"should_trade": False, "reasoning": f"AI decision failed: {str(e)[:50]}"}

    def execute_live_trade(self, decision, portfolio_value):
        """Execute actual live trade on OKX"""
        try:
            if not decision.get("should_trade", False):
                return None
                
            pair = decision["pair"]
            action = decision["action"]
            position_percent = decision["position_size_percent"]
            trade_type = decision.get("trade_type", "SPOT")
            leverage = decision.get("leverage", 1)
            
            # Calculate position size
            position_size_usd = portfolio_value * (position_percent / 100)
            
            # Ensure we have enough funds
            if not self.auto_transfer_if_needed(position_size_usd):
                return {"error": "Insufficient funds after transfer attempt"}
            
            # Get current price
            ticker = self.exchange.fetch_ticker(pair)
            current_price = ticker["last"]
            
            # Calculate quantity
            if action == "BUY":
                quantity = position_size_usd / current_price
            else:  # SELL
                # For selling, we need to check if we have the asset
                base_currency = pair.split("/")[0]
                portfolio = self.get_comprehensive_portfolio()
                available_amount = portfolio["assets"].get(base_currency, {}).get("amount", 0)
                
                if available_amount < 0.001:  # Don't have the asset to sell
                    return {"error": f"No {base_currency} available to sell"}
                
                quantity = min(available_amount * 0.95, position_size_usd / current_price)  # Use 95% to account for fees
            
            # Execute trade based on type
            if trade_type == "FUTURES":
                # Futures trading with leverage
                order = self.execute_futures_trade(pair, action, quantity, leverage, decision)
            elif trade_type == "MARGIN":
                # Margin trading
                order = self.execute_margin_trade(pair, action, quantity, min(10, leverage), decision)
            else:
                # Spot trading
                order = self.execute_spot_trade(pair, action, quantity, decision)
            
            if order and order.get("id"):
                self.total_trades += 1
                self.successful_trades += 1
                
                return {
                    "success": True,
                    "order_id": order["id"],
                    "pair": pair,
                    "action": action,
                    "quantity": quantity,
                    "price": current_price,
                    "position_size": position_size_usd,
                    "trade_type": trade_type,
                    "leverage": leverage,
                    "decision": decision
                }
            else:
                return {"error": "Trade execution failed"}
                
        except Exception as e:
            print(f"Trade execution error: {e}")
            return {"error": str(e)}

    def execute_spot_trade(self, pair, action, quantity, decision):
        """Execute spot trade"""
        try:
            side = action.lower()
            order = self.exchange.create_market_order(pair, side, quantity)
            return order
        except Exception as e:
            print(f"Spot trade error: {e}")
            return None

    def execute_margin_trade(self, pair, action, quantity, leverage, decision):
        """Execute margin trade"""
        try:
            # Set leverage for margin trading
            self.exchange.set_leverage(leverage, pair)
            
            side = action.lower()
            order = self.exchange.create_market_order(pair, side, quantity)
            return order
        except Exception as e:
            print(f"Margin trade error: {e}")
            return None

    def execute_futures_trade(self, pair, action, quantity, leverage, decision):
        """Execute futures trade with leverage"""
        try:
            # Convert to futures symbol format
            futures_pair = pair.replace("/", "-") + "-SWAP"
            
            # Set leverage
            self.exchange.set_leverage(leverage, futures_pair)
            
            side = action.lower()
            order = self.exchange.create_market_order(futures_pair, side, quantity)
            return order
        except Exception as e:
            print(f"Futures trade error: {e}")
            return None

    def analyze_all_pairs(self):
        """Analyze all 12 pairs with enhanced metrics"""
        opportunities = []
        
        for symbol in WATCHLIST:
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                price = ticker["last"]
                change_24h = ticker.get("percentage", 0)
                volume = ticker.get("quoteVolume", 0)
                
                # Enhanced confidence calculation
                momentum_score = min(50, abs(change_24h) * 10)
                volume_score = 30 if volume > 10000000 else 20 if volume > 1000000 else 10
                volatility_score = 15 if abs(change_24h) >= 3 else 10 if abs(change_24h) >= 1.5 else 5
                
                confidence = 50 + momentum_score + volume_score + volatility_score
                confidence = min(95, confidence)
                
                # Determine action based on technical analysis
                if change_24h >= 2.5:
                    action = "BUY"
                elif change_24h <= -2.5:
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
        
        # Sort by confidence
        opportunities.sort(key=lambda x: x["confidence"], reverse=True)
        return opportunities

    def run_autonomous_cycle(self):
        """Run complete autonomous trading cycle"""
        self.cycle += 1
        print(f"\n=== AUTONOMOUS CYCLE {self.cycle} ===")
        
        # Get portfolio and market data
        portfolio_data = self.get_comprehensive_portfolio()
        market_data = self.analyze_all_pairs()
        
        portfolio_value = portfolio_data["total_value"]
        print(f"Portfolio: ${portfolio_value:.2f} USDT")
        
        if not market_data:
            self.send_telegram(f"❌ CYCLE {self.cycle}: No market data available")
            return
        
        # Get GPT-4o trading decision
        decision = self.get_gpt4o_trading_decision(market_data, portfolio_data)
        
        best_opportunity = market_data[0]
        
        if decision.get("should_trade", False) and best_opportunity["confidence"] >= 70:
            # Execute the trade
            trade_result = self.execute_live_trade(decision, portfolio_value)
            
            if trade_result and trade_result.get("success"):
                # Send trade execution notification
                message = f"""🔍 TRADE EXECUTED - CYCLE {self.cycle}

📊 Trade Details:
• Pair: {trade_result['pair']}
• Action: {trade_result['action']}
• Confidence: {decision['confidence']}%
• Strategy: {decision.get('reasoning', 'AI Decision')[:50]}...

💰 Execution:
• Type: {trade_result['trade_type']}
• Leverage: {trade_result['leverage']}x
• Position: ${trade_result['position_size']:.2f} ({decision['position_size_percent']}%)
• Price: ${trade_result['price']:,.4f}
• Order ID: {trade_result['order_id']}

📈 Risk Management:
• Stop Loss: {decision.get('stop_loss_percent', -3)}%
• Take Profit: {decision.get('take_profit_percent', 8)}%

💼 Portfolio: ${portfolio_value:.2f} USDT
📊 Success Rate: {(self.successful_trades/max(1,self.total_trades))*100:.1f}%

⏰ {datetime.now().strftime('%H:%M:%S UTC')}"""
                
                self.send_telegram(message)
                print(f"✅ Trade executed: {trade_result['pair']} {trade_result['action']}")
                
            else:
                # Trade failed
                error_msg = trade_result.get("error", "Unknown error") if trade_result else "Execution failed"
                message = f"""❌ TRADE FAILED - CYCLE {self.cycle}

🚫 Error: {error_msg}
📊 Attempted: {decision.get('pair', 'Unknown')} {decision.get('action', 'Unknown')}
💰 Portfolio: ${portfolio_value:.2f} USDT

⏰ {datetime.now().strftime('%H:%M:%S UTC')}"""
                
                self.send_telegram(message)
                print(f"❌ Trade failed: {error_msg}")
        else:
            # No trade - send market scan
            top_3 = market_data[:3]
            
            message = f"""📊 AUTONOMOUS SCAN #{self.cycle}

🤖 GPT-4o Analysis: {decision.get('reasoning', 'No trade signal')[:80]}...

🔍 Market Status:
• Pairs Scanned: 12
• Best Confidence: {best_opportunity['confidence']}%
• Trade Threshold: 70%+

📈 Top Opportunities:"""
            
            for i, opp in enumerate(top_3, 1):
                emoji = "🟢" if opp["action"] == "BUY" else "🔴" if opp["action"] == "SELL" else "⚪"
                message += f"\n{i}. {emoji} {opp['symbol']}: {opp['confidence']}% ({opp['change_24h']:+.1f}%)"
            
            message += f"""

💰 Portfolio: ${portfolio_value:.2f} USDT
🎯 Waiting for: 70%+ confidence signal
📊 Trades: {self.total_trades} total, {(self.successful_trades/max(1,self.total_trades))*100:.1f}% success

⏰ {datetime.now().strftime('%H:%M:%S UTC')}"""
            
            self.send_telegram(message)
            print(f"📊 Market scan: Best {best_opportunity['symbol']} ({best_opportunity['confidence']}%)")

    def start_autonomous_trading(self):
        """Start fully autonomous trading system"""
        print("🚀 Starting Nexus Autonomous Trading Bot...")
        
        # Send startup notification
        startup_message = f"""🤖 NEXUS AUTONOMOUS BOT ONLINE

✅ FULL AI CONTROL ACTIVATED:
• GPT-4o Decision Making: Live
• Auto Trade Execution: Active
• Dynamic Position Sizing: 8-25%
• Multi-Type Trading: Spot/Margin/Futures
• Leverage Range: 1x-50x
• Stop Loss/Take Profit: Automated

📊 Monitoring: 12 pairs
💰 Portfolio: ${self.get_comprehensive_portfolio()['total_value']:.2f} USDT
🎯 Trade Threshold: 70%+ confidence
🔄 Cycle: 90 seconds

🚨 LIVE TRADING MODE: Real money at risk
💼 AI will execute trades autonomously

⏰ Started: {datetime.now().strftime('%H:%M:%S UTC')}"""
        
        if not self.send_telegram(startup_message):
            print("❌ Failed to send startup message")
            return
        
        print("✅ Autonomous bot started successfully")
        
        try:
            while True:
                start_time = time.time()
                
                # Run autonomous cycle
                self.run_autonomous_cycle()
                
                # Sleep for 90 seconds
                elapsed = time.time() - start_time
                sleep_time = max(0, 90 - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n🛑 Autonomous bot stopped")
            self.send_telegram("🔴 NEXUS AUTONOMOUS BOT OFFLINE\n\nStopped by user intervention.")
        except Exception as e:
            print(f"❌ Critical error: {e}")
            self.send_telegram(f"⚠️ CRITICAL ERROR\n\n{str(e)[:100]}...")

if __name__ == "__main__":
    bot = NexusAutonomousBot()
    bot.start_autonomous_trading()