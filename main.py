import asyncio
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from config import HOST, PORT
from bot import start_bot, close_bot
from routes import send_alert, AlertPayload

# FastAPI app
app = FastAPI()

# Register routes
@app.post("/send_alert")
async def send_alert_endpoint(payload: AlertPayload):
    return await send_alert(payload, None)

# Lifespan: start/stop discord bot with FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start discord bot as background task
    bot_task = asyncio.create_task(start_bot())
    try:
        yield
    finally:
        # Attempt graceful shutdown
        try:
            await close_bot()
        except Exception:
            pass
        # Wait for the task to finish
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

# Attach lifespan to app
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, lifespan="on", reload=False)
