"""Admin system for MulyonoW Bot using Supabase."""

from telegram import Update
from telegram.ext import ContextTypes

from utils.db import supabase

# Owner ID (hardcoded fallback)
OWNER_ID = 7265116685  # Ganti dengan user ID kamu


async def _is_admin(user_id: int) -> bool:
    """Check if user is admin via Supabase."""
    if user_id == OWNER_ID:
        return True
    try:
        result = supabase.table("bot_users").select("is_admin").eq("user_id", user_id).execute()
        if result.data and result.data[0].get("is_admin"):
            return True
    except Exception:
        pass
    return False


# ── Admin Commands ─────────────────────────────────────────────────────

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/admin — Cek status admin & info bot."""
    user = update.effective_user
    is_admin = await _is_admin(user.id)

    if user.id == OWNER_ID:
        status = "OWNER"
    elif is_admin:
        status = "ADMIN"
    else:
        status = "USER"

    await update.message.reply_text(
        f"Admin Check\n\n"
        f"Status: {status}\n"
        f"User ID: {user.id}\n"
        f"Username: @{user.username or 'N/A'}\n"
        f"Name: {user.first_name} {user.last_name or ''}"
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/stats — Statistik bot (admin only)."""
    user = update.effective_user
    if not await _is_admin(user.id):
        await update.message.reply_text("Command ini hanya untuk admin.")
        return

    try:
        users_result = supabase.table("bot_users").select("user_id", count="exact").execute()
        total_users = users_result.count or 0

        banned_result = supabase.table("bot_users").select("user_id", count="exact").eq("is_banned", True).execute()
        total_banned = banned_result.count or 0

        stats_result = supabase.table("bot_stats").select("id", count="exact").execute()
        total_commands = stats_result.count or 0

        await update.message.reply_text(
            f"Statistik MulyonoW Bot\n\n"
            f"Total Users: {total_users}\n"
            f"Banned: {total_banned}\n"
            f"Total Commands: {total_commands}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/broadcast <pesan> — Kirim pesan ke semua user (admin only)."""
    user = update.effective_user
    if not await _is_admin(user.id):
        await update.message.reply_text("Command ini hanya untuk admin.")
        return

    if not context.args:
        await update.message.reply_text(
            "Cara pakai: /broadcast <pesan>\n"
            "Contoh: /broadcast Bot akan maintenance jam 22:00"
        )
        return

    message = " ".join(context.args)

    try:
        result = supabase.table("bot_users").select("user_id").eq("is_banned", False).execute()
        users = result.data or []

        if not users:
            await update.message.reply_text("Tidak ada user di database.")
            return

        sent = 0
        failed = 0
        bot = context.bot

        await update.message.reply_text(f"Mengirim broadcast ke {len(users)} user...")

        for u in users:
            try:
                await bot.send_message(
                    chat_id=u["user_id"],
                    text=f"BROADCAST\n\n{message}"
                )
                sent += 1
            except Exception:
                failed += 1

        await update.message.reply_text(
            f"Broadcast Selesai!\n\n"
            f"Terkirim: {sent}\n"
            f"Gagal: {failed}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/ban <user_id> — Ban user dari bot (admin only)."""
    user = update.effective_user
    if not await _is_admin(user.id):
        await update.message.reply_text("Command ini hanya untuk admin.")
        return

    if not context.args:
        await update.message.reply_text(
            "Cara pakai: /ban <user_id>\n"
            "Contoh: /ban 123456789"
        )
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("User ID harus angka.")
        return

    if target_id == OWNER_ID:
        await update.message.reply_text("Tidak bisa ban owner!")
        return

    try:
        existing = supabase.table("bot_users").select("user_id").eq("user_id", target_id).execute()
        if not existing.data:
            await update.message.reply_text(f"User {target_id} tidak ditemukan di database.")
            return

        supabase.table("bot_users").update({"is_banned": True}).eq("user_id", target_id).execute()
        await update.message.reply_text(f"User {target_id} telah di-ban.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/unban <user_id> — Unban user (admin only)."""
    user = update.effective_user
    if not await _is_admin(user.id):
        await update.message.reply_text("Command ini hanya untuk admin.")
        return

    if not context.args:
        await update.message.reply_text("Cara pakai: /unban <user_id>\nContoh: /unban 123456789")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("User ID harus angka.")
        return

    try:
        supabase.table("bot_users").update({"is_banned": False}).eq("user_id", target_id).execute()
        await update.message.reply_text(f"User {target_id} telah di-unban.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/addadmin <user_id> — Tambah admin baru (owner only)."""
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("Command ini hanya untuk owner.")
        return

    if not context.args:
        await update.message.reply_text("Cara pakai: /addadmin <user_id>\nContoh: /addadmin 987654321")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("User ID harus angka.")
        return

    try:
        supabase.table("bot_users").upsert({
            "user_id": target_id,
            "is_admin": True,
        }).execute()
        await update.message.reply_text(f"User {target_id} sekarang adalah admin.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
