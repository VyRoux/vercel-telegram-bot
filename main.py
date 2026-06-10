"""
MulyonoW Bot — Telegram Utility Bot
Entry point untuk local dev (polling) & production (webhook via aiohttp).
"""

import asyncio
import logging
import os

from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN")
ENV = os.getenv("ENV", "development")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN belum di-set di .env!")

import utils.db  # noqa: F401

from telegram import Update
from telegram.ext import Application, CommandHandler

from handlers import (
    start, help_command,
    qr_command, calc_command, short_command,
    tr_command, tre_command,
    b64e_command, b64d_command,
    pwd_command, hash_command, crack_command,
    whois_command, ip_command,
    report_command, bug_command,
)
from admin import (
    admin_command, stats_command, broadcast_command,
    ban_command, unban_command, addadmin_command,
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Telegram Application ───────────────────────────────────────────────
ptb_app = Application.builder().token(BOT_TOKEN).build()

# Admin
ptb_app.add_handler(CommandHandler("admin", admin_command))
ptb_app.add_handler(CommandHandler("stats", stats_command))
ptb_app.add_handler(CommandHandler("broadcast", broadcast_command))
ptb_app.add_handler(CommandHandler("ban", ban_command))
ptb_app.add_handler(CommandHandler("unban", unban_command))
ptb_app.add_handler(CommandHandler("addadmin", addadmin_command))

# Bug Report
ptb_app.add_handler(CommandHandler("report", report_command))
ptb_app.add_handler(CommandHandler("bug", bug_command))

# Utilities
ptb_app.add_handler(CommandHandler("start", start))
ptb_app.add_handler(CommandHandler("help", help_command))
ptb_app.add_handler(CommandHandler("qr", qr_command))
ptb_app.add_handler(CommandHandler("calc", calc_command))
ptb_app.add_handler(CommandHandler("short", short_command))
ptb_app.add_handler(CommandHandler("tr", tr_command))
ptb_app.add_handler(CommandHandler("tre", tre_command))
ptb_app.add_handler(CommandHandler("b64e", b64e_command))
ptb_app.add_handler(CommandHandler("b64d", b64d_command))
ptb_app.add_handler(CommandHandler("pwd", pwd_command))
ptb_app.add_handler(CommandHandler("hash", hash_command))
ptb_app.add_handler(CommandHandler("crack", crack_command))
ptb_app.add_handler(CommandHandler("whois", whois_command))
ptb_app.add_handler(CommandHandler("ip", ip_command))

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"

# ── Vercel / Production: aiohttp app (top-level) ──────────────────────
from aiohttp import web

async def health(request):
    return web.json_response({"status": "ok", "bot": "MulyonoW"})

async def webhook(request):
    try:
        data = await request.json()
        update = Update.de_json(data, ptb_app.bot)
        await ptb_app.process_update(update)
    except Exception as e:
        logger.error(f"Error: {e}")
    return web.Response(text="ok")

async def set_wh(request):
    base = str(request.url).split("/set-webhook")[0]
    url = base + WEBHOOK_PATH
    result = await ptb_app.bot.set_webhook(url=url)
    return web.json_response({"ok": result, "url": url})

app = web.Application()
app.router.add_get("/", health)
app.router.add_get("/set-webhook", set_wh)
app.router.add_post(WEBHOOK_PATH, webhook)


# ── Local Development (polling) ────────────────────────────────────────
async def run_local():
    logger.info("Starting MulyonoW Bot in LOCAL mode (polling)...")
    async with ptb_app:
        await ptb_app.initialize()
        await ptb_app.start()
        await ptb_app.updater.start_polling(drop_pending_updates=True)
        logger.info("Bot is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    if ENV == "development":
        asyncio.run(run_local())
    else:
        web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
