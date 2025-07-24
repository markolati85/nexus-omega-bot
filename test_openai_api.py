#!/usr/bin/env python3
"""
OpenAI GPT-4o Connection Test
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env_okx')

print('🤖 Testing OpenAI GPT-4o Connection...')
print('=' * 40)

try:
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Test GPT-4o with trading prompt
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'user', 'content': 'Respond with exactly: "GPT-4o AI Ready for Trading"'}
        ],
        max_tokens=20
    )
    
    ai_response = response.choices[0].message.content
    print(f'🧠 AI Response: {ai_response}')
    
    if 'Ready' in ai_response:
        print('✅ GPT-4o integration confirmed')
        print('🎯 AI decision making active')
        print('AI_STATUS: SUCCESS')
    else:
        print('⚠️ GPT-4o response unexpected')
        print('AI_STATUS: WARNING')
        
except Exception as e:
    print(f'❌ OpenAI connection failed: {e}')
    if 'api_key' in str(e).lower():
        print('💡 Solution: Check OpenAI API key')
    else:
        print('💡 Solution: Verify OpenAI API key is valid')
    print('AI_STATUS: FAILED')

print('=' * 40)