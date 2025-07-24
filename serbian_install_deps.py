#!/usr/bin/env python3
"""
Simple dependency installer for Serbian server
"""
import subprocess
import sys

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    packages = [
        "ccxt==4.3.74",
        "pandas", 
        "numpy",
        "requests",
        "openai",
        "python-dotenv",
        "flask",
        "sqlalchemy"
    ]
    
    print("Installing Python packages...")
    
    # Upgrade pip first
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\nInstallation complete: {success_count}/{len(packages)} packages installed")
    
    if success_count == len(packages):
        print("✅ All dependencies installed successfully!")
        return True
    else:
        print("⚠️ Some packages failed to install")
        return False

if __name__ == "__main__":
    main()