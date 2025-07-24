#!/usr/bin/env python3
"""
Live Trading Launch and Performance Tracking
"""

import os
import time
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env_okx')

def create_trading_database():
    """Create trading performance database"""
    conn = sqlite3.connect('live_trading_performance.db')
    cursor = conn.cursor()
    
    # Create trades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS live_trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            pair TEXT NOT NULL,
            side TEXT NOT NULL,
            amount REAL NOT NULL,
            price REAL NOT NULL,
            value_usdt REAL NOT NULL,
            order_id TEXT,
            strategy TEXT,
            ai_confidence REAL,
            status TEXT DEFAULT 'executed',
            pnl_usdt REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create performance tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            total_balance_usdt REAL NOT NULL,
            available_usdt REAL NOT NULL,
            crypto_value_usdt REAL NOT NULL,
            total_trades INTEGER DEFAULT 0,
            successful_trades INTEGER DEFAULT 0,
            win_rate REAL DEFAULT 0,
            daily_pnl REAL DEFAULT 0,
            bot_status TEXT DEFAULT 'running',
            ai_confidence_avg REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Trading performance database created")

def test_live_connection():
    """Test live OKX connection"""
    try:
        import ccxt
        
        client = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'enableRateLimit': True,
            'sandbox': False  # LIVE TRADING
        })
        
        print("🔍 TESTING LIVE OKX CONNECTION...")
        
        # Test balance
        balance = client.fetch_balance()
        usdt_total = balance.get('USDT', {}).get('total', 0)
        usdt_free = balance.get('USDT', {}).get('free', 0)
        
        print(f"✅ Connection: SUCCESS")
        print(f"✅ USDT Balance: ${usdt_total:.2f}")
        print(f"✅ Available: ${usdt_free:.2f}")
        print(f"✅ Mode: LIVE TRADING (No simulation)")
        
        # Test market data
        ticker = client.fetch_ticker('BTC/USDT')
        print(f"✅ Market Data: BTC at ${ticker['last']:,.2f}")
        
        # Calculate crypto holdings value
        crypto_value = 0
        for asset, amounts in balance['total'].items():
            if asset != 'USDT' and amounts > 0.001:
                try:
                    asset_ticker = client.fetch_ticker(f'{asset}/USDT')
                    crypto_value += amounts * asset_ticker['last']
                    print(f"   {asset}: {amounts:.6f} (${amounts * asset_ticker['last']:.2f})")
                except:
                    pass
        
        total_portfolio = usdt_total + crypto_value
        print(f"✅ Total Portfolio: ${total_portfolio:.2f}")
        
        # Log initial performance
        conn = sqlite3.connect('live_trading_performance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_log 
            (timestamp, total_balance_usdt, available_usdt, crypto_value_usdt, bot_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            total_portfolio,
            usdt_total,
            crypto_value,
            'initialized'
        ))
        
        conn.commit()
        conn.close()
        
        print("✅ Performance tracking initialized")
        return True, total_portfolio
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False, 0

def launch_live_bot():
    """Launch live trading bot"""
    print("NEXUS OKX PRO - LIVE TRADING LAUNCH")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print("Mode: LIVE TRADING (Real Money)")
    print()
    
    # Create database
    create_trading_database()
    
    # Test connection
    success, portfolio_value = test_live_connection()
    
    if not success:
        print("❌ Cannot proceed without valid OKX connection")
        return
    
    print(f"\n🚀 READY FOR LIVE TRADING")
    print(f"Portfolio Value: ${portfolio_value:.2f}")
    print(f"Trading Mode: Live (No simulation)")
    print(f"AI Engine: GPT-4o powered")
    print(f"Confidence Threshold: 70%")
    print(f"Position Size: 6% per trade")
    print(f"Cycle Frequency: 3 minutes")
    
    # Launch bot
    try:
        print("\n🤖 LAUNCHING AUTONOMOUS TRADING BOT...")
        
        # Import and start bot
        from nexus_okx_pro_gpt4o import NexusOKXProAutonomous
        
        bot = NexusOKXProAutonomous()
        
        if bot.setup_okx_connection():
            print("✅ OKX connection established")
            
            if bot.setup_openai_connection():
                print("✅ GPT-4o AI engine connected")
            
            print("✅ All systems operational")
            print("\n🔄 STARTING AUTONOMOUS TRADING CYCLES...")
            
            # Start trading loop
            cycle_count = 0
            while True:
                try:
                    cycle_count += 1
                    print(f"\n--- CYCLE {cycle_count} - {datetime.now().strftime('%H:%M:%S')} ---")
                    
                    # Run trading cycle
                    bot.autonomous_trading_cycle()
                    
                    print(f"Cycle {cycle_count} completed - Waiting 180 seconds...")
                    time.sleep(180)  # 3 minutes
                    
                except KeyboardInterrupt:
                    print("\n🛑 Bot stopped by user")
                    break
                except Exception as e:
                    print(f"⚠️ Cycle error: {e}")
                    print("Continuing in 60 seconds...")
                    time.sleep(60)
        else:
            print("❌ Bot initialization failed")
            
    except Exception as e:
        print(f"❌ Launch error: {e}")

if __name__ == "__main__":
    launch_live_bot()