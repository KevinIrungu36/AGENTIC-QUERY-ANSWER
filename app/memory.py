from typing import List, Dict, Any
from datetime import datetime, timedelta

class ShortTermMemory:
    """Simple short-term memory for conversation context"""
    
    def __init__(self, max_size: int = 5, ttl_minutes: int = 30):
        self.max_size = max_size
        self.ttl_minutes = ttl_minutes
        self.conversation_history = []
    
    def add_message(self, role: str, content: str):
        """Add a message to memory"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        }
        
        self.conversation_history.append(message)
        self._cleanup()
    
    def get_recent_context(self, max_messages: int = 3) -> List[Dict]:
        """Get recent conversation context"""
        self._cleanup()
        return self.conversation_history[-max_messages:] if self.conversation_history else []
    
    def _cleanup(self):
        """Remove old messages and enforce size limits"""
        now = datetime.now()
        
        # Remove expired messages
        self.conversation_history = [
            msg for msg in self.conversation_history
            if now - msg["timestamp"] < timedelta(minutes=self.ttl_minutes)
        ]
        
        # Enforce size limit
        if len(self.conversation_history) > self.max_size:
            self.conversation_history = self.conversation_history[-self.max_size:]
    
    def clear(self):
        """Clear all memory"""
        self.conversation_history.clear()