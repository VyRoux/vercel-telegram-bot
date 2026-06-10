"""
MulyonoW Bot — Telegram Utility Bot
Entry point untuk local dev (polling) & production (webhook via ASGI).
"""

import asyncio
import json
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

ptb_app.add_handler(CommandHandler("admin", admin_command))
ptb_app.add_handler(CommandHandler("stats", stats_command))
ptb_app.add_handler(CommandHandler("broadcast", broadcast_command))
ptb_app.add_handler(CommandHandler("ban", ban_command))
ptb_app.add_handler(CommandHandler("unban", unban_command))
ptb_app.add_handler(CommandHandler("addadmin", addadmin_command))
ptb_app.add_handler(CommandHandler("report", report_command))
ptb_app.add_handler(CommandHandler("bug", bug_command))
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


# ── ASGI App (for Vercel) ──────────────────────────────────────────────
async def send_response(send, status, body, content_type="text/plain"):
    await send({"type": "http.response.start", "status": status,
                "headers": [[b"content-type", content_type.encode()]],
                "trailers": False})
    await send({"type": "http.response.body", "body": body.encode()})


async def app(scope, receive, send):
    if scope["type"] != "http":
        return

    path = scope["path"]
    method = scope["method"]

    # Read body for POST requests
    body = b""
    if method == "POST":
        while True:
            msg = await receive()
            body += msg.get("body", b"")
            if not msg.get("more_body", False):
                break

    # Health check
    if path == "/" and method == "GET":
        resp = json.dumps({"status": "ok", "bot": "MulyonoW"})
        await send_response(send, 200, resp, "application/json")

    # Set webhook
    elif path == "/set-webhook" and method == "GET":
        raw_path = scope.get("raw_path", b"").decode() or path
        qs = scope.get("query_string", b"").decode()
        base = f"https://{scope['server'][0]}" if scope.get("server") else ""
        url = base + WEBHOOK_PATH
        try:
            result = await ptb_app.bot.set_webhook(url=url)
            resp = json.dumps({"ok": result, "url": url})
        except Exception as e:
            resp = json.dumps({"ok": False, "error": str(e)})
        await send_response(send, 200, resp, "application/json")

    # Webhook
    elif path == WEBHOOK_PATH and method == "POST":
        try:
            data = json.loads(body)
            update = Update.de_json(data, ptb_app.bot)
            await ptb_app.process_update(update)
        except Exception as e:
            logger.error(f"Webhook error: {e}")
        await send_response(send, 200, "ok")

    else:
        await send_response(send, 404, "Not found")


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
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
