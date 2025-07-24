"""
Telegram Alert System for Nexus Trading Bot
Sends comprehensive trading notifications to user
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Optional


class TelegramAlertsSystem:
    def __init__(self):
        self.bot_token = "7642777600:AAGfC6vB0Zslp4ksEnAq0DI3g1lYz2BS5sY"
        self.user_id = "1762317382"  # User ID: @AAA99918
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send message to user via Telegram
        """
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.user_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"Telegram send failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
    
    def send_trade_opened_alert(self, trade_data: Dict) -> bool:
        """
        Alert when trade is opened
        """
        symbol = trade_data.get('symbol', 'N/A')
        action = trade_data.get('action', 'N/A')
        leverage = trade_data.get('leverage', 1)
        amount = trade_data.get('amount', 0)
        confidence = trade_data.get('confidence', 0)
        order_id = trade_data.get('order_id', 'N/A')
        
        message = f"""
🚀 <b>TRADE OPENED</b>

📊 <b>Trade Details:</b>
• Pair: {symbol}
• Action: <b>{action}</b>
• Leverage: <b>{leverage}x</b>
• Position Size: ${amount:.2f} USDT
• Order ID: {order_id}

🧠 <b>AI Analysis:</b>
• Confidence: <b>{confidence}%</b>
• Strategy: GPT-4o High Leverage
• Risk Level: {self._get_risk_level(leverage)}

⏰ Time: {datetime.now().strftime('%H:%M:%S UTC')}
"""
        
        return self.send_message(message)
    
    def send_trade_closed_alert(self, trade_data: Dict, pnl: float, duration: str) -> bool:
        """
        Alert when trade is closed
        """
        symbol = trade_data.get('symbol', 'N/A')
        action = trade_data.get('action', 'N/A')
        leverage = trade_data.get('leverage', 1)
        
        pnl_emoji = "💰" if pnl > 0 else "📉" if pnl < 0 else "⚪"
        pnl_status = "PROFIT" if pnl > 0 else "LOSS" if pnl < 0 else "BREAK-EVEN"
        
        message = f"""
🏁 <b>TRADE CLOSED</b>

📊 <b>Trade Summary:</b>
• Pair: {symbol}
• Action: {action}
• Leverage: {leverage}x
• Duration: {duration}

{pnl_emoji} <b>Result:</b>
• PnL: <b>${pnl:.2f} USDT</b>
• Status: <b>{pnl_status}</b>

⏰ Closed: {datetime.now().strftime('%H:%M:%S UTC')}
"""
        
        return self.send_message(message)
    
    def send_trade_skipped_alert(self, symbol: str, reason: str, confidence: int, market_data: Dict) -> bool:
        """
        Alert when trade is skipped
        """
        price = market_data.get('price', 0)
        change_24h = market_data.get('change_24h', 0)
        volatility = market_data.get('volatility', 0)
        
        message = f"""
⏸️ <b>TRADE SKIPPED</b>

📊 <b>Market Analysis:</b>
• Pair: {symbol}
• Price: ${price:.2f}
• 24h Change: {change_24h:.2f}%
• Volatility: {volatility:.1f}%

🤖 <b>AI Decision:</b>
• Confidence: <b>{confidence}%</b>
• Reason: {reason}
• Threshold: 70% required

⏰ Time: {datetime.now().strftime('%H:%M:%S UTC')}
"""
        
        return self.send_message(message)
    
    def send_balance_mismatch_alert(self, reported: float, actual: float) -> bool:
        """
        Alert when balance calculation doesn't match expected
        """
        variance = abs(reported - actual)
        variance_percent = variance / actual * 100
        
        message = f"""
🟨 <b>BALANCE MISMATCH WARNING</b>

💰 <b>Balance Discrepancy:</b>
• System Reported: <b>${reported:.2f} USDT</b>
• Expected (OKX App): <b>${actual:.2f} USDT</b>
• Variance: <b>{variance_percent:.1f}%</b>

🔧 <b>Action:</b>
Balance calculation system is being recalibrated.
Trading continues with corrected values.

⏰ Alert: {datetime.now().strftime('%H:%M:%S UTC')}
"""
        
        return self.send_message(message)
    
    def send_gpt4o_strategy_alert(self, analysis: Dict) -> bool:
        """
        Send GPT-4o strategy reasoning dump
        """
        confidence = analysis.get('confidence', 0)
        action = analysis.get('action', 'HOLD')
        reasoning = analysis.get('reasoning', 'No reasoning provided')[:200]  # Limit length
        
        message = f"""
🧠 <b>GPT-4O STRATEGY ANALYSIS</b>

🎯 <b>Decision:</b>
• Action: <b>{action}</b>
• Confidence: <b>{confidence}%</b>

📝 <b>AI Reasoning:</b>
{reasoning}...

🔄 Next analysis in 90 seconds

⏰ Time: {datetime.now().strftime('%H:%M:%S UTC')}
"""
        
        return self.send_message(message)
    
    def send_system_status_alert(self, status: str, details: str = "") -> bool:
        """
        Send system status updates
        """
        status_emoji = {
            'ONLINE': '🟢',
            'OFFLINE': '🔴', 
            'WARNING': '🟡',
            'ERROR': '🚨'
        }.get(status, '⚪')
        
        message = f"""
{status_emoji} <b>SYSTEM STATUS: {status}</b>

📊 <b>Nexus High Leverage Bot</b>
• Status: <b>{status}</b>
• Portfolio: ~$292.96 USDT
• Leverage: 1x-50x adaptive

{details}

⏰ Status: {datetime.now().strftime('%H:%M:%S UTC')}
"""
        
        return self.send_message(message)
    
    def _get_risk_level(self, leverage: int) -> str:
        """
        Get risk level based on leverage
        """
        if leverage <= 3:
            return "Low Risk"
        elif leverage <= 10:
            return "Medium Risk"
        elif leverage <= 25:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def test_connection(self) -> bool:
        """
        Test Telegram bot connection
        """
        test_message = """
🔧 <b>NEXUS BOT TEST</b>

✅ Telegram integration successful!

System online. Awaiting high-confidence opportunity.

Bot: @Nexusomega_bot
User: M L (@AAA99918)
"""
        
        return self.send_message(test_message)


# Global instance
telegram_alerts = TelegramAlertsSystem()


def send_trade_opened(trade_data: Dict) -> bool:
    """Convenient function to send trade opened alert"""
    return telegram_alerts.send_trade_opened_alert(trade_data)


def send_trade_closed(trade_data: Dict, pnl: float, duration: str) -> bool:
    """Convenient function to send trade closed alert"""
    return telegram_alerts.send_trade_closed_alert(trade_data, pnl, duration)


def send_trade_skipped(symbol: str, reason: str, confidence: int, market_data: Dict) -> bool:
    """Convenient function to send trade skipped alert"""
    return telegram_alerts.send_trade_skipped_alert(symbol, reason, confidence, market_data)


def send_balance_mismatch(reported: float, actual: float = 292.96) -> bool:
    """Convenient function to send balance mismatch alert"""
    return telegram_alerts.send_balance_mismatch_alert(reported, actual)


def send_system_status(status: str, details: str = "") -> bool:
    """Convenient function to send system status"""
    return telegram_alerts.send_system_status_alert(status, details)


if __name__ == "__main__":
    # Test the Telegram integration
    print("🔧 Testing Telegram integration...")
    
    success = telegram_alerts.test_connection()
    
    if success:
        print("✅ Telegram integration working!")
    else:
        print("❌ Telegram integration failed!")