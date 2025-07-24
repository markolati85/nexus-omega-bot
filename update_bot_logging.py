#!/usr/bin/env python3
"""
Update trading bot to output latest_log.json for dashboard
"""

import os
import json
from datetime import datetime

def add_logging_to_bot():
    """Add dashboard logging to the trading bot"""
    
    log_update_code = '''
    # Dashboard logging update
    def update_dashboard_log(self, cycle_data):
        """Update dashboard log file"""
        try:
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'cycle': cycle_data.get('cycle', 0),
                'balance': cycle_data.get('balance', 0),
                'ai_confidence': cycle_data.get('ai_confidence', 0),
                'market_analysis': cycle_data.get('market_analysis', {}),
                'trade_signals': cycle_data.get('trade_signals', []),
                'bot_status': 'RUNNING',
                'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0
            }
            
            with open('/opt/nexus-trading/latest_log.json', 'w') as f:
                json.dump(dashboard_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Dashboard log update error: {e}")
    '''
    
    print("📝 Dashboard logging code prepared")
    print("🔧 This should be integrated into the main trading bot")
    print("📊 Will output to: /opt/nexus-trading/latest_log.json")

if __name__ == "__main__":
    add_logging_to_bot()