#!/bin/bash
# Start Nexus Dashboard

cd /opt/nexus_dashboard

# Activate virtual environment
source venv/bin/activate

# Export environment variables
export $(cat .env | xargs)

# Install dependencies if needed
pip install flask flask-socketio eventlet psutil requests pandas python-dotenv ccxt > /dev/null 2>&1

# Start dashboard
echo "🚀 Starting Nexus Live Dashboard on port 8000..."
echo "📱 Access via: http://185.241.214.234:8000"
echo "🔄 Real-time updates every 5 seconds"

nohup python3 app.py > dashboard.log 2>&1 &

echo "✅ Dashboard started in background"
echo "📊 Process ID: $!"
echo "📝 Logs: /opt/nexus_dashboard/dashboard.log"