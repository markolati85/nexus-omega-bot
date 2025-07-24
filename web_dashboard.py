#!/usr/bin/env python3
"""
Nexus Live Dashboard - Real-time monitoring system
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import json
import os
import time
import threading
from datetime import datetime
import psutil
from dotenv import load_dotenv

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nexus_dashboard_secret_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

class DashboardMonitor:
    def __init__(self):
        self.latest_data = {
            'balance': {},
            'positions': [],
            'trades': [],
            'bot_status': 'Unknown',
            'market_data': [],
            'ai_signals': {},
            'system_stats': {}
        }
        
    def get_balance(self):
        """Get current OKX balance"""
        if not CCXT_AVAILABLE:
            return {'error': 'CCXT not available'}
            
        try:
            exchange = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'sandbox': False,
                'enableRateLimit': True
            })
            
            balance = exchange.fetch_balance()
            
            # Format balance data
            formatted_balance = {}
            for currency, data in balance.items():
                if currency not in ['info', 'free', 'used', 'total'] and data['total'] > 0:
                    formatted_balance[currency] = {
                        'free': data['free'],
                        'used': data['used'],
                        'total': data['total']
                    }
            
            return formatted_balance
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_market_data(self):
        """Get current market data for key pairs"""
        if not CCXT_AVAILABLE:
            return []
            
        pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOGE/USDT', 'LINK/USDT']
        market_data = []
        
        try:
            exchange = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'sandbox': False,
                'enableRateLimit': True
            })
            
            for pair in pairs:
                try:
                    ticker = exchange.fetch_ticker(pair)
                    market_data.append({
                        'pair': pair,
                        'price': ticker['last'],
                        'change': ticker['percentage'],
                        'volume': ticker['quoteVolume']
                    })
                except:
                    continue
                    
        except Exception as e:
            pass
            
        return market_data
    
    def get_bot_status(self):
        """Check if trading bot is running"""
        try:
            # Check for nexus processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'nexus_ultimate_v6_advanced.py' in ' '.join(proc.info['cmdline'] or []):
                        return {
                            'status': 'RUNNING',
                            'pid': proc.info['pid'],
                            'uptime': time.time() - proc.create_time()
                        }
                except:
                    continue
            
            return {'status': 'STOPPED', 'pid': None, 'uptime': 0}
            
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}
    
    def get_latest_log(self):
        """Read latest bot log data"""
        try:
            log_file = '/opt/nexus-trading/latest_log.json'
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    return json.load(f)
            else:
                return {'error': 'Log file not found'}
        except Exception as e:
            return {'error': str(e)}
    
    def update_dashboard_data(self):
        """Update all dashboard data"""
        self.latest_data.update({
            'balance': self.get_balance(),
            'market_data': self.get_market_data(),
            'bot_status': self.get_bot_status(),
            'log_data': self.get_latest_log(),
            'timestamp': datetime.now().isoformat()
        })

monitor = DashboardMonitor()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for dashboard data"""
    monitor.update_dashboard_data()
    return jsonify(monitor.latest_data)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status', 'Connected to Nexus Dashboard')

@socketio.on('request_update')
def handle_update_request():
    """Handle update request from client"""
    monitor.update_dashboard_data()
    emit('dashboard_update', monitor.latest_data)

def background_updates():
    """Background thread for real-time updates"""
    while True:
        monitor.update_dashboard_data()
        socketio.emit('dashboard_update', monitor.latest_data)
        time.sleep(5)  # Update every 5 seconds

if __name__ == '__main__':
    # Start background update thread
    update_thread = threading.Thread(target=background_updates)
    update_thread.daemon = True
    update_thread.start()
    
    print("🚀 Nexus Dashboard starting on port 8000...")
    socketio.run(app, host='0.0.0.0', port=8000, debug=False)