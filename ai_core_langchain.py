#!/usr/bin/env python3
"""
AI Core with LangChain - GPT-4o powered trading decisions
Advanced AI decision making using OpenAI GPT-4o
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

load_dotenv()

class AICore:
    def __init__(self):
        """Initialize AI Core with GPT-4o"""
        self.client = None
        self.setup_openai()
    
    def setup_openai(self):
        """Setup OpenAI GPT-4o client"""
        if not OPENAI_AVAILABLE:
            logging.warning("OpenAI not available - AI decisions disabled")
            return False
        
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
        """
        Get AI trading decision using GPT-4o
        
        Args:
            pair_data (dict): Market data including price, RSI, trend, volatility
            
        Returns:
            dict: Trading decision with direction, leverage, strategy
        """
        
        if not self.client:
            return self._fallback_decision(pair_data)
        
        try:
            prompt = self._create_trading_prompt(pair_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert cryptocurrency trading AI. Analyze market data and provide precise trading decisions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            ai_response = response.choices[0].message.content.strip()
            logging.info(f"GPT-4o AI Response: {ai_response}")
            
            # Parse AI decision
            decision = json.loads(ai_response)
            
            # Validate and format response
            return self._validate_decision(decision, pair_data)
            
        except Exception as e:
            logging.error(f"AI decision error: {e}")
            return self._fallback_decision(pair_data)
    
    def _create_trading_prompt(self, pair_data: Dict[str, Any]) -> str:
        """Create detailed trading prompt for GPT-4o"""
        
        pair = pair_data.get('pair', 'Unknown')
        price = pair_data.get('price', 0)
        rsi = pair_data.get('rsi', 50)
        trend = pair_data.get('trend_strength', 0)
        volatility = pair_data.get('volatility', 0)
        volume_ratio = pair_data.get('volume_ratio', 1)
        price_change_24h = pair_data.get('price_change_24h', 0)
        
        prompt = f"""
CRYPTOCURRENCY TRADING ANALYSIS FOR {pair}

MARKET DATA:
- Current Price: ${price:.4f}
- 24h Change: {price_change_24h:+.2f}%
- RSI: {rsi:.1f}
- Trend Strength: {trend:.3f}
- Volatility: {volatility:.2f}%
- Volume Ratio: {volume_ratio:.2f}x

TRADING DECISION REQUIRED:
Analyze this data and determine the optimal trading action.

Consider:
1. Market momentum and trend direction
2. Technical indicators (RSI, volume, volatility)
3. Risk-reward ratio
4. Optimal leverage based on market conditions
5. Best strategy for current market state

Respond with ONLY valid JSON in this exact format:
{{
    "direction": "long" or "short" or "hold",
    "leverage": 1-125,
    "strategy": "trend" or "breakout" or "meanreversion" or "grid",
    "confidence": 0-100,
    "reasoning": "brief explanation of decision",
    "stop_loss_pct": 0.5-3.0,
    "take_profit_pct": 1.0-8.0
}}

Base leverage recommendations:
- BTC/ETH: 10-25x
- Major alts: 25-50x  
- High volatility coins: 50-125x
"""
        
        return prompt
    
    def _validate_decision(self, decision: Dict[str, Any], pair_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize AI decision"""
        
        # Default safe values
        validated = {
            "direction": decision.get("direction", "hold").lower(),
            "leverage": max(1, min(125, decision.get("leverage", 10))),
            "strategy": decision.get("strategy", "trend").lower(),
            "confidence": max(0, min(100, decision.get("confidence", 50))),
            "reasoning": decision.get("reasoning", "AI analysis complete"),
            "stop_loss_pct": max(0.5, min(3.0, decision.get("stop_loss_pct", 2.0))),
            "take_profit_pct": max(1.0, min(8.0, decision.get("take_profit_pct", 4.0)))
        }
        
        # Validate direction
        if validated["direction"] not in ["long", "short", "hold"]:
            validated["direction"] = "hold"
        
        # Validate strategy
        if validated["strategy"] not in ["trend", "breakout", "meanreversion", "grid"]:
            validated["strategy"] = "trend"
        
        return validated
    
    def _fallback_decision(self, pair_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback decision when AI is unavailable"""
        
        rsi = pair_data.get('rsi', 50)
        trend_strength = pair_data.get('trend_strength', 0)
        volatility = pair_data.get('volatility', 0)
        
        # Simple technical analysis fallback
        if rsi < 30 and trend_strength > 0:
            direction = "long"
            confidence = 70
        elif rsi > 70 and trend_strength < 0:
            direction = "short"
            confidence = 70
        else:
            direction = "hold"
            confidence = 50
        
        return {
            "direction": direction,
            "leverage": 10,
            "strategy": "trend",
            "confidence": confidence,
            "reasoning": "Technical analysis fallback",
            "stop_loss_pct": 2.0,
            "take_profit_pct": 4.0
        }

# Global AI instance
ai_core = AICore()

def get_trade_decision(pair_data: Dict[str, Any]) -> Dict[str, Any]:
    """Global function for getting trade decisions"""
    return ai_core.get_trade_decision(pair_data)