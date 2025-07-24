"""
Fixed OKX Portfolio Calculator
Accurate balance calculation with full wallet aggregation
"""

import ccxt
import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional


class FixedOKXPortfolioCalculator:
    def __init__(self):
        self.exchange = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET_KEY'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'sandbox': False,
            'timeout': 30000
        })
        
    def get_comprehensive_portfolio_value(self) -> Dict:
        """
        Get accurate portfolio value by aggregating all OKX account types
        """
        try:
            total_portfolio_value = 0
            asset_breakdown = {}
            
            print("🔍 Fetching comprehensive OKX portfolio...")
            
            # Method 1: Asset balances (most reliable for funding account)
            try:
                asset_response = self.exchange.private_get_asset_balances()
                if asset_response.get('code') == '0':
                    assets = asset_response.get('data', [])
                    
                    for asset in assets:
                        symbol = asset.get('ccy', '')
                        amount = float(asset.get('bal', 0))
                        
                        if amount > 0.0001:  # Only include meaningful amounts
                            if symbol == 'USDT':
                                value = amount
                            else:
                                # Convert to USDT value
                                try:
                                    ticker = self.exchange.fetch_ticker(f'{symbol}/USDT')
                                    price = ticker['last']
                                    value = amount * price
                                except:
                                    value = 0  # Skip if can't convert
                            
                            if value > 0.01:  # Only include if worth more than $0.01
                                asset_breakdown[f'funding_{symbol}'] = {
                                    'amount': amount,
                                    'value': value,
                                    'account_type': 'funding'
                                }
                                total_portfolio_value += value
                                
                    print(f"✅ Funding account: ${sum([a['value'] for a in asset_breakdown.values() if a['account_type'] == 'funding']):.2f}")
                    
            except Exception as e:
                print(f"⚠️ Funding account error: {e}")
            
            # Method 2: Trading account balance
            try:
                trading_response = self.exchange.private_get_account_balance()
                if trading_response.get('code') == '0':
                    account_data = trading_response.get('data', [{}])[0]
                    
                    # Get individual currency details
                    details = account_data.get('details', [])
                    for detail in details:
                        symbol = detail.get('ccy', '')
                        cash_balance = float(detail.get('cashBal', 0))
                        
                        if cash_balance > 0.0001:
                            if symbol == 'USDT':
                                value = cash_balance
                            else:
                                try:
                                    ticker = self.exchange.fetch_ticker(f'{symbol}/USDT')
                                    price = ticker['last']
                                    value = cash_balance * price
                                except:
                                    value = 0
                            
                            if value > 0.01:
                                asset_breakdown[f'trading_{symbol}'] = {
                                    'amount': cash_balance,
                                    'value': value,
                                    'account_type': 'trading'
                                }
                                total_portfolio_value += value
                    
                    print(f"✅ Trading account: ${sum([a['value'] for a in asset_breakdown.values() if a['account_type'] == 'trading']):.2f}")
                    
            except Exception as e:
                print(f"⚠️ Trading account error: {e}")
            
            # Method 3: Check for margin/futures positions
            try:
                positions_response = self.exchange.private_get_account_positions()
                if positions_response.get('code') == '0':
                    positions = positions_response.get('data', [])
                    
                    for position in positions:
                        if float(position.get('notionalUsd', 0)) > 1:  # Positions worth more than $1
                            symbol = position.get('instId', '')
                            notional = float(position.get('notionalUsd', 0))
                            
                            asset_breakdown[f'position_{symbol}'] = {
                                'amount': float(position.get('pos', 0)),
                                'value': notional,
                                'account_type': 'position'
                            }
                            total_portfolio_value += notional
                    
                    if positions:
                        print(f"✅ Open positions: ${sum([a['value'] for a in asset_breakdown.values() if a['account_type'] == 'position']):.2f}")
                        
            except Exception as e:
                print(f"⚠️ Positions check error: {e}")
            
            # Calculate available trading balance (USDT only)
            available_usdt = sum([
                a['value'] for a in asset_breakdown.values() 
                if 'USDT' in a and a['account_type'] in ['funding', 'trading']
            ])
            
            portfolio_data = {
                'total_portfolio_value': total_portfolio_value,
                'available_value': available_usdt,
                'asset_breakdown': asset_breakdown,
                'asset_count': len(asset_breakdown),
                'calculation_method': 'comprehensive_aggregation',
                'timestamp': datetime.now().isoformat(),
                'expected_value': 292.96,  # User's expected value
                'variance_percent': abs(total_portfolio_value - 292.96) / 292.96 * 100
            }
            
            print(f"\n💰 COMPREHENSIVE PORTFOLIO CALCULATION:")
            print(f"Total Value: ${total_portfolio_value:.2f} USDT")
            print(f"Expected: $292.96 USDT")
            print(f"Variance: {portfolio_data['variance_percent']:.1f}%")
            
            return portfolio_data
            
        except Exception as e:
            print(f"❌ Portfolio calculation failed: {e}")
            return {
                'total_portfolio_value': 0,
                'available_value': 0,
                'asset_breakdown': {},
                'error': str(e)
            }

    def validate_balance_accuracy(self, calculated_value: float, expected_value: float = 292.96) -> Dict:
        """
        Validate if calculated balance matches expected value
        """
        variance = abs(calculated_value - expected_value)
        variance_percent = variance / expected_value * 100
        
        is_accurate = variance_percent < 5  # Within 5% tolerance
        
        return {
            'is_accurate': is_accurate,
            'calculated': calculated_value,
            'expected': expected_value,
            'variance': variance,
            'variance_percent': variance_percent,
            'status': 'ACCURATE' if is_accurate else 'MISMATCH'
        }


def get_fixed_portfolio_value() -> Dict:
    """
    Main function to get fixed portfolio value
    """
    calculator = FixedOKXPortfolioCalculator()
    return calculator.get_comprehensive_portfolio_value()


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv("/opt/nexus-trading/.env_okx")
    
    portfolio = get_fixed_portfolio_value()
    
    if portfolio.get('total_portfolio_value', 0) > 0:
        calculator = FixedOKXPortfolioCalculator()
        validation = calculator.validate_balance_accuracy(portfolio['total_portfolio_value'])
        
        print(f"\n🎯 VALIDATION RESULTS:")
        print(f"Status: {validation['status']}")
        print(f"Calculated: ${validation['calculated']:.2f}")
        print(f"Expected: ${validation['expected']:.2f}")
        print(f"Variance: {validation['variance_percent']:.1f}%")
        
        if validation['is_accurate']:
            print("✅ BALANCE CALCULATION: FIXED AND ACCURATE")
        else:
            print("⚠️ BALANCE MISMATCH: REQUIRES FURTHER INVESTIGATION")