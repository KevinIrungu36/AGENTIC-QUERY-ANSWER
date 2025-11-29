#!/usr/bin/env python3
import subprocess
import sys

def install_requirements():
    """Install the required packages"""
    packages = [
        "fastapi==0.122.0",
        "uvicorn==0.38.0", 
        "groq==0.36.0",
        "python-dotenv==1.2.1",
        "requests==2.32.5",
        "pydantic==2.12.5"
    ]
    
    print("Installing required packages...")
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
    
    print("\n🎉 Installation completed!")

if __name__ == "__main__":
    install_requirements()