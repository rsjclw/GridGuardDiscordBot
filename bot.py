import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from config import DISCORD_BOT_TOKEN

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True  # 👈 REQUIRED for !hello
bot = commands.Bot(command_prefix='!', intents=intents)

# Event to signal bot readiness
bot_ready = asyncio.Event()

@bot.command(name='hello')
async def hello(ctx, *, message: str = None):
    """Responds with the user's message and channel info"""
    if message:
        response = f"📝 Your message: {message}\n"
        response += f"📌 Channel ID: `{ctx.channel.id}`"
        await ctx.send(response)
    else:
        await ctx.send("👋 Please provide a message after !hello")

@bot.tree.command(name="register_grid", description="Register a new grid with the specified ID")
@app_commands.describe()
async def register_grid(interaction: discord.Interaction):
    """Register a new grid with the specified ID"""
    # Here you can add your logic to handle the grid registration
    # For now, we'll just send a confirmation message
    grid_id = interaction.channel
    await interaction.response.send_message(
        f"✅ Successfully registered grid with ID: `{grid_id}`",
        ephemeral=True  # Only visible to the user who used the command
    )

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (id={bot.user.id})")
    # Print guilds & channels for debug
    for guild in bot.guilds:
        print(f"Guild: {guild.name} ({guild.id})")
        for ch in guild.text_channels:
            print(f"  - {ch.name} ({ch.id})")
    # Sync slash commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
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
