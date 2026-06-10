"""Utility helpers for MulyonoW Bot."""

import base64
import hashlib
import io
import random
import re
import string
import urllib.parse
import urllib.request

import httpx
import qrcode
from qrcode.constants import ERROR_CORRECT_L


# ── QR Code ────────────────────────────────────────────────────────────

def gen_qr(text: str) -> io.BytesIO:
    """Generate QR code image from text. Returns BytesIO buffer."""
    qr = qrcode.QRCode(version=1, error_correction=ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# ── Calculator ─────────────────────────────────────────────────────────

def calc_expression(expr: str) -> str:
    """Safely evaluate a math expression."""
    if not re.match(r'^[\d\s\+\-\*\/\^\(\)\.]+$', expr.strip()):
        return "Ekspresi tidak valid. Hanya angka dan + - * / ^ ( ) yang diperbolehkan."
    try:
        safe = expr.replace("^", "**")
        result = eval(safe, {"__builtins__": {}}, {})
        return f"{expr} = {result}"
    except ZeroDivisionError:
        return "Tidak bisa membagi dengan nol."
    except Exception as e:
        return f"Error: {e}"


# ── URL Shortener ─────────────────────────────────────────────────────

async def short_url(url: str) -> str:
    """Shorten URL using TinyURL API."""
    if not url.startswith("http"):
        url = "https://" + url
    api = f"http://tinyurl.com/api-create.php?url={urllib.parse.quote(url)}"
    try:
        with urllib.request.urlopen(api, timeout=10) as resp:
            short = resp.read().decode()
            return f"Short URL: {short}"
    except Exception:
        return "Gagal memperpendek URL. Pastikan URL valid."


# ── Translate ─────────────────────────────────────────────────────────

async def translate_text(text: str, dest: str = "id") -> str:
    """Translate text using Google Translate (unofficial API)."""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "auto", "tl": dest, "dt": "t", "q": text}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10)
            data = resp.json()
            translated = "".join(s[0] for s in data[0] if s[0])
            src_lang = data[2] if len(data) > 2 else "auto"
            return f"Terjemahan ({src_lang} -> {dest}):\n\n{translated}"
    except Exception:
        return "Gagal menerjemahkan. Coba lagi nanti."


# ── Base64 ────────────────────────────────────────────────────────────

def b64_encode(text: str) -> str:
    """Base64 encode."""
    encoded = base64.b64encode(text.encode()).decode()
    return f"Encoded:\n{encoded}"


def b64_decode(text: str) -> str:
    """Base64 decode."""
    try:
        decoded = base64.b64decode(text.encode()).decode()
        return f"Decoded:\n{decoded}"
    except Exception:
        return "Invalid Base64 string."


# ── Password Generator ────────────────────────────────────────────────

def gen_password(length: int = 16) -> str:
    """Generate a random secure password."""
    if length < 4:
        length = 4
    if length > 128:
        length = 128
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*()-_=+"),
    ]
    password += random.choices(chars, k=length - 4)
    random.shuffle(password)
    pwd = "".join(password)
    return f"Password Generated ({length} karakter):\n\n{pwd}\n\nSimpan di tempat yang aman!"


# ── Hash Generator ────────────────────────────────────────────────────

def gen_hash(text: str) -> str:
    """Generate MD5, SHA1, SHA256, SHA512 hashes."""
    encoded = text.encode("utf-8")
    md5 = hashlib.md5(encoded).hexdigest()
    sha1 = hashlib.sha1(encoded).hexdigest()
    sha256 = hashlib.sha256(encoded).hexdigest()
    sha512 = hashlib.sha512(encoded).hexdigest()
    return (
        f"Hash Results:\n\n"
        f"MD5:\n{md5}\n\n"
        f"SHA1:\n{sha1}\n\n"
        f"SHA256:\n{sha256}\n\n"
        f"SHA512:\n{sha512}"
    )


# ── Hash Lookup (Crack) ───────────────────────────────────────────────

async def crack_hash(hash_value: str) -> str:
    """Try to crack hash using online lookup."""
    hash_value = hash_value.strip().lower()

    hash_len = len(hash_value)
    hash_type = None
    if hash_len == 32:
        hash_type = "md5"
    elif hash_len == 40:
        hash_type = "sha1"
    elif hash_len == 64:
        hash_type = "sha256"
    elif hash_len == 128:
        hash_type = "sha512"
    else:
        return "Hash type tidak dikenali. Support: MD5 (32), SHA1 (40), SHA256 (64), SHA512 (128) karakter hex."

    try:
        url = f"https://www.nitrxgen.net/md5db/{hash_value}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            result = resp.text.strip()
            if result:
                return f"Hash Cracked!\n\nType: {hash_type.upper()}\nHash: {hash_value}\nPlaintext: {result}"
    except Exception:
        pass

    return (
        f"Hash tidak ditemukan di database.\n\n"
        f"Type: {hash_type.upper()}\n"
        f"Hash: {hash_value}\n\n"
        f"Hash mungkin terlalu kompleks atau belum ada di database publik."
    )


# ── WHOIS / Domain Info ───────────────────────────────────────────────

async def whois_lookup(domain: str) -> str:
    """Get domain info using free API."""
    domain = domain.strip().lower()
    domain = re.sub(r'^https?://', '', domain)
    domain = domain.split('/')[0]

    try:
        url = f"http://ip-api.com/json/{domain}?fields=status,message,country,regionName,city,isp,org,as,query"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            data = resp.json()

        if data.get("status") == "success":
            return (
                f"Domain Info: {domain}\n\n"
                f"IP: {data.get('query', 'N/A')}\n"
                f"Country: {data.get('country', 'N/A')}\n"
                f"Region: {data.get('regionName', 'N/A')}\n"
                f"City: {data.get('city', 'N/A')}\n"
                f"ISP: {data.get('isp', 'N/A')}\n"
                f"Org: {data.get('org', 'N/A')}\n"
                f"AS: {data.get('as', 'N/A')}"
            )
        else:
            return f"Gagal mendapatkan info domain: {data.get('message', 'Unknown error')}"
    except Exception as e:
        return f"Error: {e}"


# ── IP Info ───────────────────────────────────────────────────────────

async def ip_info(ip: str) -> str:
    """Get IP address info using ip-api.com."""
    ip = ip.strip()
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            data = resp.json()

        if data.get("status") == "success":
            flags = []
            if data.get("proxy"):
                flags.append("Proxy/VPN")
            if data.get("mobile"):
                flags.append("Mobile")
            if data.get("hosting"):
                flags.append("Hosting/DC")
            flag_str = " ".join(flags) if flags else "Residential"

            return (
                f"IP Info: {data.get('query', ip)}\n\n"
                f"Country: {data.get('country', 'N/A')} ({data.get('regionName', '')})\n"
                f"City: {data.get('city', 'N/A')} {data.get('zip', '')}\n"
                f"Coords: {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}\n"
                f"Timezone: {data.get('timezone', 'N/A')}\n"
                f"ISP: {data.get('isp', 'N/A')}\n"
                f"Org: {data.get('org', 'N/A')}\n"
                f"AS: {data.get('as', 'N/A')}\n"
                f"Reverse DNS: {data.get('reverse', 'N/A')}\n"
                f"Type: {flag_str}"
            )
        else:
            return f"Gagal: {data.get('message', 'IP tidak valid')}"
    except Exception as e:
        return f"Error: {e}"
