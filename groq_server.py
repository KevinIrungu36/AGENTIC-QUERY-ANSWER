import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import groq
from dotenv import load_dotenv
import traceback

load_dotenv()

app = FastAPI(
    title="AI Question-Answer Helper",
    description="Simple AI agent with search tool - Powered by Groq",
    version="4.1.0"
)

# Enhanced knowledge base with better organization
knowledge_base = {
    # Capitals - organized by country
    "france": {"capital": "Paris", "full_answer": "The capital of France is Paris."},
    "germany": {"capital": "Berlin", "full_answer": "The capital of Germany is Berlin."},
    "italy": {"capital": "Rome", "full_answer": "The capital of Italy is Rome."},
    "spain": {"capital": "Madrid", "full_answer": "The capital of Spain is Madrid."},
    "japan": {"capital": "Tokyo", "full_answer": "The capital of Japan is Tokyo."},
    "china": {"capital": "Beijing", "full_answer": "The capital of China is Beijing."},
    "india": {"capital": "New Delhi", "full_answer": "The capital of India is New Delhi."},
    "russia": {"capital": "Moscow", "full_answer": "The capital of Russia is Moscow."},
    "brazil": {"capital": "Brasília", "full_answer": "The capital of Brazil is Brasília."},
    "canada": {"capital": "Ottawa", "full_answer": "The capital of Canada is Ottawa."},
    "australia": {"capital": "Canberra", "full_answer": "The capital of Australia is Canberra."},
    "kenya": {"capital": "Nairobi", "full_answer": "The capital of Kenya is Nairobi."},
    "egypt": {"capital": "Cairo", "full_answer": "The capital of Egypt is Cairo."},
    "south africa": {"capital": "Pretoria", "full_answer": "The capital of South Africa is Pretoria."},
    "nigeria": {"capital": "Abuja", "full_answer": "The capital of Nigeria is Abuja."},
    "ethiopia": {"capital": "Addis Ababa", "full_answer": "The capital of Ethiopia is Addis Ababa."},
    "ghana": {"capital": "Accra", "full_answer": "The capital of Ghana is Accra."},
    "united states": {"capital": "Washington D.C.", "full_answer": "The capital of United States is Washington D.C."},
    "united kingdom": {"capital": "London", "full_answer": "The capital of United Kingdom is London."},
    
    # Science facts
    "mount everest": {"height": "8,848 meters", "full_answer": "Mount Everest is 8,848 meters (29,029 feet) tall."},
    "telephone": {"inventor": "Alexander Graham Bell", "full_answer": "Alexander Graham Bell is credited with inventing the telephone."},
    "china": {"population": "1.4 billion", "full_answer": "The population of China is approximately 1.4 billion people."},
    "india": {"population": "1.3 billion", "full_answer": "The population of India is approximately 1.3 billion people."},
    "pacific ocean": {"size": "largest", "full_answer": "The Pacific Ocean is the largest ocean on Earth."},
    "light": {"speed": "299,792,458 m/s", "full_answer": "The speed of light in vacuum is 299,792,458 meters per second."},
    "gold": {"symbol": "Au", "full_answer": "The chemical symbol for gold is Au."},
    "oxygen": {"symbol": "O", "full_answer": "The chemical symbol for oxygen is O."},
    "water": {"formula": "H₂O", "full_answer": "The chemical formula for water is H₂O."},
    "world war ii": {"end_year": "1945", "full_answer": "World War II ended in 1945."},
    "microsoft": {"founder": "Bill Gates and Paul Allen", "full_answer": "Microsoft was founded by Bill Gates and Paul Allen."},
    "apple": {"founder": "Steve Jobs, Steve Wozniak, and Ronald Wayne", "full_answer": "Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne."},
    "solar system": {"planets": "8", "full_answer": "There are 8 planets in our solar system: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune."},
    
    # General knowledge
    "python": {"description": "programming language", "full_answer": "Python is a high-level programming language known for its simplicity and readability."},
    "artificial intelligence": {"description": "AI simulation", "full_answer": "Artificial Intelligence (AI) is the simulation of human intelligence in machines."},
    "machine learning": {"description": "AI subset", "full_answer": "Machine learning is a subset of AI that enables computers to learn without being explicitly programmed."},
    "groq": {"description": "AI chip company", "full_answer": "Groq is a company that develops AI inference chips and provides fast AI API services."},
}

