from fastapi import FastAPI
from aiogram import types, executor
from bot import bot
from dotenv import load_dotenv
import os
from aiogram.dispatcher.dispatcher import Dispatcher, Bot
import uvicorn

from core.handlers import dp
from admin.handlers import dp
from bot import dp
from imageai.handlers import dp

from admin.views import router

from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="layout/static"), name="static")

app.include_router(router, prefix="/admin")

WEBHOOK_PATH = f"/bot/{os.environ.get('BOT_TOKEN')}"
WEBHOOK_URL = "https://535d-213-230-82-9.ngrok-free.app" + WEBHOOK_PATH


@app.on_event("startup")
async def on_startup():
    webhookInfo = await bot.get_webhook_info()

    if webhookInfo.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    tgUpdate = types.Update(**update)

    Dispatcher.set_current(dp)
    Bot.set_current(bot)

    await dp.process_update(tgUpdate)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()


if __name__ == "__main__":
    
    uvicorn.run("app:app", host='0.0.0.0', port=8000, reload=True, workers=3)
