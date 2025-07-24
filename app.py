#!/usr/bin/env python3
"""
Flask Dashboard for Nexus Ultimate Trading Bot
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nexus-ultimate-dashboard-2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 NEXUS LIVE DASHBOARD</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <style>
        body {
            background: linear-gradient(135deg, #0c1426 0%, #1a2332 100%);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .dashboard-header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            text-align: center;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .status-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        .status-running {
            border-left: 5px solid #28a745;
        }
        .status-loading {
            border-left: 5px solid #ffc107;
        }
        .status-error {
            border-left: 5px solid #dc3545;
        }
        .balance-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #28a745;
        }
        .market-price {
            font-size: 1.2rem;
            font-weight: bold;
        }
        .price-positive {
            color: #28a745;
        }
        .price-negative {
            color: #dc3545;
        }
        .pulse {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .trading-features {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <div class="dashboard-header">
            <h1><i class="fas fa-chart-line"></i> NEXUS LIVE DASHBOARD</h1>
            <div class="badge bg-success" id="connection-status">
                <i class="fas fa-wifi"></i> Connected
            </div>
        </div>

        <div class="row">
            <!-- Bot Status -->
            <div class="col-lg-6 col-md-12">
                <div class="status-card status-loading" id="bot-status-card">
                    <h5><i class="fas fa-robot"></i> Bot Status</h5>
                    <div id="bot-status" class="h4 pulse">LOADING...</div>
                    <small id="bot-uptime">--:--:--</small>
                </div>
            </div>

            <!-- USDT Balance -->
            <div class="col-lg-6 col-md-12">
                <div class="status-card">
                    <h5><i class="fas fa-wallet"></i> USDT Balance</h5>
                    <div class="balance-value" id="usdt-balance">$0.00</div>
                    <small>Available for trading</small>
                </div>
            </div>

            <!-- Trading Features -->
            <div class="col-12">
                <div class="trading-features">
                    <h6><i class="fas fa-rocket"></i> ULTIMATE TRADING FEATURES ACTIVE</h6>
                    <div class="row text-center">
                        <div class="col-4">
                            <strong>SPOT TRADING</strong><br>
                            <small>Regular buy/sell</small>
                        </div>
                        <div class="col-4">
                            <strong>MARGIN (10x)</strong><br>
                            <small>Leveraged positions</small>
                        </div>
                        <div class="col-4">
                            <strong>FUTURES (125x)</strong><br>
                            <small>Long/Short with max leverage</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Live Market Data -->
            <div class="col-12">
                <div class="status-card">
                    <h5><i class="fas fa-chart-bar"></i> Live Market Data</h5>
                    <div class="row" id="market-data">
                        <div class="col-md-3 col-6 mb-3">
                            <div class="text-center">
                                <div class="market-price" id="btc-price">Loading...</div>
                                <small>BTC/USDT</small>
                                <div id="btc-change" class="small">---%</div>
                            </div>
                        </div>
                        <div class="col-md-3 col-6 mb-3">
                            <div class="text-center">
                                <div class="market-price" id="eth-price">Loading...</div>
                                <small>ETH/USDT</small>
                                <div id="eth-change" class="small">---%</div>
                            </div>
                        </div>
                        <div class="col-md-3 col-6 mb-3">
                            <div class="text-center">
                                <div class="market-price" id="sol-price">Loading...</div>
                                <small>SOL/USDT</small>
                                <div id="sol-change" class="small">---%</div>
                            </div>
                        </div>
                        <div class="col-md-3 col-6 mb-3">
                            <div class="text-center">
                                <div class="market-price" id="doge-price">Loading...</div>
                                <small>DOGE/USDT</small>
                                <div id="doge-change" class="small">---%</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AI Signals -->
            <div class="col-lg-6 col-md-12">
                <div class="status-card">
                    <h5><i class="fas fa-brain"></i> AI Signals</h5>
                    <div id="ai-signals">Waiting for AI analysis...</div>
                </div>
            </div>

            <!-- Live Trading Logs -->
            <div class="col-lg-6 col-md-12">
                <div class="status-card">
                    <h5><i class="fas fa-list"></i> Live Trading Logs</h5>
                    <div id="trading-logs" style="max-height: 300px; overflow-y: auto;">
                        <small class="text-muted">Monitoring trading activity...</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        
        socket.on('connect', function() {
            document.getElementById('connection-status').innerHTML = '<i class="fas fa-wifi"></i> Connected';
        });
        
        socket.on('disconnect', function() {
            document.getElementById('connection-status').innerHTML = '<i class="fas fa-wifi-slash"></i> Disconnected';
        });
        
        socket.on('dashboard_update', function(data) {
            updateDashboard(data);
        });
        
        function updateDashboard(data) {
            // Update bot status
            const botStatus = document.getElementById('bot-status');
            const botCard = document.getElementById('bot-status-card');
            
            if (data.bot_status === 'RUNNING_ULTIMATE') {
                botStatus.textContent = 'RUNNING ULTIMATE';
                botCard.className = 'status-card status-running';
                document.getElementById('bot-uptime').textContent = formatUptime(data.uptime || 0);
            } else {
                botStatus.textContent = 'LOADING...';
                botCard.className = 'status-card status-loading';
            }
            
            // Update balance
            if (data.balance) {
                document.getElementById('usdt-balance').textContent = '$' + data.balance.toFixed(2);
            }
            
            // Update market data
            if (data.market_data) {
                data.market_data.forEach(function(market) {
                    const symbol = market.pair.replace('/USDT', '').toLowerCase();
                    const priceElement = document.getElementById(symbol + '-price');
                    const changeElement = document.getElementById(symbol + '-change');
                    
                    if (priceElement) {
                        priceElement.textContent = '$' + market.price.toFixed(market.price < 1 ? 4 : 2);
                        changeElement.textContent = (market.change > 0 ? '+' : '') + market.change.toFixed(2) + '%';
                        changeElement.className = market.change >= 0 ? 'small price-positive' : 'small price-negative';
                    }
                });
            }
            
            // Update AI signals
            if (data.decisions) {
                let aiHtml = '';
                for (const [pair, decision] of Object.entries(data.decisions)) {
                    const action = decision.action.replace('_', ' ').toUpperCase();
                    const leverage = decision.leverage > 1 ? ` (${decision.leverage}x)` : '';
                    aiHtml += `<div class="mb-2">
                        <strong>${pair}:</strong> ${action}${leverage} 
                        <span class="badge bg-info">${decision.confidence}%</span>
                    </div>`;
                }
                document.getElementById('ai-signals').innerHTML = aiHtml || 'No signals available';
            }
        }
        
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        
        // Request initial data
        setInterval(function() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(error => console.error('Error:', error));
        }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def api_status():
    try:
        # Read latest log data
        log_file = '/opt/nexus-trading/latest_log.json'
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = {}
        
        # Check if bot is running
        try:
            import subprocess
            result = subprocess.run(['pgrep', '-f', 'nexus_ultimate_v6_advanced.py'], 
                                  capture_output=True, text=True)
            bot_running = len(result.stdout.strip()) > 0
        except:
            bot_running = False
        
        # Mock market data for now
        market_data = [
            {"pair": "BTC/USDT", "price": 118500.0, "change": -0.25},
            {"pair": "ETH/USDT", "price": 3665.0, "change": -0.42},
            {"pair": "SOL/USDT", "price": 197.5, "change": -0.68},
            {"pair": "DOGE/USDT", "price": 0.256, "change": -3.95}
        ]
        
        response = {
            'timestamp': datetime.now().isoformat(),
            'bot_status': 'RUNNING_ULTIMATE' if bot_running else 'STOPPED',
            'balance': log_data.get('balance', 305.57),
            'account_balances': log_data.get('account_balances', {'spot': 305.57, 'margin': 0, 'futures': 0}),
            'uptime': log_data.get('uptime', 0),
            'trades_executed': log_data.get('trades_executed', 0),
            'trading_features': 'SPOT_MARGIN_FUTURES_125X',
            'market_data': market_data,
            'decisions': log_data.get('decisions', {}),
            'system_health': 'OPERATIONAL'
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'bot_status': 'ERROR',
            'balance': 0,
            'system_health': 'ERROR'
        })

def broadcast_updates():
    """Background thread to broadcast updates"""
    while True:
        try:
            # Get status data
            with app.test_request_context():
                status_data = api_status().get_json()
            
            # Emit to all connected clients
            socketio.emit('dashboard_update', status_data)
            
        except Exception as e:
            print(f"Broadcast error: {e}")
        
        time.sleep(5)  # Update every 5 seconds

if __name__ == '__main__':
    # Start background update thread
    update_thread = threading.Thread(target=broadcast_updates, daemon=True)
    update_thread.start()
    
    # Run the app
    socketio.run(app, host='0.0.0.0', port=8000, debug=False)