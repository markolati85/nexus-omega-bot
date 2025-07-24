import json
import logging

def handle_gpt_response(response_data, symbol, executor, portfolio_balance):
    """Handle GPT-4o response and execute trades if conditions match"""
    try:
        if not response_data or not isinstance(response_data, dict):
            print("⚠️ Invalid GPT response format")
            return False
        
        action = response_data.get("action", "").lower()
        confidence = response_data.get("confidence", 0)
        leverage = response_data.get("leverage", 1)
        reason = response_data.get("reason", "No reason provided")
        
        print(f"🤖 GPT-4o Decision: {action.upper()} {symbol} (Confidence: {confidence}%)")
        print(f"📊 Reasoning: {reason}")
        
        # Execute trade if confidence > 70
        if confidence > 70:
            if action == "buy":
                trade_amount = portfolio_balance * 0.05 * leverage  # 5% base position with leverage
                print(f"🚀 EXECUTING GPT-4o BUY: {symbol} | Amount: ${trade_amount:.2f} | Leverage: {leverage}x")
                return executor(symbol, "BUY", trade_amount, leverage)
                
            elif action == "sell":
                print(f"🔻 EXECUTING GPT-4o SELL: {symbol} | Leverage: {leverage}x")
                return executor(symbol, "SELL", 0, leverage)
                
        else:
            print(f"⏸️ GPT-4o confidence {confidence}% below execution threshold (70%)")
            return False
            
    except Exception as e:
        print(f"⚠️ GPT Response Handling Error: {e}")
        return False

def validate_gpt_decision(decision_data):
    """Validate GPT-4o decision data structure"""
    required_fields = ["action", "confidence", "leverage", "reason"]
    
    if not isinstance(decision_data, dict):
        return False, "Response is not a dictionary"
    
    for field in required_fields:
        if field not in decision_data:
            return False, f"Missing required field: {field}"
    
    # Validate ranges
    if not (0 <= decision_data["confidence"] <= 100):
        return False, "Confidence must be between 0-100"
    
    if not (1 <= decision_data["leverage"] <= 5):
        return False, "Leverage must be between 1-5"
    
    if decision_data["action"] not in ["buy", "sell", "hold"]:
        return False, "Action must be buy, sell, or hold"
    
    return True, "Valid decision"
