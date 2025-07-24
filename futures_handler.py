#!/usr/bin/env python3
"""
Futures Handler - OKX Futures Trading Implementation
Handles futures positions with leverage up to 125x
"""

import logging
import json
from typing import Dict, Any, Optional

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

class FuturesHandler:
    def __init__(self, exchange_client):
        """Initialize futures handler with OKX client"""
        self.client = exchange_client
        self.active_positions = {}
        
        if self.client:
            # Switch to futures trading mode
            self.client.options['defaultType'] = 'swap'
            logging.info("Futures handler initialized - swap trading mode active")
    
    def open_futures_position(self, pair: str, direction: str, leverage: int, qty: float) -> Dict[str, Any]:
        """
        Open futures position with leverage
        
        Args:
            pair (str): Trading pair (e.g., 'BTC/USDT')
            direction (str): 'long' or 'short'
            leverage (int): Leverage multiplier (1-125)
            qty (float): Position size in base currency
            
        Returns:
            dict: Order result with success status
        """
        
        if not self.client:
            logging.error("No exchange client available")
            return {"success": False, "error": "No client"}
        
        try:
            # Set leverage for the pair
            self.client.set_leverage(leverage, pair)
            logging.info(f"Set leverage {leverage}x for {pair}")
            
            # Determine order side
            side = 'buy' if direction == 'long' else 'sell'
            
            # Create futures order
            order = self.client.create_market_order(
                symbol=pair,
                type='market',
                side=side,
                amount=qty,
                params={'positionSide': direction}
            )
            
            if order and order.get('id'):
                self.active_positions[pair] = {
                    'order_id': order['id'],
                    'direction': direction,
                    'leverage': leverage,
                    'quantity': qty,
                    'entry_price': order.get('average', 0),
                    'timestamp': order.get('timestamp')
                }
                
                logging.info(f"✅ Futures {direction.upper()} opened: {qty:.6f} {pair} at {leverage}x leverage")
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
                logging.error("Failed to create futures order - no order ID")
                return {"success": False, "error": "Order creation failed"}
                
        except ccxt.InsufficientFunds as e:
            logging.error(f"Insufficient funds for futures position: {e}")
            return {"success": False, "error": "Insufficient funds"}
        except ccxt.InvalidOrder as e:
            logging.error(f"Invalid futures order: {e}")
            return {"success": False, "error": f"Invalid order: {e}"}
        except Exception as e:
            logging.error(f"Futures position error: {e}")
            return {"success": False, "error": str(e)}
    
    def close_futures_position(self, pair: str) -> Dict[str, Any]:
        """
        Close existing futures position
        
        Args:
            pair (str): Trading pair
            
        Returns:
            dict: Close result with success status
        """
        
        if pair not in self.active_positions:
            logging.warning(f"No active position for {pair}")
            return {"success": False, "error": "No active position"}
        
        try:
            position_info = self.active_positions[pair]
            
            # Get current position from exchange
            positions = self.client.fetch_positions([pair])
            current_position = None
            
            for pos in positions:
                if pos['symbol'] == pair and pos['size'] > 0:
                    current_position = pos
                    break
            
            if not current_position:
                logging.info(f"No open position found for {pair}")
                del self.active_positions[pair]
                return {"success": True, "message": "Position already closed"}
            
            # Close position with market order
            side = 'sell' if position_info['direction'] == 'long' else 'buy'
            quantity = abs(current_position['size'])
            
            close_order = self.client.create_market_order(
                symbol=pair,
                type='market',
                side=side,
                amount=quantity,
                params={'reduceOnly': True}
            )
            
            if close_order and close_order.get('id'):
                # Calculate PnL
                entry_price = position_info.get('entry_price', 0)
                exit_price = close_order.get('average', 0)
                pnl = self._calculate_pnl(position_info['direction'], entry_price, exit_price, quantity, position_info['leverage'])
                
                logging.info(f"✅ Futures position closed: {pair}")
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
                logging.error("Failed to close position - no order ID")
                return {"success": False, "error": "Close order failed"}
                
        except Exception as e:
            logging.error(f"Error closing futures position: {e}")
            return {"success": False, "error": str(e)}
    
    def get_futures_balance(self) -> float:
        """Get available USDT balance for futures trading"""
        try:
            balance = self.client.fetch_balance({'type': 'swap'})
            return balance.get('USDT', {}).get('free', 0)
        except Exception as e:
            logging.error(f"Error fetching futures balance: {e}")
            return 0
    
    def get_active_positions(self) -> Dict[str, Any]:
        """Get all active futures positions"""
        try:
            positions = self.client.fetch_positions()
            active = {}
            
            for pos in positions:
                if pos['size'] > 0:
                    active[pos['symbol']] = {
                        'size': pos['size'],
                        'side': pos['side'],
                        'entry_price': pos['entryPrice'],
                        'mark_price': pos['markPrice'],
                        'pnl': pos['unrealizedPnl'],
                        'leverage': pos['leverage']
                    }
            
            return active
        except Exception as e:
            logging.error(f"Error fetching positions: {e}")
            return {}
    
    def _calculate_pnl(self, direction: str, entry_price: float, exit_price: float, quantity: float, leverage: int) -> float:
        """Calculate PnL for position"""
        if entry_price == 0:
            return 0
        
        if direction == 'long':
            price_diff = exit_price - entry_price
        else:
            price_diff = entry_price - exit_price
        
        pnl = (price_diff / entry_price) * quantity * entry_price * leverage
        return pnl
    
    def set_position_mode(self, mode: str = 'hedge') -> bool:
        """Set position mode (hedge/oneway)"""
        try:
            self.client.set_position_mode(hedged=(mode == 'hedge'))
            logging.info(f"Position mode set to: {mode}")
            return True
        except Exception as e:
            logging.error(f"Failed to set position mode: {e}")
            return False