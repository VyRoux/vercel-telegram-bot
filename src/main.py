"""
MulyonoW Bot — Telegram Utility Bot
Entry point untuk Vercel serverless function & local dev.
"""

import asyncio
import logging
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram import Update
from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv

# Load .env from project root (mulyonow-bot/)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN")
ENV = os.getenv("ENV", "development")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN belum di-set di .env!")

# Lazy import handlers
from src.handlers import start, help_command

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Telegram Application ───────────────────────────────────────────────
ptb_app = Application.builder().token(BOT_TOKEN).build()
ptb_app.add_handler(CommandHandler("start", start))
ptb_app.add_handler(CommandHandler("help", help_command))

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"


# ── Local Development (polling) ────────────────────────────────────────
async def run_local():
    """Run bot with polling for local development."""
    logger.info("Starting MulyonoW Bot in LOCAL mode (polling)...")
    async with ptb_app:
        await ptb_app.initialize()
        await ptb_app.start()
        await ptb_app.updater.start_polling(drop_pending_updates=True)
        logger.info("Bot is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(3600)


# ── Entry Point ────────────────────────────────────────────────────────
if __name__ == "__main__":
    if ENV == "development":
        asyncio.run(run_local())
    else:
        from aiohttp import web

        async def health(request):
            return web.json_response({"status": "ok"})

        async def webhook_handler(request):
            try:
                data = await request.json()
                update = Update.de_json(data, ptb_app.bot)
                await ptb_app.process_update(update)
            except Exception as e:
                logger.error(f"Error: {e}")
            return web.Response(text="ok")

        async def set_webhook(request):
            base = str(request.url).split("/set-webhook")[0]
            result = await ptb_app.bot.set_webhook(url=base + WEBHOOK_PATH)
            return web.json_response({"ok": result})

        app = web.Application()
        app.router.add_get("/", health)
        app.router.add_get("/set-webhook", set_webhook)
        app.router.add_post(WEBHOOK_PATH, webhook_handler)

        logger.info("Starting in PRODUCTION mode (webhook)...")
        web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