# Fixed Simple memory system
class SimpleMemory:
    def __init__(self, max_size: int = 6):
        self.max_size = max_size
        self.conversation = []  # Initialize the conversation attribute
    
    def add_message(self, role: str, content: str):
        self.conversation.append({"role": role, "content": content})
        if len(self.conversation) > self.max_size:
            self.conversation = self.conversation[-self.max_size:]
    
    def get_context(self, max_messages: int = 4):
        return self.conversation[-max_messages:] if len(self.conversation) > max_messages else self.conversation
    
    def clear(self):
        self.conversation.clear()

# Initialize components
memory = SimpleMemory()

# Initialize Groq client
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    # Correct way to initialize Groq client
    groq_client = groq.Groq(api_key=groq_api_key)
    print("✅ Groq client initialized successfully!")
except Exception as e:
    print(f"❌ Groq initialization error: {e}")
    groq_client = None

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    used_tool: bool
    tool_result: Optional[str] = None
    status: str

def search_tool(query: str) -> str:
    """Search the knowledge base for factual information"""
    query_lower = query.lower().strip()
    
    print(f"🔍 Raw query: '{query_lower}'")
    
    # Extract country/city names and topics
    countries = ["france", "germany", "italy", "spain", "japan", "china", "india", "russia", 
                "brazil", "canada", "australia", "kenya", "egypt", "south africa", "nigeria",
                "ethiopia", "ghana", "united states", "united kingdom"]
    
    topics = ["capital", "population", "height", "inventor", "founder", "speed", "symbol", "formula"]
    
    # Look for country names in the query
    found_country = None
    for country in countries:
        if country in query_lower:
            found_country = country
            break
    
    # Look for topics in the query
    found_topic = None
    for topic in topics:
        if topic in query_lower:
            found_topic = topic
            break
    
    print(f"🔍 Found country: {found_country}, topic: {found_topic}")
    
    # Case 1: Capital questions
    if found_country and ("capital" in query_lower or "capital of" in query_lower):
        if found_country in knowledge_base and "capital" in knowledge_base[found_country]:
            return knowledge_base[found_country]["full_answer"]
    
    # Case 2: Population questions
    elif found_country and "population" in query_lower:
        if found_country in knowledge_base and "population" in knowledge_base[found_country]:
            return knowledge_base[found_country]["full_answer"]
    
    # Case 3: Specific fact questions
    elif "mount everest" in query_lower and "height" in query_lower:
        return knowledge_base["mount everest"]["full_answer"]
    
    elif "telephone" in query_lower and "invent" in query_lower:
        return knowledge_base["telephone"]["full_answer"]
    
    elif "largest ocean" in query_lower:
        return knowledge_base["pacific ocean"]["full_answer"]
    
    elif "speed of light" in query_lower:
        return knowledge_base["light"]["full_answer"]
    
    elif "gold" in query_lower and "symbol" in query_lower:
        return knowledge_base["gold"]["full_answer"]
    elif "world war" in query_lower and "end" in query_lower:
        return knowledge_base["world war ii"]["full_answer"]
    
    elif "microsoft" in query_lower and "found" in query_lower:
        return knowledge_base["microsoft"]["full_answer"]
    
    elif "solar system" in query_lower and "planet" in query_lower:
        return knowledge_base["solar system"]["full_answer"]
    
    # Case 4: General "what is" questions
    elif "what is" in query_lower:
        if "python" in query_lower:
            return knowledge_base["python"]["full_answer"]
        elif "artificial intelligence" in query_lower or "ai" in query_lower:
            return knowledge_base["artificial intelligence"]["full_answer"]
        elif "machine learning" in query_lower:
            return knowledge_base["machine learning"]["full_answer"]
        elif "groq" in query_lower:
            return knowledge_base["groq"]["full_answer"]
    
    # Fallback: Try direct matching
    for key, value in knowledge_base.items():
        if key in query_lower and "full_answer" in value:
            return value["full_answer"]
    
    return f"I couldn't find specific information about '{query}' in my knowledge base."

def is_factual_question(question: str) -> bool:
    """Determine if a question is factual and requires search"""
    factual_keywords = [
        'what is', 'who is', 'when was', 'where is', 'how many', 
        'how much', 'capital of', 'population of', 'height of',
        'inventor of', 'year', 'largest', 'smallest', 'chemical symbol',
        'founder of', 'speed of', 'distance to', 'how tall', 'how big',
        'what are', 'who invented', 'when did', 'where are'
    ]
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in factual_keywords)

