#!/usr/bin/env python3
"""
Strategy Selector - AI-powered trading strategy selection
Selects optimal strategy based on market conditions
"""

def select_optimal_strategy(pair_data: dict) -> str:
    """
    Select optimal trading strategy based on market conditions
    
    Args:
        pair_data (dict): Market data including volatility, trend_strength, RSI, price_range
        
    Returns:
        str: Strategy name ("Breakout", "Trend", "MeanReversion", "Grid")
    """
    
    volatility = pair_data.get('volatility', 0)
    trend_strength = pair_data.get('trend_strength', 0)
    rsi = pair_data.get('rsi', 50)
    price_range = pair_data.get('price_range', 0)
    
    # High volatility = Breakout strategy
    if volatility > 2.0:
        return "Breakout"
    
    # Strong trend = Trend following
    if trend_strength > 0.5:
        return "Trend"
    
    # Oversold/Overbought = Mean reversion
    if rsi < 30 or rsi > 70:
        return "MeanReversion"
    
    # Low volatility = Grid trading
    if price_range < 1.5:
        return "Grid"
    
    # Default to trend strategy
    return "Trend"

def get_strategy_parameters(strategy: str, pair_data: dict) -> dict:
    """
    Get specific parameters for selected strategy
    
    Args:
        strategy (str): Selected strategy name
        pair_data (dict): Market data
        
    Returns:
        dict: Strategy-specific parameters
    """
    
    base_params = {
        "stop_loss_pct": 2.0,
        "take_profit_pct": 4.0,
        "position_size_pct": 5.0
    }
    
    if strategy == "Breakout":
        return {
            **base_params,
            "stop_loss_pct": 1.5,
            "take_profit_pct": 6.0,
            "position_size_pct": 8.0,
            "entry_threshold": 0.5
        }
    
    elif strategy == "Trend":
        return {
            **base_params,
            "stop_loss_pct": 2.5,
            "take_profit_pct": 5.0,
            "position_size_pct": 6.0,
            "trend_confirmation": True
        }
    
    elif strategy == "MeanReversion":
        return {
            **base_params,
            "stop_loss_pct": 1.0,
            "take_profit_pct": 3.0,
            "position_size_pct": 4.0,
            "oversold_threshold": 30,
            "overbought_threshold": 70
        }
    
    elif strategy == "Grid":
        return {
            **base_params,
            "stop_loss_pct": 0.8,
            "take_profit_pct": 2.0,
            "position_size_pct": 3.0,
            "grid_levels": 5,
            "grid_spacing": 0.5
        }
    
    return base_params