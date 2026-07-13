import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from handlers import Handlers
from config import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Initialize bot with aiogram 3.x
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

# Initialize handlers
handlers = Handlers(OPENAI_API_KEY)

@dp.message(Command("start"))
async def start_command(message: Message):
    """Handle /start command"""
    welcome_text = (
        "🤖 *Welcome to Stakefields9 Bot!*\n\n"
        "I'm your AI-powered assistant that can help you with various tasks:\n"
        "• Answer questions on any topic\n"
        "• Write and rewrite text, emails, and messages\n"
        "• Summarize long text\n"
        "• Translate text into different languages\n"
        "• Generate ideas, code, and creative content\n\n"
        "📝 *Available Commands:*\n"
        "/help - Show this help message\n"
        "/clear - Clear chat history\n"
        "/new - Start a new conversation\n\n"
        "💡 *Tip:* You can also use me for natural conversations!\n"
        "Just send me a message and I'll respond."
    )
    
    # Create inline keyboard
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="💬 Help", callback_data="help"))
    builder.add(types.InlineKeyboardButton(text="🔄 New Chat", callback_data="new_chat"))
    builder.add(types.InlineKeyboardButton(text="❓ About", callback_data="about"))
    builder.adjust(2)
    
    await message.reply(
        welcome_text,
        reply_markup=builder.as_markup()
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    """Handle /help command"""
    help_text = (
        "🤖 *Stakefields9 Bot Help*\n\n"
        "*Commands:*\n"
        "/start - Start the bot and see welcome message\n"
        "/help - Show this help message\n"
        "/clear - Clear your chat history\n"
        "/new - Start a new conversation\n\n"
        "*Features:*\n"
        "• Natural conversations with AI\n"
        "• Text writing and rewriting\n"
        "• Text summarization\n"
        "• Language translation\n"
        "• Code generation\n"
        "• Creative content creation\n\n"
        "*How to use:*\n"
        "Simply send me a message, and I'll respond intelligently.\n"
        "For specific tasks, just describe what you need!"
    )
    
    await message.reply(help_text)

@dp.message(Command("clear"))
async def clear_command(message: Message):
    """Handle /clear command"""
    user_id = message.from_user.id
    handlers.clear_history(user_id)
    await message.reply("✅ Chat history cleared! You can start fresh.")

@dp.message(Command("new"))
async def new_command(message: Message):
    """Handle /new command"""
    user_id = message.from_user.id
    handlers.new_conversation(user_id)
    await message.reply("🔄 New conversation started! Let's chat!")

@dp.callback_query()
async def handle_callbacks(callback_query: types.CallbackQuery):
    """Handle inline keyboard callbacks"""
    user_id = callback_query.from_user.id
    
    if callback_query.data == "help":
        await help_command(callback_query.message)
    
    elif callback_query.data == "new_chat":
        handlers.new_conversation(user_id)
        await callback_query.message.reply("🔄 New conversation started!")
    
    elif callback_query.data == "about":
        about_text = (
            "ℹ️ *About Stakefields9 Bot*\n\n"
            "This bot uses OpenAI's powerful language model to help you with various tasks.\n\n"
            "• *Developer:* Stakefields\n"
            "• *Powered by:* OpenAI GPT-3.5-turbo\n"
            "• *Version:* 2.0.0\n\n"
            "I'm here to help with your daily tasks, creative projects, and information needs!"
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
            "❌ Sorry, I encountered an error while processing your request.\n"
            "Please try again or use /clear to reset the conversation."
        )
        await message.reply(error_message)

async def main():
    """Main function to start the bot"""
    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
