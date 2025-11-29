#!/usr/bin/env python3
import uvicorn
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    
    # Check if OpenAI API key is set
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file like this:")
        print("OPENAI_API_KEY=sk-your-actual-key-here")
        exit(1)
    
    if openai_key.startswith("your_") or "example" in openai_key:
        print("❌ ERROR: Please replace the placeholder OpenAI API key with your actual key")
        exit(1)
    
    print("✅ OpenAI API key found")
    print("🚀 Starting AI Question-Answer Helper API...")
    print("📚 API Documentation will be available at: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Simple uvicorn run without reload
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)