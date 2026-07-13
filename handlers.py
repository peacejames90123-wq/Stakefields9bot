import openai
import logging
from typing import Dict, List
from config import OPENAI_API_KEY

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

logger = logging.getLogger(__name__)

class Handlers:
    def __init__(self):
        # Store conversation history for each user
        self.conversations: Dict[int, List[Dict[str, str]]] = {}
        self.max_history_length = 10  # Number of messages to remember
    
    def get_or_create_conversation(self, user_id: int) -> List[Dict[str, str]]:
        """Get or create a conversation history for a user"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        return self.conversations[user_id]
    
    def clear_history(self, user_id: int):
        """Clear conversation history for a user"""
        if user_id in self.conversations:
            self.conversations[user_id] = []
    
    def new_conversation(self, user_id: int):
        """Start a new conversation"""
        self.clear_history(user_id)
        # Add system message
        self.conversations[user_id].append({
            "role": "system",
            "content": "You are Stakefields9 Bot, a helpful AI assistant. You are friendly, knowledgeable, and provide accurate information. You help with writing, coding, translation, summarization, and creative tasks. Be concise but thorough in your responses."
        })
    
    async def get_openai_response(self, user_id: int, user_input: str) -> str:
        """Get response from OpenAI"""
        try:
            # Get conversation history
            history = self.get_or_create_conversation(user_id)
            
            # Initialize with system message if empty
            if not history:
                self.new_conversation(user_id)
                history = self.conversations[user_id]
            
            # Add user message
            history.append({"role": "user", "content": user_input})
            
            # Keep only last N messages
            if len(history) > self.max_history_length + 1:  # +1 for system message
                history = [history[0]] + history[-(self.max_history_length):]
                self.conversations[user_id] = history
            
            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=history,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract response text
            assistant_message = response.choices[0].message['content'].strip()
            
            # Add assistant message to history
            history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except openai.error.RateLimitError:
            return "⚠️ Rate limit exceeded. Please try again in a moment."
        except openai.error.AuthenticationError:
            return "❌ Authentication error. Please check your API key."
        except openai.error.APIError:
            return "❌ OpenAI API error. Please try again later."
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return "❌ An error occurred while processing your request. Please try again."
