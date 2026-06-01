"""Bot command handlers."""

from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    await update.message.reply_text(
        f"Halo, {user.first_name}!\n\n"
        f"Selamat datang di MulyonoW Bot — bot utilitas yang siap membantumu.\n\n"
        f"Liat /help untuk daftar perintah yang tersedia.\n\n"
        f"Mulia di era sekarang",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await update.message.reply_text(
        "Daftar Perintah:\n\n"
        "/start — Mulai bot\n"
        "/help — Tampilkan bantuan\n\n"
        "Fitur utilitas akan ditambahkan segera...",
    )
