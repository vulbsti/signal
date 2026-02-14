import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")

# ADK backend
ADK_HOST = os.getenv("ADK_HOST", "127.0.0.1")
ADK_PORT = int(os.getenv("ADK_PORT", "3030"))
ADK_BASE_URL = f"http://{ADK_HOST}:{ADK_PORT}"
ADK_APP_NAME = "signal_agent"

# Model names
FLASH_MODEL = "gemini-3-flash-preview"
PRO_MODEL = "gemini-3-pro-preview"

# Scoring
SCORE_THRESHOLD = 60
BATCH_SIZE = 20

# Paths
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory_data")
