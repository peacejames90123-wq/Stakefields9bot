import openai
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class Handlers:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.conversations: Dict[int, List[Dict[str, str]]] = {}
        self.max_history_length = 10
    
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
        """Start a new conversation with Spanish system message"""
        self.clear_history(user_id)
        self.conversations[user_id].append({
            "role": "system",
            "content": "Eres Stakefields9 Bot, un asistente de IA útil y amigable. Hablas exclusivamente en español. Eres conocedor, preciso y proporcionas información precisa. Ayudas con escritura, codificación, traducción, resumen y tareas creativas. Sé conciso pero completo en tus respuestas. Siempre respondes en español, sin importar el idioma en que te pregunten."
        })
    
    async def get_openai_response(self, user_id: int, user_input: str) -> str:
        """Get response from OpenAI"""
        try:
            history = self.get_or_create_conversation(user_id)
            
            if not history:
                self.new_conversation(user_id)
                history = self.conversations[user_id]
            
            # Add user message
            history.append({"role": "user", "content": user_input})
            
            # Keep only last N messages
            if len(history) > self.max_history_length + 1:
                history = [history[0]] + history[-(self.max_history_length):]
                self.conversations[user_id] = history
            
            # Get response from OpenAI using new API
            client = openai.OpenAI(api_key=openai.api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=history,
                max_tokens=1000,
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message.content.strip()
            
            history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except openai.RateLimitError:
            return "⚠️ Límite de velocidad excedido. Por favor, intenta de nuevo en un momento."
        except openai.AuthenticationError:
            return "❌ Error de autenticación. Por favor, verifica tu clave API."
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "❌ Error en la API de OpenAI. Por favor, intenta más tarde."
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return "❌ Ocurrió un error al procesar tu solicitud. Por favor, intenta de nuevo."
