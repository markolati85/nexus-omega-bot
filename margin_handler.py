#!/usr/bin/env python3
"""
Margin Handler - OKX Margin Trading Implementation  
Handles margin positions with leverage up to 10x
"""

import logging
from typing import Dict, Any, Optional

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

class MarginHandler:
    def __init__(self, exchange_client):
        """Initialize margin handler with OKX client"""
        self.client = exchange_client
        self.active_positions = {}
        
        if self.client:
            logging.info("Margin handler initialized")
    
    def open_margin_position(self, pair: str, direction: str, leverage: int, qty: float) -> Dict[str, Any]:
        """
        Open margin position with leverage
        
        Args:
            pair (str): Trading pair (e.g., 'BTC/USDT')
            direction (str): 'long' or 'short'  
            leverage (int): Leverage multiplier (1-10 for margin)
            qty (float): Position size in base currency
            
        Returns:
            dict: Order result with success status
        """
        
        if not self.client:
            logging.error("No exchange client available")
            return {"success": False, "error": "No client"}
        
        try:
            # Switch to margin mode
            original_type = self.client.options.get('defaultType', 'spot')
            self.client.options['defaultType'] = 'margin'
            
            # Set leverage for margin trading
            leverage = min(leverage, 10)  # OKX margin max leverage is 10x
            
            # Determine order side
            side = 'buy' if direction == 'long' else 'sell'
            
            # Create margin order
            order = self.client.create_market_order(
                symbol=pair,
                type='market',
                side=side,
                amount=qty,
                params={
                    'marginMode': 'isolated',
                    'lever': leverage
                }
            )
            
            # Restore original type
            self.client.options['defaultType'] = original_type
            
            if order and order.get('id'):
                self.active_positions[pair] = {
                    'order_id': order['id'],
                    'direction': direction,
                    'leverage': leverage,
                    'quantity': qty,
                    'entry_price': order.get('average', 0),
                    'timestamp': order.get('timestamp')
                }
                
                logging.info(f"✅ Margin {direction.upper()} opened: {qty:.6f} {pair} at {leverage}x leverage")
                logging.info(f"Order ID: {order['id']}")
                
                return {
                    "success": True,
                    "order_id": order['id'],
                    "direction": direction,
                    "leverage": leverage,
                    "quantity": qty,
                    "entry_price": order.get('average', 0)
                }
            else:
                logging.error("Failed to create margin order - no order ID")
                return {"success": False, "error": "Order creation failed"}
                
        except ccxt.InsufficientFunds as e:
            logging.error(f"Insufficient funds for margin position: {e}")
            return {"success": False, "error": "Insufficient funds"}
        except ccxt.InvalidOrder as e:
            logging.error(f"Invalid margin order: {e}")
            return {"success": False, "error": f"Invalid order: {e}"}
        except Exception as e:
            logging.error(f"Margin position error: {e}")
            return {"success": False, "error": str(e)}
    
    def close_margin_position(self, pair: str) -> Dict[str, Any]:
        """
        Close existing margin position
        
        Args:
            pair (str): Trading pair
            
        Returns:
            dict: Close result with success status
        """
        
        if pair not in self.active_positions:
            logging.warning(f"No active margin position for {pair}")
            return {"success": False, "error": "No active position"}
        
        try:
            position_info = self.active_positions[pair]
            
            # Switch to margin mode
            original_type = self.client.options.get('defaultType', 'spot')
            self.client.options['defaultType'] = 'margin'
            
            # Get current margin balance for the pair
            balance = self.client.fetch_balance({'type': 'margin'})
            base_asset = pair.split('/')[0]
            
            if base_asset in balance and balance[base_asset]['used'] > 0:
                # Close position by selling/buying back
                side = 'sell' if position_info['direction'] == 'long' else 'buy'
                quantity = balance[base_asset]['used']
                
                close_order = self.client.create_market_order(
                    symbol=pair,
                    type='market',
                    side=side,
                    amount=quantity,
                    params={'marginMode': 'isolated'}
                )
                
                # Restore original type
                self.client.options['defaultType'] = original_type
                
                if close_order and close_order.get('id'):
                    # Calculate PnL
                    entry_price = position_info.get('entry_price', 0)
                    exit_price = close_order.get('average', 0)
                    pnl = self._calculate_margin_pnl(position_info['direction'], entry_price, exit_price, quantity)
                    
                    logging.info(f"✅ Margin position closed: {pair}")
                    logging.info(f"Close Order ID: {close_order['id']}")
                    logging.info(f"PnL: ${pnl:.2f}")
                    
                    # Remove from active positions
                    del self.active_positions[pair]
                    
                    return {
                        "success": True,
                        "close_order_id": close_order['id'],
                        "pnl": pnl,
                        "exit_price": exit_price
                    }
                else:
                    logging.error("Failed to close margin position - no order ID")
                    return {"success": False, "error": "Close order failed"}
            else:
                logging.info(f"No margin position found for {pair}")
                del self.active_positions[pair]
                return {"success": True, "message": "Position already closed"}
                
        except Exception as e:
            logging.error(f"Error closing margin position: {e}")
            return {"success": False, "error": str(e)}
    
    def get_margin_balance(self) -> float:
        """Get available USDT balance for margin trading"""
        try:
            balance = self.client.fetch_balance({'type': 'margin'})
            return balance.get('USDT', {}).get('free', 0)
        except Exception as e:
            logging.error(f"Error fetching margin balance: {e}")
            return 0
    
    def get_margin_info(self, pair: str) -> Dict[str, Any]:
        """Get margin trading info for a pair"""
        try:
            margin_info = self.client.fetch_trading_fees([pair])
            return margin_info.get(pair, {})
        except Exception as e:
            logging.error(f"Error fetching margin info: {e}")
            return {}
    
    def _calculate_margin_pnl(self, direction: str, entry_price: float, exit_price: float, quantity: float) -> float:
        """Calculate PnL for margin position"""
        if entry_price == 0:
            return 0
        
        if direction == 'long':
            price_diff = exit_price - entry_price
        else:
            price_diff = entry_price - exit_price
        
        pnl = (price_diff / entry_price) * quantity * entry_price
        return pnl