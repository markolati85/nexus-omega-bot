#!/usr/bin/env python3
"""
Nexus Binance German VPN Activated Edition
Automatically activates trading when German VPN is detected
"""

import os
import time
import logging
import requests
import subprocess
from binance.client import Client
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_german_activated.log'),
        logging.StreamHandler()
    ]
)

class NexusBinanceGermanActivated:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.german_ip = "91.99.238.81"
        self.vpn_proxies = {
            'http': 'socks5://127.0.0.1:8080',
            'https': 'socks5://127.0.0.1:8080'
        }
        self.trading_active = False
        
    def check_german_vpn(self):
        """Check if German VPN is active and working"""
        try:
            # Test current IP via VPN proxy
            response = requests.get(
                'https://httpbin.org/ip', 
                proxies=self.vpn_proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                current_ip = response.json().get('origin')
                
                if current_ip == self.german_ip:
                    self.logger.info(f"✅ German VPN active! IP: {current_ip}")
                    return True
                else:
                    self.logger.info(f"⚠️ VPN active but wrong IP: {current_ip}")
                    return False
            else:
                return False
                
        except Exception as e:
            self.logger.debug(f"VPN check failed: {e}")
            return False
    
    def test_binance_via_german_vpn(self):
        """Test Binance connection via German VPN"""
        try:
            self.logger.info("🧪 Testing Binance via German VPN...")
            
            # Create client with German VPN proxy
            client = Client(
                os.getenv('BINANCE_API_KEY'),
                os.getenv('BINANCE_API_SECRET'),
                requests_params={
                    'proxies': self.vpn_proxies,
                    'timeout': 30
                }
            )
            
            # Test server time
            server_time = client.get_server_time()
            self.logger.info("✅ Server time sync via VPN successful")
            
            # Test account access
            account = client.get_account()
            
            permissions = account.get('permissions', [])
            can_trade = account.get('canTrade', False)
            
            # Show account details
            balances = account.get('balances', [])
            active_balances = [b for b in balances if float(b['free']) > 0 or float(b['locked']) > 0]
            
            self.logger.info("🎉 BINANCE ACCESS VIA GERMAN VPN SUCCESSFUL!")
            self.logger.info(f"🔐 Permissions: {permissions}")
            self.logger.info(f"🎯 Trading enabled: {can_trade}")
            self.logger.info(f"💰 Active assets: {len(active_balances)}")
            
            if active_balances:
                self.logger.info("💼 PORTFOLIO:")
                for balance in active_balances[:8]:
                    asset = balance['asset']
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    total = free + locked
                    if total > 0:
                        self.logger.info(f"   {asset}: {total:.8f}")
            
            if can_trade:
                self.logger.info("🚀 READY FOR LIVE TRADING!")
                return True
            else:
                self.logger.info("⚠️ Connected but trading permissions needed")
                return False
                
        except Exception as e:
            error_str = str(e)
            if '-2015' in error_str:
                self.logger.error("❌ Still blocked even via German VPN")
            else:
                self.logger.error(f"❌ VPN connection error: {e}")
            return False
    
    def activate_vpn_tunnel(self):
        """Attempt to activate German VPN tunnel"""
        try:
            self.logger.info("🔄 Attempting to activate German VPN tunnel...")
            
            # Run the VPN connection script
            result = subprocess.run(
                ['./connect_german_vpn.sh'],
                cwd='/opt/nexus-trading',
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.logger.info("✅ VPN tunnel activation successful")
                return True
            else:
                self.logger.info("❌ VPN tunnel activation failed")
                self.logger.info("💡 Ensure SSH key is added to German server")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ VPN activation error: {e}")
            return False
    
    def monitor_and_activate(self):
        """Main monitoring loop with automatic VPN activation"""
        self.logger.info("🚀 Nexus Binance German VPN Auto-Activation")
        self.logger.info(f"🇩🇪 Target: {self.german_ip}")
        
        cycle = 1
        vpn_attempts = 0
        max_vpn_attempts = 3
        
        while True:
            try:
                self.logger.info(f"🔄 Activation Cycle #{cycle}")
                
                # Check if German VPN is already active
                if self.check_german_vpn():
                    # Test Binance with VPN
                    if self.test_binance_via_german_vpn():
                        self.logger.info("🎯 BINANCE TRADING ACTIVATED VIA GERMAN VPN!")
                        self.trading_active = True
                        break
                    else:
                        self.logger.info("⚠️ VPN active but Binance access failed")
                
                elif vpn_attempts < max_vpn_attempts:
                    # Attempt to activate VPN tunnel
                    self.logger.info(f"🔄 VPN activation attempt {vpn_attempts + 1}/{max_vpn_attempts}")
                    
                    if self.activate_vpn_tunnel():
                        self.logger.info("✅ VPN tunnel activated - testing Binance...")
                        vpn_attempts = 0  # Reset on success
                        continue
                    else:
                        vpn_attempts += 1
                        self.logger.info(f"❌ VPN attempt {vpn_attempts} failed")
                
                else:
                    self.logger.info("💡 Manual VPN setup required")
                    self.logger.info("🔑 Ensure SSH public key is added to German server")
                    self.logger.info("🔄 Monitoring for VPN activation...")
                
                cycle += 1
                time.sleep(120)  # Check every 2 minutes
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Activation monitor stopped")
                break
            except Exception as e:
                self.logger.error(f"❌ Monitor error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = NexusBinanceGermanActivated()
    bot.monitor_and_activate()
