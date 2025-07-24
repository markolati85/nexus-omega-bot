#!/usr/bin/env python3

import os
import subprocess

# Get OpenAI API key from local environment
openai_key = os.getenv('OPENAI_API_KEY')

if openai_key:
    print(f"Updating server with OpenAI key: {openai_key[:20]}...")
    
    # Read current .env file
    env_content = []
    try:
        with open('.env', 'r') as f:
            env_content = f.readlines()
    except:
        pass
    
    # Create new .env content
    new_env = []
    openai_found = False
    
    for line in env_content:
        if line.startswith('OPENAI_API_KEY='):
            new_env.append(f'OPENAI_API_KEY={openai_key}\n')
            openai_found = True
        else:
            new_env.append(line)
    
    if not openai_found:
        new_env.append(f'OPENAI_API_KEY={openai_key}\n')
    
    # Write updated .env file
    with open('.env_updated', 'w') as f:
        f.writelines(new_env)
    
    print("Updated .env file created locally")
    
    # Copy to server
    subprocess.run([
        'sshpass', '-p', 'Simanovci1', 'scp', 
        '.env_updated', 'root@185.241.214.234:/opt/nexus-trading/.env'
    ])
    
    print("✅ OpenAI API key updated on server")
    
else:
    print("❌ No OpenAI API key found in local environment")