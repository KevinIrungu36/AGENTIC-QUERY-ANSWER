from typing import Dict

class SearchTool:
    """Simple dictionary-based search tool for factual queries"""
    
    def __init__(self):
        self.knowledge_base = {
            "capital of france": "The capital of France is Paris.",
            "population of china": "The population of China is approximately 1.4 billion.",
            "height of mount everest": "Mount Everest is 8,848 meters (29,029 feet) tall.",
            "inventor of telephone": "Alexander Graham Bell is credited with inventing the telephone.",
            "year world war ii ended": "World War II ended in 1945.",
            "largest ocean": "The Pacific Ocean is the largest ocean on Earth.",
            "chemical symbol for gold": "The chemical symbol for gold is Au.",
            "planets in solar system": "There are 8 planets in our solar system: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.",
            "founder of microsoft": "Microsoft was founded by Bill Gates and Paul Allen.",
            "speed of light": "The speed of light in vacuum is 299,792,458 meters per second."
        }
    
    def search(self, query: str) -> str:
        """Search for factual information in the knowledge base"""
        query_lower = query.lower().strip()
        
        # Exact match
        if query_lower in self.knowledge_base:
            return self.knowledge_base[query_lower]
        
        # Partial match
        for key, value in self.knowledge_base.items():
            if query_lower in key or key in query_lower:
                return value
        
        return f"I couldn't find specific information about '{query}'. Please try another factual question."

    def __call__(self, query: str) -> str:
        return self.search(query)