import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from handlers import Handlers
from config import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Initialize bot with aiogram 3.x
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

# Initialize handlers
handlers = Handlers(OPENAI_API_KEY)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

def run_health_server():
    """Run a simple HTTP server for health checks"""
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health check server running on port {port}")
    server.serve_forever()

@dp.message(Command("start"))
async def start_command(message: Message):
    """Handle /start command with Spanish welcome message"""
    welcome_text = (
        "🤖 *¡Bienvenido a Stakefields9 Bot!*\n\n"
        "Soy tu asistente impulsado por IA que puede ayudarte con diversas tareas:\n"
        "• Responder preguntas sobre cualquier tema\n"
        "• Escribir y reescribir textos, correos electrónicos y mensajes\n"
        "• Resumir textos largos\n"
        "• Traducir texto a diferentes idiomas\n"
        "• Generar ideas, código y contenido creativo\n\n"
        "📝 *Comandos Disponibles:*\n"
        "/help - Mostrar este mensaje de ayuda\n"
        "/clear - Borrar el historial de la conversación\n"
        "/new - Iniciar una nueva conversación\n\n"
        "💡 *Consejo:* ¡También puedes usarme para conversaciones naturales!\n"
        "Solo envíame un mensaje y te responderé."
    )
    
    # Create inline keyboard
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="💬 Ayuda", callback_data="help"))
    builder.add(types.InlineKeyboardButton(text="🔄 Nueva Conversación", callback_data="new_chat"))
    builder.add(types.InlineKeyboardButton(text="❓ Acerca de", callback_data="about"))
    builder.adjust(2)
    
    await message.reply(
        welcome_text,
        reply_markup=builder.as_markup()
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    """Handle /help command in Spanish"""
    help_text = (
        "🤖 *Ayuda de Stakefields9 Bot*\n\n"
        "*Comandos:*\n"
        "/start - Iniciar el bot y ver mensaje de bienvenida\n"
        "/help - Mostrar este mensaje de ayuda\n"
        "/clear - Borrar el historial de la conversación\n"
        "/new - Iniciar una nueva conversación\n\n"
        "*Características:*\n"
        "• Conversaciones naturales con IA\n"
        "• Escritura y reescritura de textos\n"
        "• Resumen de textos\n"
        "• Traducción de idiomas\n"
        "• Generación de código\n"
        "• Creación de contenido creativo\n\n"
        "*Cómo usar:*\n"
        "¡Simplemente envíame un mensaje y te responderé inteligentemente!\n"
        "Para tareas específicas, ¡solo describe lo que necesitas!"
    )
    
    await message.reply(help_text)

@dp.message(Command("clear"))
async def clear_command(message: Message):
    """Handle /clear command in Spanish"""
    user_id = message.from_user.id
    handlers.clear_history(user_id)
    await message.reply("✅ ¡Historial de conversación borrado! Puedes empezar de nuevo.")

@dp.message(Command("new"))
async def new_command(message: Message):
    """Handle /new command in Spanish"""
    user_id = message.from_user.id
    handlers.new_conversation(user_id)
    await message.reply("🔄 ¡Nueva conversación iniciada! ¡Hablemos!")

@dp.callback_query()
async def handle_callbacks(callback_query: types.CallbackQuery):
    """Handle inline keyboard callbacks in Spanish"""
    user_id = callback_query.from_user.id
    
    if callback_query.data == "help":
        await help_command(callback_query.message)
    
    elif callback_query.data == "new_chat":
        handlers.new_conversation(user_id)
        await callback_query.message.reply("🔄 ¡Nueva conversación iniciada!")
    
    elif callback_query.data == "about":
        about_text = (
            "ℹ️ *Acerca de Stakefields9 Bot*\n\n"
            "Este bot utiliza el potente modelo de lenguaje de OpenAI para ayudarte con diversas tareas.\n\n"
            "• *Desarrollador:* Stakefields\n"
            "• *Impulsado por:* OpenAI GPT-3.5-turbo\n"
            "• *Versión:* 2.0.0\n\n"
            "¡Estoy aquí para ayudarte con tus tareas diarias, proyectos creativos y necesidades de información!"
        )
        await callback_query.message.reply(about_text)
    
    await callback_query.answer()

@dp.message()
async def handle_message(message: Message):
    """Handle all other messages"""
    user_id = message.from_user.id
    user_input = message.text
    
    if not user_input:
        return
    
    try:
        # Show typing indicator
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        
        # Get response from OpenAI
        response = await handlers.get_openai_response(user_id, user_input)
        
        # Send response (split if too long)
        if len(response) > 4096:
            for chunk in [response[i:i+4096] for i in range(0, len(response), 4096)]:
                await message.reply(chunk)
        else:
            await message.reply(response)
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        error_message = (
            "❌ Lo siento, encontré un error al procesar tu solicitud.\n"
            "Por favor, intenta de nuevo o usa /clear para reiniciar la conversación."
        )
        await message.reply(error_message)

async def main():
    """Main function to start the bot"""
    try:
        # Start health check server in a separate thread
        health_thread = threading.Thread(target=run_health_server, daemon=True)
        health_thread.start()
        
        logger.info("Starting Telegram bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
