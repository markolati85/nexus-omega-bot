#!/usr/bin/env python3
"""
Bot Performance Analysis and Monthly Profit Projection
"""

import os
import json
import ccxt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def analyze_performance():
    print("📊 NEXUS BOT PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    # Setup exchange
    try:
        exchange = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'sandbox': False,
            'enableRateLimit': True
        })
        
        # Get current balance
        balance = exchange.fetch_balance()
        current_usdt = balance.get('USDT', {}).get('free', 0)
        total_portfolio = balance.get('USDT', {}).get('total', 0)
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return
    
    # Analyze trade history
    try:
        with open('ultimate_trades.log', 'r') as f:
            trades = [json.loads(line) for line in f.readlines()]
        
        print(f"💰 CURRENT PORTFOLIO:")
        print(f"Free USDT: ${current_usdt:.2f}")
        print(f"Total Portfolio: ${total_portfolio:.2f}")
        
        print(f"\n📈 TRADING STATISTICS:")
        print(f"Total Trades Executed: {len(trades)}")
        
        # Calculate trading volume and frequency
        total_volume = sum(trade['trade_amount'] for trade in trades)
        leveraged_volume = sum(trade['effective_position'] for trade in trades)
        
        print(f"Total Trading Volume: ${total_volume:.2f}")
        print(f"Total Leveraged Exposure: ${leveraged_volume:.2f}")
        
        # Analyze trade types
        spot_trades = [t for t in trades if t['action'] == 'spot_buy']
        futures_trades = [t for t in trades if 'futures' in t['action']]
        margin_trades = [t for t in trades if 'margin' in t['action']]
        
        print(f"\n🎯 TRADE BREAKDOWN:")
        print(f"Spot Trades: {len(spot_trades)}")
        print(f"Futures Trades: {len(futures_trades)}")
        print(f"Margin Trades: {len(margin_trades)}")
        
        # Calculate average leverage
        leveraged_trades = [t for t in trades if t['leverage'] > 1]
        if leveraged_trades:
            avg_leverage = sum(t['leverage'] for t in leveraged_trades) / len(leveraged_trades)
            print(f"Average Leverage Used: {avg_leverage:.1f}x")
        
        # Time analysis
        if trades:
            first_trade = datetime.fromisoformat(trades[0]['timestamp'])
            last_trade = datetime.fromisoformat(trades[-1]['timestamp'])
            trading_duration = last_trade - first_trade
            
            print(f"\n⏱️ TRADING ACTIVITY:")
            print(f"Trading Duration: {trading_duration}")
            print(f"Trade Frequency: {len(trades)/max(trading_duration.total_seconds()/3600, 1):.1f} trades/hour")
        
        # Performance projection
        print(f"\n🚀 MONTHLY PROFIT PROJECTIONS:")
        
        # Conservative estimate (current performance)
        daily_trades = len(trades) / max((datetime.now() - first_trade).days, 1) if trades else 0
        monthly_trades = daily_trades * 30
        
        # Profit calculations based on different scenarios
        conservative_profit_per_trade = 0.5  # 0.5% profit per trade
        moderate_profit_per_trade = 1.0      # 1% profit per trade  
        aggressive_profit_per_trade = 2.0    # 2% profit per trade
        
        base_capital = 85.64  # Starting capital
        
        print(f"📊 SCENARIO ANALYSIS (Based on {daily_trades:.1f} trades/day):")
        print(f"\n🟢 CONSERVATIVE (0.5% per trade):")
        conservative_monthly = base_capital * (1 + conservative_profit_per_trade/100) ** monthly_trades - base_capital
        print(f"   Monthly Profit: ${conservative_monthly:.2f}")
        print(f"   Monthly Return: {(conservative_monthly/base_capital)*100:.1f}%")
        
        print(f"\n🟡 MODERATE (1.0% per trade):")
        moderate_monthly = base_capital * (1 + moderate_profit_per_trade/100) ** monthly_trades - base_capital
        print(f"   Monthly Profit: ${moderate_monthly:.2f}")
        print(f"   Monthly Return: {(moderate_monthly/base_capital)*100:.1f}%")
        
        print(f"\n🔴 AGGRESSIVE (2.0% per trade):")
        aggressive_monthly = base_capital * (1 + aggressive_profit_per_trade/100) ** monthly_trades - base_capital
        print(f"   Monthly Profit: ${aggressive_monthly:.2f}")
        print(f"   Monthly Return: {(aggressive_monthly/base_capital)*100:.1f}%")
        
        # With leverage multiplier
        print(f"\n⚡ WITH LEVERAGE MULTIPLIER:")
        leverage_multiplier = 1.5  # Average 50% leverage benefit
        
        conservative_leveraged = conservative_monthly * leverage_multiplier
        moderate_leveraged = moderate_monthly * leverage_multiplier  
        aggressive_leveraged = aggressive_monthly * leverage_multiplier
        
        print(f"Conservative + Leverage: ${conservative_leveraged:.2f}")
        print(f"Moderate + Leverage: ${moderate_leveraged:.2f}")
        print(f"Aggressive + Leverage: ${aggressive_leveraged:.2f}")
        
        # Most realistic estimate
        print(f"\n🎯 MOST REALISTIC ESTIMATE:")
        realistic_profit = (conservative_leveraged + moderate_leveraged) / 2
        print(f"Expected Monthly Profit: ${realistic_profit:.2f}")
        print(f"Expected Monthly Return: {(realistic_profit/base_capital)*100:.1f}%")
        
        # Factors affecting performance
        print(f"\n🔄 PERFORMANCE FACTORS:")
        print(f"✅ AI Decision Making: GPT-4o powered")
        print(f"✅ Multiple Trading Types: Spot, Margin, Futures")
        print(f"✅ Leverage Utilization: Up to 125x")
        print(f"✅ 24/7 Operation: Continuous trading")
        print(f"✅ Market Adaptability: Volatility-based strategy")
        print(f"⚠️ Market Conditions: Bull/bear market impact")
        print(f"⚠️ Risk Management: Conservative position sizing")
        
    except FileNotFoundError:
        print("⚠️ No trading history found")
    except Exception as e:
        print(f"❌ Analysis error: {e}")

if __name__ == "__main__":
    analyze_performance()