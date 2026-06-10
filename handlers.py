"""Bot command handlers for MulyonoW Bot."""

from telegram import Update
from telegram.ext import ContextTypes

from utils.helpers import (
    gen_qr, calc_expression, short_url, translate_text,
    b64_encode, b64_decode,
    gen_password, gen_hash, crack_hash,
    whois_lookup, ip_info,
)

# ── Bug Report Target ──────────────────────────────────────────────────
BUG_REPORT_CHAT_ID = -1003943670097
BUG_REPORT_TOPIC_ID = None  # None = kirim ke general chat grup


# ── Basic ──────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start — Perkenalan bot."""
    user = update.effective_user
    await update.message.reply_text(
        f"Halo, {user.first_name}!\n\n"
        f"Selamat datang di MulyonoW Bot — bot utilitas yang siap membantumu.\n\n"
        f"Ketik /help untuk daftar perintah.\n\n"
        f"Mulia di era sekarang"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help — Tampilkan daftar perintah."""
    await update.message.reply_text(
        "Daftar Perintah MulyonoW Bot\n\n"
        "Utilitas:\n"
        "/qr <teks> — Buat QR Code\n"
        "/calc <ekspresi> — Kalkulator\n"
        "/short <url> — Perpendek URL\n"
        "/tr <teks> — Terjemah (auto -> Indonesia)\n"
        "/tre <teks> — Translate to English\n"
        "/b64e <teks> — Base64 Encode\n"
        "/b64d <teks> — Base64 Decode\n\n"
        "Security:\n"
        "/pwd [panjang] — Generate Password (default: 16)\n"
        "/hash <teks> — Generate Hash (MD5/SHA1/SHA256/SHA512)\n"
        "/crack <hash> — Crack/Reverse Hash\n\n"
        "Network:\n"
        "/whois <domain> — Info Domain/IP\n"
        "/ip <alamat IP> — Info IP Address\n\n"
        "Admin:\n"
        "/admin — Cek status admin\n"
        "/stats — Statistik bot\n"
        "/broadcast <pesan> — Broadcast ke semua user\n"
        "/ban <user_id> — Ban user\n"
        "/unban <user_id> — Unban user\n"
        "/addadmin <user_id> — Tambah admin (owner only)\n\n"
        "Feedback:\n"
        "/report <pesan> — Kirim bug report ke developer\n"
        "/bug <pesan> — Alias untuk /report\n\n"
        "Lainnya:\n"
        "/start — Mulai bot\n"
        "/help — Tampilkan bantuan ini\n\n"
        "Fitur baru akan ditambahkan secara berkala!"
    )


# ── QR Code ────────────────────────────────────────────────────────────

async def qr_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/qr <teks> — Generate QR Code."""
    if not context.args:
        await update.message.reply_text(
            "Cara pakai: /qr <teks atau URL>\n"
            "Contoh: /qr https://google.com atau /qr Halo Dunia"
        )
        return
    text = " ".join(context.args)
    await update.message.reply_text("Membuat QR Code...")
    try:
        buf = gen_qr(text)
        await update.message.reply_photo(
            photo=buf,
            caption=f"QR Code untuk: {text[:50]}"
        )
    except Exception as e:
        await update.message.reply_text(f"Gagal membuat QR: {e}")


# ── Calculator ─────────────────────────────────────────────────────────

async def calc_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/calc <ekspresi> — Kalkulator."""
    if not context.args:
        await update.message.reply_text(
            "Cara pakai: /calc <ekspresi matematika>\n"
            "Contoh:\n"
            "/calc 2 + 2\n"
            "/calc 10 * 5 - 3\n"
            "/calc 2 ^ 10 (pangkat)\n"
            "/calc (4 + 2) * 3"
        )
        return
    expr = " ".join(context.args)
    result = calc_expression(expr)
    await update.message.reply_text(result)


# ── URL Shortener ─────────────────────────────────────────────────────

async def short_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/short <url> — Perpendek URL."""
    if not context.args:
        await update.message.reply_text(
            "Cara pakai: /short <URL>\n"
            "Contoh: /short https://example.com/very/long/url"
        )
        return
    url = " ".join(context.args)
    await update.message.reply_text("Memperpendek URL...")
    result = await short_url(url)
    await update.message.reply_text(result)


# ── Translate ─────────────────────────────────────────────────────────

async def tr_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/tr <teks> — Terjemahkan ke Indonesia."""
    text = _get_text_from_message(update, context)
    if not text:
        await update.message.reply_text(
            "Cara pakai: /tr <teks> atau reply pesan dengan /tr\n"
            "Contoh: /tr Hello world"
        )
        return
    await update.message.reply_text("Menerjemahkan...")
    result = await translate_text(text, dest="id")
    await update.message.reply_text(result)


async def tre_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/tre <teks> — Translate to English."""
    text = _get_text_from_message(update, context)
    if not text:
        await update.message.reply_text(
            "Cara pakai: /tre <teks> atau reply pesan dengan /tre\n"
            "Contoh: /tre Halo dunia"
        )
        return
    await update.message.reply_text("Translating...")
    result = await translate_text(text, dest="en")
    await update.message.reply_text(result)


# ── Base64 ────────────────────────────────────────────────────────────

async def b64e_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/b64e <teks> — Base64 Encode."""
    text = _get_text_from_message(update, context)
    if not text:
        await update.message.reply_text(
            "Cara pakai: /b64e <teks> atau reply pesan dengan /b64e\n"
            "Contoh: /b64e Halo"
        )
        return
    result = b64_encode(text)
    await update.message.reply_text(result)


async def b64d_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/b64d <teks> — Base64 Decode."""
    text = _get_text_from_message(update, context)
    if not text:
        await update.message.reply_text(
            "Cara pakai: /b64d <base64 string> atau reply pesan dengan /b64d\n"
            "Contoh: /b64d SGFsbG8="
        )
        return
    result = b64_decode(text)
    await update.message.reply_text(result)


# ── Password Generator ────────────────────────────────────────────────

async def pwd_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/pwd [panjang] — Generate secure password."""
    length = 16
    if context.args:
        try:
            length = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Panjang harus angka. Contoh: /pwd 20")
            return
    result = gen_password(length)
    await update.message.reply_text(result)


# ── Hash ──────────────────────────────────────────────────────────────

async def hash_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/hash <teks> — Generate hash (MD5, SHA1, SHA256, SHA512)."""
    text = _get_text_from_message(update, context)
    if not text:
        await update.message.reply_text(
            "Cara pakai: /hash <teks> atau reply pesan dengan /hash\n"
            "Contoh: /hash password123"
        )
        return
    result = gen_hash(text)
    await update.message.reply_text(result)


async def crack_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/crack <hash> — Crack/reverse hash."""
    if not context.args:
        await update.message.reply_text(
            "Cara pakai: /crack <hash_value>\n"
            "Contoh: /crack 5f4dcc3b5aa765d61d8327deb882cf99\n"
            "Support: MD5, SHA1, SHA256, SHA512"
        )
        return
    hash_value = context.args[0]
    await update.message.reply_text("Mencoba crack hash...")
    result = await crack_hash(hash_value)
    await update.message.reply_text(result)


# ── Network ───────────────────────────────────────────────────────────

async def whois_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/whois <domain> — Info domain."""
    if not context.args:
        await update.message.reply_text(
            "Cara pakai: /whois <domain>\nContoh: /whois google.com"
        )
        return
    domain = context.args[0]
    await update.message.reply_text("Mencari info domain...")
    result = await whois_lookup(domain)
    await update.message.reply_text(result)


async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/ip <alamat_ip> — Info IP address."""
    if not context.args:
        await update.message.reply_text(
            "Cara pakai: /ip <alamat IP>\nContoh: /ip 8.8.8.8"
        )
        return
    ip = context.args[0]
    await update.message.reply_text("Mencari info IP...")
    result = await ip_info(ip)
    await update.message.reply_text(result)


# ── Bug Report ─────────────────────────────────────────────────────────

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/report <pesan> — Kirim bug report ke developer."""
    if not context.args:
        await update.message.reply_text(
            "Cara pakai: /report <pesan bug>\n"
            "Contoh: /report /qr error saat bikin QR code\n"
            "Atau reply pesan error dengan /report"
        )
        return

    user = update.effective_user
    text = " ".join(context.args)

    report_text = (
        "BUG REPORT\n\n"
        f"From: {user.first_name} (ID: {user.id})\n"
        f"Username: @{user.username or 'N/A'}\n\n"
        f"Pesan:\n{text}"
    )

    try:
        kwargs = {"chat_id": BUG_REPORT_CHAT_ID, "text": report_text}
        if BUG_REPORT_TOPIC_ID:
            kwargs["message_thread_id"] = BUG_REPORT_TOPIC_ID
        await context.bot.send_message(**kwargs)
        await update.message.reply_text(
            "Bug report terkirim!\n\n"
            "Terima kasih, developer akan segera memeriksa."
        )
    except Exception as e:
        await update.message.reply_text(f"Gagal mengirim report: {e}")


async def bug_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/bug <pesan> — Alias untuk /report."""
    await report_command(update, context)


# ── Helper ─────────────────────────────────────────────────────────────

def _get_text_from_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    """Get text from command args or from replied message."""
    if context.args:
        return " ".join(context.args)
    if update.message.reply_to_message and update.message.reply_to_message.text:
        return update.message.reply_to_message.text
    return None
