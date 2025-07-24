#!/usr/bin/env python3
"""
Bot Live Trading Assessment and Control
Real-time monitoring and stability checks
"""

import os
import sqlite3
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv('.env_okx')

def assess_bot_performance():
    """Assess current bot performance and trading status"""
    print("NEXUS BOT LIVE ASSESSMENT")
    print("=" * 40)
    print(f"Assessment Time: {datetime.now()}")
    print()
    
    # Check database connection
    try:
        conn = sqlite3.connect('live_trading_performance.db')
        cursor = conn.cursor()
        
        # Get recent trades
        cursor.execute('''
            SELECT COUNT(*) as total_trades, 
                   SUM(CASE WHEN pnl_usdt > 0 THEN 1 ELSE 0 END) as winning_trades,
                   SUM(pnl_usdt) as total_pnl,
                   AVG(ai_confidence) as avg_confidence
            FROM live_trades 
            WHERE timestamp > datetime('now', '-24 hours')
        ''')
        
        trade_stats = cursor.fetchone()
        total_trades = trade_stats[0] or 0
        winning_trades = trade_stats[1] or 0
        total_pnl = trade_stats[2] or 0
        avg_confidence = trade_stats[3] or 0
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        print(f"📊 TRADING STATISTICS (24h):")
        print(f"   Total Trades: {total_trades}")
        print(f"   Winning Trades: {winning_trades}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Total P&L: ${total_pnl:.2f}")
        print(f"   Avg AI Confidence: {avg_confidence:.1f}%")
        
        # Get recent bot status
        cursor.execute('''
            SELECT status, balance_usdt, timestamp
            FROM bot_status 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        
        status_row = cursor.fetchone()
        if status_row:
            last_status, last_balance, last_update = status_row
            print(f"\n🤖 BOT STATUS:")
            print(f"   Last Status: {last_status}")
            print(f"   Last Balance: ${last_balance:.2f}")
            print(f"   Last Update: {last_update}")
        
        conn.close()
        
    except Exception as e:
        print(f"⚠️  Database error: {e}")
    
    # Check live connection
    try:
        import ccxt
        
        client = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'enableRateLimit': True,
            'sandbox': False
        })
        
        balance = client.fetch_balance()
        usdt_total = balance.get('USDT', {}).get('total', 0)
        
        print(f"\n💰 LIVE BALANCE:")
        print(f"   Current USDT: ${usdt_total:.2f}")
        print(f"   Trading Ready: {'Yes' if usdt_total >= 5 else 'No - Insufficient'}")
        
        # Check recent market activity
        ticker = client.fetch_ticker('BTC/USDT')
        print(f"   BTC Price: ${ticker['last']:,.2f}")
        
        print(f"\n✅ CONNECTION STATUS: ACTIVE")
        print(f"✅ MODE: LIVE TRADING")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    print(f"\n🎯 ASSESSMENT COMPLETE")

def check_trading_conditions():
    """Check if trading conditions are favorable"""
    print("\nTRADING CONDITIONS CHECK")
    print("-" * 30)
    
    try:
        import ccxt
        
        client = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'enableRateLimit': True,
            'sandbox': False
        })
        
        # Check multiple trading pairs
        pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT']
        favorable_conditions = 0
        
        for pair in pairs:
            try:
                ticker = client.fetch_ticker(pair)
                volume_24h = ticker.get('quoteVolume', 0)
                price_change = ticker.get('percentage', 0)
                
                if volume_24h > 1000000 and abs(price_change) > 0.5:  # Good volume and movement
                    favorable_conditions += 1
                    status = "✅ Favorable"
                else:
                    status = "⚠️  Low activity"
                
                print(f"{pair}: {status} (Vol: ${volume_24h:,.0f}, Change: {price_change:+.2f}%)")
                
            except:
                print(f"{pair}: ❌ Data unavailable")
        
        condition_score = (favorable_conditions / len(pairs)) * 100
        print(f"\nMarket Condition Score: {condition_score:.0f}%")
        
        if condition_score >= 75:
            print("🟢 Excellent trading conditions")
        elif condition_score >= 50:
            print("🟡 Good trading conditions")
        else:
            print("🔴 Poor trading conditions")
            
    except Exception as e:
        print(f"❌ Market check failed: {e}")

if __name__ == "__main__":
    assess_bot_performance()
    check_trading_conditions()