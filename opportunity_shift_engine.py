#!/usr/bin/env python3
"""
Opportunity Shift Engine - Smart capital reallocation system
Detects better opportunities and shifts capital to maximize profits
"""

import logging
from typing import Dict, Any, List, Optional
from ai_core_langchain import get_trade_decision

class OpportunityShiftEngine:
    def __init__(self, exchange_client, futures_handler, margin_handler):
        """Initialize opportunity shift engine"""
        self.client = exchange_client
        self.futures_handler = futures_handler
        self.margin_handler = margin_handler
        self.active_monitors = {}
        self.shift_threshold = 2.0  # 2% better ROI required to shift
        
        logging.info("Opportunity Shift Engine initialized")
    
    def monitor_positions(self, trading_pairs: List[str]) -> List[Dict[str, Any]]:
        """
        Monitor all positions for better opportunities
        
        Args:
            trading_pairs (List[str]): Pairs to monitor
            
        Returns:
            List[Dict]: Recommended shifts
        """
        
        recommendations = []
        
        try:
            # Get current positions
            current_positions = self._get_all_positions()
            
            # Analyze each position for potential shifts
            for pair, position in current_positions.items():
                shift_recommendation = self._analyze_position_for_shift(pair, position, trading_pairs)
                
                if shift_recommendation:
                    recommendations.append(shift_recommendation)
            
            return recommendations
            
        except Exception as e:
            logging.error(f"Error monitoring positions: {e}")
            return []
    
    def execute_opportunity_shift(self, shift_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute capital shift from losing position to better opportunity
        
        Args:
            shift_data (dict): Shift recommendation data
            
        Returns:
            dict: Execution result
        """
        
        try:
            from_pair = shift_data['from_pair']
            to_pair = shift_data['to_pair']
            from_type = shift_data['from_type']
            to_type = shift_data['to_type']
            
            logging.info(f"🔄 Executing opportunity shift: {from_pair} → {to_pair}")
            logging.info(f"📊 Expected improvement: {shift_data['roi_improvement']:+.2f}%")
            
            # Step 1: Close losing position
            close_result = self._close_position(from_pair, from_type)
            if not close_result['success']:
                logging.error("Failed to close source position")
                return {"success": False, "error": "Failed to close source position"}
            
            # Step 2: Get available capital
            capital = self._get_available_capital(to_type)
            if capital < 10:  # Minimum $10 for trading
                logging.warning("Insufficient capital for shift")
                return {"success": False, "error": "Insufficient capital"}
            
            # Step 3: Open new position
            new_position_data = shift_data['new_position']
            open_result = self._open_position(
                to_pair,
                new_position_data['direction'],
                new_position_data['leverage'],
                capital * 0.9,  # Use 90% of available capital
                to_type
            )
            
            if open_result['success']:
                logging.info(f"✅ Opportunity shift completed successfully")
                logging.info(f"💰 Capital deployed: ${capital * 0.9:.2f}")
                
                return {
                    "success": True,
                    "from_pair": from_pair,
                    "to_pair": to_pair,
                    "close_pnl": close_result.get('pnl', 0),
                    "new_position": open_result,
                    "roi_improvement": shift_data['roi_improvement']
                }
            else:
                logging.error("Failed to open new position")
                return {"success": False, "error": "Failed to open new position"}
                
        except Exception as e:
            logging.error(f"Error executing opportunity shift: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_all_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active positions across spot, margin, and futures"""
        all_positions = {}
        
        try:
            # Get futures positions
            futures_positions = self.futures_handler.get_active_positions()
            for pair, pos in futures_positions.items():
                all_positions[pair] = {**pos, 'type': 'futures'}
            
            # Get margin positions (from active_positions tracking)
            margin_positions = self.margin_handler.active_positions
            for pair, pos in margin_positions.items():
                # Calculate current PnL for margin
                current_price = self._get_current_price(pair)
                entry_price = pos.get('entry_price', current_price)
                unrealized_pnl = self._calculate_unrealized_pnl(
                    pos['direction'], entry_price, current_price, pos['quantity']
                )
                
                all_positions[pair] = {
                    'size': pos['quantity'],
                    'side': pos['direction'],
                    'entry_price': entry_price,
                    'mark_price': current_price,
                    'pnl': unrealized_pnl,
                    'leverage': pos['leverage'],
                    'type': 'margin'
                }
            
            return all_positions
            
        except Exception as e:
            logging.error(f"Error getting positions: {e}")
            return {}
    
    def _analyze_position_for_shift(self, pair: str, position: Dict[str, Any], trading_pairs: List[str]) -> Optional[Dict[str, Any]]:
        """Analyze if position should be shifted to better opportunity"""
        
        try:
            current_pnl_pct = self._calculate_pnl_percentage(position)
            
            # Only consider shifts for losing positions or low-profit positions
            if current_pnl_pct > 1.0:  # Position is doing well, keep it
                return None
            
            # Find better opportunities
            best_opportunity = None
            best_roi = current_pnl_pct
            
            for target_pair in trading_pairs:
                if target_pair == pair:
                    continue
                
                # Get market data for potential target
                market_data = self._get_market_data(target_pair)
                if not market_data:
                    continue
                
                # Get AI decision for this pair
                ai_decision = get_trade_decision(market_data)
                
                if ai_decision['confidence'] > 75 and ai_decision['direction'] != 'hold':
                    # Estimate potential ROI
                    estimated_roi = self._estimate_roi(ai_decision, market_data)
                    
                    if estimated_roi > best_roi + self.shift_threshold:
                        best_opportunity = {
                            'pair': target_pair,
                            'roi': estimated_roi,
                            'ai_decision': ai_decision,
                            'market_data': market_data
                        }
                        best_roi = estimated_roi
            
            if best_opportunity:
                return {
                    'from_pair': pair,
                    'to_pair': best_opportunity['pair'],
                    'from_type': position['type'],
                    'to_type': 'futures',  # Prefer futures for better opportunities
                    'current_pnl_pct': current_pnl_pct,
                    'roi_improvement': best_roi - current_pnl_pct,
                    'new_position': {
                        'direction': best_opportunity['ai_decision']['direction'],
                        'leverage': best_opportunity['ai_decision']['leverage'],
                        'strategy': best_opportunity['ai_decision']['strategy']
                    },
                    'confidence': best_opportunity['ai_decision']['confidence']
                }
            
            return None
            
        except Exception as e:
            logging.error(f"Error analyzing position {pair}: {e}")
            return None
    
    def _calculate_pnl_percentage(self, position: Dict[str, Any]) -> float:
        """Calculate PnL percentage for position"""
        try:
            pnl = position.get('pnl', 0)
            entry_price = position.get('entry_price', 0)
            size = position.get('size', 0)
            
            if entry_price == 0 or size == 0:
                return 0
            
            position_value = entry_price * size
            pnl_pct = (pnl / position_value) * 100
            
            return pnl_pct
            
        except:
            return 0
    
    def _get_market_data(self, pair: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive market data for analysis"""
        try:
            ticker = self.client.fetch_ticker(pair)
            ohlcv = self.client.fetch_ohlcv(pair, '1h', limit=50)
            
            if not ohlcv or len(ohlcv) < 20:
                return None
            
            closes = [candle[4] for candle in ohlcv[-20:]]
            rsi = self._calculate_rsi(closes, 14)
            
            volatility = self._calculate_volatility(closes)
            trend_strength = self._calculate_trend_strength(closes)
            
            return {
                'pair': pair,
                'price': ticker['last'],
                'price_change_24h': ticker.get('percentage', 0),
                'volume_24h': ticker.get('quoteVolume', 0),
                'rsi': rsi,
                'volatility': volatility,
                'trend_strength': trend_strength
            }
            
        except Exception as e:
            logging.error(f"Error getting market data for {pair}: {e}")
            return None
    
    def _estimate_roi(self, ai_decision: Dict[str, Any], market_data: Dict[str, Any]) -> float:
        """Estimate potential ROI based on AI decision and market conditions"""
        
        confidence = ai_decision.get('confidence', 50)
        leverage = ai_decision.get('leverage', 1)
        take_profit_pct = ai_decision.get('take_profit_pct', 4.0)
        
        # Base ROI estimate
        base_roi = take_profit_pct * (confidence / 100)
        
        # Apply leverage multiplier (capped for safety)
        leverage_multiplier = min(leverage / 10, 5.0)  # Max 5x multiplier
        estimated_roi = base_roi * leverage_multiplier
        
        # Apply volatility adjustment
        volatility = market_data.get('volatility', 1.0)
        volatility_factor = min(volatility / 2.0, 2.0)  # Max 2x multiplier
        
        final_roi = estimated_roi * volatility_factor
        
        return min(final_roi, 50.0)  # Cap at 50% ROI estimate
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return 50
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility"""
        if len(prices) < 2:
            return 0
        
        changes = [(prices[i] / prices[i-1] - 1) * 100 for i in range(1, len(prices))]
        avg = sum(changes) / len(changes)
        variance = sum((x - avg) ** 2 for x in changes) / len(changes)
        volatility = variance ** 0.5
        
        return volatility
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate trend strength (-1 to 1)"""
        if len(prices) < 10:
            return 0
        
        recent_avg = sum(prices[-5:]) / 5
        older_avg = sum(prices[-15:-10]) / 5
        
        if older_avg == 0:
            return 0
        
        trend_strength = (recent_avg / older_avg - 1) * 10
        return max(-1, min(1, trend_strength))
    
    def _get_current_price(self, pair: str) -> float:
        """Get current price for a pair"""
        try:
            ticker = self.client.fetch_ticker(pair)
            return ticker['last']
        except:
            return 0
    
    def _calculate_unrealized_pnl(self, direction: str, entry_price: float, current_price: float, quantity: float) -> float:
        """Calculate unrealized PnL"""
        if entry_price == 0:
            return 0
        
        if direction == 'long':
            price_diff = current_price - entry_price
        else:
            price_diff = entry_price - current_price
        
        pnl = (price_diff / entry_price) * quantity * entry_price
        return pnl
    
    def _close_position(self, pair: str, position_type: str) -> Dict[str, Any]:
        """Close position based on type"""
        if position_type == 'futures':
            return self.futures_handler.close_futures_position(pair)
        elif position_type == 'margin':
            return self.margin_handler.close_margin_position(pair)
        else:
            return {"success": False, "error": "Unknown position type"}
    
    def _get_available_capital(self, trading_type: str) -> float:
        """Get available capital for trading type"""
        if trading_type == 'futures':
            return self.futures_handler.get_futures_balance()
        elif trading_type == 'margin':
            return self.margin_handler.get_margin_balance()
        else:
            balance = self.client.fetch_balance()
            return balance.get('USDT', {}).get('free', 0)
    
    def _open_position(self, pair: str, direction: str, leverage: int, amount: float, trading_type: str) -> Dict[str, Any]:
        """Open position based on trading type"""
        
        # Calculate quantity
        current_price = self._get_current_price(pair)
        if current_price == 0:
            return {"success": False, "error": "Cannot get price"}
        
        quantity = amount / current_price
        
        if trading_type == 'futures':
            return self.futures_handler.open_futures_position(pair, direction, leverage, quantity)
        elif trading_type == 'margin':
            return self.margin_handler.open_margin_position(pair, direction, leverage, quantity)
        else:
            return {"success": False, "error": "Unsupported trading type"}