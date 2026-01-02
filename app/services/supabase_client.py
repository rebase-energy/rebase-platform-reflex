"""Supabase client configuration and initialization."""
import os
from pathlib import Path
import base64
import json
from dotenv import load_dotenv

# Load environment variables from .env file
_ROOT_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_ROOT_ENV_PATH, override=False)

def get_supabase_url() -> str | None:
    """Get Supabase URL from environment (loaded from .env)."""
    return os.getenv("SUPABASE_URL")


def get_supabase_key() -> str | None:
    """Get Supabase key from environment (loaded from .env).

    This project expects the **service role** key in SUPABASE_KEY (server-side).
    SUPABASE_SERVICE_KEY is supported as a backwards-compatible alias.
    """
    key = os.getenv("SUPABASE_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    # If both are present, avoid accidentally using an anon key by preferring the
    # key whose JWT payload role is "service_role".
    if key and service_key:
        def _jwt_role(token: str) -> str | None:
            try:
                parts = token.split(".")
                if len(parts) < 2:
                    return None
                payload_b64 = parts[1]
                # Add padding for base64url decode
                payload_b64 += "=" * (-len(payload_b64) % 4)
                payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8"))
                role = payload.get("role")
                return str(role) if role else None
            except Exception:
                return None

        if _jwt_role(service_key) == "service_role":
            return service_key
        # If SUPABASE_KEY is anon but service key exists, prefer service key
        if _jwt_role(key) == "anon" and service_key:
            return service_key

    return key or service_key

# Create Supabase client singleton
_supabase_client = None
_supabase_available = False
_supabase_client_config: tuple[str, str] | None = None


def is_supabase_configured() -> bool:
    """Check if Supabase is properly configured."""
    return bool(get_supabase_url() and get_supabase_key())


def get_supabase_client():
    """Get the Supabase client instance (singleton pattern).
    
    Returns None if Supabase is not configured.
    """
    global _supabase_client, _supabase_available, _supabase_client_config
    
    if not is_supabase_configured():
        return None
    
    url = get_supabase_url()
    key = get_supabase_key()
    if not url or not key:
        return None

    # Recreate the client if the env config changed (prevents stale anon-key clients).
    if _supabase_client is None or _supabase_client_config != (url, key):
        try:
            from supabase import create_client
            _supabase_client = create_client(url, key)
            _supabase_client_config = (url, key)
            _supabase_available = True
        except Exception as e:
            print(f"Failed to create Supabase client: {e}")
            _supabase_available = False
            return None
    
    return _supabase_client

