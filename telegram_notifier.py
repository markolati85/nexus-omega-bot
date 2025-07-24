#!/usr/bin/env python3
"""
Telegram Notification System for Nexus AI Binance Bot
Sends notifications for bot events and trading signals
"""
import os
import requests
import json
import sqlite3
from datetime import datetime
from typing import Optional

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram chat"""
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False
    
    def send_bot_startup(self, server_ip: str):
        """Send bot startup notification"""
        message = f"""
🚀 <b>Nexus AI Binance Bot Started</b>

🌍 Server: Serbian VPS ({server_ip})
🔐 VPN: WireGuard Active
📈 Exchange: Binance
⏰ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

✅ System operational and ready for trading
        """
        self.send_message(message.strip())
    
    def send_trade_signal(self, signal_type: str, symbol: str, price: float, 
                         quantity: float, reason: str):
        """Send trading signal notification"""
        emoji = {"BUY": "📈", "SELL": "📉", "LONG": "🟢", "SHORT": "🔴"}
        
        message = f"""
{emoji.get(signal_type, '🔄')} <b>{signal_type} Signal</b>

💰 Symbol: {symbol}
💲 Price: ${price:.4f}
📊 Quantity: {quantity:.6f}
🎯 Reason: {reason}
⏰ Time: {datetime.utcnow().strftime('%H:%M:%S')} UTC
        """
        self.send_message(message.strip())
    
    def send_error_alert(self, error_type: str, details: str):
        """Send error notification"""
        message = f"""
⚠️ <b>Bot Error Alert</b>

🚨 Type: {error_type}
📝 Details: {details}
⏰ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

🔧 Auto-restart will attempt recovery
        """
        self.send_message(message.strip())
    
    def send_daily_summary(self, trades_count: int, profit_loss: float, balance: float):
        """Send daily trading summary"""
        status = "📈 Profit" if profit_loss > 0 else "📉 Loss" if profit_loss < 0 else "➖ Neutral"
        
        message = f"""
📊 <b>Daily Trading Summary</b>

🔄 Trades: {trades_count}
{status}: ${profit_loss:.2f}
💰 Balance: ${balance:.2f}
📅 Date: {datetime.utcnow().strftime('%Y-%m-%d')}

🤖 Nexus AI Bot continues monitoring...
        """
        self.send_message(message.strip())

def load_telegram_config():
    """Load Telegram configuration from environment"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Warning: Telegram configuration not found")
        return None
    
    return TelegramNotifier(bot_token, chat_id)

def test_telegram_connection():
    """Test Telegram notification system"""
    notifier = load_telegram_config()
    if notifier:
        success = notifier.send_message("🧪 Test message from Nexus Bot")
        print(f"Telegram test: {'✅ Success' if success else '❌ Failed'}")
        return success
    return False

if __name__ == "__main__":
    # Test the notification system
    test_telegram_connection()