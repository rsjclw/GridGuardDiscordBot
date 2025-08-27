import os
import dotenv

dotenv.load_dotenv()

# Discord configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DEFAULT_CHANNEL_ID = os.getenv("DEFAULT_CHANNEL_ID")

# API configuration
HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = int(os.getenv("API_PORT", "3390"))

# Validation
if not DISCORD_BOT_TOKEN:
    raise SystemExit("Set DISCORD_BOT_TOKEN in environment")
