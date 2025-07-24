# Clean Flask application for Serbian Binance deployment
from flask import Flask, render_template_string
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "nexus-clean-deployment-2025")

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nexus AI Binance Bot - Serbian Deployment</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 20px; background: #2d2d2d; border-radius: 8px; margin: 20px 0; }
            .success { border-left: 4px solid #4CAF50; }
            .info { border-left: 4px solid #2196F3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Nexus AI Binance Bot</h1>
            <div class="status success">
                <h3>✅ Clean Environment Deployed</h3>
                <p>All old OKX/MEXC systems removed. Ready for Serbian Binance deployment.</p>
            </div>
            <div class="status info">
                <h3>📊 Deployment Status</h3>
                <ul>
                    <li>Enhanced Nexus Binance Bot: Ready</li>
                    <li>Telegram Notifications: Configured</li>
                    <li>Web Dashboard: Available on port 8080</li>
                    <li>Automation Scripts: Prepared</li>
                </ul>
            </div>
            <div class="status info">
                <h3>🚀 Next Steps</h3>
                <p>Upload files to Serbian server (185.241.214.234) and run automation setup.</p>
            </div>
        </div>
    </body>
    </html>
    ''')