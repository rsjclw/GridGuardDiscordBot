import asyncio
import os
import logging
import httpx
from dotenv import load_dotenv
from discord import app_commands, Embed, Color, Interaction, Intents
from discord.ext import commands
from typing import Optional
from config import DISCORD_BOT_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
backend_url = os.getenv("BACKEND_URL")

# Discord bot setup
intents = Intents.default()
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
async def register_grid(interaction: Interaction):
    """Register a new grid with the specified ID"""
    grid_id = interaction.channel.name
    payload = {
        "grid_id": str(grid_id),
        "discord_channel_id": interaction.channel.id,
        "guild_id": str(interaction.guild.id) if interaction.guild else None,
        "guild_name": interaction.guild.name if interaction.guild else None
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{backend_url}/register",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully registered grid {grid_id}")
                await interaction.response.send_message(
                    f"✅ Successfully registered grid with ID: `{grid_id}`",
                    ephemeral=False
                )
            else:
                error_detail = response.json().get('detail', 'No details provided')
                logger.error(f"Failed to register grid {grid_id}: {response.text}")
                await interaction.response.send_message(
                    f"❌ Failed to register grid. Error: {error_detail}",
                    ephemeral=True
                )
    except Exception as e:
        logger.error(f"Error registering grid {grid_id}: {str(e)}")
        await interaction.response.send_message(
            "❌ An error occurred while registering the grid.",
            ephemeral=True
        )

@bot.tree.command(name="register_pond", description="Register a new pond with the specified parameters")
@app_commands.describe(
    pond_area="Area of the pond (in square meters)",
    pond_water_height="Water height of the pond (in centimeters)",
    reservoir_area="Area of the water reservoir (in square meters)",
    reservoir_water_height="Water height of the reservoir (in centimeters)"
)
async def register_pond(
    interaction: Interaction,
    pond_area: float,
    pond_water_height: float,
    reservoir_area: float,
    reservoir_water_height: float
):
    """Register a new pond with the specified parameters"""
    # Convert heights from cm to meters for volume calculation
    pond_height_m = pond_water_height / 100
    reservoir_height_m = reservoir_water_height / 100
    
    # Calculate volumes in cubic meters
    pond_volume = pond_area * pond_height_m
    reservoir_volume = reservoir_area * reservoir_height_m
    
    payload = {
        "pond_id": interaction.channel.name,
        "discord_channel_id": str(interaction.channel.id),
        "pond_area": pond_area,
        "pond_water_height": pond_water_height,
        "pond_volume": pond_volume,
        "reservoir_area": reservoir_area,
        "reservoir_water_height": reservoir_water_height,
        "reservoir_volume": reservoir_volume,
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{backend_url}/register/pond",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully registered pond in channel {interaction.channel.id}")
                
                # Create response embed
                embed = Embed(
                    title="✅ Pond Registration Successful",
                    description=f"Pond registered in channel <#{interaction.channel.id}>",
                    color=Color.green()
                )
                
                # Add fields with the provided parameters
                embed.add_field(name="🌊 Pond Area", value=f"{pond_area} m²", inline=True)
                embed.add_field(name="📏 Pond Water Height", value=f"{pond_water_height} cm", inline=True)
                embed.add_field(name="💧 Pond Volume", value=f"{pond_volume:.2f} m³", inline=True)
                embed.add_field(name="🏞️ Reservoir Area", value=f"{reservoir_area} m²", inline=True)
                embed.add_field(name="📐 Reservoir Water Height", value=f"{reservoir_water_height} cm", inline=True)
                embed.add_field(name="💦 Reservoir Volume", value=f"{reservoir_volume:.2f} m³", inline=True)
                
                await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                error_detail = response.json().get('detail', 'No details provided')
                logger.error(f"Failed to register pond: {response.text}")
                await interaction.response.send_message(
                    f"❌ Failed to register pond. Error: {error_detail}",
                    ephemeral=True
                )
    except Exception as e:
        logger.error(f"Error registering pond: {str(e)}")
        await interaction.response.send_message(
            "❌ An error occurred while registering the pond.",
            ephemeral=True
        )

