import discord
from fastapi import Request, HTTPException
from pydantic import BaseModel
from bot import get_bot, wait_for_bot_ready
from config import DEFAULT_CHANNEL_ID

class AlertPayload(BaseModel):
    message: str
    channel_id: int | None = None  # optional; if omitted uses DEFAULT_CHANNEL_ID

async def send_alert(payload: AlertPayload, request: Request):
    # Wait until bot is ready
    await wait_for_bot_ready()
    
    bot = await get_bot()

    # Determine target channel id
    channel_id = payload.channel_id
    if channel_id is None:
        if DEFAULT_CHANNEL_ID:
            try:
                channel_id = int(DEFAULT_CHANNEL_ID)
            except ValueError:
                raise HTTPException(status_code=400, detail="DEFAULT_CHANNEL_ID invalid")
        else:
            raise HTTPException(status_code=400, detail="channel_id missing and DEFAULT_CHANNEL_ID not set")

    # Try cached channel first
    channel = bot.get_channel(channel_id)
    if channel is None:
        # Fallback to fetching from API (slower but reliable)
        try:
            channel = await bot.fetch_channel(channel_id)
        except discord.NotFound:
            raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")
        except discord.HTTPException as e:
            raise HTTPException(status_code=502, detail=f"Discord API error: {e}")

    # Send message
    try:
        await channel.send(payload.message, allowed_mentions=discord.AllowedMentions(everyone=True))
    except discord.Forbidden:
        raise HTTPException(status_code=403, detail="Bot has no permission to send messages in that channel")
    except discord.HTTPException as e:
        raise HTTPException(status_code=502, detail=f"Failed to send message: {e}")

    return {"status": "ok", "sent": payload.message, "channel_id": channel_id}
