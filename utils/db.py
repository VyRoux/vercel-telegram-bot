"""Supabase database client for MulyonoW Bot."""

import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[DB] Supabase connected!")
    except ImportError as e:
        print(f"[DB] Import error: {e}")
        print("[DB] Tip: Check if all dependencies are installed: pip install -r requirements.txt")
        print("[DB] Tip: Check Python version compatibility (pydantic_core needs Python <= 3.13)")
    except Exception as e:
        print(f"[DB] Supabase connection failed: {type(e).__name__}: {e}")
else:
    print("[DB] SUPABASE_URL / SUPABASE_KEY not set in .env")
