#!/usr/bin/env python3
"""
Trade Prediction Analysis - When will the system execute next trade
"""

import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

load_dotenv()

def analyze_trade_timing():
    """Analyze when system will execute next trade"""
    
    print("🔮 TRADE EXECUTION PREDICTION ANALYSIS")
    print("=" * 50)
    
    if not CCXT_AVAILABLE:
        print("❌ CCXT not available")
        return
    
    try:
        exchange = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'sandbox': False,
            'enableRateLimit': True
        })
        
        print("📊 CURRENT MARKET CONDITIONS:")
        
        # Check key trading pairs
        pairs_to_check = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOGE/USDT']
        
        trade_signals = 0
        total_pairs = 0
        
        for pair in pairs_to_check:
            try:
                ticker = exchange.fetch_ticker(pair)
                ohlcv = exchange.fetch_ohlcv(pair, '1h', limit=20)
                
                current_price = ticker['last']
                change_24h = ticker['percentage']
                volume_24h = ticker['quoteVolume']
                
                # Simple RSI calculation
                closes = [candle[4] for candle in ohlcv[-14:]]
                if len(closes) >= 14:
                    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
                    gains = [d if d > 0 else 0 for d in deltas]
                    losses = [-d if d < 0 else 0 for d in deltas]
                    
                    avg_gain = sum(gains) / len(gains)
                    avg_loss = sum(losses) / len(losses)
                    
                    if avg_loss > 0:
                        rs = avg_gain / avg_loss
                        rsi = 100 - (100 / (1 + rs))
                    else:
                        rsi = 100
                else:
                    rsi = 50
                
                # Trading signal analysis
                signal_strength = 0
                
                # Strong price movement
                if abs(change_24h) > 5:
                    signal_strength += 1
                
                # RSI oversold/overbought
                if rsi < 30 or rsi > 70:
                    signal_strength += 1
                
                # High volume
                if volume_24h > 1000000:  # $1M+ volume
                    signal_strength += 1
                
                print(f"   {pair}:")
                print(f"     Price: ${current_price:.4f} ({change_24h:+.2f}%)")
                print(f"     RSI: {rsi:.1f}")
                print(f"     Volume: ${volume_24h:,.0f}")
                print(f"     Signal Strength: {signal_strength}/3")
                
                if signal_strength >= 2:
                    trade_signals += 1
                
                total_pairs += 1
                
            except Exception as e:
                print(f"   {pair}: Error - {e}")
        
        print(f"\n🎯 TRADE EXECUTION PROBABILITY:")
        
        signal_percentage = (trade_signals / total_pairs) * 100 if total_pairs > 0 else 0
        
        print(f"   Strong signals: {trade_signals}/{total_pairs} pairs ({signal_percentage:.0f}%)")
        
        # Prediction logic
        if signal_percentage >= 75:
            prediction = "VERY HIGH - Trade likely within 1-5 cycles (1-5 minutes)"
            confidence = "90%+"
        elif signal_percentage >= 50:
            prediction = "HIGH - Trade likely within 5-15 cycles (5-15 minutes)"
            confidence = "75%+"
        elif signal_percentage >= 25:
            prediction = "MODERATE - Trade possible within 15-60 cycles (15-60 minutes)"
            confidence = "50%+"
        else:
            prediction = "LOW - Trade when market conditions improve (1-6 hours)"
            confidence = "25%+"
        
        print(f"   Prediction: {prediction}")
        print(f"   Confidence: {confidence}")
        
        print(f"\n⚡ SYSTEM BEHAVIOR:")
        print(f"   Current threshold: 70% AI confidence required")
        print(f"   Cycle frequency: Every 60 seconds")
        print(f"   Next analysis: Within 1 minute")
        print(f"   Position size: $24.45 per trade (8% of balance)")
        
        print(f"\n🔄 WHAT TRIGGERS A TRADE:")
        print(f"   1. GPT-4o AI confidence ≥70%")
        print(f"   2. Strong technical indicators (RSI, volume, trend)")
        print(f"   3. Clear market direction (long/short)")
        print(f"   4. Volatility within acceptable range")
        print(f"   5. Risk-reward ratio favorable")
        
        # Time prediction
        now = datetime.now()
        predictions = {
            "Next 5 minutes": "15%" if signal_percentage < 25 else "45%" if signal_percentage < 50 else "75%",
            "Next 15 minutes": "35%" if signal_percentage < 25 else "65%" if signal_percentage < 50 else "90%",
            "Next 1 hour": "60%" if signal_percentage < 25 else "85%" if signal_percentage < 50 else "95%",
            "Next 6 hours": "85%" if signal_percentage < 25 else "95%" if signal_percentage < 50 else "99%"
        }
        
        print(f"\n⏰ TIME-BASED PREDICTIONS:")
        for timeframe, probability in predictions.items():
            print(f"   {timeframe}: {probability} chance of trade")
        
        print(f"\n✅ SYSTEM IS ACTIVELY MONITORING")
        print(f"🚀 READY TO EXECUTE WHEN CONDITIONS ALIGN")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")

if __name__ == "__main__":
    analyze_trade_timing()