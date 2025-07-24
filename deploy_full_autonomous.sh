#!/bin/bash

echo "🚀 DEPLOYING NEXUS AUTONOMOUS DEVOPS SYSTEM"
echo "=============================================="

# Kill any existing bot processes
echo "Stopping existing processes..."
pkill -f python.*nexus 2>/dev/null || true
pkill -f python.*bot 2>/dev/null || true
sleep 3

# Set up environment
echo "Setting up environment..."
export OPENAI_API_KEY="sk-proj-f8xANGmWZYdbtm6ZGhtOT3BlbkFJG4kOMhYW5CsArCQ1qPZ8"

# Create logs directory
mkdir -p /opt/nexus-trading/logs

# Navigate to working directory
cd /opt/nexus-trading

# Activate virtual environment
source nexus_env/bin/activate

echo "Starting Nexus Autonomous DevOps System..."
echo "Features:"
echo "• 12-pair monitoring (BTC, ETH, SOL, BNB, XRP, DOGE, APT, OP, AVAX, MATIC, ARB, LTC)"
echo "• GPT-4o autonomous decision making"
echo "• Telegram remote control interface"
echo "• Self-repair and diagnostics"
echo "• Live trading execution"
echo ""

# Start the autonomous system
nohup python3 nexus_autonomous_devops.py > logs/autonomous_devops.log 2>&1 &
DEVOPS_PID=$!

# Save PID
echo $DEVOPS_PID > logs/devops_pid.txt

echo "Autonomous DevOps system started with PID: $DEVOPS_PID"

# Wait and verify
sleep 8

if ps -p $DEVOPS_PID > /dev/null; then
    echo "✅ DEPLOYMENT SUCCESSFUL"
    echo ""
    echo "System Status:"
    echo "• PID: $DEVOPS_PID"
    echo "• Log: logs/autonomous_devops.log"
    echo "• 12-pair monitoring: ACTIVE"
    echo "• Telegram control: READY"
    echo ""
    echo "Telegram Commands Available:"
    echo "/status - System health check"
    echo "/restart - Restart entire system"
    echo "/logs - View recent activity"
    echo "/tradeconf 75 - Set confidence threshold"
    echo "/leverage 20 - Set trading leverage"
    echo "/repair - Run self-diagnostics"
    echo ""
    echo "Log preview:"
    tail -5 logs/autonomous_devops.log
else
    echo "❌ DEPLOYMENT FAILED"
    echo "Check logs:"
    cat logs/autonomous_devops.log
fi

echo ""
echo "Deployment complete. Check Telegram for startup confirmation."