@bot.tree.command(name="pond_water_level_adjust", description="Adjust the water level of the pond")
@app_commands.describe(height="New water height for the pond (in centimeters)")
async def pond_water_level_adjust(interaction: Interaction, height: float):
    """Adjust the water level of the pond"""
    payload = {
        "pond_id": str(interaction.channel.name),
        "height": height,
        "adjustment_type": "pond"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{backend_url}/water_level_adjust",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"Adjusted pond water level to {height}m in channel {interaction.channel.id}")
                
                embed = Embed(
                    title="🌊 Pond Water Level Adjusted",
                    description=f"Successfully set pond water level to **{height} cm**",
                    color=Color.blue()
                )
                embed.add_field(name="Channel", value=f"<#{interaction.channel.id}>")
                embed.add_field(name="New Height", value=f"{height} cm")
                
                await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                error_detail = response.json().get('detail', 'No details provided')
                logger.error(f"Failed to adjust pond water level: {response.text}")
                await interaction.response.send_message(
                    f"❌ Failed to adjust pond water level. Error: {error_detail}",
                    ephemeral=True
                )
    except Exception as e:
        logger.error(f"Error adjusting pond water level: {str(e)}")
        await interaction.response.send_message(
            "❌ An error occurred while adjusting the pond water level.",
            ephemeral=True
        )

@bot.tree.command(name="reservoir_water_level_adjust", description="Adjust the water level of the reservoir")
@app_commands.describe(height="New water height for the reservoir (in centimeters)")
async def reservoir_water_level_adjust(interaction: Interaction, height: float):
    """Adjust the water level of the reservoir"""
    payload = {
        "pond_id": str(interaction.channel.name),
        "height": height,
        "adjustment_type": "reservoir"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{backend_url}/water_level_adjust",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"Adjusted reservoir water level to {height}m in channel {interaction.channel.id}")
                
                embed = Embed(
                    title="🏞️ Reservoir Water Level Adjusted",
                    description=f"Successfully set reservoir water level to **{height} cm**",
                    color=Color.blue()
                )
                embed.add_field(name="Channel", value=f"<#{interaction.channel.id}>")
                embed.add_field(name="New Height", value=f"{height} cm")
                
                await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                error_detail = response.json().get('detail', 'No details provided')
                logger.error(f"Failed to adjust reservoir water level: {response.text}")
                await interaction.response.send_message(
                    f"❌ Failed to adjust reservoir water level. Error: {error_detail}",
                    ephemeral=True
                )
    except Exception as e:
        logger.error(f"Error adjusting reservoir water level: {str(e)}")
        await interaction.response.send_message(
            "❌ An error occurred while adjusting the reservoir water level.",
            ephemeral=True
        )

@bot.tree.command(name="disinfection", description="Trigger disinfection for the reservoir")
@app_commands.describe(water_height="Water height for the reservoir (in centimeters)")
async def disinfection(interaction: Interaction, water_height: float):
    """Trigger disinfection for the reservoir"""
    payload = {
        "pond_name": str(interaction.channel.name),
        "disinfection_type": "reservoir",
        "water_height": water_height
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{backend_url}/disinfect",
                json=payload,
                timeout=5
            )
            msg = response.json()['message']
            
            if response.status_code == 200:
                logger.info(f"Triggered reservoir disinfection in channel {interaction.channel.id}")
                embed = Embed(
                    title="🧴 Reservoir Disinfection",
                    description=msg,
                    color=Color.green()
                )
                await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                error_detail = response.json().get('detail', 'No details provided')
                logger.error(f"Failed to trigger reservoir disinfection: {response.text}")
                await interaction.response.send_message(
                    f"❌ Failed to start reservoir disinfection. Error: {error_detail}",
                    ephemeral=True
                )
    except Exception as e:
        logger.error(f"Error triggering reservoir disinfection: {str(e)}")
        await interaction.response.send_message(
            "❌ An error occurred while starting reservoir disinfection.",
            ephemeral=True
        )

@bot.tree.command(name="disinfection_pond", description="Trigger disinfection for the pond")
@app_commands.describe(water_height="Water height for the pond (in centimeters)")
async def disinfection_pond(interaction: Interaction, water_height: float):
    """Trigger disinfection for the pond"""
    payload = {
        "pond_name": str(interaction.channel.name),
        "disinfection_type": "pond",
        "water_height": water_height
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{backend_url}/disinfect",
                json=payload,
                timeout=5
            )
            msg = response.json()['message']
            
            if response.status_code == 200:
                logger.info(f"Triggered pond disinfection in channel {interaction.channel.id}")
                embed = Embed(
                    title="🧴 Pond Disinfection",
                    description=msg,
                    color=Color.green()
                )
                await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                error_detail = response.json().get('detail', 'No details provided')
                logger.error(f"Failed to trigger pond disinfection: {response.text}")
                await interaction.response.send_message(
                    f"❌ Failed to start pond disinfection. Error: {error_detail}",
                    ephemeral=True
                )
    except Exception as e:
        logger.error(f"Error triggering pond disinfection: {str(e)}")
        await interaction.response.send_message(
            "❌ An error occurred while starting pond disinfection.",
            ephemeral=True
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
