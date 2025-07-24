#!/bin/bash

# Simple Serbian Server Setup Script
echo "Setting up Serbian server environment..."

# Step 1: Create directory and setup Python
ssh -o StrictHostKeyChecking=no root@185.241.214.234 << 'EOF'
    mkdir -p /opt/nexus-trading
    cd /opt/nexus-trading
    
    # Install dependencies
    apt update
    apt install -y python3 python3-pip python3-venv git
    
    # Create virtual environment
    python3 -m venv nexus_env
    source nexus_env/bin/activate
    
    # Install Python packages
    pip install ccxt pandas numpy requests openai python-dotenv flask sqlalchemy
    
    echo "Environment setup complete"
EOF

echo "Server environment ready!"