def generate_groq_response(messages: list) -> str:
    """Generate response using Groq API with latest models"""
    if not groq_client:
        return "I'm currently unavailable. Please check if the Groq API key is properly configured."
    
    try:
        # Updated list of available Groq models
        available_models = [
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile", 
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        
        for model in available_models:
            try:
                print(f"🔄 Trying model: {model}")
                response = groq_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024,
                    top_p=1,
                    stream=False
                )
                print(f"✅ Success with model: {model}")
                return response.choices[0].message.content
            except Exception as e:
                print(f"❌ Model {model} failed: {e}")
                continue
        
        # If all models fail, provide a helpful fallback response
        return "I'm currently experiencing technical difficulties with the AI service. However, I can still answer questions using my built-in knowledge base for factual information."
        
    except Exception as e:
        error_msg = f"I encountered an error: {str(e)}"
        print(f"❌ Groq API error: {traceback.format_exc()}")
        return error_msg

@app.get("/")
async def root():
    groq_status = "connected" if groq_client else "disconnected"
    return {
        "message": "AI Question-Answer Helper API is running!",
        "status": "healthy",
        "groq_api": groq_status,
        "features": "Factual Q&A + Conversational AI with Groq",
        "version": "4.1.0"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        print(f"📨 Received message: {request.message}")
        
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        user_message = request.message.strip()
        memory.add_message("user", user_message)
        is_factual = is_factual_question(user_message)
        tool_result = None
        
        print(f"🔍 Question type: {'Factual' if is_factual else 'Conversational'}")
        
        # Prepare messages for Groq
        messages = []
        
        if is_factual:
            # Use search tool for factual questions
            tool_result = search_tool(user_message)
            print(f"🔧 Tool result: {tool_result}")
            
            system_prompt = """You are a helpful AI assistant that answers questions using provided search results.
            
            Guidelines:
            - Use the search result to answer factual questions accurately
            - If the search result doesn't contain the answer, acknowledge this and provide a helpful response
            - Keep answers concise and informative
            - Always be helpful and friendly"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {user_message}\n\nSearch Result: {tool_result}\n\nPlease answer the question based on the search result above."}
            ]
        else:
            # For conversational questions, use context
            context = memory.get_context()
            system_prompt = "You are a helpful, friendly, and concise AI assistant. Use the conversation history for context when relevant."
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            for msg in context:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            print(f"💭 Using {len(context)} context messages")
        
        print(f"🤖 Sending {len(messages)} messages to Groq API")
        
        # Generate response using Groq
        ai_response = generate_groq_response(messages)
        
        print(f"✅ AI Response: {ai_response[:100]}...")
        
        # Add AI response to memory
        memory.add_message("assistant", ai_response)
        
        return ChatResponse(
            response=ai_response,
            used_tool=is_factual,
            tool_result=tool_result,
            status="success"
        )
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Server error: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    groq_status = "connected" if groq_client else "disconnected"
    return {
        "status": "healthy", 
        "service": "AI Question-Answer Helper",
        "groq_api": groq_status,
        "memory_size": len(memory.conversation),
        "version": "4.1.0"
    }

@app.post("/clear")
async def clear_memory():
    """Clear conversation memory"""
    memory.clear()
    return {"status": "success", "message": "Memory cleared"}

@app.get("/knowledge")
async def list_knowledge():
    """Endpoint to see all available knowledge"""
    countries_with_capitals = [f"{country} - {knowledge_base[country]['capital']}" 
                              for country in knowledge_base 
                              if "capital" in knowledge_base[country]]
    
    science_facts = [key for key in knowledge_base 
                    if any(word in key for word in ["mount", "telephone", "light", "gold", "oxygen", "water", "solar"])]
    
    general_topics = [key for key in knowledge_base 
                     if key not in countries_with_capitals and key not in science_facts]
    
    return {
        "total_topics": len(knowledge_base),
        "capitals": countries_with_capitals,
        "science_facts": science_facts,
        "general_topics": general_topics
    }

if __name__ == "__main__":
    print("🚀 Starting AI Question-Answer Helper with Groq...")
    print("📚 Open http://localhost:8000/docs for API documentation")
    print("🔑 Using Groq API for AI responses")
    print("🔍 Built-in knowledge base for factual queries")
    print("💭 Conversation memory enabled")
    print("🐛 Debug mode: ON")
    print("🆕 Using latest Groq models")
    print("🎯 Improved search tool with better matching")
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=True)