import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables!")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in environment variables!")

logger = logging.getLogger(__name__)
logger.info("Configuration loaded successfully")
