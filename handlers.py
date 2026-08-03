import openai
import logging
from typing import Dict, List
from config import OPENAI_API_KEY

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

logger = logging.getLogger(__name__)

class Handlers:
    def __init__(self):
        self.conversations: Dict[int, List[Dict[str, str]]] = {}
        self.max_history_length = 10
    
    def get_or_create_conversation(self, user_id: int) -> List[Dict[str, str]]:
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        return self.conversations[user_id]
    
    def clear_history(self, user_id: int):
        if user_id in self.conversations:
            self.conversations[user_id] = []
    
    def new_conversation(self, user_id: int):
        self.clear_history(user_id)
        # STRONG SYSTEM PROMPT - FORCE SPANISH
        self.conversations[user_id].append({
            "role": "system",
            "content": (
                "Eres @Stakefields9bot, un asistente de IA avanzado. "
                "INSTRUCCIÓN OBLIGATORIA: DEBES RESPONDER EXCLUSIVAMENTE EN ESPAÑOL. "
                "NUNCA RESPONDAS EN INGLÉS. SIEMPRE RESPONDE EN ESPAÑOL.\n\n"
                "Eres amigable, conocedor, preciso y proporcionas información útil. "
                "Ayudas con: conversaciones naturales, escritura, reescritura, traducción, "
                "resumen de textos, generación de código, explicación de código, "
                "y creación de contenido creativo. Sé conciso pero completo en tus respuestas."
            )
        })
    
    async def get_openai_response(self, user_id: int, user_input: str) -> str:
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
            
            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=history,
                max_tokens=1000,
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message['content'].strip()
            history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except openai.error.RateLimitError:
            return "⚠️ Límite de velocidad excedido. Por favor, intenta de nuevo en un momento."
        except openai.error.AuthenticationError:
            return "❌ Error de autenticación. Por favor, verifica tu clave API."
        except openai.error.APIError:
            return "❌ Error en la API de OpenAI. Por favor, intenta más tarde."
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return "❌ Ocurrió un error al procesar tu solicitud. Por favor, intenta de nuevo."
