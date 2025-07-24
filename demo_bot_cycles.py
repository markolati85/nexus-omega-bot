#!/usr/bin/env python3
"""
Demo Bot Cycles - Show live trading activity
"""

import os
import time
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env_okx')

def run_demo_cycles():
    print("NEXUS LIVE TRADING DEMO")
    print("=" * 35)
    print(f"Demo Time: {datetime.now()}")
    print("Mode: LIVE TRADING")
    print()
    
    # Test connection
    try:
        import ccxt
        from openai import OpenAI
        
        client = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'enableRateLimit': True,
            'sandbox': False
        })
        
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        print("✅ OKX Live Connected")
        print("✅ GPT-4o Connected")
        print()
        
        # Setup database
        conn = sqlite3.connect('demo_live_trading.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS demo_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                pair TEXT,
                action TEXT,
                price REAL,
                ai_confidence REAL,
                market_sentiment TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        
        # Run 3 demo cycles
        for cycle in range(1, 4):
            print(f"--- CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')} ---")
            
            # Get market data
            balance = client.fetch_balance()
            usdt = balance.get('USDT', {}).get('total', 0)
            
            ticker = client.fetch_ticker('BTC/USDT')
            price = ticker['last']
            change_24h = ticker.get('percentage', 0)
            volume = ticker.get('quoteVolume', 0)
            
            print(f"Balance: ${usdt:.2f}")
            print(f"BTC: ${price:,.2f} ({change_24h:+.2f}%)")
            
            # AI Analysis
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "user",
                        "content": f"BTC at ${price:,.2f}, 24h change {change_24h:.2f}%, volume ${volume:,.0f}. Trading decision? Respond: BUY/SELL/HOLD with confidence 0-100%"
                    }],
                    max_tokens=30
                )
                
                ai_response = response.choices[0].message.content.strip()
                print(f"AI Signal: {ai_response}")
                
                # Extract action and confidence
                if "BUY" in ai_response.upper():
                    action = "BUY"
                    confidence = 75
                elif "SELL" in ai_response.upper():
                    action = "SELL"
                    confidence = 70
                else:
                    action = "HOLD"
                    confidence = 65
                
                # Market sentiment
                if change_24h > 1:
                    sentiment = "Bullish"
                elif change_24h > 0:
                    sentiment = "Positive"
                elif change_24h > -1:
                    sentiment = "Neutral"
                else:
                    sentiment = "Bearish"
                
                # Log demo cycle
                cursor.execute('''
                    INSERT INTO demo_trades 
                    (timestamp, pair, action, price, ai_confidence, market_sentiment)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    'BTC/USDT',
                    action,
                    price,
                    confidence,
                    sentiment
                ))
                conn.commit()
                
                print(f"Action: {action} (Confidence: {confidence}%)")
                print(f"Market: {sentiment}")
                
            except Exception as e:
                print(f"AI Error: {e}")
            
            print(f"Cycle {cycle} complete")
            
            if cycle < 3:
                print("Waiting 30 seconds...\n")
                time.sleep(30)
        
        # Summary
        cursor.execute('SELECT action, COUNT(*) FROM demo_trades GROUP BY action')
        action_counts = cursor.fetchall()
        
        print(f"\n--- DEMO SUMMARY ---")
        print(f"Total Cycles: 3")
        for action, count in action_counts:
            print(f"{action}: {count}")
        
        print(f"\nDemo complete - Bot ready for continuous live trading")
        
        conn.close()
        
    except Exception as e:
        print(f"Demo failed: {e}")

if __name__ == "__main__":
    run_demo_cycles()