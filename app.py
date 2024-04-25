from contextlib import asynccontextmanager
from fastapi import FastAPI
from aiogram import types
from apps.common.midlleware import MessageMiddleware, CallbackMiddleware
from apps.common.settings import settings
import uvicorn
from apps.core.handlers import coreRouter
from apps.admin.handlers import adminRouter
from bot import dp, bot
from apps.subscription.handlers import subscriptionRouter
from apps.admin.views import router
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from celery import Celery
from fastapi import Request
import logging


celery = Celery(
    'tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

WEBHOOK_PATH = f"/bot/{settings.BOT_TOKEN}"
WEBHOOK_URL = settings.WEB_URL + WEBHOOK_PATH


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhookInfo = await bot.get_webhook_info()
    dp.include_router(adminRouter)
    dp.include_router(subscriptionRouter)
    dp.include_router(coreRouter)
    dp.message.middleware(MessageMiddleware())
    dp.callback_query.middleware(CallbackMiddleware())

    if webhookInfo.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )

    yield

    await dp.storage.close()
    await bot.delete_webhook(drop_pending_updates=True)


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="layout/static"), name="static")

app.include_router(router, prefix="/moderator")

@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):
    tgUpdate = types.Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, tgUpdate)


add_pagination(app)


if __name__ == "__main__":
    uvicorn.run("app:app", host='0.0.0.0', port=8005, reload=False, workers=2)