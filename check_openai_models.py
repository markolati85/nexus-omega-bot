#!/usr/bin/env python3
"""
OpenAI API Key Verification and Model Check
Tests the new API key and lists available models
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv('.env_okx')

def check_openai_connection():
    """Test OpenAI API connection and list available models"""
    print("OPENAI API KEY VERIFICATION")
    print("=" * 40)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OPENAI_API_KEY found in environment")
        return False
    
    print(f"API Key: {api_key[:20]}...{api_key[-10:] if len(api_key) > 30 else api_key}")
    print()
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Test connection with a simple request
        print("Testing API connection...")
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            messages=[{"role": "user", "content": "Hello, test connection"}],
            max_tokens=10
        )
        
        print("✅ API Key is valid and working!")
        print(f"Test response: {response.choices[0].message.content}")
        print()
        
        # List available models
        print("Available Models:")
        print("-" * 20)
        models = client.models.list()
        
        # Filter for relevant models
        relevant_models = []
        for model in models.data:
            if any(keyword in model.id.lower() for keyword in ['gpt-4', 'gpt-3.5', 'davinci', 'curie', 'babbage', 'ada']):
                relevant_models.append(model.id)
        
        relevant_models.sort()
        for model in relevant_models[:15]:  # Show first 15 relevant models
            print(f"  • {model}")
        
        if len(relevant_models) > 15:
            print(f"  ... and {len(relevant_models) - 15} more models")
        
        print(f"\nTotal models available: {len(models.data)}")
        print(f"Relevant models: {len(relevant_models)}")
        
        return True
        
    except Exception as e:
        print("❌ API Key verification failed!")
        print(f"Error: {str(e)}")
        
        if "401" in str(e) or "Unauthorized" in str(e):
            print("\nTroubleshooting:")
            print("1. Verify the API key is correct")
            print("2. Check if the key has proper permissions")
            print("3. Ensure billing is set up in OpenAI account")
            print("4. Try regenerating the API key")
        
        return False

def test_gpt4o_specifically():
    """Test GPT-4o model specifically for trading bot"""
    print("\nTESTING GPT-4O FOR TRADING BOT")
    print("=" * 40)
    
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Test market analysis prompt similar to trading bot
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            messages=[{
                "role": "user",
                "content": "BTC at $118,000, 24h change +1.5%, volume high. Trading decision: BUY/SELL/HOLD with confidence 0-100%"
            }],
            max_tokens=50
        )
        
        print("✅ GPT-4o is working for trading analysis!")
        print(f"Sample trading response: {response.choices[0].message.content}")
        print("\n🚀 Ready for live trading bot deployment!")
        
        return True
        
    except Exception as e:
        print("❌ GPT-4o test failed!")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_openai_connection()
    if success:
        test_gpt4o_specifically()
    else:
        print("\n⚠️  Please provide a valid OpenAI API key to continue.")