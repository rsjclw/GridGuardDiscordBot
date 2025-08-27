import asyncio
import discord
from config import DISCORD_BOT_TOKEN

# Discord bot setup
intents = discord.Intents.default()
bot = discord.Client(intents=intents)

# Event to signal bot readiness
bot_ready = asyncio.Event()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (id={bot.user.id})")
    # Print guilds & channels for debug
    for guild in bot.guilds:
        print(f"Guild: {guild.name} ({guild.id})")
        for ch in guild.text_channels:
            print(f"  - {ch.name} ({ch.id})")
    bot_ready.set()

async def get_bot():
    """Get the bot instance"""
    return bot

async def wait_for_bot_ready():
    """Wait until the bot is ready"""
    await bot_ready.wait()

async def start_bot():
    """Start the Discord bot"""
    await bot.start(DISCORD_BOT_TOKEN)

async def close_bot():
    """Close the Discord bot connection"""
    await bot.close()
