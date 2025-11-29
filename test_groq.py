import os
import groq
from dotenv import load_dotenv

load_dotenv()

def test_groq():
    try:
        client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": "Hello, how are you?"}],
            temperature=0.7,
            max_tokens=100
        )
        
        print("✅ Groq test successful!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Groq test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_groq()